import type { AuthUser, UserRole } from '../auth/authStore'
import { useAuthStore } from '../auth/authStore'
import { apiRequest } from './apiClient'

interface LoginResponse {
  access: string
  user: AuthUser
}

export async function login(
  username: string,
  password: string,
  expectedRole: UserRole,
): Promise<AuthUser> {
  const response = await apiRequest<LoginResponse>('/api/v1/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username,
      password,
      expected_role: expectedRole,
      client_type: 'WEB',
    }),
    retryAfterRefresh: false,
  })
  useAuthStore.getState().setSession(response.access, response.user)
  return response.user
}

export async function loadCurrentUser(): Promise<AuthUser> {
  return apiRequest<AuthUser>('/api/v1/auth/me/')
}

export async function logout(): Promise<void> {
  try {
    await apiRequest<void>('/api/v1/auth/logout/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
      retryAfterRefresh: false,
    })
  } finally {
    useAuthStore.getState().clearSession()
  }
}
