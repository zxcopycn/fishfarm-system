""" 数据库配置和会话管理 """

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from app.config import settings
from app.models import Device, SensorData, ControlDevice, ControlRecord, ProductionRecord, Reminder, User, Backup, AlarmRule, AlarmRecord, UserPermission

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    获取数据库会话的依赖函数
    用于FastAPI的依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    数据库上下文管理器
    用于直接使用Python代码时管理数据库会话
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def init_database():
    """
    初始化数据库
    创建所有表
    """
    print("正在初始化数据库...")
    try:
        # 导入所有模型以注册到Base.metadata
        from app.models.device import Base as DeviceBase
        from app.models.reminder import Base as ReminderBase
        
        # 创建所有表，忽略已存在的索引
        DeviceBase.metadata.create_all(bind=engine, checkfirst=True)
        ReminderBase.metadata.create_all(bind=engine, checkfirst=True)
        print("数据库初始化完成！")
    except Exception as e:
        print(f"数据库初始化时出现警告（可以忽略）：{e}")
        print("应用将在现有数据库基础上继续运行")


def drop_all_tables():
    """
    删除所有表（谨慎使用！）
    """
    print("正在删除所有表...")
    from app.models.device import Base as DeviceBase
    from app.models.reminder import Base as ReminderBase
    
    DeviceBase.metadata.drop_all(bind=engine)
    ReminderBase.metadata.drop_all(bind=engine)
    print("所有表已删除！")
