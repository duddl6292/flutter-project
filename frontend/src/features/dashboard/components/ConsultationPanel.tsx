import { useNavigate } from 'react-router-dom'

import type { DashboardConsultation } from '../dashboard.types'
import { consultationStatusLabel, consultationStatusTone, formatDateTime, PanelTitle, StatusBadge } from './dashboardUi'

export type ConsultationTab = 'all' | 'waiting' | 'completed'
interface Props {
  consultations: DashboardConsultation[]
  activeTab: ConsultationTab
  counts: { all: number; waiting: number; completed: number }
  onTabChange: (tab: ConsultationTab) => void
  onSelect?: (id: string | number) => void
}
export function ConsultationPanel({ consultations, activeTab, counts, onTabChange, onSelect }: Props) {
  const navigate = useNavigate()
  return <article className="dashboard-panel consultation-dashboard-panel"><PanelTitle title="협진 현황" onShowMore={() => navigate('/consultations')} /><div className="consult-tabs"><button className={activeTab === 'all' ? 'active' : ''} type="button" onClick={() => onTabChange('all')}>전체 ({counts.all})</button><button className={activeTab === 'waiting' ? 'active' : ''} type="button" onClick={() => onTabChange('waiting')}>답변 대기 ({counts.waiting})</button><button className={activeTab === 'completed' ? 'active' : ''} type="button" onClick={() => onTabChange('completed')}>답변 완료 ({counts.completed})</button></div><div className="consult-list">{consultations.map((item) => <button type="button" className="consult-item" key={item.consultation_id} onClick={() => onSelect?.(item.consultation_id)}><div className="consult-badges"><StatusBadge tone={consultationStatusTone(item.status)}>{consultationStatusLabel(item.status)}</StatusBadge><StatusBadge tone="blue">{item.department}</StatusBadge></div><strong>{item.title}</strong><div className="consult-meta"><span>{item.patient_display}</span><span>{formatDateTime(item.responded_at ?? item.requested_at)}</span></div></button>)}{consultations.length === 0 && <p className="dashboard-empty">해당하는 협진이 없습니다.</p>}</div></article>
}
