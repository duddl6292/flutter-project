class ClinicianPatientDetail {
  const ClinicianPatientDetail({
    required this.id,
    required this.name,
    required this.medicalRecordNumber,
    required this.birthDate,
    required this.sex,
    required this.phone,
    required this.emergencyContact,
    required this.address,
    required this.status,
  });

  final String id;
  final String name;
  final String medicalRecordNumber;
  final DateTime? birthDate;
  final String sex;
  final String phone;
  final String emergencyContact;
  final String address;
  final String status;

  int? get age {
    final birth = birthDate;
    if (birth == null) return null;
    final today = DateTime.now();
    var value = today.year - birth.year;
    if (today.month < birth.month ||
        (today.month == birth.month && today.day < birth.day)) {
      value--;
    }
    return value;
  }

  factory ClinicianPatientDetail.fromJson(Map<String, dynamic> json) {
    return ClinicianPatientDetail(
      id: json['patient_id']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      medicalRecordNumber: json['medical_record_number']?.toString() ?? '',
      birthDate: DateTime.tryParse(json['birth_date']?.toString() ?? ''),
      sex: json['sex']?.toString() ?? '',
      phone: json['phone']?.toString() ?? '',
      emergencyContact: json['emergency_contact']?.toString() ?? '',
      address: json['address']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
    );
  }
}

enum PatientResourceType {
  examinations,
  medicalHistory,
  appointments,
  prescriptions,
}

class PatientResourceItem {
  const PatientResourceItem({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.status,
    this.examination,
  });

  final String id;
  final String title;
  final String subtitle;
  final String status;
  final ClinicianExamination? examination;
}

class ClinicianExamination {
  const ClinicianExamination({
    required this.id,
    required this.patientId,
    required this.testName,
    required this.performedAt,
    required this.status,
    required this.statusLabel,
    required this.interpretation,
    required this.interpretationLabel,
    required this.abnormalCount,
    required this.observations,
    required this.report,
  });

  final String id;
  final String patientId;
  final String testName;
  final DateTime? performedAt;
  final String status;
  final String statusLabel;
  final String interpretation;
  final String interpretationLabel;
  final int abnormalCount;
  final List<ExaminationObservation> observations;
  final ExaminationReport? report;

  factory ClinicianExamination.fromJson(Map<String, dynamic> json) {
    final report = json['report'];
    return ClinicianExamination(
      id: json['examination_id']?.toString() ?? '',
      patientId: json['patient_id']?.toString() ?? '',
      testName: json['test_name']?.toString() ?? '',
      performedAt: DateTime.tryParse(json['performed_at']?.toString() ?? ''),
      status: json['status']?.toString() ?? '',
      statusLabel: json['status_label']?.toString() ?? '',
      interpretation: json['overall_interpretation']?.toString() ?? '',
      interpretationLabel:
          json['overall_interpretation_label']?.toString() ?? '',
      abnormalCount:
          int.tryParse(json['abnormal_count']?.toString() ?? '') ?? 0,
      observations: (json['observations'] as List<dynamic>? ?? const [])
          .map(
            (item) =>
                ExaminationObservation.fromJson(item as Map<String, dynamic>),
          )
          .toList(),
      report: report is Map<String, dynamic>
          ? ExaminationReport.fromJson(report)
          : null,
    );
  }
}

class ExaminationObservation {
  const ExaminationObservation({
    required this.name,
    required this.value,
    required this.unit,
    required this.reference,
    required this.interpretation,
  });

  final String name;
  final String value;
  final String unit;
  final String reference;
  final String interpretation;

  factory ExaminationObservation.fromJson(Map<String, dynamic> json) {
    return ExaminationObservation(
      name: json['name']?.toString() ?? '',
      value: json['formatted_value']?.toString() ?? '',
      unit: json['unit']?.toString() ?? '',
      reference: json['reference_text']?.toString() ?? '',
      interpretation: json['interpretation_label']?.toString() ?? '',
    );
  }
}

class ExaminationReport {
  const ExaminationReport({
    required this.authorName,
    required this.summary,
    required this.conclusion,
    required this.isReleased,
    required this.assets,
  });

  final String authorName;
  final String summary;
  final String conclusion;
  final bool isReleased;
  final List<String> assets;

  factory ExaminationReport.fromJson(Map<String, dynamic> json) {
    return ExaminationReport(
      authorName: json['author_name']?.toString() ?? '',
      summary: json['summary']?.toString() ?? '',
      conclusion: json['conclusion']?.toString() ?? '',
      isReleased: json['is_released_to_patient'] == true,
      assets: (json['assets'] as List<dynamic>? ?? const [])
          .map(
            (item) =>
                (item as Map<String, dynamic>)['display_name']?.toString() ??
                '',
          )
          .where((value) => value.isNotEmpty)
          .toList(),
    );
  }
}
