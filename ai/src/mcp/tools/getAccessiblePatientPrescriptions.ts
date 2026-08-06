import { z } from 'genkit/beta';

import { ai } from '../../genkit.js';
import { getBrainOnApi } from './brainOnApi.js';

const prescriptionItemSchema = z.object({
  medicine_name: z.string(),
  dosage: z.string(),
  dose_unit: z.string(),
  frequency: z.string(),
  route: z.string(),
  instructions: z.string(),
  start_date: z.string(),
  end_date: z.string().nullable(),
});

const prescriptionSchema = z.object({
  prescription_id: z.string().uuid(),
  encounter_id: z.string().uuid(),
  patient_id: z.string().uuid(),
  clinician_name: z.string(),
  status: z.enum([
    'DRAFT', 'ACTIVE', 'COMPLETED', 'DISCONTINUED', 'CANCELLED',
  ]),
  status_label: z.string(),
  notes: z.string(),
  prescribed_at: z.string().nullable(),
  discontinued_at: z.string().nullable(),
  items: z.array(prescriptionItemSchema),
});

const metaSchema = z.object({
  page: z.number().int(),
  page_size: z.number().int(),
  total_count: z.number().int(),
  total_pages: z.number().int(),
});

export const getAccessiblePatientPrescriptionsInputSchema = z.object({
  patient_id: z.string().uuid(),
  status: z.enum([
    'DRAFT', 'ACTIVE', 'COMPLETED', 'DISCONTINUED', 'CANCELLED',
  ]).optional(),
  limit: z.number().int().min(1).max(20).optional().default(5),
});

export const getAccessiblePatientPrescriptionsOutputSchema = z.object({
  prescriptions: z.array(prescriptionSchema),
  meta: metaSchema,
});

const responseSchema = z.object({
  data: z.array(prescriptionSchema),
  meta: metaSchema,
});

export async function fetchAccessiblePatientPrescriptions(input: {
  patient_id: string;
  status?: string;
  limit?: number;
}) {
  const parsed = responseSchema.parse(await getBrainOnApi(
    '/api/v1/prescriptions/',
    {
      patient_id: input.patient_id,
      status: input.status,
      page: 1,
      page_size: input.limit ?? 5,
    },
  ));
  return { prescriptions: parsed.data, meta: parsed.meta };
}

export const getAccessiblePatientPrescriptions = ai.defineTool(
  {
    name: 'getAccessiblePatientPrescriptions',
    description:
      'Returns prescriptions authored by the authenticated clinician for one '
      + 'patient. Use the patient_id from searchAccessiblePatients. Includes '
      + 'medicine, dose, frequency, route, instructions, and prescription status.',
    inputSchema: getAccessiblePatientPrescriptionsInputSchema,
    outputSchema: getAccessiblePatientPrescriptionsOutputSchema,
  },
  async (input) => fetchAccessiblePatientPrescriptions(input),
);
