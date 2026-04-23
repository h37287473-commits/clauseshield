# Day 2 核心流水线代码 - 技术架构准备

## 目标
搭建ClauseShield核心扫描流水线，包含：
1. 文件预处理（PDF→纯文本）
2. 条款切分（基于标题正则）
3. 6个专项Agent并行扫描
4. 报告聚合与分级展示
5. Streamlit极简前端

## 目录结构
```
clauseshield/
├── main.py                 # Streamlit入口
├── config.py               # 配置管理
├── requirements.txt        # 依赖清单
├── .env.example           # 环境变量模板
├── core/
│   ├── __init__.py
│   ├── pdf_extractor.py   # PDF文本提取
│   ├── clause_splitter.py # 条款切分
│   ├── scanner.py         # 扫描调度器
│   └── reporter.py        # 报告生成
├── agents/
│   ├── __init__.py
│   ├── base_agent.py      # Agent基类
│   ├── ip_agent.py        # IP归属扫描
│   ├── payment_agent.py   # 付款节点扫描
│   ├── liability_agent.py # 无限责任扫描
│   ├── maintenance_agent.py # 维护范围扫描
│   ├── confidentiality_agent.py # 保密期限扫描
│   └── noncompete_agent.py # 竞业限制扫描
├── prompts/
│   ├── ip_prompt.txt
│   ├── payment_prompt.txt
│   ├── liability_prompt.txt
│   ├── maintenance_prompt.txt
│   ├── confidentiality_prompt.txt
│   └── noncompete_prompt.txt
├── data/
│   ├── few_shot_lib.json
│   └── few_shot_lib_en.json
└── utils/
    ├── __init__.py
    └── helpers.py
```

## 技术选型
- **框架**: Streamlit (全栈，无需前端分离)
- **PDF解析**: pdfplumber (优先) / PyPDF2 (备用)
- **AI调用**: OpenAI兼容接口 (DeepSeek API)
- **向量存储**: ChromaDB (本地模式，嵌入可选)
- **数据模型**: Pydantic v2
- **并发**: asyncio + aiohttp (并行调用6个Agent)

## 核心数据模型
```python
from pydantic import BaseModel
from typing import Literal

class RiskItem(BaseModel):
    clause_text: str           # 条款原文
    risk_level: Literal["高危", "警告", "提示"]
    confidence: int           # 0-100
    category: str             # 风险类别
    description: str          # 白话解释
    common_practice: str      # 行业常规
    suggestion: str           # 建议关注点

class ScanReport(BaseModel):
    filename: str
    total_clauses: int
    risk_items: list[RiskItem]
    high_risks: list[RiskItem]      # confidence >= 80
    medium_risks: list[RiskItem]    # 60 <= confidence < 80
    low_risks: list[RiskItem]       # confidence < 60
    scan_time: float
    language: Literal["zh", "en"]
```

## 分级展示逻辑
- **红色【高危预警】**: confidence >= 80，置顶
- **橙色【建议关注】**: 60 <= confidence < 80，中置
- **灰色折叠区【其他存疑表述】**: confidence < 60，置底可折叠

## 合规文案要求
1. 上传前强制勾选免责声明
2. 报告顶部固定红字警告
3. 所有输出不含法律建议、修改意见、维权指引

## 兑换码体系
- 生成脚本: `gen_codes.py` (UUID格式)
- 验证函数: 读取codes.txt，更新使用状态
- 界面: Streamlit输入框"输入兑换码解锁扫描"

## 开发顺序
1. 环境搭建 (requirements.txt + .env)
2. PDF提取模块
3. 条款切分模块
4. Agent基类 + 6个专项Agent
5. 报告聚合 + Streamlit UI
6. 兑换码系统
7. 中英文路由 (?lang=en)
