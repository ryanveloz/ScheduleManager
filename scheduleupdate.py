import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

class ScheduleManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("个人日程管理 - By RyanZhao")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)  # 允许调整窗口大小
        
        # 设置窗口图标
        try:
            self.root.iconbitmap("schedule.ico")
        except:
            pass
        
        # 创建数据库连接
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schedule.db')
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()
        
        # 创建界面
        self.create_gui()
        
        # 设置主题色
        style = ttk.Style()
        style.configure("Treeview", font=('微软雅黑', 9))
        style.configure("TButton", padding=5)
        
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT '普通',
                status TEXT DEFAULT '未完成',
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        
    def create_gui(self):
        # 创建主框架
        main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧添加日程区域
        left_frame = ttk.LabelFrame(main_frame, text="添加新日程", padding=10)
        main_frame.add(left_frame, weight=1)
        
        # 输入框架
        input_frame = ttk.Frame(left_frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(input_frame, text="标题:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 日期
        ttk.Label(input_frame, text="日期:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # 时间
        ttk.Label(input_frame, text="时间:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.time_entry = ttk.Entry(input_frame)
        self.time_entry.grid(row=2, column=1, padx=5, pady=5)
        self.time_entry.insert(0, datetime.now().strftime('%H:%M'))
        
        # 优先级
        ttk.Label(input_frame, text="优先级:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.StringVar(value="普通")
        priority_frame = ttk.Frame(input_frame)
        priority_frame.grid(row=3, column=1, padx=5, pady=5)
        ttk.Radiobutton(priority_frame, text="高", variable=self.priority_var, value="高").pack(side=tk.LEFT)
        ttk.Radiobutton(priority_frame, text="普通", variable=self.priority_var, value="普通").pack(side=tk.LEFT)
        ttk.Radiobutton(priority_frame, text="低", variable=self.priority_var, value="低").pack(side=tk.LEFT)
        
        # 描述
        ttk.Label(input_frame, text="描述:").grid(row=4, column=0, sticky=tk.W+tk.N, pady=5)
        self.desc_text = tk.Text(input_frame, height=10, width=40)
        self.desc_text.grid(row=4, column=1, columnspan=2, padx=5, pady=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="添加日程", command=self.add_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空输入", command=self.clear_inputs).pack(side=tk.LEFT, padx=5)
        
        # 右侧日程列表区域
        right_frame = ttk.LabelFrame(main_frame, text="日程列表", padding=10)
        main_frame.add(right_frame, weight=2)
        
        # 搜索框
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh_list())
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 创建树形视图
        columns = ('title', 'date', 'time', 'priority', 'status')
        self.tree = ttk.Treeview(right_frame, columns=columns, show='headings')
        self.tree.heading('title', text='标题')
        self.tree.heading('date', text='日期')
        self.tree.heading('time', text='时间')
        self.tree.heading('priority', text='优先级')
        self.tree.heading('status', text='状态')
        
        # 设置列宽
        self.tree.column('title', width=200)
        self.tree.column('date', width=100)
        self.tree.column('time', width=100)
        self.tree.column('priority', width=60)
        self.tree.column('status', width=60)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 操作按钮
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="完成", command=self.mark_complete).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除", command=self.delete_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刷新", command=self.refresh_list).pack(side=tk.LEFT, padx=5)
        
        self.refresh_list()
        
    def add_schedule(self):
        title = self.title_entry.get().strip()
        date = self.date_entry.get().strip()
        time = self.time_entry.get().strip()
        priority = self.priority_var.get()
        desc = self.desc_text.get('1.0', tk.END).strip()
        
        if not all([title, date, time]):
            messagebox.showerror("错误", "请填写必要信息！")
            return
            
        try:
            datetime.strptime(date, '%Y-%m-%d')
            datetime.strptime(time, '%H:%M')
        except ValueError:
            messagebox.showerror("错误", "日期或时间格式不正确！\n日期格式：YYYY-MM-DD\n时间格式：HH:MM")
            return
            
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO schedules (title, date, time, description, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, date, time, desc, priority))
        self.conn.commit()
        
        self.clear_inputs()
        self.refresh_list()
        messagebox.showinfo("成功", "日程添加成功！")
        
    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, datetime.now().strftime('%H:%M'))
        self.priority_var.set("普通")
        self.desc_text.delete('1.0', tk.END)
        
    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        cursor = self.conn.cursor()
        search_term = self.search_var.get()
        
        if search_term:
            cursor.execute('''
                SELECT title, date, time, priority, status 
                FROM schedules 
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY date, time
            ''', (f'%{search_term}%', f'%{search_term}%'))
        else:
            cursor.execute('''
                SELECT title, date, time, priority, status 
                FROM schedules 
                ORDER BY date, time
            ''')
            
        for row in cursor.fetchall():
            self.tree.insert('', tk.END, values=row)
            
    def mark_complete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个日程！")
            return
            
        item = self.tree.item(selected[0])
        title = item['values'][0]
        date = item['values'][1]
        
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE schedules 
            SET status = '已完成'
            WHERE title = ? AND date = ?
        ''', (title, date))
        self.conn.commit()
        self.refresh_list()
        
    def delete_schedule(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个日程！")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的日程吗？"):
            item = self.tree.item(selected[0])
            title = item['values'][0]
            date = item['values'][1]
            
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM schedules WHERE title = ? AND date = ?', (title, date))
            self.conn.commit()
            self.refresh_list()
            
    def run(self):
        self.root.mainloop()
        
if __name__ == '__main__':
    app = ScheduleManager()
    app.run()