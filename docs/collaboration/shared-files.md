# 공유 파일과 충돌 위험

아래 파일은 여러 담당자가 동시에 수정하면 충돌 위험이 높다. 수정 전에 팀 채널에 목적과 예상 변경 범위를 공유한다.

## 루트 공통 파일

```text
README.md
.env.example
compose.yaml
.gitignore
```

## Flutter 공통 파일

```text
mobile/pubspec.yaml
mobile/pubspec.lock
mobile/lib/main.dart
mobile/lib/app/app.dart
mobile/lib/app/app_theme.dart
mobile/lib/firebase_options.dart
mobile/android/
mobile/ios/
```

다음 파일은 FCM 담당자가 관리한다.

```text
mobile/lib/main.dart
mobile/pubspec.yaml
mobile/pubspec.lock
mobile/lib/firebase_options.dart
mobile/android/app/google-services.json
mobile/android/app/build.gradle.kts
mobile/android/settings.gradle.kts
```

Flutter UI 담당자가 위 파일을 수정해야 한다면 먼저 통합 담당자와 협의한다.

## React 공통 파일

```text
frontend/package.json
frontend/package-lock.json
frontend/vite.config.ts
frontend/src/main.tsx
frontend/src/index.css
frontend/.env.example
```

## Django 공통 파일

```text
backend/config/settings.py
backend/config/urls.py
backend/requirements.txt
backend/manage.py
```

## 계약 파일

```text
contracts/
```

API 요청·응답 형식은 한 담당자가 임의로 수정하지 않는다. Flutter, React, Django 담당자가 합의한 뒤 `contracts/`를 변경한다.
