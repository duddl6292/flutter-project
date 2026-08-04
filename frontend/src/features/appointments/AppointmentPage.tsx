import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import { useNavigate } from 'react-router-dom'

import { logout } from '../../core/api/authApi'
import { useAuthStore } from '../../core/auth/authStore'
import {
  DashboardHeader,
} from '../dashboard/components/DashboardHeader'
import {
  DashboardSidebar,
} from '../dashboard/components/DashboardSidebar'
import { getPatients } from '../patients/patient.api'
import type {
  PatientSummary,
} from '../patients/patient.types'
import {
  cancelAppointment,
  createAppointment,
  getAppointments,
  updateAppointment,
} from './appointment.api'
import {
  APPOINTMENT_CALENDAR_START_HOUR,
} from './appointment.constants'
import {
  AppointmentCalendar,
} from './AppointmentCalendar'
import {
  AppointmentCreateModal,
} from './AppointmentCreateModal'
import {
  AppointmentDetailModal,
} from './AppointmentDetailModal'
import type {
  Appointment,
  AppointmentCreateInput,
  AppointmentStatus,
  AppointmentUpdateInput,
} from './appointment.types'

import '../dashboard/dashboard.css'
import './appointments.css'

function toDateKey(date: Date): string {
  const offset =
    date.getTimezoneOffset() * 60_000

  return new Date(
    date.getTime() - offset,
  )
    .toISOString()
    .slice(0, 10)
}

function toLocalDateTimeInput(
  date: Date,
): string {
  const offset =
    date.getTimezoneOffset() * 60_000

  return new Date(
    date.getTime() - offset,
  )
    .toISOString()
    .slice(0, 16)
}

function startOfWeek(date: Date): Date {
  const result = new Date(date)
  const day = result.getDay()
  const distanceFromMonday =
    day === 0 ? -6 : 1 - day

  result.setDate(
    result.getDate()
    + distanceFromMonday,
  )
  result.setHours(0, 0, 0, 0)

  return result
}

function addDays(
  date: Date,
  amount: number,
): Date {
  const result = new Date(date)
  result.setDate(result.getDate() + amount)
  return result
}

function sortAppointments(
  appointments: Appointment[],
): Appointment[] {
  return [...appointments].sort(
    (left, right) =>
      new Date(left.scheduled_at).getTime()
      - new Date(right.scheduled_at).getTime(),
  )
}

function hasConflict(
  appointments: Appointment[],
  input: AppointmentUpdateInput,
  excludedAppointmentId?: string,
): boolean {
  const requestedStart =
    new Date(input.scheduled_at).getTime()
  const requestedEnd =
    requestedStart
    + input.duration_minutes * 60_000

  return appointments.some(
    (appointment) => {
      if (
        appointment.appointment_id
          === excludedAppointmentId
        || [
          'CANCELLED',
          'NO_SHOW',
        ].includes(appointment.status)
      ) {
        return false
      }

      const existingStart =
        new Date(
          appointment.scheduled_at,
        ).getTime()
      const existingEnd =
        existingStart
        + appointment.duration_minutes
          * 60_000

      return (
        requestedStart < existingEnd
        && requestedEnd > existingStart
      )
    },
  )
}

export function AppointmentPage() {
  const navigate = useNavigate()
  const searchInputRef =
    useRef<HTMLInputElement>(null)
  const clinician = useAuthStore(
    (state) => state.clinician,
  )

  const [searchText, setSearchText] =
    useState('')
  const [selectedDate, setSelectedDate] =
    useState(new Date())
  const [appointments, setAppointments] =
    useState<Appointment[]>([])
  const [patients, setPatients] =
    useState<PatientSummary[]>([])
  const [statusFilter, setStatusFilter] =
    useState<AppointmentStatus | ''>('')
  const [loading, setLoading] =
    useState(true)
  const [error, setError] =
    useState('')

  const [createModalOpen, setCreateModalOpen] =
    useState(false)
  const [createInitialDateTime, setCreateInitialDateTime] =
    useState('')
  const [selectedAppointment, setSelectedAppointment] =
    useState<Appointment | null>(null)
  const [saving, setSaving] =
    useState(false)
  const [cancellingAppointment, setCancellingAppointment] =
    useState(false)
  const [createError, setCreateError] =
    useState('')
  const [detailError, setDetailError] =
    useState('')

  const weekStart = useMemo(
    () => startOfWeek(selectedDate),
    [selectedDate],
  )
  const weekEnd = useMemo(
    () => addDays(weekStart, 6),
    [weekStart],
  )

  const visibleAppointments = useMemo(
    () =>
      statusFilter
        ? appointments.filter(
          (appointment) =>
            appointment.status
            === statusFilter,
        )
        : appointments,
    [appointments, statusFilter],
  )

  const doctor = {
    name: clinician?.name ?? '의료진',
    department:
      clinician?.department_name ?? '-',
    title: '의료진',
  }

  const isInVisibleWeek = (
    appointment: Appointment,
  ) => {
    const key = toDateKey(
      new Date(appointment.scheduled_at),
    )

    return (
      key >= toDateKey(weekStart)
      && key <= toDateKey(weekEnd)
    )
  }

  const openCreateModal = (date: Date) => {
    setCreateError('')
    setCreateInitialDateTime(
      toLocalDateTimeInput(date),
    )
    setCreateModalOpen(true)
  }

  useEffect(() => {
    const controller = new AbortController()

    const loadAppointments = async () => {
      setLoading(true)
      setError('')

      try {
        const response = await getAppointments({
          dateFrom: toDateKey(weekStart),
          dateTo: toDateKey(weekEnd),
          signal: controller.signal,
        })

        setAppointments(
          sortAppointments(response.data),
        )
      } catch (requestError) {
        if (
          requestError instanceof DOMException
          && requestError.name === 'AbortError'
        ) {
          return
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : '예약 목록을 불러오지 못했습니다.',
        )
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    void loadAppointments()

    return () => controller.abort()
  }, [weekStart, weekEnd])

  useEffect(() => {
    const controller = new AbortController()

    const loadPatients = async () => {
      try {
        const response = await getPatients({
          status: 'ACTIVE',
          page: 1,
          pageSize: 100,
          signal: controller.signal,
        })

        setPatients(response.data)
      } catch {
        if (!controller.signal.aborted) {
          setCreateError(
            '환자 목록을 불러오지 못했습니다.',
          )
        }
      }
    }

    void loadPatients()

    return () => controller.abort()
  }, [])

  const handleCreateAppointment = async (
    input: AppointmentCreateInput,
  ) => {
    setCreateError('')

    if (hasConflict(appointments, input)) {
      setCreateError(
        '해당 시간에는 이미 다른 예약이 있습니다.',
      )
      return
    }

    setSaving(true)

    try {
      const created =
        await createAppointment(input)

      if (isInVisibleWeek(created)) {
        setAppointments(
          (current) =>
            sortAppointments([
              ...current,
              created,
            ]),
        )
      } else {
        setSelectedDate(
          new Date(created.scheduled_at),
        )
      }

      setCreateModalOpen(false)
    } catch (requestError) {
      setCreateError(
        requestError instanceof Error
          ? requestError.message
          : '예약을 등록하지 못했습니다.',
      )
    } finally {
      setSaving(false)
    }
  }

  const handleUpdateAppointment = async (
    input: AppointmentUpdateInput,
  ): Promise<boolean> => {
    if (!selectedAppointment) {
      return false
    }

    setDetailError('')

    if (
      hasConflict(
        appointments,
        input,
        selectedAppointment.appointment_id,
      )
    ) {
      setDetailError(
        '해당 시간에는 이미 다른 예약이 있습니다.',
      )
      return false
    }

    setSaving(true)

    try {
      const updated = await updateAppointment(
        selectedAppointment.appointment_id,
        input,
      )

      setAppointments(
        (current) =>
          sortAppointments(
            current.map(
              (appointment) =>
                appointment.appointment_id
                  === updated.appointment_id
                  ? updated
                  : appointment,
            ),
          ),
      )
      setSelectedAppointment(updated)

      if (!isInVisibleWeek(updated)) {
        setSelectedDate(
          new Date(updated.scheduled_at),
        )
      }

      return true
    } catch (requestError) {
      setDetailError(
        requestError instanceof Error
          ? requestError.message
          : '예약을 변경하지 못했습니다.',
      )
      return false
    } finally {
      setSaving(false)
    }
  }

  const handleCancelAppointment = async () => {
    if (!selectedAppointment) {
      return
    }

    const confirmed = window.confirm(
      `${selectedAppointment.patient_name} 환자의 예약을 취소하시겠습니까?`,
    )

    if (!confirmed) {
      return
    }

    setCancellingAppointment(true)
    setDetailError('')

    try {
      const updated = await cancelAppointment(
        selectedAppointment.appointment_id,
      )

      setAppointments(
        (current) =>
          current.map(
            (appointment) =>
              appointment.appointment_id
                === updated.appointment_id
                ? updated
                : appointment,
          ),
      )
      setSelectedAppointment(updated)
    } catch (requestError) {
      setDetailError(
        requestError instanceof Error
          ? requestError.message
          : '예약을 취소하지 못했습니다.',
      )
    } finally {
      setCancellingAppointment(false)
    }
  }

  const handleOpenSelectedPatient = () => {
    if (!selectedAppointment) {
      return
    }

    const keyword =
      selectedAppointment.patient_number
      ?? selectedAppointment.patient_name

    setSelectedAppointment(null)
    navigate(
      `/patients?search=${
        encodeURIComponent(keyword)
      }`,
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
          onSearch={() => {
            const keyword = searchText.trim()
            navigate(
              keyword
                ? `/patients?search=${
                  encodeURIComponent(keyword)
                }`
                : '/patients',
            )
          }}
          onLogout={() => {
            logout()
            navigate(
              '/login',
              { replace: true },
            )
          }}
        />

        <main className="appointment-page">
          <div className="appointment-page-heading">
            <div>
              <h1>예약 관리</h1>
              <p>
                빈 시간을 눌러 예약을 등록하고
                기존 일정을 변경할 수 있습니다.
              </p>
            </div>

            <button
              type="button"
              className="appointment-create-button"
              onClick={() => {
                const initial =
                  new Date(selectedDate)
                initial.setHours(
                  APPOINTMENT_CALENDAR_START_HOUR,
                  0,
                  0,
                  0,
                )
                openCreateModal(initial)
              }}
            >
              예약 등록
            </button>
          </div>

          <section className="appointment-toolbar">
            <div className="appointment-date-controls">
              <button
                type="button"
                className="appointment-week-arrow"
                aria-label="이전 주"
                onClick={() =>
                  setSelectedDate(
                    (current) =>
                      addDays(current, -7),
                  )
                }
              >
                ‹
              </button>

              <strong className="appointment-week-range">
                {weekStart.toLocaleDateString(
                  'ko-KR',
                  {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                  },
                )}
                {' ~ '}
                {weekEnd.toLocaleDateString(
                  'ko-KR',
                  {
                    month: '2-digit',
                    day: '2-digit',
                  },
                )}
              </strong>

              <button
                type="button"
                className="appointment-week-arrow"
                aria-label="다음 주"
                onClick={() =>
                  setSelectedDate(
                    (current) =>
                      addDays(current, 7),
                  )
                }
              >
                ›
              </button>

              <button
                type="button"
                className="appointment-today-button"
                onClick={() =>
                  setSelectedDate(new Date())
                }
              >
                이번 주
              </button>
            </div>

            <label>
              예약 상태

              <select
                value={statusFilter}
                onChange={(event) =>
                  setStatusFilter(
                    event.target.value as
                      AppointmentStatus | '',
                  )
                }
              >
                <option value="">전체</option>
                <option value="SCHEDULED">예약</option>
                <option value="CONFIRMED">확정</option>
                <option value="CHECKED_IN">접수</option>
                <option value="COMPLETED">완료</option>
                <option value="CANCELLED">취소</option>
                <option value="NO_SHOW">미방문</option>
              </select>
            </label>
          </section>

          {error && (
            <p
              role="alert"
              className="appointment-page-error"
            >
              {error}
            </p>
          )}

          {loading && (
            <p className="appointment-loading">
              예약을 불러오는 중입니다.
            </p>
          )}

          <AppointmentCalendar
            weekStart={weekStart}
            appointments={visibleAppointments}
            blockingAppointments={appointments}
            loading={loading}
            onSelectAppointment={(appointment) => {
              setDetailError('')
              setSelectedAppointment(appointment)
            }}
            onSelectEmptySlot={openCreateModal}
          />
        </main>
      </div>

      {createModalOpen && (
        <AppointmentCreateModal
          key={createInitialDateTime}
          initialDateTime={createInitialDateTime}
          patients={patients}
          clinicianName={
            clinician?.name ?? '의료진'
          }
          saving={saving}
          error={createError}
          onClose={() =>
            setCreateModalOpen(false)
          }
          onSubmit={handleCreateAppointment}
        />
      )}

      {selectedAppointment && (
        <AppointmentDetailModal
          appointment={selectedAppointment}
          saving={saving}
          cancelling={cancellingAppointment}
          error={detailError}
          onClose={() => {
            setDetailError('')
            setSelectedAppointment(null)
          }}
          onOpenPatient={handleOpenSelectedPatient}
          onCancel={handleCancelAppointment}
          onUpdate={handleUpdateAppointment}
        />
      )}
    </div>
  )
}
