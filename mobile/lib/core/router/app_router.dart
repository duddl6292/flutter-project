import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/appointment/appointment_create_screen.dart';
import 'package:brainon_mobile/features/appointment/appointment_detail_screen.dart';
import 'package:brainon_mobile/features/appointment/appointment_list_screen.dart';
import 'package:brainon_mobile/features/appointment/hospital_select_screen.dart';
import 'package:brainon_mobile/features/auth/forgot_password_screen.dart';
import 'package:brainon_mobile/features/auth/login_screen.dart';
import 'package:brainon_mobile/features/auth/patient_signup_screen.dart';
import 'package:brainon_mobile/features/auth/role_selection_screen.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/features/patient/patient_main_screen.dart';
import 'package:brainon_mobile/shared/models/appointment.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final router = GoRouter(
    initialLocation: '/',
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
      // 예약 생성
      // ============================================================
      GoRoute(
        path: '/appointments/create',
        name: RouteNames.appointmentCreate,
        builder: (context, state) {
          return const AppointmentCreateScreen();
        },
      ),
    ],
  );

  ref.onDispose(router.dispose);

  return router;
});
