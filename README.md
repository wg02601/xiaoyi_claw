# 小艺Claw

OpenClaw AI 助手技能集合，包含邮件发送、飞书机器人、每日简报等功能。

## 技能列表

### 📧 smtp-mailer
SMTP 邮件发送技能，支持通过 SMTP 协议发送邮件。

**功能：**
- 纯文本邮件发送
- HTML 邮件发送
- 支持 QQ、163、Gmail、Outlook 等邮箱

**使用：**
```bash
cd smtp-mailer
npm install
node scripts/send-mail.js config smtp.qq.com 465 your@qq.com your-auth-code
node scripts/send-mail.js send recipient@example.com "主题" "内容"
```

### 💬 feishu-websocket
飞书 WebSocket 长连接机器人，支持接收消息和 AI 对话。

**功能：**
- WebSocket 长连接
- 消息接收与回复
- AI 对话（GLM-4）
- 天气查询

**使用：**
```bash
cd feishu-websocket
pip install lark-oapi requests
python3 scripts/feishu_ai_bot.py
```

### 📰 hongmeng-daily-report
鸿蒙智行每日资讯简报定时任务。

**功能：**
- 每天 16:00 自动收集资讯
- 发送邮件简报

## 配置要求

- Node.js 18+
- Python 3.8+
- OpenClaw 运行环境

## 作者

小艺Claw - OpenClaw AI 助手自动生成
