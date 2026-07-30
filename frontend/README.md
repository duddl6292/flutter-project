# BrainOn Frontend

의료진 전용 React·TypeScript CDSS입니다. 기존 Django health 확인 화면을 유지하면서 React Router, TanStack Query, Zustand 인증 상태 및 공통 fetch wrapper가 구성되어 있습니다.

Refresh Token은 HttpOnly Cookie로만 전달하며 JavaScript에서 읽지 않습니다. Access Token과 인증 사용자는 메모리에만 보관합니다. 실제 로그인 및 의료진 화면 디자인은 후속 구현 범위입니다.

```powershell
Set-Location frontend
npm.cmd ci
npm.cmd run dev
npm.cmd run build
```

로컬 기본 주소는 `http://localhost:5173`이며 API 주소는 `VITE_API_BASE_URL`로 설정합니다.
