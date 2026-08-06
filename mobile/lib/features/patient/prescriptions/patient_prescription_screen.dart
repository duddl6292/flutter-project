import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/features/patient/prescriptions/patient_prescription_model.dart';
import 'package:brainon_mobile/features/patient/prescriptions/patient_prescription_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class PatientPrescriptionScreen extends ConsumerWidget {
  const PatientPrescriptionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final prescriptions = ref.watch(patientPrescriptionsProvider);
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        title: const Text('내 처방전'),
      ),
      body: prescriptions.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _ErrorState(
          error: error,
          onRetry: () => ref.invalidate(patientPrescriptionsProvider),
        ),
        data: (items) {
          if (items.isEmpty) {
            return const Center(child: Text('처방전이 없습니다.'));
          }
          return RefreshIndicator(
            onRefresh: () => ref.refresh(patientPrescriptionsProvider.future),
            child: ListView.separated(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(20),
              itemCount: items.length,
              separatorBuilder: (_, _) => const SizedBox(height: 12),
              itemBuilder: (context, index) =>
                  _PrescriptionCard(prescription: items[index]),
            ),
          );
        },
      ),
    );
  }
}

class _PrescriptionCard extends StatelessWidget {
  const _PrescriptionCard({required this.prescription});

  final PatientPrescription prescription;

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
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    prescription.hospitalName.isEmpty
                        ? '처방 정보'
                        : prescription.hospitalName,
                    style: const TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                _StatusBadge(
                  label: prescription.statusLabel.isEmpty
                      ? prescription.status
                      : prescription.statusLabel,
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              [
                if (prescription.prescribedAt != null)
                  _formatDate(prescription.prescribedAt!),
                if (prescription.clinicianName.isNotEmpty)
                  '담당 의료진 ${prescription.clinicianName}',
              ].join(' · '),
              style: const TextStyle(color: Color(0xFF6B7280)),
            ),
            if (prescription.items.isNotEmpty) ...[
              const SizedBox(height: 12),
              const Divider(height: 1),
              const SizedBox(height: 12),
              for (final item in prescription.items)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Text(
                          item.medicineName,
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                      ),
                      Text(
                        '${item.dosage}${item.doseUnit} · ${item.frequency}',
                        style: const TextStyle(color: Color(0xFF6B7280)),
                      ),
                    ],
                  ),
                ),
            ],
            if (prescription.notes.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                prescription.notes,
                style: const TextStyle(color: Color(0xFF4B5563)),
              ),
            ],
          ],
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
            unauthorized ? '로그인이 만료되었습니다. 다시 로그인해주세요.' : '처방전을 불러오지 못했습니다.',
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
