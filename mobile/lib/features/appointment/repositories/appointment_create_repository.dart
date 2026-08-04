import 'package:brainon_mobile/shared/models/appointment_create_request.dart';

class AppointmentCreateRepository {
  Future<void> createAppointment(AppointmentCreateRequest request) async {
    // TODO: Django 예약 생성 API 연결
    await Future<void>.delayed(const Duration(milliseconds: 700));

    request.toJson();
  }
}
