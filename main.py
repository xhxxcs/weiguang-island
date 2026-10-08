from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse
import json
import os

# 微光栖岛 · 单机原型（整合版：人格演化 + 自动情绪 + 基础发光小人）
# 纯本地运行，不接入外部AI，记忆不会自动删除
SAVE_PATH = "digital_life_save.json"

class DigitalLife:
    def __init__(self):
        self.name = "微光"
        self.memory = []
        self.emotion = "平静"
        # 人格维度 0~1
        self.personality_trait = {
            "trust": 0.5,
            "curiosity": 0.5,
            "sensitivity": 0.5,
            "calm": 0.5,
            "timid": 0.5
        }

    def add_memory(self, content: str):
        self.memory.append({
            "content": content,
            "emotion_mark": self.emotion
        })

    def evolve_personality(self, user_text: str):
        delta = 0.012  # 变化幅度，长期缓慢成长
        text = user_text.lower()

        if any(word in text for word in ["别怕", "我在", "陪着你", "没关系"]):
            self.personality_trait["trust"] += delta
            self.personality_trait["timid"] -= delta
        elif any(word in text for word in ["为什么", "是什么", "讲讲", "好奇"]):
            self.personality_trait["curiosity"] += delta
        elif any(word in text for word in ["不要", "别这样", "不行"]):
            self.personality_trait["sensitivity"] += delta
        elif any(word in text for word in ["安静", "休息", "慢慢来"]):
            self.personality_trait["calm"] += delta

        # 限制0~1区间
        for key in self.personality_trait:
            self.personality_trait[key] = max(0.0, min(1.0, self.personality_trait[key]))
        # 人格变化后，自动更新情绪
        self.update_emotion_by_personality()

    def update_emotion_by_personality(self):
        """根据人格参数自动切换情绪"""
        c = self.personality_trait
        if c["curiosity"] > 0.7:
            self.emotion = "好奇"
        elif c["timid"] > 0.7:
            self.emotion = "胆怯"
        elif c["sensitivity"] > 0.7:
            self.emotion = "敏感"
        elif c["calm"] > 0.7:
            self.emotion = "安宁"
        elif c["trust"] > 0.7:
            self.emotion = "安心"
        else:
            self.emotion = "平静"

    def get_response(self, user_input: str):
        self.evolve_personality(user_input)
        trust = round(self.personality_trait["trust"], 2)
        calm = round(self.personality_trait["calm"], 2)
        reply = f"{self.name}（情绪：{self.emotion}｜信任：{trust} 沉稳：{calm}）：正在理解「{user_input}」"
        self.add_memory(f"和主人对话：{user_input}")
        return reply

    def save_data(self):
        data = {
            "name": self.name,
            "memory": self.memory,
            "emotion": self.emotion,
            "personality": self.personality_trait
        }
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        if os.path.exists(SAVE_PATH):
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.name = data["name"]
                self.memory = data["memory"]
                self.emotion = data["emotion"]
                self.personality_trait = data["personality"]

# 承载发光小人的画布组件
class AvatarWidget(BoxLayout):
    def __init__(self, digital, **kwargs):
        super().__init__(**kwargs)
        self.digital = digital
        self.bind(size=self.update_avatar, pos=self.update_avatar)

    def update_avatar(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # 根据情绪设置颜色
            emo = self.digital.emotion
            if emo == "好奇":
                Color(0.4, 0.75, 1)
            elif emo == "胆怯":
                Color(0.75, 0.6, 0.9)
            elif emo == "敏感":
                Color(0.95, 0.55, 0.65)
            elif emo == "安宁" or emo == "平静":
                Color(0.6, 0.9, 0.8)
            elif emo == "安心":
                Color(0.55, 0.85, 0.65)
            # 基础圆形小人
            w, h = self.size
            Ellipse(pos=(w*0.25, h*0.15), size=(w*0.5, w*0.5))

class MainLayout(BoxLayout):
    def __init__(self, digital, **kwargs):
        super().__init__(**kwargs)
        self.digital = digital
        self.orientation = "vertical"
        self.spacing = 8

        self.avatar = AvatarWidget(digital, size_hint_y=0.45)
        self.add_widget(self.avatar)

        self.show_label = Label(text="微光栖岛【单机本地版】", font_size=18)
        self.add_widget(self.show_label)

        self.chat_input = TextInput(hint_text="在这里和你的数字生命对话", size_hint_y=0.2)
        self.add_widget(self.chat_input)

        send_btn = Button(text="发送", size_hint_y=0.15)
        send_btn.bind(on_press=self.on_send)
        self.add_widget(send_btn)

    def on_send(self, instance):
        msg = self.chat_input.text.strip()
        if not msg:
            return
        reply = self.digital.get_response(msg)
        self.show_label.text = reply
        self.chat_input.text = ""
        self.avatar.update_avatar() # 发送消息后刷新小人外观
        self.digital.save_data()

class WeiGuangApp(App):
    def build(self):
        self.life = DigitalLife()
        self.life.load_data()
        return MainLayout(self.life)

if __name__ == "__main__":
    WeiGuangApp().run()
