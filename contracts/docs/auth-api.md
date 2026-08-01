# 인증 API

| Method | Endpoint | 기능 |
|---|---|---|
| POST | `/api/v1/auth/login` | 로그인 |
| POST | `/api/v1/auth/token/refresh` | Access Token 갱신 |
| POST | `/api/v1/auth/logout` | Refresh Token 폐기 |
| POST | `/api/v1/auth/password/reset` | 비밀번호 재설정 요청 |
| GET | `/api/v1/users/me` | 현재 사용자와 역할 조회 |

로그인 성공 시 `access_token`, `refresh_token`, `expires_in`, `user`를 반환합니다.
