import 'package:brainon_mobile/app/app.dart';
import 'package:brainon_mobile/features/home/home_screen.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Home screen is displayed', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: BrainOnApp(),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.byType(HomeScreen), findsOneWidget);
  });
}