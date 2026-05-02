# ClauseShield 上线部署指南

## 🚀 5分钟完成上线

---

## 第1步：创建GitHub仓库（2分钟）

访问 https://github.com/new 创建仓库：
- **Repository name**: `clauseshield`
- **Description**: `AI合同风险扫描器 - 独立开发者MVP`
- **Visibility**: Public
- **Initialize**: 不要勾选（代码已准备好）

创建后复制仓库地址，例如：`https://github.com/你的用户名/clauseshield.git`

---

## 第2步：推送代码（1分钟）

在本地项目目录运行以下命令（替换为你的仓库地址）：

```bash
cd C:\Users\PC\.openclaw\workspace\projects\clauseshield
git remote add origin https://github.com/你的用户名/clauseshield.git
git branch -M main
git push -u origin main
```

---

## 第3步：Streamlit Cloud部署（2分钟）

1. 访问 https://streamlit.io/cloud
2. 用GitHub账号登录
3. 点击 "New app"
4. 选择仓库：`你的用户名/clauseshield`
5. 主文件路径：`main.py`
6. 点击 "Deploy"

**完成！** 约1-2分钟后获得访问链接，例如：
`https://clauseshield-xxx.streamlit.app`

---

## ⚠️ 重要：环境变量配置

Streamlit Cloud部署后，需要在App Settings中添加：
- `DEEPSEEK_API_KEY` = `sk-d788e50f3145424081a6bfe1ffefed38`
- `DEEPSEEK_BASE_URL` = `https://api.deepseek.com/v1`
- `DEFAULT_MODEL` = `deepseek-chat`

操作路径：App → Settings → Secrets → 添加键值对

---

## 📋 兑换码清单

50个兑换码已生成，保存在：
- `data/redemption_codes_50.json` — 完整记录
- `data/redemption_codes_50.txt` — 纯码值列表（方便复制分发）

**前5个码（测试用）：**
```
CLAUS-IKOR-3CMX
CLAUS-5QDT-5PX9
CLAUS-BB1C-YUPI
CLAUS-5E5W-VT0A
CLAUS-20LJ-BH50
```

---

## 🔗 部署后操作

1. **截图替换README占位** — 访问部署链接，截图主界面和报告页，替换 `assets/landing/` 下的占位文件
2. **更新README中的链接** — 将 `README.md` 中的占位URL替换为真实部署地址
3. **分享兑换码** — 首批50个码可用于朋友测试或早期用户

---

## 📊 项目状态

| 阶段 | 状态 |
|------|------|
| Day 1 Few-Shot库 + API测试 | ✅ 完成 |
| Day 2 核心流水线 | ✅ 完成 |
| Day 3 合规包装 + 兑换码支付 | ✅ 完成 |
| Day 4 冷启动 + 防刷 + GitHub | ✅ 完成 |
| **部署上线** | ⏳ 等你执行上述3步 |

---

*生成时间：2026-04-23 15:35*
