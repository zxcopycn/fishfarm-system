"""
数据备份服务
自动备份数据库
"""

import os
import subprocess
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Backup
from loguru import logger
import shutil


class BackupService:
    """数据备份服务类"""

    @staticmethod
    def backup_database(db: Session) -> dict:
        """
        备份数据库

        返回:
            备份信息字典
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"fishfarm_backup_{timestamp}.sql"
        backup_dir = "backups"

        # 创建备份目录
        os.makedirs(backup_dir, exist_ok=True)

        backup_path = os.path.join(backup_dir, backup_file)

        try:
            # 执行mysqldump备份
            cmd = [
                "mysqldump",
                "-h", "localhost",
                "-u", "root",
                "-p", "password",  # 密码暂用默认
                "--single-transaction",
                "--routines",
                "--triggers",
                "--events",
                "fishfarm",
                ">", backup_path
            ]

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"数据库备份失败：{result.stderr}")
                raise Exception(f"备份失败：{result.stderr}")

            # 计算文件大小
            file_size = os.path.getsize(backup_path)

            # 记录备份信息到数据库
            backup_record = Backup(
                backup_type="database",
                file_name=backup_file,
                file_path=backup_path,
                file_size=file_size,
                remark=f"数据库自动备份 - {timestamp}"
            )
            db.add(backup_record)
            db.commit()

            logger.info(f"数据库备份成功：{backup_file} ({file_size} bytes)")
            return {
                "status": "success",
                "backup_file": backup_file,
                "backup_path": backup_path,
                "file_size": file_size,
                "backup_time": timestamp
            }

        except Exception as e:
            logger.error(f"数据库备份异常：{e}")
            raise

    @staticmethod
    def get_backup_list(db: Session, limit: int = 10):
        """
        获取备份列表

        参数:
            db: 数据库会话
            limit: 返回条数，默认10条

        返回:
            备份列表
        """
        backups = db.query(Backup).order_by(
            Backup.backup_time.desc()
        ).limit(limit).all()

        return [
            {
                "id": backup.id,
                "backup_type": backup.backup_type,
                "file_name": backup.file_name,
                "file_size": backup.file_size,
                "backup_time": backup.backup_time.strftime("%Y-%m-%d %H:%M:%S"),
                "is_deleted": backup.is_deleted,
                "remark": backup.remark
            }
            for backup in backups
        ]

    @staticmethod
    def delete_backup(db: Session, backup_id: int) -> bool:
        """
        删除备份文件

        参数:
            db: 数据库会话
            backup_id: 备份记录ID

        返回:
            是否成功
        """
        backup = db.query(Backup).filter(Backup.id == backup_id).first()
        if not backup:
            logger.warning(f"备份记录不存在：{backup_id}")
            return False

        try:
            # 删除物理文件
            if os.path.exists(backup.file_path):
                os.remove(backup.file_path)

            # 标记为已删除
            backup.is_deleted = 1
            db.commit()

            logger.info(f"备份文件已删除：{backup.file_name}")
            return True

        except Exception as e:
            logger.error(f"删除备份文件失败：{e}")
            return False


# 全局备份服务实例
_backup_service = None


def get_backup_service() -> BackupService:
    """获取备份服务实例"""
    global _backup_service
    if _backup_service is None:
        _backup_service = BackupService()
    return _backup_service
