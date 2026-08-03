import {
  useState,
} from 'react'

import type {
  PatientSummary,
} from '../patients/patient.types'

import type {
  AppointmentCreateInput,
} from './appointment.types'

import {
  APPOINTMENT_DURATION_OPTIONS,
  DEFAULT_APPOINTMENT_DURATION_MINUTES,
} from './appointment.constants'

interface AppointmentCreateModalProps {
  selectedDate: string
  patients: PatientSummary[]
  clinicianName: string
  saving: boolean
  error: string

  onClose: () => void

  onSubmit: (
    input: AppointmentCreateInput,
  ) => Promise<void>
}

export function AppointmentCreateModal({
  selectedDate,
  patients,
  clinicianName,
  saving,
  error,
  onClose,
  onSubmit,
}: AppointmentCreateModalProps) {
  const [patientId, setPatientId] =
    useState('')

  const [
    scheduledAt,
    setScheduledAt,
  ] = useState(
    `${selectedDate}T09:00`,
  )

  const [
    durationMinutes,
    setDurationMinutes,
  ] = useState(
    DEFAULT_APPOINTMENT_DURATION_MINUTES,
  )

  const [location, setLocation] =
    useState('')

  const [reason, setReason] =
    useState('')

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
        className="appointment-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="appointment-modal-title"
      >
        <header>
          <h2 id="appointment-modal-title">
            예약 등록
          </h2>

          <button
            type="button"
            onClick={onClose}
            aria-label="예약 등록 닫기"
          >
            ×
          </button>
        </header>

        <form
          onSubmit={(event) => {
            event.preventDefault()

            if (
              !patientId
              || !scheduledAt
            ) {
              return
            }

            void onSubmit({
              patient_id:
                patientId,

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
          }}
        >
          <label>
            담당 의료진

            <input
              value={clinicianName}
              readOnly
            />
          </label>

          <label>
            환자

            <select
              required
              value={patientId}
              onChange={(event) =>
                setPatientId(
                  event.target.value,
                )
              }
            >
              <option value="">
                환자를 선택해주세요
              </option>

              {patients.map(
                (patient) => (
                  <option
                    key={
                      patient.patient_id
                    }
                    value={
                      patient.patient_id
                    }
                  >
                    {
                      patient
                        .medical_record_number
                      ?? '-'
                    }
                    {' · '}
                    {patient.name}
                  </option>
                ),
              )}
            </select>
          </label>

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
              {
                APPOINTMENT_DURATION_OPTIONS.map(
                  (minutes) => (
                    <option
                      key={minutes}
                      value={minutes}
                    >
                      {minutes}분
                    </option>
                  ),
                )
              }
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
              placeholder="예약 사유를 입력해주세요."
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
              onClick={onClose}
            >
              취소
            </button>

            <button
              type="submit"
              className="appointment-submit-button"
              disabled={
                saving
                || !patientId
                || !scheduledAt
              }
            >
              {
                saving
                  ? '등록 중'
                  : '예약 등록'
              }
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}
