# 의료진·진료과 API

| Method | Endpoint | 기능 |
|---|---|---|
| GET | `/api/v1/departments` | 진료과 목록 |
| GET | `/api/v1/clinicians` | 의료진 검색 |
| GET | `/api/v1/clinicians/{clinician_id}` | 의료진 상세 |
| GET | `/api/v1/clinicians/me/dashboard` | 의료진 대시보드 |

예약 생성 전에 진료과와 의료진을 조회할 수 있어야 합니다. 검색 조건은 `keyword`, `department_id`, 페이지네이션을 사용합니다.
