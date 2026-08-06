import { ClipboardCheck, Plus, Search } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'

import { AccountPageLayout } from '../account/AccountPageLayout'
import { getExaminations } from './examination.api'
import { ExaminationCreateModal } from './ExaminationCreateModal'
import { ExaminationDetailModal } from './ExaminationDetailModal'
import type {
  Examination,
  ExaminationCategory,
  ExaminationInterpretation,
  ExaminationListMeta,
  ExaminationStatus,
} from './examination.types'
import './examinations.css'

const initialMeta: ExaminationListMeta = {
  page: 1, page_size: 20, total_count: 0, total_pages: 1,
}

const formatDateTime = (value: string | null) => value
  ? new Intl.DateTimeFormat('ko-KR', {
    year: '2-digit', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  }).format(new Date(value))
  : '-'

export function ExaminationPage() {
  const navigate = useNavigate()
  const { examinationId } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()
  const [rows, setRows] = useState<Examination[]>([])
  const [meta, setMeta] = useState(initialMeta)
  const [searchText, setSearchText] = useState('')
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<ExaminationStatus | ''>('')
  const [category, setCategory] = useState<ExaminationCategory | ''>('')
  const [interpretation, setInterpretation] = useState<ExaminationInterpretation | ''>('')
  const [released, setReleased] = useState<'' | 'true' | 'false'>('')
  const [page, setPage] = useState(1)
  const [reloadKey, setReloadKey] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [createOpen, setCreateOpen] = useState(searchParams.get('create') === '1')

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const response = await getExaminations({
        search, status, category, interpretation, released,
        page, pageSize: 20, signal,
      })
      setRows(response.data)
      setMeta(response.meta)
    } catch (requestError) {
      if (!(requestError instanceof DOMException && requestError.name === 'AbortError')) {
        setError(requestError instanceof Error ? requestError.message : '검사결과를 불러오지 못했습니다.')
      }
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [category, interpretation, page, released, reloadKey, search, status])

  useEffect(() => {
    const controller = new AbortController()
    void load(controller.signal)
    return () => controller.abort()
  }, [load])

  const refresh = () => setReloadKey((value) => value + 1)
  const closeCreate = () => {
    setCreateOpen(false)
    if (searchParams.has('create')) {
      const next = new URLSearchParams(searchParams)
      next.delete('create')
      setSearchParams(next, { replace: true })
    }
  }

  return (
    <AccountPageLayout>
      <main className="examination-page">
        <header className="examination-page-heading">
          <div>
            <h1><ClipboardCheck size={28} /> 검사 결과</h1>
            <p>환자의 검사 수치와 판독 보고서를 확인하고 최종 확정·환자 공개까지 관리합니다.</p>
          </div>
          <button type="button" className="examination-primary-button" onClick={() => setCreateOpen(true)}>
            <Plus size={18} /> 새 검사 결과
          </button>
        </header>

        <section className="examination-list-card">
          <div className="examination-toolbar">
            <form onSubmit={(event) => { event.preventDefault(); setPage(1); setSearch(searchText.trim()) }}>
              <Search size={18} />
              <input type="search" enterKeyHint="search" value={searchText} onChange={(event) => setSearchText(event.target.value)} placeholder="환자명, 환자번호, 검사명 또는 검사코드 검색" />
              <button type="submit">검색</button>
            </form>
            <select aria-label="검사 분류" value={category} onChange={(event) => { setCategory(event.target.value as ExaminationCategory | ''); setPage(1) }}>
              <option value="">전체 분류</option><option value="LABORATORY">진단검사</option><option value="IMAGING">영상검사</option><option value="PHYSIOLOGY">생리기능검사</option><option value="PATHOLOGY">병리검사</option><option value="NEURO_ASSESSMENT">신경계 평가</option><option value="OTHER">기타</option>
            </select>
            <select aria-label="검사 상태" value={status} onChange={(event) => { setStatus(event.target.value as ExaminationStatus | ''); setPage(1) }}>
              <option value="">전체 상태</option><option value="PRELIMINARY">예비 결과</option><option value="FINAL">최종 결과</option><option value="CORRECTED">정정</option><option value="IN_PROGRESS">검사 중</option><option value="REGISTERED">등록</option><option value="CANCELLED">취소</option>
            </select>
            <select aria-label="결과 판정" value={interpretation} onChange={(event) => { setInterpretation(event.target.value as ExaminationInterpretation | ''); setPage(1) }}>
              <option value="">전체 판정</option><option value="CRITICAL">위험</option><option value="ABNORMAL">이상</option><option value="HIGH">높음</option><option value="LOW">낮음</option><option value="NORMAL">정상</option><option value="UNKNOWN">미판정</option>
            </select>
            <select aria-label="환자 공개 여부" value={released} onChange={(event) => { setReleased(event.target.value as '' | 'true' | 'false'); setPage(1) }}>
              <option value="">공개 전체</option><option value="true">환자 공개</option><option value="false">미공개</option>
            </select>
          </div>

          <div className="examination-list-summary">총 <strong>{meta.total_count}</strong>건</div>
          {error && <p className="examination-error" role="alert">{error}</p>}
          <div className="examination-table-wrap">
            <table className="examination-table">
              <thead><tr><th>판정</th><th>환자</th><th>검사</th><th>주요 결과</th><th>시행일</th><th>상태</th><th>환자 공개</th><th aria-label="상세" /></tr></thead>
              <tbody>
                {loading && <tr><td colSpan={8}>검사결과를 불러오는 중입니다.</td></tr>}
                {!loading && rows.length === 0 && <tr><td colSpan={8}>조건에 맞는 검사결과가 없습니다.</td></tr>}
                {!loading && rows.map((row) => (
                  <tr key={row.examination_id}>
                    <td><span className={`examination-interpretation interpretation-${row.overall_interpretation.toLowerCase()}`}>{row.overall_interpretation_label}</span></td>
                    <td><strong>{row.patient_name}</strong><small>{row.patient_number ?? '-'}</small></td>
                    <td><strong>{row.test_name}</strong><small>{row.test_code} · {row.category_label}</small></td>
                    <td><strong>{row.report?.summary || row.observations[0]?.formatted_value || '-'}</strong><small>{row.abnormal_count > 0 ? `이상 항목 ${row.abnormal_count}개` : `${row.observations.length}개 항목`}</small></td>
                    <td>{formatDateTime(row.performed_at)}</td>
                    <td><span className={`examination-status status-${row.status.toLowerCase()}`}>{row.status_label}</span></td>
                    <td>{row.report?.is_released_to_patient ? <span className="examination-release released">공개</span> : <span className="examination-release">미공개</span>}</td>
                    <td><button type="button" onClick={() => navigate(`/examinations/${row.examination_id}`)}>상세 보기</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <footer className="examination-pagination">
            <button type="button" disabled={page <= 1 || loading} onClick={() => setPage((value) => value - 1)}>이전</button>
            <span>{meta.page} / {meta.total_pages}</span>
            <button type="button" disabled={page >= meta.total_pages || loading} onClick={() => setPage((value) => value + 1)}>다음</button>
          </footer>
        </section>
      </main>

      {createOpen && <ExaminationCreateModal onClose={closeCreate} onCreated={(created) => { closeCreate(); refresh(); navigate(`/examinations/${created.examination_id}`) }} />}
      {examinationId && <ExaminationDetailModal examinationId={examinationId} onClose={() => navigate('/examinations')} onUpdated={refresh} />}
    </AccountPageLayout>
  )
}
