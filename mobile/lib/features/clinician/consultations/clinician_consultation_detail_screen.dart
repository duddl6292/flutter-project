import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_model.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_provider.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_repository.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
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
    if (saving) {
      return;
    }
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
      if (mounted) {
        setState(() => saving = false);
      }
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
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(
          child: FilledButton(
            onPressed: () => ref.invalidate(
              clinicianConsultationDetailProvider(widget.consultationId),
            ),
            child: const Text('다시 시도'),
          ),
        ),
        data: buildDetail,
      ),
    );
  }

  Widget buildDetail(ClinicianConsultation item) {
    final closed = item.status == 'COMPLETED' || item.status == 'CANCELLED';
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        _section('요청 정보', [
          _line('상태', item.statusLabel),
          _line('긴급도', item.priorityLabel),
          _line(
            '요청 의료진',
            '${item.requester.name} · ${item.requester.departmentName}',
          ),
          _line(
            '대상 의료진',
            '${item.consultant.name} · ${item.consultant.departmentName}',
          ),
        ]),
        _section('환자 정보', [
          _line('환자', item.patientName),
          _line('환자번호', item.patientNumber),
          _line('진료번호', item.encounterNumber),
          _line('진료과', item.departmentName),
        ]),
        _section(item.subject, [Text(item.question)]),
        if (item.messages.isNotEmpty)
          _section('협진 메시지', item.messages.map(_message).toList()),
        if (item.response.isNotEmpty)
          _section('최종 협진 소견', [Text(item.response)]),
        if (!closed) ...[
          TextField(
            controller: message,
            onChanged: (_) => setState(() {}),
            maxLines: 3,
            decoration: const InputDecoration(labelText: '메시지 작성'),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: saving || message.text.trim().isEmpty
                ? null
                : () => run(() async {
                    await ref
                        .read(clinicianConsultationRepositoryProvider)
                        .sendMessage(item.id, message.text.trim());
                    message.clear();
                  }),
            icon: const Icon(Icons.send),
            label: const Text('메시지 전송'),
          ),
        ],
        if (item.myRole == 'CONSULTANT' && item.status == 'REQUESTED')
          FilledButton(
            onPressed: saving
                ? null
                : () => run(() async {
                    await ref
                        .read(clinicianConsultationRepositoryProvider)
                        .accept(item.id);
                  }),
            child: const Text('협진 수락'),
          ),
        if (item.myRole == 'CONSULTANT' && item.status == 'IN_PROGRESS')
          FilledButton(
            onPressed: saving ? null : () => complete(item),
            child: const Text('완료 처리'),
          ),
        if (item.myRole == 'REQUESTER' &&
            (item.status == 'REQUESTED' || item.status == 'IN_PROGRESS'))
          OutlinedButton(
            onPressed: saving ? null : () => cancel(item),
            child: const Text('요청 취소'),
          ),
      ],
    );
  }

  Widget _section(String title, List<Widget> children) => Card(
    margin: const EdgeInsets.only(bottom: 14),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 12),
          ...children,
        ],
      ),
    ),
  );
  Widget _line(String label, String value) => value.isEmpty
      ? const SizedBox.shrink()
      : Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(
                width: 100,
                child: Text(label, style: const TextStyle(color: Colors.grey)),
              ),
              Expanded(child: Text(value)),
            ],
          ),
        );
  Widget _message(ConsultationMessage item) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          item.isSystem ? '시스템' : item.sender.name,
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
        Text(item.content),
        for (final attachment in item.attachments)
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: Row(
              children: [
                const Icon(Icons.attach_file, size: 16),
                Expanded(child: Text(attachment.displayName)),
              ],
            ),
          ),
      ],
    ),
  );

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
