import type {
  CSSProperties,
} from 'react'

import {
  APPOINTMENT_CALENDAR_END_HOUR,
  APPOINTMENT_CALENDAR_SLOT_MINUTES,
  APPOINTMENT_CALENDAR_START_HOUR,
} from './appointment.constants'

import type {
  Appointment,
  AppointmentStatus,
} from './appointment.types'

interface AppointmentCalendarProps {
  weekStart: Date
  appointments: Appointment[]
  blockingAppointments: Appointment[]
  loading: boolean

  onSelectAppointment: (
    appointment: Appointment,
  ) => void

  onSelectEmptySlot: (
    date: Date,
  ) => void
}

const startMinutes =
  APPOINTMENT_CALENDAR_START_HOUR
  * 60

const endMinutes =
  APPOINTMENT_CALENDAR_END_HOUR
  * 60

const slotMinutes = Array.from(
  {
    length:
      (endMinutes - startMinutes)
      / APPOINTMENT_CALENDAR_SLOT_MINUTES,
  },
  (_, index) =>
    startMinutes
    + index
      * APPOINTMENT_CALENDAR_SLOT_MINUTES,
)

function addDays(
  date: Date,
  amount: number,
): Date {
  const next = new Date(date)
  next.setDate(next.getDate() + amount)
  return next
}

function dateKey(date: Date): string {
  const offset =
    date.getTimezoneOffset() * 60_000

  return new Date(
    date.getTime() - offset,
  )
    .toISOString()
    .slice(0, 10)
}

function formatDay(date: Date): string {
  return new Intl.DateTimeFormat(
    'ko-KR',
    {
      month: 'numeric',
      day: 'numeric',
      weekday: 'short',
    },
  ).format(date)
}

function formatMinutes(
  minutes: number,
): string {
  const hour = Math.floor(
    minutes / 60,
  )
  const minute = minutes % 60

  return `${String(hour).padStart(2, '0')}:${
    String(minute).padStart(2, '0')
  }`
}

function formatTime(value: string): string {
  return new Intl.DateTimeFormat(
    'ko-KR',
    {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    },
  ).format(new Date(value))
}

function statusLabel(
  status: AppointmentStatus,
): string {
  const labels: Record<
    AppointmentStatus,
    string
  > = {
    SCHEDULED: '예약',
    CONFIRMED: '확정',
    CHECKED_IN: '접수',
    COMPLETED: '완료',
    CANCELLED: '취소',
    NO_SHOW: '미방문',
  }

  return labels[status]
}

function isBlocking(
  appointment: Appointment,
): boolean {
  return ![
    'CANCELLED',
    'NO_SHOW',
  ].includes(appointment.status)
}

function overlaps(
  appointment: Appointment,
  slotStart: Date,
): boolean {
  if (!isBlocking(appointment)) {
    return false
  }

  const appointmentStart =
    new Date(
      appointment.scheduled_at,
    ).getTime()

  const appointmentEnd =
    appointmentStart
    + appointment.duration_minutes
      * 60_000

  const requestedStart =
    slotStart.getTime()

  const requestedEnd =
    requestedStart
    + APPOINTMENT_CALENDAR_SLOT_MINUTES
      * 60_000

  return (
    requestedStart < appointmentEnd
    && requestedEnd > appointmentStart
  )
}

function appointmentGridStyle(
  appointment: Appointment,
  dayIndex: number,
): CSSProperties | null {
  const start = new Date(
    appointment.scheduled_at,
  )
  const minutes =
    start.getHours() * 60
    + start.getMinutes()

  if (
    minutes < startMinutes
    || minutes >= endMinutes
  ) {
    return null
  }

  const row =
    Math.floor(
      (minutes - startMinutes)
      / APPOINTMENT_CALENDAR_SLOT_MINUTES,
    ) + 2

  const availableRows =
    slotMinutes.length
    - (row - 2)

  const rowSpan = Math.min(
    availableRows,
    Math.max(
      1,
      Math.ceil(
        appointment.duration_minutes
        / APPOINTMENT_CALENDAR_SLOT_MINUTES,
      ),
    ),
  )

  return {
    gridColumn: dayIndex + 2,
    gridRow: `${row} / span ${rowSpan}`,
  }
}

export function AppointmentCalendar({
  weekStart,
  appointments,
  blockingAppointments,
  loading,
  onSelectAppointment,
  onSelectEmptySlot,
}: AppointmentCalendarProps) {
  const days = Array.from(
    { length: 7 },
    (_, index) =>
      addDays(weekStart, index),
  )

  const outsideHoursAppointments =
    appointments.filter((appointment) => {
      const start = new Date(
        appointment.scheduled_at,
      )
      const minutes =
        start.getHours() * 60
        + start.getMinutes()

      return (
        days.some(
          (day) =>
            dateKey(day)
            === dateKey(start),
        )
        && (
          minutes < startMinutes
          || minutes >= endMinutes
        )
      )
    })

  return (
    <div className="appointment-calendar-wrapper">
      <div
        className="appointment-time-grid"
        aria-busy={loading}
      >
        <div className="appointment-time-corner">
          시간
        </div>

        {days.map((day, dayIndex) => (
          <header
            className="appointment-day-header"
            key={dateKey(day)}
            style={{
              gridColumn: dayIndex + 2,
              gridRow: 1,
            }}
          >
            {formatDay(day)}
          </header>
        ))}

        {slotMinutes.map(
          (minutes, slotIndex) => (
            <div
              className="appointment-time-label"
              key={`time-${minutes}`}
              style={{
                gridColumn: 1,
                gridRow: slotIndex + 2,
              }}
            >
              {
                minutes % 60 === 0
                  ? formatMinutes(minutes)
                  : ''
              }
            </div>
          ),
        )}

        {days.flatMap(
          (day, dayIndex) =>
            slotMinutes.map(
              (minutes, slotIndex) => {
                const slot = new Date(day)
                slot.setHours(
                  Math.floor(minutes / 60),
                  minutes % 60,
                  0,
                  0,
                )

                const occupied =
                  blockingAppointments.some(
                    (appointment) =>
                      dateKey(
                        new Date(
                          appointment.scheduled_at,
                        ),
                      ) === dateKey(day)
                      && overlaps(
                        appointment,
                        slot,
                      ),
                  )

                return (
                  <button
                    type="button"
                    className="appointment-slot-button"
                    key={`${dateKey(day)}-${minutes}`}
                    style={{
                      gridColumn: dayIndex + 2,
                      gridRow: slotIndex + 2,
                    }}
                    disabled={occupied}
                    aria-label={`${formatDay(day)} ${formatMinutes(minutes)} 예약 등록`}
                    title={
                      occupied
                        ? '이미 예약된 시간입니다.'
                        : '이 시간에 예약 등록'
                    }
                    onClick={() =>
                      onSelectEmptySlot(slot)
                    }
                  >
                    {!occupied && (
                      <span>+</span>
                    )}
                  </button>
                )
              },
            ),
        )}

        {appointments.flatMap(
          (appointment) => {
            const start = new Date(
              appointment.scheduled_at,
            )
            const dayIndex =
              days.findIndex(
                (day) =>
                  dateKey(day)
                  === dateKey(start),
              )

            if (dayIndex < 0) {
              return []
            }

            const style =
              appointmentGridStyle(
                appointment,
                dayIndex,
              )

            if (!style) {
              return []
            }

            return [
              <button
                type="button"
                key={appointment.appointment_id}
                className={`appointment-card appointment-${appointment.status.toLowerCase()}`}
                style={style}
                onClick={() =>
                  onSelectAppointment(
                    appointment,
                  )
                }
              >
                <strong>
                  {formatTime(
                    appointment.scheduled_at,
                  )}
                  {' · '}
                  {appointment.patient_name}
                </strong>

                <small>
                  {appointment.duration_minutes}분
                  {' · '}
                  {
                    appointment.location
                    || '진료실 미정'
                  }
                </small>

                <em>
                  {statusLabel(
                    appointment.status,
                  )}
                </em>
              </button>,
            ]
          },
        )}
      </div>

      {outsideHoursAppointments.length > 0 && (
        <section className="appointment-outside-hours">
          <h2>진료시간 외 예약</h2>

          <div>
            {outsideHoursAppointments.map(
              (appointment) => (
                <button
                  type="button"
                  key={appointment.appointment_id}
                  onClick={() =>
                    onSelectAppointment(
                      appointment,
                    )
                  }
                >
                  {formatTime(
                    appointment.scheduled_at,
                  )}
                  {' · '}
                  {appointment.patient_name}
                </button>
              ),
            )}
          </div>
        </section>
      )}
    </div>
  )
}
