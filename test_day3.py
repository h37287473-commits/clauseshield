# -*- coding: utf-8 -*-
"""
ClauseShield - Day 3 功能测试脚本
验证合规包装、兑换码系统、Unicode输出修复
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def test_compliance_module():
    """测试合规包装模块"""
    print("=" * 60)
    print("测试: 合规包装模块 (compliance)")
    print("=" * 60)

    from core.compliance import (
        normalize_risk_level,
        get_standard_advice,
        generate_disclaimer,
        wrap_report_header,
        wrap_report_footer,
        normalize_risk_items,
        build_full_text_report,
    )
    from config import RiskItem, ScanReport

    # 1. 风险等级标准化
    assert normalize_risk_level("高危") == "高危"
    assert normalize_risk_level("high") == "高危"
    assert normalize_risk_level("critical") == "高危"
    assert normalize_risk_level("警告") == "警告"
    assert normalize_risk_level("medium") == "警告"
    assert normalize_risk_level("提示") == "提示"
    assert normalize_risk_level("low") == "提示"
    assert normalize_risk_level("安全") == "安全"
    assert normalize_risk_level("unknown") == "提示"  # 未知映射到提示
    print("[OK] 风险等级标准化映射正确")

    # 2. 建议模板库
    advice_ip = get_standard_advice("IP归属")
    advice_payment = get_standard_advice("付款节点")
    advice_unknown = get_standard_advice("不存在类别")
    assert "知识产权" in advice_ip
    assert "付款" in advice_payment
    assert "咨询专业律师" in advice_unknown or "建议" in advice_unknown
    print("[OK] 建议模板库返回正确")

    # 3. 免责声明生成
    disclaimer = generate_disclaimer(2, 1, 0, is_paid=True)
    assert "2 项高危风险" in disclaimer
    assert "付费用户" in disclaimer
    print("[OK] 个性化免责声明生成正确")

    disclaimer_free = generate_disclaimer(0, 0, 0, is_paid=False)
    assert "未识别到" in disclaimer_free
    print("[OK] 空结果免责声明生成正确")

    # 4. 报告头部/尾部
    report = ScanReport(
        filename="test.pdf",
        total_clauses=10,
        risk_items=[],
        high_risks=[],
        medium_risks=[],
        low_risks=[],
        scan_time=1.5,
        language="zh"
    )
    header = wrap_report_header(report)
    assert "ClauseShield" in header
    assert "test.pdf" in header
    assert "法律声明" in header
    print("[OK] 报告头部包装正确")

    footer = wrap_report_footer()
    assert "免责声明" in footer
    assert "联系方式" in footer
    print("[OK] 报告尾部包装正确")

    # 5. 风险项目标准化
    raw_items = [
        RiskItem(
            clause_text="测试", risk_level="高危", confidence=85,
            category="IP归属", description="desc", common_practice="practice", suggestion=""
        ),
        RiskItem(
            clause_text="测试2", risk_level="警告", confidence=70,
            category="付款节点", description="desc2", common_practice="practice2", suggestion="短"
        ),
    ]
    # 模拟非标准输入：通过直接修改字段绕过Pydantic验证
    import copy
    raw0 = copy.deepcopy(raw_items[0])
    raw0.risk_level = "高"  # type: ignore
    raw1 = copy.deepcopy(raw_items[1])
    raw1.risk_level = "medium"  # type: ignore
    
    normalized = normalize_risk_items([raw0, raw1])
    assert normalized[0].risk_level == "高危"
    assert normalized[1].risk_level == "警告"
    assert len(normalized[1].suggestion) > 10  # 短建议被替换为标准建议
    print("[OK] 风险项目标准化正确")

    # 6. 完整合规报告
    full_report = build_full_text_report(report, is_paid=False)
    assert "ClauseShield" in full_report
    assert "法律声明" in full_report
    assert "免责声明" in full_report
    print("[OK] 完整合规报告构建正确")

    print("[PASS] 合规包装模块测试通过\n")
    return True


def test_code_generator():
    """测试兑换码生成工具"""
    print("=" * 60)
    print("测试: 兑换码生成工具 (code_generator)")
    print("=" * 60)

    from utils.code_generator import (
        generate_single_code,
        generate_batch,
        validate_code_format,
        _CODE_PATTERN,
    )
    import re

    # 1. 单码生成
    code = generate_single_code()
    assert isinstance(code, str)
    assert len(code.split("-")) == 3  # PREFIX + 2段
    assert re.match(r"^[A-Z]+-[A-Z0-9]{4}-[A-Z0-9]{4}$", code)
    print(f"[OK] 单码生成: {code}")

    # 2. 批量生成
    batch = generate_batch(5, prefix="TEST", max_uses=3, expiry_days=30)
    assert len(batch) == 5
    assert batch[0]["max_uses"] == 3
    assert batch[0]["used_count"] == 0
    assert batch[0]["status"] == "unused"
    assert batch[0]["expires_at"] is not None
    print("[OK] 批量生成5个兑换码")

    # 3. 唯一性
    codes = [b["code"] for b in batch]
    assert len(codes) == len(set(codes))
    print("[OK] 批量生成码值唯一")

    print("[PASS] 兑换码生成工具测试通过\n")
    return True


def test_payment_module():
    """测试兑换码支付系统"""
    print("=" * 60)
    print("测试: 兑换码支付系统 (payment)")
    print("=" * 60)

    from core.payment import (
        validate_code_format,
        verify_code,
        redeem_code,
        get_code_status,
        check_free_trial,
        mark_free_trial_used,
        has_full_access,
    )

    # 1. 格式验证
    assert validate_code_format("CLAU-8X2M-9P3Q") is True
    assert validate_code_format("clau-8x2m-9p3q") is True  # 小写应通过
    assert validate_code_format("INVALID") is False
    assert validate_code_format("") is False
    assert validate_code_format("CLAU-8X2M-9P3") is False  # 长度不足
    print("[OK] 兑换码格式验证正确")

    # 2. 验证存在的码
    result = verify_code("CLAU-8X2M-9P3Q")
    if result["valid"]:
        print(f"[OK] 有效码验证通过: {result['message']}")
    else:
        print(f"[INFO] 有效码验证结果: {result['message']}（可能码未入库）")

    # 3. 验证不存在的码
    result_fake = verify_code("FAKE-0000-0000")
    assert result_fake["valid"] is False
    assert "不存在" in result_fake["message"]
    print("[OK] 无效码验证正确")

    # 4. 核销流程（使用新码）
    from utils.code_generator import generate_batch
    test_codes = generate_batch(1, prefix="TEST", max_uses=2, expiry_days=365)
    test_code = test_codes[0]["code"]

    # 导入并写入数据库
    from utils.helpers import load_json_file, save_json_file
    db_path = Path("data/codes_db.json")
    db = load_json_file(db_path)
    if "codes" not in db:
        db["codes"] = []
    db["codes"].append(test_codes[0])
    save_json_file(db_path, db)

    # 第一次核销
    r1 = redeem_code(test_code)
    assert r1["success"] is True
    assert r1["remaining"] == 1
    print(f"[OK] 第一次核销成功，剩余: {r1['remaining']}")

    # 第二次核销
    r2 = redeem_code(test_code)
    assert r2["success"] is True
    assert r2["remaining"] == 0
    print(f"[OK] 第二次核销成功，剩余: {r2['remaining']}")

    # 第三次应失败
    r3 = redeem_code(test_code)
    assert r3["success"] is False
    print("[OK] 第三次核销被拒绝（已达上限）")

    # 5. 状态查询
    status = get_code_status(test_code)
    assert status["exists"] is True
    assert status["used_count"] == 2
    print("[OK] 码状态查询正确")

    # 6. 免费试用
    fake_session = {}
    assert check_free_trial(fake_session) is True
    mark_free_trial_used(fake_session)
    assert check_free_trial(fake_session) is False
    assert has_full_access(fake_session) is True  # 已试用视为有权限
    print("[OK] 免费试用状态管理正确")

    # 7. 权限判断
    paid_session = {"code_redeemed": True}
    assert has_full_access(paid_session) is True

    empty_session = {}
    assert has_full_access(empty_session) is False
    print("[OK] 权限判断正确")

    print("[PASS] 兑换码支付系统测试通过\n")
    return True


def test_unicode_output():
    """测试Unicode输出修复"""
    print("=" * 60)
    print("测试: Unicode输出修复 (reporter)")
    print("=" * 60)

    from core.reporter import generate_text_report, _safe_text, _stdout_encoding_safe
    from config import RiskItem, ScanReport

    # 1. 构建含中文的测试报告
    risks = [
        RiskItem(
            clause_text="全部知识产权归甲方所有",
            risk_level="高危",
            confidence=85,
            category="IP归属",
            description="此条款要求乙方转让所有知识产权",
            common_practice="通常保留开源部分或分层授权",
            suggestion="建议要求修改",
        ),
        RiskItem(
            clause_text="验收合格后付款",
            risk_level="警告",
            confidence=70,
            category="付款节点",
            description="付款条件模糊",
            common_practice="应绑定可验收里程碑",
            suggestion="建议明确节点",
        ),
    ]
    report = ScanReport(
        filename="unicode_test.pdf",
        total_clauses=5,
        risk_items=risks,
        high_risks=[risks[0]],
        medium_risks=[risks[1]],
        low_risks=[],
        scan_time=2.0,
        language="zh"
    )

    # 2. 安全模式输出
    safe_report = generate_text_report(report, safe_mode=True)
    assert "[高危]" in safe_report
    assert "[警告]" in safe_report
    # 确保没有emoji残留
    assert "🚨" not in safe_report
    assert "⚠️" not in safe_report
    print("[OK] 安全模式报告不含emoji，终端兼容")

    # 3. 中文内容完整性
    assert "知识产权" in safe_report
    assert "验收合格后付款" in safe_report
    assert "ClauseShield" in safe_report
    print("[OK] 中文内容完整输出")

    # 4. _safe_text 函数
    mixed = "🚨高危⚠️警告🔍提示✅安全"
    safe = _safe_text(mixed)
    assert "🚨" not in safe
    assert "[高危]" in safe
    print("[OK] emoji替换为安全标记")

    # 5. stdout编码检测
    result = _stdout_encoding_safe()
    print(f"[OK] stdout编码检测: {'UTF-8' if result else '非UTF-8'}")

    # 6. 文件写入兼容性（模拟Windows记事本打开）
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("\ufeff")  # BOM
        f.write(safe_report)
        temp_path = f.name

    # 验证能正确读取
    with open(temp_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "ClauseShield" in content
    Path(temp_path).unlink()
    print("[OK] 带BOM的UTF-8文件写入/读取正常")

    print("[PASS] Unicode输出修复测试通过\n")
    return True


def test_compliance_integration():
    """测试合规模块与现有流水线集成"""
    print("=" * 60)
    print("测试: 合规模块集成")
    print("=" * 60)

    from core.compliance import normalize_risk_items, build_full_text_report
    from config import RiskItem, ScanReport

    # 模拟Agent输出（可能包含非标准等级）
    raw = [
        RiskItem(
            clause_text="高风险条款", risk_level="高危", confidence=90,
            category="无限责任", description="无上限赔偿", common_practice="应设上限", suggestion=""
        ),
        RiskItem(
            clause_text="中等风险", risk_level="警告", confidence=65,
            category="维护范围", description="终身维护", common_practice="12个月", suggestion="太短"
        ),
    ]
    # 修改为模拟的非标准输入
    import copy
    raw0 = copy.deepcopy(raw[0])
    raw0.risk_level = "严重"  # type: ignore
    raw1 = copy.deepcopy(raw[1])
    raw1.risk_level = "medium"  # type: ignore

    normalized = normalize_risk_items([raw0, raw1])
    assert normalized[0].risk_level == "高危"
    assert normalized[1].risk_level == "警告"
    # 空建议被补全
    assert len(normalized[0].suggestion) > 10
    print("[OK] Agent输出标准化正确")

    report = ScanReport(
        filename="integration.pdf", total_clauses=8,
        risk_items=normalized, high_risks=[normalized[0]],
        medium_risks=[normalized[1]], low_risks=[],
        scan_time=1.0, language="zh"
    )
    full = build_full_text_report(report, is_paid=False)
    assert "法律声明" in full
    assert "AI生成内容声明" in full
    print("[OK] 完整报告集成正确")

    print("[PASS] 合规模块集成测试通过\n")
    return True


def run_all_tests():
    """运行所有Day 3测试"""
    print("\n" + "=" * 60)
    print("ClauseShield Day 3 功能测试")
    print("=" * 60 + "\n")

    tests = [
        ("合规包装模块", test_compliance_module),
        ("兑换码生成工具", test_code_generator),
        ("兑换码支付系统", test_payment_module),
        ("Unicode输出修复", test_unicode_output),
        ("合规模块集成", test_compliance_integration),
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
        print("\n[OK] 所有测试通过！Day 3 功能就绪。")
    else:
        print(f"\n[WARNING] {failed} 个测试未通过，请检查。")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
