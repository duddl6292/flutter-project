# 협진 API

| Method | Endpoint | 기능 |
|---|---|---|
| GET | `/api/v1/consultations` | 협진 요청 목록 |
| POST | `/api/v1/consultations` | 협진 요청 |
| GET | `/api/v1/consultations/{consultation_id}` | 상세 |
| PATCH | `/api/v1/consultations/{consultation_id}` | 상태·답변 변경 |

상태는 `REQUESTED`, `IN_REVIEW`, `COMPLETED`, `CANCELLED`입니다. 협진은 의료진 전용이며 환자에게 자동 공개하지 않습니다.
