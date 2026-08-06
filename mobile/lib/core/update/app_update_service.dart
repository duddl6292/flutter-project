import 'dart:convert';

import 'package:brainon_mobile/core/config/app_config.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:in_app_update/in_app_update.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:url_launcher/url_launcher.dart';

enum UpdateDelivery { directDownload, playImmediate, playFlexible }

class AvailableAppUpdate {
  const AvailableAppUpdate({
    required this.versionName,
    required this.versionCode,
    required this.message,
    required this.isRequired,
    required this.delivery,
    this.apkUrl,
  });

  final String versionName;
  final int versionCode;
  final String message;
  final bool isRequired;
  final UpdateDelivery delivery;
  final Uri? apkUrl;

  factory AvailableAppUpdate.fromDirectJson(
    Map<String, dynamic> json, {
    required int currentVersionCode,
  }) {
    final versionName = json['versionName'] as String?;
    final versionCode = _readInt(json['versionCode']);
    final minimumVersionCode =
        _readInt(json['minimumVersionCode'], fallback: 1) ?? 1;
    final apkUrlValue = json['apkUrl'] as String?;
    final apkUrl = apkUrlValue == null ? null : Uri.tryParse(apkUrlValue);

    if (versionName == null ||
        versionName.isEmpty ||
        versionCode == null ||
        apkUrl == null ||
        !apkUrl.hasScheme) {
      throw const FormatException('업데이트 정보 형식이 올바르지 않습니다.');
    }

    return AvailableAppUpdate(
      versionName: versionName,
      versionCode: versionCode,
      message: json['message'] as String? ?? '업데이트 항목이 있습니다. 업데이트를 진행해 주세요.',
      isRequired:
          json['forceUpdate'] == true ||
          currentVersionCode < minimumVersionCode,
      delivery: UpdateDelivery.directDownload,
      apkUrl: apkUrl,
    );
  }

  bool isNewerThan(int currentVersionCode) {
    return versionCode > currentVersionCode;
  }

  static int? _readInt(Object? value, {int? fallback}) {
    if (value is int) {
      return value;
    }
    if (value is String) {
      return int.tryParse(value) ?? fallback;
    }
    return fallback;
  }
}

class AppUpdateService {
  const AppUpdateService();

  Future<AvailableAppUpdate?> checkForUpdate() async {
    // Play 인앱 업데이트는 Android의 Google Play 설치 앱에서만 동작한다.
    if (kIsWeb || defaultTargetPlatform != TargetPlatform.android) {
      return null;
    }

    return switch (AppConfig.distributionChannel) {
      DistributionChannel.direct => _checkDirectUpdate(),
      DistributionChannel.play => _checkPlayUpdate(),
    };
  }

  Future<AvailableAppUpdate?> _checkDirectUpdate() async {
    final packageInfo = await PackageInfo.fromPlatform();
    final currentVersionCode = int.tryParse(packageInfo.buildNumber);
    if (currentVersionCode == null) {
      throw const FormatException('현재 앱 버전을 확인할 수 없습니다.');
    }

    final response = await http
        .get(
          Uri.parse(AppConfig.updateMetadataUrl),
          headers: const {'Accept': 'application/json'},
        )
        .timeout(const Duration(seconds: 10));

    if (response.statusCode != 200) {
      throw StateError('업데이트 정보를 불러오지 못했습니다.');
    }

    final json = jsonDecode(utf8.decode(response.bodyBytes));
    if (json is! Map<String, dynamic>) {
      throw const FormatException('업데이트 정보 형식이 올바르지 않습니다.');
    }

    final update = AvailableAppUpdate.fromDirectJson(
      json,
      currentVersionCode: currentVersionCode,
    );
    return update.isNewerThan(currentVersionCode) ? update : null;
  }

  Future<AvailableAppUpdate?> _checkPlayUpdate() async {
    final updateInfo = await InAppUpdate.checkForUpdate();
    if (updateInfo.updateAvailability != UpdateAvailability.updateAvailable) {
      return null;
    }

    final delivery = updateInfo.immediateUpdateAllowed
        ? UpdateDelivery.playImmediate
        : updateInfo.flexibleUpdateAllowed
        ? UpdateDelivery.playFlexible
        : null;
    if (delivery == null) {
      return null;
    }

    final packageInfo = await PackageInfo.fromPlatform();
    final currentVersionCode = int.tryParse(packageInfo.buildNumber) ?? 0;

    return AvailableAppUpdate(
      versionName: 'Google Play 새 버전',
      versionCode: updateInfo.availableVersionCode ?? currentVersionCode + 1,
      message: '업데이트 항목이 있습니다. 업데이트를 진행해 주세요.',
      isRequired: false,
      delivery: delivery,
    );
  }

  Future<void> startUpdate(AvailableAppUpdate update) async {
    switch (update.delivery) {
      case UpdateDelivery.directDownload:
        final apkUrl = update.apkUrl;
        if (apkUrl == null ||
            !await launchUrl(apkUrl, mode: LaunchMode.externalApplication)) {
          throw StateError('APK 다운로드 페이지를 열 수 없습니다.');
        }
      case UpdateDelivery.playImmediate:
        await InAppUpdate.performImmediateUpdate();
      case UpdateDelivery.playFlexible:
        await InAppUpdate.startFlexibleUpdate();
        await InAppUpdate.completeFlexibleUpdate();
    }
  }
}
