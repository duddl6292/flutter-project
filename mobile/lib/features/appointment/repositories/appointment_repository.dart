import 'package:brainon_mobile/shared/models/appointment.dart';
import 'package:brainon_mobile/shared/mock/appointment_mock.dart';

class AppointmentRepository {
  Future<List<Appointment>> getAppointments() async {
    await Future<void>.delayed(
      const Duration(milliseconds: 300),
    );

    return appointmentMock
        .map(
          (json) => Appointment.fromJson(json),
        )
        .toList();
  }
}