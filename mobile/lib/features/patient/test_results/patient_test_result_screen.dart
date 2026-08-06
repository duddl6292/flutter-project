import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/patient/test_results/patient_test_result_model.dart';
import 'package:brainon_mobile/features/patient/test_results/patient_test_result_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class PatientTestResultScreen extends ConsumerWidget {
  const PatientTestResultScreen({super.key, required this.onOpenDrawer});

  final VoidCallback onOpenDrawer;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final results = ref.watch(patientTestResultsProvider);
    return Scaffold(
      backgroundColor: const Color(0xFFF6F8FC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        leading: IconButton(
          onPressed: onOpenDrawer,
          icon: const Icon(Icons.menu_rounded),
        ),
        title: const Text('검사 결과'),
      ),
      body: results.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _ErrorState(
          error: error,
          onRetry: () => ref.invalidate(patientTestResultsProvider),
        ),
        data: (items) {
          if (items.isEmpty) {
            return const _EmptyState();
          }
          return RefreshIndicator(
            onRefresh: () => ref.refresh(patientTestResultsProvider.future),
            child: ListView.separated(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(20),
              itemCount: items.length,
              separatorBuilder: (_, _) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final result = items[index];
                return _ResultCard(
                  result: result,
                  onTap: () => context.pushNamed(
                    RouteNames.patientTestResultDetail,
                    pathParameters: {'testResultId': result.id},
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

class _ResultCard extends StatelessWidget {
  const _ResultCard({required this.result, required this.onTap});

  final PatientTestResult result;
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
                      result.title,
                      style: const TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                  _StatusBadge(label: result.statusLabel),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                [
                  if (result.testType.isNotEmpty) result.testType,
                  _formatDate(result.performedAt),
                ].join(' · '),
                style: const TextStyle(color: Color(0xFF6B7280)),
              ),
              if (result.hospitalName.isNotEmpty) ...[
                const SizedBox(height: 6),
                Text(
                  result.hospitalName,
                  style: const TextStyle(color: Color(0xFF4B5563)),
                ),
              ],
              if (result.summary.isNotEmpty) ...[
                const SizedBox(height: 12),
                Text(
                  result.summary,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
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

class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Text(
          '환자에게 공개된 검사 결과가 없습니다.',
          textAlign: TextAlign.center,
          style: TextStyle(color: Color(0xFF6B7280)),
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
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              unauthorized ? '로그인이 만료되었습니다. 다시 로그인해주세요.' : '검사 결과를 불러오지 못했습니다.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('다시 시도'),
            ),
          ],
        ),
      ),
    );
  }
}

String _formatDate(DateTime date) {
  return '${date.year}.${date.month.toString().padLeft(2, '0')}.'
      '${date.day.toString().padLeft(2, '0')}';
}
