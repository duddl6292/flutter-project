import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/core/api/auth_interceptor.dart';
import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/core/config/app_config.dart';
import 'package:brainon_mobile/core/storage/token_storage.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final tokenStorageProvider = Provider<TokenStorage>((ref) => TokenStorage());

final apiClientProvider = Provider<Dio>((ref) {
  final options = BaseOptions(
    baseUrl: AppConfig.apiBaseUrl,
    connectTimeout: const Duration(seconds: 15),
    receiveTimeout: const Duration(seconds: 30),
    headers: {'Accept': 'application/json'},
  );
  final dio = Dio(options);
  final refreshDio = Dio(options);
  dio.interceptors.add(
    AuthInterceptor(dio, refreshDio, ref.watch(tokenStorageProvider), () async {
      ref.read(authProvider.notifier).signedOut();
    }),
  );
  return dio;
});

Future<T> runApiRequest<T>(Future<T> Function() request) async {
  try {
    return await request();
  } on DioException catch (error) {
    throw ApiException.fromDioException(error);
  }
}
