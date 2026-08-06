import 'package:brainon_mobile/features/clinician/notifications/clinician_notification_model.dart';
import 'package:brainon_mobile/shared/mock/clinician_notification_mock.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianNotificationRepositoryProvider = Provider(
  (ref) => const ClinicianNotificationRepository(),
);

class ClinicianNotificationRepository {
  const ClinicianNotificationRepository(); // TODO(API): GET /api/v1/clinicians/notifications/
  Future<List<ClinicianNotification>> fetchAll() async {
    await Future<void>.delayed(const Duration(milliseconds: 200));
    return clinicianNotificationMock
        .map(ClinicianNotification.fromJson)
        .toList();
  }
}
