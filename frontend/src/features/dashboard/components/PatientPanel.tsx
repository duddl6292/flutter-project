import { useNavigate } from 'react-router-dom'

import type { DashboardPatient } from '../dashboard.types'
import { formatDateTime, genderLabel, PanelTitle, patientStatusLabel, patientStatusTone, StatusBadge } from './dashboardUi'

interface Props { patients: DashboardPatient[]; loading: boolean }
export function PatientPanel({ patients, loading }: Props) {
  const navigate = useNavigate()
  return <article className="dashboard-panel patient-panel"><PanelTitle title="오늘 진료 환자" onShowMore={() => navigate('/patients')} /><div className="table-wrapper"><table className="patient-table"><thead><tr><th>환자 ID</th><th>이름</th><th>나이</th><th>성별</th><th>진료과</th><th>예약일시</th><th>상태</th></tr></thead><tbody>{patients.map((patient) => <tr key={patient.patient_id} onClick={() => navigate(`/patients/${patient.patient_id}`)}><td className="patient-id">{patient.patient_id}</td><td>{patient.name}</td><td>{patient.age}</td><td>{genderLabel(patient.gender)}</td><td>{patient.department}</td><td>{formatDateTime(patient.appointment_at)}</td><td><StatusBadge tone={patientStatusTone(patient.status)}>{patientStatusLabel(patient.status)}</StatusBadge></td></tr>)}{!loading && patients.length === 0 && <tr><td colSpan={7} className="dashboard-empty">표시할 환자가 없습니다.</td></tr>}</tbody></table></div></article>
}
