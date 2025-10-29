# flolower_os_v10_with_real_browser.py
# Требуется: pip install PyQt5 PyQtWebEngine

import tkinter as tk
import random, time, json, os, calendar, datetime
import subprocess
from PIL import Image, ImageTk
import webbrowser
from tkinter import ttk
import sys
import threading

# Попытка импортировать Qt WebEngine
try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtWebEngineWidgets import *
    from PyQt5.QtGui import *
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    print("Qt WebEngine не установлен. Используется демо-режим браузера.")
    print("Установите: pip install PyQt5 PyQtWebEngine")

# Попытка импортировать pyjokes
try:
    import pyjokes
except Exception:
    pyjokes = None

# ------------------ Config ------------------
BG = "#0f0b18"
MENU_BG = "#231a30"
MENU_ITEM = "#2b2036"
TASKBAR_BG = "#18121f"
WINDOW_BG = "#241b2b"
TITLE_BG = "#2a2030"
TEXT = "white"

APP_LIST = [
    ("🔢", "Калькулятор", "calculator"),
    ("🗒️", "Заметки", "notes"),
    ("🌐", "Браузер", "browser"),
    ("📅", "Календарь", "calendar"),
    ("💻", "Терминал", "terminal"),
]

DESKTOP_ICONS = [
    ("🔢", "Калькулятор", "calculator"),
    ("🗒️", "Заметки", "notes"),
    ("📅", "Календарь", "calendar"),
    ("💻", "Терминал", "terminal"),
]

ICON_FONT = ("Segoe UI Emoji", 34)
TITLE_FONT = ("Segoe UI", 10, "bold")
TEXT_FONT = ("Segoe UI", 10)
ICON_POS_FILE = "icons_pos_v10.json"
NOTES_SAVE_PATH = r"D:\замітки.txt"
PINNED_APPS_FILE = "pinned_apps_v10.json"

# ------------------ Root ------------------
root = tk.Tk()
root.title("Flolower OS v1.0(beta)")
root.attributes("-fullscreen", True)
root.configure(bg=BG)
SW, SH = root.winfo_screenwidth(), root.winfo_screenheight()

# ------------------ Load saved icon positions ------------------
try:
    if os.path.exists(ICON_POS_FILE):
        with open(ICON_POS_FILE, "r", encoding="utf-8") as f:
            saved_positions = json.load(f)
    else:
        saved_positions = {}
except Exception:
    saved_positions = {}

# ------------------ Load pinned apps ------------------
try:
    if os.path.exists(PINNED_APPS_FILE):
        with open(PINNED_APPS_FILE, "r", encoding="utf-8") as f:
            pinned_apps = json.load(f)
    else:
        pinned_apps = []
except Exception:
    pinned_apps = []

# ------------------ Canvas abstract wallpaper ------------------
canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
canvas.place(relwidth=1, relheight=1)

class AbstractCircle:
    def __init__(self, x, y, r, color, vx, vy):
        self.x, self.y, self.r = x, y, r
        self.color = color
        self.vx, self.vy = vx, vy
        self.oid = canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")

    def step(self):
        self.x += self.vx
        self.y += self.vy
        if self.x - self.r < 0 or self.x + self.r > SW: self.vx *= -1
        if self.y - self.r < 0 or self.y + self.r > SH: self.vy *= -1
        canvas.coords(self.oid, self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r)

    def fade_color(self):
        try:
            r = min(255, max(50, int(int(self.color[1:3],16)+random.randint(-4,4))))
            g = min(255, max(50, int(int(self.color[3:5],16)+random.randint(-4,4))))
            b = min(255, max(50, int(int(self.color[5:7],16)+random.randint(-4,4))))
            self.color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.itemconfig(self.oid, fill=self.color)
        except Exception:
            pass

abstract_circles = []
for _ in range(35):
    r = random.randint(80, 200)
    x = random.randint(r, SW-r)
    y = random.randint(r, SH-r)
    color = random.choice(["#ff4d4d","#4dffff","#ffff4d","#ff4dff","#4dff4d"])
    vx = random.uniform(-0.15,0.15)
    vy = random.uniform(-0.1,0.1)
    abstract_circles.append(AbstractCircle(x,y,r,color,vx,vy))

def animate_abstract():
    for c in abstract_circles:
        c.step(); c.fade_color()
    root.after(60, animate_abstract)

animate_abstract()
canvas.tag_lower("all")

# ------------------ Desktop ------------------
desktop = tk.Frame(root, bg=BG)
desktop.place(relwidth=1, relheight=1)

# ------------------ Taskbar ------------------
TASK_H = 56
taskbar = tk.Frame(root, bg=TASKBAR_BG, height=TASK_H)
taskbar.pack(side="bottom", fill="x")

# Загрузка и отображение изображения вместо кнопки "Пуск"
try:
    start_img = Image.open("Frame 14.png")
    start_img = start_img.resize((40, 40), Image.Resampling.LANCZOS)
    start_photo = ImageTk.PhotoImage(start_img)
    
    start_btn = tk.Label(taskbar, image=start_photo, bg=TASKBAR_BG, cursor="hand2")
    start_btn.image = start_photo
    start_btn.pack(side="left", padx=12, pady=8)
    
except Exception as e:
    print(f"Ошибка загрузки изображения: {e}")
    start_btn = tk.Button(taskbar, text="⊞ Пуск", bg=MENU_BG, fg=TEXT, font=TEXT_FONT, bd=0, padx=12, pady=6)
    start_btn.pack(side="left", padx=12, pady=6)

# Фрейм для закрепленных приложений
pinned_frame = tk.Frame(taskbar, bg=TASKBAR_BG)
pinned_frame.pack(side="left", padx=8, pady=6)

# Фрейм для открытых окон
task_buttons_frame = tk.Frame(taskbar, bg=TASKBAR_BG)
task_buttons_frame.pack(side="left", padx=8, pady=6)

time_lbl = tk.Label(taskbar, text=time.strftime("%H:%M"), bg=TASKBAR_BG, fg=TEXT, font=TEXT_FONT)
time_lbl.pack(side="right", padx=12)
def tick_time(): time_lbl.config(text=time.strftime("%H:%M")); root.after(1000,tick_time)
tick_time()
task_buttons={}

# ------------------ Pinned apps on taskbar ------------------
pinned_buttons = {}

def save_pinned_apps():
    try:
        with open(PINNED_APPS_FILE, "w", encoding="utf-8") as f:
            json.dump(pinned_apps, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def create_pinned_button(emoji, title, key):
    btn = tk.Button(pinned_frame, text=emoji, bg=TASKBAR_BG, fg=TEXT, font=("Segoe UI Emoji", 16),
                   bd=0, padx=8, pady=4, width=2,
                   command=lambda: open_app_window(key, title))
    btn.pack(side="left", padx=2)
    
    def show_tooltip(event):
        tooltip = tk.Toplevel(root)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root-30}")
        label = tk.Label(tooltip, text=title, bg="#333333", fg="white", padx=6, pady=2)
        label.pack()
        btn.tooltip = tooltip
        
    def hide_tooltip(event):
        if hasattr(btn, 'tooltip'):
            btn.tooltip.destroy()
            
    btn.bind("<Enter>", show_tooltip)
    btn.bind("<Leave>", hide_tooltip)
    
    pinned_buttons[key] = btn
    return btn

def pin_app(key, title, emoji):
    if key not in pinned_apps:
        pinned_apps.append(key)
        save_pinned_apps()
        create_pinned_button(emoji, title, key)

def unpin_app(key):
    if key in pinned_apps:
        pinned_apps.remove(key)
        save_pinned_apps()
        if key in pinned_buttons:
            pinned_buttons[key].destroy()
            del pinned_buttons[key]

# Инициализация закрепленных приложений при запуске
for app_key in pinned_apps:
    for emoji, title, key in APP_LIST:
        if key == app_key:
            create_pinned_button(emoji, title, key)
            break

# ------------------ Start menu ------------------
MENU_W = min(560,int(SW*0.52))
MENU_H = min(560,int(SH*0.62))
MENU_X = (SW-MENU_W)//2
MENU_Y_SHOWN = (SH-MENU_H)//2
MENU_Y_HIDDEN = SH+20
start_menu = tk.Frame(root, bg=MENU_BG, bd=0)
start_menu.place(x=MENU_X, y=MENU_Y_HIDDEN, width=MENU_W, height=MENU_H)
menu_visible=False

search_var = tk.StringVar()
search_entry = tk.Entry(start_menu,textvariable=search_var,bg="#2b2334",fg=TEXT,bd=0,font=TEXT_FONT,insertbackground=TEXT)
search_entry.place(x=16,y=16,width=MENU_W-32,height=36)
apps_frame = tk.Frame(start_menu,bg=MENU_BG)
apps_frame.place(x=16,y=72,width=MENU_W-32,height=MENU_H-88)
app_widgets=[]

def on_start_app(app_key, app_title):
    toggle_menu(False)
    open_app_window(app_key, app_title)

for emoji,title,key in APP_LIST:
    row=tk.Frame(apps_frame,bg=MENU_ITEM,height=44)
    row.pack(fill="x", pady=6)
    ico=tk.Label(row,text=emoji,bg=MENU_ITEM,fg=TEXT,font=ICON_FONT)
    ico.pack(side="left", padx=(8,10))
    
    text_pin_frame = tk.Frame(row, bg=MENU_ITEM)
    text_pin_frame.pack(side="left", fill="x", expand=True)
    
    lbl=tk.Label(text_pin_frame,text=title,bg=MENU_ITEM,fg=TEXT,font=TEXT_FONT,anchor="w")
    lbl.pack(side="left", fill="x", expand=True)
    
    pin_btn = tk.Button(text_pin_frame, text="📌" if key in pinned_apps else "📍", 
                       bg=MENU_ITEM, fg=TEXT, bd=0, font=("Segoe UI Emoji", 12),
                       command=lambda k=key, t=title, e=emoji: toggle_pin(k, t, e))
    pin_btn.pack(side="right", padx=(0, 8))
    
    for w in (row,ico,lbl): 
        w.bind("<Button-1>", lambda e,k=key,t=title:on_start_app(k,t))
    app_widgets.append((row,title))

def toggle_pin(key, title, emoji):
    if key in pinned_apps:
        unpin_app(key)
    else:
        pin_app(key, title, emoji)
    for widget in apps_frame.winfo_children():
        for child in widget.winfo_children():
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Button) and grandchild['text'] in ("📌", "📍"):
                        if key in pinned_apps:
                            grandchild.config(text="📌")
                        else:
                            grandchild.config(text="📍")

def refresh_app_list(*_):
    q=search_var.get().lower().strip()
    for w,title in app_widgets:
        w.pack_forget()
        if not q or q in title.lower(): w.pack(fill="x",pady=6)
search_var.trace_add("write", refresh_app_list)

def show_menu():
    global menu_visible
    if menu_visible: return
    menu_visible=True; start_menu.lift()
    steps=12; start_y=MENU_Y_HIDDEN; dy=(MENU_Y_SHOWN-start_y)/steps
    def step(i=0):
        if i<=steps: y=int(start_y+dy*i); start_menu.place(y=y); root.after(10,lambda:step(i+1))
        else: start_menu.place(y=MENU_Y_SHOWN); search_entry.focus_set()
    step()

def hide_menu():
    global menu_visible
    if not menu_visible: return
    menu_visible=False; steps=10; start_y=MENU_Y_SHOWN; dy=(MENU_Y_HIDDEN-start_y)/steps
    def step(i=0):
        if i<=steps: y=int(start_y+dy*i); start_menu.place(y=y); root.after(10,lambda:step(i+1))
        else: start_menu.place(y=MENU_Y_HIDDEN)
    step()

def toggle_menu(force=None):
    if force is None: hide_menu() if menu_visible else show_menu()
    elif force: show_menu()
    else: hide_menu()

start_btn.bind("<Button-1>", lambda e: toggle_menu())
root.bind("<Button-1>", lambda e: hide_menu() if menu_visible and not start_menu.winfo_containing(e.x_root,e.y_root) else None, add="+")
root.bind("<Key>", lambda e: toggle_menu() if e.keysym in ("Super_L","Super_R") else None)
root.bind("<Escape>", lambda e: hide_menu())

# ------------------ Window system ------------------
open_windows=[]
pinned_windows = {}

def create_task_button(win, title):
    btn = tk.Button(task_buttons_frame, text=title, bg="#2a2233", fg=TEXT, bd=0, padx=8, pady=4,
                   command=lambda: toggle_window(win))
    btn.pack(side="left", padx=4)
    
    def show_task_menu(event):
        menu = tk.Menu(root, tearoff=0, bg=MENU_BG, fg=TEXT)
        
        is_pinned = win in pinned_windows
        
        if is_pinned:
            menu.add_command(label="Открепить от панели задач", 
                           command=lambda: unpin_window(win, btn))
        else:
            menu.add_command(label="Закрепить в панели задач", 
                           command=lambda: pin_window(win, btn))
        
        menu.add_separator()
        menu.add_command(label="Закрыть", command=lambda: close_window(win, btn))
        menu.tk_popup(event.x_root, event.y_root)
    
    btn.bind("<Button-3>", show_task_menu)
    task_buttons[win] = btn
    return btn

def toggle_window(win):
    if win.state() == 'withdrawn':
        win.deiconify()
        win.lift()
    else:
        win.withdraw()

def pin_window(win, btn):
    if win not in pinned_windows:
        pinned_windows[win] = True
        btn.config(bg="#4a3255")
        
def unpin_window(win, btn):
    if win in pinned_windows:
        del pinned_windows[win]
        btn.config(bg="#2a2233")

def close_window(win, btn):
    try:
        if win in pinned_windows:
            del pinned_windows[win]
        
        if win in task_buttons:
            del task_buttons[win]
        btn.destroy()
    except:
        pass
    
    try:
        win.destroy()
    except:
        pass

# ------------------ Real Browser Functionality ------------------
def build_browser(parent):
    """Создает интерфейс браузера в окне Flolower OS"""
    
    class BrowserInterface:
        def __init__(self, master):
            self.master = master
            self.create_browser_interface()
            
        def create_browser_interface(self):
            # Главный фрейм браузера
            main_frame = tk.Frame(self.master, bg=WINDOW_BG)
            main_frame.pack(expand=True, fill="both", padx=0, pady=0)
            
            if QT_AVAILABLE:
                self.create_qt_browser_interface(main_frame)
            else:
                self.create_demo_browser_interface(main_frame)
        
        def create_qt_browser_interface(self, parent):
            """Создает интерфейс для реального браузера с Qt"""
            # Панель навигации
            nav_frame = tk.Frame(parent, bg="#2b2036", height=50)
            nav_frame.pack(fill="x", padx=0, pady=0)
            nav_frame.pack_propagate(False)
            
            # Кнопки навигации
            nav_buttons = tk.Frame(nav_frame, bg="#2b2036")
            nav_buttons.pack(side="left", padx=8, pady=8)
            
            back_btn = tk.Button(nav_buttons, text="←", bg="#3a2b45", fg=TEXT, bd=0,
                               font=("Segoe UI", 12), width=2, command=self.launch_browser)
            back_btn.pack(side="left", padx=2)
            
            forward_btn = tk.Button(nav_buttons, text="→", bg="#3a2b45", fg=TEXT, bd=0,
                                  font=("Segoe UI", 12), width=2, command=self.launch_browser)
            forward_btn.pack(side="left", padx=2)
            
            reload_btn = tk.Button(nav_buttons, text="↻", bg="#3a2b45", fg=TEXT, bd=0,
                                 font=("Segoe UI", 12), width=2, command=self.launch_browser)
            reload_btn.pack(side="left", padx=2)
            
            home_btn = tk.Button(nav_buttons, text="⌂", bg="#3a2b45", fg=TEXT, bd=0,
                               font=("Segoe UI", 12), width=2, command=lambda: self.launch_browser("https://www.google.com"))
            home_btn.pack(side="left", padx=2)
            
            # Адресная строка
            url_frame = tk.Frame(nav_frame, bg="#2b2036")
            url_frame.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            
            self.url_var = tk.StringVar(value="https://www.google.com")
            url_entry = tk.Entry(url_frame, textvariable=self.url_var, bg="#1b1820", fg=TEXT,
                               font=TEXT_FONT, bd=1, relief="solid", insertbackground=TEXT)
            url_entry.pack(side="left", fill="x", expand=True)
            url_entry.bind("<Return>", lambda e: self.launch_browser())
            
            go_btn = tk.Button(url_frame, text="→", bg="#4d7fff", fg=TEXT, bd=0,
                             font=("Segoe UI", 12), width=2, command=lambda: self.launch_browser())
            go_btn.pack(side="left", padx=5)
            
            # Быстрый доступ к сайтам
            quick_access_frame = tk.Frame(parent, bg=WINDOW_BG)
            quick_access_frame.pack(fill="x", padx=12, pady=10)
            
            tk.Label(quick_access_frame, text="🚀 Быстрый доступ:", 
                    bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")
            
            sites_frame = tk.Frame(quick_access_frame, bg=WINDOW_BG)
            sites_frame.pack(fill="x", pady=8)
            
            sites = [
                ("🔍 Google", "https://www.google.com"),
                ("📺 YouTube", "https://www.youtube.com"),
                ("💻 GitHub", "https://www.github.com"),
                ("📚 Wikipedia", "https://www.wikipedia.org"),
                ("🛒 Amazon", "https://www.amazon.com"),
                ("💬 Reddit", "https://www.reddit.com")
            ]
            
            for name, url in sites:
                btn = tk.Button(sites_frame, text=name, bg="#2b2036", fg=TEXT, 
                              font=TEXT_FONT, bd=0, padx=12, pady=6,
                              command=lambda u=url: self.launch_browser(u))
                btn.pack(side="left", padx=4, pady=2)
            
            # Информация о браузере
            info_frame = tk.Frame(parent, bg=WINDOW_BG)
            info_frame.pack(fill="both", expand=True, padx=12, pady=12)
            
            info_text = """
╔══════════════════════════════════════════════════════════════╗
║                   FLOLOWER BROWSER                           ║
║                 Режим: Qt WebEngine                          ║
╚══════════════════════════════════════════════════════════════╝

✅ ВАШ БРАУЗЕР ГОТОВ К РАБОТЕ!

🌐 ВОЗМОЖНОСТИ:
• Полноценный веб-серфинг через Qt WebEngine
• Поддержка всех современных веб-стандартов
• Быстрый движок Chromium
• Воспроизведение видео и аудио
• Поддержка JavaScript
• Безопасное соединение (HTTPS)

🚀 КАК ИСПОЛЬЗОВАТЬ:
1. Нажмите на кнопку с сайтом для быстрого доступа
2. Или введите любой URL в адресную строку выше
3. Нажмите Enter или кнопку "→" для перехода

💡 ПОДСКАЗКИ:
• Браузер откроется в отдельном окне с полным функционалом
• Используйте Ctrl+T для новой вкладки
• Ctrl+D чтобы добавить в закладки
• F5 для обновления страницы

🔧 ТЕХНОЛОГИИ:
• Qt WebEngine 5.15+
• Chromium движок
• Аппаратное ускорение
"""
            
            text_widget = tk.Text(info_frame, bg="#1b1820", fg="white", bd=0, wrap="word",
                                font=("Consolas", 10), padx=15, pady=15)
            text_widget.pack(expand=True, fill="both")
            text_widget.insert("1.0", info_text)
            text_widget.config(state="disabled")
            
        def create_demo_browser_interface(self, parent):
            """Создает демо-интерфейс браузера"""
            # Панель навигации (демо)
            nav_frame = tk.Frame(parent, bg="#2b2036", height=50)
            nav_frame.pack(fill="x", padx=0, pady=0)
            nav_frame.pack_propagate(False)
            
            nav_buttons = tk.Frame(nav_frame, bg="#2b2036")
            nav_buttons.pack(side="left", padx=8, pady=8)
            
            # Демо-кнопки
            for btn_text in ["←", "→", "↻", "⌂"]:
                btn = tk.Button(nav_buttons, text=btn_text, bg="#3a2b45", fg=TEXT, bd=0,
                              font=("Segoe UI", 12), width=2, command=self.show_demo_message)
                btn.pack(side="left", padx=2)
            
            # Адресная строка (демо)
            url_frame = tk.Frame(nav_frame, bg="#2b2036")
            url_frame.pack(side="left", fill="x", expand=True, padx=10, pady=8)
            
            url_entry = tk.Entry(url_frame, bg="#1b1820", fg=TEXT, font=TEXT_FONT,
                               bd=1, relief="solid", insertbackground=TEXT)
            url_entry.pack(side="left", fill="x", expand=True)
            url_entry.insert(0, "https://www.google.com")
            url_entry.bind("<Return>", lambda e: self.show_demo_message())
            
            go_btn = tk.Button(url_frame, text="→", bg="#4d7fff", fg=TEXT, bd=0,
                             font=("Segoe UI", 12), width=2, command=self.show_demo_message)
            go_btn.pack(side="left", padx=5)
            
            # Контент демо-браузера
            content_frame = tk.Frame(parent, bg=WINDOW_BG)
            content_frame.pack(expand=True, fill="both", padx=12, pady=12)
            
            # Заголовок
            title_frame = tk.Frame(content_frame, bg=WINDOW_BG)
            title_frame.pack(fill="x", pady=(0, 20))
            
            tk.Label(title_frame, text="🌐 Flolower Browser (Демо-режим)", 
                    bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(anchor="w")
            
            tk.Label(title_frame, text="Для использования реального браузера установите Qt WebEngine",
                    bg=WINDOW_BG, fg="#ff6b6b", font=TEXT_FONT).pack(anchor="w", pady=(5, 0))
            
            # Быстрый доступ к сайтам (в системном браузере)
            quick_frame = tk.Frame(content_frame, bg=WINDOW_BG)
            quick_frame.pack(fill="x", pady=(0, 20))
            
            tk.Label(quick_frame, text="🚀 Открыть в системном браузере:",
                    bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")
            
            sites_frame = tk.Frame(quick_frame, bg=WINDOW_BG)
            sites_frame.pack(fill="x", pady=10)
            
            sites = [
                ("🔍 Google", "https://www.google.com"),
                ("📺 YouTube", "https://www.youtube.com"),
                ("💻 GitHub", "https://www.github.com"),
                ("📚 Wikipedia", "https://www.wikipedia.org")
            ]
            
            for name, url in sites:
                btn = tk.Button(sites_frame, text=name, bg="#2b2036", fg=TEXT, 
                              font=TEXT_FONT, bd=0, padx=12, pady=6,
                              command=lambda u=url: webbrowser.open(u))
                btn.pack(side="left", padx=4, pady=2)
            
            # Информация об установке
            info_frame = tk.Frame(content_frame, bg=WINDOW_BG)
            info_frame.pack(fill="both", expand=True)
            
            info_text = """
🌐 ДЕМО-РЕЖИМ БРАУЗЕРА

Для полноценного веб-серфинга в Flolower OS необходимо установить:

>>> pip install PyQt5 PyQtWebEngine <<<

После установки перезапустите Flolower OS.

✅ РЕАЛЬНЫЙ БРАУЗЕР БУДЕТ ВКЛЮЧАТЬ:
• Полноценный веб-серфинг через Qt WebEngine
• Поддержка всех современных веб-стандартов
• Быстрый движок Chromium
• Воспроизведение видео и аудио
• Поддержка JavaScript

💡 СЕЙЧАС ВЫ МОЖЕТЕ:
• Открывать сайты в вашем системном браузере
• Использовать кнопки выше для быстрого доступа
• Установить Qt для полноценной работы в Flolower OS

🔧 КОМАНДА ДЛЯ УСТАНОВКИ:
Откройте Терминал в Flolower OS и выполните:
pip install PyQt5 PyQtWebEngine
"""
            
            text_widget = tk.Text(info_frame, bg="#1b1820", fg="white", bd=0, wrap="word",
                                font=("Consolas", 10), padx=15, pady=15)
            text_widget.pack(expand=True, fill="both")
            text_widget.insert("1.0", info_text)
            text_widget.config(state="disabled")
            
        def launch_browser(self, url=None):
            """Запускает реальный браузер с Qt WebEngine"""
            if not url:
                url = self.url_var.get() if hasattr(self, 'url_var') else "https://www.google.com"
            
            def start_qt_browser():
                class RealBrowser(QMainWindow):
                    def __init__(self, url):
                        super().__init__()
                        self.setWindowTitle(f"Flolower Browser - {url}")
                        self.setGeometry(100, 100, 1200, 800)
                        
                        # Темная тема
                        self.setStyleSheet("""
                            QMainWindow {
                                background-color: #0f0b18;
                                color: white;
                            }
                            QToolBar {
                                background-color: #2b2036;
                                border: none;
                                spacing: 5px;
                                padding: 5px;
                            }
                            QLineEdit {
                                background-color: #1b1820;
                                color: white;
                                border: 1px solid #4a3654;
                                border-radius: 3px;
                                padding: 5px;
                                font-family: 'Segoe UI';
                            }
                            QPushButton {
                                background-color: #3a2b45;
                                color: white;
                                border: none;
                                border-radius: 3px;
                                padding: 5px 10px;
                                font-family: 'Segoe UI';
                            }
                            QPushButton:hover {
                                background-color: #4a3654;
                            }
                        """)
                        
                        self.browser = QWebEngineView()
                        self.browser.setUrl(QUrl(url))
                        
                        # Панель навигации
                        navbar = QToolBar()
                        self.addToolBar(navbar)
                        
                        # Кнопки навигации
                        back_btn = QPushButton("←")
                        back_btn.setFixedSize(30, 30)
                        back_btn.clicked.connect(self.browser.back)
                        navbar.addWidget(back_btn)
                        
                        forward_btn = QPushButton("→")
                        forward_btn.setFixedSize(30, 30)
                        forward_btn.clicked.connect(self.browser.forward)
                        navbar.addWidget(forward_btn)
                        
                        reload_btn = QPushButton("↻")
                        reload_btn.setFixedSize(30, 30)
                        reload_btn.clicked.connect(self.browser.reload)
                        navbar.addWidget(reload_btn)
                        
                        home_btn = QPushButton("⌂")
                        home_btn.setFixedSize(30, 30)
                        home_btn.clicked.connect(self.navigate_home)
                        navbar.addWidget(home_btn)
                        
                        # Адресная строка
                        self.url_bar = QLineEdit()
                        self.url_bar.setText(url)
                        self.url_bar.returnPressed.connect(self.navigate_to_url)
                        navbar.addWidget(self.url_bar)
                        
                        # Кнопка перехода
                        go_btn = QPushButton("Перейти")
                        go_btn.setFixedSize(80, 30)
                        go_btn.clicked.connect(self.navigate_to_url)
                        navbar.addWidget(go_btn)
                        
                        # Обновление URL и заголовка
                        self.browser.urlChanged.connect(self.update_url_bar)
                        self.browser.titleChanged.connect(self.update_title)
                        
                        self.setCentralWidget(self.browser)
                        
                    def navigate_home(self):
                        self.browser.setUrl(QUrl("https://www.google.com"))
                        
                    def navigate_to_url(self):
                        url = self.url_bar.text().strip()
                        if not url:
                            return
                        if not url.startswith(('http://', 'https://')):
                            url = 'https://' + url
                        self.browser.setUrl(QUrl(url))
                        
                    def update_url_bar(self, q):
                        self.url_bar.setText(q.toString())
                        
                    def update_title(self, title):
                        self.setWindowTitle(f"{title} - Flolower Browser")
                
                app = QApplication([])
                browser = RealBrowser(url)
                browser.show()
                app.exec_()
            
            # Запуск в отдельном потоке
            thread = threading.Thread(target=start_qt_browser)
            thread.daemon = True
            thread.start()
            
        def show_demo_message(self):
            """Показывает сообщение в демо-режиме"""
            message = "Для использования реального браузера установите: pip install PyQt5 PyQtWebEngine"
            print(message)
    
    # Создаем и возвращаем экземпляр браузера
    browser = BrowserInterface(parent)
    return browser

# ------------------ Terminal ------------------
def build_terminal(parent):
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(expand=True, fill="both", padx=12, pady=12)

    output = tk.Text(frame, bg="#000000", fg="#00ff00", insertbackground="#00ff00", bd=0, font=("Consolas", 11))
    output.pack(expand=True, fill="both", pady=(0,8))
    entry = tk.Entry(frame, bg="#111111", fg="#00ff00", insertbackground="#00ff00", bd=0, font=("Consolas", 11))
    entry.pack(fill="x", pady=(0,4))

    def write(text=""):
        output.insert("end", text + "\n")
        output.see("end")

    write("Flolower OS Terminal v1.0 (type 'help' for commands)")

    def process_command(event=None):
        cmd = entry.get().strip()
        entry.delete(0, "end")
        if not cmd:
            return
        write(f"Flolover OS> {cmd}")

        if cmd == "help":
            write("Available commands: help, exit, ls, quit, about, joke, roll, flip, time, create, delete, write, mkdir, echo, python, cd, pwd, clear")
            write("Python commands: python <code> - execute Python code")
            return

        if cmd == "ls":
            list_dir = os.listdir(".")
            write(str(list_dir))
            return

        elif cmd == "clear":
            output.delete("1.0", "end")
            return

        if cmd == "time":
            now = datetime.datetime.now()
            write(now.strftime("%H:%M:%S.%f")[:-3])
            return

        if cmd in ("exit", "quit"):
            try:
                parent.master.destroy()
            except Exception:
                pass
            return

        if cmd == "joke":
            if pyjokes is None:
                write("pyjokes not installed. Install with: pip install pyjokes")
            else:
                try:
                    write(pyjokes.get_joke())
                except Exception as e:
                    write("Error getting joke.")
            return

        if cmd == "roll":
            write("roll: enter maximum integer (e.g. 6)")
            entry.unbind("<Return>")
            def wait_roll(event=None):
                val = entry.get().strip()
                entry.delete(0, "end")
                try:
                    n = int(val)
                    if n < 1:
                        write("Must be >= 1")
                    else:
                        r = random.randint(1, n)
                        write(f"🎲 {r}")
                except Exception:
                    write("Invalid number.")
                entry.bind("<Return>", process_command)
            entry.bind("<Return>", wait_roll)
            return

        if cmd == "flip":
            write("Enter text to flip:")
            entry.unbind("<Return>")
            def wait_flip(event=None):
                txt = entry.get()
                entry.delete(0, "end")
                if txt is None: txt = ""
                flipped = txt[::-1]
                write(f"🔄 {flipped}")
                entry.bind("<Return>", process_command)
            entry.bind("<Return>", wait_flip)
            return

        elif cmd.startswith("create "):
            filename = cmd[7:].strip()
            try:
                with open(filename, 'w') as file:
                    file.write("")
                write(f"File '{filename}' created successfully.")
            except Exception as e:
                write(f"Error creating file: {e}")

        elif cmd.startswith("delete "):
            filename = cmd[7:].strip()
            try:
                os.remove(filename)
                write(f"File '{filename}' deleted successfully.")
            except FileNotFoundError:
                write("File not found.")
            except Exception as e:
                write(f"Error deleting file: {e}")

        elif cmd == "pwd":
            write(os.getcwd())
            return
            
        elif cmd.startswith("cd "):
            path = cmd[3:].strip()
            try:
                os.chdir(path)
                write(f"Changed directory to: {os.getcwd()}")
            except FileNotFoundError:
                write("Directory not found.")
            except NotADirectoryError:
                write("Not a directory.")
            except PermissionError:
                write("Permission denied.")
            except Exception as e:
                write(f"Error: {e}")
            return
            
        elif cmd.startswith("write "):
            filename = cmd[6:].strip()
            try:
                write(f"Enter content for '{filename}':")
                entry.unbind("<Return>")
                def wait_write_content(event=None):
                    content = entry.get()
                    entry.delete(0, "end")
                    try:
                        with open(filename, 'w', encoding='utf-8') as file:
                            file.write(content)
                        write(f"Content written to '{filename}' successfully.")
                    except Exception as e:
                        write(f"Error writing to file: {e}")
                    entry.bind("<Return>", process_command)
                entry.bind("<Return>", wait_write_content)
            except Exception as e:
                write(f"Error: {e}")

        elif cmd.startswith("mkdir "):
            dir_name = cmd[6:].strip()
            try:
                os.mkdir(dir_name)
                write(f"Directory '{dir_name}' created successfully.")
            except Exception as e:
                write(f"Error creating directory: {e}")

        elif cmd.startswith("echo "):
            message = cmd[5:].strip()
            write(message)

        elif cmd.startswith("python "):
            python_code = cmd[7:].strip()
            try:
                try:
                    result = eval(python_code)
                    if result is not None:
                        write(str(result))
                except:
                    exec(python_code)
                write("Python code executed successfully")
                
            except Exception as e:
                write(f"Error executing Python code: {e}")
                
        elif cmd == "about":
            write("Flolower OS v1.0 (Beta)")
            write("A custom operating system interface built with Python and Tkinter")
            return
            
        else:
            write("Command not found!!!")

    entry.bind("<Return>", process_command)
    entry.focus_set()

# ------------------ Other app builders ------------------
def build_notes(parent):
    frame=tk.Frame(parent,bg=WINDOW_BG)
    frame.pack(expand=True,fill="both",padx=12,pady=12)
    text_widget=tk.Text(frame,bg="#1b1820",fg="white",bd=0,wrap="word")
    text_widget.pack(expand=True,fill="both",padx=6,pady=(6,10))
    try:
        if os.path.exists(NOTES_SAVE_PATH):
            with open(NOTES_SAVE_PATH,"r",encoding="utf-8") as rf: text_widget.insert("1.0",rf.read())
    except: pass
    def save_notes():
        entered_text=text_widget.get("1.0","end").rstrip("\n")
        try:
            os.makedirs(os.path.dirname(NOTES_SAVE_PATH),exist_ok=True)
            with open(NOTES_SAVE_PATH,"w",encoding="utf-8") as wf: wf.write(entered_text)
        except: pass
    btn_save=tk.Button(frame,text="Зберегти",command=save_notes,bg="#334155",fg="white",bd=0,padx=10,pady=6)
    btn_save.pack(side="bottom",fill="x",padx=6)

def build_calendar(parent):
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(expand=True, fill="both", padx=12, pady=12)

    now = datetime.datetime.now()
    year, month = now.year, now.month
    selected_day = [None]

    header = tk.Label(frame, text="", bg=WINDOW_BG, fg="white", font=TITLE_FONT)
    header.pack(pady=6)

    days_frame = tk.Frame(frame, bg=WINDOW_BG)
    days_frame.pack()

    buttons_frame = tk.Frame(frame, bg=WINDOW_BG)
    buttons_frame.pack(pady=6)

    def draw_calendar():
        header.config(text=f"{calendar.month_name[month]} {year}")
        for w in days_frame.winfo_children(): w.destroy()
        days=["Mo","Tu","We","Th","Fr","Sa","Su"]
        for i,d in enumerate(days): tk.Label(days_frame,text=d,bg=WINDOW_BG,fg="white",font=TEXT_FONT,width=4).grid(row=0,column=i)
        month_days = calendar.monthcalendar(year,month)
        for r,week in enumerate(month_days,start=1):
            for c,day in enumerate(week):
                if day!=0:
                    bg_color="#2b2036"
                    if day==now.day and month==now.month and year==now.year: bg_color="#4d7fff"
                    if selected_day[0]==day: bg_color="#00aaff"
                    tk.Button(days_frame,text=str(day),width=4,bg=bg_color,fg="white",relief="flat",command=lambda d=day:selected_day.__setitem__(0,d) or draw_calendar()).grid(row=r,column=c,padx=2,pady=2)

    tk.Button(buttons_frame,text="←",width=4,bg=MENU_ITEM,fg="white",relief="flat",command=lambda:prev_month()).pack(side="left",padx=6)
    tk.Button(buttons_frame,text="→",width=4,bg=MENU_ITEM,fg="white",relief="flat",command=lambda:next_month()).pack(side="right",padx=6)

    def prev_month():
        nonlocal month, year
        month -= 1
        if month < 1:
            month, year = 12, year - 1
        selected_day[0] = None
        draw_calendar()

    def next_month():
        nonlocal month, year
        month += 1
        if month > 12:
            month, year = 1, year + 1
        selected_day[0] = None
        draw_calendar()

    draw_calendar()

# ------------------ Open app window ------------------
def open_app_window(key,title):
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.configure(bg=WINDOW_BG)
    target_w, target_h = int(SW*0.56), int(SH*0.62)
    cx, cy = (SW-target_w)//2, (SH-target_h)//2
    win.geometry(f"{target_w}x{target_h}+{cx}+{cy}")

    title_bar = tk.Frame(win, bg=TITLE_BG, height=36)
    title_bar.pack(fill="x")
    tk.Label(title_bar, text=title, bg=TITLE_BG, fg=TEXT, font=TITLE_FONT).pack(side="left", padx=8)
    ctrls = tk.Frame(title_bar, bg=TITLE_BG)
    ctrls.pack(side="right", padx=6)

    def close_win():
        try:
            if win in task_buttons:
                btn = task_buttons[win]
                if win in pinned_windows:
                    del pinned_windows[win]
                btn.destroy()
                del task_buttons[win]
        except Exception:
        pass
        try:
            win.destroy()
        except:
            pass

    def minimize_win():
        try:
            win.withdraw()
        except:
            pass

    win.is_max = False
    win.normal_geom = None
    def toggle_max():
        try:
            if not win.is_max:
                g = win.geometry().split("+"); wh = g[0].split("x")
                win.normal_geom = (int(g[1]), int(g[2]), int(wh[0]), int(wh[1]))
                win.is_max = True
                win.geometry(f"{SW}x{SH}+0+0")
            else:
                win.is_max = False
                nx, ny, nw, nh = win.normal_geom
                win.geometry(f"{nw}x{nh}+{nx}+{ny}")
        except:
            pass

    b_min = tk.Button(ctrls, text="🗕", bg=TITLE_BG, fg=TEXT, bd=0, command=minimize_win)
    b_max = tk.Button(ctrls, text="🗖", bg=TITLE_BG, fg=TEXT, bd=0, command=toggle_max)
    b_close = tk.Button(ctrls, text="✕", bg=TITLE_BG, fg=TEXT, bd=0, command=close_win)
    b_min.pack(side="left", padx=4); b_max.pack(side="left", padx=4); b_close.pack(side="left", padx=4)

    content = tk.Frame(win, bg=WINDOW_BG)
    content.pack(expand=True, fill="both")

    # Содержимое приложения
    if key == "calculator":
        expr = tk.StringVar()
        e = tk.Entry(content, textvariable=expr, font=("Consolas",18), justify="right",
                     bg="#1b1820", fg="white", bd=0, insertbackground="white")
        e.pack(fill="x", padx=12, pady=12, ipady=6)
        grid = tk.Frame(content, bg=WINDOW_BG); grid.pack(expand=True, fill="both", padx=12, pady=(0,12))
        buttons = ["7","8","9","/","4","5","6","*","1","2","3","-","0",".","=","+"]
        def press(ch):
            if ch == "=":
                try:
                    expr.set(str(eval(expr.get())))
                except:
                    expr.set("Err")
            else:
                expr.set(expr.get()+ch)
        for i,ch in enumerate(buttons):
            b = tk.Button(grid, text=ch, command=lambda c=ch:press(c), bg="#2b2430", fg="white", bd=0, font=("Segoe UI",14))
            b.grid(row=i//4, column=i%4, sticky="nsew", padx=6, pady=6)
        for i in range(4): grid.columnconfigure(i, weight=1); grid.rowconfigure(i, weight=1)
    elif key == "notes":
        build_notes(content)
    elif key == "browser":
        build_browser(content)
    elif key == "calendar":
        build_calendar(content)
    elif key == "terminal":
        build_terminal(content)
    else:
        tk.Label(content, text=f"{title} — демo", bg=WINDOW_BG, fg=TEXT).pack(padx=12, pady=12)

    def start_move(e):
        try:
            win._drag_x_root, win._drag_y_root = e.x_root, e.y_root
            geo = win.geometry().split("+"); win._drag_win_x, win._drag_win_y = int(geo[1]), int(geo[2])
        except:
            pass
    def do_move(e):
        try:
            dx, dy = e.x_root - win._drag_x_root, e.y_root - win._drag_y_root
            nx, ny = win._drag_win_x + dx, win._drag_win_y + dy
            geo = win.geometry().split("+")[0]
            win.geometry(f"{geo}+{nx}+{ny}")
        except:
            pass
    title_bar.bind("<Button-1>", start_move)
    title_bar.bind("<B1-Motion>", do_move)

    task_btn = create_task_button(win, title)

    open_windows.append({"win": win, "key": key, "title": title, "id": id(win)})

    def on_closing():
        close_win()
    
    win.protocol("WM_DELETE_WINDOW", on_closing)

# ------------------ Desktop icons ------------------
desktop_icons = []
def save_icon_positions():
    data = {}
    for i, (f, emoji, title, key) in enumerate(desktop_icons):
        try:
            data[str(i)] = {"x": f.winfo_x(), "y": f.winfo_y(), "key": key}
        except:
            data[str(i)] = {"x": 64, "y": 84 + i*110, "key": key}
    try:
        with open(ICON_POS_FILE, "w", encoding="utf-8") as fp: json.dump(data, fp, ensure_ascii=False, indent=2)
    except:
        pass

def create_desktop_icon(x, y, emoji, title, key):
    f = tk.Frame(desktop, bg=BG)
    f.place(x=x, y=y)
    ico = tk.Label(f, text=emoji, font=ICON_FONT, bg=BG, fg=TEXT); ico.pack()
    lbl = tk.Label(f, text=title, bg=BG, fg=TEXT, font=TEXT_FONT); lbl.pack(pady=(6,0))

    def on_open(e=None): open_app_window(key, title)
    for w in (f, ico, lbl):
        w.bind("<Double-Button-1>", on_open)

    def start_drag(e):
        f._drag_offset_x = e.x_root - f.winfo_x()
        f._drag_offset_y = e.x_root - f.winfo_y() if False else e.y_root - f.winfo_y()

    def do_drag(e):
        try:
            nx = max(0, min(SW-60, e.x_root - f._drag_offset_x))
            ny = max(0, min(SH-120, e.y_root - f._drag_offset_y))
            f.place(x=nx, y=ny)
        except:
            pass

    def end_drag(e):
        save_icon_positions()

    for w in (f, ico, lbl):
        w.bind("<Button-1>", start_drag)
        w.bind("<B1-Motion>", do_drag)
        w.bind("<ButtonRelease-1>", end_drag)

    desktop_icons.append((f, emoji, title, key))

for i, (emoji, title, key) in enumerate(DESKTOP_ICONS):
    pos = saved_positions.get(str(i))
    if pos and isinstance(pos, dict) and "x" in pos and "y" in pos:
        create_desktop_icon(pos["x"], pos["y"], emoji, title, key)
    else:
        create_desktop_icon(64, 84 + i*110, emoji, title, key)

# ------------------ Mainloop ------------------
start_menu.place(y=SH+20)
canvas.tag_lower("all")
root.protocol("WM_DELETE_WINDOW", lambda: (save_icon_positions(), root.destroy()))
root.mainloop()
