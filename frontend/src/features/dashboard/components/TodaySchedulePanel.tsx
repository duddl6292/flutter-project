import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import type { DashboardSchedule } from '../dashboard.types'
import { formatDateTitle, formatTime } from './dashboardUi'

interface Props { selectedDate: string; schedules: DashboardSchedule[]; totalCount: number; onPreviousDate: () => void; onNextDate: () => void }
export function TodaySchedulePanel({ selectedDate, schedules, totalCount, onPreviousDate, onNextDate }: Props) {
  const navigate = useNavigate()
  return <article className="dashboard-panel schedule-panel"><div className="schedule-header"><h2>진료 일정</h2><div className="schedule-date"><span>{formatDateTitle(selectedDate)}</span><button type="button" aria-label="이전 날짜" onClick={onPreviousDate}><ChevronLeft size={17} /></button><button type="button" aria-label="다음 날짜" onClick={onNextDate}><ChevronRight size={17} /></button></div></div><div className="schedule-list">{schedules.map((item) => <div key={item.schedule_id} className={`schedule-item ${item.status === 'in_progress' ? 'current' : ''}`}><time>{formatTime(item.start_at)}</time><div className="schedule-card"><strong>{item.patient_name} 진료</strong><span>{item.room}</span></div></div>)}</div>{schedules.length === 0 && <p className="dashboard-empty">선택한 날짜의 진료 일정이 없습니다.</p>}{totalCount > schedules.length && <button className="dashboard-panel-more" type="button" onClick={() => navigate('/appointments')}>예약 {totalCount - schedules.length}건 더 보기 <ChevronRight size={14} /></button>}</article>
}
