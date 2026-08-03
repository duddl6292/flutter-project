import type { ReactNode } from 'react'
import { ChevronRight } from 'lucide-react'

import type { CtStatus } from '../dashboard.types'

export type BadgeTone =
  | 'purple'
  | 'yellow'
  | 'green'
  | 'blue'
  | 'gray'

export function formatDateTitle(
  dateValue: string,
): string {
  const [year, month, day] =
    dateValue.split('-').map(Number)
  const date = new Date(
    year,
    month - 1,
    day,
  )

  return new Intl.DateTimeFormat(
    'ko-KR',
    {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      weekday: 'short',
    },
  ).format(date)
}

export function formatDateTime(
  value: string,
): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value || '-'
  }

  return new Intl.DateTimeFormat(
    'ko-KR',
    {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    },
  ).format(date)
}

export function formatTime(
  value: string,
): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value || '-'
  }

  return new Intl.DateTimeFormat(
    'ko-KR',
    {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    },
  ).format(date)
}

export function genderLabel(
  gender: string,
): string {
  if (gender === 'M') return '남'
  if (gender === 'F') return '여'
  return gender || '-'
}

export function patientStatusLabel(
  status: string,
): string {
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

export function patientStatusTone(
  status: string,
): BadgeTone {
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

export function activityTypeLabel(
  type: string,
): string {
  const labels: Record<string, string> = {
    medical_record: '진료 기록',
    test_result: '검사 결과',
    consultation: '협진',
    ct_analysis: 'CT 분석',
    prescription: '처방전',
  }

  return labels[type] ?? type
}

export function activityTone(
  type: string,
): BadgeTone {
  const tones: Record<string, BadgeTone> = {
    medical_record: 'purple',
    test_result: 'purple',
    consultation: 'green',
    ct_analysis: 'blue',
    prescription: 'purple',
  }

  return tones[type] ?? 'gray'
}

export function consultationStatusLabel(
  status: string,
): string {
  const labels: Record<string, string> = {
    requested: '요청',
    waiting: '응답 대기',
    answered: '응답 완료',
    completed: '응답 완료',
  }

  return labels[status] ?? status
}

export function consultationStatusTone(
  status: string,
): BadgeTone {
  return status === 'answered'
    || status === 'completed'
    ? 'green'
    : 'purple'
}

export function ctStatusLabel(
  status: CtStatus,
): string {
  const labels: Record<CtStatus, string> = {
    waiting: '분석 대기',
    processing: '분석 중',
    completed: '분석 완료',
    failed: '분석 실패',
  }

  return labels[status]
}

export function ctStatusTone(
  status: CtStatus,
): BadgeTone {
  const tones: Record<CtStatus, BadgeTone> = {
    waiting: 'gray',
    processing: 'yellow',
    completed: 'green',
    failed: 'gray',
  }

  return tones[status]
}

export function StatusBadge({
  children,
  tone,
}: {
  children: ReactNode
  tone: BadgeTone
}) {
  return (
    <span
      className={`status-badge status-${tone}`}
    >
      {children}
    </span>
  )
}

export function PanelTitle({
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
        <button
          className="text-button"
          type="button"
        >
          전체 보기
          <ChevronRight size={15} />
        </button>
      )}
    </div>
  )
}
