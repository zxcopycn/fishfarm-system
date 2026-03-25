"""
生产记录管理API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from typing import Optional
from datetime import date
from app.database import get_db
from app.models import ProductionRecord
from app.utils import format_datetime, get_time_ago_string
from pydantic import BaseModel

router = APIRouter()


class ProductionRecordResponse(BaseModel):
    """生产记录响应模型"""
    id: int
    fish_type: str
    quantity: float
    spawn_date: str
    hatch_date: str
    growth_stage: str
    weight: float
    length: float
    feed_amount: float
    remark: str
    created_at: str
    time_ago: str

    class Config:
        from_attributes = True


@router.get("/list", response_model=List[ProductionRecordResponse])
def get_production_records(
    fish_type: Optional[str] = Query(None, description="鱼类品种筛选"),
    limit: int = Query(50, ge=1, le=100, description="返回条数"),
    db: Session = Depends(get_db)
):
    """
    获取生产记录列表

    参数:
        fish_type: 鱼类品种筛选（可选）
        limit: 返回条数，默认50条

    返回:
        生产记录列表
    """
    query = db.query(ProductionRecord)

    if fish_type:
        query = query.filter(ProductionRecord.fish_type.like(f"%{fish_type}%"))

    records = query.order_by(ProductionRecord.spawn_date.desc()).limit(limit).all()

    return [ProductionRecordResponse(
        id=record.id,
        fish_type=record.fish_type or "",
        quantity=float(record.quantity) if record.quantity else 0,
        spawn_date=format_datetime(record.spawn_date) if record.spawn_date else "",
        hatch_date=format_datetime(record.hatch_date) if record.hatch_date else "",
        growth_stage=record.growth_stage or "",
        weight=float(record.weight) if record.weight else 0,
        length=float(record.length) if record.length else 0,
        feed_amount=float(record.feed_amount) if record.feed_amount else 0,
        remark=record.remark or "",
        created_at=format_datetime(record.created_at),
        time_ago=get_time_ago_string(record.created_at) if record.created_at else ""
    ) for record in records]


@router.get("/statistics", response_model=dict)
def get_production_statistics(
    db: Session = Depends(get_db)
):
    """
    获取生产统计数据

    返回:
        生产统计信息
    """
    # 统计不同鱼类的数量
    fish_stats = db.query(
        ProductionRecord.fish_type,
        ProductionRecord.quantity,
    ).group_by(
        ProductionRecord.fish_type
    ).all()

    # 统计总数量
    total_quantity = sum(float(q.quantity) for _, q in fish_stats)

    # 统计记录数
    total_records = db.query(ProductionRecord.id).count()

    # 按月份统计（最近6个月）
    from datetime import datetime, timedelta
    six_months_ago = datetime.now() - timedelta(days=180)

    monthly_stats = db.query(
        ProductionRecord.spawn_date
    ).filter(
        ProductionRecord.spawn_date >= six_months_ago
    ).group_by(
        ProductionRecord.spawn_date
    ).all()

    month_data = {}
    for spawn_date, _ in monthly_stats:
        month_key = spawn_date.strftime("%Y-%m")
        if month_key not in month_data:
            month_data[month_key] = 0
        month_data[month_key] += 1

    return {
        "total_records": total_records,
        "total_quantity": total_quantity,
        "fish_types": {ft: float(q.quantity) for ft, q in fish_stats},
        "monthly_stats": month_data
    }
