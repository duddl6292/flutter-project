# BrainOn 팀 작업 영역

이 문서는 담당자별 기본 작업 경계를 정의한다. 공유 파일이나 다른 담당 영역을 수정해야 한다면 작업 전에 담당자와 변경 범위를 합의한다.

## 담당 영역 1: Flutter 앱

작업 경로:

- `mobile/lib/features/auth/`
- `mobile/lib/features/patient/`
- `mobile/lib/features/clinician/`
- `mobile/lib/shared/`
- Flutter 화면 및 위젯

주요 작업:

- 역할 선택 및 로그인 화면
- 환자 앱 화면
- 의료진 앱 화면
- 예약, 복약, 검사 결과 화면
- 환자·의료진 대시보드
- 앱 내 화면 이동
- Mock 데이터 기반 UI 구현

Flutter 앱은 하나이며 로그인 역할에 따라 다음처럼 분기한다.

```text
Flutter
├─ PATIENT → 환자 모드
└─ CLINICIAN → 의료진 모드
```

## 담당 영역 2: React 의료진 CDSS

작업 경로:

- `frontend/src/app/`
- `frontend/src/core/`
- `frontend/src/features/`
- `frontend/src/shared/`

주요 작업:

- 의료진 전용 대시보드
- 환자 관리
- 예약 관리
- 처방전 작성
- 검사 결과 작성
- 협진 관리
- CT 분석 요청 및 결과 화면
- Mock 데이터 기반 UI 구현

React 웹은 환자용 웹이 아니라 의료진 전용 CDSS다.

## 담당 영역 3: Django·PostgreSQL

작업 경로:

- `backend/apps/`
- `backend/config/`
- `backend/tests/`

주요 작업:

- 사용자 인증과 환자·의료진 역할 관리
- 환자 정보, 예약, 처방, 검사 결과
- 진료 기록, 협진, 알림 데이터
- PostgreSQL 모델 및 마이그레이션
- Flutter·React 공통 REST API

## 담당 영역 4: 통합·AI·알림·추론

작업 경로:

- `ai/`
- `inference/`
- `contracts/`
- `docs/architecture/`
- Firebase 관련 공통 설정
- 루트 Compose 및 환경설정

주요 작업:

- FCM 연결 검증과 Flutter 로컬 알림
- Genkit + Gemini PoC
- MCP 서버 및 MCP 도구 호출 PoC
- FastAPI Gateway·MOSEC·nnU-Net 유지
- 서비스 간 연결
- 환경변수 및 Docker 구성
- 통합 smoke test

FCM, Genkit, MCP는 별도 브랜치에서 검증하여 다른 팀원의 UI 개발을 방해하지 않는다. `inference/`의 기존 추론 내부 로직은 유지한다.
