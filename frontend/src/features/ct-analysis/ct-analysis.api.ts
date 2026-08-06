import {
  apiRequest,
  apiRequestBlob,
} from '../../core/api/apiClient'
import type { CTCase, CTSource } from './ct-analysis.types'

interface DataEnvelope<T> {
  data: T
}

export async function getCTCases(signal?: AbortSignal): Promise<CTCase[]> {
  const response = await apiRequest<DataEnvelope<CTCase[]>>(
    '/api/v1/ct-analysis/cases/?limit=100',
    { signal },
  )
  return response.data
}

export async function getCTCase(caseId: string, signal?: AbortSignal): Promise<CTCase> {
  const response = await apiRequest<DataEnvelope<CTCase>>(
    `/api/v1/ct-analysis/cases/${encodeURIComponent(caseId)}/`,
    { signal },
  )
  return response.data
}

export async function getCTSources(patientId: string, signal?: AbortSignal): Promise<CTSource[]> {
  const response = await apiRequest<DataEnvelope<CTSource[]>>(
    `/api/v1/ct-analysis/sources/?patient_id=${encodeURIComponent(patientId)}`,
    { signal },
  )
  return response.data
}

export async function createCTCase(input: {
  patientId: string
  sourceId?: string
  sourceType?: CTSource['source_type']
  file?: File
  studyType: CTCase['study_type']
  description: string
}): Promise<CTCase> {
  const body = new FormData()
  body.append('patient_id', input.patientId)
  body.append('study_type', input.studyType)
  body.append('description', input.description)
  if (input.sourceId && input.sourceType === 'IMAGING_ASSET') {
    body.append('imaging_asset_id', input.sourceId)
  }
  if (input.sourceId && input.sourceType === 'CT_CASE') {
    body.append('source_case_id', input.sourceId)
  }
  if (input.file) body.append('ct_file', input.file)
  const response = await apiRequest<DataEnvelope<CTCase>>(
    '/api/v1/ct-analysis/cases/',
    { method: 'POST', body },
  )
  return response.data
}

export async function runCTCase(caseId: string): Promise<CTCase> {
  const response = await apiRequest<DataEnvelope<CTCase>>(
    `/api/v1/ct-analysis/cases/${encodeURIComponent(caseId)}/run/`,
    { method: 'POST' },
  )
  return response.data
}

export function downloadCTAsset(path: string): Promise<Blob> {
  return apiRequestBlob(path)
}
