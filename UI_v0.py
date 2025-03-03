import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import openai
import json
import re
import time


class TrainingApp(tk.Toplevel):
    """分步式模型训练窗口（完整功能版）"""

    def __init__(self, master):
        super().__init__(master)
        self.title("模型训练流程")
        self.geometry("800x500")
        self.training_data = {}  # 存储训练数据

        # 创建步骤控制器
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 初始化各步骤
        self.step_frames = [
            CopywritingFrame(self.notebook, self),
            AudioTrainingFrame(self.notebook, self),
            VideoTrainingFrame(self.notebook, self)
        ]

        # 添加标签页并初始禁用
        for i, frame in enumerate(self.step_frames):
            self.notebook.add(frame, text=f"{i + 1}. {['文案生成', '声音训练', '视频训练'][i]}")
            if i > 0:
                self.notebook.tab(i, state="disabled")

        # 底部控制栏
        self.control_bar = ttk.Frame(self)
        self.control_bar.pack(fill=tk.X, padx=10, pady=10)

        # 控制按钮
        self.prev_btn = ttk.Button(self.control_bar, text="上一步", command=self.prev_step)
        self.next_btn = ttk.Button(self.control_bar, text="下一步", command=self.next_step)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        self.next_btn.pack(side=tk.RIGHT, padx=5)

        # 绑定事件
        self.notebook.bind("<<NotebookTabChanged>>", self.update_controls)

    def update_controls(self, event=None):
        """更新按钮状态"""
        current_idx = self.notebook.index("current")
        self.prev_btn["state"] = "normal" if current_idx > 0 else "disabled"
        self.next_btn["text"] = "开始训练" if current_idx == 2 else "下一步"

    def next_step(self):
        """带验证的下一步"""
        current_idx = self.notebook.index("current")

        if not self.step_frames[current_idx].validate():
            return

        if current_idx < 2:
            self.notebook.tab(current_idx + 1, state="normal")
            self.notebook.select(current_idx + 1)

    def prev_step(self):
        """返回上一步"""
        current_idx = self.notebook.index("current")
        if current_idx > 0:
            self.notebook.select(current_idx - 1)


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
        upload_frame = ttk.LabelFrame(self, text="文本上传")
        upload_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Button(upload_frame, text="上传文本文件",
                   command=self.upload_text).pack(pady=5, fill=tk.X)
        ttk.Separator(upload_frame).pack(fill=tk.X, pady=5)
        self.text_preview = scrolledtext.ScrolledText(upload_frame, wrap=tk.WORD, width=30)
        self.text_preview.pack(fill=tk.BOTH, expand=True)

        # 右侧生成区
        generate_frame = ttk.LabelFrame(self, text="文案生成")
        generate_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(generate_frame, text="生成文案",
                   command=self.generate_text).pack(pady=5, fill=tk.X)
        self.result_area = scrolledtext.ScrolledText(generate_frame, wrap=tk.WORD)
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
            except Exception as e:
                messagebox.showerror("错误", f"文件读取失败：{str(e)}")

            
    def generate_text(self):
        
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
        
        """生成文案"""
        if not self.text_preview.get(1.0, tk.END).strip():
            messagebox.showwarning("警告", "请先上传文本内容")
            return

        # 从文本框中获取内容
        input_text = self.text_preview.get(1.0, tk.END).strip()

        # 设置 OpenAI API 密钥
        openai.api_key = 'okpEeej2VMQK8WRU43De430fA8F4425191CaFe0991Ef8575'

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

        # 上传区
        upload_frame = ttk.LabelFrame(self, text="样本上传")
        upload_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(upload_frame, text="添加音频文件",
                   command=self.add_audio).pack(pady=5, fill=tk.X)
        self.file_list = tk.Listbox(upload_frame)
        self.file_list.pack(fill=tk.BOTH, expand=True)

        # 进度区
        progress_frame = ttk.LabelFrame(self, text="训练进度")
        progress_frame.pack(fill=tk.X, padx=10, pady=10)

        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        ttk.Button(progress_frame, text="开始训练",
                   command=self.start_training).pack(pady=5)

    def add_audio(self):
        files = filedialog.askopenfilenames(
            filetypes=[("音频文件", "*.wav *.mp3"), ("所有文件", "*.*")]
        )
        if files:
            self.audio_files.extend(files)
            self.file_list.delete(0, tk.END)
            for f in self.audio_files:
                self.file_list.insert(tk.END, f.split("/")[-1])
            messagebox.showinfo("成功", f"添加了{len(files)}个音频文件")

    def start_training(self):
        if not self.audio_files:
            messagebox.showwarning("错误", "请先上传音频文件")
            return

        # 模拟训练过程
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


class VideoTrainingFrame(BaseStep):
    """视频训练步骤"""

    def __init__(self, master, controller):
        super().__init__(master, controller)

        # 输入区
        input_frame = ttk.LabelFrame(self, text="输入样本")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(input_frame, text="选择视频",
                   command=self.select_video).grid(row=0, column=0, padx=5)
        ttk.Button(input_frame, text="选择音频",
                   command=self.select_audio).grid(row=0, column=1, padx=5)
        self.video_label = ttk.Label(input_frame, text="未选择视频")
        self.audio_label = ttk.Label(input_frame, text="未选择音频")
        self.video_label.grid(row=1, column=0, sticky=tk.W)
        self.audio_label.grid(row=1, column=1, sticky=tk.W)

        # 参数区
        param_frame = ttk.LabelFrame(self, text="训练参数")
        param_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(param_frame, text="训练轮数:").grid(row=0, column=0)
        self.epochs = ttk.Spinbox(param_frame, from_=1, to=100, width=5)
        self.epochs.grid(row=0, column=1)
        ttk.Button(param_frame, text="开始生成",
                   command=self.start_training).grid(row=0, column=2, padx=10)

    def select_video(self):
        if path := filedialog.askopenfilename(
                filetypes=[("视频文件", "*.mp4 *.avi"), ("所有文件", "*.*")]
        ):
            self.video_label.config(text=path.split("/")[-1])
            self.controller.training_data['video_path'] = path

    def select_audio(self):
        if path := filedialog.askopenfilename(
                filetypes=[("音频文件", "*.wav *.mp3"), ("所有文件", "*.*")]
        ):
            self.audio_label.config(text=path.split("/")[-1])
            self.controller.training_data['audio_path'] = path

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

class MainApplication(tk.Tk):
    """主窗口（完整菜单版）"""

    def __init__(self):
        super().__init__()
        self.title("数字主播X5")
        self.geometry("800x600")
        self._init_ui()
        self._training_window = None

    def _init_ui(self):
        # 主界面布局
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(main_frame,
                  text="数字主播X5",
                  font=("微软雅黑", 18, "bold"),
                  padding=20).pack()

        # 直播预览
        preview_frame = ttk.LabelFrame(main_frame, text="直播预览")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.canvas = tk.Canvas(preview_frame, bg="#F0F0F0")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 菜单系统
        menubar = tk.Menu(self)
        sys_menu = tk.Menu(menubar, tearoff=0)
        sys_menu.add_command(label="模型训练", command=self.show_training)
        sys_menu.add_command(label="预设回应管理")
        sys_menu.add_separator()
        sys_menu.add_command(label="退出", command=self.destroy)
        menubar.add_cascade(label="系统", menu=sys_menu)
        self.config(menu=menubar)

    def show_training(self):
        """显示训练窗口"""
        if self._training_window is None or not self._training_window.winfo_exists():
            self._training_window = TrainingApp(self)
        else:
            self._training_window.lift()




if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()