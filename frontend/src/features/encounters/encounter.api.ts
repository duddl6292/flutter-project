import {
  apiRequest,
} from '../../core/api/apiClient'

import type {
  ClinicalRecord,
  ClinicalRecordInput,
  EncounterDetail,
  EncounterListResponse,
  EncounterStatus,
} from './encounter.types'

interface EncounterResponse {
  data: EncounterDetail
}

interface ClinicalRecordResponse {
  data: ClinicalRecord
}

export function getEncounters({
  dateFrom,
  dateTo,
  status = '',
  search = '',
  page = 1,
  pageSize = 20,
  signal,
}: {
  dateFrom: string
  dateTo: string
  status?: EncounterStatus | ''
  search?: string
  page?: number
  pageSize?: number
  signal?: AbortSignal
}): Promise<EncounterListResponse> {
  const params = new URLSearchParams({
    date_from: dateFrom,
    date_to: dateTo,
    page: String(page),
    page_size: String(pageSize),
  })

  if (status) params.set('status', status)
  if (search.trim()) {
    params.set('search', search.trim())
  }

  return apiRequest<EncounterListResponse>(
    `/api/v1/encounters/?${params.toString()}`,
    { signal },
  )
}

export async function getEncounter(
  encounterId: string,
  signal?: AbortSignal,
): Promise<EncounterDetail> {
  const response = await apiRequest<EncounterResponse>(
    `/api/v1/encounters/${
      encodeURIComponent(encounterId)
    }/`,
    { signal },
  )

  return response.data
}

export async function updateEncounterStatus(
  encounterId: string,
  status: EncounterStatus,
): Promise<EncounterDetail> {
  const response = await apiRequest<EncounterResponse>(
    `/api/v1/encounters/${
      encodeURIComponent(encounterId)
    }/status/`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    },
  )

  return response.data
}

export async function saveClinicalRecord(
  encounterId: string,
  input: ClinicalRecordInput,
): Promise<ClinicalRecord> {
  const response =
    await apiRequest<ClinicalRecordResponse>(
      `/api/v1/encounters/${
        encodeURIComponent(encounterId)
      }/clinical-record/`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(input),
      },
    )

  return response.data
}
