# 智能渔场系统 - Flutter移动端

## 项目说明

智能渔场环境控制监测系统的Flutter移动端应用，支持Android和iOS。

## 功能列表

### 1. 实时数据监控
- 显示所有传感器的最新数据
- 仪表盘视图（温度、PH、氨氮、亚盐、溶氧）
- 数据更新频率：实时（WebSocket）

### 2. 设备控制
- 查看所有控制设备列表
- 远程开关控制
- 调节功率设置
- 实时查看设备状态

### 3. 历史数据查询
- 按设备查询历史数据
- 按时间范围筛选（1小时、24小时、7天、30天）
- 图表展示数据趋势

### 4. 预警管理
- 查看当前预警列表
- 预警级别筛选（提醒/警告/危险）
- 标记预警为已解决
- 预警消息推送通知

### 5. 生产记录管理
- 查看所有生产记录
- 按鱼类品种筛选
- 按生长阶段筛选
- 统计分析

### 6. 备忘提醒
- 添加备忘事项
- 提醒时间设置
- 提醒状态管理

### 7. 系统设置
- 用户登录
- API地址配置
- 推送通知设置
- 数据刷新频率设置

## 技术栈

- **语言**: Dart
- **框架**: Flutter 3.0+
- **状态管理**: Provider
- **网络请求**: Dio
- **WebSocket**: web_socket_channel
- **图表**: fl_chart
- **本地存储**: shared_preferences
- **权限管理**: permission_handler

## 项目结构

```
lib/
├── main.dart                 # 应用入口
├── app.dart                  # 应用配置
├── models/                   # 数据模型
│   ├── sensor_data.dart
│   ├── device.dart
│   ├── alarm.dart
│   ├── production.dart
│   └── user.dart
├── services/                 # 服务层
│   ├── api_service.dart      # API请求
│   ├── websocket_service.dart # WebSocket连接
│   ├── storage_service.dart  # 本地存储
│   └── notification_service.dart # 推送通知
├── providers/                # 状态管理
│   ├── sensor_provider.dart
│   ├── device_provider.dart
│   ├── alarm_provider.dart
│   └── production_provider.dart
├── screens/                  # 页面
│   ├── login/               # 登录页
│   ├── dashboard/           # 仪表盘
│   ├── sensors/             # 传感器数据
│   ├── devices/             # 设备控制
│   ├── alarms/              # 预警管理
│   ├── production/          # 生产记录
│   ├── reminders/           # 备忘提醒
│   └── settings/            # 设置页
├── widgets/                  # 自定义组件
│   ├── sensor_card.dart
│   ├── device_card.dart
│   ├── alarm_list.dart
│   ├── data_chart.dart
│   └── refresh_indicator.dart
└── utils/                    # 工具类
    ├── constants.dart
    ├── validators.dart
    └── formatters.dart

assets/
├── images/                   # 图片资源
├── icons/                    # 图标资源
└── fonts/                    # 自定义字体
