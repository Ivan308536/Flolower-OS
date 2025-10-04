import tkinter as tk
import random
import time

# ---------------- Настройки ----------------
root = tk.Tk()
root.title("Flolower OS v6")
root.attributes("-fullscreen", True)

SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()

TASKBAR_H = 56
START_MENU_H = 420
START_MENU_W = 300

# Цвета
BG = "#222222"
TASKBAR_BG = "#2f2f2f"
WINDOW_BG = "#2b2b2b"
TITLE_BG = "#3b3b3b"
TITLE_FG = "white"
ACCENT = "#5a9bd4"
CLOSE_RED = "#cc4444"
BTN_GRAY = "#444444"

root.configure(bg=BG)

canvas = tk.Canvas(root, width=SCREEN_W, height=SCREEN_H, bg=BG, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# ---------------- Фоновые сферы ----------------
sphere_colors = ["#111111", "#333333", "#444444"]
spheres = []
for _ in range(40):
    r = random.randint(20, 70)
    x = random.randint(0, SCREEN_W - r)
    y = random.randint(0, SCREEN_H - r - TASKBAR_H - 20)
    color = random.choice(sphere_colors)
    dx = random.choice([-1, 1]) * random.uniform(0.3, 1.2)
    dy = random.choice([-1, 1]) * random.uniform(0.3, 1.2)
    oid = canvas.create_oval(x, y, x + r, y + r, fill=color, outline="")
    spheres.append({"id": oid, "x": x, "y": y, "r": r, "dx": dx, "dy": dy})

WORKSPACE_H = SCREEN_H - TASKBAR_H

def move_spheres():
    for s in spheres:
        s["x"] += s["dx"]
        s["y"] += s["dy"]
        if s["x"] <= 0 or s["x"] + s["r"] >= SCREEN_W:
            s["dx"] *= -1
        if s["y"] <= 0 or s["y"] + s["r"] >= WORKSPACE_H:
            s["dy"] *= -1
        canvas.coords(s["id"], s["x"], s["y"], s["x"] + s["r"], s["y"] + s["r"])
    root.after(30, move_spheres)
move_spheres()

# ---------------- Панель задач ----------------
canvas.create_rectangle(0, SCREEN_H - TASKBAR_H, SCREEN_W, SCREEN_H, fill=TASKBAR_BG, outline="")

taskbar_frame = tk.Frame(root, bg=TASKBAR_BG)
canvas.create_window(0, SCREEN_H - TASKBAR_H, anchor="nw", window=taskbar_frame, width=SCREEN_W, height=TASKBAR_H)

# Start button with hover effect
def start_btn_enter(e):
    start_btn.config(bg="#3a3a3a")
def start_btn_leave(e):
    start_btn.config(bg=TASKBAR_BG)

start_btn = tk.Button(taskbar_frame, text="☰ Пуск", bg=TASKBAR_BG, fg="white", bd=0, relief="flat", padx=10)
start_btn.pack(side="left", padx=(8, 6), pady=6)
start_btn.bind("<Enter>", start_btn_enter)
start_btn.bind("<Leave>", start_btn_leave)

task_buttons_frame = tk.Frame(taskbar_frame, bg=TASKBAR_BG)
task_buttons_frame.pack(side="left", padx=8, pady=6, expand=True, fill="y")

right_frame = tk.Frame(taskbar_frame, bg=TASKBAR_BG)
right_frame.pack(side="right", padx=8)
clock_label = tk.Label(right_frame, text="", bg=TASKBAR_BG, fg="white", font=("Segoe UI", 12))
clock_label.pack(side="right", padx=(8, 0))
fs_btn = tk.Button(right_frame, text="Esc → Exit FS", bg=TASKBAR_BG, fg="white", bd=0, relief="flat")
fs_btn.pack(side="right", padx=6)

def update_clock():
    clock_label.config(text=time.strftime("%H:%M:%S"))
    root.after(1000, update_clock)
update_clock()

def exit_fullscreen(event=None):
    root.attributes("-fullscreen", False)
root.bind("<Escape>", exit_fullscreen)
fs_btn.config(command=lambda: exit_fullscreen())

# ---------------- Start Menu (toggle + auto-hide) ----------------
start_menu = tk.Frame(root, bg="#2d2d2d", width=START_MENU_W, height=START_MENU_H)
# initially hidden (placed off-screen)
start_menu.place(x=0, y=SCREEN_H, anchor="sw")

def show_start_menu():
    start_menu.place(x=0, y=SCREEN_H - TASKBAR_H, anchor="sw")

def hide_start_menu():
    start_menu.place(x=0, y=SCREEN_H, anchor="sw")

def toggle_start():
    if start_menu.winfo_y() >= SCREEN_H:
        show_start_menu()
    else:
        hide_start_menu()

start_btn.config(command=toggle_start)

# close start_menu when clicking outside
def global_click(event):
    # if start menu visible and click not inside it or start_btn -> hide
    if start_menu.winfo_ismapped():
        x_root, y_root = event.x_root, event.y_root
        sx = start_menu.winfo_rootx()
        sy = start_menu.winfo_rooty()
        sw = start_menu.winfo_width()
        sh = start_menu.winfo_height()
        # start_btn bbox
        bx = start_btn.winfo_rootx()
        by = start_btn.winfo_rooty()
        bw = start_btn.winfo_width()
        bh = start_btn.winfo_height()
        inside_start = (sx <= x_root <= sx+sw and sy <= y_root <= sy+sh)
        inside_startbtn = (bx <= x_root <= bx+bw and by <= y_root <= by+bh)
        if not inside_start and not inside_startbtn:
            hide_start_menu()

# bind global clicks (add so it doesn't replace other bindings)
root.bind("<Button-1>", global_click, add="+")

# ---------------- Менеджер окон ----------------
EDGE_SNAP_MARGIN = 40
TOP_SNAP_MARGIN = 40
DRAG_TO_TASKBAR_MARGIN = 20

class AppWindow:
    id_counter = 0
    def __init__(self, manager, title="Window", w=420, h=300, x=100, y=100, app_type=None):
        self.manager = manager
        self.title = title
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.app_type = app_type
        self.minimized = False
        self.maximized = False
        self.prev_geom = None
        AppWindow.id_counter += 1

        self.frame = tk.Frame(root, bg=WINDOW_BG, bd=0, highlightthickness=0)
        self.titlebar = tk.Frame(self.frame, bg=TITLE_BG, height=30)
        self.titlebar.pack(side="top", fill="x")

        self.title_lbl = tk.Label(self.titlebar, text=self.title, bg=TITLE_BG, fg=TITLE_FG)
        self.title_lbl.pack(side="left", padx=8)

        # правильные цвета кнопок управления
        self.btn_close = tk.Button(self.titlebar, text="✕", bg=CLOSE_RED, fg="white",
                                   bd=0, relief="flat", width=3, command=self.close)
        self.btn_min = tk.Button(self.titlebar, text="▁", bg=BTN_GRAY, fg="white",
                                 bd=0, relief="flat", width=3, command=self.minimize)
        self.btn_max = tk.Button(self.titlebar, text="▢", bg=BTN_GRAY, fg="white",
                                 bd=0, relief="flat", width=3, command=self.maximize_restore)
        self.btn_close.pack(side="right", padx=1)
        self.btn_max.pack(side="right", padx=1)
        self.btn_min.pack(side="right", padx=1)

        self.content = tk.Frame(self.frame, bg=WINDOW_BG)
        self.content.pack(fill="both", expand=True)

        # attach app content
        if app_type == "calculator":
            build_calculator(self.content)
        elif app_type == "notes":
            build_text_app(self.content)
        elif app_type == "browser":
            build_browser_app(self.content)

        self.canvas_window = canvas.create_window(self.x, self.y, anchor="nw", window=self.frame, width=self.w, height=self.h)

        # move bindings
        self.titlebar.bind("<Button-1>", self.start_move)
        self.titlebar.bind("<B1-Motion>", self.do_move)
        self.titlebar.bind("<ButtonRelease-1>", self.end_move)
        self.title_lbl.bind("<Button-1>", self.start_move)
        self.title_lbl.bind("<B1-Motion>", self.do_move)
        self.title_lbl.bind("<ButtonRelease-1>", self.end_move)

        self.frame.bind("<Button-1>", lambda e: self.manager.focus_window(self))
        self.titlebar.bind("<Double-Button-1>", lambda e: self.maximize_restore())

        self.task_btn = tk.Button(task_buttons_frame, text=self.title, bg=TASKBAR_BG, fg="white", bd=0, relief="flat", command=self.toggle_minimize)
        self.task_btn.pack(side="left", padx=4, ipadx=6)

        self.manager.register(self)

    def start_move(self, event):
        self.manager.focus_window(self)
        self._move_start_x = event.x
        self._move_start_y = event.y

    def do_move(self, event):
        dx = event.x - self._move_start_x
        dy = event.y - self._move_start_y
        cur = canvas.coords(self.canvas_window)
        if cur:
            nx = cur[0] + dx
            ny = cur[1] + dy
            nx = max(0, min(nx, SCREEN_W - 60))
            ny = max(0, min(ny, WORKSPACE_H - 40))
            canvas.coords(self.canvas_window, nx, ny)
            bottom_of_win = ny + self.h
            if bottom_of_win >= SCREEN_H - (TASKBAR_H - DRAG_TO_TASKBAR_MARGIN):
                highlight_taskbar(True)
            else:
                highlight_taskbar(False)

    def end_move(self, event):
        cur = canvas.coords(self.canvas_window)
        if cur:
            nx, ny = int(cur[0]), int(cur[1])
            if ny <= TOP_SNAP_MARGIN:
                self.maximize_to_workspace()
            elif nx <= EDGE_SNAP_MARGIN:
                self.snap_left()
            elif nx + self.w >= SCREEN_W - EDGE_SNAP_MARGIN:
                self.snap_right()
            else:
                bottom_of_win = ny + self.h
                if bottom_of_win >= SCREEN_H - (TASKBAR_H - DRAG_TO_TASKBAR_MARGIN):
                    self.minimize()
                    highlight_taskbar(False)
            self.x, self.y = nx, ny

    def close(self):
        self.manager.unregister(self)
        canvas.delete(self.canvas_window)
        self.frame.destroy()
        self.task_btn.destroy()

    def minimize(self):
        if not self.minimized:
            self.minimized = True
            canvas.itemconfigure(self.canvas_window, state="hidden")
            self.task_btn.config(relief="sunken")
        else:
            self.minimized = False
            canvas.itemconfigure(self.canvas_window, state="normal")
            self.task_btn.config(relief="flat")
            self.manager.focus_window(self)

    def toggle_minimize(self):
        self.minimize()

    def maximize_restore(self):
        if not self.maximized:
            cur = canvas.coords(self.canvas_window)
            width = canvas.itemcget(self.canvas_window, "width")
            height = canvas.itemcget(self.canvas_window, "height")
            try:
                w = int(float(width)); h = int(float(height))
            except:
                w, h = self.w, self.h
            self.prev_geom = (int(cur[0]), int(cur[1]), w, h)
            canvas.coords(self.canvas_window, 0, 0)
            canvas.itemconfigure(self.canvas_window, width=SCREEN_W, height=WORKSPACE_H)
            self.maximized = True
        else:
            if self.prev_geom:
                x, y, w, h = self.prev_geom
                canvas.coords(self.canvas_window, x, y)
                canvas.itemconfigure(self.canvas_window, width=w, height=h)
            self.maximized = False

    def maximize_to_workspace(self):
        canvas.coords(self.canvas_window, 0, 0)
        canvas.itemconfigure(self.canvas_window, width=SCREEN_W, height=WORKSPACE_H)
        self.maximized = True

    def snap_left(self):
        canvas.coords(self.canvas_window, 0, 0)
        canvas.itemconfigure(self.canvas_window, width=SCREEN_W//2, height=WORKSPACE_H)
        self.maximized = False

    def snap_right(self):
        canvas.coords(self.canvas_window, SCREEN_W//2, 0)
        canvas.itemconfigure(self.canvas_window, width=SCREEN_W//2, height=WORKSPACE_H)
        self.maximized = False

    def focus(self):
        canvas.lift(self.canvas_window)
        self.titlebar.config(bg=ACCENT)
        self.title_lbl.config(bg=ACCENT)
        self.task_btn.config(bg="#3f3f3f")
        # when focused, accent buttons except close
        self.btn_min.config(bg=BTN_GRAY)
        self.btn_max.config(bg=BTN_GRAY)
        self.btn_close.config(bg=CLOSE_RED)

    def unfocus(self):
        self.titlebar.config(bg=TITLE_BG)
        self.title_lbl.config(bg=TITLE_BG)
        self.task_btn.config(bg=TASKBAR_BG)
        self.btn_min.config(bg=BTN_GRAY)
        self.btn_max.config(bg=BTN_GRAY)
        self.btn_close.config(bg=CLOSE_RED)

class WindowManager:
    def __init__(self):
        self.windows = []
    def register(self, w):
        self.windows.append(w)
        self.focus_window(w)
    def unregister(self, w):
        if w in self.windows:
            self.windows.remove(w)
    def focus_window(self, w):
        for win in self.windows:
            if win is not w:
                win.unfocus()
        if w in self.windows:
            self.windows.remove(w)
        self.windows.append(w)
        w.focus()

manager = WindowManager()

# ---------------- Подсветка панели задач ----------------
def highlight_taskbar(on=True):
    if on:
        canvas.itemconfig(taskbar_highlight, state="normal")
    else:
        canvas.itemconfig(taskbar_highlight, state="hidden")

taskbar_highlight = canvas.create_rectangle(
    0, SCREEN_H - TASKBAR_H, SCREEN_W, SCREEN_H,
    fill="#ffffff", stipple="gray25", outline="", state="hidden"
)

# ---------------- Приложения ----------------
def build_calculator(parent):
    display_var = tk.StringVar()
    entry = tk.Entry(parent, textvariable=display_var, font=("Segoe UI", 18), bg="#1f1f1f", fg="white", justify="right", bd=0)
    entry.pack(fill="x", padx=8, pady=8, ipady=8)

    def press(ch):
        display_var.set(display_var.get() + str(ch))
    def clear():
        display_var.set("")
    def calculate():
        try:
            res = str(eval(display_var.get()))
            display_var.set(res)
        except:
            display_var.set("Err")

    btns = [
        ("7","8","9","/"),
        ("4","5","6","*"),
        ("1","2","3","-"),
        ("0",".","=","+")
    ]
    grid = tk.Frame(parent, bg=WINDOW_BG)
    grid.pack(expand=True, fill="both", padx=6, pady=6)
    for r, row in enumerate(btns):
        for c, ch in enumerate(row):
            if ch == "=":
                cmd = calculate
            else:
                cmd = lambda x=ch: press(x)
            b = tk.Button(grid, text=ch, command=cmd, bg="#3a3a3a", fg="white", font=("Segoe UI", 14), bd=0)
            b.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
    clr = tk.Button(parent, text="C", command=clear, bg="#b34a4a", fg="white", bd=0)
    clr.pack(fill="x", padx=8, pady=(0,8))
    for i in range(4):
        grid.columnconfigure(i, weight=1)
    for i in range(4):
        grid.rowconfigure(i, weight=1)

def build_text_app(parent):
    t = tk.Text(parent, bg="#1e1e1e", fg="white")
    t.insert("1.0", "Приложение заметки. Перетащи окно, разверни, минимизируй.")
    t.pack(expand=True, fill="both", padx=8, pady=8)

def build_browser_app(parent):
    lbl = tk.Label(parent, text="Прототип браузера (демо)", fg="white", bg=WINDOW_BG, font=("Segoe UI", 14))
    lbl.pack(pady=20)
    t = tk.Text(parent, bg="#1e1e1e", fg="white")
    t.insert("1.0", "Здесь мог бы быть встроенный браузер :)")
    t.pack(expand=True, fill="both", padx=8, pady=8)

# ---------------- Кнопки в меню Пуск ----------------
def launch_calc(): AppWindow(manager, title="Калькулятор", w=420, h=360, x=200, y=120, app_type="calculator")
def launch_notes(): AppWindow(manager, title="Заметки", w=500, h=400, x=220, y=140, app_type="notes")
def launch_browser(): AppWindow(manager, title="Браузер", w=640, h=480, x=250, y=160, app_type="browser")

tk.Button(start_menu, text="Калькулятор", command=launch_calc, bg="#3a3a3a", fg="white", relief="flat").pack(fill="x", padx=10, pady=5)
tk.Button(start_menu, text="Заметки", command=launch_notes, bg="#3a3a3a", fg="white", relief="flat").pack(fill="x", padx=10, pady=5)
tk.Button(start_menu, text="Браузер", command=launch_browser, bg="#3a3a3a", fg="white", relief="flat").pack(fill="x", padx=10, pady=5)

# ---------------- Рабочий стол с ярлыками ----------------
desktop_icons = []
def create_desktop_icon(x, y, text, app_type):
    frame = tk.Frame(root, bg="", bd=0, highlightthickness=0)
    icon = tk.Label(frame, text="🗂", font=("Segoe UI Emoji", 32), bg=BG)
    lbl = tk.Label(frame, text=text, fg="white", bg=BG, font=("Segoe UI", 10))
    icon.pack()
    lbl.pack()
    win = canvas.create_window(x, y, anchor="nw", window=frame)

    def launch(event=None):
        AppWindow(manager, title=text, w=420, h=360, x=200, y=120, app_type=app_type)

    frame.bind("<Double-Button-1>", launch)
    icon.bind("<Double-Button-1>", launch)
    lbl.bind("<Double-Button-1>", launch)

    desktop_icons.append(win)

create_desktop_icon(40, 40, "Калькулятор", "calculator")
create_desktop_icon(40, 140, "Заметки", "notes")
create_desktop_icon(40, 240, "Браузер", "browser")

# ---------------- Запуск (демо окна) ----------------
# create a couple demo windows so you see behavior
AppWindow(manager, title="Проводник", w=520, h=360, x=80, y=120, app_type="notes")
AppWindow(manager, title="Почтовый клиент", w=460, h=320, x=520, y=200, app_type="browser")

# ---------------- Запуск цикла Tk ----------------
root.mainloop()
