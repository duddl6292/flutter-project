import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_model.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class ClinicianConsultationScreen extends ConsumerStatefulWidget {
  const ClinicianConsultationScreen({required this.onOpenDrawer, super.key});

  final VoidCallback onOpenDrawer;

  @override
  ConsumerState<ClinicianConsultationScreen> createState() => _State();
}

class _State extends ConsumerState<ClinicianConsultationScreen> {
  String box = 'all';

  @override
  Widget build(BuildContext context) {
    final value = ref.watch(clinicianConsultationsProvider(box));
    return ClinicianPageScaffold(
      title: '협진 요청',
      onOpenDrawer: widget.onOpenDrawer,
      floatingActionButton: FloatingActionButton(
        heroTag: 'new-consultation',
        backgroundColor: ClinicianUiColors.primary,
        foregroundColor: Colors.white,
        onPressed: () =>
            context.pushNamed(RouteNames.clinicianConsultationCreate),
        child: const Icon(Icons.add_rounded),
      ),
      body: Column(
        children: [
          _FilterBar(
            selected: box,
            onSelected: (value) => setState(() => box = value),
          ),
          Expanded(
            child: value.when(
              loading: () => const ClinicianLoadingView(),
              error: (_, _) => ClinicianErrorView(
                message: '협진 요청을 불러오지 못했습니다.',
                onRetry: () =>
                    ref.invalidate(clinicianConsultationsProvider(box)),
              ),
              data: (items) {
                if (items.isEmpty) {
                  return const ClinicianEmptyView(
                    message: '해당하는 협진 요청이 없습니다.',
                    icon: Icons.forum_outlined,
                  );
                }
                return RefreshIndicator(
                  color: ClinicianUiColors.primary,
                  onRefresh: () =>
                      ref.refresh(clinicianConsultationsProvider(box).future),
                  child: ListView.builder(
                    padding: const EdgeInsets.fromLTRB(20, 6, 20, 90),
                    itemCount: items.length,
                    itemBuilder: (context, index) {
                      final item = items[index];
                      return _ConsultationCard(
                        item: item,
                        onTap: () async {
                          await context.pushNamed(
                            RouteNames.clinicianConsultationDetail,
                            pathParameters: {'consultationId': item.id},
                          );
                          if (!context.mounted) return;
                          ref.invalidate(clinicianConsultationsProvider);
                        },
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _FilterBar extends StatelessWidget {
  const _FilterBar({required this.selected, required this.onSelected});

  final String selected;
  final ValueChanged<String> onSelected;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 14),
      child: Row(
        children: [
          for (final item in const [
            ('all', '전체'),
            ('received', '받은 협진'),
            ('sent', '요청한 협진'),
          ]) ...[
            ChoiceChip(
              label: Text(item.$2),
              selected: selected == item.$1,
              showCheckmark: selected == item.$1,
              checkmarkColor: ClinicianUiColors.primary,
              selectedColor: const Color(0xFFE3EDFF),
              backgroundColor: Colors.white,
              side: BorderSide(
                color: selected == item.$1
                    ? const Color(0xFFB9D0F7)
                    : ClinicianUiColors.border,
              ),
              labelStyle: TextStyle(
                color: selected == item.$1
                    ? ClinicianUiColors.primary
                    : ClinicianUiColors.mutedText,
                fontWeight: selected == item.$1
                    ? FontWeight.w700
                    : FontWeight.w600,
              ),
              onSelected: (_) => onSelected(item.$1),
            ),
            const SizedBox(width: 8),
          ],
        ],
      ),
    );
  }
}

class _ConsultationCard extends StatelessWidget {
  const _ConsultationCard({required this.item, required this.onTap});

  final ClinicianConsultation item;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final counterpart = item.isReceived ? item.requester : item.consultant;
    final statusLabel = item.statusLabel.isEmpty
        ? item.status
        : item.statusLabel;
    final priorityLabel = item.priorityLabel.isEmpty
        ? item.priority
        : item.priorityLabel;

    return ClinicianListCard(
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: const BoxDecoration(
                  color: Color(0xFFEEF3FC),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.person_outline_rounded,
                  color: ClinicianUiColors.primary,
                  size: 22,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      counterpart.name.isEmpty ? '-' : counterpart.name,
                      style: const TextStyle(
                        color: ClinicianUiColors.text,
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      [
                        counterpart.departmentName,
                        item.patientName,
                      ].where((value) => value.isNotEmpty).join(' · '),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: ClinicianUiColors.mutedText,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              ClinicianStatusBadge(
                label: statusLabel,
                tone: _statusTone(item.status),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Text(
            item.subject.isEmpty ? '-' : item.subject,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: ClinicianUiColors.text,
              fontSize: 16,
              fontWeight: FontWeight.w800,
            ),
          ),
          if (item.question.isNotEmpty) ...[
            const SizedBox(height: 5),
            Text(
              item.question,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                color: Color(0xFF4D586A),
                fontSize: 13,
                height: 1.45,
              ),
            ),
          ],
          const SizedBox(height: 14),
          Row(
            children: [
              if (priorityLabel.isNotEmpty)
                ClinicianStatusBadge(
                  label: priorityLabel,
                  tone: _priorityTone(item.priority),
                ),
              if (item.unreadCount > 0) ...[
                const SizedBox(width: 8),
                ClinicianStatusBadge(
                  label: '읽지 않음 ${item.unreadCount}',
                  tone: ClinicianStatusTone.danger,
                ),
              ],
              const Spacer(),
              Text(
                _dateTime(item.createdAt),
                style: const TextStyle(color: Color(0xFF8B94A4), fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

ClinicianStatusTone _statusTone(String status) => switch (status) {
  'REQUESTED' => ClinicianStatusTone.danger,
  'IN_PROGRESS' => ClinicianStatusTone.info,
  'COMPLETED' => ClinicianStatusTone.success,
  'CANCELLED' => ClinicianStatusTone.neutral,
  _ => ClinicianStatusTone.neutral,
};

ClinicianStatusTone _priorityTone(String priority) => switch (priority) {
  'EMERGENCY' => ClinicianStatusTone.danger,
  'URGENT' => ClinicianStatusTone.warning,
  _ => ClinicianStatusTone.neutral,
};

String _dateTime(DateTime? value) {
  if (value == null) return '';
  final local = value.toLocal();
  final month = local.month.toString().padLeft(2, '0');
  final day = local.day.toString().padLeft(2, '0');
  final hour = local.hour.toString().padLeft(2, '0');
  final minute = local.minute.toString().padLeft(2, '0');
  return '$month.$day $hour:$minute';
}
