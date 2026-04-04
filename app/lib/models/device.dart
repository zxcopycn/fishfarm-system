class DeviceType {
  final int id;
  final String typeName;

  DeviceType({
    required this.id,
    required this.typeName,
  });

  factory DeviceType.fromJson(Map<String, dynamic> json) {
    return DeviceType(
      id: json['id'] is int ? json['id'] : (json['id'] is String ? int.tryParse(json['id'].toString()) ?? 0 : 0),
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
      id: json['id'] is int ? json['id'] : (json['id'] is String ? int.tryParse(json['id'].toString()) ?? 0 : 0),
      deviceName: json['device_name']?.toString() ?? '',
      deviceTypeId: json['device_type_id'] is int ? json['device_type_id'] : (json['device_type_id'] is String ? int.tryParse(json['device_type_id'].toString()) ?? 0 : 0),
      deviceTypeName: json['device_type_name']?.toString(),
      location: json['location']?.toString() ?? '',
      ipAddress: json['ip_address']?.toString(),
      mqttTopic: json['mqtt_topic']?.toString(),
      status: json['status'] is int ? json['status'] : (json['status'] is String ? int.tryParse(json['status'].toString()) ?? 0 : 0),
      currentValue: json['current_value'] is num ? (json['current_value'] is int ? json['current_value'].toDouble() : json['current_value']) : null,
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at'].toString()) : DateTime.now(),
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
      id: json['id'] is int ? json['id'] : (json['id'] is String ? int.tryParse(json['id'].toString()) ?? 0 : 0),
      deviceName: json['device_name']?.toString() ?? '',
      deviceType: json['device_type']?.toString() ?? '',
      location: json['location']?.toString() ?? '',
      status: json['status'] is int ? json['status'] : (json['status'] is String ? int.tryParse(json['status'].toString()) ?? 0 : 0),
      mqttTopic: json['mqtt_topic']?.toString(),
      currentPower: json['current_power'] != null
          ? (json['current_power'] is num
              ? (json['current_power'] is int ? json['current_power'].toDouble() : json['current_power'])
              : null)
          : null,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'].toString())
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'].toString())
          : DateTime.now(),
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
