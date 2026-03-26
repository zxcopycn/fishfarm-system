#!/bin/bash

echo "======================================"
echo "  Flutter应用 - 快速启动脚本"
echo "======================================"
echo ""

# 检查Flutter是否安装
if ! command -v flutter &> /dev/null; then
    echo "❌ 错误：未检测到Flutter"
    echo "请先安装 Flutter SDK"
    echo "下载地址: https://flutter.dev/docs/get-started/install"
    exit 1
fi

# 进入Flutter项目目录
cd /home/node/.openclaw/workspace/fishfarm-system/flutter

echo "📦 检查依赖..."
flutter pub get

echo ""
echo "🚀 启动应用..."

# 模拟器启动（MacOS）
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📱 检查模拟器..."
    flutter devices
    echo ""
    echo "请在模拟器中选择设备"
    echo "然后按回车继续..."
    read
fi

# 启动应用
flutter run

echo ""
echo "======================================"
echo "按 q 退出应用"
echo "======================================"
