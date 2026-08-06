import 'package:brainon_mobile/features/clinician/notices/clinician_notice_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianNoticeScreen extends ConsumerWidget {
  const ClinicianNoticeScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(clinicianNoticesProvider);
    return ClinicianDetailScaffold(
      title: '공지사항',
      body: data.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(
          child: FilledButton(
            onPressed: () => ref.invalidate(clinicianNoticesProvider),
            child: const Text('다시 시도'),
          ),
        ),
        data: (items) => items.isEmpty
            ? const Center(child: Text('공지사항이 없습니다.'))
            : ListView(
                padding: const EdgeInsets.all(20),
                children: items
                    .map(
                      (e) => Card(
                        elevation: 0,
                        child: ListTile(
                          onTap: () => showModalBottomSheet<void>(
                            context: context,
                            builder: (_) => SafeArea(
                              child: Padding(
                                padding: const EdgeInsets.all(24),
                                child: Text(e.content),
                              ),
                            ),
                          ),
                          leading: e.isImportant
                              ? const Chip(label: Text('중요'))
                              : null,
                          title: Text(
                            e.title,
                            style: const TextStyle(fontWeight: FontWeight.w800),
                          ),
                          subtitle: Text(
                            e.publishedAt?.toString().split(' ').first ?? '',
                          ),
                        ),
                      ),
                    )
                    .toList(),
              ),
      ),
    );
  }
}
