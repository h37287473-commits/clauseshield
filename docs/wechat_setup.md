# 微信公众号接入指南

> 本文档说明如何将 ClauseShield 与微信公众号/服务号集成，实现关键词自动回复。

---

## 前提条件

1. 已注册**微信公众号**（订阅号）或**微信服务号**（服务号权限更全）
2. 拥有服务器或云函数接收微信消息推送（如腾讯云函数、Vercel、阿里云函数）
3. 已完成 ClauseShield 主应用的部署

---

## 接入流程

### 1. 配置服务器 URL

在微信公众平台 **开发 → 基本配置 → 服务器配置** 中：

- **服务器 URL**：`https://your-domain.com/wechat/webhook`
- **Token**：自定义令牌（如 `clauseshield2026`）
- **EncodingAESKey**：随机生成或手动填写
- **消息加解密方式**：明文模式（测试阶段）或兼容模式/安全模式（生产阶段）

### 2. 验证服务器有效性

微信会发送 GET 请求验证服务器，示例处理逻辑：

```python
# wechat_handler.py 示例
import hashlib
from flask import Flask, request

app = Flask(__name__)
TOKEN = "clauseshield2026"

@app.route("/wechat/webhook", methods=["GET", "POST"])
def wechat_webhook():
    if request.method == "GET":
        # 微信服务器验证
        signature = request.args.get("signature", "")
        timestamp = request.args.get("timestamp", "")
        nonce = request.args.get("nonce", "")
        echostr = request.args.get("echostr", "")
        tmp = sorted([TOKEN, timestamp, nonce])
        hashcode = hashlib.sha1("".join(tmp).encode()).hexdigest()
        if hashcode == signature:
            return echostr
        return "fail"
    # POST 处理用户消息...
```

### 3. 自动回复规则配置

在 **功能 → 自动回复 → 关键词回复** 中添加规则：

| 规则名称 | 关键词 | 匹配类型 | 回复内容 |
|---------|--------|---------|---------|
| 扫描引导 | `扫描` | 全匹配 | 欢迎使用 ClauseShield！点击链接开始扫描：[你的应用URL] |
| 兑换指引 | `兑换` | 全匹配 | 请输入兑换码（格式：CLAU-XXXX-XXXX-XXXX），在应用内侧边栏输入即可激活。 |
| 帮助 | `帮助` / `?` | 全匹配 | 发送「扫描」获取使用链接，发送「兑换」获取兑换码指引。 |
| 默认回复 | （无匹配时）| — | 你好！我是 ClauseShield 助手。发送「扫描」开始合同风险扫描，发送「兑换」了解兑换码使用方式。 |

---

## 消息推送处理（进阶）

如需通过代码自动回复（而非平台关键词规则），在 webhook POST 中解析 XML：

```xml
<!-- 微信推送的消息格式示例 -->
<xml>
  <ToUserName><![CDATA[gh_xxx]]></ToUserName>
  <FromUserName><![CDATA[openid_xxx]]></FromUserName>
  <CreateTime>123456789</CreateTime>
  <MsgType><![CDATA[text]]></MsgType>
  <Content><![CDATA[扫描]]></Content>
  <MsgId>1234567890123456</MsgId>
</xml>
```

回复 XML 示例：

```xml
<xml>
  <ToUserName><![CDATA[openid_xxx]]></ToUserName>
  <FromUserName><![CDATA[gh_xxx]]></FromUserName>
  <CreateTime>123456789</CreateTime>
  <MsgType><![CDATA[text]]></MsgType>
  <Content><![CDATA[欢迎使用 ClauseShield！点击开始扫描：https://your-domain.com]]></Content>
</xml>
```

---

## 关键词触发映射

| 用户输入 | 系统动作 |
|---------|---------|
| `扫描` / `开始扫描` / `合同扫描` | 返回应用使用链接 |
| `兑换` / `兑换码` / `激活码` | 返回兑换码格式说明 + 输入位置指引 |
| `帮助` / `?` / `怎么用` | 返回基础操作指南 |
| `价格` / `多少钱` / `付费` | 返回兑换码获取渠道说明 |
| `隐私` / `安全` / `数据` | 返回数据安全 FAQ 摘要 |

---

## 测试 checklist

- [ ] 服务器 URL 验证通过（微信公众平台显示"配置成功"）
- [ ] 发送「扫描」能收到带链接的自动回复
- [ ] 发送「兑换」能收到兑换码格式说明
- [ ] 发送其他文本能收到默认引导回复
- [ ] 链接跳转后应用能正常加载

---

## 注意事项

1. **订阅号限制**：订阅号无客服消息接口，仅能通过被动回复与用户交互（48小时内可回复）
2. **服务号优势**：服务号支持模板消息、客服消息，体验更好
3. **HTTPS 必须**：微信要求服务器 URL 必须为 HTTPS
4. **域名备案**：使用国内服务器需域名备案
5. **Token 安全**：生产环境应使用安全模式加密消息，避免 Token 泄露

---

## 参考文档

- [微信官方开发文档](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html)
- [微信公众平台接入指南](https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Access_Overview.html)
