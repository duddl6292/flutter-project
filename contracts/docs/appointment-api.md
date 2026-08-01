# 예약 API

| Method | Endpoint | 기능 |
|---|---|---|
| GET | `/api/v1/appointments` | 예약 목록 |
| POST | `/api/v1/appointments` | 예약 생성 |
| GET | `/api/v1/appointments/{appointment_id}` | 상세 |
| PATCH | `/api/v1/appointments/{appointment_id}` | 일정·담당 의료진 변경 |
| POST | `/api/v1/appointments/{appointment_id}/cancel` | 취소 |

상태는 `SCHEDULED`, `COMPLETED`, `CANCELLED`, `NO_SHOW`입니다. 동일 의료진·시간 중복 예약은 `409`로 처리합니다.
