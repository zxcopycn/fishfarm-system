import '../../utils/type_converters.dart';

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
      id: TypeConverters.safeInt(json['id']) ?? 0,
      title: json['title']?.toString() ?? '',
      content: json['content']?.toString(),
      reminderTime: json['reminder_time']?.toString() ?? DateTime.now().toIso8601String(),
      isCompleted: TypeConverters.safeBool(json['is_completed']) ?? false,
      completedAt: json['completed_at']?.toString(),
      createdAt: json['created_at']?.toString() ?? DateTime.now().toIso8601String(),
      updatedAt: json['updated_at']?.toString() ?? DateTime.now().toIso8601String(),
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
