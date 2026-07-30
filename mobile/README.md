# BrainOn Mobile

환자·의료진이 함께 사용하는 Flutter 앱입니다. 현재 기존 BrainOn 홈 화면과 다음 공통 기반이 구현되어 있습니다.

- `go_router`: 앱 라우팅
- `flutter_riverpod`: 인증·공통 상태
- `dio`: API 요청과 단일 Refresh 재시도
- `flutter_secure_storage`: Access·Refresh Token 보안 저장
- 기존 Firebase 및 알림 패키지

실제 로그인 화면과 의료 업무 화면은 후속 구현 범위입니다. 역할은 사용자가 고른 화면이 아니라 Django `/api/v1/auth/me/` 응답을 기준으로 판단합니다.

```powershell
Set-Location mobile
flutter pub get
flutter analyze
flutter test
flutter run
```

API 주소는 빌드 시 `--dart-define=API_BASE_URL=http://...`로 지정할 수 있습니다. Android 에뮬레이터에서 호스트 Django를 호출할 때에는 일반적으로 `10.0.2.2` 주소가 필요합니다.
