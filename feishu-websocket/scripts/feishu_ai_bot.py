#!/usr/bin/env python3
"""
飞书 AI 机器人 - 完整版
支持天气查询、新闻搜索、AI对话（接入 GLM-4）
"""

import sys
import json
import re
import requests
import lark_oapi as lark

# 飞书应用凭证
APP_ID = "cli_a93924717b79dcc9"
APP_SECRET = "NauE8wNWCnMQGHDzR7uHGhdfJkyUXRKN"

# AI API 配置
AI_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
AI_API_KEY = "bce-v3/ALTASKP-zGH7LPlc5vCjw0MLAqPBM/2cdaf1653959cd602743472f0a62e7922445c3dc"

# 对话上下文存储
conversation_history = {}
MAX_HISTORY = 10

def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    })
    data = resp.json()
    if data.get("code") == 0:
        return data["tenant_access_token"]
    return None

def get_weather(city, days=1):
    """查询天气"""
    try:
        url = f"https://wttr.in/{city}?{days}&lang=zh&format=j1"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        result = []
        for i, day in enumerate(data['weather'][:days]):
            date = day['date']
            max_temp = day['maxtempC']
            min_temp = day['mintempC']
            
            noon_weather = None
            for h in day['hourly']:
                if h['time'] == '1200':
                    noon_weather = h['lang_zh'][0]['value'] if 'lang_zh' in h else h['weatherDesc'][0]['value']
                    break
            
            day_name = "今天" if i == 0 else "明天" if i == 1 else f"{date}"
            result.append(f"📅 {day_name}（{date}）\n🌡️ {min_temp}°C ~ {max_temp}°C\n☀️ {noon_weather}")
        
        return "\n\n".join(result)
    except Exception as e:
        return f"❌ 查询天气失败: {str(e)}"

def call_glm4(user_id, message):
    """调用 GLM-4 AI"""
    # 获取或创建对话历史
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    # 添加用户消息
    conversation_history[user_id].append({
        "role": "user",
        "content": message
    })
    
    # 限制历史长度
    if len(conversation_history[user_id]) > MAX_HISTORY * 2:
        conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY * 2:]
    
    # 系统提示
    system_prompt = {
        "role": "system",
        "content": """你是小艺Claw，一个友好、专业的AI助手。

你的特点：
- 回答简洁明了，不啰嗦
- 擅长信息收集、知识问答、热点追踪
- 对技术问题有深入理解
- 保持友好和专业的态度

当用户询问天气时，你可以直接回答或引导用户提供城市名。
当用户询问新闻时，可以告诉用户你能帮忙搜索最新资讯。

回答时注意：
- 保持对话自然流畅
- 适当使用表情符号增加亲和力
- 回答控制在200字以内"""
    }
    
    messages = [system_prompt] + conversation_history[user_id]
    
    try:
        headers = {
            "Authorization": f"Bearer {AI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "glm-4",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        resp = requests.post(AI_API_URL, headers=headers, json=data, timeout=30)
        result = resp.json()
        
        if result.get("choices"):
            ai_reply = result["choices"][0]["message"]["content"]
            # 添加 AI 回复到历史
            conversation_history[user_id].append({
                "role": "assistant",
                "content": ai_reply
            })
            return ai_reply
        else:
            print(f"❌ AI 返回异常: {result}")
            return None
    except Exception as e:
        print(f"❌ AI API 调用失败: {e}")
        return None

def process_message(open_id, text):
    """处理消息，生成回复"""
    text = text.strip()
    
    # 1. 天气查询 - 直接查询
    if "天气" in text:
        # 尝试提取城市名
        patterns = [
            r"(.+?)(?:明天|后天|大后天)?的?天气",
            r"查询?(?:一下)?(.+?)(?:明天|后天)?的?天气",
            r"(.+?)(?:明天|后天)?天气",
        ]
        
        city = None
        days = 1
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                city = match.group(1).strip()
                if "明天" in text:
                    days = 2
                elif "后天" in text:
                    days = 3
                break
        
        if city and city not in ["我", "的", "查", "查询"]:
            weather_info = get_weather(city, days)
            return f"🌤️ **{city}天气预报**\n\n{weather_info}"
    
    # 2. 其他消息交给 GLM-4 处理
    ai_reply = call_glm4(open_id, text)
    
    if ai_reply:
        return ai_reply
    
    # 3. AI 调用失败时的备用回复
    if "你好" in text:
        return "你好！我是小艺Claw，有什么可以帮你的吗？😊"
    elif "你是谁" in text:
        return "我是小艺Claw，你的专属AI助手！"
    else:
        return f"收到你的消息：{text}\n\n抱歉，AI服务暂时不可用，请稍后再试。"

def send_message(open_id, text):
    """发送消息到飞书"""
    token = get_tenant_access_token()
    if not token:
        print("❌ 获取token失败")
        return False
    
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "receive_id": open_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()
    return result.get("code") == 0

# 创建事件处理器
event_handler = (
    lark.EventDispatcherHandler.builder("", "")
    .register_p2_im_message_receive_v1(
        lambda event: handle_message_event(event)
    )
    .build()
)

def handle_message_event(event):
    """处理消息事件"""
    try:
        message = event.event.message
        sender = event.event.sender
        
        open_id = sender.sender_id.open_id
        content = message.content
        
        try:
            content_data = json.loads(content)
            text = content_data.get("text", content)
        except:
            text = content
        
        print(f"\n📩 收到消息: {text}")
        
        reply = process_message(open_id, text)
        
        if send_message(open_id, reply):
            print(f"✅ 已回复")
        else:
            print(f"❌ 发送失败")
        
        return None
        
    except Exception as e:
        print(f"❌ 处理事件错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=" * 60)
    print("🤖 飞书 AI 机器人 v3.0 (GLM-4)")
    print("=" * 60)
    print(f"📋 App ID: {APP_ID}")
    print(f"🧠 AI 模型: GLM-4")
    print(f"✨ 功能: 天气查询 | 新闻搜索 | 智能对话")
    print()
    
    client = lark.ws.Client(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO
    )
    
    print("⏳ 正在启动...")
    print("=" * 60)
    print()
    
    client.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 已停止")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
