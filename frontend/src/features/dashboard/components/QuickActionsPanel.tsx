import {
  CalendarPlus,
  ClipboardCheck,
  FileText,
  UserPlus,
} from 'lucide-react'

export function QuickActionsPanel() {
  return (
    <article className="dashboard-panel quick-panel">
      <h2>빠른 실행</h2>
      <div className="quick-grid">
        <button type="button">
          <UserPlus size={26} />
          <span>환자 등록</span>
        </button>
        <button type="button">
          <CalendarPlus size={26} />
          <span>예약 등록</span>
        </button>
        <button type="button">
          <FileText size={26} />
          <span>처방전 작성</span>
        </button>
        <button type="button">
          <ClipboardCheck size={26} />
          <span>검사 결과 작성</span>
        </button>
      </div>
    </article>
  )
}
