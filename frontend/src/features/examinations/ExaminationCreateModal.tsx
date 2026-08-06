import { Plus, Trash2, X } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

import { createExamination, getExaminationContexts } from './examination.api'
import type {
  Examination,
  ExaminationCategory,
  ExaminationContext,
  ExaminationInterpretation,
  ExaminationObservationInput,
  ExaminationSource,
} from './examination.types'

interface Props {
  onClose: () => void
  onCreated: (examination: Examination) => void
}

const nowLocal = () => {
  const now = new Date()
  return new Date(now.getTime() - now.getTimezoneOffset() * 60_000).toISOString().slice(0, 16)
}

const emptyObservation = (): ExaminationObservationInput => ({
  code: '', name: '', value_type: 'NUMERIC', numeric_value: '', text_value: '',
  unit: '', reference_low: null, reference_high: null, reference_text: '', interpretation: 'UNKNOWN',
})

export function ExaminationCreateModal({ onClose, onCreated }: Props) {
  const [contexts, setContexts] = useState<ExaminationContext[]>([])
  const [encounterId, setEncounterId] = useState('')
  const [testCode, setTestCode] = useState('')
  const [testName, setTestName] = useState('')
  const [category, setCategory] = useState<ExaminationCategory>('LABORATORY')
  const [source, setSource] = useState<ExaminationSource>('INTERNAL')
  const [performedAt, setPerformedAt] = useState(nowLocal)
  const [observations, setObservations] = useState<ExaminationObservationInput[]>([emptyObservation()])
  const [reportTitle, setReportTitle] = useState('')
  const [reportSummary, setReportSummary] = useState('')
  const [reportConclusion, setReportConclusion] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    void getExaminationContexts()
      .then((items) => { setContexts(items); setEncounterId(items[0]?.encounter_id ?? '') })
      .catch((requestError) => setError(requestError instanceof Error ? requestError.message : '진료 목록을 불러오지 못했습니다.'))
      .finally(() => setLoading(false))
  }, [])

  const selectedContext = useMemo(() => contexts.find((item) => item.encounter_id === encounterId), [contexts, encounterId])
  const updateObservation = (index: number, values: Partial<ExaminationObservationInput>) => {
    setObservations((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, ...values } : item))
  }

  const submit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')
    if (!encounterId || !testCode.trim() || !testName.trim() || !reportTitle.trim()) {
      setError('환자 진료 건과 검사 기본정보를 모두 입력해주세요.')
      return
    }
    if (observations.some((item) => !item.code.trim() || !item.name.trim() || (item.value_type === 'NUMERIC' ? item.numeric_value === '' || item.numeric_value == null : !item.text_value?.trim()))) {
      setError('각 검사 항목의 코드, 항목명, 결과값을 입력해주세요.')
      return
    }
    setSubmitting(true)
    try {
      const examination = await createExamination({
        encounter_id: encounterId,
        test_code: testCode.trim(), test_name: testName.trim(), category, source,
        performed_at: new Date(performedAt).toISOString(),
        observations: observations.map((item) => ({
          ...item,
          code: item.code.trim(), name: item.name.trim(),
          numeric_value: item.value_type === 'NUMERIC' ? item.numeric_value : null,
          text_value: item.value_type === 'TEXT' ? item.text_value?.trim() : '',
          reference_low: item.reference_low === '' ? null : item.reference_low,
          reference_high: item.reference_high === '' ? null : item.reference_high,
        })),
        report_title: reportTitle.trim(), report_summary: reportSummary.trim(), report_conclusion: reportConclusion.trim(),
      })
      onCreated(examination)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : '검사결과를 등록하지 못했습니다.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="examination-modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}>
      <section className="examination-modal examination-create-modal" role="dialog" aria-modal="true" aria-labelledby="examination-create-title">
        <header className="examination-modal-header"><div><h2 id="examination-create-title">새 검사 결과</h2><p>측정값을 입력하면 예비 결과로 저장됩니다.</p></div><button type="button" aria-label="닫기" onClick={onClose}><X size={20} /></button></header>
        <form className="examination-form" onSubmit={submit}>
          {error && <p className="examination-error" role="alert">{error}</p>}
          <label>환자 진료 건 <strong>*</strong><select disabled={loading} value={encounterId} onChange={(event) => setEncounterId(event.target.value)}><option value="">진료 건 선택</option>{contexts.map((item) => <option key={item.encounter_id} value={item.encounter_id}>{item.patient_name} ({item.patient_number ?? '-'}) · {item.encounter_number}</option>)}</select></label>
          {selectedContext && <div className="examination-context-preview"><strong>{selectedContext.patient_name}</strong><span>{selectedContext.patient_number ?? '-'} · {selectedContext.department_name} · {selectedContext.encounter_number}</span></div>}
          <div className="examination-form-row three"><label>검사 코드 <strong>*</strong><input value={testCode} onChange={(event) => setTestCode(event.target.value)} placeholder="예: CBC" /></label><label>검사명 <strong>*</strong><input value={testName} onChange={(event) => setTestName(event.target.value)} placeholder="예: 일반혈액검사" /></label><label>시행일시 <strong>*</strong><input type="datetime-local" max={nowLocal()} value={performedAt} onChange={(event) => setPerformedAt(event.target.value)} /></label></div>
          <div className="examination-form-row"><label>검사 분류<select value={category} onChange={(event) => setCategory(event.target.value as ExaminationCategory)}><option value="LABORATORY">진단검사</option><option value="IMAGING">영상검사</option><option value="PHYSIOLOGY">생리기능검사</option><option value="PATHOLOGY">병리검사</option><option value="NEURO_ASSESSMENT">신경계 평가</option><option value="OTHER">기타</option></select></label><label>결과 출처<select value={source} onChange={(event) => setSource(event.target.value as ExaminationSource)}><option value="INTERNAL">원내</option><option value="EXTERNAL">외부 기관</option><option value="PATIENT_UPLOAD">환자 업로드</option></select></label></div>

          <fieldset className="examination-observation-fieldset"><legend>검사 항목 <strong>*</strong></legend>
            {observations.map((item, index) => <div className="examination-observation-editor" key={index}>
              <div className="examination-observation-title"><strong>항목 {index + 1}</strong>{observations.length > 1 && <button type="button" aria-label={`항목 ${index + 1} 삭제`} onClick={() => setObservations((current) => current.filter((_, itemIndex) => itemIndex !== index))}><Trash2 size={16} /></button>}</div>
              <div className="examination-form-row three"><label>항목 코드<input value={item.code} onChange={(event) => updateObservation(index, { code: event.target.value })} placeholder="PLT" /></label><label>항목명<input value={item.name} onChange={(event) => updateObservation(index, { name: event.target.value })} placeholder="혈소판" /></label><label>값 유형<select value={item.value_type} onChange={(event) => updateObservation(index, { value_type: event.target.value as 'NUMERIC' | 'TEXT', numeric_value: '', text_value: '' })}><option value="NUMERIC">숫자</option><option value="TEXT">문자</option></select></label></div>
              {item.value_type === 'NUMERIC' ? <div className="examination-form-row four"><label>결과값<input type="number" step="any" value={item.numeric_value ?? ''} onChange={(event) => updateObservation(index, { numeric_value: event.target.value })} /></label><label>단위<input value={item.unit} onChange={(event) => updateObservation(index, { unit: event.target.value })} placeholder="mg/dL" /></label><label>참고 하한<input type="number" step="any" value={item.reference_low ?? ''} onChange={(event) => updateObservation(index, { reference_low: event.target.value })} /></label><label>참고 상한<input type="number" step="any" value={item.reference_high ?? ''} onChange={(event) => updateObservation(index, { reference_high: event.target.value })} /></label></div> : <label>결과 내용<textarea rows={2} value={item.text_value ?? ''} onChange={(event) => updateObservation(index, { text_value: event.target.value })} /></label>}
              <div className="examination-form-row"><label>판정<select value={item.interpretation} onChange={(event) => updateObservation(index, { interpretation: event.target.value as ExaminationInterpretation })}><option value="UNKNOWN">미판정</option><option value="NORMAL">정상</option><option value="LOW">낮음</option><option value="HIGH">높음</option><option value="ABNORMAL">이상</option><option value="CRITICAL">위험</option></select></label><label>참고 설명<input value={item.reference_text} onChange={(event) => updateObservation(index, { reference_text: event.target.value })} placeholder="음성 또는 임상 참고범위" /></label></div>
            </div>)}
            <button type="button" className="examination-add-observation" onClick={() => setObservations((current) => [...current, emptyObservation()])}><Plus size={16} /> 검사 항목 추가</button>
          </fieldset>

          <fieldset className="examination-report-fieldset"><legend>판독 보고서</legend><label>보고서 제목 <strong>*</strong><input value={reportTitle} onChange={(event) => setReportTitle(event.target.value)} placeholder="검사결과 보고서 제목" /></label><label>요약<textarea rows={2} value={reportSummary} onChange={(event) => setReportSummary(event.target.value)} placeholder="주요 소견을 요약해주세요." /></label><label>결론<textarea rows={3} value={reportConclusion} onChange={(event) => setReportConclusion(event.target.value)} placeholder="최종 확정 시 결론을 보완할 수 있습니다." /></label></fieldset>
          <div className="examination-modal-actions"><button type="button" className="examination-secondary-button" onClick={onClose}>취소</button><button type="submit" className="examination-primary-button" disabled={submitting || loading}>{submitting ? '저장 중...' : '예비 결과 저장'}</button></div>
        </form>
      </section>
    </div>
  )
}
