import 'package:brainon_mobile/features/clinician/ai_analysis/clinician_ai_analysis_screen.dart';
import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_screen.dart';
import 'package:brainon_mobile/features/clinician/notices/clinician_notice_screen.dart';
import 'package:brainon_mobile/features/clinician/notifications/clinician_notification_screen.dart';
import 'package:brainon_mobile/features/clinician/prescriptions/clinician_prescription_screen.dart';
import 'package:brainon_mobile/features/clinician/statistics/clinician_statistics_screen.dart';
import 'package:brainon_mobile/features/clinician/support/clinician_support_screen.dart';
import 'package:brainon_mobile/features/clinician/test_results/clinician_test_result_screen.dart';
import 'package:flutter/material.dart';

abstract final class ClinicianFeatureNavigation {
  static Future<void> open(BuildContext context, Widget screen) {
    return Navigator.of(
      context,
    ).push<void>(MaterialPageRoute<void>(builder: (_) => screen));
  }

  static Future<void> notifications(BuildContext context) =>
      open(context, const ClinicianNotificationScreen());
  static Future<void> testResults(BuildContext context) =>
      open(context, const ClinicianTestResultScreen());
  static Future<void> prescriptions(BuildContext context) =>
      open(context, const ClinicianPrescriptionScreen());
  static Future<void> records(BuildContext context) =>
      open(context, const ClinicianRecordScreen());
  static Future<void> aiAnalysis(BuildContext context) =>
      open(context, const ClinicianAiAnalysisScreen());
  static Future<void> statistics(BuildContext context) =>
      open(context, const ClinicianStatisticsScreen());
  static Future<void> notices(BuildContext context) =>
      open(context, const ClinicianNoticeScreen());
  static Future<void> support(BuildContext context) =>
      open(context, const ClinicianSupportScreen());
}
