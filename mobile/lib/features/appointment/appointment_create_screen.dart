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

  final DoctorRepository _doctorRepository = DoctorRepository();

  final AppointmentCreateRepository _appointmentRepository =
      AppointmentCreateRepository();

  Hospital? _selectedHospital;
  Department? _selectedDepartment;
  Doctor? _selectedDoctor;
  DateTime? _selectedDate;
  String? _selectedTime;

  List<Department> _departments = [];
  List<Doctor> _doctors = [];

  int _currentStep = 0;

  bool _isLoading = false;
  bool _isSubmitting = false;

  bool get _canSubmit =>
      _selectedHospital != null &&
      _selectedDepartment != null &&
      _selectedDoctor != null &&
      _selectedDate != null &&
      _selectedTime != null;

  // ============================================================
  // 병원 선택
  // ============================================================
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

      // 상위 항목이 바뀌면 하위 선택값 초기화
      _selectedDepartment = null;
      _selectedDoctor = null;
      _selectedDate = null;
      _selectedTime = null;

      _departments = [];
      _doctors = [];

      _isLoading = true;
    });

    try {
      final departments =
          await _departmentRepository.getDepartmentsByHospital(
        hospital.hospitalId,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _departments = departments;
        _isLoading = false;

        // 병원 선택 후 진료과 단계로 자동 이동
        _currentStep = 1;
      });

      if (departments.isEmpty) {
        _showMessage('선택한 병원에 등록된 진료과가 없습니다.');
      }
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
      });

      _showMessage('진료과 정보를 불러오지 못했습니다.');
    }
  }

  // ============================================================
  // 진료과 선택
  // ============================================================
  Future<void> _selectDepartment(
    Department department,
  ) async {
    setState(() {
      _selectedDepartment = department;

      _selectedDoctor = null;
      _selectedDate = null;
      _selectedTime = null;

      _doctors = [];
      _isLoading = true;
    });

    try {
      final doctors =
          await _doctorRepository.getDoctorsByDepartment(
        department.departmentId,
      );

      if (!mounted) {
        return;
      }

      setState(() {
        _doctors = doctors;
        _isLoading = false;

        // 진료과 선택 후 의료진 단계로 자동 이동
        _currentStep = 2;
      });

      if (doctors.isEmpty) {
        _showMessage('선택한 진료과에 등록된 의료진이 없습니다.');
      }
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _isLoading = false;
      });

      _showMessage('의료진 정보를 불러오지 못했습니다.');
    }
  }

  // ============================================================
  // 의료진 선택
  // ============================================================
  void _selectDoctor(Doctor doctor) {
    setState(() {
      _selectedDoctor = doctor;

      _selectedDate = null;
      _selectedTime = null;

      // 의료진 선택 후 날짜 단계로 자동 이동
      _currentStep = 3;
    });
  }

  // ============================================================
  // 날짜 선택
  // ============================================================
  Future<void> _selectDate() async {
    final today = DateTime.now();

    final selectedDate = await showDatePicker(
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

    if (selectedDate == null || !mounted) {
      return;
    }

    setState(() {
      _selectedDate = selectedDate;
      _selectedTime = null;

      // 날짜 선택 후 시간 단계로 자동 이동
      _currentStep = 4;
    });
  }

  // ============================================================
  // 시간 선택
  // ============================================================
  void _selectTime(String time) {
    setState(() {
      _selectedTime = time;

      // 시간 선택 후 예약 확인 단계로 자동 이동
      _currentStep = 5;
    });
  }

  // ============================================================
  // 완료한 이전 단계로 돌아가기
  // ============================================================
  void _moveToStep(int step) {
    final highestAvailableStep = _highestAvailableStep;

    if (step > highestAvailableStep) {
      return;
    }

    setState(() {
      _currentStep = step;
    });
  }

  int get _highestAvailableStep {
    if (_selectedHospital == null) {
      return 0;
    }

    if (_selectedDepartment == null) {
      return 1;
    }

    if (_selectedDoctor == null) {
      return 2;
    }

    if (_selectedDate == null) {
      return 3;
    }

    if (_selectedTime == null) {
      return 4;
    }

    return 5;
  }

  // ============================================================
  // 예약 생성
  // ============================================================
  Future<void> _submitAppointment() async {
    if (!_canSubmit || _isSubmitting) {
      _showMessage('예약 정보를 모두 선택해 주세요.');
      return;
    }

    final timeParts = _selectedTime!.split(':');

    if (timeParts.length != 2) {
      _showMessage('진료 시간 형식이 올바르지 않습니다.');
      return;
    }

    final hour = int.tryParse(timeParts[0]);
    final minute = int.tryParse(timeParts[1]);

    if (hour == null || minute == null) {
      _showMessage('진료 시간 형식이 올바르지 않습니다.');
      return;
    }

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
      await _appointmentRepository.createAppointment(request);

      if (!mounted) {
        return;
      }

      await showDialog<void>(
        context: context,
        barrierDismissible: false,
        builder: (dialogContext) {
          return AlertDialog(
            title: const Row(
              children: [
                Icon(
                  Icons.check_circle_rounded,
                  color: Color(0xFF2563EB),
                ),
                SizedBox(width: 8),
                Text(
                  '예약 완료',
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
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
                  Navigator.of(dialogContext).pop();
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

      Navigator.of(context).pop(true);
    } catch (error) {
      if (!mounted) {
        return;
      }

      _showMessage('예약을 완료하지 못했습니다.');
    } finally {
      if (mounted) {
        setState(() {
          _isSubmitting = false;
        });
      }
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(message),
          behavior: SnackBarBehavior.floating,
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

  String get _stepTitle {
    switch (_currentStep) {
      case 0:
        return '병원을 선택해 주세요.';
      case 1:
        return '진료과를 선택해 주세요.';
      case 2:
        return '담당 의료진을 선택해 주세요.';
      case 3:
        return '진료 날짜를 선택해 주세요.';
      case 4:
        return '진료 시간을 선택해 주세요.';
      case 5:
        return '예약 정보를 확인해 주세요.';
      default:
        return '예약 정보를 선택해 주세요.';
    }
  }

  String get _stepDescription {
    switch (_currentStep) {
      case 0:
        return '검색하거나 찜한 병원에서 선택할 수 있습니다.';
      case 1:
        return '${_selectedHospital?.hospitalName ?? ''}의 진료과입니다.';
      case 2:
        return '${_selectedDepartment?.departmentName ?? ''} 의료진을 선택해 주세요.';
      case 3:
        return '진료 가능한 날짜를 선택해 주세요.';
      case 4:
        return '원하는 진료 시간을 선택해 주세요.';
      case 5:
        return '아래 정보가 맞는지 확인한 후 예약해 주세요.';
      default:
        return '';
    }
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
            // ======================================================
            // 상단 진행 상태창
            // ======================================================
            Container(
              color: Colors.white,
              padding: const EdgeInsets.fromLTRB(
                16,
                14,
                16,
                16,
              ),
              child: _AppointmentStepIndicator(
                currentStep: _currentStep,
                highestAvailableStep: _highestAvailableStep,
                onStepTap: _moveToStep,
              ),
            ),

            Expanded(
              child: _isLoading
                  ? const Center(
                      child: CircularProgressIndicator(),
                    )
                  : AnimatedSwitcher(
                      duration: const Duration(
                        milliseconds: 280,
                      ),
                      switchInCurve: Curves.easeOut,
                      switchOutCurve: Curves.easeIn,
                      transitionBuilder: (
                        child,
                        animation,
                      ) {
                        final offsetAnimation = Tween<Offset>(
                          begin: const Offset(0.08, 0),
                          end: Offset.zero,
                        ).animate(animation);

                        return FadeTransition(
                          opacity: animation,
                          child: SlideTransition(
                            position: offsetAnimation,
                            child: child,
                          ),
                        );
                      },
                      child: _buildCurrentStep(),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentStep() {
    return ListView(
      key: ValueKey<int>(_currentStep),
      padding: const EdgeInsets.fromLTRB(
        20,
        24,
        20,
        32,
      ),
      children: [
        Text(
          _stepTitle,
          style: const TextStyle(
            color: Color(0xFF111827),
            fontSize: 23,
            fontWeight: FontWeight.w800,
          ),
        ),

        const SizedBox(height: 7),

        Text(
          _stepDescription,
          style: const TextStyle(
            color: Color(0xFF6B7280),
            fontSize: 14,
            height: 1.4,
          ),
        ),

        const SizedBox(height: 26),

        switch (_currentStep) {
          0 => _buildHospitalStep(),
          1 => _buildDepartmentStep(),
          2 => _buildDoctorStep(),
          3 => _buildDateStep(),
          4 => _buildTimeStep(),
          _ => _buildConfirmStep(),
        },
      ],
    );
  }

  // ============================================================
  // 1단계: 병원
  // ============================================================
  Widget _buildHospitalStep() {
    return Column(
      children: [
        _SelectedValueCard(
          icon: Icons.local_hospital_outlined,
          title: '병원',
          value: _selectedHospital?.hospitalName,
          emptyText: '아직 병원을 선택하지 않았습니다.',
        ),

        const SizedBox(height: 18),

        SizedBox(
          width: double.infinity,
          height: 56,
          child: FilledButton.icon(
            onPressed: _selectHospital,
            icon: const Icon(Icons.search_rounded),
            label: Text(
              _selectedHospital == null
                  ? '병원 검색하기'
                  : '병원 다시 선택하기',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
              ),
            ),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF2563EB),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
          ),
        ),
      ],
    );
  }

  // ============================================================
  // 2단계: 진료과
  // ============================================================
  Widget _buildDepartmentStep() {
    if (_departments.isEmpty) {
      return _EmptyStepCard(
        icon: Icons.medical_services_outlined,
        message: '선택 가능한 진료과가 없습니다.',
        buttonText: '병원 다시 선택하기',
        onPressed: () {
          _moveToStep(0);
        },
      );
    }

    return Column(
      children: _departments.map((department) {
        final selected =
            _selectedDepartment?.departmentId ==
            department.departmentId;

        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: _SelectionCard(
            icon: Icons.medical_services_outlined,
            title: department.departmentName,
            subtitle: _selectedHospital?.hospitalName,
            selected: selected,
            onTap: () {
              _selectDepartment(department);
            },
          ),
        );
      }).toList(),
    );
  }

  // ============================================================
  // 3단계: 의료진
  // ============================================================
  Widget _buildDoctorStep() {
    if (_doctors.isEmpty) {
      return _EmptyStepCard(
        icon: Icons.person_outline,
        message: '선택 가능한 의료진이 없습니다.',
        buttonText: '진료과 다시 선택하기',
        onPressed: () {
          _moveToStep(1);
        },
      );
    }

    return Column(
      children: _doctors.map((doctor) {
        final selected =
            _selectedDoctor?.doctorId == doctor.doctorId;

        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: _SelectionCard(
            icon: Icons.person_outline,
            title: doctor.doctorName,
            subtitle: doctor.departmentName,
            selected: selected,
            onTap: () {
              _selectDoctor(doctor);
            },
          ),
        );
      }).toList(),
    );
  }

  // ============================================================
  // 4단계: 날짜
  // ============================================================
  Widget _buildDateStep() {
    return Column(
      children: [
        _SelectedValueCard(
          icon: Icons.calendar_month_outlined,
          title: '선택한 날짜',
          value: _selectedDate == null
              ? null
              : _formatDate(_selectedDate!),
          emptyText: '진료 날짜를 선택해 주세요.',
        ),

        const SizedBox(height: 18),

        SizedBox(
          width: double.infinity,
          height: 56,
          child: FilledButton.icon(
            onPressed: _selectDate,
            icon: const Icon(
              Icons.calendar_month_outlined,
            ),
            label: Text(
              _selectedDate == null
                  ? '날짜 선택하기'
                  : '날짜 다시 선택하기',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
              ),
            ),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF2563EB),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
          ),
        ),
      ],
    );
  }

  // ============================================================
  // 5단계: 시간
  // ============================================================
  Widget _buildTimeStep() {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: appointmentTimeMock.length,
      gridDelegate:
          const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 2.1,
      ),
      itemBuilder: (context, index) {
        final time = appointmentTimeMock[index];
        final selected = _selectedTime == time;

        return OutlinedButton(
          onPressed: () {
            _selectTime(time);
          },
          style: OutlinedButton.styleFrom(
            foregroundColor: selected
                ? Colors.white
                : const Color(0xFF2563EB),
            backgroundColor: selected
                ? const Color(0xFF2563EB)
                : Colors.white,
            side: BorderSide(
              color: selected
                  ? const Color(0xFF2563EB)
                  : const Color(0xFFBFDBFE),
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
          ),
          child: Text(
            time,
            style: const TextStyle(
              fontWeight: FontWeight.w800,
            ),
          ),
        );
      },
    );
  }

  // ============================================================
  // 6단계: 예약 확인
  // ============================================================
  Widget _buildConfirmStep() {
    return Column(
      children: [
        _AppointmentSummaryCard(
          hospitalName:
              _selectedHospital?.hospitalName ?? '',
          departmentName:
              _selectedDepartment?.departmentName ?? '',
          doctorName: _selectedDoctor?.doctorName ?? '',
          date: _selectedDate == null
              ? ''
              : _formatDate(_selectedDate!),
          time: _selectedTime ?? '',
          onEditStep: _moveToStep,
        ),

        const SizedBox(height: 22),

        SizedBox(
          width: double.infinity,
          height: 56,
          child: FilledButton(
            onPressed:
                !_canSubmit || _isSubmitting
                    ? null
                    : _submitAppointment,
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF2563EB),
              disabledBackgroundColor:
                  const Color(0xFFC7D2FE),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
            child: _isSubmitting
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(
                      color: Colors.white,
                      strokeWidth: 2.4,
                    ),
                  )
                : const Text(
                    '예약 확정하기',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
          ),
        ),
      ],
    );
  }
}

// =================================================================
// 예약 진행 상태 표시기
// =================================================================
class _AppointmentStepIndicator extends StatelessWidget {
  const _AppointmentStepIndicator({
    required this.currentStep,
    required this.highestAvailableStep,
    required this.onStepTap,
  });

  final int currentStep;
  final int highestAvailableStep;
  final ValueChanged<int> onStepTap;

  static const List<String> _labels = [
    '병원',
    '진료과',
    '의료진',
    '날짜',
    '시간',
    '확인',
  ];

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: List.generate(
        _labels.length * 2 - 1,
        (position) {
          if (position.isOdd) {
            final leftStep = (position - 1) ~/ 2;
            final completed =
                highestAvailableStep > leftStep;

            return Expanded(
              child: AnimatedContainer(
                duration: const Duration(
                  milliseconds: 220,
                ),
                height: 2,
                margin: const EdgeInsets.only(
                  top: 15,
                  left: 2,
                  right: 2,
                ),
                color: completed
                    ? const Color(0xFF2563EB)
                    : const Color(0xFFE2E8F0),
              ),
            );
          }

          final index = position ~/ 2;
          final completed = index < currentStep;
          final current = index == currentStep;
          final available =
              index <= highestAvailableStep;

          return GestureDetector(
            onTap: available
                ? () {
                    onStepTap(index);
                  }
                : null,
            behavior: HitTestBehavior.opaque,
            child: SizedBox(
              width: 38,
              child: Column(
                children: [
                  AnimatedContainer(
                    duration: const Duration(
                      milliseconds: 220,
                    ),
                    width: 30,
                    height: 30,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: completed || current
                          ? const Color(0xFF2563EB)
                          : Colors.white,
                      border: Border.all(
                        color: completed || current
                            ? const Color(0xFF2563EB)
                            : const Color(0xFFCBD5E1),
                        width: 1.5,
                      ),
                    ),
                    child: completed
                        ? const Icon(
                            Icons.check_rounded,
                            size: 18,
                            color: Colors.white,
                          )
                        : Text(
                            '${index + 1}',
                            style: TextStyle(
                              color: current
                                  ? Colors.white
                                  : const Color(
                                      0xFF94A3B8,
                                    ),
                              fontSize: 12,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                  ),

                  const SizedBox(height: 6),

                  Text(
                    _labels[index],
                    maxLines: 1,
                    style: TextStyle(
                      color: completed || current
                          ? const Color(0xFF2563EB)
                          : const Color(0xFF94A3B8),
                      fontSize: 10,
                      fontWeight: current
                          ? FontWeight.w800
                          : FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

// =================================================================
// 공통 선택 카드
// =================================================================
class _SelectionCard extends StatelessWidget {
  const _SelectionCard({
    required this.icon,
    required this.title,
    required this.selected,
    required this.onTap,
    this.subtitle,
  });

  final IconData icon;
  final String title;
  final String? subtitle;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: selected
                  ? const Color(0xFF2563EB)
                  : const Color(0xFFE5E7EB),
              width: selected ? 1.5 : 1,
            ),
          ),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Icon(
                  icon,
                  color: const Color(0xFF2563EB),
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
                      style: const TextStyle(
                        color: Color(0xFF111827),
                        fontSize: 16,
                        fontWeight: FontWeight.w800,
                      ),
                    ),

                    if (subtitle != null &&
                        subtitle!.trim().isNotEmpty) ...[
                      const SizedBox(height: 5),
                      Text(
                        subtitle!,
                        style: const TextStyle(
                          color: Color(0xFF6B7280),
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ],
                ),
              ),

              Icon(
                selected
                    ? Icons.check_circle_rounded
                    : Icons.chevron_right_rounded,
                color: selected
                    ? const Color(0xFF2563EB)
                    : const Color(0xFF94A3B8),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// =================================================================
// 현재 선택값 카드
// =================================================================
class _SelectedValueCard extends StatelessWidget {
  const _SelectedValueCard({
    required this.icon,
    required this.title,
    required this.emptyText,
    this.value,
  });

  final IconData icon;
  final String title;
  final String? value;
  final String emptyText;

  @override
  Widget build(BuildContext context) {
    final hasValue =
        value != null && value!.trim().isNotEmpty;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: const Color(0xFFE5E7EB),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: const Color(0xFFEFF6FF),
              borderRadius: BorderRadius.circular(15),
            ),
            child: Icon(
              icon,
              color: const Color(0xFF2563EB),
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
                  style: const TextStyle(
                    color: Color(0xFF6B7280),
                    fontSize: 13,
                  ),
                ),

                const SizedBox(height: 5),

                Text(
                  hasValue ? value! : emptyText,
                  style: TextStyle(
                    color: hasValue
                        ? const Color(0xFF111827)
                        : const Color(0xFF94A3B8),
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
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

// =================================================================
// 비어 있는 단계 안내
// =================================================================
class _EmptyStepCard extends StatelessWidget {
  const _EmptyStepCard({
    required this.icon,
    required this.message,
    required this.buttonText,
    required this.onPressed,
  });

  final IconData icon;
  final String message;
  final String buttonText;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: const Color(0xFFE5E7EB),
        ),
      ),
      child: Column(
        children: [
          Icon(
            icon,
            size: 42,
            color: const Color(0xFF94A3B8),
          ),

          const SizedBox(height: 12),

          Text(
            message,
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: Color(0xFF6B7280),
              fontSize: 14,
            ),
          ),

          const SizedBox(height: 18),

          OutlinedButton(
            onPressed: onPressed,
            child: Text(buttonText),
          ),
        ],
      ),
    );
  }
}

// =================================================================
// 예약 확인 카드
// =================================================================
class _AppointmentSummaryCard extends StatelessWidget {
  const _AppointmentSummaryCard({
    required this.hospitalName,
    required this.departmentName,
    required this.doctorName,
    required this.date,
    required this.time,
    required this.onEditStep,
  });

  final String hospitalName;
  final String departmentName;
  final String doctorName;
  final String date;
  final String time;
  final ValueChanged<int> onEditStep;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: const Color(0xFFE5E7EB),
        ),
      ),
      child: Column(
        children: [
          _SummaryRow(
            label: '병원',
            value: hospitalName,
            onEdit: () => onEditStep(0),
          ),
          _SummaryRow(
            label: '진료과',
            value: departmentName,
            onEdit: () => onEditStep(1),
          ),
          _SummaryRow(
            label: '의료진',
            value: doctorName,
            onEdit: () => onEditStep(2),
          ),
          _SummaryRow(
            label: '날짜',
            value: date,
            onEdit: () => onEditStep(3),
          ),
          _SummaryRow(
            label: '시간',
            value: time,
            onEdit: () => onEditStep(4),
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
    required this.onEdit,
    this.isLast = false,
  });

  final String label;
  final String value;
  final VoidCallback onEdit;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: isLast ? 0 : 14,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          SizedBox(
            width: 58,
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
                fontSize: 14,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),

          TextButton(
            onPressed: onEdit,
            child: const Text(
              '수정',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}