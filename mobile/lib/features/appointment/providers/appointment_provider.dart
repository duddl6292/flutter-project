import 'package:brainon_mobile/features/appointment/repositories/appointment_repository.dart';
import 'package:brainon_mobile/shared/models/appointment.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final patientAppointmentsProvider = FutureProvider<List<Appointment>>(
  (ref) => ref.watch(appointmentRepositoryProvider).getAppointments(),
);
