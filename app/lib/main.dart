import 'package:flutter/material.dart';
import 'package:fishfarm_monitor/screens/login_page.dart';
import 'package:fishfarm_monitor/screens/home_page.dart';
import 'package:fishfarm_monitor/services/api_service.dart';
import 'package:fishfarm_monitor/services/websocket_service.dart';

class FishFarmApp extends StatelessWidget {
  const FishFarmApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '智能渔场监测',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.blue[700],
          foregroundColor: Colors.white,
          elevation: 0,
        ),
        cardTheme: CardTheme(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      home: const LoginPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // 初始化API服务，加载保存的服务器地址
  try {
    await ApiService.init();
  } catch (e, stackTrace) {
    print('API服务初始化失败: $e\n$stackTrace');
  }
  
  // 延迟初始化WebSocket服务，确保UI先渲染
  Future.delayed(Duration(milliseconds: 500), () {
    try {
      WebSocketService().initConnection();
    } catch (e) {
      print('WebSocket服务初始化失败: $e');
    }
  });
  
  runApp(const FishFarmApp());
}
