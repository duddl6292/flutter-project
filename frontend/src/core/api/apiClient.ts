import { useAuthStore } from '../auth/authStore'
import { env } from '../config/env'
import { ApiError } from './apiError'

interface RequestOptions
  extends RequestInit {
  retryAfterRefresh?: boolean
}

interface ApiEnvelope<T> {
  data: T
}

interface RefreshResponse {
  access: string
  refresh?: string
}

let refreshInFlight:
Promise<string> | null = null

async function refreshAccessToken():
Promise<string> {
  if (refreshInFlight) {
    return refreshInFlight
  }

  refreshInFlight = (async () => {
    const refreshToken =
      useAuthStore
        .getState()
        .refreshToken

    if (!refreshToken) {
      throw new Error(
        'Refresh Token이 없습니다.',
      )
    }

    const response = await fetch(
      `${env.apiBaseUrl}/api/v1/auth/token/refresh/`,
      {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify({
          refresh: refreshToken,
        }),
      },
    )

    if (!response.ok) {
      throw await ApiError.fromResponse(
        response,
      )
    }

    const body =
      await response.json() as
        ApiEnvelope<RefreshResponse>

    useAuthStore
      .getState()
      .updateTokens(
        body.data.access,
        body.data.refresh,
      )

    return body.data.access
  })()

  try {
    return await refreshInFlight
  } catch (error) {
    useAuthStore
      .getState()
      .clearSession()

    throw error
  } finally {
    refreshInFlight = null
  }
}

async function requestWithAuth(
  path: string,
  options: RequestOptions = {},
): Promise<Response> {
  const {
    retryAfterRefresh = true,
    headers,
    ...requestInit
  } = options

  const accessToken =
    useAuthStore
      .getState()
      .accessToken

  const requestHeaders =
    new Headers(headers)

  requestHeaders.set(
    'Accept',
    'application/json',
  )

  if (accessToken) {
    requestHeaders.set(
      'Authorization',
      `Bearer ${accessToken}`,
    )
  }

  const response = await fetch(
    `${env.apiBaseUrl}${path}`,
    {
      ...requestInit,
      headers: requestHeaders,
    },
  )

  if (
    response.status === 401
    && retryAfterRefresh
  ) {
    const newAccessToken =
      await refreshAccessToken()

    requestHeaders.set(
      'Authorization',
      `Bearer ${newAccessToken}`,
    )

    return requestWithAuth(
      path,
      {
        ...requestInit,
        headers: requestHeaders,
        retryAfterRefresh: false,
      },
    )
  }

  if (!response.ok) {
    throw await ApiError.fromResponse(
      response,
    )
  }

  return response
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const response = await requestWithAuth(
    path,
    options,
  )

  if (response.status === 204) {
    return undefined as T
  }

  return await response.json() as T
}

export async function apiRequestBlob(
  path: string,
  options: RequestOptions = {},
): Promise<Blob> {
  const response = await requestWithAuth(
    path,
    options,
  )
  return response.blob()
}
