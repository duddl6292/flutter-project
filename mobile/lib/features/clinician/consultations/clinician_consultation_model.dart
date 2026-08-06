class ConsultationClinician {
  const ConsultationClinician({
    required this.id,
    required this.name,
    required this.departmentName,
    required this.hospitalName,
  });
  final String id, name, departmentName, hospitalName;
  factory ConsultationClinician.fromJson(Map<String, dynamic>? json) =>
      ConsultationClinician(
        id: json?['clinician_id']?.toString() ?? '',
        name: json?['name']?.toString() ?? '',
        departmentName:
            json?['department_name']?.toString() ??
            (json?['department'] as Map<String, dynamic>?)?['name']
                ?.toString() ??
            '',
        hospitalName:
            json?['hospital_name']?.toString() ??
            (json?['hospital'] as Map<String, dynamic>?)?['hospital_name']
                ?.toString() ??
            '',
      );
}

class ConsultationAttachment {
  const ConsultationAttachment({
    required this.id,
    required this.type,
    required this.sourceId,
    required this.displayName,
  });
  final String id, type, sourceId, displayName;
  factory ConsultationAttachment.fromJson(Map<String, dynamic> json) =>
      ConsultationAttachment(
        id: json['attachment_id']?.toString() ?? '',
        type: json['attachment_type']?.toString() ?? '',
        sourceId: json['source_id']?.toString() ?? '',
        displayName: json['display_name']?.toString() ?? '',
      );
}

class ConsultationMessage {
  const ConsultationMessage({
    required this.id,
    required this.sender,
    required this.content,
    required this.isSystem,
    required this.createdAt,
    required this.attachments,
  });
  final String id, content;
  final ConsultationClinician sender;
  final bool isSystem;
  final DateTime? createdAt;
  final List<ConsultationAttachment> attachments;
  factory ConsultationMessage.fromJson(Map<String, dynamic> json) =>
      ConsultationMessage(
        id: json['message_id']?.toString() ?? '',
        sender: ConsultationClinician.fromJson(
          json['sender'] as Map<String, dynamic>?,
        ),
        content: json['content']?.toString() ?? '',
        isSystem: json['is_system'] == true,
        createdAt: DateTime.tryParse(
          json['created_at']?.toString() ?? '',
        )?.toLocal(),
        attachments: (json['attachments'] as List<dynamic>? ?? const [])
            .map(
              (item) =>
                  ConsultationAttachment.fromJson(item as Map<String, dynamic>),
            )
            .toList(),
      );
}

class ClinicianConsultation {
  const ClinicianConsultation({
    required this.id,
    required this.encounterId,
    required this.encounterNumber,
    required this.patientId,
    required this.patientNumber,
    required this.patientName,
    required this.patientBirthDate,
    required this.patientSex,
    required this.departmentName,
    required this.requester,
    required this.consultant,
    required this.subject,
    required this.priority,
    required this.priorityLabel,
    required this.question,
    required this.response,
    required this.status,
    required this.statusLabel,
    required this.myRole,
    required this.unreadCount,
    required this.messages,
    required this.dueAt,
    required this.completedAt,
    required this.createdAt,
  });
  final String id,
      encounterId,
      encounterNumber,
      patientId,
      patientNumber,
      patientName,
      patientSex,
      departmentName,
      subject,
      priority,
      priorityLabel,
      question,
      response,
      status,
      statusLabel,
      myRole;
  final DateTime? patientBirthDate, dueAt, completedAt, createdAt;
  final ConsultationClinician requester, consultant;
  final int unreadCount;
  final List<ConsultationMessage> messages;
  bool get isReceived => myRole == 'CONSULTANT';

  factory ClinicianConsultation.fromJson(Map<String, dynamic> json) =>
      ClinicianConsultation(
        id: json['consultation_id']?.toString() ?? '',
        encounterId: json['encounter_id']?.toString() ?? '',
        encounterNumber: json['encounter_number']?.toString() ?? '',
        patientId: json['patient_id']?.toString() ?? '',
        patientNumber: json['patient_number']?.toString() ?? '',
        patientName: json['patient_name']?.toString() ?? '',
        patientBirthDate: DateTime.tryParse(
          json['patient_birth_date']?.toString() ?? '',
        ),
        patientSex: json['patient_sex']?.toString() ?? '',
        departmentName: json['department_name']?.toString() ?? '',
        requester: ConsultationClinician.fromJson(
          json['requester'] as Map<String, dynamic>?,
        ),
        consultant: ConsultationClinician.fromJson(
          json['consultant'] as Map<String, dynamic>?,
        ),
        subject: json['subject']?.toString() ?? '',
        priority: json['priority']?.toString() ?? '',
        priorityLabel: json['priority_label']?.toString() ?? '',
        question: json['question']?.toString() ?? '',
        response: json['response']?.toString() ?? '',
        status: json['status']?.toString() ?? '',
        statusLabel: json['status_label']?.toString() ?? '',
        myRole: json['my_role']?.toString() ?? '',
        unreadCount: int.tryParse(json['unread_count']?.toString() ?? '') ?? 0,
        messages: (json['messages'] as List<dynamic>? ?? const [])
            .map(
              (item) =>
                  ConsultationMessage.fromJson(item as Map<String, dynamic>),
            )
            .toList(),
        dueAt: DateTime.tryParse(json['due_at']?.toString() ?? '')?.toLocal(),
        completedAt: DateTime.tryParse(
          json['completed_at']?.toString() ?? '',
        )?.toLocal(),
        createdAt: DateTime.tryParse(
          json['created_at']?.toString() ?? '',
        )?.toLocal(),
      );
}

class ConsultationContext {
  const ConsultationContext({
    required this.encounterId,
    required this.encounterNumber,
    required this.patientId,
    required this.patientNumber,
    required this.patientName,
    required this.departmentName,
  });
  final String encounterId,
      encounterNumber,
      patientId,
      patientNumber,
      patientName,
      departmentName;
  factory ConsultationContext.fromJson(Map<String, dynamic> json) =>
      ConsultationContext(
        encounterId: json['encounter_id']?.toString() ?? '',
        encounterNumber: json['encounter_number']?.toString() ?? '',
        patientId: json['patient_id']?.toString() ?? '',
        patientNumber: json['patient_number']?.toString() ?? '',
        patientName: json['patient_name']?.toString() ?? '',
        departmentName: json['department_name']?.toString() ?? '',
      );
}

class ConsultationCreateInput {
  const ConsultationCreateInput({
    required this.encounterId,
    required this.consultantId,
    required this.subject,
    required this.priority,
    required this.question,
    required this.dueAt,
  });
  final String encounterId, consultantId, subject, priority, question;
  final DateTime? dueAt;
  Map<String, dynamic> toJson() => {
    'encounter_id': encounterId,
    'consultant_clinician_id': consultantId,
    'subject': subject,
    'priority': priority,
    'question': question,
    'due_at': dueAt?.toUtc().toIso8601String(),
  };
}
