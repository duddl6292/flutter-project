import {
  apiRequest,
} from '../../core/api/apiClient'

const DEVICE_IDENTIFIER_KEY =
  'brainon-clinician-web-device-id'

let memoryDeviceIdentifier:
string | null = null

function createDeviceIdentifier(): string {
  if (
    'randomUUID' in crypto
  ) {
    return crypto.randomUUID()
  }

  return `${Date.now()}-${
    Math.random()
      .toString(36)
      .slice(2)
  }`
}

export function getExistingDeviceIdentifier():
string | null {
  try {
    return localStorage.getItem(
      DEVICE_IDENTIFIER_KEY,
    )
  } catch {
    return memoryDeviceIdentifier
  }
}

export function getOrCreateDeviceIdentifier():
string {
  const existing =
    getExistingDeviceIdentifier()

  if (existing) {
    return existing
  }

  const created = createDeviceIdentifier()
  memoryDeviceIdentifier = created

  try {
    localStorage.setItem(
      DEVICE_IDENTIFIER_KEY,
      created,
    )
  } catch {
    // Private browsing can block persistent storage.
  }

  return created
}

interface NotificationDevice {
  device_id: string
  platform: 'WEB'
  client_type: 'CLINICIAN_WEB'
  device_identifier: string
  device_name: string
  app_version: string
  is_active: boolean
  registered_at: string
  last_used_at: string | null
}

interface NotificationDeviceResponse {
  data: NotificationDevice
}

export async function registerWebNotificationDevice(
  fcmToken: string,
): Promise<NotificationDevice> {
  const response =
    await apiRequest<
      NotificationDeviceResponse
    >(
      '/api/v1/notifications/devices/register/',
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify({
          platform: 'WEB',
          client_type: 'CLINICIAN_WEB',
          device_identifier:
            getOrCreateDeviceIdentifier(),
          fcm_token: fcmToken,
          device_name:
            navigator.userAgent.slice(
              0,
              200,
            ),
          app_version: '0.1.0',
        }),
      },
    )

  return response.data
}

interface DeviceUnregisterResponse {
  data: {
    updated_count: number
  }
}

export async function unregisterWebNotificationDevice():
Promise<number> {
  const deviceIdentifier =
    getExistingDeviceIdentifier()

  if (!deviceIdentifier) {
    return 0
  }

  const response =
    await apiRequest<
      DeviceUnregisterResponse
    >(
      '/api/v1/notifications/devices/unregister/',
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify({
          client_type: 'CLINICIAN_WEB',
          device_identifier:
            deviceIdentifier,
        }),
        retryAfterRefresh: false,
      },
    )

  return response.data.updated_count
}
