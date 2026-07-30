# BrainOn 아키텍처 결정사항

## 사용자 및 역할

- Django Custom User가 `AbstractUser`를 상속한다.
- 주요 역할은 `PATIENT`, `CLINICIAN`, `ADMIN`이다.
- 한 사용자는 하나의 주요 역할만 가진다.
- `PatientProfile`과 `ClinicianProfile`은 User와 OneToOne 관계다.
- 로그인 화면의 역할 선택은 권한을 바꾸지 않는다.
- Django가 `expected_role`과 실제 계정 역할을 비교한다.
- Profile은 signal로 자동 생성하지 않고 명시적인 서비스/호출 흐름에서 생성한다. 역할 오류를 호출자가 처리하고 예상하지 못한 자동 레코드 생성을 피하기 위한 결정이다.

## JWT

- `djangorestframework-simplejwt`를 사용한다.
- Access Token은 15분, Refresh Token은 7일이다.
- Refresh Token 회전과 회전 후 blacklist를 활성화한다.
- 로그아웃 시 Refresh Token을 blacklist 처리한다.
- `UPDATE_LAST_LOGIN=False`다. 로그인마다 DB write를 만들지 않고 감사 로그 정책과 분리하기 위해서다.
- 모바일은 Access/Refresh Token을 JSON으로 받고 secure storage에 저장한다.
- 웹은 Access Token만 JSON으로 받고 Refresh Token은 HttpOnly Cookie로 받는다.
- 로컬 웹 Cookie는 `SameSite=Lax`, 허용 Origin과 credential CORS를 사용한다.
- 교차 사이트 배포에서 `SameSite=None`이 필요하면 운영 전 CSRF Token 또는 동등한 Origin 검증을 추가한다. 현재 placeholder 웹은 교차 사이트 배포를 지원한다고 간주하지 않는다.

## Flutter

- 라우팅: `go_router`
- 상태 관리: `flutter_riverpod`
- HTTP: `dio`
- 토큰 저장: `flutter_secure_storage`
- 사용자와 역할은 `/auth/me/` 결과를 신뢰한다.

## React

- 라우팅: `react-router-dom`
- 서버 상태: `@tanstack/react-query`
- 전역 클라이언트 상태: `zustand`
- HTTP: 공통 fetch wrapper
- Refresh Token: HttpOnly Cookie
- Access Token과 인증 사용자: 메모리 상태

## API

- prefix: `/api/v1/`
- 날짜와 시간: ISO 8601
- 상태값: 대문자 Enum
- 부분 수정: PATCH
- 목록: 페이지네이션
- 파일: `multipart/form-data`
- 오류: 공통 `error` envelope

## 포트

| 서비스 | 포트 |
| --- | ---: |
| React | 5173 |
| Django | 8000 |
| MOSEC | 8001 |
| FastAPI Gateway | 8100 |
| Genkit AI HTTP | 8200 |
| MCP Server | 8201 |
| PostgreSQL | 5432 |

## 의료진 권한

- 담당 환자 또는 협진 참여 환자만 접근한다.
- 확정 의료 기록은 직접 수정·삭제하지 않는다.
- 정정 기록 또는 새 버전을 사용한다.
- 의료진은 사용자 역할과 감사 로그를 수정할 수 없다.
