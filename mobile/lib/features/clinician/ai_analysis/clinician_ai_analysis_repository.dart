import 'package:brainon_mobile/features/clinician/ai_analysis/clinician_ai_analysis_model.dart';
import 'package:brainon_mobile/shared/mock/clinician_ai_analysis_mock.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianAiAnalysisRepositoryProvider = Provider(
  (ref) => const ClinicianAiAnalysisRepository(),
);

class ClinicianAiAnalysisRepository {
  const ClinicianAiAnalysisRepository(); // TODO(API): GET /api/v1/clinicians/ai-analyses/
  Future<List<ClinicianAiAnalysis>> fetchAll() async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return clinicianAiAnalysisMock.map(ClinicianAiAnalysis.fromJson).toList();
  }
}
