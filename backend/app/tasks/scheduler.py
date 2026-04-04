"""
定时任务调度模块
使用APScheduler管理定时任务
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import SensorData, Device, Backup
from app.utils.logger import logger
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

# 创建调度器实例
scheduler = AsyncIOScheduler()


def cleanup_old_sensor_data():
    """清理旧的传感器数据"""
    logger.info("开始清理旧的传感器数据")
    
    db = SessionLocal()
    try:
        # 计算清理日期（保留7天数据）
        cutoff_date = datetime.now() - timedelta(days=settings.REALTIME_DATA_RETENTION_DAYS)
        
        # 删除旧数据
        deleted_count = db.query(SensorData).filter(
            SensorData.created_at < cutoff_date
        ).delete()
        
        db.commit()
        logger.info(f"成功清理 {deleted_count} 条旧传感器数据")
        
        # 清理设备状态（将长期离线的设备标记为离线）
        from app.models import Device
        offline_threshold = datetime.now() - timedelta(days=1)
        offline_devices = db.query(Device).filter(
            Device.status == 1,
            Device.updated_at < offline_threshold
        ).all()
        
        for device in offline_devices:
            device.status = 0
            logger.warning(f"设备 {device.device_name} 已离线")
        
        db.commit()
        logger.info(f"已更新 {len(offline_devices)} 个设备状态为离线")
        
    except Exception as e:
        logger.error(f"清理传感器数据失败: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def cleanup_old_alarm_records():
    """清理已解决的旧预警记录"""
    logger.info("开始清理已解决的旧预警记录")
    
    db = SessionLocal()
    try:
        # 计算清理日期（保留30天已解决的记录）
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # 删除已解决的旧预警记录
        from app.models import AlarmRecord
        deleted_count = db.query(AlarmRecord).filter(
            AlarmRecord.is_resolved == 1,
            AlarmRecord.resolved_at < cutoff_date
        ).delete()
        
        db.commit()
        logger.info(f"成功清理 {deleted_count} 条已解决预警记录")
        
    except Exception as e:
        logger.error(f"清理预警记录失败: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def create_daily_backup():
    """创建每日数据库备份"""
    logger.info("开始创建每日备份")
    
    db = SessionLocal()
    try:
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.sql"
        backup_path = f"backups/{backup_name}"
        
        # 创建备份目录
        import os
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # 执行备份（这里使用简单的数据导出）
        # 在实际应用中，可以使用mysqldump或类似的工具
        from sqlalchemy import create_engine
        engine = create_engine(settings.DATABASE_URL)
        
        # 导出数据（简化版）
        import pandas as pd
        from app.models import Device, SensorData, AlarmRecord
        
        # 导出设备数据
        devices = pd.read_sql("SELECT * FROM devices", engine)
        devices.to_csv(f"{backup_path}_devices.csv", index=False)
        
        # 导出传感器数据（最近24小时）
        recent_sensors = pd.read_sql(
            f"SELECT * FROM sensor_data WHERE created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)",
            engine
        )
        recent_sensors.to_csv(f"{backup_path}_sensor_data.csv", index=False)
        
        # 导出预警记录（最近7天）
        recent_alarms = pd.read_sql(
            f"SELECT * FROM alarm_records WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)",
            engine
        )
        recent_alarms.to_csv(f"{backup_path}_alarm_records.csv", index=False)
        
        # 记录备份信息
        backup = Backup(
            backup_type="database",
            file_name=backup_name,
            file_path=backup_path,
            backup_time=datetime.now()
        )
        db.add(backup)
        db.commit()
        
        logger.info(f"备份创建成功: {backup_path}")
        
    except Exception as e:
        logger.error(f"创建备份失败: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def check_system_health():
    """系统健康检查"""
    logger.info("开始系统健康检查")
    
    db = SessionLocal()
    try:
        # 检查数据库连接
        result = db.execute("SELECT 1").scalar()
        if result != 1:
            logger.error("数据库连接失败")
            return
        
        # 检查设备在线状态
        from app.models import Device
        total_devices = db.query(Device).count()
        online_devices = db.query(Device).filter(Device.status == 1).count()
        
        logger.info(f"系统健康状态 - 总设备: {total_devices}, 在线设备: {online_devices}")
        
        # 检查传感器数据最近更新时间
        recent_data = db.query(SensorData).filter(
            SensorData.created_at > datetime.now() - timedelta(minutes=10)
        ).count()
        
        logger.info(f"最近10分钟内的传感器数据: {recent_data} 条")
        
        # 检查未解决的预警数量
        from app.models import AlarmRecord
        unresolved_alarms = db.query(AlarmRecord).filter(
            AlarmRecord.is_resolved == 0
        ).count()
        
        logger.warning(f"未解决预警数量: {unresolved_alarms}")
        
        if unresolved_alarms > 10:
            logger.error("预警数量过多，需要及时处理")
        
    except Exception as e:
        logger.error(f"系统健康检查失败: {e}", exc_info=True)
    finally:
        db.close()


def generate_daily_report():
    """生成日报数据"""
    logger.info("开始生成日报数据")
    
    db = SessionLocal()
    try:
        from app.models import SensorData, Device, AlarmRecord
        
        # 获取昨天的数据
        yesterday_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        yesterday_end = yesterday_start + timedelta(days=1)
        
        # 统计设备数量
        total_devices = db.query(Device).count()
        online_devices = db.query(Device).filter(Device.status == 1).count()
        
        # 统计传感器数据数量
        sensor_count = db.query(SensorData).filter(
            SensorData.created_at.between(yesterday_start, yesterday_end)
        ).count()
        
        # 统计预警数量
        alarm_count = db.query(AlarmRecord).filter(
            AlarmRecord.created_at.between(yesterday_start, yesterday_end)
        ).count()
        
        # 统计未解决预警
        unresolved_alarms = db.query(AlarmRecord).filter(
            AlarmRecord.is_resolved == 1,
            AlarmRecord.resolved_at.between(yesterday_start, yesterday_end)
        ).count()
        
        logger.info(f"日报数据 - 设备: {total_devices}个, 在线: {online_devices}个")
        logger.info(f"日报数据 - 传感器数据: {sensor_count}条, 预警: {alarm_count}条, 已解决: {unresolved_alarms}条")
        
        # 保存日报数据（可以存储到报表表或文件）
        report_data = {
            "date": yesterday_start.date(),
            "total_devices": total_devices,
            "online_devices": online_devices,
            "sensor_count": sensor_count,
            "alarm_count": alarm_count,
            "unresolved_alarms": unresolved_alarms
        }
        
        # TODO: 可以保存到专门的报表表
        logger.info(f"日报数据: {report_data}")
        
    except Exception as e:
        logger.error(f"生成日报失败: {e}", exc_info=True)
    finally:
        db.close()


def init_scheduler():
    """
    初始化调度器并添加任务
    """
    # 数据清理任务 - 每天凌晨2点
    scheduler.add_job(
        cleanup_old_sensor_data,
        trigger=CronTrigger(hour=2, minute=0),
        id="cleanup_sensor_data",
        name="清理旧传感器数据",
        replace_existing=True
    )
    
    # 预警记录清理 - 每天凌晨3点
    scheduler.add_job(
        cleanup_old_alarm_records,
        trigger=CronTrigger(hour=3, minute=0),
        id="cleanup_alarm_records",
        name="清理已解决预警记录",
        replace_existing=True
    )
    
    # 数据备份 - 每天凌晨4点
    scheduler.add_job(
        create_daily_backup,
        trigger=CronTrigger(hour=4, minute=0),
        id="daily_backup",
        name="创建每日备份",
        replace_existing=True
    )
    
    # 系统健康检查 - 每30分钟
    scheduler.add_job(
        check_system_health,
        trigger=IntervalTrigger(minutes=30),
        id="health_check",
        name="系统健康检查",
        replace_existing=True
    )
    
    # 生成日报 - 每天23:30
    scheduler.add_job(
        generate_daily_report,
        trigger=CronTrigger(hour=23, minute=30),
        id="daily_report",
        name="生成日报数据",
        replace_existing=True
    )
    
    logger.info("调度器初始化完成，已添加以下任务：")
    logger.info("1. 清理旧传感器数据 - 每天02:00")
    logger.info("2. 清理已解决预警记录 - 每天03:00")
    logger.info("3. 创建每日备份 - 每天04:00")
    logger.info("4. 系统健康检查 - 每30分钟")
    logger.info("5. 生成日报数据 - 每天23:30")


# 初始化调度器
init_scheduler()
