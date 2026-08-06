// 의료진 홈 대시보드 API 응답의 data 영역을 표현하는 모델
class ClinicianDashboard {
  const ClinicianDashboard({
    required this.summary,
    required this.schedules,
    required this.consultations,
  });

  final ClinicianDashboardSummary summary;
  final List<ClinicianSchedule> schedules;
  final List<ClinicianConsultation> consultations;

  // Mock 또는 API의 data 객체를 Dart 모델로 변환
  factory ClinicianDashboard.fromJson(Map<String, dynamic> json) {
    return ClinicianDashboard(
      summary: ClinicianDashboardSummary.fromJson(_asMap(json['summary'])),
      schedules: _asList(
        json['schedules'],
      ).map((item) => ClinicianSchedule.fromJson(_asMap(item))).toList(),
      consultations: _asList(
        json['consultations'],
      ).map((item) => ClinicianConsultation.fromJson(_asMap(item))).toList(),
    );
  }
}

// 의료진 홈 상단의 숫자 요약 정보
class ClinicianDashboardSummary {
  const ClinicianDashboardSummary({
    required this.appointmentTotal,
    required this.appointmentWaiting,
    required this.consultationWaiting,
    required this.testResultWaiting,
  });

  final int appointmentTotal;
  final int appointmentWaiting;
  final int consultationWaiting;
  final int testResultWaiting;

  factory ClinicianDashboardSummary.fromJson(Map<String, dynamic> json) {
    final appointments = _asMap(json['appointments']);
    final consultations = _asMap(json['consultations']);
    final tests = _asMap(json['tests']);

    return ClinicianDashboardSummary(
      appointmentTotal: _asInt(appointments['total']),
      appointmentWaiting: _asInt(appointments['waiting']),
      consultationWaiting: _asInt(consultations['waiting']),
      testResultWaiting: _asInt(tests['result_waiting']),
    );
  }
}

// 오늘 일정 한 건
class ClinicianSchedule {
  const ClinicianSchedule({
    required this.id,
    required this.patientId,
    required this.patientName,
    required this.room,
    required this.status,
    required this.startAt,
  });

  final String id;
  final String patientId;
  final String patientName;
  final String room;
  final String status;
  final DateTime startAt;

  factory ClinicianSchedule.fromJson(Map<String, dynamic> json) {
    return ClinicianSchedule(
      id: _asString(json['appointment_id']),
      patientId: _asString(json['patient_id']),
      patientName: _asString(json['patient_name']),
      room: _asString(json['location']),
      status: _asString(json['status']).toLowerCase(),
      startAt: _asDateTime(json['scheduled_at']),
    );
  }
}

// 협진 요청 한 건
class ClinicianConsultation {
  const ClinicianConsultation({
    required this.id,
    required this.department,
    required this.status,
  });

  final String id;
  final String department;
  final String status;

  factory ClinicianConsultation.fromJson(Map<String, dynamic> json) {
    return ClinicianConsultation(
      id: _asString(json['consultation_id']),
      department: _asString(json['department']),
      status: _asString(json['status']),
    );
  }
}

// ==========================================================
// JSON 안전 변환 함수
// API 값이 null이거나 예상 타입과 달라도 앱이 바로 종료되지 않게 처리
// ==========================================================

Map<String, dynamic> _asMap(Object? value) {
  if (value is Map<String, dynamic>) {
    return value;
  }

  if (value is Map) {
    return value.map((key, item) => MapEntry(key.toString(), item));
  }

  return <String, dynamic>{};
}

List<dynamic> _asList(Object? value) {
  if (value is List) {
    return value;
  }

  return const [];
}

String _asString(Object? value) {
  return value?.toString() ?? '';
}

int _asInt(Object? value) {
  if (value is int) {
    return value;
  }

  if (value is num) {
    return value.toInt();
  }

  return int.tryParse(value?.toString() ?? '') ?? 0;
}

DateTime _asDateTime(Object? value) {
  if (value is DateTime) {
    return value;
  }

  return DateTime.tryParse(value?.toString() ?? '') ??
      DateTime.fromMillisecondsSinceEpoch(0);
}
