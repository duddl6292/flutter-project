import 'package:dio/dio.dart';

class ApiException implements Exception {
  const ApiException({
    required this.code,
    required this.message,
    this.details,
    this.statusCode,
  });

  final String code;
  final String message;
  final Object? details;
  final int? statusCode;

  factory ApiException.fromDioException(DioException exception) {
    final data = exception.response?.data;
    if (data is Map<String, dynamic>) {
      final error = data['error'];
      if (error is Map<String, dynamic>) {
        return ApiException(
          code: error['code']?.toString() ?? 'API_ERROR',
          message: error['message']?.toString() ?? '요청을 처리하지 못했습니다.',
          details: error['details'],
          statusCode: exception.response?.statusCode,
        );
      }
    }
    return ApiException(
      code: 'NETWORK_ERROR',
      message: '서버에 연결할 수 없습니다.',
      statusCode: exception.response?.statusCode,
    );
  }

  @override
  String toString() => message;
}
