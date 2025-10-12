import tkinter as tk
import random
import time
import threading

# ------------------ Config ------------------
BG = "#1b1530"          # deep purple background
SPHERE_COLORS = ["#241035", "#2c1540", "#34194a", "#3b1d56"]
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
    ("📁", "Проводник", "explorer"),
    ("⚙️", "Настройки", "settings"),
    ("✉️", "Почта", "mail"),
]

DESKTOP_ICONS = [
    ("🔢", "Калькулятор", "calculator"),
    ("🗒️", "Заметки", "notes"),
    ("⚙️", "Настройки", "settings"),
]

ICON_FONT = ("Segoe UI Emoji", 30)
TITLE_FONT = ("Segoe UI", 10, "bold")
TEXT_FONT = ("Segoe UI", 10)

# ------------------ Root ------------------
root = tk.Tk()
root.title("Flolower OS v7 (restored)")
root.attributes("-fullscreen", True)
root.configure(bg=BG)

SW = root.winfo_screenwidth()
SH = root.winfo_screenheight()

# ------------------ Background canvas with spheres ------------------
canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
canvas.place(relwidth=1, relheight=1)

spheres = []
for _ in range(26):
    r = random.randint(40, 140)
    x = random.randint(0, SW - r)
    y = random.randint(0, SH - r)
    col = random.choice(SPHERE_COLORS)
    oid = canvas.create_oval(x, y, x + r, y + r, fill=col, outline="")
    vx = random.uniform(-0.45, 0.45)
    vy = random.uniform(-0.25, 0.25)
    spheres.append({"id": oid, "x": x, "y": y, "r": r, "vx": vx, "vy": vy})

def animate_spheres():
    for s in spheres:
        s["x"] += s["vx"]
        s["y"] += s["vy"]
        if s["x"] < -s["r"] or s["x"] > SW:
            s["vx"] *= -1
        if s["y"] < -s["r"] or s["y"] > SH:
            s["vy"] *= -1
        canvas.coords(s["id"], s["x"], s["y"], s["x"] + s["r"], s["y"] + s["r"])
    root.after(50, animate_spheres)

animate_spheres()

# ensure canvas is bottom
canvas.tag_lower("all")

# ------------------ Desktop frame ------------------
desktop = tk.Frame(root, bg=BG)
desktop.place(relwidth=1, relheight=1)

# ------------------ Taskbar ------------------
TASK_H = 56
taskbar = tk.Frame(root, bg=TASKBAR_BG, height=TASK_H)
taskbar.pack(side="bottom", fill="x")

# left area start button, center area flexible, right area time
start_btn = tk.Button(taskbar, text="⊞ Пуск", bg=MENU_BG, fg=TEXT, font=TEXT_FONT, bd=0, padx=12, pady=6)
start_btn.pack(side="left", padx=12, pady=6)

task_buttons_frame = tk.Frame(taskbar, bg=TASKBAR_BG)
task_buttons_frame.pack(side="left", padx=8, pady=6)

time_lbl = tk.Label(taskbar, text=time.strftime("%H:%M"), bg=TASKBAR_BG, fg=TEXT, font=TEXT_FONT)
time_lbl.pack(side="right", padx=12)

def tick_time():
    time_lbl.config(text=time.strftime("%H:%M"))
    root.after(1000, tick_time)
tick_time()

# keep track of minimized windows to add taskbar buttons
task_buttons = {}  # win -> button

# ------------------ Start menu (centered, slide + fade simulation) ------------------
MENU_W = min(520, int(SW * 0.5))
MENU_H = min(540, int(SH * 0.6))
MENU_X = (SW - MENU_W) // 2
MENU_Y_SHOWN = (SH - MENU_H) // 2
MENU_Y_HIDDEN = SH + 20

start_menu = tk.Frame(root, bg=MENU_BG, bd=0)
start_menu.place(x=MENU_X, y=MENU_Y_HIDDEN, width=MENU_W, height=MENU_H)
menu_visible = False

# Search box
search_var = tk.StringVar()
search_entry = tk.Entry(start_menu, textvariable=search_var, bg="#2b2334", fg=TEXT, bd=0, font=TEXT_FONT, insertbackground=TEXT)
search_entry.place(x=16, y=16, width=MENU_W - 32, height=36)

# Apps area
apps_frame = tk.Frame(start_menu, bg=MENU_BG)
apps_frame.place(x=16, y=72, width=MENU_W - 32, height=MENU_H - 88)

app_widgets = []  # (button widget, app tuple)

def on_start_app(app_key, app_title):
    toggle_menu(False)
    open_app_window(app_key, app_title)

# populate apps in menu with icons
for emoji, title, key in APP_LIST:
    row = tk.Frame(apps_frame, bg=MENU_ITEM, height=44)
    row.pack(fill="x", pady=6)
    ico = tk.Label(row, text=emoji, bg=MENU_ITEM, fg=TEXT, font=ICON_FONT)
    ico.pack(side="left", padx=(8,10))
    lbl = tk.Label(row, text=title, bg=MENU_ITEM, fg=TEXT, font=TEXT_FONT, anchor="w")
    lbl.pack(side="left", fill="x", expand=True)
    # click opens app
    row.bind("<Button-1>", lambda e, k=key, t=title: on_start_app(k, t))
    ico.bind("<Button-1>", lambda e, k=key, t=title: on_start_app(k, t))
    lbl.bind("<Button-1>", lambda e, k=key, t=title: on_start_app(k, t))
    app_widgets.append((row, title))

# search filtering
def refresh_app_list(*_):
    q = search_var.get().lower().strip()
    for w, title in app_widgets:
        if not q or q in title.lower():
            w.pack_configure(fill="x", pady=6)
        else:
            w.pack_forget()
search_var.trace_add("write", refresh_app_list)

# show/hide animations (simple slide)
def show_menu():
    global menu_visible
    if menu_visible: return
    menu_visible = True
    start_menu.lift()
    steps = 12
    start_y = MENU_Y_HIDDEN
    dy = (MENU_Y_SHOWN - start_y) / steps
    def step(i=0):
        if i <= steps:
            y = int(start_y + dy * i)
            start_menu.place(y=y)
            root.after(12, lambda: step(i+1))
        else:
            start_menu.place(y=MENU_Y_SHOWN)
            search_entry.focus_set()
    step()

def hide_menu():
    global menu_visible
    if not menu_visible: return
    menu_visible = False
    steps = 10
    start_y = MENU_Y_SHOWN
    dy = (MENU_Y_HIDDEN - start_y) / steps
    def step(i=0):
        if i <= steps:
            y = int(start_y + dy * i)
            start_menu.place(y=y)
            root.after(12, lambda: step(i+1))
        else:
            start_menu.place(y=MENU_Y_HIDDEN)
    step()

def toggle_menu(force=None):
    if force is None:
        if menu_visible: hide_menu()
        else: show_menu()
    elif force:
        show_menu()
    else:
        hide_menu()

start_btn.config(command=toggle_menu)

# close menu when clicking outside
def on_global_click(e):
    if menu_visible:
        mx, my = start_menu.winfo_rootx(), start_menu.winfo_rooty()
        mw, mh = start_menu.winfo_width(), start_menu.winfo_height()
        if not (mx <= e.x_root <= mx + mw and my <= e.y_root <= my + mh):
            hide_menu()
root.bind("<Button-1>", on_global_click, add="+")

root.bind("<Key>", lambda e: toggle_menu() if e.keysym in ("Super_L","Super_R") else None)
root.bind("<Escape>", lambda e: hide_menu())

# ------------------ App window management ------------------
open_windows = []  # list of window dicts

def restore_from_task(win_id):
    # restore hidden window by id
    for item in open_windows:
        if item["id"] == win_id:
            top = item["win"]
            try:
                top.deiconify()
            except:
                pass
            # bring to front
            top.lift()
            # remove task button
            btn = task_buttons.pop(top, None)
            if btn:
                btn.destroy()
            break

def create_task_button(win, title):
    # small button on taskbar to restore minimized window
    btn = tk.Button(task_buttons_frame, text=title, bg="#2a2233", fg=TEXT, bd=0, padx=8, pady=4,
                    command=lambda w=win: (w.deiconify(), btn.destroy(), task_buttons.pop(win, None)))
    btn.pack(side="left", padx=4)
    task_buttons[win] = btn

def open_app_window(key, title):
    # create Toplevel with custom titlebar + controls
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.configure(bg=WINDOW_BG)
    target_w = int(SW * 0.56)
    target_h = int(SH * 0.62)
    cx = (SW - target_w)//2
    cy = (SH - target_h)//2

    # shadow rectangle on canvas
    shadow = canvas.create_rectangle(cx+10, cy+10, cx+10+target_w, cy+10+target_h, fill="#000000", outline="", stipple="gray25")

    # initial small placement
    start_w, start_h = max(60, target_w//10), max(40, target_h//10)
    sx = cx + (target_w - start_w)//2
    sy = cy + (target_h - start_h)//2
    win.geometry(f"{start_w}x{start_h}+{sx}+{sy}")

    # title bar
    title_bar = tk.Frame(win, bg=TITLE_BG, height=36)
    title_bar.pack(fill="x")
    title_lbl = tk.Label(title_bar, text=title, bg=TITLE_BG, fg=TEXT, font=TITLE_FONT)
    title_lbl.pack(side="left", padx=8)

    # control buttons
    ctrls = tk.Frame(title_bar, bg=TITLE_BG)
    ctrls.pack(side="right", padx=6)
    def close_win():
        # remove from lists and destroy
        try:
            canvas.delete(shadow)
        except: pass
        try:
            btn = task_buttons.pop(win)
            if btn: btn.destroy()
        except: pass
        try:
            win.destroy()
        except: pass
    def minimize_win():
        try:
            win.withdraw()
            create_task_button(win, title)
        except: pass
    # maximize toggle
    win.is_max = False
    win.normal_geom = None
    def toggle_max():
        try:
            if not win.is_max:
                # save normal
                g = win.geometry().split("+")
                wh = g[0].split("x")
                win.normal_geom = (int(g[1]), int(g[2]), int(wh[0]), int(wh[1]))
                win.is_max = True
                win.geometry(f"{SW}x{SH}+0+0")
                canvas.coords(shadow, 8, 8, SW-8, SH-8)
            else:
                win.is_max = False
                nx, ny, nw, nh = win.normal_geom
                win.geometry(f"{nw}x{nh}+{nx}+{ny}")
                canvas.coords(shadow, nx+10, ny+10, nx+10+nw, ny+10+nh)
        except Exception:
            pass

    b_min = tk.Button(ctrls, text="🗕", bg=TITLE_BG, fg=TEXT, bd=0, command=minimize_win)
    b_max = tk.Button(ctrls, text="🗖", bg=TITLE_BG, fg=TEXT, bd=0, command=toggle_max)
    b_close = tk.Button(ctrls, text="✕", bg=TITLE_BG, fg=TEXT, bd=0, command=close_win)
    b_min.pack(side="left", padx=4); b_max.pack(side="left", padx=4); b_close.pack(side="left", padx=4)

    # content area
    content = tk.Frame(win, bg=WINDOW_BG)
    content.pack(expand=True, fill="both")

    # fill content by key
    if key == "calculator":
        build_calculator(content)
    elif key == "notes":
        build_notes(content)
    elif key == "browser":
        build_browser(content)
    else:
        tk.Label(content, text=f"{title} — демо", bg=WINDOW_BG, fg=TEXT, font=TEXT_FONT).pack(padx=12, pady=12)

    # animate open (scale + fade)
    try:
        win.attributes("-alpha", 0.0)
        can_alpha = True
    except:
        can_alpha = False

    steps = 16
    def anim_open():
        for i in range(steps+1):
            t = i/steps
            w = int(start_w + (target_w - start_w) * t)
            h = int(start_h + (target_h - start_h) * t)
            x = cx + (target_w - w)//2
            y = cy + (target_h - h)//2
            try:
                win.geometry(f"{w}x{h}+{x}+{y}")
                if can_alpha:
                    win.attributes("-alpha", t)
                canvas.coords(shadow, x+10, y+10, x+10+w, y+10+h)
            except:
                pass
            time.sleep(0.009)
        try:
            win.geometry(f"{target_w}x{target_h}+{cx}+{cy}")
            if can_alpha:
                win.attributes("-alpha", 1.0)
        except:
            pass

    t = threading.Thread(target=anim_open, daemon=True)
    t.start()

    # dragging titlebar
    def start_move(e):
        win._drag_x = e.x
        win._drag_y = e.y
    def do_move(e):
        try:
            geo = win.geometry().split("+")
            wh = geo[0].split("x")
            cur_x = int(geo[1]); cur_y = int(geo[2])
            nx = cur_x + (e.x - win._drag_x)
            ny = cur_y + (e.y - win._drag_y)
            win.geometry(f"{wh[0]}x{wh[1]}+{nx}+{ny}")
            canvas.coords(shadow, nx+10, ny+10, nx+10+int(wh[0]), ny+10+int(wh[1]))
        except:
            pass
    title_bar.bind("<Button-1>", start_move)
    title_bar.bind("<B1-Motion>", do_move)

    # record
    open_windows.append({"win": win, "key": key, "title": title, "id": id(win)})

# ------------------ Basic app content builders ------------------
def build_calculator(parent):
    expr = tk.StringVar()
    e = tk.Entry(parent, textvariable=expr, font=("Consolas", 18), justify="right", bg="#1b1820", fg="white", bd=0, insertbackground="white")
    e.pack(fill="x", padx=12, pady=12, ipady=6)
    grid = tk.Frame(parent, bg=WINDOW_BG)
    grid.pack(expand=True, fill="both", padx=12, pady=(0,12))
    buttons = [
        "7","8","9","/",
        "4","5","6","*",
        "1","2","3","-",
        "0",".","=","+"
    ]
    def press(ch):
        if ch == "=":
            try:
                expr.set(str(eval(expr.get())))
            except:
                expr.set("Err")
        else:
            expr.set(expr.get() + ch)
    for i,ch in enumerate(buttons):
        b = tk.Button(grid, text=ch, command=lambda c=ch: press(c), bg="#2b2430", fg="white", bd=0, font=("Segoe UI", 14))
        b.grid(row=i//4, column=i%4, sticky="nsew", padx=6, pady=6)
    for i in range(4):
        grid.columnconfigure(i, weight=1)
        grid.rowconfigure(i, weight=1)

def build_notes(parent):
    t = tk.Text(parent, bg="#1b1820", fg="white", bd=0)
    t.insert("1.0", "Новая заметка...\n")
    t.pack(fill="both", expand=True, padx=12, pady=12)

def build_browser(parent):
    tk.Label(parent, text="Браузер (демо)", bg=WINDOW_BG, fg=TEXT).pack(anchor="nw", padx=12, pady=12)
    tk.Text(parent, bg="#1b1820", fg="white", bd=0).pack(fill="both", expand=True, padx=12, pady=(0,12))

# ------------------ Desktop icons creation ------------------
ICON_X = 64
ICON_Y = 84
ICON_GAP = 110
def create_desktop_icon(x, y, emoji, title, key):
    f = tk.Frame(desktop, bg=BG)
    f.place(x=x, y=y)
    btn = tk.Button(f, text=emoji, font=ICON_FONT, bg=WINDOW_BG, fg=TEXT, bd=0,
                    activebackground="#3a2d44", command=lambda: open_app_window(key, title))
    btn.pack()
    lbl = tk.Label(f, text=title, bg=BG, fg=TEXT, font=TEXT_FONT)
    lbl.pack(pady=(6,0))
    # double click also opens
    btn.bind("<Double-Button-1>", lambda e: open_app_window(key, title))
    lbl.bind("<Double-Button-1>", lambda e: open_app_window(key, title))

for i, (emoji, title, key) in enumerate(DESKTOP_ICONS):
    create_desktop_icon(ICON_X, ICON_Y + i * ICON_GAP, emoji, title, key)

# ------------------ Start conditions ------------------
# hide menu initially
start_menu.place(y=MENU_Y_HIDDEN)

# ------------------ Win key binding and start button already wired ------------------
# already wired earlier with start_btn.config

# ------------------ Keep canvas below widgets ------------------
canvas.tag_lower("all")

# ------------------ Start mainloop ------------------
root.mainloop()

