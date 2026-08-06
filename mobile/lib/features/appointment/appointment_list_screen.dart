import 'package:brainon_mobile/core/router/route_names.dart';
import 'package:brainon_mobile/features/appointment/providers/appointment_provider.dart';
import 'package:brainon_mobile/shared/models/appointment.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class AppointmentListScreen extends ConsumerWidget {
  const AppointmentListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final value = ref.watch(patientAppointmentsProvider);
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FB),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        surfaceTintColor: Colors.white,
        title: const Text(
          '진료 일정',
          style: TextStyle(
            color: Color(0xFF111827),
            fontSize: 21,
            fontWeight: FontWeight.w800,
          ),
        ),
        centerTitle: false,
      ),
      body: SafeArea(
        child: value.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => Center(
            child: OutlinedButton.icon(
              onPressed: () => ref.invalidate(patientAppointmentsProvider),
              icon: const Icon(Icons.refresh),
              label: const Text('예약 정보 다시 불러오기'),
            ),
          ),
          data: (appointments) {
            if (appointments.isEmpty) {
              return const Center(child: Text('예정된 진료가 없습니다.'));
            }
            return RefreshIndicator(
              onRefresh: () => ref.refresh(patientAppointmentsProvider.future),
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
                children: [
                  const Text(
                    '진료 예약 내역',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF111827),
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    '로그인한 환자의 예약을 확인하세요.',
                    style: TextStyle(fontSize: 14, color: Color(0xFF6B7280)),
                  ),
                  const SizedBox(height: 24),
                  ...appointments.map(
                    (appointment) => Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: _AppointmentCard(appointment: appointment),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

class _AppointmentCard extends StatelessWidget {
  const _AppointmentCard({required this.appointment});

  final Appointment appointment;

  @override
  Widget build(BuildContext context) {
    final scheduledAt = appointment.scheduledAt;

    return InkWell(
      onTap: () {
        context.pushNamed(RouteNames.appointmentDetail, extra: appointment);
      },
      borderRadius: BorderRadius.circular(22),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(22),
          border: Border.all(color: const Color(0xFFE5E7EB)),
          boxShadow: const [
            BoxShadow(
              color: Color(0x0D000000),
              blurRadius: 18,
              offset: Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _DateBox(
                  date:
                      '${scheduledAt.month}.${scheduledAt.day.toString().padLeft(2, '0')}',
                  day: _weekdayText(scheduledAt),
                  dDay: appointment.dDay,
                ),
                const SizedBox(width: 18),
                Expanded(child: _AppointmentInfo(appointment: appointment)),
              ],
            ),
            const SizedBox(height: 18),
            const Divider(height: 1, color: Color(0xFFE5E7EB)),
            const SizedBox(height: 16),
            Row(
              children: [
                const Icon(
                  Icons.check_circle_outline,
                  size: 19,
                  color: Color(0xFF16A34A),
                ),
                const SizedBox(width: 8),
                Text(
                  appointment.status,
                  style: const TextStyle(
                    color: Color(0xFF15803D),
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const Spacer(),
                const Text(
                  '상세보기',
                  style: TextStyle(
                    color: Color(0xFF2563EB),
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(width: 4),
                const Icon(Icons.chevron_right, color: Color(0xFF2563EB)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _weekdayText(DateTime date) {
    const weekdays = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'];

    return weekdays[date.weekday - 1];
  }
}

// 날짜정보 클래스
class _DateBox extends StatelessWidget {
  const _DateBox({required this.date, required this.day, required this.dDay});

  final String date;
  final String day;
  final String dDay;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 84,
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFEFF6FF),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        children: [
          Text(
            date,
            style: const TextStyle(
              color: Color(0xFF2563EB),
              fontSize: 24,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            day,
            style: const TextStyle(
              color: Color(0xFF6B7280),
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              dDay,
              style: const TextStyle(
                color: Color(0xFF2563EB),
                fontSize: 13,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

//예약정보 클래스
class _AppointmentInfo extends StatelessWidget {
  const _AppointmentInfo({required this.appointment});

  final Appointment appointment;

  @override
  Widget build(BuildContext context) {
    final scheduledAt = appointment.scheduledAt;

    final time =
        '${scheduledAt.hour.toString().padLeft(2, '0')}:'
        '${scheduledAt.minute.toString().padLeft(2, '0')}';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              time,
              style: const TextStyle(
                color: Color(0xFF111827),
                fontSize: 22,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(width: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: const Color(0xFFEFF6FF),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                appointment.type,
                style: const TextStyle(
                  color: Color(0xFF2563EB),
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 14),
        Text(
          '${appointment.hospitalName} ${appointment.department}',
          style: const TextStyle(
            color: Color(0xFF111827),
            fontSize: 17,
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          appointment.doctorName,
          style: const TextStyle(
            color: Color(0xFF4B5563),
            fontSize: 15,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 10),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(
              Icons.location_on_outlined,
              size: 19,
              color: Color(0xFF94A3B8),
            ),
            const SizedBox(width: 6),
            Expanded(
              child: Text(
                appointment.location,
                style: const TextStyle(
                  color: Color(0xFF6B7280),
                  fontSize: 13,
                  height: 1.4,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
