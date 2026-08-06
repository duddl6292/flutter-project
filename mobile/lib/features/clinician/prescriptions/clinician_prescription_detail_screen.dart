import 'package:brainon_mobile/features/clinician/prescriptions/clinician_prescription_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianPrescriptionDetailScreen extends ConsumerWidget {
  const ClinicianPrescriptionDetailScreen({
    required this.prescriptionId,
    super.key,
  });
  final String prescriptionId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final value = ref.watch(
      clinicianPrescriptionDetailProvider(prescriptionId),
    );
    return ClinicianDetailScaffold(
      title: '처방 상세',
      body: value.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(
          child: FilledButton(
            onPressed: () => ref.invalidate(
              clinicianPrescriptionDetailProvider(prescriptionId),
            ),
            child: const Text('다시 시도'),
          ),
        ),
        data: (item) => ListView(
          padding: const EdgeInsets.all(20),
          children: [
            _line('환자', item.patientName),
            _line('환자 등록번호', item.patientNumber),
            _line('담당 의료진', item.clinicianName),
            _line(
              '상태',
              item.statusLabel.isEmpty ? item.status : item.statusLabel,
            ),
            if (item.notes.isNotEmpty) _line('메모', item.notes),
            const SizedBox(height: 16),
            const Text(
              '처방 약품',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 8),
            if (item.items.isEmpty) const Text('처방 약품이 없습니다.'),
            for (final medicine in item.items)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        medicine.medicineName,
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                      Text(
                        '${medicine.dosage}${medicine.doseUnit} · ${medicine.frequency}',
                      ),
                      if (medicine.route.isNotEmpty)
                        Text('투여 경로: ${medicine.route}'),
                      if (medicine.instructions.isNotEmpty)
                        Text('복약 안내: ${medicine.instructions}'),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _line(String label, String value) => value.isEmpty
      ? const SizedBox.shrink()
      : Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(width: 110, child: Text(label)),
              Expanded(
                child: Text(
                  value,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
        );
}
