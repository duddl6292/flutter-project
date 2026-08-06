import 'package:brainon_mobile/features/clinician/support/clinician_support_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianSupportScreen extends ConsumerWidget {
  const ClinicianSupportScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(clinicianSupportProvider);
    return ClinicianDetailScaffold(
      title: '고객센터',
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text(
            '자주 묻는 질문',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 10),
          data.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (_, _) => const Text('FAQ를 불러오지 못했습니다.'),
            data: (items) => Column(
              children: items
                  .map(
                    (e) => ExpansionTile(
                      title: Text(e.question),
                      children: [
                        Padding(
                          padding: const EdgeInsets.all(16),
                          child: Text(e.answer),
                        ),
                      ],
                    ),
                  )
                  .toList(),
            ),
          ),
          const SizedBox(height: 20),
          const Card(
            elevation: 0,
            child: ListTile(
              leading: Icon(Icons.schedule),
              title: Text('운영시간'),
              subtitle: Text('평일 09:00~18:00'),
            ),
          ),
          FilledButton.icon(
            onPressed: () => ScaffoldMessenger.of(
              context,
            ).showSnackBar(const SnackBar(content: Text('문의하기 기능은 준비 중입니다.'))),
            icon: const Icon(Icons.chat_outlined),
            label: const Text('문의하기'),
          ),
        ],
      ),
    );
  }
}
