# -*- coding: utf-8 -*-
"""
ClauseShield 合同风险扫描工具

专为独立开发者设计的 AI 驱动合同风险识别 SaaS。

<p align="center">
  <img src="assets/landing/screenshot_main.png" alt="主界面" width="700">
</p>

---

## 简介

**ClauseShield** 通过并行调用 6 个专业 AI Agent，在数秒内扫描合同中的常见风险点：

| Agent | 扫描目标 |
|-------|---------|
| IP归属 | 知识产权被完全转让 |
| 付款节点 | 模糊付款条件、尾款陷阱 |
| 无限责任 | 无上限赔偿、终身担保 |
| 维护范围 | 终身免费维护、模糊响应级别 |
| 保密期限 | 永久保密义务 |
| 竞业限制 | 过度竞业限制、无补偿条款 |

扫描结果按 **高危 / 警告 / 提示 / 安全** 四级分级，附带白话解释与行业常规参考。

> ⚠️ **免责声明**：ClauseShield 仅做风险提示与行业参考，**不构成法律建议**。签署合同前请咨询专业律师。

---

## 功能截图

### 主界面

<p align="center">
  <img src="assets/landing/screenshot_main.png" alt="主界面截图" width="700">
</p>

*（待替换为真实截图）*

### 扫描报告

<p align="center">
  <img src="assets/landing/screenshot_report.png" alt="报告截图" width="700">
</p>

*（待替换为真实截图）*

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/yourname/clauseshield.git
cd clauseshield
```

### 2. 安装依赖

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY
```

### 4. 启动应用

```bash
streamlit run main.py
```

### 5. 运行测试

```bash
python test_day2.py   # Day 2 核心流水线测试
python test_day3.py   # Day 3 合规 + 兑换码测试
python test_day4.py   # Day 4 防刷 + 验证测试
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Streamlit |
| 后端 | Python 3.14 |
| AI 模型 | DeepSeek API |
| 数据 | Pydantic, JSON |
| 文档提取 | pdfplumber |
| 支付 | 本地兑换码系统（零外部依赖） |

---

## 项目结构

```
clauseshield/
├── agents/              # 6个专业扫描Agent
├── core/                # 扫描引擎 + 合规包装 + 支付 + 防刷
│   ├── scanner.py       # 并行调度
│   ├── compliance.py    # 合规报告包装
│   ├── payment.py       # 兑换码支付
│   ├── rate_limiter.py  # 频率限制
│   └── validator.py     # 输入验证
├── ui/                  # Streamlit UI组件（预留）
├── utils/               # 辅助工具
├── data/                # Few-Shot库 + 兑换码数据库
├── prompts/             # Agent提示词模板
├── docs/                # 文档与FAQ
├── assets/landing/      # 截图与宣传物料
├── main.py              # 应用入口
└── config.py            # 全局配置
```

---

## 核心特性

- **6 Agent 并行扫描**：异步调度，3-5 秒出结果
- **Few-Shot 增强**：内置中英文示例库，提升识别准确率
- **兑换码付费**：纯本地兑换码系统，无支付 API 依赖
- **分级风险报告**：高危/警告/提示/安全四级可视化
- **合规包装**：自动附加法律声明与 AI 生成内容提示
- **防刷机制**：IP 日限 + 文件大小/长度限制 + 敏感词过滤

---

## 免责声明

ClauseShield 是一款面向独立开发者的**合同风险扫描辅助工具**，基于行业惯例和公开案例进行风险提示。

1. **不构成法律建议**：扫描结果不能替代具有执业资质的律师的专业审查。
2. **不保证准确性**：AI 系统可能存在误判、遗漏或对特定语境理解不足的情况。
3. **用户自担风险**：用户应独立判断并承担使用本工具的全部责任。
4. **不承担责任**：ClauseShield 及其开发方不对任何因使用本服务导致的损失或纠纷承担法律责任。

在签署任何具有法律约束力的合同文件前，强烈建议您咨询专业律师。

---

## 许可证

[MIT License](LICENSE)

---

<p align="center">
  <sub>Built for indie developers 🛡️</sub>
</p>
