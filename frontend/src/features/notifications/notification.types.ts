export type NotificationType =
  | 'APPOINTMENT'
  | 'MEDICATION'
  | 'TEST_RESULT'
  | 'CONSULTATION'
  | 'EMERGENCY'
  | 'SYSTEM'
  | 'OTHER'

export interface AppNotification {
  notification_id: string
  type: NotificationType
  title: string
  body: string

  data: {
    path?: string
    [key: string]: unknown
  }

  is_read: boolean
  read_at: string | null
  created_at: string
}

export interface NotificationListResponse {
  data: AppNotification[]

  meta: {
    unread_count: number
  }
}
