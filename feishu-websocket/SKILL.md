---
name: feishu-websocket
description: 飞书WebSocket长连接客户端，支持接收飞书事件推送。配置后可实时接收飞书消息、机器人事件等。
---

# 飞书 WebSocket 技能

## 简介

通过 WebSocket 长连接接收飞书事件推送，支持：
- ✅ 飞书国内版 (open.feishu.cn)
- ✅ 实时事件推送
- ✅ 消息接收与处理
- ✅ 机器人事件订阅

## 文件结构

```
feishu-websocket/
├── SKILL.md           # 使用说明
├── package.json       # 项目配置
├── scripts/
│   └── feishu-ws.js   # 主程序
└── config/
    └── feishu-config.json  # 配置文件（自动生成）
```

## 安装依赖

```bash
cd ~/.openclaw/workspace/skills/feishu-websocket
npm install
```

## 配置步骤

### 1️⃣ 飞书开放平台配置

1. 登录 [飞书开放平台](https://open.feishu.cn)
2. 创建企业自建应用或使用已有应用
3. 在「事件订阅」中开启 **「使用长连接接收事件」**
4. 添加需要订阅的事件类型（如 `im.message.receive_v1`）
5. 记录 App ID 和 App Secret

### 2️⃣ 配置技能

```bash
cd ~/.openclaw/workspace/skills/feishu-websocket

# 配置应用凭证
node scripts/feishu-ws.js config cli_a93924717b79dcc9 NauE8wNWCnMQGHDzR7uHGhdfJkyUXRKN
```

### 3️⃣ 测试连接

```bash
node scripts/feishu-ws.js test
```

### 4️⃣ 启动服务

```bash
node scripts/feishu-ws.js start
```

## 命令说明

| 命令 | 说明 |
|------|------|
| `config <appId> <appSecret>` | 配置飞书应用凭证 |
| `test` | 测试连接配置 |
| `start` | 启动WebSocket连接 |

## 常见事件类型

| 事件类型 | 说明 |
|---------|------|
| `im.message.receive_v1` | 接收消息 |
| `im.message.created_v1` | 消息创建 |
| `contact.user.created_v1` | 用户创建 |
| `approval.instance.created_v1` | 审批实例创建 |

## 注意事项

1. **长连接需在飞书开放平台开启**：事件订阅 → 使用长连接接收事件
2. **WebSocket连接会持续运行**：适合后台服务场景
3. **Token自动刷新**：客户端会自动处理token过期刷新

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| 认证失败 | 检查App ID和App Secret是否正确 |
| 无法获取WebSocket地址 | 确认已在开放平台开启长连接 |
| 连接断开 | 检查网络，客户端会自动重连 |
