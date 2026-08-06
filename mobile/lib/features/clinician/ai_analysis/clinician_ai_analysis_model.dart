enum ClinicianAiAnalysisStatus { queued, processing, completed, failed }

class ClinicianAiAnalysis {
  const ClinicianAiAnalysis({
    required this.id,
    required this.patientName,
    required this.patientNumber,
    required this.sex,
    required this.age,
    required this.analysisType,
    required this.description,
    required this.requestedAt,
    required this.status,
    required this.resultSummary,
    required this.result,
  });

  final String id, patientName, patientNumber, sex, analysisType, description, resultSummary;
  final int? age;
  final DateTime? requestedAt;
  final ClinicianAiAnalysisStatus status;
  final Map<String, dynamic> result;

  factory ClinicianAiAnalysis.fromJson(Map<String, dynamic> json) {
    final raw = json['status']?.toString().toUpperCase();
    final patient = Map<String, dynamic>.from(json['patient'] as Map? ?? const {});
    final result = Map<String, dynamic>.from(json['result'] as Map? ?? const {});
    final detected = result['lesion_detected'] as bool?;
    return ClinicianAiAnalysis(
      id: json['case_id']?.toString() ?? '',
      patientName: patient['name']?.toString() ?? '환자 정보 없음',
      patientNumber: patient['medical_record_number']?.toString() ?? '',
      sex: patient['sex']?.toString() ?? '',
      age: int.tryParse(patient['age']?.toString() ?? ''),
      analysisType: json['study_type_label']?.toString() ?? 'CT 분석',
      description: json['description']?.toString() ?? '',
      requestedAt: DateTime.tryParse(json['created_at']?.toString() ?? '')?.toLocal(),
      status: switch (raw) {
        'PROCESSING' => ClinicianAiAnalysisStatus.processing,
        'COMPLETED' => ClinicianAiAnalysisStatus.completed,
        'FAILED' => ClinicianAiAnalysisStatus.failed,
        _ => ClinicianAiAnalysisStatus.queued,
      },
      resultSummary: detected == null ? '' : detected ? '병변 의심 영역이 탐지되었습니다.' : '탐지된 병변 영역이 없습니다.',
      result: result,
    );
  }
}
