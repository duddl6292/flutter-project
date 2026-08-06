import 'package:brainon_mobile/features/clinician/widgets/clinician_tab_header.dart';
import 'package:flutter/material.dart';

abstract final class ClinicianUiColors {
  static const background = Color(0xFFF4F5FB);
  static const surface = Colors.white;
  static const primary = Color(0xFF2867D8);
  static const text = Color(0xFF172033);
  static const mutedText = Color(0xFF6B7280);
  static const border = Color(0xFFE5E9F2);
}

enum ClinicianStatusTone { neutral, info, success, warning, danger }

class ClinicianPageScaffold extends StatelessWidget {
  const ClinicianPageScaffold({
    required this.title,
    required this.body,
    this.onOpenDrawer,
    this.floatingActionButton,
    super.key,
  });

  final String title;
  final Widget body;
  final VoidCallback? onOpenDrawer;
  final Widget? floatingActionButton;

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: ClinicianUiColors.background,
      child: SafeArea(
        bottom: false,
        child: Stack(
          children: [
            Column(
              children: [
                ClinicianTabHeader(title: title, onOpenDrawer: onOpenDrawer),
                Expanded(child: body),
              ],
            ),
            if (floatingActionButton != null)
              Positioned(right: 20, bottom: 20, child: floatingActionButton!),
          ],
        ),
      ),
    );
  }
}

class ClinicianSectionCard extends StatelessWidget {
  const ClinicianSectionCard({
    required this.child,
    this.title,
    this.trailing,
    this.padding = const EdgeInsets.all(18),
    this.margin = const EdgeInsets.only(bottom: 12),
    super.key,
  });

  final String? title;
  final Widget? trailing;
  final Widget child;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry margin;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      padding: padding,
      decoration: BoxDecoration(
        color: ClinicianUiColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: ClinicianUiColors.border),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0D172033),
            blurRadius: 20,
            offset: Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (title != null || trailing != null) ...[
            Row(
              children: [
                if (title != null)
                  Expanded(
                    child: Text(
                      title!,
                      style: const TextStyle(
                        color: ClinicianUiColors.text,
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  )
                else
                  const Spacer(),
                ?trailing,
              ],
            ),
            const SizedBox(height: 14),
          ],
          child,
        ],
      ),
    );
  }
}

class ClinicianInfoRow extends StatelessWidget {
  const ClinicianInfoRow({
    required this.label,
    required this.value,
    this.valueWidget,
    this.labelWidth = 92,
    super.key,
  });

  final String label;
  final String value;
  final Widget? valueWidget;
  final double labelWidth;

  @override
  Widget build(BuildContext context) {
    if (value.isEmpty && valueWidget == null) {
      return const SizedBox.shrink();
    }
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: labelWidth,
            child: Text(
              label,
              style: const TextStyle(
                color: ClinicianUiColors.mutedText,
                fontSize: 13,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child:
                valueWidget ??
                Text(
                  value,
                  style: const TextStyle(
                    color: ClinicianUiColors.text,
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    height: 1.45,
                  ),
                ),
          ),
        ],
      ),
    );
  }
}

class ClinicianStatusBadge extends StatelessWidget {
  const ClinicianStatusBadge({
    required this.label,
    this.tone = ClinicianStatusTone.neutral,
    this.icon,
    super.key,
  });

  final String label;
  final ClinicianStatusTone tone;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final (foreground, background) = switch (tone) {
      ClinicianStatusTone.info => (
        const Color(0xFF2463C7),
        const Color(0xFFE7F0FF),
      ),
      ClinicianStatusTone.success => (
        const Color(0xFF16845B),
        const Color(0xFFE3F6ED),
      ),
      ClinicianStatusTone.warning => (
        const Color(0xFFC15F16),
        const Color(0xFFFFECDD),
      ),
      ClinicianStatusTone.danger => (
        const Color(0xFFD43D4E),
        const Color(0xFFFFE7EA),
      ),
      ClinicianStatusTone.neutral => (
        const Color(0xFF626B7B),
        const Color(0xFFEEF1F5),
      ),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 13, color: foreground),
            const SizedBox(width: 4),
          ],
          Text(
            label,
            style: TextStyle(
              color: foreground,
              fontSize: 12,
              fontWeight: FontWeight.w800,
            ),
          ),
        ],
      ),
    );
  }
}

class ClinicianInfoNoticeCard extends StatelessWidget {
  const ClinicianInfoNoticeCard({
    required this.message,
    this.title = '안내',
    this.icon = Icons.info_outline_rounded,
    this.margin = const EdgeInsets.only(bottom: 12),
    super.key,
  });

  final String title;
  final String message;
  final IconData icon;
  final EdgeInsetsGeometry margin;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: ClinicianUiColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: ClinicianUiColors.border),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0A172033),
            blurRadius: 16,
            offset: Offset(0, 5),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: const BoxDecoration(
              color: Color(0xFFE7F0FF),
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: Icon(icon, color: ClinicianUiColors.primary, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: ClinicianUiColors.text,
                    fontSize: 15,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  message,
                  style: const TextStyle(
                    color: ClinicianUiColors.mutedText,
                    fontSize: 13,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class ClinicianSettingsTile extends StatelessWidget {
  const ClinicianSettingsTile({
    required this.icon,
    required this.title,
    this.subtitle,
    this.trailing,
    this.onTap,
    this.showDivider = true,
    this.iconColor = ClinicianUiColors.primary,
    this.iconBackgroundColor = const Color(0xFFE7F0FF),
    this.titleColor = ClinicianUiColors.text,
    super.key,
  });

  final IconData icon;
  final String title;
  final String? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;
  final bool showDivider;
  final Color iconColor;
  final Color iconBackgroundColor;
  final Color titleColor;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onTap,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: iconBackgroundColor,
                      borderRadius: BorderRadius.circular(13),
                    ),
                    alignment: Alignment.center,
                    child: Icon(icon, color: iconColor, size: 23),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          title,
                          style: TextStyle(
                            color: titleColor,
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        if (subtitle != null && subtitle!.isNotEmpty) ...[
                          const SizedBox(height: 4),
                          Text(
                            subtitle!,
                            style: const TextStyle(
                              color: ClinicianUiColors.mutedText,
                              fontSize: 12,
                              height: 1.35,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  const SizedBox(width: 10),
                  trailing ??
                      (onTap == null
                          ? const SizedBox.shrink()
                          : const Icon(
                              Icons.chevron_right_rounded,
                              color: Color(0xFF7A8494),
                            )),
                ],
              ),
            ),
          ),
        ),
        if (showDivider)
          const Divider(
            height: 1,
            indent: 74,
            endIndent: 16,
            color: ClinicianUiColors.border,
          ),
      ],
    );
  }
}

class ClinicianListCard extends StatelessWidget {
  const ClinicianListCard({
    required this.child,
    required this.onTap,
    super.key,
  });

  final Widget child;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: ClinicianUiColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: ClinicianUiColors.border),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0D172033),
            blurRadius: 18,
            offset: Offset(0, 5),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(16),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: onTap,
          child: Padding(padding: const EdgeInsets.all(18), child: child),
        ),
      ),
    );
  }
}

class ClinicianFormField extends StatelessWidget {
  const ClinicianFormField({
    required this.controller,
    required this.hintText,
    this.labelText,
    this.onChanged,
    this.maxLines = 1,
    this.maxLength,
    this.validator,
    this.suffixIcon,
    this.enabled = true,
    this.readOnly = false,
    this.onTap,
    this.obscureText = false,
    this.keyboardType,
    this.textInputAction,
    this.prefixIcon,
    super.key,
  });

  final TextEditingController controller;
  final String hintText;
  final String? labelText;
  final ValueChanged<String>? onChanged;
  final int maxLines;
  final int? maxLength;
  final FormFieldValidator<String>? validator;
  final Widget? suffixIcon;
  final bool enabled;
  final bool readOnly;
  final VoidCallback? onTap;
  final bool obscureText;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final Widget? prefixIcon;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      enabled: enabled,
      readOnly: readOnly,
      obscureText: obscureText,
      keyboardType: keyboardType,
      textInputAction: textInputAction,
      onTap: onTap,
      onChanged: onChanged,
      validator: validator,
      maxLength: maxLength,
      minLines: 1,
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: labelText,
        hintText: hintText,
        hintStyle: const TextStyle(color: Color(0xFF9AA2B1)),
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 13,
        ),
        suffixIcon: suffixIcon,
        prefixIcon: prefixIcon,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: ClinicianUiColors.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: ClinicianUiColors.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(
            color: ClinicianUiColors.primary,
            width: 1.5,
          ),
        ),
      ),
    );
  }
}

class ClinicianLoadingView extends StatelessWidget {
  const ClinicianLoadingView({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: CircularProgressIndicator(color: ClinicianUiColors.primary),
    );
  }
}

class ClinicianEmptyView extends StatelessWidget {
  const ClinicianEmptyView({
    required this.message,
    this.icon = Icons.inbox_outlined,
    super.key,
  });

  final String message;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 42, color: const Color(0xFF9AA7BA)),
            const SizedBox(height: 12),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(color: ClinicianUiColors.mutedText),
            ),
          ],
        ),
      ),
    );
  }
}

class ClinicianErrorView extends StatelessWidget {
  const ClinicianErrorView({
    required this.message,
    required this.onRetry,
    super.key,
  });

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.cloud_off_rounded,
              size: 42,
              color: Color(0xFF8A95A8),
            ),
            const SizedBox(height: 12),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(color: ClinicianUiColors.mutedText),
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('다시 시도'),
            ),
          ],
        ),
      ),
    );
  }
}
