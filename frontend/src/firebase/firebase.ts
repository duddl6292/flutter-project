import {
  initializeApp,
} from 'firebase/app'
import type {
  FirebaseOptions,
} from 'firebase/app'
import {
  getAnalytics,
  isSupported as isAnalyticsSupported,
} from 'firebase/analytics'
import {
  getMessaging,
  isSupported as isMessagingSupported,
} from 'firebase/messaging'
import type {
  Messaging,
} from 'firebase/messaging'

export const firebaseConfig:
FirebaseOptions = {
  apiKey:
    import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain:
    import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId:
    import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket:
    import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId:
    import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId:
    import.meta.env.VITE_FIREBASE_APP_ID,
  measurementId:
    import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
}

const app = initializeApp(firebaseConfig)

let messagingPromise:
Promise<Messaging | null> | null = null

export function getFirebaseMessaging():
Promise<Messaging | null> {
  if (!messagingPromise) {
    messagingPromise =
      isMessagingSupported()
        .then(
          (supported) =>
            supported
              ? getMessaging(app)
              : null,
        )
  }

  return messagingPromise
}

export async function initializeAnalytics() {
  if (await isAnalyticsSupported()) {
    return getAnalytics(app)
  }

  return null
}

export default app
