# -*- coding: utf-8 -*-
"""
ClauseShield - 扫描调度器
并行调用6个Agent进行合同风险扫描
"""

import asyncio
import time
from typing import List
import json

from config import RiskItem, ScanReport, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD
from core.clause_splitter import split_into_clauses
from agents.ip_agent import IPAgent
from agents.payment_agent import PaymentAgent
from agents.liability_agent import LiabilityAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.confidentiality_agent import ConfidentialityAgent
from agents.noncompete_agent import NonCompeteAgent


def load_few_shot_examples(category: str, language: str = "zh") -> List[dict]:
    """
    从Few-Shot库加载指定类别的示例
    
    Args:
        category: 风险类别
        language: 语言 (zh/en)
        
    Returns:
        示例列表
    """
    import config
    
    lib_path = config.FEW_SHOT_LIB_EN_PATH if language == "en" else config.FEW_SHOT_LIB_PATH
    
    try:
        with open(lib_path, 'r', encoding='utf-8') as f:
            lib = json.load(f)
        
        examples = lib.get("examples", [])
        # 过滤匹配类别的示例
        matched = [e for e in examples if e.get("category") == category]
        
        # 如果没有精确匹配，返回前3个通用示例
        if not matched:
            matched = [e for e in examples if category in e.get("category", "")]
        
        return matched[:3]  # 最多返回3个示例
    except Exception as e:
        print(f"⚠️ 加载Few-Shot示例失败: {e}")
        return []


async def scan_contract(contract_text: str, filename: str = "", language: str = "zh") -> ScanReport:
    """
    扫描合同，并行调用6个Agent
    
    Args:
        contract_text: 合同全文
        filename: 文件名
        language: 语言 (zh/en)
        
    Returns:
        扫描报告
    """
    start_time = time.time()
    
    # 条款切分
    clauses = split_into_clauses(contract_text)
    total_clauses = len(clauses)
    
    # 初始化6个Agent
    agents = [
        IPAgent(),
        PaymentAgent(),
        LiabilityAgent(),
        MaintenanceAgent(),
        ConfidentialityAgent(),
        NonCompeteAgent()
    ]
    
    # 加载各Agent的Few-Shot示例
    agent_configs = [
        ("IP归属", agents[0]),
        ("付款节点", agents[1]),
        ("无限责任", agents[2]),
        ("维护范围", agents[3]),
        ("保密期限", agents[4]),
        ("竞业限制", agents[5]),
    ]
    
    # 构建并行任务
    tasks = []
    for category, agent in agent_configs:
        examples = load_few_shot_examples(category, language)
        task = agent.scan(contract_text, examples)
        tasks.append(task)
    
    # 并行执行所有Agent扫描
    print(f"🚀 启动6个Agent并行扫描，合同共{total_clauses}个条款...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 聚合结果
    all_risks: List[RiskItem] = []
    for i, (category, agent) in enumerate(agent_configs):
        result = results[i]
        if isinstance(result, Exception):
            print(f"❌ {category}Agent扫描异常: {result}")
            continue
        
        risks = result
        print(f"✅ {category}Agent完成，发现{len(risks)}个风险")
        all_risks.extend(risks)
    
    # 按confidence排序（降序）
    all_risks.sort(key=lambda x: x.confidence, reverse=True)
    
    # 分级
    high_risks = [r for r in all_risks if r.confidence >= HIGH_RISK_THRESHOLD]
    medium_risks = [r for r in all_risks if MEDIUM_RISK_THRESHOLD <= r.confidence < HIGH_RISK_THRESHOLD]
    low_risks = [r for r in all_risks if r.confidence < MEDIUM_RISK_THRESHOLD]
    
    scan_time = time.time() - start_time
    
    report = ScanReport(
        filename=filename,
        total_clauses=total_clauses,
        risk_items=all_risks,
        high_risks=high_risks,
        medium_risks=medium_risks,
        low_risks=low_risks,
        scan_time=scan_time,
        language=language  # type: ignore
    )
    
    print(f"\n📊 扫描完成！耗时{scan_time:.1f}秒")
    print(f"   高危风险: {len(high_risks)}个")
    print(f"   中危风险: {len(medium_risks)}个")
    print(f"   低危风险: {len(low_risks)}个")
    
    return report
