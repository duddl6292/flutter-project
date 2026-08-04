import {
  CalendarCheck2,
  ChevronDown,
  Download,
  Pill,
  ScanLine,
  Users,
} from 'lucide-react'

import {
  Fragment,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'

import {
  useNavigate,
} from 'react-router-dom'

import {
  AccountPageLayout,
} from '../account/AccountPageLayout'

import {
  getClinicianReportDetails,
  getClinicianSummaryReport,
} from './report.api'

import type {
  ClinicianSummaryReport,
  ReportDetailItem,
  ReportDetailType,
  ReportStatusCount,
} from './report.types'

import './reports.css'

function toDateInputValue(date: Date): string {
  const offset =
    date.getTimezoneOffset() * 60_000

  return new Date(date.getTime() - offset)
    .toISOString()
    .slice(0, 10)
}

function currentMonthPeriod() {
  const today = new Date()
  const start = new Date(
    today.getFullYear(),
    today.getMonth(),
    1,
  )

  return {
    startDate: toDateInputValue(start),
    endDate: toDateInputValue(today),
  }
}

function statusTotal(
  statuses: ReportStatusCount[],
): number {
  return statuses.reduce(
    (total, item) => total + item.count,
    0,
  )
}

function StatusChart({
  title,
  statuses,
  selectedStatus,
  onSelect,
}: {
  title: string
  statuses: ReportStatusCount[]
  selectedStatus: string
  onSelect: (status: string) => void
}) {
  const total = statusTotal(statuses)

  return (
    <section className="report-card">
      <header>
        <div>
          <h2>{title}</h2>
          <p>선택한 기간의 상태별 건수입니다.</p>
        </div>
        <strong>{total}건</strong>
      </header>

      <div className="report-status-list">
        {statuses.map((item) => {
          const percentage = total
            ? item.count / total * 100
            : 0

          return (
            <button
              type="button"
              key={item.status}
              className={
                selectedStatus === item.status
                  ? 'is-selected'
                  : ''
              }
              onClick={() => onSelect(item.status)}
            >
              <div>
                <span>{item.label}</span>
                <strong>{item.count}건</strong>
              </div>
              <span className="report-progress-track">
                <span
                  style={{
                    width: `${percentage}%`,
                  }}
                />
              </span>
            </button>
          )
        })}
      </div>
    </section>
  )
}

const detailTypeLabels: Record<
  ReportDetailType,
  string
> = {
  encounters: '진료 환자',
  appointments: '예약',
  prescriptions: '처방',
  ct_analyses: 'CT 분석',
}

function formatDateTime(value: string | null | undefined) {
  if (!value) return '-'

  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function DetailExpanded({
  item,
}: {
  item: ReportDetailItem
}) {
  const details = item.details

  return (
    <div className="report-detail-expanded">
      {item.type === 'encounters' && (
        <dl>
          <div><dt>진료 유형</dt><dd>{details.encounter_type ?? '-'}</dd></div>
          <div><dt>진료 시작</dt><dd>{formatDateTime(details.started_at)}</dd></div>
          <div><dt>진료 완료</dt><dd>{formatDateTime(details.completed_at)}</dd></div>
        </dl>
      )}

      {item.type === 'appointments' && (
        <dl>
          <div><dt>소요 시간</dt><dd>{details.duration_minutes ?? '-'}분</dd></div>
          <div><dt>장소</dt><dd>{details.location || '-'}</dd></div>
          <div><dt>예약 사유</dt><dd>{details.reason || '-'}</dd></div>
          <div><dt>취소 사유</dt><dd>{details.cancellation_reason || '-'}</dd></div>
        </dl>
      )}

      {item.type === 'prescriptions' && (
        <>
          <p><strong>처방 메모</strong>{details.notes || '-'}</p>
          <div className="report-medicine-details">
            {details.items?.map((medicine) => (
              <div key={`${item.record_id}-${medicine.medicine_name}`}>
                <strong>{medicine.medicine_name}</strong>
                <span>{medicine.dosage}{medicine.dose_unit}</span>
                <span>{medicine.frequency}</span>
                <span>{medicine.route || '-'}</span>
              </div>
            ))}
          </div>
        </>
      )}

      {item.type === 'ct_analyses' && (
        <dl>
          <div><dt>검사 유형</dt><dd>{details.study_type ?? '-'}</dd></div>
          <div><dt>케이스 상태</dt><dd>{details.case_status_label ?? '-'}</dd></div>
          <div><dt>검사 일시</dt><dd>{formatDateTime(details.performed_at)}</dd></div>
          <div><dt>설명</dt><dd>{details.description || '-'}</dd></div>
        </dl>
      )}
    </div>
  )
}

function escapeCsv(value: unknown): string {
  const text = String(value ?? '')

  return `"${text.replaceAll('"', '""')}"`
}

function downloadCsv(
  report: ClinicianSummaryReport,
) {
  const rows: Array<Array<unknown>> = [
    ['BrainOn 의료진 통계 리포트'],
    ['의료진', report.clinician.name],
    [
      '기간',
      `${report.period.start_date} ~ ${
        report.period.end_date
      }`,
    ],
    [],
    ['요약', '값'],
    [
      '진료 환자 수',
      report.summary.patient_count,
    ],
    [
      '예약 완료율',
      `${
        report.summary
          .appointment_completion_rate
      }%`,
    ],
    [
      '처방 건수',
      report.summary.prescription_count,
    ],
    [
      'CT 분석 건수',
      report.summary.ct_analysis_count,
    ],
    [],
    ['일자별 진료', '환자 수'],
    ...report.daily_encounters.map(
      (item) => [item.date, item.count],
    ),
    [],
    ['예약 상태', '건수'],
    ...report.appointment_statuses.map(
      (item) => [item.label, item.count],
    ),
    [],
    ['처방 상태', '건수'],
    ...report.prescription_statuses.map(
      (item) => [item.label, item.count],
    ),
    [],
    ['상위 처방 약품', '건수'],
    ...report.top_medicines.map(
      (item) => [
        item.medicine_name,
        item.count,
      ],
    ),
  ]
  const csv = rows
    .map((row) =>
      row.map(escapeCsv).join(','),
    )
    .join('\r\n')
  const blob = new Blob(
    [`\uFEFF${csv}`],
    {
      type: 'text/csv;charset=utf-8',
    },
  )
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')

  anchor.href = url
  anchor.download = (
    `brainon-report-${
      report.period.start_date
    }-${report.period.end_date}.csv`
  )
  anchor.click()
  URL.revokeObjectURL(url)
}

export function ReportPage() {
  const navigate = useNavigate()
  const detailSectionRef =
    useRef<HTMLElement>(null)
  const initialPeriod = useMemo(
    currentMonthPeriod,
    [],
  )
  const [startDate, setStartDate] =
    useState(initialPeriod.startDate)
  const [endDate, setEndDate] =
    useState(initialPeriod.endDate)
  const [report, setReport] =
    useState<ClinicianSummaryReport | null>(
      null,
    )
  const [loading, setLoading] =
    useState(true)
  const [error, setError] =
    useState('')
  const [detailType, setDetailType] =
    useState<ReportDetailType>('encounters')
  const [detailDate, setDetailDate] =
    useState('')
  const [detailStatus, setDetailStatus] =
    useState('')
  const [detailMedicine, setDetailMedicine] =
    useState('')
  const [detailItems, setDetailItems] =
    useState<ReportDetailItem[]>([])
  const [detailPage, setDetailPage] =
    useState(1)
  const [detailMeta, setDetailMeta] =
    useState({
      page: 1,
      page_size: 20,
      total_count: 0,
      total_pages: 1,
    })
  const [detailLoading, setDetailLoading] =
    useState(true)
  const [detailError, setDetailError] =
    useState('')
  const [expandedRecordId, setExpandedRecordId] =
    useState('')

  useEffect(() => {
    const controller = new AbortController()

    setLoading(true)
    setError('')

    void getClinicianSummaryReport(
      startDate,
      endDate,
      controller.signal,
    )
      .then(setReport)
      .catch((requestError) => {
        if (
          requestError instanceof DOMException
          && requestError.name === 'AbortError'
        ) {
          return
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : '통계 데이터를 불러오지 못했습니다.',
        )
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      })

    return () => controller.abort()
  }, [startDate, endDate])

  useEffect(() => {
    const controller = new AbortController()

    setDetailLoading(true)
    setDetailError('')

    void getClinicianReportDetails({
      type: detailType,
      startDate: detailDate || startDate,
      endDate: detailDate || endDate,
      status: detailStatus,
      medicine: detailMedicine,
      page: detailPage,
      pageSize: 20,
      signal: controller.signal,
    })
      .then((response) => {
        setDetailItems(response.data)
        setDetailMeta(response.meta)
      })
      .catch((requestError) => {
        if (
          requestError instanceof DOMException
          && requestError.name === 'AbortError'
        ) {
          return
        }

        setDetailError(
          requestError instanceof Error
            ? requestError.message
            : '상세 내역을 불러오지 못했습니다.',
        )
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setDetailLoading(false)
        }
      })

    return () => controller.abort()
  }, [
    detailDate,
    detailMedicine,
    detailPage,
    detailStatus,
    detailType,
    endDate,
    startDate,
  ])

  const selectDetails = (
    type: ReportDetailType,
    options: {
      date?: string
      status?: string
      medicine?: string
    } = {},
  ) => {
    setDetailType(type)
    setDetailDate(options.date ?? '')
    setDetailStatus(options.status ?? '')
    setDetailMedicine(options.medicine ?? '')
    setDetailPage(1)
    setExpandedRecordId('')

    window.requestAnimationFrame(() => {
      detailSectionRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
    })
  }

  const resetDetailCriteria = () => {
    setDetailDate('')
    setDetailStatus('')
    setDetailMedicine('')
    setDetailPage(1)
    setExpandedRecordId('')
  }

  const setPreset = (
    preset: 'today' | 'week' | 'month',
  ) => {
    const today = new Date()
    let start = new Date(today)

    if (preset === 'week') {
      const weekday = today.getDay()
      const daysFromMonday =
        weekday === 0 ? 6 : weekday - 1
      start.setDate(
        today.getDate() - daysFromMonday,
      )
    }

    if (preset === 'month') {
      start = new Date(
        today.getFullYear(),
        today.getMonth(),
        1,
      )
    }

    setStartDate(toDateInputValue(start))
    setEndDate(toDateInputValue(today))
    resetDetailCriteria()
  }

  const maxDailyCount = Math.max(
    1,
    ...(report?.daily_encounters.map(
      (item) => item.count,
    ) ?? [0]),
  )
  const maxMedicineCount = Math.max(
    1,
    ...(report?.top_medicines.map(
      (item) => item.count,
    ) ?? [0]),
  )
  const detailStatusLabel = (
    detailType === 'appointments'
      ? report?.appointment_statuses
      : report?.prescription_statuses
  )?.find(
    (item) => item.status === detailStatus,
  )?.label

  return (
    <AccountPageLayout>
      <main className="report-page">
        <header className="report-page-heading">
          <div>
            <h1>통계·리포트</h1>
            <p>
              로그인한 의료진 본인의 업무 데이터를 분석합니다.
            </p>
          </div>

          <button
            type="button"
            className="report-download-button"
            disabled={!report || loading}
            onClick={() => {
              if (report) downloadCsv(report)
            }}
          >
            <Download size={17} />
            CSV 다운로드
          </button>
        </header>

        <section className="report-period-card">
          <div className="report-presets">
            <button
              type="button"
              onClick={() => setPreset('today')}
            >
              오늘
            </button>
            <button
              type="button"
              onClick={() => setPreset('week')}
            >
              이번 주
            </button>
            <button
              type="button"
              onClick={() => setPreset('month')}
            >
              이번 달
            </button>
          </div>

          <div className="report-date-fields">
            <label>
              <span>시작일</span>
              <input
                type="date"
                value={startDate}
                max={endDate}
                onChange={(event) => {
                  setStartDate(event.target.value)
                  resetDetailCriteria()
                }}
              />
            </label>
            <span>~</span>
            <label>
              <span>종료일</span>
              <input
                type="date"
                value={endDate}
                min={startDate}
                onChange={(event) => {
                  setEndDate(event.target.value)
                  resetDetailCriteria()
                }}
              />
            </label>
          </div>
        </section>

        {loading && (
          <p className="report-message">
            통계 데이터를 계산하는 중입니다.
          </p>
        )}

        {error && (
          <p role="alert" className="report-error">
            {error}
          </p>
        )}

        {report && (
          <>
            <p className="report-owner">
              <strong>{report.clinician.name}</strong>
              {' 의료진 · '}
              {report.period.start_date}
              {' ~ '}
              {report.period.end_date}
            </p>

            <section className="report-summary-grid">
              <button
                type="button"
                className={
                  detailType === 'encounters'
                  && !detailDate
                    ? 'is-selected'
                    : ''
                }
                onClick={() =>
                  selectDetails('encounters')
                }
              >
                <div><Users size={22} /></div>
                <span>진료 환자</span>
                <strong>
                  {report.summary.patient_count}
                  <small>명</small>
                </strong>
              </button>
              <button
                type="button"
                className={
                  detailType === 'appointments'
                  && !detailStatus
                    ? 'is-selected'
                    : ''
                }
                onClick={() =>
                  selectDetails('appointments')
                }
              >
                <div><CalendarCheck2 size={22} /></div>
                <span>예약 완료율</span>
                <strong>
                  {report.summary
                    .appointment_completion_rate}
                  <small>%</small>
                </strong>
              </button>
              <button
                type="button"
                className={
                  detailType === 'prescriptions'
                  && !detailStatus
                  && !detailMedicine
                    ? 'is-selected'
                    : ''
                }
                onClick={() =>
                  selectDetails('prescriptions')
                }
              >
                <div><Pill size={22} /></div>
                <span>처방 건수</span>
                <strong>
                  {report.summary.prescription_count}
                  <small>건</small>
                </strong>
              </button>
              <button
                type="button"
                className={
                  detailType === 'ct_analyses'
                    ? 'is-selected'
                    : ''
                }
                onClick={() =>
                  selectDetails('ct_analyses')
                }
              >
                <div><ScanLine size={22} /></div>
                <span>CT 분석</span>
                <strong>
                  {report.summary.ct_analysis_count}
                  <small>건</small>
                </strong>
              </button>
            </section>

            <section className="report-card daily-report-card">
              <header>
                <div>
                  <h2>일자별 진료 추이</h2>
                  <p>진료 완료 환자 수 기준입니다.</p>
                </div>
              </header>

              <div className="daily-chart-scroll">
                <div
                  className="daily-chart"
                  style={{
                    minWidth: `${Math.max(
                      580,
                      report.daily_encounters.length
                        * 38,
                    )}px`,
                  }}
                >
                  {report.daily_encounters.map(
                    (item) => (
                      <button
                        type="button"
                        key={item.date}
                        className={
                          detailType === 'encounters'
                          && detailDate === item.date
                            ? 'is-selected'
                            : ''
                        }
                        title={`${item.date} 진료 상세 보기`}
                        onClick={() =>
                          selectDetails(
                            'encounters',
                            { date: item.date },
                          )
                        }
                      >
                        <span>{item.count}</span>
                        <i
                          style={{
                            height: `${Math.max(
                              item.count
                                / maxDailyCount
                                * 150,
                              item.count ? 8 : 2,
                            )}px`,
                          }}
                        />
                        <small>
                          {item.date.slice(5)}
                        </small>
                      </button>
                    ),
                  )}
                </div>
              </div>
            </section>

            <div className="report-two-column-grid">
              <StatusChart
                title="예약 상태"
                statuses={
                  report.appointment_statuses
                }
                selectedStatus={
                  detailType === 'appointments'
                    ? detailStatus
                    : ''
                }
                onSelect={(status) =>
                  selectDetails(
                    'appointments',
                    { status },
                  )
                }
              />
              <StatusChart
                title="처방 상태"
                statuses={
                  report.prescription_statuses
                }
                selectedStatus={
                  detailType === 'prescriptions'
                    ? detailStatus
                    : ''
                }
                onSelect={(status) =>
                  selectDetails(
                    'prescriptions',
                    { status },
                  )
                }
              />
            </div>

            <section className="report-card">
              <header>
                <div>
                  <h2>많이 처방한 약품 TOP 5</h2>
                  <p>처방 약품 항목의 건수 기준입니다.</p>
                </div>
              </header>

              <div className="top-medicine-list">
                {report.top_medicines.length === 0 && (
                  <p>해당 기간의 처방 약품이 없습니다.</p>
                )}

                {report.top_medicines.map(
                  (medicine, index) => (
                    <button
                      type="button"
                      key={medicine.medicine_name}
                      className={
                        detailMedicine
                          === medicine.medicine_name
                          ? 'is-selected'
                          : ''
                      }
                      onClick={() =>
                        selectDetails(
                          'prescriptions',
                          {
                            medicine:
                              medicine.medicine_name,
                          },
                        )
                      }
                    >
                      <strong>{index + 1}</strong>
                      <span>{medicine.medicine_name}</span>
                      <i>
                        <i
                          style={{
                            width: `${
                              medicine.count
                              / maxMedicineCount
                              * 100
                            }%`,
                          }}
                        />
                      </i>
                      <b>{medicine.count}건</b>
                    </button>
                  ),
                )}
              </div>
            </section>

            <section
              ref={detailSectionRef}
              className="report-card report-detail-card"
            >
              <header>
                <div>
                  <h2>
                    {detailTypeLabels[detailType]}
                    {' 상세 내역'}
                  </h2>
                  <p>
                    {detailDate
                      ? `${detailDate} 기준`
                      : `${startDate} ~ ${endDate}`}
                    {detailStatus
                      ? ` · ${
                        detailStatusLabel
                        ?? detailStatus
                      }`
                      : ''}
                    {detailMedicine
                      ? ` · ${detailMedicine}`
                      : ''}
                  </p>
                </div>
                <strong>
                  총 {detailMeta.total_count}건
                </strong>
              </header>

              {detailError && (
                <p
                  role="alert"
                  className="report-error"
                >
                  {detailError}
                </p>
              )}

              <div className="report-detail-table-wrap">
                <table className="report-detail-table">
                  <thead>
                    <tr>
                      <th>일시</th>
                      <th>환자</th>
                      <th>환자번호</th>
                      <th>참조번호</th>
                      <th>상태</th>
                      <th aria-label="상세 펼치기" />
                    </tr>
                  </thead>
                  <tbody>
                    {detailLoading && (
                      <tr>
                        <td colSpan={6}>
                          상세 내역을 불러오는 중입니다.
                        </td>
                      </tr>
                    )}

                    {!detailLoading
                    && detailItems.length === 0 && (
                      <tr>
                        <td colSpan={6}>
                          선택한 조건의 상세 내역이 없습니다.
                        </td>
                      </tr>
                    )}

                    {!detailLoading
                    && detailItems.map((item) => (
                      <Fragment key={item.record_id}>
                        <tr>
                          <td>
                            {formatDateTime(
                              item.occurred_at,
                            )}
                          </td>
                          <td>
                            <button
                              type="button"
                              className="report-patient-link"
                              disabled={!item.patient_id}
                              onClick={() => {
                                const keyword =
                                  item.patient_number
                                  ?? item.patient_name
                                navigate(
                                  `/patients?search=${
                                    encodeURIComponent(
                                      keyword,
                                    )
                                  }`,
                                )
                              }}
                            >
                              {item.patient_name}
                            </button>
                          </td>
                          <td>
                            {item.patient_number ?? '-'}
                          </td>
                          <td className="report-reference">
                            {item.reference}
                          </td>
                          <td>
                            <span className="report-detail-status">
                              {item.status_label}
                            </span>
                          </td>
                          <td>
                            <button
                              type="button"
                              className="report-expand-button"
                              aria-label="상세정보 펼치기"
                              aria-expanded={
                                expandedRecordId
                                  === item.record_id
                              }
                              onClick={() =>
                                setExpandedRecordId(
                                  (current) =>
                                    current
                                      === item.record_id
                                      ? ''
                                      : item.record_id,
                                )
                              }
                            >
                              <ChevronDown size={17} />
                            </button>
                          </td>
                        </tr>

                        {expandedRecordId
                          === item.record_id && (
                          <tr className="report-expanded-row">
                            <td colSpan={6}>
                              <DetailExpanded item={item} />
                            </td>
                          </tr>
                        )}
                      </Fragment>
                    ))}
                  </tbody>
                </table>
              </div>

              <footer className="report-detail-pagination">
                <button
                  type="button"
                  disabled={
                    detailLoading
                    || detailPage <= 1
                  }
                  onClick={() =>
                    setDetailPage(
                      (current) => current - 1,
                    )
                  }
                >
                  이전
                </button>
                <span>
                  {detailMeta.page}
                  {' / '}
                  {detailMeta.total_pages}
                </span>
                <button
                  type="button"
                  disabled={
                    detailLoading
                    || detailPage
                      >= detailMeta.total_pages
                  }
                  onClick={() =>
                    setDetailPage(
                      (current) => current + 1,
                    )
                  }
                >
                  다음
                </button>
              </footer>
            </section>
          </>
        )}
      </main>
    </AccountPageLayout>
  )
}
