import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import openai
import json
import re
import time
import pygame
from gradio_client import Client, file
import shutil
import os
from PIL import Image, ImageTk

# 温馨主题配置
THEME = {
    "primary_color": "#98FB98",
    "secondary_color": "#76EEC6",
    "background_color": "#F0FFF0",
    "preview_color": "#E0FFFF",
    "font_family": "Microsoft YaHei Light",
    "button_color": "#90EE90",
    "hover_color": "#98FB98"
}


class ReplyPresetFrame(tk.Toplevel):
    """集成主窗口风格的预制回复管理窗口"""

    def __init__(self, master):
        super().__init__(master)
        self.title("🌸 预制回复 🌸")
        self.geometry("900x600")
        self.media_folder = "D:/25038/Documents/" #预制回应媒体文件夹
        self.current_file = None
        self._init_styles()
        self._init_ui()
        self._load_media_files()

    def _init_styles(self):
        """继承主窗口样式配置"""
        self.configure(bg=THEME["background_color"])
        self.option_add('*TButton*highlightBackground', THEME["background_color"])
        self.option_add('*TButton*highlightColor', THEME["background_color"])

    def _init_ui(self):
        """构建界面布局（继承主窗口组件结构）"""
        # 主容器分栏布局
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧媒体列表（带滚动条）
        left_frame = ttk.LabelFrame(main_frame, text="📁 媒体库", style="Cute.TLabelframe")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动区域实现（参考网页1）
        self.canvas = tk.Canvas(left_frame, bg=THEME["preview_color"])
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)

        self.scroll_frame.bind("<Configure>",
                               lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 右侧控制面板
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 播放按钮（集成CuteButton样式）
        self.preview_btn = CuteButton(right_frame, text="播放媒体",
                                      command=self._play_media)
        self.preview_btn.pack(pady=30, fill=tk.X)

        # 预览面板（继承视频训练窗口的缩略图显示）
        self.preview_panel = tk.Canvas(right_frame, bg=THEME["preview_color"],
                                       width=500, height=500)
        self.preview_panel.pack(pady=30)

        # 状态标签（保持字体统一）
        self.status_label = ttk.Label(right_frame, text="等待选择媒体文件...",
                                      font=(THEME["font_family"], 10))
        self.status_label.pack(pady=10)

    def _load_media_files(self):
        """加载媒体文件（集成文案生成窗口的异常处理）"""
        try:
            media_files = [f for f in os.listdir(self.media_folder)
                           if f.lower().endswith(('.mp3', '.mp4', '.wav'))]
            for filename in media_files:
                self._create_media_item(filename)
        except FileNotFoundError:
            messagebox.showerror("错误", f"媒体文件夹不存在：{self.media_folder}")

    def _create_media_item(self, filename):
        """创建媒体列表项（集成单选按钮交互）"""
        frame = ttk.Frame(self.scroll_frame)
        rb = ttk.Radiobutton(frame, text=filename, value=filename,
                             command=lambda: self._select_file(filename))
        rb.pack(side=tk.LEFT, padx=5)

        # 文件类型标识（继承主窗口图标风格）
        icon = "🎵" if filename.endswith(('.mp3', '.wav')) else "🎥"
        ttk.Label(frame, text=icon, font=("Arial", 12)).pack(side=tk.LEFT)
        frame.pack(fill=tk.X, pady=2)

    def _select_file(self, filename):
        """处理文件选择（集成视频训练窗口的预览功能）"""
        self.current_file = os.path.join(self.media_folder, filename)
        self.status_label.config(text=f"已选择：{filename}")

        # 显示预览（完全复用视频训练窗口的缩略图逻辑）
        if filename.endswith('.mp4'):
            self._show_video_thumbnail()
        else:
            self.preview_panel.delete("all")
            self.preview_panel.create_text(150, 150, text="🎧 音频文件",
                                           font=(THEME["font_family"], 14))

    def _show_video_thumbnail(self):
        """显示视频首帧（完全复用视频训练窗口代码）"""
        import cv2
        cap = cv2.VideoCapture(self.current_file)
        ret, frame = cap.read()
        cap.release()

        if ret:
            frame = cv2.resize(frame, (300, 300))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.thumbnail = ImageTk.PhotoImage(Image.fromarray(frame))
            self.preview_panel.create_image(0, 0, image=self.thumbnail, anchor=tk.NW)

    def _play_media(self):
        if self.current_file.endswith(('.mp4', '.avi')):
            import cv2
            cap = cv2.VideoCapture(self.current_file)
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    imgtk = ImageTk.PhotoImage(img)
                    self.preview_panel.create_image(0, 0, image=imgtk, anchor=tk.NW)
                    self.preview_panel.imgtk = imgtk  # 防止图像被垃圾回收
                    self.update_idletasks()
                else:
                    break
            cap.release()
        else:
            """播放媒体（集成声音训练窗口的音频播放）"""
            if not self.current_file:
                messagebox.showwarning("警告", "请先选择媒体文件")
                return

            if self.current_file.endswith(('.mp3', '.wav')):
                pygame.mixer.music.load(self.current_file)
                pygame.mixer.music.play()
                self.status_label.config(text="正在播放音频...")
            else:
                messagebox.showinfo("提示", "视频播放功能需调用视频解码库实现")
                self.status_label.config(text="暂不支持视频播放")

    def destroy(self):
        """窗口销毁处理（继承音频训练窗口的资源释放）"""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        super().destroy()





class CuteButton(ttk.Button):
    """带可爱动画效果的按钮"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def on_hover(self, event):
        self.config(style="Cute.TButton")

    def on_leave(self, event):
        self.config(style="TButton")

class TrainingApp(tk.Toplevel):
    """分步式模型训练窗口（可爱风格版）"""
    
    def __init__(self, master):
        super().__init__(master)
        self.title("🌸 模型训练流程 🌸")
        self.geometry("800x500")
        self.configure(bg=THEME["background_color"])
        self.training_data = {}
        
        # 创建步骤控制器
        self.notebook = ttk.Notebook(self, style="Cute.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 初始化各步骤
        self.step_frames = [
            CopywritingFrame(self.notebook, self),
            AudioTrainingFrame(self.notebook, self),
            VideoTrainingFrame(self.notebook, self)
        ]

        # 添加可爱风格的标签页
        for i, frame in enumerate(self.step_frames):
            self.notebook.add(frame, text=f"🌸 {['文案生成', '声音训练', '视频训练'][i]}")

        # 底部控制栏
        self.control_bar = ttk.Frame(self)
        self.control_bar.pack(fill=tk.X, padx=10, pady=10)

        # 控制按钮
        self.prev_btn = CuteButton(self.control_bar, text="上一步", command=self.prev_step)
        self.next_btn = CuteButton(self.control_bar, text="下一步", command=self.next_step)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        self.next_btn.pack(side=tk.RIGHT, padx=5)

        # 绑定事件
        self.notebook.bind("<<NotebookTabChanged>>", self.update_controls)

    def update_controls(self, event=None):
        current_idx = self.notebook.index("current")
        self.prev_btn["state"] = "normal" if current_idx > 0 else "disabled"
        self.next_btn["text"] = "开始训练" if current_idx == 2 else "下一步"

    def prev_step(self):
        current_idx = self.notebook.index("current")
        if current_idx > 0:
            self.notebook.select(current_idx - 1)

    def next_step(self):
        current_idx = self.notebook.index("current")
        if current_idx < 2:
            if self.step_frames[current_idx].validate():
                self.notebook.select(current_idx + 1)
        else:
            self.start_training()

    def start_training(self):
        if all(frame.validate() for frame in self.step_frames):
            messagebox.showinfo("训练完成", "所有步骤已完成，开始训练...")
            # 在这里添加训练逻辑
        else:
            messagebox.showwarning("验证失败", "请完成所有步骤")

class CopywritingFrame(ttk.Frame):
    """可爱风格文案生成步骤"""
    
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.generated = False
        
        # 左侧上传区
        upload_frame = ttk.LabelFrame(self, text="📁 文本上传区", style="Cute.TLabelframe")
        upload_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        CuteButton(upload_frame, text="上传文本文件", command=self.upload_text).pack(pady=5, fill=tk.X)
        
        self.text_preview = scrolledtext.ScrolledText(upload_frame, wrap=tk.WORD, width=30,
                                                    bg="#FFF0F5", font=("微软雅黑", 10))
        self.text_preview.pack(fill=tk.BOTH, expand=True)

        # 右侧生成区
        generate_frame = ttk.LabelFrame(self, text="✨ 文案生成区", style="Cute.TLabelframe")
        generate_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        CuteButton(generate_frame, text="生成文案", command=self.generate_text).pack(pady=5, fill=tk.X)
        
        self.result_area = scrolledtext.ScrolledText(generate_frame, wrap=tk.WORD,
                                                   bg="#FFF0F5", font=("微软雅黑", 10))
        self.result_area.pack(fill=tk.BOTH, expand=True)

    def upload_text(self):
        """上传文本文件"""
        filetypes = [("文本文件", "*.txt"), ("所有文件", "*.*")]
        if path := filedialog.askopenfilename(filetypes=filetypes):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_preview.delete(1.0, tk.END)
                    self.text_preview.insert(tk.END, content)
                    messagebox.showinfo("上传成功", f"已加载文件：{path.split('/')[-1]}")
            except FileNotFoundError:
                messagebox.showerror("错误", "文件未找到，请检查路径是否正确")
            except PermissionError:
                messagebox.showerror("错误", "无法读取文件，请检查文件权限")
            except Exception as e:
                messagebox.showerror("错误", f"文件读取失败：{str(e)}")

    def generate_text(self):
        """生成文案"""
        def save_bracketed_content_to_json(text, filename="output.json"):
            try:
                # 删除 <think> 和 </think> 标签之间的内容
                text_without_think = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
                
                # 使用正则表达式提取 [] 中的内容
                bracketed_content = re.findall(r'\[(.*?)\]', text_without_think)
                
                if bracketed_content:
                    # 将提取的内容保存到字典中
                    data = {"bracketed_content": bracketed_content}
                    
                    # 打开 JSON 文件并写入内容
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    
                    print(f"已将内容保存到 {filename}")
                else:
                    print("没有找到任何被 [] 括起来的内容。")
            
            except Exception as e:
                print(f"保存内容到 JSON 文件时发生错误: {str(e)}")
        
        if not self.text_preview.get(1.0, tk.END).strip():
            messagebox.showwarning("警告", "请先上传文本内容")
            return

        # 从文本框中获取内容
        input_text = self.text_preview.get(1.0, tk.END).strip()

        # 设置 OpenAI API 密钥
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            messagebox.showerror("错误", "未设置 OpenAI API 密钥，请检查环境变量 OPENAI_API_KEY")
            return

        # 设置基础 URL
        openai.base_url = "http://activity.scnet.cn:61080/v1/"

        try:
            # 创建完成任务
            completion = openai.chat.completions.create(
                model="DeepSeek-R1-Distill-Qwen-32B",
                messages=[
                    {
                        "role": "user",
                        "content": "假设我是一个带货主播，根据我要卖的商品，生成文案（要求文案开头有'[',结尾有']',方便我识别），我要卖的商品是："+input_text,
                    },
                ],
                stream=True,  # 设置为流式输出
            )
            
            # 清空结果区
            self.result_area.delete(1.0, tk.END)

            # 逐步处理API返回的数据，直到完成
            full_text = ""  # 用于存储最终文案内容
            for chunk in completion:
                if len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:  # 确保 content 不是空值
                        full_text += content  # 将内容累积到full_text中
                        self.after(0, lambda c=content: self.result_area.insert(tk.END, c))  # 异步更新UI
                        self.after(0, lambda: self.result_area.yview(tk.END))  # 自动滚动到最新内容

            # 文案生成成功
            self.generated = True
            self.controller.training_data['copywriting'] = input_text
            save_bracketed_content_to_json(full_text)
            
        except openai.error.OpenAIError as e:
            messagebox.showerror("API 错误", f"OpenAI API 错误：{str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"生成文案时出错：{str(e)}")

    def validate(self):
        if not self.generated:
            messagebox.showwarning("验证失败", "请先生成文案")
            return False
        return True


class MainApplication(tk.Tk):
    """主窗口（完整功能可爱版）"""
    
    def __init__(self):
        super().__init__()
        self.title("🌸 数字主播X5 🌸")
        self.geometry("1000x600")  # 增加窗口宽度以适应直播预览
        self._init_styles()
        self._init_ui()
        self._training_window = None
        self._response_preset_window = None

    def _init_styles(self):
        """初始化可爱风格"""
        style = ttk.Style()
        style.theme_use("default")
        
        # 按钮样式
        style.configure("TButton", font=("微软雅黑", 12), padding=6)
        style.map("Cute.TButton",
                background=[("active", "#76EEC6"), ("!active", "#98FB98")],
                foreground=[("active", "#000000"), ("!active", "#000000")])
                
        # 标签样式
        style.configure("TLabel", background=THEME["background_color"], font=("微软雅黑", 14))
        style.configure("Title.TLabel", font=("微软雅黑", 18, "bold"), foreground="#006400")
        
        # 框架样式
        style.configure("Cute.TLabelframe", 
                      background=THEME["background_color"],
                      bordercolor="#76EEC6",
                      relief="solid")

    def _init_ui(self):
        """主界面布局"""
        # 标题
        title_label = ttk.Label(self, text="🌸 欢迎来到数字主播X5 🌸", style="Title.TLabel")
        title_label.pack(pady=20)

        # 主功能区
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # 直播预览区
        preview_frame = ttk.LabelFrame(main_frame, text="🌈 直播预览 🌈", style="Cute.TLabelframe")
        preview_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.canvas = tk.Canvas(preview_frame, bg=THEME["preview_color"], width=400, height=300)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # 功能按钮区
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        BUTTONS = [
            ("🎥 开始直播", self.show_live_stream),
            ("📝 文案生成", self.show_copywriting_frame),
            ("🎶 声音训练", self.show_audio_training_frame),
            ("🎬 视频训练", self.show_video_training_frame),
            ("   预制回复", self.show_reply_frame),
            ("❌ 退出", self.quit)
        ]
        
        for text, command in BUTTONS:
            self._create_button(button_frame, text, command)

    def _create_button(self, parent, text, command):
        """创建按钮并绑定命令"""
        button = CuteButton(parent, text=text, command=lambda cmd=command: self._safe_execute(cmd))
        button.config(style="Cute.TButton")  # 设置按钮样式为Cute.TButton
        button.pack(pady=10, fill=tk.X)

    def _safe_execute(self, func):
        """安全执行按钮命令，捕获异常"""
        try:
            func()
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {e}")

    def show_live_stream(self):
        """显示直播预览窗口"""
        # 创建直播预览窗口
        live_stream_window = tk.Toplevel(self)
        live_stream_window.title("🌸 直播预览 🌸")
        live_stream_window.geometry("800x500")
        live_stream_window.configure(bg=THEME["background_color"])
        
        # 直播预览区
        preview_frame = ttk.LabelFrame(live_stream_window, text="🌈 直播预览 🌈", style="Cute.TLabelframe")
        preview_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        canvas = tk.Canvas(preview_frame, bg=THEME["preview_color"], width=400, height=300)
        canvas.pack(expand=True, fill=tk.BOTH)

        # 控制栏
        control_bar = ttk.Frame(live_stream_window)
        control_bar.pack(fill=tk.X, padx=10, pady=10)

        # 控制按钮
        CuteButton(control_bar, text="开始直播", command=lambda: messagebox.showinfo("直播预览", "直播预览功能正在开发中...")).pack(side=tk.LEFT, padx=5)
        CuteButton(control_bar, text="结束直播", command=live_stream_window.destroy).pack(side=tk.RIGHT, padx=5)

    def show_copywriting_frame(self):
        """显示文案生成窗口"""
        if self._training_window is None or not self._training_window.winfo_exists():
            self._training_window = TrainingApp(self)
            self._training_window.notebook.select(0)  # 选择第一个标签页（文案生成）
            self._training_window.grab_set()
        else:
            self._training_window.lift()
            self._training_window.notebook.select(0)  # 选择第一个标签页（文案生成）

    def show_audio_training_frame(self):
        """显示声音训练窗口"""
        if self._training_window is None or not self._training_window.winfo_exists():
            self._training_window = TrainingApp(self)
            self._training_window.notebook.select(1)  # 选择第二个标签页（声音训练）
            self._training_window.grab_set()
        else:
            self._training_window.lift()
            self._training_window.notebook.select(1)  # 选择第二个标签页（声音训练）

    def show_video_training_frame(self):
        """显示视频训练窗口"""
        if self._training_window is None or not self._training_window.winfo_exists():
            self._training_window = TrainingApp(self)
            self._training_window.notebook.select(2)  # 选择第三个标签页（视频训练）
            self._training_window.grab_set()
        else:
            self._training_window.lift()
            self._training_window.notebook.select(2)  # 选择第三个标签页（视频训练）

    def show_reply_frame(self):
        """显示预制回复管理窗口（集成现有窗口管理逻辑）"""
        if not hasattr(self, '_reply_window') or not self._reply_window.winfo_exists():
            self._reply_window = ReplyPresetFrame(self)
            self._reply_window.grab_set()
        else:
            self._reply_window.lift()
    def show_reply_frame(self):  # 后定义调用方法
        if not hasattr(self, '_reply_window') or not self._reply_window.winfo_exists():
            self._reply_window = ReplyPresetFrame(self)  # ✅ 此时类已定义
            self._reply_window.grab_set()
        else:
            self._reply_window.lift()

class BaseStep(ttk.Frame):
    """步骤基类"""

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

    def validate(self):
        """验证步骤完成（子类实现）"""
        return True

class CopywritingFrame(BaseStep):
    """文案生成步骤"""

    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.generated = False
        self.current_file = None  # 跟踪当前文件路径

        # 左侧上传区
        upload_frame = ttk.LabelFrame(self, text="文本上传", style="Cute.TLabelframe")
        upload_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20, expand=True)

        ttk.Button(upload_frame, text="上传文本文件",
                   command=self.upload_text).pack(pady=10, fill=tk.X)
        ttk.Separator(upload_frame).pack(fill=tk.X, pady=10)

        # 用户输入区
        self.user_input = scrolledtext.ScrolledText(upload_frame, wrap=tk.WORD, width=30, height=10,
                                                   bg="#F0FFF0", font=("微软雅黑", 10))
        self.user_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 添加标签提示
        ttk.Label(upload_frame, text="上传文本预览", style="TLabel").pack(anchor=tk.NW, padx=10, pady=5)

        # 上传文本显示区
        self.text_preview = scrolledtext.ScrolledText(upload_frame, wrap=tk.WORD, width=30, height=10,
                                                    bg="#F0FFF0", font=("微软雅黑", 10))
        self.text_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 添加标签提示
        ttk.Label(upload_frame, text="手动输入文本", style="TLabel").pack(anchor=tk.NW, padx=10, pady=5)

        # 右侧生成区
        generate_frame = ttk.LabelFrame(self, text="文案生成", style="Cute.TLabelframe")
        generate_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Button(generate_frame, text="生成文案",
                   command=self.generate_text).pack(pady=10, fill=tk.X)
        self.result_area = scrolledtext.ScrolledText(generate_frame, wrap=tk.WORD, height=20,
                                                   bg="#F0FFF0", font=("微软雅黑", 10))
        self.result_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def upload_text(self):
        """上传文本文件"""
        filetypes = [("文本文件", "*.txt"), ("所有文件", "*.*")]
        if path := filedialog.askopenfilename(filetypes=filetypes):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_preview.delete(1.0, tk.END)
                    self.text_preview.insert(tk.END, content)
                    messagebox.showinfo("上传成功", f"已加载文件：{os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("错误", f"文件读取失败：{str(e)}")

    def generate_text(self):
        """生成文案"""
        def save_bracketed_content_to_json(text, filename="output.json"):
            try:
                # 删除 <think> 和 </think> 标签之间的内容
                text_without_think = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
                
                # 使用正则表达式提取 [] 中的内容
                bracketed_content = re.findall(r'\[(.*?)\]', text_without_think)
                
                if bracketed_content:
                    # 将提取的内容保存到字典中
                    data = {"bracketed_content": bracketed_content}
                    
                    # 打开 JSON 文件并写入内容
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    
                    print(f"已将内容保存到 {filename}")
                else:
                    print("没有找到任何被 [] 括起来的内容。")
            
            except Exception as e:
                print(f"保存内容到 JSON 文件时发生错误: {str(e)}")
        
        if not self.text_preview.get(1.0, tk.END).strip():
            messagebox.showwarning("警告", "请先上传文本内容")
            return

        # 从文本框中获取内容
        input_text = self.text_preview.get(1.0, tk.END).strip()

        # 设置 OpenAI API 密钥
        openai.api_key = 'yJp1OukONYi67su4B698E011605742A88a8f4590437664Fc'

        # 设置基础 URL
        openai.base_url = "http://activity.scnet.cn:61080/v1/"

        try:
            # 创建完成任务
            completion = openai.chat.completions.create(
                model="DeepSeek-R1-Distill-Qwen-32B",
                messages=[{
                    "role": "user",
                    "content": "假设我是一个带货主播，根据我要卖的商品，生成文案（要求文案开头有'[',结尾有']',方便我识别），我要卖的商品是："+input_text,
                }],
                stream=True,  # 设置为流式输出
            )
            
            # 清空结果区
            self.result_area.delete(1.0, tk.END)

            # 逐步处理API返回的数据，直到完成
            full_text = ""  # 用于存储最终文案内容
            for chunk in completion:
                if len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:  # 确保 content 不是空值
                        full_text += content  # 将内容累积到full_text中
                        self.result_area.insert(tk.END, content)  # 插入内容
                        self.result_area.yview(tk.END)  # 自动滚动到最新内容
                        self.result_area.update()  # 强制更新UI

            # 文案生成成功
            self.generated = True
            self.controller.training_data['copywriting'] = input_text
            save_bracketed_content_to_json(full_text)
            
        except Exception as e:
            print(e)
            messagebox.showerror("错误", f"生成文案时出错：{str(e)}")

    def validate(self):
        if not self.generated:
            messagebox.showwarning("验证失败", "请先生成文案")
            return False
        return True

class AudioTrainingFrame(BaseStep):
    """声音训练步骤"""

    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.audio_files = []
        self.current_audio_path = None  # 新增：存储当前音频文件路径
        self.output_file = "output/audio_output.wav"

        # 上传区
        upload_frame = ttk.LabelFrame(self, text="样本上传", style="Cute.TLabelframe")
        upload_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Button(upload_frame, text="添加音频文件",
                   command=self.add_audio).pack(pady=10, fill=tk.X)
        self.file_list = tk.Listbox(upload_frame, height=10)
        self.file_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 输入区
        input_frame = ttk.LabelFrame(self, text="输入音频对应文本内容")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=5)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # 进度区
        progress_frame = ttk.LabelFrame(self, text="训练进度", style="Cute.TLabelframe")
        progress_frame.pack(fill=tk.X, padx=20, pady=20)

        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=300)
        self.progress.pack(fill=tk.X, pady=10)
        ttk.Button(progress_frame, text="开始训练",
                   command=self.start_training).pack(pady=10)

    def add_audio(self):
        files = filedialog.askopenfilenames(
            filetypes=[("音频文件", "*.wav *.mp3"), ("所有文件", "*.*")]
        )
        if files:
            self.audio_files.extend(files)
            self.current_audio_path = files
            self.file_list.delete(0, tk.END)
            for f in self.audio_files:
                self.file_list.insert(tk.END, f.split("/")[-1])
            messagebox.showinfo("成功", f"添加了{len(files)}个音频文件")

    def start_training(self):
        if not self.audio_files:
            messagebox.showwarning("错误", "请先上传音频文件")
            return

        # 获取输入文本框的内容
        input_content = self.input_text.get(1.0, tk.END).strip()
        if not input_content:
            messagebox.showwarning("错误", "请输入训练文本")
            return

        # 模拟训练过程
        self.get_audio()
        self.progress['value'] = 0
        self._simulate_progress()

    def _simulate_progress(self):
        if self.progress['value'] < 100:
            self.progress['value'] += 10
            self.after(500, self._simulate_progress)
        else:
            self.controller.training_data['audio_model'] = "训练完成"
            messagebox.showinfo("完成", "声音训练已完成！")

    def validate(self):
        if 'audio_model' not in self.controller.training_data:
            messagebox.showwarning("验证失败", "请先完成声音训练")
            return False
        return True

    def get_audio(self):
        json_file_path = "output.json"  # 假设 JSON 文件路径为 output.json

        try:
            # 读取 JSON 文件
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 从 JSON 数据中提取文本
            if "bracketed_content" in data and data["bracketed_content"]:
                audiotext = data["bracketed_content"][0]  # 使用第一个 [] 中的内容
            else:
                messagebox.showwarning("警告", "JSON 文件中未找到有效内容")
                return
        except FileNotFoundError:
            messagebox.showerror("错误", f"未找到 JSON 文件：{json_file_path}")
        except json.JSONDecodeError:
            messagebox.showerror("错误", "JSON 文件格式错误")
        except Exception as e:
            messagebox.showerror("错误", f"读取 JSON 文件时出错：{str(e)}")

        text_content = self.input_text.get("1.0", "end-1c")

        client = Client("https://75af8b77611414691b.gradio.live/")

        client.predict(
            api_name="/change_choices"
        )

        client.predict(
            sovits_path="SoVITS_weights_v3/x5_e2_s30_l32.pth",
            prompt_language="中文",
            text_language="中文",
            api_name="/change_sovits_weights"
        )

        client.predict(
            gpt_path="GPT_weights_v3/x5-e15.ckpt",
            api_name="/change_gpt_weights"
        )

        audio_result = client.predict(
            ref_wav_path=file('data/1.mp3'),
            prompt_text=text_content,
            prompt_language="中文",
            text=audiotext,
            text_language="中文",
            how_to_cut="凑四句一切",
            top_k=15,
            top_p=1,
            temperature=1,
            ref_free=False,
            speed=1,
            if_freeze=False,
            inp_refs=None,
            sample_steps=32,
            api_name="/get_tts_wav"
        )

        output_path = "output/audio_output.wav"
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # 移动文件到新的输出路径
        shutil.move(audio_result, output_path)

class VideoTrainingFrame(BaseStep):
    """视频训练步骤"""

    def __init__(self, master, controller):
        super().__init__(master, controller)
        pygame.mixer.init()  # 初始化pygame的混音器

        # 主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 视频选择区
        video_frame = ttk.LabelFrame(main_frame, text="选择视频", style="Cute.TLabelframe")
        video_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Button(video_frame, text="选择视频",
                   command=self.select_video).grid(row=0, column=0, padx=5, pady=5)
        self.video_label = ttk.Label(video_frame, text="未选择视频", font=("微软雅黑", 10))
        self.video_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)

        # 视频预览窗口
        self.video_preview_frame = ttk.LabelFrame(video_frame, text="视频预览", style="Cute.TLabelframe")
        self.video_preview_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.video_preview_canvas = tk.Canvas(self.video_preview_frame, bg="black", height=200, width=400)
        self.video_preview_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 音频选择区
        audio_frame = ttk.LabelFrame(main_frame, text="选择音频", style="Cute.TLabelframe")
        audio_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ttk.Button(audio_frame, text="选择音频",
                   command=self.select_audio).grid(row=0, column=0, padx=5, pady=5)
        self.audio_label = ttk.Label(audio_frame, text="未选择音频", font=("微软雅黑", 10))
        self.audio_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)

        # 音频预览窗口
        self.audio_preview_frame = ttk.LabelFrame(audio_frame, text="音频预览", style="Cute.TLabelframe")
        self.audio_preview_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        # 音频控制按钮
        audio_control_frame = ttk.Frame(audio_frame)
        audio_control_frame.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        ttk.Button(audio_control_frame, text="播放", command=self.play_audio).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(audio_control_frame, text="暂停", command=self.pause_audio).grid(row=0, column=1, padx=5, pady=5)

        # 参数区
        param_frame = ttk.LabelFrame(self, text="训练参数", style="Cute.TLabelframe")
        param_frame.pack(fill=tk.X, padx=20, pady=20)

        ttk.Label(param_frame, text="训练轮数:", font=("微软雅黑", 10)).grid(row=0, column=0, padx=10, pady=5)
        self.epochs = ttk.Spinbox(param_frame, from_=1, to=100, width=5)
        self.epochs.grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(param_frame, text="开始生成",
                   command=self.start_training).grid(row=0, column=2, padx=10, pady=5)

    def select_video(self):
        if path := filedialog.askopenfilename(
                filetypes=[("视频文件", "*.mp4 *.avi"), ("所有文件", "*.*")]
        ):
            self.video_label.config(text=path.split("/")[-1])
            self.controller.training_data['video_path'] = path
            self.display_video_frame(path)

    def display_video_frame(self, video_path):
        import cv2
        # 读取视频的第一帧
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        if ret:
            # 调整帧大小以适应画布
            frame = cv2.resize(frame, (400, 200))
            # 将BGR格式转换为RGB格式
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 创建图像对象
            img = Image.fromarray(frame)
            # 将图像转换为Tkinter兼容的格式
            self.photo = ImageTk.PhotoImage(img)
            # 在画布上显示图像
            self.video_preview_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def select_audio(self):
        if path := filedialog.askopenfilename(
                filetypes=[("音频文件", "*.wav *.mp3"), ("所有文件", "*.*")]
        ):
            self.audio_label.config(text=path.split("/")[-1])
            self.controller.training_data['audio_path'] = path
            # 在音频预览窗口中显示音频
            self.audio_preview_canvas.create_text(200, 100, text="音频预览", fill="white")
            self.audio_path = path  # 保存音频路径

    def play_audio(self):
        if hasattr(self, 'audio_path'):
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.play()

    def pause_audio(self):
        pygame.mixer.music.pause()

    def start_training(self):
        if not all(key in self.controller.training_data for key in ('video_path', 'audio_path')):
            messagebox.showwarning("错误", "请先选择视频和音频文件")
            return

        messagebox.showinfo("开始", "视频生成任务已启动...")
        self.controller.training_data['video_model'] = "生成完成"

    def validate(self):
        if 'video_model' not in self.controller.training_data:
            messagebox.showwarning("验证失败", "请先完成视频生成")
            return False
        return True

class ResponsePresetManager(tk.Toplevel):
    """增强版回应预设管理窗口"""
    
    def __init__(self, master):
        super().__init__(master)
        self.title("智能回应预设管理")
        self.geometry("800x600")
        
        # 初始化容器结构
        self._create_ui_containers()
        self._setup_keyword_input()
        self._setup_display_area()
        
        # 数据存储结构
        self.keyword_frames = {}  # 存储关键词与对应视频区的映射

    def _create_ui_containers(self):
        """创建三层容器结构"""
        self.top_frame = ttk.Frame(self)
        self.mid_frame = ttk.LabelFrame(self, text="关键词列表")
        self.bottom_frame = ttk.LabelFrame(self, text="视频展示区")
        
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        self.mid_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _setup_keyword_input(self):
        """顶部输入区域"""
        self.keyword_entry = ttk.Entry(self.top_frame, width=40)
        self.keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(self.top_frame, text="添加关键词", 
                 command=self.add_keyword).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.top_frame, text="清空输入",
                 command=lambda: self.keyword_entry.delete(0, tk.END)).pack(side=tk.LEFT)

    def _setup_display_area(self):
        """中下部展示区域"""
        # 关键词列表区（带滚动条）
        self.keyword_canvas = tk.Canvas(self.mid_frame)
        self.scrollbar = ttk.Scrollbar(self.mid_frame, orient="vertical", 
                                     command=self.keyword_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.keyword_canvas)
        
        # 配置Canvas滚动
        self.scrollable_frame.bind("<Configure>", 
            lambda e: self.keyword_canvas.configure(scrollregion=self.keyword_canvas.bbox("all")))
        self.keyword_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.keyword_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 视频展示区初始化
        self.video_container = ttk.Frame(self.bottom_frame)
        self.video_container.pack(fill=tk.BOTH, expand=True)
        
        # 布局
        self.keyword_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_keyword(self):
        """增强版添加关键词功能"""
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning("输入错误", "请输入有效关键词")
            return
        
        # 创建关键词标签
        keyword_frame = ttk.Frame(self.scrollable_frame)
        ttk.Label(keyword_frame, text=f"🔑 {keyword}", 
                font=('微软雅黑', 10)).pack(side=tk.LEFT)
        
        # 添加操作按钮
        ttk.Button(keyword_frame, text="预览", width=6,
                 command=lambda k=keyword: self.preview_video(k)).pack(side=tk.LEFT, padx=5)
        ttk.Button(keyword_frame, text="删除", width=6,
                 command=lambda: self.delete_keyword(keyword)).pack(side=tk.LEFT)
        
        # 创建对应的视频展示区
        video_frame = ttk.LabelFrame(self.video_container, text=f"视频区 - {keyword}")
        self._create_video_placeholder(video_frame)
        
        # 存储关联关系
        self.keyword_frames[keyword] = {
            'label_frame': keyword_frame,
            'video_frame': video_frame
        }
        
        # 动态布局更新
        keyword_frame.pack(fill=tk.X, pady=2)
        video_frame.pack_forget()  # 初始隐藏视频区
        
        self.keyword_entry.delete(0, tk.END)
        self.update_idletasks()
        self.keyword_canvas.configure(scrollregion=self.keyword_canvas.bbox("all"))

    def _create_video_placeholder(self, parent):
        """创建视频占位界面（可扩展为真实视频播放）"""
        placeholder = ttk.Frame(parent, width=320, height=240)
        ttk.Label(placeholder, text="视频加载区", 
                relief="sunken", background="#f0f0f0").pack(expand=True)
        
        # 模拟视频控制按钮
        control_frame = ttk.Frame(placeholder)
        ttk.Button(control_frame, text="▶", width=4).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="⏸", width=4).pack(side=tk.LEFT)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X)
        placeholder.pack_propagate(False)
        placeholder.pack(pady=5)

    def preview_video(self, keyword):
        """显示对应关键词的视频区"""
        # 隐藏所有视频区
        for frame in self.keyword_frames.values():
            frame['video_frame'].pack_forget()
        
        # 显示选中视频区
        target_frame = self.keyword_frames[keyword]['video_frame']
        target_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 滚动到可视区域
        self.bottom_frame.update_idletasks()
        self.video_container.yview_moveto(0)

    def delete_keyword(self, keyword):
        """删除关键词及其关联元素"""
        if keyword in self.keyword_frames:
            self.keyword_frames[keyword]['label_frame'].destroy()
            self.keyword_frames[keyword]['video_frame'].destroy()
            del self.keyword_frames[keyword]
            self.update_layout()

    def update_layout(self):
        """动态更新布局"""
        self.keyword_canvas.configure(scrollregion=self.keyword_canvas.bbox("all"))
        self.update_idletasks()


if __name__ == "__main__":
    pygame.mixer.init()
    app = MainApplication()
    app.mainloop()