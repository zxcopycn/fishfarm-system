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
      id: json['id'],
      sensorType: json['sensor_type'],
      level: json['level'],
      minThreshold: json['min_threshold'].toDouble(),
      maxThreshold: json['max_threshold'].toDouble(),
      description: json['description'],
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
      id: json['id'],
      deviceId: json['device_id'],
      deviceName: json['device_name'],
      level: AlarmLevel.fromString(json['alarm_level']),
      thresholdValue: json['threshold_value']?.toDouble(),
      actualValue: json['actual_value']?.toDouble(),
      message: json['message'],
      isResolved: json['is_resolved'],
      createdAt: DateTime.parse(json['created_at']),
      timeAgo: json['time_ago'] ?? '',
    );
  }
}
