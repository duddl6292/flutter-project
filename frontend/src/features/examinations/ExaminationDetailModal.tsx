import { CheckCircle2, Send, X } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

import { finalizeExamination, getExamination, releaseExamination } from './examination.api'
import type { Examination, ExaminationObservation } from './examination.types'

interface Props { examinationId: string; onClose: () => void; onUpdated: () => void }

const formatDateTime = (value: string | null) => value ? new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) : '-'
const referenceRange = (item: ExaminationObservation) => item.reference_text || (item.reference_low != null || item.reference_high != null ? `${item.reference_low ?? '-'} ~ ${item.reference_high ?? '-'} ${item.unit}` : '-')

export function ExaminationDetailModal({ examinationId, onClose, onUpdated }: Props) {
  const [result, setResult] = useState<Examination | null>(null)
  const [summary, setSummary] = useState('')
  const [conclusion, setConclusion] = useState('')
  const [loading, setLoading] = useState(true)
  const [acting, setActing] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true); setError('')
    try {
      const data = await getExamination(examinationId, signal)
      setResult(data); setSummary(data.report?.summary ?? ''); setConclusion(data.report?.conclusion ?? '')
    } catch (requestError) {
      if (!(requestError instanceof DOMException && requestError.name === 'AbortError')) setError(requestError instanceof Error ? requestError.message : '검사결과를 불러오지 못했습니다.')
    } finally { if (!signal?.aborted) setLoading(false) }
  }, [examinationId])

  useEffect(() => { const controller = new AbortController(); void load(controller.signal); return () => controller.abort() }, [load])

  const finalize = async () => {
    if (!conclusion.trim()) { setError('최종 결론을 입력해주세요.'); return }
    setActing(true); setError('')
    try { const updated = await finalizeExamination(examinationId, summary.trim(), conclusion.trim()); setResult(updated); onUpdated() }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : '결과를 확정하지 못했습니다.') }
    finally { setActing(false) }
  }
  const release = async () => {
    setActing(true); setError('')
    try { const updated = await releaseExamination(examinationId); setResult(updated); onUpdated() }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : '환자에게 공개하지 못했습니다.') }
    finally { setActing(false) }
  }

  return <div className="examination-modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}>
    <section className="examination-modal examination-detail-modal" role="dialog" aria-modal="true" aria-labelledby="examination-detail-title">
      <header className="examination-modal-header"><div><h2 id="examination-detail-title">검사결과 상세</h2><p>{result ? `${result.patient_name} · ${result.test_name}` : '검사결과를 확인합니다.'}</p></div><button type="button" aria-label="닫기" onClick={onClose}><X size={20} /></button></header>
      {loading && <p className="examination-message-state">검사결과를 불러오는 중입니다.</p>}
      {error && <p className="examination-error" role="alert">{error}</p>}
      {!loading && result && <div className="examination-detail-content">
        <section className="examination-detail-summary">
          <div><span>환자</span><strong>{result.patient_name}</strong><small>{result.patient_number ?? '-'}</small></div>
          <div><span>검사</span><strong>{result.test_name}</strong><small>{result.test_code} · {result.category_label}</small></div>
          <div><span>시행일</span><strong>{formatDateTime(result.performed_at)}</strong><small>{result.source_label}</small></div>
          <div><span>전체 판정</span><strong className={`examination-interpretation interpretation-${result.overall_interpretation.toLowerCase()}`}>{result.overall_interpretation_label}</strong><small>이상 {result.abnormal_count}개</small></div>
          <div><span>상태</span><strong className={`examination-status status-${result.status.toLowerCase()}`}>{result.status_label}</strong><small>{result.report?.is_released_to_patient ? '환자 공개' : '환자 미공개'}</small></div>
        </section>

        <section className="examination-detail-section"><h3>세부 검사값</h3><div className="examination-observation-table-wrap"><table className="examination-observation-table"><thead><tr><th>항목</th><th>결과</th><th>참고범위</th><th>판정</th></tr></thead><tbody>{result.observations.map((item) => <tr key={item.observation_id}><td><strong>{item.name}</strong><small>{item.code}</small></td><td><strong>{item.formatted_value}</strong>{item.unit && <span> {item.unit}</span>}</td><td>{referenceRange(item)}</td><td><span className={`examination-interpretation interpretation-${item.interpretation.toLowerCase()}`}>{item.interpretation_label}</span></td></tr>)}</tbody></table></div></section>

        {result.report && <section className="examination-detail-section examination-report-card"><div className="examination-section-heading"><h3>{result.report.title}</h3><span className={`examination-status report-${result.report.status.toLowerCase()}`}>{result.report.status_label}</span></div><dl><div><dt>요약</dt><dd>{result.report.summary || '-'}</dd></div><div><dt>결론</dt><dd>{result.report.conclusion || '-'}</dd></div></dl><footer>판독 {result.report.author_name} · 발행 {formatDateTime(result.report.issued_at)} · 서명 {formatDateTime(result.report.signed_at)}</footer></section>}

        {result.status === 'PRELIMINARY' && <section className="examination-action-card"><div><h3>최종 결과 확정</h3><p>결론을 확인한 뒤 서명하여 최종 결과로 확정합니다.</p></div><label>요약<textarea rows={2} value={summary} onChange={(event) => setSummary(event.target.value)} /></label><label>최종 결론 <strong>*</strong><textarea rows={3} value={conclusion} onChange={(event) => setConclusion(event.target.value)} /></label><button type="button" className="examination-primary-button" disabled={acting} onClick={() => void finalize()}><CheckCircle2 size={18} /> {acting ? '처리 중...' : '최종 확정'}</button></section>}

        {(result.status === 'FINAL' || result.status === 'CORRECTED') && result.report && <section className={`examination-release-card ${result.report.is_released_to_patient ? 'done' : ''}`}><div><h3>{result.report.is_released_to_patient ? '환자 공개 완료' : '환자에게 결과 공개'}</h3><p>{result.report.is_released_to_patient ? `${formatDateTime(result.report.released_at)}에 공개되었습니다.` : '확정된 검사결과와 판독 보고서를 환자 앱에서 확인할 수 있게 합니다.'}</p></div>{result.report.is_released_to_patient ? <CheckCircle2 size={24} /> : <button type="button" className="examination-primary-button" disabled={acting} onClick={() => void release()}><Send size={17} /> {acting ? '처리 중...' : '환자에게 공개'}</button>}</section>}
      </div>}
    </section>
  </div>
}
