import 'package:brainon_mobile/features/clinician/home/clinician_dashboard_model.dart';
import 'package:brainon_mobile/features/clinician/repository/clinician_dashboard_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// ==========================================================
// 의료진 홈 대시보드 Provider
//
// 역할:
// 1. Repository에서 대시보드 데이터를 요청한다.
// 2. 로딩 / 성공 / 실패 상태를 화면에 전달한다.
// 3. 현재는 Mock Repository를 사용하고,
//    나중에는 Repository 내부만 실제 API 호출로 변경한다.
// ==========================================================
final clinicianDashboardProvider = FutureProvider<ClinicianDashboard>((
  ref,
) async {
  final repository = ref.watch(clinicianDashboardRepositoryProvider);

  return repository.fetchDashboard();
});
