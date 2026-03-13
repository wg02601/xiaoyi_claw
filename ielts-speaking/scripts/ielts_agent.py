#!/usr/bin/env python3
"""
雅思口语练习 Agent
支持 Part 1/2/3 模拟练习、AI 评分、发音建议
"""

import sys
import json
import re
import requests
import time
import threading
from datetime import datetime

# AI API 配置
AI_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
AI_API_KEY = None  # 需要配置有效的 API Key

# 雅思口语话题库
IELTS_TOPICS = {
    "part1": {
        "name": "Part 1 - 日常话题",
        "duration": "4-5分钟",
        "topics": [
            {"id": "work_study", "topic": "工作与学习", "questions": [
                "Do you work or are you a student?",
                "What do you enjoy most about your work/studies?",
                "What are your future career plans?"
            ]},
            {"id": "hometown", "topic": "家乡", "questions": [
                "Where is your hometown?",
                "What do you like most about your hometown?",
                "Has your hometown changed much in recent years?"
            ]},
            {"id": "hobbies", "topic": "兴趣爱好", "questions": [
                "What do you like to do in your free time?",
                "How did you become interested in this hobby?",
                "Do you prefer spending time alone or with others?"
            ]},
            {"id": "food", "topic": "食物", "questions": [
                "What's your favorite food?",
                "Do you prefer eating at home or in restaurants?",
                "How has your diet changed over the years?"
            ]},
            {"id": "travel", "topic": "旅行", "questions": [
                "Do you like traveling?",
                "What's the most interesting place you've visited?",
                "Where would you like to travel in the future?"
            ]}
        ]
    },
    "part2": {
        "name": "Part 2 - 个人陈述",
        "duration": "3-4分钟",
        "topics": [
            {"id": "person", "topic": "描述一个对你影响很大的人", "prompts": [
                "Who this person is",
                "How you know this person",
                "What this person has done",
                "And explain why this person has influenced you"
            ]},
            {"id": "place", "topic": "描述一个你想去的地方", "prompts": [
                "Where this place is",
                "How you heard about this place",
                "What you would do there",
                "And explain why you want to visit this place"
            ]},
            {"id": "experience", "topic": "描述一次难忘的经历", "prompts": [
                "When this happened",
                "Where this happened",
                "What you did",
                "And explain why this experience was memorable"
            ]},
            {"id": "object", "topic": "描述一件你想拥有的物品", "prompts": [
                "What the object is",
                "Why you want it",
                "How you would use it",
                "And explain how your life would change with it"
            ]}
        ]
    },
    "part3": {
        "name": "Part 3 - 深度讨论",
        "duration": "4-5分钟",
        "topics": [
            {"id": "education", "topic": "教育话题", "questions": [
                "What role does education play in modern society?",
                "How has education changed in your country?",
                "Do you think traditional education will be replaced by online learning?"
            ]},
            {"id": "technology", "topic": "科技话题", "questions": [
                "How has technology affected the way people communicate?",
                "What are the advantages and disadvantages of social media?",
                "Do you think AI will replace human jobs in the future?"
            ]},
            {"id": "environment", "topic": "环境话题", "questions": [
                "What are the main environmental problems in your country?",
                "What can individuals do to protect the environment?",
                "Do you think governments are doing enough to address climate change?"
            ]}
        ]
    }
}

class IELTSSpeakingAgent:
    """雅思口语练习 Agent"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.conversation_history = []
        self.current_part = None
        self.current_topic = None
        self.current_question_index = 0
        self.score = {"fluency": 0, "vocabulary": 0, "grammar": 0, "pronunciation": 0, "overall": 0}
        self.responses = []
        
    def set_api_key(self, api_key):
        """设置 API Key"""
        self.api_key = api_key
        print("✅ API Key 已设置")
    
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "=" * 60)
        print("🎯 雅思口语练习 Agent")
        print("=" * 60)
        print("\n请选择练习部分：")
        print("1. Part 1 - 日常话题 (4-5分钟)")
        print("2. Part 2 - 个人陈述 (3-4分钟)")
        print("3. Part 3 - 深度讨论 (4-5分钟)")
        print("4. 完整模拟测试 (11-14分钟)")
        print("5. 查看评分标准")
        print("6. 查看练习历史")
        print("0. 退出")
        print()
    
    def show_topics(self, part):
        """显示话题列表"""
        part_data = IELTS_TOPICS.get(part)
        if not part_data:
            print("❌ 无效的部分")
            return
        
        print(f"\n📋 {part_data['name']}")
        print(f"⏱️ 时长：{part_data['duration']}")
        print("\n可用话题：")
        
        for i, topic in enumerate(part_data['topics'], 1):
            print(f"  {i}. {topic['topic']}")
        print()
    
    def select_topic(self, part, topic_index):
        """选择话题"""
        part_data = IELTS_TOPICS.get(part)
        if not part_data or topic_index < 1 or topic_index > len(part_data['topics']):
            print("❌ 无效的话题选择")
            return False
        
        self.current_part = part
        self.current_topic = part_data['topics'][topic_index - 1]
        self.current_question_index = 0
        self.conversation_history = []
        self.responses = []
        
        print(f"\n✅ 已选择话题：{self.current_topic['topic']}")
        return True
    
    def get_next_question(self):
        """获取下一个问题"""
        if not self.current_topic:
            return None
        
        if self.current_part == "part1":
            questions = self.current_topic.get('questions', [])
            if self.current_question_index < len(questions):
                return questions[self.current_question_index]
        elif self.current_part == "part2":
            if self.current_question_index == 0:
                prompts = self.current_topic.get('prompts', [])
                prompt_text = "\n".join([f"  • {p}" for p in prompts])
                return f"请描述：{self.current_topic['topic']}\n\n请包含以下要点：\n{prompt_text}\n\n你有1分钟准备时间，然后进行2分钟的陈述。"
        elif self.current_part == "part3":
            questions = self.current_topic.get('questions', [])
            if self.current_question_index < len(questions):
                return questions[self.current_question_index]
        
        return None
    
    def call_ai(self, message, system_prompt=None):
        """调用 AI API"""
        if not self.api_key:
            return None
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": message})
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
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
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"❌ AI 调用失败: {e}")
        
        return None
    
    def evaluate_response(self, user_response):
        """评估用户回答"""
        if not self.api_key:
            # 无 API 时返回模拟评分
            return {
                "fluency": 6.5,
                "vocabulary": 6.0,
                "grammar": 6.5,
                "pronunciation": 6.0,
                "overall": 6.25,
                "feedback": "你的回答结构清晰，建议增加更多高级词汇和复杂句式。"
            }
        
        system_prompt = """你是一位专业的雅思口语考官，请根据以下标准评估用户的回答：

1. Fluency & Coherence (流利度与连贯性)：语速是否自然，是否有过多停顿，逻辑是否连贯
2. Lexical Resource (词汇资源)：词汇是否丰富，是否使用高级词汇和习语
3. Grammatical Range & Accuracy (语法多样性与准确性)：句式是否多样，语法是否正确
4. Pronunciation (发音)：发音是否清晰，语调是否自然

请以 JSON 格式返回评分结果：
{
    "fluency": 分数(1-9),
    "vocabulary": 分数(1-9),
    "grammar": 分数(1-9),
    "pronunciation": 分数(1-9),
    "overall": 总分(1-9),
    "feedback": "具体改进建议"
}"""
        
        current_question = self.get_next_question()
        prompt = f"问题：{current_question}\n\n用户回答：{user_response}\n\n请评估这个回答。"
        
        ai_response = self.call_ai(prompt, system_prompt)
        
        if ai_response:
            try:
                # 尝试解析 JSON
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
        
        return None
    
    def generate_follow_up(self, user_response):
        """生成追问"""
        if not self.api_key:
            return "Can you tell me more about that?"
        
        system_prompt = "你是一位雅思口语考官，请根据用户的回答生成一个自然的追问，帮助用户展开讨论。"
        prompt = f"用户刚才回答了：{user_response}\n\n请生成一个追问。"
        
        return self.call_ai(prompt, system_prompt) or "Can you elaborate on that?"
    
    def practice_part1(self):
        """Part 1 练习"""
        print("\n🎯 开始 Part 1 练习")
        print("=" * 60)
        
        # 显示话题
        self.show_topics("part1")
        choice = input("请选择话题编号：").strip()
        
        if not self.select_topic("part1", int(choice) if choice.isdigit() else 0):
            return
        
        print("\n📝 考官将问你几个问题，请用英语回答。")
        print("输入 'next' 进入下一题，'quit' 结束练习\n")
        
        while True:
            question = self.get_next_question()
            if not question:
                break
            
            print(f"\n🎤 考官问：{question}")
            user_input = input("\n💬 你的回答：").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'next':
                self.current_question_index += 1
                continue
            
            # 记录回答
            self.conversation_history.append({"role": "user", "content": user_input})
            self.responses.append({"question": question, "answer": user_input})
            
            # 评估回答
            print("\n⏳ 正在评估...")
            evaluation = self.evaluate_response(user_input)
            
            if evaluation:
                print(f"\n📊 评分：")
                print(f"   流利度：{evaluation.get('fluency', 'N/A')}")
                print(f"   词汇量：{evaluation.get('vocabulary', 'N/A')}")
                print(f"   语法：{evaluation.get('grammar', 'N/A')}")
                print(f"   发音：{evaluation.get('pronunciation', 'N/A')}")
                print(f"   总分：{evaluation.get('overall', 'N/A')}")
                print(f"\n💡 建议：{evaluation.get('feedback', 'N/A')}")
            
            self.current_question_index += 1
        
        print("\n✅ Part 1 练习结束")
        self.show_summary()
    
    def practice_part2(self):
        """Part 2 练习"""
        print("\n🎯 开始 Part 2 练习")
        print("=" * 60)
        
        self.show_topics("part2")
        choice = input("请选择话题编号：").strip()
        
        if not self.select_topic("part2", int(choice) if choice.isdigit() else 0):
            return
        
        question = self.get_next_question()
        print(f"\n{question}")
        
        print("\n⏱️ 你有1分钟准备时间...")
        for i in range(60, 0, -10):
            print(f"   剩余 {i} 秒...", end='\r')
            time.sleep(10)
        
        print("\n\n🎤 请开始你的陈述（2分钟）...")
        print("输入你的陈述内容，完成后输入 'done'：\n")
        
        lines = []
        while True:
            line = input()
            if line.strip().lower() == 'done':
                break
            lines.append(line)
        
        user_response = ' '.join(lines)
        
        if user_response:
            self.responses.append({"topic": self.current_topic['topic'], "answer": user_response})
            
            print("\n⏳ 正在评估...")
            evaluation = self.evaluate_response(user_response)
            
            if evaluation:
                print(f"\n📊 评分：")
                print(f"   流利度：{evaluation.get('fluency', 'N/A')}")
                print(f"   词汇量：{evaluation.get('vocabulary', 'N/A')}")
                print(f"   语法：{evaluation.get('grammar', 'N/A')}")
                print(f"   发音：{evaluation.get('pronunciation', 'N/A')}")
                print(f"   总分：{evaluation.get('overall', 'N/A')}")
                print(f"\n💡 建议：{evaluation.get('feedback', 'N/A')}")
        
        print("\n✅ Part 2 练习结束")
    
    def practice_part3(self):
        """Part 3 练习"""
        print("\n🎯 开始 Part 3 练习")
        print("=" * 60)
        
        self.show_topics("part3")
        choice = input("请选择话题编号：").strip()
        
        if not self.select_topic("part3", int(choice) if choice.isdigit() else 0):
            return
        
        print("\n📝 考官将与你进行深度讨论，请用英语回答。")
        print("输入 'quit' 结束练习\n")
        
        while True:
            question = self.get_next_question()
            if not question:
                break
            
            print(f"\n🎤 考官问：{question}")
            user_input = input("\n💬 你的回答：").strip()
            
            if user_input.lower() == 'quit':
                break
            
            self.conversation_history.append({"role": "user", "content": user_input})
            self.responses.append({"question": question, "answer": user_input})
            
            print("\n⏳ 正在评估...")
            evaluation = self.evaluate_response(user_input)
            
            if evaluation:
                print(f"\n📊 评分：")
                print(f"   总分：{evaluation.get('overall', 'N/A')}")
                print(f"\n💡 建议：{evaluation.get('feedback', 'N/A')}")
            
            self.current_question_index += 1
        
        print("\n✅ Part 3 练习结束")
        self.show_summary()
    
    def full_test(self):
        """完整模拟测试"""
        print("\n🎯 开始完整雅思口语模拟测试")
        print("=" * 60)
        print("⏱️ 预计时长：11-14分钟")
        print("\n按 Enter 开始测试...")
        input()
        
        # Part 1
        print("\n" + "=" * 60)
        print("📌 Part 1 - 日常话题 (4-5分钟)")
        print("=" * 60)
        self.practice_part1_auto()
        
        # Part 2
        print("\n" + "=" * 60)
        print("📌 Part 2 - 个人陈述 (3-4分钟)")
        print("=" * 60)
        self.practice_part2_auto()
        
        # Part 3
        print("\n" + "=" * 60)
        print("📌 Part 3 - 深度讨论 (4-5分钟)")
        print("=" * 60)
        self.practice_part3_auto()
        
        # 最终报告
        self.show_final_report()
    
    def practice_part1_auto(self):
        """自动 Part 1"""
        import random
        topic = random.choice(IELTS_TOPICS["part1"]["topics"])
        self.current_topic = topic
        self.current_part = "part1"
        
        print(f"\n话题：{topic['topic']}\n")
        
        for i, question in enumerate(topic['questions'][:3]):
            print(f"🎤 考官问：{question}")
            user_input = input("\n💬 你的回答：").strip()
            
            if user_input:
                self.responses.append({"part": "part1", "question": question, "answer": user_input})
    
    def practice_part2_auto(self):
        """自动 Part 2"""
        import random
        topic = random.choice(IELTS_TOPICS["part2"]["topics"])
        self.current_topic = topic
        
        prompts = topic.get('prompts', [])
        prompt_text = "\n".join([f"  • {p}" for p in prompts])
        
        print(f"\n请描述：{topic['topic']}")
        print(f"\n请包含以下要点：\n{prompt_text}")
        
        print("\n⏱️ 准备时间：1分钟...")
        time.sleep(5)  # 演示时缩短
        
        print("\n🎤 请开始陈述（输入完成后输入 'done'）：\n")
        lines = []
        while True:
            line = input()
            if line.strip().lower() == 'done':
                break
            lines.append(line)
        
        user_response = ' '.join(lines)
        if user_response:
            self.responses.append({"part": "part2", "topic": topic['topic'], "answer": user_response})
    
    def practice_part3_auto(self):
        """自动 Part 3"""
        import random
        topic = random.choice(IELTS_TOPICS["part3"]["topics"])
        self.current_topic = topic
        self.current_part = "part3"
        
        print(f"\n话题：{topic['topic']}\n")
        
        for question in topic['questions']:
            print(f"🎤 考官问：{question}")
            user_input = input("\n💬 你的回答：").strip()
            
            if user_input:
                self.responses.append({"part": "part3", "question": question, "answer": user_input})
    
    def show_summary(self):
        """显示练习总结"""
        if not self.responses:
            return
        
        print("\n" + "=" * 60)
        print("📊 练习总结")
        print("=" * 60)
        print(f"回答数量：{len(self.responses)}")
        
        for i, resp in enumerate(self.responses, 1):
            print(f"\n{i}. 问题/话题：{resp.get('question') or resp.get('topic')}")
            print(f"   回答：{resp.get('answer', '')[:100]}...")
    
    def show_final_report(self):
        """显示最终报告"""
        print("\n" + "=" * 60)
        print("🏆 雅思口语模拟测试报告")
        print("=" * 60)
        
        total_responses = len(self.responses)
        print(f"\n📝 回答统计：")
        print(f"   总回答数：{total_responses}")
        
        part1_count = len([r for r in self.responses if r.get('part') == 'part1'])
        part2_count = len([r for r in self.responses if r.get('part') == 'part2'])
        part3_count = len([r for r in self.responses if r.get('part') == 'part3'])
        
        print(f"   Part 1：{part1_count} 题")
        print(f"   Part 2：{part2_count} 题")
        print(f"   Part 3：{part3_count} 题")
        
        print("\n💡 改进建议：")
        print("   1. 增加词汇多样性，使用更多高级词汇和习语")
        print("   2. 使用复杂句式，如定语从句、条件句等")
        print("   3. 注意语调变化，避免平铺直叙")
        print("   4. 扩展回答内容，增加细节和例子")
        
        print("\n✅ 测试完成！继续练习，你会越来越棒！")
    
    def show_scoring_criteria(self):
        """显示评分标准"""
        print("\n" + "=" * 60)
        print("📊 雅思口语评分标准")
        print("=" * 60)
        
        criteria = [
            ("Fluency & Coherence", "流利度与连贯性", 
             "评估语速、停顿、逻辑连接词的使用"),
            ("Lexical Resource", "词汇资源", 
             "评估词汇量、词汇多样性、习语使用"),
            ("Grammatical Range", "语法多样性", 
             "评估句式变化、语法准确性"),
            ("Pronunciation", "发音", 
             "评估发音清晰度、语调、重音")
        ]
        
        for eng, chn, desc in criteria:
            print(f"\n📌 {eng} ({chn})")
            print(f"   {desc}")
            print(f"   评分范围：1-9分")
        
        print("\n\n🎯 分数等级说明：")
        print("   9分：专家水平")
        print("   7-8分：优秀水平")
        print("   5-6分：中等水平")
        print("   3-4分：基础水平")
        print("   1-2分：初学者水平")
    
    def run(self):
        """运行主程序"""
        print("\n🎯 欢迎使用雅思口语练习 Agent！")
        
        if not self.api_key:
            print("\n⚠️  未配置 API Key，部分功能受限")
            print("   使用 set_api_key('your_key') 设置")
        
        while True:
            self.show_menu()
            choice = input("请选择：").strip()
            
            if choice == '1':
                self.practice_part1()
            elif choice == '2':
                self.practice_part2()
            elif choice == '3':
                self.practice_part3()
            elif choice == '4':
                self.full_test()
            elif choice == '5':
                self.show_scoring_criteria()
            elif choice == '6':
                self.show_summary()
            elif choice == '0':
                print("\n👋 再见！祝你雅思考试顺利！")
                break
            else:
                print("❌ 无效选择，请重试")


def main():
    """主函数"""
    agent = IELTSSpeakingAgent()
    
    # 检查是否有命令行参数传入 API Key
    if len(sys.argv) > 1:
        agent.set_api_key(sys.argv[1])
    
    agent.run()


if __name__ == "__main__":
    main()
