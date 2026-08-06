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

AI HTTP는 18200, MCP 서버는 18201 포트를 사용합니다. 로컬에서는 Google Cloud ADC를 사용하고, Cloud Run에서는 서비스 계정으로 Vertex AI에 인증합니다.
