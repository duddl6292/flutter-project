import { vertexAI } from '@genkit-ai/google-genai';
import { z } from 'genkit/beta';

import { env } from '../config/env.js';
import { ai, genkitConfigured } from '../genkit.js';
import { createBrainOnMcpClient } from '../mcp/client.js';

const PROTECTED_SUBJECT_PATTERN = /(?:환자|담당\s*환자|patient|medical\s*record)/i;
const PROTECTED_ACTION_PATTERN = /(?:조회|찾아|알려|요약|확인|예약|진료|검사|처방|투약|협진|결과|시간|record|appointment|prescription|result)/i;
const NAMED_PATIENT_ACTION_PATTERN = /[가-힣]{2,4}(?:님|씨)?\s*(?:환자\s*)?(?:의\s*)?(?:예약|진료|검사|처방|투약|협진|결과)/;
const PERSONAL_HEALTH_ACTION_PATTERN = /(?:내|나의|오늘|이번\s*주).*(?:약|복약|예약|진료|검사|처방|CT|알림)/i;

export function requestsProtectedPatientData(message: string): boolean {
  return (
    (
      PROTECTED_SUBJECT_PATTERN.test(message)
      && PROTECTED_ACTION_PATTERN.test(message)
    )
    || NAMED_PATIENT_ACTION_PATTERN.test(message)
    || PERSONAL_HEALTH_ACTION_PATTERN.test(message)
  );
}

export const assistantFlow = ai.defineFlow(
  {
    name: 'assistantFlow',
    inputSchema: z.object({
      message: z.string().min(1).max(2000),
      userAccessToken: z.string().min(1).optional(),
      userRole: z.enum(['PATIENT', 'CLINICIAN', 'ADMIN']).optional(),
    }),
    outputSchema: z.object({
      text: z.string(),
    }),
  },
  async ({ message, userAccessToken, userRole }) => {
    if (!genkitConfigured) {
      throw new Error('GOOGLE_CLOUD_PROJECT is not configured.');
    }

    const patientDataRequested = requestsProtectedPatientData(message);

    if (patientDataRequested && !userAccessToken) {
      return {
        text: [
          '환자 정보를 조회하려면 BrainOn 로그인이 필요합니다.',
          '인증 정보가 없어 실제 환자 데이터를 확인하거나 추측해서 답변할 수 없습니다.',
          '다시 로그인한 뒤 요청해 주세요.',
        ].join(' '),
      };
    }

    const mcpClient = createBrainOnMcpClient(userAccessToken);
    try {
      let tools: Awaited<ReturnType<typeof mcpClient.getActiveTools>> = [];
      try {
        tools = await mcpClient.getActiveTools(ai);
      } catch (error) {
        console.warn(
          '[brainon-ai] MCP tools unavailable:',
          error instanceof Error ? error.message : 'unknown error',
        );
        if (patientDataRequested) {
          return {
            text: [
              '현재 환자 조회 도구에 연결할 수 없습니다.',
              '환자 정보를 추측해서 답변하지 않으며, 잠시 후 다시 시도해 주세요.',
            ].join(' '),
          };
        }
      }
      const response = await ai.generate({
        model: vertexAI.model(env.aiModel),
        system: [
          'You are the BrainOn clinical support assistant.',
          `The authenticated BrainOn role is ${userRole ?? 'UNKNOWN'}.`,
          'Use the available MCP tools for BrainOn system status or BrainOn factual data instead of guessing.',
          'Never claim database or medical-record access unless a tool result explicitly provides it.',
          'For patient lookup, only use searchAccessiblePatients and only report patients returned by that tool.',
          'For appointment questions, first call searchAccessiblePatients with the patient name. If exactly one patient matches, call getAccessiblePatientAppointments with that patient_id. If multiple patients match, ask the user to identify the correct patient by medical record number or birth date.',
          'For a broad patient overview, first identify the patient and then call getAccessiblePatientClinicalSummary instead of guessing or calling every detail tool.',
          'For detailed examination, prescription, consultation, or CT questions, identify the patient first and use the corresponding authenticated tool.',
          'For today workload questions, use getClinicianWorkSummary.',
          'For PATIENT role questions about my data, only use tools whose names start with getMy. Never use clinician patient-search tools for a patient account.',
          'For CLINICIAN or ADMIN roles, use accessible-patient tools and never use getMy patient-app tools.',
          'Medication tools only restate active schedules and records. Never advise changing, skipping, stopping, or doubling a medicine.',
          'Patient test and CT answers must only restate released summaries and clinician comments. Never expose raw internal AI results to a patient.',
          'CT tools report mask-derived slice and volume measurements only. Never invent an anatomical brain region.',
          'Never say that an appointment does not exist unless getAccessiblePatientAppointments returned zero results.',
          'Answer general knowledge questions directly even when no tool is needed.',
          'Answer in the same language as the user.',
        ].join(' '),
        prompt: message,
        tools,
      });
      return { text: response.text };
    } finally {
      try {
        await mcpClient.disable();
      } catch (error) {
        console.warn(
          '[brainon-ai] MCP client cleanup failed:',
          error instanceof Error ? error.message : 'unknown error',
        );
      }
    }
  },
);
