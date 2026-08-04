import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import {
  Bell,
  Mail,
  Monitor,
  Moon,
  Smartphone,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { logout } from '../../core/api/authApi'
import { useAuthStore } from '../../core/auth/authStore'
import {
  requestFcmToken,
} from '../../firebase/requestFcmToken'
import {
  DashboardHeader,
} from '../dashboard/components/DashboardHeader'
import {
  DashboardSidebar,
} from '../dashboard/components/DashboardSidebar'
import {
  getNotificationSettings,
  updateNotificationSettings,
} from './notification-settings.api'
import {
  registerWebNotificationDevice,
} from './notification-device.api'
import type {
  NotificationPreference,
  NotificationSettings,
} from './notification-settings.types'
import type {
  NotificationType,
} from './notification.types'

import '../dashboard/dashboard.css'
import './notification-settings.css'

const notificationTypeContent:
Partial<Record<
  NotificationType,
  {
    title: string
    description: string
  }
>> = {
  APPOINTMENT: {
    title: '예약 변경 알림',
    description:
      '신규 예약, 예약 일정 변경 및 예약 취소를 알려드립니다.',
  },
  TEST_RESULT: {
    title: '검사 결과 알림',
    description:
      '담당 환자의 새로운 검사 결과 등록을 알려드립니다.',
  },
  CONSULTATION: {
    title: '협진 알림',
    description:
      '협진 요청과 답변 등록을 알려드립니다.',
  },
  SYSTEM: {
    title: '시스템 알림',
    description:
      '계정, 보안 및 서비스 운영 안내를 알려드립니다.',
  },
}

type PreferenceField =
  | 'push_enabled'
  | 'email_enabled'

function Toggle({
  checked,
  disabled = false,
  label,
  onChange,
}: {
  checked: boolean
  disabled?: boolean
  label: string
  onChange: (checked: boolean) => void
}) {
  return (
    <label className="notification-toggle">
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) =>
          onChange(event.target.checked)
        }
      />

      <span aria-hidden="true" />
      <b>{label}</b>
    </label>
  )
}

export function NotificationSettingsPage() {
  const navigate = useNavigate()
  const searchInputRef =
    useRef<HTMLInputElement>(null)
  const user = useAuthStore(
    (state) => state.user,
  )
  const clinician = useAuthStore(
    (state) => state.clinician,
  )

  const [searchText, setSearchText] =
    useState('')
  const [settings, setSettings] =
    useState<NotificationSettings | null>(
      null,
    )
  const [loading, setLoading] =
    useState(true)
  const [saving, setSaving] =
    useState(false)
  const [error, setError] =
    useState('')
  const [saved, setSaved] =
    useState(false)
  const [browserConnecting, setBrowserConnecting] =
    useState(false)
  const [browserMessage, setBrowserMessage] =
    useState('')

  const browserPermission = useMemo(
    () =>
      'Notification' in window
        ? Notification.permission
        : 'unsupported',
    [browserConnecting],
  )

  const doctor = {
    name: clinician?.name ?? '의료진',
    department:
      clinician?.department_name ?? '-',
    title: '의료진',
  }

  useEffect(() => {
    const controller = new AbortController()

    const loadSettings = async () => {
      setLoading(true)
      setError('')

      try {
        const response =
          await getNotificationSettings()

        if (!controller.signal.aborted) {
          setSettings(response.data)
        }
      } catch (requestError) {
        if (!controller.signal.aborted) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : '알림 설정을 불러오지 못했습니다.',
          )
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    void loadSettings()

    return () => controller.abort()
  }, [])

  const updatePreference = (
    notificationType: NotificationType,
    field: PreferenceField,
    value: boolean,
  ) => {
    setSaved(false)
    setSettings(
      (current) =>
        current
          ? {
            ...current,
            preferences:
              current.preferences.map(
                (preference) =>
                  preference.notification_type
                    === notificationType
                    ? {
                      ...preference,
                      [field]: value,
                    }
                    : preference,
              ),
          }
          : current,
    )
  }

  const updateQuietHours = (
    changes: Partial<
      NotificationSettings['global_setting']
    >,
  ) => {
    setSaved(false)
    setSettings(
      (current) =>
        current
          ? {
            ...current,
            global_setting: {
              ...current.global_setting,
              ...changes,
            },
          }
          : current,
    )
  }

  const handleSave = async () => {
    if (!settings) {
      return
    }

    const {
      quiet_hours_enabled: enabled,
      quiet_hours_start: start,
      quiet_hours_end: end,
    } = settings.global_setting

    if (
      enabled
      && (!start || !end)
    ) {
      setError(
        '방해금지 시작 시간과 종료 시간을 모두 입력해주세요.',
      )
      return
    }

    if (
      start
      && end
      && start === end
    ) {
      setError(
        '방해금지 시작 시간과 종료 시간은 달라야 합니다.',
      )
      return
    }

    setSaving(true)
    setError('')
    setSaved(false)

    try {
      const updated =
        await updateNotificationSettings(
          settings,
        )

      setSettings(updated)
      setSaved(true)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : '알림 설정을 저장하지 못했습니다.',
      )
    } finally {
      setSaving(false)
    }
  }

  const handleConnectBrowser = async () => {
    setBrowserConnecting(true)
    setBrowserMessage('')

    try {
      const token = await requestFcmToken()

      if (!token) {
        setBrowserMessage(
          '브라우저 권한과 Firebase 설정을 확인해주세요.',
        )
        return
      }

      await registerWebNotificationDevice(
        token,
      )

      setBrowserMessage(
        '이 브라우저가 현재 계정에 연결되었습니다.',
      )
    } catch (requestError) {
      setBrowserMessage(
        requestError instanceof Error
          ? requestError.message
          : '브라우저 기기를 등록하지 못했습니다.',
      )
    } finally {
      setBrowserConnecting(false)
    }
  }

  const handlePatientSearch = () => {
    const keyword = searchText.trim()

    navigate(
      keyword
        ? `/patients?search=${
          encodeURIComponent(keyword)
        }`
        : '/patients',
    )
  }

  return (
    <div className="brainon-dashboard">
      <DashboardSidebar />

      <div className="main-area">
        <DashboardHeader
          searchInputRef={searchInputRef}
          searchText={searchText}
          doctor={doctor}
          onSearchTextChange={setSearchText}
          onSearch={handlePatientSearch}
          onLogout={() => {
            logout()
            navigate(
              '/login',
              { replace: true },
            )
          }}
        />

        <main className="notification-settings-page">
          <header className="notification-settings-heading">
            <div>
              <h1>알림 설정</h1>
              <p>
                받을 알림과 전달 채널,
                방해금지 시간을 설정합니다.
              </p>
            </div>

            <button
              type="button"
              className="notification-settings-save"
              disabled={
                loading
                || saving
                || !settings
              }
              onClick={() => {
                void handleSave()
              }}
            >
              {saving ? '저장 중' : '변경사항 저장'}
            </button>
          </header>

          {loading && (
            <p className="notification-settings-message">
              알림 설정을 불러오는 중입니다.
            </p>
          )}

          {error && (
            <p
              role="alert"
              className="notification-settings-error"
            >
              {error}
            </p>
          )}

          {saved && (
            <p
              role="status"
              className="notification-settings-success"
            >
              알림 설정을 저장했습니다.
            </p>
          )}

          {settings && (
            <div className="notification-settings-content">
              <section className="notification-settings-card">
                <header>
                  <div className="notification-settings-icon">
                    <Bell size={21} />
                  </div>

                  <div>
                    <h2>알림 종류별 설정</h2>
                    <p>
                      인앱 알림은 항상 저장되며,
                      푸시와 이메일만 선택할 수 있습니다.
                    </p>
                  </div>
                </header>

                <div className="notification-preference-table">
                  <div className="notification-preference-head">
                    <span>알림 종류</span>
                    <span>
                      <Smartphone size={15} />
                      푸시
                    </span>
                    <span>
                      <Mail size={15} />
                      이메일
                    </span>
                  </div>

                  {settings.preferences.map(
                    (preference: NotificationPreference) => {
                      const content =
                        notificationTypeContent[
                          preference.notification_type
                        ] ?? {
                          title:
                            preference.notification_type,
                          description:
                            '알림 전달 여부를 설정합니다.',
                        }

                      return (
                        <div
                          className="notification-preference-row"
                          key={preference.notification_type}
                        >
                          <div>
                            <strong>{content.title}</strong>
                            <small>{content.description}</small>
                          </div>

                          <Toggle
                            label={`${content.title} 푸시`}
                            checked={preference.push_enabled}
                            onChange={(checked) =>
                              updatePreference(
                                preference.notification_type,
                                'push_enabled',
                                checked,
                              )
                            }
                          />

                          <Toggle
                            label={`${content.title} 이메일`}
                            checked={preference.email_enabled}
                            onChange={(checked) =>
                              updatePreference(
                                preference.notification_type,
                                'email_enabled',
                                checked,
                              )
                            }
                          />
                        </div>
                      )
                    },
                  )}
                </div>
              </section>

              <section className="notification-settings-card browser-push-card">
                <header>
                  <div className="notification-settings-icon">
                    <Monitor size={21} />
                  </div>

                  <div>
                    <h2>이 브라우저 알림</h2>
                    <p>
                      현재 Chrome 브라우저를
                      FCM 푸시 알림에 연결합니다.
                    </p>
                  </div>
                </header>

                <div className="browser-push-control">
                  <div>
                    <strong>
                      상태:{' '}
                      {
                        browserPermission === 'granted'
                          ? '권한 허용됨'
                          : browserPermission === 'denied'
                            ? '권한 차단됨'
                            : browserPermission === 'unsupported'
                              ? '지원하지 않는 브라우저'
                              : '연결 전'
                      }
                    </strong>

                    {browserMessage && (
                      <small>{browserMessage}</small>
                    )}
                  </div>

                  <button
                    type="button"
                    disabled={
                      browserConnecting
                      || browserPermission
                        === 'unsupported'
                    }
                    onClick={() => {
                      void handleConnectBrowser()
                    }}
                  >
                    {
                      browserConnecting
                        ? '연결 중'
                        : browserPermission === 'granted'
                          ? '브라우저 알림 재연결'
                          : '브라우저 알림 연결'
                    }
                  </button>
                </div>
              </section>

              <section className="notification-settings-card quiet-hours-card">
                <header>
                  <div className="notification-settings-icon">
                    <Moon size={21} />
                  </div>

                  <div>
                    <h2>방해금지 모드</h2>
                    <p>
                      지정한 시간에는 푸시와 이메일을
                      보내지 않고 인앱 알림만 저장합니다.
                    </p>
                  </div>

                  <Toggle
                    label="방해금지 모드"
                    checked={
                      settings.global_setting
                        .quiet_hours_enabled
                    }
                    onChange={(checked) =>
                      updateQuietHours({
                        quiet_hours_enabled: checked,
                        quiet_hours_start:
                          checked
                            ? settings.global_setting
                              .quiet_hours_start
                              ?? '22:00'
                            : settings.global_setting
                              .quiet_hours_start,
                        quiet_hours_end:
                          checked
                            ? settings.global_setting
                              .quiet_hours_end
                              ?? '07:00'
                            : settings.global_setting
                              .quiet_hours_end,
                      })
                    }
                  />
                </header>

                <div className="quiet-hours-fields">
                  <label>
                    시작 시간
                    <input
                      type="time"
                      disabled={
                        !settings.global_setting
                          .quiet_hours_enabled
                      }
                      value={
                        settings.global_setting
                          .quiet_hours_start
                        ?? ''
                      }
                      onChange={(event) =>
                        updateQuietHours({
                          quiet_hours_start:
                            event.target.value
                            || null,
                        })
                      }
                    />
                  </label>

                  <span>부터</span>

                  <label>
                    종료 시간
                    <input
                      type="time"
                      disabled={
                        !settings.global_setting
                          .quiet_hours_enabled
                      }
                      value={
                        settings.global_setting
                          .quiet_hours_end
                        ?? ''
                      }
                      onChange={(event) =>
                        updateQuietHours({
                          quiet_hours_end:
                            event.target.value
                            || null,
                        })
                      }
                    />
                  </label>

                  <span>까지</span>
                </div>
              </section>

              <p className="notification-in-app-note">
                인앱 알림은 끌 수 없으며 모든 알림이
                상단 종 아이콘에 안전하게 저장됩니다.
                {' '}
                {user?.email
                  ? `이메일 알림 수신 주소: ${user.email}`
                  : '이메일 알림을 사용하려면 계정 이메일이 필요합니다.'}
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
