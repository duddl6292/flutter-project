import {
  apiRequest,
} from '../../core/api/apiClient'

import type {
  PatientListResponse,
  PatientStatus,
} from './patient.types'

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