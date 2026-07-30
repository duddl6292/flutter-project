# 로컬 개발 실행

Windows 11과 PowerShell 기준이다.

## PostgreSQL

```powershell
Set-Location C:\flutter_project\brainon
Copy-Item .env.example .env
docker compose --env-file .env up -d postgres
```

## Django

```powershell
Set-Location backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py runserver 8000
```

## React

```powershell
Set-Location frontend
npm.cmd ci
npm.cmd run dev
```

## Flutter

```powershell
Set-Location mobile
flutter pub get
flutter run
```

AI 서비스는 패키지와 포트 결정 전이므로 아직 실행 명령을 제공하지 않는다.
