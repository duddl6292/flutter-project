import 'package:brainon_mobile/features/appointment/hospital_select_screen.dart';
import 'package:brainon_mobile/features/appointment/repositories/appointment_create_repository.dart';
import 'package:brainon_mobile/features/appointment/repositories/department_repository.dart';
import 'package:brainon_mobile/features/appointment/repositories/doctor_repository.dart';
import 'package:brainon_mobile/shared/mock/appointment_time_mock.dart';
import 'package:brainon_mobile/shared/models/appointment_create_request.dart';
import 'package:brainon_mobile/shared/models/department.dart';
import 'package:brainon_mobile/shared/models/doctor.dart';
import 'package:brainon_mobile/shared/models/hospital.dart';
import 'package:flutter/material.dart';

class AppointmentCreateScreen extends StatefulWidget {
  const AppointmentCreateScreen({super.key});

  @override
  State<AppointmentCreateScreen> createState() =>
      _AppointmentCreateScreenState();
}

class _AppointmentCreateScreenState extends State<AppointmentCreateScreen> {
  final DepartmentRepository _departmentRepository =
      DepartmentRepository();

  final DoctorRepository _doctorRepository =
      DoctorRepository();

  final AppointmentCreateRepository _appointmentRepository =
      AppointmentCreateRepository();

  Hospital? _selectedHospital;
  Department? _selectedDepartment;
  Doctor? _selectedDoctor;
  DateTime? _selectedDate;
  String? _selectedTime;

  bool _isSubmitting = false;

  bool get _canSelectDepartment => _selectedHospital != null;

  bool get _canSelectDoctor =>
      _selectedHospital != null &&
      _selectedDepartment != null;

  bool get _canSelectDate =>
      _selectedHospital != null &&
      _selectedDepartment != null &&
      _selectedDoctor != null;

  bool get _canSelectTime =>
      _selectedHospital != null &&
      _selectedDepartment != null &&
      _selectedDoctor != null &&
      _selectedDate != null;

  bool get _canSubmit =>
      _selectedHospital != null &&
      _selectedDepartment != null &&
      _selectedDoctor != null &&
      _selectedDate != null &&
      _selectedTime != null;

  Future<void> _selectHospital() async {
    final hospital = await Navigator.of(context).push<Hospital>(
      MaterialPageRoute(
        builder: (context) {
          return const HospitalSelectScreen();
        },
      ),
    );

    if (hospital == null || !mounted) {
      return;
    }

    setState(() {
      _selectedHospital = hospital;

      // 병원이 변경되면 하위 선택값 초기화
      _selectedDepartment = null;
      _selectedDoctor = null;
      _selectedDate = null;
      _selectedTime = null;
    });
  }

  Future<void> _selectDepartment() async {
    if (_selectedHospital == null) {
      _showMessage('병원을 먼저 선택해 주세요.');
      return;
    }

    final departments =
        await _departmentRepository.getDepartmentsByHospital(
      _selectedHospital!.hospitalId,
    );

    if (!mounted) {
      return;
    }

    if (departments.isEmpty) {
      _showMessage('선택 가능한 진료과가 없습니다.');
      return;
    }

    final department =
        await showModalBottomSheet<Department>(
      context: context,
      backgroundColor: Colors.white,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (context) {
        return _DepartmentBottomSheet(
          departments: departments,
        );
      },
    );

    if (department == null || !mounted) {
      return;
    }

    setState(() {
      _selectedDepartment = department;

      // 진료과가 변경되면 하위 선택값 초기화
      _selectedDoctor = null;
      _selectedDate = null;
      _selectedTime = null;
    });
  }

  Future<void> _selectDoctor() async {
    if (_selectedDepartment == null) {
      _showMessage('진료과를 먼저 선택해 주세요.');
      return;
    }

    final doctors =
        await _doctorRepository.getDoctorsByDepartment(
      _selectedDepartment!.departmentId,
    );

    if (!mounted) {
      return;
    }

    if (doctors.isEmpty) {
      _showMessage('선택 가능한 의료진이 없습니다.');
      return;
    }

    final doctor = await showModalBottomSheet<Doctor>(
      context: context,
      backgroundColor: Colors.white,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (context) {
        return _DoctorBottomSheet(
          doctors: doctors,
        );
      },
    );

    if (doctor == null || !mounted) {
      return;
    }

    setState(() {
      _selectedDoctor = doctor;

      // 의료진이 변경되면 하위 선택값 초기화
      _selectedDate = null;
      _selectedTime = null;
    });
  }

  Future<void> _selectDate() async {
    if (_selectedDoctor == null) {
      _showMessage('담당 의료진을 먼저 선택해 주세요.');
      return;
    }

    final today = DateTime.now();

    final date = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? today,
      firstDate: DateTime(
        today.year,
        today.month,
        today.day,
      ),
      lastDate: DateTime(today.year + 1),
      helpText: '진료 날짜 선택',
      cancelText: '취소',
      confirmText: '선택',
    );

    if (date == null || !mounted) {
      return;
    }

    setState(() {
      _selectedDate = date;

      // 날짜가 변경되면 시간 초기화
      _selectedTime = null;
    });
  }

  Future<void> _selectTime() async {
    if (_selectedDate == null) {
      _showMessage('진료 날짜를 먼저 선택해 주세요.');
      return;
    }

    final time = await showModalBottomSheet<String>(
      context: context,
      backgroundColor: Colors.white,
      showDragHandle: true,
      isScrollControlled: true,
      builder: (context) {
        return const _TimeBottomSheet();
      },
    );

    if (time == null || !mounted) {
      return;
    }

    setState(() {
      _selectedTime = time;
    });
  }

  Future<void> _submitAppointment() async {
    if (!_canSubmit) {
      _showMessage('예약 정보를 모두 선택해 주세요.');
      return;
    }

    final timeParts = _selectedTime!.split(':');

    final hour = int.parse(timeParts[0]);
    final minute = int.parse(timeParts[1]);

    final scheduledAt = DateTime(
      _selectedDate!.year,
      _selectedDate!.month,
      _selectedDate!.day,
      hour,
      minute,
    );

    final request = AppointmentCreateRequest(
      hospitalId: _selectedHospital!.hospitalId,
      departmentId: _selectedDepartment!.departmentId,
      doctorId: _selectedDoctor!.doctorId,
      scheduledAt: scheduledAt,
    );

    setState(() {
      _isSubmitting = true;
    });

    try {
      await _appointmentRepository.createAppointment(
        request,
      );

      if (!mounted) {
        return;
      }

      await showDialog<void>(
        context: context,
        builder: (context) {
          return AlertDialog(
            title: const Text(
              '예약이 완료되었습니다.',
              style: TextStyle(
                fontWeight: FontWeight.w800,
              ),
            ),
            content: Text(
              '${_selectedHospital!.hospitalName}\n'
              '${_selectedDepartment!.departmentName}\n'
              '${_selectedDoctor!.doctorName}\n'
              '${_formatDate(_selectedDate!)} $_selectedTime',
            ),
            actions: [
              FilledButton(
                onPressed: () {
                  Navigator.of(context).pop();
                },
                child: const Text('확인'),
              ),
            ],
          );
        },
      );

      if (!mounted) {
        return;
      }

      Navigator.of(context).pop();
    } catch (error) {
      if (!mounted) {
        return;
      }

      _showMessage(
        '예약을 완료하지 못했습니다.\n$error',
      );
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
      ),
    );
  }

  String _formatDate(DateTime date) {
    const weekdays = <String>[
      '월',
      '화',
      '수',
      '목',
      '금',
      '토',
      '일',
    ];

    final weekday = weekdays[date.weekday - 1];

    return '${date.year}.${date.month.toString().padLeft(2, '0')}.'
        '${date.day.toString().padLeft(2, '0')} ($weekday)';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FB),
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        elevation: 0,
        title: const Text(
          '진료 예약',
          style: TextStyle(
            color: Color(0xFF111827),
            fontSize: 20,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(
                  20,
                  24,
                  20,
                  24,
                ),
                children: [
                  const Text(
                    '예약 정보를 선택해 주세요.',
                    style: TextStyle(
                      color: Color(0xFF2563EB),
                      fontSize: 21,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    '병원부터 진료 시간까지 순서대로 선택해 주세요.',
                    style: TextStyle(
                      color: Color(0xFF6B7280),
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 24),

                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: const Color(0xFFE5E7EB),
                      ),
                    ),
                    child: Column(
                      children: [
                        _AppointmentSelectTile(
                          icon: Icons.local_hospital_outlined,
                          title: '병원',
                          value:
                              _selectedHospital?.hospitalName,
                          placeholder: '선택해 주세요',
                          enabled: true,
                          onTap: _selectHospital,
                        ),
                        const _TileDivider(),

                        _AppointmentSelectTile(
                          icon: Icons.medical_services_outlined,
                          title: '진료과',
                          value: _selectedDepartment
                              ?.departmentName,
                          placeholder: _canSelectDepartment
                              ? '선택해 주세요'
                              : '병원을 먼저 선택해 주세요',
                          enabled: _canSelectDepartment,
                          onTap: _selectDepartment,
                        ),
                        const _TileDivider(),

                        _AppointmentSelectTile(
                          icon: Icons.person_outline,
                          title: '담당 의료진',
                          value: _selectedDoctor?.doctorName,
                          placeholder: _canSelectDoctor
                              ? '선택해 주세요'
                              : '진료과를 먼저 선택해 주세요',
                          enabled: _canSelectDoctor,
                          onTap: _selectDoctor,
                        ),
                        const _TileDivider(),

                        _AppointmentSelectTile(
                          icon: Icons.calendar_month_outlined,
                          title: '진료 날짜',
                          value: _selectedDate == null
                              ? null
                              : _formatDate(
                                  _selectedDate!,
                                ),
                          placeholder: _canSelectDate
                              ? '선택해 주세요'
                              : '의료진을 먼저 선택해 주세요',
                          enabled: _canSelectDate,
                          onTap: _selectDate,
                        ),
                        const _TileDivider(),

                        _AppointmentSelectTile(
                          icon: Icons.access_time_outlined,
                          title: '진료 시간',
                          value: _selectedTime,
                          placeholder: _canSelectTime
                              ? '선택해 주세요'
                              : '날짜를 먼저 선택해 주세요',
                          enabled: _canSelectTime,
                          onTap: _selectTime,
                          isLast: true,
                        ),
                      ],
                    ),
                  ),

                  if (_canSubmit) ...[
                    const SizedBox(height: 20),

                    _AppointmentSummaryCard(
                      hospitalName:
                          _selectedHospital!.hospitalName,
                      departmentName:
                          _selectedDepartment!.departmentName,
                      doctorName:
                          _selectedDoctor!.doctorName,
                      date: _formatDate(_selectedDate!),
                      time: _selectedTime!,
                    ),
                  ],
                ],
              ),
            ),

            Container(
              padding: const EdgeInsets.fromLTRB(
                20,
                12,
                20,
                24,
              ),
              child: SizedBox(
                width: double.infinity,
                height: 56,
                child: FilledButton(
                  onPressed:
                      !_canSubmit || _isSubmitting
                          ? null
                          : _submitAppointment,
                  style: FilledButton.styleFrom(
                    backgroundColor:
                        const Color(0xFF2563EB),
                    disabledBackgroundColor:
                        const Color(0xFFC7D2FE),
                    disabledForegroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.circular(16),
                    ),
                  ),
                  child: _isSubmitting
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child:
                              CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2.4,
                          ),
                        )
                      : const Text(
                          '예약 확인하기',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AppointmentSelectTile extends StatelessWidget {
  const _AppointmentSelectTile({
    required this.icon,
    required this.title,
    required this.placeholder,
    required this.enabled,
    required this.onTap,
    this.value,
    this.isLast = false,
  });

  final IconData icon;
  final String title;
  final String? value;
  final String placeholder;
  final bool enabled;
  final VoidCallback onTap;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    final hasValue =
        value != null && value!.trim().isNotEmpty;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: enabled ? onTap : null,
        borderRadius: BorderRadius.vertical(
          top: title == '병원'
              ? const Radius.circular(20)
              : Radius.zero,
          bottom: isLast
              ? const Radius.circular(20)
              : Radius.zero,
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 17,
          ),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: enabled
                      ? const Color(0xFFEFF6FF)
                      : const Color(0xFFF1F5F9),
                  borderRadius:
                      BorderRadius.circular(14),
                ),
                child: Icon(
                  icon,
                  color: enabled
                      ? const Color(0xFF2563EB)
                      : const Color(0xFF94A3B8),
                ),
              ),
              const SizedBox(width: 14),

              Expanded(
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        color: enabled
                            ? const Color(0xFF111827)
                            : const Color(0xFF64748B),
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      hasValue ? value! : placeholder,
                      style: TextStyle(
                        color: hasValue
                            ? const Color(0xFF2563EB)
                            : const Color(0xFF64748B),
                        fontSize: 13,
                        fontWeight: hasValue
                            ? FontWeight.w700
                            : FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),

              Icon(
                Icons.chevron_right,
                color: enabled
                    ? const Color(0xFF475569)
                    : const Color(0xFFCBD5E1),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TileDivider extends StatelessWidget {
  const _TileDivider();

  @override
  Widget build(BuildContext context) {
    return const Divider(
      height: 1,
      indent: 16,
      endIndent: 16,
      color: Color(0xFFE8EBF1),
    );
  }
}

class _DepartmentBottomSheet extends StatelessWidget {
  const _DepartmentBottomSheet({
    required this.departments,
  });

  final List<Department> departments;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          20,
          4,
          20,
          28,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [
            const Text(
              '진료과 선택',
              style: TextStyle(
                color: Color(0xFF111827),
                fontSize: 20,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 14),

            ...departments.map(
              (department) {
                return ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const CircleAvatar(
                    backgroundColor: Color(0xFFEFF6FF),
                    child: Icon(
                      Icons.medical_services_outlined,
                      color: Color(0xFF2563EB),
                    ),
                  ),
                  title: Text(
                    department.departmentName,
                    style: const TextStyle(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  trailing: const Icon(
                    Icons.chevron_right,
                  ),
                  onTap: () {
                    Navigator.of(context).pop(
                      department,
                    );
                  },
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _DoctorBottomSheet extends StatelessWidget {
  const _DoctorBottomSheet({
    required this.doctors,
  });

  final List<Doctor> doctors;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          20,
          4,
          20,
          28,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [
            const Text(
              '담당 의료진 선택',
              style: TextStyle(
                color: Color(0xFF111827),
                fontSize: 20,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 14),

            ...doctors.map(
              (doctor) {
                return ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const CircleAvatar(
                    backgroundColor: Color(0xFFEFF6FF),
                    child: Icon(
                      Icons.person_outline,
                      color: Color(0xFF2563EB),
                    ),
                  ),
                  title: Text(
                    doctor.doctorName,
                    style: const TextStyle(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  subtitle: Text(
                    doctor.departmentName,
                  ),
                  trailing: const Icon(
                    Icons.chevron_right,
                  ),
                  onTap: () {
                    Navigator.of(context).pop(
                      doctor,
                    );
                  },
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _TimeBottomSheet extends StatelessWidget {
  const _TimeBottomSheet();

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          20,
          4,
          20,
          28,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [
            const Text(
              '진료 시간 선택',
              style: TextStyle(
                color: Color(0xFF111827),
                fontSize: 20,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 18),

            GridView.builder(
              shrinkWrap: true,
              physics:
                  const NeverScrollableScrollPhysics(),
              itemCount: appointmentTimeMock.length,
              gridDelegate:
                  const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: 2.2,
              ),
              itemBuilder: (context, index) {
                final time =
                    appointmentTimeMock[index];

                return OutlinedButton(
                  onPressed: () {
                    Navigator.of(context).pop(time);
                  },
                  style: OutlinedButton.styleFrom(
                    foregroundColor:
                        const Color(0xFF2563EB),
                    side: const BorderSide(
                      color: Color(0xFFBFDBFE),
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    time,
                    style: const TextStyle(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _AppointmentSummaryCard extends StatelessWidget {
  const _AppointmentSummaryCard({
    required this.hospitalName,
    required this.departmentName,
    required this.doctorName,
    required this.date,
    required this.time,
  });

  final String hospitalName;
  final String departmentName;
  final String doctorName;
  final String date;
  final String time;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFEFF6FF),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          const Text(
            '예약 내용',
            style: TextStyle(
              color: Color(0xFF1D4ED8),
              fontSize: 16,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 14),

          _SummaryRow(
            label: '병원',
            value: hospitalName,
          ),
          _SummaryRow(
            label: '진료과',
            value: departmentName,
          ),
          _SummaryRow(
            label: '의료진',
            value: doctorName,
          ),
          _SummaryRow(
            label: '날짜',
            value: date,
          ),
          _SummaryRow(
            label: '시간',
            value: time,
            isLast: true,
          ),
        ],
      ),
    );
  }
}

class _SummaryRow extends StatelessWidget {
  const _SummaryRow({
    required this.label,
    required this.value,
    this.isLast = false,
  });

  final String label;
  final String value;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: isLast ? 0 : 10,
      ),
      child: Row(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 60,
            child: Text(
              label,
              style: const TextStyle(
                color: Color(0xFF64748B),
                fontSize: 13,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                color: Color(0xFF111827),
                fontSize: 13,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}