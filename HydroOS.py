import tkinter as tk
import random
# from platform import processor

import time
from tkinter import messagebox
import os
import requests
import platform
from Browser import openBrowser
from weather_app import openWeather

WIDTH = 1280
HEIGHT = 768

root = tk.Tk()
root.title("QJRdesktop")
root.geometry(f"{WIDTH}x{HEIGHT}")
# root.configure(bg=(255, 0, 0))
# root.attributes("-fullscreen", True)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack(fill="both", expand=True)

# Генеруємо фонові сфери
for _ in range(50):
    radius = random.randint(20, 80)
    x = random.randint(0, WIDTH - radius)
    y = random.randint(0, HEIGHT - radius)
    color = random.choice(["#9933ff", "#aa44ff", "#7744dd", "#cc66ff", "#6600cc"])
    canvas.create_oval(x, y, x + radius, y + radius, fill=color, outline="")

# --- ФУНКЦІЇ ДЛЯ КНОПОК ---

# class AppWindow:
#     id_counter = 0
#     def __init__(self, manager, title="Window", w=420, h=300, x=100, y=100, app_type=None):
#         self.manager = manager
#         self.title = title
#         self.w = w
#         self.h = h
#         self.x = x
#         self.y = y
#         self.app_type = app_type
#         self.minimized = False
#         self.maximized = False
#         self.prev_geom = None
#         AppWindow.id_counter += 1
#
#         self.frame = tk.Frame(root, bg=WINDOW_BG, bd=0, highlightthickness=0)
#         self.titlebar = tk.Frame(self.frame, bg=TITLE_BG, height=30)
#         self.titlebar.pack(side="top", fill="x")
#
#         self.title_lbl = tk.Label(self.titlebar, text=self.title, bg=TITLE_BG, fg=TITLE_FG)
#         self.title_lbl.pack(side="left", padx=8)
#
#         # правильные цвета кнопок управления
#         # self.btn_close = tk.Button(self.titlebar, text="✕", bg=CLOSE_RED, fg="white",
#         #                            bd=0, relief="flat", width=3, command=self.close)
#         # self.btn_min = tk.Button(self.titlebar, text="▁", bg=BTN_GRAY, fg="white",
#         #                          bd=0, relief="flat", width=3, command=self.minimize)
#         # self.btn_max = tk.Button(self.titlebar, text="▢", bg=BTN_GRAY, fg="white",
#         #                          bd=0, relief="flat", width=3, command=self.maximize_restore)
#
#         self.btn_close = tk.Button(self.titlebar, text="✕", fg="white",
#                                    bd=0, relief="flat", width=3, command=self.close)
#         self.btn_min = tk.Button(self.titlebar, text="▁", fg="white",
#                                  bd=0, relief="flat", width=3, command=self.minimize)
#         self.btn_max = tk.Button(self.titlebar, text="▢", fg="white",
#                                  bd=0, relief="flat", width=3, command=self.maximize_restore)
#         self.btn_close.pack(side="right", padx=1)
#         self.btn_max.pack(side="right", padx=1)
#         self.btn_min.pack(side="right", padx=1)
#
#         # self.content = tk.Frame(self.frame, bg=WINDOW_BG)
#         # self.content.pack(fill="both", expand=True)
#
#         # attach app content
#         # if app_type == "calculator":
#         #     build_calculator(self.content)
#         # elif app_type == "notes":
#         #     build_text_app(self.content)
#         # elif app_type == "browser":
#         #     build_browser_app(self.content)
#
#         self.canvas_window = canvas.create_window(self.x, self.y, anchor="nw", window=self.frame, width=self.w, height=self.h)
#
#         # move bindings
#         self.titlebar.bind("<Button-1>", self.start_move)
#         self.titlebar.bind("<B1-Motion>", self.do_move)
#         self.titlebar.bind("<ButtonRelease-1>", self.end_move)
#         self.title_lbl.bind("<Button-1>", self.start_move)
#         self.title_lbl.bind("<B1-Motion>", self.do_move)
#         self.title_lbl.bind("<ButtonRelease-1>", self.end_move)
#
#         self.frame.bind("<Button-1>", lambda e: self.manager.focus_window(self))
#         self.titlebar.bind("<Double-Button-1>", lambda e: self.maximize_restore())
#
#         # self.task_btn = tk.Button(task_buttons_frame, text=self.title, bg=TASKBAR_BG, fg="white", bd=0, relief="flat", command=self.toggle_minimize)
#         # self.task_btn.pack(side="left", padx=4, ipadx=6)
#
#         self.manager.register(self)



def weather():
    # win = tk.Toplevel(root)
    # win.title("QJRweather")
    # win.geometry("450x250")
    # win.configure(bg="#332244")
    #
    # url = requests.get("sinoptik.")
    #
    # temperature = ...
    # pass
    openWeather()


def open_clock():
    win = tk.Toplevel(root)
    win.title("QJRclock")
    WIDTH_ = 360
    HEIGHT_ = 240

    win.geometry(f"{WIDTH_}x{HEIGHT_}")
    win.configure(bg="#332244")

    clock_label = tk.Label(win, font=("Consolas", 30), bg="#222233", fg="white")
    # clock_label.pack(padx=WIDTH_//2, pady=HEIGHT_//2)
    clock_label.place(x=10, y=10)

    def update_time():
        current_time = time.strftime("%H:%M:%S")
        clock_label.config(text=current_time)
        root.after(1000, update_time)

    update_time()

def open_taskmgr():
    win = tk.Toplevel(root)
    win.title("QJRtaskmgr")
    win.geometry("360x240")
    win.configure(bg="#332244")

    user_current = tk.Label(text="[👨] User: Administrator")
    user_current.place(x=10, y=40)

    yourIP = ...

    processor = tk.Label(text="[🖥️] Processor: QJR CORE")
    processor.place(x=10, y=10)


def open_timer():
    import time

    win = tk.Toplevel(root)
    win.title("QJRtimer")
    win.geometry("360x240")
    win.configure(bg="#332244")

    def s5():
        for i in range(5):
            status = tk.Label(win, text=f"Status: {i + 1}/5", font=("Consolas", 14))
            status.place(x=10, y=70)
            time.sleep(1)

        expire_label = tk.Label(win, text="Timer has been expired.", font=("Consolas", 14))
        expire_label.place(x=10, y=45)

    def s10():
        for i in range(10):
            status = tk.Label(win, text=f"Status: {i + 1}/10", font=("Consolas", 14))
            status.place(x=10, y=70)
            time.sleep(1)

        expire_label = tk.Label(win, text="Timer has been expired.", font=("Consolas", 14))
        expire_label.place(x=10, y=45)

    def s30():
        for i in range(30):
            status = tk.Label(win, text=f"Status: {i + 1}/30", font=("Consolas", 14))
            status.place(x=10, y=70)
            time.sleep(1)

        expire_label = tk.Label(win, text="Timer has been expired.", font=("Consolas", 14))
        expire_label.place(x=10, y=45)

    sec5 = tk.Button(win, text="5 seconds", font=("Consolas", 14), command=s5)
    sec5.place(x=10, y=10)

    sec10 = tk.Button(win, text="10 seconds", font=("Consolas", 14), command=s10)
    sec10.place(x=120, y=10)

    sec30 = tk.Button(win, text="30 seconds", font=("Consolas", 14), command=s30)
    sec30.place(x=237, y=10)


def open_browser():
    # win = tk.Toplevel(root)
    # win.title("QJRwebBrowsar")
    # win.geometry("360x240")
    # win.configure(bg="#332244")
    #
    # enter_url_top = tk.Entry(win, font=("Consolas", 12), width=35)
    # enter_url_top.place(x=10, y=10)
    #
    # openweb_button = tk.Button(win, entry.get)
    openBrowser()

def QJRnetwork():
    pass

def cnw():
    appname = ""
    win = tk.Toplevel(root)
    win.title(appname)
    win.geometry("450x250")
    win.configure(bg="#332244")


def open_ligvo():
    win = tk.Toplevel(root)
    win.title("QJR")
    win.geometry("450x250")
    win.configure(bg="#332244")

    status = "Fully working"
    statusLabel = tk.Label(win, text=f"Status: {status}", font=("Consolas", 14), bg="#332244", fg="white")
    statusLabel.pack(expand=True)

def open_sphere():
    # popup("Sphere запущено")
    pass

def open_post():
    # popup("QJR Post Office відкрито")
    pass

def open_core():
    # popup("Core Utility запущено")
    pass

def open_aprnce():
    prsn = tk.Toplevel(root)
    prsn.title("QJR Settings")
    prsn.geometry("600x400")
    prsn.configure(bg="#332244")

    setup_theme = tk.Label(prsn, text="Theme: Circles - magenta")
    setup_theme.place(x=10, y=20)



def open_settings():
    # popup("Налаштування відкрито")
    settings_win = tk.Toplevel(root)
    settings_win.title("QJR Settings")
    settings_win.geometry("600x400")
    settings_win.configure(bg="#332244")

    settings_text = ()

    stng_lbl = tk.Label(settings_win, text="Settings", font=("Consolas", 19))
    stng_lbl.place(x=10, y=10)

    about_btn = tk.Button(settings_win, text="ℹ️ About\n shows you information\n about your system.",font=("Consolas", 14), command=open_info)
    about_btn.place(x=10, y=45)

    apperience = tk.Button(settings_win, text="🖥️ Apperience\nshows you customisation settings\nto personalize your PC.", font=("Consolas", 14), command=open_aprnce)
    apperience.place(x=200, y=45)

def open_explorer():
    explorer = tk.Toplevel(root)
    explorer.title("QJR Explorer")
    explorer.geometry("600x400")
    explorer.configure(bg="#332244")

    qjr_root = os.path.abspath("../../../../New/qjr-root")
    path_var = tk.StringVar(value=qjr_root)

    def list_dir(path):
        listbox.delete(0, tk.END)
        path_var.set(path)
        try:
            items = os.listdir(path)
            items.sort()
            # Only show ".." if not at root
            if os.path.abspath(path) != qjr_root:
                listbox.insert(tk.END, "..")
            for item in items:
                listbox.insert(tk.END, item)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_open(event=None):
        selection = listbox.curselection()
        if not selection:
            return
        name = listbox.get(selection[0])
        current_path = path_var.get()
        if name == "..":
            new_path = os.path.dirname(current_path)
            # Prevent going above qjr_root
            if os.path.abspath(new_path).startswith(qjr_root):
                list_dir(new_path)
        else:
            full_path = os.path.join(current_path, name)
            if os.path.isdir(full_path):
                list_dir(full_path)
            else:
                messagebox.showinfo("File Selected", f"Selected file:\n{full_path}")

    path_entry = tk.Entry(explorer, textvariable=path_var, font=("Consolas", 12), bg="#222233", fg="white")
    path_entry.pack(fill="x", padx=5, pady=5)

    listbox = tk.Listbox(explorer, font=("Consolas", 12), bg="#222233", fg="white")
    listbox.pack(fill="both", expand=True, padx=5, pady=5)
    listbox.bind("<Double-1>", on_open)

    list_dir(qjr_root)

    # path_var = tk.StringVar(value=os.path.expanduser("~"))
    #
    # def list_dir(path):
    #     listbox.delete(0, tk.END)
    #     path_var.set(path)
    #     try:
    #         items = os.listdir(path)
    #         items.sort()
    #         if os.path.dirname(path) != path:
    #             listbox.insert(tk.END, "..")
    #         for item in items:
    #             listbox.insert(tk.END, item)
    #     except Exception as e:
    #         messagebox.showerror("Error", str(e))
    #
    # def on_open(event=None):
    #     selection = listbox.curselection()
    #     if not selection:
    #         return
    #     name = listbox.get(selection[0])
    #     current_path = path_var.get()
    #     if name == "..":
    #         new_path = os.path.dirname(current_path)
    #         list_dir(new_path)
    #     else:
    #         full_path = os.path.join(current_path, name)
    #         if os.path.isdir(full_path):
    #             list_dir(full_path)
    #         else:
    #             messagebox.showinfo("File Selected", f"Selected file:\n{full_path}")
    #
    # path_entry = tk.Entry(explorer, textvariable=path_var, font=("Consolas", 12), bg="#222233", fg="white")
    # path_entry.pack(fill="x", padx=5, pady=5)
    #
    # listbox = tk.Listbox(explorer, font=("Consolas", 12), bg="#222233", fg="white")
    # listbox.pack(fill="both", expand=True, padx=5, pady=5)
    # listbox.bind("<Double-1>", on_open)
    #
    # list_dir(path_var.get())

def open_info():
    info_win = tk.Toplevel(root)
    info_win.title("QJR Info")
    info_win.geometry("400x200")
    info_win.configure(bg="#332244")

    info_text = (
        "QJR (Quantum Java Runtime) is a fictional operating system\n"
        "\n\n"
        "Version: 5.11.2\n"
        "Developed by: © QJR Team 2019 - 2025\n"
        "License: Open Source\n\n"
        "For more information, visit our website: qjr.home\n"
    )

    label = tk.Label(info_win, text=info_text, font=("Consolas", 12), bg="#332244", fg="white")
    label.pack(expand=True, padx=10, pady=10)

# Вікно-повідомлення
# def popup(text):
#     win = tk.Toplevel(root)
#     win.title("QJR")
#     win.geometry("300x100")
#     win.configure(bg="#332244")
#     label = tk.Label(win, text=text, font=("Consolas", 14), bg="#332244", fg="white")
#     label.pack(expand=True)

def open_applications():
    pass

def open_start():
    startmenu = tk.Toplevel(root)
    startmenu.title("Start")
    startmenu.geometry("300x335")
    startmenu.configure(bg="#332244")

    open_explorer_ = tk.Button(startmenu, text="📂File manager", width=35, font=("Consolas", 12), command=open_explorer)
    open_explorer_.place(x=10, y=10)

    open_settings_ = tk.Button(startmenu, text="⚙️Settings", width=35, font=("Consolas", 12), command=open_settings)
    open_settings_.place(x=10, y=40)

    # clock_in_start = tk.Label(startmenu, font=("Consolas", 14), bg="#222233", fg="white")
    # clock_in_start.place(x=20, y=250)

    open_weather = tk.Button(startmenu, text="🌦️Weather", width=35, font=("Consolas", 12), command=weather)
    open_weather.place(x=10, y=70)

    open_clock_ = tk.Button(startmenu, text="🕑Clock", width=35, font=("Consolas", 12), command=open_clock)
    open_clock_.place(x=10, y=100)

    open_taskmgr_ = tk.Button(startmenu, text="📟Task Manager", width=35, font=("Consolas", 12), command=open_taskmgr)
    open_taskmgr_.place(x=10, y=130)

    open_timer_ = tk.Button(startmenu, text="⏰Timer", width=35, font=("Consolas", 12), command=open_timer)
    open_timer_.place(x=10, y=160)

    open_browser_ = tk.Button(startmenu, text="🌏Browser", width=35, font=("Consolas", 12), command=open_browser)
    open_browser_.place(x=10, y=190)

    open_qjrnetwork_ = tk.Button(startmenu, text="📡QJRnetwork", width=35, font=("Consolas", 12), command=QJRnetwork)
    open_qjrnetwork_.place(x=10, y=220)

    open_calendar = tk.Button(startmenu, text="📆Calendar", width=35, font=("Consolas", 12), command=QJRnetwork)
    open_calendar.place(x=10, y=250)

    shutdown = tk.Button(startmenu, text="🔻Shutdown", width=12, font=("Consolas", 12), command=exit)
    shutdown.place(x=163, y=285)
    #
    # def update_time():
    #     current_time = time.strftime("%H:%M:%S")
    #     clock_label.config(text=current_time)
    #     root.after(1000, update_time)
    #
    # update_time()

# Dock: контейнер-панель внизу
dock_frame = tk.Frame(root, bg="#222233")
dock_height = 50
canvas.create_window(WIDTH//2, HEIGHT - dock_height//2, window=dock_frame, width=WIDTH, height=dock_height)

# option_frame = tk.Frame(root, bg="#222233")
# option_height = 25
# canvas.create_window(WIDTH//2, 12, window=option_frame, width=WIDTH, height=option_height)

# Кнопки в Dock
# apps = [
#     ("🛌 Ligvo", open_ligvo),
#     ("📦 Sphere", open_sphere),
#     ("💻 Post", open_post),
#     ("🖲️ Core", open_core),
#     ("⚙️ Settings", open_settings)
# ]

apps = [
    ("➡️", open_start),
    ("📂File Manager", open_explorer),
    ("⚙️Settings", open_settings),
    ("ℹ️About", open_info),
]



for name, command in apps:
    btn = tk.Button(dock_frame, text=name, font=("Consolas", 12), width=10, command=command)
    btn.pack(side="left", padx=10, pady=10)

def update_date():
    current_date = time.strftime("%d-%m-%Y")
    date_label.config(text=current_date)
    root.after(60000, update_date)  # оновлення щохвилини

# Годинник у нижньому правому кутку
clock_label = tk.Label(dock_frame, font=("Consolas", 14), bg="#222233", fg="white")
clock_label.pack(side="right", padx=15)

date_label = tk.Label(dock_frame, font=("Consolas", 14), bg="#222233", fg="white")
date_label.pack(side="right", padx=10)

# Отримання IP-даних

response = requests.get("https://ipinfo.io/json").json()
city = response.get("city", "Unknown")
country = response.get("country", "Unknown")
ip = response.get("ip", "Unknown")

# BTC Price

def update_btc():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    data = response.json()
    price = data.get("price")
    price = float(price) if price else None
    btc_label.configure(text=f"BTC: {price}")
    root.after(1000, update_btc)

btc_label = tk.Label(root, text="", font=("Consolas", 13), bg="#222233", fg="white")
btc_label.place(x=WIDTH - 365, y = HEIGHT - 35, anchor="ne")
# btc_label.place(x=360, y=340)

url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
response = requests.get(url)
data = response.json()
price = data.get("price")
price = float(price) if price else None
btc_label.configure(text=f"BTC: {price}")
root.after(1000, update_btc)


# ip_label = tk.Label(root, text="Завантаження IP-даних...", font=("Consolas", 13))
# ip_label.place(side="right", padx=1)

# ip_label.configure(text=f"IP: {ip}\nМісто: {city}\nКраїна: {country}")
# ip_label = tk.Label(root,text=f"IP: {ip}\nМісто: {city}\nКраїна: {country}", font=("Consolas", 13))
# ip_label.pack(side="right", padx=5)

ip_label = tk.Label(root, text=f"IP: {ip}\nМісто: {city}\nКраїна: {country}", font=("Consolas", 13), bg="#222233", fg="white")
ip_label.place(x=WIDTH - 200, y=HEIGHT - 50, anchor="ne")

# Процесор + оновлення часу
processor_info = platform.processor()

def update_time():
    current_time = time.strftime("%H:%M:%S")
    clock_label.config(text=current_time)
    root.after(1000, update_time)

# def update_date():
#     current_date = time.strftime("%d-%m-%Y")
#     date_label.config(text=current_date)
#     root.after(60000, update_date)  # оновлення щохвилини

update_date()
update_time()
root.mainloop()
