class AppNotification {
  const AppNotification({
    required this.id,
    required this.type,
    required this.title,
    required this.body,
    required this.data,
    required this.isRead,
    required this.createdAt,
  });

  final String id;
  final String type;
  final String title;
  final String body;
  final Map<String, dynamic> data;
  final bool isRead;
  final DateTime createdAt;

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['notification_id'] as String,
      type: json['type'] as String? ?? 'OTHER',
      title: json['title'] as String? ?? '',
      body: json['body'] as String? ?? '',
      data: Map<String, dynamic>.from(json['data'] as Map? ?? const {}),
      isRead: json['is_read'] as bool? ?? false,
      createdAt:
          DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.now(),
    );
  }
}

class NotificationPreference {
  const NotificationPreference({
    required this.type,
    required this.pushEnabled,
    required this.emailEnabled,
  });

  final String type;
  final bool pushEnabled;
  final bool emailEnabled;

  factory NotificationPreference.fromJson(Map<String, dynamic> json) {
    return NotificationPreference(
      type: json['notification_type'] as String,
      pushEnabled: json['push_enabled'] as bool? ?? true,
      emailEnabled: json['email_enabled'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
    'notification_type': type,
    'push_enabled': pushEnabled,
    'email_enabled': emailEnabled,
  };

  NotificationPreference copyWith({bool? pushEnabled, bool? emailEnabled}) {
    return NotificationPreference(
      type: type,
      pushEnabled: pushEnabled ?? this.pushEnabled,
      emailEnabled: emailEnabled ?? this.emailEnabled,
    );
  }
}

class NotificationSettings {
  const NotificationSettings({
    required this.preferences,
    required this.quietHoursEnabled,
    this.quietHoursStart,
    this.quietHoursEnd,
  });

  final List<NotificationPreference> preferences;
  final bool quietHoursEnabled;
  final String? quietHoursStart;
  final String? quietHoursEnd;

  factory NotificationSettings.fromJson(Map<String, dynamic> json) {
    final global = Map<String, dynamic>.from(
      json['global_setting'] as Map? ?? const {},
    );
    return NotificationSettings(
      preferences: (json['preferences'] as List? ?? const [])
          .map(
            (item) => NotificationPreference.fromJson(
              Map<String, dynamic>.from(item as Map),
            ),
          )
          .toList(),
      quietHoursEnabled: global['quiet_hours_enabled'] as bool? ?? false,
      quietHoursStart: global['quiet_hours_start'] as String?,
      quietHoursEnd: global['quiet_hours_end'] as String?,
    );
  }
}
