import 'package:brainon_mobile/features/clinician/prescriptions/clinician_prescription_model.dart';
import 'package:brainon_mobile/features/clinician/prescriptions/clinician_prescription_provider.dart';
import 'package:brainon_mobile/features/clinician/prescriptions/clinician_prescription_repository.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianPrescriptionCreateScreen extends ConsumerStatefulWidget {
  const ClinicianPrescriptionCreateScreen({super.key});
  @override
  ConsumerState<ClinicianPrescriptionCreateScreen> createState() =>
      _CreateState();
}

class _CreateState extends ConsumerState<ClinicianPrescriptionCreateScreen> {
  final _formKey = GlobalKey<FormState>();
  final _notes = TextEditingController();
  final List<_MedicationFields> _medications = [_MedicationFields()];
  PrescriptionContext? _context;
  String _status = 'ACTIVE';
  bool _saving = false;

  @override
  void dispose() {
    _notes.dispose();
    for (final fields in _medications) {
      fields.dispose();
    }
    super.dispose();
  }

  Future<void> _submit() async {
    if (_saving || !_formKey.currentState!.validate() || _context == null) {
      return;
    }
    if (_medications.any(
      (item) => item.endDate != null && item.endDate!.isBefore(item.startDate),
    )) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('복용 종료일은 시작일보다 빠를 수 없습니다.')));
      return;
    }
    setState(() => _saving = true);
    try {
      final input = PrescriptionCreateInput(
        clinicalRecordId: _context!.clinicalRecordId,
        status: _status,
        notes: _notes.text.trim(),
        items: _medications.map((e) => e.toInput()).toList(),
      );
      await ref.read(clinicianPrescriptionRepositoryProvider).create(input);
      ref.invalidate(clinicianPrescriptionsProvider);
      if (mounted) {
        Navigator.of(context).pop();
      }
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('처방 발행에 실패했습니다: $error')));
      }
    } finally {
      if (mounted) {
        setState(() => _saving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final contexts = ref.watch(prescriptionContextsProvider);
    return ClinicianDetailScaffold(
      title: '새 처방',
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            contexts.when(
              loading: () => const LinearProgressIndicator(),
              error: (_, _) => FilledButton(
                onPressed: () => ref.invalidate(prescriptionContextsProvider),
                child: const Text('진료 기록 다시 불러오기'),
              ),
              data: (items) => DropdownButtonFormField<PrescriptionContext>(
                initialValue: _context,
                decoration: const InputDecoration(labelText: '환자 / 진료 기록'),
                items: items
                    .map(
                      (item) => DropdownMenuItem(
                        value: item,
                        child: Text(
                          '${item.patientName} (${item.patientNumber})',
                        ),
                      ),
                    )
                    .toList(),
                onChanged: (value) => setState(() => _context = value),
                validator: (value) =>
                    value == null ? '처방할 진료 기록을 선택해 주세요.' : null,
              ),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: _status,
              decoration: const InputDecoration(labelText: '처방 상태'),
              items: const [
                DropdownMenuItem(value: 'ACTIVE', child: Text('처방 중')),
                DropdownMenuItem(value: 'DRAFT', child: Text('작성 중')),
              ],
              onChanged: (value) => setState(() => _status = value ?? 'ACTIVE'),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _notes,
              decoration: const InputDecoration(labelText: '메모'),
              maxLines: 3,
            ),
            const SizedBox(height: 20),
            for (var index = 0; index < _medications.length; index++)
              _MedicationCard(
                fields: _medications[index],
                index: index,
                removable: _medications.length > 1,
                onRemove: () =>
                    setState(() => _medications.removeAt(index).dispose()),
              ),
            OutlinedButton.icon(
              onPressed: () =>
                  setState(() => _medications.add(_MedicationFields())),
              icon: const Icon(Icons.add),
              label: const Text('약품 추가'),
            ),
            const SizedBox(height: 20),
            FilledButton(
              onPressed: _saving ? null : _submit,
              child: Text(_saving ? '발행 중...' : '처방 발행'),
            ),
          ],
        ),
      ),
    );
  }
}

class _MedicationCard extends StatelessWidget {
  const _MedicationCard({
    required this.fields,
    required this.index,
    required this.removable,
    required this.onRemove,
  });
  final _MedicationFields fields;
  final int index;
  final bool removable;
  final VoidCallback onRemove;

  @override
  Widget build(BuildContext context) => Card(
    margin: const EdgeInsets.only(bottom: 12),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  '약품 ${index + 1}',
                  style: const TextStyle(fontWeight: FontWeight.w800),
                ),
              ),
              if (removable)
                IconButton(
                  onPressed: onRemove,
                  icon: const Icon(Icons.delete_outline),
                ),
            ],
          ),
          _required(fields.name, '약품명'),
          Row(
            children: [
              Expanded(child: _required(fields.dosage, '용량', number: true)),
              const SizedBox(width: 8),
              Expanded(child: _required(fields.unit, '단위')),
            ],
          ),
          _required(fields.frequency, '복용 빈도'),
          TextFormField(
            controller: fields.route,
            decoration: const InputDecoration(labelText: '투여 경로'),
          ),
          TextFormField(
            controller: fields.instructions,
            decoration: const InputDecoration(labelText: '복약 안내'),
          ),
          Row(
            children: [
              Expanded(
                child: _DateField(
                  label: '시작일',
                  value: fields.startDate,
                  onChanged: (v) => fields.startDate = v,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _DateField(
                  label: '종료일',
                  value: fields.endDate,
                  onChanged: (v) => fields.endDate = v,
                ),
              ),
            ],
          ),
        ],
      ),
    ),
  );

  Widget _required(
    TextEditingController controller,
    String label, {
    bool number = false,
  }) => TextFormField(
    controller: controller,
    decoration: InputDecoration(labelText: label),
    keyboardType: number
        ? const TextInputType.numberWithOptions(decimal: true)
        : null,
    validator: (value) {
      if (value == null || value.trim().isEmpty) {
        return '$label을(를) 입력해 주세요.';
      }
      if (number && (double.tryParse(value) ?? 0) <= 0) {
        return '0보다 큰 값을 입력해 주세요.';
      }
      return null;
    },
  );
}

class _DateField extends StatefulWidget {
  const _DateField({
    required this.label,
    required this.value,
    required this.onChanged,
  });
  final String label;
  final DateTime? value;
  final ValueChanged<DateTime> onChanged;
  @override
  State<_DateField> createState() => _DateFieldState();
}

class _DateFieldState extends State<_DateField> {
  late DateTime? value = widget.value;
  @override
  Widget build(BuildContext context) => InkWell(
    onTap: () async {
      final selected = await showDatePicker(
        context: context,
        firstDate: DateTime(2020),
        lastDate: DateTime(2100),
        initialDate: value ?? DateTime.now(),
      );
      if (selected != null) {
        setState(() => value = selected);
        widget.onChanged(selected);
      }
    },
    child: InputDecorator(
      decoration: InputDecoration(labelText: widget.label),
      child: Text(
        value == null ? '선택' : '${value!.year}-${value!.month}-${value!.day}',
      ),
    ),
  );
}

class _MedicationFields {
  final name = TextEditingController();
  final dosage = TextEditingController(text: '1');
  final unit = TextEditingController();
  final frequency = TextEditingController(text: '하루 1회');
  final route = TextEditingController(text: '경구');
  final instructions = TextEditingController();
  DateTime startDate = DateTime.now();
  DateTime? endDate;

  PrescriptionItemInput toInput() => PrescriptionItemInput(
    medicineName: name.text.trim(),
    dosage: dosage.text.trim(),
    doseUnit: unit.text.trim(),
    frequency: frequency.text.trim(),
    route: route.text.trim(),
    instructions: instructions.text.trim(),
    startDate: startDate,
    endDate: endDate,
  );
  void dispose() {
    name.dispose();
    dosage.dispose();
    unit.dispose();
    frequency.dispose();
    route.dispose();
    instructions.dispose();
  }
}
