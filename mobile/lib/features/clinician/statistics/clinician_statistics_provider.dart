import 'package:brainon_mobile/features/clinician/statistics/clinician_statistics_model.dart';
import 'package:brainon_mobile/features/clinician/statistics/clinician_statistics_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianStatisticsProvider = FutureProvider<ClinicianStatistics>(
  (ref) => ref.watch(clinicianStatisticsRepositoryProvider).fetch(),
);
