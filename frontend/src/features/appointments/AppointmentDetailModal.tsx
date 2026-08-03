import {
  useEffect,
} from 'react'

import type {
  Appointment,
  AppointmentStatus,
} from './appointment.types'

interface AppointmentDetailModalProps {
  appointment: Appointment

  cancelling: boolean
  error: string

  onClose: () => void
  onOpenPatient: () => void
  onCancel: () => void
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
  ).format(
    new Date(value),
  )
}

export function AppointmentDetailModal({
  appointment,
  cancelling,
  error,
  onClose,
  onOpenPatient,
  onCancel,
}: AppointmentDetailModalProps) {
  useEffect(() => {
    const handleKeyDown = (
      event: KeyboardEvent,
    ) => {
      if (event.key === 'Escape') {
        onClose()
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
  }, [onClose])

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
            예약 상세
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
            {
              statusLabels[
                appointment.status
              ]
            }
          </span>
        </div>

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
              {
                appointment
                  .duration_minutes
              }
              분
            </dd>
          </div>

          <div>
            <dt>진료과</dt>

            <dd>
              {
                appointment
                  .department_name
              }
            </dd>
          </div>

          <div>
            <dt>담당 의료진</dt>

            <dd>
              {
                appointment
                  .clinician_name
              }
            </dd>
          </div>

          <div>
            <dt>병원</dt>

            <dd>
              {
                appointment
                  .hospital_name
              }
            </dd>
          </div>

          <div>
            <dt>진료실</dt>

            <dd>
              {
                appointment.location
                || '미정'
              }
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
              {
                appointment.status
                !== 'CANCELLED'
                && appointment.status
                !== 'COMPLETED'
                && (
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
                )
            }
        </footer>
      </section>
    </div>
  )
}