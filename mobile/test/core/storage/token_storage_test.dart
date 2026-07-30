import 'package:brainon_mobile/core/storage/token_storage.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    FlutterSecureStorage.setMockInitialValues({});
  });

  test('stores, reads, and clears tokens', () async {
    final storage = TokenStorage();

    await storage.writeTokens(
      accessToken: 'access-token',
      refreshToken: 'refresh-token',
    );
    expect(await storage.readAccessToken(), 'access-token');
    expect(await storage.readRefreshToken(), 'refresh-token');

    await storage.clear();
    expect(await storage.readAccessToken(), isNull);
    expect(await storage.readRefreshToken(), isNull);
  });
}
