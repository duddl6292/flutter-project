import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class CustomerServiceScreen extends StatelessWidget {
  const CustomerServiceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('고객센터')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Card(
            child: Column(
              children: [
                ExpansionTile(
                  title: Text('로그인이 되지 않아요'),
                  childrenPadding: EdgeInsets.all(16),
                  children: [Text('아이디와 역할을 확인하고, 계속 실패하면 비밀번호 찾기를 이용해 주세요.')],
                ),
                ExpansionTile(
                  title: Text('알림이 오지 않아요'),
                  childrenPadding: EdgeInsets.all(16),
                  children: [
                    Text('휴대전화 설정에서 BrainOn 알림 권한을 허용하고 앱의 푸시 알림 설정도 확인해 주세요.'),
                  ],
                ),
                ExpansionTile(
                  title: Text('의료 정보가 다르게 보여요'),
                  childrenPadding: EdgeInsets.all(16),
                  children: [
                    Text('의료 정보는 담당 병원에서 등록합니다. 내용이 다르면 담당 의료진에게 문의해 주세요.'),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          ListTile(
            leading: const Icon(Icons.email_outlined),
            title: const Text('이메일 문의'),
            subtitle: const Text('support@brainon.kr'),
            trailing: const Icon(Icons.copy),
            onTap: () async {
              await Clipboard.setData(
                const ClipboardData(text: 'support@brainon.kr'),
              );
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('이메일 주소를 복사했습니다.')),
                );
              }
            },
          ),
          const ListTile(
            leading: Icon(Icons.schedule),
            title: Text('상담 시간'),
            subtitle: Text('평일 09:00~18:00 (공휴일 제외)'),
          ),
        ],
      ),
    );
  }
}
