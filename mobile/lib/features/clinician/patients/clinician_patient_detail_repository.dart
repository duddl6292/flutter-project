import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_detail_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianPatientDetailRepositoryProvider =
    Provider<ClinicianPatientDetailRepository>(
      (ref) => ClinicianPatientDetailRepository(ref.watch(apiClientProvider)),
    );

class ClinicianPatientDetailRepository {
  const ClinicianPatientDetailRepository(this._dio);
  final Dio _dio;

  Future<ClinicianPatientDetail> fetchDetail(String patientId) {
    return runApiRequest(() async {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/patients/$patientId/',
      );
      return ClinicianPatientDetail.fromJson(
        response.data!['data'] as Map<String, dynamic>,
      );
    });
  }

  Future<ClinicianExamination> fetchExamination(String examinationId) {
    return runApiRequest(() async {
      final response = await _dio.get<Map<String, dynamic>>(
        '/api/v1/examinations/$examinationId/',
      );
      return ClinicianExamination.fromJson(
        response.data!['data'] as Map<String, dynamic>,
      );
    });
  }

  Future<List<PatientResourceItem>> fetchResources({
    required ClinicianPatientDetail patient,
    required PatientResourceType type,
  }) {
    return runApiRequest(() async {
      return switch (type) {
        PatientResourceType.examinations => _fetchExaminations(patient),
        PatientResourceType.medicalHistory => _fetchMedicalHistory(patient.id),
        PatientResourceType.appointments => _fetchAppointments(patient.id),
        PatientResourceType.prescriptions => _fetchPrescriptions(patient),
      };
    });
  }

  Future<List<PatientResourceItem>> _fetchExaminations(
    ClinicianPatientDetail patient,
  ) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/examinations/',
      queryParameters: {
        'search': patient.medicalRecordNumber,
        'page_size': 100,
      },
    );
    final rows = response.data?['data'] as List<dynamic>? ?? const [];
    return rows
        .map(
          (row) => ClinicianExamination.fromJson(row as Map<String, dynamic>),
        )
        .where((item) => item.patientId == patient.id)
        .map(
          (item) => PatientResourceItem(
            id: item.id,
            title: item.testName,
            subtitle: _date(item.performedAt),
            status: item.statusLabel.isEmpty ? item.status : item.statusLabel,
            examination: item,
          ),
        )
        .toList();
  }

  Future<List<PatientResourceItem>> _fetchMedicalHistory(
    String patientId,
  ) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/patients/$patientId/medical-history/',
      queryParameters: {'page_size': 100},
    );
    final rows = response.data?['data'] as List<dynamic>? ?? const [];
    return rows.map((raw) {
      final row = raw as Map<String, dynamic>;
      final record = row['clinical_record'] as Map<String, dynamic>?;
      return PatientResourceItem(
        id: row['encounter_id']?.toString() ?? '',
        title: record?['chief_complaint']?.toString().isNotEmpty == true
            ? record!['chief_complaint'].toString()
            : row['encounter_type_label']?.toString() ?? '',
        subtitle: [
          row['clinician_name']?.toString() ?? '',
          _date(DateTime.tryParse(row['completed_at']?.toString() ?? '')),
        ].where((value) => value.isNotEmpty).join(' · '),
        status:
            row['status_label']?.toString() ?? row['status']?.toString() ?? '',
      );
    }).toList();
  }

  Future<List<PatientResourceItem>> _fetchAppointments(String patientId) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/appointments/',
    );
    final rows = response.data?['data'] as List<dynamic>? ?? const [];
    return rows
        .where(
          (raw) =>
              (raw as Map<String, dynamic>)['patient_id']?.toString() ==
              patientId,
        )
        .map((raw) {
          final row = raw as Map<String, dynamic>;
          return PatientResourceItem(
            id: row['appointment_id']?.toString() ?? '',
            title: row['reason']?.toString().isNotEmpty == true
                ? row['reason'].toString()
                : row['department_name']?.toString() ?? '',
            subtitle: _date(
              DateTime.tryParse(row['scheduled_at']?.toString() ?? ''),
            ),
            status: row['status']?.toString() ?? '',
          );
        })
        .toList();
  }

  Future<List<PatientResourceItem>> _fetchPrescriptions(
    ClinicianPatientDetail patient,
  ) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/prescriptions/',
      queryParameters: {
        'search': patient.medicalRecordNumber,
        'page_size': 100,
      },
    );
    final rows = response.data?['data'] as List<dynamic>? ?? const [];
    return rows
        .where(
          (raw) =>
              (raw as Map<String, dynamic>)['patient_id']?.toString() ==
              patient.id,
        )
        .map((raw) {
          final row = raw as Map<String, dynamic>;
          final items = row['items'] as List<dynamic>? ?? const [];
          final medicines = items
              .map(
                (item) =>
                    (item as Map<String, dynamic>)['medicine_name']
                        ?.toString() ??
                    '',
              )
              .where((value) => value.isNotEmpty)
              .join(', ');
          return PatientResourceItem(
            id: row['prescription_id']?.toString() ?? '',
            title: medicines,
            subtitle: _date(
              DateTime.tryParse(row['prescribed_at']?.toString() ?? ''),
            ),
            status:
                row['status_label']?.toString() ??
                row['status']?.toString() ??
                '',
          );
        })
        .toList();
  }

  static String _date(DateTime? value) {
    if (value == null) return '';
    final local = value.toLocal();
    return '${local.year}.${local.month.toString().padLeft(2, '0')}.${local.day.toString().padLeft(2, '0')}';
  }
}
