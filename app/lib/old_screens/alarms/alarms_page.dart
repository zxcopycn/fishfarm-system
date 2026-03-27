import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:fishfarm_monitor/models/alarm.dart';
import 'package:fishfarm_monitor/services/api_service.dart';
import 'package:fishfarm_monitor/services/websocket_service.dart';
import 'alarm_detail_page.dart';

class AlarmsPage extends StatefulWidget {
  const AlarmsPage({super.key});

  @override
  State<AlarmsPage> createState() => _AlarmsPageState();
}

class _AlarmsPageState extends State<AlarmsPage> {
  bool _isLoading = true;
  List<AlarmRecord> _alarms = [];
  String _filterLevel = 'all'; // all, 提醒, 警告, 危险
  bool _showResolved = false;
  bool _wsConnected = false;

  @override
  void initState() {
    super.initState();
    _setupWebSocket();
    _loadAlarms();
  }

  @override
  void dispose() {
    wsService.removeListener('alarm_alert', _onAlarmAlert);
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
    wsService.addListener('alarm_alert', _onAlarmAlert);
    wsService.addListener('device_status_update', _onDeviceStatusUpdate);
  }

  void _onAlarmAlert(Map<String, dynamic> data) {
    // 实时添加新的预警
    final alarm = AlarmRecord.fromJson(data['data']);
    
    if (!mounted) return;

    setState(() {
      _alarms.insert(0, alarm); // 将新预警添加到列表顶部
    });

    // 显示预警通知
    _showAlertNotification(alarm);
  }

  void _onDeviceStatusUpdate(Map<String, dynamic> data) {
    // 根据设备状态更新可能引发的预警
    final deviceId = data['data']['device_id'] as int?;
    final status = data['data']['status'] as int?;
    
    if (deviceId != null && status != null && status == 0) {
      // 如果设备停止运行，可能需要生成预警
      _showAlertNotification(
        AlarmRecord(
          id: 0,
          deviceName: '设备异常',
          level: '提醒',
          message: '设备已停止运行',
          status: 0,
          timestamp: DateTime.now(),
          resolved: false,
        ),
      );
    }
  }

  void _showAlertNotification(AlarmRecord alarm) {
    if (!mounted) return;

    // 根据预警级别选择颜色
    Color color;
    switch (alarm.level) {
      case '提醒':
        color = Colors.blue;
        break;
      case '警告':
        color = Colors.orange;
        break;
      case '危险':
        color = Colors.red;
        break;
      default:
        color = Colors.grey;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              Icons.warning,
              color: Colors.white,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '⚠️ ${alarm.level}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    alarm.message,
                    style: const TextStyle(color: Colors.white),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
        backgroundColor: color,
        duration: const Duration(seconds: 4),
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        action: SnackBarAction(
          label: '查看',
          textColor: Colors.white,
          onPressed: () {
            // 跳转到预警页面
            if (mounted) {
              Navigator.of(context).pop();
              setState(() {
                _filterLevel = alarm.level;
                _showResolved = false;
              });
              _loadAlarms();
            }
          },
        ),
      ),
    );
  }

  Future<void> _loadAlarms() async {
    try {
      String? level;
      if (_filterLevel != 'all') {
        level = _filterLevel;
      }

      final alarms = await ApiService().getAlarmRecords(
        level: level,
        isResolved: _showResolved ? null : false,
        days: 7,
      );

      setState(() {
        _alarms = alarms;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载预警记录失败: $e')),
        );
      }
    }
  }

  Future<void> _resolveAlarm(AlarmRecord alarm) async {
    try {
      final success = await ApiService().resolveAlarm(alarm.id);

      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('预警已解决'),
            backgroundColor: Colors.green,
          ),
        );
        _loadAlarms();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('解决预警失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Color _getLevelColor(String level) {
    switch (level) {
      case '提醒':
        return Colors.orange;
      case '警告':
        return Colors.orangeAccent;
      case '危险':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getLevelIcon(String level) {
    switch (level) {
      case '提醒':
        return Icons.info;
      case '警告':
        return Icons.warning;
      case '危险':
        return Icons.error;
      default:
        return Icons.notifications;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('预警管理'),
        backgroundColor: Colors.blue[700],
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAlarms,
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
                _buildFilters(),
                Expanded(
                  child: _buildAlarmList(),
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
            _wsConnected ? '实时预警监控已开启' : '连接断开',
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

  Widget _buildFilters() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 级别筛选
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildFilterChip('all', '全部'),
                const SizedBox(width: 8),
                _buildFilterChip('提醒', '提醒'),
                const SizedBox(width: 8),
                _buildFilterChip('警告', '警告'),
                const SizedBox(width: 8),
                _buildFilterChip('危险', '危险'),
              ],
            ),
          ),
          const SizedBox(height: 16),
          // 已解决/未解决筛选
          Row(
            children: [
              Checkbox(
                value: _showResolved,
                onChanged: (value) {
                  setState(() {
                    _showResolved = value ?? false;
                  });
                  _loadAlarms();
                },
              ),
              const Text('显示已解决的预警'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String level, String label) {
    final isSelected = _filterLevel == level;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _filterLevel = level;
        });
        _loadAlarms();
      },
      selectedColor: Colors.blue[700],
      checkmarkColor: Colors.white,
      backgroundColor: Colors.grey[200],
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : Colors.black,
      ),
    );
  }

  Widget _buildAlarmList() {
    if (_alarms.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.check_circle, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            const Text(
              '暂无预警记录',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadAlarms,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: _alarms.length,
        itemBuilder: (context, index) {
          final alarm = _alarms[index];
          return _buildAlarmCard(alarm);
        },
      ),
    );
  }

  Widget _buildAlarmCard(AlarmRecord alarm) {
    final isResolved = alarm.isResolved == 1;
    final levelColor = _getLevelColor(alarm.alarmLevel);

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => AlarmDetailPage(
                alarm: alarm,
                onAlarmResolved: () {
                  setState(() {
                    _loadAlarms();
                  });
                },
              ),
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: levelColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _getLevelIcon(alarm.alarmLevel),
                          size: 16,
                          color: levelColor,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          alarm.alarmLevel,
                          style: TextStyle(
                            fontSize: 12,
                            color: levelColor,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  if (isResolved)
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.green.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.check,
                            size: 16,
                            color: Colors.green,
                          ),
                          SizedBox(width: 4),
                          Text(
                            '已解决',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.green,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  const Spacer(),
                  Text(
                    DateFormat('MM-dd HH:mm').format(alarm.createdAt),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                alarm.message ?? '未知预警',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (alarm.deviceId != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.devices, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(
                      '设备ID: ${alarm.deviceId}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ],
              if (alarm.actualValue != null) ...[
                const SizedBox(height: 4),
                Row(
                  children: [
                    const Icon(Icons.straighten, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(
                      '实际值: ${alarm.actualValue}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(width: 16),
                    const Icon(Icons.warning, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(
                      '阈值: ${alarm.thresholdValue}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ],
              if (!isResolved) ...[
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  height: 40,
                  child: ElevatedButton.icon(
                    onPressed: () => _resolveAlarm(alarm),
                    icon: const Icon(Icons.check),
                    label: const Text('标记为已解决'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
