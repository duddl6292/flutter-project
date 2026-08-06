import 'package:brainon_mobile/features/clinician/statistics/clinician_statistics_model.dart';
import 'package:brainon_mobile/shared/mock/clinician_statistics_mock.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianStatisticsRepositoryProvider = Provider(
  (ref) => const ClinicianStatisticsRepository(),
);

class ClinicianStatisticsRepository {
  const ClinicianStatisticsRepository(); // TODO(API): GET /api/v1/clinicians/statistics/
  Future<ClinicianStatistics> fetch() async {
    await Future<void>.delayed(const Duration(milliseconds: 200));
    return ClinicianStatistics.fromJson(clinicianStatisticsMock);
  }
}
