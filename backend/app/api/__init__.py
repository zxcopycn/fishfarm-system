"""
API路由模块
"""

from fastapi import APIRouter
from app.api import sensor_api, device_api, alarm_api, production_api, control_api, reminder_api

router = APIRouter()

# 注册子路由
router.include_router(sensor_api.router, prefix="/sensor", tags=["传感器"])
router.include_router(device_api.router, prefix="/devices", tags=["设备"])
router.include_router(alarm_api.router, prefix="/alarms", tags=["预警"])
router.include_router(production_api.router, prefix="/production", tags=["生产记录"])
router.include_router(control_api.router, prefix="/control", tags=["设备控制"])
router.include_router(reminder_api.router, prefix="/reminders", tags=["提醒"])
