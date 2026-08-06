import 'package:brainon_mobile/features/clinician/appointments/clinician_schedule_model.dart';
import 'package:brainon_mobile/features/clinician/appointments/clinician_schedule_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianSchedulesProvider = FutureProvider<List<ClinicianSchedule>>((
  ref,
) {
  return ref.watch(clinicianScheduleRepositoryProvider).fetchSchedules();
});
