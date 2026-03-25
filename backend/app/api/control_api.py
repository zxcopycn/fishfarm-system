"""
设备控制API
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List
from typing import Optional
from app.database import get_db
from app.models import ControlDevice, ControlRecord
from app.utils import format_datetime, get_time_ago_string
from pydantic import BaseModel

router = APIRouter()


class ControlDeviceResponse(BaseModel):
    """控制设备响应模型"""
    id: int
    device_name: str
    device_type: str
    location: str
    status: int
    mqtt_topic: str
    current_power: float
    created_at: str

    class Config:
        from_attributes = True


class ControlRecordResponse(BaseModel):
    """控制记录响应模型"""
    id: int
    device_id: int
    device_name: str
    action: str
    target_value: float
    actual_value: float
    operator: str
    remark: str
    created_at: str
    time_ago: str

    class Config:
        from_attributes = True


class ControlRequest(BaseModel):
    """控制请求模型"""
    action: str = Body(..., description="操作类型：开启/关闭/调节")
    target_value: float = Body(None, description="目标数值")
    remark: str = Body("", description="备注")


@router.get("/devices", response_model=List[ControlDeviceResponse])
def get_control_devices(
    status: Optional[int] = Query(None, description="按状态筛选：1-开启 0-关闭"),
    db: Session = Depends(get_db)
):
    """
    获取控制设备列表

    参数:
        status: 按状态筛选（可选）

    返回:
        控制设备列表
    """
    query = db.query(ControlDevice)

    if status is not None:
        query = query.filter(ControlDevice.status == status)

    devices = query.order_by(ControlDevice.device_name).all()

    return [ControlDeviceResponse(
        id=device.id,
        device_name=device.device_name,
        device_type=device.device_type,
        location=device.location or "",
        status=device.status,
        mqtt_topic=device.mqtt_topic or "",
        current_power=float(device.current_power) if device.current_power else 0,
        created_at=format_datetime(device.created_at)
    ) for device in devices]


@router.post("/{device_id}/control")
def control_device(
    device_id: int,
    request: ControlRequest,
    operator: str = "admin",
    db: Session = Depends(get_db)
):
    """
    控制设备（开启/关闭/调节）

    参数:
        device_id: 设备ID
        request: 控制请求
        operator: 操作人

    返回:
        控制结果
    """
    device = db.query(ControlDevice).filter(ControlDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="控制设备不存在")

    # 更新设备状态
    action = request.action
    actual_value = request.target_value

    if action == "开启":
        device.status = 1
        actual_value = 1.0
    elif action == "关闭":
        device.status = 0
        actual_value = 0.0
    elif action == "调节":
        # 调节功率
        device.status = 1
        if actual_value is None:
            actual_value = device.current_power
    else:
        raise HTTPException(status_code=400, detail="操作类型错误")

    # 保存当前功率
    device.current_power = actual_value

    # 创建控制记录
    record = ControlRecord(
        device_id=device_id,
        action=action,
        target_value=request.target_value,
        actual_value=actual_value,
        operator=operator,
        remark=request.remark
    )
    db.add(record)

    db.commit()

    return {
        "status": "success",
        "message": f"设备{device.device_name}已{action}",
        "device_id": device_id,
        "device_name": device.device_name,
        "action": action,
        "status": device.status,
        "current_power": float(device.current_power)
    }


@router.get("/records", response_model=List[ControlRecordResponse])
def get_control_records(
    device_id: Optional[int] = Query(None, description="设备ID"),
    limit: int = Query(50, ge=1, le=100, description="返回条数"),
    db: Session = Depends(get_db)
):
    """
    获取设备控制记录

    参数:
        device_id: 设备ID（可选）
        limit: 返回条数，默认50条

    返回:
        控制记录列表
    """
    query = db.query(ControlDevice, ControlRecord).join(
        ControlRecord, ControlDevice.id == ControlRecord.device_id
    )

    if device_id:
        query = query.filter(ControlRecord.device_id == device_id)

    records = query.order_by(ControlRecord.created_at.desc()).limit(limit).all()

    results = []
    for device, record in records:
        results.append(ControlRecordResponse(
            id=record.id,
            device_id=record.device_id,
            device_name=device.device_name,
            action=record.action,
            target_value=float(record.target_value) if record.target_value else 0,
            actual_value=float(record.actual_value) if record.actual_value else 0,
            operator=record.operator or "系统",
            remark=record.remark or "",
            created_at=format_datetime(record.created_at),
            time_ago=get_time_ago_string(record.created_at)
        ))

    return results
