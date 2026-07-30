import { useEffect, useState } from 'react'

type HealthStatus = 'loading' | 'connected' | 'unavailable'

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function App() {
  const [healthStatus, setHealthStatus] =
    useState<HealthStatus>('loading')

  useEffect(() => {
    const controller = new AbortController()

    async function checkBackend() {
      try {
        const response = await fetch(`${apiBaseUrl}/api/health/`, {
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error(`Backend returned ${response.status}`)
        }

        setHealthStatus('connected')
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          return
        }
        setHealthStatus('unavailable')
      }
    }

    void checkBackend()

    return () => controller.abort()
  }, [])

  const statusMessage = {
    loading: '백엔드 연결 확인 중',
    connected: '백엔드 연결 정상',
    unavailable: '백엔드에 연결할 수 없습니다',
  }[healthStatus]

  return (
    <main className="app-shell">
      <section className="welcome-card">
        <p className="eyebrow">BrainOn Medical</p>
        <h1>의료진용 웹</h1>
        <p>환자와 진료 정보를 관리할 기본 화면입니다.</p>
        <p className={`status status--${healthStatus}`}>
          {statusMessage}
        </p>
      </section>
    </main>
  )
}

export default App
