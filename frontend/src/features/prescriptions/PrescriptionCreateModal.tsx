import {
  Plus,
  Trash2,
  X,
} from 'lucide-react'

import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  createPrescription,
  getPrescriptionContexts,
} from './prescription.api'

import type {
  Prescription,
  PrescriptionContext,
  PrescriptionItemInput,
} from './prescription.types'

interface PrescriptionCreateModalProps {
  onClose: () => void
  onCreated: (
    prescription: Prescription,
  ) => void
}

function todayValue(): string {
  const now = new Date()
  const offset =
    now.getTimezoneOffset() * 60_000

  return new Date(now.getTime() - offset)
    .toISOString()
    .slice(0, 10)
}

function emptyItem(): PrescriptionItemInput {
  return {
    medicine_name: '',
    dosage: '1',
    dose_unit: '정',
    frequency: '하루 1회',
    route: '경구',
    instructions: '',
    start_date: todayValue(),
    end_date: null,
  }
}

export function PrescriptionCreateModal({
  onClose,
  onCreated,
}: PrescriptionCreateModalProps) {
  const [contexts, setContexts] =
    useState<PrescriptionContext[]>([])
  const [contextId, setContextId] =
    useState('')
  const [notes, setNotes] =
    useState('')
  const [items, setItems] =
    useState<PrescriptionItemInput[]>([
      emptyItem(),
    ])
  const [loading, setLoading] =
    useState(true)
  const [saving, setSaving] =
    useState(false)
  const [error, setError] =
    useState('')

  useEffect(() => {
    let active = true

    void getPrescriptionContexts()
      .then((data) => {
        if (!active) return

        setContexts(data)
        setContextId(
          data[0]?.clinical_record_id ?? '',
        )
      })
      .catch((requestError) => {
        if (!active) return

        setError(
          requestError instanceof Error
            ? requestError.message
            : '처방 가능한 진료기록을 불러오지 못했습니다.',
        )
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    const handleKeyDown = (
      event: KeyboardEvent,
    ) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    window.addEventListener(
      'keydown',
      handleKeyDown,
    )

    return () => {
      window.removeEventListener(
        'keydown',
        handleKeyDown,
      )
    }
  }, [onClose])

  const selectedContext = useMemo(
    () => contexts.find(
      (context) =>
        context.clinical_record_id
        === contextId,
    ),
    [contexts, contextId],
  )

  const updateItem = (
    index: number,
    field: keyof PrescriptionItemInput,
    value: string | null,
  ) => {
    setItems((current) =>
      current.map(
        (item, itemIndex) =>
          itemIndex === index
            ? {
              ...item,
              [field]: value,
            }
            : item,
      ),
    )
  }

  const submit = async (
    status: 'DRAFT' | 'ACTIVE',
  ) => {
    setError('')

    if (!contextId) {
      setError(
        '처방할 환자의 진료기록을 선택해주세요.',
      )
      return
    }

    if (
      items.some(
        (item) =>
          !item.medicine_name.trim()
          || !item.dosage
          || Number(item.dosage) <= 0
          || !item.dose_unit.trim()
          || !item.frequency.trim(),
      )
    ) {
      setError(
        '각 약품의 이름, 용량, 단위와 복용 빈도를 확인해주세요.',
      )
      return
    }

    setSaving(true)

    try {
      const prescription =
        await createPrescription({
          clinical_record_id: contextId,
          status,
          notes: notes.trim(),
          items: items.map((item) => ({
            ...item,
            medicine_name:
              item.medicine_name.trim(),
            dose_unit:
              item.dose_unit.trim(),
            frequency:
              item.frequency.trim(),
            route:
              item.route.trim(),
            instructions:
              item.instructions.trim(),
            end_date:
              item.end_date || null,
          })),
        })

      onCreated(prescription)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : '처방전을 저장하지 못했습니다.',
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      className="prescription-modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose()
        }
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="prescription-create-title"
        className="prescription-modal prescription-create-modal"
      >
        <header className="prescription-modal-header">
          <div>
            <h2 id="prescription-create-title">
              새 처방전 작성
            </h2>
            <p>
              진료기록을 선택하고 처방 약품을 입력합니다.
            </p>
          </div>

          <button
            type="button"
            aria-label="닫기"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </header>

        <div className="prescription-modal-body">
          {loading ? (
            <p className="prescription-message">
              진료기록을 불러오는 중입니다.
            </p>
          ) : (
            <>
              <label className="prescription-field">
                <span>환자·진료기록</span>
                <select
                  value={contextId}
                  onChange={(event) =>
                    setContextId(
                      event.target.value,
                    )
                  }
                >
                  {contexts.length === 0 && (
                    <option value="">
                      처방 가능한 진료기록이 없습니다
                    </option>
                  )}

                  {contexts.map((context) => (
                    <option
                      key={
                        context.clinical_record_id
                      }
                      value={
                        context.clinical_record_id
                      }
                    >
                      {context.patient_name}
                      {' ('}
                      {context.patient_number ?? '-'}
                      {') · '}
                      {context.encounter_number}
                    </option>
                  ))}
                </select>
              </label>

              {selectedContext && (
                <p className="selected-prescription-context">
                  {selectedContext.patient_name}
                  {' · 진료기록 '}
                  {new Date(
                    selectedContext.recorded_at,
                  ).toLocaleString('ko-KR')}
                </p>
              )}

              <div className="prescription-items-heading">
                <h3>처방 약품</h3>
                <button
                  type="button"
                  onClick={() =>
                    setItems((current) => [
                      ...current,
                      emptyItem(),
                    ])
                  }
                >
                  <Plus size={16} />
                  약품 추가
                </button>
              </div>

              <div className="prescription-item-editor-list">
                {items.map((item, index) => (
                  <article
                    className="prescription-item-editor"
                    key={index}
                  >
                    <header>
                      <strong>약품 {index + 1}</strong>

                      <button
                        type="button"
                        aria-label={`약품 ${index + 1} 삭제`}
                        disabled={items.length === 1}
                        onClick={() =>
                          setItems((current) =>
                            current.filter(
                              (_value, itemIndex) =>
                                itemIndex !== index,
                            ),
                          )
                        }
                      >
                        <Trash2 size={16} />
                      </button>
                    </header>

                    <div className="prescription-item-grid">
                      <label>
                        <span>약품명</span>
                        <input
                          value={item.medicine_name}
                          placeholder="예: 아스피린"
                          onChange={(event) =>
                            updateItem(
                              index,
                              'medicine_name',
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label>
                        <span>1회 용량</span>
                        <input
                          type="number"
                          min="0.0001"
                          step="0.0001"
                          value={item.dosage}
                          onChange={(event) =>
                            updateItem(
                              index,
                              'dosage',
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label>
                        <span>단위</span>
                        <input
                          value={item.dose_unit}
                          placeholder="mg, mL, 정"
                          onChange={(event) =>
                            updateItem(
                              index,
                              'dose_unit',
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label>
                        <span>복용 빈도</span>
                        <input
                          value={item.frequency}
                          placeholder="예: 하루 2회"
                          onChange={(event) =>
                            updateItem(
                              index,
                              'frequency',
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label>
                        <span>투여 경로</span>
                        <input
                          value={item.route}
                          placeholder="예: 경구"
                          onChange={(event) =>
                            updateItem(
                              index,
                              'route',
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label>
                        <span>복용 시작일</span>
                        <input
                          type="date"
                          value={item.start_date}
                          onChange={(event) =>
                            updateItem(
                              index,
                              'start_date',
                              event.target.value,
                            )
                          }
                        />
                      </label>

                      <label>
                        <span>복용 종료일</span>
                        <input
                          type="date"
                          min={item.start_date}
                          value={item.end_date ?? ''}
                          onChange={(event) =>
                            updateItem(
                              index,
                              'end_date',
                              event.target.value || null,
                            )
                          }
                        />
                      </label>

                      <label className="prescription-wide-field">
                        <span>복약 지시</span>
                        <input
                          value={item.instructions}
                          placeholder="예: 아침 식후 복용"
                          onChange={(event) =>
                            updateItem(
                              index,
                              'instructions',
                              event.target.value,
                            )
                          }
                        />
                      </label>
                    </div>
                  </article>
                ))}
              </div>

              <label className="prescription-field">
                <span>처방 참고사항</span>
                <textarea
                  rows={3}
                  value={notes}
                  onChange={(event) =>
                    setNotes(event.target.value)
                  }
                />
              </label>
            </>
          )}

          {error && (
            <p
              role="alert"
              className="prescription-error"
            >
              {error}
            </p>
          )}
        </div>

        <footer className="prescription-modal-footer">
          <button
            type="button"
            className="prescription-secondary-button"
            onClick={onClose}
          >
            취소
          </button>

          <button
            type="button"
            className="prescription-primary-button"
            disabled={saving || loading}
            onClick={() => {
              void submit('ACTIVE')
            }}
          >
            {saving ? '저장 중' : '처방 발행'}
          </button>
        </footer>
      </section>
    </div>
  )
}
