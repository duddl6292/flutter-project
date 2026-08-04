import { AlertTriangle, CheckCircle2, ChevronRight, Clock3, Handshake } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import type { Examination } from '../../examinations/examination.types'
import type { DashboardConsultation } from '../dashboard.types'

interface Props { examinations: Examination[]; consultations: DashboardConsultation[]; loading: boolean }

export function WorkQueuePanel({ examinations, consultations, loading }: Props) {
  const navigate = useNavigate()
  const urgent = examinations.filter((item) => item.overall_interpretation === 'CRITICAL' || item.overall_interpretation === 'ABNORMAL')
  const preliminary = examinations.filter((item) => item.status === 'PRELIMINARY')
  const waitingConsultations = consultations.filter((item) => item.status === 'requested' || item.status === 'waiting')
  const items = [
    ...urgent.map((item) => ({ id: `result-${item.examination_id}`, tone: 'danger', icon: AlertTriangle, title: `${item.patient_name} · ${item.test_name}`, description: `${item.overall_interpretation_label} 결과 확인`, path: `/examinations/${item.examination_id}` })),
    ...preliminary.filter((item) => !urgent.some((urgentItem) => urgentItem.examination_id === item.examination_id)).map((item) => ({ id: `preliminary-${item.examination_id}`, tone: 'warning', icon: Clock3, title: `${item.patient_name} · ${item.test_name}`, description: '최종 결과 확정 대기', path: `/examinations/${item.examination_id}` })),
    ...waitingConsultations.map((item) => ({ id: `consultation-${item.consultation_id}`, tone: 'consultation', icon: Handshake, title: item.title, description: `${item.patient_display} · 협진 답변 대기`, path: `/consultations/${item.consultation_id}` })),
  ].slice(0, 5)

  return (
    <article className="dashboard-panel work-queue-panel">
      <div className="panel-title-row"><div><h2>우선 확인할 업무</h2><p>위험도와 처리 상태를 기준으로 정렬했습니다.</p></div><span>{items.length}</span></div>
      {loading && <p className="dashboard-empty">업무를 불러오는 중입니다.</p>}
      {!loading && items.length === 0 && <div className="work-queue-complete"><CheckCircle2 size={25} /><strong>처리할 긴급 업무가 없습니다.</strong></div>}
      {!loading && <div className="work-queue-list">{items.map((item) => { const Icon = item.icon; return <button type="button" key={item.id} onClick={() => navigate(item.path)}><span className={`work-queue-icon ${item.tone}`}><Icon size={17} /></span><span><strong>{item.title}</strong><small>{item.description}</small></span><ChevronRight size={16} /></button> })}</div>}
    </article>
  )
}
