class ClinicianSupportFaq {
  const ClinicianSupportFaq({
    required this.id,
    required this.question,
    required this.answer,
  });
  final String id, question, answer;
  factory ClinicianSupportFaq.fromJson(Map<String, dynamic> json) =>
      ClinicianSupportFaq(
        id: json['id']?.toString() ?? '',
        question: json['question']?.toString() ?? '',
        answer: json['answer']?.toString() ?? '',
      );
}
