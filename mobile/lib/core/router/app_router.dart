import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/appointment/appointment_list_screen.dart';
import 'package:brainon_mobile/features/auth/login_screen.dart';
//import 'package:brainon_mobile/features/clinician/clinician_home_screen.dart';
import 'package:brainon_mobile/features/auth/role_selection_screen.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/features/home/home_screen.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:brainon_mobile/features/appointment/appointment_detail_screen.dart';
import 'package:brainon_mobile/shared/models/appointment.dart';
import 'package:brainon_mobile/features/auth/patient_signup_screen.dart';
import 'package:brainon_mobile/features/auth/forgot_password_screen.dart';
import 'package:brainon_mobile/features/appointment/hospital_select_screen.dart';
import 'package:brainon_mobile/features/appointment/appointment_create_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final router = GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/home',
        name: RouteNames.home,
        builder: (context, state) {
          return const HomeScreen();
        },
      ),

      GoRoute(
        path: '/',
        name: RouteNames.roleSelection,
        builder: (context, state) {
          return const RoleSelectionScreen();
        },
      ),

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

      GoRoute(
        //회원가입
        path: '/patient/signup',
        name: RouteNames.patientSignup,
        builder: (context, state) {
          return const PatientSignupScreen();
        },
      ),

      GoRoute(
        //비밀번호 찾기 화면
        path: '/forgot-password',
        name: RouteNames.forgotPassword,
        builder: (context, state) {
          return const ForgotPasswordScreen();
        },
      ),

      GoRoute(
        path: '/appointments',
        name: RouteNames.appointments,
        builder: (context, state) {
          return const AppointmentListScreen();
        },
      ),

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

      GoRoute(
        path: '/appointments/hospital-select',
        name: RouteNames.hospitalSelect,
        builder: (context, state) {
          return const HospitalSelectScreen();
        },
      ),

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
