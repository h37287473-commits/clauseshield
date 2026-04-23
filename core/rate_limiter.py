# -*- coding: utf-8 -*-
"""
ClauseShield - 输入速率限制器
MVP阶段基于内存字典的轻量级频率限制
"""

import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class _RateRecord:
    """单IP的扫描记录"""
    count: int = 0
    reset_at: float = 0.0
    blocked: bool = False


# 内存存储：IP -> 记录
_ip_records: Dict[str, _RateRecord] = {}

# 默认配置
DEFAULT_DAILY_LIMIT = 5          # 单IP每日最大扫描次数
DEFAULT_FILE_MAX_MB = 10         # 单文件大小限制（MB）
DEFAULT_CONTENT_MAX_CHARS = 50000  # 扫描内容长度限制
MB_TO_BYTES = 1024 * 1024


def _now() -> float:
    """当前时间戳"""
    return time.time()


def _get_midnight_ts() -> float:
    """获取今日午夜时间戳（用于日限重置）"""
    import datetime
    now = datetime.datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.timestamp()


def check_ip_limit(ip: str, daily_limit: int = DEFAULT_DAILY_LIMIT) -> Tuple[bool, str, int]:
    """
    检查IP是否超出日扫描次数限制

    Args:
        ip: 客户端IP地址
        daily_limit: 每日允许的最大扫描次数

    Returns:
        (是否允许, 提示消息, 剩余次数)
    """
    if not ip:
        return True, "", daily_limit

    midnight_ts = _get_midnight_ts()
    record = _ip_records.get(ip)

    if record is None:
        # 首次访问
        _ip_records[ip] = _RateRecord(count=1, reset_at=midnight_ts)
        remaining = daily_limit - 1
        return True, f"今日还可扫描 {remaining} 次", remaining

    # 检查是否跨天，跨天则重置
    if _now() >= record.reset_at + 86400:
        record.count = 1
        record.reset_at = midnight_ts
        record.blocked = False
        remaining = daily_limit - 1
        return True, f"今日还可扫描 {remaining} 次", remaining

    # 检查是否已超限
    if record.count >= daily_limit:
        msg = "今日扫描次数已用完，请明天再来或使用兑换码解锁更多次数"
        return False, msg, 0

    # 允许本次，计数+1
    record.count += 1
    remaining = daily_limit - record.count
    return True, f"今日还可扫描 {remaining} 次", remaining


def record_scan(ip: str) -> None:
    """
    显式记录一次扫描（用于在验证通过后正式计数）

    Args:
        ip: 客户端IP地址
    """
    if not ip:
        return
    record = _ip_records.get(ip)
    if record is None:
        _ip_records[ip] = _RateRecord(count=1, reset_at=_get_midnight_ts())
    else:
        record.count += 1


def check_file_size(file_bytes: bytes, max_mb: int = DEFAULT_FILE_MAX_MB) -> Tuple[bool, str]:
    """
    检查文件大小是否超限

    Args:
        file_bytes: 文件字节内容
        max_mb: 最大允许MB数

    Returns:
        (是否允许, 提示消息)
    """
    max_bytes = max_mb * MB_TO_BYTES
    if len(file_bytes) > max_bytes:
        return False, f"文件过大（{len(file_bytes) / MB_TO_BYTES:.1f} MB），最大支持 {max_mb} MB"
    return True, ""


def check_content_length(text: str, max_chars: int = DEFAULT_CONTENT_MAX_CHARS) -> Tuple[bool, str]:
    """
    检查扫描文本长度是否超限

    Args:
        text: 待扫描文本
        max_chars: 最大允许字符数

    Returns:
        (是否允许, 提示消息)
    """
    length = len(text)
    if length > max_chars:
        return False, f"合同文本过长（{length} 字符），最大支持 {max_chars} 字符，建议分段上传"
    return True, ""


def get_ip_status(ip: str, daily_limit: int = DEFAULT_DAILY_LIMIT) -> Dict[str, object]:
    """
    获取IP的当前限流状态

    Args:
        ip: 客户端IP地址
        daily_limit: 每日限制次数

    Returns:
        状态字典 {count, limit, remaining, reset_at}
    """
    if not ip:
        return {"count": 0, "limit": daily_limit, "remaining": daily_limit, "reset_at": None}

    record = _ip_records.get(ip)
    if record is None:
        return {"count": 0, "limit": daily_limit, "remaining": daily_limit, "reset_at": None}

    # 跨天状态过期
    if _now() >= record.reset_at + 86400:
        return {"count": 0, "limit": daily_limit, "remaining": daily_limit, "reset_at": None}

    remaining = max(0, daily_limit - record.count)
    return {
        "count": record.count,
        "limit": daily_limit,
        "remaining": remaining,
        "reset_at": record.reset_at + 86400,
    }


def reset_ip(ip: str) -> bool:
    """
    手动重置IP计数（管理接口）

    Args:
        ip: 客户端IP地址

    Returns:
        是否成功重置
    """
    if ip in _ip_records:
        del _ip_records[ip]
        return True
    return False
