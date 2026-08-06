class ClinicianNotificationSettings {
  const ClinicianNotificationSettings({
    required this.quietHoursEnabled,
    required this.quietHoursStart,
    required this.quietHoursEnd,
    required this.preferences,
  });

  final bool quietHoursEnabled;
  final String? quietHoursStart;
  final String? quietHoursEnd;
  final List<ClinicianNotificationPreference> preferences;

  factory ClinicianNotificationSettings.fromJson(Map<String, dynamic> json) {
    final global = json['global_setting'] as Map<String, dynamic>? ?? const {};
    final rows = json['preferences'] as List<dynamic>? ?? const [];
    return ClinicianNotificationSettings(
      quietHoursEnabled: global['quiet_hours_enabled'] == true,
      quietHoursStart: global['quiet_hours_start']?.toString(),
      quietHoursEnd: global['quiet_hours_end']?.toString(),
      preferences: rows
          .map(
            (row) => ClinicianNotificationPreference.fromJson(
              row as Map<String, dynamic>,
            ),
          )
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
    'global_setting': {
      'quiet_hours_enabled': quietHoursEnabled,
      'quiet_hours_start': quietHoursStart,
      'quiet_hours_end': quietHoursEnd,
    },
    'preferences': preferences.map((item) => item.toJson()).toList(),
  };
}

class ClinicianNotificationPreference {
  const ClinicianNotificationPreference({
    required this.type,
    required this.pushEnabled,
    required this.emailEnabled,
  });

  final String type;
  final bool pushEnabled;
  final bool emailEnabled;

  factory ClinicianNotificationPreference.fromJson(Map<String, dynamic> json) {
    return ClinicianNotificationPreference(
      type: json['notification_type']?.toString() ?? '',
      pushEnabled: json['push_enabled'] == true,
      emailEnabled: json['email_enabled'] == true,
    );
  }

  ClinicianNotificationPreference copyWith({
    bool? pushEnabled,
    bool? emailEnabled,
  }) {
    return ClinicianNotificationPreference(
      type: type,
      pushEnabled: pushEnabled ?? this.pushEnabled,
      emailEnabled: emailEnabled ?? this.emailEnabled,
    );
  }

  Map<String, dynamic> toJson() => {
    'notification_type': type,
    'push_enabled': pushEnabled,
    'email_enabled': emailEnabled,
  };
}
