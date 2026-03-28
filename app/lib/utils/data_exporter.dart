import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:intl/intl.dart';
import 'package:fishfarm_monitor/models/alarm.dart';
import 'package:fishfarm_monitor/models/production.dart';
import 'package:fishfarm_monitor/models/device.dart';
import 'package:fishfarm_monitor/models/sensor_data.dart';

class DataExporter {
  /// 导出预警记录为CSV
  static Future<void> exportAlarmsToCsv(List<AlarmRecord> alarms) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
      final fileName = '预警记录_$timestamp.csv';
      final filePath = '${directory.path}/$fileName';

      // CSV 表头
      final headers = [
        '预警ID',
        '预警级别',
        '阈值类型',
        '阈值设置',
        '实际值',
        '偏离率',
        '描述',
        '设备名称',
        '设备编号',
        '状态',
        '创建时间',
        '解决时间'
      ];

      // CSV 内容
      final buffer = StringBuffer();
      buffer.writeln(headers.join(','));

      for (final alarm in alarms) {
        final row = [
          alarm.id,
          alarm.level.level,
          '', // thresholdType 已废弃
          alarm.thresholdValue?.toString() ?? '0',
          alarm.actualValue?.toString() ?? '0',
          _calculateDeviation(alarm).toString(),
          alarm.message,
          _getDeviceName(alarm.deviceId),
          alarm.deviceId?.toString() ?? '',
          alarm.isResolved == 1 ? '已解决' : '未解决',
          _formatDateTimeString(alarm.createdAt),
          alarm.isResolved == 1 ? _formatDateTimeString(alarm.createdAt) : ''
        ];
        buffer.writeln(row.join(','));
      }

      // 写入文件
      final file = File(filePath);
      await file.writeAsString(buffer.toString());

      // 分享文件
      await Share.shareXFiles(
        [XFile(filePath)],
        subject: '预警记录导出',
        text: '这是渔场预警记录的导出文件',
      );

      print('导出成功: $filePath');
    } catch (e) {
      print('导出失败: $e');
      rethrow;
    }
  }

  /// 导出生产记录为CSV
  static Future<void> exportProductionToCsv(List<ProductionRecord> records) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
      final fileName = '生产记录_$timestamp.csv';
      final filePath = '${directory.path}/$fileName';

      // CSV 表头
      final headers = [
        '记录ID',
        '鱼类品种',
        '数量',
        '平均体重',
        '平均体长',
        '投喂量',
        '投喂日期',
        '孵化日期',
        '生长阶段',
        '备注',
        '创建时间'
      ];

      // CSV 内容
      final buffer = StringBuffer();
      buffer.writeln(headers.join(','));

      for (final record in records) {
        final row = [
          record.id,
          record.fishType,
          record.quantity.toString(),
          record.weight?.toString() ?? '0',
          record.length?.toString() ?? '0',
          record.feedAmount?.toString() ?? '0',
          record.spawnDate != null ? _formatDateTimeString(record.spawnDate!) : '',
          record.hatchDate != null ? _formatDateTimeString(record.hatchDate!) : '',
          record.growthStage ?? '',
          record.remark ?? '',
          _formatDateTimeString(record.createdAt.toIso8601String())
        ];
        buffer.writeln(row.join(','));
      }

      // 写入文件
      final file = File(filePath);
      await file.writeAsString(buffer.toString());

      // 分享文件
      await Share.shareXFiles(
        [XFile(filePath)],
        subject: '生产记录导出',
        text: '这是渔场生产记录的导出文件',
      );

      print('导出成功: $filePath');
    } catch (e) {
      print('导出失败: $e');
      rethrow;
    }
  }

  /// 导出传感器数据为CSV
  static Future<void> exportSensorData(
    List<Device> devices,
    List<SensorData> sensorData,
  ) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
      final fileName = '传感器数据_$timestamp.csv';
      final filePath = '${directory.path}/$fileName';

      // CSV 表头
      final headers = [
        '时间',
        '设备ID',
        '设备名称',
        '传感器类型',
        '数值',
        '单位'
      ];

      // CSV 内容
      final buffer = StringBuffer();
      buffer.writeln(headers.join(','));

      for (final data in sensorData) {
        final device = devices.firstWhere(
          (d) => d.id == data.deviceId,
          orElse: () => Device(id: 0, deviceName: '未知设备', deviceTypeId: 0, location: '未知', status: 0, createdAt: DateTime.now()),
        );
        final row = [
          _formatDateTimeString(data.timestamp),
          data.deviceId.toString(),
          device.deviceName,
          '传感器',
          data.temperature?.toString() ?? data.ph?.toString() ?? '0',
          '℃'
        ];
        buffer.writeln(row.join(','));
      }

      // 写入文件
      final file = File(filePath);
      await file.writeAsString(buffer.toString());

      // 分享文件
      await Share.shareXFiles(
        [XFile(filePath)],
        subject: '传感器数据导出',
        text: '这是渔场传感器数据的导出文件',
      );

      print('导出成功: $filePath');
    } catch (e) {
      print('导出失败: $e');
      rethrow;
    }
  }

  /// 导出所有设备信息为CSV
  static Future<void> exportDevicesToCsv(List<Device> devices) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());
      final fileName = '设备信息_$timestamp.csv';
      final filePath = '${directory.path}/$fileName';

      // CSV 表头
      final headers = [
        '设备ID',
        '设备名称',
        '设备编号',
        '设备类型',
        '安装位置',
        '设备状态',
        '创建时间'
      ];

      // CSV 内容
      final buffer = StringBuffer();
      buffer.writeln(headers.join(','));

      for (final device in devices) {
        final row = [
          device.id.toString(),
          device.deviceName,
          device.deviceName, // deviceNumber 已废弃，使用 deviceName
          device.deviceTypeName ?? '', // deviceType 已废弃，使用 deviceTypeName
          device.location,
          device.status,
          _formatDateTimeString(device.createdAt.toIso8601String())
        ];
        buffer.writeln(row.join(','));
      }

      // 写入文件
      final file = File(filePath);
      await file.writeAsString(buffer.toString());

      // 分享文件
      await Share.shareXFiles(
        [XFile(filePath)],
        subject: '设备信息导出',
        text: '这是渔场设备信息的导出文件',
      );

      print('导出成功: $filePath');
    } catch (e) {
      print('导出失败: $e');
      rethrow;
    }
  }

  // ==================== 私有辅助方法 ====================

  static String _formatDateTimeFrom(DateTime dateTime) {
    return DateFormat('yyyy-MM-dd HH:mm:ss').format(dateTime);
  }

  static String _formatDateTimeString(dynamic dateTime) {
    try {
      DateTime dt;
      if (dateTime is DateTime) {
        dt = dateTime;
      } else if (dateTime is String) {
        dt = DateTime.parse(dateTime);
      } else {
        return dateTime?.toString() ?? '';
      }
      return DateFormat('yyyy-MM-dd HH:mm:ss').format(dt);
    } catch (e) {
      return dateTime?.toString() ?? '';
    }
  }

  static String _getDeviceName(int? deviceId) {
    // 这里需要传入设备列表，简化处理返回ID
    return deviceId?.toString() ?? '未知设备';
  }

  static String _calculateDeviation(AlarmRecord alarm) {
    final threshold = alarm.thresholdValue ?? 0;
    final actual = alarm.actualValue ?? 0;
    if (threshold == 0 || actual == 0) return '0';
    final deviation = ((actual - threshold) / threshold * 100);
    return deviation.toStringAsFixed(2);
  }
}
