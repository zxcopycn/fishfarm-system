import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:intl/intl.dart';
import 'package:fishfarm_monitor/services/api_service.dart';
import 'package:fishfarm_monitor/utils/data_exporter.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  String _apiUrl = 'http://192.168.1.200:8000';
  bool _autoRefresh = true;
  int _refreshInterval = 30;
  bool _notificationsEnabled = true;
  bool _darkMode = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _apiUrl = prefs.getString('api_url') ?? 'http://192.168.1.200:8000';
      _autoRefresh = prefs.getBool('auto_refresh') ?? true;
      _refreshInterval = prefs.getInt('refresh_interval') ?? 30;
      _notificationsEnabled = prefs.getBool('notifications_enabled') ?? true;
      _darkMode = prefs.getBool('dark_mode') ?? false;
    });
  }

  Future<void> _saveSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('api_url', _apiUrl);
    await prefs.setBool('auto_refresh', _autoRefresh);
    await prefs.setInt('refresh_interval', _refreshInterval);
    await prefs.setBool('notifications_enabled', _notificationsEnabled);
    await prefs.setBool('dark_mode', _darkMode);
  }

  Future<void> _testApiConnection() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final success = await ApiService().healthCheck();
      if (mounted) {
        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('API连接成功'),
              backgroundColor: Colors.green,
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('API连接失败'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('API连接失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('系统设置'),
        backgroundColor: Colors.blue[700],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _buildSectionTitle('API 设置'),
                _buildApiSettings(),
                const SizedBox(height: 24),
                _buildSectionTitle('应用设置'),
                _buildAppSettings(),
                const SizedBox(height: 24),
                _buildSectionTitle('通知设置'),
                _buildNotificationSettings(),
                const SizedBox(height: 24),
                _buildSectionTitle('数据导出'),
                _buildDataExportSection(),
                const SizedBox(height: 24),
                _buildSectionTitle('关于应用'),
                _buildAboutSection(),
                const SizedBox(height: 32),
                _buildSaveButton(),
              ],
            ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: Colors.grey,
        ),
      ),
    );
  }

  Widget _buildApiSettings() {
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
            _buildSettingItem(
              'API 地址',
              _apiUrl,
              Icon(Icons.link),
              onTap: () => _showUrlDialog(_apiUrl),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _testApiConnection,
              icon: const Icon(Icons.check_circle),
              label: const Text('测试连接'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue[700],
                foregroundColor: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '输入服务器地址后点击测试连接',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppSettings() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildSwitchItem(
              '自动刷新',
              _autoRefresh,
              onChanged: (value) => setState(() => _autoRefresh = value),
              icon: Icon(Icons.refresh,
            ),
            if (_autoRefresh) ...[
              const SizedBox(height: 16),
              _buildSliderItem(
                '刷新间隔',
                '$_refreshInterval 秒',
                _refreshInterval,
                10,
                300,
                (value) => setState(() => _refreshInterval = value.round()),
                icon: Icon(Icons.timer,
              ),
            ],
            const SizedBox(height: 16),
            _buildSwitchItem(
              '深色模式',
              _darkMode,
              onChanged: (value) => setState(() => _darkMode = value),
              icon: Icon(Icons.dark_mode,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationSettings() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildSwitchItem(
              '启用通知',
              _notificationsEnabled,
              onChanged: (value) => setState(() => _notificationsEnabled = value),
              icon: Icon(Icons.notifications,
            ),
            const SizedBox(height: 16),
            _buildSwitchItem(
              '预警推送',
              true, // TODO: 从设置中读取
              onChanged: (value) {},
              icon: Icon(Icons.warning,
            ),
            const SizedBox(height: 16),
            _buildSwitchItem(
              '设备状态推送',
              true, // TODO: 从设置中读取
              onChanged: (value) {},
              icon: Icon(Icons.device_hub,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDataExportSection() {
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
            const Text(
              '数据导出',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 16),
            _buildExportButton(
              icon: Icon(Icons.warning,
              title: '导出预警记录',
              subtitle: '导出所有预警记录为CSV文件',
              onTap: _exportAlarms,
            ),
            const SizedBox(height: 12),
            _buildExportButton(
              icon: Icon(Icons.agriculture,
              title: '导出生产记录',
              subtitle: '导出所有生产记录为CSV文件',
              onTap: _exportProduction,
            ),
            const SizedBox(height: 12),
            _buildExportButton(
              icon: Icon(Icons.sensors,
              title: '导出传感器数据',
              subtitle: '导出传感器历史数据为CSV文件',
              onTap: _exportSensorData,
            ),
            const SizedBox(height: 12),
            _buildExportButton(
              icon: Icon(Icons.devices,
              title: '导出设备信息',
              subtitle: '导出所有设备信息为CSV文件',
              onTap: _exportDevices,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExportButton({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.blue[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: Colors.blue[700]),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.grey),
          ],
        ),
      ),
    );
  }

  Future<void> _exportAlarms() async {
    try {
      final alarms = await ApiService().getAlarmRecords(days: 30);
      if (alarms.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('没有预警记录可导出'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }
      await DataExporter.exportAlarmsToCsv(alarms);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('预警记录导出成功'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('导出失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _exportProduction() async {
    try {
      final records = await ApiService().getProductionRecords(limit: 1000);
      if (records.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('没有生产记录可导出'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }
      await DataExporter.exportProductionToCsv(records);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('生产记录导出成功'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('导出失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _exportSensorData() async {
    try {
      final devices = await ApiService().getDevices();
      final sensorData = await ApiService().getSensorData(limit: 1000);

      if (sensorData.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('没有传感器数据可导出'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }

      await DataExporter.exportSensorData(devices, sensorData);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('传感器数据导出成功'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('导出失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _exportDevices() async {
    try {
      final devices = await ApiService().getDevices();

      if (devices.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('没有设备信息可导出'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }

      await DataExporter.exportDevicesToCsv(devices);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('设备信息导出成功'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('导出失败: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Widget _buildAboutSection() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildInfoItem('应用版本', '1.1.0'),
            _buildInfoItem('开发团队', '智能渔场项目组'),
            _buildInfoItem('技术栈', 'Flutter 3.0+ + FastAPI'),
            _buildInfoItem('更新时间', DateFormat('yyyy-MM-dd').format(DateTime.now())),
            const SizedBox(height: 16),
            _buildLinkItem('查看文档', 'https://docs.openclaw.ai'),
            _buildLinkItem('反馈问题', 'mailto:support@example.com'),
          ],
        ),
      ),
    );
  }

  Widget _buildSettingItem(String label, String value, Icon icon, {Function()? onTap}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Padding(
              padding: const EdgeInsets.only(right: 12),
              child: icon,
            ),
            Expanded(
              child: Text(
                value,
                style: const TextStyle(fontSize: 16),
              ),
            ),
            const Icon(Icons.chevron_right, color: Colors.grey),
          ],
        ),
      ),
    );
  }

  Widget _buildSwitchItem(
    String label,
    bool value,
    Function(bool) onChanged, {
    required Icon icon,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: icon,
          ),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(fontSize: 16),
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: Colors.blue[700],
          ),
        ],
      ),
    );
  }

  Widget _buildSliderItem(
    String label,
    String value,
    double currentValue,
    double min,
    double max,
    Function(double) onChanged, {
    required Icon icon,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Padding(
                padding: const EdgeInsets.only(right: 12),
                child: icon,
              ),
              Expanded(
                child: Text(
                  label,
                  style: const TextStyle(fontSize: 16),
                ),
              ),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.grey,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Slider(
            value: currentValue,
            min: min,
            max: max,
            divisions: ((max - min) / 10).round(),
            onChanged: onChanged,
            activeColor: Colors.blue[700],
          ),
        ],
      ),
    );
  }

  Widget _buildInfoItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text(
            '$label: ',
            style: const TextStyle(
              fontSize: 14,
              color: Colors.grey,
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLinkItem(String label, String url) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: InkWell(
        onTap: () => _launchUrl(url),
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(8),
          child: Row(
            children: [
              const Icon(Icons.link, size: 16, color: Colors.blue),
              const SizedBox(width: 8),
              Text(
                label,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.blue[700],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSaveButton() {
    return ElevatedButton(
      onPressed: () async {
        await _saveSettings();
        ApiService().setBaseUrl(_apiUrl);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('设置已保存'),
              backgroundColor: Colors.green,
            ),
          );
        }
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.blue[700],
        foregroundColor: Colors.white,
        minimumSize: const Size(double.infinity, 50),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      child: const Text(
        '保存设置',
        style: TextStyle(fontSize: 16),
      ),
    );
  }

  void _showUrlDialog(String currentUrl) {
    final controller = TextEditingController(text: currentUrl);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('设置API地址'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: 'API地址',
                hintText: 'http://example.com:8000',
                prefixIcon: Icon(Icons.link),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              '请输入后端API的地址，确保包含协议(http/https)和端口',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              final newUrl = controller.text.trim();
              if (newUrl.isNotEmpty) {
                setState(() {
                  _apiUrl = newUrl;
                });
              }
              Navigator.pop(context);
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  Future<void> _launchUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('无法打开链接: $url')),
        );
      }
    }
  }
}