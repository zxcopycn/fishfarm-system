import '../../utils/type_converters.dart';

class AlarmLevel {
  final String level;
  final int code;

  AlarmLevel(this.level, this.code);

  static AlarmLevel fromString(String level) {
    switch (level) {
      case '提醒':
        return AlarmLevel('提醒', 1);
      case '警告':
        return AlarmLevel('警告', 2);
      case '危险':
        return AlarmLevel('危险', 3);
      default:
        return AlarmLevel('提醒', 1);
    }
  }
}

class AlarmRule {
  final int id;
  final String sensorType;
  final String level;
  final double minThreshold;
  final double maxThreshold;
  final String description;

  AlarmRule({
    required this.id,
    required this.sensorType,
    required this.level,
    required this.minThreshold,
    required this.maxThreshold,
    required this.description,
  });

  factory AlarmRule.fromJson(Map<String, dynamic> json) {
    return AlarmRule(
      id: TypeConverters.safeInt(json['id']) ?? 0,
      sensorType: json['sensor_type']?.toString() ?? '',
      level: json['level']?.toString() ?? '',
      minThreshold: TypeConverters.safeDouble(json['min_threshold']) ?? 0.0,
      maxThreshold: TypeConverters.safeDouble(json['max_threshold']) ?? 0.0,
      description: json['description']?.toString() ?? '',
    );
  }
}

class AlarmRecord {
  final int id;
  final int deviceId;
  final String? deviceName;
  final AlarmLevel level;
  final double? thresholdValue;
  final double? actualValue;
  final String message;
  final int isResolved; // 0-未解决 1-已解决
  final DateTime createdAt;
  final String timeAgo;

  AlarmRecord({
    required this.id,
    required this.deviceId,
    this.deviceName,
    required this.level,
    this.thresholdValue,
    this.actualValue,
    required this.message,
    required this.isResolved,
    required this.createdAt,
    required this.timeAgo,
  });

  factory AlarmRecord.fromJson(Map<String, dynamic> json) {
    return AlarmRecord(
      id: TypeConverters.safeInt(json['id']) ?? 0,
      deviceId: TypeConverters.safeInt(json['device_id']) ?? 0,
      deviceName: json['device_name']?.toString(),
      level: AlarmLevel.fromString(json['alarm_level']),
      thresholdValue: TypeConverters.safeDouble(json['threshold_value']),
      actualValue: TypeConverters.safeDouble(json['actual_value']),
      message: json['message']?.toString() ?? '',
      isResolved: TypeConverters.safeInt(json['is_resolved']) ?? 0,
      createdAt: TypeConverters.safeDateTime(json['created_at']) ?? DateTime.now(),
      timeAgo: json['time_ago']?.toString() ?? '',
    );
  }

  AlarmRecord copyWith({
    int? id,
    int? deviceId,
    String? deviceName,
    AlarmLevel? level,
    double? thresholdValue,
    double? actualValue,
    String? message,
    int? isResolved,
    DateTime? createdAt,
    String? timeAgo,
  }) {
    return AlarmRecord(
      id: id ?? this.id,
      deviceId: deviceId ?? this.deviceId,
      deviceName: deviceName ?? this.deviceName,
      level: level ?? this.level,
      thresholdValue: thresholdValue ?? this.thresholdValue,
      actualValue: actualValue ?? this.actualValue,
      message: message ?? this.message,
      isResolved: isResolved ?? this.isResolved,
      createdAt: createdAt ?? this.createdAt,
      timeAgo: timeAgo ?? this.timeAgo,
    );
  }
}
