import { ChevronRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import type { Examination } from '../../examinations/examination.types'

interface Props { examinations: Examination[]; loading: boolean }

const formatDate = (value: string | null) => value
  ? new Intl.DateTimeFormat('ko-KR', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
  : '-'

export function ExaminationOverviewPanel({ examinations, loading }: Props) {
  const navigate = useNavigate()
  return (
    <article className="dashboard-panel examination-overview-panel">
      <div className="panel-title-row"><h2>최근 검사결과</h2><button className="text-button" type="button" onClick={() => navigate('/examinations')}>전체 보기 <ChevronRight size={15} /></button></div>
      <div className="dashboard-examination-list">
        {loading && <p className="dashboard-empty">검사결과를 불러오는 중입니다.</p>}
        {!loading && examinations.length === 0 && <p className="dashboard-empty">최근 검사결과가 없습니다.</p>}
        {!loading && examinations.slice(0, 5).map((item) => (
          <button type="button" key={item.examination_id} onClick={() => navigate(`/examinations/${item.examination_id}`)}>
            <span className={`dashboard-result-dot result-${item.overall_interpretation.toLowerCase()}`} />
            <span className="dashboard-result-main"><strong>{item.test_name}</strong><small>{item.patient_name} · {item.patient_number ?? '-'}</small></span>
            <span className="dashboard-result-meta"><strong>{item.overall_interpretation_label}</strong><small>{formatDate(item.performed_at)}</small></span>
            <ChevronRight size={16} />
          </button>
        ))}
      </div>
    </article>
  )
}
