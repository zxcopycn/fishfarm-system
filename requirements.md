# 智能渔场系统 - 开发文档

## 📋 系统功能清单

### 已实现功能 ✅

#### 后端功能
- ✅ 完整的数据库结构（8个核心表）
- ✅ 传感器数据管理（CRUD、查询、统计）
- ✅ 预警规则管理（阈值配置、分级预警）
- ✅ 设备控制（远程开关、历史记录）
- ✅ 生产记录管理（鱼类繁育、投喂记录）
- ✅ 数据验证和自动预警
- ✅ 模拟数据生成器（开发测试用）
- ✅ 数据自动清理（定时任务）
- ✅ 数据库自动备份
- ✅ WebSocket实时推送（预留）
- ✅ 完整的API接口
- ✅ Docker部署配置

#### 预警规则
- ✅ 水温预警（正常22-28℃，警告<21℃或>30℃，危险<18℃或>32℃）
- ✅ PH值预警（正常6-6.8，警告<5.5或>7.5，危险<5或>8）
- ✅ 分级预警（提醒、警告、危险）
- ✅ 预警记录和解决状态
- ✅ 预警汇总统计

#### 数据库
- ✅ MySQL数据库初始化脚本
- ✅ 自动创建所有表结构
- ✅ 索引优化
- ✅ 默认预警规则
- ✅ 默认管理员用户

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- MySQL 8.0+
- Redis 7.0+
- Docker & Docker Compose（推荐）

### 2. 本地部署

#### 方式一：Docker部署（推荐）

```bash
# 克隆项目
cd /home/node/.openclaw/workspace/fishfarm-system

# 创建 .env 文件
cp .env.example .env

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 测试API
curl http://localhost:8000/health
```

#### 方式二：手动部署

```bash
# 1. 安装Python依赖
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. 初始化数据库
mysql -u root -p < sql/init.sql
# 输入MySQL密码

# 3. 创建模拟设备数据
python -c "
from app.database import SessionLocal
from app.services.mocking import MockDataGenerator
db = SessionLocal()
MockDataGenerator.generate_initial_devices(db, count=5)
MockDataGenerator.generate_initial_control_devices(db, count=3)
MockDataGenerator.generate_initial_production_records(db, count=10)
db.close()
print('模拟数据生成完成！')
"

# 4. 启动后端服务
python -m uvicorn app.main:app --reload --port 8000
```

### 3. 访问系统

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **生产记录**: http://localhost:8000/api/production/list
- **传感器数据**: http://localhost:8000/api/sensor/latest

---

## 📖 API接口文档

### 传感器数据

#### 获取最新传感器数据
```
GET /api/sensor/latest?limit=20
```

#### 获取设备历史数据
```
GET /api/sensor/device/{device_id}/history?hours=24
```

#### 获取传感器统计
```
GET /api/sensor/statistics?hours=24
```

### 设备管理

#### 获取设备列表
```
GET /api/devices/list?device_type=temperature&status=1
```

#### 获取设备详情
```
GET /api/devices/{device_id}
```

#### 更新设备状态
```
PATCH /api/devices/{device_id}/status?status=1
```

### 预警管理

#### 获取预警规则
```
GET /api/alarms/rules
```

#### 获取预警记录
```
GET /api/alarms/records?level=警告&is_resolved=0&days=7
```

#### 解决预警记录
```
POST /api/alarms/records/{record_id}/resolve
```

#### 获取预警汇总
```
GET /api/alarms/summary?days=7
```

### 设备控制

#### 获取控制设备列表
```
GET /api/control/devices?status=1
```

#### 控制设备（开启/关闭）
```
POST /api/control/{device_id}/control
{
  "action": "开启",  或 "关闭"
  "target_value": 2.5,
  "remark": "手动控制"
}
```

#### 获取控制记录
```
GET /api/control/records?device_id=1&limit=50
```

### 生产记录

#### 获取生产记录
```
GET /api/production/list?fish_type=锦鲤&limit=50
```

#### 获取生产统计
```
GET /api/production/statistics
```

---

## 🧪 测试

### API测试

```bash
cd backend/tests
pytest test_api.py -v
```

### 模拟数据测试

```python
from app.database import SessionLocal
from app.services.mocking import MockDataGenerator

db = SessionLocal()

# 生成传感器数据
count = MockDataGenerator.generate_sensor_data(db, hours=1)
print(f"生成了 {count} 条传感器数据")

# 生成控制设备数据
count = MockDataGenerator.generate_control_devices(db, hours=1)
print(f"生成了 {count} 条控制记录")

# 生成生产记录
count = MockDataGenerator.generate_initial_production_records(db, count=10)
print(f"生成了 {count} 条生产记录")

db.close()
```

---

## 🗄️ 数据库说明

### 核心数据表

#### 1. device_types（设备类型表）
存储所有设备类型：温度传感器、PH传感器、氨氮传感器等

#### 2. devices（设备表）
存储所有设备的基本信息和状态

#### 3. sensor_data（传感器数据表）
存储实时传感器数据（保留7天）

#### 4. alarm_rules（预警规则表）
存储各种参数的预警阈值配置

#### 5. alarm_records（预警记录表）
存储所有触发预警的历史记录

#### 6. control_devices（控制设备表）
存储可远程控制的设备（水泵、气泵等）

#### 7. control_records（控制记录表）
存储所有设备控制操作的历史

#### 8. production_records（生产记录表）
存储鱼类繁育、投喂等生产数据

---

## 📱 移动端开发（Flutter）

### 技术栈
- Flutter 3.0+
- Dart
- HTTP客户端
- WebSocket客户端
- Charts图表库

### 项目结构
```
lib/
├── main.dart              # 应用入口
├── screens/               # 页面
│   ├── dashboard/         # 仪表盘
│   ├── sensors/           # 传感器数据
│   ├── devices/           # 设备控制
│   ├── alarms/            # 预警管理
│   ├── production/        # 生产记录
│   └── settings/          # 设置
├── widgets/               # 组件
├── services/              # 服务层
└── models/                # 数据模型
```

### API集成示例

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  final String baseUrl = 'http://your-server:8000';

  // 获取传感器数据
  Future<List<SensorData>> getSensorData() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/sensor/latest?limit=20')
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((e) => SensorData.fromJson(e)).toList();
    } else {
      throw Exception('获取传感器数据失败');
    }
  }
}
```

---

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| APP_ENV | 应用环境 | development |
| DATABASE_URL | 数据库连接串 | mysql+pymysql://root:password@localhost:3306/fishfarm |
| REDIS_URL | Redis连接串 | redis://localhost:6379/0 |
| MQTT_BROKER | MQTT服务地址 | localhost |
| MQTT_PORT | MQTT服务端口 | 1883 |
| LOG_LEVEL | 日志级别 | INFO |

### 数据保留策略

- **实时数据**：保留7天（自动清理）
- **历史数据**：保留1年
- **控制记录**：永久保留
- **生产记录**：永久保留

---

## 🐛 常见问题

### 1. MySQL连接失败
- 检查MySQL是否启动
- 检查用户名密码是否正确
- 检查防火墙设置

### 2. Redis连接失败
- 检查Redis是否启动
- 检查Redis端口是否开放

### 3. 模拟数据不显示
- 运行模拟数据生成脚本
- 检查数据库连接

---

## 📞 技术支持

如有问题，请联系开发团队。

---

**文档版本**: 1.0.0
**最后更新**: 2026-03-22
