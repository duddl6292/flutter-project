import { z } from 'genkit/beta';

import { ai } from '../../genkit.js';
import { getBrainOnApi } from './brainOnApi.js';

const clinicianSchema = z.object({
  clinician_id: z.string().uuid(),
  name: z.string(),
  department_name: z.string(),
  hospital_name: z.string(),
});

const messageSchema = z.object({
  message_id: z.string().uuid(),
  sender: clinicianSchema.nullable(),
  content: z.string(),
  is_system: z.boolean(),
  created_at: z.string(),
});

const consultationSchema = z.object({
  consultation_id: z.string().uuid(),
  patient_id: z.string().uuid(),
  patient_name: z.string(),
  requester: clinicianSchema,
  consultant: clinicianSchema,
  subject: z.string(),
  priority: z.enum(['ROUTINE', 'URGENT', 'EMERGENCY']),
  priority_label: z.string(),
  question: z.string(),
  response: z.string(),
  status: z.enum(['REQUESTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']),
  status_label: z.string(),
  my_role: z.enum(['REQUESTER', 'CONSULTANT', 'OBSERVER']),
  unread_count: z.number().int(),
  messages: z.array(messageSchema),
  due_at: z.string().nullable(),
  accepted_at: z.string().nullable(),
  completed_at: z.string().nullable(),
  cancelled_at: z.string().nullable(),
  created_at: z.string(),
});

const consultationSummarySchema = consultationSchema.omit({ messages: true }).extend({
  latest_message: messageSchema.nullable(),
});

const metaSchema = z.object({
  page: z.number().int(),
  page_size: z.number().int(),
  total_count: z.number().int(),
  total_pages: z.number().int(),
});

export const searchAccessibleConsultationsInputSchema = z.object({
  patient_id: z.string().uuid().optional(),
  box: z.enum(['all', 'received', 'sent']).optional().default('all'),
  status: z.enum([
    'REQUESTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED',
  ]).optional(),
  priority: z.enum(['ROUTINE', 'URGENT', 'EMERGENCY']).optional(),
  search: z.string().max(100).optional().default(''),
  limit: z.number().int().min(1).max(20).optional().default(10),
});

export const searchAccessibleConsultationsOutputSchema = z.object({
  consultations: z.array(consultationSummarySchema),
  meta: metaSchema,
});

const responseSchema = z.object({
  data: z.array(consultationSchema),
  meta: metaSchema,
});

export async function fetchAccessibleConsultations(input: {
  patient_id?: string;
  box?: string;
  status?: string;
  priority?: string;
  search?: string;
  limit?: number;
}) {
  const parsed = responseSchema.parse(await getBrainOnApi(
    '/api/v1/consultations/',
    {
      patient_id: input.patient_id,
      box: input.box ?? 'all',
      status: input.status,
      priority: input.priority,
      search: input.search,
      page: 1,
      page_size: input.limit ?? 10,
    },
  ));
  return {
    consultations: parsed.data.map(({ messages, ...consultation }) => ({
      ...consultation,
      latest_message: messages.at(-1) ?? null,
    })),
    meta: parsed.meta,
  };
}

export const searchAccessibleConsultations = ai.defineTool(
  {
    name: 'searchAccessibleConsultations',
    description:
      'Searches consultations where the authenticated clinician is an active '
      + 'participant. Can filter by patient, inbox, status, priority, or text. '
      + 'Returns the latest message and final response when available.',
    inputSchema: searchAccessibleConsultationsInputSchema,
    outputSchema: searchAccessibleConsultationsOutputSchema,
  },
  async (input) => fetchAccessibleConsultations(input),
);
