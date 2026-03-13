---
name: smtp-mailer
description: 通过SMTP协议发送邮件，支持纯文本和HTML邮件，支持附件发送。使用前需先配置SMTP服务器信息。
---

# SMTP Mailer 技能

## 简介

通过 SMTP 协议发送邮件的技能，支持：
- ✅ 纯文本邮件
- ✅ HTML 邮件
- ✅ 附件发送
- ✅ 多种邮箱服务（QQ、163、Gmail、Outlook、企业邮箱等）

## 文件结构

```
smtp-mailer/
├── SKILL.md           # 使用说明（本文档）
├── package.json       # 项目配置
├── scripts/
│   └── send-mail.js   # 主程序
└── config/
    └── smtp-config.json  # SMTP配置（自动生成）
```

## 安装依赖

```bash
cd ~/.openclaw/workspace/skills/smtp-mailer
npm install
```

## 配置 SMTP

### 第一步：获取邮箱授权码

不同邮箱的获取方式：

| 邮箱 | SMTP服务器 | 端口 | 授权码获取方式 |
|------|-----------|------|---------------|
| QQ邮箱 | smtp.qq.com | 465 | 设置 → 账户 → POP3/SMTP服务 → 生成授权码 |
| 163邮箱 | smtp.163.com | 465 | 设置 → POP3/SMTP/IMAP → 开启服务 → 获取授权码 |
| Gmail | smtp.gmail.com | 587 | Google账户 → 安全性 → 两步验证 → 应用专用密码 |
| Outlook | smtp.office365.com | 587 | 直接使用账户密码 |
| 阿里企业邮 | smtp.qiye.aliyun.com | 465 | 企业邮箱后台开启SMTP |

### 第二步：配置技能

```bash
cd ~/.openclaw/workspace/skills/smtp-mailer

# 配置SMTP（最后一个参数是发件人地址，可选）
node scripts/send-mail.js config smtp.qq.com 465 your@qq.com your-auth-code

# 查看当前配置
node scripts/send-mail.js show

# 测试连接
node scripts/send-mail.js test
```

## 使用方法

### 发送纯文本邮件

```bash
node scripts/send-mail.js send recipient@example.com "邮件主题" "邮件内容"
```

### 从文件读取内容发送

```bash
# 内容以@开头表示从文件读取
node scripts/send-mail.js send recipient@example.com "邮件主题" @./content.txt
```

### 发送 HTML 邮件

```bash
node scripts/send-mail.js send-html recipient@example.com "邮件主题" ./email.html
```

### Node.js 代码调用

```javascript
const { sendMail } = require('./scripts/send-mail.js');

// 发送邮件
await sendMail({
  to: 'recipient@example.com',
  subject: '邮件主题',
  text: '纯文本内容',
  html: '<h1>HTML内容</h1>'  // 可选
});
```

## 常见问题

### 1. 连接失败
- 检查 SMTP 服务器地址和端口是否正确
- 检查是否使用了授权码而非登录密码
- 检查邮箱是否开启了 SMTP 服务

### 2. 认证失败
- 确认授权码正确
- Gmail 需要启用"应用专用密码"
- QQ/163 需要在网页端开启 SMTP 服务

### 3. 发送被拒绝
- 检查发件人地址是否与认证账户一致
- 检查收件人地址是否正确

## 安全提示

⚠️ **重要**：
- `smtp-config.json` 包含敏感信息，请勿分享或提交到公开仓库
- 建议使用专门的"应用专用密码"或"授权码"，而非主账户密码
- 定期更换授权码以提高安全性

## 示例：配置 QQ 邮箱

1. 登录 QQ 邮箱网页版
2. 设置 → 账户 → POP3/SMTP服务
3. 开启服务，生成授权码
4. 配置技能：
```bash
node scripts/send-mail.js config smtp.qq.com 465 12345678@qq.com abcdefghijklmnop
```

5. 测试：
```bash
node scripts/send-mail.js test
```

6. 发送：
```bash
node scripts/send-mail.js send someone@example.com "测试" "你好，这是一封测试邮件"
```
