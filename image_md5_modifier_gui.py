"""
图片MD5修改工具 - GUI版本
带图形界面的图片MD5修改工具
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import threading
from image_md5_modifier import process_image


class ImageMD5ModifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图片MD5修改工具")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # 变量
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.num_versions = tk.IntVar(value=3)
        self.is_processing = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # 标题
        title_label = tk.Label(
            self.root, 
            text="图片MD5修改工具", 
            font=("微软雅黑", 16, "bold"),
            pady=10
        )
        title_label.pack()
        
        # 输入文件选择
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(input_frame, text="选择图片:", font=("微软雅黑", 10)).pack(anchor=tk.W)
        
        file_frame = tk.Frame(input_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        self.file_entry = tk.Entry(file_frame, textvariable=self.input_file, font=("微软雅黑", 9))
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        browse_btn = tk.Button(
            file_frame, 
            text="浏览...", 
            command=self.browse_file,
            font=("微软雅黑", 9),
            width=10
        )
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 输出目录选择
        output_frame = tk.Frame(self.root, pady=10)
        output_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(output_frame, text="输出目录 (留空则与输入文件同目录):", font=("微软雅黑", 10)).pack(anchor=tk.W)
        
        dir_frame = tk.Frame(output_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        self.dir_entry = tk.Entry(dir_frame, textvariable=self.output_dir, font=("微软雅黑", 9))
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        browse_dir_btn = tk.Button(
            dir_frame, 
            text="浏览...", 
            command=self.browse_directory,
            font=("微软雅黑", 9),
            width=10
        )
        browse_dir_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 生成数量
        num_frame = tk.Frame(self.root, pady=10)
        num_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(num_frame, text="生成数量:", font=("微软雅黑", 10)).pack(side=tk.LEFT)
        
        num_spinbox = tk.Spinbox(
            num_frame,
            from_=1,
            to=100,
            textvariable=self.num_versions,
            font=("微软雅黑", 10),
            width=10
        )
        num_spinbox.pack(side=tk.LEFT, padx=10)
        
        tk.Label(num_frame, text="张", font=("微软雅黑", 10)).pack(side=tk.LEFT)
        
        # 处理按钮
        process_btn = tk.Button(
            self.root,
            text="开始处理",
            command=self.start_processing,
            font=("微软雅黑", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            relief=tk.RAISED,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        process_btn.pack(pady=20)
        
        # 进度条
        self.progress = ttk.Progressbar(
            self.root,
            mode='indeterminate',
            length=560
        )
        self.progress.pack(pady=10, padx=20)
        
        # 日志输出区域
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(log_frame, text="处理日志:", font=("微软雅黑", 10)).pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            font=("Consolas", 9),
            wrap=tk.WORD,
            bg="#f5f5f5"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 保存原始输出
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # 重定向输出到日志
        self.redirect_output()
        
    def redirect_output(self):
        """重定向print输出到日志窗口"""
        class TextRedirector:
            def __init__(self, text_widget, root):
                self.text_widget = text_widget
                self.root = root
                
            def write(self, string):
                if string.strip():  # 只显示非空内容
                    self.text_widget.insert(tk.END, string)
                    self.text_widget.see(tk.END)
                    self.root.update_idletasks()
                
            def flush(self):
                pass
        
        sys.stdout = TextRedirector(self.log_text, self.root)
        sys.stderr = TextRedirector(self.log_text, self.root)
        
    def browse_file(self):
        """浏览选择图片文件"""
        filename = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("PNG文件", "*.png"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.input_file.set(filename)
            
    def browse_directory(self):
        """浏览选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)
            
    def start_processing(self):
        """开始处理图片"""
        if self.is_processing:
            messagebox.showwarning("警告", "正在处理中，请稍候...")
            return
            
        input_path = self.input_file.get().strip()
        if not input_path:
            messagebox.showerror("错误", "请选择输入图片文件！")
            return
            
        if not os.path.exists(input_path):
            messagebox.showerror("错误", "输入文件不存在！")
            return
            
        output_path = self.output_dir.get().strip() or None
        num_versions = self.num_versions.get()
        
        if num_versions < 1:
            messagebox.showerror("错误", "生成数量必须大于0！")
            return
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 在新线程中处理，避免界面卡顿
        self.is_processing = True
        self.progress.start()
        
        thread = threading.Thread(
            target=self.process_image_thread,
            args=(input_path, output_path, num_versions),
            daemon=True
        )
        thread.start()
        
    def process_image_thread(self, input_path, output_path, num_versions):
        """在后台线程中处理图片"""
        try:
            # 调用处理函数
            process_image(input_path, output_path, num_versions)
            
            # 处理完成
            self.root.after(0, self.processing_complete, True, "处理完成！")
        except Exception as e:
            import traceback
            error_msg = f"处理出错: {str(e)}\n{traceback.format_exc()}"
            self.root.after(0, self.processing_complete, False, error_msg)
            
    def processing_complete(self, success, message):
        """处理完成回调"""
        self.is_processing = False
        self.progress.stop()
        
        if success:
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("错误", message)


def main():
    root = tk.Tk()
    app = ImageMD5ModifierGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

