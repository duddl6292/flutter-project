import type { LucideIcon } from 'lucide-react'

export interface SummaryItem {
  title: string
  value: number
  unit: string
  detail: string
  icon: LucideIcon
  color: string
  background: string
}

interface SummaryCardsProps {
  items: SummaryItem[]
  loading: boolean
}

export function SummaryCards({
  items,
  loading,
}: SummaryCardsProps) {
  return (
    <section className="summary-grid">
      {items.map((item) => {
        const Icon = item.icon

        return (
          <article
            className="summary-card"
            key={item.title}
          >
            <div
              className="summary-icon"
              style={{
                color: item.color,
                backgroundColor:
                  item.background,
              }}
            >
              <Icon size={34} />
            </div>

            <div>
              <h3>{item.title}</h3>
              <div className="summary-value">
                <strong>
                  {loading ? '-' : item.value}
                </strong>
                <span>{item.unit}</span>
              </div>
              <p>
                {loading
                  ? '불러오는 중'
                  : item.detail}
              </p>
            </div>
          </article>
        )
      })}
    </section>
  )
}
