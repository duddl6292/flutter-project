# 처방·복약 API

## 처방

| Method | Endpoint | 기능 |
|---|---|---|
| GET | `/api/v1/prescriptions` | 목록 |
| POST | `/api/v1/prescriptions` | 처방과 약 항목 생성 |
| GET | `/api/v1/prescriptions/{prescription_id}` | 상세 |
| PATCH | `/api/v1/prescriptions/{prescription_id}` | 수정 |
| POST | `/api/v1/prescriptions/{prescription_id}/discontinue` | 중단 |

## 복약

| Method | Endpoint | 기능 |
|---|---|---|
| GET | `/api/v1/patients/me/medications` | 현재 약 목록 |
| GET | `/api/v1/medication-schedules` | 복약 일정 |
| GET | `/api/v1/medication-records` | 복약 기록 |
| POST | `/api/v1/medication-records` | 복용·미복용·건너뜀 기록 |

정시 알림은 Flutter 로컬 알림이 담당하고, 서버는 일정과 사용자의 복약 기록을 관리합니다.
