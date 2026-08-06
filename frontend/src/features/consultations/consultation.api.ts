import { apiRequest } from '../../core/api/apiClient'
import { useAuthStore } from '../../core/auth/authStore'

import type {
  Consultation,
  ConsultationBox,
  ConsultationClinician,
  ConsultationContext,
  ConsultationCreateInput,
  ConsultationListMeta,
  ConsultationMessage,
  ConsultationPriority,
  ConsultationStatus,
} from './consultation.types'

interface ConsultationListResponse {
  data: Consultation[]
  meta: ConsultationListMeta
}

interface ConsultationResponse {
  data: Consultation
}

interface ConsultationMessageResponse {
  data: ConsultationMessage
}

interface ConsultationContextResponse {
  data: ConsultationContext[]
}

interface ClinicianListResponse {
  data: Array<{
    clinician_id: string
    name: string
    hospital: { hospital_name: string }
    department: { name: string }
  }>
}

export function getConsultations({
  box = 'all',
  search = '',
  status = '',
  priority = '',
  page = 1,
  pageSize = 20,
  signal,
}: {
  box?: ConsultationBox
  search?: string
  status?: ConsultationStatus | ''
  priority?: ConsultationPriority | ''
  page?: number
  pageSize?: number
  signal?: AbortSignal
}): Promise<ConsultationListResponse> {
  const params = new URLSearchParams({
    box,
    page: String(page),
    page_size: String(pageSize),
  })
  if (search.trim()) params.set('search', search.trim())
  if (status) params.set('status', status)
  if (priority) params.set('priority', priority)

  return apiRequest<ConsultationListResponse>(
    `/api/v1/consultations/?${params.toString()}`,
    { signal },
  )
}

export async function getConsultation(
  consultationId: string,
  signal?: AbortSignal,
): Promise<Consultation> {
  const response = await apiRequest<ConsultationResponse>(
    `/api/v1/consultations/${encodeURIComponent(consultationId)}/`,
    { signal },
  )
  return response.data
}

export async function getConsultationContexts():
Promise<ConsultationContext[]> {
  const response = await apiRequest<ConsultationContextResponse>(
    '/api/v1/consultations/contexts/',
  )
  return response.data
}

export async function getConsultationClinicians(
  keyword = '',
): Promise<ConsultationClinician[]> {
  const params = new URLSearchParams({ page_size: '100' })
  if (keyword.trim()) params.set('keyword', keyword.trim())
  const response = await apiRequest<ClinicianListResponse>(
    `/api/v1/clinicians/clinicians?${params.toString()}`,
  )
  const currentClinicianId =
    useAuthStore.getState().clinician?.id

  return response.data
    .filter((clinician) =>
      clinician.clinician_id !== currentClinicianId
    )
    .map((clinician) => ({
      clinician_id: clinician.clinician_id,
      name: clinician.name,
      department_name: clinician.department.name,
      hospital_name: clinician.hospital.hospital_name,
    }))
}

export async function createConsultation(
  input: ConsultationCreateInput,
): Promise<Consultation> {
  const response = await apiRequest<ConsultationResponse>(
    '/api/v1/consultations/',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    },
  )
  return response.data
}

async function consultationCommand(
  consultationId: string,
  action: 'accept' | 'complete' | 'cancel',
  body: Record<string, unknown> = {},
): Promise<Consultation> {
  const response = await apiRequest<ConsultationResponse>(
    `/api/v1/consultations/${encodeURIComponent(consultationId)}/${action}/`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    },
  )
  return response.data
}

export const acceptConsultation = (consultationId: string) =>
  consultationCommand(consultationId, 'accept')

export const completeConsultation = (
  consultationId: string,
  response: string,
) => consultationCommand(consultationId, 'complete', { response })

export const cancelConsultation = (
  consultationId: string,
  reason: string,
) => consultationCommand(consultationId, 'cancel', { reason })

export async function sendConsultationMessage(
  consultationId: string,
  content: string,
): Promise<ConsultationMessage> {
  const response = await apiRequest<ConsultationMessageResponse>(
    `/api/v1/consultations/${encodeURIComponent(consultationId)}/messages/`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    },
  )
  return response.data
}
