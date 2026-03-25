from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, SmallInteger, Index, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Reminder(Base):
    """
    备忘提醒表
    存储用户的备忘提醒事项
    """

    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="提醒标题")
    content = Column(Text, comment="提醒内容")
    reminder_time = Column(TIMESTAMP, nullable=False, comment="提醒时间")
    is_completed = Column(SmallInteger, default=0, comment="是否完成：1-完成 0-未完成")
    completed_at = Column(TIMESTAMP, comment="完成时间")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")

    # 建立索引以提高查询性能
    __table_args__ = (
        Index("idx_time", "reminder_time"),
        Index("idx_completed", "is_completed"),
    )

    def __repr__(self):
        return f"<Reminder(id={self.id}, title={self.title}, completed={self.is_completed})>"
