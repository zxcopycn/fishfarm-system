"""
传感器数据API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Device, SensorData, AlarmRecord
from app.utils import format_datetime, get_time_ago_string, validate_sensor_value
from pydantic import BaseModel

router = APIRouter()


class SensorDataResponse(BaseModel):
    """传感器数据响应模型"""
    id: int
    device_id: int
    device_name: str
    temperature: Optional[float]
    ph: Optional[float]
    ammonia: Optional[float]
    nitrite: Optional[float]
    oxygen: Optional[float]
    created_at: str
    time_ago: str

    class Config:
        from_attributes = True


class SensorDataListResponse(BaseModel):
    """传感器数据列表响应"""
    total: int
    data: List[SensorDataResponse]


@router.get("/latest", response_model=List[SensorDataResponse])
def get_latest_sensor_data(
    limit: int = Query(20, ge=1, le=100, description="返回数据条数"),
    db: Session = Depends(get_db)
):
    """
    获取最新的传感器数据

    参数:
        limit: 返回数据条数，默认20条

    返回:
        最新的传感器数据列表
    """
    query = db.query(Device, SensorData).join(
        SensorData, Device.id == SensorData.device_id
    ).order_by(
        SensorData.created_at.desc()
    ).limit(limit)

    results = []
    for device, sensor_data in query:
        results.append(SensorDataResponse(
            id=sensor_data.id,
            device_id=device.id,
            device_name=device.device_name,
            temperature=sensor_data.temperature,
            ph=sensor_data.ph,
            ammonia=sensor_data.ammonia,
            nitrite=sensor_data.nitrite,
            oxygen=sensor_data.oxygen,
            created_at=format_datetime(sensor_data.created_at),
            time_ago=get_time_ago_string(sensor_data.created_at)
        ))

    return results[::-1]  # 反转，按时间正序


@router.get("/device/{device_id}/history", response_model=List[SensorDataResponse])
def get_device_history(
    device_id: int,
    hours: int = Query(24, ge=1, le=720, description="查询小时数，默认24小时"),
    db: Session = Depends(get_db)
):
    """
    获取指定设备的传感器历史数据

    参数:
        device_id: 设备ID
        hours: 查询小时数，默认24小时

    返回:
        历史数据列表
    """
    # 检查设备是否存在
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    # 查询历史数据
    start_time = datetime.now() - timedelta(hours=hours)
    sensor_data_list = db.query(SensorData).filter(
        SensorData.device_id == device_id,
        SensorData.created_at >= start_time
    ).order_by(SensorData.created_at.asc()).all()

    results = []
    for sensor_data in sensor_data_list:
        results.append(SensorDataResponse(
            id=sensor_data.id,
            device_id=device.id,
            device_name=device.device_name,
            temperature=sensor_data.temperature,
            ph=sensor_data.ph,
            ammonia=sensor_data.ammonia,
            nitrite=sensor_data.nitrite,
            oxygen=sensor_data.oxygen,
            created_at=format_datetime(sensor_data.created_at),
            time_ago=get_time_ago_string(sensor_data.created_at)
        ))

    return results


@router.get("/statistics", response_model=dict)
def get_sensor_statistics(
    hours: int = Query(24, ge=1, le=720, description="查询小时数，默认24小时"),
    db: Session = Depends(get_db)
):
    """
    获取传感器统计数据

    参数:
        hours: 查询小时数，默认24小时

    返回:
        各项参数的平均值、最小值、最大值等统计信息
    """
    start_time = datetime.now() - timedelta(hours=hours)

    # 查询所有传感器数据
    sensor_data_list = db.query(SensorData).filter(
        SensorData.created_at >= start_time
    ).all()

    stats = {
        "count": len(sensor_data_list),
        "temperature": {
            "avg": sum(d.temperature for d in sensor_data_list if d.temperature) / len(sensor_data_list) if sensor_data_list else 0,
            "min": min((d.temperature for d in sensor_data_list if d.temperature), default=None),
            "max": max((d.temperature for d in sensor_data_list if d.temperature), default=None),
        },
        "ph": {
            "avg": sum(d.ph for d in sensor_data_list if d.ph) / len(sensor_data_list) if sensor_data_list else 0,
            "min": min((d.ph for d in sensor_data_list if d.ph), default=None),
            "max": max((d.ph for d in sensor_data_list if d.ph), default=None),
        },
        "oxygen": {
            "avg": sum(d.oxygen for d in sensor_data_list if d.oxygen) / len(sensor_data_list) if sensor_data_list else 0,
            "min": min((d.oxygen for d in sensor_data_list if d.oxygen), default=None),
            "max": max((d.oxygen for d in sensor_data_list if d.oxygen), default=None),
        }
    }

    return stats
