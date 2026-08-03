import {
  useEffect,
  useRef,
  useState,
} from 'react'
import {
  useNavigate,
  useSearchParams,
} from 'react-router-dom'

import {
  logout,
} from '../../core/api/authApi'

import {
  useAuthStore,
} from '../../core/auth/authStore'

import {
  DashboardHeader,
} from '../dashboard/components/DashboardHeader'

import {
  DashboardSidebar,
} from '../dashboard/components/DashboardSidebar'

import {
  getPatients,
} from './patient.api'

import type {
  PatientListMeta,
  PatientStatus,
  PatientSummary,
} from './patient.types'

import '../dashboard/dashboard.css'
import './patients.css'

const initialMeta: PatientListMeta = {
  page: 1,
  page_size: 20,
  total_count: 0,
  total_pages: 1,
}

function sexLabel(
  sex: PatientSummary['sex'],
): string {
  if (sex === 'M') return '남'
  if (sex === 'F') return '여'
  return '미상'
}

function statusLabel(
  status: PatientStatus,
): string {
  const labels: Record<
    PatientStatus,
    string
  > = {
    ACTIVE: '활성',
    INACTIVE: '비활성',
    MERGED: '통합됨',
  }

  return labels[status]
}

function calculateAge(
  birthDate: string | null,
): string {
  if (!birthDate) return '-'

  const birth = new Date(birthDate)

  if (
    Number.isNaN(birth.getTime())
  ) {
    return '-'
  }

  const today = new Date()

  let age =
    today.getFullYear()
    - birth.getFullYear()

  const birthdayPassed =
    today.getMonth()
      > birth.getMonth()
    || (
      today.getMonth()
        === birth.getMonth()
      && today.getDate()
        >= birth.getDate()
    )

  if (!birthdayPassed) {
    age -= 1
  }

  return String(age)
}

export function PatientListPage() {
  const navigate = useNavigate()
  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams()

  const initialSearch =
    searchParams.get('search')
    ?? ''

  const searchInputRef =
    useRef<HTMLInputElement>(null)

  const clinician =
    useAuthStore(
      (state) => state.clinician,
    )

  const [patients, setPatients] =
    useState<PatientSummary[]>([])

  const [meta, setMeta] =
    useState<PatientListMeta>(
      initialMeta,
    )

  const [searchText, setSearchText] =
    useState(initialSearch)

  const [
    submittedSearch,
    setSubmittedSearch,
  ] = useState(initialSearch)

  const [statusFilter, setStatusFilter] =
    useState<PatientStatus | ''>('')

  const [page, setPage] =
    useState(1)

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState('')

  const doctor = {
    name:
      clinician?.name
      ?? '의료진',

    department:
      clinician?.department_name
      ?? '-',

    title:
      '의료진',
  }

  const handleLogout = () => {
    logout()

    navigate(
      '/login',
      { replace: true },
    )
  }

  useEffect(() => {
    const handleShortcut = (
      event: KeyboardEvent,
    ) => {
      if (
        (
          event.ctrlKey
          || event.metaKey
        )
        && event.key.toLowerCase()
          === 'k'
      ) {
        event.preventDefault()
        searchInputRef.current?.focus()
      }
    }

    window.addEventListener(
      'keydown',
      handleShortcut,
    )

    return () => {
      window.removeEventListener(
        'keydown',
        handleShortcut,
      )
    }
  }, [])

  useEffect(() => {
    const controller =
      new AbortController()

    const loadPatients = async () => {
      setLoading(true)
      setError('')

      try {
        const response =
          await getPatients({
            search: submittedSearch,
            status: statusFilter,
            page,
            pageSize: 20,
            signal: controller.signal,
          })

        setPatients(response.data)
        setMeta(response.meta)
      } catch (requestError) {
        if (
          requestError
            instanceof DOMException
          && requestError.name
            === 'AbortError'
        ) {
          return
        }

        setError(
          requestError
            instanceof Error
            ? requestError.message
            : '환자 목록을 불러오지 못했습니다.',
        )
      } finally {
        if (
          !controller.signal.aborted
        ) {
          setLoading(false)
        }
      }
    }

    // 검색어 입력마다 즉시 요청하지 않고
    // 300ms 기다린 후 요청합니다.
    const timerId =
      window.setTimeout(
        () => {
          void loadPatients()
        },
        300,
      )

    return () => {
      window.clearTimeout(timerId)
      controller.abort()
    }
  }, [
    submittedSearch,
    statusFilter,
    page,
  ])

  const handleSearchChange = (
    value: string,
  ) => {
    setSearchText(value)
  }

  const handleSearch = () => {
    const keyword =
        searchText.trim()

    setSubmittedSearch(keyword)
    setPage(1)

    if (!keyword) {
        setSearchParams({})
        return
    }

    setSearchParams({
        search: keyword,
    })
    }

  const handleStatusChange = (
    value: string,
  ) => {
    setStatusFilter(
      value as PatientStatus | '',
    )

    setPage(1)
  }

  return (
    <div className="brainon-dashboard">
      <DashboardSidebar />

      <div className="main-area">
        <DashboardHeader
            searchInputRef={searchInputRef}
            searchText={searchText}
            doctor={doctor}
            onSearchTextChange={
                handleSearchChange
            }
            onSearch={
                handleSearch
            }
            onLogout={handleLogout}
            />

        <main className="patient-management-content">
          <div className="patient-page-heading">
            <div>
              <h1>환자 관리</h1>

              <p>
                등록된 환자를 검색하고
                상태를 확인합니다.
              </p>
            </div>

            <button
              type="button"
              className="patient-create-button"
            >
              환자 등록
            </button>
          </div>

          <section className="patient-filter-card">
            <label>
              환자 상태

              <select
                value={
                  statusFilter
                }
                onChange={(event) =>
                  handleStatusChange(
                    event.target.value,
                  )
                }
              >
                <option value="">
                  전체
                </option>

                <option value="ACTIVE">
                  활성
                </option>

                <option value="INACTIVE">
                  비활성
                </option>
              </select>
            </label>

            <span>
              총 {meta.total_count}명
            </span>
          </section>

          {error && (
            <p
              role="alert"
              className="patient-error"
            >
              {error}
            </p>
          )}

          <section className="patient-list-card">
            <div className="patient-table-wrapper">
              <table className="patient-management-table">
                <thead>
                  <tr>
                    <th>환자번호</th>
                    <th>이름</th>
                    <th>생년월일</th>
                    <th>나이</th>
                    <th>성별</th>
                    <th>전화번호</th>
                    <th>상태</th>
                  </tr>
                </thead>

                <tbody>
                  {patients.map(
                    (patient) => (
                      <tr
                        key={
                          patient.patient_id
                        }
                      >
                        <td className="patient-number">
                          {
                            patient
                              .medical_record_number
                            ?? '-'
                          }
                        </td>

                        <td>
                          {patient.name}
                        </td>

                        <td>
                          {
                            patient.birth_date
                            ?? '-'
                          }
                        </td>

                        <td>
                          {
                            calculateAge(
                              patient.birth_date,
                            )
                          }
                        </td>

                        <td>
                          {
                            sexLabel(
                              patient.sex,
                            )
                          }
                        </td>

                        <td>
                          {
                            patient.phone
                            || '-'
                          }
                        </td>

                        <td>
                          <span
                            className={`patient-status patient-status-${patient.status.toLowerCase()}`}
                          >
                            {
                              statusLabel(
                                patient.status,
                              )
                            }
                          </span>
                        </td>
                      </tr>
                    ),
                  )}

                  {!loading
                    && patients.length === 0
                    && (
                      <tr>
                        <td
                          colSpan={7}
                          className="patient-empty"
                        >
                          검색 결과가 없습니다.
                        </td>
                      </tr>
                    )}
                </tbody>
              </table>
            </div>

            {loading && (
              <p className="patient-loading">
                환자 목록을 불러오는 중입니다.
              </p>
            )}

            <div className="patient-pagination">
              <button
                type="button"
                disabled={
                  loading
                  || page <= 1
                }
                onClick={() =>
                  setPage(
                    (current) =>
                      current - 1,
                  )
                }
              >
                이전
              </button>

              <span>
                {meta.page}
                {' / '}
                {meta.total_pages}
              </span>

              <button
                type="button"
                disabled={
                  loading
                  || page
                    >= meta.total_pages
                }
                onClick={() =>
                  setPage(
                    (current) =>
                      current + 1,
                  )
                }
              >
                다음
              </button>
            </div>
          </section>
        </main>
      </div>
    </div>
  )
}
