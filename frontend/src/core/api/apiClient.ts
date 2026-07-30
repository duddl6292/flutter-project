import { useAuthStore } from '../auth/authStore'
import { env } from '../config/env'
import { ApiError } from './apiError'

interface RequestOptions extends RequestInit {
  retryAfterRefresh?: boolean
}

let refreshInFlight: Promise<string> | null = null

async function refreshAccessToken(): Promise<string> {
  if (refreshInFlight) {
    return refreshInFlight
  }
  refreshInFlight = (async () => {
    const response = await fetch(`${env.apiBaseUrl}/api/v1/auth/refresh/`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_type: 'WEB' }),
    })
    if (!response.ok) {
      throw await ApiError.fromResponse(response)
    }
    const data = (await response.json()) as { access: string }
    useAuthStore.getState().setAccessToken(data.access)
    return data.access
  })()

  try {
    return await refreshInFlight
  } finally {
    refreshInFlight = null
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { retryAfterRefresh = true, headers, ...requestInit } = options
  const accessToken = useAuthStore.getState().accessToken
  const requestHeaders = new Headers(headers)
  requestHeaders.set('Accept', 'application/json')
  if (accessToken) {
    requestHeaders.set('Authorization', `Bearer ${accessToken}`)
  }

  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    ...requestInit,
    credentials: 'include',
    headers: requestHeaders,
  })

  if (
    response.status === 401 &&
    retryAfterRefresh &&
    path !== '/api/v1/auth/refresh/'
  ) {
    try {
      const refreshedAccessToken = await refreshAccessToken()
      requestHeaders.set('Authorization', `Bearer ${refreshedAccessToken}`)
      return apiRequest<T>(path, {
        ...requestInit,
        headers: requestHeaders,
        retryAfterRefresh: false,
      })
    } catch (error) {
      useAuthStore.getState().clearSession()
      throw error
    }
  }

  if (!response.ok) {
    throw await ApiError.fromResponse(response)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}
