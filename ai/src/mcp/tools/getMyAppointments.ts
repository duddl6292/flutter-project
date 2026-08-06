import { z } from 'genkit/beta';

import { ai } from '../../genkit.js';
import { getBrainOnApi } from './brainOnApi.js';

const appointmentSchema = z.object({
  appointment_id: z.string().uuid(),
  hospital_name: z.string().nullable(),
  department_name: z.string(),
  clinician_name: z.string(),
  scheduled_at: z.string(),
  location: z.string(),
  reason: z.string(),
  status: z.string(),
  status_label: z.string(),
});
const metaSchema = z.object({
  page: z.number().int(), page_size: z.number().int(),
  total_count: z.number().int(), total_pages: z.number().int(),
});
const responseSchema = z.object({ data: z.array(appointmentSchema), meta: metaSchema });

export const getMyAppointmentsInputSchema = z.object({
  status: z.enum([
    'SCHEDULED', 'CONFIRMED', 'CHECKED_IN',
    'COMPLETED', 'CANCELLED', 'NO_SHOW',
  ]).optional(),
  upcoming_only: z.boolean().optional().default(true),
  limit: z.number().int().min(1).max(20).optional().default(10),
});

export const getMyAppointmentsOutputSchema = z.object({
  appointments: z.array(appointmentSchema),
  total_count: z.number().int(),
});

export const getMyAppointments = ai.defineTool(
  {
    name: 'getMyAppointments',
    description:
      'Returns appointments belonging only to the authenticated patient. '
      + 'Use for next appointment, hospital, department, clinician, location, '
      + 'or appointment status questions.',
    inputSchema: getMyAppointmentsInputSchema,
    outputSchema: getMyAppointmentsOutputSchema,
  },
  async ({ status, upcoming_only, limit }) => {
    const parsed = responseSchema.parse(await getBrainOnApi(
      '/api/v1/patients/me/appointments/',
      { status, page: 1, page_size: 100 },
    ));
    const now = Date.now();
    const appointments = parsed.data
      .filter((item) => !upcoming_only || (
        Date.parse(item.scheduled_at) >= now
        && !['COMPLETED', 'CANCELLED', 'NO_SHOW'].includes(item.status)
      ))
      .sort((left, right) => Date.parse(left.scheduled_at) - Date.parse(right.scheduled_at))
      .slice(0, limit);
    return { appointments, total_count: appointments.length };
  },
);
