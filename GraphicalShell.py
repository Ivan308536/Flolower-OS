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
import shutil
import tkinter.filedialog
import tkinter.messagebox
from pathlib import Path
import math

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
    ("📁", "Файлы", "files"),
    ("🎮", "Click on smile!", "smile_game"),
    ("🎨", "Рисовалка", "paint"),
    ("🎵", "Музыка", "music"),
    ("📊", "Погода", "weather"),
    ("🧮", "Конвертер", "converter"),
    ("⏰", "Таймер", "timer"),
    ("📷", "Камера", "camera"),
    ("🔍", "Поиск", "search"),
    ("📝", "Текст редактор", "text_editor"),
    ("🎲", "Игры", "games"),
    ("🖼️", "Галерея", "gallery"),
    ("⚙️", "Настройки", "settings"),
    ("📚", "Книги", "books"),
    ("🗂️", "Менеджер задач", "task_manager"),
]

DESKTOP_ICONS = [
    ("🔢", "Калькулятор", "calculator"),
    ("🗒️", "Заметки", "notes"),
    ("📅", "Календарь", "calendar"),
    ("💻", "Терминал", "terminal"),
    ("🗑️", "Корзина", "trash"),
    ("📁", "Файлы", "files"),
    ("🎮", "Click on smile!", "smile_game"),
    ("🎨", "Рисовалка", "paint"),
    ("🎵", "Музыка", "music"),
    ("📊", "Погода", "weather"),
]

ICON_FONT = ("Segoe UI Emoji", 34)
TITLE_FONT = ("Segoe UI", 10, "bold")
TEXT_FONT = ("Segoe UI", 10)
ICON_POS_FILE = "icons_pos_v10.json"
NOTES_SAVE_PATH = r"D:\замітки.txt"
PINNED_APPS_FILE = "pinned_apps_v10.json"
WALLPAPER_PATH = "Flolower fone.jpg"
TRASH_DIR = "FlolowerTrash"  # Папка для корзины

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

# ------------------ Root ------------------
root = tk.Tk()
root.title("Flolower OS v1.0(beta)")
root.attributes("-fullscreen", True)
root.configure(bg=BG)
SW, SH = root.winfo_screenwidth(), root.winfo_screenheight()

# ------------------ Canvas with wallpaper ------------------
canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
canvas.place(relwidth=1, relheight=1)

# Флаг для отслеживания, какое изображение используется
use_abstract_background = True

print(f"Попытка загрузить фоновое изображение: {WALLPAPER_PATH}")
print(f"Файл существует: {os.path.exists(WALLPAPER_PATH)}")
print(f"Текущая директория: {os.getcwd()}")

try:
    if os.path.exists(WALLPAPER_PATH):
        wallpaper_img = Image.open(WALLPAPER_PATH)
        # Масштабируем изображение под размер экрана
        wallpaper_img = wallpaper_img.resize((SW, SH), Image.Resampling.LANCZOS)
        wallpaper_photo = ImageTk.PhotoImage(wallpaper_img)
        
        # Создаем фоновое изображение на canvas
        canvas.create_image(0, 0, anchor="nw", image=wallpaper_photo)
        canvas.image = wallpaper_photo  # Сохраняем ссылку на изображение
        
        print(f"Фоновое изображение '{WALLPAPER_PATH}' успешно загружено")
        use_abstract_background = False
    else:
        print(f"Файл '{WALLPAPER_PATH}' не найден")
        use_abstract_background = True
    
except Exception as e:
    print(f"Ошибка загрузки фонового изображения: {e}")
    print("Используется абстрактный фон с кругами")
    use_abstract_background = True

# Создаем абстрактные круги только если не удалось загрузить изображение
if use_abstract_background:
    print("Создание абстрактного фона с кругами...")
    
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
    print("Абстрактный фон с кругами создан успешно")

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

# Кнопка выключения
shutdown_btn = tk.Button(taskbar, text="⏻", bg=TASKBAR_BG, fg="#ff4444", 
                        font=("Segoe UI Emoji", 20), bd=0, padx=12, pady=4,
                        command=lambda: shutdown_system())
shutdown_btn.pack(side="right", padx=8)

time_lbl = tk.Label(taskbar, text=time.strftime("%H:%M"), bg=TASKBAR_BG, fg=TEXT, font=TEXT_FONT)
time_lbl.pack(side="right", padx=12)
def tick_time(): time_lbl.config(text=time.strftime("%H:%M")); root.after(1000,tick_time)
tick_time()
task_buttons={}

# ------------------ Shutdown function ------------------
def shutdown_system():
    """Функция выключения системы"""
    def confirm_shutdown():
        # Создаем окно подтверждения
        confirm_win = tk.Toplevel(root)
        confirm_win.overrideredirect(True)
        confirm_win.configure(bg=WINDOW_BG)
        confirm_win.attributes("-topmost", True)
        
        # Центрируем окно
        win_w, win_h = 400, 200
        x = (SW - win_w) // 2
        y = (SH - win_h) // 2
        confirm_win.geometry(f"{win_w}x{win_h}+{x}+{y}")
        
        # Заголовок
        title_bar = tk.Frame(confirm_win, bg=TITLE_BG, height=36)
        title_bar.pack(fill="x")
        tk.Label(title_bar, text="Выключение системы", bg=TITLE_BG, fg=TEXT, font=TITLE_FONT).pack(side="left", padx=8)
        
        # Контент
        content = tk.Frame(confirm_win, bg=WINDOW_BG)
        content.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Сообщение
        msg = tk.Label(content, text="Вы уверены, что хотите выключить систему?", 
                      bg=WINDOW_BG, fg=TEXT, font=TEXT_FONT)
        msg.pack(pady=10)
        
        # Кнопки
        btn_frame = tk.Frame(content, bg=WINDOW_BG)
        btn_frame.pack(side="bottom", pady=20)
        
        def do_shutdown():
            # Анимация выключения
            shutdown_animation()
            # Закрываем все окна и выходим
            root.after(2000, lambda: (save_icon_positions(), root.destroy()))
        
        def cancel_shutdown():
            confirm_win.destroy()
        
        tk.Button(btn_frame, text="Выключить", bg="#ff4444", fg="white", 
                 font=TEXT_FONT, bd=0, padx=20, pady=8,
                 command=do_shutdown).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Отмена", bg=MENU_ITEM, fg=TEXT,
                 font=TEXT_FONT, bd=0, padx=20, pady=8,
                 command=cancel_shutdown).pack(side="right", padx=10)
        
        # Закрытие по ESC
        confirm_win.bind("<Escape>", lambda e: cancel_shutdown())
    
    confirm_shutdown()

def shutdown_animation():
    """Анимация выключения системы"""
    # Создаем полноэкранное затемнение
    overlay = tk.Canvas(root, bg="black", highlightthickness=0)
    overlay.place(relwidth=1, relheight=1)
    
    # Добавляем сообщение
    message = overlay.create_text(SW//2, SH//2, text="Система выключается...", 
                                 fill="white", font=("Segoe UI", 24), anchor="center")
    
    # Анимация затемнения
    def fade_out(alpha=0):
        if alpha < 1.0:
            overlay.config(bg=f"#000000")
            root.after(50, lambda: fade_out(alpha + 0.05))
        else:
            overlay.config(bg="black")
    
    fade_out()

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

# Увеличиваем высоту apps_frame чтобы вместить все приложения
apps_frame = tk.Frame(start_menu,bg=MENU_BG)
apps_frame.place(x=16,y=72,width=MENU_W-32,height=MENU_H-88)

# Создаем Canvas и Scrollbar для прокрутки
apps_canvas = tk.Canvas(apps_frame, bg=MENU_BG, highlightthickness=0)
scrollbar = tk.Scrollbar(apps_frame, orient="vertical", command=apps_canvas.yview)
scrollable_frame = tk.Frame(apps_canvas, bg=MENU_BG)

scrollable_frame.bind(
    "<Configure>",
    lambda e: apps_canvas.configure(scrollregion=apps_canvas.bbox("all"))
)

apps_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
apps_canvas.configure(yscrollcommand=scrollbar.set)

apps_canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Привязываем колесико мыши к прокрутке
def on_mousewheel(event):
    apps_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

apps_canvas.bind("<MouseWheel>", on_mousewheel)

app_widgets=[]

def on_start_app(app_key, app_title):
    toggle_menu(False)
    open_app_window(app_key, app_title)

# Создаем приложения в scrollable_frame вместо apps_frame
for emoji,title,key in APP_LIST:
    row=tk.Frame(scrollable_frame,bg=MENU_ITEM,height=44)
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
    # Обновляем все кнопки закрепления
    for widget in scrollable_frame.winfo_children():
        for child in widget.winfo_children():
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Button) and grandchild['text'] in ("📌", "📍"):
                        # Находим соответствующий ключ приложения
                        for app_emoji, app_title, app_key in APP_LIST:
                            if app_key == key:
                                if key in pinned_apps:
                                    grandchild.config(text="📌")
                                else:
                                    grandchild.config(text="📍")
                                break

def refresh_app_list(*_):
    q=search_var.get().lower().strip()
    for w,title in app_widgets:
        if not q or q in title.lower(): 
            w.pack(fill="x", pady=6)
        else:
            w.pack_forget()
            
    # Обновляем scrollregion после фильтрации
    apps_canvas.configure(scrollregion=apps_canvas.bbox("all"))

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

# ------------------ Trash System ------------------
def ensure_trash_dir():
    """Создает папку для корзины если её нет"""
    if not os.path.exists(TRASH_DIR):
        os.makedirs(TRASH_DIR, exist_ok=True)

def get_trash_contents():
    """Возвращает содержимое корзины"""
    ensure_trash_dir()
    contents = []
    try:
        for item in os.listdir(TRASH_DIR):
            item_path = os.path.join(TRASH_DIR, item)
            stat = os.stat(item_path)
            contents.append({
                'name': item,
                'path': item_path,
                'size': stat.st_size,
                'deleted_time': stat.st_mtime,
                'is_dir': os.path.isdir(item_path)
            })
    except Exception as e:
        print(f"Ошибка чтения корзины: {e}")
    return contents

def move_to_trash(file_path):
    """Перемещает файл/папку в корзину"""
    try:
        ensure_trash_dir()
        if not os.path.exists(file_path):
            return False, "Файл не существует"
        
        file_name = os.path.basename(file_path)
        trash_path = os.path.join(TRASH_DIR, file_name)
        
        # Если файл с таким именем уже есть в корзине, добавляем суффикс
        counter = 1
        original_trash_path = trash_path
        while os.path.exists(trash_path):
            name, ext = os.path.splitext(file_name)
            trash_path = os.path.join(TRASH_DIR, f"{name}_{counter}{ext}")
            counter += 1
        
        shutil.move(file_path, trash_path)
        return True, "Успешно перемещено в корзину"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

def restore_from_trash(trash_item_name, restore_path=None):
    """Восстанавливает файл из корзины"""
    try:
        trash_path = os.path.join(TRASH_DIR, trash_item_name)
        if not os.path.exists(trash_path):
            return False, "Файл не найден в корзине"
        
        if restore_path is None:
            restore_path = os.path.join(os.getcwd(), trash_item_name)
        
        # Если файл уже существует в месте восстановления
        counter = 1
        original_restore_path = restore_path
        while os.path.exists(restore_path):
            name, ext = os.path.splitext(trash_item_name)
            restore_path = os.path.join(os.path.dirname(original_restore_path), f"{name}_restored_{counter}{ext}")
            counter += 1
        
        shutil.move(trash_path, restore_path)
        return True, "Файл восстановлен"
    except Exception as e:
        return False, f"Ошибка восстановления: {str(e)}"

def empty_trash():
    """Очищает корзину полностью"""
    try:
        ensure_trash_dir()
        for item in os.listdir(TRASH_DIR):
            item_path = os.path.join(TRASH_DIR, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        return True, "Корзина очищена"
    except Exception as e:
        return False, f"Ошибка очистки: {str(e)}"

def delete_permanently(trash_item_name):
    """Удаляет файл из корзины навсегда"""
    try:
        trash_path = os.path.join(TRASH_DIR, trash_item_name)
        if os.path.isdir(trash_path):
            shutil.rmtree(trash_path)
        else:
            os.remove(trash_path)
        return True, "Файл удален навсегда"
    except Exception as e:
        return False, f"Ошибка удаления: {str(e)}"

# ------------------ Game Class ------------------
class SmileGame:
    def __init__(self, parent):
        self.parent = parent
        self.points = 0
        self.jumping = False
        self.jump_start_time = 0
        self.jump_offset = 0
        self.game_active = True
        
        # Константы игры
        self.WIDTH, self.HEIGHT = 600, 500
        self.BLOCK_SIZE = 120
        self.JUMP_DURATION = 0.3
        self.JUMP_HEIGHT = 25
        
        # Создаем фрейм для игры
        self.frame = tk.Frame(parent, bg=WINDOW_BG)
        self.frame.pack(expand=True, fill="both", padx=12, pady=12)
        
        # Канва для игры
        self.canvas = tk.Canvas(self.frame, width=self.WIDTH, height=self.HEIGHT, 
                               bg=WINDOW_BG, highlightthickness=0)
        self.canvas.pack(pady=20)
        
        # Заголовок
        title_label = tk.Label(self.frame, text="🎮 Click on smile!", 
                              bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=10)
        
        # Создаем смайл (используем эмодзи если нет изображения)
        try:
            # Пробуем загрузить изображение смайла
            if os.path.exists("smile.png"):
                img = Image.open("smile.png").resize((self.BLOCK_SIZE, self.BLOCK_SIZE))
                self.smile_image = ImageTk.PhotoImage(img)
                self.smile = self.canvas.create_image(self.WIDTH//2, self.HEIGHT//2, 
                                                    image=self.smile_image)
            else:
                # Создаем смайл с помощью эмодзи
                self.smile = self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2, 
                                                   text="😊", font=("Segoe UI Emoji", 80))
        except Exception as e:
            print(f"Ошибка загрузки изображения смайла: {e}")
            # Создаем смайл с помощью эмодзи
            self.smile = self.canvas.create_text(self.WIDTH//2, self.HEIGHT//2, 
                                               text="😊", font=("Segoe UI Emoji", 80))
        
        # Текст очков
        self.score_text = self.canvas.create_text(self.WIDTH//2, 40, 
                                                text="Очки: 0", 
                                                font=("Segoe UI", 24), 
                                                fill=TEXT)
        
        # Инструкция
        instruction = self.canvas.create_text(self.WIDTH//2, self.HEIGHT - 30, 
                                            text="Кликай на смайл чтобы зарабатывать очки!", 
                                            font=("Segoe UI", 12), 
                                            fill=TEXT)
        
        # Кнопка сброса
        reset_btn = tk.Button(self.frame, text="🔄 Начать заново", 
                             bg=MENU_ITEM, fg=TEXT, font=TEXT_FONT,
                             command=self.reset_game)
        reset_btn.pack(pady=10)
        
        # Обработка кликов
        self.canvas.bind("<Button-1>", self.click)
        
        # Запуск обновления игры
        self.update()

    def click(self, event):
        if not self.game_active:
            return
            
        # Координаты смайла
        x1 = self.WIDTH//2 - self.BLOCK_SIZE//2
        y1 = self.HEIGHT//2 - self.BLOCK_SIZE//2 - self.jump_offset
        x2 = x1 + self.BLOCK_SIZE
        y2 = y1 + self.BLOCK_SIZE

        # Проверка попадания по смайлу
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            self.points += 1
            self.jumping = True
            self.jump_start_time = time.time()
            
            # Меняем цвет смайла при клике
            self.canvas.itemconfig(self.score_text, fill="#4dff4d")  # Зеленый цвет

    def update(self):
        # Анимация прыжка
        if self.jumping:
            elapsed = time.time() - self.jump_start_time
            if elapsed < self.JUMP_DURATION:
                # Параболическая траектория прыжка
                progress = elapsed / self.JUMP_DURATION
                self.jump_offset = self.JUMP_HEIGHT * (1 - (2 * progress - 1) ** 2)
            else:
                self.jumping = False
                self.jump_offset = 0
                # Возвращаем обычный цвет текста
                self.canvas.itemconfig(self.score_text, fill=TEXT)

        # Перемещение смайла
        if hasattr(self, 'smile_image'):
            # Если используем изображение
            self.canvas.coords(self.smile, self.WIDTH//2, self.HEIGHT//2 - self.jump_offset)
        else:
            # Если используем текст (эмодзи)
            self.canvas.coords(self.smile, self.WIDTH//2, self.HEIGHT//2 - self.jump_offset)

        # Обновление счёта
        self.canvas.itemconfig(self.score_text, text=f"Очки: {self.points}")
        
        # Увеличиваем сложность при достижении определенного количества очков
        if self.points >= 20:
            self.JUMP_DURATION = 0.2
            self.JUMP_HEIGHT = 35
        elif self.points >= 10:
            self.JUMP_DURATION = 0.25
            self.JUMP_HEIGHT = 30

        # Следующий кадр
        if self.game_active:
            self.parent.after(30, self.update)

    def reset_game(self):
        """Сброс игры"""
        self.points = 0
        self.jumping = False
        self.jump_offset = 0
        self.JUMP_DURATION = 0.3
        self.JUMP_HEIGHT = 25
        self.game_active = True
        self.canvas.itemconfig(self.score_text, fill=TEXT)
        self.update()

def build_smile_game(parent):
    """Создает экземпляр игры в окне"""
    game = SmileGame(parent)
    return game

# ------------------ New Apps Classes ------------------

class PaintApp:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.parent, bg=WINDOW_BG)
        main_frame.pack(expand=True, fill="both", padx=12, pady=12)
        
        # Title
        title_label = tk.Label(main_frame, text="🎨 Рисовалка", 
                              bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=10)
        
        # Toolbar
        toolbar = tk.Frame(main_frame, bg=MENU_ITEM)
        toolbar.pack(fill="x", pady=10)
        
        # Colors
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", 
                 "#000000", "#FFFFFF", "#FFA500", "#800080"]
        
        self.current_color = tk.StringVar(value="#FF0000")
        
        for color in colors:
            btn = tk.Radiobutton(toolbar, bg=color, variable=self.current_color, 
                               value=color, width=2, height=1, indicatoron=0)
            btn.pack(side="left", padx=2)
        
        # Brush size
        size_frame = tk.Frame(toolbar, bg=MENU_ITEM)
        size_frame.pack(side="right", padx=10)
        
        tk.Label(size_frame, text="Размер:", bg=MENU_ITEM, fg=TEXT).pack(side="left")
        self.brush_size = tk.Scale(size_frame, from_=1, to=20, orient="horizontal",
                                 bg=MENU_ITEM, fg=TEXT, highlightbackground=MENU_ITEM)
        self.brush_size.set(5)
        self.brush_size.pack(side="left", padx=5)
        
        # Clear button
        clear_btn = tk.Button(toolbar, text="Очистить", bg="#ff4444", fg="white",
                            command=self.clear_canvas)
        clear_btn.pack(side="right", padx=10)
        
        # Canvas
        self.canvas = tk.Canvas(main_frame, bg="white", width=600, height=400)
        self.canvas.pack(expand=True, fill="both", pady=10)
        
        # Bind events
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<Button-1>", self.paint)
        
        self.last_x = None
        self.last_y = None
        
    def paint(self, event):
        x, y = event.x, event.y
        if self.last_x is not None and self.last_y is not None:
            self.canvas.create_line(self.last_x, self.last_y, x, y,
                                  width=self.brush_size.get(),
                                  fill=self.current_color.get(),
                                  capstyle=tk.ROUND, smooth=tk.TRUE)
        self.last_x = x
        self.last_y = y
        
    def clear_canvas(self):
        self.canvas.delete("all")
        self.last_x = None
        self.last_y = None

class MusicPlayer:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.playlist = []
        self.current_track = 0
        self.playing = False
        
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg=WINDOW_BG)
        main_frame.pack(expand=True, fill="both", padx=12, pady=12)
        
        # Title
        title_label = tk.Label(main_frame, text="🎵 Музыкальный плеер", 
                              bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=10)
        
        # Track info
        self.track_label = tk.Label(main_frame, text="Выберите трек", 
                                   bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 12))
        self.track_label.pack(pady=5)
        
        # Progress
        self.progress = tk.Scale(main_frame, from_=0, to=100, orient="horizontal",
                               bg=WINDOW_BG, fg=TEXT, highlightbackground=WINDOW_BG)
        self.progress.pack(fill="x", padx=20, pady=10)
        
        # Controls
        controls_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        controls_frame.pack(pady=20)
        
        self.play_btn = tk.Button(controls_frame, text="▶️", font=("Segoe UI Emoji", 20),
                                bg=MENU_ITEM, fg=TEXT, command=self.toggle_play)
        self.play_btn.pack(side="left", padx=10)
        
        tk.Button(controls_frame, text="⏮️", font=("Segoe UI Emoji", 16),
                 bg=MENU_ITEM, fg=TEXT, command=self.previous_track).pack(side="left", padx=10)
        
        tk.Button(controls_frame, text="⏭️", font=("Segoe UI Emoji", 16),
                 bg=MENU_ITEM, fg=TEXT, command=self.next_track).pack(side="left", padx=10)
        
        # Volume
        volume_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        volume_frame.pack(pady=10)
        
        tk.Label(volume_frame, text="Громкость:", bg=WINDOW_BG, fg=TEXT).pack(side="left")
        self.volume = tk.Scale(volume_frame, from_=0, to=100, orient="horizontal",
                             bg=WINDOW_BG, fg=TEXT, highlightbackground=WINDOW_BG)
        self.volume.set(50)
        self.volume.pack(side="left", padx=10)
        
        # Playlist
        playlist_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        playlist_frame.pack(expand=True, fill="both", pady=10)
        
        tk.Label(playlist_frame, text="Плейлист:", bg=WINDOW_BG, fg=TEXT, 
                font=("Segoe UI", 12, "bold")).pack(anchor="w")
        
        self.playlist_listbox = tk.Listbox(playlist_frame, bg="#1b1820", fg=TEXT,
                                         selectbackground=MENU_ITEM)
        self.playlist_listbox.pack(expand=True, fill="both", pady=5)
        
        # Add demo tracks
        self.playlist = [
            "🎵 Легендарная мелодия 1",
            "🎵 Эпический саундтрек 2", 
            "🎵 Романтическая композиция 3",
            "🎵 Энергичный бит 4",
            "🎵 Спокойная музыка 5"
        ]
        
        for track in self.playlist:
            self.playlist_listbox.insert(tk.END, track)
            
        self.playlist_listbox.bind("<<ListboxSelect>>", self.select_track)
        
    def toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.play_btn.config(text="⏸️")
            self.simulate_playback()
        else:
            self.play_btn.config(text="▶️")
            
    def simulate_playback(self):
        if self.playing:
            current = self.progress.get()
            if current < 100:
                self.progress.set(current + 1)
                self.parent.after(100, self.simulate_playback)
            else:
                self.playing = False
                self.play_btn.config(text="▶️")
                
    def previous_track(self):
        self.current_track = (self.current_track - 1) % len(self.playlist)
        self.update_track_info()
        
    def next_track(self):
        self.current_track = (self.current_track + 1) % len(self.playlist)
        self.update_track_info()
        
    def select_track(self, event):
        selection = self.playlist_listbox.curselection()
        if selection:
            self.current_track = selection[0]
            self.update_track_info()
            
    def update_track_info(self):
        self.track_label.config(text=f"Сейчас играет: {self.playlist[self.current_track]}")
        self.progress.set(0)
        if self.playing:
            self.simulate_playback()

class WeatherApp:
    def __init__(self, parent):
        self.parent = parent
        self.cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg=WINDOW_BG)
        main_frame.pack(expand=True, fill="both", padx=12, pady=12)
        
        # Title
        title_label = tk.Label(main_frame, text="📊 Погода", 
                              bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=10)
        
        # City selection and search
        city_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        city_frame.pack(fill="x", pady=10)
        
        # Search frame
        search_frame = tk.Frame(city_frame, bg=WINDOW_BG)
        search_frame.pack(fill="x", pady=5)
        
        tk.Label(search_frame, text="Поиск города:", bg=WINDOW_BG, fg=TEXT).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                                   bg="#1b1820", fg=TEXT, font=TEXT_FONT, width=25)
        self.search_entry.pack(side="left", padx=10)
        
        search_btn = tk.Button(search_frame, text="🔍 Поиск", bg=MENU_ITEM, fg=TEXT,
                             command=self.search_weather)
        search_btn.pack(side="left", padx=5)
        
        # City selection frame
        selection_frame = tk.Frame(city_frame, bg=WINDOW_BG)
        selection_frame.pack(fill="x", pady=5)
        
        tk.Label(selection_frame, text="Быстрый выбор:", bg=WINDOW_BG, fg=TEXT).pack(side="left")
        self.city_var = tk.StringVar(value=self.cities[0])
        city_menu = tk.OptionMenu(selection_frame, self.city_var, *self.cities)
        city_menu.config(bg=MENU_ITEM, fg=TEXT, highlightbackground=WINDOW_BG)
        city_menu.pack(side="left", padx=10)
        
        update_btn = tk.Button(selection_frame, text="Обновить", bg=MENU_ITEM, fg=TEXT,
                             command=self.update_weather)
        update_btn.pack(side="left", padx=10)
        
        # Weather display
        self.weather_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        self.weather_frame.pack(expand=True, fill="both", pady=20)
        
        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda e: self.search_weather())
        
        self.update_weather()
        
    def search_weather(self):
        """Поиск погоды по названию города"""
        city = self.search_var.get().strip()
        if not city:
            return
            
        # Clear previous weather
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
            
        # Show loading
        loading_label = tk.Label(self.weather_frame, text=f"Поиск погоды для: {city}...", 
                               bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 12))
        loading_label.pack(pady=20)
        
        # Update the display
        self.parent.update()
        
        # Simulate API call with random data
        self.parent.after(1000, lambda: self.show_searched_weather(city))
        
    def show_searched_weather(self, city):
        """Показать погоду для найденного города"""
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
            
        # Generate random weather data for searched city
        temps = [-15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40]
        conditions = ["☀️ Солнечно", "⛅ Облачно", "🌧️ Дождь", "❄️ Снег", "🌤️ Переменная облачность", 
                     "🌫️ Туман", "⛈️ Гроза", "🌦️ Небольшой дождь"]
        winds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20]
        
        # Current weather for searched city
        current_temp = random.choice(temps)
        current_condition = random.choice(conditions)
        current_wind = random.choice(winds)
        current_humidity = random.randint(30, 90)
        current_pressure = random.randint(980, 1030)
        
        # Current weather frame
        current_frame = tk.Frame(self.weather_frame, bg=MENU_ITEM, relief="ridge", bd=2)
        current_frame.pack(fill="x", pady=10, padx=20)
        
        tk.Label(current_frame, text=f"🏙️ {city.title()}", bg=MENU_ITEM, fg=TEXT,
                font=("Segoe UI", 16, "bold")).pack(pady=8)
        
        # Temperature and condition
        temp_frame = tk.Frame(current_frame, bg=MENU_ITEM)
        temp_frame.pack(pady=5)
        
        tk.Label(temp_frame, text=f"🌡️ {current_temp}°C", bg=MENU_ITEM, fg=TEXT,
                font=("Segoe UI", 24, "bold")).pack(side="left", padx=20)
        
        tk.Label(temp_frame, text=current_condition, bg=MENU_ITEM, fg=TEXT,
                font=("Segoe UI", 16)).pack(side="left", padx=20)
        
        # Additional weather info
        info_frame = tk.Frame(current_frame, bg=MENU_ITEM)
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text=f"💨 Ветер: {current_wind} м/с", bg=MENU_ITEM, fg=TEXT,
                font=("Segoe UI", 12)).pack(side="left", padx=15)
                
        tk.Label(info_frame, text=f"💧 Влажность: {current_humidity}%", bg=MENU_ITEM, fg=TEXT,
                font=("Segoe UI", 12)).pack(side="left", padx=15)
                
        tk.Label(info_frame, text=f"📊 Давление: {current_pressure} гПа", bg=MENU_ITEM, fg=TEXT,
                font=("Segoe UI", 12)).pack(side="left", padx=15)
        
        # Forecast for searched city
        forecast_frame = tk.Frame(self.weather_frame, bg=WINDOW_BG)
        forecast_frame.pack(fill="x", pady=20)
        
        tk.Label(forecast_frame, text="Прогноз на 5 дней:", bg=WINDOW_BG, fg=TEXT,
                font=("Segoe UI", 14, "bold")).pack()
        
        days_frame = tk.Frame(forecast_frame, bg=WINDOW_BG)
        days_frame.pack(fill="x", pady=10)
        
        days = ["Сегодня", "Завтра", "Послезавтра", "Через 3 дня", "Через 4 дня"]
        
        for i, day in enumerate(days):
            day_frame = tk.Frame(days_frame, bg=MENU_ITEM, relief="ridge", bd=1)
            day_frame.pack(side="left", expand=True, fill="both", padx=2)
            
            day_temp = current_temp + random.randint(-8, 8)
            day_condition = random.choice(conditions)
            day_temp_min = day_temp - random.randint(2, 6)
            day_temp_max = day_temp + random.randint(2, 6)
            
            tk.Label(day_frame, text=day, bg=MENU_ITEM, fg=TEXT, 
                    font=("Segoe UI", 10, "bold")).pack(pady=8)
            tk.Label(day_frame, text=f"{day_temp_min}° / {day_temp_max}°", bg=MENU_ITEM, fg=TEXT,
                    font=("Segoe UI", 12)).pack(pady=2)
            tk.Label(day_frame, text=day_condition, bg=MENU_ITEM, fg=TEXT,
                    font=("Segoe UI", 8)).pack(pady=5)
                    
        # Add to quick selection if not already there
        if city.title() not in self.cities:
            self.cities.append(city.title())
            # Update the dropdown menu (this is simplified - in real app would need to recreate menu)
        
    def update_weather(self):
        for widget in self.weather_frame.winfo_children():
            widget.destroy()
            
        city = self.city_var.get()
        
        # Generate random weather data
        temps = [-5, 0, 5, 10, 15, 20, 25, 30]
        conditions = ["☀️ Солнечно", "⛅ Облачно", "🌧️ Дождь", "❄️ Снег", "🌤️ Переменная облачность"]
        winds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Current weather
        current_temp = random.choice(temps)
        current_condition = random.choice(conditions)
        current_wind = random.choice(winds)
        current_humidity = random.randint(30, 90)
        
        # Current weather frame
        current_frame = tk.Frame(self.weather_frame, bg=MENU_ITEM, relief="ridge", bd=2)
        current_frame.pack(fill="x", pady=10, padx=20)
        
        tk.Label(current_frame, text=f"🏙️ {city}", bg=MENU_ITEM, fg=TEXT,
                font=("Segoe UI", 14, "bold")).pack(pady=5)
        
        tk.Label(current_frame, text=f"🌡️ {current_temp}°C", bg=MENU_ITEM, fg=TEXT,
                font=("Segoe UI", 18, "bold")).pack(pady=5)
        
        tk.Label(current_frame, text=current_condition, bg=MENU_ITEM, fg=TEXT,
                font=("Segoe UI", 12)).pack(pady=2)
                
        tk.Label(current_frame, text=f"💨 Ветер: {current_wind} м/с", bg=MENU_ITEM, fg=TEXT).pack(pady=2)
        tk.Label(current_frame, text=f"💧 Влажность: {current_humidity}%", bg=MENU_ITEM, fg=TEXT).pack(pady=2)
        
        # Forecast
        forecast_frame = tk.Frame(self.weather_frame, bg=WINDOW_BG)
        forecast_frame.pack(fill="x", pady=20)
        
        tk.Label(forecast_frame, text="Прогноз на 5 дней:", bg=WINDOW_BG, fg=TEXT,
                font=("Segoe UI", 12, "bold")).pack()
        
        days_frame = tk.Frame(forecast_frame, bg=WINDOW_BG)
        days_frame.pack(fill="x", pady=10)
        
        days = ["Сегодня", "Завтра", "Послезавтра", "Через 3 дня", "Через 4 дня"]
        
        for i, day in enumerate(days):
            day_frame = tk.Frame(days_frame, bg=MENU_ITEM, relief="ridge", bd=1)
            day_frame.pack(side="left", expand=True, fill="both", padx=2)
            
            day_temp = current_temp + random.randint(-5, 5)
            day_condition = random.choice(conditions)
            
            tk.Label(day_frame, text=day, bg=MENU_ITEM, fg=TEXT, 
                    font=("Segoe UI", 10, "bold")).pack(pady=5)
            tk.Label(day_frame, text=f"{day_temp}°C", bg=MENU_ITEM, fg=TEXT).pack(pady=2)
            tk.Label(day_frame, text=day_condition, bg=MENU_ITEM, fg=TEXT,
                    font=("Segoe UI", 8)).pack(pady=2)

class ConverterApp:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg=WINDOW_BG)
        main_frame.pack(expand=True, fill="both", padx=12, pady=12)
        
        # Title
        title_label = tk.Label(main_frame, text="🧮 Конвертер величин", 
                              bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=10)
        
        # Conversion type
        type_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        type_frame.pack(fill="x", pady=10)
        
        tk.Label(type_frame, text="Тип конвертации:", bg=WINDOW_BG, fg=TEXT).pack(side="left")
        self.conv_type = tk.StringVar(value="length")
        types = [("Длина", "length"), ("Вес", "weight"), ("Температура", "temperature")]
        
        for text, value in types:
            tk.Radiobutton(type_frame, text=text, variable=self.conv_type, value=value,
                          bg=WINDOW_BG, fg=TEXT, selectcolor=MENU_ITEM,
                          command=self.update_units).pack(side="left", padx=10)
        
        # Input frame
        input_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        input_frame.pack(fill="x", pady=20)
        
        # From unit
        from_frame = tk.Frame(input_frame, bg=WINDOW_BG)
        from_frame.pack(side="left", expand=True)
        
        tk.Label(from_frame, text="Из:", bg=WINDOW_BG, fg=TEXT).pack()
        self.from_unit = tk.StringVar()
        self.from_menu = tk.OptionMenu(from_frame, self.from_unit, "")
        self.from_menu.config(bg=MENU_ITEM, fg=TEXT, width=15)
        self.from_menu.pack(pady=5)
        
        self.from_value = tk.Entry(from_frame, bg="#1b1820", fg=TEXT, font=TEXT_FONT)
        self.from_value.pack(pady=5)
        self.from_value.bind("<KeyRelease>", self.convert)
        
        # To unit
        to_frame = tk.Frame(input_frame, bg=WINDOW_BG)
        to_frame.pack(side="right", expand=True)
        
        tk.Label(to_frame, text="В:", bg=WINDOW_BG, fg=TEXT).pack()
        self.to_unit = tk.StringVar()
        self.to_menu = tk.OptionMenu(to_frame, self.to_unit, "")
        self.to_menu.config(bg=MENU_ITEM, fg=TEXT, width=15)
        self.to_menu.pack(pady=5)
        
        self.result_label = tk.Label(to_frame, text="0", bg=WINDOW_BG, fg=TEXT,
                                   font=("Segoe UI", 14, "bold"))
        self.result_label.pack(pady=5)
        
        # Swap button
        swap_btn = tk.Button(main_frame, text="↔️ Поменять местами", bg=MENU_ITEM, fg=TEXT,
                           command=self.swap_units)
        swap_btn.pack(pady=10)
        
        self.update_units()
        
    def update_units(self):
        conv_type = self.conv_type.get()
        
        if conv_type == "length":
            units = ["Метры", "Километры", "Сантиметры", "Мили", "Футы", "Дюймы"]
        elif conv_type == "weight":
            units = ["Килограммы", "Граммы", "Фунты", "Унции", "Тонны"]
        else:  # temperature
            units = ["Цельсий", "Фаренгейт", "Кельвин"]
            
        # Update menus
        self.from_menu['menu'].delete(0, 'end')
        self.to_menu['menu'].delete(0, 'end')
        
        for unit in units:
            self.from_menu['menu'].add_command(label=unit, command=tk._setit(self.from_unit, unit))
            self.to_menu['menu'].add_command(label=unit, command=tk._setit(self.to_unit, unit))
            
        self.from_unit.set(units[0])
        self.to_unit.set(units[1] if len(units) > 1 else units[0])
        
    def swap_units(self):
        from_unit = self.from_unit.get()
        to_unit = self.to_unit.get()
        self.from_unit.set(to_unit)
        self.to_unit.set(from_unit)
        self.convert()
        
    def convert(self, event=None):
        try:
            value = float(self.from_value.get() or 0)
            from_u = self.from_unit.get()
            to_u = self.to_unit.get()
            conv_type = self.conv_type.get()
            
            result = self.do_conversion(value, from_u, to_u, conv_type)
            self.result_label.config(text=f"{result:.4f}")
        except ValueError:
            self.result_label.config(text="Ошибка")
            
    def do_conversion(self, value, from_u, to_u, conv_type):
        if conv_type == "length":
            # Convert to meters first
            to_meters = {
                "Метры": 1,
                "Километры": 1000,
                "Сантиметры": 0.01,
                "Мили": 1609.34,
                "Футы": 0.3048,
                "Дюймы": 0.0254
            }
            
            meters = value * to_meters.get(from_u, 1)
            return meters / to_meters.get(to_u, 1)
            
        elif conv_type == "weight":
            # Convert to kg first
            to_kg = {
                "Килограммы": 1,
                "Граммы": 0.001,
                "Фунты": 0.453592,
                "Унции": 0.0283495,
                "Тонны": 1000
            }
            
            kg = value * to_kg.get(from_u, 1)
            return kg / to_kg.get(to_u, 1)
            
        else:  # temperature
            # Convert to Celsius first
            if from_u == "Цельсий":
                celsius = value
            elif from_u == "Фаренгейт":
                celsius = (value - 32) * 5/9
            else:  # Kelvin
                celsius = value - 273.15
                
            # Convert from Celsius to target
            if to_u == "Цельсий":
                return celsius
            elif to_u == "Фаренгейт":
                return celsius * 9/5 + 32
            else:  # Kelvin
                return celsius + 273.15

class TimerApp:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        self.running = False
        self.remaining = 0
        self.total = 0
        
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg=WINDOW_BG)
        main_frame.pack(expand=True, fill="both", padx=12, pady=12)
        
        # Title
        title_label = tk.Label(main_frame, text="⏰ Таймер", 
                              bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=10)
        
        # Time display
        self.time_label = tk.Label(main_frame, text="00:00", bg=WINDOW_BG, fg=TEXT,
                                 font=("Segoe UI", 48, "bold"))
        self.time_label.pack(pady=20)
        
        # Input frame
        input_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Минуты:", bg=WINDOW_BG, fg=TEXT).pack(side="left")
        self.minutes_entry = tk.Entry(input_frame, bg="#1b1820", fg=TEXT, width=5,
                                    font=("Segoe UI", 12))
        self.minutes_entry.pack(side="left", padx=5)
        
        tk.Label(input_frame, text="Секунды:", bg=WINDOW_BG, fg=TEXT).pack(side="left", padx=(20,0))
        self.seconds_entry = tk.Entry(input_frame, bg="#1b1820", fg=TEXT, width=5,
                                    font=("Segoe UI", 12))
        self.seconds_entry.pack(side="left", padx=5)
        
        # Controls
        controls_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        controls_frame.pack(pady=20)
        
        self.start_btn = tk.Button(controls_frame, text="Старт", bg="#4CAF50", fg="white",
                                 font=("Segoe UI", 12), padx=20, command=self.start_timer)
        self.start_btn.pack(side="left", padx=10)
        
        self.pause_btn = tk.Button(controls_frame, text="Пауза", bg="#FF9800", fg="white",
                                 font=("Segoe UI", 12), padx=20, command=self.pause_timer,
                                 state="disabled")
        self.pause_btn.pack(side="left", padx=10)
        
        reset_btn = tk.Button(controls_frame, text="Сброс", bg="#f44336", fg="white",
                            font=("Segoe UI", 12), padx=20, command=self.reset_timer)
        reset_btn.pack(side="left", padx=10)
        
        # Progress
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=20)
        
    def start_timer(self):
        if not self.running:
            try:
                minutes = int(self.minutes_entry.get() or 0)
                seconds = int(self.seconds_entry.get() or 0)
                self.total = minutes * 60 + seconds
                self.remaining = self.total
                
                if self.remaining > 0:
                    self.running = True
                    self.start_btn.config(state="disabled")
                    self.pause_btn.config(state="normal")
                    self.update_timer()
            except ValueError:
                pass
        else:
            self.running = True
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.update_timer()
            
    def pause_timer(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        
    def reset_timer(self):
        self.running = False
        self.remaining = 0
        self.total = 0
        self.time_label.config(text="00:00")
        self.progress["value"] = 0
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        
    def update_timer(self):
        if self.running and self.remaining > 0:
            minutes = self.remaining // 60
            seconds = self.remaining % 60
            self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
            
            # Update progress
            if self.total > 0:
                progress = 100 * (self.total - self.remaining) / self.total
                self.progress["value"] = progress
                
            self.remaining -= 1
            self.parent.after(1000, self.update_timer)
        elif self.remaining <= 0 and self.total > 0:
            self.time_label.config(text="00:00")
            self.progress["value"] = 100
            self.running = False
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            # Show completion message
            self.show_completion()
            
    def show_completion(self):
        completion_win = tk.Toplevel(self.parent)
        completion_win.title("Таймер")
        completion_win.geometry("300x150")
        completion_win.configure(bg=WINDOW_BG)
        completion_win.resizable(False, False)
        
        tk.Label(completion_win, text="⏰ Время вышло!", bg=WINDOW_BG, fg=TEXT,
                font=("Segoe UI", 16, "bold")).pack(expand=True)
        
        tk.Button(completion_win, text="OK", bg=MENU_ITEM, fg=TEXT,
                 command=completion_win.destroy).pack(pady=10)

class TextEditor:
    def __init__(self, parent):
        self.parent = parent
        self.filename = None
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg=WINDOW_BG)
        main_frame.pack(expand=True, fill="both", padx=12, pady=12)
        
        # Menu bar
        menubar = tk.Frame(main_frame, bg=MENU_ITEM, height=30)
        menubar.pack(fill="x", pady=(0,10))
        menubar.pack_propagate(False)
        
        # File menu
        file_btn = tk.Menubutton(menubar, text="Файл", bg=MENU_ITEM, fg=TEXT)
        file_btn.pack(side="left")
        file_menu = tk.Menu(file_btn, tearoff=0, bg=MENU_BG, fg=TEXT)
        file_btn.config(menu=file_menu)
        file_menu.add_command(label="Новый", command=self.new_file)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_command(label="Сохранить как", command=self.save_as_file)
        
        # Edit menu
        edit_btn = tk.Menubutton(menubar, text="Правка", bg=MENU_ITEM, fg=TEXT)
        edit_btn.pack(side="left")
        edit_menu = tk.Menu(edit_btn, tearoff=0, bg=MENU_BG, fg=TEXT)
        edit_btn.config(menu=edit_menu)
        edit_menu.add_command(label="Вырезать", command=self.cut_text)
        edit_menu.add_command(label="Копировать", command=self.copy_text)
        edit_menu.add_command(label="Вставить", command=self.paste_text)
        
        # Text area
        text_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        text_frame.pack(expand=True, fill="both")
        
        self.text_area = tk.Text(text_frame, bg="#1b1820", fg=TEXT, wrap="word",
                               font=("Consolas", 11), undo=True)
        
        scrollbar = tk.Scrollbar(text_frame, command=self.text_area.yview)
        self.text_area.config(yscrollcommand=scrollbar.set)
        
        self.text_area.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")
        
        # Status bar
        self.status_bar = tk.Label(main_frame, text="Готов", bg=MENU_ITEM, fg=TEXT,
                                 anchor="w")
        self.status_bar.pack(fill="x", pady=(10,0))
        
        # Bind events
        self.text_area.bind("<KeyRelease>", self.update_status)
        
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.filename = None
        self.status_bar.config(text="Новый файл")
        
    def open_file(self):
        filename = tk.filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)
                    self.filename = filename
                    self.status_bar.config(text=f"Открыт: {filename}")
            except Exception as e:
                tk.messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")
                
    def save_file(self):
        if self.filename:
            try:
                with open(self.filename, 'w', encoding='utf-8') as file:
                    content = self.text_area.get(1.0, tk.END)
                    file.write(content)
                    self.status_bar.config(text=f"Сохранено: {self.filename}")
            except Exception as e:
                tk.messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        filename = tk.filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            self.filename = filename
            self.save_file()
            
    def cut_text(self):
        self.text_area.event_generate("<<Cut>>")
        
    def copy_text(self):
        self.text_area.event_generate("<<Copy>>")
        
    def paste_text(self):
        self.text_area.event_generate("<<Paste>>")
        
    def update_status(self, event=None):
        text = self.text_area.get(1.0, tk.END)
        lines = text.count('\n')
        words = len(text.split())
        chars = len(text.replace('\n', ''))
        self.status_bar.config(text=f"Строк: {lines} | Слов: {words} | Символов: {chars}")

class GamesCollection:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg=WINDOW_BG)
        main_frame.pack(expand=True, fill="both", padx=12, pady=12)
        
        # Title
        title_label = tk.Label(main_frame, text="🎲 Коллекция игр", 
                              bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=10)
        
        # Games grid
        games_frame = tk.Frame(main_frame, bg=WINDOW_BG)
        games_frame.pack(expand=True, fill="both", pady=20)
        
        games = [
            ("🎯", "Попади в цель", self.target_game),
            ("🎲", "Кости", self.dice_game),
            ("🔢", "Угадай число", self.guess_number),
            ("🎮", "Змейка", self.snake_game),
            ("🧩", "Пазл", self.puzzle_game),
            ("🎴", "Память", self.memory_game),
        ]
        
        for i, (emoji, name, command) in enumerate(games):
            btn = tk.Button(games_frame, text=f"{emoji}\n{name}", 
                          bg=MENU_ITEM, fg=TEXT, font=("Segoe UI", 12),
                          command=command, width=12, height=4)
            btn.grid(row=i//3, column=i%3, padx=10, pady=10)
            
    def target_game(self):
        game_win = tk.Toplevel(self.parent)
        game_win.title("Попади в цель")
        game_win.geometry("400x400")
        game_win.configure(bg=WINDOW_BG)
        
        canvas = tk.Canvas(game_win, bg=WINDOW_BG, highlightthickness=0)
        canvas.pack(expand=True, fill="both")
        
        score = 0
        target = None
        
        def create_target():
            nonlocal target
            x = random.randint(50, 350)
            y = random.randint(50, 350)
            target = canvas.create_oval(x-20, y-20, x+20, y+20, fill="red", tags="target")
            
        def on_click(event):
            nonlocal score
            items = canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
            if target in items:
                canvas.delete("target")
                score += 1
                score_label.config(text=f"Очки: {score}")
                create_target()
                
        canvas.bind("<Button-1>", on_click)
        
        score_label = tk.Label(game_win, text="Очки: 0", bg=WINDOW_BG, fg=TEXT)
        score_label.pack()
        
        create_target()
        
    def dice_game(self):
        game_win = tk.Toplevel(self.parent)
        game_win.title("Кости")
        game_win.geometry("300x200")
        game_win.configure(bg=WINDOW_BG)
        
        def roll_dice():
            result = random.randint(1, 6)
            result_label.config(text=f"🎲 Выпало: {result}")
            
        tk.Label(game_win, text="Бросок костей", bg=WINDOW_BG, fg=TEXT,
                font=("Segoe UI", 14, "bold")).pack(pady=20)
                
        result_label = tk.Label(game_win, text="🎲 Нажмите 'Бросить'", bg=WINDOW_BG, fg=TEXT,
                              font=("Segoe UI", 16))
        result_label.pack(pady=20)
        
        tk.Button(game_win, text="Бросить кости", bg=MENU_ITEM, fg=TEXT,
                 command=roll_dice).pack(pady=10)
                 
    def guess_number(self):
        game_win = tk.Toplevel(self.parent)
        game_win.title("Угадай число")
        game_win.geometry("300x250")
        game_win.configure(bg=WINDOW_BG)
        
        number = random.randint(1, 100)
        attempts = 0
        
        def check_guess():
            nonlocal attempts
            try:
                guess = int(entry.get())
                attempts += 1
                
                if guess < number:
                    result_label.config(text="📈 Загаданное число больше!")
                elif guess > number:
                    result_label.config(text="📉 Загаданное число меньше!")
                else:
                    result_label.config(text=f"🎉 Правильно! Попыток: {attempts}")
                    entry.config(state="disabled")
                    check_btn.config(state="disabled")
            except ValueError:
                result_label.config(text="Введите число!")
                
        def new_game():
            nonlocal number, attempts
            number = random.randint(1, 100)
            attempts = 0
            entry.config(state="normal")
            check_btn.config(state="normal")
            entry.delete(0, tk.END)
            result_label.config(text="Угадайте число от 1 до 100")
            
        tk.Label(game_win, text="Угадай число (1-100)", bg=WINDOW_BG, fg=TEXT,
                font=("Segoe UI", 14, "bold")).pack(pady=10)
                
        entry = tk.Entry(game_win, bg="#1b1820", fg=TEXT, font=("Segoe UI", 12))
        entry.pack(pady=10)
        
        result_label = tk.Label(game_win, text="Угадайте число от 1 до 100", 
                              bg=WINDOW_BG, fg=TEXT)
        result_label.pack(pady=10)
        
        check_btn = tk.Button(game_win, text="Проверить", bg=MENU_ITEM, fg=TEXT,
                            command=check_guess)
        check_btn.pack(pady=5)
        
        tk.Button(game_win, text="Новая игра", bg=MENU_ITEM, fg=TEXT,
                 command=new_game).pack(pady=5)
                 
    def snake_game(self):
        # Простая реализация змейки
        game_win = tk.Toplevel(self.parent)
        game_win.title("Змейка")
        game_win.geometry("400x400")
        game_win.configure(bg=WINDOW_BG)
        
        canvas = tk.Canvas(game_win, bg="black", highlightthickness=0)
        canvas.pack(expand=True, fill="both")
        
        # Простое сообщение о том, что игра в разработке
        canvas.create_text(200, 200, text="🐍 Змейка в разработке!\n\nЭта игра появится\nв следующем обновлении!", 
                         fill="white", font=("Segoe UI", 14), justify="center")
                         
    def puzzle_game(self):
        game_win = tk.Toplevel(self.parent)
        game_win.title("Пазл")
        game_win.geometry("300x200")
        game_win.configure(bg=WINDOW_BG)
        
        tk.Label(game_win, text="🧩 Игра 'Пазл'", bg=WINDOW_BG, fg=TEXT,
                font=("Segoe UI", 14, "bold")).pack(expand=True)
        tk.Label(game_win, text="В разработке", bg=WINDOW_BG, fg=TEXT).pack()
        
    def memory_game(self):
        game_win = tk.Toplevel(self.parent)
        game_win.title("Память")
        game_win.geometry("300x200")
        game_win.configure(bg=WINDOW_BG)
        
        tk.Label(game_win, text="🎴 Игра 'Память'", bg=WINDOW_BG, fg=TEXT,
                font=("Segoe UI", 14, "bold")).pack(expand=True)
        tk.Label(game_win, text="В разработке", bg=WINDOW_BG, fg=TEXT).pack()

# ------------------ Build functions for new apps ------------------

def build_paint(parent):
    paint = PaintApp(parent)
    return paint

def build_music(parent):
    music = MusicPlayer(parent)
    return music

def build_weather(parent):
    weather = WeatherApp(parent)
    return weather

def build_converter(parent):
    converter = ConverterApp(parent)
    return converter

def build_timer(parent):
    timer = TimerApp(parent)
    return timer

def build_text_editor(parent):
    editor = TextEditor(parent)
    return editor

def build_games(parent):
    games = GamesCollection(parent)
    return games

def build_camera(parent):
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(expand=True, fill="both", padx=12, pady=12)
    
    tk.Label(frame, text="📷 Камера", bg=WINDOW_BG, fg=TEXT,
            font=("Segoe UI", 16, "bold")).pack(pady=20)
    
    # Имитация камеры
    camera_frame = tk.Frame(frame, bg="black", width=400, height=300)
    camera_frame.pack(pady=20)
    camera_frame.pack_propagate(False)
    
    tk.Label(camera_frame, text="📷 Камера\n\nДля использования реальной камеры\nтребуется подключение устройства", 
            bg="black", fg="white", font=("Segoe UI", 12), justify="center").pack(expand=True)
    
    controls = tk.Frame(frame, bg=WINDOW_BG)
    controls.pack(pady=20)
    
    tk.Button(controls, text="📸 Сделать снимок", bg=MENU_ITEM, fg=TEXT,
             command=lambda: tk.messagebox.showinfo("Камера", "Снимок сохранен!")).pack(side="left", padx=10)
    
    tk.Button(controls, text="🎥 Записать видео", bg=MENU_ITEM, fg=TEXT,
             command=lambda: tk.messagebox.showinfo("Камера", "Запись начата!")).pack(side="left", padx=10)
    
    return frame

def build_search(parent):
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(expand=True, fill="both", padx=12, pady=12)
    
    tk.Label(frame, text="🔍 Умный поиск", bg=WINDOW_BG, fg=TEXT,
            font=("Segoe UI", 16, "bold")).pack(pady=20)
    
    search_frame = tk.Frame(frame, bg=WINDOW_BG)
    search_frame.pack(fill="x", pady=20, padx=50)
    
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, bg="#1b1820", fg=TEXT,
                          font=("Segoe UI", 12), width=40)
    search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    
    def perform_search():
        query = search_var.get().lower()
        results = [
            "📁 Файлы: найдено 3 совпадения",
            "🌐 Веб: 15 результатов в браузере", 
            "📝 Заметки: 2 совпадения",
            "🎵 Музыка: 1 трек",
            "🖼️ Фото: 7 изображений"
        ]
        
        for widget in results_frame.winfo_children():
            widget.destroy()
            
        for result in results:
            tk.Label(results_frame, text=result, bg=WINDOW_BG, fg=TEXT,
                   font=("Segoe UI", 10)).pack(anchor="w", pady=2)
    
    tk.Button(search_frame, text="Искать", bg=MENU_ITEM, fg=TEXT,
             command=perform_search).pack(side="right")
    
    results_frame = tk.Frame(frame, bg=WINDOW_BG)
    results_frame.pack(fill="both", expand=True, pady=20)
    
    search_entry.bind("<Return>", lambda e: perform_search())
    
    return frame

def build_gallery(parent):
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(expand=True, fill="both", padx=12, pady=12)
    
    tk.Label(frame, text="🖼️ Галерея изображений", bg=WINDOW_BG, fg=TEXT,
            font=("Segoe UI", 16, "bold")).pack(pady=20)
    
    # Сетка изображений
    gallery_frame = tk.Frame(frame, bg=WINDOW_BG)
    gallery_frame.pack(expand=True, fill="both")
    
    # Заглушки для изображений
    for i in range(6):
        img_frame = tk.Frame(gallery_frame, bg=MENU_ITEM, width=150, height=150, relief="ridge", bd=2)
        img_frame.grid(row=i//3, column=i%3, padx=10, pady=10)
        img_frame.pack_propagate(False)
        
        tk.Label(img_frame, text=f"Изображение {i+1}", bg=MENU_ITEM, fg=TEXT,
                font=("Segoe UI", 10)).pack(expand=True)
    
    return frame

def build_settings(parent):
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(expand=True, fill="both", padx=12, pady=12)
    
    tk.Label(frame, text="⚙️ Настройки системы", bg=WINDOW_BG, fg=TEXT,
            font=("Segoe UI", 16, "bold")).pack(pady=20)
    
    settings_frame = tk.Frame(frame, bg=WINDOW_BG)
    settings_frame.pack(fill="both", expand=True, pady=20)
    
    # Настройки внешнего вида
    appearance_frame = tk.LabelFrame(settings_frame, text="Внешний вид", bg=WINDOW_BG, fg=TEXT,
                                   font=("Segoe UI", 12, "bold"))
    appearance_frame.pack(fill="x", pady=10, padx=20)
    
    tk.Checkbutton(appearance_frame, text="Темная тема", bg=WINDOW_BG, fg=TEXT,
                  selectcolor=MENU_ITEM).pack(anchor="w", pady=5)
    
    tk.Checkbutton(appearance_frame, text="Показывать анимации", bg=WINDOW_BG, fg=TEXT,
                  selectcolor=MENU_ITEM).pack(anchor="w", pady=5)
    
    # Настройки системы
    system_frame = tk.LabelFrame(settings_frame, text="Система", bg=WINDOW_BG, fg=TEXT,
                               font=("Segoe UI", 12, "bold"))
    system_frame.pack(fill="x", pady=10, padx=20)
    
    tk.Checkbutton(system_frame, text="Автозагрузка", bg=WINDOW_BG, fg=TEXT,
                  selectcolor=MENU_ITEM).pack(anchor="w", pady=5)
    
    tk.Checkbutton(system_frame, text="Уведомления", bg=WINDOW_BG, fg=TEXT,
                  selectcolor=MENU_ITEM).pack(anchor="w", pady=5)
    
    return frame

def build_books(parent):
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(expand=True, fill="both", padx=12, pady=12)
    
    tk.Label(frame, text="📚 Электронная библиотека", bg=WINDOW_BG, fg=TEXT,
            font=("Segoe UI", 16, "bold")).pack(pady=20)
    
    books_frame = tk.Frame(frame, bg=WINDOW_BG)
    books_frame.pack(expand=True, fill="both", pady=20)
    
    books = [
        "📖 Война и мир - Л. Толстой",
        "📖 Преступление и наказание - Ф. Достоевский", 
        "📖 Мастер и Маргарита - М. Булгаков",
        "📖 1984 - Дж. Оруэлл",
        "📖 Гарри Поттер - Дж. Роулинг",
        "📖 Властелин колец - Дж. Толкин"
    ]
    
    for book in books:
        book_frame = tk.Frame(books_frame, bg=MENU_ITEM, relief="ridge", bd=1)
        book_frame.pack(fill="x", pady=5, padx=50)
        
        tk.Label(book_frame, text=book, bg=MENU_ITEM, fg=TEXT,
                font=("Segoe UI", 11)).pack(pady=8)
    
    return frame

def build_task_manager(parent):
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(expand=True, fill="both", padx=12, pady=12)
    
    tk.Label(frame, text="🗂️ Диспетчер задач", bg=WINDOW_BG, fg=TEXT,
            font=("Segoe UI", 16, "bold")).pack(pady=20)
    
    # Список процессов
    tree = ttk.Treeview(frame, columns=("PID", "Name", "CPU", "Memory"), show="headings", height=15)
    tree.heading("PID", text="PID")
    tree.heading("Name", text="Имя процесса")
    tree.heading("CPU", text="CPU %")
    tree.heading("Memory", text="Память")
    
    tree.column("PID", width=80)
    tree.column("Name", width=200)
    tree.column("CPU", width=80)
    tree.column("Memory", width=100)
    
    # Демо-процессы
    processes = [
        ("1001", "system", "2%", "45 MB"),
        ("1002", "explorer", "5%", "120 MB"),
        ("1003", "browser", "15%", "450 MB"),
        ("1004", "music_player", "3%", "85 MB"),
        ("1005", "text_editor", "2%", "65 MB")
    ]
    
    for proc in processes:
        tree.insert("", "end", values=proc)
    
    tree.pack(expand=True, fill="both", padx=20, pady=10)
    
    # Кнопки управления
    controls = tk.Frame(frame, bg=WINDOW_BG)
    controls.pack(fill="x", pady=10, padx=20)
    
    tk.Button(controls, text="🔄 Обновить", bg=MENU_ITEM, fg=TEXT).pack(side="left", padx=5)
    tk.Button(controls, text="⏹️ Завершить", bg="#ff4444", fg="white").pack(side="left", padx=5)
    
    return frame

# ------------------ Real Browser Functionality ------------------
class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Создаем веб-движок
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        
        # Панель инструментов
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Кнопки навигации
        back_btn = QAction("Назад", self)
        back_btn.triggered.connect(self.browser.back)
        toolbar.addAction(back_btn)
        
        forward_btn = QAction("Вперед", self)
        forward_btn.triggered.connect(self.browser.forward)
        toolbar.addAction(forward_btn)
        
        reload_btn = QAction("Обновить", self)
        reload_btn.triggered.connect(self.browser.reload)
        toolbar.addAction(reload_btn)
        
        home_btn = QAction("Домой", self)
        home_btn.triggered.connect(self.navigate_home)
        toolbar.addAction(home_btn)
        
        # Адресная строка
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        # Обновление URL
        self.browser.urlChanged.connect(self.update_url)
        
        self.setCentralWidget(self.browser)
        self.setWindowTitle("Простой браузер на Python")
        self.show()
    
    def navigate_home(self):
        self.browser.setUrl(QUrl("https://www.google.com"))
    
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.browser.setUrl(QUrl(url))
    
    def update_url(self, q):
        self.url_bar.setText(q.toString())

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
            # Информация о браузере
            info_frame = tk.Frame(parent, bg=WINDOW_BG)
            info_frame.pack(expand=True, fill="both", padx=12, pady=12)
            
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
Нажмите кнопку "Запустить браузер" ниже для открытия
полнофункционального веб-браузера.

💡 ПОДСКАЗКИ:
• Браузер откроется в отдельном окне с полным функционалом
• Используйте кнопки навигации для перемещения по страницам
• Вводите URL в адресную строку для перехода на сайты
• Нажмите Enter для перехода по введенному URL

🔧 ТЕХНОЛОГИИ:
• Qt WebEngine 5.15+
• Chromium движок
• Аппарачное ускорение
"""
            
            text_widget = tk.Text(info_frame, bg="#1b1820", fg="white", bd=0, wrap="word",
                                font=("Consolas", 10), padx=15, pady=15)
            text_widget.pack(expand=True, fill="both")
            text_widget.insert("1.0", info_text)
            text_widget.config(state="disabled")
            
            # Кнопка запуска браузера
            launch_frame = tk.Frame(parent, bg=WINDOW_BG)
            launch_frame.pack(fill="x", pady=20)
            
            launch_btn = tk.Button(launch_frame, text="🚀 Запустить браузер", 
                                 bg="#4d7fff", fg="white", font=("Segoe UI", 14, "bold"),
                                 padx=20, pady=10, command=self.launch_browser)
            launch_btn.pack()
            
        def create_demo_browser_interface(self, parent):
            """Создает демо-интерфейс браузера"""
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
            
        def launch_browser(self):
            """Запускает реальный браузер с Qt WebEngine"""
            def start_qt_browser():
                browser = SimpleBrowser()
                # Запускаем Qt приложение
                app = QApplication([])
                browser.show()
                app.exec_()
            
            # Запуск в отдельном потоке
            thread = threading.Thread(target=start_qt_browser)
            thread.daemon = True
            thread.start()
    
    # Создаем и возвращаем экземпляр браузера
    browser = BrowserInterface(parent)
    return browser

# ------------------ File Manager ------------------
def build_files(parent):
    """Файловый менеджер с удалением в корзину"""
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(expand=True, fill="both", padx=12, pady=12)
    
    # Панель инструментов
    toolbar = tk.Frame(frame, bg=WINDOW_BG)
    toolbar.pack(fill="x", pady=(0, 10))
    
    # Поле текущего пути
    current_path = tk.StringVar(value=os.getcwd())
    path_entry = tk.Entry(toolbar, textvariable=current_path, bg="#1b1820", fg=TEXT, 
                         font=TEXT_FONT, width=50)
    path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    
    # Кнопка обновления
    def refresh_files():
        display_files(current_path.get())
    
    refresh_btn = tk.Button(toolbar, text="🔄", bg=MENU_ITEM, fg=TEXT,
                           font=("Segoe UI Emoji", 12), command=refresh_files)
    refresh_btn.pack(side="right", padx=5)
    
    # Кнопка наверх
    def go_up():
        current_dir = current_path.get()
        parent_dir = os.path.dirname(current_dir)
        if parent_dir != current_dir:  # Не поднимаемся выше корня
            current_path.set(parent_dir)
            display_files(parent_dir)
    
    up_btn = tk.Button(toolbar, text="⬆️", bg=MENU_ITEM, fg=TEXT,
                      font=("Segoe UI Emoji", 12), command=go_up)
    up_btn.pack(side="right", padx=5)
    
    # Область отображения файлов
    files_frame = tk.Frame(frame, bg=WINDOW_BG)
    files_frame.pack(expand=True, fill="both")
    
    # Заголовки колонок
    columns_frame = tk.Frame(files_frame, bg=MENU_ITEM)
    columns_frame.pack(fill="x")
    
    tk.Label(columns_frame, text="Имя", bg=MENU_ITEM, fg=TEXT, 
             font=TEXT_FONT, width=40, anchor="w").pack(side="left", padx=5)
    tk.Label(columns_frame, text="Тип", bg=MENU_ITEM, fg=TEXT,
             font=TEXT_FONT, width=15).pack(side="left", padx=5)
    tk.Label(columns_frame, text="Размер", bg=MENU_ITEM, fg=TEXT,
             font=TEXT_FONT, width=15).pack(side="left", padx=5)
    tk.Label(columns_frame, text="Действия", bg=MENU_ITEM, fg=TEXT,
             font=TEXT_FONT, width=20).pack(side="left", padx=5)
    
    # Прокручиваемая область для файлов
    canvas = tk.Canvas(files_frame, bg=WINDOW_BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(files_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=WINDOW_BG)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Словарь для хранения привязок колесика мыши
    mousewheel_bindings = {}
    
    def on_mousewheel(event):
        """Обработчик колесика мыши с проверкой существования canvas"""
        try:
            # Проверяем, существует ли еще canvas
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            # Если canvas был уничтожен, удаляем привязку
            pass
    
    def bind_mousewheel():
        """Привязывает колесико мыши к canvas"""
        if canvas not in mousewheel_bindings:
            canvas.bind("<MouseWheel>", on_mousewheel)
            mousewheel_bindings[canvas] = True
    
    def unbind_mousewheel():
        """Отвязывает колесико мыши от canvas"""
        if canvas in mousewheel_bindings:
            canvas.unbind("<MouseWheel>")
            del mousewheel_bindings[canvas]
    
    # Привязываем колесико мыши при создании
    bind_mousewheel()
    
    # Отвязываем при уничтожении окна
    def on_close():
        unbind_mousewheel()
    
    parent.winfo_toplevel().bind("<Destroy>", lambda e: on_close())
    
    def display_files(directory):
        """Отображает файлы в указанной директории"""
        # Очищаем предыдущий список
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        try:
            # Показываем текущий путь
            current_path.set(directory)
            
            # Получаем список файлов и папок
            items = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                items.append({
                    'name': item,
                    'path': item_path,
                    'is_dir': os.path.isdir(item_path),
                    'size': os.path.getsize(item_path) if not os.path.isdir(item_path) else 0
                })
            
            # Сортируем: сначала папки, потом файлы
            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            
            if not items:
                empty_label = tk.Label(scrollable_frame, text="Папка пуста", 
                                     bg=WINDOW_BG, fg=TEXT, font=TEXT_FONT)
                empty_label.pack(pady=20)
                return
            
            for item in items:
                create_file_row(scrollable_frame, item)
                
        except PermissionError:
            error_label = tk.Label(scrollable_frame, text="❌ Нет доступа к папке", 
                                 bg=WINDOW_BG, fg="#ff6b6b", font=TEXT_FONT)
            error_label.pack(pady=20)
        except Exception as e:
            error_label = tk.Label(scrollable_frame, text=f"❌ Ошибка: {str(e)}", 
                                 bg=WINDOW_BG, fg="#ff6b6b", font=TEXT_FONT)
            error_label.pack(pady=20)
    
    def create_file_row(parent_frame, item):
        """Создает строку с информацией о файле/папке"""
        row_frame = tk.Frame(parent_frame, bg=WINDOW_BG)
        row_frame.pack(fill="x", pady=2)
        
        # Иконка и имя
        icon = "📁" if item['is_dir'] else "📄"
        name_label = tk.Label(row_frame, text=f"{icon} {item['name']}", 
                             bg=WINDOW_BG, fg=TEXT, font=TEXT_FONT, anchor="w")
        name_label.pack(side="left", padx=5, fill="x", expand=True)
        
        # Тип
        type_text = "Папка" if item['is_dir'] else "Файл"
        type_label = tk.Label(row_frame, text=type_text, bg=WINDOW_BG, fg=TEXT,
                             font=TEXT_FONT, width=15)
        type_label.pack(side="left", padx=5)
        
        # Размер
        if item['is_dir']:
            size_text = "—"
        else:
            size_kb = item['size'] / 1024
            if size_kb < 1024:
                size_text = f"{size_kb:.1f} KB"
            else:
                size_text = f"{size_kb/1024:.1f} MB"
        
        size_label = tk.Label(row_frame, text=size_text, bg=WINDOW_BG, fg=TEXT,
                             font=TEXT_FONT, width=15)
        size_label.pack(side="left", padx=5)
        
        # Кнопки действий
        action_frame = tk.Frame(row_frame, bg=WINDOW_BG)
        action_frame.pack(side="left", padx=5)
        
        def open_item():
            if item['is_dir']:
                display_files(item['path'])
            else:
                # Открываем файл в стандартной программе
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(item['path'])
                    else:  # Linux/Mac
                        subprocess.run(['xdg-open', item['path']])
                except Exception as e:
                    print(f"Ошибка открытия файла: {e}")
        
        def delete_item():
            def do_delete():
                success, message = move_to_trash(item['path'])
                
                # Показываем уведомление
                notification = tk.Toplevel(parent)
                notification.overrideredirect(True)
                notification.configure(bg="#2b2036")
                notification.attributes("-topmost", True)
                notification.geometry(f"300x80+{SW-320}+{SH-100}")
                
                if success:
                    tk.Label(notification, text="✅ Файл перемещен в корзину", 
                            bg="#2b2036", fg="white", font=TEXT_FONT).pack(expand=True, padx=10, pady=10)
                    refresh_files()  # Обновляем список
                else:
                    tk.Label(notification, text=f"❌ {message}", 
                            bg="#2b2036", fg="#ff6b6b", font=TEXT_FONT).pack(expand=True, padx=10, pady=10)
                
                notification.after(3000, notification.destroy)
                confirm_win.destroy()
            
            # Подтверждение удаления
            confirm_win = tk.Toplevel(parent)
            confirm_win.title("Удаление")
            confirm_win.geometry("350x120")
            confirm_win.configure(bg=WINDOW_BG)
            confirm_win.resizable(False, False)
            
            tk.Label(confirm_win, text=f"Переместить '{item['name']}' в корзину?", 
                    bg=WINDOW_BG, fg=TEXT, font=TEXT_FONT).pack(expand=True, pady=10)
            
            btn_frame = tk.Frame(confirm_win, bg=WINDOW_BG)
            btn_frame.pack(fill="x", pady=10, padx=20)
            
            tk.Button(btn_frame, text="Удалить", bg="#ff4444", fg="white",
                     command=do_delete).pack(side="left", padx=10)
            tk.Button(btn_frame, text="Отмена", bg=MENU_ITEM, fg=TEXT,
                     command=confirm_win.destroy).pack(side="right", padx=10)
        
        open_btn = tk.Button(action_frame, text="Открыть", bg="#4CAF50", fg="white",
                           font=("Segoe UI", 8), padx=8, pady=2, command=open_item)
        open_btn.pack(side="left", padx=2)
        
        delete_btn = tk.Button(action_frame, text="Удалить", bg="#ff4444", fg="white",
                             font=("Segoe UI", 8), padx=8, pady=2, command=delete_item)
        delete_btn.pack(side="left", padx=2)
        
        # Двойной клик для открытия
        def on_double_click(event):
            open_item()
        
        row_frame.bind("<Double-Button-1>", on_double_click)
        name_label.bind("<Double-Button-1>", on_double_click)
        type_label.bind("<Double-Button-1>", on_double_click)
        size_label.bind("<Double-Button-1>", on_double_click)
    
    # Обработчик изменения пути
    def on_path_change(*args):
        new_path = current_path.get()
        if os.path.exists(new_path):
            display_files(new_path)
    
    current_path.trace_add("write", on_path_change)
    
    # Начальное отображение файлов
    display_files(os.getcwd())
    
    return frame

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
            write("Available commands: help, exit, ls, quit, about, joke, roll, flip, time, create, delete, write, mkdir, outpu, python, cd, pwd, clear")
            write("System commands: date, whoami, hostname, uname, ps, df, du, find, grep, wget, curl, ping, ifconfig, netstat")
            write("File commands: cat, head, tail, cp, mv, rename, chmod, stat, file, size, tree")
            write("Python commands: python <code> - execute Python code")
            write("Fun commands: weather, calc, quote, fact, password, base64, md5, sha1")
            write("Trash commands: trash, trash_empty, trash_restore, trash_delete")
            return

        if cmd == swearing:
            pass

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
            
        if cmd == "date":
            now = datetime.datetime.now()
            write(now.strftime("%Y-%m-%d %A"))
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
                success, message = move_to_trash(filename)
                write(message)
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

        elif cmd.startswith("outpu "):
            message = cmd[5:].strip()
            write(message)
            
        elif cmd.startswith("cat "):
            filename = cmd[4:].strip()
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                    write(f"Content of '{filename}':")
                    write(content)
            except FileNotFoundError:
                write("File not found.")
            except Exception as e:
                write(f"Error reading file: {e}")
                
        elif cmd.startswith("head "):
            filename = cmd[5:].strip()
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    lines = file.readlines()[:10]
                    write(f"First 10 lines of '{filename}':")
                    for line in lines:
                        write(line.rstrip())
            except FileNotFoundError:
                write("File not found.")
            except Exception as e:
                write(f"Error reading file: {e}")
                
        elif cmd.startswith("tail "):
            filename = cmd[5:].strip()
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    lines = file.readlines()[-10:]
                    write(f"Last 10 lines of '{filename}':")
                    for line in lines:
                        write(line.rstrip())
            except FileNotFoundError:
                write("File not found.")
            except Exception as e:
                write(f"Error reading file: {e}")
                
        elif cmd.startswith("cp "):
            parts = cmd[3:].strip().split()
            if len(parts) == 2:
                src, dst = parts
                try:
                    with open(src, 'rb') as source_file:
                        with open(dst, 'wb') as dest_file:
                            dest_file.write(source_file.read())
                    write(f"Copied '{src}' to '{dst}'")
                except Exception as e:
                    write(f"Error copying file: {e}")
            else:
                write("Usage: cp <source> <destination>")
                
        elif cmd.startswith("mv "):
            parts = cmd[3:].strip().split()
            if len(parts) == 2:
                src, dst = parts
                try:
                    os.rename(src, dst)
                    write(f"Moved '{src}' to '{dst}'")
                except Exception as e:
                    write(f"Error moving file: {e}")
            else:
                write("Usage: mv <source> <destination>")
                
        elif cmd.startswith("rename "):
            parts = cmd[7:].strip().split()
            if len(parts) == 2:
                old_name, new_name = parts
                try:
                    os.rename(old_name, new_name)
                    write(f"Renamed '{old_name}' to '{new_name}'")
                except Exception as e:
                    write(f"Error renaming file: {e}")
            else:
                write("Usage: rename <old_name> <new_name>")
                
        elif cmd == "whoami":
            write(os.getlogin())
            
        elif cmd == "hostname":
            write(os.uname().nodename)
            
        elif cmd == "uname":
            system_info = os.uname()
            write(f"System: {system_info.sysname}")
            write(f"Node: {system_info.nodename}")
            write(f"Release: {system_info.release}")
            write(f"Version: {system_info.version}")
            write(f"Machine: {system_info.machine}")
            
        elif cmd.startswith("find "):
            pattern = cmd[5:].strip()
            try:
                matches = []
                for root_dir, dirs, files in os.walk("."):
                    for file in files:
                        if pattern in file:
                            matches.append(os.path.join(root_dir, file))
                if matches:
                    write(f"Found {len(matches)} files:")
                    for match in matches[:20]:  # Limit output
                        write(f"  {match}")
                    if len(matches) > 20:
                        write(f"... and {len(matches) - 20} more files")
                else:
                    write("No files found.")
            except Exception as e:
                write(f"Error searching: {e}")
                
        elif cmd.startswith("grep "):
            pattern = cmd[5:].strip()
            write("grep: enter filename to search in:")
            entry.unbind("<Return>")
            def wait_grep_file(event=None):
                filename = entry.get().strip()
                entry.delete(0, "end")
                try:
                    with open(filename, 'r', encoding='utf-8') as file:
                        lines = file.readlines()
                        matches = []
                        for i, line in enumerate(lines, 1):
                            if pattern in line:
                                matches.append(f"Line {i}: {line.rstrip()}")
                        if matches:
                            write(f"Found {len(matches)} matches in '{filename}':")
                            for match in matches[:10]:
                                write(f"  {match}")
                            if len(matches) > 10:
                                write(f"... and {len(matches) - 10} more matches")
                        else:
                            write(f"No matches found in '{filename}'")
                except FileNotFoundError:
                    write("File not found.")
                except Exception as e:
                    write(f"Error searching file: {e}")
                entry.bind("<Return>", process_command)
            entry.bind("<Return>", wait_grep_file)
            
        elif cmd.startswith("wget "):
            url = cmd[5:].strip()
            write(f"Downloading {url}... (simulated)")
            write("Note: Real download functionality requires internet connection")
            
        elif cmd.startswith("curl "):
            url = cmd[5:].strip()
            write(f"Fetching {url}... (simulated)")
            write("Note: Real HTTP request requires internet connection")
            
        elif cmd.startswith("ping "):
            host = cmd[5:].strip()
            write(f"Pinging {host}... (simulated)")
            write("Reply from 127.0.0.1: bytes=32 time<1ms TTL=128")
            write("Reply from 127.0.0.1: bytes=32 time<1ms TTL=128")
            write("Reply from 127.0.0.1: bytes=32 time<1ms TTL=128")
            write("Reply from 127.0.0.1: bytes=32 time<1ms TTL=128")
            
        elif cmd == "ifconfig":
            write("eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500")
            write("        inet 192.168.1.100  netmask 255.255.255.0  broadcast 192.168.1.255")
            write("        ether 00:11:22:33:44:55  txqueuelen 1000  (Ethernet)")
            write("lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536")
            write("        inet 127.0.0.1  netmask 255.0.0.0")
            
        elif cmd == "netstat":
            write("Active Internet connections (simulated)")
            write("Proto Recv-Q Send-Q Local Address           Foreign Address         State")
            write("tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN")
            write("tcp        0      0 127.0.0.1:631           0.0.0.0:*               LISTEN")
            
        elif cmd.startswith("chmod "):
            parts = cmd[6:].strip().split()
            if len(parts) == 2:
                mode, filename = parts
                write(f"Changed permissions of '{filename}' to {mode} (simulated)")
            else:
                write("Usage: chmod <mode> <filename>")
                
        elif cmd.startswith("stat "):
            filename = cmd[5:].strip()
            try:
                stat_info = os.stat(filename)
                write(f"File: {filename}")
                write(f"Size: {stat_info.st_size} bytes")
                write(f"Permissions: {oct(stat_info.st_mode)[-3:]}")
                write(f"Modified: {datetime.datetime.fromtimestamp(stat_info.st_mtime)}")
            except FileNotFoundError:
                write("File not found.")
            except Exception as e:
                write(f"Error getting file info: {e}")
                
        elif cmd.startswith("file "):
            filename = cmd[5:].strip()
            try:
                if os.path.isdir(filename):
                    write(f"{filename}: directory")
                else:
                    write(f"{filename}: regular file")
            except Exception as e:
                write(f"Error: {e}")
                
        elif cmd.startswith("size "):
            filename = cmd[5:].strip()
            try:
                size = os.path.getsize(filename)
                write(f"{filename}: {size} bytes ({size/1024:.2f} KB)")
            except FileNotFoundError:
                write("File not found.")
            except Exception as e:
                write(f"Error: {e}")
                
        elif cmd == "tree":
            def print_tree(directory=".", prefix="", level=0):
                if level > 3:  # Limit depth
                    return
                try:
                    entries = os.listdir(directory)
                    for i, entry in enumerate(entries):
                        if entry.startswith('.'):  # Skip hidden files
                            continue
                        path = os.path.join(directory, entry)
                        is_last = i == len(entries) - 1
                        connector = "└── " if is_last else "├── "
                        write(prefix + connector + entry)
                        if os.path.isdir(path):
                            extension = "    " if is_last else "│   "
                            print_tree(path, prefix + extension, level + 1)
                except PermissionError:
                    write(prefix + "└── [Permission Denied]")
                except Exception:
                    pass
                    
            write(".")
            print_tree()
            
        elif cmd == "weather":
            cities = ["New York", "London", "Tokyo", "Paris", "Berlin"]
            city = random.choice(cities)
            temp = random.randint(-10, 35)
            conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy"]
            condition = random.choice(conditions)
            write(f"Weather in {city}: {temp}°C, {condition}")
            
        elif cmd.startswith("calc "):
            expression = cmd[5:].strip()
            try:
                result = eval(expression)
                write(f"{expression} = {result}")
            except Exception as e:
                write(f"Error calculating: {e}")
                
        elif cmd == "quote":
            quotes = [
                "The only way to do great work is to love what you do. - Steve Jobs",
                "Innovation distinguishes between a leader and a follower. - Steve Jobs",
                "Stay hungry, stay foolish. - Steve Jobs",
                "Your time is limited, don't waste it living someone else's life. - Steve Jobs"
            ]
            write(random.choice(quotes))
            
        elif cmd == "fact":
            facts = [
                "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly good to eat.",
                "Octopuses have three hearts.",
                "A day on Venus is longer than a year on Venus.",
                "Bananas are berries, but strawberries aren't."
            ]
            write(random.choice(facts))
            
        elif cmd == "password":
            length = 12
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
            password = ''.join(random.choice(chars) for _ in range(length))
            write(f"Generated password: {password}")
            
        elif cmd.startswith("base64 "):
            text = cmd[7:].strip()
            import base64
            try:
                encoded = base64.b64encode(text.encode()).decode()
                write(f"Base64 encoded: {encoded}")
            except Exception as e:
                write(f"Error encoding: {e}")
                
        elif cmd.startswith("md5 "):
            text = cmd[4:].strip()
            import hashlib
            try:
                hash_md5 = hashlib.md5(text.encode()).hexdigest()
                write(f"MD5 hash: {hash_md5}")
            except Exception as e:
                write(f"Error hashing: {e}")
                
        elif cmd.startswith("sha1 "):
            text = cmd[5:].strip()
            import hashlib
            try:
                hash_sha1 = hashlib.sha1(text.encode()).hexdigest()
                write(f"SHA1 hash: {hash_sha1}")
            except Exception as e:
                write(f"Error hashing: {e}")

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
                
        # Trash commands
        elif cmd == "trash":
            contents = get_trash_contents()
            if not contents:
                write("Корзина пуста")
            else:
                write(f"Содержимое корзины ({len(contents)} объектов):")
                for item in contents:
                    item_type = "📁" if item['is_dir'] else "📄"
                    size = f"{item['size']} bytes" if not item['is_dir'] else "папка"
                    time_str = datetime.datetime.fromtimestamp(item['deleted_time']).strftime("%Y-%m-%d %H:%M")
                    write(f"  {item_type} {item['name']} ({size}) - удалено: {time_str}")
                    
        elif cmd == "trash_empty":
            success, message = empty_trash()
            write(message)
            
        elif cmd.startswith("trash_restore "):
            item_name = cmd[14:].strip()
            success, message = restore_from_trash(item_name)
            write(message)
            
        elif cmd.startswith("trash_delete "):
            item_name = cmd[13:].strip()
            success, message = delete_permanently(item_name)
            write(message)
                
        elif cmd == "about":
            write("Flolower OS v1.0 (Beta)")
            write("A custom operating system interface built with Python and Tkinter")
            write("Terminal with enhanced command set")
            return
            
        else:
            write("Command not found!!!")

    entry.bind("<Return>", process_command)
    entry.focus_set()

# ------------------ Trash App ------------------
def build_trash(parent):
    """Создает интерфейс корзины"""
    frame = tk.Frame(parent, bg=WINDOW_BG)
    frame.pack(expand=True, fill="both", padx=12, pady=12)
    
    # Заголовок и кнопки управления
    header_frame = tk.Frame(frame, bg=WINDOW_BG)
    header_frame.pack(fill="x", pady=(0, 12))
    
    tk.Label(header_frame, text="🗑️ Корзина", bg=WINDOW_BG, fg=TEXT, 
             font=("Segoe UI", 16, "bold")).pack(side="left")
    
    # Кнопки управления
    btn_frame = tk.Frame(header_frame, bg=WINDOW_BG)
    btn_frame.pack(side="right")
    
    def refresh_contents():
        for widget in content_frame.winfo_children():
            widget.destroy()
        display_trash_contents()
    
    def empty_trash_confirm():
        def do_empty():
            success, message = empty_trash()
            status_label.config(text=message)
            if success:
                refresh_contents()
            confirm_win.destroy()
        
        confirm_win = tk.Toplevel(parent)
        confirm_win.title("Очистка корзины")
        confirm_win.geometry("300x150")
        confirm_win.configure(bg=WINDOW_BG)
        confirm_win.resizable(False, False)
        
        tk.Label(confirm_win, text="Вы уверены, что хотите\nочистить корзину?", 
                bg=WINDOW_BG, fg=TEXT, font=TEXT_FONT).pack(expand=True)
        
        btn_frame = tk.Frame(confirm_win, bg=WINDOW_BG)
        btn_frame.pack(fill="x", pady=10)
        
        tk.Button(btn_frame, text="Да", bg="#ff4444", fg="white",
                 command=do_empty).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Отмена", bg=MENU_ITEM, fg=TEXT,
                 command=confirm_win.destroy).pack(side="right", padx=10)
    
    refresh_btn = tk.Button(btn_frame, text="🔄 Обновить", bg=MENU_ITEM, fg=TEXT,
                           command=refresh_contents, padx=10, pady=5)
    refresh_btn.pack(side="left", padx=5)
    
    empty_btn = tk.Button(btn_frame, text="🧹 Очистить", bg="#ff4444", fg="white",
                         command=empty_trash_confirm, padx=10, pady=5)
    empty_btn.pack(side="left", padx=5)
    
    # Статус
    status_label = tk.Label(header_frame, text="", bg=WINDOW_BG, fg=TEXT, font=TEXT_FONT)
    status_label.pack(side="bottom", fill="x", pady=(5, 0))
    
    # Контент корзины
    content_frame = tk.Frame(frame, bg=WINDOW_BG)
    content_frame.pack(expand=True, fill="both")
    
    def display_trash_contents():
        contents = get_trash_contents()
        
        if not contents:
            empty_label = tk.Label(content_frame, text="Корзина пуста", 
                                 bg=WINDOW_BG, fg=TEXT, font=("Segoe UI", 14))
            empty_label.pack(expand=True)
            return
        
        # Заголовки колонок
        columns_frame = tk.Frame(content_frame, bg=MENU_ITEM)
        columns_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(columns_frame, text="Имя", bg=MENU_ITEM, fg=TEXT, 
                font=TEXT_FONT, width=30, anchor="w").pack(side="left", padx=5)
        tk.Label(columns_frame, text="Тип", bg=MENU_ITEM, fg=TEXT,
                font=TEXT_FONT, width=10).pack(side="left", padx=5)
        tk.Label(columns_frame, text="Размер", bg=MENU_ITEM, fg=TEXT,
                font=TEXT_FONT, width=15).pack(side="left", padx=5)
        tk.Label(columns_frame, text="Дата удаления", bg=MENU_ITEM, fg=TEXT,
                font=TEXT_FONT, width=20).pack(side="left", padx=5)
        tk.Label(columns_frame, text="Действия", bg=MENU_ITEM, fg=TEXT,
                font=TEXT_FONT, width=15).pack(side="left", padx=5)
        
        # Прокручиваемая область для содержимого
        canvas = tk.Canvas(content_frame, bg=WINDOW_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=WINDOW_BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Безопасная обработка колесика мыши для корзины
        def on_mousewheel_safe(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        
        canvas.bind("<MouseWheel>", on_mousewheel_safe)
        
        for item in contents:
            item_frame = tk.Frame(scrollable_frame, bg=WINDOW_BG)
            item_frame.pack(fill="x", pady=2)
            
            # Имя файла
            name_label = tk.Label(item_frame, text=item['name'], bg=WINDOW_BG, fg=TEXT,
                                font=TEXT_FONT, width=30, anchor="w")
            name_label.pack(side="left", padx=5)
            
            # Тип
            type_icon = "📁" if item['is_dir'] else "📄"
            type_label = tk.Label(item_frame, text=type_icon, bg=WINDOW_BG, fg=TEXT,
                                font=TEXT_FONT, width=10)
            type_label.pack(side="left", padx=5)
            
            # Размер
            if item['is_dir']:
                size_text = "Папка"
            else:
                size_kb = item['size'] / 1024
                if size_kb < 1024:
                    size_text = f"{size_kb:.1f} KB"
                else:
                    size_text = f"{size_kb/1024:.1f} MB"
            size_label = tk.Label(item_frame, text=size_text, bg=WINDOW_BG, fg=TEXT,
                                font=TEXT_FONT, width=15)
            size_label.pack(side="left", padx=5)
            
            # Дата удаления
            time_str = datetime.datetime.fromtimestamp(item['deleted_time']).strftime("%Y-%m-%d %H:%M")
            time_label = tk.Label(item_frame, text=time_str, bg=WINDOW_BG, fg=TEXT,
                                font=TEXT_FONT, width=20)
            time_label.pack(side="left", padx=5)
            
            # Кнопки действий
            action_frame = tk.Frame(item_frame, bg=WINDOW_BG)
            action_frame.pack(side="left", padx=5)
            
            def restore_item(name=item['name']):
                success, message = restore_from_trash(name)
                status_label.config(text=message)
                if success:
                    refresh_contents()
            
            def delete_item(name=item['name']):
                def do_delete():
                    success, message = delete_permanently(name)
                    status_label.config(text=message)
                    if success:
                        refresh_contents()
                    confirm_win.destroy()
                
                confirm_win = tk.Toplevel(parent)
                confirm_win.title("Удаление")
                confirm_win.geometry("300x120")
                confirm_win.configure(bg=WINDOW_BG)
                confirm_win.resizable(False, False)
                
                tk.Label(confirm_win, text=f"Удалить '{name}' навсегда?", 
                        bg=WINDOW_BG, fg=TEXT, font=TEXT_FONT).pack(expand=True)
                
                btn_frame = tk.Frame(confirm_win, bg=WINDOW_BG)
                btn_frame.pack(fill="x", pady=10)
                
                tk.Button(btn_frame, text="Удалить", bg="#ff4444", fg="white",
                         command=do_delete).pack(side="left", padx=10)
                tk.Button(btn_frame, text="Отмена", bg=MENU_ITEM, fg=TEXT,
                         command=confirm_win.destroy).pack(side="right", padx=10)
            
            restore_btn = tk.Button(action_frame, text="Восстановить", bg="#4CAF50", fg="white",
                                  font=("Segoe UI", 8), padx=5, pady=2, command=restore_item)
            restore_btn.pack(side="left", padx=2)
            
            delete_btn = tk.Button(action_frame, text="Удалить", bg="#ff4444", fg="white",
                                 font=("Segoe UI", 8), padx=5, pady=2, command=delete_item)
            delete_btn.pack(side="left", padx=2)
    
    display_trash_contents()

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
    elif key == "trash":
        build_trash(content)
    elif key == "files":
        build_files(content)
    elif key == "smile_game":
        build_smile_game(content)
    elif key == "paint":
        build_paint(content)
    elif key == "music":
        build_music(content)
    elif key == "weather":
        build_weather(content)
    elif key == "converter":
        build_converter(content)
    elif key == "timer":
        build_timer(content)
    elif key == "camera":
        build_camera(content)
    elif key == "search":
        build_search(content)
    elif key == "text_editor":
        build_text_editor(content)
    elif key == "games":
        build_games(content)
    elif key == "gallery":
        build_gallery(content)
    elif key == "settings":
        build_settings(content)
    elif key == "books":
        build_books(content)
    elif key == "task_manager":
        build_task_manager(content)
    else:
        tk.Label(content, text=f"{title} — демо", bg=WINDOW_BG, fg=TEXT).pack(padx=12, pady=12)

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

# Используем только DESKTOP_ICONS (без дублирования корзины)
for i, (emoji, title, key) in enumerate(DESKTOP_ICONS):
    pos = saved_positions.get(str(i))
    if pos and isinstance(pos, dict) and "x" in pos and "y" in pos:
        create_desktop_icon(pos["x"], pos["y"], emoji, title, key)
    else:
        create_desktop_icon(64, 84 + i*110, emoji, title, key)

# ------------------ Mainloop ------------------
start_menu.place(y=SH+20)
# Убедитесь, что canvas находится позади всего
canvas.lower = lambda: None  # Убираем проблемный вызов

# Создаем папку для корзины при запуске
ensure_trash_dir()

root.protocol("WM_DELETE_WINDOW", lambda: (save_icon_positions(), root.destroy()))
root.mainloop()
