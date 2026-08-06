import { z } from 'genkit/beta';

import { ai } from '../../genkit.js';
import { getBrainOnApi } from './brainOnApi.js';

const pageMetaSchema = z.object({
  page: z.number().int(),
  page_size: z.number().int(),
  total_count: z.number().int(),
  total_pages: z.number().int(),
});

const scheduleSchema = z.object({
  schedule_id: z.string().uuid(),
  hospital_name: z.string().nullable(),
  medicine_name: z.string(),
  dosage: z.string(),
  dose_unit: z.string(),
  frequency: z.string(),
  instructions: z.string(),
  dose_time: z.string(),
  days_of_week: z.array(z.number().int()),
  start_date: z.string(),
  end_date: z.string().nullable(),
  is_active: z.boolean(),
});

const recordSchema = z.object({
  medication_record_id: z.string().uuid(),
  schedule_id: z.string().uuid(),
  scheduled_at: z.string(),
  taken_at: z.string().nullable(),
  status: z.enum(['TAKEN', 'MISSED', 'SKIPPED']),
  status_label: z.string(),
  note: z.string(),
});

const scheduleResponseSchema = z.object({
  data: z.array(scheduleSchema),
  meta: pageMetaSchema,
});
const recordResponseSchema = z.object({
  data: z.array(recordSchema),
  meta: pageMetaSchema,
});

function dateInSeoul(date = new Date()): string {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date);
}

function isoWeekday(date: string): number {
  const day = new Date(`${date}T12:00:00+09:00`).getUTCDay();
  return day === 0 ? 7 : day;
}

export const getMyMedicationPlanInputSchema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  remaining_only: z.boolean().optional().default(false),
});

export const getMyMedicationPlanOutputSchema = z.object({
  date: z.string(),
  timezone: z.literal('Asia/Seoul'),
  medications: z.array(z.object({
    schedule_id: z.string().uuid(),
    medicine_name: z.string(),
    dosage: z.string(),
    dose_unit: z.string(),
    dose_time: z.string(),
    scheduled_at: z.string(),
    instructions: z.string(),
    hospital_name: z.string().nullable(),
    status: z.enum(['PLANNED', 'TAKEN', 'MISSED', 'SKIPPED']),
    taken_at: z.string().nullable(),
  })),
  total_count: z.number().int(),
  remaining_count: z.number().int(),
});

export const getMyMedicationPlan = ai.defineTool(
  {
    name: 'getMyMedicationPlan',
    description:
      'Returns the authenticated patient medication schedule for a date, '
      + 'calculated from active schedule dates, weekday rules, and medication '
      + 'records. Use for questions such as what medicine to take today. '
      + 'Never recommend changing or stopping a medication.',
    inputSchema: getMyMedicationPlanInputSchema,
    outputSchema: getMyMedicationPlanOutputSchema,
  },
  async ({ date, remaining_only }) => {
    const targetDate = date ?? dateInSeoul();
    const [scheduleRaw, recordRaw] = await Promise.all([
      getBrainOnApi('/api/v1/patients/me/medication-schedules/', {
        active: true,
        page: 1,
        page_size: 100,
      }),
      getBrainOnApi('/api/v1/patients/me/medication-records/', {
        page: 1,
        page_size: 100,
      }),
    ]);
    const schedules = scheduleResponseSchema.parse(scheduleRaw).data;
    const records = recordResponseSchema.parse(recordRaw).data;
    const weekday = isoWeekday(targetDate);
    const recordBySchedule = new Map(
      records
        .filter((record) => dateInSeoul(new Date(record.scheduled_at)) === targetDate)
        .map((record) => [record.schedule_id, record]),
    );

    let medications = schedules
      .filter((schedule) => (
        schedule.start_date <= targetDate
        && (schedule.end_date === null || schedule.end_date >= targetDate)
        && (
          schedule.days_of_week.length === 0
          || schedule.days_of_week.includes(weekday)
        )
      ))
      .map((schedule) => {
        const record = recordBySchedule.get(schedule.schedule_id);
        return {
          schedule_id: schedule.schedule_id,
          medicine_name: schedule.medicine_name,
          dosage: schedule.dosage,
          dose_unit: schedule.dose_unit,
          dose_time: schedule.dose_time,
          scheduled_at: `${targetDate}T${schedule.dose_time}+09:00`,
          instructions: schedule.instructions,
          hospital_name: schedule.hospital_name,
          status: record?.status ?? 'PLANNED' as const,
          taken_at: record?.taken_at ?? null,
        };
      })
      .sort((left, right) => left.dose_time.localeCompare(right.dose_time));

    const remainingCount = medications.filter((item) => (
      item.status === 'PLANNED' || item.status === 'MISSED'
    )).length;
    const totalCount = medications.length;
    if (remaining_only) {
      medications = medications.filter((item) => (
        item.status === 'PLANNED' || item.status === 'MISSED'
      ));
    }

    return {
      date: targetDate,
      timezone: 'Asia/Seoul' as const,
      medications,
      total_count: totalCount,
      remaining_count: remainingCount,
    };
  },
);
