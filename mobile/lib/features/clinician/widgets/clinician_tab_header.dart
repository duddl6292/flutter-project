import 'package:flutter/material.dart';

class ClinicianTabHeader extends StatelessWidget {
  const ClinicianTabHeader({
    required this.title,
    this.onOpenDrawer,
    this.showBackButton = false,
    this.onBack,
    this.notificationCount = 0,
    this.onNotificationTap,
    super.key,
  });

  final String title;
  final VoidCallback? onOpenDrawer;
  final bool showBackButton;
  final VoidCallback? onBack;
  final int notificationCount;
  final VoidCallback? onNotificationTap;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 8),
      child: Row(
        children: [
          IconButton(
            onPressed: showBackButton
                ? (onBack ?? () => Navigator.of(context).pop())
                : onOpenDrawer,
            icon: Icon(
              showBackButton ? Icons.arrow_back_rounded : Icons.menu_rounded,
              size: 28,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            title,
            style: const TextStyle(
              color: Color(0xFF111827),
              fontSize: 20,
              fontWeight: FontWeight.w800,
            ),
          ),
          const Spacer(),
          IconButton(
            onPressed: onNotificationTap,
            icon: Badge(
              isLabelVisible: notificationCount > 0,
              label: Text('$notificationCount'),
              child: const Icon(Icons.notifications_none_rounded, size: 26),
            ),
          ),
        ],
      ),
    );
  }
}
