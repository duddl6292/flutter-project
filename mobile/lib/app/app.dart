import 'package:brainon_mobile/app/app_theme.dart';
import 'package:brainon_mobile/core/router/app_router.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class BrainOnApp extends ConsumerWidget {
  const BrainOnApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: '호닥',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      routerConfig: router,

      locale: const Locale('ko', 'KR'),

      supportedLocales: const [Locale('ko', 'KR'), Locale('en', 'US')],

      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
    );
  }
}
