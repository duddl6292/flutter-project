import { z } from 'genkit/beta';

import { ai } from '../../genkit.js';
import { getBrainOnApi } from './brainOnApi.js';

const metaSchema = z.object({
  page: z.number().int(), page_size: z.number().int(),
  total_count: z.number().int(), total_pages: z.number().int(),
});

const releasedTestResultSchema = z.object({
  test_result_id: z.string().uuid(),
  hospital_name: z.string().nullable(),
  test_type: z.string(),
  title: z.string(),
  performed_at: z.string(),
  status: z.string(),
  status_label: z.string(),
  summary: z.string(),
  clinician_comment: z.string(),
  released_at: z.string().nullable(),
  has_result_file: z.boolean(),
});

const prescriptionSchema = z.object({
  prescription_id: z.string().uuid(),
  hospital_name: z.string().nullable(),
  clinician_name: z.string(),
  status: z.string(),
  status_label: z.string(),
  notes: z.string(),
  prescribed_at: z.string(),
  discontinued_at: z.string().nullable(),
  items: z.array(z.object({
    medicine_name: z.string(), dosage: z.string(), dose_unit: z.string(),
    frequency: z.string(), route: z.string(), instructions: z.string(),
    start_date: z.string(), end_date: z.string().nullable(),
  })),
});

const historySchema = z.object({
  encounter_id: z.string().uuid(),
  encounter_number: z.string(),
  encounter_type_label: z.string(),
  status: z.string(),
  status_label: z.string(),
  hospital_name: z.string().nullable(),
  department_name: z.string(),
  clinician_name: z.string(),
  event_at: z.string(),
});

const releasedCTSchema = z.object({
  test_result_id: z.string().uuid(),
  case_id: z.string().uuid(),
  hospital_name: z.string().nullable(),
  study_type: z.string(),
  study_type_label: z.string(),
  analysis_status: z.string(),
  analysis_status_label: z.string(),
  title: z.string(),
  performed_at: z.string(),
  summary: z.string(),
  clinician_comment: z.string(),
  released_at: z.string().nullable(),
  has_report_file: z.boolean(),
});

const notificationSchema = z.object({
  notification_id: z.string().uuid(),
  type: z.string(),
  type_label: z.string(),
  title: z.string(),
  body: z.string(),
  data: z.unknown(),
  is_read: z.boolean(),
  read_at: z.string().nullable(),
  created_at: z.string(),
});

const limitInputSchema = z.object({
  limit: z.number().int().min(1).max(20).optional().default(10),
});

export const getMyReleasedTestResultsInputSchema = limitInputSchema.extend({
  test_type: z.string().max(100).optional(),
});
export const getMyReleasedTestResultsOutputSchema = z.object({
  results: z.array(releasedTestResultSchema), total_count: z.number().int(),
});

export const getMyReleasedTestResults = ai.defineTool(
  {
    name: 'getMyReleasedTestResults',
    description:
      'Returns only final or corrected test results explicitly released to the '
      + 'authenticated patient. Use for patient questions about recent results. '
      + 'Do not add diagnoses beyond the released summary and clinician comment.',
    inputSchema: getMyReleasedTestResultsInputSchema,
    outputSchema: getMyReleasedTestResultsOutputSchema,
  },
  async ({ limit, test_type }) => {
    const parsed = z.object({ data: z.array(releasedTestResultSchema), meta: metaSchema })
      .parse(await getBrainOnApi('/api/v1/patients/me/test-results/', {
        test_type, page: 1, page_size: limit,
      }));
    return { results: parsed.data, total_count: parsed.meta.total_count };
  },
);

export const getMyPrescriptionsInputSchema = limitInputSchema.extend({
  status: z.enum(['ACTIVE', 'COMPLETED', 'DISCONTINUED', 'CANCELLED']).optional(),
});
export const getMyPrescriptionsOutputSchema = z.object({
  prescriptions: z.array(prescriptionSchema), total_count: z.number().int(),
});

export const getMyPrescriptions = ai.defineTool(
  {
    name: 'getMyPrescriptions',
    description:
      'Returns non-draft prescriptions belonging only to the authenticated '
      + 'patient, including medicine directions. Never recommend dose changes.',
    inputSchema: getMyPrescriptionsInputSchema,
    outputSchema: getMyPrescriptionsOutputSchema,
  },
  async ({ limit, status }) => {
    const parsed = z.object({ data: z.array(prescriptionSchema), meta: metaSchema })
      .parse(await getBrainOnApi('/api/v1/patients/me/prescriptions/', {
        status, page: 1, page_size: limit,
      }));
    return { prescriptions: parsed.data, total_count: parsed.meta.total_count };
  },
);

export const getMyMedicalHistoryInputSchema = limitInputSchema;
export const getMyMedicalHistoryOutputSchema = z.object({
  encounters: z.array(historySchema), total_count: z.number().int(),
});

export const getMyMedicalHistory = ai.defineTool(
  {
    name: 'getMyMedicalHistory',
    description:
      'Returns medical encounter history belonging only to the authenticated '
      + 'patient. It provides visit metadata, not an invented clinical diagnosis.',
    inputSchema: getMyMedicalHistoryInputSchema,
    outputSchema: getMyMedicalHistoryOutputSchema,
  },
  async ({ limit }) => {
    const parsed = z.object({ data: z.array(historySchema), meta: metaSchema })
      .parse(await getBrainOnApi('/api/v1/patients/me/medical-history/', {
        page: 1, page_size: limit,
      }));
    return { encounters: parsed.data, total_count: parsed.meta.total_count };
  },
);

export const getMyReleasedCTResultsInputSchema = limitInputSchema;
export const getMyReleasedCTResultsOutputSchema = z.object({
  results: z.array(releasedCTSchema), total_count: z.number().int(),
});

export const getMyReleasedCTResults = ai.defineTool(
  {
    name: 'getMyReleasedCTResults',
    description:
      'Returns only clinician-reviewed CT result summaries released to the '
      + 'authenticated patient. It never exposes raw masks or internal storage URIs.',
    inputSchema: getMyReleasedCTResultsInputSchema,
    outputSchema: getMyReleasedCTResultsOutputSchema,
  },
  async ({ limit }) => {
    const parsed = z.object({ data: z.array(releasedCTSchema), meta: metaSchema })
      .parse(await getBrainOnApi('/api/v1/patients/me/ct-results/', {
        page: 1, page_size: limit,
      }));
    return { results: parsed.data, total_count: parsed.meta.total_count };
  },
);

export const getMyNotificationsInputSchema = limitInputSchema;
export const getMyNotificationsOutputSchema = z.object({
  notifications: z.array(notificationSchema),
  total_count: z.number().int(),
  unread_count: z.number().int(),
});

export const getMyNotifications = ai.defineTool(
  {
    name: 'getMyNotifications',
    description:
      'Returns notifications belonging only to the authenticated patient. '
      + 'This is read-only and does not mark notifications as read.',
    inputSchema: getMyNotificationsInputSchema,
    outputSchema: getMyNotificationsOutputSchema,
  },
  async ({ limit }) => {
    const parsed = z.object({
      data: z.array(notificationSchema),
      meta: metaSchema.extend({ unread_count: z.number().int().optional() }),
    }).parse(await getBrainOnApi('/api/v1/patients/me/notifications/', {
      page: 1, page_size: limit,
    }));
    return {
      notifications: parsed.data,
      total_count: parsed.meta.total_count,
      unread_count: parsed.meta.unread_count
        ?? parsed.data.filter((item) => !item.is_read).length,
    };
  },
);
