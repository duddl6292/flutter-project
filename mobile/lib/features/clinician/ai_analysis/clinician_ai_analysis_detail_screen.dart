import 'package:brainon_mobile/features/clinician/ai_analysis/clinician_ai_analysis_model.dart';
import 'package:brainon_mobile/features/clinician/ai_analysis/clinician_ai_analysis_repository.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianAiAnalysisDetailScreen extends ConsumerWidget {
  const ClinicianAiAnalysisDetailScreen({required this.caseId, super.key});
  final String caseId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final repository = ref.watch(clinicianAiAnalysisRepositoryProvider);
    return ClinicianDetailScaffold(
      title: 'AI 분석 상세',
      body: FutureBuilder<ClinicianAiAnalysis>(
        future: repository.fetchDetail(caseId),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            if (snapshot.hasError) return Center(child: Text('분석 결과를 불러오지 못했습니다.\n${snapshot.error}'));
            return const Center(child: CircularProgressIndicator());
          }
          final item = snapshot.data!;
          final result = item.result;
          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              _section('환자 정보', {
                '이름': item.patientName,
                '환자번호': item.patientNumber,
                '성별 / 나이': '${item.sex}${item.age == null ? '' : ' / ${item.age}세'}',
                '검사 유형': item.analysisType,
                '설명': item.description,
              }),
              _section('분석 결과', {
                '판정': item.resultSummary,
                '병변 부피': '${result['lesion_volume_ml'] ?? '-'} mL',
                '병변 복셀': '${result['lesion_voxels'] ?? '-'}',
                '병변 슬라이스': '${result['lesion_slice_start'] ?? '-'} ~ ${result['lesion_slice_end'] ?? '-'} (${result['lesion_slice_count'] ?? '-'}장)',
                '최대 병변 슬라이스': '${result['max_lesion_slice'] ?? '-'}',
                '영상 크기': '${result['shape'] ?? '-'}',
                '간격': '${result['spacing'] ?? '-'}',
              }),
              _section('모델 및 처리 정보', {
                '모델': '${result['model_id'] ?? '-'} ${result['model_version'] ?? ''}',
                '전처리': '${result['preprocessing_seconds'] ?? '-'}초',
                '추론': '${result['inference_seconds'] ?? '-'}초',
                '후처리': '${result['postprocessing_seconds'] ?? '-'}초',
                '전체 처리': '${result['total_seconds'] ?? '-'}초',
                'GPU 최대 메모리': '${result['gpu_memory_peak_mb'] ?? '-'} MB',
              }),
            ],
          );
        },
      ),
    );
  }

  Widget _section(String title, Map<String, String> values) => Card(
    margin: const EdgeInsets.only(bottom: 14),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w800)),
        const Divider(),
        for (final entry in values.entries)
          if (entry.value.trim().isNotEmpty)
            Padding(padding: const EdgeInsets.symmetric(vertical: 5), child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [SizedBox(width: 120, child: Text(entry.key, style: const TextStyle(color: Colors.grey))), Expanded(child: Text(entry.value))])),
      ]),
    ),
  );
}
