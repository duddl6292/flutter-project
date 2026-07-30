import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/home/home_screen.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final router = GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        name: RouteNames.home,
        builder: (context, state) => const HomeScreen(),
      ),
    ],
  );
  ref.onDispose(router.dispose);
  return router;
});
