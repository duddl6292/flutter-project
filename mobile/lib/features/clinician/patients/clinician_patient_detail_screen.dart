import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_detail_model.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_detail_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class ClinicianPatientDetailScreen extends ConsumerWidget {
  const ClinicianPatientDetailScreen({required this.patientId, super.key});
  final String patientId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final value = ref.watch(clinicianPatientDetailProvider(patientId));
    return Scaffold(
      appBar: AppBar(title: const Text('환자 상세')),
      body: value.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _ErrorView(
          error: error,
          onRetry: () =>
              ref.invalidate(clinicianPatientDetailProvider(patientId)),
        ),
        data: (patient) => ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(
              patient.name,
              style: Theme.of(
                context,
              ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 16),
            _InfoCard(patient: patient),
            const SizedBox(height: 24),
            Text('의료 정보', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 10),
            _MenuTile(
              icon: Icons.science_outlined,
              title: '검사 결과',
              onTap: () =>
                  _open(context, patient, PatientResourceType.examinations),
            ),
            _MenuTile(
              icon: Icons.description_outlined,
              title: '진료 기록',
              onTap: () =>
                  _open(context, patient, PatientResourceType.medicalHistory),
            ),
            _MenuTile(
              icon: Icons.calendar_month_outlined,
              title: '예약 내역',
              onTap: () =>
                  _open(context, patient, PatientResourceType.appointments),
            ),
            _MenuTile(
              icon: Icons.medication_outlined,
              title: '처방 내역',
              onTap: () =>
                  _open(context, patient, PatientResourceType.prescriptions),
            ),
          ],
        ),
      ),
    );
  }

  void _open(
    BuildContext context,
    ClinicianPatientDetail patient,
    PatientResourceType type,
  ) {
    context.pushNamed(
      RouteNames.clinicianPatientResources,
      pathParameters: {'patientId': patient.id, 'resource': type.name},
      extra: patient,
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.patient});
  final ClinicianPatientDetail patient;

  @override
  Widget build(BuildContext context) {
    final birth = patient.birthDate;
    final age = patient.age;
    final rows = <(String, String)>[
      ('환자 등록번호', patient.medicalRecordNumber),
      ('성별', patient.sex),
      if (birth != null)
        (
          '생년월일',
          '${birth.year}-${birth.month.toString().padLeft(2, '0')}-${birth.day.toString().padLeft(2, '0')}',
        ),
      if (age != null) ('나이', '$age'),
      ('전화번호', patient.phone),
      ('응급 연락처', patient.emergencyContact),
      ('주소', patient.address),
      ('상태', patient.status),
    ].where((row) => row.$2.isNotEmpty).toList();
    return Card(
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            for (final row in rows)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 7),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(width: 105, child: Text(row.$1)),
                    Expanded(
                      child: Text(
                        row.$2,
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _MenuTile extends StatelessWidget {
  const _MenuTile({
    required this.icon,
    required this.title,
    required this.onTap,
  });
  final IconData icon;
  final String title;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => Card(
    elevation: 0,
    child: ListTile(
      leading: Icon(icon),
      title: Text(title),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    ),
  );
}

class ClinicianPatientResourceScreen extends ConsumerWidget {
  const ClinicianPatientResourceScreen({
    required this.patient,
    required this.type,
    super.key,
  });
  final ClinicianPatientDetail patient;
  final PatientResourceType type;

  String get title => switch (type) {
    PatientResourceType.examinations => '검사 결과',
    PatientResourceType.medicalHistory => '진료 기록',
    PatientResourceType.appointments => '예약 내역',
    PatientResourceType.prescriptions => '처방 내역',
  };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final request = (patient: patient, type: type);
    final value = ref.watch(clinicianPatientResourcesProvider(request));
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: value.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _ErrorView(
          error: error,
          onRetry: () =>
              ref.invalidate(clinicianPatientResourcesProvider(request)),
        ),
        data: (items) {
          if (items.isEmpty) return Center(child: Text('$title 데이터가 없습니다.'));
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
              return Card(
                elevation: 0,
                child: ListTile(
                  title: Text(item.title.isEmpty ? '-' : item.title),
                  subtitle: item.subtitle.isEmpty ? null : Text(item.subtitle),
                  trailing: Text(item.status),
                  onTap: item.examination == null
                      ? null
                      : () => context.pushNamed(
                          RouteNames.clinicianExaminationDetail,
                          pathParameters: {'examinationId': item.id},
                          extra: item.examination,
                        ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

class ClinicianExaminationDetailScreen extends ConsumerWidget {
  const ClinicianExaminationDetailScreen({
    required this.examinationId,
    super.key,
  });
  final String examinationId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final value = ref.watch(clinicianExaminationDetailProvider(examinationId));
    return Scaffold(
      appBar: AppBar(title: const Text('검사 결과 상세')),
      body: value.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _ErrorView(
          error: error,
          onRetry: () =>
              ref.invalidate(clinicianExaminationDetailProvider(examinationId)),
        ),
        data: (examination) => _ExaminationContent(examination: examination),
      ),
    );
  }
}

class _ExaminationContent extends StatelessWidget {
  const _ExaminationContent({required this.examination});
  final ClinicianExamination examination;

  @override
  Widget build(BuildContext context) {
    final report = examination.report;
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          examination.testName,
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        const SizedBox(height: 16),
        _line('검사일', _date(examination.performedAt)),
        _line(
          '검사 상태',
          examination.statusLabel.isEmpty
              ? examination.status
              : examination.statusLabel,
        ),
        _line('판독 결과', examination.interpretationLabel),
        _line('이상 소견 수', '${examination.abnormalCount}'),
        if (examination.observations.isNotEmpty) ...[
          const SizedBox(height: 20),
          Text('검사 수치', style: Theme.of(context).textTheme.titleMedium),
          for (final observation in examination.observations)
            ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text(observation.name),
              subtitle: Text(
                [
                  observation.reference,
                  observation.interpretation,
                ].where((v) => v.isNotEmpty).join(' · '),
              ),
              trailing: Text('${observation.value} ${observation.unit}'.trim()),
            ),
        ],
        if (report != null) ...[
          const SizedBox(height: 20),
          Text('의료진 소견', style: Theme.of(context).textTheme.titleMedium),
          if (report.authorName.isNotEmpty) _line('작성 의료진', report.authorName),
          if (report.summary.isNotEmpty) _line('요약', report.summary),
          if (report.conclusion.isNotEmpty) _line('결론', report.conclusion),
          _line('환자 공개', report.isReleased ? '공개' : '미공개'),
          if (report.assets.isNotEmpty) _line('첨부파일', report.assets.join(', ')),
        ],
      ],
    );
  }

  static Widget _line(String label, String value) {
    if (value.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 7),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 100, child: Text(label)),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  static String _date(DateTime? value) {
    if (value == null) return '';
    final local = value.toLocal();
    return '${local.year}.${local.month.toString().padLeft(2, '0')}.${local.day.toString().padLeft(2, '0')}';
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});
  final Object error;
  final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) {
    final expired =
        error is ApiException && (error as ApiException).statusCode == 401;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              expired ? '인증이 만료되었습니다. 다시 로그인해주세요.' : error.toString(),
              textAlign: TextAlign.center,
            ),
            if (!expired) ...[
              const SizedBox(height: 12),
              FilledButton(onPressed: onRetry, child: const Text('다시 시도')),
            ],
          ],
        ),
      ),
    );
  }
}
