import 'package:brainon_mobile/core/update/app_update_service.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('현재 versionCode보다 높은 직접 배포 버전을 업데이트로 판단한다', () {
    final update = AvailableAppUpdate.fromDirectJson({
      'versionName': '1.0.2',
      'versionCode': 3,
      'minimumVersionCode': 1,
      'forceUpdate': false,
      'message': '업데이트 항목이 있습니다. 업데이트를 진행해 주세요.',
      'apkUrl':
          'https://github.com/duddl6292/flutter-project/releases/latest/download/brainon.apk',
    }, currentVersionCode: 2);

    expect(update.isNewerThan(2), isTrue);
    expect(update.isRequired, isFalse);
    expect(update.delivery, UpdateDelivery.directDownload);
  });

  test('minimumVersionCode보다 낮은 앱은 필수 업데이트로 판단한다', () {
    final update = AvailableAppUpdate.fromDirectJson({
      'versionName': '2.0.0',
      'versionCode': 5,
      'minimumVersionCode': 3,
      'forceUpdate': false,
      'apkUrl':
          'https://github.com/duddl6292/flutter-project/releases/latest/download/brainon.apk',
    }, currentVersionCode: 2);

    expect(update.isRequired, isTrue);
  });
}
