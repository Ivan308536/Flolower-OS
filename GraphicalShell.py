# flolower_os_v9_with_terminal_full.py
# Для команды "joke" может понадобиться: pip install pyjokes

import tkinter as tk
import random, time, json, os, calendar, datetime

# Попытка импортировать pyjokes — если нет, будем обрабатывать аккуратно
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
ICON_POS_FILE = "icons_pos_v9.json"
NOTES_SAVE_PATH = r"D:\замітки.txt"

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
        # мягкое изменение цвета вокруг исходного
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
start_btn = tk.Button(taskbar, text="⊞ Пуск", bg=MENU_BG, fg=TEXT, font=TEXT_FONT, bd=0, padx=12, pady=6)
start_btn.pack(side="left", padx=12, pady=6)
task_buttons_frame = tk.Frame(taskbar, bg=TASKBAR_BG)
task_buttons_frame.pack(side="left", padx=8, pady=6)
time_lbl = tk.Label(taskbar, text=time.strftime("%H:%M"), bg=TASKBAR_BG, fg=TEXT, font=TEXT_FONT)
time_lbl.pack(side="right", padx=12)
def tick_time(): time_lbl.config(text=time.strftime("%H:%M")); root.after(1000,tick_time)
tick_time()
task_buttons={}

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
    lbl=tk.Label(row,text=title,bg=MENU_ITEM,fg=TEXT,font=TEXT_FONT,anchor="w")
    lbl.pack(side="left",fill="x",expand=True)
    for w in (row,ico,lbl): w.bind("<Button-1>", lambda e,k=key,t=title:on_start_app(k,t))
    app_widgets.append((row,title))

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

start_btn.config(command=toggle_menu)
root.bind("<Button-1>", lambda e: hide_menu() if menu_visible and not start_menu.winfo_containing(e.x_root,e.y_root) else None, add="+")
root.bind("<Key>", lambda e: toggle_menu() if e.keysym in ("Super_L","Super_R") else None)
root.bind("<Escape>", lambda e: hide_menu())

# ------------------ Window system ------------------
open_windows=[]
def create_task_button(win,title):
    btn=tk.Button(task_buttons_frame,text=title,bg="#2a2233",fg=TEXT,bd=0,padx=8,pady=4,command=lambda w=win, b=None: (w.deiconify(), task_buttons.pop(w, None) and b.destroy() if False else None))
    # note: we bind real destroy below when creating the button to keep references
    btn.pack(side="left", padx=4)
    task_buttons[win]=btn

# ------------------ Terminal ------------------
def build_terminal(parent):
    frame=tk.Frame(parent,bg=WINDOW_BG)
    frame.pack(expand=True,fill="both",padx=12,pady=12)

    output = tk.Text(frame, bg="#000000", fg="#00ff00", insertbackground="#00ff00", bd=0, font=("Consolas", 11))
    output.pack(expand=True, fill="both", pady=(0,8))
    entry = tk.Entry(frame, bg="#111111", fg="#00ff00", insertbackground="#00ff00", bd=0, font=("Consolas", 11))
    entry.pack(fill="x", pady=(0,4))

    def write(text=""):
        output.insert("end", text + "\n")
        output.see("end")

    write("Flolower OS Terminal v1.0 (type 'help' for commands)")

    # Для команд, которые требуют запроса дополнительного ввода,
    # мы используем временные обработчики нажатия Enter.
    def process_command(event=None):
        cmd = entry.get().strip()
        entry.delete(0, "end")
        if not cmd:
            return
        write(f"Flolover OS> {cmd}")

        # Базовые команды
        if cmd == "help":
            write("Available commands: help, exit, quit, about, joke, roll, flip, time.")
            return

        if cmd == "about":
            write("Flolover OS v1 (beta)")
            return

        if cmd == "time":
            now = datetime.datetime.now()
            write(now.strftime("%H:%M:%S.%f")[:-3])
            return

        if cmd in ("exit", "quit"):
            # Закрываем родительское окно приложения (не всю ОС)
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
            # Запрашиваем число — используем временную функцию ожидания ввода
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
                # восстанавливаем основной обработчик
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

        # Если ничего не подошло:
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

def build_browser(parent):
    tk.Label(parent,text="Браузер (демо)",bg=WINDOW_BG,fg=TEXT).pack(anchor="nw",padx=12,pady=12)
    tk.Text(parent,bg="#1b1820",fg="white",bd=0).pack(fill="both",expand=True,padx=12,pady=(0,12))

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
            btn = task_buttons.pop(win)
            try: btn.destroy()
            except: pass
        except Exception:
            pass
        try:
            win.destroy()
        except:
            pass

    def minimize_win():
        try:
            win.withdraw()
            # recreate a task button that will restore the window
            def restore():
                try:
                    win.deiconify()
                    tb = task_buttons.pop(win, None)
                    if tb:
                        try: tb.destroy()
                        except: pass
                except: pass
            tb = tk.Button(task_buttons_frame, text=title, bg="#2a2233", fg=TEXT, bd=0, padx=8, pady=4, command=restore)
            tb.pack(side="left", padx=4)
            task_buttons[win] = tb
        except:
            pass

    win.is_max = False
    win.normal_geom = None
    def toggle_max():
        try:
            if not win.is_max:
                # сохранить текущее положение
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
                    # безопасный eval? здесь простой для demo
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

    # Перетаскивание окна
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

    # регистрируем окно в списке открытых
    open_windows.append({"win": win, "key": key, "title": title, "id": id(win)})

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
