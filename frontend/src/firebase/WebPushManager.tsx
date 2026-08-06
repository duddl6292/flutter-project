import {
  useCallback,
  useEffect,
  useState,
} from 'react'
import {
  Bell,
  CalendarClock,
  FlaskConical,
  Handshake,
  X,
} from 'lucide-react'
import {
  onMessage,
} from 'firebase/messaging'
import { useNavigate } from 'react-router-dom'

import {
  useAuthStore,
} from '../core/auth/authStore'
import {
  registerWebNotificationDevice,
} from '../features/notifications/notification-device.api'
import {
  getFirebaseMessaging,
} from './firebase'
import {
  registerFirebaseMessagingServiceWorker,
  requestFcmToken,
} from './requestFcmToken'

import './web-push-manager.css'

export const WEB_PUSH_NOTIFICATION_EVENT =
  'brainon:web-push-notification'

let connectionPromise: Promise<boolean> | null =
  null

async function connectWebPush(
  requestPermission: boolean,
): Promise<boolean> {
  if (connectionPromise) {
    return connectionPromise
  }

  connectionPromise = (async () => {
    const token = await requestFcmToken({
      requestPermission,
    })

    if (!token) {
      return false
    }

    await registerWebNotificationDevice(token)
    return true
  })()

  try {
    return await connectionPromise
  } finally {
    connectionPromise = null
  }
}

function getBrowserPermission():
NotificationPermission | 'unsupported' {
  if (
    typeof window === 'undefined'
    || !('Notification' in window)
  ) {
    return 'unsupported'
  }

  return Notification.permission
}

export function WebPushManager() {
  const navigate = useNavigate()
  const accessToken = useAuthStore(
    (state) => state.accessToken,
  )
  const userRole = useAuthStore(
    (state) => state.user?.role,
  )
  const [permission, setPermission] =
    useState(getBrowserPermission)
  const [connecting, setConnecting] =
    useState(false)
  const [dismissed, setDismissed] =
    useState(false)
  const [error, setError] = useState('')
  const [toast, setToast] = useState<{
    title: string
    body: string
    path: string
    type: string
  } | null>(null)

  const isClinicianSession = Boolean(
    accessToken && userRole === 'CLINICIAN',
  )

  const enableNotifications = useCallback(
    async () => {
      setConnecting(true)
      setError('')

      try {
        const connected =
          await connectWebPush(true)

        setPermission(getBrowserPermission())

        if (!connected) {
          setError(
            '브라우저 알림 권한과 Firebase 설정을 확인해주세요.',
          )
        }
      } catch (requestError) {
        setError(
          requestError instanceof Error
            ? requestError.message
            : '브라우저 알림을 연결하지 못했습니다.',
        )
      } finally {
        setConnecting(false)
      }
    },
    [],
  )

  useEffect(() => {
    if (
      !isClinicianSession
      || permission !== 'granted'
    ) {
      return
    }

    void connectWebPush(false).catch(
      (connectionError: unknown) => {
        if (import.meta.env.DEV) {
          console.warn(
            '웹 푸시 자동 연결 실패:',
            connectionError,
          )
        }
      },
    )
  }, [isClinicianSession, permission])

  useEffect(() => {
    if (!isClinicianSession) {
      return
    }

    let unsubscribe: (() => void) | undefined
    let cancelled = false

    void getFirebaseMessaging()
      .then((messaging) => {
        if (!messaging || cancelled) {
          return
        }

        unsubscribe = onMessage(
          messaging,
          (payload) => {
            const data = payload.data ?? {}

            window.dispatchEvent(
              new CustomEvent(
                WEB_PUSH_NOTIFICATION_EVENT,
                { detail: data },
              ),
            )

            setToast({
              title: data.title ?? 'BrainOn 알림',
              body: data.body ?? '새로운 알림을 확인해주세요.',
              path: data.path?.startsWith('/')
                ? data.path
                : '/dashboard',
              type: data.type ?? 'SYSTEM',
            })

            if (
              Notification.permission
              !== 'granted'
            ) {
              return
            }

            void registerFirebaseMessagingServiceWorker()
              .then((registration) =>
                registration.showNotification(
                  data.title
                    ?? 'BrainOn 알림',
                  {
                    body:
                      data.body
                      ?? '새로운 알림을 확인해주세요.',
                    icon: '/brainon-notification.svg',
                    badge: '/brainon-notification.svg',
                    tag:
                      data.notification_id,
                    data,
                  },
                ),
              )
          },
        )
      })

    return () => {
      cancelled = true
      unsubscribe?.()
    }
  }, [isClinicianSession])

  useEffect(() => {
    if (!toast) {
      return
    }

    const timerId = window.setTimeout(() => {
      setToast(null)
    }, 6_000)

    return () => window.clearTimeout(timerId)
  }, [toast])

  if (!isClinicianSession) {
    return null
  }

  const showPrompt =
    permission === 'default' && !dismissed

  const ToastIcon =
    toast?.type === 'CONSULTATION'
      ? Handshake
      : toast?.type === 'APPOINTMENT'
        ? CalendarClock
        : toast?.type === 'TEST_RESULT'
          ? FlaskConical
          : Bell

  return (
    <>
      {showPrompt && (
        <aside
          className="web-push-prompt"
          aria-label="브라우저 알림 설정"
        >
          <button
            type="button"
            className="web-push-prompt-close"
            aria-label="알림 안내 닫기"
            onClick={() => setDismissed(true)}
          >
            <X size={17} />
          </button>

          <span className="web-push-prompt-icon">
            <Bell size={21} />
          </span>

          <div>
            <strong>실시간 알림 받기</strong>
            <p>
              협진 요청과 검사 결과를 바로 알려드려요.
            </p>
            {error && <small role="alert">{error}</small>}
          </div>

          <button
            type="button"
            className="web-push-prompt-enable"
            disabled={connecting}
            onClick={() => {
              void enableNotifications()
            }}
          >
            {connecting ? '연결 중' : '알림 허용'}
          </button>
        </aside>
      )}

      {toast && (
        <aside
          className={`web-push-toast type-${toast.type.toLowerCase()}`}
          role="status"
          aria-live="polite"
        >
          <button
            type="button"
            className="web-push-toast-content"
            onClick={() => {
              const path = toast.path
              setToast(null)
              navigate(path)
            }}
          >
            <span className="web-push-toast-icon">
              <ToastIcon size={22} />
            </span>
            <span className="web-push-toast-copy">
              <small>BrainOn 실시간 알림</small>
              <strong>{toast.title}</strong>
              <span>{toast.body}</span>
            </span>
          </button>
          <button
            type="button"
            className="web-push-toast-close"
            aria-label="알림 닫기"
            onClick={() => setToast(null)}
          >
            <X size={17} />
          </button>
        </aside>
      )}
    </>
  )
}
