import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/shared/models/medication.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final medicationRepositoryProvider = Provider<MedicationRepository>((ref) => MedicationRepository(ref.watch(apiClientProvider)));

class MedicationRepository {
  const MedicationRepository(this._dio);
  final Dio _dio;

  Future<List<Medication>> getTodayMedications() => runApiRequest(() async {
    final responses = await Future.wait([
      _dio.get<Map<String, dynamic>>('/api/v1/patients/me/medication-schedules/', queryParameters: {'active': true, 'page_size': 100}),
      _dio.get<Map<String, dynamic>>('/api/v1/patients/me/medication-records/', queryParameters: {'page_size': 100}),
      _dio.get<Map<String, dynamic>>('/api/v1/patients/me/prescriptions/', queryParameters: {'status': 'ACTIVE', 'page_size': 100}),
    ]);
    final schedules = _rows(responses[0].data).map(MedicationScheduleDto.fromJson);
    final records = _rows(responses[1].data).map(MedicationRecordDto.fromJson).toList();
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final items = schedules.where((schedule) {
      final end = schedule.endDate;
      return schedule.isActive && !today.isBefore(schedule.startDate) && (end == null || !today.isAfter(end)) && (schedule.daysOfWeek.isEmpty || schedule.daysOfWeek.contains(today.weekday));
    }).map((schedule) {
      final parts = schedule.doseTime.split(':');
      final scheduledAt = DateTime(today.year, today.month, today.day, int.tryParse(parts.first) ?? 0, parts.length > 1 ? int.tryParse(parts[1]) ?? 0 : 0);
      MedicationRecordDto? matching;
      for (final record in records) {
        if (record.scheduleId == schedule.id && _sameDay(record.scheduledAt, today)) {
          matching = record;
          break;
        }
      }
      return Medication(
        id: schedule.id,
        scheduleId: schedule.id,
        name: schedule.name,
        dose: '${schedule.dosage}${schedule.doseUnit}',
        scheduledAt: scheduledAt,
        period: schedule.frequency,
        instruction: schedule.instructions,
        completed: matching?.status == 'TAKEN',
        takenAt: matching?.takenAt,
      );
    }).toList();

    final scheduledItemIds = schedules.map((item) => item.prescriptionItemId).toSet();
    for (final prescription in _rows(responses[2].data)) {
      for (final rawItem in prescription['items'] as List<dynamic>? ?? const []) {
        final item = Map<String, dynamic>.from(rawItem as Map);
        final itemId = item['prescription_item_id']?.toString() ?? '';
        final start = DateTime.tryParse(item['start_date']?.toString() ?? '');
        final end = DateTime.tryParse(item['end_date']?.toString() ?? '');
        if (scheduledItemIds.contains(itemId) || start == null || today.isBefore(start) || (end != null && today.isAfter(end))) continue;
        items.add(Medication(
          id: itemId,
          name: item['medicine_name']?.toString() ?? '',
          dose: '${item['dosage'] ?? ''}${item['dose_unit'] ?? ''}',
          scheduledAt: DateTime(today.year, today.month, today.day, 9),
          period: item['frequency']?.toString() ?? '',
          instruction: item['instructions']?.toString() ?? '',
          completed: false,
          takenAt: null,
        ));
      }
    }
    return items..sort((a, b) => a.scheduledAt.compareTo(b.scheduledAt));
  });

  /// 복용 체크를 토글한다. 이미 복용 완료 상태면 다시 취소된다.
  Future<bool> toggleTaken({
    required String scheduleId,
    required DateTime scheduledAt,
  }) => runApiRequest(() async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/patients/me/medication-records/mark-taken/',
      data: {
        'schedule_id': scheduleId,
        'scheduled_at': scheduledAt.toUtc().toIso8601String(),
      },
    );
    final data = response.data?['data'] as Map<String, dynamic>? ?? const {};
    return data['status']?.toString() == 'TAKEN';
  });

  List<Map<String, dynamic>> _rows(Map<String, dynamic>? body) => (body?['data'] as List<dynamic>? ?? const []).cast<Map<String, dynamic>>();
  bool _sameDay(DateTime first, DateTime second) => first.year == second.year && first.month == second.month && first.day == second.day;
}
