import { z } from 'genkit/beta';

import { ai } from '../../genkit.js';
import { getBrainOnApi } from './brainOnApi.js';

const appointmentSchema = z.object({
  appointment_id: z.string().uuid(),
  patient_id: z.string().uuid(),
  patient_name: z.string(),
  clinician_id: z.string().uuid(),
  clinician_name: z.string(),
  department_code: z.string(),
  department_name: z.string(),
  hospital_id: z.string().uuid().nullable(),
  hospital_name: z.string().nullable(),
  scheduled_at: z.string(),
  duration_minutes: z.number().int(),
  location: z.string(),
  status: z.string(),
});

export const getAccessiblePatientAppointmentsInputSchema = z.object({
  patient_id: z
    .string()
    .uuid()
    .describe('Patient UUID returned by searchAccessiblePatients.'),
  status: z
    .enum([
      'SCHEDULED',
      'CONFIRMED',
      'CHECKED_IN',
      'COMPLETED',
      'CANCELLED',
      'NO_SHOW',
    ])
    .optional()
    .describe('Optional appointment status filter.'),
  date_from: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/)
    .optional()
    .describe('Optional start date in YYYY-MM-DD format.'),
  date_to: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/)
    .optional()
    .describe('Optional end date in YYYY-MM-DD format.'),
});

export const getAccessiblePatientAppointmentsOutputSchema = z.object({
  appointments: z.array(appointmentSchema),
  meta: z.object({ total_count: z.number().int() }),
});

const djangoResponseSchema = z.object({
  data: z.array(appointmentSchema),
  meta: z.object({ total_count: z.number().int() }),
});

export const getAccessiblePatientAppointments = ai.defineTool(
  {
    name: 'getAccessiblePatientAppointments',
    description:
      'Returns appointments for one patient that are visible to the '
      + 'authenticated clinician or admin. The patient_id must come from '
      + 'searchAccessiblePatients. Use this for appointment date, time, '
      + 'location, clinician, department, and status questions.',
    inputSchema: getAccessiblePatientAppointmentsInputSchema,
    outputSchema: getAccessiblePatientAppointmentsOutputSchema,
  },
  async (input) => fetchAccessiblePatientAppointments(input),
);

export async function fetchAccessiblePatientAppointments(input: {
  patient_id: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}) {
    const parsed = djangoResponseSchema.parse(await getBrainOnApi(
      '/api/v1/appointments/',
      input,
    ));
    console.info(
      `[brainon-mcp] appointment lookup executed: result_count=${parsed.data.length}`,
    );
    return {
      appointments: parsed.data,
      meta: parsed.meta,
    };
}
