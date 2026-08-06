import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_model.dart';
import 'package:brainon_mobile/features/clinician/clinical_records/clinician_record_repository.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_model.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianRecordCreateScreen extends ConsumerStatefulWidget {
  const ClinicianRecordCreateScreen({this.record, super.key});
  final ClinicianRecord? record;

  @override
  ConsumerState<ClinicianRecordCreateScreen> createState() =>
      _ClinicianRecordCreateScreenState();
}

class _ClinicianRecordCreateScreenState
    extends ConsumerState<ClinicianRecordCreateScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _chiefComplaint;
  late final TextEditingController _assessment;
  late final TextEditingController _subjective;
  late final TextEditingController _objective;
  late final TextEditingController _plan;
  late final TextEditingController _summary;
  ClinicianPatient? _patient;
  late DateTime _recordedAt;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    final record = widget.record;
    _recordedAt = record?.recordedAt ?? DateTime.now();
    _chiefComplaint = TextEditingController(text: record?.chiefComplaint);
    _assessment = TextEditingController(text: record?.assessment);
    _subjective = TextEditingController(text: record?.subjective);
    _objective = TextEditingController(text: record?.objective);
    _plan = TextEditingController(text: record?.plan);
    _summary = TextEditingController(text: record?.patientVisibleSummary);
  }

  @override
  void dispose() {
    _chiefComplaint.dispose();
    _assessment.dispose();
    _subjective.dispose();
    _objective.dispose();
    _plan.dispose();
    _summary.dispose();
    super.dispose();
  }

  Future<void> _selectDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: _recordedAt,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (date != null) {
      setState(() {
        _recordedAt = DateTime(
          date.year,
          date.month,
          date.day,
          _recordedAt.hour,
          _recordedAt.minute,
        );
      });
    }
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    final patientId = _patient?.id ?? widget.record?.patientId ?? '';
    if (patientId.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('환자를 선택해 주세요.')));
      return;
    }
    setState(() => _saving = true);
    try {
      await ref
          .read(clinicianRecordRepositoryProvider)
          .save(
            ClinicianRecordInput(
              patientId: patientId,
              recordedAt: _recordedAt,
              chiefComplaint: _chiefComplaint.text.trim(),
              subjective: _subjective.text.trim(),
              objective: _objective.text.trim(),
              assessment: _assessment.text.trim(),
              plan: _plan.text.trim(),
              patientVisibleSummary: _summary.text.trim(),
            ),
          );
      if (mounted) Navigator.of(context).pop(true);
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final patients = ref.watch(clinicianPatientsProvider);
    final editing = widget.record != null;
    return ClinicianDetailScaffold(
      title: editing ? '진료 기록 수정' : '새 진료 기록 작성',
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
          children: [
            const _FieldLabel('환자'),
            if (editing)
              _ReadOnlyField(
                value:
                    '${widget.record!.patientName} (${widget.record!.patientNumber})',
              )
            else
              patients.when(
                loading: () => const LinearProgressIndicator(),
                error: (_, _) => const Text('환자 목록을 불러오지 못했습니다.'),
                data: (items) => DropdownButtonFormField<ClinicianPatient>(
                  initialValue: _patient,
                  hint: const Text('환자명을 검색하세요'),
                  items: items
                      .map(
                        (patient) => DropdownMenuItem(
                          value: patient,
                          child: Text(
                            '${patient.name} (${patient.registrationNumber})',
                          ),
                        ),
                      )
                      .toList(),
                  onChanged: (value) => setState(() => _patient = value),
                  validator: (value) => value == null ? '환자를 선택해 주세요.' : null,
                  decoration: _decoration(),
                ),
              ),
            const SizedBox(height: 14),
            const _FieldLabel('진료일'),
            InkWell(
              onTap: _selectDate,
              child: _ReadOnlyField(
                value:
                    '${_recordedAt.year}.${_recordedAt.month.toString().padLeft(2, '0')}.${_recordedAt.day.toString().padLeft(2, '0')}',
                icon: Icons.calendar_month_outlined,
              ),
            ),
            const SizedBox(height: 14),
            _RecordField(
              label: '주증상',
              controller: _chiefComplaint,
              isRequired: true,
            ),
            _RecordField(
              label: '진단명',
              controller: _assessment,
              isRequired: true,
            ),
            _RecordField(label: '진료 내용', controller: _subjective, maxLines: 3),
            _RecordField(
              label: '검사 및 관찰 내용',
              controller: _objective,
              maxLines: 3,
            ),
            _RecordField(label: '의사 소견', controller: _plan, maxLines: 3),
            _RecordField(label: '추가 메모', controller: _summary, maxLines: 3),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _saving
                        ? null
                        : () => Navigator.of(context).pop(false),
                    child: const Text('취소'),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: FilledButton(
                    onPressed: _saving ? null : _save,
                    child: _saving
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Text('저장'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _FieldLabel extends StatelessWidget {
  const _FieldLabel(this.value);
  final String value;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 7),
    child: Text(value, style: const TextStyle(fontWeight: FontWeight.w700)),
  );
}

class _RecordField extends StatelessWidget {
  const _RecordField({
    required this.label,
    required this.controller,
    this.maxLines = 1,
    this.isRequired = false,
  });
  final String label;
  final TextEditingController controller;
  final int maxLines;
  final bool isRequired;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 14),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _FieldLabel(label),
        TextFormField(
          controller: controller,
          maxLines: maxLines,
          validator: isRequired
              ? (value) =>
                    (value?.trim().isEmpty ?? true) ? '$label을 입력해 주세요.' : null
              : null,
          decoration: _decoration(hint: '$label을 입력하세요'),
        ),
      ],
    ),
  );
}

class _ReadOnlyField extends StatelessWidget {
  const _ReadOnlyField({required this.value, this.icon});
  final String value;
  final IconData? icon;
  @override
  Widget build(BuildContext context) => InputDecorator(
    decoration: _decoration(suffixIcon: icon == null ? null : Icon(icon)),
    child: Text(value),
  );
}

InputDecoration _decoration({String? hint, Widget? suffixIcon}) =>
    InputDecoration(
      hintText: hint,
      suffixIcon: suffixIcon,
      filled: true,
      fillColor: Colors.white,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: Color(0xFFE5EAF2)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: Color(0xFFE5EAF2)),
      ),
    );
