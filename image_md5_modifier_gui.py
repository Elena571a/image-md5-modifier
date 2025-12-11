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
        self.input_files = []  # 改为列表存储多个文件
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
        
        tk.Label(input_frame, text="选择图片 (可多选):", font=("微软雅黑", 10)).pack(anchor=tk.W)
        
        file_frame = tk.Frame(input_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        # 使用Listbox显示多个文件
        listbox_frame = tk.Frame(file_frame)
        listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            listbox_frame,
            font=("微软雅黑", 9),
            height=3,
            yscrollcommand=scrollbar.set
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        btn_frame = tk.Frame(file_frame)
        btn_frame.pack(side=tk.RIGHT, padx=(5, 0))
        
        browse_btn = tk.Button(
            btn_frame, 
            text="浏览...", 
            command=self.browse_files,
            font=("微软雅黑", 9),
            width=10
        )
        browse_btn.pack(pady=2)
        
        clear_btn = tk.Button(
            btn_frame,
            text="清空",
            command=self.clear_files,
            font=("微软雅黑", 9),
            width=10
        )
        clear_btn.pack(pady=2)
        
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
        
        # 作者信息
        author_frame = tk.Frame(self.root, bg="#f0f0f0", pady=5)
        author_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        author_label = tk.Label(
            author_frame,
            text="作者：小杨 | 微信：Zi_ming1020 | 欢迎反馈",
            font=("微软雅黑", 8),
            fg="#666",
            bg="#f0f0f0"
        )
        author_label.pack()
        
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
        
    def browse_files(self):
        """浏览选择多个图片文件"""
        filenames = filedialog.askopenfilenames(
            title="选择图片文件（可多选）",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("PNG文件", "*.png"),
                ("所有文件", "*.*")
            ]
        )
        if filenames:
            for filename in filenames:
                if filename not in self.input_files:
                    self.input_files.append(filename)
                    self.file_listbox.insert(tk.END, os.path.basename(filename))
    
    def clear_files(self):
        """清空已选择的文件"""
        self.input_files.clear()
        self.file_listbox.delete(0, tk.END)
            
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
            
        if not self.input_files:
            messagebox.showerror("错误", "请选择至少一个图片文件！")
            return
        
        # 验证所有文件是否存在
        for file_path in self.input_files:
            if not os.path.exists(file_path):
                messagebox.showerror("错误", f"文件不存在: {os.path.basename(file_path)}")
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
            target=self.process_images_thread,
            args=(self.input_files.copy(), output_path, num_versions),
            daemon=True
        )
        thread.start()
        
    def process_images_thread(self, input_files, output_path, num_versions):
        """在后台线程中处理多个图片"""
        try:
            total = len(input_files)
            success_count = 0
            failed_files = []
            
            for i, input_path in enumerate(input_files, 1):
                try:
                    print(f"\n[{i}/{total}] 正在处理: {os.path.basename(input_path)}")
                    process_image(input_path, output_path, num_versions)
                    success_count += 1
                    print(f"✓ 完成: {os.path.basename(input_path)}")
                except Exception as e:
                    failed_files.append((os.path.basename(input_path), str(e)))
                    print(f"✗ 失败: {os.path.basename(input_path)} - {str(e)}")
            
            # 处理完成
            if failed_files:
                msg = f"处理完成！成功: {success_count}/{total}\n失败的文件:\n" + "\n".join([f"  - {f[0]}: {f[1]}" for f in failed_files])
            else:
                msg = f"处理完成！成功处理 {success_count} 个文件。"
            self.root.after(0, self.processing_complete, True, msg)
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

