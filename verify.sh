#!/bin/bash

echo "======================================"
echo "  智能渔场系统 - 快速验证脚本"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Docker是否安装
echo -e "${YELLOW}📋 检查Docker安装...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ 错误：未检测到Docker${NC}"
    echo "请先安装 Docker 和 Docker Compose"
    exit 1
fi
echo -e "${GREEN}✅ Docker已安装${NC}"
echo ""

# 检查项目目录
echo -e "${YELLOW}📋 检查项目目录...${NC}"
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ 错误：未找到docker-compose.yml${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 项目目录检查通过${NC}"
echo ""

# 创建.env文件
echo -e "${YELLOW}📋 创建配置文件...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env文件已创建${NC}"
else
    echo -e "${YELLOW}⚠️  .env文件已存在${NC}"
fi
echo ""

# 创建日志目录
echo -e "${YELLOW}📋 创建日志目录...${NC}"
mkdir -p backend/logs
mkdir -p backups
echo -e "${GREEN}✅ 日志目录已创建${NC}"
echo ""

# 启动服务
echo -e "${YELLOW}🚀 启动Docker服务...${NC}"
docker-compose up -d

echo ""
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 15

# 检查服务状态
echo ""
echo -e "${YELLOW}📊 检查服务状态...${NC}"
docker-compose ps

echo ""
echo -e "${YELLOW}🔍 测试API接口...${NC}"

# 测试健康检查
echo -e "  • 健康检查: ",
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
else
    echo -e "${RED}❌ 失败${NC}"
fi

# 测试设备列表
echo -e "  • 设备列表: ",
if curl -s http://localhost:8000/api/devices/list > /dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
else
    echo -e "${RED}❌ 失败${NC}"
fi

# 测试传感器数据
echo -e "  • 传感器数据: ",
if curl -s http://localhost:8000/api/sensor/latest > /dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
else
    echo -e "${RED}❌ 失败${NC}"
fi

echo ""
echo -e "${YELLOW}🔍 查看后端日志...${NC}"
docker-compose logs --tail=30 backend

echo ""
echo "======================================"
echo -e "${GREEN}✅ 验证完成！${NC}"
echo ""
echo "访问地址："
echo "  • API文档: http://localhost:8000/docs"
echo "  • 健康检查: http://localhost:8000/health"
echo "  • 设备列表: http://localhost:8000/api/devices/list"
echo ""
echo "常用命令："
echo "  • 查看日志: docker-compose logs -f"
echo "  • 停止服务: docker-compose down"
echo "  • 重启服务: docker-compose restart"
echo "======================================"
