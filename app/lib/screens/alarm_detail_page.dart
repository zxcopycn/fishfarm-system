import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:fishfarm_monitor/models/alarm.dart';
import 'package:fishfarm_monitor/models/device.dart';
import 'package:fishfarm_monitor/services/api_service.dart';

class AlarmDetailPage extends StatefulWidget {
  final AlarmRecord alarm;
  final VoidCallback? onAlarmResolved;

  const AlarmDetailPage({
    super.key,
    required this.alarm,
    this.onAlarmResolved,
  });

  @override
  State<AlarmDetailPage> createState() => _AlarmDetailPageState();
}

class _AlarmDetailPageState extends State<AlarmDetailPage> {
  bool _isLoading = false;
  bool _isResolved = false;
  late AlarmRecord _alarm;
  Device? _device;
  List<AlarmRecord> _historyRecords = [];

  @override
  void initState() {
    super.initState();
    _alarm = widget.alarm;
    _isResolved = widget.alarm.isResolved == 1;
    _loadDeviceDetails();
    _loadHistoryRecords();
  }

  Future<void> _loadDeviceDetails() async {
    try {
      final devices = await ApiService().getDevices();
      final device = devices.firstWhere(
        (d) => d.id == _alarm.deviceId,
        orElse: () => Device(id: 0, deviceName: '未知设备', deviceTypeId: 0, location: '未知', status: 0, createdAt: DateTime.now()),
      );
      setState(() {
        _device = device;
      });
    } catch (e) {
      print('加载设备详情失败: $e');
    }
  }

  Future<void> _loadHistoryRecords() async {
    try {
      final history = await ApiService().getAlarmRecords(
        isResolved: true,
        days: 30,
      );
      setState(() {
        _historyRecords = history.where(
          (record) => record.deviceId == _alarm.deviceId && record.id != _alarm.id
        ).toList();
      });
    } catch (e) {
      print('加载历史预警记录失败: $e');
    }
  }

  Future<void> _resolveAlarm() async {
    if (_isResolved) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认解决'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('确定要将此预警标记为已解决吗？'),
            const SizedBox(height: 12),
            Text(
              '预警级别: ${_alarm.level.level}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Text(
              '设备: ${_device?.deviceName ?? "未知设备"}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Text(
              '问题描述: ${_alarm.message}',
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('确认解决'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final success = await ApiService().resolveAlarm(_alarm.id);
      if (success) {
        setState(() {
          _isResolved = true;
          _alarm = _alarm.copyWith(
            isResolved: true,
          );
        });

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('预警已标记为已解决'),
            backgroundColor: Colors.green,
          ),
        );

        widget.onAlarmResolved?.call();
      } else {
        throw Exception('解决预警失败');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('解决失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  String _getLevelColor(String level) {
    switch (level) {
      case '提醒':
        return '#FFA500'; // 橙色
      case '警告':
        return '#FF4500'; // 橙红色
      case '危险':
        return '#DC143C'; // 深红色
      default:
        return '#666666'; // 灰色
    }
  }

  Color _getLevelBgColor(AlarmLevel level) {
    switch (level.level) {
      case '提醒':
        return Colors.orange.shade100;
      case '警告':
        return Colors.orange.shade200;
      case '危险':
        return Colors.red.shade200;
      default:
        return Colors.grey.shade200;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('预警详情'),
        backgroundColor: Colors.blue[700],
        actions: [
          if (!_isResolved && !_isLoading)
            IconButton(
              icon: const Icon(Icons.check_circle_outline),
              onPressed: _resolveAlarm,
              tooltip: '标记为已解决',
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildAlertHeader(),
                  const SizedBox(height: 20),
                  _buildDeviceInfo(),
                  const SizedBox(height: 20),
                  _buildAlertInfo(),
                  const SizedBox(height: 20),
                  if (_historyRecords.isNotEmpty) ...[
                    _buildHistorySection(),
                  ],
                ],
              ),
            ),
    );
  }

  Widget _buildAlertHeader() {
    return Card(
      elevation: 3,
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
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getLevelBgColor(_alarm.level),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    _alarm.level.level,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  _isResolved ? '已解决' : '待处理',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: _isResolved ? Colors.green[700] : Colors.red[700],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              _alarm.message,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '预警ID: ${_alarm.id}',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
                Text(
                  _isResolved 
                      ? '解决时间: ${_formatDateTime(_alarm.createdAt)}'
                      : '创建时间: ${_formatDateTime(_alarm.createdAt)}',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDeviceInfo() {
    if (_device == null) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '设备信息',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              Text('设备信息加载中...'),
            ],
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '设备信息',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildInfoRow(Icons.device_hub, '设备名称', _device!.deviceName),
            _buildInfoRow(Icons.tag, '设备编号', '设备_${_device!.id}'),
            _buildInfoRow(Icons.category, '设备类型', _device!.deviceTypeName ?? '未知类型'),
            _buildInfoRow(Icons.location_on, '安装位置', _device!.location),
            _buildInfoRow(Icons.info, '设备状态', _device!.status == 1 ? '在线' : '离线'),
          ],
        ),
      ),
    );
  }

  Widget _buildAlertInfo() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '预警详情',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildInfoRow(Icons.warning, '预警级别', _alarm.level.level),
            _buildInfoRow(Icons.compare_arrows, '阈值设置', '${_alarm.thresholdValue}'),
            _buildInfoRow(Icons.show_chart, '实际值', '${_alarm.actualValue}'),
            _buildInfoRow(Icons.trending_up, '偏离率', '${_calculateDeviation()}%'),
            if (_alarm.isResolved == 1) ...[
              const SizedBox(height: 8),
              _buildInfoRow(Icons.check_circle, '解决时间', _formatDateTime(_alarm.createdAt)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildHistorySection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text(
                  '历史预警记录',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const SizedBox(width: 8),
                Text(
                  '(${_historyRecords.length}条)',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ..._historyRecords.take(3).map((record) => _buildHistoryItem(record)),
            if (_historyRecords.length > 3)
              TextButton(
                onPressed: () {
                  // 可以跳转到历史预警页面
                },
                child: Text('查看全部 ${_historyRecords.length} 条记录'),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryItem(AlarmRecord record) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: _getLevelBgColor(record.level),
          borderRadius: BorderRadius.circular(6),
        ),
        child: Row(
          children: [
            Icon(
              Icons.circle,
              size: 8,
              color: _isResolved ? Colors.green : Colors.orange,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    record.message,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    '${_formatDateTime(record.createdAt)}',
                    style: TextStyle(
                      fontSize: 11,
                      color: Colors.grey[700],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(icon, size: 16, color: Colors.grey[600]),
          const SizedBox(width: 8),
          Expanded(
            flex: 1,
            child: Text(
              '$label: ',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  String _formatDateTime(DateTime? dateTime) {
    if (dateTime == null) return '未知';
    try {
      return DateFormat('yyyy-MM-dd HH:mm:ss').format(dateTime);
    } catch (e) {
      return '未知';
    }
  }

  String _calculateDeviation() {
    if (_alarm.thresholdValue == null || _alarm.actualValue == null) return '0';
    if (_alarm.thresholdValue == 0) return '0';
    return (((_alarm.actualValue! - _alarm.thresholdValue!) / _alarm.thresholdValue! * 100).toStringAsFixed(2));
  }
}
