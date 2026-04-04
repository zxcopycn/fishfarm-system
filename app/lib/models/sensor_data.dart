import 'dart:convert';
import '../../utils/type_converters.dart';

class SensorData {
  final int id;
  final int deviceId;
  final String? deviceName;
  final double? temperature;  // 修改为可为空
  final double? ph;          // 修改为可为空
  final double? ammonia;     // 修改为可为空
  final double? nitrite;     // 修改为可为空
  final double? oxygen;      // 修改为可为空
  final double humidity;
  final DateTime timestamp;
  final DateTime createdAt;
  final String? status;
  final Map<String, dynamic>? additionalData;

  SensorData({
    required this.id,
    required this.deviceId,
    this.deviceName,
    this.temperature,
    this.ph,
    this.ammonia,
    this.nitrite,
    this.oxygen,
    this.humidity = 0.0,
    required this.timestamp,
    required this.createdAt,
    this.status,
    this.additionalData,
  });

  // 从JSON创建对象
  factory SensorData.fromJson(Map<String, dynamic> json) {
    return SensorData(
      id: TypeConverters.safeInt(json['id']) ?? 0,
      deviceId: TypeConverters.safeInt(json['device_id']) ?? 0,
      deviceName: json['device_name']?.toString(),
      temperature: TypeConverters.safeDouble(json['temperature']),
      ph: TypeConverters.safeDouble(json['ph']),
      ammonia: TypeConverters.safeDouble(json['ammonia']),
      nitrite: TypeConverters.safeDouble(json['nitrite']),
      oxygen: TypeConverters.safeDouble(json['oxygen']),
      humidity: 0.0, // 后端没有提供此字段，使用默认值
      timestamp: TypeConverters.safeDateTime(json['created_at']) ?? DateTime.now(),
      createdAt: TypeConverters.safeDateTime(json['created_at']) ?? DateTime.now(),
      status: json['status']?.toString(),
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