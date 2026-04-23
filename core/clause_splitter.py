# -*- coding: utf-8 -*-
"""
ClauseShield - 条款切分模块
基于标题正则表达式将合同文本切分为独立条款
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class Clause:
    """合同条款数据结构"""
    title: str          # 条款标题
    content: str        # 条款正文
    position: int       # 原始位置（字符偏移量）
    index: int          # 条款序号


def split_into_clauses(text: str) -> List[Clause]:
    """
    基于常见标题模式将合同文本切分为条款列表
    
    支持的标题模式：
    - 中文数字标题：第一条、第1条、第X章
    - 英文标题：Article X, Section X
    - 数字标题：1. / 1.1 / (1)
    - 粗体/特殊标记标题
    
    Args:
        text: 合同纯文本
        
    Returns:
        条款对象列表
    """
    if not text or not text.strip():
        return []
    
    # 定义标题匹配正则表达式（按优先级排序）
    title_patterns = [
        # 中文：第X条、第X章、第X节
        r'(?:^|\n)\s*第[一二三四五六七八九十百千万\d]+[条章节]\s*[：:.．]?\s*[^\n]*',
        # 英文：Article X, Section X
        r'(?:^|\n)\s*(?:Article|Section|Clause)\s+[IVX\d]+[.:\s][^\n]*',
        # 数字标题：1. / 1.1 / (1)
        r'(?:^|\n)\s*\d+[.．]\d*[\s.．]*[^\n]{2,50}',
        # 中文数字+顿号：一、/ （一）
        r'(?:^|\n)\s*[（(]?[一二三四五六七八九十][）)]?\s*[、.．][^\n]{2,50}',
    ]
    
    # 合并所有模式
    combined_pattern = '|'.join(f'({p})' for p in title_patterns)
    
    # 查找所有匹配的标题位置
    matches = list(re.finditer(combined_pattern, text, re.IGNORECASE | re.MULTILINE))
    
    if not matches:
        # 如果没有找到标题，将整个文本作为一个条款返回
        return [Clause(
            title="全文",
            content=text.strip(),
            position=0,
            index=0
        )]
    
    clauses = []
    
    for i, match in enumerate(matches):
        title = match.group().strip()
        position = match.start()
        
        # 确定条款内容的结束位置
        if i + 1 < len(matches):
            content_end = matches[i + 1].start()
        else:
            content_end = len(text)
        
        # 提取内容（排除标题本身）
        content = text[position + len(title):content_end].strip()
        
        # 清理标题中的换行符
        title = re.sub(r'\s+', ' ', title).strip()
        
        clauses.append(Clause(
            title=title,
            content=content,
            position=position,
            index=i
        ))
    
    return clauses


def get_clauses_text(clauses: List[Clause]) -> str:
    """
    将条款列表合并为文本（用于Agent扫描）
    
    Args:
        clauses: 条款列表
        
    Returns:
        合并后的文本
    """
    parts = []
    for clause in clauses:
        parts.append(f"【{clause.title}】\n{clause.content}")
    return "\n\n".join(parts)


def find_clause_by_text(clauses: List[Clause], text_fragment: str) -> Clause | None:
    """
    根据文本片段查找对应的条款
    
    Args:
        clauses: 条款列表
        text_fragment: 文本片段
        
    Returns:
        匹配的条款或None
    """
    for clause in clauses:
        if text_fragment in clause.content or text_fragment in clause.title:
            return clause
    return None
