import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:fishfarm_monitor/dashboard/dashboard_page.dart';
import 'package:fishfarm_monitor/control/control_page.dart';
import 'package:fishfarm_monitor/history/history_page.dart';
import 'package:fishfarm_monitor/alarms/alarms_page.dart';
import 'package:fishfarm_monitor/production/production_page.dart';
import 'package:fishfarm_monitor/reminder/reminder_list_page.dart';
import 'package:fishfarm_monitor/settings/settings_page.dart';
import 'package:fishfarm_monitor/services/api_service.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> with WidgetsBindingObserver {
  int _currentIndex = 0;
  bool _isWebSocketConnected = false;

  final List<Widget> _pages = [
    const DashboardPage(),
    const ControlPage(),
    const HistoryPage(),
    const AlarmsPage(),
    const ProductionPage(),
    const ReminderListPage(),
    const SettingsPage(),
  ];

  final List<String> _titles = [
    '仪表盘',
    '设备控制',
    '历史数据',
    '预警管理',
    '生产记录',
    '提醒管理',
    '设置',
  ];

  final List<BottomNavigationBarItem> _items = [
    const BottomNavigationBarItem(
      icon: Icon(Icons.dashboard),
      label: '仪表盘',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.settings_remote),
      label: '设备控制',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.history),
      label: '历史',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.warning),
      label: '预警',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.agriculture),
      label: '生产',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.notifications),
      label: '提醒',
    ),
    const BottomNavigationBarItem(
      icon: Icon(Icons.settings),
      label: '设置',
    ),
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _connectWebSocket();
  }

  void _connectWebSocket() async {
    try {
      await ApiService().connectWebSocket(clientId: 'fishfarm_mobile');
      setState(() {
        _isWebSocketConnected = true;
      });

      // 订阅所有设备的状态更新
      ApiService().subscribeToDeviceStatus(0); // 0 表示订阅所有设备

    } catch (e) {
      print('连接WebSocket失败: $e');
    }
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      // 应用恢复时重新连接WebSocket
      _connectWebSocket();
    } else if (state == AppLifecycleState.inactive ||
               state == AppLifecycleState.paused) {
      // 应用暂停时可以保持连接，或者断开连接以节省资源
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    ApiService().disconnectWebSocket();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _pages,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Colors.blue[700],
        unselectedItemColor: Colors.grey,
        items: _items,
      ),
    );
  }
}
