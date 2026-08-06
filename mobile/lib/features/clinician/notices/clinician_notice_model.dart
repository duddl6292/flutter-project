class ClinicianNotice {
  const ClinicianNotice({
    required this.id,
    required this.title,
    required this.content,
    required this.publishedAt,
    required this.isImportant,
  });
  final String id, title, content;
  final DateTime? publishedAt;
  final bool isImportant;
  factory ClinicianNotice.fromJson(Map<String, dynamic> json) =>
      ClinicianNotice(
        id: json['id']?.toString() ?? '',
        title: json['title']?.toString() ?? '',
        content: json['content']?.toString() ?? '',
        publishedAt: DateTime.tryParse(json['published_at']?.toString() ?? ''),
        isImportant: json['is_important'] == true,
      );
}
