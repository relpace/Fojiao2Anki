import base64
import json
import requests
import gzip
from io import BytesIO
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def remove_newlines(input_string: str) -> str:
    return input_string.replace('\n', '').replace('\r', '')

def download(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            messagebox.showerror("下载错误", f"无法下载文件，状态码：{response.status_code}")
            return None
    except Exception as e:
        messagebox.showerror("下载错误", f"下载时发生错误：{e}")
        return None

def process_file(n, i):
    url = f"https://f.7-xk.com/shuati/qFile/{n}.{i}.q"
    file_data = download(url)
    if not file_data:
        return None
    try:
        bin_data = base64.b64encode(file_data).decode('utf-8')
        a = {'bin': bin_data, 'q_time': i}
        bin_data = base64.b64decode(a['bin'])
        
        # 注意：原代码中 bin_data[1:]，假设是去掉第一个字节
        with gzip.GzipFile(fileobj=BytesIO(bin_data[1:])) as gz:
            decompressed_data = gz.read()
        
        u = json.loads(decompressed_data.decode('utf-8'))
        qs = [dict(item, i=str(item['i']), o=[o for o in item['o'] if o]) for item in u]
        return qs
    except Exception as e:
        messagebox.showerror("处理错误", f"处理文件时发生错误：{e}")
        return None


def is_chinese(str):
    for i in str:
        if '\u4e00' <= i <= '\u9fa5':
            return True
        

def transform(name, qs, n, i, save_path):
    try:
        file_path = os.path.join(save_path, f"{n}_{name}.txt")
        with open(file_path, 'a', encoding='utf-8') as file:
            headers = "#separator:tab\n#html:true\n#deck column:1\n#tags column:7\n"
            file.write(headers)
            separator = "\t"
            n_qs = len(qs)
            for idx in range(n_qs):
                options = []
                answers = []
                if int(qs[idx]['k']) != 4: #不是判断题
                    for o in range(len(qs[idx]['o'])):
                        options.append(remove_newlines(str(qs[idx]['o'][o])))
                else:
                    options =['对','错']
                for a in range(len(qs[idx]['a'])):
                    answers.append(remove_newlines(str(qs[idx]['a'][a])))
                difficulty = remove_newlines(str(qs[idx]['d']))
                false = remove_newlines(qs[idx]['f'])
                question = remove_newlines(qs[idx]['s'])
                answer = ''
                for j in range(len(answers)):
                    answer += str(ord(answers[j].upper()) - ord("A") + 1)
                tag=''
                if len(answers) != 1:
                    tag = "多选"
                elif int(qs[idx]['k']) != 4:
                    tag = "单选"
                else:
                    tag = "判断"
                if not is_chinese(question):
                    tag+= " 英文"
                # 正确处理 {{c1::}}，需要在f-string中转义花括号
                line = (
                    f"{name}{separator}"
                    f"{name}#{idx}{separator}"
                    f"{question}:{{{{c1::}}}}{separator}"
                    f"{'||'.join(options)}{separator}"
                    f"{'||'.join(answer)}{separator}"
                    f"难度:{difficulty}；易错项:{false}{separator}{tag}\n"
                )
                file.write(line)
        messagebox.showinfo("成功", f"文件已成功保存到 {file_path}")
    except Exception as e:
        messagebox.showerror("写入错误", f"写入文件时发生错误：{e}")

def on_submit():
    n = entry_id.get().strip()
    name = entry_name.get().strip()
    save_path = entry_save.get().strip()

    if not n:
        messagebox.showwarning("输入缺失", "请填写题库ID。")
        return
    if not name:
        messagebox.showwarning("输入缺失", "请填写题库名称。")
        return
    if not save_path:
        messagebox.showwarning("输入缺失", "请选择保存位置。")
        return

    i = "123"  # 如果需要用户输入 'i'，可以添加一个输入框
    qs = process_file(n, i)
    if qs:
        transform(name, qs, n, i, save_path)

def browse_save_location():
    path = filedialog.askdirectory()
    if path:
        entry_save.delete(0, tk.END)
        entry_save.insert(0, path)

# 创建主窗口
root = tk.Tk()
root.title("题库处理工具")
root.geometry("500x250")
root.resizable(False, False)

# 题库ID
label_id = tk.Label(root, text="题库ID:")
label_id.pack(pady=(20, 0))
entry_id = tk.Entry(root, width=50)
entry_id.pack()

# 题库名称
label_name = tk.Label(root, text="题库名称:")
label_name.pack(pady=(10, 0))
entry_name = tk.Entry(root, width=50)
entry_name.pack()

# 保存位置
frame_save = tk.Frame(root)
frame_save.pack(pady=(10, 0))

label_save = tk.Label(frame_save, text="保存位置:")
label_save.pack(side=tk.LEFT)

entry_save = tk.Entry(frame_save, width=40)
entry_save.pack(side=tk.LEFT, padx=(5, 0))

button_browse = tk.Button(frame_save, text="浏览", command=browse_save_location)
button_browse.pack(side=tk.LEFT, padx=(5, 0))

# 提交按钮
button_submit = tk.Button(root, text="开始处理", command=on_submit, width=20, height=2)
button_submit.pack(pady=(20, 0))

# 运行主循环
root.mainloop()
