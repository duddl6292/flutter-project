import {
  CalendarDays,
  Pill,
  UserRound,
  X,
} from 'lucide-react'

import {
  useEffect,
  useState,
} from 'react'

import {
  updatePrescriptionStatus,
} from './prescription.api'

import type {
  Prescription,
  PrescriptionStatus,
} from './prescription.types'

interface PrescriptionDetailModalProps {
  prescription: Prescription
  onClose: () => void
  onUpdated: (
    prescription: Prescription,
  ) => void
}

const nextStatusActions: Partial<
  Record<
    PrescriptionStatus,
    Array<{
      status: PrescriptionStatus
      label: string
      danger?: boolean
    }>
  >
> = {
  DRAFT: [
    {
      status: 'ACTIVE',
      label: '처방 발행',
    },
    {
      status: 'CANCELLED',
      label: '작성 취소',
      danger: true,
    },
  ],
  ACTIVE: [
    {
      status: 'COMPLETED',
      label: '처방 완료',
    },
    {
      status: 'DISCONTINUED',
      label: '처방 중단',
      danger: true,
    },
    {
      status: 'CANCELLED',
      label: '처방 취소',
      danger: true,
    },
  ],
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat(
    'ko-KR',
    {
      dateStyle: 'medium',
      timeStyle: 'short',
    },
  ).format(new Date(value))
}

export function PrescriptionDetailModal({
  prescription,
  onClose,
  onUpdated,
}: PrescriptionDetailModalProps) {
  const [updating, setUpdating] =
    useState(false)
  const [error, setError] =
    useState('')

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

  const handleStatus = async (
    nextStatus: PrescriptionStatus,
    danger = false,
  ) => {
    if (
      danger
      && !window.confirm(
        '이 처방의 상태를 변경할까요?',
      )
    ) {
      return
    }

    setUpdating(true)
    setError('')

    try {
      const updated =
        await updatePrescriptionStatus(
          prescription.prescription_id,
          nextStatus,
        )

      onUpdated(updated)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : '처방 상태를 변경하지 못했습니다.',
      )
    } finally {
      setUpdating(false)
    }
  }

  const actions =
    nextStatusActions[prescription.status]
    ?? []

  return (
    <div
      className="prescription-modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose()
        }
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="prescription-detail-title"
        className="prescription-modal"
      >
        <header className="prescription-modal-header">
          <div>
            <h2 id="prescription-detail-title">
              처방전 상세
            </h2>
            <p>{prescription.encounter_number}</p>
          </div>

          <button
            type="button"
            aria-label="닫기"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </header>

        <div className="prescription-modal-body">
          <div className="prescription-detail-summary">
            <div>
              <UserRound size={18} />
              <span>
                환자
                <strong>
                  {prescription.patient_name}
                  {' ('}
                  {prescription.patient_number ?? '-'}
                  {')'}
                </strong>
              </span>
            </div>

            <div>
              <CalendarDays size={18} />
              <span>
                처방 일시
                <strong>
                  {formatDateTime(
                    prescription.prescribed_at,
                  )}
                </strong>
              </span>
            </div>

            <div>
              <Pill size={18} />
              <span>
                상태
                <strong>
                  {prescription.status_label}
                </strong>
              </span>
            </div>
          </div>

          <section className="prescription-detail-section">
            <h3>처방 약품</h3>

            <div className="prescription-detail-items">
              {prescription.items.map((item) => (
                <article
                  key={
                    item.prescription_item_id
                  }
                >
                  <header>
                    <strong>
                      {item.medicine_name}
                    </strong>
                    <span>
                      {Number(item.dosage)}
                      {item.dose_unit}
                    </span>
                  </header>

                  <dl>
                    <div>
                      <dt>복용 빈도</dt>
                      <dd>{item.frequency}</dd>
                    </div>
                    <div>
                      <dt>투여 경로</dt>
                      <dd>{item.route || '-'}</dd>
                    </div>
                    <div>
                      <dt>복용 기간</dt>
                      <dd>
                        {item.start_date}
                        {' ~ '}
                        {item.end_date ?? '계속'}
                      </dd>
                    </div>
                    <div>
                      <dt>복약 지시</dt>
                      <dd>
                        {item.instructions || '-'}
                      </dd>
                    </div>
                  </dl>
                </article>
              ))}
            </div>
          </section>

          <section className="prescription-detail-section">
            <h3>참고사항</h3>
            <p>{prescription.notes || '없음'}</p>
          </section>

          {error && (
            <p
              role="alert"
              className="prescription-error"
            >
              {error}
            </p>
          )}
        </div>

        <footer className="prescription-modal-footer">
          <button
            type="button"
            className="prescription-secondary-button"
            onClick={onClose}
          >
            닫기
          </button>

          {actions.map((action) => (
            <button
              type="button"
              key={action.status}
              disabled={updating}
              className={
                action.danger
                  ? 'prescription-danger-button'
                  : 'prescription-primary-button'
              }
              onClick={() => {
                void handleStatus(
                  action.status,
                  action.danger,
                )
              }}
            >
              {action.label}
            </button>
          ))}
        </footer>
      </section>
    </div>
  )
}
