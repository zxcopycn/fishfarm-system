import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:fishfarm_monitor/models/device.dart';
import 'package:fishfarm_monitor/services/api_service.dart';
import 'package:fishfarm_monitor/services/websocket_service.dart';

class ControlPage extends StatefulWidget {
  const ControlPage({super.key});

  @override
  State<ControlPage> createState() => _ControlPageState();
}

class _ControlPageState extends State<ControlPage> {
  bool _isLoading = true;
  List<ControlDevice> _devices = [];
  Map<int, bool> _deviceStatus = {};
  bool _wsConnected = false;

  @override
  void initState() {
    super.initState();
    _loadDevices();
    _setupWebSocket();
  }

  @override
  void dispose() {
    wsService.removeListener('device_status_update', _onDeviceStatusUpdate);
    wsService.removeListener('alarm_alert', _onAlarmAlert);
    super.dispose();
  }

  void _setupWebSocket() {
    // 监听WebSocket连接状态
    wsService.connectionStatus.addListener(() {
      setState(() {
        _wsConnected = wsService.isConnected;
      });
    });

    // 初始化WebSocket连接
    wsService.initConnection();

    // 添加监听器
    wsService.addListener('device_status_update', _onDeviceStatusUpdate);
    wsService.addListener('alarm_alert', _onAlarmAlert);
  }

  void _onDeviceStatusUpdate(Map<String, dynamic> data) {
    // 更新设备状态
    final deviceId = data['data']['device_id'] as int?;
    final status = data['data']['status'] as int?;
    if (deviceId != null && status != null) {
      setState(() {
        _deviceStatus[deviceId] = status == 1;
      });
      
      // 显示状态更新通知
      final device = _devices.firstWhere(
        (d) => d.id == deviceId,
        orElse: () => _devices.first,
      );
      _showStatusNotification(device, status == 1);
    }
  }

  void _onAlarmAlert(Map<String, dynamic> data) {
    // 显示预警通知
    setState(() {
      final message = data['data']['message'] ?? '设备预警';
      _showAlarmNotification(message);
    });
  }

  void _showStatusNotification(ControlDevice device, bool isOn) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(isOn ? Icons.power_settings_new : Icons.power_off, color: Colors.white),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '${device.deviceName}已${isOn ? '开启' : '关闭'}',
                  style: const TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
          backgroundColor: Colors.green,
          duration: const Duration(seconds: 2),
          behavior: SnackBarBehavior.floating,
          margin: const EdgeInsets.all(16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      );
    }
  }

  void _showAlarmNotification(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.warning, color: Colors.orange),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '⚠️ 预警: $message',
                  style: const TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
          backgroundColor: Colors.orange,
          duration: const Duration(seconds: 3),
          behavior: SnackBarBehavior.floating,
          margin: const EdgeInsets.all(16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      );
    }
  }

  Future<void> _loadDevices() async {
    try {
      final devices = await ApiService().getControlDevices();
      setState(() {
        _devices = devices;
        _isLoading = false;
        // 初始化设备状态
        for (var device in devices) {
          _deviceStatus[device.id] = device.isOn;
        }
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载设备失败: $e')),
        );
      }
    }
  }

  Future<void> _toggleDevice(ControlDevice device) async {
    final action = _deviceStatus[device.id] == true ? 'off' : 'on';

    try {
      await ApiService().controlDevice(
        deviceId: device.id,
        action: action,
        remark: '用户控制',
      );

      setState(() {
        _deviceStatus[device.id] = !_deviceStatus[device.id]!;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                Icon(action == 'on' ? Icons.power_settings_new : Icons.power_off, color: Colors.white),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${device.deviceName}已${action == 'on' ? '开启' : '关闭'}',
                    style: const TextStyle(color: Colors.white),
                  ),
                ),
              ],
            ),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
            margin: const EdgeInsets.all(16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        );
      }

    } catch (e) {
      setState(() {
        _deviceStatus[device.id] = !_deviceStatus[device.id]!;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('控制失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设备控制'),
        backgroundColor: Colors.blue[700],
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDevices,
          ),
          IconButton(
            icon: Icon(
              Icons.wifi,
              color: _wsConnected ? Colors.green : Colors.red,
            ),
            tooltip: 'WebSocket连接状态',
            onPressed: _wsConnected ? null : () {
              wsService.initConnection();
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                _buildConnectionStatus(),
                Expanded(
                  child: RefreshIndicator(
                    onRefresh: _loadDevices,
                    child: _buildDeviceList(),
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildConnectionStatus() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Icon(
            _wsConnected ? Icons.wifi : Icons.wifi_off,
            color: _wsConnected ? Colors.green : Colors.red,
          ),
          const SizedBox(width: 8),
          Text(
            _wsConnected ? '实时连接已建立' : '连接断开',
            style: TextStyle(
              color: _wsConnected ? Colors.green : Colors.red,
              fontWeight: FontWeight.bold,
            ),
          ),
          if (!_wsConnected) ...[
            const SizedBox(width: 8),
            const Text(
              '🔄 点击WiFi图标重新连接',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildDeviceList() {
    if (_devices.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.device_unknown, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            const Text(
              '暂无可控制设备',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _devices.length,
      itemBuilder: (context, index) {
        final device = _devices[index];
        final isOn = _deviceStatus[device.id] ?? false;

        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          elevation: 4,
          child: ListTile(
            leading: Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: isOn ? Colors.green.shade100 : Colors.grey.shade100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.power_settings_new,
                size: 32,
                color: isOn ? Colors.green : Colors.grey,
              ),
            ),
            title: Text(
              device.deviceName,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  device.deviceName,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '状态: ${isOn ? '运行中' : '已停止'}',
                  style: TextStyle(
                    color: isOn ? Colors.green : Colors.red,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
            trailing: Switch(
              value: isOn,
               (value) => _toggleDevice(device),
              activeColor: Colors.green,
            ),
            onTap: () => _toggleDevice(device),
          ),
        );
      },
    );
  }
}