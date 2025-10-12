import tkinter as tk
import random
import time
import threading

# ---------------- Настройки ----------------
BG_COLOR = "#1f1f27"
SPHERE_COLOR = "#292935"
MENU_BG = "#232430"
MENU_ITEM = "#2b2d35"
TASKBAR_BG = "#17171b"
WINDOW_BG = "#2c2c38"
TITLE_BG = "#24232a"
TEXT_COLOR = "white"

root = tk.Tk()
root.title("Flolower OS — Final")
root.attributes("-fullscreen", True)   # запускаем полноэкранно
root.configure(bg=BG_COLOR)

SW = root.winfo_screenwidth()
SH = root.winfo_screenheight()

# ---------------- Фон (шарики) ----------------
canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0)
canvas.place(relwidth=1, relheight=1)

spheres = []
for _ in range(28):
    r = random.randint(50, 140)
    x = random.randint(0, SW - r)
    y = random.randint(0, SH - r)
    col = random.choice([SPHERE_COLOR, "#34323a", "#2f2f3a"])
    oid = canvas.create_oval(x, y, x + r, y + r, fill=col, outline="")
    vx = random.uniform(-0.5, 0.5)
    vy = random.uniform(-0.3, 0.3)
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

# ---------------- Рабочий стол ----------------
desktop = tk.Frame(root, bg=BG_COLOR)
desktop.place(relwidth=1, relheight=1)

ICON_FONT = ("Segoe UI Emoji", 28)
ICON_GAP_Y = 110
ICON_START_X = 70
ICON_START_Y = 80

APPS = [
    ("Калькулятор", "calculator"),
    ("Заметки", "notes"),
    ("Браузер", "browser")
]

# ---------------- Окна приложений ----------------
def open_app_window(key, title):
    """Создаёт окно с анимацией, заголовком, кнопками: свернуть, развернуть, закрыть."""
    # размеры целевые
    target_w = int(SW * 0.5)
    target_h = int(SH * 0.6)
    cx = SW // 2 - target_w // 2
    cy = SH // 2 - target_h // 2

    # shadow на canvas
    shadow = canvas.create_rectangle(cx+10, cy+10, cx+10+target_w, cy+10+target_h, fill="#000000", outline="", stipple="gray12")
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.configure(bg=WINDOW_BG)
    # начальные маленькие размеры в центре
    start_w, start_h = max(60, target_w // 10), max(40, target_h // 10)
    sx = cx + (target_w - start_w)//2
    sy = cy + (target_h - start_h)//2
    win.geometry(f"{start_w}x{start_h}+{sx}+{sy}")
    # заголовок
    title_bar = tk.Frame(win, bg=TITLE_BG, height=34)
    title_bar.pack(fill="x")
    lbl = tk.Label(title_bar, text=title, bg=TITLE_BG, fg=TEXT_COLOR, font=("Segoe UI", 10, "bold"))
    lbl.pack(side="left", padx=8)
    btns = tk.Frame(title_bar, bg=TITLE_BG)
    btns.pack(side="right")

    # управление полноэкранным состоянием окна
    win.is_max = False
    normal_geom = (sx, sy, start_w, start_h)

    def close_anim():
        # shrink + fade
        try:
            can_alpha = True
            win.attributes("-alpha", 1.0)
        except Exception:
            can_alpha = False
        w0 = win.winfo_width(); h0 = win.winfo_height()
        g = win.geometry().split("+"); posx = int(g[1]); posy = int(g[2])
        steps = 12
        for i in range(steps+1):
            t = i/steps
            nw = int(w0 * (1 - t) + 8)
            nh = int(h0 * (1 - t) + 6)
            nx = posx + (w0 - nw)//2
            ny = posy + (h0 - nh)//2
            try:
                win.geometry(f"{nw}x{nh}+{nx}+{ny}")
                if can_alpha:
                    win.attributes("-alpha", 1 - t)
                canvas.coords(shadow, nx+10, ny+10, nx+10+nw, ny+10+nh)
            except Exception:
                pass
            time.sleep(0.01)
        try:
            win.destroy()
        except:
            pass
        try:
            canvas.delete(shadow)
        except:
            pass

    def minimize():
        win.withdraw()

    def toggle_max():
        nonlocal normal_geom
        if not win.is_max:
            # save normal
            g = win.geometry().split("+")
            wh = g[0].split("x")
            normal_geom = (int(g[1]), int(g[2]), int(wh[0]), int(wh[1]))
            win.is_max = True
            win.geometry(f"{SW}x{SH}+0+0")
            canvas.coords(shadow, 10, 10, SW-10, SH-10)
        else:
            win.is_max = False
            nx, ny, nw, nh = normal_geom
            win.geometry(f"{nw}x{nh}+{nx}+{ny}")
            canvas.coords(shadow, nx+10, ny+10, nx+10+nw, ny+10+nh)

    # кнопки
    b_min = tk.Button(btns, text="🗕", bg=TITLE_BG, fg=TEXT_COLOR, bd=0, command=minimize)
    b_max = tk.Button(btns, text="🗖", bg=TITLE_BG, fg=TEXT_COLOR, bd=0, command=toggle_max)
    b_close = tk.Button(btns, text="✕", bg=TITLE_BG, fg=TEXT_COLOR, bd=0, command=lambda: threading.Thread(target=close_anim, daemon=True).start())
    for b in (b_min, b_max, b_close):
        b.pack(side="left", padx=3)

    # содержимое окна (пример)
    content = tk.Frame(win, bg=WINDOW_BG)
    content.pack(expand=True, fill="both")
    if key == "calculator":
        build_calculator(content)
    elif key == "notes":
        build_notes(content)
    else:
        tk.Label(content, text=f"{title} — демо", bg=WINDOW_BG, fg=TEXT_COLOR, font=("Segoe UI", 12)).pack(padx=12, pady=12)

    # анимация открытия (scale + fade)
    try:
        win.attributes("-alpha", 0.0); can_alpha = True
    except Exception:
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
            except Exception:
                pass
            time.sleep(0.01)
        # final ensure
        win.geometry(f"{target_w}x{target_h}+{cx}+{cy}")
        if can_alpha:
            win.attributes("-alpha", 1.0)
    threading.Thread(target=anim_open, daemon=True).start()

    # перетаскивание за заголовок
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
        except Exception:
            pass
    title_bar.bind("<Button-1>", start_move)
    title_bar.bind("<B1-Motion>", do_move)

# ---------------- Контент билдера (калькулятор/заметки) ----------------
def build_calculator(parent):
    expr = tk.StringVar()
    e = tk.Entry(parent, textvariable=expr, font=("Consolas", 18), justify="right", bg="#1b1c21", fg="white", bd=0, insertbackground="white")
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
        b = tk.Button(grid, text=ch, command=lambda c=ch: press(c), bg="#2b2b33", fg="white", bd=0, font=("Segoe UI", 14))
        b.grid(row=i//4, column=i%4, sticky="nsew", padx=6, pady=6)
    for i in range(4):
        grid.columnconfigure(i, weight=1)
        grid.rowconfigure(i, weight=1)

def build_notes(parent):
    t = tk.Text(parent, bg="#1b1c21", fg="white", bd=0)
    t.insert("1.0", "Новая заметка...\n")
    t.pack(fill="both", expand=True, padx=12, pady=12)

# ---------------- Создание иконок ----------------
def create_desktop_icon(x, y, title, key):
    frame = tk.Frame(desktop, bg=BG_COLOR)
    frame.place(x=x, y=y)
    btn = tk.Button(frame, text="🗂", font=ICON_FONT, bg=WINDOW_BG, fg="white", bd=0,
                    activebackground="#3a3a44", command=lambda k=key, t=title: open_app_window(k, t))
    btn.pack()
    lbl = tk.Label(frame, text=title, bg=BG_COLOR, fg="white", font=("Segoe UI", 10))
    lbl.pack(pady=(6,0))

for idx, (title, key) in enumerate(APPS):
    create_desktop_icon(ICON_START_X, ICON_START_Y + idx * ICON_GAP_Y, title, key)

# ---------------- Панель задач и центрированное меню (v5-7 style) ----------------
TASK_H = 54
taskbar = tk.Frame(root, bg=TASKBAR_BG, height=TASK_H)
taskbar.pack(side="bottom", fill="x")

start_btn = tk.Button(taskbar, text="⊞ Пуск", bg=TASKBAR_BG, fg=TEXT_COLOR, bd=0, font=("Segoe UI", 11, "bold"))
start_btn.pack(side="left", padx=12, pady=8)

MENU_W = int(SW * 0.38)
MENU_H = int(SH * 0.54)
menu_x = (SW - MENU_W) // 2
menu_y_hidden = SH + 20
menu_y_shown = (SH - MENU_H) // 2
menu_frame = tk.Frame(root, bg=MENU_BG, bd=0)
menu_frame.place(x=menu_x, y=menu_y_hidden, width=MENU_W, height=MENU_H)
menu_visible = False

# Поиск
search_var = tk.StringVar()
search_entry = tk.Entry(menu_frame, textvariable=search_var, bg="#27272f", fg="white", bd=0, font=("Segoe UI", 12), insertbackground="white")
search_entry.place(x=16, y=16, width=MENU_W-32, height=36)

apps_frame = tk.Frame(menu_frame, bg=MENU_BG)
apps_frame.place(x=16, y=72, width=MENU_W-32, height=MENU_H-88)

app_button_widgets = []
for title, key in APPS:
    b = tk.Button(apps_frame, text=title, anchor="w", bg=MENU_ITEM, fg=TEXT_COLOR, bd=0, relief="flat",
                  command=lambda k=key, t=title: (hide_menu(), open_app_window(k, t)))
    b.pack(fill="x", pady=8)
    app_button_widgets.append((b, title))

def refresh_app_list(q=""):
    q = q.lower().strip()
    for btn, title in app_button_widgets:
        if not q or q in title.lower():
            btn.pack_configure(fill="x", pady=8)
        else:
            btn.pack_forget()

refresh_app_list("")

def show_menu():
    global menu_visible
    if menu_visible: return
    menu_visible = True
    steps = 12
    start = menu_y_hidden
    dy = (menu_y_shown - start) / steps
    def step(i=0):
        if i <= steps:
            y = int(start + dy * i)
            menu_frame.place(y=y)
            root.after(12, lambda: step(i+1))
        else:
            menu_frame.place(y=menu_y_shown)
            search_entry.focus_set()
    step()

def hide_menu():
    global menu_visible
    if not menu_visible: return
    menu_visible = False
    steps = 12
    start = menu_y_shown
    dy = (menu_y_hidden - start) / steps
    def step(i=0):
        if i <= steps:
            y = int(start + dy * i)
            menu_frame.place(y=y)
            root.after(12, lambda: step(i+1))
        else:
            menu_frame.place(y=menu_y_hidden)
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
root.bind("<Key>", lambda e: toggle_menu() if e.keysym in ("Super_L","Super_R") else None)
search_var.trace_add("write", lambda *a: refresh_app_list(search_var.get()))

# закрывать меню кликом вне меню
def global_click(e):
    if menu_visible:
        mx, my = menu_frame.winfo_rootx(), menu_frame.winfo_rooty()
        mw, mh = menu_frame.winfo_width(), menu_frame.winfo_height()
        if not (mx <= e.x_root <= mx+mw and my <= e.y_root <= my+mh):
            hide_menu()
root.bind("<Button-1>", global_click, add="+")

# опустить canvas под всеми виджетами
canvas.tag_lower("all")

root.mainloop()
