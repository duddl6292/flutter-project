import type {
  DashboardConsultation,
} from '../dashboard.types'
import {
  consultationStatusLabel,
  consultationStatusTone,
  formatDateTime,
  PanelTitle,
  StatusBadge,
} from './dashboardUi'

export type ConsultationTab =
  | 'all'
  | 'waiting'
  | 'completed'

interface ConsultationCounts {
  all: number
  waiting: number
  completed: number
}

interface ConsultationPanelProps {
  consultations: DashboardConsultation[]
  activeTab: ConsultationTab
  counts: ConsultationCounts
  onTabChange: (tab: ConsultationTab) => void
}

export function ConsultationPanel({
  consultations,
  activeTab,
  counts,
  onTabChange,
}: ConsultationPanelProps) {
  return (
    <article className="dashboard-panel">
      <PanelTitle title="협진 요청 현황" />

      <div className="consult-tabs">
        <button
          className={
            activeTab === 'all' ? 'active' : ''
          }
          type="button"
          onClick={() => onTabChange('all')}
        >
          전체 ({counts.all})
        </button>

        <button
          className={
            activeTab === 'waiting'
              ? 'active'
              : ''
          }
          type="button"
          onClick={() => onTabChange('waiting')}
        >
          응답 대기 ({counts.waiting})
        </button>

        <button
          className={
            activeTab === 'completed'
              ? 'active'
              : ''
          }
          type="button"
          onClick={() => onTabChange('completed')}
        >
          응답 완료 ({counts.completed})
        </button>
      </div>

      <div className="consult-list">
        {consultations.map((request) => (
          <div
            className="consult-item"
            key={request.consultation_id}
          >
            <div className="consult-badges">
              <StatusBadge
                tone={consultationStatusTone(
                  request.status,
                )}
              >
                {consultationStatusLabel(
                  request.status,
                )}
              </StatusBadge>

              <StatusBadge tone="blue">
                {request.department}
              </StatusBadge>
            </div>

            <strong>{request.title}</strong>

            <div className="consult-meta">
              <span>{request.patient_display}</span>
              <span>
                {formatDateTime(
                  request.responded_at
                    ?? request.requested_at,
                )}
              </span>
            </div>
          </div>
        ))}
      </div>
    </article>
  )
}
