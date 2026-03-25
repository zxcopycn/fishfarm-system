# 渔场系统移动端APP构建指南

## 📱 快速构建Android APK

### 前置要求
- Flutter SDK 3.24.5+
- Android SDK（API 21+）
- Java JDK 11+

---

## 🚀 构建步骤

### 方法一：在有Android环境的机器上构建

#### 1. 安装Flutter和Android SDK
```bash
# 下载Flutter SDK
git clone https://github.com/flutter/flutter.git -b stable
export PATH="$PATH:`pwd`/flutter/bin"

# 安装Android Studio或单独安装Android SDK
# 下载地址：https://developer.android.com/studio
```

#### 2. 克隆项目
```bash
cd /path/to/fishfarm-system/fishfarm_app
flutter pub get
```

#### 3. 构建APK
```bash
# 调试版APK（快速构建）
flutter build apk --debug

# 发布版APK（优化性能）
flutter build apk --release
```

#### 4. APK位置
构建完成后，APK文件位于：
```
build/app/outputs/flutter-apk/app-release.apk
```

---

### 方法二：使用GitHub Actions自动构建

创建 `.github/workflows/build.yml`：

```yaml
name: Build Flutter APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Flutter
      uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.24.5'
    
    - name: Install dependencies
      run: |
        cd fishfarm_app
        flutter pub get
    
    - name: Build APK
      run: |
        cd fishfarm_app
        flutter build apk --release
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: app-release.apk
        path: fishfarm_app/build/app/outputs/flutter-apk/app-release.apk
```

---

### 方法三：使用Codemagic云构建

1. 访问 https://codemagic.io
2. 连接GitHub仓库
3. 选择Flutter项目
4. 自动构建并下载APK

---

## 🔧 配置修改

### 修改API地址
编辑 `lib/services/api_service.dart`：

```dart
// 本地开发
const String baseUrl = "http://192.168.1.200:8000";

// 生产环境（需要修改为实际服务器地址）
const String baseUrl = "https://your-domain.com";
```

### 修改应用名称和图标
编辑 `android/app/src/main/AndroidManifest.xml`：
```xml
<application
    android:label="渔场监控"
    android:icon="@mipmap/ic_launcher">
```

---

## 📋 构建检查清单

- [ ] Flutter环境已安装
- [ ] Android SDK已配置
- [ ] 项目依赖已下载 (`flutter pub get`)
- [ ] API地址已配置为生产环境地址
- [ ] 应用图标和名称已设置
- [ ] 构建APK (`flutter build apk --release`)
- [ ] APK测试通过

---

## 🔐 签名配置（发布版）

### 创建签名密钥
```bash
keytool -genkey -v -keystore fishfarm.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias fishfarm
```

### 配置签名
创建 `android/key.properties`：
```properties
storePassword=your_password
keyPassword=your_password
keyAlias=fishfarm
storeFile=../fishfarm.jks
```

---

## 📱 iOS版本（需要Mac）

```bash
# 构建iOS（需要Mac + Xcode）
flutter build ios --release

# 或使用Xcode打开项目
open ios/Runner.xcworkspace
```

---

## 🎯 当前项目状态

- ✅ Flutter代码完整（10个页面）
- ✅ API集成测试通过（6/6）
- ✅ 所有依赖已配置
- ⚠️ 需要Android环境构建APK

---

## 💡 推荐

如果当前机器没有Android环境，建议：

1. **使用在线构建服务**：Codemagic、Bitrise
2. **在有环境的机器上构建**
3. **使用GitHub Actions自动构建**

需要我帮您配置自动构建流程吗？