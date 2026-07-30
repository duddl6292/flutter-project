# 공유 파일과 충돌 위험

다음 파일은 수정 전에 담당자 간 변경 범위를 공유한다.

## 공통

```text
README.md
.env.example
.gitignore
compose.yaml
.github/workflows/
contracts/
```

## Flutter·FCM

```text
mobile/lib/main.dart
mobile/lib/app/
mobile/lib/core/api/
mobile/lib/core/auth/
mobile/lib/core/notifications/
mobile/pubspec.yaml
mobile/pubspec.lock
mobile/lib/firebase_options.dart
mobile/android/
mobile/ios/
```

## React

```text
frontend/package.json
frontend/package-lock.json
frontend/vite.config.ts
frontend/src/main.tsx
frontend/src/app/
frontend/src/core/
```

## Django·AI·배포

```text
backend/config/settings.py
backend/config/urls.py
backend/requirements.txt
backend/apps/accounts/
ai/package.json
ai/package-lock.json
ai/.env.example
```

API 계약과 인증 동작은 Django·React·Flutter 담당자가 합의한 뒤 변경한다. Secret과 실제 의료 데이터는 공유 파일에 기록하지 않는다.
