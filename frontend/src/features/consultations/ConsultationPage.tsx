import { Handshake, Plus, Search } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { AccountPageLayout } from '../account/AccountPageLayout'
import { getConsultations } from './consultation.api'
import { ConsultationCreateModal } from './ConsultationCreateModal'
import { ConsultationDetailModal } from './ConsultationDetailModal'
import type {
  Consultation,
  ConsultationBox,
  ConsultationListMeta,
  ConsultationPriority,
  ConsultationStatus,
} from './consultation.types'
import './consultations.css'

const initialMeta: ConsultationListMeta = {
  page: 1, page_size: 20, total_count: 0, total_pages: 1,
}

const formatDateTime = (value: string | null) => value
  ? new Intl.DateTimeFormat('ko-KR', {
    year: '2-digit', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  }).format(new Date(value))
  : '-'

export function ConsultationPage() {
  const navigate = useNavigate()
  const { consultationId } = useParams()
  const [consultations, setConsultations] = useState<Consultation[]>([])
  const [meta, setMeta] = useState(initialMeta)
  const [box, setBox] = useState<ConsultationBox>('all')
  const [status, setStatus] = useState<ConsultationStatus | ''>('')
  const [priority, setPriority] = useState<ConsultationPriority | ''>('')
  const [searchText, setSearchText] = useState('')
  const [submittedSearch, setSubmittedSearch] = useState('')
  const [page, setPage] = useState(1)
  const [reloadKey, setReloadKey] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [createOpen, setCreateOpen] = useState(false)

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const response = await getConsultations({
        box, status, priority, search: submittedSearch,
        page, pageSize: 20, signal,
      })
      setConsultations(response.data)
      setMeta(response.meta)
    } catch (requestError) {
      if (!(requestError instanceof DOMException && requestError.name === 'AbortError')) {
        setError(requestError instanceof Error ? requestError.message : '협진 목록을 불러오지 못했습니다.')
      }
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [box, page, priority, reloadKey, status, submittedSearch])

  useEffect(() => {
    const controller = new AbortController()
    void load(controller.signal)
    return () => controller.abort()
  }, [load])

  const refresh = () => setReloadKey((value) => value + 1)
  const resetPage = () => setPage(1)

  return (
    <AccountPageLayout>
      <main className="consultation-page">
        <header className="consultation-page-heading">
          <div>
            <h1><Handshake size={28} /> 협진 관리</h1>
            <p>의료진 간 협진 요청을 확인하고 환자별 의견을 안전하게 공유합니다.</p>
          </div>
          <button type="button" className="consultation-primary-button" onClick={() => setCreateOpen(true)}><Plus size={18} /> 새 협진 요청</button>
        </header>

        <section className="consultation-list-card">
          <div className="consultation-box-tabs">
            {([
              ['all', '전체 협진'], ['received', '받은 협진'], ['sent', '보낸 협진'],
            ] as Array<[ConsultationBox, string]>).map(([value, label]) => (
              <button key={value} type="button" className={box === value ? 'active' : ''} onClick={() => { setBox(value); resetPage() }}>{label}</button>
            ))}
          </div>

          <div className="consultation-toolbar">
            <form onSubmit={(event) => { event.preventDefault(); resetPage(); setSubmittedSearch(searchText.trim()) }}>
              <Search size={18} />
              <input type="search" enterKeyHint="search" value={searchText} onChange={(event) => setSearchText(event.target.value)} placeholder="환자명, 환자번호, 제목, 의료진 검색" />
              <button type="submit">검색</button>
            </form>
            <select aria-label="협진 상태" value={status} onChange={(event) => { setStatus(event.target.value as ConsultationStatus | ''); resetPage() }}>
              <option value="">전체 상태</option><option value="REQUESTED">요청</option><option value="IN_PROGRESS">진행 중</option><option value="COMPLETED">완료</option><option value="CANCELLED">취소</option>
            </select>
            <select aria-label="협진 우선순위" value={priority} onChange={(event) => { setPriority(event.target.value as ConsultationPriority | ''); resetPage() }}>
              <option value="">전체 우선순위</option><option value="ROUTINE">일반</option><option value="URGENT">긴급</option><option value="EMERGENCY">응급</option>
            </select>
          </div>

          <div className="consultation-list-summary">총 <strong>{meta.total_count}</strong>건</div>
          {error && <p className="consultation-error" role="alert">{error}</p>}

          <div className="consultation-table-wrap">
            <table className="consultation-table">
              <thead><tr><th>우선순위</th><th>환자</th><th>협진 내용</th><th>요청자 → 담당자</th><th>요청일 / 희망일</th><th>상태</th><th aria-label="상세" /></tr></thead>
              <tbody>
                {loading && <tr><td colSpan={7}>협진 목록을 불러오는 중입니다.</td></tr>}
                {!loading && consultations.length === 0 && <tr><td colSpan={7}>조건에 맞는 협진이 없습니다.</td></tr>}
                {!loading && consultations.map((consultation) => (
                  <tr key={consultation.consultation_id} className={consultation.unread_count > 0 ? 'unread' : ''}>
                    <td><span className={`consultation-priority priority-${consultation.priority.toLowerCase()}`}>{consultation.priority_label}</span></td>
                    <td><strong>{consultation.patient_name}</strong><small>{consultation.patient_number ?? '-'}</small></td>
                    <td><strong>{consultation.subject}</strong><small>{consultation.department_name}{consultation.unread_count > 0 ? ` · 새 메시지 ${consultation.unread_count}` : ''}</small></td>
                    <td>{consultation.requester.name}<span> → </span>{consultation.consultant.name}</td>
                    <td>{formatDateTime(consultation.created_at)}<small>희망 {formatDateTime(consultation.due_at)}</small></td>
                    <td><span className={`consultation-status status-${consultation.status.toLowerCase()}`}>{consultation.status_label}</span></td>
                    <td><button type="button" onClick={() => navigate(`/consultations/${consultation.consultation_id}`)}>상세 보기</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <footer className="consultation-pagination">
            <button type="button" disabled={page <= 1 || loading} onClick={() => setPage((value) => value - 1)}>이전</button>
            <span>{meta.page} / {meta.total_pages}</span>
            <button type="button" disabled={page >= meta.total_pages || loading} onClick={() => setPage((value) => value + 1)}>다음</button>
          </footer>
        </section>
      </main>

      {createOpen && <ConsultationCreateModal onClose={() => setCreateOpen(false)} onCreated={(consultation) => { setCreateOpen(false); refresh(); navigate(`/consultations/${consultation.consultation_id}`) }} />}
      {consultationId && <ConsultationDetailModal consultationId={consultationId} onClose={() => navigate('/consultations')} onUpdated={refresh} />}
    </AccountPageLayout>
  )
}
