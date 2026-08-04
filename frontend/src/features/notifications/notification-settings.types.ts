import type {
  NotificationType,
} from './notification.types'

export interface NotificationPreference {
  notification_type: NotificationType
  push_enabled: boolean
  email_enabled: boolean
}

export interface NotificationGlobalSetting {
  quiet_hours_enabled: boolean
  quiet_hours_start: string | null
  quiet_hours_end: string | null
}

export interface NotificationSettings {
  global_setting: NotificationGlobalSetting
  preferences: NotificationPreference[]
}

export interface NotificationSettingsResponse {
  data: NotificationSettings
}

export type NotificationSettingsUpdateInput =
  NotificationSettings
