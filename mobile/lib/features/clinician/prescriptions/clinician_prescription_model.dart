class ClinicianPrescriptionItem {
  const ClinicianPrescriptionItem({
    required this.id,
    required this.medicineName,
    required this.dosage,
    required this.doseUnit,
    required this.frequency,
    required this.route,
    required this.instructions,
    required this.startDate,
    required this.endDate,
    required this.mealTimes,
  });

  final String id;
  final String medicineName;
  final String dosage;
  final String doseUnit;
  final String frequency;
  final String route;
  final String instructions;
  final DateTime? startDate;
  final DateTime? endDate;
  final List<String> mealTimes;

  factory ClinicianPrescriptionItem.fromJson(Map<String, dynamic> json) =>
      ClinicianPrescriptionItem(
        id: json['prescription_item_id']?.toString() ?? '',
        medicineName: json['medicine_name']?.toString() ?? '',
        dosage: json['dosage']?.toString() ?? '',
        doseUnit: json['dose_unit']?.toString() ?? '',
        frequency: json['frequency']?.toString() ?? '',
        route: json['route']?.toString() ?? '',
        instructions: json['instructions']?.toString() ?? '',
        startDate: DateTime.tryParse(json['start_date']?.toString() ?? ''),
        endDate: DateTime.tryParse(json['end_date']?.toString() ?? ''),
        mealTimes: (json['meal_times'] as List<dynamic>? ?? const [])
            .map((value) => value.toString())
            .toList(),
      );
}

class ClinicianPrescription {
  const ClinicianPrescription({
    required this.id,
    required this.clinicalRecordId,
    required this.patientId,
    required this.patientNumber,
    required this.patientName,
    required this.clinicianName,
    required this.status,
    required this.statusLabel,
    required this.notes,
    required this.prescribedAt,
    required this.items,
  });

  final String id;
  final String clinicalRecordId;
  final String patientId;
  final String patientNumber;
  final String patientName;
  final String clinicianName;
  final String status;
  final String statusLabel;
  final String notes;
  final DateTime? prescribedAt;
  final List<ClinicianPrescriptionItem> items;

  factory ClinicianPrescription.fromJson(
    Map<String, dynamic> json,
  ) => ClinicianPrescription(
    id: json['prescription_id']?.toString() ?? '',
    clinicalRecordId: json['clinical_record_id']?.toString() ?? '',
    patientId: json['patient_id']?.toString() ?? '',
    patientNumber: json['patient_number']?.toString() ?? '',
    patientName: json['patient_name']?.toString() ?? '',
    clinicianName: json['clinician_name']?.toString() ?? '',
    status: json['status']?.toString() ?? '',
    statusLabel: json['status_label']?.toString() ?? '',
    notes: json['notes']?.toString() ?? '',
    prescribedAt: DateTime.tryParse(json['prescribed_at']?.toString() ?? ''),
    items: (json['items'] as List<dynamic>? ?? const [])
        .map(
          (item) =>
              ClinicianPrescriptionItem.fromJson(item as Map<String, dynamic>),
        )
        .toList(),
  );
}

class PrescriptionContext {
  const PrescriptionContext({
    required this.clinicalRecordId,
    required this.patientId,
    required this.patientNumber,
    required this.patientName,
    required this.recordedAt,
  });
  final String clinicalRecordId, patientId, patientNumber, patientName;
  final DateTime? recordedAt;

  factory PrescriptionContext.fromJson(Map<String, dynamic> json) =>
      PrescriptionContext(
        clinicalRecordId: json['clinical_record_id']?.toString() ?? '',
        patientId: json['patient_id']?.toString() ?? '',
        patientNumber: json['patient_number']?.toString() ?? '',
        patientName: json['patient_name']?.toString() ?? '',
        recordedAt: DateTime.tryParse(json['recorded_at']?.toString() ?? ''),
      );
}

class PrescriptionItemInput {
  const PrescriptionItemInput({
    required this.medicineName,
    required this.dosage,
    required this.doseUnit,
    required this.frequency,
    required this.route,
    required this.instructions,
    required this.startDate,
    required this.endDate,
    required this.mealTimes,
  });
  final String medicineName, dosage, doseUnit, frequency, route, instructions;
  final DateTime startDate;
  final DateTime? endDate;
  final List<String> mealTimes;

  Map<String, dynamic> toJson() => {
    'medicine_name': medicineName,
    'dosage': dosage,
    'dose_unit': doseUnit,
    'frequency': frequency,
    'route': route,
    'instructions': instructions,
    'start_date': _date(startDate),
    'end_date': endDate == null ? null : _date(endDate!),
    'meal_times': mealTimes,
  };
}

class PrescriptionCreateInput {
  const PrescriptionCreateInput({
    required this.clinicalRecordId,
    required this.status,
    required this.notes,
    required this.items,
  });
  final String clinicalRecordId, status, notes;
  final List<PrescriptionItemInput> items;

  Map<String, dynamic> toJson() => {
    'clinical_record_id': clinicalRecordId,
    'status': status,
    'notes': notes,
    'items': items.map((item) => item.toJson()).toList(),
  };
}

String _date(DateTime value) =>
    '${value.year.toString().padLeft(4, '0')}-${value.month.toString().padLeft(2, '0')}-${value.day.toString().padLeft(2, '0')}';
