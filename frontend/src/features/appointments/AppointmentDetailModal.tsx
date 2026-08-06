import {
  useEffect,
  useState,
} from 'react'

import {
  APPOINTMENT_DURATION_OPTIONS,
} from './appointment.constants'

import type {
  Appointment,
  AppointmentStatus,
  AppointmentUpdateInput,
} from './appointment.types'

interface AppointmentDetailModalProps {
  appointment: Appointment
  saving: boolean
  cancelling: boolean
  registeringEncounter: boolean
  error: string

  onClose: () => void
  onOpenPatient: () => void
  onCancel: () => void
  onRegisterEncounter: () => void
  onOpenEncounter: () => void
  onUpdate: (
    input: AppointmentUpdateInput,
  ) => Promise<boolean>
}

const statusLabels: Record<
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

function formatDateTime(
  value: string,
): string {
  return new Intl.DateTimeFormat(
    'ko-KR',
    {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      weekday: 'short',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    },
  ).format(new Date(value))
}

function toLocalDateTimeInput(
  value: string,
): string {
  const date = new Date(value)
  const offset =
    date.getTimezoneOffset() * 60_000

  return new Date(
    date.getTime() - offset,
  )
    .toISOString()
    .slice(0, 16)
}

export function AppointmentDetailModal({
  appointment,
  saving,
  cancelling,
  registeringEncounter,
  error,
  onClose,
  onOpenPatient,
  onCancel,
  onRegisterEncounter,
  onOpenEncounter,
  onUpdate,
}: AppointmentDetailModalProps) {
  const [editing, setEditing] =
    useState(false)

  const [scheduledAt, setScheduledAt] =
    useState(
      toLocalDateTimeInput(
        appointment.scheduled_at,
      ),
    )

  const [durationMinutes, setDurationMinutes] =
    useState(
      appointment.duration_minutes,
    )

  const [location, setLocation] =
    useState(appointment.location)

  const [reason, setReason] =
    useState(appointment.reason)

  const editable = ![
    'CANCELLED',
    'COMPLETED',
  ].includes(appointment.status)
  const scheduledDate = toLocalDateTimeInput(
    appointment.scheduled_at,
  ).slice(0, 10)
  const today = toLocalDateTimeInput(new Date().toISOString()).slice(0, 10)
  const canRegisterEncounter = (
    !appointment.encounter_id
    && scheduledDate === today
    && [
      'SCHEDULED',
      'CONFIRMED',
      'CHECKED_IN',
    ].includes(appointment.status)
  )

  useEffect(() => {
    setScheduledAt(
      toLocalDateTimeInput(
        appointment.scheduled_at,
      ),
    )
    setDurationMinutes(
      appointment.duration_minutes,
    )
    setLocation(appointment.location)
    setReason(appointment.reason)
  }, [appointment])

  useEffect(() => {
    const handleKeyDown = (
      event: KeyboardEvent,
    ) => {
      if (event.key === 'Escape') {
        if (editing) {
          setEditing(false)
        } else {
          onClose()
        }
      }
    }

    window.addEventListener(
      'keydown',
      handleKeyDown,
    )

    return () => {
      window.removeEventListener(
        'keydown',
        handleKeyDown,
      )
    }
  }, [editing, onClose])

  const resetEditForm = () => {
    setScheduledAt(
      toLocalDateTimeInput(
        appointment.scheduled_at,
      ),
    )
    setDurationMinutes(
      appointment.duration_minutes,
    )
    setLocation(appointment.location)
    setReason(appointment.reason)
    setEditing(false)
  }

  return (
    <div
      className="appointment-modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (
          event.target
          === event.currentTarget
        ) {
          onClose()
        }
      }}
    >
      <section
        className="appointment-modal appointment-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="appointment-detail-title"
      >
        <header>
          <h2 id="appointment-detail-title">
            {editing ? '예약 변경' : '예약 상세'}
          </h2>

          <button
            type="button"
            aria-label="예약 상세 닫기"
            onClick={onClose}
          >
            ×
          </button>
        </header>

        <div className="appointment-detail-summary">
          <div>
            <strong>
              {appointment.patient_name}
            </strong>

            <span>
              {
                appointment.patient_number
                ?? '환자번호 없음'
              }
            </span>
          </div>

          <span
            className={`appointment-detail-status appointment-${appointment.status.toLowerCase()}`}
          >
            {statusLabels[appointment.status]}
          </span>
        </div>

        {editing ? (
          <form
            className="appointment-edit-form"
            onSubmit={(event) => {
              event.preventDefault()

              void (async () => {
                const updated =
                  await onUpdate({
                    scheduled_at:
                      new Date(
                        scheduledAt,
                      ).toISOString(),
                    duration_minutes:
                      durationMinutes,
                    location:
                      location.trim(),
                    reason:
                      reason.trim(),
                  })

                if (updated) {
                  setEditing(false)
                }
              })()
            }}
          >
            <label>
              예약 일시

              <input
                type="datetime-local"
                required
                value={scheduledAt}
                onChange={(event) =>
                  setScheduledAt(
                    event.target.value,
                  )
                }
              />
            </label>

            <label>
              예상 진료시간

              <select
                value={durationMinutes}
                onChange={(event) =>
                  setDurationMinutes(
                    Number(
                      event.target.value,
                    ),
                  )
                }
              >
                {APPOINTMENT_DURATION_OPTIONS.map(
                  (minutes) => (
                    <option
                      key={minutes}
                      value={minutes}
                    >
                      {minutes}분
                    </option>
                  ),
                )}
              </select>
            </label>

            <label>
              진료실

              <input
                value={location}
                placeholder="예: 제1진료실"
                onChange={(event) =>
                  setLocation(
                    event.target.value,
                  )
                }
              />
            </label>

            <label>
              예약 사유

              <textarea
                value={reason}
                onChange={(event) =>
                  setReason(
                    event.target.value,
                  )
                }
              />
            </label>

            {error && (
              <p
                role="alert"
                className="appointment-form-error"
              >
                {error}
              </p>
            )}

            <footer>
              <button
                type="button"
                className="appointment-cancel-button"
                disabled={saving}
                onClick={resetEditForm}
              >
                변경 취소
              </button>

              <button
                type="submit"
                className="appointment-submit-button"
                disabled={
                  saving
                  || !scheduledAt
                }
              >
                {
                  saving
                    ? '저장 중'
                    : '변경 저장'
                }
              </button>
            </footer>
          </form>
        ) : (
          <>
            <dl className="appointment-detail-list">
              <div>
                <dt>예약 일시</dt>
                <dd>
                  {formatDateTime(
                    appointment.scheduled_at,
                  )}
                </dd>
              </div>

              <div>
                <dt>소요시간</dt>
                <dd>
                  {appointment.duration_minutes}분
                </dd>
              </div>

              <div>
                <dt>진료과</dt>
                <dd>{appointment.department_name}</dd>
              </div>

              <div>
                <dt>담당 의료진</dt>
                <dd>{appointment.clinician_name}</dd>
              </div>

              <div>
                <dt>병원</dt>
                <dd>{appointment.hospital_name}</dd>
              </div>

              <div>
                <dt>진료실</dt>
                <dd>
                  {appointment.location || '미정'}
                </dd>
              </div>

              <div className="appointment-detail-full-row">
                <dt>예약 사유</dt>
                <dd>
                  {
                    appointment.reason
                    || '등록된 예약 사유가 없습니다.'
                  }
                </dd>
              </div>
            </dl>

            {error && (
              <p
                role="alert"
                className="appointment-form-error"
              >
                {error}
              </p>
            )}

            <footer>
              <button
                type="button"
                className="appointment-cancel-button"
                onClick={onClose}
              >
                닫기
              </button>

              <button
                type="button"
                className="appointment-patient-button"
                onClick={onOpenPatient}
              >
                환자 관리에서 보기
              </button>

              {appointment.encounter_id && (
                <button
                  type="button"
                  className="appointment-encounter-button"
                  onClick={onOpenEncounter}
                >
                  진료관리에서 보기
                </button>
              )}

              {canRegisterEncounter && (
                <button
                  type="button"
                  className="appointment-encounter-button"
                  disabled={registeringEncounter}
                  onClick={onRegisterEncounter}
                >
                  {registeringEncounter
                    ? '등록 중'
                    : '진료관리 등록'}
                </button>
              )}

              {editable && (
                <button
                  type="button"
                  className="appointment-edit-button"
                  onClick={() =>
                    setEditing(true)
                  }
                >
                  일정 변경
                </button>
              )}

              {editable && (
                <button
                  type="button"
                  className="appointment-danger-button"
                  disabled={cancelling}
                  onClick={onCancel}
                >
                  {
                    cancelling
                      ? '취소 처리 중'
                      : '예약 취소'
                  }
                </button>
              )}
            </footer>
          </>
        )}
      </section>
    </div>
  )
}
