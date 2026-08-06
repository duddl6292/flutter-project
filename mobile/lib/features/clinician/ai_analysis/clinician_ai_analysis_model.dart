enum ClinicianAiAnalysisStatus { queued, processing, completed, failed }

class ClinicianAiAnalysis {
  const ClinicianAiAnalysis({
    required this.id,
    required this.patientName,
    required this.analysisType,
    required this.requestedAt,
    required this.status,
    required this.resultSummary,
  });
  final String id, patientName, analysisType, resultSummary;
  final DateTime? requestedAt;
  final ClinicianAiAnalysisStatus status;
  factory ClinicianAiAnalysis.fromJson(Map<String, dynamic> json) {
    final raw = json['status']?.toString();
    return ClinicianAiAnalysis(
      id: json['id']?.toString() ?? '',
      patientName: json['patient_name']?.toString() ?? '',
      analysisType: json['analysis_type']?.toString() ?? '',
      requestedAt: DateTime.tryParse(json['requested_at']?.toString() ?? ''),
      status: switch (raw) {
        'processing' => ClinicianAiAnalysisStatus.processing,
        'completed' => ClinicianAiAnalysisStatus.completed,
        'failed' => ClinicianAiAnalysisStatus.failed,
        _ => ClinicianAiAnalysisStatus.queued,
      },
      resultSummary: json['result_summary']?.toString() ?? '',
    );
  }
}
