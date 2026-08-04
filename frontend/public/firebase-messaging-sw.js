/* global firebase */

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
    const notification =
      payload.notification

    if (!notification) {
      return
    }

    self.registration.showNotification(
      notification.title
      ?? 'BrainOn 알림',
      {
        body: notification.body ?? '',
        icon:
          notification.image
          ?? '/favicon.ico',
        data: payload.data ?? {},
      },
    )
  },
)
