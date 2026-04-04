"""
Redis缓存服务
提供缓存功能，提高系统性能
"""
import json
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError
from app.config import settings
from app.utils.logger import logger

class CacheService:
    """缓存服务类"""
    
    def __init__(self):
        """初始化Redis连接"""
        self.redis: Optional[Redis] = None
        self.connected = False
    
    async def connect(self):
        """连接Redis服务器"""
        try:
            self.redis = Redis(
                host=settings.REDIS_URL.split('://')[1].split(':')[0] if '://' in settings.REDIS_URL else 'localhost',
                port=int(settings.REDIS_URL.split(':')[-1].split('/')[0]) if ':' in settings.REDIS_URL else 6379,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                encoding='utf-8'
            )
            
            # 测试连接
            await self.redis.ping()
            self.connected = True
            logger.info("Redis缓存连接成功")
            return True
            
        except ConnectionError as e:
            logger.error(f"Redis连接失败: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Redis连接异常: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """断开Redis连接"""
        if self.redis:
            await self.redis.close()
            self.connected = False
            logger.info("Redis连接已断开")
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.connected or not self.redis:
            return None
            
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except (json.JSONDecodeError, RedisError) as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存值"""
        if not self.connected or not self.redis:
            return False
            
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            result = await self.redis.set(key, json_value, ex=expire)
            return bool(result)
        except (TypeError, RedisError) as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.connected or not self.redis:
            return False
            
        try:
            result = await self.redis.delete(key)
            return result > 0
        except RedisError as e:
            logger.error(f"删除缓存失败 {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.connected or not self.redis:
            return False
            
        try:
            result = await self.redis.exists(key)
            return result > 0
        except RedisError as e:
            logger.error(f"检查缓存存在性失败 {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        if not self.connected or not self.redis:
            return False
            
        try:
            result = await self.redis.expire(key, seconds)
            return result
        except RedisError as e:
            logger.error(f"设置缓存过期时间失败 {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> Optional[int]:
        """获取剩余过期时间"""
        if not self.connected or not self.redis:
            return None
            
        try:
            return await self.redis.ttl(key)
        except RedisError as e:
            logger.error(f"获取缓存TTL失败 {key}: {e}")
            return None
    
    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的键"""
        if not self.connected or not self.redis:
            return 0
            
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"清除匹配键 {pattern}: {len(keys)} 个, 删除 {deleted} 个")
                return deleted
            return 0
        except RedisError as e:
            logger.error(f"清除匹配键失败 {pattern}: {e}")
            return 0


# 创建全局缓存服务实例
cache_service = CacheService()


# 缓存装饰器
def cache_result(key_prefix: str, expire: int = 300, clear_on_error: bool = True):
    """
    缓存装饰器
    
    参数:
        key_prefix: 缓存键前缀
        expire: 过期时间（秒）
        clear_on_error: 出错时是否清除缓存
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            key = f"{key_prefix}:{func.__name__}"
            
            # 尝试从缓存获取
            cached_result = await cache_service.get(key)
            if cached_result is not None:
                logger.debug(f"缓存命中: {key}")
                return cached_result
            
            logger.debug(f"缓存未命中: {key}")
            
            # 执行函数
            try:
                result = await func(*args, **kwargs)
                
                # 缓存结果
                await cache_service.set(key, result, expire)
                logger.debug(f"已缓存结果: {key}")
                
                return result
            except Exception as e:
                # 出错时清除缓存（可选）
                if clear_on_error:
                    await cache_service.delete(key)
                    logger.warning(f"函数执行出错，已清除缓存: {key}")
                raise
        
        return wrapper
    return decorator


# 缓存失效装饰器
def invalidate_cache(key_prefix: str):
    """
    缓存失效装饰器
    当函数执行成功时，清除相关缓存
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # 清除相关缓存
            await cache_service.clear_pattern(f"{key_prefix}*")
            logger.info(f"已清除相关缓存: {key_prefix}*")
            
            return result
        return wrapper
    return decorator


# 使用示例：
# 
# @cache_result("device_config", expire=600)
# async def get_device_config(device_id: int):
#     # 从数据库获取配置
#     pass
#
# @invalidate_cache("device_config")
# async def update_device_config(device_id: int, config: dict):
#     # 更新配置
#     pass
