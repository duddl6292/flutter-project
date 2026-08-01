import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import type {
  ChangeEvent,
  DragEvent,
  ReactNode,
} from 'react'
import type { LucideIcon } from 'lucide-react'

import {
  BrainCircuit,
  CalendarDays,
  CalendarPlus,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  FileText,
  FlaskConical,
  Handshake,
  LayoutDashboard,
  Search,
  ScanLine,
  UploadCloud,
  UserPlus,
  Users,
} from 'lucide-react'

import {
  createCtAnalysis,
  getCtHistory,
  getCtStatus,
  getDashboard,
} from './dashboard.api'
import type {
  CtHistoryItem,
  CtStatus,
  DashboardResponse,
} from './dashboard.types'
import './dashboard.css'

type BadgeTone = 'purple' | 'yellow' | 'green' | 'blue' | 'gray'
type ConsultationTab = 'all' | 'waiting' | 'completed'

interface NavigationItem {
  label: string
  icon: LucideIcon
  active?: boolean
  count?: number
}

interface SummaryItem {
  title: string
  value: number
  unit: string
  detail: string
  icon: LucideIcon
  color: string
  background: string
}

const navigationItems: NavigationItem[] = [
  { label: '대시보드', icon: LayoutDashboard, active: true },
  { label: '환자 관리', icon: Users },
  { label: '예약 관리', icon: CalendarDays },
  { label: '검사 요청', icon: FlaskConical },
  { label: '검사 결과', icon: ClipboardCheck },
  { label: '협진 관리', icon: Handshake },
  { label: 'CT 분석', icon: ScanLine },
]

const POLL_INTERVAL_MS = 1000
const MAX_POLL_COUNT = 60
const MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}

function delay(milliseconds: number, signal: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal.aborted) {
      reject(new DOMException('Aborted', 'AbortError'))
      return
    }

    const timerId = window.setTimeout(resolve, milliseconds)

    signal.addEventListener(
      'abort',
      () => {
        window.clearTimeout(timerId)
        reject(new DOMException('Aborted', 'AbortError'))
      },
      { once: true },
    )
  })
}

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

function formatDateTitle(dateValue: string): string {
  const [year, month, day] = dateValue.split('-').map(Number)
  const date = new Date(year, month - 1, day)

  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    weekday: 'short',
  }).format(date)
}

function formatDateTime(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return value || '-'

  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date)
}

function formatTime(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return value || '-'

  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(date)
}

function genderLabel(gender: string): string {
  if (gender === 'M') return '남'
  if (gender === 'F') return '여'
  return gender || '-'
}

function patientStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    scheduled: '진료 예정',
    confirmed: '예약 확정',
    waiting: '대기 중',
    in_progress: '진료 중',
    completed: '진료 완료',
    cancelled: '예약 취소',
  }

  return labels[status] ?? status
}

function patientStatusTone(status: string): BadgeTone {
  const tones: Record<string, BadgeTone> = {
    scheduled: 'purple',
    confirmed: 'blue',
    waiting: 'yellow',
    in_progress: 'green',
    completed: 'gray',
    cancelled: 'gray',
  }

  return tones[status] ?? 'gray'
}

function activityTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    medical_record: '진료 기록',
    test_result: '검사 결과',
    consultation: '협진',
    ct_analysis: 'CT 분석',
    prescription: '처방전',
  }

  return labels[type] ?? type
}

function activityTone(type: string): BadgeTone {
  const tones: Record<string, BadgeTone> = {
    medical_record: 'purple',
    test_result: 'purple',
    consultation: 'green',
    ct_analysis: 'blue',
    prescription: 'purple',
  }

  return tones[type] ?? 'gray'
}

function consultationStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    requested: '요청',
    waiting: '응답 대기',
    answered: '응답 완료',
    completed: '응답 완료',
  }

  return labels[status] ?? status
}

function consultationStatusTone(status: string): BadgeTone {
  return status === 'answered' || status === 'completed'
    ? 'green'
    : 'purple'
}

function ctStatusLabel(status: CtStatus): string {
  const labels: Record<CtStatus, string> = {
    waiting: '분석 대기',
    processing: '분석 중',
    completed: '분석 완료',
    failed: '분석 실패',
  }

  return labels[status]
}

function ctStatusTone(status: CtStatus): BadgeTone {
  const tones: Record<CtStatus, BadgeTone> = {
    waiting: 'gray',
    processing: 'yellow',
    completed: 'green',
    failed: 'gray',
  }

  return tones[status]
}

function validateCtFile(file: File): string | null {
  const name = file.name.toLowerCase()
  const supported =
    name.endsWith('.dcm') ||
    name.endsWith('.nii') ||
    name.endsWith('.nii.gz')

  if (!supported) {
    return 'DICOM(.dcm) 또는 NIfTI(.nii, .nii.gz) 파일만 업로드할 수 있습니다.'
  }

  if (file.size > MAX_FILE_SIZE) {
    return '파일 크기는 최대 2GB까지 가능합니다.'
  }

  return null
}

function StatusBadge({
  children,
  tone,
}: {
  children: ReactNode
  tone: BadgeTone
}) {
  return (
    <span className={`status-badge status-${tone}`}>
      {children}
    </span>
  )
}

function PanelTitle({
  title,
  showMore = true,
}: {
  title: string
  showMore?: boolean
}) {
  return (
    <div className="panel-title-row">
      <h2>{title}</h2>

      {showMore && (
        <button className="text-button" type="button">
          전체 보기
          <ChevronRight size={15} />
        </button>
      )}
    </div>
  )
}

export function DashboardPlaceholder() {
  const today = useMemo(() => toDateInputValue(new Date()), [])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)
  const uploadControllerRef = useRef<AbortController | null>(null)

  const [selectedDate, setSelectedDate] = useState(today)
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null)
  const [history, setHistory] = useState<CtHistoryItem[]>([])
  const [searchText, setSearchText] = useState('')
  const [consultationTab, setConsultationTab] =
    useState<ConsultationTab>('all')
  const [selectedPatientId, setSelectedPatientId] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dashboardLoading, setDashboardLoading] = useState(true)
  const [historyLoading, setHistoryLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [currentCtStatus, setCurrentCtStatus] = useState<CtStatus | null>(null)
  const [currentCtProgress, setCurrentCtProgress] = useState(0)
  const [dashboardError, setDashboardError] = useState('')
  const [historyError, setHistoryError] = useState('')
  const [uploadError, setUploadError] = useState('')

  const loadDashboard = useCallback(
    async (signal?: AbortSignal) => {
      setDashboardLoading(true)
      setDashboardError('')

      try {
        const data = await getDashboard(selectedDate, signal)
        setDashboard(data)

        setSelectedPatientId((current) => {
          if (
            current &&
            data.patients.some((patient) => patient.patient_id === current)
          ) {
            return current
          }

          return data.patients[0]?.patient_id ?? ''
        })
      } catch (error) {
        if (!isAbortError(error)) {
          setDashboardError(
            error instanceof Error
              ? error.message
              : '대시보드 데이터를 불러오지 못했습니다.',
          )
        }
      } finally {
        if (!signal?.aborted) setDashboardLoading(false)
      }
    },
    [selectedDate],
  )

  const loadHistory = useCallback(async (signal?: AbortSignal) => {
    setHistoryLoading(true)
    setHistoryError('')

    try {
      const data = await getCtHistory(4, signal)
      setHistory(data.results)
    } catch (error) {
      if (!isAbortError(error)) {
        setHistoryError(
          error instanceof Error
            ? error.message
            : '최근 CT 분석 이력을 불러오지 못했습니다.',
        )
      }
    } finally {
      if (!signal?.aborted) setHistoryLoading(false)
    }
  }, [])

  useEffect(() => {
    const controller = new AbortController()

    void loadDashboard(controller.signal)
    void loadHistory(controller.signal)

    return () => controller.abort()
  }, [loadDashboard, loadHistory])

  useEffect(() => {
    const handleShortcut = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        searchInputRef.current?.focus()
      }
    }

    window.addEventListener('keydown', handleShortcut)
    return () => window.removeEventListener('keydown', handleShortcut)
  }, [])

  useEffect(() => {
    return () => uploadControllerRef.current?.abort()
  }, [])

  const summaryItems: SummaryItem[] = useMemo(() => {
    const summary = dashboard?.summary

    return [
      {
        title: '오늘 예약',
        value: summary?.appointments.total ?? 0,
        unit: '건',
        detail: `확정 ${summary?.appointments.confirmed ?? 0}  |  대기 ${summary?.appointments.waiting ?? 0}`,
        icon: CalendarDays,
        color: '#6157d8',
        background: '#f1efff',
      },
      {
        title: '협진 요청',
        value: summary?.consultations.total ?? 0,
        unit: '건',
        detail: `대기 ${summary?.consultations.waiting ?? 0}  |  응답 ${summary?.consultations.answered ?? 0}`,
        icon: Users,
        color: '#675ad7',
        background: '#f2efff',
      },
      {
        title: '검사 대기',
        value: summary?.tests.total ?? 0,
        unit: '건',
        detail: `검사 중 ${summary?.tests.processing ?? 0}  |  결과 대기 ${summary?.tests.result_waiting ?? 0}`,
        icon: FlaskConical,
        color: '#4f9dd5',
        background: '#edf8ff',
      },
      {
        title: 'CT 분석 요청',
        value: summary?.ct_analyses.total ?? 0,
        unit: '건',
        detail: `분석 중 ${summary?.ct_analyses.processing ?? 0}  |  결과 완료 ${summary?.ct_analyses.completed ?? 0}`,
        icon: ScanLine,
        color: '#51b78a',
        background: '#eaf9f1',
      },
    ]
  }, [dashboard])

  const filteredPatients = useMemo(() => {
    const keyword = searchText.trim().toLowerCase()
    const patients = dashboard?.patients ?? []

    if (!keyword) return patients

    return patients.filter((patient) =>
      [patient.patient_id, patient.name, patient.phone ?? '']
        .join(' ')
        .toLowerCase()
        .includes(keyword),
    )
  }, [dashboard, searchText])

  const consultationCounts = useMemo(() => {
    const rows = dashboard?.consultations ?? []

    return {
      all: rows.length,
      waiting: rows.filter(
        (row) => row.status === 'requested' || row.status === 'waiting',
      ).length,
      completed: rows.filter(
        (row) => row.status === 'answered' || row.status === 'completed',
      ).length,
    }
  }, [dashboard])

  const filteredConsultations = useMemo(() => {
    const rows = dashboard?.consultations ?? []

    if (consultationTab === 'waiting') {
      return rows.filter(
        (row) => row.status === 'requested' || row.status === 'waiting',
      )
    }

    if (consultationTab === 'completed') {
      return rows.filter(
        (row) => row.status === 'answered' || row.status === 'completed',
      )
    }

    return rows
  }, [consultationTab, dashboard])

  const pollCtStatus = async (
    ctId: string | number,
    signal: AbortSignal,
  ) => {
    for (let count = 0; count < MAX_POLL_COUNT; count += 1) {
      const result = await getCtStatus(ctId, signal)
      setCurrentCtStatus(result.status)
      setCurrentCtProgress(result.progress)

      if (result.status === 'completed') return

      if (result.status === 'failed') {
        throw new Error(result.error_message || 'CT 분석에 실패했습니다.')
      }

      await delay(POLL_INTERVAL_MS, signal)
    }

    throw new Error('CT 분석 시간이 초과되었습니다.')
  }

  const uploadCtFile = async (file: File) => {
    const validationError = validateCtFile(file)

    if (validationError) {
      setUploadError(validationError)
      return
    }

    if (!selectedPatientId) {
      setUploadError('CT를 등록할 환자를 먼저 선택해주세요.')
      return
    }

    uploadControllerRef.current?.abort()
    const controller = new AbortController()
    uploadControllerRef.current = controller

    setSelectedFile(file)
    setUploading(true)
    setCurrentCtStatus('waiting')
    setCurrentCtProgress(0)
    setUploadError('')

    try {
      const created = await createCtAnalysis(
        file,
        selectedPatientId,
        controller.signal,
      )

      setCurrentCtStatus(created.status)
      setCurrentCtProgress(created.progress)

      await pollCtStatus(created.ct_id, controller.signal)
      await Promise.all([
        loadHistory(controller.signal),
        loadDashboard(controller.signal),
      ])
    } catch (error) {
      if (!isAbortError(error)) {
        setUploadError(
          error instanceof Error
            ? error.message
            : 'CT 파일 업로드 중 오류가 발생했습니다.',
        )
      }
    } finally {
      if (!controller.signal.aborted) setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) void uploadCtFile(file)
  }

  const handleDrop = (event: DragEvent<HTMLButtonElement>) => {
    event.preventDefault()
    const file = event.dataTransfer.files?.[0]
    if (file) void uploadCtFile(file)
  }

  const doctor = dashboard?.doctor ?? {
    name: '김의사',
    department: '신경외과',
    title: '전문의',
  }

  return (
    <div className="brainon-dashboard">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <BrainCircuit size={29} />
          </div>
          <span>BrainOn</span>
        </div>

        <nav className="sidebar-nav">
          {navigationItems.map((item) => {
            const Icon = item.icon

            return (
              <button
                key={item.label}
                type="button"
                className={`nav-item ${item.active ? 'active' : ''}`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
                {item.count !== undefined && (
                  <strong className="nav-count">{item.count}</strong>
                )}
              </button>
            )
          })}
        </nav>

        <div className="sidebar-bottom">
          <button className="collapse-button" type="button">
            <ChevronLeft size={18} />
            메뉴 접기
          </button>
          <p className="copyright">© 2026 BrainOn. All rights reserved.</p>
        </div>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <div className="search-box">
            <Search size={20} />
            <input
              ref={searchInputRef}
              type="text"
              aria-label="환자 검색"
              placeholder="환자 검색 (이름, 환자ID, 전화번호)"
              value={searchText}
              onChange={(event: ChangeEvent<HTMLInputElement>) => setSearchText(event.target.value)}
            />
            <kbd>Ctrl K</kbd>
          </div>

          <div className="topbar-actions">
            <div className="doctor-profile">
              <div className="doctor-avatar">의</div>
              <div className="doctor-info">
                <strong>{doctor.name}</strong>
                <span>{doctor.department} {doctor.title}</span>
              </div>
              <ChevronDown size={18} />
            </div>
          </div>
        </header>

        <main className="dashboard-content">
          {dashboardError && (
            <p role="alert" style={{ color: '#b42318' }}>
              {dashboardError}
            </p>
          )}

          <section className="summary-grid">
            {summaryItems.map((item) => {
              const Icon = item.icon

              return (
                <article className="summary-card" key={item.title}>
                  <div
                    className="summary-icon"
                    style={{
                      color: item.color,
                      backgroundColor: item.background,
                    }}
                  >
                    <Icon size={34} />
                  </div>

                  <div>
                    <h3>{item.title}</h3>
                    <div className="summary-value">
                      <strong>{dashboardLoading ? '-' : item.value}</strong>
                      <span>{item.unit}</span>
                    </div>
                    <p>{dashboardLoading ? '불러오는 중' : item.detail}</p>
                  </div>
                </article>
              )
            })}
          </section>

          <section className="dashboard-grid">
            <div className="left-column">
              <article className="dashboard-panel patient-panel">
                <PanelTitle title="오늘 진료 환자" />
                <div className="table-wrapper">
                  <table className="patient-table">
                    <thead>
                      <tr>
                        <th>환자 ID</th>
                        <th>이름</th>
                        <th>나이</th>
                        <th>성별</th>
                        <th>진료과</th>
                        <th>최근 예약일</th>
                        <th>상태</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredPatients.map((patient) => (
                        <tr key={patient.patient_id}>
                          <td className="patient-id">{patient.patient_id}</td>
                          <td>{patient.name}</td>
                          <td>{patient.age}</td>
                          <td>{genderLabel(patient.gender)}</td>
                          <td>{patient.department}</td>
                          <td>{formatDateTime(patient.appointment_at)}</td>
                          <td>
                            <StatusBadge tone={patientStatusTone(patient.status)}>
                              {patientStatusLabel(patient.status)}
                            </StatusBadge>
                          </td>
                        </tr>
                      ))}

                      {!dashboardLoading && filteredPatients.length === 0 && (
                        <tr>
                          <td colSpan={7} style={{ textAlign: 'center' }}>
                            표시할 환자가 없습니다.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </article>

              <div className="bottom-grid">
                <article className="dashboard-panel">
                  <PanelTitle title="협진 요청 현황" />
                  <div className="consult-tabs">
                    <button
                      className={consultationTab === 'all' ? 'active' : ''}
                      type="button"
                      onClick={() => setConsultationTab('all')}
                    >
                      전체 ({consultationCounts.all})
                    </button>
                    <button
                      className={consultationTab === 'waiting' ? 'active' : ''}
                      type="button"
                      onClick={() => setConsultationTab('waiting')}
                    >
                      응답 대기 ({consultationCounts.waiting})
                    </button>
                    <button
                      className={consultationTab === 'completed' ? 'active' : ''}
                      type="button"
                      onClick={() => setConsultationTab('completed')}
                    >
                      응답 완료 ({consultationCounts.completed})
                    </button>
                  </div>

                  <div className="consult-list">
                    {filteredConsultations.map((request) => (
                      <div className="consult-item" key={request.consultation_id}>
                        <div className="consult-badges">
                          <StatusBadge tone={consultationStatusTone(request.status)}>
                            {consultationStatusLabel(request.status)}
                          </StatusBadge>
                          <StatusBadge tone="blue">{request.department}</StatusBadge>
                        </div>
                        <strong>{request.title}</strong>
                        <div className="consult-meta">
                          <span>{request.patient_display}</span>
                          <span>{formatDateTime(request.responded_at ?? request.requested_at)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </article>

                <article className="dashboard-panel ct-panel">
                  <PanelTitle title="CT 분석 요청 및 결과" />
                  <p className="section-caption">새로운 CT 분석 요청</p>

                  <select
                    aria-label="CT 분석 대상 환자"
                    value={selectedPatientId}
                    onChange={(event: ChangeEvent<HTMLSelectElement>) => setSelectedPatientId(event.target.value)}
                    disabled={dashboardLoading || uploading}
                    style={{
                      width: '100%',
                      minHeight: 42,
                      marginBottom: 12,
                      padding: '0 12px',
                      border: '1px solid #d9dce5',
                      borderRadius: 10,
                      background: '#fff',
                    }}
                  >
                    <option value="">환자를 선택해주세요</option>
                    {(dashboard?.patients ?? []).map((patient) => (
                      <option key={patient.patient_id} value={patient.patient_id}>
                        {patient.patient_id} · {patient.name}
                      </option>
                    ))}
                  </select>

                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".dcm,.nii,.nii.gz"
                    hidden
                    onChange={handleFileChange}
                  />

                  <button
                    className="upload-box"
                    type="button"
                    disabled={uploading || !selectedPatientId}
                    onClick={() => fileInputRef.current?.click()}
                    onDragOver={(event: DragEvent<HTMLButtonElement>) => event.preventDefault()}
                    onDrop={handleDrop}
                  >
                    <UploadCloud size={35} />
                    <div>
                      <strong>
                        {uploading
                          ? `${currentCtStatus ? ctStatusLabel(currentCtStatus) : '업로드 중'} (${currentCtProgress}%)`
                          : selectedFile?.name ?? 'CT 파일을 끌어오거나 클릭하여 업로드'}
                      </strong>
                      <span>지원 형식: DICOM (.dcm), NIfTI (.nii, .nii.gz)</span>
                    </div>
                    <span className="file-button">
                      {uploading ? '분석 진행 중' : '파일 선택'}
                    </span>
                  </button>

                  {uploading && (
                    <progress
                      value={currentCtProgress}
                      max={100}
                      style={{ width: '100%', marginTop: 10 }}
                    />
                  )}

                  {uploadError && (
                    <p role="alert" className="upload-error" style={{ color: '#b42318' }}>
                      {uploadError}
                    </p>
                  )}

                  <p className="section-caption recent-caption">최근 분석 결과</p>

                  {historyError && (
                    <p role="alert" style={{ color: '#b42318' }}>
                      {historyError}
                    </p>
                  )}

                  <div className="ct-result-list">
                    {history.map((result) => (
                      <div className="ct-result-item" key={String(result.ct_id)}>
                        <strong>{result.display_id}</strong>
                        <span>
                          {result.patient_name} ({genderLabel(result.gender)}/{result.age})
                        </span>
                        <StatusBadge tone={ctStatusTone(result.status)}>
                          {ctStatusLabel(result.status)}
                        </StatusBadge>
                        <time>{formatDateTime(result.created_at)}</time>
                      </div>
                    ))}

                    {!historyLoading && history.length === 0 && (
                      <p style={{ textAlign: 'center' }}>최근 CT 분석 이력이 없습니다.</p>
                    )}
                  </div>
                </article>
              </div>
            </div>

            <div className="middle-column">
              <article className="dashboard-panel activity-panel">
                <PanelTitle title="최근 활동" />
                <div className="activity-list">
                  {(dashboard?.activities ?? []).map((activity) => (
                    <div className="activity-item" key={activity.activity_id}>
                      <time>{formatTime(activity.occurred_at)}</time>
                      <div className="activity-line">
                        <span className={`activity-dot ${activityTone(activity.type)}`} />
                      </div>
                      <p>{activity.message}</p>
                      <StatusBadge tone={activityTone(activity.type)}>
                        {activityTypeLabel(activity.type)}
                      </StatusBadge>
                    </div>
                  ))}
                </div>
              </article>
            </div>

            <aside className="right-column">
              <article className="dashboard-panel schedule-panel">
                <div className="schedule-header">
                  <h2>오늘 일정</h2>
                  <div className="schedule-date">
                    <span>{formatDateTitle(selectedDate)}</span>
                    <button
                      type="button"
                      aria-label="이전 날짜"
                      onClick={() => setSelectedDate((value) => shiftDate(value, -1))}
                    >
                      <ChevronLeft size={17} />
                    </button>
                    <button
                      type="button"
                      aria-label="다음 날짜"
                      onClick={() => setSelectedDate((value) => shiftDate(value, 1))}
                    >
                      <ChevronRight size={17} />
                    </button>
                  </div>
                </div>

                <div className="schedule-list">
                  {(dashboard?.schedules ?? []).map((item) => (
                    <div
                      key={item.schedule_id}
                      className={`schedule-item ${item.status === 'in_progress' ? 'current' : ''}`}
                    >
                      <time>{formatTime(item.start_at)}</time>
                      <div className="schedule-card">
                        <strong>{item.patient_name} 진료</strong>
                        <span>{item.room}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </article>

              <article className="dashboard-panel quick-panel">
                <h2>빠른 실행</h2>
                <div className="quick-grid">
                  <button type="button"><UserPlus size={26} /><span>환자 등록</span></button>
                  <button type="button"><CalendarPlus size={26} /><span>예약 등록</span></button>
                  <button type="button"><FileText size={26} /><span>처방전 작성</span></button>
                  <button type="button"><ClipboardCheck size={26} /><span>검사 결과 작성</span></button>
                </div>
              </article>
            </aside>
          </section>
        </main>
      </div>
    </div>
  )
}
