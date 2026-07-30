# BrainOn AI

Genkit·Gemini·MCP 기반 AI 통합 서비스의 최소 실행 골격입니다.

현재 구현:

- `GET /health`: Gemini 키 없이 실행 가능
- `/assistant`: 키가 있을 때만 Gemini 모델 호출
- MCP Streamable HTTP 서버와 비의료 `getSystemStatus` Mock 도구
- 환경변수 검증, TypeScript 빌드 및 테스트

AI와 MCP는 PostgreSQL에 직접 접근하지 않습니다. 향후 예약·복약·검사 도구는 Django 내부 API를 통해서만 구현합니다.

```powershell
Set-Location ai
npm.cmd ci
npm.cmd run typecheck
npm.cmd run build
npm.cmd test
npm.cmd run dev
npm.cmd run dev:mcp
```

AI HTTP는 8200, MCP 서버는 8201 포트를 사용합니다. 실제 `GEMINI_API_KEY`는 로컬 `.env` 또는 배포 Secret으로만 제공하며 Git에 기록하지 않습니다.
