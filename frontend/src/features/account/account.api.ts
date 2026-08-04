import {
  apiRequest,
} from '../../core/api/apiClient'

import type {
  AuthUser,
  ClinicianProfile,
} from '../../core/auth/authStore'

export interface CurrentAccount {
  user: AuthUser
  clinician: ClinicianProfile | null
}

interface AccountResponse {
  data: CurrentAccount
}

export async function getCurrentAccount():
Promise<CurrentAccount> {
  const response =
    await apiRequest<AccountResponse>(
      '/api/v1/auth/me/',
    )

  return response.data
}

export async function updateAccountEmail(
  email: string,
): Promise<CurrentAccount> {
  const response =
    await apiRequest<AccountResponse>(
      '/api/v1/auth/me/',
      {
        method: 'PATCH',
        headers: {
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify({
          email,
        }),
      },
    )

  return response.data
}

interface PasswordChangeInput {
  currentPassword: string
  newPassword: string
  newPasswordConfirm: string
}

export async function changePassword({
  currentPassword,
  newPassword,
  newPasswordConfirm,
}: PasswordChangeInput): Promise<void> {
  await apiRequest(
    '/api/v1/auth/password/change/',
    {
      method: 'POST',
      headers: {
        'Content-Type':
          'application/json',
      },
      body: JSON.stringify({
        current_password:
          currentPassword,
        new_password:
          newPassword,
        new_password_confirm:
          newPasswordConfirm,
      }),
    },
  )
}
