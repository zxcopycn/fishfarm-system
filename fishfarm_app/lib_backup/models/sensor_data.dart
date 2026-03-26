import 'dart:convert';

class SensorData {
  final int id;
  final int deviceId;
  final double temperature;
  final double ph;
  final double ammonia;
  final double nitrite;
  final double oxygen;
  final double humidity;
  final DateTime timestamp;
  final Map<String, dynamic>? additionalData;

  SensorData({
    required this.id,
    required this.deviceId,
    required this.temperature,
    required this.ph,
    required this.ammonia,
    required this.nitrite,
    required this.oxygen,
    required this.humidity,
    required this.timestamp,
    this.additionalData,
  });

  // 从JSON创建对象
  factory SensorData.fromJson(Map<String, dynamic> json) {
    return SensorData(
      id: json['id'],
      deviceId: json['device_id'],
      temperature: (json['temperature'] as num).toDouble(),
      ph: (json['ph'] as num).toDouble(),
      ammonia: (json['ammonia'] as num).toDouble(),
      nitrite: (json['nitrite'] as num).toDouble(),
      oxygen: (json['oxygen'] as num).toDouble(),
      humidity: (json['humidity'] as num).toDouble(),
      timestamp: DateTime.parse(json['timestamp']),
      additionalData: json['additional_data'],
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