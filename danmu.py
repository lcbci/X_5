import threading
import time
import tkinter.simpledialog
from tkinter import END, messagebox
import requests
import os  # 新增导入
import glob  # 新增导入
import json  # 新增导入

is_exit = True


class Danmu():
    def __init__(self, room_id):
        self.url = 'https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory'
        self.headers = {
            'Host': 'api.live.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
        }
        self.data = {'roomid': room_id, 'csrf_token': '', 'csrf': '', 'visit_id': ''}
        self.log_file_write = open('danmu.log', mode='a', encoding='utf-8')
        log_file_read = open('danmu.log', mode='r', encoding='utf-8')
        self.log = log_file_read.readlines()

    def get_danmu(self):
        time.sleep(1)
        html = requests.post(url=self.url, headers=self.headers, data=self.data).json()
        for content in html['data']['room']:
            nickname = content['nickname']
            text = content['text']
            timeline = content['timeline'].split(" ")[1]
            msg = timeline + ' ' + nickname + ': ' + text
            if msg + '\n' not in self.log:
                listb.insert(END, msg)
                listb.see(END)
                self.log_file_write.write(msg + '\n')
                self.log.append(msg + '\n')
            nickname = text = timeline = msg = ''


def bilibili(room_id):
    bDanmu = Danmu(room_id)
    bDanmu.get_danmu()


class BilibiliThread(threading.Thread):
    def __init__(self, room_id=None):
        threading.Thread.__init__(self)
        self.room_id = room_id

    def run(self):
        global is_exit
        while not is_exit:
            bilibili(self.room_id)
            time.sleep(0.5)


# 新增保存弹幕函数
def save_danmu():
    save_dir = r'D:\X5_danmu'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 计算保存次数
    existing_files = glob.glob(os.path.join(save_dir, '*.json'))
    max_num = 0
    for file in existing_files:
        filename = os.path.basename(file).split('.')[0]
        if filename.isdigit():
            max_num = max(max_num, int(filename))
    count = max_num + 1

    # 获取并结构化弹幕数据
    items = listb.get(0, END)
    danmu_list = []
    for item in items:
        try:
            time_part, rest = item.split(' ', 1)
            nickname, text = rest.split(': ', 1)
            danmu_list.append({
                "time": time_part,
                "nickname": nickname,
                "content": text
            })
        except:
            continue

    # 保存为JSON
    filename = os.path.join(save_dir, f'{count}.json')
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(danmu_list, f, ensure_ascii=False, indent=2)
    messagebox.showinfo("保存成功", f"弹幕已保存至：{filename}")


def author():
    messagebox.showinfo(title='关于', message='作者：jonssonyan\nGitHub：jonssonyan\n日期：2021年2月4日')


window = tkinter.Tk()
window.title('BiliBli弹幕查看工具')
window.minsize(300, 110)
window.geometry('400x600+250+100')
window.wm_attributes('-topmost', 1)

menubar = tkinter.Menu(window)
menubar.add_command(label='关于', command=author)
window.config(menu=menubar)

frame = tkinter.Frame(window)
frame.pack()

frame_t = tkinter.Frame(frame)
frame_b = tkinter.Frame(frame)
frame_t.pack(side=tkinter.TOP)
frame_b.pack(side=tkinter.BOTTOM)

tkinter.Label(frame_t, text='请输入房间号：', width=10, font=('Arial', 10)).pack(side=tkinter.LEFT)
default_text = tkinter.StringVar()
default_text.set("32155509")
e1 = tkinter.Entry(frame_t, show=None, width=15, textvariable=default_text, font=('Arial', 10))
e1.pack(side=tkinter.LEFT)

# 新增保存按钮
b3 = tkinter.Button(frame_t, text='保存弹幕', width=10, command=save_danmu, font=('Arial', 10))  # 新增按钮
b3.pack(side=tkinter.LEFT)  # 新增按钮布局


def start_point():
    try:
        room = e1.get()
        room_int = int(room)
        e1.configure(state=tkinter.DISABLED)
        b1.configure(state=tkinter.DISABLED)
        b2.configure(state=tkinter.NORMAL)
        if room_int is not None:
            global is_exit
            is_exit = False
            t = BilibiliThread()
            t.room_id = room_int
            t.setDaemon(True)
            t.start()
    except ValueError:
        messagebox.showinfo(title='警告', message='输入的房间号格式不正确,请再次尝试输入!')


def end_point():
    global is_exit
    is_exit = True
    e1.configure(state=tkinter.NORMAL)
    b1.configure(state=tkinter.NORMAL)
    b2.configure(state=tkinter.DISABLED)


b1 = tkinter.Button(frame_t, text='开始', width=10, command=start_point, font=('Arial', 10))
b1.pack(side=tkinter.LEFT)
b2 = tkinter.Button(frame_t, text='停止', width=10, command=end_point, font=('Arial', 10))
b2.pack(side=tkinter.LEFT)

sc = tkinter.Scrollbar(frame_b)
sc.pack(side=tkinter.RIGHT, fill=tkinter.Y)
listb = tkinter.Listbox(frame_b, yscrollcommand=sc.set, width=200, height=120)
listb.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
sc.config(command=listb.yview)

window.mainloop()