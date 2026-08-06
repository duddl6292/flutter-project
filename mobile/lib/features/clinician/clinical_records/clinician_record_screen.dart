import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_create_screen.dart';
import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_detail_screen.dart';
import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_model.dart';
import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianRecordScreen extends ConsumerStatefulWidget {
  const ClinicianRecordScreen({super.key});
  @override
  ConsumerState<ClinicianRecordScreen> createState() => _RecordState();
}

class _RecordState extends ConsumerState<ClinicianRecordScreen> {
  String query = '';
  bool todayOnly = false;

  Future<void> _openCreate() async {
    final saved = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => const ClinicianRecordCreateScreen()),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('진료 기록이 저장되었습니다.')));
      ref.invalidate(clinicianRecordsProvider);
    }
  }

  @override
  Widget build(BuildContext context) {
    final data = ref.watch(clinicianRecordsProvider);
    return ClinicianDetailScaffold(
      title: '진료 기록',
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 10, 20, 8),
            child: TextField(
              onChanged: (value) => setState(() => query = value.trim()),
              decoration: InputDecoration(
                prefixIcon: const Icon(Icons.search_rounded),
                hintText: '환자명, 주증상 검색',
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                  borderSide: const BorderSide(color: Color(0xFFE5EAF2)),
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Align(
              alignment: Alignment.centerLeft,
              child: FilterChip(
                avatar: todayOnly ? const Icon(Icons.check, size: 16) : null,
                label: const Text('오늘 진료'),
                selected: todayOnly,
                onSelected: (value) => setState(() => todayOnly = value),
              ),
            ),
          ),
          Expanded(
            child: data.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (_, _) => Center(
                child: FilledButton(
                  onPressed: () => ref.invalidate(clinicianRecordsProvider),
                  child: const Text('다시 시도'),
                ),
              ),
              data: (items) {
                final now = DateTime.now();
                final records = items.where((record) {
                  final matchesQuery =
                      '${record.patientName}${record.chiefComplaint}${record.assessment}'
                          .toLowerCase()
                          .contains(query.toLowerCase());
                  final date = record.recordedAt;
                  final matchesDate =
                      !todayOnly ||
                      (date != null &&
                          date.year == now.year &&
                          date.month == now.month &&
                          date.day == now.day);
                  return matchesQuery && matchesDate;
                }).toList();
                return ListView(
                  padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
                  children: [
                    if (records.isEmpty)
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 60),
                        child: Center(child: Text('진료 기록이 없습니다.')),
                      ),
                    ...records.map(
                      (record) => _RecordCard(
                        record: record,
                        onTap: () => Navigator.of(context).push<void>(
                          MaterialPageRoute(
                            builder: (_) =>
                                ClinicianRecordDetailScreen(record: record),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    OutlinedButton.icon(
                      onPressed: _openCreate,
                      icon: const Icon(Icons.add_rounded),
                      label: const Text('새 진료 기록 작성'),
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size.fromHeight(52),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _RecordCard extends StatelessWidget {
  const _RecordCard({required this.record, required this.onTap});
  final ClinicianRecord record;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final completed = record.status == ClinicianRecordStatus.completed;
    return Card(
      elevation: 0,
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: Color(0xFFE5EAF2)),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      record.patientName,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                  Text(
                    completed ? '작성 완료' : '작성 중',
                    style: TextStyle(
                      color: completed
                          ? const Color(0xFF64748B)
                          : const Color(0xFF28669E),
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                record.assessment.isEmpty
                    ? record.chiefComplaint
                    : record.assessment,
              ),
              const SizedBox(height: 4),
              Text(
                record.summary,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: Color(0xFF6B7280), height: 1.4),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
