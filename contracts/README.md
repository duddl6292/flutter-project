# API 계약 운영 원칙

`contracts/`는 Flutter, React, Django, 추론 서비스 사이의 합의된 요청·응답 예시를 관리한다.

- React와 Flutter 담당자가 API 형식을 임의로 확정하지 않는다.
- Django 담당자가 일반 서비스 API 계약 초안을 작성한다.
- 관련 프론트엔드 담당자와 합의한 뒤 `contracts/`에 반영한다.
- Mock 데이터는 공식 API 계약이 아니다.
- 실제 환자 정보는 계약 예시에 사용하지 않는다.
- API 변경 시 기존 Flutter·React 클라이언트 영향도를 확인한다.
- CT 추론 계약과 일반 서비스 계약을 구분한다.

현재 파일:

- `examples/`: 향후 합의된 일반 서비스 계약 예시 영역
- `inference-request.example.json`: Django에서 Gateway로 보내는 추론 요청 예시
- `inference-response.example.json`: Gateway가 반환하는 추론 응답 예시
- `mosec-api.md`: Gateway와 MOSEC 사이의 추론 계약

예약·처방·검사 API JSON은 팀 합의 후 추가한다.
