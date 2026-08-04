import { apiRequest } from '../../core/api/apiClient'

import type {
  Examination,
  ExaminationCategory,
  ExaminationContext,
  ExaminationCreateInput,
  ExaminationInterpretation,
  ExaminationListMeta,
  ExaminationStatus,
} from './examination.types'

interface ExaminationListResponse {
  data: Examination[]
  meta: ExaminationListMeta
}

interface ExaminationResponse {
  data: Examination
}

interface ExaminationContextResponse {
  data: ExaminationContext[]
}

export function getExaminations({
  search = '',
  status = '',
  category = '',
  interpretation = '',
  released = '',
  page = 1,
  pageSize = 20,
  signal,
}: {
  search?: string
  status?: ExaminationStatus | ''
  category?: ExaminationCategory | ''
  interpretation?: ExaminationInterpretation | ''
  released?: '' | 'true' | 'false'
  page?: number
  pageSize?: number
  signal?: AbortSignal
}): Promise<ExaminationListResponse> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  })
  if (search.trim()) params.set('search', search.trim())
  if (status) params.set('status', status)
  if (category) params.set('category', category)
  if (interpretation) params.set('interpretation', interpretation)
  if (released) params.set('released', released)

  return apiRequest<ExaminationListResponse>(
    `/api/v1/examinations/?${params.toString()}`,
    { signal },
  )
}

export async function getExamination(
  examinationId: string,
  signal?: AbortSignal,
): Promise<Examination> {
  const response = await apiRequest<ExaminationResponse>(
    `/api/v1/examinations/${encodeURIComponent(examinationId)}/`,
    { signal },
  )
  return response.data
}

export async function getExaminationContexts():
Promise<ExaminationContext[]> {
  const response = await apiRequest<ExaminationContextResponse>(
    '/api/v1/examinations/contexts/',
  )
  return response.data
}

export async function createExamination(
  input: ExaminationCreateInput,
): Promise<Examination> {
  const response = await apiRequest<ExaminationResponse>(
    '/api/v1/examinations/',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    },
  )
  return response.data
}

export async function finalizeExamination(
  examinationId: string,
  summary: string,
  conclusion: string,
): Promise<Examination> {
  const response = await apiRequest<ExaminationResponse>(
    `/api/v1/examinations/${encodeURIComponent(examinationId)}/finalize/`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ summary, conclusion }),
    },
  )
  return response.data
}

export async function releaseExamination(
  examinationId: string,
): Promise<Examination> {
  const response = await apiRequest<ExaminationResponse>(
    `/api/v1/examinations/${encodeURIComponent(examinationId)}/release/`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
    },
  )
  return response.data
}
