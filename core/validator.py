# -*- coding: utf-8 -*-
"""
ClauseShield - 输入验证器
文件类型、内容安全、敏感词过滤
"""

import re
import os
from pathlib import Path
from typing import List, Tuple, Set

# 允许的文件扩展名白名单（小写）
_ALLOWED_EXTENSIONS: Set[str] = {".txt", ".pdf", ".doc", ".docx"}

# 敏感词基础列表（中文 + 英文，按类别分组便于维护）
_SENSITIVE_WORDS: List[str] = [
    # 暴力
    "杀人", "爆炸", "恐怖袭击", "炸弹", "枪支", "射击", "屠杀", "暴力",
    "kill", "bomb", "terrorist", "shooting", "massacre", "murder",
    # 色情
    "色情", "淫秽", "裸照", "性交易", "卖淫", "嫖娼", "av", "三级片",
    "porn", "nude", "prostitution", "sex trade", "xxx",
    # 政治
    "颠覆国家", "反动", "分裂", "暴乱", "煽动", "政变", "独裁", "专政",
    "subvert", "rebel", "secession", "insurrection", "coup",
    # 其他违法
    "毒品", "贩毒", "走私", "洗钱", "造假币", "人口贩卖", "黑客攻击",
    "drug", "trafficking", "smuggling", "money laundering", "counterfeit",
    # 垃圾内容特征
    "刷单", "传销", "诈骗", "钓鱼", " Ponzi ", "pyramid scheme",
]

# 最小有效内容比例（用于检测乱码/空文件）
_MIN_VALID_RATIO = 0.3


def get_file_extension(filename: str) -> str:
    """
    提取文件扩展名（小写）

    Args:
        filename: 文件名

    Returns:
        小写扩展名字符串
    """
    return Path(filename).suffix.lower()


def validate_file_type(filename: str) -> Tuple[bool, str]:
    """
    验证文件类型是否在白名单内

    Args:
        filename: 文件名

    Returns:
        (是否合法, 提示消息)
    """
    ext = get_file_extension(filename)
    if not ext:
        return False, "无法识别文件类型，请上传带有扩展名的文件"
    if ext not in _ALLOWED_EXTENSIONS:
        allowed = ", ".join(_ALLOWED_EXTENSIONS)
        return False, f"不支持的文件格式（{ext}），目前支持: {allowed}"
    return True, ""


def validate_content_not_empty(text: str) -> Tuple[bool, str]:
    """
    验证内容非空

    Args:
        text: 文本内容

    Returns:
        (是否合法, 提示消息)
    """
    if not text or not text.strip():
        return False, "文件内容为空或无法提取文本，请检查文件是否损坏"
    return True, ""


def _is_gibberish(text: str, sample_size: int = 500) -> bool:
    """
    快速检测文本是否为乱码/无意义内容

    策略：抽样检查可打印ASCII和常见中文字符比例

    Args:
        text: 文本内容
        sample: 抽样长度

    Returns:
        是否为乱码
    """
    sample = text[:sample_size] if len(text) > sample_size else text
    if not sample:
        return True

    total = len(sample)
    valid_chars = 0

    for ch in sample:
        # 常见有效字符范围
        if ch.isalnum() or ch.isspace():
            valid_chars += 1
        elif "\u4e00" <= ch <= "\u9fff":  # CJK统一汉字
            valid_chars += 1
        elif ch in "，。！？；：""''（）《》【】、·—–…":
            valid_chars += 1
        elif ord(ch) < 32 and ch not in "\n\r\t":
            # 控制字符过多视为乱码
            return True

    ratio = valid_chars / total if total > 0 else 0
    return ratio < _MIN_VALID_RATIO


def validate_content_readable(text: str) -> Tuple[bool, str]:
    """
    验证内容为可读文本（非乱码/非二进制垃圾）

    Args:
        text: 文本内容

    Returns:
        (是否合法, 提示消息)
    """
    if _is_gibberish(text):
        return False, "文件内容无法识别为有效文本，可能是扫描件/图片PDF或损坏文件"
    return True, ""


def check_sensitive_words(text: str) -> Tuple[bool, str, List[str]]:
    """
    检查文本是否包含敏感词

    Args:
        text: 文本内容

    Returns:
        (是否通过, 提示消息, 命中的敏感词列表)
    """
    text_lower = text.lower()
    hits: List[str] = []

    for word in _SENSITIVE_WORDS:
        if word.lower() in text_lower:
            hits.append(word)

    if hits:
        unique_hits = list(dict.fromkeys(hits))  # 去重保序
        # 最多展示5个
        display = ", ".join(unique_hits[:5])
        if len(unique_hits) > 5:
            display += f" 等 {len(unique_hits)} 个"
        return (
            False,
            f"文件内容触发敏感词过滤：{display}。请确保上传的是合法合同文本。",
            unique_hits,
        )

    return True, "", []


def validate_upload(filename: str, file_bytes: bytes, text: str) -> Tuple[bool, str]:
    """
    一站式上传验证：文件类型 + 内容安全 + 敏感词

    Args:
        filename: 文件名
        file_bytes: 原始字节（用于大小检查等）
        text: 提取后的文本

    Returns:
        (是否通过, 统一提示消息)
    """
    # 1. 文件类型
    ok, msg = validate_file_type(filename)
    if not ok:
        return False, msg

    # 2. 非空
    ok, msg = validate_content_not_empty(text)
    if not ok:
        return False, msg

    # 3. 可读性
    ok, msg = validate_content_readable(text)
    if not ok:
        return False, msg

    # 4. 敏感词
    ok, msg, _ = check_sensitive_words(text)
    if not ok:
        return False, msg

    return True, ""


def get_allowed_extensions() -> List[str]:
    """
    获取支持的文件扩展名列表

    Returns:
        扩展名列表
    """
    return sorted(_ALLOWED_EXTENSIONS)


def add_sensitive_words(words: List[str]) -> None:
    """
    动态追加敏感词（运行时扩展）

    Args:
        words: 待追加的敏感词列表
    """
    _SENSITIVE_WORDS.extend([w for w in words if w not in _SENSITIVE_WORDS])
