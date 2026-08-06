import { CalendarPlus, ClipboardCheck, FileText, Handshake, Stethoscope, UserPlus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function QuickActionsPanel() {
  const navigate = useNavigate()
  const actions = [
    { label: '환자 관리', icon: UserPlus, path: '/patients' },
    { label: '예약 관리', icon: CalendarPlus, path: '/appointments' },
    { label: '진료 관리', icon: Stethoscope, path: '/encounters' },
    { label: '처방 작성', icon: FileText, path: '/prescriptions' },
    { label: '검사결과 작성', icon: ClipboardCheck, path: '/examinations?create=1' },
    { label: '협진 관리', icon: Handshake, path: '/consultations' },
  ]
  return <article className="dashboard-panel quick-panel"><h2>빠른 실행</h2><div className="quick-grid">{actions.map((action) => { const Icon = action.icon; return <button key={action.label} type="button" onClick={() => navigate(action.path)}><Icon size={24} /><span>{action.label}</span></button> })}</div></article>
}
