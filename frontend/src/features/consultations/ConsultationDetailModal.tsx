import { useCallback, useEffect, useState } from 'react'
import { Send, X } from 'lucide-react'

import {
  acceptConsultation,
  cancelConsultation,
  completeConsultation,
  getConsultation,
  sendConsultationMessage,
} from './consultation.api'
import type { Consultation } from './consultation.types'

const formatDateTime = (value: string | null) => value
  ? new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  }).format(new Date(value))
  : '-'

export function ConsultationDetailModal({
  consultationId,
  onClose,
  onUpdated,
}: {
  consultationId: string
  onClose: () => void
  onUpdated: () => void
}) {
  const [consultation, setConsultation] = useState<Consultation | null>(null)
  const [message, setMessage] = useState('')
  const [finalResponse, setFinalResponse] = useState('')
  const [cancelReason, setCancelReason] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true)
    setError('')
    try {
      const data = await getConsultation(consultationId, signal)
      setConsultation(data)
      setFinalResponse(data.response)
    } catch (requestError) {
      if (!(requestError instanceof DOMException && requestError.name === 'AbortError')) {
        setError(requestError instanceof Error ? requestError.message : '협진 상세를 불러오지 못했습니다.')
      }
    } finally {
      if (!signal?.aborted) setLoading(false)
    }
  }, [consultationId])

  useEffect(() => {
    const controller = new AbortController()
    void load(controller.signal)
    return () => controller.abort()
  }, [load])

  const runAction = async (action: () => Promise<Consultation>) => {
    setSaving(true)
    setError('')
    try {
      const updated = await action()
      setConsultation(updated)
      setFinalResponse(updated.response)
      onUpdated()
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : '요청을 처리하지 못했습니다.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="consultation-modal-backdrop" role="presentation">
      <section className="consultation-modal consultation-detail-modal" role="dialog" aria-modal="true" aria-label="협진 상세">
        <header className="consultation-modal-header">
          <div>
            <h2>{consultation?.subject ?? '협진 상세'}</h2>
            <p>{consultation ? `${consultation.patient_name} · ${consultation.encounter_number}` : '협진 정보를 불러오고 있습니다.'}</p>
          </div>
          <button type="button" aria-label="닫기" onClick={onClose}><X size={22} /></button>
        </header>

        {error && <p className="consultation-error" role="alert">{error}</p>}
        {loading && <p className="consultation-message-state">협진 상세를 불러오는 중입니다.</p>}

        {consultation && (
          <div className="consultation-detail-content">
            <section className="consultation-detail-summary">
              <div><span>상태</span><strong className={`consultation-status status-${consultation.status.toLowerCase()}`}>{consultation.status_label}</strong></div>
              <div><span>우선순위</span><strong className={`consultation-priority priority-${consultation.priority.toLowerCase()}`}>{consultation.priority_label}</strong></div>
              <div><span>요청자</span><strong>{consultation.requester.name} · {consultation.requester.department_name}</strong></div>
              <div><span>담당자</span><strong>{consultation.consultant.name} · {consultation.consultant.department_name}</strong></div>
              <div><span>답변 희망일</span><strong>{formatDateTime(consultation.due_at)}</strong></div>
            </section>

            <section className="consultation-question-card">
              <h3>협진 요청 내용</h3>
              <p>{consultation.question}</p>
            </section>

            <section className="consultation-thread">
              <h3>협진 대화</h3>
              <div className="consultation-thread-list">
                {consultation.messages.map((item) => (
                  <article key={item.message_id} className={`consultation-thread-item ${item.is_system ? 'system' : ''}`}>
                    {!item.is_system && <strong>{item.sender?.name ?? '의료진'} <small>{item.sender?.department_name}</small></strong>}
                    <p>{item.content}</p>
                    <time>{formatDateTime(item.created_at)}</time>
                  </article>
                ))}
              </div>

              {!['COMPLETED', 'CANCELLED'].includes(consultation.status) && (
                <form
                  className="consultation-message-form"
                  onSubmit={async (event) => {
                    event.preventDefault()
                    if (!message.trim()) return
                    setSaving(true)
                    setError('')
                    try {
                      await sendConsultationMessage(consultation.consultation_id, message.trim())
                      setMessage('')
                      await load()
                      onUpdated()
                    } catch (requestError) {
                      setError(requestError instanceof Error ? requestError.message : '메시지를 전송하지 못했습니다.')
                    } finally {
                      setSaving(false)
                    }
                  }}
                >
                  <textarea rows={3} value={message} onChange={(event) => setMessage(event.target.value)} placeholder="협진 메시지를 입력하세요." />
                  <button type="submit" disabled={saving || !message.trim()} aria-label="메시지 전송"><Send size={18} /> 전송</button>
                </form>
              )}
            </section>

            {consultation.status === 'COMPLETED' && (
              <section className="consultation-final-card">
                <h3>최종 협진 소견</h3>
                <p>{consultation.response}</p>
                <time>{formatDateTime(consultation.completed_at)}</time>
              </section>
            )}

            {consultation.my_role === 'CONSULTANT' && consultation.status === 'REQUESTED' && (
              <div className="consultation-workflow-card">
                <div><h3>협진 요청을 확인하셨나요?</h3><p>수락하면 진행 중 상태로 변경됩니다.</p></div>
                <button type="button" className="consultation-primary-button" disabled={saving} onClick={() => void runAction(() => acceptConsultation(consultation.consultation_id))}>협진 수락</button>
              </div>
            )}

            {consultation.my_role === 'CONSULTANT' && consultation.status === 'IN_PROGRESS' && (
              <section className="consultation-complete-card">
                <h3>최종 협진 소견</h3>
                <textarea rows={6} value={finalResponse} onChange={(event) => setFinalResponse(event.target.value)} placeholder="진료에 반영할 수 있는 최종 소견을 작성해주세요." />
                <button type="button" className="consultation-primary-button" disabled={saving || !finalResponse.trim()} onClick={() => void runAction(() => completeConsultation(consultation.consultation_id, finalResponse.trim()))}>답변 등록 및 완료</button>
              </section>
            )}

            {consultation.my_role === 'REQUESTER' && ['REQUESTED', 'IN_PROGRESS'].includes(consultation.status) && (
              <section className="consultation-cancel-card">
                <h3>협진 취소</h3>
                <div>
                  <input value={cancelReason} onChange={(event) => setCancelReason(event.target.value)} placeholder="취소 사유(선택)" />
                  <button type="button" disabled={saving} onClick={() => void runAction(() => cancelConsultation(consultation.consultation_id, cancelReason.trim()))}>협진 취소</button>
                </div>
              </section>
            )}
          </div>
        )}
      </section>
    </div>
  )
}
