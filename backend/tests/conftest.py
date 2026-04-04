"""
测试配置模块
"""
import pytest
import sys
import os
from typing import Generator

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# 测试数据库URL（使用SQLite进行测试）
TEST_DATABASE_URL = "sqlite:///./test_fishfarm.db"

# 测试Redis URL（使用Redis进行测试）
TEST_REDIS_URL = "redis://localhost:6379/1"


@pytest.fixture(scope="session")
def test_settings() -> Generator:
    """测试配置fixture"""
    # 保存原始配置
    original_db_url = settings.DATABASE_URL
    original_redis_url = settings.REDIS_URL
    original_debug = settings.DEBUG
    
    # 设置测试配置
    settings.DATABASE_URL = TEST_DATABASE_URL
    settings.REDIS_URL = TEST_REDIS_URL
    settings.DEBUG = True
    
    yield settings
    
    # 恢复原始配置
    settings.DATABASE_URL = original_db_url
    settings.REDIS_URL = original_redis_url
    settings.DEBUG = original_debug


@pytest.fixture
def db_session(test_settings) -> Generator:
    """测试数据库会话"""
    # 在实际应用中，应该使用测试数据库
    # 这里为了简化，直接返回None
    yield None