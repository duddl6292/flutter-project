import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_model.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_provider.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_repository.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianConsultationDetailScreen extends ConsumerStatefulWidget {
  const ClinicianConsultationDetailScreen({
    required this.consultationId,
    super.key,
  });

  final String consultationId;

  @override
  ConsumerState<ClinicianConsultationDetailScreen> createState() => _State();
}

class _State extends ConsumerState<ClinicianConsultationDetailScreen> {
  final message = TextEditingController();
  bool saving = false;

  @override
  void dispose() {
    message.dispose();
    super.dispose();
  }

  Future<void> run(Future<void> Function() action) async {
    if (saving) return;
    setState(() => saving = true);
    try {
      await action();
      ref.invalidate(
        clinicianConsultationDetailProvider(widget.consultationId),
      );
      ref.invalidate(clinicianConsultationsProvider);
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('협진 처리에 실패했습니다: $error')));
      }
    } finally {
      if (mounted) setState(() => saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final value = ref.watch(
      clinicianConsultationDetailProvider(widget.consultationId),
    );
    return ClinicianDetailScaffold(
      title: '협진 상세',
      body: value.when(
        loading: () => const ClinicianLoadingView(),
        error: (error, _) => ClinicianErrorView(
          message: error.toString(),
          onRetry: () => ref.invalidate(
            clinicianConsultationDetailProvider(widget.consultationId),
          ),
        ),
        data: buildDetail,
      ),
    );
  }

  Widget buildDetail(ClinicianConsultation item) {
    final closed = item.status == 'COMPLETED' || item.status == 'CANCELLED';
    final statusLabel = item.statusLabel.isEmpty
        ? item.status
        : item.statusLabel;
    final priorityLabel = item.priorityLabel.isEmpty
        ? item.priority
        : item.priorityLabel;

    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
      children: [
        ClinicianSectionCard(
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              const Text(
                '상태',
                style: TextStyle(
                  color: ClinicianUiColors.mutedText,
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
              ClinicianStatusBadge(
                label: statusLabel,
                tone: _statusTone(item.status),
              ),
              const SizedBox(width: 8),
              const Text(
                '긴급도',
                style: TextStyle(
                  color: ClinicianUiColors.mutedText,
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
              ClinicianStatusBadge(
                label: priorityLabel,
                tone: _priorityTone(item.priority),
              ),
            ],
          ),
        ),
        ClinicianSectionCard(
          title: '환자 정보',
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: const BoxDecoration(
                  color: Color(0xFFEAF1FF),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.person_outline_rounded,
                  color: ClinicianUiColors.primary,
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  children: [
                    ClinicianInfoRow(label: '환자', value: item.patientName),
                    ClinicianInfoRow(label: '환자번호', value: item.patientNumber),
                    ClinicianInfoRow(
                      label: '진료번호',
                      value: item.encounterNumber,
                    ),
                    ClinicianInfoRow(label: '진료과', value: item.departmentName),
                    ClinicianInfoRow(
                      label: '생년월일',
                      value: _date(item.patientBirthDate),
                    ),
                    ClinicianInfoRow(label: '성별', value: item.patientSex),
                  ],
                ),
              ),
            ],
          ),
        ),
        ClinicianSectionCard(
          title: '요청 정보',
          child: Column(
            children: [
              ClinicianInfoRow(
                label: '요청 의료진',
                value: _clinicianLabel(item.requester),
              ),
              ClinicianInfoRow(
                label: '대상 의료진',
                value: _clinicianLabel(item.consultant),
              ),
              ClinicianInfoRow(label: '요청일', value: _dateTime(item.createdAt)),
              ClinicianInfoRow(label: '답변 희망일', value: _dateTime(item.dueAt)),
            ],
          ),
        ),
        ClinicianSectionCard(
          title: '협진 요청 내용',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                item.subject,
                style: const TextStyle(
                  color: ClinicianUiColors.text,
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                ),
              ),
              if (item.question.isNotEmpty) ...[
                const SizedBox(height: 10),
                Text(
                  item.question,
                  style: const TextStyle(
                    color: Color(0xFF414B5D),
                    fontSize: 14,
                    height: 1.55,
                  ),
                ),
              ],
            ],
          ),
        ),
        if (item.messages.isNotEmpty)
          ClinicianSectionCard(
            title: '협진 메시지',
            child: Column(
              children: [
                for (final chat in item.messages) _message(item, chat),
              ],
            ),
          ),
        if (item.response.isNotEmpty)
          ClinicianSectionCard(
            title: '최종 협진 소견',
            child: Text(
              item.response,
              style: const TextStyle(
                color: ClinicianUiColors.text,
                fontSize: 14,
                height: 1.55,
              ),
            ),
          ),
        if (!closed) ...[
          ClinicianFormField(
            controller: message,
            hintText: '메시지를 입력하세요',
            onChanged: (_) => setState(() {}),
            maxLines: 3,
            enabled: !saving,
            suffixIcon: IconButton(
              tooltip: '메시지 전송',
              onPressed: saving || message.text.trim().isEmpty
                  ? null
                  : () => run(() async {
                      await ref
                          .read(clinicianConsultationRepositoryProvider)
                          .sendMessage(item.id, message.text.trim());
                      message.clear();
                    }),
              icon: const Icon(Icons.send_rounded),
              color: ClinicianUiColors.primary,
            ),
          ),
          const SizedBox(height: 14),
        ],
        if (saving) ...[
          const LinearProgressIndicator(color: ClinicianUiColors.primary),
          const SizedBox(height: 12),
        ],
        if (item.myRole == 'CONSULTANT' && item.status == 'REQUESTED')
          _PrimaryActionButton(
            label: '협진 수락',
            icon: Icons.check_circle_outline_rounded,
            onPressed: saving
                ? null
                : () => run(() async {
                    await ref
                        .read(clinicianConsultationRepositoryProvider)
                        .accept(item.id);
                  }),
          ),
        if (item.myRole == 'CONSULTANT' && item.status == 'IN_PROGRESS')
          _PrimaryActionButton(
            label: '협진 완료',
            icon: Icons.task_alt_rounded,
            backgroundColor: const Color(0xFF16845B),
            onPressed: saving ? null : () => complete(item),
          ),
        if (item.myRole == 'REQUESTER' &&
            (item.status == 'REQUESTED' || item.status == 'IN_PROGRESS'))
          SizedBox(
            height: 48,
            child: OutlinedButton.icon(
              onPressed: saving ? null : () => cancel(item),
              icon: const Icon(Icons.close_rounded),
              label: const Text('요청 취소'),
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFFD43D4E),
                side: const BorderSide(color: Color(0xFFF0A7AF)),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),
      ],
    );
  }

  Widget _message(
    ClinicianConsultation consultation,
    ConsultationMessage item,
  ) {
    if (item.isSystem) {
      return Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: Center(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
            decoration: BoxDecoration(
              color: const Color(0xFFF0F2F6),
              borderRadius: BorderRadius.circular(999),
            ),
            child: Text(
              item.content,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: ClinicianUiColors.mutedText,
                fontSize: 12,
              ),
            ),
          ),
        ),
      );
    }

    final currentClinician = switch (consultation.myRole) {
      'REQUESTER' => consultation.requester,
      'CONSULTANT' => consultation.consultant,
      _ => null,
    };
    final mine =
        currentClinician != null &&
        currentClinician.id.isNotEmpty &&
        currentClinician.id == item.sender.id;

    return Align(
      alignment: mine ? Alignment.centerRight : Alignment.centerLeft,
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.sizeOf(context).width * 0.74,
        ),
        child: Padding(
          padding: const EdgeInsets.only(bottom: 14),
          child: Column(
            crossAxisAlignment: mine
                ? CrossAxisAlignment.end
                : CrossAxisAlignment.start,
            children: [
              Text(
                [
                  item.sender.name,
                  item.sender.departmentName,
                ].where((value) => value.isNotEmpty).join(' · '),
                style: const TextStyle(
                  color: ClinicianUiColors.mutedText,
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 5),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 11,
                ),
                decoration: BoxDecoration(
                  color: mine
                      ? ClinicianUiColors.primary
                      : const Color(0xFFF0F2F7),
                  borderRadius: BorderRadius.only(
                    topLeft: const Radius.circular(15),
                    topRight: const Radius.circular(15),
                    bottomLeft: Radius.circular(mine ? 15 : 4),
                    bottomRight: Radius.circular(mine ? 4 : 15),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.content,
                      style: TextStyle(
                        color: mine ? Colors.white : ClinicianUiColors.text,
                        fontSize: 14,
                        height: 1.4,
                      ),
                    ),
                    for (final attachment in item.attachments)
                      Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.attach_file_rounded,
                              size: 15,
                              color: mine
                                  ? Colors.white70
                                  : ClinicianUiColors.mutedText,
                            ),
                            const SizedBox(width: 4),
                            Flexible(
                              child: Text(
                                attachment.displayName,
                                style: TextStyle(
                                  color: mine
                                      ? Colors.white70
                                      : ClinicianUiColors.mutedText,
                                  fontSize: 11,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
              if (item.createdAt != null) ...[
                const SizedBox(height: 4),
                Text(
                  _dateTime(item.createdAt),
                  style: const TextStyle(
                    color: Color(0xFF9AA2B1),
                    fontSize: 10,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Future<void> complete(ClinicianConsultation item) async {
    final response = await askText('최종 협진 소견', '최종 답변을 입력해 주세요.');
    if (response != null && response.trim().isNotEmpty) {
      await run(() async {
        await ref
            .read(clinicianConsultationRepositoryProvider)
            .complete(item.id, response.trim());
      });
    }
  }

  Future<void> cancel(ClinicianConsultation item) async {
    final reason = await askText('협진 요청 취소', '취소 사유 (선택)');
    if (reason != null) {
      await run(() async {
        await ref
            .read(clinicianConsultationRepositoryProvider)
            .cancel(item.id, reason.trim());
      });
    }
  }

  Future<String?> askText(String title, String hint) async {
    final controller = TextEditingController();
    final result = await showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(title),
        content: TextField(
          controller: controller,
          maxLines: 4,
          decoration: InputDecoration(hintText: hint),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('취소'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, controller.text),
            child: const Text('확인'),
          ),
        ],
      ),
    );
    controller.dispose();
    return result;
  }
}

class _PrimaryActionButton extends StatelessWidget {
  const _PrimaryActionButton({
    required this.label,
    required this.icon,
    this.backgroundColor = ClinicianUiColors.primary,
    required this.onPressed,
  });

  final String label;
  final IconData icon;
  final Color backgroundColor;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 48,
      child: FilledButton.icon(
        onPressed: onPressed,
        icon: Icon(icon),
        label: Text(label),
        style: FilledButton.styleFrom(
          backgroundColor: backgroundColor,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
      ),
    );
  }
}

ClinicianStatusTone _statusTone(String status) => switch (status) {
  'REQUESTED' => ClinicianStatusTone.danger,
  'IN_PROGRESS' => ClinicianStatusTone.info,
  'COMPLETED' => ClinicianStatusTone.success,
  _ => ClinicianStatusTone.neutral,
};

ClinicianStatusTone _priorityTone(String priority) => switch (priority) {
  'EMERGENCY' => ClinicianStatusTone.danger,
  'URGENT' => ClinicianStatusTone.warning,
  _ => ClinicianStatusTone.neutral,
};

String _clinicianLabel(ConsultationClinician clinician) {
  return [
    clinician.name,
    clinician.departmentName,
    clinician.hospitalName,
  ].where((value) => value.isNotEmpty).join(' · ');
}

String _date(DateTime? value) {
  if (value == null) return '';
  final local = value.toLocal();
  final month = local.month.toString().padLeft(2, '0');
  final day = local.day.toString().padLeft(2, '0');
  return '${local.year}.$month.$day';
}

String _dateTime(DateTime? value) {
  if (value == null) return '';
  final local = value.toLocal();
  final hour = local.hour.toString().padLeft(2, '0');
  final minute = local.minute.toString().padLeft(2, '0');
  return '${_date(local)} $hour:$minute';
}
