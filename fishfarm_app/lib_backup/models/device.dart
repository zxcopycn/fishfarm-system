class DeviceType {
  final int id;
  final String typeName;

  DeviceType({
    required this.id,
    required this.typeName,
  });

  factory DeviceType.fromJson(Map<String, dynamic> json) {
    return DeviceType(
      id: json['id'],
      typeName: json['type_name'] ?? json['device_type'],
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
      id: json['id'],
      deviceName: json['device_name'],
      deviceTypeId: json['device_type_id'],
      deviceTypeName: json['device_type_name'],
      location: json['location'],
      ipAddress: json['ip_address'],
      mqttTopic: json['mqtt_topic'],
      status: json['status'],
      currentValue: json['current_value'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

class SensorData {
  final int id;
  final int deviceId;
  final String? deviceName;
  final double? temperature; // 温度（℃）
  final double? ph; // PH值
  final double? ammonia; // 氨氮（mg/L）
  final double? nitrite; // 亚盐（mg/L）
  final double? oxygen; // 溶氧（mg/L）
  final String? rawValue; // 原始数据
  final DateTime createdAt;

  SensorData({
    required this.id,
    required this.deviceId,
    this.deviceName,
    this.temperature,
    this.ph,
    this.ammonia,
    this.nitrite,
    this.oxygen,
    this.rawValue,
    required this.createdAt,
  });

  factory SensorData.fromJson(Map<String, dynamic> json) {
    return SensorData(
      id: json['id'],
      deviceId: json['device_id'],
      deviceName: json['device_name'],
      temperature: json['temperature'],
      ph: json['ph'],
      ammonia: json['ammonia'],
      nitrite: json['nitrite'],
      oxygen: json['oxygen'],
      rawValue: json['raw_value'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

/// 控制设备模型
class ControlDevice {
  final int id;
  final String deviceName;
  final String deviceType;
  final String? location;
  final int status; // 0: 关闭, 1: 开启
  final String? mqttTopic;
  final double? currentPower;
  final DateTime createdAt;
  final DateTime updatedAt;

  ControlDevice({
    required this.id,
    required this.deviceName,
    required this.deviceType,
    this.location,
    required this.status,
    this.mqttTopic,
    this.currentPower,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ControlDevice.fromJson(Map<String, dynamic> json) {
    return ControlDevice(
      id: json['id'] ?? 0,
      deviceName: json['device_name'] ?? '',
      deviceType: json['device_type'] ?? '',
      location: json['location'],
      status: json['status'] ?? 0,
      mqttTopic: json['mqtt_topic'],
      currentPower: json['current_power'] != null
          ? (json['current_power'] is int
              ? json['current_power'].toDouble()
              : json['current_power'])
          : null,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : DateTime.now(),
    );
  }

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

