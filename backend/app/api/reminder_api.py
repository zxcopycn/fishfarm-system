""" 备忘提醒API """

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models import Reminder
from app.utils import format_datetime

router = APIRouter()


class ReminderCreate(BaseModel):
    """提醒创建模型"""
    title: str
    content: Optional[str] = None
    reminder_time: Optional[str] = None


class ReminderResponse(BaseModel):
    """提醒响应模型"""
    id: int
    title: str
    content: Optional[str] = None
    reminder_time: str
    is_completed: bool
    completed_at: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


def reminder_to_response(reminder: Reminder) -> ReminderResponse:
    """将ORM Reminder对象转换为Pydantic ReminderResponse"""
    return ReminderResponse(
        id=reminder.id,
        title=reminder.title,
        content=reminder.content,
        reminder_time=format_datetime(reminder.reminder_time),
        is_completed=reminder.is_completed == 1,
        completed_at=format_datetime(reminder.completed_at) if reminder.completed_at else None,
        created_at=format_datetime(reminder.created_at),
        updated_at=format_datetime(reminder.updated_at)
    )


@router.get("", response_model=List[ReminderResponse])
def get_reminders(
    is_completed: int = 0,
    db: Session = Depends(get_db)
) -> List[ReminderResponse]:
    """
    获取提醒列表

    参数:
        is_completed: 是否已完成：0-未完成 1-已完成（默认0）

    返回:
        List[ReminderResponse]: 提醒列表
    """
    query = db.query(Reminder)
    if is_completed != -1:
        query = query.filter(Reminder.is_completed == is_completed)

    # 按提醒时间排序
    reminders = query.order_by(Reminder.reminder_time.asc()).all()
    return [reminder_to_response(r) for r in reminders]


@router.post("", response_model=ReminderResponse)
def create_reminder(
    reminder: ReminderCreate,
    db: Session = Depends(get_db)
) -> ReminderResponse:
    """
    创建新提醒

    参数:
        title: 提醒标题
        content: 提醒内容（可选）
        reminder_time: 提醒时间（可选，默认当前时间）

    返回:
        ReminderResponse: 创建的提醒信息
    """
    new_reminder = Reminder(
        title=reminder.title,
        content=reminder.content,
        reminder_time=datetime.fromisoformat(reminder.reminder_time) if reminder.reminder_time else datetime.now()
    )
    
    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)
    
    return reminder_to_response(new_reminder)


@router.put("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    reminder_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    reminder_time: Optional[str] = None,
    is_completed: Optional[int] = None,
    db: Session = Depends(get_db)
) -> ReminderResponse:
    """
    更新提醒

    参数:
        reminder_id: 提醒ID
        title: 提醒标题（可选）
        content: 提醒内容（可选）
        reminder_time: 提醒时间（可选）
        is_completed: 是否完成（可选）

    返回:
        ReminderResponse: 更新的提醒信息
    """
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")

    if title is not None:
        reminder.title = title
    if content is not None:
        reminder.content = content
    if reminder_time is not None:
        reminder.reminder_time = datetime.fromisoformat(reminder_time)
    if is_completed is not None:
        reminder.is_completed = is_completed
        if is_completed == 1:
            reminder.completed_at = datetime.now()

    db.commit()
    db.refresh(reminder)
    
    return reminder_to_response(reminder)


@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    """
    删除提醒

    参数:
        reminder_id: 提醒ID

    返回:
        删除结果
    """
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")

    db.delete(reminder)
    db.commit()
    
    return {
        "status": "success",
        "message": "提醒已删除",
        "reminder_id": reminder_id
    }


@router.patch("/{reminder_id}/complete")
def mark_as_completed(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    """
    标记提醒为已完成

    参数:
        reminder_id: 提醒ID

    返回:
        更新结果
    """
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")

    reminder.is_completed = 1
    reminder.completed_at = datetime.now()
    db.commit()
    
    return {
        "status": "success",
        "message": "提醒已标记为完成",
        "reminder_id": reminder_id
    }


@router.get("/summary", response_model=dict)
def get_reminder_summary(db: Session = Depends(get_db)):
    """
    获取提醒统计

    返回:
        提醒统计信息
    """
    total = db.query(Reminder).count()
    completed = db.query(Reminder).filter(Reminder.is_completed == 1).count()
    pending = db.query(Reminder).filter(Reminder.is_completed == 0).count()
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending
    }
