import 'package:brainon_mobile/features/clinician/statistics/clinician_statistics_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClinicianStatisticsScreen extends ConsumerStatefulWidget {
  const ClinicianStatisticsScreen({super.key});
  @override
  ConsumerState<ClinicianStatisticsScreen> createState() => _StatisticsState();
}

class _StatisticsState extends ConsumerState<ClinicianStatisticsScreen> {
  int period = 0;
  @override
  Widget build(BuildContext context) {
    final data = ref.watch(clinicianStatisticsProvider);
    return ClinicianDetailScaffold(
      title: '진료 통계',
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: SegmentedButton<int>(
              segments: const [
                ButtonSegment(value: 0, label: Text('오늘')),
                ButtonSegment(value: 1, label: Text('이번 주')),
                ButtonSegment(value: 2, label: Text('이번 달')),
              ],
              selected: {period},
              onSelectionChanged: (value) =>
                  setState(() => period = value.first),
            ),
          ),
          Expanded(
            child: data.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (_, _) => Center(
                child: FilledButton(
                  onPressed: () => ref.invalidate(clinicianStatisticsProvider),
                  child: const Text('다시 시도'),
                ),
              ),
              data: (statistics) {
                final values = [
                  ('진료 환자', statistics.patientCount, Colors.blue),
                  ('대기 환자', statistics.waitingCount, Colors.orange),
                  ('협진 요청', statistics.consultationCount, Colors.red),
                  ('검사 결과', statistics.testResultCount, Colors.purple),
                ];
                return GridView.count(
                  padding: const EdgeInsets.all(20),
                  crossAxisCount: 2,
                  mainAxisSpacing: 12,
                  crossAxisSpacing: 12,
                  children: values
                      .map(
                        (value) => Card(
                          elevation: 0,
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(value.$1),
                                const SizedBox(height: 10),
                                Text(
                                  '${value.$2}',
                                  style: TextStyle(
                                    fontSize: 28,
                                    fontWeight: FontWeight.w900,
                                    color: value.$3,
                                  ),
                                ),
                                const SizedBox(height: 10),
                                FractionallySizedBox(
                                  widthFactor: (value.$2 / 20).clamp(.1, 1),
                                  child: Container(
                                    height: 7,
                                    decoration: BoxDecoration(
                                      color: value.$3,
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      )
                      .toList(),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
