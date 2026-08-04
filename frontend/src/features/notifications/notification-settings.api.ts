import {
  apiRequest,
} from '../../core/api/apiClient'

import type {
  NotificationSettingsResponse,
  NotificationSettingsUpdateInput,
} from './notification-settings.types'

export function getNotificationSettings():
Promise<NotificationSettingsResponse> {
  return apiRequest<
    NotificationSettingsResponse
  >(
    '/api/v1/notifications/settings/',
  )
}

export async function updateNotificationSettings(
  input: NotificationSettingsUpdateInput,
) {
  const response =
    await apiRequest<
      NotificationSettingsResponse
    >(
      '/api/v1/notifications/settings/',
      {
        method: 'PATCH',
        headers: {
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify(input),
      },
    )

  return response.data
}
