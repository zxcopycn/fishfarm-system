"""
日期工具函数
"""

from datetime import datetime, timedelta
from typing import Tuple


def get_date_range(days: int = 7) -> Tuple[datetime, datetime]:
    """
    获取日期范围

    参数:
        days: 天数

    返回:
        (start_date, end_date)
    """
    now = datetime.now()
    start_date = now - timedelta(days=days)
    end_date = now
    return start_date, end_date


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间

    参数:
        dt: 日期时间对象
        format_str: 格式字符串

    返回:
        格式化后的字符串
    """
    if dt is None:
        return ""
    return dt.strftime(format_str)


def parse_datetime(datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    解析日期时间字符串

    参数:
        datetime_str: 日期时间字符串
        format_str: 格式字符串

    返回:
        日期时间对象
    """
    return datetime.strptime(datetime_str, format_str)


def get_current_time() -> datetime:
    """
    获取当前时间
    """
    return datetime.now()


def get_time_ago_string(dt: datetime) -> str:
    """
    获取"xx分钟前"/"xx小时前"等相对时间字符串

    参数:
        dt: 日期时间对象

    返回:
        相对时间字符串
    """
    now = get_current_time()
    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "刚刚"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}分钟前"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours}小时前"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days}天前"
    else:
        return format_datetime(dt, "%Y-%m-%d")
