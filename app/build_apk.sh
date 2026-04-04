#!/bin/bash
# 重新构建APK

echo "开始构建APK..."

# 检查Flutter环境
if ! command -v flutter &> /dev/null; then
    echo "Flutter未安装"
    exit 1
fi

flutter clean
flutter pub get
flutter build apk --release

if [ $? -eq 0 ]; then
    echo "✅ APK构建成功！"
    ls -lh build/app/outputs/flutter-apk/app-release.apk
else
    echo "❌ APK构建失败"
fi
