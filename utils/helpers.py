# -*- coding: utf-8 -*-
"""
ClauseShield - 工具函数
通用辅助函数
"""

import json
from pathlib import Path


def load_json_file(file_path: str | Path) -> dict:
    """
    加载JSON文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        JSON字典，失败时返回空字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载JSON文件失败: {e}")
        return {}


def save_json_file(file_path: str | Path, data: dict) -> bool:
    """
    保存JSON文件
    
    Args:
        file_path: 文件路径
        data: 数据字典
        
    Returns:
        是否成功
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"⚠️ 保存JSON文件失败: {e}")
        return False


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原文本
        max_length: 最大长度
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def format_confidence(confidence: int) -> str:
    """
    格式化置信度显示
    
    Args:
        confidence: 置信度值 (0-100)
        
    Returns:
        格式化字符串
    """
    if confidence >= 80:
        return f"🔴 {confidence}% (高危)"
    elif confidence >= 60:
        return f"🟠 {confidence}% (关注)"
    else:
        return f"⚪ {confidence}% (存疑)"
