# 渔场系统自动构建APK指南

## 🚀 快速开始

### 步骤1：初始化Git仓库（如果还没有）
```bash
cd /home/node/.openclaw/workspace/fishfarm-system
git init
git add .
git commit -m "初始化渔场系统项目"
```

### 步骤2：创建GitHub仓库
1. 访问 https://github.com/new
2. 创建新仓库，例如：`fishfarm-monitor`
3. 不要勾选"Add a README file"

### 步骤3：推送代码到GitHub
```bash
cd /home/node/.openclaw/workspace/fishfarm-system
git remote add origin https://github.com/你的用户名/fishfarm-monitor.git
git branch -M main
git push -u origin main
```

### 步骤4：触发自动构建
推送代码后，GitHub Actions会自动开始构建。

或者手动触发：
1. 进入仓库页面
2. 点击"Actions"标签
3. 选择"Build Flutter APK"
4. 点击"Run workflow"

---

## 📥 下载APK

构建完成后：

1. 进入仓库的 **Actions** 页面
2. 点击最新的workflow运行记录
3. 滚动到底部 **Artifacts** 区域
4. 点击 `fishfarm-app-release` 下载APK

---

## 📱 安装APK

### Android手机
1. 下载APK文件
2. 允许"安装未知来源应用"
3. 点击APK安装

### HarmonyOS 4.x手机
1. 直接安装APK（兼容模式）
2. 体验与Android一致

---

## 📊 构建状态

- ✅ Flutter SDK: 3.24.5
- ✅ Android SDK: 自动配置
- ✅ 构建类型: Release（优化版）
- ✅ 签名: Debug签名（测试用）

---

## ⏱️ 预计时间

- 首次构建：约10-15分钟
- 后续构建：约5-10分钟

---

## 🔧 修改API地址

如需修改后端地址，编辑 `fishfarm_app/lib/services/api_service.dart`：

```dart
// 修改为您的服务器地址
const String baseUrl = "http://您的服务器IP:8000";
```

然后重新推送代码触发构建。

---

## 📞 需要帮助？

如果构建失败，请检查：
1. Flutter项目结构是否正确
2. pubspec.yaml配置是否完整
3. Actions日志查看具体错误

---

**创建时间**: 2026-03-25
**状态**: ✅ 配置完成，等待推送到GitHub