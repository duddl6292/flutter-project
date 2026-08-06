import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_model.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_provider.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_repository.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianConsultationCreateScreen extends ConsumerStatefulWidget {
  const ClinicianConsultationCreateScreen({super.key});
  @override
  ConsumerState<ClinicianConsultationCreateScreen> createState() => _State();
}

class _State extends ConsumerState<ClinicianConsultationCreateScreen> {
  final formKey = GlobalKey<FormState>();
  final subject = TextEditingController();
  final question = TextEditingController();
  ConsultationContext? selectedContext;
  ConsultationClinician? consultant;
  String priority = 'ROUTINE';
  DateTime? dueAt;
  bool saving = false;

  @override
  void dispose() {
    subject.dispose();
    question.dispose();
    super.dispose();
  }

  Future<void> submit() async {
    if (saving ||
        !formKey.currentState!.validate() ||
        selectedContext == null ||
        consultant == null) {
      return;
    }
    setState(() => saving = true);
    try {
      await ref
          .read(clinicianConsultationRepositoryProvider)
          .create(
            ConsultationCreateInput(
              encounterId: selectedContext!.encounterId,
              consultantId: consultant!.id,
              subject: subject.text.trim(),
              priority: priority,
              question: question.text.trim(),
              dueAt: dueAt,
            ),
          );
      ref.invalidate(clinicianConsultationsProvider);
      if (mounted) {
        Navigator.of(context).pop();
      }
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('협진 요청을 전송하지 못했습니다: $error')));
      }
    } finally {
      if (mounted) {
        setState(() => saving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final contexts = ref.watch(consultationContextsProvider);
    final clinicians = ref.watch(consultationCliniciansProvider);
    final myId = ref.watch(authProvider).user?.clinician?.id ?? '';
    return ClinicianDetailScaffold(
      title: '협진 요청 작성',
      body: Form(
        key: formKey,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            const Text(
              '환자 및 관련 진료 건',
              style: TextStyle(fontWeight: FontWeight.w800),
            ),
            contexts.when(
              loading: () => const LinearProgressIndicator(),
              error: (_, _) => OutlinedButton(
                onPressed: () => ref.invalidate(consultationContextsProvider),
                child: const Text('진료 건 다시 불러오기'),
              ),
              data: (items) => DropdownButtonFormField<ConsultationContext>(
                initialValue: selectedContext,
                items: items
                    .map(
                      (item) => DropdownMenuItem(
                        value: item,
                        child: Text(
                          '${item.patientName} · ${item.encounterNumber}',
                        ),
                      ),
                    )
                    .toList(),
                onChanged: (value) => setState(() => selectedContext = value),
                validator: (value) =>
                    value == null ? '환자 진료 건을 선택해 주세요.' : null,
              ),
            ),
            if (selectedContext != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  '${selectedContext!.departmentName} · 환자번호 ${selectedContext!.patientNumber}',
                ),
              ),
            const SizedBox(height: 18),
            const Text('요청 의료진', style: TextStyle(fontWeight: FontWeight.w800)),
            clinicians.when(
              loading: () => const LinearProgressIndicator(),
              error: (_, _) => OutlinedButton(
                onPressed: () => ref.invalidate(consultationCliniciansProvider),
                child: const Text('의료진 다시 불러오기'),
              ),
              data: (items) {
                final available = items
                    .where((item) => item.id != myId)
                    .toList();
                return DropdownButtonFormField<ConsultationClinician>(
                  initialValue: consultant,
                  items: available
                      .map(
                        (item) => DropdownMenuItem(
                          value: item,
                          child: Text('${item.name} · ${item.departmentName}'),
                        ),
                      )
                      .toList(),
                  onChanged: (value) => setState(() => consultant = value),
                  validator: (value) =>
                      value == null ? '협진 의료진을 선택해 주세요.' : null,
                );
              },
            ),
            if (consultant != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  '${consultant!.departmentName} · ${consultant!.hospitalName}',
                ),
              ),
            const SizedBox(height: 18),
            DropdownButtonFormField<String>(
              initialValue: priority,
              decoration: const InputDecoration(labelText: '긴급도'),
              items: const [
                DropdownMenuItem(value: 'ROUTINE', child: Text('일반')),
                DropdownMenuItem(value: 'URGENT', child: Text('긴급')),
                DropdownMenuItem(value: 'EMERGENCY', child: Text('응급')),
              ],
              onChanged: (value) =>
                  setState(() => priority = value ?? 'ROUTINE'),
            ),
            TextFormField(
              controller: subject,
              maxLength: 200,
              decoration: const InputDecoration(labelText: '협진 제목'),
              validator: requiredText,
            ),
            TextFormField(
              controller: question,
              maxLines: 6,
              decoration: const InputDecoration(labelText: '요청 사유'),
              validator: requiredText,
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: const Text('답변 희망일 (선택)'),
              subtitle: Text(dueAt == null ? '선택하지 않음' : dueAt.toString()),
              trailing: const Icon(Icons.calendar_month),
              onTap: pickDueAt,
            ),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: saving ? null : submit,
              child: Text(saving ? '요청 중...' : '요청 전송'),
            ),
          ],
        ),
      ),
    );
  }

  String? requiredText(String? value) =>
      value == null || value.trim().isEmpty ? '필수 항목입니다.' : null;
  Future<void> pickDueAt() async {
    final date = await showDatePicker(
      context: context,
      firstDate: DateTime.now().add(const Duration(days: 1)),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      initialDate: DateTime.now().add(const Duration(days: 1)),
    );
    if (date != null) {
      setState(() => dueAt = DateTime(date.year, date.month, date.day, 18));
    }
  }
}
