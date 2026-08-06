import { Check, Circle, Cpu, Database, FileCheck2, LoaderCircle, ScanLine } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { ApiError } from '../../core/api/apiError'
import { AccountPageLayout } from '../account/AccountPageLayout'
import { getCTCase, runCTCase } from './ct-analysis.api'
import type { CTCase } from './ct-analysis.types'
import './ct-analysis.css'

const steps = [
  { title: '입력 데이터 준비', description: '환자와 CT 매핑 및 GCS 입력 파일 확인', icon: Database },
  { title: 'NIfTI 검증', description: '영상 형식·크기·좌표계 검증', icon: FileCheck2 },
  { title: 'Cloud Run GPU 분석', description: 'nnU-Net 2.5D 모델 추론', icon: Cpu },
  { title: '병변 마스크 생성', description: '후처리·부피 계산·결과 저장', icon: ScanLine },
  { title: '분석 완료', description: '원본과 마스크 오버레이 준비', icon: Check },
]

const activeRunRequests = new Map<string, Promise<CTCase>>()

function requestCaseRun(caseId: string): Promise<CTCase> {
  const activeRequest = activeRunRequests.get(caseId)
  if (activeRequest) return activeRequest

  const request = runCTCase(caseId).finally(() => {
    if (activeRunRequests.get(caseId) === request) {
      activeRunRequests.delete(caseId)
    }
  })
  activeRunRequests.set(caseId, request)
  return request
}

export function CTAnalysisProcessPage() {
  const navigate = useNavigate()
  const { caseId = '' } = useParams()
  const [ctCase, setCTCase] = useState<CTCase | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!caseId) return
    let disposed = false
    let navigationTimer: number | undefined
    const startedAt = Date.now()
    const timer = window.setInterval(() => setElapsed(Math.floor((Date.now() - startedAt) / 1000)), 1000)
    let poller: number | undefined

    const stopTimers = () => {
      window.clearInterval(timer)
      if (poller !== undefined) window.clearInterval(poller)
    }
    const applyCase = (current: CTCase) => {
      if (disposed) return
      setCTCase(current)
      if (current.status === 'PROCESSING' || current.status === 'READY') setError('')
      if (current.status === 'COMPLETED') {
        stopTimers()
        navigationTimer = window.setTimeout(
          () => navigate(`/ct-analysis/${caseId}`, { replace: true }),
          1200,
        )
      } else if (current.status === 'FAILED') {
        stopTimers()
        setError(current.job?.error_message || 'AI 분석을 완료하지 못했습니다.')
      }
    }
    const pollCase = async () => {
      try {
        applyCase(await getCTCase(caseId))
      } catch {
        // 실행 요청의 연결이 끊겨도 서버 작업은 계속될 수 있으므로 다음 폴링을 유지한다.
      }
    }

    poller = window.setInterval(() => void pollCase(), 2500)
    void requestCaseRun(caseId)
      .then(applyCase)
      .catch(async (runError) => {
        if (!(runError instanceof ApiError && runError.code === 'JOB_ALREADY_RUNNING')) {
          setError('실행 요청 응답을 받지 못했습니다. 서버의 작업 상태를 계속 확인합니다.')
        }
        await pollCase()
      })

    return () => {
      disposed = true
      stopTimers()
      if (navigationTimer !== undefined) window.clearTimeout(navigationTimer)
    }
  }, [caseId, navigate])

  const completed = ctCase?.status === 'COMPLETED'
  const failed = ctCase?.status === 'FAILED'
  const displayedProgress = completed || failed
    ? 100
    : Math.min(90, Math.max(ctCase?.job?.progress ?? 20, 20 + elapsed * 3))
  const activeStep = completed ? 4 : failed ? 2 : displayedProgress < 35 ? 1 : displayedProgress < 75 ? 2 : 3

  return (
    <AccountPageLayout>
      <main className="ct-process-page">
        <section className="ct-process-card">
          <div className={`ct-process-orbit ${failed ? 'failed' : ''}`}><LoaderCircle size={44} /></div>
          <span className="ct-process-eyebrow">{ctCase?.display_id ?? 'CT 분석 작업'}</span>
          <h1>{failed ? '분석을 완료하지 못했습니다.' : completed ? '분석이 완료되었습니다.' : 'AI가 CT 영상을 분석하고 있습니다.'}</h1>
          <p>{failed ? ctCase?.job?.error_message || error : 'Cloud Run GPU에서 병변 영역을 분할하고 결과 마스크를 생성합니다.'}</p>
          <div className="ct-process-meta"><span>진행률 <strong>{displayedProgress}%</strong></span><span>경과 시간 <strong>{elapsed}초</strong></span><span>상태 <strong>{ctCase?.status_label ?? '준비 중'}</strong></span></div>

          <ol className="ct-process-steps">
            {steps.map((step, index) => {
              const Icon = step.icon
              const state = failed && index >= activeStep ? 'failed' : index < activeStep || completed ? 'done' : index === activeStep ? 'active' : 'waiting'
              return <li key={step.title} className={state}><div>{state === 'done' ? <Check size={19} /> : state === 'active' ? <LoaderCircle size={19} /> : <Circle size={16} />}</div><Icon size={21} /><span><strong>{step.title}</strong><small>{step.description}</small></span></li>
            })}
          </ol>

          {error && <p className="ct-error" role="alert">{error}</p>}
          {(failed || completed) && <button className="ct-process-result-button" type="button" onClick={() => navigate(`/ct-analysis/${caseId}`, { replace: true })}>{completed ? '분석 결과 보기' : '분석 화면으로 돌아가기'}</button>}
          {!failed && !completed && <small className="ct-process-notice">분석이 완료될 때까지 이 화면을 유지해 주세요.</small>}
        </section>
      </main>
    </AccountPageLayout>
  )
}
