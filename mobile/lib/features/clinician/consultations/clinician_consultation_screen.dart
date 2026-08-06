import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_model.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_tab_header.dart';
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
    return ColoredBox(
      color: const Color(0xFFF6F8FC),
      child: SafeArea(
        bottom: false,
        child: Stack(
          children: [
            Column(
              children: [
                ClinicianTabHeader(
                  title: '협진 요청',
                  onOpenDrawer: widget.onOpenDrawer,
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 8, 20, 12),
                  child: Row(
                    children: [
                      for (final item in const [
                        ('all', '전체'),
                        ('received', '받은 협진'),
                        ('sent', '요청한 협진'),
                      ]) ...[
                        ChoiceChip(
                          label: Text(item.$2),
                          selected: box == item.$1,
                          onSelected: (_) => setState(() => box = item.$1),
                        ),
                        const SizedBox(width: 8),
                      ],
                    ],
                  ),
                ),
                Expanded(
                  child: value.when(
                    loading: () =>
                        const Center(child: CircularProgressIndicator()),
                    error: (_, _) => Center(
                      child: FilledButton(
                        onPressed: () =>
                            ref.invalidate(clinicianConsultationsProvider(box)),
                        child: const Text('다시 시도'),
                      ),
                    ),
                    data: (items) {
                    if (items.isEmpty) {
                      return const Center(child: Text('해당하는 협진 요청이 없습니다.'));
                    }
                      return RefreshIndicator(
                        onRefresh: () => ref.refresh(
                          clinicianConsultationsProvider(box).future,
                        ),
                        child: ListView.builder(
                          padding: const EdgeInsets.fromLTRB(20, 6, 20, 90),
                          itemCount: items.length,
                          itemBuilder: (context, index) => _Card(
                            item: items[index],
                            onTap: () => context.pushNamed(
                              RouteNames.clinicianConsultationDetail,
                              pathParameters: {
                                'consultationId': items[index].id,
                              },
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
            Positioned(
              right: 20,
              bottom: 20,
              child: FloatingActionButton(
                heroTag: 'new-consultation',
                onPressed: () =>
                    context.pushNamed(RouteNames.clinicianConsultationCreate),
                child: const Icon(Icons.add),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Card extends StatelessWidget {
  const _Card({required this.item, required this.onTap});
  final ClinicianConsultation item;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) {
    final color = switch (item.status) {
      'REQUESTED' => Colors.red,
      'IN_PROGRESS' => Colors.blue,
      'COMPLETED' => Colors.green,
      _ => Colors.grey,
    };
    final counterpart = item.isReceived ? item.requester : item.consultant;
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      counterpart.name,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                  _Badge(item.statusLabel, color),
                ],
              ),
              Text(
                '${counterpart.departmentName} · ${item.patientName}',
                style: const TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 10),
              Text(
                item.subject,
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 4),
              Text(item.question, maxLines: 2, overflow: TextOverflow.ellipsis),
            ],
          ),
        ),
      ),
    );
  }
}

class _Badge extends StatelessWidget {
  const _Badge(this.label, this.color);
  final String label;
  final Color color;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
    decoration: BoxDecoration(
      color: color.withValues(alpha: .1),
      borderRadius: BorderRadius.circular(10),
    ),
    child: Text(
      label,
      style: TextStyle(color: color, fontWeight: FontWeight.w700),
    ),
  );
}
