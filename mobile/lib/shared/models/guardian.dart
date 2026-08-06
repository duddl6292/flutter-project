class Guardian {
  const Guardian({
    required this.id,
    required this.name,
    required this.relationship,
    required this.phone,
    required this.emergencyPriority,
  });

  final int id;
  final String name;
  final String relationship;
  final String phone;
  final int emergencyPriority;

  Guardian copyWith({
    int? id,
    String? name,
    String? relationship,
    String? phone,
    int? emergencyPriority,
  }) {
    return Guardian(
      id: id ?? this.id,
      name: name ?? this.name,
      relationship: relationship ?? this.relationship,
      phone: phone ?? this.phone,
      emergencyPriority: emergencyPriority ?? this.emergencyPriority,
    );
  }
}
