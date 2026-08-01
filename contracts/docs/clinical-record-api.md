# 진료기록 API

| Method | Endpoint | 기능 |
|---|---|---|
| GET | `/api/v1/clinical-records` | 환자·예약 기준 진료기록 조회 |
| POST | `/api/v1/clinical-records` | 진료기록 작성 |
| GET | `/api/v1/clinical-records/{clinical_record_id}` | 상세 |
| PATCH | `/api/v1/clinical-records/{clinical_record_id}` | 수정 |

진료기록은 내부 의료진용 `subjective`, `objective`, `assessment`, `plan`과 환자에게 보여줄 `patient_visible_summary`를 구분합니다.
