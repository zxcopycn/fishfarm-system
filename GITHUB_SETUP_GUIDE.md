# GitHub 项目设置指南

## 📧 您的信息
- 邮箱：zx@lanbe.com

## 🚀 步骤 1：创建 GitHub 账号（如果还没有）

1. 访问 https://github.com/signup
2. 使用邮箱 `zx@lanbe.com` 注册
3. 设置用户名（建议：`lanbe` 或 `zx-lanbe`）
4. 验证邮箱

## 🚀 步骤 2：创建新仓库

1. 登录 GitHub
2. 点击右上角 **+** → **New repository**
3. 填写信息：
   - **Repository name**: `fishfarm-system`
   - **Description**: `渔场智能监控系统 - IoT Monitoring System`
   - **Public** ✅（免费使用 GitHub Actions）
   - **不要勾选** "Add a README file"
4. 点击 **Create repository**

## 🚀 步骤 3：获取 Personal Access Token

### 3.1 创建 Token
1. 登录 GitHub
2. 点击右上角头像 → **Settings**
3. 左侧菜单最下方 → **Developer settings**
4. 点击 **Personal access tokens** → **Tokens (classic)**
5. 点击 **Generate new token** → **Generate new token (classic)**
6. 填写：
   - **Note**: `OpenClaw FishFarm Build`
   - **Expiration**: `90 days` 或 `No expiration`
   - **Select scopes**: 勾选以下权限：
     - ✅ `repo`（完整仓库访问）
     - ✅ `workflow`（更新 GitHub Actions）
     - ✅ `write:packages`（上传构建产物）
7. 点击 **Generate token**
8. **⚠️ 立即复制 token**（只显示一次！）

### 3.2 保存 Token
将 token 告诉我，我会帮您配置本地 Git。

## 🚀 步骤 4：启用 GitHub Actions

1. 进入仓库页面
2. 点击 **Settings** 标签
3. 左侧菜单 → **Actions** → **General**
4. 在 **Actions permissions** 选择：
   - ✅ **Allow all actions and reusable workflows**
5. 点击 **Save**

## 📦 自动构建流程

完成上述步骤后，我会：
1. 配置本地 Git（使用您的邮箱）
2. 提交所有代码
3. 推送到 GitHub
4. 自动触发 GitHub Actions 构建
5. 构建完成后通知您下载 APK

## ⚙️ 构建产物位置

- **APK 文件**: `build/app/outputs/flutter-apk/app-release.apk`
- **下载位置**: GitHub Releases 页面
- **文件大小**: 约 30-50MB
- **支持架构**: ARM64（现代 Android 手机）

## 🔧 故障排除

### 如果构建失败
1. 检查 Actions 标签页查看错误日志
2. 常见问题：
   - Flutter 版本不匹配 → 修改 `.github/workflows/build-apk.yml` 中的 Flutter 版本
   - 依赖下载超时 → 重新运行构建

### 如果需要重新构建
- 推送新代码到 `master` 分支会自动触发
- 或在 Actions 页面点击 **Re-run all jobs**

---

## 📝 需要提供的信息

请告诉我：
1. **GitHub 用户名**（如果已有账号）
2. **Personal Access Token**（创建后复制给我）

我会立即为您配置并开始自动构建！
