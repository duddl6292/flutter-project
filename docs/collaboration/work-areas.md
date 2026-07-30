# BrainOn 팀 작업 영역

## 김호영

- 백엔드 애플리케이션과 Django
- Genkit·Gemini
- MCP
- FCM
- 서비스 통합
- API 계약

주요 경로: `backend/`, `ai/`, `contracts/`, Flutter 알림·Firebase 공통 설정

## 김효은

- React 의료진 웹
- 웹 API 연동

주요 경로: `frontend/src/app/`, `frontend/src/core/`, `frontend/src/features/`, `frontend/src/shared/`

## 노지원

- Flutter 환자·의료진 앱
- 모바일 API 연동

주요 경로: `mobile/lib/features/`, `mobile/lib/shared/`, 화면과 일반 위젯

## 최유림

- PostgreSQL
- Docker
- Cloud
- CI/CD
- 운영 인프라

주요 경로: Compose, Dockerfile, `.github/workflows/`, `scripts/`, `docs/deployment/`

## 협의가 필요한 공유 파일

김호영과 노지원:

```text
mobile/lib/main.dart
mobile/pubspec.yaml
mobile/pubspec.lock
mobile/lib/firebase_options.dart
mobile/android/
mobile/ios/
```

김호영과 최유림:

```text
backend/config/settings.py
.env.example
compose.yaml
ai/ 배포 설정
Django 배포 설정
Secret 설정
```

김호영과 김효은·노지원:

```text
contracts/
API endpoint
요청·응답 형식
인증 동작
```
