# 智能渔场环境控制监测系统

## 🎯 项目简介

这是一个完整的智能渔场环境控制监测系统，实时监控水温、PH值、氨氮、亚盐、溶氧等关键指标，提供设备远程控制、预警管理、生产记录等功能。

### ✨ 核心功能

1. **实时数据监控** - 显示所有传感器的最新数据
2. **设备远程控制** - 支持水泵、气泵、空调等设备的远程开关控制
3. **预警管理系统** - 多级预警（提醒、警告、危险），自动检测和提醒
4. **历史数据查询** - 查询历史数据，支持时间范围筛选
5. **生产记录管理** - 鱼类繁育、投喂记录管理
6. **移动端支持** - Flutter移动应用，Android/iOS双平台

---

## 📊 技术栈

### 后端
- **框架**: FastAPI (Python)
- **数据库**: MySQL 8.0
- **缓存**: Redis 7.0
- **物联网**: MQTT协议
- **容器**: Docker

### 移动端
- **框架**: Flutter 3.0+
- **语言**: Dart
- **状态管理**: Provider
- **网络请求**: Dio

---

## 🚀 快速开始

### 方式一：Docker部署（推荐）

```bash
# 克隆或进入项目目录
cd /home/node/.openclaw/workspace/fishfarm-system

# 运行快速启动脚本
./start.sh

# 访问API文档
open http://localhost:8000/docs
```

### 方式二：手动部署

```bash
# 1. 后端服务
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# 2. 初始化数据库
mysql -u root -p < sql/init.sql

# 3. 生成模拟数据
python -c "
from app.database import SessionLocal
from app.services.mocking import MockDataGenerator
db = SessionLocal()
MockDataGenerator.generate_initial_devices(db, count=5)
MockDataGenerator.generate_initial_control_devices(db, count=3)
MockDataGenerator.generate_initial_production_records(db, count=10)
db.close()
print('✅ 模拟数据生成完成！')
"
```

### 方式三：验证系统

```bash
./verify.sh
```

---

## 📱 移动端启动

```bash
cd /home/node/.openclaw/workspace/fishfarm-system/flutter

# 安装依赖
flutter pub get

# 启动应用
flutter run
```

---

## 📖 API文档

启动服务后访问：**http://localhost:8000/docs**

### 主要接口

```
GET  /api/devices/list          # 获取设备列表
GET  /api/sensor/latest         # 获取最新传感器数据
GET  /api/alarms/rules          # 获取预警规则
GET  /api/alarms/records        # 获取预警记录
GET  /api/production/list       # 获取生产记录
POST /api/control/{id}/control  # 控制设备
```

---

## 📊 预警规则

| 传感器类型 | 参数 | 正常范围 | 提醒 | 警告 | 危险 |
|-----------|------|---------|------|------|------|
| **水温** | 温度（℃） | 22-28 | <21 或 >30 | <18 或 >32 | <18 或 >32 |
| **PH值** | pH值 | 6.0-6.8 | <5.5 或 >7.5 | <5.5 或 >8 | <5 或 >8 |
| **氨氮** | 氨氮（mg/L） | 0-0.5 | >0.5 或 >1.0 | >0.1 或 >1.5 | >0.1 或 >2.0 |
| **亚盐** | 亚盐（mg/L） | 0.1-0.3 | >0.1 或 >0.5 | >0.3 或 >0.5 | >0.1 或 >1.0 |
| **溶氧** | 溶氧（mg/L） | 5-10 | <3 或 >12 | <4 或 >12 | <4 或 >12 |

---

## 🗂️ 项目结构

```
fishfarm-system/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API接口
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务服务
│   │   └── utils/             # 工具函数
│   ├── sql/                   # 数据库脚本
│   ├── tests/                 # 测试文件
│   ├── Dockerfile
│   └── requirements.txt
├── flutter/                    # Flutter移动端
│   ├── lib/
│   ├── pubspec.yaml
│   └── QUICKSTART.md
├── docker-compose.yml         # Docker编排
├── nginx/                      # Nginx配置
├── start.sh                    # 快速启动脚本
├── verify.sh                   # 验证脚本
├── README.md                   # 项目说明
├── requirements.md             # 开发文档
├── PROJECT_SUMMARY.md          # 项目总结
└── .env.example                # 环境变量示例
```

---

## 🧪 测试

### API测试

```bash
cd backend/tests
pytest test_api.py -v
```

### 模拟数据测试

```bash
python -c "
from app.database import SessionLocal
from app.services.mocking import MockDataGenerator

db = SessionLocal()
MockDataGenerator.generate_sensor_data(db, hours=1)
MockDataGenerator.generate_control_devices(db, hours=1)
db.close()
print('✅ 模拟数据生成完成')
"
```

---

## 📚 文档

- **项目说明**: `README.md`
- **开发文档**: `requirements.md`
- **项目总结**: `PROJECT_SUMMARY.md`
- **Flutter说明**: `flutter/README.md`
- **Flutter快速开始**: `flutter/QUICKSTART.md`

---

## 🔧 配置

### 环境变量

编辑 `.env` 文件：

```bash
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/fishfarm
REDIS_URL=redis://localhost:6379/0
MQTT_BROKER=localhost
LOG_LEVEL=INFO
```

### 数据库

- **用户名**: `root`
- **密码**: `password`
- **数据库名**: `fishfarm`

---

## 🐛 常见问题

### 1. MySQL连接失败
```bash
# 检查MySQL是否启动
docker-compose ps

# 查看日志
docker-compose logs mysql
```

### 2. 无法访问API
```bash
# 检查后端服务
docker-compose logs backend

# 重启服务
docker-compose restart
```

### 3. 移动端无法连接API
- 确保移动端和后端在同一网络
- 修改 `flutter/lib/services/api_service.dart` 中的API地址
- 确保后端服务已启动

---

## 📞 技术支持

详细文档请查看：
- `/home/node/.openclaw/workspace/fishfarm-system/requirements.md`
- `/home/node/.openclaw/workspace/fishfarm-system/PROJECT_SUMMARY.md`

---

**版本**: 1.0.0
**状态**: 可测试、可部署
**更新日期**: 2026-03-22
