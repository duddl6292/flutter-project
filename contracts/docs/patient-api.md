# 환자 API

| Method | Endpoint | 역할 | 기능 |
|---|---|---|---|
| GET | `/api/v1/patients/me` | 환자 | 내 정보 |
| PATCH | `/api/v1/patients/me` | 환자 | 연락처 수정 |
| GET | `/api/v1/patients/me/home` | 환자 | 홈 요약 |
| GET | `/api/v1/patients` | 의료진/관리자 | 목록·검색 |
| POST | `/api/v1/patients` | 의료진/관리자 | 등록 |
| GET | `/api/v1/patients/{patient_id}` | 의료진/관리자 | 상세 |
| PATCH | `/api/v1/patients/{patient_id}` | 의료진/관리자 | 수정 |
| GET | `/api/v1/patients/{patient_id}/summary` | 의료진/관리자 | 진료 요약 |

환자 검색은 `keyword`, `status`, `page`, `page_size`를 지원합니다.
