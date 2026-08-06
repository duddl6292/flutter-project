import 'dart:async';

import 'package:brainon_mobile/core/storage/token_storage.dart';
import 'package:dio/dio.dart';

class AuthInterceptor extends Interceptor {
  AuthInterceptor(
    this._dio,
    this._refreshDio,
    this._tokenStorage,
    this._onSignedOut,
  );

  static const _retriedKey = 'brainon_auth_retried';

  final Dio _dio;
  final Dio _refreshDio;
  final TokenStorage _tokenStorage;
  final Future<void> Function() _onSignedOut;
  Future<String>? _refreshInFlight;

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final accessToken = await _tokenStorage.readAccessToken();
    if (accessToken != null && accessToken.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    final request = err.requestOptions;
    final shouldRefresh =
        err.response?.statusCode == 401 &&
        request.extra[_retriedKey] != true &&
        !request.path.endsWith('/api/v1/auth/token/refresh/');
    if (!shouldRefresh) {
      handler.next(err);
      return;
    }

    try {
      final accessToken = await _refreshOnce();
      request.extra[_retriedKey] = true;
      request.headers['Authorization'] = 'Bearer $accessToken';
      handler.resolve(await _dio.fetch<dynamic>(request));
    } on Object {
      await _tokenStorage.clear();
      await _onSignedOut();
      handler.next(err);
    }
  }

  Future<String> _refreshOnce() {
    final inFlight = _refreshInFlight;
    if (inFlight != null) {
      return inFlight;
    }
    final refresh = _refreshAccessToken();
    _refreshInFlight = refresh;
    return refresh.whenComplete(() {
      if (identical(_refreshInFlight, refresh)) {
        _refreshInFlight = null;
      }
    });
  }

  Future<String> _refreshAccessToken() async {
    final refreshToken = await _tokenStorage.readRefreshToken();
    if (refreshToken == null || refreshToken.isEmpty) {
      throw StateError('Refresh Token이 없습니다.');
    }
    final response = await _refreshDio.post<Map<String, dynamic>>(
      '/api/v1/auth/token/refresh/',
      data: {'refresh': refreshToken},
    );
    final data = response.data?['data'] as Map<String, dynamic>?;
    final accessToken = data?['access'] as String?;
    final rotatedRefreshToken = data?['refresh'] as String?;
    if (accessToken == null || accessToken.isEmpty) {
      throw StateError('Access Token 갱신 응답이 올바르지 않습니다.');
    }
    if (rotatedRefreshToken != null && rotatedRefreshToken.isNotEmpty) {
      await _tokenStorage.writeTokens(
        accessToken: accessToken,
        refreshToken: rotatedRefreshToken,
      );
    } else {
      await _tokenStorage.writeAccessToken(accessToken);
    }
    return accessToken;
  }
}
