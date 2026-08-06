import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/features/patient/medical_history/patient_medical_history_model.dart';
import 'package:brainon_mobile/features/patient/medical_history/patient_medical_history_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class PatientMedicalHistoryDetailScreen extends ConsumerWidget {
  const PatientMedicalHistoryDetailScreen({
    super.key,
    required this.encounterId,
  });

  final String encounterId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final history = ref.watch(patientMedicalHistoryDetailProvider(encounterId));
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        title: const Text('진료 상세'),
      ),
      body: history.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _DetailError(
          error: error,
          onRetry: () =>
              ref.invalidate(patientMedicalHistoryDetailProvider(encounterId)),
        ),
        data: (item) => RefreshIndicator(
          onRefresh: () => ref.refresh(
            patientMedicalHistoryDetailProvider(encounterId).future,
          ),
          child: _DetailContent(history: item),
        ),
      ),
    );
  }
}

class _DetailContent extends StatelessWidget {
  const _DetailContent({required this.history});

  final PatientMedicalHistory history;

  @override
  Widget build(BuildContext context) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      padding: const EdgeInsets.all(20),
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: const Color(0xFFE5E7EB)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                history.departmentName,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 20),
              _DetailRow(label: '진료번호', value: history.encounterNumber),
              _DetailRow(
                label: '진료 유형',
                value: history.encounterTypeLabel.isEmpty
                    ? history.encounterType
                    : history.encounterTypeLabel,
              ),
              _DetailRow(
                label: '상태',
                value: history.statusLabel.isEmpty
                    ? history.status
                    : history.statusLabel,
              ),
              _DetailRow(label: '병원', value: history.hospitalName),
              _DetailRow(label: '진료과', value: history.departmentName),
              _DetailRow(label: '담당 의료진', value: history.clinicianName),
              _DetailRow(label: '진료일', value: _formatDateTime(history.eventAt)),
              if (history.arrivedAt != null)
                _DetailRow(
                  label: '도착 시각',
                  value: _formatDateTime(history.arrivedAt!),
                ),
              if (history.startedAt != null)
                _DetailRow(
                  label: '시작 시각',
                  value: _formatDateTime(history.startedAt!),
                ),
              if (history.completedAt != null)
                _DetailRow(
                  label: '완료 시각',
                  value: _formatDateTime(history.completedAt!),
                ),
            ],
          ),
        ),
      ],
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
      padding: const EdgeInsets.only(bottom: 13),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 88,
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
            unauthorized ? '로그인이 만료되었습니다. 다시 로그인해주세요.' : '진료 상세를 불러오지 못했습니다.',
          ),
          const SizedBox(height: 16),
          OutlinedButton(onPressed: onRetry, child: const Text('다시 시도')),
        ],
      ),
    );
  }
}

String _formatDateTime(DateTime date) {
  return '${date.year}.${date.month.toString().padLeft(2, '0')}.'
      '${date.day.toString().padLeft(2, '0')} '
      '${date.hour.toString().padLeft(2, '0')}:'
      '${date.minute.toString().padLeft(2, '0')}';
}
