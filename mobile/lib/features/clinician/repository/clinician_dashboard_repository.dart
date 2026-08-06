import 'package:brainon_mobile/core/api/api_client.dart';
import 'package:brainon_mobile/features/clinician/home/clinician_dashboard_model.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// ==========================================================
// 의료진 대시보드 Repository Provider
// - 화면이나 Provider가 Repository 구현체를 직접 생성하지 않도록 관리한다.
// - 나중에 API Repository로 교체하기 쉬워진다.
// ==========================================================
final clinicianDashboardRepositoryProvider =
    Provider<ClinicianDashboardRepository>((ref) {
      return ClinicianDashboardRepository(ref.watch(apiClientProvider));
    });

// ==========================================================
// 의료진 홈 대시보드 데이터 처리 Repository
//
// 현재:
// Mock 데이터를 모델로 변환하여 반환
//
// 추후:
// 실제 API 요청 결과를 모델로 변환하여 반환
// ==========================================================
class ClinicianDashboardRepository {
  const ClinicianDashboardRepository(this._dio);

  final Dio _dio;

  Future<ClinicianDashboard> fetchDashboard() {
    return runApiRequest(() async {
      final today = _date(DateTime.now());
      final dashboardResponse = await _dio.get<Map<String, dynamic>>(
        '/api/v1/clinicians/clinicians/me/dashboard',
        queryParameters: {'date': today},
      );
      final appointmentResponse = await _dio.get<Map<String, dynamic>>(
        '/api/v1/appointments/',
        queryParameters: {'date_from': today, 'date_to': today},
      );

      final dashboardData = Map<String, dynamic>.from(
        dashboardResponse.data?['data'] as Map? ?? const {},
      );
      dashboardData['schedules'] =
          appointmentResponse.data?['data'] as List<dynamic>? ?? const [];
      return ClinicianDashboard.fromJson(dashboardData);
    });
  }

  String _date(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-'
        '${date.day.toString().padLeft(2, '0')}';
  }
}
