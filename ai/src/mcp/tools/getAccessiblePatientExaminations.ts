import { z } from 'genkit/beta';

import { ai } from '../../genkit.js';
import { getBrainOnApi } from './brainOnApi.js';

const interpretationSchema = z.enum([
  'NORMAL', 'LOW', 'HIGH', 'ABNORMAL', 'CRITICAL', 'UNKNOWN',
]);

const observationSchema = z.object({
  name: z.string(),
  formatted_value: z.string(),
  unit: z.string(),
  reference_low: z.string().nullable(),
  reference_high: z.string().nullable(),
  reference_text: z.string(),
  interpretation: interpretationSchema,
  interpretation_label: z.string(),
});

const examinationSchema = z.object({
  examination_id: z.string().uuid(),
  patient_id: z.string().uuid(),
  test_code: z.string(),
  test_name: z.string(),
  category: z.string(),
  category_label: z.string(),
  status: z.string(),
  status_label: z.string(),
  performed_at: z.string().nullable(),
  result_available_at: z.string().nullable(),
  overall_interpretation: interpretationSchema,
  overall_interpretation_label: z.string(),
  abnormal_count: z.number().int(),
  observations: z.array(observationSchema),
  report: z.object({
    title: z.string(),
    summary: z.string(),
    conclusion: z.string(),
    status: z.string(),
    issued_at: z.string().nullable(),
    is_released_to_patient: z.boolean(),
  }).nullable(),
});

const metaSchema = z.object({
  page: z.number().int(),
  page_size: z.number().int(),
  total_count: z.number().int(),
  total_pages: z.number().int(),
});

export const getAccessiblePatientExaminationsInputSchema = z.object({
  patient_id: z.string().uuid(),
  status: z.enum([
    'REGISTERED', 'IN_PROGRESS', 'PRELIMINARY',
    'FINAL', 'CORRECTED', 'CANCELLED',
  ]).optional(),
  interpretation: interpretationSchema.optional(),
  limit: z.number().int().min(1).max(20).optional().default(5),
});

export const getAccessiblePatientExaminationsOutputSchema = z.object({
  examinations: z.array(examinationSchema),
  meta: metaSchema,
});

const responseSchema = z.object({
  data: z.array(examinationSchema),
  meta: metaSchema,
});

export async function fetchAccessiblePatientExaminations(input: {
  patient_id: string;
  status?: string;
  interpretation?: string;
  limit?: number;
}) {
  const parsed = responseSchema.parse(await getBrainOnApi(
    '/api/v1/examinations/',
    {
      patient_id: input.patient_id,
      status: input.status,
      interpretation: input.interpretation,
      page: 1,
      page_size: input.limit ?? 5,
    },
  ));
  return { examinations: parsed.data, meta: parsed.meta };
}

export const getAccessiblePatientExaminations = ai.defineTool(
  {
    name: 'getAccessiblePatientExaminations',
    description:
      'Returns examination results for one patient within the authenticated '
      + 'clinician consultation or hospital access scope. Use the patient_id '
      + 'from searchAccessiblePatients. Includes observations and report summary.',
    inputSchema: getAccessiblePatientExaminationsInputSchema,
    outputSchema: getAccessiblePatientExaminationsOutputSchema,
  },
  async (input) => fetchAccessiblePatientExaminations(input),
);
