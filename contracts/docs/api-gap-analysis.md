# 기본 API 검토 결과

## 이미 포함되어 있어 좋은 영역

- JWT 로그인·갱신·로그아웃·현재 사용자
- 환자 본인/의료진 환자 조회
- 예약 조회·생성·변경·취소
- 처방·복약 일정·복약 기록
- CT Case 생성, Signed URL 업로드, 업로드 완료
- 비동기 추론 Job, 상태, 취소, 결과
- Django ↔ FastAPI 내부 추론 계약
- FCM 기기 등록과 알림 조회/읽음
- 환자 홈 요약과 의료진 대시보드
- 공통 성공·목록·오류 응답 형식

## 추가가 필요한 큰 API 영역

### 1. 의료진·진료과 API — 필수

예약 화면에서 의료진과 진료과를 선택하고, 의료진 프로필 및 담당 부서를 표시하려면 필요합니다.

- `GET /api/v1/departments`
- `GET /api/v1/clinicians`
- `GET /api/v1/clinicians/{clinician_id}`
- `GET /api/v1/clinicians/me/dashboard`

### 2. 진료기록 API — 필수

예약 완료 후 의사 소견, 평가, 치료 계획을 남기고 처방과 연결하는 기준 리소스입니다.

- `GET/POST /api/v1/clinical-records`
- `GET/PATCH /api/v1/clinical-records/{clinical_record_id}`

### 3. 일반 검사 결과 및 환자 공개 API — 필수

CT AI 기술 결과와 환자에게 보여주는 공식 검사 결과를 분리해야 합니다. `is_released_to_patient`, `released_at`, `released_by`를 이 리소스가 관리합니다.

- `GET/POST /api/v1/test-results`
- `GET/PATCH /api/v1/test-results/{test_result_id}`
- `POST /api/v1/test-results/{test_result_id}/release`

### 4. 협진 API — 프로젝트 기능에 포함한다면 필요

- `GET/POST /api/v1/consultations`
- `GET/PATCH /api/v1/consultations/{consultation_id}`

### 5. 의료진이 환자에게 보내는 알림 생성 API — 필수

기존 문서에는 환자 측 조회/읽음만 있으므로, 예약 변경·처방 등록·검사 결과 공개 시 Django가 알림 레코드를 만드는 계약을 추가했습니다.

- `POST /api/v1/notifications`

### 6. 서비스 상태 API — 권장

Compose, Cloud Run, 배포 점검에 필요합니다.

- `GET /api/v1/health`
- `GET /internal/v1/health`
- `GET /internal/v1/model`

## 지금은 API로 만들지 않아도 되는 기능

- 응급 FAST 안내와 119 연결: 앱 내 정적 화면 및 전화 URI로 처리
- 복약 정시 알림: Flutter 로컬 알림이 담당하며 서버는 복약 일정만 제공
- 근처 병원 검색: 지도/장소 API를 붙일 때 별도 설계
- 신원미상 환자 병합: 데이터 모델과 감사 정책 확정 후 후순위 구현

## 계약 정규화 결정

- 역할 값은 `PATIENT`, `CLINICIAN`, `ADMIN`으로 통일
- 상태 enum은 대문자 snake case로 통일
- 모든 성공 응답은 `data` wrapper 사용
- 공개 API와 내부 추론 API를 분리
- CT 기술 결과는 `/cases/{case_id}/result`, 환자 공개용 의료 결과는 `/test-results`에서 관리
- 클라이언트는 FastAPI/MOSEC를 직접 호출하지 않음
