import 'package:flutter/material.dart';

class NoticeListScreen extends StatelessWidget {
  const NoticeListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final notices = [
      ('BrainOn 서비스 안내', '예약·복약·검사 결과 알림을 앱에서 확인할 수 있습니다.'),
      ('AI 상담 이용 안내', 'AI 답변은 건강 정보 제공을 위한 참고 자료이며 진단을 대신하지 않습니다.'),
      ('응급 상황 안내', '응급 증상이 있으면 앱 답변을 기다리지 말고 즉시 119 또는 응급실을 이용하세요.'),
    ];
    return Scaffold(
      appBar: AppBar(title: const Text('공지사항')),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: notices.length,
        separatorBuilder: (_, _) => const SizedBox(height: 8),
        itemBuilder: (context, index) => Card(
          child: ExpansionTile(
            leading: const Icon(Icons.campaign_outlined),
            title: Text(
              notices[index].$1,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
            childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 18),
            children: [
              Align(
                alignment: Alignment.centerLeft,
                child: Text(notices[index].$2),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
