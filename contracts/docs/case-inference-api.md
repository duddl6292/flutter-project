# CT Case·추론 API

## 공개 API: React → Django

| Method | Endpoint | 기능 |
|---|---|---|
| POST | `/api/v1/cases` | Case 생성 |
| GET | `/api/v1/cases` | 목록 |
| GET | `/api/v1/cases/{case_id}` | 상세 |
| POST | `/api/v1/cases/{case_id}/upload-url` | Signed URL 발급 |
| POST | `/api/v1/cases/{case_id}/upload-complete` | 업로드 검증·완료 |
| POST | `/api/v1/cases/{case_id}/inference` | 추론 Job 생성 |
| GET | `/api/v1/inference-jobs/{job_id}` | 상태 |
| POST | `/api/v1/inference-jobs/{job_id}/cancel` | 취소 |
| GET | `/api/v1/cases/{case_id}/result` | 최종 AI 결과 |
| GET | `/api/v1/cases/{case_id}/viewer` | Viewer용 Signed URL |

## 내부 API: Django ↔ FastAPI

| Method | Endpoint | 기능 |
|---|---|---|
| POST | `/internal/v1/inference/jobs` | 추론 접수 |
| GET | `/internal/v1/inference/jobs/{job_id}` | 상태 |
| POST | `/internal/v1/inference/callback` | 완료·실패 전달 |
| GET | `/internal/v1/health` | 상태 |
| GET | `/internal/v1/model` | 모델 정보 |

CT 파일은 DB에 저장하지 않고 Cloud Storage 경로만 저장합니다. `upload-complete`에서 객체 존재, 크기, 해시를 검증한 뒤에만 추론을 허용합니다.
