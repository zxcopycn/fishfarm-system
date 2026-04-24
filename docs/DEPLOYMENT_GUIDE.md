# 智能渔场监控系统 - 客户部署指南

**版本**: v1.0.1 (Build #4)
**发布日期**: 2026-04-24
**文档编号**: DOC-2026-0422-001

---

## 📦 一、安装包清单

| 文件名 | 说明 | 大小 |
|--------|------|------|
| `fishfarm_monitor_v1.0.0.apk` | Android安装包 | 23MB |
| `final-fishfarm-server.js` | 后端服务程序 | - |
| `部署指南.md` | 本文档 | - |

---

## 🖥️ 二、服务器部署（后端）

### 2.1 环境要求

- **操作系统**: Linux / Windows / macOS
- **Node.js**: v14 或更高版本
- **网络**: 固定IP地址，端口8080可访问

### 2.2 部署步骤

**Step 1: 确保已安装Node.js**

```bash
node --version   # 应显示 v14.x 或更高
npm --version    # 应显示 6.x 或更高
```

**Step 2: 上传后端程序**

将 `final-fishfarm-server.js` 上传到服务器任意目录，例如 `/home/fishfarm/`

```bash
mkdir -p /home/fishfarm
cp final-fishfarm-server.js /home/fishfarm/
```

**Step 3: 启动服务**

```bash
cd /home/fishfarm
node final-fishfarm-server.js
```

看到以下输出表示启动成功：

```
🚀 渔场API服务器已启动
📱 局域网地址: http://192.168.1.200:8080
💊 健康检查: http://localhost:8080/health
```

**Step 4: 验证服务**

在服务器本地测试：

```bash
curl http://localhost:8080/health
```

应返回：

```json
{"status":"healthy","service":"fishfarm-api","message":"服务器正常运行"}
```

### 2.3 开机自启动（Linux systemd）

创建服务文件：

```bash
sudo nano /etc/systemd/system/fishfarm.service
```

写入以下内容：

```ini
[Unit]
Description=FishFarm API Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/fishfarm
ExecStart=/usr/bin/node /home/fishfarm/final-fishfarm-server.js
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable fishfarm
sudo systemctl start fishfarm
```

---

## 📱 三、移动端安装（Android APP）

### 3.1 安装APK

1. 将 `fishfarm_monitor_v1.0.0.apk` 复制到手机
2. 打开手机 **设置 → 安全**
3. 启用 **未知来源/安装未知应用**
4. 点击APK文件，按提示安装

### 3.2 配置服务器地址

1. 打开已安装的渔场监控APP
2. 进入 **设置** 页面（右下角）
3. 在 **服务器地址** 栏输入服务器IP和端口
4. 格式：`http://服务器IP:8080`
5. 例如：`http://192.168.1.100:8080`
6. 点击 **保存**

### 3.3 验证连接

返回首页，如果看到设备列表和传感器数据，说明连接成功。

---

## 🌐 四、网络配置

### 4.1 防火墙设置

服务器端需开放端口 **8080**：

```bash
# Ubuntu/Debian
sudo ufw allow 8080/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

### 4.2 路由器端口转发（如需外网访问）

如需从外网访问，需在路由器设置端口转发：

- 内部端口：8080
- 外部端口：8080（或其他）
- 协议：TCP

**注意**：外网访问需考虑安全性，建议使用VPN或白名单限制。

### 4.3 局域网连接

确保手机和服务器在同一局域网内。服务器IP需使用局域网固定IP，建议在路由器上设置DHCP静态分配。

---

## ⚠️ 五、注意事项

1. **数据说明**：当前版本使用虚拟传感器数据，用于功能测试。真实传感器对接需后续开发。

2. **IP地址**：服务器需使用固定IP地址，避免重启后IP变化导致APP无法连接。

3. **时间同步**：服务器和手机建议保持NTP时间同步，避免历史数据时间显示异常。

---

## 🔧 六、故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| APP显示"连接失败" | 服务器未启动 | 确认服务器程序已运行 |
| | IP地址错误 | 检查APP中的服务器地址 |
| | 防火墙拦截 | 开放8080端口 |
| | 网络不通 | ping服务器IP测试 |
| 健康检查正常但数据加载失败 | API路径问题 | 重启APP或检查设置 |
| 数据为0或为空 | 虚拟数据未生成 | 联系技术支持 |

**快速诊断命令**：

```bash
# 在手机浏览器或电脑访问：
http://服务器IP:8080/health

# 应该返回：
{"status":"healthy","service":"fishfarm-api"}
```

```bash
# 获取设备列表：
curl http://服务器IP:8080/api/devices

# 获取传感器数据：
curl http://服务器IP:8080/api/sensor-data
```

---

## 📞 七、技术支持

如遇到问题，请提供：

1. 服务器IP和端口
2. APP截图或错误信息
3. 服务器端日志（若有）

---

## 📋 八、当前版本功能清单

| 模块 | 功能 | 状态 |
|------|------|------|
| 仪表盘 | 设备列表展示 | ✅ |
| 仪表盘 | 实时传感器数据 | ✅ |
| 仪表盘 | 数据可视化图表 | ✅ |
| 历史 | 历史数据查询 | ✅ |
| 预警 | 预警规则配置 | ✅ |
| 预警 | 预警记录（危险/警告/提醒） | ✅ |
| 预警 | 预警处理 | ✅ |
| 生产 | 生产记录管理 | ✅ |
| 提醒 | 提醒列表 | ✅ |
| 设置 | 服务器地址配置 | ✅ |

---

## 🔄 九、版本更新说明

### 9.1 版本号规则

系统采用以下版本号格式：

| 格式 | 说明 | 示例 |
|------|------|------|
| `VERSION_NAME` | 主版本号 | 1.0.1 |
| `BUILD_NUMBER` | 构建号（递增） | 3 |
| `完整版本` | NAME+BUILD | 1.0.1+3 |

### 9.2 APK命名规则

构建出的APK文件名格式为：`fishfarm_monitor_v{完整版本}.apk`

示例：
- `fishfarm_monitor_v1.0.1+3.apk`

### 9.3 版本更新流程

当需要发布新版本时：

```bash
# 1. 进入项目目录
cd /path/to/fishfarm-system

# 2. 递增构建号（自动更新VERSION文件）
./version.sh increment

# 3. 构建新APK
cd app && ./build_apk.sh

# 4. 新APK会输出到 docs/ 目录
```

### 9.4 版本管理文件

- `VERSION` - 版本配置主文件
- `version.sh` - 版本管理脚本

---

*本文档由旺财助手生成 | 2026-04-24*
