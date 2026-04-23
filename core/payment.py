# -*- coding: utf-8 -*-
"""
ClauseShield - 兑换码支付系统
纯本地兑换码验证，无外部支付API依赖
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Literal
from datetime import datetime

from utils.helpers import load_json_file, save_json_file

# 兑换码正则: PREFIX-XXXX-XXXX（支持自定义前缀）
_CODE_PATTERN = re.compile(r"^[A-Z]+-[A-Z0-9]{4}-[A-Z0-9]{4}$")

CodeStatus = Literal["unused", "used", "expired"]


def _get_db_path() -> Path:
    """获取兑换码数据库路径"""
    return Path(__file__).parent.parent / "data" / "codes_db.json"


def _load_db() -> Dict:
    """加载兑换码数据库，不存在则返回空结构"""
    db_path = _get_db_path()
    data = load_json_file(db_path)
    if not data or "codes" not in data:
        return {"codes": []}
    return data


def _save_db(data: Dict) -> bool:
    """保存兑换码数据库"""
    db_path = _get_db_path()
    return save_json_file(db_path, data)


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
    # 支持带前缀和连字符的标准格式
    return bool(_CODE_PATTERN.match(code.strip().upper()))


def verify_code(code: str, user_id: Optional[str] = None) -> Dict[str, object]:
    """
    验证兑换码有效性

    Args:
        code: 兑换码
        user_id: 可选用户标识（用于追踪使用记录）

    Returns:
        验证结果字典 {valid: bool, message: str, record: dict|None}
    """
    clean_code = code.strip().upper()

    if not validate_code_format(clean_code):
        return {"valid": False, "message": "兑换码格式错误，应为 CLAU-XXXX-XXXX-XXXX", "record": None}

    db = _load_db()
    records: List[Dict] = db.get("codes", [])

    # 查找匹配的码
    record: Optional[Dict] = None
    for r in records:
        if r.get("code", "").upper() == clean_code:
            record = r
            break

    if record is None:
        return {"valid": False, "message": "兑换码不存在", "record": None}

    # 检查过期
    expires = record.get("expires_at")
    if expires:
        try:
            expiry_dt = datetime.fromisoformat(expires)
            if datetime.now() > expiry_dt:
                record["status"] = "expired"
                _save_db(db)
                return {"valid": False, "message": "兑换码已过期", "record": record}
        except Exception:
            pass

    # 检查使用次数
    max_uses = int(record.get("max_uses", 1))
    used_count = int(record.get("used_count", 0))

    if used_count >= max_uses:
        record["status"] = "used"
        _save_db(db)
        return {"valid": False, "message": "兑换码使用次数已达上限", "record": record}

    return {"valid": True, "message": "兑换码有效", "record": record}


def redeem_code(code: str, user_id: Optional[str] = None) -> Dict[str, object]:
    """
    核销兑换码（验证 + 计数 + 记录）

    Args:
        code: 兑换码
        user_id: 可选用户标识

    Returns:
        核销结果 {success: bool, message: str, remaining: int}
    """
    verification = verify_code(code, user_id)

    if not verification["valid"]:
        return {
            "success": False,
            "message": verification["message"],
            "remaining": 0,
        }

    record: Dict = verification["record"]
    max_uses = int(record.get("max_uses", 1))
    used_count = int(record.get("used_count", 0))

    # 更新使用记录
    record["used_count"] = used_count + 1
    if record["used_count"] >= max_uses:
        record["status"] = "used"

    used_by: List[str] = record.get("used_by", [])
    if user_id:
        used_by.append(f"{user_id}@{datetime.now().isoformat()}")
    else:
        used_by.append(f"anonymous@{datetime.now().isoformat()}")
    record["used_by"] = used_by

    # 写回数据库
    db = _load_db()
    for i, r in enumerate(db.get("codes", [])):
        if r.get("code", "").upper() == record["code"].upper():
            db["codes"][i] = record
            break
    _save_db(db)

    remaining = max_uses - record["used_count"]

    return {
        "success": True,
        "message": "兑换成功",
        "remaining": remaining,
    }


def get_code_status(code: str) -> Dict[str, object]:
    """
    查询兑换码状态（管理接口）

    Args:
        code: 兑换码

    Returns:
        状态信息
    """
    clean_code = code.strip().upper()
    db = _load_db()

    for r in db.get("codes", []):
        if r.get("code", "").upper() == clean_code:
            max_uses = int(r.get("max_uses", 1))
            used_count = int(r.get("used_count", 0))
            remaining = max_uses - used_count
            return {
                "exists": True,
                "code": r["code"],
                "status": r.get("status", "unused"),
                "max_uses": max_uses,
                "used_count": used_count,
                "remaining": remaining,
                "created_at": r.get("created_at"),
                "expires_at": r.get("expires_at"),
            }

    return {"exists": False, "code": clean_code}


def check_free_trial(session_state: Dict) -> bool:
    """
    检查用户是否可享受免费试用

    Args:
        session_state: Streamlit session_state 字典或等效对象

    Returns:
        是否允许免费试用
    """
    return not bool(session_state.get("has_used_free_trial", False))


def mark_free_trial_used(session_state: Dict) -> None:
    """
    标记免费试用已使用

    Args:
        session_state: Streamlit session_state 字典
    """
    session_state["has_used_free_trial"] = True
    session_state["free_trial_timestamp"] = datetime.now().isoformat()


def has_full_access(session_state: Dict) -> bool:
    """
    判断用户是否有完整访问权限（已兑换或已试用）

    Args:
        session_state: Streamlit session_state 字典

    Returns:
        是否有完整权限
    """
    if session_state.get("code_redeemed", False):
        return True
    if session_state.get("has_used_free_trial", False):
        return True
    return False
