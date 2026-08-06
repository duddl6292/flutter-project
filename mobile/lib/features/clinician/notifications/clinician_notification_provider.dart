import 'package:brainon_mobile/features/clinician/notifications/clinician_notification_model.dart';
import 'package:brainon_mobile/features/clinician/notifications/clinician_notification_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianNotificationsProvider =
    FutureProvider<List<ClinicianNotification>>(
      (ref) => ref.watch(clinicianNotificationRepositoryProvider).fetchAll(),
    );
