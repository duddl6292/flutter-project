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

          return AppointmentDetailScreen(
            appointment: appointment,
          );
        },
      ),


    ],
  );

  ref.onDispose(router.dispose);
  return router;
});