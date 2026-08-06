import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/patient/medical_history/patient_medical_history_model.dart';
import 'package:brainon_mobile/features/patient/medical_history/patient_medical_history_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class PatientMedicalHistoryScreen extends ConsumerWidget {
  const PatientMedicalHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final histories = ref.watch(patientMedicalHistoriesProvider);
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        title: const Text('진료 내역'),
      ),
      body: histories.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _ErrorState(
          error: error,
          onRetry: () => ref.invalidate(patientMedicalHistoriesProvider),
        ),
        data: (items) {
          if (items.isEmpty) {
            return const Center(child: Text('진료 내역이 없습니다.'));
          }
          return RefreshIndicator(
            onRefresh: () =>
                ref.refresh(patientMedicalHistoriesProvider.future),
            child: ListView.separated(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(20),
              itemCount: items.length,
              separatorBuilder: (_, _) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final history = items[index];
                return _HistoryCard(
                  history: history,
                  onTap: () => context.pushNamed(
                    RouteNames.patientMedicalHistoryDetail,
                    pathParameters: {'encounterId': history.encounterId},
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}

class _HistoryCard extends StatelessWidget {
  const _HistoryCard({required this.history, required this.onTap});

  final PatientMedicalHistory history;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      elevation: 0,
      color: Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: const BorderSide(color: Color(0xFFE5E7EB)),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      history.departmentName,
                      style: const TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                  _StatusBadge(
                    label: history.statusLabel.isEmpty
                        ? history.status
                        : history.statusLabel,
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                '${_formatDate(history.eventAt)} · '
                '${history.encounterTypeLabel}',
                style: const TextStyle(color: Color(0xFF6B7280)),
              ),
              if (history.hospitalName.isNotEmpty) ...[
                const SizedBox(height: 6),
                Text(history.hospitalName),
              ],
              if (history.clinicianName.isNotEmpty) ...[
                const SizedBox(height: 5),
                Text(
                  '담당 의료진 ${history.clinicianName}',
                  style: const TextStyle(color: Color(0xFF4B5563)),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: const Color(0xFFEFF6FF),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Color(0xFF2563EB),
          fontSize: 12,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.error, required this.onRetry});

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
            unauthorized ? '로그인이 만료되었습니다. 다시 로그인해주세요.' : '진료 내역을 불러오지 못했습니다.',
          ),
          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh_rounded),
            label: const Text('다시 시도'),
          ),
        ],
      ),
    );
  }
}

String _formatDate(DateTime date) {
  return '${date.year}.${date.month.toString().padLeft(2, '0')}.'
      '${date.day.toString().padLeft(2, '0')}';
}
