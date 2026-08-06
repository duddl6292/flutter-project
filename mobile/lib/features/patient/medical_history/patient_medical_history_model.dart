class PatientMedicalHistory {
  const PatientMedicalHistory({
    required this.encounterId,
    required this.encounterNumber,
    required this.encounterType,
    required this.encounterTypeLabel,
    required this.status,
    required this.statusLabel,
    required this.hospitalName,
    required this.departmentName,
    required this.clinicianName,
    required this.eventAt,
    this.arrivedAt,
    this.startedAt,
    this.completedAt,
  });

  final String encounterId;
  final String encounterNumber;
  final String encounterType;
  final String encounterTypeLabel;
  final String status;
  final String statusLabel;
  final String hospitalName;
  final String departmentName;
  final String clinicianName;
  final DateTime eventAt;
  final DateTime? arrivedAt;
  final DateTime? startedAt;
  final DateTime? completedAt;

  factory PatientMedicalHistory.fromJson(Map<String, dynamic> json) {
    return PatientMedicalHistory(
      encounterId: json['encounter_id']?.toString() ?? '',
      encounterNumber: json['encounter_number']?.toString() ?? '',
      encounterType: json['encounter_type']?.toString() ?? '',
      encounterTypeLabel: json['encounter_type_label']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      statusLabel: json['status_label']?.toString() ?? '',
      hospitalName: json['hospital_name']?.toString() ?? '',
      departmentName: json['department_name']?.toString() ?? '',
      clinicianName: json['clinician_name']?.toString() ?? '',
      eventAt: DateTime.parse(json['event_at'].toString()).toLocal(),
      arrivedAt: _dateTime(json['arrived_at']),
      startedAt: _dateTime(json['started_at']),
      completedAt: _dateTime(json['completed_at']),
    );
  }

  static DateTime? _dateTime(Object? value) {
    return DateTime.tryParse(value?.toString() ?? '')?.toLocal();
  }
}
