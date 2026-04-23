# -*- coding: utf-8 -*-
"""
ClauseShield - 兑换码批量生成工具
用于生成、管理和导出兑换码
"""

import secrets
import string
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta


import re

# 兑换码正则: PREFIX-XXXX-XXXX（支持自定义前缀）
_CODE_PATTERN = re.compile(r"^[A-Z]+-[A-Z0-9]{4}-[A-Z0-9]{4}$")


def validate_code_format(code: str) -> bool:
    """
    验证兑换码格式

    Args:
        code: 兑换码字符串

    Returns:
        格式是否合法
    """
    if not code or not isinstance(code, str):
        return False
    return bool(_CODE_PATTERN.match(code.strip().upper()))


DEFAULT_PREFIX: str = "CLAU"
DEFAULT_SEGMENTS: int = 2
DEFAULT_SEGMENT_LENGTH: int = 4
DEFAULT_MAX_USES: int = 1
DEFAULT_EXPIRY_DAYS: int = 365


def generate_single_code(
    prefix: str = DEFAULT_PREFIX,
    segments: int = DEFAULT_SEGMENTS,
    segment_length: int = DEFAULT_SEGMENT_LENGTH,
) -> str:
    """
    生成单个兑换码

    格式: PREFIX-XXXX-XXXX-XXXX，每段为字母数字混合

    Args:
        prefix: 兑换码前缀
        segments: 段数（不含前缀）
        segment_length: 每段字符数

    Returns:
        兑换码字符串
    """
    alphabet = string.ascii_uppercase + string.digits
    parts: List[str] = [prefix]

    for _ in range(segments):
        segment = "".join(secrets.choice(alphabet) for _ in range(segment_length))
        parts.append(segment)

    return "-".join(parts)


def generate_batch(
    count: int,
    prefix: str = DEFAULT_PREFIX,
    segments: int = DEFAULT_SEGMENTS,
    segment_length: int = DEFAULT_SEGMENT_LENGTH,
    max_uses: int = DEFAULT_MAX_USES,
    expiry_days: int = DEFAULT_EXPIRY_DAYS,
) -> List[Dict[str, object]]:
    """
    批量生成兑换码

    Args:
        count: 生成数量
        prefix: 兑换码前缀
        segments: 段数
        segment_length: 每段长度
        max_uses: 每个码最大使用次数
        expiry_days: 有效期（天），0表示永不过期

    Returns:
        兑换码记录列表
    """
    codes: List[Dict[str, object]] = []
    created = datetime.now().isoformat()

    expiry: Optional[str] = None
    if expiry_days > 0:
        expiry = (datetime.now() + timedelta(days=expiry_days)).isoformat()

    for _ in range(count):
        code = generate_single_code(prefix, segments, segment_length)
        record: Dict[str, object] = {
            "code": code,
            "max_uses": max_uses,
            "used_count": 0,
            "status": "unused",
            "created_at": created,
            "expires_at": expiry,
            "used_by": [],
        }
        codes.append(record)

    return codes


def export_to_json(
    codes: List[Dict[str, object]],
    output_path: str | Path,
    append: bool = False,
) -> bool:
    """
    将兑换码导出到JSON文件

    Args:
        codes: 兑换码记录列表
        output_path: 输出文件路径
        append: 是否追加到已有文件

    Returns:
        是否成功
    """
    path = Path(output_path)

    existing: List[Dict[str, object]] = []
    if append and path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            existing = data.get("codes", [])
        except Exception:
            existing = []

    all_codes = existing + codes

    payload = {
        "generated_at": datetime.now().isoformat(),
        "total": len(all_codes),
        "codes": all_codes,
    }

    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"导出失败: {e}")
        return False


def export_plain_list(
    codes: List[Dict[str, object]],
    output_path: str | Path,
) -> bool:
    """
    导出纯兑换码列表（仅码值，方便分发）

    Args:
        codes: 兑换码记录列表
        output_path: 输出文件路径

    Returns:
        是否成功
    """
    try:
        lines = [c["code"] for c in codes]
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        return True
    except Exception as e:
        print(f"导出失败: {e}")
        return False


if __name__ == "__main__":
    # CLI 用法：生成10个兑换码并导出
    import sys

    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    out_file = sys.argv[2] if len(sys.argv) > 2 else "codes_db.json"

    generated = generate_batch(count, max_uses=1, expiry_days=365)
    export_to_json(generated, out_file, append=False)
    export_plain_list(generated, out_file.replace(".json", ".txt"))

    print(f"生成 {count} 个兑换码")
    for record in generated:
        print(f"  {record['code']}")
