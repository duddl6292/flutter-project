class Medication {
  const Medication({
    required this.id,
    required this.name,
    required this.dose,
    required this.scheduledAt,
    required this.period,
    required this.instruction,
    required this.completed,
    required this.takenAt,
  });
  final String id, name, dose, period, instruction;
  final DateTime scheduledAt;
  final bool completed;
  final DateTime? takenAt;
}

class MedicationScheduleDto {
  const MedicationScheduleDto({
    required this.id,
    required this.prescriptionItemId,
    required this.name,
    required this.dosage,
    required this.doseUnit,
    required this.frequency,
    required this.instructions,
    required this.doseTime,
    required this.daysOfWeek,
    required this.startDate,
    required this.endDate,
    required this.isActive,
  });
  final String id, prescriptionItemId, name, dosage, doseUnit, frequency, instructions, doseTime;
  final List<int> daysOfWeek;
  final DateTime startDate;
  final DateTime? endDate;
  final bool isActive;

  factory MedicationScheduleDto.fromJson(Map<String, dynamic> json) => MedicationScheduleDto(
    id: json['schedule_id']?.toString() ?? '',
    prescriptionItemId: json['prescription_item_id']?.toString() ?? '',
    name: json['medicine_name']?.toString() ?? '',
    dosage: json['dosage']?.toString() ?? '',
    doseUnit: json['dose_unit']?.toString() ?? '',
    frequency: json['frequency']?.toString() ?? '',
    instructions: json['instructions']?.toString() ?? '',
    doseTime: json['dose_time']?.toString() ?? '',
    daysOfWeek: (json['days_of_week'] as List<dynamic>? ?? const []).map((value) => int.tryParse(value.toString()) ?? 0).where((value) => value > 0).toList(),
    startDate: DateTime.parse(json['start_date'].toString()),
    endDate: DateTime.tryParse(json['end_date']?.toString() ?? ''),
    isActive: json['is_active'] == true,
  );
}

class MedicationRecordDto {
  const MedicationRecordDto({required this.scheduleId, required this.scheduledAt, required this.takenAt, required this.status});
  final String scheduleId, status;
  final DateTime scheduledAt;
  final DateTime? takenAt;
  factory MedicationRecordDto.fromJson(Map<String, dynamic> json) => MedicationRecordDto(
    scheduleId: json['schedule_id']?.toString() ?? '',
    scheduledAt: DateTime.parse(json['scheduled_at'].toString()).toLocal(),
    takenAt: DateTime.tryParse(json['taken_at']?.toString() ?? '')?.toLocal(),
    status: json['status']?.toString() ?? '',
  );
}
