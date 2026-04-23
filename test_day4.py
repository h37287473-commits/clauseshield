# -*- coding: utf-8 -*-
"""
ClauseShield - Day 4 功能测试脚本
验证防刷模块（rate_limiter + validator）及冷启动文件完整性
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_rate_limiter():
    """测试频率限制模块"""
    print("=" * 60)
    print("测试: 频率限制模块 (rate_limiter)")
    print("=" * 60)

    from core.rate_limiter import (
        check_ip_limit,
        record_scan,
        check_file_size,
        check_content_length,
        get_ip_status,
        reset_ip,
        DEFAULT_DAILY_LIMIT,
        DEFAULT_FILE_MAX_MB,
        DEFAULT_CONTENT_MAX_CHARS,
    )

    test_ip = "192.168.1.100"

    # 1. 新IP首次访问
    ok, msg, remaining = check_ip_limit(test_ip, daily_limit=3)
    assert ok is True
    assert remaining == 2  # 3限制-1已用=2
    assert "还可扫描" in msg
    print(f"[OK] 新IP首次访问: 允许, 剩余 {remaining}")

    # 2. 连续访问至超限
    ok2, _, remaining2 = check_ip_limit(test_ip, daily_limit=3)
    assert ok2 is True
    assert remaining2 == 1
    ok3, _, remaining3 = check_ip_limit(test_ip, daily_limit=3)
    assert ok3 is True
    assert remaining3 == 0
    ok4, msg4, remaining4 = check_ip_limit(test_ip, daily_limit=3)
    assert ok4 is False
    assert remaining4 == 0
    assert "今日扫描次数已用完" in msg4
    assert "兑换码" in msg4
    print("[OK] 超限后正确拒绝并提示兑换码")

    # 3. 空IP不限制
    ok_empty, _, _ = check_ip_limit("")
    assert ok_empty is True
    print("[OK] 空IP不触发限制")

    # 4. 手动重置
    reset_ip(test_ip)
    status = get_ip_status(test_ip, daily_limit=3)
    assert status["count"] == 0
    assert status["remaining"] == 3
    print("[OK] 手动重置IP计数正确")

    # 5. 文件大小检查
    small_bytes = b"x" * (5 * 1024 * 1024)  # 5 MB
    ok_size, _ = check_file_size(small_bytes, max_mb=10)
    assert ok_size is True

    large_bytes = b"x" * (11 * 1024 * 1024)  # 11 MB
    ok_size2, msg_size = check_file_size(large_bytes, max_mb=10)
    assert ok_size2 is False
    assert "11.0 MB" in msg_size
    assert "最大支持 10 MB" in msg_size
    print("[OK] 文件大小限制正确")

    # 6. 内容长度检查
    short_text = "a" * 1000
    ok_len, _ = check_content_length(short_text, max_chars=50000)
    assert ok_len is True

    long_text = "b" * 50001
    ok_len2, msg_len = check_content_length(long_text, max_chars=50000)
    assert ok_len2 is False
    assert "50001" in msg_len
    assert "最大支持 50000" in msg_len
    print("[OK] 内容长度限制正确")

    # 7. 状态查询
    reset_ip("status_test_ip")
    ok_s, _, _ = check_ip_limit("status_test_ip", daily_limit=5)
    assert ok_s is True
    st = get_ip_status("status_test_ip", daily_limit=5)
    assert st["count"] == 1
    assert st["limit"] == 5
    assert st["remaining"] == 4
    print("[OK] IP状态查询正确")

    # 8. record_scan 显式计数
    reset_ip("record_test_ip")
    record_scan("record_test_ip")
    record_scan("record_test_ip")
    st2 = get_ip_status("record_test_ip", daily_limit=5)
    assert st2["count"] == 2
    print("[OK] 显式记录扫描正确")

    print("[PASS] 频率限制模块测试通过\n")
    return True


def test_validator():
    """测试输入验证模块"""
    print("=" * 60)
    print("测试: 输入验证模块 (validator)")
    print("=" * 60)

    from core.validator import (
        validate_file_type,
        validate_content_not_empty,
        validate_content_readable,
        check_sensitive_words,
        validate_upload,
        get_allowed_extensions,
        add_sensitive_words,
    )

    # 1. 文件类型白名单
    assert validate_file_type("contract.txt")[0] is True
    assert validate_file_type("contract.pdf")[0] is True
    assert validate_file_type("contract.doc")[0] is True
    assert validate_file_type("contract.docx")[0] is True
    assert validate_file_type("contract.png")[0] is False
    assert validate_file_type("contract.exe")[0] is False
    assert validate_file_type("contract")[0] is False
    print("[OK] 文件类型白名单正确")

    # 2. 非空验证
    assert validate_content_not_empty("有效内容")[0] is True
    assert validate_content_not_empty("")[0] is False
    assert validate_content_not_empty("   ")[0] is False
    print("[OK] 非空验证正确")

    # 3. 可读性验证
    readable = "本合同由甲方与乙方于2024年签署，约定软件开发事项。"
    assert validate_content_readable(readable)[0] is True

    # 纯乱码应被拒绝
    gibberish = "\x00\x01\x02\x03\x04\x05" * 100
    ok_gib, msg_gib = validate_content_readable(gibberish)
    assert ok_gib is False
    assert "无法识别" in msg_gib
    print("[OK] 可读性验证正确")

    # 4. 敏感词检测
    safe_text = "本合同为一般商业软件开发协议，双方本着平等自愿原则签署。"
    ok_sw, msg_sw, hits_sw = check_sensitive_words(safe_text)
    assert ok_sw is True
    assert hits_sw == []

    bad_text = "本文件涉及色情内容和炸弹制造方法，用于恐怖袭击策划。"
    ok_sw2, msg_sw2, hits_sw2 = check_sensitive_words(bad_text)
    assert ok_sw2 is False
    assert len(hits_sw2) >= 3
    assert "触发敏感词" in msg_sw2
    print(f"[OK] 敏感词检测正确，命中: {hits_sw2}")

    # 5. 一站式上传验证
    ok_up, _ = validate_upload("test.pdf", b"pdf content", "正常合同内容")
    assert ok_up is True

    ok_up2, msg_up2 = validate_upload("test.png", b"png", "正常内容")
    assert ok_up2 is False
    assert "不支持的文件格式" in msg_up2

    ok_up3, msg_up3 = validate_upload("test.txt", b"txt", "")
    assert ok_up3 is False
    assert "内容为空" in msg_up3

    bad_upload_text = "本文包含杀人炸弹恐怖袭击内容"
    ok_up4, msg_up4 = validate_upload("test.txt", b"txt", bad_upload_text)
    assert ok_up4 is False
    assert "触发敏感词" in msg_up4
    print("[OK] 一站式上传验证正确")

    # 6. 扩展名列表
    exts = get_allowed_extensions()
    assert ".txt" in exts
    assert ".pdf" in exts
    assert ".png" not in exts
    print("[OK] 扩展名列表正确")

    # 7. 动态追加敏感词
    add_sensitive_words(["新增敏感词TEST"])
    ok_dyn, _, hits_dyn = check_sensitive_words("这句话包含新增敏感词TEST")
    assert ok_dyn is False
    assert "新增敏感词TEST" in hits_dyn
    print("[OK] 动态追加敏感词正确")

    print("[PASS] 输入验证模块测试通过\n")
    return True


def test_cold_start_files():
    """测试冷启动物料文件完整性"""
    print("=" * 60)
    print("测试: 冷启动物料文件完整性")
    print("=" * 60)

    root = Path(__file__).parent

    files_to_check = [
        ("README.md", ["ClauseShield", "简介", "技术栈", "免责声明", "MIT"]),
        (".gitignore", ["__pycache__", ".env", "venv/"]),
        ("LICENSE", ["MIT License", "Copyright"]),
        ("docs/FAQ.md", ["免费", "支持什么格式", "准确率", "数据安全"]),
        ("docs/CHANGELOG.md", ["0.1.0", "MVP"]),
        ("docs/wechat_setup.md", ["微信公众号", "扫描", "兑换"]),
        (".github/ISSUE_TEMPLATE/bug_report.md", ["Bug", "复现步骤"]),
        (".github/ISSUE_TEMPLATE/feature_request.md", ["Feature", "动机"]),
        ("assets/landing/screenshot_main.png", ["待替换为真实截图", "主界面"]),
        ("assets/landing/screenshot_report.png", ["待替换为真实截图", "报告"]),
    ]

    for filepath, expected_snippets in files_to_check:
        full_path = root / filepath
        assert full_path.exists(), f"文件不存在: {filepath}"
        content = full_path.read_text(encoding="utf-8")
        for snippet in expected_snippets:
            assert snippet in content, f"{filepath} 缺少内容: '{snippet}'"
        print(f"[OK] {filepath} 存在且内容完整")

    print("[PASS] 冷启动物料文件完整性测试通过\n")
    return True


def test_code_style():
    """测试代码规范：docstring + 类型注解"""
    print("=" * 60)
    print("测试: 代码规范 (docstring + 类型注解)")
    print("=" * 60)

    import ast
    import inspect

    from core import rate_limiter, validator

    modules = [rate_limiter, validator]

    for mod in modules:
        source = inspect.getsource(mod)
        tree = ast.parse(source)

        # 检查模块级 docstring
        assert ast.get_docstring(tree) is not None, f"{mod.__name__} 缺少模块 docstring"
        print(f"[OK] {mod.__name__} 模块 docstring 存在")

        # 检查函数定义
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name
                # 跳过私有函数（不要求docstring的，但这里要求）
                if func_name.startswith("_"):
                    continue

                # 检查 docstring
                doc = ast.get_docstring(node)
                assert doc is not None, f"{mod.__name__}.{func_name} 缺少 docstring"

                # 检查是否有返回类型注解（返回 annotation 存在，或为 None）
                # 至少检查 args 有 annotation 或返回有 annotation
                has_annotations = False
                if node.returns is not None:
                    has_annotations = True
                for arg in node.args.args + node.args.kwonlyargs:
                    if arg.annotation is not None:
                        has_annotations = True
                        break
                assert has_annotations, f"{mod.__name__}.{func_name} 缺少类型注解"

        print(f"[OK] {mod.__name__} 所有公开函数具备 docstring 和类型注解")

    print("[PASS] 代码规范测试通过\n")
    return True


def test_integration_rate_limit_with_validator():
    """测试防刷模块与现有流水线的集成"""
    print("=" * 60)
    print("测试: 防刷模块集成")
    print("=" * 60)

    from core.rate_limiter import check_ip_limit, check_file_size, check_content_length
    from core.validator import validate_upload

    # 模拟一次完整上传前的验证链
    filename = "test_contract.txt"
    file_bytes = b"This is a valid contract text content." * 100
    text = file_bytes.decode("utf-8")

    # Step 1: 上传验证
    ok_upload, msg_upload = validate_upload(filename, file_bytes, text)
    assert ok_upload is True, f"上传验证失败: {msg_upload}"
    print("[OK] 上传验证通过")

    # Step 2: 文件大小
    ok_size, msg_size = check_file_size(file_bytes, max_mb=10)
    assert ok_size is True
    print("[OK] 文件大小检查通过")

    # Step 3: 内容长度
    ok_len, msg_len = check_content_length(text, max_chars=50000)
    assert ok_len is True
    print("[OK] 内容长度检查通过")

    # Step 4: IP限流
    ok_ip, msg_ip, remaining = check_ip_limit("integration_test_ip", daily_limit=5)
    assert ok_ip is True
    print(f"[OK] IP限流检查通过，剩余 {remaining} 次")

    print("[PASS] 防刷模块集成测试通过\n")
    return True


def run_all_tests():
    """运行所有 Day 4 测试"""
    print("\n" + "=" * 60)
    print("ClauseShield Day 4 功能测试")
    print("=" * 60 + "\n")

    tests = [
        ("频率限制模块", test_rate_limiter),
        ("输入验证模块", test_validator),
        ("冷启动物料文件完整性", test_cold_start_files),
        ("代码规范", test_code_style),
        ("防刷模块集成", test_integration_rate_limit_with_validator),
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
        print("\n[OK] 所有测试通过！Day 4 功能就绪。")
    else:
        print(f"\n[WARNING] {failed} 个测试未通过，请检查。")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
