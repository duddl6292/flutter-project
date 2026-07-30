import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/core/auth/auth_state.dart';
import 'package:brainon_mobile/core/storage/token_storage.dart';
import 'package:dio/dio.dart';

class AuthRepository {
  AuthRepository(this._dio, this._tokenStorage);

  final Dio _dio;
  final TokenStorage _tokenStorage;

  Future<AuthUser> login({
    required String username,
    required String password,
    required String expectedRole,
  }) {
    return runApiRequest(() async {
      final response = await _dio.post<Map<String, dynamic>>(
        '/api/v1/auth/login/',
        data: {
          'username': username,
          'password': password,
          'expected_role': expectedRole,
          'client_type': 'MOBILE',
        },
      );
      final data = response.data!;
      await _tokenStorage.writeTokens(
        accessToken: data['access'] as String,
        refreshToken: data['refresh'] as String,
      );
      return AuthUser.fromJson(data['user'] as Map<String, dynamic>);
    });
  }

  Future<AuthUser> me() {
    return runApiRequest(() async {
      final response = await _dio.get<Map<String, dynamic>>('/api/v1/auth/me/');
      return AuthUser.fromJson(response.data!);
    });
  }

  Future<void> logout() async {
    final refreshToken = await _tokenStorage.readRefreshToken();
    try {
      if (refreshToken != null) {
        await _dio.post<void>(
          '/api/v1/auth/logout/',
          data: {'refresh': refreshToken},
        );
      }
    } finally {
      await _tokenStorage.clear();
    }
  }
}
