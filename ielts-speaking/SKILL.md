---
name: ielts-speaking
description: 雅思口语练习Agent，支持Part 1/2/3模拟练习、AI评分、发音建议。适合准备雅思考试的用户进行口语练习。
---

# 雅思口语练习 Agent

## 简介

专业的雅思口语练习工具，支持：
- ✅ Part 1 - 日常话题练习
- ✅ Part 2 - 个人陈述练习
- ✅ Part 3 - 深度讨论练习
- ✅ 完整模拟测试
- ✅ AI 智能评分
- ✅ 个性化改进建议

## 文件结构

```
ielts-speaking/
├── SKILL.md           # 使用说明
├── scripts/
│   └── ielts_agent.py # 主程序
└── topics/            # 话题库（可选扩展）
```

## 安装依赖

```bash
pip install requests
```

## 使用方法

### 基本使用

```bash
python3 scripts/ielts_agent.py
```

### 配置 AI 评分（可选）

```bash
python3 scripts/ielts_agent.py YOUR_API_KEY
```

或在程序中设置：
```python
agent.set_api_key('your_api_key')
```

## 功能说明

### Part 1 - 日常话题
- 时长：4-5分钟
- 内容：工作、学习、家乡、爱好等日常话题
- 问题数：3-4个问题

### Part 2 - 个人陈述
- 时长：3-4分钟（含1分钟准备）
- 内容：描述人物、地点、经历、物品等
- 要求：连续陈述2分钟

### Part 3 - 深度讨论
- 时长：4-5分钟
- 内容：教育、科技、环境等抽象话题
- 形式：与考官进行深入讨论

### 完整模拟测试
- 时长：11-14分钟
- 内容：完整模拟真实雅思口语考试流程

## 评分标准

| 维度 | 说明 |
|------|------|
| Fluency & Coherence | 流利度与连贯性 |
| Lexical Resource | 词汇资源 |
| Grammatical Range | 语法多样性 |
| Pronunciation | 发音 |

评分范围：1-9分

## 示例对话

```
🎤 考官问：What do you like to do in your free time?

💬 你的回答：In my free time, I enjoy reading books and 
watching movies. Reading helps me relax and learn new things, 
while movies are a great way to unwind after a long day.

📊 评分：
   流利度：7.0
   词汇量：6.5
   语法：7.0
   发音：6.5
   总分：6.75

💡 建议：尝试使用更多高级词汇和复杂句式...
```

## 注意事项

1. **API Key**：AI 评分功能需要有效的 API Key
2. **网络连接**：使用 AI 功能需要网络连接
3. **练习建议**：建议每天练习30分钟以上

## 扩展话题

可以在 `topics/` 目录下添加自定义话题 JSON 文件。
