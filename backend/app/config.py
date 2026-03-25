"""
配置文件
包含所有系统配置参数
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """系统配置类"""

    # 应用基本信息
    APP_NAME: str = "智能渔场环境控制监测系统"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # development, production

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # 数据库配置（使用 SQLite）
    DATABASE_URL: str = "sqlite:///./fishfarm.db"
    DATABASE_ECHO: bool = False  # 是否打印SQL语句（调试用）

    # Redis配置（暂时禁用）
    REDIS_URL: str = ""  # redis://localhost:6379/0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # MQTT配置
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    MQTT_TOPIC_PREFIX: str = "fishfarm"

    # 数据保留配置
    REALTIME_DATA_RETENTION_DAYS: int = 7  # 实时数据保留7天
    HISTORY_DATA_RETENTION_DAYS: int = 365  # 历史数据保留1年

    # 预警配置
    DEFAULT_ALARM_LEVEL: str = "提醒"  # 默认预警级别
    NOTIFICATION_METHODS: list = ["推送", "短信", "电话"]  # 预警通知方式

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "30 days"

    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".pdf"]

    # CORS配置
    CORS_ORIGINS: list = ["*"]

    # 时区配置
    TIMEZONE: str = "Asia/Shanghai"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 导出配置实例
settings = get_settings()
