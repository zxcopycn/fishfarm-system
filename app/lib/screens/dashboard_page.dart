import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:fishfarm_monitor/models/device.dart';
import 'package:fishfarm_monitor/models/sensor_data.dart';
import 'package:fishfarm_monitor/services/api_service.dart';
import 'package:fishfarm_monitor/services/websocket_service.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  bool _isLoading = true;
  List<Device> _devices = [];
  List<SensorData> _sensorData = [];
  bool _wsConnected = false;

  @override
  void initState() {
    super.initState();
    _loadData();
    _setupWebSocket();
  }

  @override
  void dispose() {
    wsService.removeListener('sensor_update', _onSensorUpdate);
    wsService.removeListener('device_status_update', _onDeviceStatusUpdate);
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
    wsService.addListener('sensor_update', _onSensorUpdate);
    wsService.addListener('device_status_update', _onDeviceStatusUpdate);

    // 订阅所有设备的传感器和状态更新
    Future.delayed(const Duration(seconds: 1), () {
      for (final device in _devices) {
        wsService.subscribeToSensorUpdates(device.id);
        wsService.subscribeToDeviceStatusUpdates(device.id);
      }
    });
  }

  void _onSensorUpdate(Map<String, dynamic> data) {
    // 更新传感器数据
    setState(() {
      _sensorData.removeWhere((s) => s.deviceId == data['device_id']);
      _sensorData.add(SensorData.fromJson(data['data']));
      
      // 如果数据太多，只保留最新的10条
      if (_sensorData.length > 10) {
        _sensorData = _sensorData.take(10).toList();
      }
    });
  }

  void _onDeviceStatusUpdate(Map<String, dynamic> data) {
    // 更新设备状态
    final deviceId = data['data']['device_id'] as int?;
    final status = data['data']['status'] as int?;
    if (deviceId != null && status != null) {
      final index = _devices.indexWhere((d) => d.id == deviceId);
      if (index != -1) {
        setState(() {
          // 由于 Device 的 status 属性是 final，需要重新创建对象
          _devices[index] = Device(
            id: _devices[index].id,
            deviceName: _devices[index].deviceName,
            deviceTypeId: _devices[index].deviceTypeId,
            deviceTypeName: _devices[index].deviceTypeName,
            location: _devices[index].location,
            ipAddress: _devices[index].ipAddress,
            mqttTopic: _devices[index].mqttTopic,
            status: status,
            currentValue: _devices[index].currentValue,
            createdAt: _devices[index].createdAt,
          );
        });
      }
    }
  }

  Future<void> _loadData() async {
    try {
      // 并行获取数据
      final results = await Future.wait([
        ApiService().getDevices(),
        ApiService().getSensorData(limit: 10),
      ]);

      setState(() {
        _devices = results[0] as List<Device>;
        _sensorData = results[1] as List<SensorData>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载数据失败: $e')),
        );
      }
    }
  }

  @override
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('仪表盘'),
        backgroundColor: Colors.blue[700],
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
          IconButton(
            icon: Icon(
              Icons.wifi,
              color: _wsConnected ? Colors.green : Colors.red,
            ),
            tooltip: 'WebSocket连接状态',
            onPressed: null,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildDashboard(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _refreshData,
        icon: const Icon(Icons.refresh),
        label: const Text('刷新'),
      ),
    );
  }

  Widget _buildDashboard() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 设备状态卡片
          _buildStatusCard(),
          const SizedBox(height: 16),

          // 传感器数据列表
          const Text(
            '传感器数据',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          _buildSensorList(),
        ],
      ),
    );
  }

  Widget _buildStatusCard() {
    final onlineCount = _devices.where((d) => d.status == 1).length;
    final offlineCount = _devices.length - onlineCount;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.info, color: Colors.blue),
                const SizedBox(width: 8),
                const Text(
                  '设备状态',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatusItem(
                  '总设备',
                  _devices.length.toString(),
                  Icons.devices,
                ),
                _buildStatusItem(
                  '在线',
                  onlineCount.toString(),
                  Icons.cloud_done,
                  Colors.green,
                ),
                _buildStatusItem(
                  '离线',
                  offlineCount.toString(),
                  Icons.cloud_off,
                  Colors.red,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusItem(String label, String value, IconData icon,
      [Color? color]) {
    return Column(
      children: [
        Icon(icon, size: 32, color: color ?? Colors.blue),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(fontSize: 14, color: Colors.grey),
        ),
      ],
    );
  }

  Widget _buildSensorList() {
    if (_sensorData.isEmpty) {
      return Card(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Padding(
          padding: EdgeInsets.all(32),
          child: Center(
            child: Text('暂无传感器数据'),
          ),
        ),
      );
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: _sensorData.length,
        separatorBuilder: (context, index) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final data = _sensorData[index];
          return ListTile(
            leading: const Icon(Icons.sensors, color: Colors.blue),
            title: Text(data.deviceName ?? '未知设备'),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (data.temperature != null)
                  _buildSensorRow('温度', '${data.temperature!.toStringAsFixed(1)}℃'),
                if (data.ph != null)
                  _buildSensorRow('PH值', '${data.ph!.toStringAsFixed(1)}'),
                if (data.ammonia != null)
                  _buildSensorRow('氨氮', '${data.ammonia!.toStringAsFixed(3)} mg/L'),
                if (data.nitrite != null)
                  _buildSensorRow('亚盐', '${data.nitrite!.toStringAsFixed(3)} mg/L'),
                if (data.oxygen != null)
                  _buildSensorRow('溶氧', '${data.oxygen!.toStringAsFixed(1)} mg/L'),
              ],
            ),
            trailing: Text(
              DateFormat('HH:mm').format(data.createdAt),
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          );
        },
      ),
    );
  }

  Widget _buildSensorRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: Colors.grey),
          ),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Future<void> _refreshData() async {
    await _loadData();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('已刷新数据')),
      );
    }
  }
}
