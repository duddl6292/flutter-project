class ClinicianStatistics {
  const ClinicianStatistics({
    required this.patientCount,
    required this.waitingCount,
    required this.consultationCount,
    required this.testResultCount,
  });
  final int patientCount, waitingCount, consultationCount, testResultCount;
  factory ClinicianStatistics.fromJson(
    Map<String, dynamic> json,
  ) => ClinicianStatistics(
    patientCount: int.tryParse(json['patient_count']?.toString() ?? '') ?? 0,
    waitingCount: int.tryParse(json['waiting_count']?.toString() ?? '') ?? 0,
    consultationCount:
        int.tryParse(json['consultation_count']?.toString() ?? '') ?? 0,
    testResultCount:
        int.tryParse(json['test_result_count']?.toString() ?? '') ?? 0,
  );
}
