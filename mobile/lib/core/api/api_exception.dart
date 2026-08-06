import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

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
    if (kDebugMode) {
      debugPrint(
        '[API] ${exception.requestOptions.method} '
        '${exception.requestOptions.uri.path} '
        'type=${exception.type.name} '
        'status=${exception.response?.statusCode ?? '-'}',
      );
    }

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

    final response = exception.response;
    if (response != null) {
      final responseMessage = data is Map<String, dynamic>
          ? data['message'] ?? data['detail']
          : null;
      return ApiException(
        code: 'HTTP_ERROR',
        message: responseMessage is String && responseMessage.isNotEmpty
            ? responseMessage
            : '요청을 처리하지 못했습니다.',
        details: data,
        statusCode: response.statusCode,
      );
    }

    return switch (exception.type) {
      DioExceptionType.connectionTimeout ||
      DioExceptionType.sendTimeout ||
      DioExceptionType.receiveTimeout => const ApiException(
        code: 'TIMEOUT',
        message: '서버 응답 시간이 초과되었습니다.',
      ),
      DioExceptionType.cancel => const ApiException(
        code: 'REQUEST_CANCELLED',
        message: '요청이 취소되었습니다.',
      ),
      DioExceptionType.badCertificate => const ApiException(
        code: 'CERTIFICATE_ERROR',
        message: '서버 인증서를 확인할 수 없습니다.',
      ),
      _ => const ApiException(
        code: 'NETWORK_ERROR',
        message: '서버에 연결할 수 없습니다.',
      ),
    };
  }

  @override
  String toString() => message;
}
