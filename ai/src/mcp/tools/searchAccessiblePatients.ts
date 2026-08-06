import { z } from 'genkit/beta';

import { env } from '../../config/env.js';
import { ai } from '../../genkit.js';
import { requireUserAccessToken } from '../authContext.js';

const patientSchema = z.object({
  patient_id: z.string().uuid(),
  medical_record_number: z.string().nullable(),
  name: z.string(),
  birth_date: z.string(),
  sex: z.string(),
  status: z.string(),
  access_scope: z.enum(['ADMIN', 'HOSPITAL', 'CONSULTATION']),
  shared_consultation_id: z.string().uuid().nullable(),
  access_expires_at: z.string().nullable(),
});

const patientMetaSchema = z.object({
  page: z.number().int(),
  page_size: z.number().int(),
  total_count: z.number().int(),
  total_pages: z.number().int(),
});

export const searchAccessiblePatientsInputSchema = z.object({
  search: z
    .string()
    .max(100)
    .optional()
    .default('')
    .describe('Patient name or medical record number to search for.'),
  limit: z
    .number()
    .int()
    .min(1)
    .max(20)
    .optional()
    .default(5)
    .describe('Maximum number of accessible patients to return.'),
});

export const searchAccessiblePatientsOutputSchema = z.object({
  patients: z.array(patientSchema),
  meta: patientMetaSchema,
});

const djangoResponseSchema = z.object({
  data: z.array(patientSchema.extend({ phone: z.string().optional() })),
  meta: patientMetaSchema,
});

export const searchAccessiblePatients = ai.defineTool(
  {
    name: 'searchAccessiblePatients',
    description:
      'Searches only BrainOn patients that the authenticated clinician or admin '
      + 'is authorized to access through their hospital or an active consultation. '
      + 'Use this tool for patient lookup; never infer patients not returned here.',
    inputSchema: searchAccessiblePatientsInputSchema,
    outputSchema: searchAccessiblePatientsOutputSchema,
  },
  async ({ search, limit }) => {
    const userAccessToken = requireUserAccessToken();
    const url = new URL('/api/v1/patients/', `${env.backendInternalUrl}/`);
    if (search) {
      url.searchParams.set('search', search);
    }
    url.searchParams.set('page', '1');
    url.searchParams.set('page_size', String(limit));

    const response = await fetch(url, {
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${userAccessToken}`,
      },
      signal: AbortSignal.timeout(5_000),
    });
    if (!response.ok) {
      console.warn(
        `[brainon-mcp] patient search failed: status=${response.status}`,
      );
      throw new Error(`BrainOn patient search failed (${response.status}).`);
    }

    const parsed = djangoResponseSchema.parse(await response.json());
    console.info(
      `[brainon-mcp] patient search executed: result_count=${parsed.data.length}`,
    );
    return {
      patients: parsed.data.map(({ phone: _phone, ...patient }) => patient),
      meta: parsed.meta,
    };
  },
);
