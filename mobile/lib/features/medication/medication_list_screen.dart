import 'package:brainon_mobile/features/medication/providers/medication_provider.dart';
import 'package:brainon_mobile/shared/models/medication.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class MedicationListScreen extends ConsumerWidget {
  const MedicationListScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final value = ref.watch(todayMedicationsProvider);
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FB),
      appBar: AppBar(title: const Text('복약 관리')),
      body: value.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(child: OutlinedButton.icon(
          onPressed: () => ref.invalidate(todayMedicationsProvider),
          icon: const Icon(Icons.refresh),
          label: const Text('복약 정보 다시 불러오기'),
        )),
        data: (items) => RefreshIndicator(
          onRefresh: () => ref.refresh(todayMedicationsProvider.future),
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(20),
            children: [
              Text(_todayLabel(), style: const TextStyle(fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              _Progress(items: items),
              const SizedBox(height: 18),
              if (items.isEmpty)
                const Padding(padding: EdgeInsets.only(top: 80), child: Center(child: Text('오늘 예정된 복약 일정이 없습니다.'))),
              for (final medication in items) _MedicationCard(medication: medication),
              if (items.isNotEmpty)
                const Padding(
                  padding: EdgeInsets.only(top: 8),
                  child: Text('복용 완료 여부는 병원에 등록된 실제 복약 기록을 표시합니다.', style: TextStyle(color: Colors.grey)),
                ),
            ],
          ),
        ),
      ),
    );
  }

  String _todayLabel() {
    final now = DateTime.now();
    return '${now.year}년 ${now.month}월 ${now.day}일';
  }
}

class _Progress extends StatelessWidget {
  const _Progress({required this.items});
  final List<Medication> items;
  @override
  Widget build(BuildContext context) {
    final completed = items.where((item) => item.completed).length;
    return Card(
      color: const Color(0xFFEFF6FF),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Text('${items.length}건 중 $completed건 복용 완료', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
      ),
    );
  }
}

class _MedicationCard extends StatelessWidget {
  const _MedicationCard({required this.medication});
  final Medication medication;
  @override
  Widget build(BuildContext context) {
    final time = '${medication.scheduledAt.hour.toString().padLeft(2, '0')}:${medication.scheduledAt.minute.toString().padLeft(2, '0')}';
    return Card(
      margin: const EdgeInsets.only(top: 12),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: Icon(medication.completed ? Icons.check_circle : Icons.medication_outlined, color: medication.completed ? Colors.green : Colors.blue),
        title: Text(medication.name, style: const TextStyle(fontWeight: FontWeight.w800)),
        subtitle: Text('$time · ${medication.dose}\n${medication.period}${medication.instruction.isEmpty ? '' : '\n${medication.instruction}'}'),
        trailing: Text(medication.completed ? '복용 완료' : '복용 예정', style: TextStyle(color: medication.completed ? Colors.green : Colors.grey)),
      ),
    );
  }
}
