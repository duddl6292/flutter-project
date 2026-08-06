import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/features/patient/test_results/patient_test_result_model.dart';
import 'package:brainon_mobile/features/patient/test_results/patient_test_result_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class PatientTestResultDetailScreen extends ConsumerWidget {
  const PatientTestResultDetailScreen({super.key, required this.testResultId});

  final String testResultId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final result = ref.watch(patientTestResultDetailProvider(testResultId));
    return Scaffold(
      backgroundColor: const Color(0xFFF6F8FC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        title: const Text('검사 결과 상세'),
      ),
      body: result.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _DetailError(
          error: error,
          onRetry: () =>
              ref.invalidate(patientTestResultDetailProvider(testResultId)),
        ),
        data: (item) => RefreshIndicator(
          onRefresh: () =>
              ref.refresh(patientTestResultDetailProvider(testResultId).future),
          child: _DetailContent(result: item),
        ),
      ),
    );
  }
}

class _DetailContent extends StatelessWidget {
  const _DetailContent({required this.result});

  final PatientTestResult result;

  @override
  Widget build(BuildContext context) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(20),
      children: [
        _SectionCard(
          title: result.title,
          children: [
            _DetailRow(label: '검사 종류', value: result.testType),
            _DetailRow(
              label: '검사일',
              value: _formatDateTime(result.performedAt),
            ),
            _DetailRow(
              label: '상태',
              value: result.statusLabel.isEmpty
                  ? result.status
                  : result.statusLabel,
            ),
            if (result.hospitalName.isNotEmpty)
              _DetailRow(label: '검사 기관', value: result.hospitalName),
            if (result.releasedAt != null)
              _DetailRow(
                label: '공개일',
                value: _formatDateTime(result.releasedAt!),
              ),
          ],
        ),
        if (result.summary.isNotEmpty) ...[
          const SizedBox(height: 14),
          _TextCard(title: '검사 결과', text: result.summary),
        ],
        if (result.clinicianComment.isNotEmpty) ...[
          const SizedBox(height: 14),
          _TextCard(title: '의료진 판독', text: result.clinicianComment),
        ],
      ],
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.title, required this.children});

  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: _cardDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 18),
          ...children,
        ],
      ),
    );
  }
}

class _TextCard extends StatelessWidget {
  const _TextCard({required this.title, required this.text});

  final String title;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: _cardDecoration(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
          const SizedBox(height: 10),
          Text(text, style: const TextStyle(height: 1.5)),
        ],
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 76,
            child: Text(
              label,
              style: const TextStyle(color: Color(0xFF6B7280)),
            ),
          ),
          Expanded(child: Text(value.isEmpty ? '-' : value)),
        ],
      ),
    );
  }
}

class _DetailError extends StatelessWidget {
  const _DetailError({required this.error, required this.onRetry});

  final Object error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final unauthorized =
        error is ApiException && (error as ApiException).statusCode == 401;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            unauthorized
                ? '로그인이 만료되었습니다. 다시 로그인해주세요.'
                : '검사 결과 상세를 불러오지 못했습니다.',
          ),
          const SizedBox(height: 16),
          OutlinedButton(onPressed: onRetry, child: const Text('다시 시도')),
        ],
      ),
    );
  }
}

BoxDecoration _cardDecoration() {
  return BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(18),
    border: Border.all(color: const Color(0xFFE5E7EB)),
  );
}

String _formatDateTime(DateTime date) {
  return '${date.year}.${date.month.toString().padLeft(2, '0')}.'
      '${date.day.toString().padLeft(2, '0')} '
      '${date.hour.toString().padLeft(2, '0')}:'
      '${date.minute.toString().padLeft(2, '0')}';
}
