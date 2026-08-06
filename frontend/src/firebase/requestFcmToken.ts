import {
  getToken,
} from 'firebase/messaging'

import {
  firebaseConfig,
  getFirebaseMessaging,
} from './firebase'

function getServiceWorkerUrl(): string {
  const url = new URL(
    '/firebase-messaging-sw.js',
    window.location.origin,
  )

  Object.entries(firebaseConfig).forEach(
    ([key, value]) => {
      if (
        typeof value === 'string'
        && value
      ) {
        url.searchParams.set(key, value)
      }
    },
  )

  return url.toString()
}

export async function registerFirebaseMessagingServiceWorker():
Promise<ServiceWorkerRegistration> {
  const registration =
    await navigator.serviceWorker.register(
      getServiceWorkerUrl(),
      {
        scope: '/',
        updateViaCache: 'none',
      },
    )

  await navigator.serviceWorker.ready

  return registration
}

interface RequestFcmTokenOptions {
  requestPermission?: boolean
}

export async function requestFcmToken({
  requestPermission = true,
}: RequestFcmTokenOptions = {}):
Promise<string | null> {
  try {
    if (!window.isSecureContext) {
      console.error(
        '브라우저 푸시는 HTTPS 또는 localhost에서만 사용할 수 있습니다.',
      )
      return null
    }

    if (
      !('Notification' in window)
      || !('serviceWorker' in navigator)
    ) {
      console.error(
        '이 브라우저는 웹 푸시 알림을 지원하지 않습니다.',
      )
      return null
    }

    const vapidKey =
      import.meta.env.VITE_FIREBASE_VAPID_KEY

    if (!vapidKey) {
      console.error(
        'VITE_FIREBASE_VAPID_KEY가 설정되지 않았습니다.',
      )
      return null
    }

    const permission =
      Notification.permission === 'granted'
        ? 'granted'
        : requestPermission
          ? await Notification
            .requestPermission()
          : Notification.permission

    if (permission !== 'granted') {
      console.warn(
        '브라우저 알림 권한이 허용되지 않았습니다.',
      )
      return null
    }

    const messaging =
      await getFirebaseMessaging()

    if (!messaging) {
      console.error(
        '이 브라우저에서는 Firebase Messaging을 사용할 수 없습니다.',
      )
      return null
    }

    const serviceWorkerRegistration =
      await registerFirebaseMessagingServiceWorker()

    const token = await getToken(
      messaging,
      {
        vapidKey,
        serviceWorkerRegistration,
      },
    )

    if (!token) {
      console.error(
        'FCM 토큰이 발급되지 않았습니다.',
      )
      return null
    }

    return token
  } catch (error) {
    console.error(
      'FCM 토큰 발급 실패:',
      error,
    )
    return null
  }
}
