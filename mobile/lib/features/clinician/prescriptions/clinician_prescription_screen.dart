import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/prescriptions/clinician_prescription_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class ClinicianPrescriptionScreen extends ConsumerStatefulWidget {
  const ClinicianPrescriptionScreen({super.key});
  @override
  ConsumerState<ClinicianPrescriptionScreen> createState() =>
      _PrescriptionState();
}

class _PrescriptionState extends ConsumerState<ClinicianPrescriptionScreen> {
  String query = '';
  String? status;

  @override
  Widget build(BuildContext context) {
    final data = ref.watch(clinicianPrescriptionsProvider);
    return ClinicianDetailScaffold(
      title: '처방 관리',
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    onChanged: (value) => setState(() => query = value),
                    decoration: const InputDecoration(
                      hintText: '환자 검색',
                      prefixIcon: Icon(Icons.search),
                      filled: true,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                FilledButton.icon(
                  onPressed: () =>
                      context.pushNamed(RouteNames.clinicianPrescriptionCreate),
                  icon: const Icon(Icons.add),
                  label: const Text('새 처방'),
                ),
              ],
            ),
          ),
          Wrap(
            spacing: 8,
            children: [
              for (final entry in const [
                (null, '전체'),
                ('ACTIVE', '처방 중'),
                ('DRAFT', '작성 중'),
              ])
                ChoiceChip(
                  label: Text(entry.$2),
                  selected: status == entry.$1,
                  onSelected: (_) => setState(() => status = entry.$1),
                ),
            ],
          ),
          Expanded(
            child: data.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(
                child: FilledButton(
                  onPressed: () =>
                      ref.invalidate(clinicianPrescriptionsProvider),
                  child: const Text('다시 시도'),
                ),
              ),
              data: (items) {
                final list = items
                    .where(
                      (item) =>
                          (status == null || item.status == status) &&
                          item.patientName.contains(query),
                    )
                    .toList();
                if (list.isEmpty) {
                  return const Center(child: Text('처방 내역이 없습니다.'));
                }
                return RefreshIndicator(
                  onRefresh: () =>
                      ref.refresh(clinicianPrescriptionsProvider.future),
                  child: ListView.builder(
                    padding: const EdgeInsets.all(20),
                    itemCount: list.length,
                    itemBuilder: (context, index) {
                      final item = list[index];
                      final medicines = item.items
                          .map((e) => e.medicineName)
                          .where((e) => e.isNotEmpty)
                          .join(', ');
                      return Card(
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(16),
                          onTap: () => context.pushNamed(
                            RouteNames.clinicianPrescriptionDetail,
                            pathParameters: {'prescriptionId': item.id},
                          ),
                          title: Text(
                            item.patientName,
                            style: const TextStyle(fontWeight: FontWeight.w800),
                          ),
                          subtitle: Text(
                            medicines.isEmpty ? '처방 약품 없음' : medicines,
                          ),
                          trailing: Text(
                            item.statusLabel.isEmpty
                                ? item.status
                                : item.statusLabel,
                          ),
                        ),
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
