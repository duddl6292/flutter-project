import 'package:brainon_mobile/features/medication/repositories/medication_repository.dart';
import 'package:brainon_mobile/shared/models/medication.dart';
import 'package:flutter/material.dart';

class MedicationListScreen extends StatefulWidget {
  const MedicationListScreen({super.key});

  @override
  State<MedicationListScreen> createState() =>
      _MedicationListScreenState();
}

class _MedicationListScreenState extends State<MedicationListScreen> {
  final MedicationRepository _repository = MedicationRepository();

  late final Future<List<Medication>> _medicationsFuture;

  @override
  void initState() {
    super.initState();
    _medicationsFuture = _repository.getMedications();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FB),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        elevation: 0,
        title: const Text(
          '복용 관리',
          style: TextStyle(
            color: Color(0xFF111827),
            fontSize: 21,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: FutureBuilder<List<Medication>>(
          future: _medicationsFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(
                child: CircularProgressIndicator(),
              );
            }

            if (snapshot.hasError) {
              return Center(
                child: Text(
                  '복용 정보를 불러오지 못했습니다.\n${snapshot.error}',
                  textAlign: TextAlign.center,
                ),
              );
            }

            final medications =
                snapshot.data ?? <Medication>[];

            if (medications.isEmpty) {
              return const Center(
                child: Text('오늘 복용할 약이 없습니다.'),
              );
            }

            return _MedicationContent(
              medications: medications,
            );
          },
        ),
      ),
    );
  }
}

class _MedicationContent extends StatefulWidget {
  const _MedicationContent({
    required this.medications,
  });

  final List<Medication> medications;

  @override
  State<_MedicationContent> createState() =>
      _MedicationContentState();
}

class _MedicationContentState extends State<_MedicationContent> {
  late List<Medication> _medications;

  @override
  void initState() {
    super.initState();
    _medications = List<Medication>.from(
      widget.medications,
    );
  }

  int get _completedCount {
    return _medications
        .where((medication) => medication.completed)
        .length;
  }

  void _toggleMedication(int index) {
    final medication = _medications[index];

    setState(() {
      _medications[index] = medication.copyWith(
        completed: !medication.completed,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final totalCount = _medications.length;

    final progress = totalCount == 0
        ? 0.0
        : _completedCount / totalCount;

    return ListView(
      padding: const EdgeInsets.fromLTRB(
        20,
        20,
        20,
        32,
      ),
      children: [
        const Text(
          '오늘 복용할 약',
          style: TextStyle(
            color: Color(0xFF111827),
            fontSize: 23,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 6),
        const Text(
          '복용 시간을 확인하고 복용 여부를 기록해 주세요.',
          style: TextStyle(
            color: Color(0xFF6B7280),
            fontSize: 14,
          ),
        ),
        const SizedBox(height: 22),

        _ProgressCard(
          completedCount: _completedCount,
          totalCount: totalCount,
          progress: progress,
        ),

        const SizedBox(height: 24),

        ...List.generate(
          _medications.length,
          (index) {
            final medication = _medications[index];

            return Padding(
              padding: const EdgeInsets.only(
                bottom: 16,
              ),
              child: _MedicationCard(
                medication: medication,
                onChanged: () {
                  _toggleMedication(index);
                },
              ),
            );
          },
        ),
      ],
    );
  }
}

class _ProgressCard extends StatelessWidget {
  const _ProgressCard({
    required this.completedCount,
    required this.totalCount,
    required this.progress,
  });

  final int completedCount;
  final int totalCount;
  final double progress;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFEFF6FF),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Icon(
                  Icons.medication_outlined,
                  color: Color(0xFF2563EB),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '오늘의 복용 현황',
                      style: TextStyle(
                        color: Color(0xFF111827),
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '$totalCount개 중 '
                      '$completedCount개 복용 완료',
                      style: const TextStyle(
                        color: Color(0xFF64748B),
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
              Text(
                '${(progress * 100).round()}%',
                style: const TextStyle(
                  color: Color(0xFF2563EB),
                  fontSize: 20,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 10,
              backgroundColor: Colors.white,
              valueColor:
                  const AlwaysStoppedAnimation<Color>(
                Color(0xFF2563EB),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _MedicationCard extends StatelessWidget {
  const _MedicationCard({
    required this.medication,
    required this.onChanged,
  });

  final Medication medication;
  final VoidCallback onChanged;

  @override
  Widget build(BuildContext context) {
    final isCompleted = medication.completed;

    final time =
        '${medication.scheduledAt.hour.toString().padLeft(2, '0')}:'
        '${medication.scheduledAt.minute.toString().padLeft(2, '0')}';

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isCompleted
              ? const Color(0xFF86EFAC)
              : const Color(0xFFE5E7EB),
        ),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0D000000),
            blurRadius: 16,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              Container(
                width: 58,
                padding: const EdgeInsets.symmetric(
                  vertical: 12,
                ),
                decoration: BoxDecoration(
                  color: isCompleted
                      ? const Color(0xFFF0FDF4)
                      : const Color(0xFFEFF6FF),
                  borderRadius:
                      BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    Icon(
                      Icons.medication_outlined,
                      color: isCompleted
                          ? const Color(0xFF16A34A)
                          : const Color(0xFF2563EB),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      medication.period,
                      style: TextStyle(
                        color: isCompleted
                            ? const Color(0xFF15803D)
                            : const Color(0xFF2563EB),
                        fontSize: 13,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          time,
                          style: const TextStyle(
                            color: Color(0xFF111827),
                            fontSize: 20,
                            fontWeight:
                                FontWeight.w800,
                          ),
                        ),
                        const Spacer(),
                        Container(
                          padding:
                              const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: isCompleted
                                ? const Color(0xFFF0FDF4)
                                : const Color(0xFFF1F5F9),
                            borderRadius:
                                BorderRadius.circular(10),
                          ),
                          child: Text(
                            isCompleted
                                ? '복용 완료'
                                : '복용 예정',
                            style: TextStyle(
                              color: isCompleted
                                  ? const Color(0xFF15803D)
                                  : const Color(0xFF64748B),
                              fontSize: 12,
                              fontWeight:
                                  FontWeight.w700,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Text(
                      medication.name,
                      style: const TextStyle(
                        color: Color(0xFF111827),
                        fontSize: 17,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      medication.dose,
                      style: const TextStyle(
                        color: Color(0xFF475569),
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      crossAxisAlignment:
                          CrossAxisAlignment.start,
                      children: [
                        const Icon(
                          Icons.info_outline,
                          size: 17,
                          color: Color(0xFF94A3B8),
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            medication.instruction,
                            style: const TextStyle(
                              color: Color(0xFF6B7280),
                              fontSize: 13,
                              height: 1.4,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          SizedBox(
            width: double.infinity,
            height: 50,
            child: FilledButton.icon(
              onPressed: onChanged,
              style: FilledButton.styleFrom(
                backgroundColor: isCompleted
                    ? const Color(0xFFE2E8F0)
                    : const Color(0xFF2563EB),
                foregroundColor: isCompleted
                    ? const Color(0xFF475569)
                    : Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius:
                      BorderRadius.circular(14),
                ),
              ),
              icon: Icon(
                isCompleted
                    ? Icons.undo
                    : Icons.check_circle_outline,
              ),
              label: Text(
                isCompleted
                    ? '복용 취소'
                    : '복용 완료',
                style: const TextStyle(
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}