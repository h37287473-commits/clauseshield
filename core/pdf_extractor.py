# -*- coding: utf-8 -*-
"""
ClauseShield - PDF文本提取模块
使用pdfplumber提取PDF中的纯文本内容
"""

import pdfplumber
from pathlib import Path


def extract_text_from_pdf(file_path: str | Path) -> str:
    """
    从PDF文件中提取纯文本
    
    Args:
        file_path: PDF文件路径
        
    Returns:
        提取的纯文本字符串，失败时返回空字符串
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"⚠️ 警告：PDF文件不存在: {file_path}")
        return ""
    
    if not file_path.suffix.lower() == '.pdf':
        print(f"⚠️ 警告：文件不是PDF格式: {file_path}")
        return ""
    
    try:
        text_parts = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    print(f"⚠️ 警告：提取第{page_num}页时出错: {e}")
                    continue
        
        full_text = "\n\n".join(text_parts)
        
        if not full_text.strip():
            print("⚠️ 警告：PDF中未提取到任何文本（可能是扫描件或图片PDF）")
            return ""
        
        return full_text
        
    except Exception as e:
        print(f"⚠️ 警告：PDF解析失败: {e}")
        return ""


def extract_text_from_bytes(file_bytes: bytes, filename: str = "uploaded.pdf") -> str:
    """
    从PDF字节流中提取纯文本（用于Streamlit上传的文件）
    
    Args:
        file_bytes: PDF文件的字节流
        filename: 文件名（用于日志）
        
    Returns:
        提取的纯文本字符串，失败时返回空字符串
    """
    try:
        text_parts = []
        
        with pdfplumber.open(file_bytes) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    print(f"⚠️ 警告：提取第{page_num}页时出错: {e}")
                    continue
        
        full_text = "\n\n".join(text_parts)
        
        if not full_text.strip():
            print(f"⚠️ 警告：PDF '{filename}' 中未提取到任何文本")
            return ""
        
        return full_text
        
    except Exception as e:
        print(f"⚠️ 警告：PDF '{filename}' 解析失败: {e}")
        return ""
