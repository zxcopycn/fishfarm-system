# 智能渔场环境控制监测系统

## 项目概述

一个基于物联网技术的智能渔场环境监测与控制系统，实现对养殖水体环境参数的实时监测、自动控制和预警提醒。

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│              移动端 APP (Android / iOS)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │ 实时数据  │  │ 设备控制  │  │ 预警管理     │    │
│  └──────────┘  └──────────┘  ┄──────────────┄    │
└────────────┬───────────────────────┬─────────────┘
             │ HTTPS / MQTT           │ HTTPS
             ↓                        ↓
┌─────────────────────────────────────────────────────┐
│              Web 后端服务 (FastAPI)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │ REST API │  │ WebSocket│  │  定时任务引擎 │    │
│  └────┬─────┘  └────┬─────┘  └──────────┬───┘    │
│       │             │                    │         │
│       └─────────────┴────────────────────┘         │
│                          ↓                           │
│              ┌──────────────────────┐               │
│              │  数据处理 & 预警系统  │               │
│              └──────────┬───────────┘               │
│                         ↓                           │
└─────────────────────────────────────────────────────┘
                      │ MQTT
         ┌────────────┼────────────┐
         ↓            ↓            ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  水温传感器   │ │  PH传感器    │ │  其他传感器   │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┴────────────────┘
                   传感器网关
                      ↓
              ┌──────────────┐
              │  主控制器     │
              │  (水泵/气泵等) │
              └──────────────┘
```

## 功能特性

### 📊 实时监测
- 水温、PH值、氨氮、亚盐、溶氧等环境参数实时监测
- 数据刷新频率：1秒/次（可配置）
- 支持多点位同时监测

### 🎛️ 设备控制
- 远程开关控制（水泵、气泵、空调、排气扇等）
- 定时任务控制
- 批量控制多个设备

### ⚠️ 智能预警
- 多级预警（提醒、警告、危险）
- 灵活的阈值配置
- 多种预警方式（推送、短信、电话）

### 📈 数据分析
- 实时数据展示（7天）
- 历史数据查询（1年）
- 可视化图表（温度曲线、趋势分析等）
- 数据自动备份

### 📝 生产管理
- 鱼类繁育记录
- 投喂记录
- 生长周期追踪
- 生产报表生成

## 技术栈

### 后端
- **框架**: Python 3.9+ / FastAPI
- **数据库**: MySQL 8.0
- **缓存**: Redis 7.0
- **物联网**: MQTT（paho-mqtt）
- **任务调度**: APScheduler
- **日志**: Loguru
- **部署**: Docker + Docker Compose

### 前端
- **框架**: Flutter 3.0+
- **开发语言**: Dart
- **支持平台**: Android & iOS

## 项目结构

```
fishfarm-system/
├── backend/                      # 后端服务
│   ├── app/
│   │   ├── api/                 # API路由
│   │   ├── models/              # 数据模型
│   │   ├── schemas/             # 数据验证
│   │   ├── services/            # 业务逻辑
│   │   ├── utils/               # 工具函数
│   │   ├── config.py            # 配置
│   │   └── main.py              # 应用入口
│   ├── tests/                   # 测试代码
│   ├── requirements.txt         # Python依赖
│   └── Dockerfile               # Docker配置
│
├── frontend/                     # Flutter前端
│   ├── lib/
│   │   ├── main.dart            # 应用入口
│   │   ├── screens/             # 页面
│   │   ├── widgets/             # 组件
│   │   ├── services/            # 服务层
│   │   └── models/              # 数据模型
│   ├── pubspec.yaml             # Flutter依赖
│   └── Dockerfile               # Docker配置
│
├── docker-compose.yml            # Docker编排
├── README.md                     # 项目文档
└── requirements.md               # 开发文档
```

## 快速开始

### 1. 环境准备

#### 后端环境
```bash
# 克隆项目
git clone <repository-url>
cd fishfarm-system

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r backend/requirements.txt
```

#### 前端环境
```bash
# 安装 Flutter
# 下载: https://flutter.dev/docs/get-started/install

# 进入前端目录
cd frontend

# 安装依赖
flutter pub get
```

### 2. 配置数据库

```bash
# 启动MySQL和Redis
docker-compose up -d mysql redis

# 等待服务启动完成
# 数据库初始化脚本在 backend/sql/init.sql
```

### 3. 配置后端

编辑 `backend/app/config.py`：

```python
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/fishfarm"
REDIS_URL = "redis://localhost:6379/0"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "fishfarm/sensor"
```

### 4. 初始化数据库

```bash
# 执行数据库初始化
mysql -u root -p fishfarm < backend/sql/init.sql
```

### 5. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 6. 启动前端APP

```bash
cd frontend
flutter run
```

## API文档

启动后端服务后，访问：

- API文档：http://localhost:8000/docs
- OpenAPI JSON：http://localhost:8000/openapi.json

## 开发说明

### 代码规范
- 所有函数和类必须有详细的中文注释
- 代码符合 PEP 8 规范
- 遵循 FastAPI 最佳实践

### 测试

```bash
# 后端测试
cd backend
pytest tests/

# 前端测试
cd frontend
flutter test
```

## 部署

### Docker部署

```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 部署架构

```
nginx (反向代理 + SSL)
    ↓
├─→ backend (FastAPI后端)
└─→ frontend (Flutter静态文件)
```

## 未来规划

- [ ] 接入真实传感器设备
- [ ] 支持更多控制设备类型
- [ ] 增加视频监控功能
- [ ] 多用户权限管理
- [ ] 移动端推送通知
- [ ] 数据导出功能（Excel/PDF）

## 联系方式

如有问题或建议，请联系项目维护者。

---

**开发进度**: 0% (开始搭建)
**预计完成**: 2周
**最后更新**: 2026-03-21
