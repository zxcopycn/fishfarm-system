# 智能渔场系统 - Flutter应用快速开始

## 📱 功能清单

### 已实现功能
- ✅ 用户登录页面
- ✅ 仪表盘首页
- ✅ 设备列表展示
- ✅ 传感器数据展示
- ✅ 数据刷新功能
- ✅ API服务层

### 待实现功能
- ⏳ 设备控制页面
- ⏳ 历史数据查询
- ⏳ 预警管理页面
- ⏳ 生产记录页面
- ⏳ 备忘提醒页面
- ⏳ 系统设置页面
- ⏳ WebSocket实时推送
- ⏳ 图表展示

---

## 🚀 快速启动

### 前置要求

1. **安装 Flutter SDK**
   - 访问 https://flutter.dev/docs/get-started/install
   - 按照说明安装（推荐使用Flutter 3.0+）

2. **配置环境**
   ```bash
   export PATH="$PATH:$HOME/flutter/bin"
   flutter doctor
   ```

### 启动应用

```bash
cd /home/node/.openclaw/workspace/fishfarm-system/flutter

# 安装依赖
flutter pub get

# 启动应用（选择设备）
./flutter_start.sh
```

### 手动启动

```bash
# 1. 安装依赖
flutter pub get

# 2. 检查可用设备
flutter devices

# 3. 启动应用
flutter run
```

---

## 📊 API配置

### 修改API地址

编辑文件：`lib/services/api_service.dart`

```dart
// 默认地址
String _baseUrl = 'http://192.168.1.200:8000';

// 修改为你的服务器地址
String _baseUrl = 'http://your-server-ip:8000';
```

### 配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| API地址 | 后端服务地址 | http://192.168.1.200:8000 |
| 数据库端口 | MySQL端口 | 3306 |
| WebSocket端口 | WebSocket端口 | 8000 |

---

## 📖 API接口

应用使用以下API接口：

### 设备管理
- `GET /api/devices/list` - 获取设备列表
- `GET /api/devices/{id}` - 获取设备详情

### 传感器数据
- `GET /api/sensor/latest?limit=20` - 获取最新传感器数据
- `GET /api/sensor/device/{id}/history` - 获取历史数据

### 预警管理
- `GET /api/alarms/rules` - 获取预警规则
- `GET /api/alarms/records` - 获取预警记录
- `POST /api/alarms/records/{id}/resolve` - 解决预警

### 设备控制
- `POST /api/control/{id}/control` - 控制设备

### 生产记录
- `GET /api/production/list` - 获取生产记录
- `GET /api/production/statistics` - 获取统计数据

---

## 🎨 技术栈

- **框架**: Flutter 3.0+
- **语言**: Dart
- **状态管理**: Provider
- **网络请求**: Dio
- **图表展示**: fl_chart
- **本地存储**: shared_preferences

---

## 📱 支持平台

- ✅ Android 5.0+
- ✅ iOS 12.0+
- ✅ Web（可选）

---

## 🔧 开发命令

```bash
# 安装依赖
flutter pub get

# 检查代码规范
flutter analyze

# 运行单元测试
flutter test

# 打包应用
flutter build apk  # Android
flutter build ios  # iOS
flutter build web  # Web
```

---

## 🐛 常见问题

### 1. Flutter依赖安装失败
```bash
flutter clean
flutter pub get
```

### 2. 无法连接到API
- 检查后端服务是否启动
- 检查IP地址是否正确
- 检查防火墙设置

### 3. 设备无法运行
- 运行 `flutter doctor` 检查环境
- 安装缺失的SDK
- 重启VS Code/Android Studio

---

## 📞 技术支持

如有问题，请联系开发团队。

---

**文档版本**: 1.0.0
**最后更新**: 2026-03-22
