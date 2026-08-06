import {
  BrainCircuit,
  BarChart3,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  FlaskConical,
  Handshake,
  LayoutDashboard,
  Pill,
  ScanLine,
  Stethoscope,
  Users,
} from 'lucide-react'
import { useState } from 'react'
import type {
  LucideIcon,
} from 'lucide-react'
import {
  Link,
  useLocation,
  useNavigate,
} from 'react-router-dom'

interface NavigationItem {
  label: string
  icon: LucideIcon
  path?: string
  count?: number
}

const navigationItems:
NavigationItem[] = [
  {
    label: '대시보드',
    icon: LayoutDashboard,
    path: '/dashboard',
  },
  {
    label: '환자 관리',
    icon: Users,
    path: '/patients',
  },
  {
    label: '예약 관리',
    icon: CalendarDays,
    path: '/appointments',
  },
  {
    label: '진료 관리',
    icon: Stethoscope,
    path: '/encounters',
  },
  {
    label: '처방 관리',
    icon: Pill,
    path: '/prescriptions',
  },
  {
    label: '검사 결과',
    icon: ClipboardCheck,
    path: '/examinations',
  },
  {
    label: '협진 관리',
    icon: Handshake,
    path: '/consultations',
  },
  {
    label: 'CT 분석',
    icon: ScanLine,
    path: '/ct-analysis',
  },
  {
    label: '통계·리포트',
    icon: BarChart3,
    path: '/reports',
  },
]

const SIDEBAR_STORAGE_KEY = 'brainon-sidebar-collapsed'

function readInitialCollapsedState(): boolean {
  try {
    return localStorage.getItem(SIDEBAR_STORAGE_KEY) === 'true'
  } catch {
    return false
  }
}

export function DashboardSidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const [collapsed, setCollapsed] = useState(readInitialCollapsedState)

  const toggleCollapsed = () => {
    setCollapsed((current) => {
      const next = !current
      try {
        localStorage.setItem(SIDEBAR_STORAGE_KEY, String(next))
      } catch {
        // 저장소를 사용할 수 없어도 현재 화면의 접기 기능은 유지한다.
      }
      return next
    })
  }

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <Link
        className="brand"
        to="/dashboard"
        aria-label="BrainOn 홈으로 이동"
      >
        <div className="brand-icon">
          <BrainCircuit size={29} />
        </div>

        <span>BrainOn</span>
      </Link>

      <nav className="sidebar-nav">
        {navigationItems.map(
          (item) => {
            const Icon = item.icon

            const active =
              Boolean(
                item.path
                && (
                  item.path === location.pathname
                  || location.pathname.startsWith(
                    `${item.path}/`,
                  )
                )
              )

            return (
              <button
                key={item.label}
                type="button"
                className={`nav-item ${
                  active
                    ? 'active'
                    : ''
                }`}
                aria-label={item.label}
                title={collapsed ? item.label : undefined}
                onClick={() => {
                  if (item.path) {
                    navigate(item.path)
                  }
                }}
              >
                <Icon size={20} />

                <span>
                  {item.label}
                </span>

                {
                  item.count
                    !== undefined
                  && (
                    <strong className="nav-count">
                      {item.count}
                    </strong>
                  )
                }
              </button>
            )
          },
        )}
      </nav>

      <div className="sidebar-bottom">
        <button
          className="collapse-button"
          type="button"
          onClick={toggleCollapsed}
          aria-expanded={!collapsed}
          aria-label={collapsed ? '메뉴 펼치기' : '메뉴 접기'}
          title={collapsed ? '메뉴 펼치기' : '메뉴 접기'}
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          <span>{collapsed ? '메뉴 펼치기' : '메뉴 접기'}</span>
        </button>

        <p className="copyright">
          © 2026 BrainOn.
          All rights reserved.
        </p>
      </div>
    </aside>
  )
}
