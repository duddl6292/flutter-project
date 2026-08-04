class Medication {
  final String id;
  final String name;
  final String dose;
  final DateTime scheduledAt;
  final String period;
  final String instruction;
  final bool completed;

  const Medication({
    required this.id,
    required this.name,
    required this.dose,
    required this.scheduledAt,
    required this.period,
    required this.instruction,
    required this.completed,
  });

  factory Medication.fromJson(
    Map<String, dynamic> json,
  ) {
    return Medication(
      id: json['id'].toString(),
      name: json['name']?.toString() ?? '',
      dose: json['dose']?.toString() ?? '',
      scheduledAt: DateTime.parse(
        json['scheduled_at'].toString(),
      ),
      period: json['period']?.toString() ?? '',
      instruction:
          json['instruction']?.toString() ?? '',
      completed: json['completed'] == true,
    );
  }

  Medication copyWith({
    String? id,
    String? name,
    String? dose,
    DateTime? scheduledAt,
    String? period,
    String? instruction,
    bool? completed,
  }) {
    return Medication(
      id: id ?? this.id,
      name: name ?? this.name,
      dose: dose ?? this.dose,
      scheduledAt: scheduledAt ?? this.scheduledAt,
      period: period ?? this.period,
      instruction: instruction ?? this.instruction,
      completed: completed ?? this.completed,
    );
  }
}