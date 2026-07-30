# 최소 검증 명령

저장소 루트에서 각 영역을 순서대로 검증합니다.

## Flutter

```powershell
Set-Location mobile
flutter pub get
flutter analyze
flutter test
Set-Location ..
```

## React

```powershell
Set-Location frontend
npm.cmd ci
npm.cmd run build
Set-Location ..
```

## Django

```powershell
Set-Location backend
$env:DJANGO_SETTINGS_MODULE = "config.test_settings"
.\.venv\Scripts\python.exe manage.py makemigrations --check
.\.venv\Scripts\python.exe manage.py test
Set-Location ..
```

## AI

```powershell
Set-Location ai
npm.cmd ci
npm.cmd run typecheck
npm.cmd run build
npm.cmd test
Set-Location ..
```

## Compose 정적 검증

```powershell
$env:POSTGRES_DB = "brainon"
$env:POSTGRES_USER = "brainon"
$env:POSTGRES_PASSWORD = "local-validation-only"
docker compose config
docker compose -f inference\compose.mock.yaml config
docker compose -f inference\compose.yaml config
```
