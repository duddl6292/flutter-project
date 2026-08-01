# 검사 결과 API

| Method | Endpoint | 기능 |
|---|---|---|
| GET | `/api/v1/test-results` | 환자 또는 의료진 검사 결과 목록 |
| POST | `/api/v1/test-results` | 결과 등록 |
| GET | `/api/v1/test-results/{test_result_id}` | 상세 |
| PATCH | `/api/v1/test-results/{test_result_id}` | 결과·소견 수정 |
| POST | `/api/v1/test-results/{test_result_id}/release` | 환자 공개 |

CT 추론 결과는 기술적 AI 산출물이며, 환자에게 공개되는 공식 결과와 분리합니다. 공개 시 `is_released_to_patient=true`, `released_at`, `released_by`를 저장하고 `TEST_RESULT_READY` 알림을 생성합니다.
