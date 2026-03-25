# 渔场系统移动端开发计划

## 📊 当前状态分析

### ✅ 已完成功能
- 用户登录页面
- 仪表盘首页
- 设备列表展示
- 传感器数据展示
- 设备控制页面
- 历史数据查询页面（fl_chart图表）
- 预警管理页面
- 生产记录页面
- 系统设置页面（完整实现）
- API服务层
- 数据模型（Device、SensorData、Alarm、Production）

### ⚠️ 发现的问题
1. **api_service.dart 导入错误** - 最后一行有多余的导入语句
2. **缺少Reminder功能** - 没有备忘提醒模块
3. **数据交互不够完善** - 部分功能缺少完整的CRUD操作

---

## 🎯 开发计划（按优先级）

## 第一阶段：基础功能完善（2-3天）

### 1. 修复API服务问题
- [ ] 修复 api_service.dart 底部的导入错误
- [ ] 清理冗余代码
- [ ] 验证所有API调用正常工作

### 2. 实现Reminder功能（核心功能）
#### 2.1 数据模型
```
lib/models/reminder.dart
```
需要包含：
- Reminder 类（id、title、description、trigger_time、is_repeat、repeat_config）
- ReminderType（提醒类型：定时、事件、预警）
- RepeatType（重复类型：不重复、每天、每周、每月）

#### 2.2 页面开发
```
lib/screens/reminder/reminder_list_page.dart    # 提醒列表页
lib/screens/reminder/reminder_detail_page.dart  # 提醒详情/编辑页
lib/screens/reminder/reminder_add_page.dart     # 添加提醒页
```

功能需求：
- 显示所有提醒列表
- 支持添加新提醒
- 支持编辑现有提醒
- 支持删除提醒
- 支持标记为已完成
- 支持按提醒类型筛选
- 支持重复提醒设置

#### 2.3 API服务扩展
在 api_service.dart 中添加：
```dart
// 获取提醒列表
Future<List<Reminder>> getReminders();

// 创建提醒
Future<Reminder> createReminder(Reminder reminder);

// 更新提醒
Future<Reminder> updateReminder(Reminder reminder);

// 删除提醒
Future<bool> deleteReminder(int id);

// 标记为已完成
Future<bool> markAsCompleted(int id);
```

#### 2.4 更新导航
- 修改 `lib/screens/home/home_page.dart`
- 在底部导航栏添加"提醒"图标
- 集成Reminder页面路由

### 3. 完善预警详情页面
- [ ] 创建预警详情页面（`lib/screens/alarms/alarm_detail_page.dart`）
- [ ] 显示预警详细信息（设备、传感器、阈值、时间）
- [ ] 查看历史预警记录
- [ ] 提供解决预警的操作
- [ ] 添加警告级别颜色区分

---

## 第二阶段：数据交互完善（2-3天）

### 4. 完善生产记录CRUD
当前问题：生产记录页面只能查看，不能添加/编辑/删除

#### 4.1 添加生产记录功能
- [ ] 在生产记录页面添加"添加记录"按钮
- [ ] 创建添加记录的表单页面
- [ ] 支持选择鱼类品种
- [ ] 支持输入数量
- [ ] 支持设置产卵日期、孵化日期
- [ ] 支持输入生长阶段、重量、长度
- [ ] 支持输入投喂量
- [ ] 支持添加备注
- [ ] 集成后端API创建记录

#### 4.2 编辑生产记录功能
- [ ] 每条记录添加"编辑"按钮
- [ ] 创建编辑表单（复用添加表单逻辑）
- [ ] 预填充现有数据
- [ ] 集成后端API更新记录

#### 4.3 删除生产记录功能
- [ ] 每条记录添加"删除"按钮（带确认对话框）
- [ ] 集成后端API删除记录
- [ ] 添加删除确认提示

### 5. 完善预警详情页面
- [ ] 创建预警详情页面（`lib/screens/alarms/alarm_detail_page.dart`）
- [ ] 显示预警详细信息（设备、传感器、阈值、时间）
- [ ] 查看历史预警记录
- [ ] 提供解决预警的操作
- [ ] 添加警告级别颜色区分

---

## 第三阶段：体验优化（1-2天）

### 6. 实现WebSocket实时推送
#### 6.1 后端验证
- [ ] 确认后端WebSocket服务已实现
- [ ] 测试WebSocket连接
- [ ] 验证消息格式和类型

#### 6.2 客户端集成
- [ ] 在 api_service.dart 中完善WebSocket连接逻辑
- [ ] 添加订阅传感器更新功能
- [ ] 添加订阅设备状态更新功能
- [ ] 创建WebSocket监听器
- [ ] 实时更新UI界面

#### 6.3 页面优化
- [ ] 仪表盘实时刷新传感器数据
- [ ] 预警实时推送通知
- [ ] 设备状态实时更新

### 7. 添加数据导出功能
- [ ] 在设置页面添加"导出数据"按钮
- [ ] 支持导出历史数据（CSV格式）
- [ ] 支持导出生产记录（CSV格式）
- [ ] 支持导出预警记录（CSV格式）
- [ ] 集成分享功能

---

## 第四阶段：测试和优化（1-2天）

### 8. 测试和修复
- [ ] 单元测试（核心业务逻辑）
- [ ] 集成测试（API调用）
- [ ] UI测试（页面交互）
- [ ] 修复发现的bug
- [ ] 性能优化

### 9. 多端适配
- [ ] Android端测试
- [ ] iOS端测试（如果需要）
- [ ] 平板适配（横屏模式）
- [ ] 不同屏幕尺寸适配

---

## 📋 完成标准

### 必须完成（MVP）
- [ ] 修复所有已知bug
- [ ] 实现Reminder功能（完整CRUD）
- [ ] 完善生产记录CRUD
- [ ] WebSocket实时推送正常工作

### 建议完成
- [ ] 数据导出功能
- [ ] 完整的单元测试
- [ ] 多端适配

### 可选完成
- [ ] 深色模式完善
- [ ] 数据分析图表
- [ ] 推送通知集成

---

## 🚀 快速开始

### 启动开发
```bash
cd /home/node/.openclaw/workspace/fishfarm-system/flutter

# 安装依赖
flutter pub get

# 启动应用
flutter run
```

### 启动后端服务
```bash
cd /home/node/.openclaw/workspace/fishfarm-system

# 启动所有服务
./start.sh

# 或单独启动后端
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

---

## 📝 开发顺序建议

1. **先修复问题**（1小时）
   - 修复 api_service.dart 导入错误
   - 验证基本功能正常

2. **实现Reminder功能**（半天到1天）
   - 创建数据模型
   - 实现Reminder页面
   - 添加API调用

3. **完善生产记录CRUD**（1天）
   - 添加记录功能
   - 编辑记录功能
   - 删除记录功能

4. **完善预警详情页面**（半天）
   - 创建详情页
   - 实现预警解决功能

5. **实现WebSocket推送**（1天）
   - 集成WebSocket
   - 实时更新UI

6. **测试和优化**（1天）
   - 测试所有功能
   - 修复bug
   - 性能优化

---

## 🎯 下一步行动

当前应该：
1. 先确认是否需要修改Reminder的API接口（如果后端没有实现）
2. 从修复 api_service.dart 开始
3. 逐步实现Reminder功能

需要我：
- [ ] 立即开始修复 api_service.dart
- [ ] 先检查后端Reminder API接口是否存在
- [ ] 有其他优先级不同的安排
