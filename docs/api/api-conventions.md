# REST API 공통 규칙

- 일반 서비스 endpoint는 `/api/v1/` prefix를 사용한다.
- 날짜와 시간은 timezone을 포함한 ISO 8601 문자열을 사용한다.
- 상태값은 대문자 Enum으로 표현한다.
- GET은 조회, POST는 생성·명령, PATCH는 부분 수정에 사용한다.
- 의료 데이터는 실제 삭제보다 취소·중단·무효 등 상태 변경을 우선한다.
- 목록은 page number pagination을 사용한다.
- 기본 `page_size`는 20이고 `page_size` query parameter를 허용하며 최대 100이다.
- 파일 업로드는 `multipart/form-data`를 사용한다.
- Mock 데이터는 공식 계약이 아니다.

공통 오류 형식:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자에게 표시할 메시지",
    "details": {}
  }
}
```

서버 stack trace와 내부 예외 세부 정보는 응답에 포함하지 않는다.

API 계약은 Django 담당자가 초안을 작성하고 React·Flutter 담당자와 합의한 뒤 `contracts/`에 반영한다. 변경 시 기존 클라이언트와 CT 추론 계약에 미치는 영향을 확인한다.
