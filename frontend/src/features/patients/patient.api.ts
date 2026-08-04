import {
  apiRequest,
} from '../../core/api/apiClient'

import type {
  PatientDetail,
  PatientListResponse,
  PatientStatus,
} from './patient.types'

import type {
  EncounterDetail,
} from '../encounters/encounter.types'

interface GetPatientsParams {
  search?: string
  status?: PatientStatus | ''
  page?: number
  pageSize?: number
  signal?: AbortSignal
}

export function getPatients({
  search = '',
  status = '',
  page = 1,
  pageSize = 20,
  signal,
}: GetPatientsParams):
Promise<PatientListResponse> {
  const searchParams =
    new URLSearchParams()

  searchParams.set(
    'page',
    String(page),
  )

  searchParams.set(
    'page_size',
    String(pageSize),
  )

  if (search.trim()) {
    searchParams.set(
      'search',
      search.trim(),
    )
  }

  if (status) {
    searchParams.set(
      'status',
      status,
    )
  }

  return apiRequest<PatientListResponse>(
    `/api/v1/patients/?${
      searchParams.toString()
    }`,
    {
      signal,
    },
  )
}

interface PatientDetailResponse {
  data: PatientDetail
}

interface PatientHistoryResponse {
  data: EncounterDetail[]
  meta: {
    page: number
    page_size: number
    total_count: number
    total_pages: number
  }
}

export async function getPatient(
  patientId: string,
  signal?: AbortSignal,
): Promise<PatientDetail> {
  const response =
    await apiRequest<PatientDetailResponse>(
      `/api/v1/patients/${
        encodeURIComponent(patientId)
      }/`,
      { signal },
    )

  return response.data
}

export function getPatientMedicalHistory({
  patientId,
  page = 1,
  pageSize = 10,
  signal,
}: {
  patientId: string
  page?: number
  pageSize?: number
  signal?: AbortSignal
}): Promise<PatientHistoryResponse> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  })

  return apiRequest<PatientHistoryResponse>(
    `/api/v1/patients/${
      encodeURIComponent(patientId)
    }/medical-history/?${params.toString()}`,
    { signal },
  )
}
