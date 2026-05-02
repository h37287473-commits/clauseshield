# -*- coding: utf-8 -*-
"""
ClauseShield - Streamlit应用入口
合同风险扫描SaaS工具前端（含兑换码验证）
"""

import streamlit as st
import asyncio
from pathlib import Path

import config
from core.pdf_extractor import extract_text_from_bytes
from core.scanner import scan_contract
from core.reporter import generate_report, generate_text_report
from core.payment import (
    check_free_trial,
    mark_free_trial_used,
    redeem_code,
    verify_code,
    has_full_access,
)
from core.compliance import build_full_text_report, wrap_report_header, wrap_report_footer


# 页面配置
st.set_page_config(
    page_title="ClauseShield - 合同风险扫描",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """初始化Session State"""
    if 'scan_result' not in st.session_state:
        st.session_state.scan_result = None
    if 'disclaimer_accepted' not in st.session_state:
        st.session_state.disclaimer_accepted = False
    if 'contract_text' not in st.session_state:
        st.session_state.contract_text = ""
    # 兑换码与试用状态
    if 'has_used_free_trial' not in st.session_state:
        st.session_state.has_used_free_trial = False
    if 'code_redeemed' not in st.session_state:
        st.session_state.code_redeemed = False
    if 'redeemed_code' not in st.session_state:
        st.session_state.redeemed_code = ""
    if 'show_paywall' not in st.session_state:
        st.session_state.show_paywall = False


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("# 🛡️")
        st.title("ClauseShield")
        st.caption("v1.0.0 - 独立开发者合同风险扫描")

        st.markdown("---")

        # 语言选择
        language = st.selectbox(
            "选择语言 / Language",
            options=["中文", "English"],
            index=0
        )
        lang_code = "zh" if language == "中文" else "en"

        # 文件上传
        st.markdown("### 📄 上传合同")
        uploaded_file = st.file_uploader(
            "上传PDF合同文件",
            type=['pdf'],
            help="支持PDF格式，建议文件大小不超过10MB"
        )

        # 免责声明
        st.markdown("---")
        st.markdown("### ⚠️ 免责声明")
        st.markdown(config.DISCLAIMER)

        disclaimer_accepted = st.checkbox(
            "我已阅读并理解免责声明",
            value=st.session_state.disclaimer_accepted
        )
        st.session_state.disclaimer_accepted = disclaimer_accepted

        # 兑换码状态显示
        st.markdown("---")
        st.markdown("### 🔑 访问状态")
        if st.session_state.code_redeemed:
            st.success(f"✅ 已激活: {st.session_state.redeemed_code}")
        elif st.session_state.has_used_free_trial:
            st.info("🆓 免费试用已使用")
        else:
            st.info("🆓 首次扫描免费")

        return uploaded_file, lang_code, disclaimer_accepted


def render_paywall():
    """渲染兑换码/付费墙界面"""
    st.markdown("---")
    st.subheader("🔐 查看完整报告")

    # 判断是否可试用
    can_trial = check_free_trial(st.session_state)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 选项一：兑换码")
        code_input = st.text_input(
            "输入兑换码",
            placeholder="CLAU-XXXX-XXXX-XXXX",
            key="code_input",
            help="格式: CLAU-XXXX-XXXX-XXXX"
        )

        if st.button("🔓 验证兑换码", key="btn_redeem"):
            if not code_input.strip():
                st.warning("请输入兑换码")
            else:
                result = redeem_code(code_input.strip())
                if result["success"]:
                    st.session_state.code_redeemed = True
                    st.session_state.redeemed_code = code_input.strip().upper()
                    st.success(f"✅ 兑换成功！剩余可用次数: {result['remaining']}")
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")

    with col2:
        st.markdown("#### 选项二：免费试用")
        if can_trial:
            st.info("新用户享有一次免费完整扫描体验")
            if st.button("🆓 开始免费试用", key="btn_trial"):
                mark_free_trial_used(st.session_state)
                st.success("✅ 免费试用已激活")
                st.rerun()
        else:
            st.warning("免费试用已使用，请输入兑换码查看完整报告")

    st.markdown("---")


def render_restricted_report(scan_result):
    """渲染受限版报告（仅摘要，无详情）"""
    st.markdown("### 📊 扫描摘要")
    st.info("检测到以下风险概况，查看详细分析需激活完整访问权限")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("高危风险", len(scan_result.high_risks), delta=None)
    with col2:
        st.metric("建议关注", len(scan_result.medium_risks), delta=None)
    with col3:
        st.metric("其他存疑", len(scan_result.low_risks), delta=None)

    total_risks = len(scan_result.high_risks) + len(scan_result.medium_risks) + len(scan_result.low_risks)

    if total_risks == 0:
        st.success("未检测到明显风险特征")
    elif len(scan_result.high_risks) > 0:
        st.error(f"⚠️ 发现 {len(scan_result.high_risks)} 项高危风险，建议仔细审阅合同")
    else:
        st.warning(f"发现 {total_risks} 项潜在风险，建议进一步分析")

    st.caption("提示: 激活完整权限后可查看每项风险的白话解释、行业常规和建议关注点")


def render_full_report(scan_result, uploaded_file):
    """渲染完整报告（含详情和下载）"""
    generate_report(scan_result)

    # 导出按钮
    col1, col2 = st.columns(2)
    with col1:
        text_report = generate_text_report(scan_result, safe_mode=True)
        # 添加UTF-8 BOM确保Windows记事本正确识别中文
        bom_report = "\ufeff" + text_report
        st.download_button(
            label="📥 下载文本报告",
            data=bom_report,
            file_name=f"ClauseShield_Report_{uploaded_file.name}.txt",
            mime="text/plain; charset=utf-8"
        )
    with col2:
        # 合规完整报告
        full_report = build_full_text_report(
            scan_result,
            is_paid=st.session_state.code_redeemed
        )
        bom_full = "\ufeff" + full_report
        st.download_button(
            label="📥 下载合规完整报告",
            data=bom_full,
            file_name=f"ClauseShield_FullReport_{uploaded_file.name}.txt",
            mime="text/plain; charset=utf-8"
        )


def render_main_content(uploaded_file, lang_code: str, disclaimer_accepted: bool):
    """渲染主内容区"""

    st.title("🛡️ ClauseShield 合同风险扫描")
    st.caption("专为独立开发者设计的合同风险识别工具 | 不做法律建议，仅做风险提示")

    # 合规声明
    st.info(config.COMPLIANCE_NOTICE)

    # 文件处理
    if uploaded_file is not None:
        if not disclaimer_accepted:
            st.warning("⚠️ 请先阅读并勾选侧边栏的免责声明")
            return

        # 提取文本
        with st.spinner("📖 正在提取PDF文本..."):
            contract_text = extract_text_from_bytes(
                uploaded_file.getvalue(),
                uploaded_file.name
            )

        if not contract_text:
            st.error("❌ 无法从PDF中提取文本，请检查文件是否为可读的文本PDF")
            return

        st.session_state.contract_text = contract_text

        # 显示文件信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("文件名", uploaded_file.name)
        with col2:
            st.metric("文件大小", f"{len(uploaded_file.getvalue()) / 1024:.1f} KB")
        with col3:
            st.metric("文本长度", f"{len(contract_text)} 字符")

        # 扫描按钮
        if st.button("🚀 开始扫描", type="primary", use_container_width=True):
            # 验证配置
            if not config.validate_config():
                st.error("❌ 配置验证失败，请检查环境变量和API Key")
                return

            # 执行扫描
            with st.spinner("🔍 正在并行扫描6个风险维度..."):
                progress_bar = st.progress(0)

                # 更新进度条
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i < 30:
                        st.caption("🤖 Agent 1-2: IP归属 & 付款节点扫描中...")
                    elif i < 60:
                        st.caption("🤖 Agent 3-4: 无限责任 & 维护范围扫描中...")
                    elif i < 90:
                        st.caption("🤖 Agent 5-6: 保密期限 & 竞业限制扫描中...")
                    else:
                        st.caption("📊 正在聚合报告...")

                # 运行扫描
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    scan_result = loop.run_until_complete(
                        scan_contract(
                            contract_text,
                            filename=uploaded_file.name,
                            language=lang_code
                        )
                    )
                    st.session_state.scan_result = scan_result

                except Exception as e:
                    st.error(f"❌ 扫描过程中出现错误: {e}")
                    return
                finally:
                    loop.close()

        # 显示扫描结果
        if st.session_state.scan_result:
            scan_result = st.session_state.scan_result

            # 判断是否有完整权限
            full_access = has_full_access(st.session_state)

            if full_access:
                # 完整报告
                render_full_report(scan_result, uploaded_file)
            else:
                # 受限摘要 + 付费墙
                render_restricted_report(scan_result)
                render_paywall()

    else:
        # 空状态
        st.markdown("""
        ## 欢迎使用 ClauseShield 🛡️

        **ClauseShield** 是专为独立开发者打造的合同风险扫描工具：

        ### 🎯 核心能力
        - **IP归属扫描**：识别知识产权被完全转让的风险
        - **付款节点扫描**：发现模糊付款条件和尾款陷阱
        - **无限责任扫描**：警惕无上限赔偿条款
        - **维护范围扫描**：防范终身免费维护陷阱
        - **保密期限扫描**：识别不合理的永久保密义务
        - **竞业限制扫描**：发现过度竞业限制条款

        ### 🚀 使用步骤
        1. 在侧边栏上传PDF合同文件
        2. 阅读并勾选免责声明
        3. 点击"开始扫描"按钮
        4. 查看分级风险报告

        ### ⚠️ 重要提醒
        本工具**不提供法律建议**，扫描结果仅供参考。
        在签署任何合同前，请咨询专业律师。
        """)


def render_footer():
    """渲染底部免责声明"""
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; border-left: 4px solid #f44336;">
        <h4 style="color: #c62828; margin: 0;">⚠️ 法律免责声明</h4>
        <p style="color: #c62828; margin: 10px 0 0 0;">
        本工具提供的扫描结果<b>不构成法律建议</b>，不能替代专业律师的审查意见。
        ClauseShield 仅做风险提示与行业参考，不对因使用本工具而产生的任何决策后果承担责任。
        在签署任何合同前，请务必咨询具有相关资质的法律专业人士。
        </p>
    </div>
    """, unsafe_allow_html=True)


def main():
    """主函数"""
    init_session_state()

    uploaded_file, lang_code, disclaimer_accepted = render_sidebar()
    render_main_content(uploaded_file, lang_code, disclaimer_accepted)
    render_footer()


if __name__ == "__main__":
    main()
