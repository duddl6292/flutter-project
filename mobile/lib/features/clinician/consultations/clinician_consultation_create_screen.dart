import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_model.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_provider.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_repository.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_ui.dart';
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
      if (mounted) Navigator.of(context).pop();
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('협진 요청을 전송하지 못했습니다: $error')));
      }
    } finally {
      if (mounted) setState(() => saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final contexts = ref.watch(consultationContextsProvider);
    final clinicians = ref.watch(consultationCliniciansProvider);
    final myId = ref.watch(authProvider).user?.clinician?.id ?? '';

    return ClinicianDetailScaffold(
      title: '협진 요청 작성',
      body: ColoredBox(
        color: ClinicianUiColors.background,
        child: Form(
          key: formKey,
          child: ListView(
            keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
            children: [
              const Padding(
                padding: EdgeInsets.fromLTRB(2, 0, 2, 16),
                child: Text(
                  '환자 진료 건과 요청 의료진을 선택해 협진을 요청하세요.',
                  style: TextStyle(
                    color: ClinicianUiColors.mutedText,
                    fontSize: 14,
                    height: 1.45,
                  ),
                ),
              ),
              ClinicianSectionCard(
                title: '기본 정보',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const _RequiredLabel('환자 및 관련 진료 건'),
                    const SizedBox(height: 8),
                    contexts.when(
                      loading: () => const LinearProgressIndicator(
                        color: ClinicianUiColors.primary,
                      ),
                      error: (_, _) => _ReloadButton(
                        label: '진료 건 다시 불러오기',
                        onPressed: () =>
                            ref.invalidate(consultationContextsProvider),
                      ),
                      data: (items) => DropdownButtonFormField<ConsultationContext>(
                        initialValue: selectedContext,
                        isExpanded: true,
                        decoration: _inputDecoration(
                          hintText: '환자 진료 건을 선택하세요',
                          prefixIcon: Icons.assignment_ind_outlined,
                        ),
                        items: items
                            .map(
                              (item) => DropdownMenuItem(
                                value: item,
                                child: Text(
                                  '${item.patientName} · ${item.encounterNumber}',
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            )
                            .toList(),
                        onChanged: saving
                            ? null
                            : (value) =>
                                  setState(() => selectedContext = value),
                        validator: (value) =>
                            value == null ? '환자 진료 건을 선택해 주세요.' : null,
                      ),
                    ),
                    if (selectedContext != null) ...[
                      const SizedBox(height: 9),
                      _SelectionSummary(
                        icon: Icons.badge_outlined,
                        text:
                            '${selectedContext!.departmentName} · 환자번호 ${selectedContext!.patientNumber}',
                      ),
                    ],
                    const SizedBox(height: 18),
                    const _RequiredLabel('요청 의료진'),
                    const SizedBox(height: 8),
                    clinicians.when(
                      loading: () => const LinearProgressIndicator(
                        color: ClinicianUiColors.primary,
                      ),
                      error: (_, _) => _ReloadButton(
                        label: '의료진 다시 불러오기',
                        onPressed: () =>
                            ref.invalidate(consultationCliniciansProvider),
                      ),
                      data: (items) {
                        final available = items
                            .where((item) => item.id != myId)
                            .toList();
                        return DropdownButtonFormField<ConsultationClinician>(
                          initialValue: consultant,
                          isExpanded: true,
                          decoration: _inputDecoration(
                            hintText: '협진 의료진을 선택하세요',
                            prefixIcon: Icons.person_search_outlined,
                          ),
                          items: available
                              .map(
                                (item) => DropdownMenuItem(
                                  value: item,
                                  child: Text(
                                    '${item.name} · ${item.departmentName}',
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              )
                              .toList(),
                          onChanged: saving
                              ? null
                              : (value) => setState(() => consultant = value),
                          validator: (value) =>
                              value == null ? '협진 의료진을 선택해 주세요.' : null,
                        );
                      },
                    ),
                    if (consultant != null) ...[
                      const SizedBox(height: 9),
                      _SelectionSummary(
                        icon: Icons.local_hospital_outlined,
                        text:
                            '${consultant!.departmentName} · ${consultant!.hospitalName}',
                      ),
                    ],
                    const SizedBox(height: 18),
                    const _RequiredLabel('긴급도'),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        for (final option in const [
                          ('ROUTINE', '일반'),
                          ('URGENT', '긴급'),
                          ('EMERGENCY', '응급'),
                        ])
                          ChoiceChip(
                            label: Text(option.$2),
                            selected: priority == option.$1,
                            showCheckmark: priority == option.$1,
                            selectedColor: _priorityBackground(option.$1),
                            checkmarkColor: _priorityForeground(option.$1),
                            side: BorderSide(
                              color: priority == option.$1
                                  ? _priorityForeground(option.$1)
                                  : ClinicianUiColors.border,
                            ),
                            labelStyle: TextStyle(
                              color: priority == option.$1
                                  ? _priorityForeground(option.$1)
                                  : ClinicianUiColors.mutedText,
                              fontWeight: FontWeight.w700,
                            ),
                            onSelected: saving
                                ? null
                                : (_) => setState(() => priority = option.$1),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
              ClinicianSectionCard(
                title: '요청 내용',
                child: Column(
                  children: [
                    ClinicianFormField(
                      controller: subject,
                      labelText: '협진 제목 *',
                      hintText: '협진 제목을 입력하세요',
                      maxLength: 200,
                      validator: requiredText,
                      enabled: !saving,
                    ),
                    const SizedBox(height: 16),
                    ClinicianFormField(
                      controller: question,
                      labelText: '요청 사유 *',
                      hintText: '협진이 필요한 내용과 확인 사항을 입력하세요',
                      maxLines: 6,
                      validator: requiredText,
                      enabled: !saving,
                    ),
                  ],
                ),
              ),
              ClinicianSectionCard(
                title: '일정',
                child: InkWell(
                  borderRadius: BorderRadius.circular(14),
                  onTap: saving ? null : pickDueAt,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 15,
                      vertical: 14,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: ClinicianUiColors.border),
                    ),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.calendar_month_outlined,
                          color: ClinicianUiColors.primary,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                '답변 희망일 (선택)',
                                style: TextStyle(
                                  color: ClinicianUiColors.text,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                dueAt == null ? '선택하지 않음' : _formatDate(dueAt!),
                                style: const TextStyle(
                                  color: ClinicianUiColors.mutedText,
                                  fontSize: 13,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Icon(
                          Icons.chevron_right_rounded,
                          color: Color(0xFF9AA7BA),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              if (saving) ...[
                const LinearProgressIndicator(color: ClinicianUiColors.primary),
                const SizedBox(height: 12),
              ],
              Row(
                children: [
                  Expanded(
                    child: SizedBox(
                      height: 50,
                      child: OutlinedButton(
                        onPressed: saving
                            ? null
                            : () => Navigator.of(context).maybePop(),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: ClinicianUiColors.mutedText,
                          side: const BorderSide(
                            color: ClinicianUiColors.border,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                        ),
                        child: const Text('취소'),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    flex: 2,
                    child: SizedBox(
                      height: 50,
                      child: FilledButton.icon(
                        onPressed: saving ? null : submit,
                        icon: const Icon(Icons.send_rounded),
                        label: Text(saving ? '요청 중...' : '요청 전송'),
                        style: FilledButton.styleFrom(
                          backgroundColor: ClinicianUiColors.primary,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
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

class _RequiredLabel extends StatelessWidget {
  const _RequiredLabel(this.label);

  final String label;

  @override
  Widget build(BuildContext context) {
    return Text.rich(
      TextSpan(
        text: label,
        style: const TextStyle(
          color: ClinicianUiColors.text,
          fontSize: 13,
          fontWeight: FontWeight.w800,
        ),
        children: const [
          TextSpan(
            text: ' *',
            style: TextStyle(color: Color(0xFFD43D4E)),
          ),
        ],
      ),
    );
  }
}

class _SelectionSummary extends StatelessWidget {
  const _SelectionSummary({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFF2F6FD),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, size: 17, color: ClinicianUiColors.primary),
          const SizedBox(width: 7),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                color: ClinicianUiColors.mutedText,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ReloadButton extends StatelessWidget {
  const _ReloadButton({required this.label, required this.onPressed});

  final String label;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: onPressed,
        icon: const Icon(Icons.refresh_rounded),
        label: Text(label),
      ),
    );
  }
}

InputDecoration _inputDecoration({
  required String hintText,
  required IconData prefixIcon,
}) {
  return InputDecoration(
    hintText: hintText,
    hintStyle: const TextStyle(color: Color(0xFF9AA2B1)),
    prefixIcon: Icon(prefixIcon, color: ClinicianUiColors.mutedText),
    filled: true,
    fillColor: Colors.white,
    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(color: ClinicianUiColors.border),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(color: ClinicianUiColors.border),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(14),
      borderSide: const BorderSide(
        color: ClinicianUiColors.primary,
        width: 1.5,
      ),
    ),
  );
}

Color _priorityForeground(String value) => switch (value) {
  'EMERGENCY' => const Color(0xFFD43D4E),
  'URGENT' => const Color(0xFFC15F16),
  _ => ClinicianUiColors.primary,
};

Color _priorityBackground(String value) => switch (value) {
  'EMERGENCY' => const Color(0xFFFFE7EA),
  'URGENT' => const Color(0xFFFFECDD),
  _ => const Color(0xFFE7F0FF),
};

String _formatDate(DateTime value) {
  final local = value.toLocal();
  final month = local.month.toString().padLeft(2, '0');
  final day = local.day.toString().padLeft(2, '0');
  final hour = local.hour.toString().padLeft(2, '0');
  final minute = local.minute.toString().padLeft(2, '0');
  return '${local.year}.$month.$day $hour:$minute';
}
