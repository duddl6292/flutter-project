import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_create_screen.dart';
import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_model.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';

class ClinicianRecordDetailScreen extends StatelessWidget {
  const ClinicianRecordDetailScreen({required this.record, super.key});
  final ClinicianRecord record;

  @override
  Widget build(BuildContext context) {
    final recordedAt = record.recordedAt;
    final dateText = recordedAt == null
        ? '-'
        : '${recordedAt.year}.${recordedAt.month.toString().padLeft(2, '0')}.${recordedAt.day.toString().padLeft(2, '0')} '
              '${recordedAt.hour.toString().padLeft(2, '0')}:${recordedAt.minute.toString().padLeft(2, '0')}';
    final sex = switch (record.patientSex) {
      'M' => '남',
      'F' => '여',
      _ => '미상',
    };
    return ClinicianDetailScaffold(
      title: '진료 기록 상세',
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
        children: [
          Row(
            children: [
              const CircleAvatar(
                radius: 30,
                backgroundColor: Color(0xFFE5E7EB),
                child: Icon(
                  Icons.person_rounded,
                  size: 38,
                  color: Color(0xFF6B7280),
                ),
              ),
              const SizedBox(width: 14),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    record.patientName,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  Text(
                    '$sex / ${record.patientAge ?? '-'}세',
                    style: const TextStyle(color: Color(0xFF6B7280)),
                  ),
                  Text(
                    record.patientNumber,
                    style: const TextStyle(color: Color(0xFF6B7280)),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 18),
          _DetailSection(label: '진료일', value: dateText),
          _DetailSection(label: '주증상', value: record.chiefComplaint),
          _DetailSection(label: '진단명', value: record.assessment),
          _DetailSection(
            label: '진료 내용',
            value: '${record.subjective}\n${record.objective}',
          ),
          _DetailSection(label: '의사 소견', value: record.plan),
          _DetailSection(label: '추가 메모', value: record.patientVisibleSummary),
          if (record.attachmentName != null)
            _DetailSection(
              label: '첨부 파일 (1)',
              value: record.attachmentName!,
              icon: Icons.picture_as_pdf_outlined,
            ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => Navigator.of(context).push<void>(
                    MaterialPageRoute(
                      builder: (_) =>
                          ClinicianRecordCreateScreen(record: record),
                    ),
                  ),
                  child: const Text('수정'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: FilledButton(
                  onPressed: null,
                  child: const Text('처방 작성'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _DetailSection extends StatelessWidget {
  const _DetailSection({required this.label, required this.value, this.icon});
  final String label;
  final String value;
  final IconData? icon;
  @override
  Widget build(BuildContext context) => Container(
    margin: const EdgeInsets.only(bottom: 8),
    padding: const EdgeInsets.all(14),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(14),
      border: Border.all(color: const Color(0xFFE5EAF2)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 6),
        Row(
          children: [
            if (icon != null) ...[
              Icon(icon, color: const Color(0xFFE34255)),
              const SizedBox(width: 8),
            ],
            Expanded(
              child: Text(
                value.isEmpty ? '-' : value,
                style: const TextStyle(height: 1.45),
              ),
            ),
          ],
        ),
      ],
    ),
  );
}
