import {
  apiRequest,
} from '../../core/api/apiClient'

import type {
  Prescription,
  PrescriptionContext,
  PrescriptionCreateInput,
  PrescriptionListMeta,
  PrescriptionStatus,
} from './prescription.types'

interface PrescriptionListResponse {
  data: Prescription[]
  meta: PrescriptionListMeta
}

interface PrescriptionResponse {
  data: Prescription
}

interface ContextListResponse {
  data: PrescriptionContext[]
}

interface GetPrescriptionsParams {
  search?: string
  status?: PrescriptionStatus | ''
  page?: number
  pageSize?: number
  signal?: AbortSignal
}

export async function getPrescriptions({
  search = '',
  status = '',
  page = 1,
  pageSize = 20,
  signal,
}: GetPrescriptionsParams):
Promise<PrescriptionListResponse> {
  const searchParams = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  })

  if (search.trim()) {
    searchParams.set('search', search.trim())
  }

  if (status) {
    searchParams.set('status', status)
  }

  return apiRequest<PrescriptionListResponse>(
    `/api/v1/prescriptions/?${
      searchParams.toString()
    }`,
    { signal },
  )
}

export async function getPrescriptionContexts():
Promise<PrescriptionContext[]> {
  const response =
    await apiRequest<ContextListResponse>(
      '/api/v1/prescriptions/contexts/',
    )

  return response.data
}

export async function createPrescription(
  input: PrescriptionCreateInput,
): Promise<Prescription> {
  const response =
    await apiRequest<PrescriptionResponse>(
      '/api/v1/prescriptions/',
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify(input),
      },
    )

  return response.data
}

export async function updatePrescriptionStatus(
  prescriptionId: string,
  status: PrescriptionStatus,
): Promise<Prescription> {
  const response =
    await apiRequest<PrescriptionResponse>(
      `/api/v1/prescriptions/${
        encodeURIComponent(prescriptionId)
      }/status/`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify({ status }),
      },
    )

  return response.data
}
