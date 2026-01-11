import tkinter as tk
from tkinter import ttk, colorchooser
import json

class ScreenMarker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("屏幕标记工具")
        self.root.geometry("1000x600")
        
        self.markers = []
        self.overlay_window = None
        self.canvas = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 顶部控制区
        top_frame = tk.Frame(self.root, bg='#f0f0f0', pady=10)
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text="屏幕标记工具", font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(side=tk.LEFT, padx=20)
        
        self.show_btn = tk.Button(top_frame, text="显示标记", command=self.toggle_overlay, 
                                   bg='#4CAF50', fg='white', font=('Arial', 10), padx=20, pady=5)
        self.show_btn.pack(side=tk.RIGHT, padx=20)
        
        # 说明区
        info_frame = tk.Frame(self.root, bg='#e3f2fd', pady=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(info_frame, text="使用说明: 输入一个坐标点 (x1, y1) 标记点 | 输入两个坐标点 (x1, y1) 和 (x2, y2) 标记矩形框 | 可添加备注文字",
                font=('Arial', 9), bg='#e3f2fd').pack()
        
        # 标记列表区域
        list_container = tk.Frame(self.root, bg='white')
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.markers_container = tk.Frame(list_container, bg='white')
        self.markers_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加按钮
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(btn_frame, text="+ 添加标记", command=self.add_marker,
                 bg='#2196F3', fg='white', font=('Arial', 10, 'bold'), padx=30, pady=8).pack()
        
        # 添加初始标记
        self.add_marker()
        
    def add_marker(self):
        marker_id = len(self.markers)
        marker_data = {
            'id': marker_id,
            'x1': tk.StringVar(),
            'y1': tk.StringVar(),
            'x2': tk.StringVar(),
            'y2': tk.StringVar(),
            'note': tk.StringVar(),
            'color': '#FF0000',
            'frame': None
        }
        self.markers.append(marker_data)
        
        # 创建标记行
        row = tk.Frame(self.markers_container, bg='#f5f5f5', pady=8, padx=10, relief=tk.RAISED, bd=1)
        row.pack(fill=tk.X, pady=3, padx=5)
        marker_data['frame'] = row
        
        # 序号
        tk.Label(row, text=f"#{marker_id + 1}", font=('Arial', 11, 'bold'), 
                bg='#f5f5f5', width=4).pack(side=tk.LEFT, padx=5)
        
        # 颜色选择
        color_frame = tk.Frame(row, bg='#f5f5f5')
        color_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(color_frame, text="颜色:", bg='#f5f5f5', font=('Arial', 9)).pack(side=tk.LEFT)
        color_btn = tk.Button(color_frame, text="  ", bg=marker_data['color'], width=4, height=1,
                             command=lambda m=marker_data: self.choose_color(m))
        color_btn.pack(side=tk.LEFT, padx=3)
        marker_data['color_btn'] = color_btn
        
        # 点1输入
        point1_frame = tk.Frame(row, bg='#f5f5f5')
        point1_frame.pack(side=tk.LEFT, padx=8)
        
        tk.Label(point1_frame, text="点1:", bg='#f5f5f5', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=3)
        tk.Label(point1_frame, text="x:", bg='#f5f5f5', font=('Arial', 9)).pack(side=tk.LEFT)
        tk.Entry(point1_frame, textvariable=marker_data['x1'], width=7, font=('Arial', 10)).pack(side=tk.LEFT, padx=2)
        tk.Label(point1_frame, text="y:", bg='#f5f5f5', font=('Arial', 9)).pack(side=tk.LEFT, padx=(5,0))
        tk.Entry(point1_frame, textvariable=marker_data['y1'], width=7, font=('Arial', 10)).pack(side=tk.LEFT, padx=2)
        
        # 点2输入
        point2_frame = tk.Frame(row, bg='#f5f5f5')
        point2_frame.pack(side=tk.LEFT, padx=8)
        
        tk.Label(point2_frame, text="点2:", bg='#f5f5f5', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=3)
        tk.Label(point2_frame, text="x:", bg='#f5f5f5', font=('Arial', 9)).pack(side=tk.LEFT)
        tk.Entry(point2_frame, textvariable=marker_data['x2'], width=7, font=('Arial', 10)).pack(side=tk.LEFT, padx=2)
        tk.Label(point2_frame, text="y:", bg='#f5f5f5', font=('Arial', 9)).pack(side=tk.LEFT, padx=(5,0))
        tk.Entry(point2_frame, textvariable=marker_data['y2'], width=7, font=('Arial', 10)).pack(side=tk.LEFT, padx=2)
        
        # 备注输入
        note_frame = tk.Frame(row, bg='#f5f5f5')
        note_frame.pack(side=tk.LEFT, padx=8)
        
        tk.Label(note_frame, text="备注:", bg='#f5f5f5', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=3)
        tk.Entry(note_frame, textvariable=marker_data['note'], width=15, font=('Arial', 10)).pack(side=tk.LEFT, padx=2)
        
        # 删除按钮
        tk.Button(row, text="✕ 删除", command=lambda m=marker_data: self.delete_marker(m),
                 bg='#f44336', fg='white', font=('Arial', 9, 'bold'), padx=10).pack(side=tk.RIGHT, padx=5)
        
        # 强制更新界面
        self.root.update_idletasks()
        
    def choose_color(self, marker_data):
        color = colorchooser.askcolor(initialcolor=marker_data['color'])[1]
        if color:
            marker_data['color'] = color
            marker_data['color_btn'].config(bg=color)
            if self.overlay_window:
                self.draw_markers()
    
    def delete_marker(self, marker_data):
        if marker_data['frame']:
            marker_data['frame'].destroy()
        self.markers.remove(marker_data)
        if self.overlay_window:
            self.draw_markers()
    
    def toggle_overlay(self):
        if self.overlay_window:
            self.hide_overlay()
        else:
            self.show_overlay()
    
    def show_overlay(self):
        # 创建全屏透明窗口
        self.overlay_window = tk.Toplevel(self.root)
        self.overlay_window.attributes('-fullscreen', True)
        self.overlay_window.attributes('-topmost', True)
        self.overlay_window.attributes('-alpha', 0.7)
        
        # Windows系统设置透明点击
        try:
            self.overlay_window.attributes('-transparentcolor', 'white')
        except:
            pass
        
        # 创建画布
        screen_width = self.overlay_window.winfo_screenwidth()
        screen_height = self.overlay_window.winfo_screenheight()
        
        self.canvas = tk.Canvas(self.overlay_window, width=screen_width, height=screen_height,
                               bg='white', highlightthickness=0)
        self.canvas.pack()
        
        # 绑定ESC键关闭覆盖层
        self.overlay_window.bind('<Escape>', lambda e: self.hide_overlay())
        
        self.draw_markers()
        self.show_btn.config(text="隐藏标记 (ESC)", bg='#f44336')
    
    def hide_overlay(self):
        if self.overlay_window:
            self.overlay_window.destroy()
            self.overlay_window = None
            self.canvas = None
            self.show_btn.config(text="显示标记", bg='#4CAF50')
    
    def draw_markers(self):
        if not self.canvas:
            return
        
        self.canvas.delete('all')
        
        for marker in self.markers:
            try:
                x1 = marker['x1'].get().strip()
                y1 = marker['y1'].get().strip()
                x2 = marker['x2'].get().strip()
                y2 = marker['y2'].get().strip()
                note = marker['note'].get().strip()
                
                if not x1 or not y1:
                    continue
                
                x1 = int(x1)
                y1 = int(y1)
                color = marker['color']
                
                # 只有第一个点 - 绘制圆点
                if not x2 or not y2:
                    # 外圈
                    self.canvas.create_oval(x1-10, y1-10, x1+10, y1+10, 
                                          outline=color, width=3)
                    # 内圈实心
                    self.canvas.create_oval(x1-6, y1-6, x1+6, y1+6, 
                                          fill=color, outline='white', width=2)
                    
                    # 绘制备注在点的左上方
                    if note:
                        # 背景框
                        text_id = self.canvas.create_text(x1, y1-15, text=note, 
                                                         font=('Arial', 11, 'bold'), 
                                                         anchor='s', fill='black')
                        bbox = self.canvas.bbox(text_id)
                        self.canvas.create_rectangle(bbox[0]-3, bbox[1]-2, bbox[2]+3, bbox[3]+2,
                                                    fill=color, outline='white', width=2)
                        # 重新绘制文字在最上层
                        self.canvas.create_text(x1, y1-15, text=note, 
                                              font=('Arial', 11, 'bold'), 
                                              anchor='s', fill='white')
                else:
                    # 两个点 - 绘制矩形
                    x2 = int(x2)
                    y2 = int(y2)
                    
                    left = min(x1, x2)
                    top = min(y1, y2)
                    
                    # 矩形边框
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                                outline=color, width=3)
                    # 半透明填充
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                                fill=color, stipple='gray25', outline='')
                    
                    # 绘制备注在矩形左上方
                    if note:
                        # 背景框
                        text_id = self.canvas.create_text(left, top-5, text=note, 
                                                         font=('Arial', 11, 'bold'), 
                                                         anchor='sw', fill='black')
                        bbox = self.canvas.bbox(text_id)
                        self.canvas.create_rectangle(bbox[0]-3, bbox[1]-2, bbox[2]+3, bbox[3]+2,
                                                    fill=color, outline='white', width=2)
                        # 重新绘制文字在最上层
                        self.canvas.create_text(left, top-5, text=note, 
                                              font=('Arial', 11, 'bold'), 
                                              anchor='sw', fill='white')
                    
            except ValueError:
                continue
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenMarker()
    app.run()