# BrainOn Backend

Django REST API입니다. 현재 사용자 역할, 환자·의료진 Profile, JWT 인증, 공통 오류 및 페이지네이션 기반이 구현되어 있습니다. 예약·처방·검사 업무 모델은 아직 예정 단계입니다.

## 실행

```powershell
Set-Location backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 현재 Endpoint

```text
GET  /api/health/
POST /api/v1/auth/login/
POST /api/v1/auth/refresh/
POST /api/v1/auth/logout/
GET  /api/v1/auth/me/
```

모바일은 Refresh Token을 JSON으로 받고 보안 저장소에 보관합니다. 웹은 JavaScript가 읽을 수 없는 HttpOnly Cookie를 사용합니다. 운영 환경에서는 HTTPS와 `JWT_COOKIE_SECURE=true`가 필수이며, 교차 사이트 배포 시 SameSite·CORS·CSRF 정책을 함께 검토해야 합니다.

## 테스트

```powershell
$env:DJANGO_SETTINGS_MODULE = "config.test_settings"
python manage.py makemigrations --check
python manage.py test
```

신규 DB는 생성된 초기 migration으로 바로 구성할 수 있습니다. 기존 `auth_user` 데이터가 있는 DB는 삭제하거나 자동 변환하지 말고 별도의 데이터 이관 계획을 수립해야 합니다.
