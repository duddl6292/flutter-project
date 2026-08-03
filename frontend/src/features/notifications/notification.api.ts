import {
  apiRequest,
} from '../../core/api/apiClient'

import type {
  AppNotification,
  NotificationListResponse,
} from './notification.types'

export function getNotifications():
Promise<NotificationListResponse> {
  return apiRequest<
    NotificationListResponse
  >(
    '/api/v1/notifications/',
  )
}

interface NotificationReadResponse {
  data: AppNotification
}

export async function markNotificationAsRead(
  notificationId: string,
): Promise<AppNotification> {
  const response =
    await apiRequest<
      NotificationReadResponse
    >(
      `/api/v1/notifications/${
        encodeURIComponent(
          notificationId,
        )
      }/read/`,
      {
        method: 'PATCH',
      },
    )

  return response.data
}

interface NotificationReadAllResponse {
  data: {
    updated_count: number
  }
}

export function markAllNotificationsAsRead():
Promise<NotificationReadAllResponse> {
  return apiRequest<
    NotificationReadAllResponse
  >(
    '/api/v1/notifications/read-all/',
    {
      method: 'POST',
    },
  )
}
