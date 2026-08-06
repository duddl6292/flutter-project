import 'package:brainon_mobile/features/clinician/patients/clinician_patient_detail_model.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_detail_repository.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final clinicianPatientDetailProvider =
    FutureProvider.family<ClinicianPatientDetail, String>((ref, patientId) {
      return ref
          .watch(clinicianPatientDetailRepositoryProvider)
          .fetchDetail(patientId);
    });

final clinicianExaminationDetailProvider =
    FutureProvider.family<ClinicianExamination, String>((ref, examinationId) {
      return ref
          .watch(clinicianPatientDetailRepositoryProvider)
          .fetchExamination(examinationId);
    });

typedef PatientResourceRequest = ({
  ClinicianPatientDetail patient,
  PatientResourceType type,
});

final clinicianPatientResourcesProvider =
    FutureProvider.family<List<PatientResourceItem>, PatientResourceRequest>((
      ref,
      request,
    ) {
      return ref
          .watch(clinicianPatientDetailRepositoryProvider)
          .fetchResources(patient: request.patient, type: request.type);
    });
