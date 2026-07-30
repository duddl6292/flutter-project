# 환경변수 관리

- 루트 `.env.example`은 변수명과 안전한 로컬 예시만 제공합니다.
- 실제 값은 추적되지 않는 `.env` 또는 배포 플랫폼 Secret에 둡니다.
- PostgreSQL, Django, React, inference, Firebase Admin, Gemini, MCP 설정을 분리해 관리합니다.
- AI HTTP 포트는 8200, MCP 서버 포트는 8201로 확정되어 있습니다.
- Flutter `google-services.json`은 클라이언트 설정이며 Firebase Admin 서비스 계정 키와 다릅니다.
- `FIREBASE_CREDENTIALS_PATH`에 저장소 내부 실제 경로를 고정하지 않습니다.
- 운영의 JWT Refresh Cookie는 HTTPS에서 Secure를 활성화하고 배포 구조에 맞춰 SameSite·CORS·CSRF를 함께 설정합니다.
- Cloud Run과 GPU 서버에는 필요한 Secret만 최소 권한으로 주입합니다.
