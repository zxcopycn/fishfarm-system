import 'dart:convert';

class SensorData {
  final int id;
  final int deviceId;
  final String? deviceName;
  final double temperature;
  final double ph;
  final double ammonia;
  final double nitrite;
  final double oxygen;
  final double humidity;
  final DateTime timestamp;
  final DateTime createdAt;
  final String? status;
  final Map<String, dynamic>? additionalData;

  SensorData({
    required this.id,
    required this.deviceId,
    this.deviceName,
    required this.temperature,
    required this.ph,
    required this.ammonia,
    required this.nitrite,
    required this.oxygen,
    this.humidity = 0.0,
    required this.timestamp,
    required this.createdAt,
    this.status,
    this.additionalData,
  });

  // 从JSON创建对象
  factory SensorData.fromJson(Map<String, dynamic> json) {
    return SensorData(
      id: json['id'],
      deviceId: json['device_id'],
      deviceName: json['device_name'],
      temperature: (json['temperature'] as num?)?.toDouble() ?? 0.0,
      ph: (json['ph'] as num?)?.toDouble() ?? 0.0,
      ammonia: (json['ammonia'] as num?)?.toDouble() ?? 0.0,
      nitrite: (json['nitrite'] as num?)?.toDouble() ?? 0.0,
      oxygen: (json['oxygen'] as num?)?.toDouble() ?? 0.0,
      humidity: 0.0, // 后端没有提供此字段，使用默认值
      timestamp: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      status: json['status'],
      additionalData: json,
    );
  }

  // 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'device_id': deviceId,
      'temperature': temperature,
      'ph': ph,
      'ammonia': ammonia,
      'nitrite': nitrite,
      'oxygen': oxygen,
      'humidity': humidity,
      'timestamp': timestamp.toIso8601String(),
      'additional_data': additionalData,
    };
  }
}