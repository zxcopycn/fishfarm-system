"""
完善的日志系统配置
支持日志分级、轮转、压缩等功能
"""
from loguru import logger
import sys
import os
from datetime import datetime
from app.config import settings


def setup_logging():
    """
    配置日志系统

    功能：
    1. 控制台日志（仅ERROR及以上）
    2. 详细日志（每天轮转）
    3. 错误日志（独立文件，保留90天）
    4. 传感器数据日志（按文件大小轮转，保留7天）
    """
    # 移除默认handler
    logger.remove()

    # 1. 控制台日志（仅ERROR及以上）
    logger.add(
        sys.stderr,
        format="<red>{level}</red> | {time:YYYY-MM-DD HH:mm:ss} | {name}:{function}:{line} | {message}",
        level="ERROR",
        colorize=True
    )

    # 2. 详细日志（每天轮转，保留30天）
    logger.add(
        "logs/debug_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        encoding="utf-8"
    )

    # 3. 错误日志（独立文件，保留90天）
    logger.add(
        "logs/error_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="90 days",
        compression="zip",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        encoding="utf-8"
    )

    # 4. 传感器数据日志（按文件大小轮转，保留7天）
    logger.add(
        "logs/sensor_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        encoding="utf-8"
    )

    # 5. WebSocket日志
    logger.add(
        "logs/websocket_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        encoding="utf-8"
    )

    # 6. MQTT日志
    logger.add(
        "logs/mqtt_{time:YYYY-MM-DD}.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        encoding="utf-8"
    )

    logger.info("日志系统初始化完成")


def get_logger(name: str = None):
    """
    获取logger实例

    参数:
        name: logger名称（通常是模块名）

    返回:
        logger: loguru logger实例
    """
    return logger.bind(name=name)


# 日志装饰器 - 记录函数调用
def log_function_call(logger_instance):
    """
    函数调用日志装饰器

    参数:
        logger_instance: logger实例
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            logger_instance.info(f"调用函数: {func.__name__} | 参数: {args}, {kwargs}")
            try:
                result = await func(*args, **kwargs)
                logger_instance.info(f"函数执行成功: {func.__name__} | 返回值: {result}")
                return result
            except Exception as e:
                logger_instance.error(f"函数执行失败: {func.__name__} | 错误: {e}", exc_info=True)
                raise
        return async_wrapper
    return decorator


def log_function_call_sync(logger_instance):
    """
    同步函数调用日志装饰器

    参数:
        logger_instance: logger实例
    """
    def decorator(func):
        def sync_wrapper(*args, **kwargs):
            logger_instance.info(f"调用函数: {func.__name__} | 参数: {args}, {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger_instance.info(f"函数执行成功: {func.__name__} | 返回值: {result}")
                return result
            except Exception as e:
                logger_instance.error(f"函数执行失败: {func.__name__} | 错误: {e}", exc_info=True)
                raise
        return sync_wrapper
    return decorator


# 添加系统信息日志
logger.info("=" * 60)
logger.info("系统启动")
logger.info(f"应用名称: {settings.APP_NAME}")
logger.info(f"应用版本: {settings.APP_VERSION}")
logger.info(f"运行环境: {settings.APP_ENV}")
logger.info(f"API版本: v{settings.API_VERSION}")
logger.info(f"数据库: MySQL")
logger.info(f"调试模式: {settings.DEBUG}")
logger.info("=" * 60)
