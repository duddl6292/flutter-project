import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_model.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_provider.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_tab_header.dart';
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
    return ColoredBox(
      color: const Color(0xFFF6F8FC),
      child: SafeArea(
        bottom: false,
        child: Column(
          children: [
            ClinicianTabHeader(
              title: '환자 검색',
              onOpenDrawer: widget.onOpenDrawer,
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 14),
              child: TextField(
                controller: _searchController,
                onChanged: (_) => setState(() {}),
                decoration: InputDecoration(
                  hintText: '이름, 등록번호 또는 전화번호 검색',
                  prefixIcon: const Icon(Icons.search_rounded),
                  filled: true,
                  fillColor: Colors.white,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
              ),
            ),
            Expanded(
              child: patients.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (error, _) => Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(error.toString(), textAlign: TextAlign.center),
                      const SizedBox(height: 12),
                      FilledButton(
                        onPressed: () =>
                            ref.invalidate(clinicianPatientsProvider),
                        child: const Text('다시 시도'),
                      ),
                    ],
                  ),
                ),
                data: (items) {
                  final query = _searchController.text.trim().toLowerCase();
                  final filtered = items.where((patient) {
                    return '${patient.name}${patient.registrationNumber}${patient.phone}'
                        .toLowerCase()
                        .contains(query);
                  }).toList();
                  if (filtered.isEmpty) {
                    return const Center(child: Text('검색된 환자가 없습니다.'));
                  }
                  return ListView.builder(
                    padding: const EdgeInsets.fromLTRB(20, 8, 20, 24),
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
                  );
                },
              ),
            ),
          ],
        ),
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
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      elevation: 0,
      child: ListTile(
        onTap: onTap,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: CircleAvatar(
          child: Text(
            patient.name.isEmpty ? '?' : patient.name.substring(0, 1),
          ),
        ),
        title: Text(
          patient.name,
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
        subtitle: Text(
          '${patient.sex}${age == null ? '' : ' / $age'}\n${patient.registrationNumber}',
        ),
        trailing: const Icon(Icons.chevron_right_rounded),
      ),
    );
  }
}
