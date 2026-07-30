# BrainOn

BrainOn은 환자·의료진 통합 모바일 앱, 의료진 CDSS, Django 업무 API, AI 통합 서비스와 CT 추론 서비스를 한 저장소에서 관리하는 의료 서비스 프로젝트입니다.

## 프로젝트 구성

| 경로 | 현재 역할 |
| --- | --- |
| `mobile/` | 환자·의료진 통합 Flutter 앱과 공통 인증 기반 |
| `frontend/` | 의료진 전용 React CDSS와 웹 인증 기반 |
| `backend/` | Django REST API, 사용자 역할, JWT 인증 및 업무 로직 |
| `ai/` | Genkit·Gemini·MCP 기반 AI 통합 서비스의 최소 실행 골격 |
| `inference/` | FastAPI Gateway, MOSEC, nnU-Net CT 추론 |
| `contracts/` | 합의된 서비스 간 API 계약과 가상 예시 |
| `docs/` | 아키텍처, API, 보안, 협업 및 배포 문서 |
| `scripts/` | Windows PowerShell 기준 실행·검증 안내 |

## 데이터 흐름

```text
일반: Flutter / React → Django REST API → PostgreSQL
AI:   Flutter / React → Django → Genkit + Gemini → MCP → Django 내부 API → PostgreSQL
CT:   React → Django → FastAPI Gateway → MOSEC → nnU-Net
알림: Django → FCM → Flutter
로컬 복약 알림: Flutter → flutter_local_notifications
```

AI와 MCP가 PostgreSQL에 직접 접근하지 않습니다. MCP 업무 도구는 향후 인증된 Django 내부 API를 호출합니다.

## 현재 구현됨

- Django Custom User와 `PATIENT`, `CLINICIAN`, `ADMIN` 역할
- 환자·의료진 최소 Profile, JWT 로그인·갱신·로그아웃, 공통 오류와 페이지네이션
- Flutter Router, Riverpod, Dio, 보안 토큰 저장 기반
- React Router, TanStack Query, Zustand, Cookie 기반 Refresh를 지원하는 fetch wrapper
- AI HTTP health endpoint와 비의료 Mock MCP 도구

예약·처방·검사 등 의료 업무 모델과 실제 화면은 후속 기능 개발 범위입니다.

## 로컬 시작

`.env.example`을 참고해 개인용 `.env`를 만든 뒤 각 서비스 README를 따릅니다. 기본 포트와 상세 검증 명령은 `docs/architecture/service-ports.md` 및 `scripts/verify/README.md`에 있습니다.

실제 환자 데이터, 의료 영상, 비밀키, Firebase Admin 서비스 계정, 모델 체크포인트 및 추론 결과를 Git에 올리지 않습니다.
