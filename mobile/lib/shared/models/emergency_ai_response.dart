class EmergencyAiResponse {
  const EmergencyAiResponse({
    required this.riskLevel,
    required this.message,
    required this.recommendedAction,
  });

  final String riskLevel;
  final String message;
  final String recommendedAction;

  factory EmergencyAiResponse.fromJson(Map<String, dynamic> json) {
    return EmergencyAiResponse(
      riskLevel: json['risk_level'] as String? ?? 'UNKNOWN',
      message: json['message'] as String? ?? '응급 안내 결과를 확인할 수 없습니다.',
      recommendedAction: json['recommended_action'] as String? ?? 'NONE',
    );
  }
}
