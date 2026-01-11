"""
AI屏幕控制系统 - 类似Manus的实现方案

技术栈：
- 截图：pillow, mss
- 鼠标键盘控制：pyautogui
- AI视觉识别：Claude API (Anthropic) 或 GPT-4V (OpenAI)
- 图像处理：opencv-python

安装依赖：
pip install pillow mss pyautogui anthropic opencv-python pyperclip
"""

import base64
import json
import time
from io import BytesIO
from PIL import ImageGrab
import pyautogui
import anthropic

class AIScreenController:
    def __init__(self, api_key):
        """初始化AI屏幕控制器"""
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def capture_screen(self):
        """截取整个屏幕"""
        screenshot = ImageGrab.grab()
        return screenshot
    
    def capture_region(self, x1, y1, x2, y2):
        """截取屏幕指定区域"""
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        return screenshot
    
    def image_to_base64(self, image):
        """将图片转换为base64"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    def ask_ai(self, image, task_description):
        """
        发送截图和任务描述给AI，获取操作指令
        
        Args:
            image: PIL Image对象
            task_description: 用户想要做什么，例如"点击登录按钮"
        
        Returns:
            AI返回的操作指令，格式如：
            {
                "actions": [
                    {"type": "click", "x": 100, "y": 200, "button": "left"},
                    {"type": "type", "text": "hello"},
                    {"type": "key", "key": "enter"}
                ]
            }
        """
        # 将图片转换为base64
        image_base64 = self.image_to_base64(image)
        
        # 构建提示词，要求AI返回特定格式的JSON
        prompt = f"""你是一个屏幕操作助手。我会给你一张屏幕截图和一个任务描述。
请分析截图，识别需要操作的UI元素位置，并返回操作步骤。

任务：{task_description}

请返回JSON格式的操作指令，格式如下：
{{
    "analysis": "你对屏幕内容的分析",
    "actions": [
        {{"type": "move", "x": 坐标x, "y": 坐标y, "description": "移动到某处"}},
        {{"type": "click", "x": 坐标x, "y": 坐标y, "button": "left/right", "description": "点击某按钮"}},
        {{"type": "double_click", "x": 坐标x, "y": 坐标y, "description": "双击某处"}},
        {{"type": "type", "text": "要输入的文本", "description": "输入文字"}},
        {{"type": "key", "key": "enter/tab/escape等", "description": "按键操作"}},
        {{"type": "wait", "seconds": 等待秒数, "description": "等待"}},
        {{"type": "scroll", "clicks": 滚动次数, "description": "滚动"}}
    ]
}}

注意：
1. 坐标(0,0)在屏幕左上角
2. 必须准确识别UI元素的位置
3. 操作步骤要符合逻辑顺序
4. 只返回JSON，不要其他文字"""

        # 调用Claude API
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        # 解析AI返回的JSON
        response_text = message.content[0].text
        
        # 提取JSON（去除可能的markdown代码块标记）
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
            
        return json.loads(response_text.strip())
    
    def execute_action(self, action):
        """执行单个操作"""
        action_type = action.get("type")
        
        if action_type == "move":
            # 移动鼠标
            x, y = action["x"], action["y"]
            pyautogui.moveTo(x, y, duration=0.5)
            print(f"移动鼠标到 ({x}, {y})")
            
        elif action_type == "click":
            # 点击
            x, y = action["x"], action["y"]
            button = action.get("button", "left")
            pyautogui.click(x, y, button=button)
            print(f"在 ({x}, {y}) {button}键点击")
            
        elif action_type == "double_click":
            # 双击
            x, y = action["x"], action["y"]
            pyautogui.doubleClick(x, y)
            print(f"在 ({x}, {y}) 双击")
            
        elif action_type == "type":
            # 输入文字
            text = action["text"]
            pyautogui.write(text, interval=0.1)
            print(f"输入文字: {text}")
            
        elif action_type == "key":
            # 按键
            key = action["key"]
            pyautogui.press(key)
            print(f"按下键: {key}")
            
        elif action_type == "wait":
            # 等待
            seconds = action["seconds"]
            time.sleep(seconds)
            print(f"等待 {seconds} 秒")
            
        elif action_type == "scroll":
            # 滚动
            clicks = action.get("clicks", 1)
            pyautogui.scroll(clicks)
            print(f"滚动 {clicks} 次")
    
    def execute_task(self, task_description):
        """
        执行完整任务
        
        Args:
            task_description: 任务描述，例如"打开记事本并输入hello world"
        """
        print(f"\n=== 开始执行任务: {task_description} ===")
        
        # 1. 截取屏幕
        print("正在截取屏幕...")
        screenshot = self.capture_screen()
        
        # 2. 询问AI
        print("正在分析屏幕并规划操作...")
        result = self.ask_ai(screenshot, task_description)
        
        # 3. 显示AI的分析
        print(f"\nAI分析: {result.get('analysis', '无')}")
        print(f"\n计划执行 {len(result['actions'])} 个操作:")
        for i, action in enumerate(result['actions'], 1):
            desc = action.get('description', action.get('type'))
            print(f"  {i}. {desc}")
        
        # 4. 执行操作
        print("\n开始执行操作...")
        for i, action in enumerate(result['actions'], 1):
            print(f"\n步骤 {i}/{len(result['actions'])}:")
            self.execute_action(action)
            time.sleep(0.5)  # 操作间隔
        
        print("\n=== 任务完成 ===")


# ============ 使用示例 ============

def main():
    # 初始化控制器（需要你的Claude API密钥）
    API_KEY = "your-claude-api-key-here"
    controller = AIScreenController(API_KEY)
    
    # 示例1: 简单任务
    controller.execute_task("点击屏幕上的搜索框并输入'hello world'")
    
    # 示例2: 复杂任务
    controller.execute_task("找到浏览器地址栏，输入google.com并回车")
    
    # 示例3: 多步骤任务
    controller.execute_task("打开开始菜单，搜索记事本，打开它")


# ============ 高级功能示例 ============

class AdvancedAIController(AIScreenController):
    """扩展版AI控制器，支持更多功能"""
    
    def continuous_task(self, goal, max_iterations=10):
        """
        持续执行任务直到目标达成
        类似于真正的AI Agent，会不断观察屏幕并调整策略
        """
        for i in range(max_iterations):
            print(f"\n=== 第 {i+1} 轮尝试 ===")
            
            # 截图
            screenshot = self.capture_screen()
            
            # 询问AI当前状态和下一步动作
            prompt = f"""当前目标：{goal}
            
请分析当前屏幕状态，判断：
1. 目标是否已完成？
2. 如果未完成，下一步应该做什么？

返回JSON格式：
{{
    "completed": true/false,
    "current_state": "当前状态描述",
    "next_actions": [...] // 如果未完成，返回下一步操作
}}"""
            
            result = self.ask_ai(screenshot, prompt)
            
            if result.get("completed"):
                print("✓ 目标已完成！")
                break
            
            print(f"当前状态: {result.get('current_state')}")
            
            # 执行下一步操作
            for action in result.get("next_actions", []):
                self.execute_action(action)
                time.sleep(0.5)
        
    def visual_search(self, target_description):
        """
        视觉搜索：在屏幕上找到特定元素的位置
        
        Returns:
            {"x": x坐标, "y": y坐标, "found": True/False}
        """
        screenshot = self.capture_screen()
        
        prompt = f"""在这个截图中找到：{target_description}
        
如果找到了，返回其中心位置坐标：
{{
    "found": true,
    "x": 坐标x,
    "y": 坐标y,
    "description": "找到的元素描述"
}}

如果没找到：
{{
    "found": false,
    "reason": "未找到的原因"
}}"""
        
        result = self.ask_ai(screenshot, prompt)
        return result


if __name__ == "__main__":
    print("""
    AI屏幕控制系统 - 实现方案
    
    这个系统可以实现类似Manus的功能：
    1. 自动截取屏幕
    2. AI视觉识别UI元素
    3. 自动执行鼠标键盘操作
    4. 支持自然语言任务描述
    
    核心优势：
    - 无需训练自己的视觉模型
    - 利用Claude/GPT-4V的强大视觉理解能力
    - 可以理解复杂的自然语言指令
    - 支持多步骤任务规划
    
    使用场景：
    - 自动化测试
    - RPA（机器人流程自动化）
    - 游戏辅助
    - 办公自动化
    """)
    
    # 取消下面的注释来运行示例
    # main()