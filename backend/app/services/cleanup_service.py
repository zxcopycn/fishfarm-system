"""
数据清理定时任务服务
自动清理过期的实时数据
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import engine, SessionLocal
from app.models import SensorData
from loguru import logger


class CleanupService:
    """数据清理服务类"""

    @staticmethod
    def cleanup_expired_data(days: int = 7):
        """
        清理过期的传感器数据

        参数:
            days: 保留天数，默认7天

        返回:
            删除的记录数
        """
        delete_date = datetime.now() - timedelta(days=days)

        with SessionLocal() as db:
            # 查询过期数据
            expired_data = db.query(SensorData).filter(
                SensorData.created_at < delete_date
            ).all()

            delete_count = len(expired_data)

            # 批量删除
            for data in expired_data:
                db.delete(data)

            db.commit()

            logger.info(f"数据清理完成：删除了 {delete_count} 条过期数据（{days}天前）")
            return delete_count

    @staticmethod
    def schedule_cleanup_task(interval_hours: int = 24):
        """
        调度清理任务（使用APScheduler）

        参数:
            interval_hours: 清理间隔（小时），默认24小时

        返回:
            调度任务函数
        """
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.interval import IntervalTrigger

        scheduler = BackgroundScheduler()

        @scheduler.scheduled_job(
            IntervalTrigger(hours=interval_hours),
            id='cleanup_expired_data',
            replace_existing=True
        )
        def cleanup_job():
            """定时清理任务"""
            try:
                count = CleanupService.cleanup_expired_data(days=7)
                logger.info(f"定时数据清理任务执行完成，删除了 {count} 条数据")
            except Exception as e:
                logger.error(f"数据清理任务执行失败：{e}")

        return scheduler


# 全局调度器实例
_cleanup_scheduler = None


def get_cleanup_scheduler() -> CleanupService:
    """获取清理服务实例"""
    global _cleanup_scheduler
    if _cleanup_scheduler is None:
        _cleanup_scheduler = CleanupService()
    return _cleanup_scheduler
