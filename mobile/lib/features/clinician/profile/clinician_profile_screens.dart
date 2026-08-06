import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/features/clinician/profile/clinician_notification_settings_model.dart';
import 'package:brainon_mobile/features/clinician/profile/clinician_profile_provider.dart';
import 'package:brainon_mobile/features/clinician/profile/clinician_profile_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class ClinicianAccountScreen extends ConsumerStatefulWidget {
  const ClinicianAccountScreen({super.key});

  @override
  ConsumerState<ClinicianAccountScreen> createState() =>
      _ClinicianAccountScreenState();
}

class _ClinicianAccountScreenState
    extends ConsumerState<ClinicianAccountScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  bool _initialized = false;
  bool _saving = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authProvider).user;
    final clinician = user?.role == UserRole.clinician ? user?.clinician : null;
    if (!_initialized) {
      _emailController.text = user?.email ?? '';
      _initialized = true;
    }
    return Scaffold(
      appBar: AppBar(title: const Text('내 정보 관리')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _InfoCard(
            children: [
              _InfoRow(label: '이름', value: clinician?.name ?? '-'),
              _InfoRow(label: '아이디', value: user?.username ?? '-'),
              _InfoRow(
                label: '면허번호',
                value: clinician?.licenseNumber ?? '-',
              ),
              _InfoRow(
                label: '승인 상태',
                value: clinician?.approvalStatus ?? '-',
              ),
            ],
          ),
          const SizedBox(height: 16),
          Form(
            key: _formKey,
            child: TextFormField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(
                labelText: '이메일',
                border: OutlineInputBorder(),
              ),
              validator: (value) {
                final email = value?.trim() ?? '';
                if (email.isEmpty || !email.contains('@')) {
                  return '올바른 이메일을 입력해주세요.';
                }
                return null;
              },
            ),
          ),
          const SizedBox(height: 16),
          FilledButton(
            onPressed: _saving ? null : _save,
            child: Text(_saving ? '저장 중...' : '이메일 저장'),
          ),
          const SizedBox(height: 12),
          const Text(
            '이름, 면허번호, 소속 병원과 진료과는 현재 API에서 수정할 수 없습니다.',
            style: TextStyle(color: Color(0xFF6B7280)),
          ),
        ],
      ),
    );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      await ref
          .read(authProvider.notifier)
          .updateEmail(_emailController.text.trim());
      if (mounted) _message('이메일을 저장했습니다.');
    } on Object catch (error) {
      if (mounted) _message(_errorMessage(error, '이메일을 저장하지 못했습니다.'));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  void _message(String value) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(value)));
  }
}

class ClinicianHospitalInfoScreen extends ConsumerWidget {
  const ClinicianHospitalInfoScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final clinician = ref.watch(authProvider).user?.clinician;
    return Scaffold(
      appBar: AppBar(title: const Text('근무 병원 정보')),
      body: RefreshIndicator(
        onRefresh: () => ref.read(authProvider.notifier).refreshAccount(),
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          children: [
            _InfoCard(
              children: [
                _InfoRow(label: '병원', value: clinician?.hospitalName ?? '-'),
                _InfoRow(label: '병원 ID', value: clinician?.hospitalId ?? '-'),
                _InfoRow(
                  label: '진료과',
                  value: clinician?.departmentName ?? '-',
                ),
                _InfoRow(
                  label: '진료과 코드',
                  value: clinician?.departmentCode ?? '-',
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              '근무 병원과 진료과는 현재 API에서 변경할 수 없습니다.',
              style: TextStyle(color: Color(0xFF6B7280)),
            ),
          ],
        ),
      ),
    );
  }
}

class ClinicianPasswordChangeScreen extends ConsumerStatefulWidget {
  const ClinicianPasswordChangeScreen({super.key});

  @override
  ConsumerState<ClinicianPasswordChangeScreen> createState() =>
      _ClinicianPasswordChangeScreenState();
}

class _ClinicianPasswordChangeScreenState
    extends ConsumerState<ClinicianPasswordChangeScreen> {
  final _formKey = GlobalKey<FormState>();
  final _current = TextEditingController();
  final _next = TextEditingController();
  final _confirm = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    _current.dispose();
    _next.dispose();
    _confirm.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('비밀번호 변경')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            _passwordField(_current, '현재 비밀번호'),
            const SizedBox(height: 14),
            _passwordField(_next, '새 비밀번호'),
            const SizedBox(height: 14),
            _passwordField(_confirm, '새 비밀번호 확인'),
            const SizedBox(height: 20),
            FilledButton(
              onPressed: _saving ? null : _save,
              child: Text(_saving ? '변경 중...' : '비밀번호 변경'),
            ),
          ],
        ),
      ),
    );
  }

  TextFormField _passwordField(TextEditingController controller, String label) {
    return TextFormField(
      controller: controller,
      obscureText: true,
      decoration: InputDecoration(labelText: label, border: const OutlineInputBorder()),
      validator: (value) {
        if ((value ?? '').length < 8) return '8자 이상 입력해주세요.';
        return null;
      },
    );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    if (_next.text != _confirm.text) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('새 비밀번호가 일치하지 않습니다.')),
      );
      return;
    }
    setState(() => _saving = true);
    try {
      await ref.read(authRepositoryProvider).changePassword(
            currentPassword: _current.text,
            newPassword: _next.text,
            newPasswordConfirm: _confirm.text,
          );
      await ref.read(authProvider.notifier).logout();
      if (mounted) context.go('/');
    } on Object catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(_errorMessage(error, '비밀번호를 변경하지 못했습니다.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }
}

class ClinicianNotificationSettingsScreen extends ConsumerStatefulWidget {
  const ClinicianNotificationSettingsScreen({super.key});

  @override
  ConsumerState<ClinicianNotificationSettingsScreen> createState() =>
      _ClinicianNotificationSettingsScreenState();
}

class _ClinicianNotificationSettingsScreenState
    extends ConsumerState<ClinicianNotificationSettingsScreen> {
  ClinicianNotificationSettings? _draft;
  bool _saving = false;

  @override
  Widget build(BuildContext context) {
    final value = ref.watch(clinicianNotificationSettingsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('알림 설정')),
      body: value.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(
          child: OutlinedButton(
            onPressed: () => ref.invalidate(clinicianNotificationSettingsProvider),
            child: Text(_errorMessage(error, '알림 설정을 불러오지 못했습니다.')),
          ),
        ),
        data: (settings) {
          final draft = _draft ?? settings;
          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              SwitchListTile(
                title: const Text('방해금지 시간'),
                value: draft.quietHoursEnabled,
                onChanged: (enabled) => setState(() {
                  _draft = _copySettings(
                    draft,
                    quietHoursEnabled: enabled,
                    quietHoursStart: draft.quietHoursStart ?? '22:00',
                    quietHoursEnd: draft.quietHoursEnd ?? '07:00',
                  );
                }),
              ),
              if (draft.quietHoursEnabled)
                ListTile(
                  title: const Text('방해금지 시간대'),
                  subtitle: Text(
                    '${draft.quietHoursStart ?? '-'} ~ ${draft.quietHoursEnd ?? '-'}',
                  ),
                  onTap: () => _selectQuietHours(draft),
                ),
              const Divider(),
              for (var index = 0; index < draft.preferences.length; index++)
                _PreferenceCard(
                  preference: draft.preferences[index],
                  onChanged: (updated) => setState(() {
                    final preferences = [...draft.preferences];
                    preferences[index] = updated;
                    _draft = _copySettings(draft, preferences: preferences);
                  }),
                ),
              const SizedBox(height: 20),
              FilledButton(
                onPressed: _saving ? null : () => _save(draft),
                child: Text(_saving ? '저장 중...' : '설정 저장'),
              ),
            ],
          );
        },
      ),
    );
  }

  Future<void> _selectQuietHours(ClinicianNotificationSettings draft) async {
    final start = await showTimePicker(
      context: context,
      initialTime: _time(draft.quietHoursStart, const TimeOfDay(hour: 22, minute: 0)),
    );
    if (start == null || !mounted) return;
    final end = await showTimePicker(
      context: context,
      initialTime: _time(draft.quietHoursEnd, const TimeOfDay(hour: 7, minute: 0)),
    );
    if (end == null || !mounted) return;
    setState(() {
      _draft = _copySettings(
        draft,
        quietHoursStart: _formatTime(start),
        quietHoursEnd: _formatTime(end),
      );
    });
  }

  Future<void> _save(ClinicianNotificationSettings settings) async {
    setState(() => _saving = true);
    try {
      final updated = await ref
          .read(clinicianProfileRepositoryProvider)
          .updateNotificationSettings(settings);
      if (mounted) setState(() => _draft = updated);
      ref.invalidate(clinicianNotificationSettingsProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('알림 설정을 저장했습니다.')),
        );
      }
    } on Object catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(_errorMessage(error, '알림 설정을 저장하지 못했습니다.'))),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }
}

class ClinicianVersionInfoScreen extends StatelessWidget {
  const ClinicianVersionInfoScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('버전 정보')),
      body: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.health_and_safety_outlined, size: 52),
            SizedBox(height: 14),
            Text('BrainOn Mobile', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
            SizedBox(height: 8),
            Text('버전 1.0.0+1'),
          ],
        ),
      ),
    );
  }
}

class _PreferenceCard extends StatelessWidget {
  const _PreferenceCard({required this.preference, required this.onChanged});

  final ClinicianNotificationPreference preference;
  final ValueChanged<ClinicianNotificationPreference> onChanged;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      child: Column(
        children: [
          ListTile(title: Text(_notificationLabel(preference.type))),
          SwitchListTile(
            title: const Text('푸시 알림'),
            value: preference.pushEnabled,
            onChanged: (value) => onChanged(preference.copyWith(pushEnabled: value)),
          ),
          SwitchListTile(
            title: const Text('이메일 알림'),
            value: preference.emailEnabled,
            onChanged: (value) => onChanged(preference.copyWith(emailEnabled: value)),
          ),
        ],
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.children});
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(children: children),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 9),
      child: Row(
        children: [
          SizedBox(width: 90, child: Text(label, style: const TextStyle(color: Color(0xFF6B7280)))),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}

ClinicianNotificationSettings _copySettings(
  ClinicianNotificationSettings source, {
  bool? quietHoursEnabled,
  String? quietHoursStart,
  String? quietHoursEnd,
  List<ClinicianNotificationPreference>? preferences,
}) {
  return ClinicianNotificationSettings(
    quietHoursEnabled: quietHoursEnabled ?? source.quietHoursEnabled,
    quietHoursStart: quietHoursStart ?? source.quietHoursStart,
    quietHoursEnd: quietHoursEnd ?? source.quietHoursEnd,
    preferences: preferences ?? source.preferences,
  );
}

TimeOfDay _time(String? value, TimeOfDay fallback) {
  final parts = value?.split(':') ?? const [];
  if (parts.length < 2) return fallback;
  return TimeOfDay(
    hour: int.tryParse(parts[0]) ?? fallback.hour,
    minute: int.tryParse(parts[1]) ?? fallback.minute,
  );
}

String _formatTime(TimeOfDay value) {
  return '${value.hour.toString().padLeft(2, '0')}:'
      '${value.minute.toString().padLeft(2, '0')}';
}

String _notificationLabel(String type) => switch (type) {
  'APPOINTMENT' => '진료 예약',
  'TEST_RESULT' => '검사 결과',
  'CONSULTATION' => '협진',
  'SYSTEM' => '시스템',
  _ => type,
};

String _errorMessage(Object error, String fallback) {
  return error is ApiException ? error.message : fallback;
}
