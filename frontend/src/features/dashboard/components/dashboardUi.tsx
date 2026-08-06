import { ChevronRight } from 'lucide-react'
import type { ReactNode } from 'react'

import type { CtStatus } from '../dashboard.types'

export type BadgeTone = 'purple' | 'yellow' | 'green' | 'blue' | 'gray'

export function formatDateTitle(value: string): string {
  const [year, month, day] = value.split('-').map(Number)
  return new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'short' }).format(new Date(year, month - 1, day))
}
export function formatDateTime(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value || '-' : new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }).format(date)
}
export function formatTime(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value || '-' : new Intl.DateTimeFormat('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false }).format(date)
}
export function genderLabel(gender: string): string { return gender === 'M' ? '남' : gender === 'F' ? '여' : gender || '-' }
export function patientStatusLabel(status: string): string { return ({ scheduled: '진료 예정', confirmed: '예약 확정', waiting: '대기 중', in_progress: '진료 중', completed: '진료 완료', cancelled: '예약 취소', no_show: '미방문' } as Record<string, string>)[status] ?? status }
export function patientStatusTone(status: string): BadgeTone { return ({ scheduled: 'purple', confirmed: 'blue', waiting: 'yellow', in_progress: 'green', completed: 'gray', cancelled: 'gray', no_show: 'gray' } as Record<string, BadgeTone>)[status] ?? 'gray' }
export function activityTypeLabel(type: string): string { return ({ medical_record: '진료 기록', test_result: '검사 결과', consultation: '협진', ct_analysis: 'CT 분석', prescription: '처방전' } as Record<string, string>)[type] ?? type }
export function activityTone(type: string): BadgeTone { return ({ medical_record: 'purple', test_result: 'purple', consultation: 'green', ct_analysis: 'blue', prescription: 'purple' } as Record<string, BadgeTone>)[type] ?? 'gray' }
export function consultationStatusLabel(status: string): string { return ({ requested: '요청', waiting: '답변 대기', answered: '답변 완료', completed: '답변 완료', cancelled: '취소' } as Record<string, string>)[status] ?? status }
export function consultationStatusTone(status: string): BadgeTone { return status === 'cancelled' ? 'gray' : status === 'answered' || status === 'completed' ? 'green' : 'purple' }
export function ctStatusLabel(status: CtStatus): string { return ({ waiting: '분석 대기', processing: '분석 중', completed: '분석 완료', failed: '분석 실패' } as Record<CtStatus, string>)[status] }
export function ctStatusTone(status: CtStatus): BadgeTone { return ({ waiting: 'gray', processing: 'yellow', completed: 'green', failed: 'gray' } as Record<CtStatus, BadgeTone>)[status] }

export function StatusBadge({ children, tone }: { children: ReactNode; tone: BadgeTone }) { return <span className={`status-badge status-${tone}`}>{children}</span> }
export function PanelTitle({ title, showMore = true, onShowMore }: { title: string; showMore?: boolean; onShowMore?: () => void }) {
  return <div className="panel-title-row"><h2>{title}</h2>{showMore && <button className="text-button" type="button" onClick={onShowMore}>전체 보기 <ChevronRight size={15} /></button>}</div>
}
