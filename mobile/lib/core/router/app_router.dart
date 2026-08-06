import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/core/auth/auth_state.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/appointment/appointment_detail_screen.dart';
import 'package:brainon_mobile/features/appointment/appointment_list_screen.dart';
import 'package:brainon_mobile/features/appointment/hospital_select_screen.dart';
import 'package:brainon_mobile/features/auth/forgot_password_screen.dart';
import 'package:brainon_mobile/features/auth/login_screen.dart';
import 'package:brainon_mobile/features/auth/patient_signup_screen.dart';
import 'package:brainon_mobile/features/auth/role_selection_screen.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/features/clinician/clinician_main_screen.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_detail_model.dart';
import 'package:brainon_mobile/features/clinician/patients/clinician_patient_detail_screen.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_create_screen.dart';
import 'package:brainon_mobile/features/clinician/consultations/clinician_consultation_detail_screen.dart';
import 'package:brainon_mobile/features/clinician/prescriptions/clinician_prescription_create_screen.dart';
import 'package:brainon_mobile/features/clinician/prescriptions/clinician_prescription_detail_screen.dart';
import 'package:brainon_mobile/features/patient/patient_main_screen.dart';
import 'package:brainon_mobile/features/patient/medical_history/patient_medical_history_detail_screen.dart';
import 'package:brainon_mobile/features/patient/medical_history/patient_medical_history_screen.dart';
import 'package:brainon_mobile/features/patient/test_results/patient_test_result_detail_screen.dart';
import 'package:brainon_mobile/shared/models/appointment.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:brainon_mobile/features/patient/notification_settings_screen.dart'
    as notification_settings;
import 'package:brainon_mobile/features/patient/profile/personal_info_screen.dart'
    as personal_info;
import 'package:brainon_mobile/features/patient/support/app_info_screen.dart'
    as app_info;
import 'package:brainon_mobile/features/patient/profile/favorite_hospitals_screen.dart'
    as favorite_hospitals;

final appRouterProvider = Provider<GoRouter>((ref) {
  final authRefresh = _AuthRouterRefresh();
  ref.listen<AuthState>(authProvider, (_, _) => authRefresh.notify());
  final router = GoRouter(
    initialLocation: '/',
    refreshListenable: authRefresh,
    routes: [
      // ============================================================
      // 역할 선택
      // ============================================================
      GoRoute(
        path: '/',
        name: RouteNames.roleSelection,
        builder: (context, state) {
          return const RoleSelectionScreen();
        },
      ),

      // ============================================================
      // 로그인
      // ============================================================
      GoRoute(
        path: '/login',
        name: RouteNames.login,
        builder: (context, state) {
          final role = state.extra;

          if (role is! UserRole) {
            return const RoleSelectionScreen();
          }

          return LoginScreen(role: role);
        },
      ),

      // ============================================================
      // 환자 메인
      // ============================================================
      GoRoute(
        path: '/patient',
        name: RouteNames.patientMain,
        builder: (context, state) {
          return const PatientMainScreen();
        },
      ),

      // ============================================================
      // 의료진 홈
      // ============================================================
      GoRoute(
        path: '/clinician',
        name: RouteNames.clinicianHome,
        builder: (context, state) {
          return const ClinicianMainScreen();
        },
      ),
      GoRoute(
        path: '/clinician/patients/:patientId',
        name: RouteNames.clinicianPatientDetail,
        builder: (context, state) => ClinicianPatientDetailScreen(
          patientId: state.pathParameters['patientId']!,
        ),
      ),
      GoRoute(
        path: '/clinician/patients/:patientId/:resource',
        name: RouteNames.clinicianPatientResources,
        builder: (context, state) {
          final patient = state.extra;
          final type = PatientResourceType.values.firstWhere(
            (value) => value.name == state.pathParameters['resource'],
            orElse: () => PatientResourceType.medicalHistory,
          );
          if (patient is! ClinicianPatientDetail) {
            return ClinicianPatientDetailScreen(
              patientId: state.pathParameters['patientId']!,
            );
          }
          return ClinicianPatientResourceScreen(patient: patient, type: type);
        },
      ),
      GoRoute(
        path: '/clinician/examinations/:examinationId',
        name: RouteNames.clinicianExaminationDetail,
        builder: (context, state) => ClinicianExaminationDetailScreen(
          examinationId: state.pathParameters['examinationId']!,
        ),
      ),
      GoRoute(
        path: '/clinician/prescriptions/new',
        name: RouteNames.clinicianPrescriptionCreate,
        builder: (context, state) => const ClinicianPrescriptionCreateScreen(),
      ),
      GoRoute(
        path: '/clinician/prescriptions/:prescriptionId',
        name: RouteNames.clinicianPrescriptionDetail,
        builder: (context, state) => ClinicianPrescriptionDetailScreen(
          prescriptionId: state.pathParameters['prescriptionId']!,
        ),
      ),
      GoRoute(
        path: '/clinician/consultations/new',
        name: RouteNames.clinicianConsultationCreate,
        builder: (context, state) => const ClinicianConsultationCreateScreen(),
      ),
      GoRoute(
        path: '/clinician/consultations/:consultationId',
        name: RouteNames.clinicianConsultationDetail,
        builder: (context, state) => ClinicianConsultationDetailScreen(
          consultationId: state.pathParameters['consultationId']!,
        ),
      ),

      // ============================================================
      // 기존 환자 홈
      // ============================================================
      GoRoute(
        path: '/home',
        name: RouteNames.home,
        builder: (context, state) {
          return const PatientMainScreen();
        },
      ),
      // ============================================================
      // 환자 회원가입
      // ============================================================
      GoRoute(
        path: '/patient/signup',
        name: RouteNames.patientSignup,
        builder: (context, state) {
          return const PatientSignupScreen();
        },
      ),

      // ============================================================
      // 비밀번호 찾기
      // ============================================================
      GoRoute(
        path: '/forgot-password',
        name: RouteNames.forgotPassword,
        builder: (context, state) {
          return const ForgotPasswordScreen();
        },
      ),

      // ============================================================
      // 예약 목록
      // ============================================================
      GoRoute(
        path: '/appointments',
        name: RouteNames.appointments,
        builder: (context, state) {
          return const AppointmentListScreen();
        },
      ),

      // ============================================================
      // 예약 상세
      // ============================================================
      GoRoute(
        path: '/appointments/detail',
        name: RouteNames.appointmentDetail,
        builder: (context, state) {
          final appointment = state.extra;

          if (appointment is! Appointment) {
            return const AppointmentListScreen();
          }

          return AppointmentDetailScreen(appointment: appointment);
        },
      ),

      // ============================================================
      // 병원 선택
      // ============================================================
      GoRoute(
        path: '/appointments/hospital-select',
        name: RouteNames.hospitalSelect,
        builder: (context, state) {
          return const HospitalSelectScreen();
        },
      ),

      // ============================================================
      // 알림 설정
      // ============================================================
      GoRoute(
        path: '/notification-settings',
        name: RouteNames.notificationSettings,
        builder: (context, state) {
          return const notification_settings.NotificationSettingsScreen();
        },
      ),

      // ============================================================
      // 개인정보 관리
      // ============================================================
      GoRoute(
        path: '/personal-info',
        name: RouteNames.personalInfo,
        builder: (context, state) {
          return const personal_info.PersonalInfoScreen();
        },
      ),
      GoRoute(
        path: '/app-info',
        name: RouteNames.appInfo,
        builder: (context, state) {
          return const app_info.AppInfoScreen();
        },
      ),
      GoRoute(
        path: '/favorite-hospitals',
        name: RouteNames.favoriteHospitals,
        builder: (context, state) {
          return const favorite_hospitals.FavoriteHospitalsScreen();
        },
      ),
      GoRoute(
        path: '/patient/test-results/:testResultId',
        name: RouteNames.patientTestResultDetail,
        builder: (context, state) => PatientTestResultDetailScreen(
          testResultId: state.pathParameters['testResultId']!,
        ),
      ),
      GoRoute(
        path: '/patient/medical-history',
        name: RouteNames.patientMedicalHistory,
        builder: (context, state) => const PatientMedicalHistoryScreen(),
      ),
      GoRoute(
        path: '/patient/medical-history/:encounterId',
        name: RouteNames.patientMedicalHistoryDetail,
        builder: (context, state) => PatientMedicalHistoryDetailScreen(
          encounterId: state.pathParameters['encounterId']!,
        ),
      ),
    ],
    redirect: (context, state) {
      return authRedirect(ref.read(authProvider), state.matchedLocation);
    },
  );

  ref.onDispose(() {
    authRefresh.dispose();
    router.dispose();
  });

  return router;
});

class _AuthRouterRefresh extends ChangeNotifier {
  void notify() => notifyListeners();
}

String? authRedirect(AuthState authState, String location) {
  // 인증 상태를 복원하거나 로그인 처리 중일 때는
  // 라우터가 임의로 다른 화면으로 이동하지 않는다.
  if (authState.status == AuthStatus.restoring ||
      authState.status == AuthStatus.authenticating) {
    return null;
  }

  final isAuthenticated =
      authState.status == AuthStatus.authenticated && authState.user != null;

  // 역할 선택 화면과 로그인 화면
  final isEntryRoute = location == '/' || location == '/login';

  // ==========================================================
  // 임시 화면 확인용 공개 경로
  //
  // 로그인 API가 연결되기 전까지
  // 환자·의료진 메인 화면 접근을 임시 허용한다.
  //
  // 실제 인증 연결 후에는
  // location == '/patient'
  // location == '/clinician'
  // 두 줄을 삭제한다.
  // ==========================================================
  final isPublicRoute =
      isEntryRoute ||
      location == '/patient/signup' ||
      location == '/forgot-password' ||
      location == '/patient' ||
      location == '/clinician';

  // 로그인하지 않은 사용자는 공개 화면만 접근 가능
  if (!isAuthenticated) {
    return isPublicRoute ? null : '/';
  }

  final role = authState.user!.role;

  final home = role == UserRole.clinician ? '/clinician' : '/patient';

  // 인증된 사용자가 역할 선택 또는 로그인 화면에 접근하면
  // 해당 역할의 메인 화면으로 이동
  if (isEntryRoute) {
    return home;
  }

  final isClinicianRoute = location.startsWith('/clinician');

  final isPatientRoute =
      location == '/patient' ||
      location == '/home' ||
      location.startsWith('/appointments') ||
      location == '/notification-settings' ||
      location == '/personal-info' ||
      location == '/app-info' ||
      location == '/favorite-hospitals' ||
      location.startsWith('/patient/test-results/') ||
      location.startsWith('/patient/medical-history');

  // 의료진이 환자 전용 화면으로 접근한 경우
  if (role == UserRole.clinician && isPatientRoute) {
    return home;
  }

  // 환자가 의료진 전용 화면으로 접근한 경우
  if (role == UserRole.patient && isClinicianRoute) {
    return home;
  }

  return null;
}
