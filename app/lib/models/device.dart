// 通用安全类型转换工具类
class TypeConverters {
  static int? safeInt(dynamic value) {
    if (value == null) return null;
    if (value is int) return value;
    if (value is String) return int.tryParse(value);
    if (value is num) return value.toInt();
    return null;
  }

  static double? safeDouble(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    if (value is num) return value.toDouble();
    return null;
  }

  static bool? safeBool(dynamic value) {
    if (value == null) return null;
    if (value is bool) return value;
    if (value is int) return value == 1;
    if (value is String) return value.toLowerCase() == 'true' || value == '1';
    return null;
  }

  static DateTime? safeDateTime(dynamic value) {
    if (value == null) return null;
    if (value is DateTime) return value;
    if (value is String) return DateTime.tryParse(value);
    return null;
  }
}

import '../../utils/type_converters.dart';

class DeviceType {
  final int id;
  final String typeName;

  DeviceType({
    required this.id,
    required this.typeName,
  });

  factory DeviceType.fromJson(Map<String, dynamic> json) {
    return DeviceType(
      id: TypeConverters.safeInt(json['id']) ?? 0,
      typeName: json['type_name']?.toString() ?? (json['device_type']?.toString() ?? ''),
    );
  }
}

class Device {
  final int id;
  final String deviceName;
  final int deviceTypeId;
  final String? deviceTypeName;
  final String location;
  final String? ipAddress;
  final String? mqttTopic;
  final int status; // 1-在线 0-离线
  final double? currentValue; // 当前值
  final DateTime createdAt;

  Device({
    required this.id,
    required this.deviceName,
    required this.deviceTypeId,
    this.deviceTypeName,
    required this.location,
    this.ipAddress,
    this.mqttTopic,
    required this.status,
    this.currentValue,
    required this.createdAt,
  });

  factory Device.fromJson(Map<String, dynamic> json) {
    return Device(
      id: TypeConverters.safeInt(json['id']) ?? 0,
      deviceName: json['device_name']?.toString() ?? '',
      deviceTypeId: TypeConverters.safeInt(json['device_type_id']) ?? 0,
      deviceTypeName: json['device_type_name']?.toString(),
      location: json['location']?.toString() ?? '',
      ipAddress: json['ip_address']?.toString(),
      mqttTopic: json['mqtt_topic']?.toString(),
      status: TypeConverters.safeInt(json['status']) ?? 0,
      currentValue: TypeConverters.safeDouble(json['current_value']),
      createdAt: TypeConverters.safeDateTime(json['created_at']) ?? DateTime.now(),
    );
  }
}

class ControlDevice {
  final int id;
  final String deviceName;
  final String deviceType;
  final String location;
  final int status;
  final String? mqttTopic;
  final double? currentPower;
  final DateTime createdAt;
  final DateTime updatedAt;

  ControlDevice({
    required this.id,
    required this.deviceName,
    required this.deviceType,
    required this.location,
    required this.status,
    this.mqttTopic,
    this.currentPower,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ControlDevice.fromJson(Map<String, dynamic> json) {
    return ControlDevice(
      id: TypeConverters.safeInt(json['id']) ?? 0,
      deviceName: json['device_name']?.toString() ?? '',
      deviceType: json['device_type']?.toString() ?? '',
      location: json['location']?.toString() ?? '',
      status: TypeConverters.safeInt(json['status']) ?? 0,
      mqttTopic: json['mqtt_topic']?.toString(),
      currentPower: TypeConverters.safeDouble(json['current_power']),
      createdAt: TypeConverters.safeDateTime(json['created_at']) ?? DateTime.now(),
      updatedAt: TypeConverters.safeDateTime(json['updated_at']) ?? DateTime.now(),
    );
  }

  String? get deviceIcon => deviceType;
  String? get description => deviceName;

  bool get isOn => status == 1;

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'device_name': deviceName,
      'device_type': deviceType,
      'location': location,
      'status': status,
      'mqtt_topic': mqttTopic,
      'current_power': currentPower,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}
