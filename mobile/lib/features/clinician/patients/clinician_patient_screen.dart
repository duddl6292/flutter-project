import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_model.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_ui.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class ClinicianPatientScreen extends ConsumerStatefulWidget {
  const ClinicianPatientScreen({required this.onOpenDrawer, super.key});
  final VoidCallback onOpenDrawer;

  @override
  ConsumerState<ClinicianPatientScreen> createState() =>
      _ClinicianPatientScreenState();
}

class _ClinicianPatientScreenState
    extends ConsumerState<ClinicianPatientScreen> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final patients = ref.watch(clinicianPatientsProvider);
    return ClinicianPageScaffold(
      title: '환자 검색',
      onOpenDrawer: widget.onOpenDrawer,
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 8, 20, 18),
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x0A172033),
                    blurRadius: 16,
                    offset: Offset(0, 5),
                  ),
                ],
              ),
              child: TextField(
                controller: _searchController,
                onChanged: (_) => setState(() {}),
                textInputAction: TextInputAction.search,
                style: const TextStyle(
                  color: ClinicianUiColors.text,
                  fontSize: 15,
                ),
                decoration: InputDecoration(
                  hintText: '이름, 등록번호 또는 전화번호 검색',
                  hintStyle: const TextStyle(color: Color(0xFF929AAA)),
                  prefixIcon: const Icon(
                    Icons.search_rounded,
                    color: Color(0xFF566174),
                  ),
                  filled: true,
                  fillColor: ClinicianUiColors.surface,
                  contentPadding: const EdgeInsets.symmetric(vertical: 15),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(
                      color: ClinicianUiColors.border,
                    ),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(
                      color: ClinicianUiColors.border,
                    ),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: const BorderSide(
                      color: ClinicianUiColors.primary,
                      width: 1.5,
                    ),
                  ),
                ),
              ),
            ),
          ),
          Expanded(
            child: patients.when(
              loading: () => const ClinicianLoadingView(),
              error: (error, _) => ClinicianErrorView(
                message: error.toString(),
                onRetry: () => ref.invalidate(clinicianPatientsProvider),
              ),
              data: (items) {
                final query = _searchController.text.trim().toLowerCase();
                final filtered = items.where((patient) {
                  return '${patient.name}${patient.registrationNumber}${patient.phone}'
                      .toLowerCase()
                      .contains(query);
                }).toList();

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(20, 0, 20, 12),
                      child: Text.rich(
                        TextSpan(
                          text: '검색 결과 ',
                          children: [
                            TextSpan(
                              text: '${filtered.length}명',
                              style: const TextStyle(
                                color: ClinicianUiColors.primary,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ],
                        ),
                        style: const TextStyle(
                          color: ClinicianUiColors.mutedText,
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    Expanded(
                      child: filtered.isEmpty
                          ? const ClinicianEmptyView(
                              message: '검색 결과가 없습니다.',
                              icon: Icons.person_search_rounded,
                            )
                          : ListView.builder(
                              keyboardDismissBehavior:
                                  ScrollViewKeyboardDismissBehavior.onDrag,
                              padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
                              itemCount: filtered.length,
                              itemBuilder: (context, index) {
                                final patient = filtered[index];
                                return _PatientTile(
                                  patient: patient,
                                  onTap: () => context.pushNamed(
                                    RouteNames.clinicianPatientDetail,
                                    pathParameters: {'patientId': patient.id},
                                  ),
                                );
                              },
                            ),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _PatientTile extends StatelessWidget {
  const _PatientTile({required this.patient, required this.onTap});
  final ClinicianPatient patient;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final age = patient.age;
    final trimmedName = patient.name.trim();
    final secondaryParts = <String>[
      if (patient.sex.trim().isNotEmpty) patient.sex,
      if (age != null) '$age세',
    ];
    final normalizedStatus = patient.status.trim().toUpperCase();

    return ClinicianListCard(
      onTap: onTap,
      child: Row(
        children: [
          CircleAvatar(
            radius: 27,
            backgroundColor: const Color(0xFFE7F0FF),
            child: trimmedName.isEmpty
                ? const Icon(
                    Icons.person_outline_rounded,
                    color: ClinicianUiColors.primary,
                    size: 27,
                  )
                : Text(
                    trimmedName.substring(0, 1),
                    style: const TextStyle(
                      color: ClinicianUiColors.primary,
                      fontSize: 21,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  patient.name,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: ClinicianUiColors.text,
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                if (secondaryParts.isNotEmpty) ...[
                  const SizedBox(height: 5),
                  Text(
                    secondaryParts.join(' · '),
                    style: const TextStyle(
                      color: ClinicianUiColors.mutedText,
                      fontSize: 13,
                      height: 1.3,
                    ),
                  ),
                ],
                const SizedBox(height: 4),
                Text(
                  patient.registrationNumber,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: ClinicianUiColors.mutedText,
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          if (patient.status.trim().isNotEmpty) ...[
            ClinicianStatusBadge(
              label: patient.status,
              tone: normalizedStatus == 'ACTIVE'
                  ? ClinicianStatusTone.success
                  : ClinicianStatusTone.neutral,
            ),
            const SizedBox(width: 6),
          ],
          const Icon(Icons.chevron_right_rounded, color: Color(0xFF667085)),
        ],
      ),
    );
  }
}
