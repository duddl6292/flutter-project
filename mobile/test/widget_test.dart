import 'package:brainon_mobile/app/app.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('BrainOn home screen is displayed', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: BrainOnApp()));
    await tester.pumpAndSettle();

    expect(find.text('BrainOn'), findsOneWidget);
    expect(find.text('환자용 뇌졸중 관리 서비스'), findsOneWidget);
  });
}
