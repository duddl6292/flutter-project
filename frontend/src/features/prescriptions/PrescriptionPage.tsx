import {
  FilePlus2,
  Search,
} from 'lucide-react'

import {
  useCallback,
  useEffect,
  useState,
} from 'react'

import {
  AccountPageLayout,
} from '../account/AccountPageLayout'

import {
  getPrescriptions,
} from './prescription.api'

import {
  PrescriptionCreateModal,
} from './PrescriptionCreateModal'

import {
  PrescriptionDetailModal,
} from './PrescriptionDetailModal'

import type {
  Prescription,
  PrescriptionListMeta,
  PrescriptionStatus,
} from './prescription.types'

import './prescriptions.css'

const initialMeta: PrescriptionListMeta = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
}

const statusOptions: Array<{
  value: PrescriptionStatus | ''
  label: string
}> = [
  { value: '', label: '전체 상태' },
  { value: 'DRAFT', label: '작성 중' },
  { value: 'ACTIVE', label: '처방 중' },
  { value: 'COMPLETED', label: '처방 완료' },
  { value: 'DISCONTINUED', label: '중단' },
  { value: 'CANCELLED', label: '취소' },
]

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(
    'ko-KR',
    {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    },
  ).format(new Date(value))
}

export function PrescriptionPage() {
  const [prescriptions, setPrescriptions] =
    useState<Prescription[]>([])
  const [meta, setMeta] =
    useState(initialMeta)
  const [searchText, setSearchText] =
    useState('')
  const [submittedSearch, setSubmittedSearch] =
    useState('')
  const [statusFilter, setStatusFilter] =
    useState<PrescriptionStatus | ''>('')
  const [page, setPage] = useState(1)
  const [loading, setLoading] =
    useState(true)
  const [error, setError] =
    useState('')
  const [createOpen, setCreateOpen] =
    useState(false)
  const [selected, setSelected] =
    useState<Prescription | null>(null)
  const [reloadKey, setReloadKey] =
    useState(0)

  const loadPrescriptions = useCallback(
    async (signal?: AbortSignal) => {
      setLoading(true)
      setError('')

      try {
        const response =
          await getPrescriptions({
            search: submittedSearch,
            status: statusFilter,
            page,
            pageSize: 20,
            signal,
          })

        setPrescriptions(response.data)
        setMeta(response.meta)
      } catch (requestError) {
        if (
          requestError instanceof DOMException
          && requestError.name === 'AbortError'
        ) {
          return
        }

        setError(
          requestError instanceof Error
            ? requestError.message
            : '처방 목록을 불러오지 못했습니다.',
        )
      } finally {
        if (!signal?.aborted) setLoading(false)
      }
    },
    [
      page,
      reloadKey,
      statusFilter,
      submittedSearch,
    ],
  )

  useEffect(() => {
    const controller = new AbortController()
    void loadPrescriptions(controller.signal)

    return () => controller.abort()
  }, [loadPrescriptions])

  const refresh = () => {
    setReloadKey((current) => current + 1)
  }

  return (
    <AccountPageLayout>
      <main className="prescription-page">
        <header className="prescription-page-heading">
          <div>
            <h1>처방 관리</h1>
            <p>
              환자의 진료기록에 연결된 처방전을 작성하고 관리합니다.
            </p>
          </div>

          <button
            type="button"
            className="prescription-primary-button"
            onClick={() => setCreateOpen(true)}
          >
            <FilePlus2 size={18} />
            새 처방전
          </button>
        </header>

        <section className="prescription-list-card">
          <header className="prescription-list-toolbar">
            <form
              className="prescription-search"
              onSubmit={(event) => {
                event.preventDefault()
                setPage(1)
                setSubmittedSearch(
                  searchText.trim(),
                )
              }}
            >
              <Search size={18} />
              <input
                type="search"
                enterKeyHint="search"
                value={searchText}
                placeholder="환자명, 환자번호, 약품명 검색"
                onChange={(event) =>
                  setSearchText(
                    event.target.value,
                  )
                }
              />
              <button type="submit">검색</button>
            </form>

            <select
              aria-label="처방 상태"
              value={statusFilter}
              onChange={(event) => {
                setPage(1)
                setStatusFilter(
                  event.target.value as (
                    PrescriptionStatus | ''
                  ),
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
          </header>

          <div className="prescription-list-summary">
            총 <strong>{meta.total_count}</strong>건
          </div>

          {error && (
            <p
              role="alert"
              className="prescription-error"
            >
              {error}
            </p>
          )}

          <div className="prescription-table-wrap">
            <table className="prescription-table">
              <thead>
                <tr>
                  <th>환자번호</th>
                  <th>환자명</th>
                  <th>처방일</th>
                  <th>처방 약품</th>
                  <th>상태</th>
                  <th aria-label="상세" />
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr>
                    <td colSpan={6}>
                      처방 목록을 불러오는 중입니다.
                    </td>
                  </tr>
                )}

                {!loading
                  && prescriptions.length === 0
                  && (
                    <tr>
                      <td colSpan={6}>
                        조건에 맞는 처방전이 없습니다.
                      </td>
                    </tr>
                  )}

                {!loading
                  && prescriptions.map(
                    (prescription) => (
                      <tr
                        key={
                          prescription.prescription_id
                        }
                      >
                        <td>
                          {prescription.patient_number
                            ?? '-'}
                        </td>
                        <td>
                          <strong>
                            {prescription.patient_name}
                          </strong>
                        </td>
                        <td>
                          {formatDate(
                            prescription.prescribed_at,
                          )}
                        </td>
                        <td>
                          {prescription.items[0]
                            ?.medicine_name ?? '-'}
                          {prescription.items.length > 1
                            ? ` 외 ${
                              prescription.items.length - 1
                            }개`
                            : ''}
                        </td>
                        <td>
                          <span
                            className={`prescription-status prescription-status-${
                              prescription.status.toLowerCase()
                            }`}
                          >
                            {prescription.status_label}
                          </span>
                        </td>
                        <td>
                          <button
                            type="button"
                            className="prescription-detail-button"
                            onClick={() =>
                              setSelected(prescription)
                            }
                          >
                            상세 보기
                          </button>
                        </td>
                      </tr>
                    ),
                  )}
              </tbody>
            </table>
          </div>

          <footer className="prescription-pagination">
            <button
              type="button"
              disabled={page <= 1 || loading}
              onClick={() =>
                setPage((current) => current - 1)
              }
            >
              이전
            </button>
            <span>
              {meta.page} / {meta.total_pages}
            </span>
            <button
              type="button"
              disabled={
                page >= meta.total_pages
                || loading
              }
              onClick={() =>
                setPage((current) => current + 1)
              }
            >
              다음
            </button>
          </footer>
        </section>
      </main>

      {createOpen && (
        <PrescriptionCreateModal
          onClose={() => setCreateOpen(false)}
          onCreated={(prescription) => {
            setCreateOpen(false)
            setSelected(prescription)
            setPage(1)
            refresh()
          }}
        />
      )}

      {selected && (
        <PrescriptionDetailModal
          prescription={selected}
          onClose={() => setSelected(null)}
          onUpdated={(prescription) => {
            setSelected(prescription)
            refresh()
          }}
        />
      )}
    </AccountPageLayout>
  )
}
