import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:fishfarm_monitor/models/device.dart';
import 'package:fishfarm_monitor/models/sensor_data.dart';
import 'package:fishfarm_monitor/models/alarm.dart';

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();

  late final WebSocketChannel _channel;
  StreamSubscription? _subscription;
  String? _clientId;
  
  // WebSocket连接状态
  ValueNotifier<bool> connectionStatus = ValueNotifier(false);
  
  // 数据监听器
  final Map<String, List<Function>> _listeners = {
    'sensor_update': [],
    'device_status_update': [],
    'alarm_alert': [],
    'production_update': [],
  };

  bool get isConnected => connectionStatus.value;

  // 初始化WebSocket连接
  Future<void> initConnection() async {
    try {
      // 获取或生成客户端ID
      _clientId = await _getClientId();
      
      // 连接WebSocket
      _channel = WebSocketChannel.connect(
        Uri.parse('ws://192.168.1.200:8000/ws'),
      );

      // 连接状态监听
      connectionStatus.value = true;

      // 开始监听消息
      _subscription = _channel.stream.listen(
        _handleMessage,
        onError: (error) {
          print('WebSocket错误: $error');
          _reconnect();
        ),
        onDone: () {
          print('WebSocket连接已关闭');
          connectionStatus.value = false;
          _reconnect();
        },
      );

      // 发送连接确认和客户端ID
      _channel.sink.add({
        'type': 'connect',
        'client_id': _clientId,
        'timestamp': DateTime.now().toIso8601String(),
      });

      print('WebSocket已连接，客户端ID: $_clientId');
      
    } catch (e) {
      print('WebSocket连接失败: $e');
      connectionStatus.value = false;
      _reconnect();
    }
  }

  // 处理WebSocket消息
  void _handleMessage(dynamic message) {
    try {
      final data = json.decode(message);
      final type = data['type'];
      
      print('收到WebSocket消息: $type');

      switch (type) {
        case 'sensor_update':
          _notifyListeners('sensor_update', data);
          break;
        case 'device_status_update':
          _notifyListeners('device_status_update', data);
          break;
        case 'alarm_alert':
          _notifyListeners('alarm_alert', data);
          break;
        case 'production_update':
          _notifyListeners('production_update', data);
          break;
        default:
          print('未知消息类型: $type');
      }
    } catch (e) {
      print('处理WebSocket消息失败: $e');
    }
  }

  // 通知监听器
  void _notifyListeners(String type, Map<String, dynamic> data) {
    final listeners = _listeners[type] ?? [];
    for (final listener in listeners) {
      try {
        listener(data);
      } catch (e) {
        print('通知监听器失败: $e');
      }
    }
  }

  // 添加监听器
  void addListener(String type, Function listener) {
    if (!_listeners.containsKey(type)) {
      _listeners[type] = [];
    }
    _listeners[type]!.add(listener);
  }

  // 移除监听器
  void removeListener(String type, Function listener) {
    _listeners[type]?.remove(listener);
  }

  // 订阅传感器更新
  void subscribeToSensorUpdates(int device_id) {
    if (_channel != null) {
      _channel.sink.add({
        'type': 'subscribe',
        'device_id': device_id,
        'client_id': _clientId,
        'timestamp': DateTime.now().toIso8601String(),
      });
    }
  }

  // 订阅设备状态更新
  void subscribeToDeviceStatusUpdates(int device_id) {
    if (_channel != null) {
      _channel.sink.add({
        'type': 'subscribe_status',
        'device_id': device_id,
        'client_id': _clientId,
        'timestamp': DateTime.now().toIso8601String(),
      });
    }
  }

  // 取消订阅
  void unsubscribe() {
    if (_channel != null) {
      _channel.sink.add({
        'type': 'unsubscribe',
        'client_id': _clientId,
        'timestamp': DateTime.now().toIso8601String(),
      });
    }
  }

  // 重连
  void _reconnect() {
    // 如果还有监听器，尝试重新连接
    if (connectionStatus.value) {
      Future.delayed(const Duration(seconds: 5), () {
        if (!connectionStatus.value) {
          initConnection();
        }
      });
    }
  }

  // 断开连接
  void disconnect() {
    _subscription?.cancel();
    _channel.sink.close();
    connectionStatus.value = false;
    print('WebSocket已断开');
  }

  // 获取或生成客户端ID
  Future<String> _getClientId() async {
    final prefs = await SharedPreferences.getInstance();
    String? clientId = prefs.getString('websocket_client_id');
    
    if (clientId == null) {
      clientId = 'client_${DateTime.now().millisecondsSinceEpoch}_${DateTime.now().microsecond}';
      await prefs.setString('websocket_client_id', clientId);
    }
    
    return clientId;
  }

  // 手动触发更新
  void triggerUpdate(String type, Map<String, dynamic> data) {
    _notifyListeners(type, data);
  }

  // 清理资源
  void dispose() {
    disconnect();
    _listeners.clear();
  }
}

// 全局WebSocket服务实例
final WebSocketService wsService = WebSocketService();