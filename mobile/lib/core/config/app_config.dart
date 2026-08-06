enum DistributionChannel { direct, play }

abstract final class AppConfig {
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  // 직접 APK와 Google Play 빌드가 같은 코드에서 각 배포 방식에 맞게
  // 업데이트를 처리할 수 있도록 빌드 시 전달한 채널 값을 사용한다.
  static const _distributionChannel = String.fromEnvironment(
    'DISTRIBUTION_CHANNEL',
    defaultValue: 'direct',
  );

  static const updateMetadataUrl = String.fromEnvironment(
    'UPDATE_METADATA_URL',
    defaultValue:
        'https://github.com/duddl6292/flutter-project/releases/latest/download/version.json',
  );

  static DistributionChannel get distributionChannel {
    return _distributionChannel.toLowerCase() == 'play'
        ? DistributionChannel.play
        : DistributionChannel.direct;
  }
}
