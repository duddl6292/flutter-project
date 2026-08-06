import {
  CalendarDays,
  ClipboardCheck,
  Handshake,
  Stethoscope,
} from 'lucide-react'
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import { useNavigate } from 'react-router-dom'

import { logout } from '../../core/api/authApi'
import {
  getExaminations,
} from '../examinations/examination.api'
import type {
  Examination,
} from '../examinations/examination.types'
import { getDashboard } from './dashboard.api'
import type { DashboardResponse } from './dashboard.types'
import {
  ConsultationPanel,
} from './components/ConsultationPanel'
import type {
  ConsultationTab,
} from './components/ConsultationPanel'
import { DashboardHeader } from './components/DashboardHeader'
import { DashboardSidebar } from './components/DashboardSidebar'
import {
  ExaminationOverviewPanel,
} from './components/ExaminationOverviewPanel'
import { PatientPanel } from './components/PatientPanel'
import { QuickActionsPanel } from './components/QuickActionsPanel'
import { RecentActivityPanel } from './components/RecentActivityPanel'
import { SummaryCards } from './components/SummaryCards'
import type { SummaryItem } from './components/SummaryCards'
import { TodaySchedulePanel } from './components/TodaySchedulePanel'
import { WorkQueuePanel } from './components/WorkQueuePanel'
import './dashboard.css'

function toDateInputValue(date: Date): string {
  const offset = date.getTimezoneOffset() * 60_000
  return new Date(date.getTime() - offset).toISOString().slice(0, 10)
}

function shiftDate(dateValue: string, amount: number): string {
  const [year, month, day] = dateValue.split('-').map(Number)
  const date = new Date(year, month - 1, day)
  date.setDate(date.getDate() + amount)
  return toDateInputValue(date)
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}

export function DashboardPlaceholder() {
  const navigate = useNavigate()
  const today = useMemo(() => toDateInputValue(new Date()), [])
  const searchInputRef = useRef<HTMLInputElement>(null)
  const [selectedDate, setSelectedDate] = useState(today)
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null)
  const [examinations, setExaminations] = useState<Examination[]>([])
  const [searchText, setSearchText] = useState('')
  const [consultationTab, setConsultationTab] = useState<ConsultationTab>('all')
  const [dashboardLoading, setDashboardLoading] = useState(true)
  const [examinationLoading, setExaminationLoading] = useState(true)
  const [dashboardError, setDashboardError] = useState('')
  const [examinationError, setExaminationError] = useState('')

  const loadDashboard = useCallback(async (signal?: AbortSignal) => {
    setDashboardLoading(true)
    setDashboardError('')
    try {
      setDashboard(await getDashboard(selectedDate, signal))
    } catch (error) {
      if (!isAbortError(error)) {
        setDashboardError(error instanceof Error ? error.message : '대시보드 정보를 불러오지 못했습니다.')
      }
    } finally {
      if (!signal?.aborted) setDashboardLoading(false)
    }
  }, [selectedDate])

  const loadExaminations = useCallback(async (signal?: AbortSignal) => {
    setExaminationLoading(true)
    setExaminationError('')
    try {
      const response = await getExaminations({ page: 1, pageSize: 8, signal })
      setExaminations(response.data)
    } catch (error) {
      if (!isAbortError(error)) {
        setExaminationError(error instanceof Error ? error.message : '최근 검사결과를 불러오지 못했습니다.')
      }
    } finally {
      if (!signal?.aborted) setExaminationLoading(false)
    }
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    void loadDashboard(controller.signal)
    return () => controller.abort()
  }, [loadDashboard])

  useEffect(() => {
    const controller = new AbortController()
    void loadExaminations(controller.signal)
    return () => controller.abort()
  }, [loadExaminations])

  useEffect(() => {
    const focusSearch = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        searchInputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', focusSearch)
    return () => window.removeEventListener('keydown', focusSearch)
  }, [])

  const handlePatientSearch = () => {
    const keyword = searchText.trim()
    navigate(keyword ? `/patients?search=${encodeURIComponent(keyword)}` : '/patients')
  }

  const consultationCounts = useMemo(() => {
    const rows = dashboard?.consultations ?? []
    return {
      all: rows.length,
      waiting: rows.filter((row) => row.status === 'requested' || row.status === 'waiting').length,
      completed: rows.filter((row) => row.status === 'answered' || row.status === 'completed').length,
    }
  }, [dashboard])

  const filteredConsultations = useMemo(() => {
    const rows = dashboard?.consultations ?? []
    if (consultationTab === 'waiting') return rows.filter((row) => row.status === 'requested' || row.status === 'waiting')
    if (consultationTab === 'completed') return rows.filter((row) => row.status === 'answered' || row.status === 'completed')
    return rows
  }, [consultationTab, dashboard])

  const summaryItems: SummaryItem[] = useMemo(() => {
    const summary = dashboard?.summary
    const activeEncounters = (dashboard?.patients ?? []).filter((patient) => patient.status === 'waiting' || patient.status === 'in_progress').length
    const urgentResults = examinations.filter((item) => item.overall_interpretation === 'CRITICAL' || item.overall_interpretation === 'ABNORMAL').length
    return [
      {
        title: '오늘 예약', value: summary?.appointments.total ?? 0, unit: '건',
        detail: `확정 ${summary?.appointments.confirmed ?? 0} · 대기 ${summary?.appointments.waiting ?? 0}`,
        icon: CalendarDays, color: '#6157d8', background: '#f1efff',
      },
      {
        title: '진료 대기·진행', value: activeEncounters, unit: '명',
        detail: `오늘 진료 환자 ${(dashboard?.patients ?? []).length}명`,
        icon: Stethoscope, color: '#397eb6', background: '#eaf5fd',
      },
      {
        title: '미처리 협진', value: summary?.consultations.waiting ?? 0, unit: '건',
        detail: `전체 ${summary?.consultations.total ?? 0} · 완료 ${summary?.consultations.answered ?? 0}`,
        icon: Handshake, color: '#7158ca', background: '#f1edff',
      },
      {
        title: '확인할 검사결과', value: (summary?.tests.result_waiting ?? 0) + urgentResults, unit: '건',
        detail: `위험·이상 ${urgentResults} · 확정 대기 ${summary?.tests.result_waiting ?? 0}`,
        icon: ClipboardCheck, color: '#c35b54', background: '#fff0ef',
      },
    ]
  }, [dashboard, examinations])

  const doctor = dashboard?.doctor ?? { name: '의료진', department: '-', title: '전문의' }

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
          onLogout={() => { logout(); navigate('/login', { replace: true }) }}
        />

        <main className="dashboard-content dashboard-redesign">
          <header className="dashboard-welcome">
            <div><span>{selectedDate === today ? '오늘의 업무' : '선택한 날짜의 업무'}</span><h1>{doctor.name}님, 확인할 업무를 모아봤어요.</h1></div>
            <button type="button" onClick={() => navigate('/examinations?create=1')}><ClipboardCheck size={17} /> 검사결과 작성</button>
          </header>

          {dashboardError && <p className="dashboard-error" role="alert">{dashboardError}</p>}
          {examinationError && <p className="dashboard-error" role="alert">{examinationError}</p>}
          <SummaryCards items={summaryItems} loading={dashboardLoading || examinationLoading} />

          <section className="dashboard-workspace">
            <div className="dashboard-primary-column">
              <div className="dashboard-top-grid">
                <TodaySchedulePanel
                  selectedDate={selectedDate}
                  schedules={dashboard?.schedules ?? []}
                  onPreviousDate={() => setSelectedDate((value) => shiftDate(value, -1))}
                  onNextDate={() => setSelectedDate((value) => shiftDate(value, 1))}
                />
                <WorkQueuePanel
                  examinations={examinations}
                  consultations={dashboard?.consultations ?? []}
                  loading={dashboardLoading || examinationLoading}
                />
              </div>

              <PatientPanel patients={dashboard?.patients ?? []} loading={dashboardLoading} />

              <div className="dashboard-bottom-grid">
                <ConsultationPanel
                  consultations={filteredConsultations.slice(0, 5)}
                  activeTab={consultationTab}
                  counts={consultationCounts}
                  onSelect={(id) => navigate(`/consultations/${id}`)}
                  onTabChange={setConsultationTab}
                />
                <ExaminationOverviewPanel
                  examinations={examinations}
                  loading={examinationLoading}
                />
              </div>
            </div>

            <aside className="dashboard-side-column">
              <QuickActionsPanel />
              <RecentActivityPanel activities={(dashboard?.activities ?? []).filter((activity) => activity.type !== 'ct_analysis')} />
            </aside>
          </section>
        </main>
      </div>
    </div>
  )
}
