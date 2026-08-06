import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_detail_model.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_detail_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_detail_scaffold.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_ui.dart';
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
      backgroundColor: ClinicianUiColors.background,
      appBar: AppBar(
        title: const Text('환자 상세'),
        backgroundColor: ClinicianUiColors.background,
        foregroundColor: ClinicianUiColors.text,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
      ),
      body: value.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _ErrorView(
          error: error,
          onRetry: () =>
              ref.invalidate(clinicianPatientDetailProvider(patientId)),
        ),
        data: (patient) => ListView(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
          children: [
            _PatientProfileCard(patient: patient),
            const SizedBox(height: 16),
            _InfoCard(patient: patient),
            const SizedBox(height: 14),
            Text(
              '의료 정보',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: ClinicianUiColors.text,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 12),
            _MenuTile(
              icon: Icons.science_outlined,
              title: '검사 결과',
              description: '혈액검사, 영상검사 등의 결과 확인',
              onTap: () =>
                  _open(context, patient, PatientResourceType.examinations),
            ),
            _MenuTile(
              icon: Icons.description_outlined,
              title: '진료 기록',
              description: '진료 및 상담 기록 확인',
              onTap: () =>
                  _open(context, patient, PatientResourceType.medicalHistory),
            ),
            _MenuTile(
              icon: Icons.calendar_month_outlined,
              title: '예약 내역',
              description: '예약 일정 및 방문 내역 확인',
              onTap: () =>
                  _open(context, patient, PatientResourceType.appointments),
            ),
            _MenuTile(
              icon: Icons.medication_outlined,
              title: '처방 내역',
              description: '약 처방 및 복약 정보 확인',
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

class _PatientProfileCard extends StatelessWidget {
  const _PatientProfileCard({required this.patient});

  final ClinicianPatientDetail patient;

  @override
  Widget build(BuildContext context) {
    final initial = _patientInitial(patient.name);

    return ClinicianSectionCard(
      margin: EdgeInsets.zero,
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Container(
            width: 72,
            height: 72,
            decoration: const BoxDecoration(
              color: Color(0xFFE8F0FF),
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: initial.isEmpty
                ? const Icon(
                    Icons.person_outline_rounded,
                    size: 34,
                    color: ClinicianUiColors.primary,
                  )
                : Text(
                    initial,
                    style: const TextStyle(
                      color: ClinicianUiColors.primary,
                      fontSize: 28,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
          ),
          const SizedBox(width: 18),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  patient.name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: ClinicianUiColors.text,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                if (patient.medicalRecordNumber.isNotEmpty) ...[
                  const SizedBox(height: 5),
                  Text(
                    patient.medicalRecordNumber,
                    style: const TextStyle(
                      color: ClinicianUiColors.mutedText,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
                if (patient.status.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  ClinicianStatusBadge(
                    label: patient.status,
                    tone: _patientStatusTone(patient.status),
                    icon: Icons.circle,
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
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
    final rows = <({String label, String value, Widget? valueWidget})>[
      (label: '환자 등록번호', value: patient.medicalRecordNumber, valueWidget: null),
      (label: '성별', value: patient.sex, valueWidget: null),
      if (birth != null)
        (
          label: '생년월일',
          value:
              '${birth.year}-${birth.month.toString().padLeft(2, '0')}-${birth.day.toString().padLeft(2, '0')}',
          valueWidget: null,
        ),
      if (age != null) (label: '나이', value: '$age', valueWidget: null),
      (label: '전화번호', value: patient.phone, valueWidget: null),
      (label: '응급 연락처', value: patient.emergencyContact, valueWidget: null),
      (label: '주소', value: patient.address, valueWidget: null),
      if (patient.status.isNotEmpty)
        (
          label: '상태',
          value: patient.status,
          valueWidget: Align(
            alignment: Alignment.centerLeft,
            child: ClinicianStatusBadge(
              label: patient.status,
              tone: _patientStatusTone(patient.status),
              icon: Icons.circle,
            ),
          ),
        ),
    ].where((row) => row.value.isNotEmpty).toList();

    return ClinicianSectionCard(
      title: '기본 정보',
      margin: EdgeInsets.zero,
      child: Column(
        children: [
          for (var index = 0; index < rows.length; index++) ...[
            ClinicianInfoRow(
              label: rows[index].label,
              value: rows[index].value,
              valueWidget: rows[index].valueWidget,
              labelWidth: 104,
            ),
            if (index < rows.length - 1)
              const Divider(height: 19, color: ClinicianUiColors.border),
          ],
        ],
      ),
    );
  }
}

class _MenuTile extends StatelessWidget {
  const _MenuTile({
    required this.icon,
    required this.title,
    required this.description,
    required this.onTap,
  });
  final IconData icon;
  final String title;
  final String description;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => ClinicianListCard(
    onTap: onTap,
    child: Row(
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: const Color(0xFFE8F0FF),
            borderRadius: BorderRadius.circular(13),
          ),
          alignment: Alignment.center,
          child: Icon(icon, color: ClinicianUiColors.primary, size: 25),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: ClinicianUiColors.text,
                  fontSize: 16,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: const TextStyle(
                  color: ClinicianUiColors.mutedText,
                  fontSize: 13,
                  height: 1.35,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(width: 10),
        const Icon(Icons.chevron_right_rounded, color: Color(0xFF596275)),
      ],
    ),
  );
}

String _patientInitial(String name) {
  final trimmed = name.trim();
  return trimmed.isEmpty ? '' : String.fromCharCode(trimmed.runes.first);
}

ClinicianStatusTone _patientStatusTone(String status) =>
    status.trim().toUpperCase() == 'ACTIVE'
    ? ClinicianStatusTone.success
    : ClinicianStatusTone.neutral;

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
    return ClinicianDetailScaffold(
      title: '검사 결과 상세',
      body: ColoredBox(
        color: ClinicianUiColors.background,
        child: value.when(
          loading: () => const ClinicianLoadingView(),
          error: (error, _) => ClinicianErrorView(
            message: error is ApiException && error.statusCode == 401
                ? '인증이 만료되었습니다. 다시 로그인해주세요.'
                : error.toString(),
            onRetry: () => ref.invalidate(
              clinicianExaminationDetailProvider(examinationId),
            ),
          ),
          data: (examination) => _ExaminationContent(examination: examination),
        ),
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
    final status = examination.statusLabel.isEmpty
        ? examination.status
        : examination.statusLabel;
    final interpretation = examination.interpretationLabel.isEmpty
        ? examination.interpretation
        : examination.interpretationLabel;

    return ListView(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 32),
      children: [
        ClinicianSectionCard(
          title: '검사 요약',
          trailing: status.isEmpty
              ? null
              : ClinicianStatusBadge(
                  label: status,
                  tone: _examinationStatusTone(examination.status),
                ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                examination.testName.isEmpty ? '-' : examination.testName,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: ClinicianUiColors.text,
                  fontWeight: FontWeight.w800,
                ),
              ),
              const SizedBox(height: 12),
              ClinicianInfoRow(
                label: '검사일',
                value: _date(examination.performedAt),
              ),
              ClinicianInfoRow(
                label: '판독 결과',
                value: interpretation,
                valueWidget: interpretation.isEmpty
                    ? null
                    : Align(
                        alignment: Alignment.centerLeft,
                        child: ClinicianStatusBadge(
                          label: interpretation,
                          tone: _interpretationTone(examination.interpretation),
                        ),
                      ),
              ),
              ClinicianInfoRow(
                label: '이상 소견 수',
                value: '${examination.abnormalCount}건',
                valueWidget: Align(
                  alignment: Alignment.centerLeft,
                  child: ClinicianStatusBadge(
                    label: '${examination.abnormalCount}건',
                    tone: examination.abnormalCount > 0
                        ? ClinicianStatusTone.warning
                        : ClinicianStatusTone.success,
                  ),
                ),
              ),
            ],
          ),
        ),
        ClinicianSectionCard(
          title: '검사 수치',
          child: examination.observations.isEmpty
              ? const Text(
                  '등록된 검사 수치가 없습니다.',
                  style: TextStyle(color: ClinicianUiColors.mutedText),
                )
              : Column(
                  children: [
                    for (
                      var index = 0;
                      index < examination.observations.length;
                      index++
                    ) ...[
                      _observationRow(context, examination.observations[index]),
                      if (index < examination.observations.length - 1)
                        const Divider(
                          height: 25,
                          color: ClinicianUiColors.border,
                        ),
                    ],
                  ],
                ),
        ),
        ClinicianSectionCard(
          title: '의료진 소견',
          trailing: report == null
              ? null
              : ClinicianStatusBadge(
                  label: report.isReleased ? '공개' : '미공개',
                  tone: report.isReleased
                      ? ClinicianStatusTone.success
                      : ClinicianStatusTone.neutral,
                ),
          child: report == null
              ? const Text(
                  '등록된 의료진 소견이 없습니다.',
                  style: TextStyle(color: ClinicianUiColors.mutedText),
                )
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    ClinicianInfoRow(label: '작성 의료진', value: report.authorName),
                    if (report.summary.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      _reportText('요약', report.summary),
                    ],
                    if (report.conclusion.isNotEmpty) ...[
                      const SizedBox(height: 14),
                      _reportText('결론', report.conclusion),
                    ],
                  ],
                ),
        ),
        ClinicianSectionCard(
          title: '첨부파일',
          child: report == null || report.assets.isEmpty
              ? const Text(
                  '첨부파일이 없습니다.',
                  style: TextStyle(color: ClinicianUiColors.mutedText),
                )
              : Column(
                  children: [
                    for (var index = 0; index < report.assets.length; index++)
                      Padding(
                        padding: EdgeInsets.only(
                          bottom: index == report.assets.length - 1 ? 0 : 10,
                        ),
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 14,
                            vertical: 12,
                          ),
                          decoration: BoxDecoration(
                            color: ClinicianUiColors.background,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: ClinicianUiColors.border),
                          ),
                          child: Row(
                            children: [
                              const Icon(
                                Icons.insert_drive_file_outlined,
                                size: 20,
                                color: ClinicianUiColors.primary,
                              ),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  report.assets[index],
                                  style: const TextStyle(
                                    color: ClinicianUiColors.text,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
        ),
      ],
    );
  }

  static Widget _observationRow(
    BuildContext context,
    ExaminationObservation observation,
  ) {
    final detail = [
      observation.reference,
      observation.interpretation,
    ].where((value) => value.isNotEmpty).join(' · ');
    final result = '${observation.value} ${observation.unit}'.trim();

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                observation.name.isEmpty ? '-' : observation.name,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: ClinicianUiColors.text,
                  fontWeight: FontWeight.w700,
                ),
              ),
              if (detail.isNotEmpty) ...[
                const SizedBox(height: 5),
                Text(
                  detail,
                  style: const TextStyle(
                    color: ClinicianUiColors.mutedText,
                    fontSize: 12,
                    height: 1.4,
                  ),
                ),
              ],
            ],
          ),
        ),
        if (result.isNotEmpty) ...[
          const SizedBox(width: 16),
          Flexible(
            child: Text(
              result,
              textAlign: TextAlign.end,
              style: const TextStyle(
                color: ClinicianUiColors.text,
                fontSize: 15,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
        ],
      ],
    );
  }

  static Widget _reportText(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: ClinicianUiColors.mutedText,
            fontSize: 13,
          ),
        ),
        const SizedBox(height: 6),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: ClinicianUiColors.background,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            value,
            style: const TextStyle(
              color: ClinicianUiColors.text,
              fontSize: 14,
              height: 1.55,
            ),
          ),
        ),
      ],
    );
  }

  static String _date(DateTime? value) {
    if (value == null) return '';
    final local = value.toLocal();
    return '${local.year}.${local.month.toString().padLeft(2, '0')}.${local.day.toString().padLeft(2, '0')}';
  }
}

ClinicianStatusTone _examinationStatusTone(String status) => switch (status) {
  'FINAL' || 'CORRECTED' => ClinicianStatusTone.success,
  'PRELIMINARY' || 'IN_PROGRESS' => ClinicianStatusTone.info,
  'CANCELLED' => ClinicianStatusTone.danger,
  _ => ClinicianStatusTone.neutral,
};

ClinicianStatusTone _interpretationTone(String interpretation) =>
    switch (interpretation) {
      'NORMAL' => ClinicianStatusTone.success,
      'CRITICAL' || 'ABNORMAL' => ClinicianStatusTone.danger,
      'HIGH' || 'LOW' => ClinicianStatusTone.warning,
      _ => ClinicianStatusTone.neutral,
    };

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
