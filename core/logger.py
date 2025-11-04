"""
日志配置模块

使用loguru实现更友好的日志输出
支持中国时区（Asia/Shanghai）
彩色输出和文件记录
"""

import sys
from pathlib import Path
from loguru import logger
from datetime import datetime
import pytz

from config.settings import settings


# 中国时区
CHINA_TZ = pytz.timezone('Asia/Shanghai')


def get_china_time() -> datetime:
    """获取中国时间"""
    return datetime.now(CHINA_TZ)


def format_china_time(dt: datetime = None) -> str:
    """
    格式化中国时间为字符串
    
    Args:
        dt: datetime对象，如果为None则使用当前时间
        
    Returns:
        格式化的时间字符串，例如：2025-11-04 21:30:45+08:00
    """
    if dt is None:
        dt = get_china_time()
    elif dt.tzinfo is None:
        # 如果没有时区信息，假设是UTC并转换为中国时区
        dt = pytz.utc.localize(dt).astimezone(CHINA_TZ)
    return dt.strftime("%Y-%m-%d %H:%M:%S%z")


def setup_logger():
    """
    配置日志系统
    
    特性：
    - 控制台输出：彩色格式，便于查看
    - 文件输出：详细日志，用于排查问题
    - 时区：中国时区（Asia/Shanghai）
    - 日志轮转：每天一个文件，保留30天
    """
    from loguru import logger as _logger
    
    # 移除默认的handler
    _logger.remove()
    
    # 日志格式
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 添加控制台输出
    _logger.add(
        sys.stdout,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # 添加文件输出（如果启用）
    if settings.LOG_TO_FILE:
        # 确保日志目录存在
        log_path = Path(settings.LOG_FILE_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        _logger.add(
            settings.LOG_FILE_PATH,
            format=log_format,
            level=settings.LOG_LEVEL,
            rotation="00:00",  # 每天0点轮转
            retention="30 days",  # 保留30天
            compression="zip",  # 压缩旧日志
            encoding="utf-8",
            backtrace=True,
            diagnose=True,
        )
        
        _logger.info(f"日志文件输出已启用: {settings.LOG_FILE_PATH}")
    
    # 设置时区（通过拦截器）
    def add_china_timezone(record):
        """添加中国时区到日志记录"""
        record["extra"]["china_time"] = format_china_time()
        return True
    
    # 应用时区补丁并返回
    _logger.patch(add_china_timezone)
    
    return _logger


# 初始化日志系统
logger = setup_logger()


# 导出常用的日志函数
def log_info(message: str, **kwargs):
    """记录信息日志"""
    logger.info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """记录警告日志"""
    logger.warning(message, **kwargs)


def log_error(message: str, **kwargs):
    """记录错误日志"""
    logger.error(message, **kwargs)


def log_debug(message: str, **kwargs):
    """记录调试日志"""
    logger.debug(message, **kwargs)


def log_critical(message: str, **kwargs):
    """记录严重错误日志"""
    logger.critical(message, **kwargs)


# 添加分隔线日志（用于美化输出）
def log_separator(char: str = "=", length: int = 80):
    """打印分隔线"""
    logger.info(char * length)


def log_section_start(title: str, char: str = "=", length: int = 80):
    """打印章节开始"""
    logger.info("")
    log_separator(char, length)
    logger.info(f"{title}")
    log_separator(char, length)
    logger.info("")


def log_section_end(char: str = "=", length: int = 80):
    """打印章节结束"""
    logger.info("")
    log_separator(char, length)
    logger.info("")


if __name__ == "__main__":
    # 测试日志输出
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.debug("这是一条调试日志（只在DEBUG级别显示）")
    
    # 测试分隔线
    log_section_start("测试章节")
    logger.info("章节内容")
    log_section_end()
    
    # 测试中国时区
    logger.info(f"当前中国时间: {format_china_time()}")
    
    print("\n✅ 日志系统测试完成")

