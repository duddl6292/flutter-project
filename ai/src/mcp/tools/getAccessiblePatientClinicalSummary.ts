import { z } from 'genkit/beta';

import { ai } from '../../genkit.js';
import { fetchAccessiblePatientAppointments } from './getAccessiblePatientAppointments.js';
import { fetchAccessibleCTAnalysisResults } from './getAccessibleCTAnalysisResults.js';
import { fetchAccessibleConsultations } from './searchAccessibleConsultations.js';
import { fetchAccessiblePatientExaminations } from './getAccessiblePatientExaminations.js';
import { fetchAccessiblePatientPrescriptions } from './getAccessiblePatientPrescriptions.js';
import { getBrainOnApi } from './brainOnApi.js';

const patientSchema = z.object({
  patient_id: z.string().uuid(),
  medical_record_number: z.string().nullable(),
  name: z.string(),
  birth_date: z.string().nullable(),
  sex: z.string(),
  status: z.string(),
  access_scope: z.enum(['ADMIN', 'HOSPITAL', 'CONSULTATION']),
  access_expires_at: z.string().nullable(),
});

const encounterSchema = z.object({
  encounter_id: z.string().uuid(),
  encounter_number: z.string(),
  encounter_type_label: z.string(),
  status_label: z.string(),
  hospital_name: z.string().nullable(),
  department_name: z.string(),
  clinician_name: z.string(),
  event_at: z.string(),
});

const historyResponseSchema = z.object({
  data: z.array(encounterSchema),
  meta: z.object({ total_count: z.number().int() }),
});

const patientResponseSchema = z.object({ data: patientSchema });

export const getAccessiblePatientClinicalSummaryInputSchema = z.object({
  patient_id: z.string().uuid(),
});

export const getAccessiblePatientClinicalSummaryOutputSchema = z.object({
  patient: patientSchema,
  recent_encounters: z.array(encounterSchema),
  counts: z.object({
    encounters: z.number().int(),
    appointments: z.number().int(),
    examinations: z.number().int(),
    active_prescriptions: z.number().int(),
    consultations: z.number().int(),
    ct_analyses: z.number().int(),
  }),
  next_appointments: z.array(z.object({
    scheduled_at: z.string(),
    clinician_name: z.string(),
    department_name: z.string(),
    hospital_name: z.string().nullable(),
    location: z.string(),
    status: z.string(),
  })),
  recent_examinations: z.array(z.object({
    examination_id: z.string().uuid(),
    test_name: z.string(),
    status: z.string(),
    performed_at: z.string().nullable(),
    overall_interpretation: z.string(),
    abnormal_count: z.number().int(),
    report_summary: z.string(),
    report_conclusion: z.string(),
  })),
  active_prescriptions: z.array(z.object({
    prescription_id: z.string().uuid(),
    prescribed_at: z.string().nullable(),
    medicines: z.array(z.string()),
  })),
  open_consultations: z.array(z.object({
    consultation_id: z.string().uuid(),
    subject: z.string(),
    priority: z.string(),
    status: z.string(),
    due_at: z.string().nullable(),
  })),
  latest_ct_analysis: z.object({
    case_id: z.string().uuid(),
    status: z.string(),
    lesion_detected: z.boolean().nullable(),
    lesion_volume_ml: z.number().nullable(),
    lesion_slice_start: z.number().int().nullable(),
    lesion_slice_end: z.number().int().nullable(),
    max_lesion_slice: z.number().int().nullable(),
  }).nullable(),
  unavailable_sections: z.array(z.string()),
});

export const getAccessiblePatientClinicalSummary = ai.defineTool(
  {
    name: 'getAccessiblePatientClinicalSummary',
    description:
      'Builds a concise authorized clinical overview for one patient by '
      + 'combining recent encounters, appointments, examinations, active '
      + 'prescriptions, consultations, and CT analysis. Use patient_id from '
      + 'searchAccessiblePatients. Never infer unavailable sections.',
    inputSchema: getAccessiblePatientClinicalSummaryInputSchema,
    outputSchema: getAccessiblePatientClinicalSummaryOutputSchema,
  },
  async ({ patient_id }) => {
    const patient = patientResponseSchema.parse(await getBrainOnApi(
      `/api/v1/patients/${encodeURIComponent(patient_id)}/`,
    )).data;

    const sections = await Promise.allSettled([
      getBrainOnApi(
        `/api/v1/patients/${encodeURIComponent(patient_id)}/medical-history/`,
        { page: 1, page_size: 5 },
      ),
      fetchAccessiblePatientAppointments({ patient_id }),
      fetchAccessiblePatientExaminations({ patient_id, limit: 5 }),
      fetchAccessiblePatientPrescriptions({
        patient_id,
        status: 'ACTIVE',
        limit: 5,
      }),
      fetchAccessibleConsultations({ patient_id, limit: 5 }),
      fetchAccessibleCTAnalysisResults({ patient_id, limit: 5 }),
    ]);

    const unavailableSections: string[] = [];
    const value = <T>(index: number, label: string): T | null => {
      const section = sections[index];
      if (section?.status === 'fulfilled') return section.value as T;
      unavailableSections.push(label);
      return null;
    };

    const historyRaw = value<unknown>(0, 'recent_encounters');
    const history = historyRaw
      ? historyResponseSchema.parse(historyRaw)
      : { data: [], meta: { total_count: 0 } };
    const appointments = value<Awaited<ReturnType<
      typeof fetchAccessiblePatientAppointments
    >>>(1, 'appointments');
    const examinations = value<Awaited<ReturnType<
      typeof fetchAccessiblePatientExaminations
    >>>(2, 'examinations');
    const prescriptions = value<Awaited<ReturnType<
      typeof fetchAccessiblePatientPrescriptions
    >>>(3, 'prescriptions');
    const consultations = value<Awaited<ReturnType<
      typeof fetchAccessibleConsultations
    >>>(4, 'consultations');
    const ctAnalyses = value<Awaited<ReturnType<
      typeof fetchAccessibleCTAnalysisResults
    >>>(5, 'ct_analyses');

    const now = Date.now();
    const nextAppointments = (appointments?.appointments ?? [])
      .filter((item) => (
        Date.parse(item.scheduled_at) >= now
        && !['COMPLETED', 'CANCELLED', 'NO_SHOW'].includes(item.status)
      ))
      .slice(0, 3)
      .map((item) => ({
        scheduled_at: item.scheduled_at,
        clinician_name: item.clinician_name,
        department_name: item.department_name,
        hospital_name: item.hospital_name,
        location: item.location,
        status: item.status,
      }));
    const latestCase = ctAnalyses?.cases[0] ?? null;

    return {
      patient,
      recent_encounters: history.data,
      counts: {
        encounters: history.meta.total_count,
        appointments: appointments?.meta.total_count ?? 0,
        examinations: examinations?.meta.total_count ?? 0,
        active_prescriptions: prescriptions?.meta.total_count ?? 0,
        consultations: consultations?.meta.total_count ?? 0,
        ct_analyses: ctAnalyses?.cases.length ?? 0,
      },
      next_appointments: nextAppointments,
      recent_examinations: (examinations?.examinations ?? []).map((item) => ({
        examination_id: item.examination_id,
        test_name: item.test_name,
        status: item.status,
        performed_at: item.performed_at,
        overall_interpretation: item.overall_interpretation,
        abnormal_count: item.abnormal_count,
        report_summary: item.report?.summary ?? '',
        report_conclusion: item.report?.conclusion ?? '',
      })),
      active_prescriptions: (prescriptions?.prescriptions ?? []).map((item) => ({
        prescription_id: item.prescription_id,
        prescribed_at: item.prescribed_at,
        medicines: item.items.map((medicine) => (
          `${medicine.medicine_name} ${medicine.dosage}${medicine.dose_unit}`
        )),
      })),
      open_consultations: (consultations?.consultations ?? [])
        .filter((item) => ['REQUESTED', 'IN_PROGRESS'].includes(item.status))
        .map((item) => ({
          consultation_id: item.consultation_id,
          subject: item.subject,
          priority: item.priority,
          status: item.status,
          due_at: item.due_at,
        })),
      latest_ct_analysis: latestCase ? {
        case_id: latestCase.case_id,
        status: latestCase.status,
        lesion_detected: latestCase.result?.lesion_detected ?? null,
        lesion_volume_ml: latestCase.result?.lesion_volume_ml ?? null,
        lesion_slice_start: latestCase.result?.lesion_slice_start ?? null,
        lesion_slice_end: latestCase.result?.lesion_slice_end ?? null,
        max_lesion_slice: latestCase.result?.max_lesion_slice ?? null,
      } : null,
      unavailable_sections: unavailableSections,
    };
  },
);
