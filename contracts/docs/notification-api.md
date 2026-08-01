# 알림 API

| Method | Endpoint | 기능 |
|---|---|---|
| POST | `/api/v1/devices` | FCM 토큰 등록·갱신 |
| DELETE | `/api/v1/devices/{device_id}` | 등록 해제 |
| GET | `/api/v1/notifications` | 내 알림 목록 |
| POST | `/api/v1/notifications` | 의료진이 환자 알림 생성 |
| PATCH | `/api/v1/notifications/{notification_id}/read` | 읽음 |
| PATCH | `/api/v1/notifications/read-all` | 모두 읽음 |

알림 DB 레코드 생성과 FCM 발송을 분리합니다. FCM 발송이 실패해도 알림 레코드는 남기고 재시도 여부를 기록하는 방식이 안전합니다.
