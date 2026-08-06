/* global firebase */

self.addEventListener(
  'notificationclick',
  (event) => {
    event.notification.close()

    const path =
      event.notification.data?.path
      ?? '/dashboard'
    const targetUrl = new URL(
      path.startsWith('/')
        ? path
        : '/dashboard',
      self.location.origin,
    )

    event.waitUntil(
      clients.matchAll({
        type: 'window',
        includeUncontrolled: true,
      }).then(async (windowClients) => {
        const existingClient =
          windowClients.find(
            (client) =>
              new URL(client.url).origin
              === targetUrl.origin,
          )

        if (existingClient) {
          await existingClient.navigate(
            targetUrl.href,
          )
          return existingClient.focus()
        }

        return clients.openWindow(targetUrl.href)
      }),
    )
  },
)

importScripts(
  'https://www.gstatic.com/firebasejs/12.17.0/firebase-app-compat.js',
)
importScripts(
  'https://www.gstatic.com/firebasejs/12.17.0/firebase-messaging-compat.js',
)

const parameters = new URL(
  self.location.href,
).searchParams

const firebaseConfig = {
  apiKey: parameters.get('apiKey'),
  authDomain: parameters.get('authDomain'),
  projectId: parameters.get('projectId'),
  storageBucket:
    parameters.get('storageBucket'),
  messagingSenderId:
    parameters.get('messagingSenderId'),
  appId: parameters.get('appId'),
  measurementId:
    parameters.get('measurementId'),
}

firebase.initializeApp(firebaseConfig)

const messaging = firebase.messaging()

messaging.onBackgroundMessage(
  (payload) => {
    // Notification payloads from the Firebase console are displayed
    // automatically by the FCM SDK. The backend sends data-only payloads,
    // which are rendered below.
    if (payload.notification) {
      return
    }

    const data = payload.data ?? {}

    self.registration.showNotification(
      data.title ?? 'BrainOn 알림',
      {
        body:
          data.body
          ?? '새로운 알림을 확인해주세요.',
        icon: '/brainon-notification.svg',
        badge: '/brainon-notification.svg',
        tag: data.notification_id,
        data,
      },
    )
  },
)
