import { z } from 'genkit/beta';

import { ai } from '../../genkit.js';
import { getBrainOnApi } from './brainOnApi.js';
import { fetchAccessibleConsultations } from './searchAccessibleConsultations.js';

const statusCountSchema = z.object({
  status: z.string(),
  label: z.string(),
  count: z.number().int(),
});

const reportSchema = z.object({
  data: z.object({
    clinician: z.object({ clinician_id: z.string().uuid(), name: z.string() }),
    period: z.object({ start_date: z.string(), end_date: z.string() }),
    summary: z.object({
      patient_count: z.number().int(),
      appointment_completion_rate: z.number(),
      prescription_count: z.number().int(),
      ct_analysis_count: z.number().int(),
    }),
    appointment_statuses: z.array(statusCountSchema),
    prescription_statuses: z.array(statusCountSchema),
    top_medicines: z.array(z.object({
      medicine_name: z.string(),
      count: z.number().int(),
    })),
  }),
});

function todayInSeoul(): string {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date());
}

export const getClinicianWorkSummaryInputSchema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
});

export const getClinicianWorkSummaryOutputSchema = z.object({
  date: z.string(),
  clinician_name: z.string(),
  patient_count: z.number().int(),
  appointment_completion_rate: z.number(),
  appointment_statuses: z.array(statusCountSchema),
  prescription_count: z.number().int(),
  prescription_statuses: z.array(statusCountSchema),
  ct_analysis_count: z.number().int(),
  open_consultation_count: z.number().int(),
  urgent_consultation_count: z.number().int(),
  open_consultations: z.array(z.object({
    consultation_id: z.string().uuid(),
    patient_name: z.string(),
    subject: z.string(),
    priority: z.string(),
    status: z.string(),
    due_at: z.string().nullable(),
  })),
  top_medicines: z.array(z.object({
    medicine_name: z.string(),
    count: z.number().int(),
  })),
});

export const getClinicianWorkSummary = ai.defineTool(
  {
    name: 'getClinicianWorkSummary',
    description:
      'Returns the authenticated clinician workload for a date, including '
      + 'appointment and prescription status counts, CT analysis count, and '
      + 'open consultations. Defaults to today in Asia/Seoul.',
    inputSchema: getClinicianWorkSummaryInputSchema,
    outputSchema: getClinicianWorkSummaryOutputSchema,
  },
  async ({ date }) => {
    const targetDate = date ?? todayInSeoul();
    const [reportRaw, consultations] = await Promise.all([
      getBrainOnApi('/api/v1/reports/clinician-summary/', {
        start_date: targetDate,
        end_date: targetDate,
      }),
      fetchAccessibleConsultations({ limit: 20 }),
    ]);
    const report = reportSchema.parse(reportRaw).data;
    const open = consultations.consultations.filter((item) => (
      item.status === 'REQUESTED' || item.status === 'IN_PROGRESS'
    ));

    return {
      date: targetDate,
      clinician_name: report.clinician.name,
      patient_count: report.summary.patient_count,
      appointment_completion_rate: report.summary.appointment_completion_rate,
      appointment_statuses: report.appointment_statuses,
      prescription_count: report.summary.prescription_count,
      prescription_statuses: report.prescription_statuses,
      ct_analysis_count: report.summary.ct_analysis_count,
      open_consultation_count: open.length,
      urgent_consultation_count: open.filter((item) => (
        item.priority === 'URGENT' || item.priority === 'EMERGENCY'
      )).length,
      open_consultations: open.map((item) => ({
        consultation_id: item.consultation_id,
        patient_name: item.patient_name,
        subject: item.subject,
        priority: item.priority,
        status: item.status,
        due_at: item.due_at,
      })),
      top_medicines: report.top_medicines,
    };
  },
);
