class EmergencyAiRequest {
  const EmergencyAiRequest({
    required this.symptomText,
    this.patientId,
  });

  final String symptomText;
  final int? patientId;

  Map<String, dynamic> toJson() {
    return {
      'symptom_text': symptomText,
      if (patientId != null) 'patient_id': patientId,
    };
  }
}
