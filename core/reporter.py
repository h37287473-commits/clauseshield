# -*- coding: utf-8 -*-
"""
ClauseShield - 报告生成模块
生成结构化的风险扫描报告，兼容终端与Streamlit环境
"""

import sys
import io

try:
    import streamlit as st
    _HAS_STREAMLIT = True
except ImportError:
    _HAS_STREAMLIT = False
    st = None  # type: ignore

from config import ScanReport, RiskItem

# 终端编码安全处理：非UTF-8环境下重配置stdout
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Emoji 到纯文本的映射（用于终端安全输出）
_EMOJI_SAFE_MAP = {
    "🚨": "[高危]",
    "⚠️": "[警告]",
    "🔍": "[提示]",
    "✅": "[安全]",
    "📋": "[报告]",
    "🟠": "[橙色]",
    "🔴": "[红色]",
    "⚪": "[灰色]",
    "📄": "[原文]",
    "💡": "[解释]",
    "📊": "[行业]",
    "🎯": "[建议]",
    "🛡️": "[Shield]",
    "📥": "[下载]",
    "❌": "[错误]",
    "📖": "[读取]",
    "🚀": "[扫描]",
    "🤖": "[AI]",
    "📊": "[聚合]",
    "—": "-",  # 全角连接号兼容性处理
    "═": "=",  # 全角等号线兼容性处理
}


def _safe_text(text: str) -> str:
    """将文本中的emoji替换为终端安全标记"""
    for emoji, safe in _EMOJI_SAFE_MAP.items():
        text = text.replace(emoji, safe)
    return text


def _stdout_encoding_safe() -> bool:
    """检测stdout是否支持UTF-8输出"""
    try:
        encoding = sys.stdout.encoding
        return encoding is not None and "utf" in encoding.lower()
    except Exception:
        return False



def generate_report(scan_result: ScanReport) -> None:
    """
    在Streamlit中生成并展示风险报告

    Args:
        scan_result: 扫描结果对象
    """
    if not _HAS_STREAMLIT:
        print("[INFO] Streamlit 不可用，跳过 UI 渲染")
        return

    # 报告头部
    st.markdown("---")
    st.header("📋 扫描报告")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("高危风险", len(scan_result.high_risks), delta=None)
    with col2:
        st.metric("建议关注", len(scan_result.medium_risks), delta=None)
    with col3:
        st.metric("其他存疑", len(scan_result.low_risks), delta=None)
    
    st.caption(f"扫描耗时: {scan_result.scan_time:.1f}秒 | 识别条款: {scan_result.total_clauses}个")
    
    # 高危预警区（红色）
    if scan_result.high_risks:
        st.markdown("## 🚨 高危预警")
        for risk in scan_result.high_risks:
            _render_risk_card(risk, "high")
    
    # 建议关注区（橙色）
    if scan_result.medium_risks:
        st.markdown("## ⚠️ 建议关注")
        for risk in scan_result.medium_risks:
            _render_risk_card(risk, "medium")
    
    # 其他存疑区（灰色折叠）
    if scan_result.low_risks:
        with st.expander(f"🔍 其他存疑表述 ({len(scan_result.low_risks)}项)", expanded=False):
            for risk in scan_result.low_risks:
                _render_risk_card(risk, "low")
    
    # 无风险提示
    if not scan_result.risk_items:
        st.success("✅ 未检测到明显风险条款，但建议人工复核确认。")


def _render_risk_card(risk: RiskItem, level: str) -> None:
    """
    渲染单条风险卡片
    
    Args:
        risk: 风险项目
        level: 风险级别 (high/medium/low)
    """
    # 根据级别设置颜色
    color_map = {
        "high": "🔴",
        "medium": "🟠", 
        "low": "⚪"
    }
    
    icon = color_map.get(level, "⚪")
    
    with st.container():
        st.markdown(f"""
        <div style="border-left: 4px solid {'#ff4b4b' if level=='high' else '#ffa500' if level=='medium' else '#808080'}; 
                    padding-left: 10px; margin: 10px 0;">
            <h4>{icon} {risk.category} <span style="color: {'#ff4b4b' if level=='high' else '#ffa500' if level=='medium' else '#808080'}">[{risk.risk_level}]</span></h4>
        </div>
        """, unsafe_allow_html=True)
        
        # 展开显示详情
        with st.expander(f"查看详情 - 置信度: {risk.confidence}%", expanded=(level == "high")):
            st.markdown(f"**📄 原文片段：**")
            st.code(risk.clause_text[:300], language=None)
            
            st.markdown(f"**💡 白话解释：**")
            st.write(risk.description)
            
            st.markdown(f"**📊 行业常规：**")
            st.info(risk.common_practice)
            
            st.markdown(f"**🎯 建议关注：**")
            st.write(risk.suggestion)
            
            st.caption(f"置信度: {risk.confidence}% | 类别: {risk.category}")
        
        st.markdown("---")


def generate_text_report(scan_result: ScanReport, safe_mode: bool = True) -> str:
    """
    生成文本格式的报告（用于导出和终端显示）

    Args:
        scan_result: 扫描结果
        safe_mode: 是否启用终端安全模式（替换emoji为纯文本标记）

    Returns:
        文本报告
    """
    lines = []
    lines.append("=" * 60)
    lines.append("ClauseShield 合同风险扫描报告")
    lines.append("=" * 60)
    lines.append(f"文件名: {scan_result.filename}")
    lines.append(f"识别条款: {scan_result.total_clauses}个")
    lines.append(f"扫描耗时: {scan_result.scan_time:.1f}秒")
    lines.append("")

    # 高危风险
    if scan_result.high_risks:
        lines.append(f"[高危] 高危风险 ({len(scan_result.high_risks)}项)")
        lines.append("-" * 40)
        for risk in scan_result.high_risks:
            lines.append(f"[{risk.category}] {risk.risk_level} (置信度: {risk.confidence}%)")
            lines.append(f"原文: {risk.clause_text[:200]}")
            lines.append(f"风险: {risk.description}")
            lines.append("")

    # 中危风险
    if scan_result.medium_risks:
        lines.append(f"[警告] 建议关注 ({len(scan_result.medium_risks)}项)")
        lines.append("-" * 40)
        for risk in scan_result.medium_risks:
            lines.append(f"[{risk.category}] {risk.risk_level} (置信度: {risk.confidence}%)")
            lines.append(f"原文: {risk.clause_text[:200]}")
            lines.append("")

    # 低危风险
    if scan_result.low_risks:
        lines.append(f"[提示] 其他存疑 ({len(scan_result.low_risks)}项)")
        lines.append("-" * 40)
        for risk in scan_result.low_risks:
            lines.append(f"[{risk.category}] {risk.risk_level} (置信度: {risk.confidence}%)")
            lines.append("")

    lines.append("=" * 60)
    lines.append("[声明] 免责声明：本报告仅供参考，不构成法律建议。")
    lines.append("=" * 60)

    report_text = "\n".join(lines)

    if safe_mode:
        report_text = _safe_text(report_text)

    return report_text
