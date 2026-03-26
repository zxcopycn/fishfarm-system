class Reminder {
  int? id;
  String title;
  String? content;
  String reminderTime;
  bool isCompleted;
  String? completedAt;
  String createdAt;
  String updatedAt;

  Reminder({
    this.id,
    required this.title,
    this.content,
    required this.reminderTime,
    this.isCompleted = false,
    this.completedAt,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Reminder.fromJson(Map<String, dynamic> json) {
    return Reminder(
      id: json['id'],
      title: json['title'] ?? '',
      content: json['content'],
      reminderTime: json['reminder_time'] ?? DateTime.now().toIso8601String(),
      isCompleted: json['is_completed'] == 1,
      completedAt: json['completed_at'],
      createdAt: json['created_at'] ?? DateTime.now().toIso8601String(),
      updatedAt: json['updated_at'] ?? DateTime.now().toIso8601String(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'reminder_time': reminderTime,
      'is_completed': isCompleted ? 1 : 0,
      'completed_at': completedAt,
      'created_at': createdAt,
      'updated_at': updatedAt,
    };
  }

  Reminder copyWith({
    int? id,
    String? title,
    String? content,
    String? reminderTime,
    bool? isCompleted,
    String? completedAt,
    String? createdAt,
    String? updatedAt,
  }) {
    return Reminder(
      id: id ?? this.id,
      title: title ?? this.title,
      content: content ?? this.content,
      reminderTime: reminderTime ?? this.reminderTime,
      isCompleted: isCompleted ?? this.isCompleted,
      completedAt: completedAt ?? this.completedAt,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
