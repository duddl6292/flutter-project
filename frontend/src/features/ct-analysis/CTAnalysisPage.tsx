import { Download, FileScan, Play, RefreshCw, UploadCloud } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { AccountPageLayout } from '../account/AccountPageLayout'
import { getPatients } from '../patients/patient.api'
import type { PatientSummary } from '../patients/patient.types'
import {
  createCTCase,
  downloadCTAsset,
  getCTCase,
  getCTCases,
  getCTSources,
} from './ct-analysis.api'
import type { CTCase, CTSource } from './ct-analysis.types'
import { NiiVueViewer } from './NiiVueViewer'
import './ct-analysis.css'

const formatDateTime = (value: string | null) => value ? new Intl.DateTimeFormat('ko-KR', {
  year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false,
}).format(new Date(value)) : '-'

const formatBytes = (value: number) => value >= 1024 ** 2
  ? `${(value / 1024 ** 2).toFixed(1)} MB`
  : `${Math.max(1, Math.round(value / 1024))} KB`

export function CTAnalysisPage() {
  const navigate = useNavigate()
  const { caseId } = useParams()
  const [patients, setPatients] = useState<PatientSummary[]>([])
  const [cases, setCases] = useState<CTCase[]>([])
  const [selectedCase, setSelectedCase] = useState<CTCase | null>(null)
  const [patientId, setPatientId] = useState('')
  const [sources, setSources] = useState<CTSource[]>([])
  const [sourceId, setSourceId] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(true)
  const [sourcesLoading, setSourcesLoading] = useState(false)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const [patientResponse, caseRows] = await Promise.all([
        getPatients({ page: 1, pageSize: 100, status: 'ACTIVE', signal }),
        getCTCases(signal),
      ])
      setPatients(patientResponse.data)
      setCases(caseRows)
      if (caseId) setSelectedCase(await getCTCase(caseId, signal))
      else setSelectedCase(caseRows[0] ?? null)
    } catch (loadError) {
      if (!(loadError instanceof DOMException && loadError.name === 'AbortError')) {
        setError(loadError instanceof Error ? loadError.message : 'CT 분석 정보를 불러오지 못했습니다.')
      }
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [caseId])

  useEffect(() => {
    const controller = new AbortController()
    void load(controller.signal)
    return () => controller.abort()
  }, [load])

  useEffect(() => {
    if (!patientId) {
      setSources([])
      setSourceId('')
      return
    }
    const controller = new AbortController()
    setSourcesLoading(true)
    setFile(null)
    void getCTSources(patientId, controller.signal)
      .then((rows) => {
        setSources(rows)
        setSourceId(rows[0]?.source_id ?? '')
      })
      .catch((loadError) => {
        if (!(loadError instanceof DOMException && loadError.name === 'AbortError')) {
          setError(loadError instanceof Error ? loadError.message : '환자의 CT 영상을 불러오지 못했습니다.')
        }
      })
      .finally(() => { if (!controller.signal.aborted) setSourcesLoading(false) })
    return () => controller.abort()
  }, [patientId])

  const selectedSource = useMemo(
    () => sources.find((source) => source.source_id === sourceId) ?? null,
    [sourceId, sources],
  )

  const startAnalysis = async () => {
    if (!patientId || (!sourceId && !file)) return
    setCreating(true)
    setError('')
    try {
      const created = await createCTCase({
        patientId,
        sourceId: sourceId || undefined,
        sourceType: selectedSource?.source_type,
        file: sourceId ? undefined : file ?? undefined,
        studyType: 'NCCT',
        description,
      })
      navigate(`/ct-analysis/${created.case_id}/process`)
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : 'CT 분석 요청을 만들지 못했습니다.')
    } finally {
      setCreating(false)
    }
  }

  const saveAsset = async (path: string, filename: string) => {
    try {
      const blob = await downloadCTAsset(path)
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = filename
      anchor.click()
      URL.revokeObjectURL(url)
    } catch (downloadError) {
      setError(downloadError instanceof Error ? downloadError.message : '파일을 저장하지 못했습니다.')
    }
  }

  const result = selectedCase?.result

  return (
    <AccountPageLayout>
      <main className="ct-analysis-page">
        <header className="ct-page-heading">
          <div><span>GPU 기반 뇌 CT 분석</span><h1>CT 분석</h1><p>환자 CT를 분석하고 원본 영상과 AI 병변 마스크를 함께 검토합니다.</p></div>
          <button type="button" onClick={() => void load()} disabled={loading}><RefreshCw size={17} /> 새로고침</button>
        </header>
        {error && <p className="ct-error" role="alert">{error}</p>}

        <section className="ct-request-card">
          <header><div><UploadCloud size={22} /><div><h2>새 CT 분석</h2><p>기존 CT가 있으면 자동 선택하고, 없으면 NIfTI를 업로드합니다.</p></div></div></header>
          <div className="ct-request-grid">
            <label>환자<select value={patientId} onChange={(event) => setPatientId(event.target.value)}><option value="">환자 선택</option>{patients.map((patient) => <option key={patient.patient_id} value={patient.patient_id}>{patient.medical_record_number ?? '환자번호 없음'} · {patient.name} · {patient.birth_date ?? '생년월일 없음'}{patient.access_scope === 'CONSULTATION' ? ' [협진 공유]' : ''}</option>)}</select></label>
            <label>검사 유형<input value="비조영 뇌 CT (NCCT)" readOnly aria-label="검사 유형은 비조영 뇌 CT로 고정됩니다" /></label>
            <label className="ct-source-field">환자 CT 데이터
              {sourcesLoading ? <div className="ct-source-message">환자의 CT를 찾는 중입니다.</div> : sources.length > 0 ? (
                <select value={sourceId} onChange={(event) => { setSourceId(event.target.value); setFile(null) }}>{sources.map((source) => <option key={`${source.source_type}-${source.source_id}`} value={source.source_id}>{formatDateTime(source.performed_at)} · {source.study_description || source.filename || 'CT NIfTI'} · {formatBytes(source.file_size_bytes)}</option>)}</select>
              ) : (
                <div className="ct-upload-input"><input type="file" accept=".nii,.nii.gz" onChange={(event) => setFile(event.target.files?.[0] ?? null)} /><span>{file?.name ?? (patientId ? '매핑된 CT가 없습니다. NIfTI를 선택해 주세요.' : '환자를 먼저 선택해 주세요.')}</span></div>
              )}
            </label>
            <label className="ct-description-field">메모<input value={description} onChange={(event) => setDescription(event.target.value)} placeholder="분석 목적이나 참고 사항" /></label>
          </div>
          {selectedSource && <p className="ct-auto-map"><FileScan size={16} /> 환자에게 매핑된 최신 CT가 자동 선택되었습니다: {selectedSource.filename || selectedSource.study_description}</p>}
          <button className="ct-start-button" type="button" disabled={creating || !patientId || (!sourceId && !file)} onClick={() => void startAnalysis()}><Play size={18} /> {creating ? '분석 준비 중...' : 'AI 분석 시작'}</button>
        </section>

        <div className="ct-content-grid">
          <section className="ct-history-card">
            <header><h2>분석 이력</h2><span>{cases.length}건</span></header>
            <div className="ct-history-list">
              {loading && <p>불러오는 중입니다.</p>}
              {!loading && cases.length === 0 && <p>아직 분석 이력이 없습니다.</p>}
              {cases.map((row) => <button type="button" key={row.case_id} className={selectedCase?.case_id === row.case_id ? 'active' : ''} onClick={() => navigate(`/ct-analysis/${row.case_id}`)}><div><strong>{row.patient?.name ?? '-'}</strong><span>{row.display_id} · {row.study_type_label}</span></div><span className={`ct-status ${row.status.toLowerCase()}`}>{row.status_label}</span><time>{formatDateTime(row.created_at)}</time></button>)}
            </div>
          </section>

          <section className="ct-result-area">
            {!selectedCase && <div className="ct-empty-result"><FileScan size={40} /><h2>분석 결과를 선택해 주세요.</h2><p>완료된 결과에서 원본과 마스크를 함께 확인할 수 있습니다.</p></div>}
            {selectedCase && !result && <div className="ct-empty-result"><FileScan size={40} /><h2>{selectedCase.status_label}</h2><p>{selectedCase.job?.error_message || '아직 표시할 분석 결과가 없습니다.'}</p>{selectedCase.status === 'READY' && <button type="button" onClick={() => navigate(`/ct-analysis/${selectedCase.case_id}/process`)}>분석 과정 보기</button>}</div>}
            {selectedCase && result && <>
              <div className="ct-result-summary">
                <article className={result.lesion_detected ? 'alert' : 'normal'}><span>병변 탐지</span><strong>{result.lesion_detected ? '탐지됨' : '탐지 없음'}</strong></article>
                <article><span>병변 부피</span><strong>{result.lesion_volume_ml.toFixed(2)} <small>mL</small></strong></article>
                <article><span>병변 슬라이스</span><strong>{result.lesion_slice_count} <small>장</small></strong></article>
                <article><span>전체 분석 시간</span><strong>{(result.end_to_end_seconds ?? result.total_seconds).toFixed(1)} <small>초</small></strong><small>요청부터 결과 저장까지</small></article>
                <article><span>AI 컨테이너 처리</span><strong>{result.total_seconds.toFixed(1)} <small>초</small></strong><small>순수 GPU 추론 {result.inference_seconds.toFixed(1)}초</small></article>
              </div>
              <NiiVueViewer
                sourceUrl={result.source_url}
                maskUrl={result.mask_url}
                displayId={selectedCase.display_id}
                lesionDetected={result.lesion_detected}
                lesionSliceIndices={result.lesion_slice_indices}
                lesionSliceStart={result.lesion_slice_start}
                lesionSliceEnd={result.lesion_slice_end}
                maxLesionSlice={result.max_lesion_slice}
              />
              <div className="ct-download-row">
                <button type="button" onClick={() => void saveAsset(result.source_url, `${selectedCase.display_id}-source.nii.gz`)}><Download size={16} /> 원본 NIfTI 저장</button>
                <button type="button" onClick={() => void saveAsset(result.mask_url, `${selectedCase.display_id}-mask.nii.gz`)}><Download size={16} /> AI 마스크 저장</button>
              </div>
              <section className="ct-clinical-note"><strong>의료진 검토 필요</strong><p>AI 분석 결과는 진단 보조 정보이며 의료진의 최종 판독을 대체하지 않습니다.</p></section>
            </>}
          </section>
        </div>
      </main>
    </AccountPageLayout>
  )
}
