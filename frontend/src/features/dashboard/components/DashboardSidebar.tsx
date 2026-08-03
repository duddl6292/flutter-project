import {
  BrainCircuit,
  CalendarDays,
  ChevronLeft,
  ClipboardCheck,
  FlaskConical,
  Handshake,
  LayoutDashboard,
  ScanLine,
  Users,
} from 'lucide-react'
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
    label: '검사 요청',
    icon: FlaskConical,
  },
  {
    label: '검사 결과',
    icon: ClipboardCheck,
  },
  {
    label: '협진 관리',
    icon: Handshake,
  },
  {
    label: 'CT 분석',
    icon: ScanLine,
  },
]

export function DashboardSidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <aside className="sidebar">
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
              item.path
              === location.pathname

            return (
              <button
                key={item.label}
                type="button"
                className={`nav-item ${
                  active
                    ? 'active'
                    : ''
                }`}
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
        >
          <ChevronLeft size={18} />
          메뉴 접기
        </button>

        <p className="copyright">
          © 2026 BrainOn.
          All rights reserved.
        </p>
      </div>
    </aside>
  )
}
