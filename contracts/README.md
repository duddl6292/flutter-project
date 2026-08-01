# BrainOn API Contracts

Flutter 환자 앱, React 의료진 웹, Django REST API, FastAPI/MOSEC 추론 서비스가 공유하는 API 계약입니다.

## 구성

```text
contracts/
├─ openapi/
│  ├─ public-api.yaml       # Flutter/React → Django
│  └─ inference-api.yaml    # Django ↔ FastAPI/MOSEC 내부 통신
├─ docs/
│  ├─ api-gap-analysis.md
│  ├─ common-conventions.md
│  ├─ auth-api.md
│  ├─ clinician-api.md
│  ├─ patient-api.md
│  ├─ appointment-api.md
│  ├─ clinical-record-api.md
│  ├─ prescription-medication-api.md
│  ├─ test-result-api.md
│  ├─ consultation-api.md
│  ├─ case-inference-api.md
│  ├─ notification-api.md
│  └─ patient-merge-api.md
└─ examples/
   └─ *.example.json
```

## 기준

- 외부 API prefix: `/api/v1`
- 내부 추론 API prefix: `/internal/v1`
- 시간: ISO 8601, 한국 시간대 포함 (`2026-08-05T10:30:00+09:00`)
- ID: UUID
- 역할: `PATIENT`, `CLINICIAN`, `ADMIN`
- 성공 응답: `{"data": ...}`
- 목록 응답: `{"data": [...], "meta": {...}}`
- 오류 응답: `{"error": {"code": "...", "message": "...", "details": {...}}}`

## 우선 구현 순서

1. 인증 및 현재 사용자
2. 환자/의료진 조회
3. 예약
4. 진료기록 및 처방/복약
5. CT Case 업로드와 추론 Job
6. 일반 검사 결과 등록·환자 공개
7. 알림 및 FCM 기기 등록
8. 협진
9. 환자 병합(후순위)

OpenAPI 파일이 최종 계약의 기준이며, 문서와 예시 JSON은 이해 및 테스트를 돕는 보조 자료입니다.
