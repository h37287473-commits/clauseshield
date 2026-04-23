# -*- coding: utf-8 -*-
"""
ClauseShield - 合规包装模块
法律免责声明生成、风险等级标准化、报告格式化
"""

from typing import Dict, List, Literal
from datetime import datetime

from config import RiskItem, ScanReport

# 风险等级四级标准化
RiskLevel = Literal["高危", "警告", "提示", "安全"]

# 风险等级映射表：统一各类输入为标准四级
_RISK_LEVEL_MAP: Dict[str, RiskLevel] = {
    "高危": "高危", "高": "高危", "high": "高危", "critical": "高危",
    "严重": "高危", "严重风险": "高危", "severe": "高危", "致命": "高危",
    "警告": "警告", "中": "警告", "medium": "警告", "warn": "警告",
    "warning": "警告", "中度": "警告", "中危": "警告", "注意": "警告",
    "提示": "提示", "低": "提示", "low": "提示", "info": "提示",
    "information": "提示", "轻微": "提示", "低危": "提示", "存疑": "提示",
    "安全": "安全", "无风险": "安全", "safe": "安全", "none": "安全",
    "正常": "安全", "ok": "安全", "good": "安全", "pass": "安全",
}

# 建议模板库
_ADVICE_TEMPLATES: Dict[str, str] = {
    "IP归属": "建议要求明确约定交付物的知识产权归属，避免默认全部转让。如项目涉及核心代码库，建议保留开源许可或分层授权。",
    "付款节点": "建议将付款与可验收的里程碑绑定，避免'验收合格后付款'等模糊表述。尾款比例建议不低于合同总额的30%。",
    "无限责任": "建议设置赔偿上限（如不超过合同总额），并要求甲方同步承担对等责任。终身担保条款应明确截止条件。",
    "维护范围": "建议明确维护期起止时间、响应级别和超出范围的收费标准。终身免费维护应改为有限期（如12个月）。",
    "保密期限": "建议保密期限与项目周期挂钩，项目终止后12-24个月即可。永久保密义务对独立开发者负担过重。",
    "竞业限制": "建议将竞业限制限定在直接竞争产品范围内，并明确补偿金额。未约定补偿的竞业限制条款效力存疑。",
    "default": "建议仔细审阅该条款，必要时咨询专业律师获取针对性意见。",
}

# 报告头部模板
_REPORT_HEADER = """ClauseShield 合同风险扫描报告
═══════════════════════════════════════════════════════

生成时间: {timestamp}
扫描文件: {filename}
条款总数: {total_clauses} 条
扫描耗时: {scan_time:.1f} 秒

【法律声明】
本报告由 ClauseShield AI 系统自动生成，仅供合同审阅参考之用。
本报告不构成任何形式的法律意见、法律建议或法律分析，不可替代
具有执业资质的律师对合同文本的专业审查。
ClauseShield 不对因使用本报告而产生的任何直接或间接后果承担责任。
在签署任何具有法律约束力的合同文件前，强烈建议您咨询专业律师。

═══════════════════════════════════════════════════════
"""

# 报告尾部模板
_REPORT_FOOTER = """
═══════════════════════════════════════════════════════

【报告说明】
- 高危: 置信度 ≥80%，强烈建议重点关注并考虑修改条款
- 警告: 置信度 60-79%，建议结合项目实际情况评估风险
- 提示: 置信度 <60%，属于存疑表述，建议人工复核确认
- 安全: 未发现明显风险特征

【联系方式】
如有疑问，请通过以下方式联系：
- 邮箱: [support@clauseshield.app]（占位符）
- 网站: [https://clauseshield.app]（占位符）

【免责声明】
ClauseShield 是一款面向独立开发者的合同风险扫描辅助工具。
本工具仅基于行业惯例和公开案例进行风险提示，不保证扫描结果的
完整性、准确性或时效性。用户应独立判断并承担使用本工具的全部
责任。ClauseShield 及其开发方不对任何因使用本服务导致的损失
或纠纷承担法律责任。

报告生成时间: {timestamp}
ClauseShield v{version} | 独立开发者合同风险扫描
"""


def normalize_risk_level(raw_level: str) -> RiskLevel:
    """
    将各Agent输出的风险等级统一映射为四级标准

    Args:
        raw_level: 原始风险等级字符串

    Returns:
        标准化后的风险等级
    """
    key = raw_level.strip().lower()
    return _RISK_LEVEL_MAP.get(key, "提示")


def get_standard_advice(category: str) -> str:
    """
    根据风险类别获取标准化建议话术

    Args:
        category: 风险类别名称

    Returns:
        标准化建议文本
    """
    return _ADVICE_TEMPLATES.get(category, _ADVICE_TEMPLATES["default"])


def generate_disclaimer(
    high_count: int,
    medium_count: int,
    low_count: int,
    is_paid: bool = False
) -> str:
    """
    根据扫描结果生成个性化免责声明

    Args:
        high_count: 高危风险数量
        medium_count: 警告风险数量
        low_count: 提示风险数量
        is_paid: 是否为付费用户（影响免责强度措辞）

    Returns:
        个性化免责声明文本
    """
    total = high_count + medium_count + low_count

    if total == 0:
        risk_summary = "本次扫描未识别到明显风险特征，但这不代表合同完全安全无虞。"
    elif high_count > 0:
        risk_summary = f"本次扫描识别到 {high_count} 项高危风险、{medium_count} 项警告风险和 {low_count} 项提示风险。"
    else:
        risk_summary = f"本次扫描识别到 {medium_count} 项警告风险和 {low_count} 项提示风险，未发现高危风险。"

    if is_paid:
        tier_note = "您是付费用户，本次扫描已启用完整风险库。"
    else:
        tier_note = "本次扫描为免费试用版本，仅展示基础风险提示。"

    disclaimer = f"""
【AI生成内容声明】
{risk_summary}
{tier_note}

本报告由人工智能系统生成，其分析基于训练数据和行业公开案例。
AI系统可能存在误判、遗漏或对特定语境理解不足的情况。
本报告的每一条结论都应经过具有法律专业背景的人员复核验证。
ClauseShield 明确声明：不对本报告的内容准确性、完整性或适用性
提供任何明示或暗示的担保。用户使用本报告即视为已知悉并接受
上述全部声明与限制。
"""
    return disclaimer.strip()


def wrap_report_header(scan_result: ScanReport, version: str = "1.0.0") -> str:
    """
    生成报告头部包装文本

    Args:
        scan_result: 扫描结果对象
        version: 应用版本号

    Returns:
        格式化后的报告头部
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return _REPORT_HEADER.format(
        timestamp=timestamp,
        filename=scan_result.filename,
        total_clauses=scan_result.total_clauses,
        scan_time=scan_result.scan_time,
        version=version,
    )


def wrap_report_footer(version: str = "1.0.0") -> str:
    """
    生成报告尾部包装文本

    Args:
        version: 应用版本号

    Returns:
        格式化后的报告尾部
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return _REPORT_FOOTER.format(
        timestamp=timestamp,
        version=version,
    )


def normalize_risk_items(risk_items: List[RiskItem]) -> List[RiskItem]:
    """
    批量标准化风险项目：统一风险等级并补充标准化建议

    Args:
        risk_items: 原始风险项目列表

    Returns:
        标准化后的风险项目列表
    """
    normalized: List[RiskItem] = []

    for item in risk_items:
        std_level = normalize_risk_level(item.risk_level)
        std_advice = get_standard_advice(item.category)

        # 如果原始建议为空或过于简短，替换为标准建议
        suggestion = item.suggestion
        if not suggestion or len(suggestion.strip()) < 10:
            suggestion = std_advice

        normalized.append(RiskItem(
            clause_text=item.clause_text,
            risk_level=std_level,  # type: ignore
            confidence=item.confidence,
            category=item.category,
            description=item.description,
            common_practice=item.common_practice,
            suggestion=suggestion,
        ))

    return normalized


def build_full_text_report(scan_result: ScanReport, is_paid: bool = False) -> str:
    """
    构建完整的合规包装文本报告

    Args:
        scan_result: 扫描结果
        is_paid: 是否为付费用户

    Returns:
        完整合规报告文本
    """
    lines: List[str] = []
    lines.append(wrap_report_header(scan_result))
    lines.append("")

    # 风险统计
    high = len(scan_result.high_risks)
    medium = len(scan_result.medium_risks)
    low = len(scan_result.low_risks)

    lines.append(f"[风险统计] 高危: {high} | 警告: {medium} | 提示: {low}")
    lines.append("")

    # 风险详情
    if scan_result.risk_items:
        lines.append("【风险详情】")
        for item in scan_result.risk_items:
            level_icon = {"高危": "[!]", "警告": "[~]", "提示": "[?]"}.get(item.risk_level, "[?]")
            lines.append(f"{level_icon} [{item.category}] {item.risk_level} (置信度: {item.confidence}%)")
            lines.append(f"   原文: {item.clause_text[:120]}")
            lines.append(f"   说明: {item.description}")
            lines.append(f"   建议: {item.suggestion}")
            lines.append("")
    else:
        lines.append("【风险详情】未发现明显风险条款。")
        lines.append("")

    # 个性化免责声明
    lines.append(generate_disclaimer(high, medium, low, is_paid))
    lines.append("")

    lines.append(wrap_report_footer())

    return "\n".join(lines)
