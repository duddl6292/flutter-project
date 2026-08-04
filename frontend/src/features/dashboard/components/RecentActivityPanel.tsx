import type { DashboardActivity } from '../dashboard.types'
import { activityTone, activityTypeLabel, formatTime, PanelTitle, StatusBadge } from './dashboardUi'

export function RecentActivityPanel({ activities }: { activities: DashboardActivity[] }) {
  return <article className="dashboard-panel activity-panel"><PanelTitle title="최근 활동" showMore={false} /><div className="activity-list">{activities.map((activity) => <div className="activity-item" key={activity.activity_id}><time>{formatTime(activity.occurred_at)}</time><div className="activity-line"><span className={`activity-dot ${activityTone(activity.type)}`} /></div><p>{activity.message}</p><StatusBadge tone={activityTone(activity.type)}>{activityTypeLabel(activity.type)}</StatusBadge></div>)}{activities.length === 0 && <p className="dashboard-empty">최근 활동이 없습니다.</p>}</div></article>
}
