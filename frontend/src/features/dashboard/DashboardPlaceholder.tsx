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
} from 'react'
import {
  CalendarDays,
  FlaskConical,
  ScanLine,
  Users,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { logout } from '../../core/api/authApi'
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
import {
  ConsultationPanel,
} from './components/ConsultationPanel'
import type {
  ConsultationTab,
} from './components/ConsultationPanel'
import {
  CtAnalysisPanel,
} from './components/CtAnalysisPanel'
import {
  DashboardHeader,
} from './components/DashboardHeader'
import {
  DashboardSidebar,
} from './components/DashboardSidebar'
import {
  PatientPanel,
} from './components/PatientPanel'
import {
  QuickActionsPanel,
} from './components/QuickActionsPanel'
import {
  RecentActivityPanel,
} from './components/RecentActivityPanel'
import {
  SummaryCards,
} from './components/SummaryCards'
import type {
  SummaryItem,
} from './components/SummaryCards'
import {
  TodaySchedulePanel,
} from './components/TodaySchedulePanel'
import './dashboard.css'

const POLL_INTERVAL_MS = 1000
const MAX_POLL_COUNT = 60
const MAX_FILE_SIZE =
  2 * 1024 * 1024 * 1024

function isAbortError(
  error: unknown,
): boolean {
  return error instanceof DOMException
    && error.name === 'AbortError'
}

function delay(
  milliseconds: number,
  signal: AbortSignal,
): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal.aborted) {
      reject(
        new DOMException(
          'Aborted',
          'AbortError',
        ),
      )
      return
    }

    const timerId = window.setTimeout(
      resolve,
      milliseconds,
    )

    signal.addEventListener(
      'abort',
      () => {
        window.clearTimeout(timerId)
        reject(
          new DOMException(
            'Aborted',
            'AbortError',
          ),
        )
      },
      { once: true },
    )
  })
}

function toDateInputValue(
  date: Date,
): string {
  const offset =
    date.getTimezoneOffset() * 60_000

  return new Date(
    date.getTime() - offset,
  )
    .toISOString()
    .slice(0, 10)
}

function shiftDate(
  dateValue: string,
  amount: number,
): string {
  const [year, month, day] =
    dateValue.split('-').map(Number)
  const date = new Date(
    year,
    month - 1,
    day,
  )

  date.setDate(date.getDate() + amount)
  return toDateInputValue(date)
}

function validateCtFile(
  file: File,
): string | null {
  const name = file.name.toLowerCase()
  const supported =
    name.endsWith('.dcm')
    || name.endsWith('.nii')
    || name.endsWith('.nii.gz')

  if (!supported) {
    return 'DICOM(.dcm) 또는 NIfTI(.nii, .nii.gz) 파일만 업로드할 수 있습니다.'
  }

  if (file.size > MAX_FILE_SIZE) {
    return '파일 크기는 최대 2GB까지 가능합니다.'
  }

  return null
}

export function DashboardPlaceholder() {
  const navigate = useNavigate()
  const today = useMemo(
    () => toDateInputValue(new Date()),
    [],
  )
  const fileInputRef =
    useRef<HTMLInputElement>(null)
  const searchInputRef =
    useRef<HTMLInputElement>(null)
  const uploadControllerRef =
    useRef<AbortController | null>(null)

  const [selectedDate, setSelectedDate] =
    useState(today)
  const [dashboard, setDashboard] =
    useState<DashboardResponse | null>(null)
  const [history, setHistory] =
    useState<CtHistoryItem[]>([])
  const [searchText, setSearchText] =
    useState('')
  const [consultationTab, setConsultationTab] =
    useState<ConsultationTab>('all')
  const [selectedPatientId, setSelectedPatientId] =
    useState('')
  const [selectedFile, setSelectedFile] =
    useState<File | null>(null)
  const [dashboardLoading, setDashboardLoading] =
    useState(true)
  const [historyLoading, setHistoryLoading] =
    useState(true)
  const [uploading, setUploading] =
    useState(false)
  const [currentCtStatus, setCurrentCtStatus] =
    useState<CtStatus | null>(null)
  const [currentCtProgress, setCurrentCtProgress] =
    useState(0)
  const [dashboardError, setDashboardError] =
    useState('')
  const [historyError, setHistoryError] =
    useState('')
  const [uploadError, setUploadError] =
    useState('')

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }
  const handlePatientSearch = () => {
    const keyword =
      searchText.trim()

    if (!keyword) {
      navigate('/patients')
      return
    }

    navigate(
      `/patients?search=${
        encodeURIComponent(keyword)
      }`,
    )
  }


  const loadDashboard = useCallback(
    async (signal?: AbortSignal) => {
      setDashboardLoading(true)
      setDashboardError('')

      try {
        const data = await getDashboard(
          selectedDate,
          signal,
        )

        setDashboard(data)
        setSelectedPatientId((current) => {
          if (
            current
            && data.patients.some(
              (patient) =>
                patient.patient_id === current,
            )
          ) {
            return current
          }

          return data.patients[0]?.patient_id
            ?? ''
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
        if (!signal?.aborted) {
          setDashboardLoading(false)
        }
      }
    },
    [selectedDate],
  )

  const loadHistory = useCallback(
    async (signal?: AbortSignal) => {
      setHistoryLoading(true)
      setHistoryError('')

      try {
        const data = await getCtHistory(
          4,
          signal,
        )
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
        if (!signal?.aborted) {
          setHistoryLoading(false)
        }
      }
    },
    [],
  )

  useEffect(() => {
    const controller = new AbortController()

    void loadDashboard(controller.signal)
    void loadHistory(controller.signal)

    return () => controller.abort()
  }, [loadDashboard, loadHistory])

  useEffect(() => {
    const handleShortcut = (
      event: KeyboardEvent,
    ) => {
      if (
        (event.ctrlKey || event.metaKey)
        && event.key.toLowerCase() === 'k'
      ) {
        event.preventDefault()
        searchInputRef.current?.focus()
      }
    }

    window.addEventListener(
      'keydown',
      handleShortcut,
    )

    return () => window.removeEventListener(
      'keydown',
      handleShortcut,
    )
  }, [])

  useEffect(() => {
    return () =>
      uploadControllerRef.current?.abort()
  }, [])

  const summaryItems: SummaryItem[] =
    useMemo(() => {
      const summary = dashboard?.summary

      return [
        {
          title: '오늘 예약',
          value:
            summary?.appointments.total ?? 0,
          unit: '건',
          detail: `확정 ${
            summary?.appointments.confirmed ?? 0
          }  |  대기 ${
            summary?.appointments.waiting ?? 0
          }`,
          icon: CalendarDays,
          color: '#6157d8',
          background: '#f1efff',
        },
        {
          title: '협진 요청',
          value:
            summary?.consultations.total ?? 0,
          unit: '건',
          detail: `대기 ${
            summary?.consultations.waiting ?? 0
          }  |  응답 ${
            summary?.consultations.answered ?? 0
          }`,
          icon: Users,
          color: '#675ad7',
          background: '#f2efff',
        },
        {
          title: '검사 대기',
          value: summary?.tests.total ?? 0,
          unit: '건',
          detail: `검사 중 ${
            summary?.tests.processing ?? 0
          }  |  결과 대기 ${
            summary?.tests.result_waiting ?? 0
          }`,
          icon: FlaskConical,
          color: '#4f9dd5',
          background: '#edf8ff',
        },
        {
          title: 'CT 분석 요청',
          value:
            summary?.ct_analyses.total ?? 0,
          unit: '건',
          detail: `분석 중 ${
            summary?.ct_analyses.processing ?? 0
          }  |  결과 완료 ${
            summary?.ct_analyses.completed ?? 0
          }`,
          icon: ScanLine,
          color: '#51b78a',
          background: '#eaf9f1',
        },
      ]
    }, [dashboard])

  const consultationCounts = useMemo(() => {
    const rows =
      dashboard?.consultations ?? []

    return {
      all: rows.length,
      waiting: rows.filter(
        (row) =>
          row.status === 'requested'
          || row.status === 'waiting',
      ).length,
      completed: rows.filter(
        (row) =>
          row.status === 'answered'
          || row.status === 'completed',
      ).length,
    }
  }, [dashboard])

  const filteredConsultations = useMemo(() => {
    const rows =
      dashboard?.consultations ?? []

    if (consultationTab === 'waiting') {
      return rows.filter(
        (row) =>
          row.status === 'requested'
          || row.status === 'waiting',
      )
    }

    if (consultationTab === 'completed') {
      return rows.filter(
        (row) =>
          row.status === 'answered'
          || row.status === 'completed',
      )
    }

    return rows
  }, [consultationTab, dashboard])

  const pollCtStatus = async (
    ctId: string | number,
    signal: AbortSignal,
  ) => {
    for (
      let count = 0;
      count < MAX_POLL_COUNT;
      count += 1
    ) {
      const result = await getCtStatus(
        ctId,
        signal,
      )

      setCurrentCtStatus(result.status)
      setCurrentCtProgress(result.progress)

      if (result.status === 'completed') {
        return
      }

      if (result.status === 'failed') {
        throw new Error(
          result.error_message
          || 'CT 분석에 실패했습니다.',
        )
      }

      await delay(POLL_INTERVAL_MS, signal)
    }

    throw new Error(
      'CT 분석 시간이 초과되었습니다.',
    )
  }

  const uploadCtFile = async (file: File) => {
    const validationError =
      validateCtFile(file)

    if (validationError) {
      setUploadError(validationError)
      return
    }

    if (!selectedPatientId) {
      setUploadError(
        'CT를 등록할 환자를 먼저 선택해주세요.',
      )
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

      await pollCtStatus(
        created.ct_id,
        controller.signal,
      )
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
      if (!controller.signal.aborted) {
        setUploading(false)
      }

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleFileChange = (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0]

    if (file) {
      void uploadCtFile(file)
    }
  }

  const handleDrop = (
    event: DragEvent<HTMLButtonElement>,
  ) => {
    event.preventDefault()
    const file = event.dataTransfer.files?.[0]

    if (file) {
      void uploadCtFile(file)
    }
  }

  const doctor = dashboard?.doctor ?? {
    name: '김의사',
    department: '신경외과',
    title: '전문의',
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
          onLogout={handleLogout}
        />

        <main className="dashboard-content">
          {dashboardError && (
            <p
              role="alert"
              style={{ color: '#b42318' }}
            >
              {dashboardError}
            </p>
          )}

          <SummaryCards
            items={summaryItems}
            loading={dashboardLoading}
          />

          <section className="dashboard-grid">
            <div className="left-column">
              <PatientPanel
                patients={
                  dashboard?.patients ?? []
                }
                loading={dashboardLoading}
              />

              <div className="bottom-grid">
                <ConsultationPanel
                  consultations={
                    filteredConsultations
                  }
                  activeTab={consultationTab}
                  counts={consultationCounts}
                  onTabChange={
                    setConsultationTab
                  }
                />

                <CtAnalysisPanel
                  patients={
                    dashboard?.patients ?? []
                  }
                  history={history}
                  selectedPatientId={
                    selectedPatientId
                  }
                  selectedFile={selectedFile}
                  currentStatus={currentCtStatus}
                  currentProgress={
                    currentCtProgress
                  }
                  dashboardLoading={
                    dashboardLoading
                  }
                  historyLoading={historyLoading}
                  uploading={uploading}
                  uploadError={uploadError}
                  historyError={historyError}
                  fileInputRef={fileInputRef}
                  onPatientChange={
                    setSelectedPatientId
                  }
                  onFileChange={handleFileChange}
                  onDrop={handleDrop}
                />
              </div>
            </div>

            <div className="middle-column">
              <RecentActivityPanel
                activities={
                  dashboard?.activities ?? []
                }
              />
            </div>

            <aside className="right-column">
              <TodaySchedulePanel
                selectedDate={selectedDate}
                schedules={
                  dashboard?.schedules ?? []
                }
                onPreviousDate={() =>
                  setSelectedDate((value) =>
                    shiftDate(value, -1),
                  )
                }
                onNextDate={() =>
                  setSelectedDate((value) =>
                    shiftDate(value, 1),
                  )
                }
              />

              <QuickActionsPanel />
            </aside>
          </section>
        </main>
      </div>
    </div>
  )
}
