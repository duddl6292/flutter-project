import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('maps the backend common error response', () {
    final request = RequestOptions(path: '/api/v1/test/');
    final exception = DioException(
      requestOptions: request,
      response: Response<dynamic>(
        requestOptions: request,
        statusCode: 400,
        data: {
          'error': {
            'code': 'VALIDATION_ERROR',
            'message': '요청 값을 확인해 주세요.',
            'details': {
              'field': ['필수 항목입니다.'],
            },
          },
        },
      ),
    );

    final apiException = ApiException.fromDioException(exception);

    expect(apiException.code, 'VALIDATION_ERROR');
    expect(apiException.statusCode, 400);
  });
}
