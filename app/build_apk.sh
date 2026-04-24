#!/bin/bash
# 重新构建APK
# 使用统一版本管理

SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 加载版本管理
source "$PROJECT_ROOT/version.sh"

echo "======================================"
echo "  智能渔场监测系统 - APK构建"
echo "  版本: v$(./version.sh show)"
echo "======================================"
echo ""

# 检查Flutter环境
if ! command -v flutter &> /dev/null; then
    echo "Flutter未安装"
    exit 1
fi

cd "$PROJECT_ROOT/app"

# 同步版本到pubspec.yaml
echo "📝 同步版本到 pubspec.yaml..."
sed -i "s/^version: .*/version: ${APK_VERSION}+${APK_BUILD}/" pubspec.yaml
echo "   pubspec.yaml: ${APK_VERSION}+${APK_BUILD}"

flutter clean
flutter pub get
flutter build apk --release

if [ $? -eq 0 ]; then
    # 重命名为带版本号的文件
    SRC_APK="build/app/outputs/flutter-apk/app-release.apk"
    DEST_APK="build/app/outputs/flutter-apk/fishfarm_monitor_v${VERSION}.apk"
    
    cp "$SRC_APK" "$DEST_APK"
    cp "$DEST_APK" "$PROJECT_ROOT/docs/fishfarm_monitor_v${VERSION}.apk"
    
    echo ""
    echo "======================================"
    echo "✅ APK构建成功！"
    echo "======================================"
    echo "📦 版本: v${VERSION}"
    echo "📁 APK位置:"
    ls -lh "$DEST_APK"
    echo ""
    echo "📋 同步更新:"
    echo "   - pubspec.yaml → ${APK_VERSION}+${APK_BUILD}"
    echo "   - docs/ → fishfarm_monitor_v${VERSION}.apk"
    echo ""
    echo "💡 提示: 如需递增构建号，运行: ./version.sh increment"
else
    echo "❌ APK构建失败"
fi
