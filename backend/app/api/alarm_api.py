"""
预警管理API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import AlarmRule, AlarmRecord
from app.models.device import AlarmLevel
from app.utils import format_datetime, get_time_ago_string
from pydantic import BaseModel

router = APIRouter()


class AlarmRuleResponse(BaseModel):
    """预警规则响应模型"""
    id: int
    rule_name: str
    sensor_type: str
    threshold_type: str
    threshold_value: float
    level: str
    is_enabled: int

    class Config:
        from_attributes = True


class AlarmRecordResponse(BaseModel):
    """预警记录响应模型"""
    id: int
    device_id: Optional[int]
    alarm_level: str
    threshold_value: float
    actual_value: float
    message: str
    is_resolved: int
    resolved_at: Optional[str]
    created_at: str
    time_ago: str

    class Config:
        from_attributes = True


@router.get("/rules", response_model=List[AlarmRuleResponse])
def get_alarm_rules(
    device_id: Optional[int] = Query(None, description="设备ID，为空则返回所有规则"),
    is_enabled: Optional[int] = Query(None, description="是否启用：1-启用 0-禁用"),
    db: Session = Depends(get_db)
):
    """
    获取预警规则列表

    参数:
        device_id: 设备ID（可选）
        is_enabled: 是否启用（可选）

    返回:
        预警规则列表
    """
    query = db.query(AlarmRule)

    if device_id is not None:
        query = query.filter(AlarmRule.device_id == device_id)
    if is_enabled is not None:
        query = query.filter(AlarmRule.is_enabled == is_enabled)

    rules = query.order_by(AlarmRule.level.desc()).all()

    return [AlarmRuleResponse(
        id=rule.id,
        rule_name=rule.rule_name,
        sensor_type=rule.sensor_type or "全部",
        threshold_type=rule.threshold_type,
        threshold_value=float(rule.threshold_value),
        level=rule.level,
        is_enabled=rule.is_enabled
    ) for rule in rules]


@router.get("/records", response_model=List[AlarmRecordResponse])
def get_alarm_records(
    device_id: Optional[int] = Query(None, description="设备ID"),
    level: Optional[str] = Query(None, description="预警级别：提醒/警告/危险"),
    is_resolved: Optional[int] = Query(None, description="是否已解决：1-已解决 0-未解决"),
    days: int = Query(7, ge=1, le=30, description="查询天数，默认7天"),
    db: Session = Depends(get_db)
):
    """
    获取预警记录列表

    参数:
        device_id: 设备ID（可选）
        level: 预警级别（可选）
        is_resolved: 是否已解决（可选）
        days: 查询天数，默认7天

    返回:
        预警记录列表
    """
    start_time = datetime.now() - timedelta(days=days)
    query = db.query(AlarmRecord).filter(AlarmRecord.created_at >= start_time)

    if device_id is not None:
        query = query.filter(AlarmRecord.device_id == device_id)
    if level:
        query = query.filter(AlarmRecord.alarm_level == level)
    if is_resolved is not None:
        query = query.filter(AlarmRecord.is_resolved == is_resolved)

    records = query.order_by(AlarmRecord.created_at.desc()).all()

    return [AlarmRecordResponse(
        id=record.id,
        device_id=record.device_id,
        alarm_level=record.alarm_level.value,
        threshold_value=float(record.threshold_value) if record.threshold_value else 0,
        actual_value=float(record.actual_value) if record.actual_value else 0,
        message=record.message,
        is_resolved=record.is_resolved,
        resolved_at=format_datetime(record.resolved_at) if record.resolved_at else None,
        created_at=format_datetime(record.created_at),
        time_ago=get_time_ago_string(record.created_at)
    ) for record in records]


@router.post("/records/{record_id}/resolve")
def resolve_alarm(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    标记预警记录为已解决

    参数:
        record_id: 预警记录ID

    返回:
        更新结果
    """
    record = db.query(AlarmRecord).filter(AlarmRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="预警记录不存在")

    record.is_resolved = 1
    record.resolved_at = datetime.now()
    db.commit()

    return {
        "status": "success",
        "message": "预警记录已标记为已解决",
        "record_id": record_id
    }


@router.get("/summary", response_model=dict)
def get_alarm_summary(
    days: int = Query(7, ge=1, le=30, description="查询天数，默认7天"),
    db: Session = Depends(get_db)
):
    """
    获取预警汇总统计

    参数:
        days: 查询天数，默认7天

    返回:
        预警统计信息
    """
    start_time = datetime.now() - timedelta(days=days)

    # 统计各级别的预警数量
    level_stats = db.query(
        AlarmRecord.alarm_level,
        AlarmRecord.is_resolved,
    ).filter(
        AlarmRecord.created_at >= start_time
    ).group_by(
        AlarmRecord.alarm_level,
        AlarmRecord.is_resolved
    ).all()

    # 统计总数
    total_records = db.query(AlarmRecord.id).filter(
        AlarmRecord.created_at >= start_time,
        AlarmRecord.is_resolved == 0
    ).count()

    level_summary = {
        "提醒": {"total": 0, "unresolved": 0},
        "警告": {"total": 0, "unresolved": 0},
        "危险": {"total": 0, "unresolved": 0},
    }

    for level, is_resolved in level_stats:
        if level.value not in level_summary:
            continue
        level_summary[level.value]["total"] += 1
        if not is_resolved:
            level_summary[level.value]["unresolved"] += 1

    return {
        "period_days": days,
        "total_records": total_records,
        "level_summary": level_summary,
        "last_updated": format_datetime(datetime.now())
    }
