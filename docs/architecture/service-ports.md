# 서비스 포트

| 서비스 | 로컬 포트 | 상태 |
| --- | ---: | --- |
| React | 5173 | 구현됨 |
| Django | 8000 | 구현됨 |
| MOSEC | 8001 | 기존 추론 설정 유지 |
| FastAPI Gateway | 8100 | 기존 추론 설정 유지 |
| Genkit AI HTTP | 18200 | 최소 실행 골격 구현됨 |
| MCP Server | 18201 | 최소 Streamable HTTP 골격 구현됨 |
| PostgreSQL | 5432 | Compose 설정됨 |

AI와 MCP는 PostgreSQL에 직접 연결하지 않는다. 향후 MCP 도구는 인증된 Django 내부 API를 통해서만 업무 데이터에 접근한다.
