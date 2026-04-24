#!/bin/bash
# 版本管理脚本
# 用法: source version.sh (在other scripts中使用)

VERSION_FILE="$(dirname "$0")/VERSION"

if [ ! -f "$VERSION_FILE" ]; then
    echo "❌ 错误: VERSION文件不存在: $VERSION_FILE"
    exit 1
fi

source "$VERSION_FILE"

# 递增构建号并更新VERSION文件
increment_build() {
    BUILD_NUMBER=$((BUILD_NUMBER + 1))
    VERSION=${VERSION_NAME}+${BUILD_NUMBER}
    APK_BUILD=${BUILD_NUMBER}
    
    cat > "$VERSION_FILE" << EOF
# 渔场系统版本管理
# 格式: VERSION_NAME+BUILD_NUMBER
# 示例: 1.0.2+3

# 主版本号.次版本号.修订号
VERSION_NAME=${VERSION_NAME}

# 构建号 (每次构建递增)
BUILD_NUMBER=${BUILD_NUMBER}

# 完整版本字符串
VERSION=${VERSION}

# APK版本 (Android显示用，通常是 VERSION_NAME)
APK_VERSION=${VERSION_NAME}

# APK构建号 (Android显示用，通常是 BUILD_NUMBER)
APK_BUILD=${BUILD_NUMBER}
EOF
    echo "✅ 版本号已更新: v${VERSION}"
}

# 显示当前版本
show_version() {
    echo "v${VERSION}"
}

# 获取版本信息
get_version() {
    echo "$VERSION"
}

get_version_name() {
    echo "$VERSION_NAME"
}

get_build_number() {
    echo "$BUILD_NUMBER"
}

# 根据参数执行相应操作
case "${1:-show}" in
    increment)
        increment_build
        ;;
    show)
        show_version
        ;;
    version)
        get_version
        ;;
    name)
        get_version_name
        ;;
    build)
        get_build_number
        ;;
    *)
        echo "用法: $0 {show|increment|version|name|build}"
        exit 1
        ;;
esac
