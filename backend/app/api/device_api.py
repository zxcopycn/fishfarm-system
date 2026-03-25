"""
设备管理API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Device, DeviceType
from pydantic import BaseModel

router = APIRouter()


class DeviceResponse(BaseModel):
    """设备响应模型"""
    id: int
    device_name: str
    device_type_id: int
    device_type_name: str
    location: str
    ip_address: str
    mqtt_topic: str
    status: int
    current_value: float

    class Config:
        from_attributes = True


@router.get("/list", response_model=List[DeviceResponse])
def get_device_list(
    device_type: Optional[str] = Query(None, description="按设备类型筛选"),
    status: Optional[int] = Query(None, description="按状态筛选：1-在线 0-离线"),
    db: Session = Depends(get_db)
):
    """
    获取设备列表

    参数:
        device_type: 按设备类型筛选（可选）
        status: 按状态筛选（可选）

    返回:
        设备列表
    """
    query = db.query(Device, DeviceType).join(
        DeviceType, Device.device_type_id == DeviceType.id
    )

    if device_type:
        query = query.filter(DeviceType.code == device_type)
    if status is not None:
        query = query.filter(Device.status == status)

    results = []
    for device, device_type in query:
        results.append(DeviceResponse(
            id=device.id,
            device_name=device.device_name,
            device_type_id=device.device_type_id,
            device_type_name=device_type.name,
            location=device.location or "",
            ip_address=device.ip_address or "",
            mqtt_topic=device.mqtt_topic or "",
            status=device.status,
            current_value=float(device.current_value) if device.current_value else 0
        ))

    return results


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(device_id: int, db: Session = Depends(get_db)):
    """
    获取单个设备详情

    参数:
        device_id: 设备ID

    返回:
        设备详情
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    device_type = db.query(DeviceType).filter(DeviceType.id == device.device_type_id).first()

    return DeviceResponse(
        id=device.id,
        device_name=device.device_name,
        device_type_id=device.device_type_id,
        device_type_name=device_type.name if device_type else "",
        location=device.location or "",
        ip_address=device.ip_address or "",
        mqtt_topic=device.mqtt_topic or "",
        status=device.status,
        current_value=float(device.current_value) if device.current_value else 0
    )


@router.patch("/{device_id}/status")
def update_device_status(
    device_id: int,
    status: int = Query(..., ge=0, le=1, description="设备状态：0-离线 1-在线"),
    db: Session = Depends(get_db)
):
    """
    更新设备状态

    参数:
        device_id: 设备ID
        status: 设备状态：0-离线 1-在线

    返回:
        更新结果
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    device.status = status
    db.commit()

    return {
        "status": "success",
        "message": f"设备状态已更新为：{'在线' if status == 1 else '离线'}",
        "device_id": device_id,
        "status": status
    }
