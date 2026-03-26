import 'package:flutter/material.dart';
import 'lib/screens/login/login_page.dart';
import 'lib/screens/home/home_page.dart';

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

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const FishFarmApp());
}
}
