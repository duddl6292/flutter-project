import 'package:brainon_mobile/core/update/app_update_service.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

class AppUpdatePrompt extends StatefulWidget {
  const AppUpdatePrompt({required this.child, super.key});

  final Widget child;

  @override
  State<AppUpdatePrompt> createState() => _AppUpdatePromptState();
}

class _AppUpdatePromptState extends State<AppUpdatePrompt> {
  final AppUpdateService _updateService = const AppUpdateService();

  AvailableAppUpdate? _availableUpdate;
  bool _isStartingUpdate = false;
  bool _isDismissed = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _checkForUpdate());
  }

  Future<void> _checkForUpdate() async {
    // 개발 중에는 GitHub 또는 Play 업데이트 창을 띄우지 않고,
    // 실제 release 빌드에서만 앱 시작 시 한 번 확인한다.
    if (kDebugMode) {
      return;
    }

    try {
      final update = await _updateService.checkForUpdate();
      if (!mounted || update == null) {
        return;
      }
      setState(() {
        _availableUpdate = update;
      });
    } on Object catch (error) {
      // 업데이트 서버나 Play Store를 일시적으로 확인할 수 없어도
      // 로그인과 주요 앱 기능은 계속 사용할 수 있도록 한다.
      debugPrint('앱 업데이트 확인 실패: $error');
    }
  }

  Future<void> _startUpdate() async {
    final update = _availableUpdate;
    if (update == null || _isStartingUpdate) {
      return;
    }

    setState(() {
      _isStartingUpdate = true;
      _errorMessage = null;
    });

    try {
      await _updateService.startUpdate(update);
    } on Object {
      if (mounted) {
        setState(() {
          _errorMessage = '업데이트 화면을 열지 못했습니다. 잠시 후 다시 시도해 주세요.';
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isStartingUpdate = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final update = _availableUpdate;
    if (update == null || _isDismissed) {
      return widget.child;
    }

    return Stack(
      fit: StackFit.expand,
      children: [
        widget.child,
        const ModalBarrier(dismissible: false, color: Colors.black54),
        SafeArea(
          child: Center(
            child: AlertDialog(
              title: const Text('앱 업데이트 안내'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(update.message),
                  const SizedBox(height: 8),
                  Text(
                    '새 버전: ${update.versionName}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  if (_errorMessage != null) ...[
                    const SizedBox(height: 12),
                    Text(
                      _errorMessage!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                  ],
                ],
              ),
              actions: [
                if (!update.isRequired)
                  TextButton(
                    onPressed: _isStartingUpdate
                        ? null
                        : () {
                            setState(() {
                              _isDismissed = true;
                            });
                          },
                    child: const Text('나중에'),
                  ),
                FilledButton(
                  onPressed: _isStartingUpdate ? null : _startUpdate,
                  child: _isStartingUpdate
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('업데이트'),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
