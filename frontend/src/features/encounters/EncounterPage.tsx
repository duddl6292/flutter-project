import {
  ClipboardPenLine,
  Pill,
  Save,
  ScanLine,
  Search,
  Stethoscope,
} from 'lucide-react'
import {
  useEffect,
  useState,
} from 'react'
import { useNavigate } from 'react-router-dom'

import {
  AccountPageLayout,
} from '../account/AccountPageLayout'

import {
  getEncounter,
  getEncounters,
  saveClinicalRecord,
  updateEncounterStatus,
} from './encounter.api'
import type {
  ClinicalRecordInput,
  EncounterDetail,
  EncounterStatus,
  EncounterSummary,
} from './encounter.types'

import './encounters.css'

const emptyRecord: ClinicalRecordInput = {
  chief_complaint: '',
  subjective: '',
  objective: '',
  assessment: '',
  plan: '',
  patient_visible_summary: '',
}

const statusOptions: Array<{
  value: EncounterStatus | ''
  label: string
}> = [
  { value: '', label: '전체 상태' },
  { value: 'REGISTERED', label: '등록' },
  { value: 'ARRIVED', label: '도착' },
  { value: 'IN_PROGRESS', label: '진료 중' },
  { value: 'COMPLETED', label: '완료' },
  { value: 'CANCELLED', label: '취소' },
]

function toDateKey(date: Date): string {
  const offset = date.getTimezoneOffset() * 60_000

  return new Date(date.getTime() - offset)
    .toISOString()
    .slice(0, 10)
}

function formatDateTime(
  value: string | null,
): string {
  if (!value) return '-'

  return new Intl.DateTimeFormat('ko-KR', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function nextStatusAction(status: EncounterStatus) {
  if (status === 'ARRIVED') {
    return {
      status: 'IN_PROGRESS' as const,
      label: '진료 시작',
    }
  }
  if (status === 'IN_PROGRESS') {
    return {
      status: 'COMPLETED' as const,
      label: '진료 완료',
    }
  }

  return null
}

export function EncounterPage() {
  const navigate = useNavigate()
  const today = toDateKey(new Date())
  const [dateFrom, setDateFrom] = useState(today)
  const [dateTo, setDateTo] = useState(today)
  const [searchText, setSearchText] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] =
    useState<EncounterStatus | ''>('')
  const [page, setPage] = useState(1)
  const [encounters, setEncounters] =
    useState<EncounterSummary[]>([])
  const [totalPages, setTotalPages] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [listLoading, setListLoading] = useState(true)
  const [listError, setListError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const [selectedId, setSelectedId] = useState('')
  const [detail, setDetail] =
    useState<EncounterDetail | null>(null)
  const [detailLoading, setDetailLoading] =
    useState(false)
  const [detailError, setDetailError] = useState('')
  const [record, setRecord] =
    useState<ClinicalRecordInput>(emptyRecord)
  const [recordSaving, setRecordSaving] = useState(false)
  const [statusSaving, setStatusSaving] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    setListLoading(true)
    setListError('')

    void getEncounters({
      dateFrom,
      dateTo,
      status: statusFilter,
      search,
      page,
      pageSize: 20,
      signal: controller.signal,
    })
      .then((response) => {
        setEncounters(response.data)
        setTotalPages(response.meta.total_pages)
        setTotalCount(response.meta.total_count)

        setSelectedId((current) => {
          if (
            current
            && response.data.some(
              (item) => item.encounter_id === current,
            )
          ) {
            return current
          }

          return response.data[0]?.encounter_id ?? ''
        })

        if (response.data.length === 0) setDetail(null)
      })
      .catch((requestError) => {
        if (
          requestError instanceof DOMException
          && requestError.name === 'AbortError'
        ) return

        setListError(
          requestError instanceof Error
            ? requestError.message
            : '진료 목록을 불러오지 못했습니다.',
        )
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setListLoading(false)
        }
      })

    return () => controller.abort()
  }, [
    dateFrom,
    dateTo,
    page,
    reloadKey,
    search,
    statusFilter,
  ])

  useEffect(() => {
    if (!selectedId) return

    const controller = new AbortController()
    setDetailLoading(true)
    setDetailError('')

    void getEncounter(selectedId, controller.signal)
      .then((response) => {
        setDetail(response)
        const saved = response.clinical_record
        setRecord(
          saved
            ? {
              chief_complaint: saved.chief_complaint,
              subjective: saved.subjective,
              objective: saved.objective,
              assessment: saved.assessment,
              plan: saved.plan,
              patient_visible_summary:
                saved.patient_visible_summary,
            }
            : emptyRecord,
        )
      })
      .catch((requestError) => {
        if (
          requestError instanceof DOMException
          && requestError.name === 'AbortError'
        ) return

        setDetailError(
          requestError instanceof Error
            ? requestError.message
            : '진료 상세정보를 불러오지 못했습니다.',
        )
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setDetailLoading(false)
        }
      })

    return () => controller.abort()
  }, [selectedId])

  const updateRecordField = (
    field: keyof ClinicalRecordInput,
    value: string,
  ) => {
    setRecord((current) => ({
      ...current,
      [field]: value,
    }))
  }

  const refresh = () => {
    setReloadKey((current) => current + 1)
  }

  const handleStatusChange = async (
    newStatus: EncounterStatus,
  ) => {
    if (!detail) return

    setStatusSaving(true)
    setDetailError('')

    try {
      const updated = await updateEncounterStatus(
        detail.encounter_id,
        newStatus,
      )
      setDetail(updated)
      refresh()
    } catch (requestError) {
      setDetailError(
        requestError instanceof Error
          ? requestError.message
          : '진료 상태를 변경하지 못했습니다.',
      )
    } finally {
      setStatusSaving(false)
    }
  }

  const action = detail
    ? nextStatusAction(detail.status)
    : null

  return (
    <AccountPageLayout>
      <main className="encounter-page">
        <header className="encounter-page-heading">
          <div>
            <h1>진료 관리</h1>
            <p>
              접수된 환자의 진료 시작, SOAP 기록과 완료를 관리합니다.
            </p>
          </div>
        </header>

        <section className="encounter-toolbar">
          <form
            className="encounter-search"
            onSubmit={(event) => {
              event.preventDefault()
              setPage(1)
              setSearch(searchText.trim())
            }}
          >
            <Search size={17} />
            <input
              value={searchText}
              placeholder="환자명, 환자번호, 진료번호 검색"
              onChange={(event) =>
                setSearchText(event.target.value)
              }
            />
            <button type="submit">검색</button>
          </form>

          <label>
            <span>시작일</span>
            <input
              type="date"
              value={dateFrom}
              max={dateTo}
              onChange={(event) => {
                setPage(1)
                setDateFrom(event.target.value)
              }}
            />
          </label>
          <label>
            <span>종료일</span>
            <input
              type="date"
              value={dateTo}
              min={dateFrom}
              onChange={(event) => {
                setPage(1)
                setDateTo(event.target.value)
              }}
            />
          </label>
          <select
            aria-label="진료 상태"
            value={statusFilter}
            onChange={(event) => {
              setPage(1)
              setStatusFilter(
                event.target.value as EncounterStatus | '',
              )
            }}
          >
            {statusOptions.map((option) => (
              <option
                key={option.value}
                value={option.value}
              >
                {option.label}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => {
              setPage(1)
              setDateFrom(today)
              setDateTo(today)
            }}
          >
            오늘
          </button>
        </section>

        {listError && (
          <p className="encounter-error" role="alert">
            {listError}
          </p>
        )}

        <div className="encounter-workspace">
          <section className="encounter-list-card">
            <header>
              <h2>진료 환자</h2>
              <strong>{totalCount}건</strong>
            </header>

            <div className="encounter-list">
              {listLoading && (
                <p>진료 목록을 불러오는 중입니다.</p>
              )}
              {!listLoading && encounters.length === 0 && (
                <p>선택한 조건의 진료가 없습니다.</p>
              )}
              {!listLoading && encounters.map((encounter) => (
                <button
                  type="button"
                  key={encounter.encounter_id}
                  className={
                    selectedId === encounter.encounter_id
                      ? 'is-selected'
                      : ''
                  }
                  onClick={() =>
                    setSelectedId(encounter.encounter_id)
                  }
                >
                  <div>
                    <strong>{encounter.patient_name}</strong>
                    <span>{encounter.patient_number ?? '임시 환자'}</span>
                  </div>
                  <small>
                    {formatDateTime(
                      encounter.arrived_at
                      ?? encounter.scheduled_at,
                    )}
                    {' · '}
                    {encounter.encounter_type_label}
                  </small>
                  <span
                    className={`encounter-status encounter-status-${
                      encounter.status.toLowerCase()
                    }`}
                  >
                    {encounter.status_label}
                  </span>
                </button>
              ))}
            </div>

            <footer className="encounter-pagination">
              <button
                type="button"
                disabled={page <= 1 || listLoading}
                onClick={() => setPage(page - 1)}
              >
                이전
              </button>
              <span>{page} / {totalPages}</span>
              <button
                type="button"
                disabled={page >= totalPages || listLoading}
                onClick={() => setPage(page + 1)}
              >
                다음
              </button>
            </footer>
          </section>

          <section className="encounter-detail-card">
            {!selectedId && (
              <div className="encounter-detail-empty">
                <Stethoscope size={38} />
                <p>진료 환자를 선택해주세요.</p>
              </div>
            )}

            {detailLoading && (
              <div className="encounter-detail-empty">
                <p>진료 상세정보를 불러오는 중입니다.</p>
              </div>
            )}

            {detailError && (
              <p className="encounter-error" role="alert">
                {detailError}
              </p>
            )}

            {detail && !detailLoading && (
              <>
                <header className="encounter-patient-header">
                  <div>
                    <div>
                      <h2>{detail.patient_name}</h2>
                      <span>{detail.status_label}</span>
                    </div>
                    <p>
                      {detail.patient_number ?? '임시 환자'}
                      {' · '}
                      {detail.patient_birth_date ?? '생년월일 미등록'}
                      {' · '}
                      {detail.patient_sex ?? '성별 미상'}
                    </p>
                    <small>
                      {detail.encounter_number}
                      {' · '}
                      {detail.appointment_reason || '진료 사유 미입력'}
                    </small>
                  </div>
                  <div className="encounter-header-actions">
                    {detail.patient_id && (
                      <button
                        type="button"
                        onClick={() =>
                          navigate(
                            `/patients?search=${
                              encodeURIComponent(
                                detail.patient_number
                                ?? detail.patient_name,
                              )
                            }`,
                          )
                        }
                      >
                        환자 정보
                      </button>
                    )}
                    {action && (
                      <button
                        type="button"
                        className="encounter-primary-button"
                        disabled={
                          statusSaving
                          || (
                            action.status === 'COMPLETED'
                            && !detail.clinical_record
                          )
                        }
                        title={
                          action.status === 'COMPLETED'
                          && !detail.clinical_record
                            ? 'SOAP 진료기록을 먼저 저장해주세요.'
                            : undefined
                        }
                        onClick={() =>
                          void handleStatusChange(action.status)
                        }
                      >
                        {action.label}
                      </button>
                    )}
                  </div>
                </header>

                <div className="encounter-timeline">
                  <span>도착 {formatDateTime(detail.arrived_at)}</span>
                  <span>시작 {formatDateTime(detail.started_at)}</span>
                  <span>완료 {formatDateTime(detail.completed_at)}</span>
                </div>

                <section className="encounter-record-section">
                  <header>
                    <div>
                      <ClipboardPenLine size={19} />
                      <h3>SOAP 진료기록</h3>
                    </div>
                    <button
                      type="button"
                      className="encounter-primary-button"
                      disabled={recordSaving}
                      onClick={() => {
                        setRecordSaving(true)
                        setDetailError('')

                        void saveClinicalRecord(
                          detail.encounter_id,
                          record,
                        )
                          .then((saved) => {
                            setDetail((current) =>
                              current
                                ? {
                                  ...current,
                                  clinical_record: saved,
                                }
                                : current,
                            )
                          })
                          .catch((requestError) => {
                            setDetailError(
                              requestError instanceof Error
                                ? requestError.message
                                : '진료기록 저장에 실패했습니다.',
                            )
                          })
                          .finally(() =>
                            setRecordSaving(false),
                          )
                      }}
                    >
                      <Save size={16} />
                      {recordSaving ? '저장 중...' : '기록 저장'}
                    </button>
                  </header>

                  <label className="encounter-field-full">
                    <span>주호소</span>
                    <textarea
                      value={record.chief_complaint}
                      placeholder="환자가 가장 불편해하는 증상"
                      onChange={(event) =>
                        updateRecordField(
                          'chief_complaint',
                          event.target.value,
                        )
                      }
                    />
                  </label>

                  <div className="encounter-soap-grid">
                    <label>
                      <span>S · 주관적 정보</span>
                      <textarea
                        value={record.subjective}
                        onChange={(event) =>
                          updateRecordField(
                            'subjective',
                            event.target.value,
                          )
                        }
                      />
                    </label>
                    <label>
                      <span>O · 객관적 정보</span>
                      <textarea
                        value={record.objective}
                        onChange={(event) =>
                          updateRecordField(
                            'objective',
                            event.target.value,
                          )
                        }
                      />
                    </label>
                    <label>
                      <span>A · 평가</span>
                      <textarea
                        value={record.assessment}
                        onChange={(event) =>
                          updateRecordField(
                            'assessment',
                            event.target.value,
                          )
                        }
                      />
                    </label>
                    <label>
                      <span>P · 계획</span>
                      <textarea
                        value={record.plan}
                        onChange={(event) =>
                          updateRecordField(
                            'plan',
                            event.target.value,
                          )
                        }
                      />
                    </label>
                  </div>

                  <label className="encounter-field-full">
                    <span>환자 앱 공개 요약</span>
                    <textarea
                      value={record.patient_visible_summary}
                      placeholder="환자가 이해하기 쉬운 내용으로 작성해주세요."
                      onChange={(event) =>
                        updateRecordField(
                          'patient_visible_summary',
                          event.target.value,
                        )
                      }
                    />
                  </label>
                </section>

                <div className="encounter-related-grid">
                  <section>
                    <header>
                      <div><Pill size={18} /><h3>처방</h3></div>
                      <button
                        type="button"
                        onClick={() => navigate('/prescriptions')}
                      >
                        처방 관리
                      </button>
                    </header>
                    {detail.prescriptions.length === 0
                      ? <p>연결된 처방이 없습니다.</p>
                      : detail.prescriptions.map((prescription) => (
                        <article key={prescription.prescription_id}>
                          <strong>
                            {prescription.medicine_names.join(', ')}
                          </strong>
                          <span>{prescription.status_label}</span>
                        </article>
                      ))}
                  </section>

                  <section>
                    <header>
                      <div><ScanLine size={18} /><h3>CT 결과</h3></div>
                    </header>
                    {detail.ct_cases.length === 0
                      ? <p>연결된 CT 검사가 없습니다.</p>
                      : detail.ct_cases.map((ctCase) => (
                        <article key={ctCase.case_id}>
                          <strong>{ctCase.study_type_label}</strong>
                          <span>{ctCase.status_label}</span>
                        </article>
                      ))}
                  </section>
                </div>
              </>
            )}
          </section>
        </div>
      </main>
    </AccountPageLayout>
  )
}
