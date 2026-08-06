import 'package:brainon_mobile/features/clinician/appointments/clinician_schedule_model.dart';
import 'package:brainon_mobile/features/clinician/appointments/clinician_schedule_provider.dart';
import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/clinician/widgets/clinician_tab_header.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class ClinicianScheduleScreen extends ConsumerStatefulWidget {
  const ClinicianScheduleScreen({required this.onOpenDrawer, super.key});
  final VoidCallback onOpenDrawer;

  @override
  ConsumerState<ClinicianScheduleScreen> createState() =>
      _ClinicianScheduleScreenState();
}

class _ClinicianScheduleScreenState
    extends ConsumerState<ClinicianScheduleScreen> {
  DateTime _visibleMonth = DateTime(2026, 8);
  DateTime _selectedDate = DateTime(2026, 8, 5);

  void _changeMonth(int offset) {
    setState(() {
      _visibleMonth = DateTime(
        _visibleMonth.year,
        _visibleMonth.month + offset,
      );
      _selectedDate = DateTime(_visibleMonth.year, _visibleMonth.month);
    });
  }

  bool _sameDay(DateTime first, DateTime second) =>
      first.year == second.year &&
      first.month == second.month &&
      first.day == second.day;

  @override
  Widget build(BuildContext context) {
    final schedules = ref.watch(clinicianSchedulesProvider);
    return ColoredBox(
      color: const Color(0xFFF6F8FC),
      child: SafeArea(
        bottom: false,
        child: Column(
          children: [
            ClinicianTabHeader(
              title: '진료 일정',
              onOpenDrawer: widget.onOpenDrawer,
            ),
            Expanded(
              child: schedules.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (_, _) => Center(
                  child: FilledButton(
                    onPressed: () => ref.invalidate(clinicianSchedulesProvider),
                    child: const Text('다시 시도'),
                  ),
                ),
                data: (items) => ListView(
                  padding: const EdgeInsets.fromLTRB(20, 8, 20, 28),
                  children: [
                    _CalendarCard(
                      month: _visibleMonth,
                      selectedDate: _selectedDate,
                      scheduleDates: items
                          .map((item) => item.startsAt)
                          .toList(),
                      onPrevious: () => _changeMonth(-1),
                      onNext: () => _changeMonth(1),
                      onSelected: (date) =>
                          setState(() => _selectedDate = date),
                    ),
                    const SizedBox(height: 20),
                    Text(
                      '${_selectedDate.month}월 ${_selectedDate.day}일 일정',
                      style: const TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 10),
                    ...items
                        .where((item) => _sameDay(item.startsAt, _selectedDate))
                        .map(
                          (item) => _ScheduleTile(
                            schedule: item,
                            onTap: () => context.pushNamed(
                              RouteNames.clinicianPatientDetail,
                              pathParameters: {'patientId': item.patientId},
                            ),
                          ),
                        ),
                    if (!items.any(
                      (item) => _sameDay(item.startsAt, _selectedDate),
                    ))
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 36),
                        child: Center(
                          child: Text(
                            '선택한 날짜에 일정이 없습니다.',
                            style: TextStyle(color: Color(0xFF6B7280)),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CalendarCard extends StatelessWidget {
  const _CalendarCard({
    required this.month,
    required this.selectedDate,
    required this.scheduleDates,
    required this.onPrevious,
    required this.onNext,
    required this.onSelected,
  });
  final DateTime month;
  final DateTime selectedDate;
  final List<DateTime> scheduleDates;
  final VoidCallback onPrevious;
  final VoidCallback onNext;
  final ValueChanged<DateTime> onSelected;

  @override
  Widget build(BuildContext context) {
    final firstDay = DateTime(month.year, month.month);
    final days = DateTime(month.year, month.month + 1, 0).day;
    final leading = firstDay.weekday % 7;
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFE5EAF2)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              IconButton(
                onPressed: onPrevious,
                icon: const Icon(Icons.chevron_left),
              ),
              Expanded(
                child: Text(
                  '${month.year}년 ${month.month}월',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              IconButton(
                onPressed: onNext,
                icon: const Icon(Icons.chevron_right),
              ),
            ],
          ),
          const Row(
            children: [
              Expanded(child: Center(child: Text('일'))),
              Expanded(child: Center(child: Text('월'))),
              Expanded(child: Center(child: Text('화'))),
              Expanded(child: Center(child: Text('수'))),
              Expanded(child: Center(child: Text('목'))),
              Expanded(child: Center(child: Text('금'))),
              Expanded(child: Center(child: Text('토'))),
            ],
          ),
          const SizedBox(height: 8),
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 7,
            ),
            itemCount: leading + days,
            itemBuilder: (context, index) {
              if (index < leading) return const SizedBox.shrink();
              final date = DateTime(
                month.year,
                month.month,
                index - leading + 1,
              );
              final selected =
                  date.year == selectedDate.year &&
                  date.month == selectedDate.month &&
                  date.day == selectedDate.day;
              final hasSchedule = scheduleDates.any(
                (item) =>
                    item.year == date.year &&
                    item.month == date.month &&
                    item.day == date.day,
              );
              return InkWell(
                borderRadius: BorderRadius.circular(12),
                onTap: () => onSelected(date),
                child: Container(
                  margin: const EdgeInsets.all(3),
                  decoration: BoxDecoration(
                    color: selected ? const Color(0xFF28669E) : null,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '${date.day}',
                        style: TextStyle(
                          color: selected
                              ? Colors.white
                              : const Color(0xFF111827),
                        ),
                      ),
                      if (hasSchedule)
                        Container(
                          width: 4,
                          height: 4,
                          decoration: BoxDecoration(
                            color: selected
                                ? Colors.white
                                : const Color(0xFF28669E),
                            shape: BoxShape.circle,
                          ),
                        ),
                    ],
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

class _ScheduleTile extends StatelessWidget {
  const _ScheduleTile({required this.schedule, required this.onTap});
  final ClinicianSchedule schedule;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final hour = schedule.startsAt.hour.toString().padLeft(2, '0');
    final minute = schedule.startsAt.minute.toString().padLeft(2, '0');
    final (label, color) = switch (schedule.status) {
      ClinicianScheduleStatus.inProgress => ('진료', const Color(0xFF2563EB)),
      ClinicianScheduleStatus.waiting => ('대기', const Color(0xFFF59E0B)),
      ClinicianScheduleStatus.confirmed => ('예약', const Color(0xFF7C3AED)),
      ClinicianScheduleStatus.completed => ('완료', const Color(0xFF059669)),
    };
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: Color(0xFFE5EAF2)),
      ),
      child: ListTile(
        onTap: onTap,
        leading: Text(
          '$hour:$minute',
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
        title: Text(
          schedule.patientName,
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
        subtitle: Text(schedule.description),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 5),
          decoration: BoxDecoration(
            color: color.withValues(alpha: .1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            label,
            style: TextStyle(color: color, fontWeight: FontWeight.w700),
          ),
        ),
      ),
    );
  }
}
