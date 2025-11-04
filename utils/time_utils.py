"""
时间工具函数模块

复用TypeScript版本的时间处理逻辑（src/utils/timeUtils.ts）
支持中国时区（Asia/Shanghai）和ISO格式转换
"""

from datetime import datetime, timezone
from typing import Optional, Union
import pytz


# 中国时区
CHINA_TZ = pytz.timezone('Asia/Shanghai')


def get_china_time() -> datetime:
    """
    获取当前中国时间（带时区信息）
    
    Returns:
        datetime: 中国时区的当前时间
        
    对应TypeScript: 无直接对应，但是日志系统中使用
    """
    return datetime.now(CHINA_TZ)


def get_china_time_iso() -> str:
    """
    获取当前中国时间的ISO格式字符串
    
    Returns:
        str: ISO格式的时间字符串，例如：2025-11-04T21:30:45+08:00
        
    对应TypeScript: src/utils/timeUtils.ts - getChinaTimeISO()
    """
    return get_china_time().isoformat()


def format_china_time(dt: Optional[Union[datetime, str]] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化中国时间为指定格式的字符串
    
    Args:
        dt: datetime对象或ISO格式字符串，如果为None则使用当前时间
        format_str: 格式化字符串，默认为 "YYYY-MM-DD HH:MM:SS"
        
    Returns:
        str: 格式化的时间字符串
        
    对应TypeScript: src/utils/timeUtils.ts - formatChinaTime()
    """
    if dt is None:
        dt_obj = get_china_time()
    elif isinstance(dt, str):
        # 如果是字符串，先解析为datetime
        dt_obj = parse_iso_time(dt)
    else:
        dt_obj = dt
    
    # 处理时区
    if dt_obj.tzinfo is None:
        # 如果没有时区信息，假设是UTC并转换为中国时区
        dt_obj = pytz.utc.localize(dt_obj).astimezone(CHINA_TZ)
    elif dt_obj.tzinfo != CHINA_TZ:
        # 如果有时区但不是中国时区，转换为中国时区
        dt_obj = dt_obj.astimezone(CHINA_TZ)
    
    return dt_obj.strftime(format_str)


def parse_iso_time(iso_str: str) -> datetime:
    """
    解析ISO格式的时间字符串
    
    Args:
        iso_str: ISO格式的时间字符串
        
    Returns:
        datetime: 解析后的datetime对象（UTC时区）
        
    对应TypeScript: Date.parse() / new Date()
    """
    # Python的datetime.fromisoformat()可以解析ISO格式
    # 但为了兼容性，我们使用dateutil
    from dateutil.parser import parse
    return parse(iso_str)


def utc_to_china(utc_dt: datetime) -> datetime:
    """
    将UTC时间转换为中国时间
    
    Args:
        utc_dt: UTC时区的datetime对象
        
    Returns:
        datetime: 中国时区的datetime对象
    """
    if utc_dt.tzinfo is None:
        # 如果没有时区信息，假设是UTC
        utc_dt = pytz.utc.localize(utc_dt)
    
    return utc_dt.astimezone(CHINA_TZ)


def china_to_utc(china_dt: datetime) -> datetime:
    """
    将中国时间转换为UTC时间
    
    Args:
        china_dt: 中国时区的datetime对象
        
    Returns:
        datetime: UTC时区的datetime对象
    """
    if china_dt.tzinfo is None:
        # 如果没有时区信息，假设是中国时区
        china_dt = CHINA_TZ.localize(china_dt)
    
    return china_dt.astimezone(pytz.utc)


def timestamp_to_china_time(timestamp: float) -> datetime:
    """
    将Unix时间戳转换为中国时间
    
    Args:
        timestamp: Unix时间戳（秒）
        
    Returns:
        datetime: 中国时区的datetime对象
    """
    utc_dt = datetime.fromtimestamp(timestamp, tz=pytz.utc)
    return utc_dt.astimezone(CHINA_TZ)


def china_time_to_timestamp(china_dt: datetime) -> float:
    """
    将中国时间转换为Unix时间戳
    
    Args:
        china_dt: 中国时区的datetime对象
        
    Returns:
        float: Unix时间戳（秒）
    """
    if china_dt.tzinfo is None:
        china_dt = CHINA_TZ.localize(china_dt)
    
    return china_dt.timestamp()


def get_time_diff_minutes(start: datetime, end: Optional[datetime] = None) -> float:
    """
    计算两个时间之间的分钟差
    
    Args:
        start: 开始时间
        end: 结束时间，如果为None则使用当前时间
        
    Returns:
        float: 时间差（分钟）
    """
    if end is None:
        end = get_china_time()
    
    diff = end - start
    return diff.total_seconds() / 60


def get_time_diff_hours(start: datetime, end: Optional[datetime] = None) -> float:
    """
    计算两个时间之间的小时差
    
    Args:
        start: 开始时间
        end: 结束时间，如果为None则使用当前时间
        
    Returns:
        float: 时间差（小时）
    """
    return get_time_diff_minutes(start, end) / 60


if __name__ == "__main__":
    # 测试时间工具函数
    print("\n" + "=" * 80)
    print("🕐 时间工具函数测试")
    print("=" * 80 + "\n")
    
    # 1. 获取当前中国时间
    china_now = get_china_time()
    print(f"当前中国时间: {china_now}")
    print(f"ISO格式: {get_china_time_iso()}")
    print(f"格式化: {format_china_time()}")
    
    # 2. 时区转换
    utc_now = datetime.now(pytz.utc)
    print(f"\nUTC时间: {utc_now}")
    print(f"转换为中国时间: {utc_to_china(utc_now)}")
    print(f"再转回UTC: {china_to_utc(utc_to_china(utc_now))}")
    
    # 3. 时间戳转换
    timestamp = datetime.now().timestamp()
    print(f"\n时间戳: {timestamp}")
    print(f"转换为中国时间: {timestamp_to_china_time(timestamp)}")
    
    # 4. 时间差计算
    from datetime import timedelta
    past_time = china_now - timedelta(hours=2, minutes=30)
    print(f"\n过去的时间: {past_time}")
    print(f"距离现在: {get_time_diff_minutes(past_time):.2f} 分钟")
    print(f"距离现在: {get_time_diff_hours(past_time):.2f} 小时")
    
    print("\n" + "=" * 80)
    print("✅ 时间工具函数测试完成")
    print("=" * 80 + "\n")

