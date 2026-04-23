# -*- coding: utf-8 -*-
"""
ClauseShield - Day 2 核心流水线测试脚本
验证各模块功能是否正常
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def test_clause_splitter():
    """测试条款切分模块"""
    print("=" * 60)
    print("测试: 条款切分模块 (clause_splitter)")
    print("=" * 60)
    
    from core.clause_splitter import split_into_clauses
    
    test_text = """第一条 合同目的
本合同旨在规范双方合作关系。

第二条 付款方式
甲方应在验收合格后付款。

第三条 知识产权
全部知识产权归甲方所有。
"""
    
    clauses = split_into_clauses(test_text)
    print(f"[OK] 识别到 {len(clauses)} 个条款")
    
    for i, c in enumerate(clauses, 1):
        print(f"  条款{i}: {c.title[:20]}... (长度: {len(c.content)} 字符)")
    
    assert len(clauses) == 3, "应识别出3个条款"
    print("[PASS] 条款切分测试通过\n")
    return True


def test_pdf_extractor():
    """测试PDF提取模块（结构测试）"""
    print("=" * 60)
    print("测试: PDF提取模块 (pdf_extractor)")
    print("=" * 60)
    
    from core.pdf_extractor import extract_text_from_pdf
    
    # 测试不存在的文件
    result = extract_text_from_pdf("nonexistent.pdf")
    assert result == "", "不存在的文件应返回空字符串"
    print("[OK] 错误处理正常（不存在的文件）")
    
    # 测试非PDF文件
    result = extract_text_from_pdf("test.txt")
    assert result == "", "非PDF文件应返回空字符串"
    print("[OK] 错误处理正常（非PDF文件）")
    
    print("[PASS] PDF提取模块结构测试通过\n")
    return True


def test_config():
    """测试配置模块"""
    print("=" * 60)
    print("测试: 配置模块 (config)")
    print("=" * 60)
    
    import config
    
    print(f"[OK] APP_NAME: {config.APP_NAME}")
    print(f"[OK] HIGH_RISK_THRESHOLD: {config.HIGH_RISK_THRESHOLD}")
    print(f"[OK] MEDIUM_RISK_THRESHOLD: {config.MEDIUM_RISK_THRESHOLD}")
    print(f"[OK] FEW_SHOT_LIB存在: {config.FEW_SHOT_LIB_PATH.exists()}")
    
    assert config.HIGH_RISK_THRESHOLD == 80
    assert config.MEDIUM_RISK_THRESHOLD == 60
    print("[PASS] 配置测试通过\n")
    return True


def test_data_models():
    """测试数据模型"""
    print("=" * 60)
    print("测试: 数据模型 (Pydantic)")
    print("=" * 60)
    
    from config import RiskItem, ScanReport
    
    # 创建RiskItem
    risk = RiskItem(
        clause_text="测试条款",
        risk_level="高危",
        confidence=85,
        category="IP归属",
        description="测试描述",
        common_practice="行业常规",
        suggestion="建议关注"
    )
    print(f"[OK] RiskItem创建成功: {risk.category} [{risk.risk_level}] {risk.confidence}%")
    
    # 创建ScanReport
    report = ScanReport(
        filename="test.pdf",
        total_clauses=10,
        risk_items=[risk],
        high_risks=[risk],
        medium_risks=[],
        low_risks=[],
        scan_time=1.5,
        language="zh"
    )
    print(f"[OK] ScanReport创建成功: {len(report.risk_items)} 个风险")
    
    print("[PASS] 数据模型测试通过\n")
    return True


def test_helpers():
    """测试工具函数"""
    print("=" * 60)
    print("测试: 工具函数 (helpers)")
    print("=" * 60)
    
    from utils.helpers import truncate_text, format_confidence
    
    # 测试文本截断
    long_text = "这是一段很长的文本" * 20
    truncated = truncate_text(long_text, 50)
    assert len(truncated) <= 53  # 50 + "..."
    print(f"[OK] 文本截断: {len(long_text)} -> {len(truncated)} 字符")
    
    # 测试置信度格式化
    high = format_confidence(85)
    medium = format_confidence(70)
    low = format_confidence(50)
    print(f"[OK] 置信度格式化: {high}, {medium}, {low}")
    
    print("[PASS] 工具函数测试通过\n")
    return True


def test_agents_structure():
    """测试Agent结构"""
    print("=" * 60)
    print("测试: Agent结构")
    print("=" * 60)
    
    # 测试Agent文件是否存在
    agents_dir = Path("agents")
    expected_agents = [
        "base_agent.py",
        "ip_agent.py",
        "payment_agent.py",
        "liability_agent.py",
        "maintenance_agent.py",
        "confidentiality_agent.py",
        "noncompete_agent.py"
    ]
    
    for agent_file in expected_agents:
        path = agents_dir / agent_file
        assert path.exists(), f"Agent文件缺失: {agent_file}"
        print(f"[OK] Agent文件存在: {agent_file}")
    
    print("[PASS] Agent结构测试通过\n")
    return True


def test_prompts():
    """测试Prompt模板"""
    print("=" * 60)
    print("测试: Prompt模板")
    print("=" * 60)
    
    prompts_dir = Path("prompts")
    expected_prompts = [
        "ip_prompt.txt",
        "payment_prompt.txt",
        "liability_prompt.txt",
        "maintenance_prompt.txt",
        "confidentiality_prompt.txt",
        "noncompete_prompt.txt"
    ]
    
    for prompt_file in expected_prompts:
        path = prompts_dir / prompt_file
        assert path.exists(), f"Prompt文件缺失: {prompt_file}"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证Prompt包含必要元素
        assert "角色" in content or "角色约束" in content, f"{prompt_file} 缺少角色定义"
        assert "不提供法律建议" in content or "不做法律建议" in content, f"{prompt_file} 缺少合规声明"
        
        print(f"[OK] Prompt模板存在且合规: {prompt_file}")
    
    print("[PASS] Prompt模板测试通过\n")
    return True


def test_few_shot_lib():
    """测试Few-Shot示例库"""
    print("=" * 60)
    print("测试: Few-Shot示例库")
    print("=" * 60)
    
    import json
    from config import FEW_SHOT_LIB_PATH, FEW_SHOT_LIB_EN_PATH
    
    # 测试中文库
    with open(FEW_SHOT_LIB_PATH, 'r', encoding='utf-8') as f:
        zh_lib = json.load(f)
    
    assert "examples" in zh_lib, "中文库缺少examples字段"
    assert len(zh_lib["examples"]) > 0, "中文库示例为空"
    print(f"[OK] 中文Few-Shot库: {len(zh_lib['examples'])} 个示例")
    
    # 验证必要字段
    required_fields = ["id", "category", "risk_level", "legal_jargon", "plain_risk", "common_practice"]
    for example in zh_lib["examples"]:
        for field in required_fields:
            assert field in example, f"示例缺少字段: {field}"
    
    print(f"[OK] 所有示例包含必要字段")
    print("[PASS] Few-Shot示例库测试通过\n")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("ClauseShield Day 2 核心流水线测试")
    print("=" * 60 + "\n")
    
    tests = [
        ("配置模块", test_config),
        ("数据模型", test_data_models),
        ("条款切分", test_clause_splitter),
        ("PDF提取", test_pdf_extractor),
        ("工具函数", test_helpers),
        ("Agent结构", test_agents_structure),
        ("Prompt模板", test_prompts),
        ("Few-Shot库", test_few_shot_lib),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"[FAIL] {name} 测试失败: {e}\n")
            failed += 1
    
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"通过: {passed}/{len(tests)}")
    print(f"失败: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n[OK] 所有测试通过！Day 2 核心流水线就绪。")
    else:
        print(f"\n[WARNING] {failed} 个测试未通过，请检查。")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
