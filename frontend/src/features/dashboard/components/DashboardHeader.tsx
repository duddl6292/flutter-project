import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react'

import type {
  RefObject,
} from 'react'

import {
  Bell,
  CalendarDays,
  ChevronDown,
  LayoutDashboard,
  LogOut,
  Search,
  Users,
} from 'lucide-react'

import {
  useNavigate,
} from 'react-router-dom'

import {
  useAuthStore,
} from '../../../core/auth/authStore'

import {
  getNotifications,
  markAllNotificationsAsRead,
  markNotificationAsRead,
} from '../../notifications/notification.api'

import type {
  AppNotification,
} from '../../notifications/notification.types'

import type {
  DashboardResponse,
} from '../dashboard.types'

interface DashboardHeaderProps {
  searchInputRef:
    RefObject<HTMLInputElement | null>

  searchText:
    string

  doctor:
    DashboardResponse['doctor']

  onSearchTextChange:
    (value: string) => void

  onSearch:
    () => void

  onLogout:
    () => void
}

type OpenMenu =
  | 'notifications'
  | 'profile'
  | null

function formatNotificationTime(
  value: string,
): string {
  return new Intl.DateTimeFormat(
    'ko-KR',
    {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    },
  ).format(
    new Date(value),
  )
}

export function DashboardHeader({
  searchInputRef,
  searchText,
  doctor,
  onSearchTextChange,
  onSearch,
  onLogout,
}: DashboardHeaderProps) {
  const navigate =
    useNavigate()

  const clinician =
    useAuthStore(
      (state) =>
        state.clinician,
    )

  const menuAreaRef =
    useRef<HTMLDivElement>(null)

  const [
    openMenu,
    setOpenMenu,
  ] = useState<OpenMenu>(null)

  const [
    notifications,
    setNotifications,
  ] = useState<AppNotification[]>([])

  const [
    unreadCount,
    setUnreadCount,
  ] = useState(0)

  const [
    notificationLoading,
    setNotificationLoading,
  ] = useState(false)

  const [
    notificationError,
    setNotificationError,
  ] = useState('')

  const loadNotifications =
    useCallback(
      async () => {
        setNotificationLoading(true)
        setNotificationError('')

        try {
          const response =
            await getNotifications()

          setNotifications(
            response.data,
          )

          setUnreadCount(
            response.meta.unread_count,
          )
        } catch (error) {
          setNotificationError(
            error instanceof Error
              ? error.message
              : '알림을 불러오지 못했습니다.',
          )
        } finally {
          setNotificationLoading(false)
        }
      },
      [],
    )

  useEffect(() => {
    void loadNotifications()

    const timer =
      window.setInterval(
        () => {
          void loadNotifications()
        },
        60_000,
      )

    return () =>
      window.clearInterval(timer)
  }, [loadNotifications])

  useEffect(() => {
    const handlePointerDown = (
      event: MouseEvent,
    ) => {
      if (
        menuAreaRef.current
        && !menuAreaRef.current.contains(
          event.target as Node,
        )
      ) {
        setOpenMenu(null)
      }
    }

    const handleKeyDown = (
      event: KeyboardEvent,
    ) => {
      if (event.key === 'Escape') {
        setOpenMenu(null)
      }
    }

    document.addEventListener(
      'mousedown',
      handlePointerDown,
    )

    window.addEventListener(
      'keydown',
      handleKeyDown,
    )

    return () => {
      document.removeEventListener(
        'mousedown',
        handlePointerDown,
      )

      window.removeEventListener(
        'keydown',
        handleKeyDown,
      )
    }
  }, [])

  const handleNotificationClick =
    async (
      notification: AppNotification,
    ) => {
      let nextNotification =
        notification

      if (!notification.is_read) {
        try {
          nextNotification =
            await markNotificationAsRead(
              notification.notification_id,
            )

          setNotifications(
            (current) =>
              current.map(
                (item) =>
                  item.notification_id
                    === nextNotification
                      .notification_id
                    ? nextNotification
                    : item,
              ),
          )

          setUnreadCount(
            (current) =>
              Math.max(0, current - 1),
          )
        } catch (error) {
          setNotificationError(
            error instanceof Error
              ? error.message
              : '알림 읽음 처리에 실패했습니다.',
          )

          return
        }
      }

      const path =
        nextNotification.data.path

      setOpenMenu(null)

      if (
        typeof path === 'string'
        && path.startsWith('/')
      ) {
        navigate(path)
      }
    }

  const handleReadAll =
    async () => {
      try {
        await markAllNotificationsAsRead()

        const readAt =
          new Date().toISOString()

        setNotifications(
          (current) =>
            current.map(
              (notification) => ({
                ...notification,
                is_read: true,
                read_at:
                  notification.read_at
                  ?? readAt,
              }),
            ),
        )

        setUnreadCount(0)
      } catch (error) {
        setNotificationError(
          error instanceof Error
            ? error.message
            : '전체 읽음 처리에 실패했습니다.',
        )
      }
    }

  const moveTo = (
    path: string,
  ) => {
    setOpenMenu(null)
    navigate(path)
  }

  const avatarText =
    doctor.name.trim().charAt(0)
    || '의'

  return (
    <header className="topbar">
      <form
        className="search-box"
        onSubmit={(event) => {
          event.preventDefault()
          onSearch()
        }}
      >
        <Search size={20} />

        <input
          ref={searchInputRef}
          type="text"
          aria-label="환자 검색"
          placeholder="환자 검색 (이름, 환자ID, 전화번호)"
          value={searchText}
          onChange={(event) =>
            onSearchTextChange(
              event.target.value,
            )
          }
        />

        <button
          type="submit"
          className="header-search-button"
        >
          검색
        </button>
      </form>

      <div
        ref={menuAreaRef}
        className="topbar-actions"
      >
        <div className="header-menu-container">
          <button
            type="button"
            className="icon-button notification-button"
            aria-label="알림"
            aria-expanded={
              openMenu === 'notifications'
            }
            onClick={() => {
              setOpenMenu(
                (current) =>
                  current === 'notifications'
                    ? null
                    : 'notifications',
              )
            }}
          >
            <Bell size={21} />

            {unreadCount > 0 && (
              <span>
                {
                  unreadCount > 99
                    ? '99+'
                    : unreadCount
                }
              </span>
            )}
          </button>

          {openMenu === 'notifications' && (
            <section className="header-dropdown notification-dropdown">
              <header className="notification-dropdown-header">
                <strong>알림</strong>

                <button
                  type="button"
                  disabled={
                    unreadCount === 0
                  }
                  onClick={() => {
                    void handleReadAll()
                  }}
                >
                  모두 읽음
                </button>
              </header>

              <div className="notification-list">
                {notificationLoading
                  && notifications.length === 0
                  && (
                    <p className="header-menu-message">
                      알림을 불러오는 중입니다.
                    </p>
                  )}

                {notificationError && (
                  <p className="header-menu-error">
                    {notificationError}
                  </p>
                )}

                {!notificationLoading
                  && !notificationError
                  && notifications.length === 0
                  && (
                    <p className="header-menu-message">
                      새로운 알림이 없습니다.
                    </p>
                  )}

                {notifications.map(
                  (notification) => (
                    <button
                      type="button"
                      key={
                        notification
                          .notification_id
                      }
                      className={`notification-item${
                        notification.is_read
                          ? ''
                          : ' notification-unread'
                      }`}
                      onClick={() => {
                        void handleNotificationClick(
                          notification,
                        )
                      }}
                    >
                      <span className="notification-dot" />

                      <span className="notification-content">
                        <strong>
                          {notification.title}
                        </strong>

                        <span>
                          {notification.body}
                        </span>

                        <time>
                          {formatNotificationTime(
                            notification.created_at,
                          )}
                        </time>
                      </span>
                    </button>
                  ),
                )}
              </div>
            </section>
          )}
        </div>

        <div className="header-menu-container">
          <button
            type="button"
            className="doctor-profile"
            aria-label="의료진 메뉴"
            aria-expanded={
              openMenu === 'profile'
            }
            onClick={() =>
              setOpenMenu(
                (current) =>
                  current === 'profile'
                    ? null
                    : 'profile',
              )
            }
          >
            <div className="doctor-avatar">
              {avatarText}
            </div>

            <div className="doctor-info">
              <strong>
                {doctor.name}
              </strong>

              <span>
                {doctor.department}
                {' '}
                {doctor.title}
              </span>
            </div>

            <ChevronDown
              size={18}
              className={
                openMenu === 'profile'
                  ? 'profile-chevron-open'
                  : ''
              }
            />
          </button>

          {openMenu === 'profile' && (
            <section className="header-dropdown profile-dropdown">
              <div className="profile-dropdown-summary">
                <div className="doctor-avatar">
                  {avatarText}
                </div>

                <div>
                  <strong>
                    {doctor.name}
                  </strong>

                  <span>
                    {
                      clinician
                        ?.department_name
                      ?? doctor.department
                    }
                  </span>

                  <small>
                    {
                      clinician
                        ?.hospital_name
                      ?? '소속 병원 정보 없음'
                    }
                  </small>
                </div>
              </div>

              {clinician?.license_number && (
                <p className="profile-license">
                  면허번호
                  {' '}
                  {
                    clinician
                      .license_number
                  }
                </p>
              )}

              <nav className="profile-menu-list">
                <button
                  type="button"
                  onClick={() =>
                    moveTo('/dashboard')
                  }
                >
                  <LayoutDashboard size={17} />
                  대시보드
                </button>

                <button
                  type="button"
                  onClick={() =>
                    moveTo('/patients')
                  }
                >
                  <Users size={17} />
                  환자 관리
                </button>

                <button
                  type="button"
                  onClick={() =>
                    moveTo('/appointments')
                  }
                >
                  <CalendarDays size={17} />
                  예약 관리
                </button>
              </nav>

              <button
                type="button"
                className="profile-logout-button"
                onClick={onLogout}
              >
                <LogOut size={17} />
                로그아웃
              </button>
            </section>
          )}
        </div>
      </div>
    </header>
  )
}
