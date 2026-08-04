import {
  ArrowLeft,
  ChevronDown,
  ClipboardPlus,
  Pill,
  ScanLine,
  UserRound,
} from 'lucide-react'
import {
  useEffect,
  useState,
} from 'react'
import {
  useNavigate,
  useParams,
} from 'react-router-dom'

import {
  AccountPageLayout,
} from '../account/AccountPageLayout'
import type {
  EncounterDetail,
} from '../encounters/encounter.types'

import {
  getPatient,
  getPatientMedicalHistory,
} from './patient.api'
import type {
  PatientDetail,
} from './patient.types'

import './patients.css'

function formatDateTime(value: string | null): string {
  if (!value) return '-'

  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function patientSexLabel(value: string): string {
  if (value === 'M') return '남성'
  if (value === 'F') return '여성'
  return '미상'
}

function RecordValue({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value || '-'}</dd>
    </div>
  )
}

export function PatientDetailPage() {
  const navigate = useNavigate()
  const { patientId = '' } = useParams()
  const [patient, setPatient] =
    useState<PatientDetail | null>(null)
  const [history, setHistory] =
    useState<EncounterDetail[]>([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [expandedId, setExpandedId] = useState('')
  const [tab, setTab] =
    useState<'history' | 'profile'>('history')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!patientId) return

    const controller = new AbortController()
    setLoading(true)
    setError('')

    void Promise.all([
      getPatient(patientId, controller.signal),
      getPatientMedicalHistory({
        patientId,
        page,
        pageSize: 10,
        signal: controller.signal,
      }),
    ])
      .then(([patientResponse, historyResponse]) => {
        setPatient(patientResponse)
        setHistory(historyResponse.data)
        setTotalPages(historyResponse.meta.total_pages)
        setTotalCount(historyResponse.meta.total_count)
        setExpandedId((current) =>
          historyResponse.data.some(
            (item) => item.encounter_id === current,
          )
            ? current
            : historyResponse.data[0]?.encounter_id ?? '',
        )
      })
      .catch((requestError) => {
        if (
          requestError instanceof DOMException
          && requestError.name === 'AbortError'
        ) return

        setError(
          requestError instanceof Error
            ? requestError.message
            : '환자 진료 기록을 불러오지 못했습니다.',
        )
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })

    return () => controller.abort()
  }, [page, patientId])

  return (
    <AccountPageLayout>
      <main className="patient-detail-page">
        <header className="patient-detail-heading">
          <div>
            <button
              type="button"
              onClick={() => navigate('/patients')}
            >
              <ArrowLeft size={17} />
              환자 목록
            </button>
            <h1>환자 상세</h1>
            <p>환자 정보와 과거 진료 결과를 확인합니다.</p>
          </div>
        </header>

        {error && (
          <p className="patient-error" role="alert">
            {error}
          </p>
        )}

        {loading && (
          <p className="patient-loading">
            환자 정보를 불러오는 중입니다.
          </p>
        )}

        {patient && !loading && (
          <>
            <section className="patient-detail-summary">
              <div className="patient-detail-avatar">
                <UserRound size={27} />
              </div>
              <div>
                <h2>{patient.name}</h2>
                <p>
                  {patient.medical_record_number ?? '환자번호 미등록'}
                  {' · '}
                  {patient.birth_date ?? '생년월일 미등록'}
                  {' · '}
                  {patientSexLabel(patient.sex)}
                </p>
              </div>
              <span className={`patient-status patient-status-${
                patient.status.toLowerCase()
              }`}>
                {patient.status === 'ACTIVE' ? '활성' : '비활성'}
              </span>
            </section>

            <nav className="patient-detail-tabs">
              <button
                type="button"
                className={tab === 'history' ? 'is-active' : ''}
                onClick={() => setTab('history')}
              >
                진료 기록
                <span>{totalCount}</span>
              </button>
              <button
                type="button"
                className={tab === 'profile' ? 'is-active' : ''}
                onClick={() => setTab('profile')}
              >
                기본정보
              </button>
            </nav>

            {tab === 'profile' && (
              <section className="patient-profile-card">
                <dl>
                  <RecordValue label="이름" value={patient.name} />
                  <RecordValue
                    label="환자번호"
                    value={patient.medical_record_number ?? ''}
                  />
                  <RecordValue
                    label="생년월일"
                    value={patient.birth_date ?? ''}
                  />
                  <RecordValue
                    label="성별"
                    value={patientSexLabel(patient.sex)}
                  />
                  <RecordValue label="전화번호" value={patient.phone} />
                  <RecordValue
                    label="비상 연락처"
                    value={patient.emergency_contact}
                  />
                  <RecordValue label="주소" value={patient.address} />
                  <RecordValue label="이메일" value={patient.email ?? ''} />
                </dl>
              </section>
            )}

            {tab === 'history' && (
              <section className="patient-history-section">
                <header>
                  <div>
                    <ClipboardPlus size={20} />
                    <div>
                      <h2>과거 진료 결과</h2>
                      <p>
                        완료된 진료의 SOAP 기록과 처방·CT 결과입니다.
                      </p>
                    </div>
                  </div>
                  <strong>총 {totalCount}건</strong>
                </header>

                {history.length === 0 && (
                  <p className="patient-history-empty">
                    저장된 과거 진료 결과가 없습니다.
                  </p>
                )}

                <div className="patient-history-list">
                  {history.map((encounter) => {
                    const record = encounter.clinical_record
                    const expanded =
                      expandedId === encounter.encounter_id

                    return (
                      <article key={encounter.encounter_id}>
                        <button
                          type="button"
                          className="patient-history-header"
                          aria-expanded={expanded}
                          onClick={() =>
                            setExpandedId(
                              expanded ? '' : encounter.encounter_id,
                            )
                          }
                        >
                          <div>
                            <strong>
                              {formatDateTime(encounter.completed_at)}
                            </strong>
                            <span>
                              {encounter.department_name}
                              {' · '}
                              {encounter.clinician_name}
                              {' · '}
                              {encounter.encounter_type_label}
                            </span>
                          </div>
                          <div>
                            <span>{encounter.encounter_number}</span>
                            <span>{encounter.status_label}</span>
                            <ChevronDown size={17} />
                          </div>
                        </button>

                        {expanded && record && (
                          <div className="patient-history-body">
                            <dl className="patient-soap-result">
                              <RecordValue
                                label="주호소"
                                value={record.chief_complaint}
                              />
                              <RecordValue
                                label="S · 주관적 정보"
                                value={record.subjective}
                              />
                              <RecordValue
                                label="O · 객관적 정보"
                                value={record.objective}
                              />
                              <RecordValue
                                label="A · 진료 결과"
                                value={record.assessment}
                              />
                              <RecordValue
                                label="P · 치료 계획"
                                value={record.plan}
                              />
                            </dl>

                            <section className="patient-visible-summary">
                              <h3>환자 공개 요약</h3>
                              <p>
                                {record.patient_visible_summary || '-'}
                              </p>
                            </section>

                            <div className="patient-history-related">
                              <section>
                                <header><Pill size={17} /><h3>처방</h3></header>
                                {encounter.prescriptions.length === 0
                                  ? <p>연결된 처방이 없습니다.</p>
                                  : encounter.prescriptions.map(
                                    (prescription) => (
                                      <div key={prescription.prescription_id}>
                                        <strong>
                                          {prescription.medicine_names.join(', ')}
                                        </strong>
                                        <span>{prescription.status_label}</span>
                                      </div>
                                    ),
                                  )}
                              </section>
                              <section>
                                <header><ScanLine size={17} /><h3>CT 결과</h3></header>
                                {encounter.ct_cases.length === 0
                                  ? <p>연결된 CT 결과가 없습니다.</p>
                                  : encounter.ct_cases.map((ctCase) => (
                                    <div key={ctCase.case_id}>
                                      <strong>{ctCase.study_type_label}</strong>
                                      <span>{ctCase.status_label}</span>
                                    </div>
                                  ))}
                              </section>
                            </div>
                          </div>
                        )}
                      </article>
                    )
                  })}
                </div>

                <footer className="patient-pagination">
                  <button
                    type="button"
                    disabled={page <= 1}
                    onClick={() => setPage(page - 1)}
                  >
                    이전
                  </button>
                  <span>{page} / {totalPages}</span>
                  <button
                    type="button"
                    disabled={page >= totalPages}
                    onClick={() => setPage(page + 1)}
                  >
                    다음
                  </button>
                </footer>
              </section>
            )}
          </>
        )}
      </main>
    </AccountPageLayout>
  )
}
