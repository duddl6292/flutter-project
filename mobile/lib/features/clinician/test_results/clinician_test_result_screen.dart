import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/test_results/clinician_test_result_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class ClinicianTestResultScreen extends ConsumerStatefulWidget {
  const ClinicianTestResultScreen({super.key});
  @override
  ConsumerState<ClinicianTestResultScreen> createState() =>
      _ClinicianTestResultScreenState();
}

class _ClinicianTestResultScreenState
    extends ConsumerState<ClinicianTestResultScreen> {
  String query = '';

  @override
  Widget build(BuildContext context) {
    final value = ref.watch(clinicianTestResultsProvider);
    return ClinicianDetailScaffold(
      title: '검사 결과 관리',
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              onChanged: (text) => setState(() => query = text),
              decoration: const InputDecoration(
                hintText: '검사명 검색',
                prefixIcon: Icon(Icons.search),
              ),
            ),
          ),
          Expanded(
            child: value.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(
                child: FilledButton(
                  onPressed: () => ref.invalidate(clinicianTestResultsProvider),
                  child: Text(error.toString()),
                ),
              ),
              data: (items) {
                final filtered = items
                    .where(
                      (item) => item.testName.toLowerCase().contains(
                        query.toLowerCase(),
                      ),
                    )
                    .toList();
                if (filtered.isEmpty) {
                  return const Center(child: Text('검사 결과가 없습니다.'));
                }
                return ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: filtered.length,
                  itemBuilder: (context, index) {
                    final item = filtered[index];
                    return Card(
                      elevation: 0,
                      child: ListTile(
                        title: Text(item.testName),
                        subtitle: Text(item.interpretationLabel),
                        trailing: Text(item.statusLabel),
                        onTap: () => context.pushNamed(
                          RouteNames.clinicianExaminationDetail,
                          pathParameters: {'examinationId': item.id},
                          extra: item,
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
