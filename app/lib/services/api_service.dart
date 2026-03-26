import 'dart:convert';
import 'dart:async';
import 'package:dio/dio.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/device.dart';
import '../models/sensor_data.dart';
import '../models/alarm.dart';
import '../models/production.dart';
import '../models/reminder.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal() {
    _initDio();
  }

  late final Dio _dio;

  // API基础URL
  String _baseUrl = 'http://192.168.1.200:8000'; // 可配置

  // WebSocket
  WebSocketChannel? _wsChannel;
  StreamSubscription? _wsSubscription;
  Map<String, List<Function>> _wsListeners = {};

  void _initDio() {
    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    // 添加拦截器
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        print('请求: ${options.method} ${options.uri}');
        handler.next(options);
      },
      onResponse: (response, handler) {
        print('响应: ${response.statusCode}');
        handler.next(response);
      },
      onError: (error, handler) {
        print('错误: ${error.message}');
        handler.next(error);
      },
    ));
  }

  // 设置API基础URL
  void setBaseUrl(String url) {
    _baseUrl = url;
    _initDio(); // 重新初始化
  }

  // 连接WebSocket
  Future<void> connectWebSocket({String? clientId}) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final wsUrl = _baseUrl.replaceFirst('http://', 'ws://').replaceFirst('https://', 'wss://');
      final url = '$wsUrl/ws?client_id=${clientId ?? prefs.getString('client_id') ?? DateTime.now().millisecondsSinceEpoch.toString()}';

      _wsChannel = WebSocketChannel.connect(Uri.parse(url));

      _wsChannel!.stream.listen(
        (message) {
          try {
            final data = jsonDecode(message);
            _onMessageReceived(data);
          } catch (e) {
            print('解析WebSocket消息失败: $e');
          }
        },
        onError: (error) {
          print('WebSocket错误: $error');
        },
        onDone: () {
          print('WebSocket已关闭');
        },
      );

      print('WebSocket连接成功');
    } catch (e) {
      print('连接WebSocket失败: $e');
      rethrow;
    }
  }

  // 断开WebSocket
  void disconnectWebSocket() {
    _wsSubscription?.cancel();
    _wsChannel?.sink.close();
    _wsChannel = null;
    _wsListeners.clear();
    print('WebSocket已断开');
  }

  // 订阅传感器更新
  void subscribeToSensor(int deviceId) {
    _sendMessage({'type': 'subscribe', 'device_id': deviceId});
  }

  // 订阅设备状态更新
  void subscribeToDeviceStatus(int deviceId) {
    _sendMessage({'type': 'subscribe_status', 'device_id': deviceId});
  }

  // 取消订阅
  void unsubscribe() {
    _sendMessage({'type': 'unsubscribe'});
  }

  // 发送WebSocket消息
  void _sendMessage(Map<String, dynamic> message) {
    _wsChannel?.sink.add(jsonEncode(message));
  }

  // 添加消息监听器
  void addMessageListener(String type, Function callback) {
    if (!_wsListeners.containsKey(type)) {
      _wsListeners[type] = [];
    }
    _wsListeners[type]!.add(callback);
  }

  // 处理接收到的消息
  void _onMessageReceived(Map<String, dynamic> message) {
    final type = message['type'];
    final data = message['data'];

    if (_wsListeners.containsKey(type)) {
      for (var callback in _wsListeners[type]!) {
        try {
          callback(data);
        } catch (e) {
          print('消息处理错误: $e');
        }
      }
    }
  }

  // 获取设备列表
  Future<List<Device>> getDevices() async {
    try {
      final response = await _dio.get('/api/devices/list');
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((e) => Device.fromJson(e)).toList();
      }
      throw Exception('获取设备列表失败');
    } catch (e) {
      throw Exception('获取设备列表失败: $e');
    }
  }

  // 获取传感器最新数据
  Future<List<SensorData>> getSensorData({int limit = 20}) async {
    try {
      final response = await _dio.get(
        '/api/sensor/latest',
        queryParameters: {'limit': limit}
      );
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((e) => SensorData.fromJson(e)).toList();
      }
      throw Exception('获取传感器数据失败');
    } catch (e) {
      throw Exception('获取传感器数据失败: $e');
    }
  }

  // 获取历史传感器数据
  Future<List<SensorData>> getHistoricalSensorData({
    required int deviceId,
    DateTime? startTime,
    DateTime? endTime,
    int limit = 100,
  }) async {
    try {
      final queryParams = <String, dynamic>{'limit': limit};
      if (startTime != null) {
        queryParams['start_time'] = startTime.toIso8601String();
      }
      if (endTime != null) {
        queryParams['end_time'] = endTime.toIso8601String();
      }

      final response = await _dio.get(
        '/api/sensor/historical',
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((e) => SensorData.fromJson(e)).toList();
      }
      throw Exception('获取历史数据失败');
    } catch (e) {
      throw Exception('获取历史数据失败: $e');
    }
  }

  // 获取控制设备列表
  Future<List<ControlDevice>> getControlDevices() async {
    try {
      final response = await _dio.get('/api/control/devices');
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((e) => ControlDevice.fromJson(e)).toList();
      }
      throw Exception('获取控制设备失败');
    } catch (e) {
      throw Exception('获取控制设备失败: $e');
    }
  }

  // 获取预警规则
  Future<List<AlarmRule>> getAlarmRules() async {
    try {
      final response = await _dio.get('/api/alarms/rules');
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((e) => AlarmRule.fromJson(e)).toList();
      }
      throw Exception('获取预警规则失败');
    } catch (e) {
      throw Exception('获取预警规则失败: $e');
    }
  }

  // 获取预警记录
  Future<List<AlarmRecord>> getAlarmRecords({
    String? level,
    bool? isResolved,
    int days = 7,
  }) async {
    try {
      final queryParams = <String, dynamic>{'days': days};
      if (level != null) queryParams['level'] = level;
      if (isResolved != null) queryParams['is_resolved'] = isResolved;

      final response = await _dio.get(
        '/api/alarms/records',
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((e) => AlarmRecord.fromJson(e)).toList();
      }
      throw Exception('获取预警记录失败');
    } catch (e) {
      throw Exception('获取预警记录失败: $e');
    }
  }

  // 获取生产记录
  Future<List<ProductionRecord>> getProductionRecords({
    String? fishType,
    int limit = 50,
  }) async {
    try {
      final queryParams = <String, dynamic>{'limit': limit};
      if (fishType != null) queryParams['fish_type'] = fishType;

      final response = await _dio.get(
        '/api/production/list',
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((e) => ProductionRecord.fromJson(e)).toList();
      }
      throw Exception('获取生产记录失败');
    } catch (e) {
      throw Exception('获取生产记录失败: $e');
    }
  }

  // 控制设备
  Future<Map<String, dynamic>> controlDevice({
    required int deviceId,
    required String action,
    double? targetValue,
    String? remark,
  }) async {
    try {
      final response = await _dio.post(
        '/api/control/$deviceId/control',
        data: {
          'action': action,
          'target_value': targetValue,
          'remark': remark,
        }
      );

      if (response.statusCode == 200) {
        return response.data;
      }
      throw Exception('控制设备失败');
    } catch (e) {
      throw Exception('控制设备失败: $e');
    }
  }

  // 解决预警
  Future<bool> resolveAlarm(int recordId) async {
    try {
      final response = await _dio.post(
        '/api/alarms/records/$recordId/resolve'
      );

      if (response.statusCode == 200) {
        return response.data['status'] == 'success';
      }
      throw Exception('解决预警失败');
    } catch (e) {
      throw Exception('解决预警失败: $e');
    }
  }

  // 创建生产记录
  Future<ProductionRecord> createProductionRecord({
    required String fishType,
    required double quantity,
    DateTime? spawnDate,
    DateTime? hatchDate,
    String? growthStage,
    double? weight,
    double? length,
    double? feedAmount,
    String? remark,
  }) async {
    try {
      final data = {
        'fish_type': fishType,
        'quantity': quantity,
      };

      if (spawnDate != null) data['spawn_date'] = spawnDate.toIso8601String();
      if (hatchDate != null) data['hatch_date'] = hatchDate.toIso8601String();
      if (growthStage != null) data['growth_stage'] = growthStage;
      if (weight != null) data['weight'] = weight;
      if (length != null) data['length'] = length;
      if (feedAmount != null) data['feed_amount'] = feedAmount;
      if (remark != null) data['remark'] = remark;

      final response = await _dio.post(
        '/api/production/create',
        data: data,
      );

      if (response.statusCode == 200) {
        return ProductionRecord.fromJson(response.data);
      }
      throw Exception('创建生产记录失败');
    } catch (e) {
      throw Exception('创建生产记录失败: $e');
    }
  }

  // 更新生产记录
  Future<ProductionRecord> updateProductionRecord({
    required int id,
    String? fishType,
    double? quantity,
    DateTime? spawnDate,
    DateTime? hatchDate,
    String? growthStage,
    double? weight,
    double? length,
    double? feedAmount,
    String? remark,
  }) async {
    try {
      final data = {};

      if (fishType != null) data['fish_type'] = fishType;
      if (quantity != null) data['quantity'] = quantity;
      if (spawnDate != null) data['spawn_date'] = spawnDate.toIso8601String();
      if (hatchDate != null) data['hatch_date'] = hatchDate.toIso8601String();
      if (growthStage != null) data['growth_stage'] = growthStage;
      if (weight != null) data['weight'] = weight;
      if (length != null) data['length'] = length;
      if (feedAmount != null) data['feed_amount'] = feedAmount;
      if (remark != null) data['remark'] = remark;

      final response = await _dio.put(
        '/api/production/$id/update',
        data: data,
      );

      if (response.statusCode == 200) {
        return ProductionRecord.fromJson(response.data);
      }
      throw Exception('更新生产记录失败');
    } catch (e) {
      throw Exception('更新生产记录失败: $e');
    }
  }

  // 删除生产记录
  Future<bool> deleteProductionRecord(int id) async {
    try {
      final response = await _dio.delete(
        '/api/production/$id/delete',
      );

      if (response.statusCode == 200) {
        return response.data['status'] == 'success';
      }
      throw Exception('删除生产记录失败');
    } catch (e) {
      throw Exception('删除生产记录失败: $e');
    }
  }

  // 健康检查
  Future<bool> healthCheck() async {
    try {
      final response = await _dio.get('/health');
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // ==================== Reminder API ====================

  // 获取提醒列表
  Future<List<Reminder>> getReminders({int isCompleted = 0}) async {
    try {
      final response = await _dio.get(
        '/api/reminders',
        queryParameters: {'is_completed': isCompleted}
      );
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((e) => Reminder.fromJson(e)).toList();
      }
      throw Exception('获取提醒列表失败');
    } catch (e) {
      throw Exception('获取提醒列表失败: $e');
    }
  }

  // 创建提醒
  Future<Reminder> createReminder({
    required String title,
    String? content,
    String? reminderTime,
  }) async {
    try {
      final response = await _dio.post(
        '/api/reminders',
        data: {
          'title': title,
          'content': content,
          'reminder_time': reminderTime,
        }
      );

      if (response.statusCode == 200) {
        return Reminder.fromJson(response.data);
      }
      throw Exception('创建提醒失败');
    } catch (e) {
      throw Exception('创建提醒失败: $e');
    }
  }

  // 更新提醒
  Future<Reminder> updateReminder({
    required int id,
    String? title,
    String? content,
    String? reminderTime,
    int? isCompleted,
  }) async {
    try {
      final data = {};

      if (title != null) data['title'] = title;
      if (content != null) data['content'] = content;
      if (reminderTime != null) data['reminder_time'] = reminderTime;
      if (isCompleted != null) data['is_completed'] = isCompleted;

      final response = await _dio.put(
        '/api/reminders/$id',
        data: data,
      );

      if (response.statusCode == 200) {
        return Reminder.fromJson(response.data);
      }
      throw Exception('更新提醒失败');
    } catch (e) {
      throw Exception('更新提醒失败: $e');
    }
  }

  // 删除提醒
  Future<bool> deleteReminder(int id) async {
    try {
      final response = await _dio.delete(
        '/api/reminders/$id',
      );

      if (response.statusCode == 200) {
        return response.data['status'] == 'success';
      }
      throw Exception('删除提醒失败');
    } catch (e) {
      throw Exception('删除提醒失败: $e');
    }
  }

  // 标记为已完成
  Future<bool> markReminderCompleted(int id) async {
    try {
      final response = await _dio.patch(
        '/api/reminders/$id/complete',
      );

      if (response.statusCode == 200) {
        return response.data['status'] == 'success';
      }
      throw Exception('标记提醒失败');
    } catch (e) {
      throw Exception('标记提醒失败: $e');
    }
  }

  // 获取提醒统计
  Future<Map<String, dynamic>> getReminderSummary() async {
    try {
      final response = await _dio.get('/api/reminders/summary');
      if (response.statusCode == 200) {
        return response.data;
      }
      throw Exception('获取提醒统计失败');
    } catch (e) {
      throw Exception('获取提醒统计失败: $e');
    }
  }
}
