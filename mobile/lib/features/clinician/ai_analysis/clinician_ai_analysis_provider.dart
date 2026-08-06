import 'package:brainon_mobile/features/clinician/ai_analysis/clinician_ai_analysis_model.dart';
import 'package:brainon_mobile/features/clinician/ai_analysis/clinician_ai_analysis_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianAiAnalysesProvider = FutureProvider<List<ClinicianAiAnalysis>>(
  (ref) => ref.watch(clinicianAiAnalysisRepositoryProvider).fetchAll(),
);
