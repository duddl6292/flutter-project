import 'package:brainon_mobile/core/api/api_exception.dart';
import 'package:brainon_mobile/core/auth/auth_provider.dart';
import 'package:brainon_mobile/features/auth/user_role.dart';
import 'package:brainon_mobile/features/clinician/profile/clinician_notification_settings_model.dart';
import 'package:brainon_mobile/features/clinician/profile/clinician_profile_provider.dart';
import 'package:brainon_mobile/features/clinician/profile/clinician_profile_repository.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_ui.dart';
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
    final approvalStatus = clinician?.approvalStatus ?? '';
    if (!_initialized) {
      _emailController.text = user?.email ?? '';
      _initialized = true;
    }
    return _ProfileScreenScaffold(
      title: '내 정보 관리',
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
        children: [
          _ProfileSummaryCard(
            icon: Icons.person_rounded,
            title: _displayValue(clinician?.name),
            subtitle: _displayValue(clinician?.departmentName),
            status: approvalStatus,
          ),
          ClinicianSectionCard(
            title: '기본 정보',
            child: Column(
              children: [
                ClinicianInfoRow(
                  label: '이름',
                  value: _displayValue(clinician?.name),
                ),
                const _InfoDivider(),
                ClinicianInfoRow(
                  label: '아이디',
                  value: _displayValue(user?.username),
                ),
                const _InfoDivider(),
                ClinicianInfoRow(
                  label: '면허번호',
                  value: _displayValue(clinician?.licenseNumber),
                ),
                const _InfoDivider(),
                ClinicianInfoRow(
                  label: '승인 상태',
                  value: _displayValue(approvalStatus),
                  valueWidget: approvalStatus.isEmpty
                      ? null
                      : Align(
                          alignment: Alignment.centerLeft,
                          child: ClinicianStatusBadge(
                            label: approvalStatus,
                            tone: _statusTone(approvalStatus),
                            icon: Icons.verified_user_outlined,
                          ),
                        ),
                ),
              ],
            ),
          ),
          ClinicianSectionCard(
            title: '이메일',
            child: Form(
              key: _formKey,
              child: Column(
                children: [
                  ClinicianFormField(
                    controller: _emailController,
                    labelText: '이메일',
                    hintText: '이메일을 입력해주세요.',
                    keyboardType: TextInputType.emailAddress,
                    textInputAction: TextInputAction.done,
                    prefixIcon: const Icon(Icons.mail_outline_rounded),
                    validator: (value) {
                      final email = value?.trim() ?? '';
                      if (email.isEmpty || !email.contains('@')) {
                        return '올바른 이메일을 입력해주세요.';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  _PrimaryActionButton(
                    label: '이메일 저장',
                    busyLabel: '저장 중...',
                    isBusy: _saving,
                    onPressed: _save,
                  ),
                ],
              ),
            ),
          ),
          const ClinicianInfoNoticeCard(
            message: '이름, 면허번호, 소속 병원과 진료과는 현재 API에서 수정할 수 없습니다.',
            margin: EdgeInsets.zero,
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
    final hospitalId = clinician?.hospitalId ?? '';
    return _ProfileScreenScaffold(
      title: '근무 병원 정보',
      body: RefreshIndicator(
        onRefresh: () => ref.read(authProvider.notifier).refreshAccount(),
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
          children: [
            _ProfileSummaryCard(
              icon: Icons.local_hospital_outlined,
              title: _displayValue(clinician?.hospitalName),
              subtitle: _displayValue(clinician?.departmentName),
            ),
            ClinicianSectionCard(
              title: '상세 정보',
              child: Column(
                children: [
                  ClinicianInfoRow(
                    label: '병원',
                    value: _displayValue(clinician?.hospitalName),
                  ),
                  const _InfoDivider(),
                  ClinicianInfoRow(
                    label: '병원 ID',
                    value: _displayValue(hospitalId),
                    valueWidget: hospitalId.isEmpty
                        ? null
                        : SelectableText(
                            hospitalId,
                            style: const TextStyle(
                              color: ClinicianUiColors.text,
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              height: 1.45,
                            ),
                          ),
                  ),
                  const _InfoDivider(),
                  ClinicianInfoRow(
                    label: '진료과',
                    value: _displayValue(clinician?.departmentName),
                  ),
                  const _InfoDivider(),
                  ClinicianInfoRow(
                    label: '진료과 코드',
                    value: _displayValue(clinician?.departmentCode),
                  ),
                ],
              ),
            ),
            const ClinicianInfoNoticeCard(
              message: '근무 병원과 진료과는 현재 API에서 변경할 수 없습니다.',
              margin: EdgeInsets.zero,
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
  bool _obscureCurrent = true;
  bool _obscureNext = true;
  bool _obscureConfirm = true;

  @override
  void dispose() {
    _current.dispose();
    _next.dispose();
    _confirm.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return _ProfileScreenScaffold(
      title: '비밀번호 변경',
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
          children: [
            ClinicianSectionCard(
              title: '보안 입력',
              child: Column(
                children: [
                  _passwordField(
                    _current,
                    '현재 비밀번호',
                    obscureText: _obscureCurrent,
                    onToggleVisibility: () =>
                        setState(() => _obscureCurrent = !_obscureCurrent),
                  ),
                  const SizedBox(height: 14),
                  _passwordField(
                    _next,
                    '새 비밀번호',
                    obscureText: _obscureNext,
                    onToggleVisibility: () =>
                        setState(() => _obscureNext = !_obscureNext),
                  ),
                  const SizedBox(height: 14),
                  _passwordField(
                    _confirm,
                    '새 비밀번호 확인',
                    obscureText: _obscureConfirm,
                    textInputAction: TextInputAction.done,
                    onToggleVisibility: () =>
                        setState(() => _obscureConfirm = !_obscureConfirm),
                  ),
                ],
              ),
            ),
            _PrimaryActionButton(
              label: '비밀번호 변경',
              busyLabel: '변경 중...',
              isBusy: _saving,
              onPressed: _save,
            ),
            const SizedBox(height: 16),
            const _PasswordRulesCard(),
          ],
        ),
      ),
    );
  }

  Widget _passwordField(
    TextEditingController controller,
    String label, {
    required bool obscureText,
    required VoidCallback onToggleVisibility,
    TextInputAction textInputAction = TextInputAction.next,
  }) {
    return ClinicianFormField(
      controller: controller,
      labelText: label,
      hintText: '$label 입력',
      obscureText: obscureText,
      textInputAction: textInputAction,
      prefixIcon: const Icon(Icons.lock_outline_rounded),
      suffixIcon: IconButton(
        tooltip: obscureText ? '비밀번호 표시' : '비밀번호 숨기기',
        onPressed: onToggleVisibility,
        icon: Icon(
          obscureText
              ? Icons.visibility_off_outlined
              : Icons.visibility_outlined,
        ),
      ),
      validator: (value) {
        if ((value ?? '').length < 8) return '8자 이상 입력해주세요.';
        return null;
      },
    );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    if (_next.text != _confirm.text) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('새 비밀번호가 일치하지 않습니다.')));
      return;
    }
    setState(() => _saving = true);
    try {
      await ref
          .read(authRepositoryProvider)
          .changePassword(
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
    return _ProfileScreenScaffold(
      title: '알림 설정',
      body: value.when(
        loading: () => const ClinicianLoadingView(),
        error: (error, _) => ClinicianErrorView(
          message: _errorMessage(error, '알림 설정을 불러오지 못했습니다.'),
          onRetry: () => ref.invalidate(clinicianNotificationSettingsProvider),
        ),
        data: (settings) {
          final draft = _draft ?? settings;
          return ListView(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
            children: [
              ClinicianSectionCard(
                padding: EdgeInsets.zero,
                child: Column(
                  children: [
                    ClinicianSettingsTile(
                      icon: Icons.nightlight_outlined,
                      title: '방해금지 시간',
                      subtitle: '설정한 시간 동안 알림을 제한합니다.',
                      trailing: Switch(
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
                      showDivider: draft.quietHoursEnabled,
                    ),
                    if (draft.quietHoursEnabled)
                      ClinicianSettingsTile(
                        icon: Icons.schedule_rounded,
                        title: '방해금지 시간대',
                        subtitle:
                            '${draft.quietHoursStart ?? '-'} ~ ${draft.quietHoursEnd ?? '-'}',
                        onTap: () => _selectQuietHours(draft),
                        showDivider: false,
                      ),
                  ],
                ),
              ),
              if (draft.preferences.isEmpty)
                const ClinicianSectionCard(
                  child: Row(
                    children: [
                      Icon(
                        Icons.notifications_off_outlined,
                        color: ClinicianUiColors.mutedText,
                      ),
                      SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          '설정 가능한 알림 항목이 없습니다.',
                          style: TextStyle(color: ClinicianUiColors.mutedText),
                        ),
                      ),
                    ],
                  ),
                )
              else ...[
                const Padding(
                  padding: EdgeInsets.fromLTRB(2, 4, 2, 12),
                  child: Text(
                    '알림 항목',
                    style: TextStyle(
                      color: ClinicianUiColors.text,
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                for (var index = 0; index < draft.preferences.length; index++)
                  _PreferenceCard(
                    preference: draft.preferences[index],
                    onChanged: (updated) => setState(() {
                      final preferences = [...draft.preferences];
                      preferences[index] = updated;
                      _draft = _copySettings(draft, preferences: preferences);
                    }),
                  ),
              ],
              _PrimaryActionButton(
                label: '설정 저장',
                busyLabel: '저장 중...',
                isBusy: _saving,
                onPressed: () => _save(draft),
              ),
              const SizedBox(height: 16),
              const ClinicianInfoNoticeCard(
                message: '알림 설정은 언제든지 변경할 수 있습니다.',
                margin: EdgeInsets.zero,
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
      initialTime: _time(
        draft.quietHoursStart,
        const TimeOfDay(hour: 22, minute: 0),
      ),
    );
    if (start == null || !mounted) return;
    final end = await showTimePicker(
      context: context,
      initialTime: _time(
        draft.quietHoursEnd,
        const TimeOfDay(hour: 7, minute: 0),
      ),
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
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('알림 설정을 저장했습니다.')));
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

  static const _appName = String.fromEnvironment('APP_NAME');
  static const _appVersion = String.fromEnvironment('APP_VERSION');
  static const _buildNumber = String.fromEnvironment('APP_BUILD_NUMBER');

  @override
  Widget build(BuildContext context) {
    final hasMetadata =
        _appName.isNotEmpty ||
        _appVersion.isNotEmpty ||
        _buildNumber.isNotEmpty;

    return _ProfileScreenScaffold(
      title: '버전 정보',
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
        children: [
          ClinicianSectionCard(
            title: '앱 정보',
            child: hasMetadata
                ? Column(
                    children: [
                      if (_appName.isNotEmpty) ...[
                        const ClinicianInfoRow(label: '앱 이름', value: _appName),
                        if (_appVersion.isNotEmpty || _buildNumber.isNotEmpty)
                          const _InfoDivider(),
                      ],
                      if (_appVersion.isNotEmpty) ...[
                        const ClinicianInfoRow(
                          label: '현재 버전',
                          value: _appVersion,
                        ),
                        if (_buildNumber.isNotEmpty) const _InfoDivider(),
                      ],
                      if (_buildNumber.isNotEmpty)
                        const ClinicianInfoRow(
                          label: '빌드 정보',
                          value: _buildNumber,
                        ),
                    ],
                  )
                : const Row(
                    children: [
                      Icon(
                        Icons.info_outline_rounded,
                        color: ClinicianUiColors.mutedText,
                      ),
                      SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          '현재 빌드에서 제공된 앱 정보가 없습니다.',
                          style: TextStyle(
                            color: ClinicianUiColors.mutedText,
                            height: 1.45,
                          ),
                        ),
                      ),
                    ],
                  ),
          ),
          const ClinicianInfoNoticeCard(
            message: '빌드 환경에서 확인 가능한 앱 이름과 버전 정보만 표시합니다.',
            margin: EdgeInsets.zero,
          ),
        ],
      ),
    );
  }
}

class _ProfileScreenScaffold extends StatelessWidget {
  const _ProfileScreenScaffold({required this.title, required this.body});

  final String title;
  final Widget body;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ClinicianUiColors.background,
      appBar: AppBar(
        title: Text(title),
        backgroundColor: ClinicianUiColors.background,
        foregroundColor: ClinicianUiColors.text,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        titleTextStyle: const TextStyle(
          color: ClinicianUiColors.text,
          fontSize: 21,
          fontWeight: FontWeight.w800,
        ),
      ),
      body: body,
    );
  }
}

class _ProfileSummaryCard extends StatelessWidget {
  const _ProfileSummaryCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.status = '',
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final String status;

  @override
  Widget build(BuildContext context) {
    return ClinicianSectionCard(
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Container(
            width: 72,
            height: 72,
            decoration: const BoxDecoration(
              color: Color(0xFFE7F0FF),
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: Icon(icon, color: ClinicianUiColors.primary, size: 36),
          ),
          const SizedBox(width: 18),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: ClinicianUiColors.text,
                    fontSize: 21,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 5),
                Text(
                  subtitle,
                  style: const TextStyle(
                    color: ClinicianUiColors.primary,
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                if (status.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  ClinicianStatusBadge(
                    label: status,
                    tone: _statusTone(status),
                    icon: Icons.verified_user_outlined,
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PrimaryActionButton extends StatelessWidget {
  const _PrimaryActionButton({
    required this.label,
    required this.busyLabel,
    required this.isBusy,
    required this.onPressed,
  });

  final String label;
  final String busyLabel;
  final bool isBusy;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: FilledButton(
        onPressed: isBusy ? null : onPressed,
        style: FilledButton.styleFrom(
          backgroundColor: ClinicianUiColors.primary,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
        child: isBusy
            ? Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text(busyLabel),
                ],
              )
            : Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
      ),
    );
  }
}

class _InfoDivider extends StatelessWidget {
  const _InfoDivider();

  @override
  Widget build(BuildContext context) {
    return const Divider(height: 17, color: ClinicianUiColors.border);
  }
}

class _PasswordRulesCard extends StatelessWidget {
  const _PasswordRulesCard();

  @override
  Widget build(BuildContext context) {
    return ClinicianSectionCard(
      title: '비밀번호 규칙',
      margin: EdgeInsets.zero,
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _RuleIcon(),
          SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _RuleText('8자 이상 입력'),
                _RuleText('현재 비밀번호와 다르게 설정'),
                _RuleText('흔한 비밀번호 또는 숫자로만 된 비밀번호 제한'),
                _RuleText('계정 정보와 유사한 비밀번호 제한', isLast: true),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _RuleIcon extends StatelessWidget {
  const _RuleIcon();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 44,
      height: 44,
      decoration: const BoxDecoration(
        color: Color(0xFFE7F0FF),
        shape: BoxShape.circle,
      ),
      alignment: Alignment.center,
      child: const Icon(
        Icons.shield_outlined,
        color: ClinicianUiColors.primary,
        size: 23,
      ),
    );
  }
}

class _RuleText extends StatelessWidget {
  const _RuleText(this.value, {this.isLast = false});

  final String value;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(bottom: isLast ? 0 : 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.only(top: 7),
            child: Icon(
              Icons.circle,
              size: 5,
              color: ClinicianUiColors.mutedText,
            ),
          ),
          const SizedBox(width: 9),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                color: ClinicianUiColors.mutedText,
                fontSize: 13,
                height: 1.45,
              ),
            ),
          ),
        ],
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
    return ClinicianSectionCard(
      padding: EdgeInsets.zero,
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
            child: Row(
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: const Color(0xFFE7F0FF),
                    borderRadius: BorderRadius.circular(13),
                  ),
                  alignment: Alignment.center,
                  child: Icon(
                    _notificationIcon(preference.type),
                    color: ClinicianUiColors.primary,
                    size: 23,
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Text(
                    _notificationLabel(preference.type),
                    style: const TextStyle(
                      color: ClinicianUiColors.text,
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: ClinicianUiColors.border),
          _NotificationSwitchRow(
            title: '푸시 알림',
            subtitle: '앱 푸시로 알림 받기',
            value: preference.pushEnabled,
            onChanged: (value) =>
                onChanged(preference.copyWith(pushEnabled: value)),
          ),
          const Divider(
            height: 1,
            indent: 16,
            endIndent: 16,
            color: ClinicianUiColors.border,
          ),
          _NotificationSwitchRow(
            title: '이메일 알림',
            subtitle: '이메일로 알림 받기',
            value: preference.emailEnabled,
            onChanged: (value) =>
                onChanged(preference.copyWith(emailEnabled: value)),
          ),
        ],
      ),
    );
  }
}

class _NotificationSwitchRow extends StatelessWidget {
  const _NotificationSwitchRow({
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
  });

  final String title;
  final String subtitle;
  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: ClinicianUiColors.text,
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  subtitle,
                  style: const TextStyle(
                    color: ClinicianUiColors.mutedText,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          Switch(value: value, onChanged: onChanged),
        ],
      ),
    );
  }
}

String _displayValue(String? value) {
  final normalized = value?.trim() ?? '';
  return normalized.isEmpty ? '-' : normalized;
}

ClinicianStatusTone _statusTone(String status) {
  return switch (status.trim().toUpperCase()) {
    'APPROVED' || 'ACTIVE' => ClinicianStatusTone.success,
    'PENDING' || 'WAITING' => ClinicianStatusTone.warning,
    'REJECTED' || 'INACTIVE' => ClinicianStatusTone.danger,
    _ => ClinicianStatusTone.neutral,
  };
}

IconData _notificationIcon(String type) => switch (type) {
  'APPOINTMENT' => Icons.calendar_month_outlined,
  'TEST_RESULT' => Icons.science_outlined,
  'CONSULTATION' => Icons.groups_outlined,
  'SYSTEM' => Icons.settings_outlined,
  _ => Icons.notifications_outlined,
};
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
