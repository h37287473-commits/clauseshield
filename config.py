# -*- coding: utf-8 -*-
"""
ClauseShield - 配置管理模块
集中管理所有环境变量和应用配置
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal, List

# 加载环境变量
load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "deepseek-v4-flash")

# 应用配置
APP_NAME = "ClauseShield"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "面向独立开发者的合同风险扫描工具"

# 扫描配置
MAX_RETRIES = 2
REQUEST_TIMEOUT = 60
TEMPERATURE = 0.3
MAX_TOKENS = 4096

# 风险分级阈值
HIGH_RISK_THRESHOLD = 80
MEDIUM_RISK_THRESHOLD = 60

# 文件路径
DATA_DIR = PROJECT_ROOT / "data"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

# Few-Shot 示例库路径
FEW_SHOT_LIB_PATH = DATA_DIR / "few_shot_lib.json"
FEW_SHOT_LIB_EN_PATH = DATA_DIR / "few_shot_lib_en.json"

# 数据模型
class RiskItem(BaseModel):
    """风险项目数据模型"""
    clause_text: str           # 条款原文
    risk_level: Literal["高危", "警告", "提示", "安全"]
    confidence: int           # 0-100
    category: str             # 风险类别
    description: str          # 白话解释
    common_practice: str      # 行业常规
    suggestion: str           # 建议关注点

class ScanReport(BaseModel):
    """扫描报告数据模型"""
    filename: str
    total_clauses: int
    risk_items: List[RiskItem]
    high_risks: List[RiskItem]      # confidence >= 80
    medium_risks: List[RiskItem]    # 60 <= confidence < 80
    low_risks: List[RiskItem]       # confidence < 60
    scan_time: float
    language: Literal["zh", "en"]

# 免责声明
DISCLAIMER = """
⚠️ **重要免责声明**

本工具仅提供合同条款的风险识别与行业惯例参考，**不构成法律建议**。
扫描结果不能替代专业律师的审查意见。在签署任何合同前，建议您咨询具有相关资质的法律专业人士。
ClauseShield 不对因使用本工具而产生的任何决策后果承担责任。
"""

# 合规约束文案
COMPLIANCE_NOTICE = """
本工具严格遵守以下原则：
1. 不提供具体法律建议或修改意见
2. 不提供维权指引或诉讼策略
3. 仅做风险提示与行业参考
"""

def validate_config() -> bool:
    """验证关键配置是否完整"""
    if not DEEPSEEK_API_KEY:
        print("❌ 错误：未设置 DEEPSEEK_API_KEY 环境变量")
        return False
    if not FEW_SHOT_LIB_PATH.exists():
        print(f"❌ 错误：Few-Shot 示例库不存在: {FEW_SHOT_LIB_PATH}")
        return False
    return True
