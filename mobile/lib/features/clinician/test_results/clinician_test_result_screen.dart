import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/test_results/clinician_test_result_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class ClinicianTestResultScreen extends ConsumerStatefulWidget {
  const ClinicianTestResultScreen({super.key});

  @override
  ConsumerState<ClinicianTestResultScreen> createState() =>
      _ClinicianTestResultScreenState();
}

class _ClinicianTestResultScreenState
    extends ConsumerState<ClinicianTestResultScreen> {
  String query = '';

  @override
  Widget build(BuildContext context) {
    final value = ref.watch(clinicianTestResultsProvider);

    return ClinicianDetailScaffold(
      title: '검사 결과 관리',
      body: ColoredBox(
        color: ClinicianUiColors.background,
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 16),
              child: _SearchField(
                onChanged: (text) => setState(() => query = text),
              ),
            ),
            Expanded(
              child: value.when(
                loading: () => const ClinicianLoadingView(),
                error: (error, _) => ClinicianErrorView(
                  message: error.toString(),
                  onRetry: () => ref.invalidate(clinicianTestResultsProvider),
                ),
                data: (items) {
                  final normalizedQuery = query.toLowerCase();
                  final filtered = items
                      .where(
                        (item) => item.testName.toLowerCase().contains(
                          normalizedQuery,
                        ),
                      )
                      .toList(growable: false);

                  if (filtered.isEmpty) {
                    return ClinicianEmptyView(
                      message: query.isEmpty ? '검사 결과가 없습니다.' : '검색 결과가 없습니다.',
                      icon: query.isEmpty
                          ? Icons.science_outlined
                          : Icons.search_off_rounded,
                    );
                  }

                  return ListView.builder(
                    keyboardDismissBehavior:
                        ScrollViewKeyboardDismissBehavior.onDrag,
                    padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
                    itemCount: filtered.length,
                    itemBuilder: (context, index) {
                      final item = filtered[index];
                      final statusLabel = item.statusLabel.isEmpty
                          ? item.status
                          : item.statusLabel;
                      final interpretationLabel =
                          item.interpretationLabel.isEmpty
                          ? item.interpretation
                          : item.interpretationLabel;

                      return ClinicianListCard(
                        onTap: () => context.pushNamed(
                          RouteNames.clinicianExaminationDetail,
                          pathParameters: {'examinationId': item.id},
                          extra: item,
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 46,
                              height: 46,
                              decoration: BoxDecoration(
                                color: const Color(0xFFEAF1FF),
                                borderRadius: BorderRadius.circular(14),
                              ),
                              child: const Icon(
                                Icons.science_outlined,
                                color: ClinicianUiColors.primary,
                                size: 24,
                              ),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    item.testName.isEmpty ? '-' : item.testName,
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      color: ClinicianUiColors.text,
                                      fontSize: 16,
                                      fontWeight: FontWeight.w800,
                                      height: 1.35,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Row(
                                    children: [
                                      const Icon(
                                        Icons.calendar_today_outlined,
                                        size: 15,
                                        color: ClinicianUiColors.mutedText,
                                      ),
                                      const SizedBox(width: 6),
                                      Text(
                                        _formatDate(item.performedAt),
                                        style: const TextStyle(
                                          color: ClinicianUiColors.mutedText,
                                          fontSize: 13,
                                          fontWeight: FontWeight.w500,
                                        ),
                                      ),
                                    ],
                                  ),
                                  if (statusLabel.isNotEmpty ||
                                      interpretationLabel.isNotEmpty) ...[
                                    const SizedBox(height: 12),
                                    Wrap(
                                      spacing: 8,
                                      runSpacing: 8,
                                      children: [
                                        if (statusLabel.isNotEmpty)
                                          ClinicianStatusBadge(
                                            label: statusLabel,
                                            tone: _statusTone(item.status),
                                          ),
                                        if (interpretationLabel.isNotEmpty)
                                          ClinicianStatusBadge(
                                            label: interpretationLabel,
                                            tone: _interpretationTone(
                                              item.interpretation,
                                            ),
                                          ),
                                      ],
                                    ),
                                  ],
                                ],
                              ),
                            ),
                            const SizedBox(width: 8),
                            const Padding(
                              padding: EdgeInsets.only(top: 10),
                              child: Icon(
                                Icons.chevron_right_rounded,
                                color: Color(0xFF9AA7BA),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SearchField extends StatelessWidget {
  const _SearchField({required this.onChanged});

  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: ClinicianUiColors.surface,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0A172033),
            blurRadius: 16,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: TextField(
        onChanged: onChanged,
        textInputAction: TextInputAction.search,
        decoration: InputDecoration(
          hintText: '검사명 검색',
          hintStyle: const TextStyle(color: Color(0xFF9AA2B1)),
          prefixIcon: const Icon(
            Icons.search_rounded,
            color: ClinicianUiColors.mutedText,
          ),
          filled: true,
          fillColor: ClinicianUiColors.surface,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 14,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: ClinicianUiColors.border),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: ClinicianUiColors.border),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(
              color: ClinicianUiColors.primary,
              width: 1.5,
            ),
          ),
        ),
      ),
    );
  }
}

String _formatDate(DateTime? value) {
  if (value == null) return '-';
  final local = value.toLocal();
  return '${local.year}.${local.month.toString().padLeft(2, '0')}.${local.day.toString().padLeft(2, '0')}';
}

ClinicianStatusTone _statusTone(String status) => switch (status) {
  'FINAL' || 'CORRECTED' => ClinicianStatusTone.success,
  'PRELIMINARY' || 'IN_PROGRESS' => ClinicianStatusTone.info,
  'CANCELLED' => ClinicianStatusTone.danger,
  _ => ClinicianStatusTone.neutral,
};

ClinicianStatusTone _interpretationTone(String interpretation) =>
    switch (interpretation) {
      'NORMAL' => ClinicianStatusTone.success,
      'CRITICAL' || 'ABNORMAL' => ClinicianStatusTone.danger,
      'HIGH' || 'LOW' => ClinicianStatusTone.warning,
      _ => ClinicianStatusTone.neutral,
    };
