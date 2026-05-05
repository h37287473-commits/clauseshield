# 📋 ClauseShield 合同风险扫描项目 — 一键复制版

## 产品定义
- **名称**：ClauseShield
- **用户**：独立开发者/自由职业者
- **痛点**：签合同前没人帮看陷阱
- **解决**：3-5秒AI扫描6大风险点
- **定价**：¥9.9/次 或 ¥29/月

## 6大扫描Agent

| Agent | 风险 | 典型陷阱示例 |
|-------|------|-------------|
| IP归属 | 知识产权被完全转让 | "项目完成后所有知识产权归甲方" |
| 付款节点 | 模糊付款、尾款陷阱 | "验收合格后30天内付款"（无标准） |
| 无限责任 | 无上限赔偿 | "乙方承担全部损失，不设上限" |
| 维护范围 | 终身免费维护 | "乙方提供终身免费技术支持" |
| 保密期限 | 永久保密义务 | "离职后永久保密" |
| 竞业限制 | 过度限制无补偿 | "离职后2年不得从事竞品工作" |

## 开发进度

- Day 1 ✅ Few-Shot库 + 5份合同测试（全对，成本¥1）
- Day 2 ✅ 核心流水线（24文件）
- Day 3 ✅ 兑换码支付 + 合规免责 + Unicode修复
- Day 4 ✅ 防刷机制 + GitHub文件 + 5/5测试通过
- **Day 5 ⏳ 部署上线** ← 当前在此

## 上线步骤（5分钟）

**Step 1：GitHub建仓库（2分钟）**
1. 访问 https://github.com/new
2. 名称：`clauseshield`，Public，**不勾选**README
3. 复制仓库地址

**Step 2：推送代码（1分钟）**
```bash
git remote add origin https://github.com/你的用户名/clauseshield.git
git branch -M main
git push -u origin main
```

**Step 3：Streamlit部署（2分钟）**
1. https://streamlit.io/cloud → GitHub登录
2. New app → 选仓库 → 主文件 `main.py` → Deploy
3. Settings → Secrets → 添加：
   - `DEEPSEEK_API_KEY` = `sk-d788e50f3145424081a6bfe1ffefed38`
   - `DEEPSEEK_BASE_URL` = `https://api.deepseek.com/v1`
   - `DEFAULT_MODEL` = `deepseek-chat`

**完成后获得：** `https://clauseshield-xxx.streamlit.app`

## 运营冷启动

**首批50个兑换码已就绪**
- 测试码前5个：`CLAUS-IKOR-3CMX`、`CLAUS-5QDT-5PX9`、`CLAUS-BB1C-YUPI`、`CLAUS-5E5W-VT0A`、`CLAUS-20LJ-BH50`
- 用途：朋友圈/开发者社群测试，收集反馈

**推广渠道**
- V2EX / 即刻 / Twitter（开发者社群）
- 小红书"AI副业"内容引流
- 知乎"合同避坑"科普回答

## 迭代路线图

| 版本 | 时间 | 功能 |
|------|------|------|
| v0.1 | 现在 | MVP上线（兑换码支付） |
| v0.2 | 1周后 | 微信扫码支付 |
| v0.3 | 2周后 | 安全合同模板库 |
| v0.4 | 1月后 | 批量扫描 |
| v0.5 | 2月后 | 企业版+API |

## 核心数据

- **代码量**：24个文件，Python + Streamlit
- **测试通过率**：5/5
- **单次成本**：~¥1（DeepSeek API）
- **技术栈**：Python 3.14 + Streamlit + DeepSeek + pdfplumber
- **完整路径**：`projects/clauseshield/`

---
*生成时间：2026-05-02*