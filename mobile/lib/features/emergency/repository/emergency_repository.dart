import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/shared/models/emergency_ai_request.dart';
import 'package:brainon_mobile/shared/models/emergency_ai_response.dart';
import 'package:dio/dio.dart';

abstract interface class EmergencyRepository {
  Future<EmergencyAiResponse> askAiSymptom({
    required EmergencyAiRequest request,
    String? accessToken,
  });
}

class HttpEmergencyRepository implements EmergencyRepository {
  const HttpEmergencyRepository(this._dio);

  final Dio _dio;

  @override
  Future<EmergencyAiResponse> askAiSymptom({
    required EmergencyAiRequest request,
    String? accessToken,
  }) async {
    try {
      return await runApiRequest(() async {
        final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/chatbot/messages/',
      data: {
        'message':
            '응급 증상 안내 요청입니다. 사용자가 입력한 증상: '
            '${request.symptomText}\n'
            '즉시 119가 필요한 위험 신호인지 안전을 최우선으로 짧고 명확하게 안내해 주세요. '
            '진단을 확정하지 말고 응급 상황이면 바로 119 또는 응급실 이용을 권고해 주세요.',
        'idempotency_key': 'emergency-${DateTime.now().microsecondsSinceEpoch}',
      },
    );
    final data = Map<String, dynamic>.from(response.data?['data'] as Map);
    final assistant = Map<String, dynamic>.from(
      data['assistant_message'] as Map,
    );
        return EmergencyAiResponse(
          riskLevel: 'AI_GUIDANCE',
          message: assistant['content'] as String? ?? '응급 안내 결과를 확인할 수 없습니다.',
          recommendedAction: 'FOLLOW_GUIDANCE',
        );
      });
    } on ApiException catch (error) {
      throw EmergencyApiException(
        message: error.message,
        statusCode: error.statusCode,
      );
    }
  }

  void dispose() {}
}

class EmergencyApiException implements Exception {
  const EmergencyApiException({required this.message, this.statusCode});

  final String message;
  final int? statusCode;
}
