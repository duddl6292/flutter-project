# Flutter 알림 영역

통합 담당자가 FCM과 로컬 알림 연결을 관리할 영역이다. 향후 다음 파일을 둘 예정이다.

- `notification_initializer.dart`
- `fcm_service.dart`
- `local_notification_service.dart`
- `notification_permission_service.dart`
- `notification_navigation.dart`

예정 책임:

- Firebase 초기화
- 알림 권한 요청
- FCM 등록 정보 관리
- foreground/background 메시지 수신
- 알림 클릭에 따른 화면 이동
- 복약 로컬 알림 예약

현재 단계에서는 실제 Dart 구현 파일이나 `main.dart` 초기화 코드를 추가하지 않는다.
