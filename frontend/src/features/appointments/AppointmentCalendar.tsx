import type {
  Appointment,
  AppointmentStatus,
} from './appointment.types'

interface AppointmentCalendarProps {
  weekStart: Date
  appointments: Appointment[]
  loading: boolean

  onSelectAppointment: (
    appointment: Appointment,
  ) => void
}

function addDays(
  date: Date,
  amount: number,
): Date {
  const next = new Date(date)

  next.setDate(
    next.getDate() + amount,
  )

  return next
}

function dateKey(
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

function formatDay(
  date: Date,
): string {
  return new Intl.DateTimeFormat(
    'ko-KR',
    {
      month: 'numeric',
      day: 'numeric',
      weekday: 'short',
    },
  ).format(date)
}

function formatTime(
  value: string,
): string {
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

export function AppointmentCalendar({
  weekStart,
  appointments,
  loading,
  onSelectAppointment,
}: AppointmentCalendarProps) {
  const days = Array.from(
    { length: 7 },
    (_, index) =>
      addDays(weekStart, index),
  )

  return (
    <div className="appointment-calendar-wrapper">
      <div className="appointment-calendar">
        {days.map((day) => {
          const key = dateKey(day)

          const dayAppointments =
            appointments
              .filter(
                (appointment) =>
                  dateKey(
                    new Date(
                      appointment.scheduled_at,
                    ),
                  ) === key,
              )
              .sort(
                (left, right) =>
                  new Date(
                    left.scheduled_at,
                  ).getTime()
                  - new Date(
                    right.scheduled_at,
                  ).getTime(),
              )

          return (
            <section
              className="appointment-day"
              key={key}
            >
              <header className="appointment-day-header">
                {formatDay(day)}
              </header>

              <div className="appointment-day-body">
                {dayAppointments.map(
                  (appointment) => (
                    <button
                      key={
                        appointment.appointment_id
                      }
                      type="button"
                      className={`appointment-card appointment-${appointment.status.toLowerCase()}`}
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
                      </strong>

                      <span>
                        {
                          appointment.patient_name
                        }
                      </span>

                      <small>
                        {
                          appointment
                            .patient_number
                          ?? '-'
                        }
                      </small>

                      <small>
                        {
                          appointment.location
                          || '진료실 미정'
                        }
                      </small>

                      <em>
                        {
                          statusLabel(
                            appointment.status,
                          )
                        }
                      </em>
                    </button>
                  ),
                )}

                {!loading
                  && dayAppointments.length
                    === 0
                  && (
                    <p className="appointment-empty-day">
                      예약 없음
                    </p>
                  )}
              </div>
            </section>
          )
        })}
      </div>
    </div>
  )
}