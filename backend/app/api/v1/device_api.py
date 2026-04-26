"""
API版本1 - 设备相关API
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from loguru import logger
from pydantic import BaseModel
from decimal import Decimal

from app.database import get_db
from app.models.device import Device, DeviceType, ControlDevice
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/devices", tags=["v1设备"])


# Pydantic响应模型
class DeviceTypeResponse(BaseModel):
    """设备类型响应模型"""
    id: int
    name: str
    code: str
    status: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeviceResponse(BaseModel):
    """设备响应模型"""
    id: int
    device_name: str
    device_type_id: int
    location: Optional[str] = None
    ip_address: Optional[str] = None
    mqtt_topic: Optional[str] = None
    status: int
    current_value: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ControlDeviceResponse(BaseModel):
    """控制设备响应模型"""
    id: int
    device_name: str
    device_type: str
    location: Optional[str] = None
    status: int
    mqtt_topic: Optional[str] = None
    current_power: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("", response_model=List[DeviceResponse])
async def get_devices(
    device_type: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """获取设备列表"""
    try:
        query = db.query(Device)
        if device_type:
            query = query.filter(Device.device_type == device_type)
        if is_active is not None:
            query = query.filter(Device.status == 1 if is_active else 0)
        devices = query.all()
        return devices
    except Exception as e:
        logger.error(f"获取设备列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取设备列表失败: {str(e)}")


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    """获取指定设备详情"""
    try:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="设备不存在")
        return device
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取设备详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取设备详情失败: {str(e)}")


class DeviceUpdateRequest(BaseModel):
    """设备更新请求模型"""
    device_name: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None
    mqtt_topic: Optional[str] = None
    status: Optional[int] = None


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    update_data: DeviceUpdateRequest,
    db: Session = Depends(get_db)
):
    """更新设备信息（支持更新设备名称）"""
    try:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="设备不存在")

        # 更新非空字段
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None and hasattr(device, field):
                setattr(device, field, value)

        device.updated_at = datetime.now()
        db.commit()
        db.refresh(device)
        return device
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新设备失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新设备失败: {str(e)}")


@router.get("/types", response_model=List[DeviceTypeResponse])
async def get_device_types(db: Session = Depends(get_db)):
    """获取设备类型列表"""
    try:
        device_types = db.query(DeviceType).all()
        return device_types
    except Exception as e:
        logger.error(f"获取设备类型失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取设备类型失败: {str(e)}")


@router.get("/control", response_model=List[ControlDeviceResponse])
async def get_control_devices(
    status: int = None,
    db: Session = Depends(get_db)
):
    """获取可控制设备列表"""
    try:
        query = db.query(ControlDevice)
        if status is not None:
            query = query.filter(ControlDevice.status == status)
        devices = query.all()
        return devices
    except Exception as e:
        logger.error(f"获取控制设备列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取控制设备列表失败: {str(e)}")
