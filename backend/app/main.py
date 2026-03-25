"""
智能渔场系统主应用
FastAPI应用入口
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from loguru import logger
from app.config import settings
from app.database import init_database, engine, get_db
from app.api import router as api_router
from app.websocket import manager, send_sensor_update, send_device_status_update, send_alarm_alert

# 配置日志
logger.remove()
logger.add(
    settings.LOG_FILE,
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)
logger.add(
    print,
    level=settings.LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

# 设置传感器数据WebSocket推送回调
from app.services.sensor_service import setup_sensor_websocket_callback
setup_sensor_websocket_callback()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info(f"正在启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"运行环境: {settings.APP_ENV}")

    # 初始化数据库
    init_database()

    # 初始化MQTT客户端
    from app.utils.mqtt_client import init_mqtt_client
    mqtt_client = init_mqtt_client()
    if mqtt_client.is_connected():
        logger.info("MQTT客户端已连接")
    else:
        logger.warning("MQTT客户端未连接")

    yield

    # 关闭时执行
    logger.info("正在关闭应用")
    mqtt_client.disconnect()
    logger.info("应用已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="智能渔场环境控制监测系统 - 实时监测、自动控制、智能预警",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api")

# 注册WebSocket路由
from app.websocket import router as websocket_router
app.include_router(websocket_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else None
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": settings.APP_NAME}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return {
        "status": "error",
        "message": "服务器内部错误",
        "detail": str(exc) if settings.DEBUG else "请稍后再试"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
