import type {
  DashboardActivity,
} from '../dashboard.types'
import {
  activityTone,
  activityTypeLabel,
  formatTime,
  PanelTitle,
  StatusBadge,
} from './dashboardUi'

interface RecentActivityPanelProps {
  activities: DashboardActivity[]
}

export function RecentActivityPanel({
  activities,
}: RecentActivityPanelProps) {
  return (
    <article className="dashboard-panel activity-panel">
      <PanelTitle title="최근 활동" />

      <div className="activity-list">
        {activities.map((activity) => (
          <div
            className="activity-item"
            key={activity.activity_id}
          >
            <time>
              {formatTime(activity.occurred_at)}
            </time>
            <div className="activity-line">
              <span
                className={`activity-dot ${
                  activityTone(activity.type)
                }`}
              />
            </div>
            <p>{activity.message}</p>
            <StatusBadge
              tone={activityTone(activity.type)}
            >
              {activityTypeLabel(activity.type)}
            </StatusBadge>
          </div>
        ))}
      </div>
    </article>
  )
}
