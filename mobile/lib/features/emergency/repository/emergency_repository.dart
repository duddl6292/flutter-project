import 'dart:convert';

import 'package:brainon_mobile/shared/models/emergency_ai_request.dart';
import 'package:brainon_mobile/shared/models/emergency_ai_response.dart';
import 'package:http/http.dart' as http;

abstract interface class EmergencyRepository {
  Future<EmergencyAiResponse> askAiSymptom({
    required EmergencyAiRequest request,
    String? accessToken,
  });
}

class HttpEmergencyRepository implements EmergencyRepository {
  HttpEmergencyRepository({required this.baseUrl, http.Client? client})
    : _client = client ?? http.Client();

  final String baseUrl;
  final http.Client _client;

  @override
  Future<EmergencyAiResponse> askAiSymptom({
    required EmergencyAiRequest request,
    String? accessToken,
  }) async {
    final uri = Uri.parse('$baseUrl/api/emergency/ai-guide');

    try {
      final response = await _client
          .post(
            uri,
            headers: {
              'Content-Type': 'application/json; charset=UTF-8',
              'Accept': 'application/json',
              if (accessToken != null && accessToken.isNotEmpty)
                'Authorization': 'Bearer $accessToken',
            },
            body: jsonEncode(request.toJson()),
          )
          .timeout(const Duration(seconds: 15));

      final decodedBody = _decodeBody(response.body);

      if (response.statusCode >= 200 && response.statusCode < 300) {
        return EmergencyAiResponse.fromJson(decodedBody);
      }

      final serverMessage =
          decodedBody['message'] as String? ?? decodedBody['detail'] as String?;

      throw EmergencyApiException(
        message: serverMessage ?? '서버 요청에 실패했습니다.',
        statusCode: response.statusCode,
      );
    } on EmergencyApiException {
      rethrow;
    } on FormatException {
      throw const EmergencyApiException(message: '서버 응답 형식이 올바르지 않습니다.');
    } catch (_) {
      throw const EmergencyApiException(message: '서버에 연결할 수 없습니다.');
    }
  }

  Map<String, dynamic> _decodeBody(String body) {
    if (body.trim().isEmpty) {
      return <String, dynamic>{};
    }

    final decoded = jsonDecode(body);

    if (decoded is! Map<String, dynamic>) {
      throw const FormatException('JSON object expected.');
    }

    return decoded;
  }

  void dispose() {
    _client.close();
  }
}

class EmergencyApiException implements Exception {
  const EmergencyApiException({required this.message, this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}
