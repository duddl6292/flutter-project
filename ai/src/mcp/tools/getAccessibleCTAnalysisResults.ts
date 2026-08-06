import { z } from 'genkit/beta';

import { ai } from '../../genkit.js';
import { getBrainOnApi } from './brainOnApi.js';

const ctResultSchema = z.object({
  result_id: z.string().uuid(),
  model_id: z.string(),
  model_version: z.string(),
  lesion_detected: z.boolean(),
  lesion_voxels: z.number().int(),
  lesion_volume_ml: z.number(),
  lesion_slice_count: z.number().int(),
  lesion_slice_indices: z.array(z.number().int()),
  lesion_slice_start: z.number().int().nullable(),
  lesion_slice_end: z.number().int().nullable(),
  max_lesion_slice: z.number().int().nullable(),
  total_seconds: z.number(),
  end_to_end_seconds: z.number().nullable(),
  source_url: z.string(),
  mask_url: z.string(),
});

const ctCaseSchema = z.object({
  case_id: z.string().uuid(),
  display_id: z.string(),
  study_type: z.enum(['NCCT', 'CTA', 'CTP', 'OTHER']),
  study_type_label: z.string(),
  description: z.string(),
  status: z.enum([
    'UPLOADED', 'VALIDATING', 'READY', 'PROCESSING',
    'COMPLETED', 'FAILED', 'ARCHIVED',
  ]),
  status_label: z.string(),
  patient: z.object({
    patient_id: z.string().uuid(),
    medical_record_number: z.string().nullable(),
    name: z.string(),
    sex: z.string(),
    age: z.number().int().nullable(),
  }).nullable(),
  job: z.object({
    job_id: z.string().uuid(),
    status: z.string(),
    progress: z.number().int(),
    error_code: z.string(),
    error_message: z.string(),
    error_retryable: z.boolean(),
    started_at: z.string().nullable(),
    completed_at: z.string().nullable(),
  }).nullable(),
  result: ctResultSchema.nullable(),
  created_at: z.string(),
});

export const getAccessibleCTAnalysisResultsInputSchema = z.object({
  patient_id: z.string().uuid(),
  limit: z.number().int().min(1).max(20).optional().default(5),
});

export const getAccessibleCTAnalysisResultsOutputSchema = z.object({
  cases: z.array(ctCaseSchema),
});

const responseSchema = z.object({ data: z.array(ctCaseSchema) });

export async function fetchAccessibleCTAnalysisResults(input: {
  patient_id: string;
  limit?: number;
}) {
  const parsed = responseSchema.parse(await getBrainOnApi(
    '/api/v1/ct-analysis/cases/',
    { patient_id: input.patient_id, limit: input.limit ?? 5 },
  ));
  return { cases: parsed.data };
}

export const getAccessibleCTAnalysisResults = ai.defineTool(
  {
    name: 'getAccessibleCTAnalysisResults',
    description:
      'Returns authorized CT analysis cases for one patient, including job '
      + 'status and lesion measurements. It can report lesion slice range, '
      + 'largest-lesion slice, and volume, but not an anatomical brain region.',
    inputSchema: getAccessibleCTAnalysisResultsInputSchema,
    outputSchema: getAccessibleCTAnalysisResultsOutputSchema,
  },
  async (input) => fetchAccessibleCTAnalysisResults(input),
);
