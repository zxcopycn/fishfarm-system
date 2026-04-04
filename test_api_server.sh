#!/bin/bash
# API服务器测试脚本

echo "🐟 渔场系统API测试"
echo "========================="

BASE_URL="http://localhost:8000"

# 测试端点列表
declare -a test_endpoints=(
    "GET /"
    "GET /health"
    "GET /api/devices"
    "GET /api/sensor-data"
    "GET /api/alarms"
    "GET /api/production-records"
    "GET /api/reminders"
    "POST /api/reminders"
)

echo "📍 测试API服务器: $BASE_URL"
echo "⏰ 测试时间: $(date)"
echo ""

# 测试每个端点
for endpoint in "${test_endpoints[@]}"; do
    method=$(echo $endpoint | awk '{print $1}')
    path=$(echo $endpoint | awk '{print $2}')
    
    echo "🔄 测试: $method $path"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "HTTP:%{http_code}" -o /tmp/api_response.json "$BASE_URL$path")
        http_code=$(echo "$response" | grep -o "HTTP:[0-9]*" | cut -d: -f2)
        
        if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
            echo "✅ 成功 ($http_code)"
            if [ "$path" = "/" ] || [ "$path" = "/health" ]; then
                cat /tmp/api_response.json | jq '.' 2>/dev/null || cat /tmp/api_response.json
            else
                cat /tmp/api_response.json | jq '.data[0]' 2>/dev/null || echo "数据格式正常"
            fi
        else
            echo "❌ 失败 ($http_code)"
        fi
    elif [ "$method" = "POST" ]; then
        # 测试POST请求
        echo "   发送测试数据..."
        response=$(curl -s -w "HTTP:%{http_code}" -o /tmp/api_response.json \
            -H "Content-Type: application/json" \
            -d '{"title":"测试提醒","content":"这是一个测试提醒","remindTime":"2026-03-30T10:00:00"}' \
            "$BASE$path")
        http_code=$(echo "$response" | grep -o "HTTP:[0-9]*" | cut -d: -f2)
        
        if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
            echo "✅ 成功 ($http_code)"
        else
            echo "❌ 失败 ($http_code)"
        fi
    fi
    
    echo ""
done

echo "📊 测试总结"
echo "============"
echo "✅ 如果所有测试都通过，说明API服务器正常运行"
echo "❌ 如果有测试失败，请检查API服务器状态"
echo ""
echo "🔧 故障排除建议:"
echo "1. 确保API服务器正在运行: python3 simple_api_server.py"
echo "2. 检查端口8000是否被占用"
echo "3. 验证网络连接"
echo ""
echo "📱 测试移动应用:"
echo "1. 重新构建APK: ./build_apk.sh"
echo "2. 安装新版本的APK"
echo "3. 测试仪表盘和各个模块功能"