class PatientTestResult {
  const PatientTestResult({
    required this.id,
    required this.testType,
    required this.title,
    required this.performedAt,
    required this.status,
    required this.statusLabel,
    required this.summary,
    required this.clinicianComment,
    required this.hospitalName,
    required this.releasedAt,
    required this.hasResultFile,
  });

  final String id;
  final String testType;
  final String title;
  final DateTime performedAt;
  final String status;
  final String statusLabel;
  final String summary;
  final String clinicianComment;
  final String hospitalName;
  final DateTime? releasedAt;
  final bool hasResultFile;

  factory PatientTestResult.fromJson(Map<String, dynamic> json) {
    return PatientTestResult(
      id: json['test_result_id']?.toString() ?? '',
      testType: json['test_type']?.toString() ?? '',
      title: json['title']?.toString() ?? '',
      performedAt: DateTime.parse(json['performed_at'].toString()).toLocal(),
      status: json['status']?.toString() ?? '',
      statusLabel: json['status_label']?.toString() ?? '',
      summary: json['summary']?.toString() ?? '',
      clinicianComment: json['clinician_comment']?.toString() ?? '',
      hospitalName: json['hospital_name']?.toString() ?? '',
      releasedAt: DateTime.tryParse(json['released_at']?.toString() ?? '')
          ?.toLocal(),
      hasResultFile: json['has_result_file'] == true,
    );
  }
}
