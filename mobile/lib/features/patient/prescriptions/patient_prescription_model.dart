class PatientPrescriptionItem {
  const PatientPrescriptionItem({
    required this.prescriptionItemId,
    required this.medicineName,
    required this.dosage,
    required this.doseUnit,
    required this.frequency,
    required this.route,
    required this.instructions,
    required this.startDate,
    this.endDate,
    this.mealTimes = const [],
  });

  final String prescriptionItemId;
  final String medicineName;
  final String dosage;
  final String doseUnit;
  final String frequency;
  final String route;
  final String instructions;
  final DateTime? startDate;
  final DateTime? endDate;
  final List<String> mealTimes;

  factory PatientPrescriptionItem.fromJson(Map<String, dynamic> json) {
    return PatientPrescriptionItem(
      prescriptionItemId: json['prescription_item_id']?.toString() ?? '',
      medicineName: json['medicine_name']?.toString() ?? '',
      dosage: json['dosage']?.toString() ?? '',
      doseUnit: json['dose_unit']?.toString() ?? '',
      frequency: json['frequency']?.toString() ?? '',
      route: json['route']?.toString() ?? '',
      instructions: json['instructions']?.toString() ?? '',
      startDate: DateTime.tryParse(json['start_date']?.toString() ?? ''),
      endDate: DateTime.tryParse(json['end_date']?.toString() ?? ''),
      mealTimes:
          (json['meal_times'] as List<dynamic>? ?? const [])
              .map((value) => value.toString())
              .toList(),
    );
  }
}

class PatientPrescription {
  const PatientPrescription({
    required this.prescriptionId,
    required this.encounterId,
    required this.hospitalName,
    required this.clinicianName,
    required this.status,
    required this.statusLabel,
    required this.notes,
    required this.prescribedAt,
    this.discontinuedAt,
    this.items = const [],
  });

  final String prescriptionId;
  final String encounterId;
  final String hospitalName;
  final String clinicianName;
  final String status;
  final String statusLabel;
  final String notes;
  final DateTime? prescribedAt;
  final DateTime? discontinuedAt;
  final List<PatientPrescriptionItem> items;

  factory PatientPrescription.fromJson(Map<String, dynamic> json) {
    return PatientPrescription(
      prescriptionId: json['prescription_id']?.toString() ?? '',
      encounterId: json['encounter_id']?.toString() ?? '',
      hospitalName: json['hospital_name']?.toString() ?? '',
      clinicianName: json['clinician_name']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      statusLabel: json['status_label']?.toString() ?? '',
      notes: json['notes']?.toString() ?? '',
      prescribedAt: DateTime.tryParse(
        json['prescribed_at']?.toString() ?? '',
      )?.toLocal(),
      discontinuedAt: DateTime.tryParse(
        json['discontinued_at']?.toString() ?? '',
      )?.toLocal(),
      items:
          (json['items'] as List<dynamic>? ?? const [])
              .map(
                (item) => PatientPrescriptionItem.fromJson(
                  item as Map<String, dynamic>,
                ),
              )
              .toList(),
    );
  }
}
