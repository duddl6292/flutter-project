# BrainOn Backend

환자·예약·처방·검사·알림 기능을 확장할 Django REST API입니다.

## 로컬 준비

저장소 루트에서 PostgreSQL을 먼저 실행합니다.

```powershell
Copy-Item .env.example .env
docker compose --env-file .env up -d postgres
```

백엔드를 실행합니다.

```powershell
Set-Location backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Health endpoint:

```text
GET http://localhost:8000/api/health/
```

테스트:

```powershell
$env:DJANGO_SETTINGS_MODULE = "config.test_settings"
python manage.py test
```
