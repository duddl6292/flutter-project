import { useEffect, useMemo, useState } from 'react'
import {
  Building2,
  Check,
  Search,
  Stethoscope,
  X,
} from 'lucide-react'

import {
  createConsultation,
  getConsultationClinicians,
  getConsultationContexts,
} from './consultation.api'
import type {
  Consultation,
  ConsultationClinician,
  ConsultationContext,
  ConsultationPriority,
} from './consultation.types'

export function ConsultationCreateModal({
  onClose,
  onCreated,
}: {
  onClose: () => void
  onCreated: (consultation: Consultation) => void
}) {
  const [contexts, setContexts] = useState<ConsultationContext[]>([])
  const [clinicians, setClinicians] = useState<ConsultationClinician[]>([])
  const [encounterId, setEncounterId] = useState('')
  const [consultantId, setConsultantId] = useState('')
  const [selectedClinician, setSelectedClinician] =
    useState<ConsultationClinician | null>(null)
  const [clinicianSearch, setClinicianSearch] =
    useState('')
  const [subject, setSubject] = useState('')
  const [question, setQuestion] = useState('')
  const [priority, setPriority] = useState<ConsultationPriority>('ROUTINE')
  const [dueAt, setDueAt] = useState('')
  const [loading, setLoading] = useState(true)
  const [clinicianLoading, setClinicianLoading] =
    useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    getConsultationContexts().then((nextContexts) => {
      if (!active) return
      setContexts(nextContexts)
      setEncounterId(nextContexts[0]?.encounter_id ?? '')
    }).catch((requestError) => {
      if (active) {
        setError(requestError instanceof Error
          ? requestError.message
          : '협진 요청 정보를 불러오지 못했습니다.')
      }
    }).finally(() => {
      if (active) setLoading(false)
    })
    return () => { active = false }
  }, [])

  useEffect(() => {
    let active = true
    setClinicianLoading(true)

    const timerId = window.setTimeout(() => {
      getConsultationClinicians(
        clinicianSearch.trim(),
      ).then((nextClinicians) => {
        if (active) setClinicians(nextClinicians)
      }).catch((requestError) => {
        if (active) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : '협진 의료진을 검색하지 못했습니다.',
          )
        }
      }).finally(() => {
        if (active) setClinicianLoading(false)
      })
    }, 250)

    return () => {
      active = false
      window.clearTimeout(timerId)
    }
  }, [clinicianSearch])

  const selectedContext = useMemo(
    () => contexts.find((context) => context.encounter_id === encounterId),
    [contexts, encounterId],
  )

  return (
    <div className="consultation-modal-backdrop" role="presentation">
      <section className="consultation-modal consultation-create-modal" role="dialog" aria-modal="true" aria-label="새 협진 요청">
        <header className="consultation-modal-header">
          <div>
            <h2>새 협진 요청</h2>
            <p>진료 건과 담당 의료진을 선택하고 요청 내용을 작성합니다.</p>
          </div>
          <button type="button" aria-label="닫기" onClick={onClose}><X size={22} /></button>
        </header>

        <form
          className="consultation-form"
          onSubmit={async (event) => {
            event.preventDefault()
            if (!encounterId || !consultantId || !subject.trim() || !question.trim()) {
              setError('필수 항목을 모두 입력해주세요.')
              return
            }
            setSaving(true)
            setError('')
            try {
              const consultation = await createConsultation({
                encounter_id: encounterId,
                consultant_clinician_id: consultantId,
                subject: subject.trim(),
                priority,
                question: question.trim(),
                due_at: dueAt ? new Date(dueAt).toISOString() : null,
              })
              onCreated(consultation)
            } catch (requestError) {
              setError(requestError instanceof Error
                ? requestError.message
                : '협진 요청을 등록하지 못했습니다.')
            } finally {
              setSaving(false)
            }
          }}
        >
          {loading && <p className="consultation-message-state">정보를 불러오는 중입니다.</p>}
          {error && <p className="consultation-error" role="alert">{error}</p>}

          <label>
            진료 건 <strong>*</strong>
            <select value={encounterId} onChange={(event) => setEncounterId(event.target.value)} disabled={loading}>
              {contexts.map((context) => (
                <option key={context.encounter_id} value={context.encounter_id}>
                  {context.patient_name} ({context.patient_number ?? '-'}) · {context.encounter_number}
                </option>
              ))}
            </select>
          </label>

          {selectedContext && (
            <div className="consultation-context-preview">
              <strong>{selectedContext.patient_name}</strong>
              <span>{selectedContext.department_name} · {selectedContext.encounter_number}</span>
            </div>
          )}

          <fieldset className="consultation-clinician-picker">
            <legend>
              협진 담당 의료진 <strong>*</strong>
            </legend>

            <div className="consultation-clinician-search">
              <Search size={18} />
              <input
                value={clinicianSearch}
                onChange={(event) =>
                  setClinicianSearch(event.target.value)
                }
                placeholder="의사명, 진료과 또는 병원명으로 검색"
                aria-label="협진 의료진 검색"
              />
            </div>

            {selectedClinician && (
              <div className="consultation-selected-clinician">
                <span className="consultation-clinician-avatar">
                  {selectedClinician.name.slice(0, 1)}
                </span>
                <div>
                  <strong>
                    {selectedClinician.name} 의료진
                  </strong>
                  <span>
                    <Stethoscope size={14} />
                    {selectedClinician.department_name}
                  </span>
                  <span>
                    <Building2 size={14} />
                    {selectedClinician.hospital_name}
                  </span>
                </div>
                <Check size={20} aria-label="선택됨" />
              </div>
            )}

            <div className="consultation-clinician-results">
              {clinicianLoading && (
                <p>의료진을 검색하는 중입니다.</p>
              )}
              {!clinicianLoading
                && clinicians.length === 0
                && (
                  <p>
                    검색 조건에 맞는 의료진이 없습니다.
                  </p>
                )}
              {!clinicianLoading
                && clinicians.map((clinician) => {
                  const selected =
                    clinician.clinician_id === consultantId

                  return (
                    <button
                      key={clinician.clinician_id}
                      type="button"
                      className={selected ? 'selected' : ''}
                      onClick={() => {
                        setConsultantId(
                          clinician.clinician_id,
                        )
                        setSelectedClinician(clinician)
                      }}
                    >
                      <span className="consultation-clinician-avatar">
                        {clinician.name.slice(0, 1)}
                      </span>
                      <span className="consultation-clinician-info">
                        <strong>{clinician.name}</strong>
                        <small>
                          {clinician.department_name}
                        </small>
                        <small>
                          {clinician.hospital_name}
                        </small>
                      </span>
                      {selected && <Check size={18} />}
                    </button>
                  )
                })}
            </div>
          </fieldset>

          <div className="consultation-form-row consultation-form-row-secondary">
            <label>
              우선순위
              <select value={priority} onChange={(event) => setPriority(event.target.value as ConsultationPriority)}>
                <option value="ROUTINE">일반</option>
                <option value="URGENT">긴급</option>
                <option value="EMERGENCY">응급</option>
              </select>
            </label>
            <label>
              답변 희망일
              <input type="datetime-local" value={dueAt} onChange={(event) => setDueAt(event.target.value)} />
            </label>
          </div>

          <label>
            제목 <strong>*</strong>
            <input maxLength={200} value={subject} onChange={(event) => setSubject(event.target.value)} placeholder="협진 목적을 간결하게 입력해주세요." />
          </label>
          <label>
            요청 내용 <strong>*</strong>
            <textarea rows={7} value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="환자 상태와 확인이 필요한 내용을 작성해주세요." />
          </label>
          <footer className="consultation-modal-actions">
            <button type="button" className="consultation-secondary-button" onClick={onClose}>취소</button>
            <button type="submit" className="consultation-primary-button" disabled={saving || loading}>
              {saving ? '요청 중...' : '협진 요청'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}
