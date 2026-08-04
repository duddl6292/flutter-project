import 'package:flutter/material.dart';

class NotificationSettingsScreen extends StatefulWidget {
  const NotificationSettingsScreen({super.key});

  @override
  State<NotificationSettingsScreen> createState() =>
      _NotificationSettingsScreenState();
}

class _NotificationSettingsScreenState
    extends State<NotificationSettingsScreen> {
  bool _appointmentNotification = true;
  bool _medicationNotification = true;
  bool _testResultNotification = true;

  bool _pushNotification = true;
  bool _emailNotification = false;

  bool _doNotDisturb = false;

  TimeOfDay _startTime = const TimeOfDay(hour: 22, minute: 0);

  TimeOfDay _endTime = const TimeOfDay(hour: 7, minute: 0);

  static const Color _backgroundColor = Color(0xFFF7F9FC);
  static const Color _primaryTextColor = Color(0xFF111827);
  static const Color _secondaryTextColor = Color(0xFF6B7280);
  static const Color _borderColor = Color(0xFFE5E7EB);
  static const Color _iconBackgroundColor = Color(0xFFEAF2FA);
  static const Color _primaryColor = Color(0xFF28669E);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _backgroundColor,
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          tooltip: '뒤로가기',
          onPressed: () {
            Navigator.of(context).pop();
          },
          icon: const Icon(Icons.arrow_back_rounded, color: _primaryTextColor),
        ),
        title: const Text(
          '알림 설정',
          style: TextStyle(
            color: _primaryTextColor,
            fontSize: 20,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 36),
          children: [
            _buildSectionTitle('알림 유형'),
            const SizedBox(height: 10),
            _buildSettingsCard(
              children: [
                _buildSwitchTile(
                  icon: Icons.calendar_month_outlined,
                  title: '진료 예약 알림',
                  subtitle: '예약 확정 및 진료 일정을 알려드려요.',
                  value: _appointmentNotification,
                  onChanged: (value) {
                    setState(() {
                      _appointmentNotification = value;
                    });
                  },
                ),
                _buildDivider(),
                _buildSwitchTile(
                  icon: Icons.medication_outlined,
                  title: '복약 알림',
                  subtitle: '약을 복용할 시간을 알려드려요.',
                  value: _medicationNotification,
                  onChanged: (value) {
                    setState(() {
                      _medicationNotification = value;
                    });
                  },
                ),
                _buildDivider(),
                _buildSwitchTile(
                  icon: Icons.description_outlined,
                  title: '검사결과 알림',
                  subtitle: '새 검사결과가 등록되면 알려드려요.',
                  value: _testResultNotification,
                  onChanged: (value) {
                    setState(() {
                      _testResultNotification = value;
                    });
                  },
                ),
              ],
            ),
            const SizedBox(height: 24),

            _buildSectionTitle('알림 수신 방법'),
            const SizedBox(height: 10),
            _buildSettingsCard(
              children: [
                _buildSwitchTile(
                  icon: Icons.notifications_active_outlined,
                  title: '앱 푸시 알림',
                  subtitle: '휴대전화 알림으로 받아요.',
                  value: _pushNotification,
                  onChanged: (value) {
                    setState(() {
                      _pushNotification = value;
                    });
                  },
                ),

                _buildDivider(),
                _buildSwitchTile(
                  icon: Icons.email_outlined,
                  title: '이메일 알림',
                  subtitle: '등록된 이메일로 알림을 받아요.',
                  value: _emailNotification,
                  onChanged: (value) {
                    setState(() {
                      _emailNotification = value;
                    });
                  },
                ),
              ],
            ),

            const SizedBox(height: 24),

            _buildSectionTitle('방해금지 시간'),
            const SizedBox(height: 10),
            _buildSettingsCard(
              children: [
                _buildSwitchTile(
                  icon: Icons.nightlight_outlined,
                  title: '방해금지 모드',
                  subtitle: '설정한 시간에는 알림을 보내지 않아요.',
                  value: _doNotDisturb,
                  onChanged: (value) {
                    setState(() {
                      _doNotDisturb = value;
                    });
                  },
                ),
                if (_doNotDisturb) ...[
                  _buildDivider(),
                  _buildTimeTile(
                    title: '시작 시간',
                    time: _startTime,
                    onTap: () {
                      _selectStartTime();
                    },
                  ),
                  _buildDivider(),
                  _buildTimeTile(
                    title: '종료 시간',
                    time: _endTime,
                    onTap: () {
                      _selectEndTime();
                    },
                  ),
                ],
              ],
            ),
            const SizedBox(height: 28),

            SizedBox(
              width: double.infinity,
              height: 54,
              child: FilledButton(
                onPressed: _saveSettings,
                style: FilledButton.styleFrom(
                  backgroundColor: _primaryColor,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: const Text(
                  '변경사항 저장',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4),
      child: Text(
        title,
        style: const TextStyle(
          color: _primaryTextColor,
          fontSize: 16,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }

  Widget _buildSettingsCard({required List<Widget> children}) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _borderColor),
      ),
      child: Column(children: children),
    );
  }

  Widget _buildSwitchTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: _iconBackgroundColor,
              borderRadius: BorderRadius.circular(13),
            ),
            child: Icon(icon, color: _primaryColor, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: _primaryTextColor,
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: const TextStyle(
                    color: _secondaryTextColor,
                    fontSize: 12,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
          Switch(value: value, onChanged: onChanged),
        ],
      ),
    );
  }

  Widget _buildTimeTile({
    required String title,
    required TimeOfDay time,
    required VoidCallback onTap,
  }) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 4),
      title: Text(
        title,
        style: const TextStyle(
          color: _primaryTextColor,
          fontSize: 15,
          fontWeight: FontWeight.w700,
        ),
      ),
      trailing: TextButton(
        onPressed: onTap,
        child: Text(
          time.format(context),
          style: const TextStyle(
            color: _primaryColor,
            fontSize: 15,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
    );
  }

  Widget _buildDivider() {
    return const Divider(
      height: 1,
      thickness: 1,
      indent: 72,
      endIndent: 16,
      color: _borderColor,
    );
  }

  Future<void> _selectStartTime() async {
    final selectedTime = await showTimePicker(
      context: context,
      initialTime: _startTime,
      helpText: '방해금지 시작 시간',
      cancelText: '취소',
      confirmText: '선택',
    );

    if (selectedTime == null || !mounted) {
      return;
    }

    setState(() {
      _startTime = selectedTime;
    });
  }

  Future<void> _selectEndTime() async {
    final selectedTime = await showTimePicker(
      context: context,
      initialTime: _endTime,
      helpText: '방해금지 종료 시간',
      cancelText: '취소',
      confirmText: '선택',
    );

    if (selectedTime == null || !mounted) {
      return;
    }

    setState(() {
      _endTime = selectedTime;
    });
  }

  void _saveSettings() {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        const SnackBar(
          content: Text('알림 설정이 저장되었습니다.'),
          behavior: SnackBarBehavior.floating,
        ),
      );
  }
}
