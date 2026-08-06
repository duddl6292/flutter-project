enum ClinicianRecordStatus { draft, completed }

class ClinicianRecord {
  const ClinicianRecord({
    required this.clinicalRecordId,
    required this.encounterId,
    required this.patientId,
    required this.patientName,
    required this.patientNumber,
    required this.patientBirthDate,
    required this.patientSex,
    required this.recordedAt,
    required this.chiefComplaint,
    required this.subjective,
    required this.objective,
    required this.assessment,
    required this.plan,
    required this.patientVisibleSummary,
    required this.status,
    required this.attachmentName,
  });

  final String clinicalRecordId;
  final String encounterId;
  final String patientId;
  final String patientName;
  final String patientNumber;
  final DateTime? patientBirthDate;
  final String patientSex;
  final DateTime? recordedAt;
  final String chiefComplaint;
  final String subjective;
  final String objective;
  final String assessment;
  final String plan;
  final String patientVisibleSummary;
  final ClinicianRecordStatus status;
  final String? attachmentName;

  factory ClinicianRecord.fromJson(Map<String, dynamic> json) {
    return ClinicianRecord(
      clinicalRecordId:
          json['clinical_record_id']?.toString() ??
          json['id']?.toString() ??
          '',
      encounterId: json['encounter_id']?.toString() ?? '',
      patientId: json['patient_id']?.toString() ?? '',
      patientName: json['patient_name']?.toString() ?? '',
      patientNumber: json['patient_number']?.toString() ?? '',
      patientBirthDate: DateTime.tryParse(
        json['patient_birth_date']?.toString() ?? '',
      ),
      patientSex: json['patient_sex']?.toString() ?? 'UNKNOWN',
      recordedAt: DateTime.tryParse(
        json['recorded_at']?.toString() ??
            json['scheduled_at']?.toString() ??
            '',
      ),
      chiefComplaint: json['chief_complaint']?.toString() ?? '',
      subjective: json['subjective']?.toString() ?? '',
      objective: json['objective']?.toString() ?? '',
      assessment: json['assessment']?.toString() ?? '',
      plan: json['plan']?.toString() ?? '',
      patientVisibleSummary: json['patient_visible_summary']?.toString() ?? '',
      status: json['record_status'] == 'draft'
          ? ClinicianRecordStatus.draft
          : ClinicianRecordStatus.completed,
      attachmentName: json['attachment_name']?.toString(),
    );
  }

  String get summary => patientVisibleSummary.isNotEmpty
      ? patientVisibleSummary
      : (plan.isNotEmpty ? plan : subjective);

  int? get patientAge {
    final birthDate = patientBirthDate;
    if (birthDate == null) return null;
    final today = DateTime.now();
    var age = today.year - birthDate.year;
    if (today.month < birthDate.month ||
        (today.month == birthDate.month && today.day < birthDate.day)) {
      age--;
    }
    return age;
  }
}

class ClinicianRecordInput {
  const ClinicianRecordInput({
    required this.patientId,
    required this.recordedAt,
    required this.chiefComplaint,
    required this.subjective,
    required this.objective,
    required this.assessment,
    required this.plan,
    required this.patientVisibleSummary,
  });
  final String patientId;
  final DateTime recordedAt;
  final String chiefComplaint;
  final String subjective;
  final String objective;
  final String assessment;
  final String plan;
  final String patientVisibleSummary;

  Map<String, dynamic> toJson() => {
    'chief_complaint': chiefComplaint,
    'subjective': subjective,
    'objective': objective,
    'assessment': assessment,
    'plan': plan,
    'patient_visible_summary': patientVisibleSummary,
  };
}
