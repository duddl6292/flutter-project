import 'package:brainon_mobile/features/clinician/ai_analysis/clinician_ai_analysis_provider.dart';
import 'package:brainon_mobile/features/clinician/ai_analysis/clinician_ai_analysis_detail_screen.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianAiAnalysisScreen extends ConsumerWidget {
  const ClinicianAiAnalysisScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(clinicianAiAnalysesProvider);
    return ClinicianDetailScaffold(
      title: 'AI 분석',
      body: data.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(
          child: FilledButton(
            onPressed: () => ref.invalidate(clinicianAiAnalysesProvider),
            child: const Text('다시 시도'),
          ),
        ),
        data: (items) => ListView(
          padding: const EdgeInsets.all(20),
          children: [
            TextField(
              decoration: InputDecoration(
                hintText: '환자 검색',
                prefixIcon: const Icon(Icons.search),
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
            ),
            const SizedBox(height: 16),
            if (items.isEmpty) const Center(child: Text('분석 내역이 없습니다.')),
            ...items.map(
              (e) => Card(
                elevation: 0,
                child: ListTile(
                  onTap: () => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => ClinicianAiAnalysisDetailScreen(caseId: e.id))),
                  title: Text(
                    e.patientName,
                    style: const TextStyle(fontWeight: FontWeight.w800),
                  ),
                  subtitle: Text(
                    '${e.analysisType}\n${e.resultSummary.isEmpty ? '분석 결과를 준비하고 있습니다.' : e.resultSummary}',
                  ),
                  trailing: const Icon(Icons.chevron_right),
                ),
              ),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: () => ref.invalidate(clinicianAiAnalysesProvider),
              icon: const Icon(Icons.add),
              label: const Text('분석 목록 새로고침'),
            ),
          ],
        ),
      ),
    );
  }
}
