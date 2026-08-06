import 'package:brainon_mobile/features/clinician/profile/clinician_notification_settings_model.dart';
import 'package:brainon_mobile/features/clinician/profile/clinician_profile_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianNotificationSettingsProvider =
    FutureProvider<ClinicianNotificationSettings>((ref) {
      return ref
          .watch(clinicianProfileRepositoryProvider)
          .fetchNotificationSettings();
    });
