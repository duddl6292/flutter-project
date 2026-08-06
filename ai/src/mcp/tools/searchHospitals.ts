import { z } from 'genkit/beta';

import { env } from '../../config/env.js';
import { ai } from '../../genkit.js';

const hospitalSchema = z.object({
  hospital_id: z.string().uuid(),
  hospital_code: z.string(),
  hospital_name: z.string(),
  address: z.string(),
  phone: z.string(),
});

const hospitalMetaSchema = z.object({
  page: z.number().int(),
  page_size: z.number().int(),
  total_count: z.number().int(),
  total_pages: z.number().int(),
});

export const searchHospitalsInputSchema = z.object({
  search: z
    .string()
    .max(100)
    .optional()
    .default('')
    .describe('Hospital name, address, or hospital code to search for.'),
  limit: z
    .number()
    .int()
    .min(1)
    .max(20)
    .optional()
    .default(5)
    .describe('Maximum number of hospitals to return.'),
});

export const searchHospitalsOutputSchema = z.object({
  hospitals: z.array(hospitalSchema),
  meta: hospitalMetaSchema,
});

const djangoResponseSchema = z.object({
  data: z.array(hospitalSchema),
  meta: hospitalMetaSchema,
});

export const searchHospitals = ai.defineTool(
  {
    name: 'searchHospitals',
    description:
      'Searches active BrainOn hospitals by hospital name, address, or code. '
      + 'Use this for hospital lookup questions. It does not access patient data.',
    inputSchema: searchHospitalsInputSchema,
    outputSchema: searchHospitalsOutputSchema,
  },
  async ({ search, limit }) => {
    const url = new URL('/api/v1/hospitals/', `${env.backendInternalUrl}/`);
    if (search) {
      url.searchParams.set('search', search);
    }
    url.searchParams.set('page', '1');
    url.searchParams.set('page_size', String(limit));

    const response = await fetch(url, {
      headers: { Accept: 'application/json' },
      signal: AbortSignal.timeout(5_000),
    });
    if (!response.ok) {
      console.warn(
        `[brainon-mcp] searchHospitals failed: status=${response.status} url=${url}`,
      );
      throw new Error(`BrainOn hospital search failed (${response.status}).`);
    }

    const parsed = djangoResponseSchema.parse(await response.json());
    console.info(
      `[brainon-mcp] searchHospitals executed: search=${JSON.stringify(search)}`,
    );
    return {
      hospitals: parsed.data,
      meta: parsed.meta,
    };
  },
);
