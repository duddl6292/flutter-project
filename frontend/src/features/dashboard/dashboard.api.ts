import type {
  CtHistoryResponse,
  CtPredictResponse,
  CtStatusResponse,
  DashboardResponse,
} from './dashboard.types'

const DEFAULT_API_BASE_URL = 'http://localhost:8001/api/v1'

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL
).replace(/\/+$/, '')

export class ApiError extends Error {
  status: number
  body: unknown

  constructor(message: string, status: number, body: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

async function requestJson<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...options.headers,
    },
  })

  const body = await response.json().catch(() => null)

  if (!response.ok) {
    const message =
      body?.detail ??
      body?.message ??
      body?.error_message ??
      `API 요청에 실패했습니다. (${response.status})`

    throw new ApiError(message, response.status, body)
  }

  return body as T
}

export function getDashboard(
  date: string,
  signal?: AbortSignal,
): Promise<DashboardResponse> {
  return requestJson<DashboardResponse>(
    `/dashboard/?date=${encodeURIComponent(date)}`,
    { signal },
  )
}

export function getCtHistory(
  limit = 4,
  signal?: AbortSignal,
): Promise<CtHistoryResponse> {
  return requestJson<CtHistoryResponse>(
    `/history/?limit=${limit}`,
    { signal },
  )
}

export function createCtAnalysis(
  file: File,
  patientId: string,
  signal?: AbortSignal,
): Promise<CtPredictResponse> {
  const formData = new FormData()
  formData.append('ct_file', file)
  formData.append('patient_id', patientId)

  return requestJson<CtPredictResponse>('/predict/', {
    method: 'POST',
    body: formData,
    signal,
  })
}

export function getCtStatus(
  ctId: string | number,
  signal?: AbortSignal,
): Promise<CtStatusResponse> {
  return requestJson<CtStatusResponse>(
    `/status/${encodeURIComponent(String(ctId))}/`,
    { signal },
  )
}
