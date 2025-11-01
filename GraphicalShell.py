# turtle_os.py
# Простая графическая оболочка "OS" на turtle
# Запуск: python turtle_os.py

import turtle
import time
import math

# --- Настройки окна ---
SCREEN_W, SCREEN_H = 1000, 650
BG_COLOR = "#0f1724"
TASKBAR_COLOR = "#111827"
START_BTN_COLOR = "#0ea5a4"
MENU_BG = "#0b1220"
ICON_COLOR = "#22c55e"
WINDOW_BG = "#f8fafc"
TITLE_BG = "#334155"

screen = turtle.Screen()
screen.setup(SCREEN_W, SCREEN_H)
screen.title("Turtle OS — demo")
screen.bgcolor(BG_COLOR)
screen.tracer(0)

# Утилитарные функции рисования прямоугольников / текста
def rect(t, x, y, w, h, color, pen_size=1):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.pensize(pen_size)
    t.color(color)
    t.fillcolor(color)
    t.begin_fill()
    for _ in range(2):
        t.forward(w)
        t.left(90)
        t.forward(h)
        t.left(90)
    t.end_fill()
    t.penup()

def write_center(t, x, y, text, font=("Arial", 10, "normal")):
    t.penup()
    t.goto(x, y)
    t.write(text, align="center", font=font)

# --- Taskbar и Start ---
taskbar = turtle.Turtle(visible=False)
taskbar.hideturtle()
taskbar.speed(0)

TASKBAR_H = 50
rect(taskbar, -SCREEN_W//2, -SCREEN_H//2, SCREEN_W, TASKBAR_H, TASKBAR_COLOR)

# Start button
start_btn = turtle.Turtle(visible=False)
start_btn.hideturtle()
start_btn.speed(0)
START_W, START_H = 90, 36
start_x = -SCREEN_W//2 + 10
start_y = -SCREEN_H//2 + 7
rect(start_btn, start_x, start_y, START_W, START_H, START_BTN_COLOR)
write_center(start_btn, start_x + START_W/2, start_y + 6, "START", ("Arial", 12, "bold"))

# Clock display (right side)
clock_t = turtle.Turtle(visible=False)
clock_t.hideturtle()
clock_t.speed(0)

def update_clock():
    now = time.strftime("%H:%M:%S")
    # очистить область часов — просто перерисуем прямоугольник
    rect(clock_t, SCREEN_W//2 - 120, -SCREEN_H//2 + 7, 110, START_H, TASKBAR_COLOR)
    write_center(clock_t, SCREEN_W//2 - 120 + 110/2, -SCREEN_H//2 + 6, now, ("Arial", 12, "normal"))
    screen.update()
    screen.ontimer(update_clock, 1000)

# --- Desktop icons ---
icons = []

class Icon:
    def __init__(self, x, y, name, action):
        self.x, self.y = x, y
        self.name = name
        self.action = action
        t = turtle.Turtle(shape="square")
        t.shapesize(2, 2)
        t.penup()
        t.goto(x, y)
        t.color(ICON_COLOR)
        t.showturtle()
        self.t = t
        label = turtle.Turtle(visible=False)
        label.hideturtle()
        label.penup()
        label.goto(x, y - 30)
        label.write(name, align="center", font=("Arial", 10, "normal"))
        self.label = label
        icons.append(self)
        # привязать клик
        t.onclick(self.on_click)

    def on_click(self, x, y):
        # открыть приложение
        self.action()

# --- Оконная система (простая) ---
windows = []

class Window:
    z_order = 0
    def __init__(self, title, x, y, w, h, content_draw=None):
        # parts: frame (background), titlebar, close button, content turtle
        self.title = title
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.content_draw = content_draw
        self.frame = turtle.Turtle(visible=False)
        self.frame.hideturtle()
        self.titlebar = turtle.Turtle(visible=False)
        self.titlebar.hideturtle()
        self.close_btn = turtle.Turtle(visible=False)
        self.close_btn.hideturtle()
        self.content = turtle.Turtle(visible=False)
        self.content.hideturtle()
        self._draw()
        self._bind_events()
        windows.append(self)
        Window.z_order += 1
        self.z = Window.z_order
        self.bring_to_front()

    def _draw(self):
        rect(self.frame, self.x, self.y, self.w, self.h, WINDOW_BG)
        # title bar
        rect(self.titlebar, self.x, self.y + self.h - 30, self.w, 30, TITLE_BG)
        write_center(self.titlebar, self.x + self.w/2, self.y + self.h - 22, self.title, ("Arial", 12, "bold"))
        # close button
        rect(self.close_btn, self.x + self.w - 34, self.y + self.h - 26, 26, 22, "#ef4444")
        write_center(self.close_btn, self.x + self.w - 21, self.y + self.h - 18, "X", ("Arial", 10, "bold"))
        # content placeholder
        if self.content_draw:
            self.content_draw(self.content, self.x + 10, self.y + 10, self.w - 20, self.h - 50)

    def _bind_events(self):
        # перетаскивание — используем titlebar.ondrag
        def start_drag(x, y):
            self._drag_offset = (x - self.x, y - (self.y + self.h))
        def do_drag(x, y):
            if hasattr(self, "_drag_offset"):
                ox, oy = self._drag_offset
                new_x = x - ox
                new_y = y - oy - self.h
                self.move_to(new_x, new_y)
        def close(x, y):
            self.close()
        # привязываем события
        self.titlebar.showturtle()
        # create an invisible big clickable region by giving shape and ondra/onclick
        self.titlebar.shape("square")
        self.titlebar.shapesize(self.h/20, self.w/20)
        self.titlebar.penup()
        self.titlebar.goto(self.x + self.w/2, self.y + self.h - 15)
        self.titlebar.ondrag(do_drag)
        self.titlebar.onclick(lambda x, y: self.bring_to_front())
        self.close_btn.shape("square")
        self.close_btn.shapesize(1.8, 1.2)
        self.close_btn.penup()
        self.close_btn.goto(self.x + self.w - 21, self.y + self.h - 15)
        self.close_btn.onclick(close)

    def move_to(self, nx, ny):
        dx = nx - self.x
        dy = ny - self.y
        self.x += dx
        self.y += dy
        for part in [self.frame, self.titlebar, self.close_btn, self.content]:
            px, py = part.position()
            part.goto(px + dx, py + dy)
        # redraw to align label text
        self.refresh()

    def refresh(self):
        # remove and redraw parts (simple approach)
        for p in [self.frame, self.titlebar, self.close_btn, self.content]:
            p.clear()
        self._draw()
        screen.update()

    def bring_to_front(self):
        # simple z-order: reappend to windows and redraw them in order
        if self in windows:
            windows.remove(self)
        windows.append(self)
        self.redraw_all()

    def redraw_all(self):
        # clear screen (except taskbar & icons) by redrawing background rectangles and all windows
        screen.clear()
        screen.bgcolor(BG_COLOR)
        # redraw taskbar + start + icons
        rect(taskbar, -SCREEN_W//2, -SCREEN_H//2, SCREEN_W, TASKBAR_H, TASKBAR_COLOR)
        rect(start_btn, start_x, start_y, START_W, START_H, START_BTN_COLOR)
        write_center(start_btn, start_x + START_W/2, start_y + 6, "START", ("Arial", 12, "bold"))
        for ic in icons:
            ic.t.goto(ic.x, ic.y)
            ic.t.showturtle()
            ic.label.clear()
            ic.label.goto(ic.x, ic.y - 30)
            ic.label.write(ic.name, align="center", font=("Arial", 10, "normal"))
        for w in windows:
            w.frame.clear(); w.titlebar.clear(); w.close_btn.clear(); w.content.clear()
            w._draw()
            # reposition titlebar / close shapes to enable events
            w.titlebar.shape("square")
            w.titlebar.shapesize(w.h/20, w.w/20)
            w.titlebar.penup()
            w.titlebar.goto(w.x + w.w/2, w.y + w.h - 15)
            w.close_btn.shape("square")
            w.close_btn.shapesize(1.8, 1.2)
            w.close_btn.penup()
            w.close_btn.goto(w.x + w.w - 21, w.y + w.h - 15)
        update_clock()
        screen.update()

    def close(self):
        # скрываем черепашек окна
        for p in [self.frame, self.titlebar, self.close_btn, self.content]:
            try:
                p.clear()
                p.hideturtle()
            except:
                pass
        if self in windows:
            windows.remove(self)
        self.redraw_all()

# --- Приложения (демо) ---
def notepad_content(t, x, y, w, h):
    # текст простым write
    t.hideturtle()
    t.penup()
    t.goto(x + w/2, y + h/2)
    t.write("Это демонстрационный блокнот.\n(только чтение)", align="center", font=("Arial", 12, "normal"))

def calc_content(t, x, y, w, h):
    t.hideturtle()
    t.penup()
    t.goto(x + w/2, y + h/2 + 20)
    t.write("Калькулятор", align="center", font=("Arial", 14, "bold"))
    # простая интерактивность — числа можно ввести из клавиатуры
    t.goto(x + w/2, y + h/2 - 10)
    t.write("Нажми клавиши 0-9, +,-,*,/ и Enter", align="center", font=("Arial", 10, "normal"))

    # состояние калькулятора (замыкание)
    calc_content.expr = ""

def create_notepad():
    Window("Блокнот", -200, -50, 420, 300, content_draw=notepad_content)

def create_calculator():
    win = Window("Калькулятор", -50, 0, 300, 220, content_draw=calc_content)
    # обработка клавиатуры для калькулятора — глобально: если последнее окно — калькулятор, добавляем ввод
    def on_keypress(key):
        if windows and windows[-1] is win:
            if key == "Return":
                try:
                    val = eval(calc_content.expr)
                    calc_content.expr = str(val)
                except Exception:
                    calc_content.expr = "Ошибка"
            elif key == "BackSpace":
                calc_content.expr = calc_content.expr[:-1]
            else:
                calc_content.expr += key
            # обновим содержимое
            win.content.clear()
            win.content.hideturtle()
            win.content.penup()
            win.content.goto(win.x + 20, win.y + win.h - 80)
            win.content.write(calc_content.expr, font=("Arial", 16, "normal"))
            screen.update()

    # привязать клавиши
    for k in list("0123456789+-*/."):
        screen.onkey(lambda k=k: on_keypress(k), k)
    screen.onkey(lambda: on_keypress("Return"), "Return")
    screen.onkey(lambda: on_keypress("BackSpace"), "BackSpace")

# --- Start menu (простая панель) ---
menu_open = False
menu_t = turtle.Turtle(visible=False)
menu_t.hideturtle()

def toggle_menu(x=None, y=None):
    global menu_open
    if not menu_open:
        # нарисовать меню
        rect(menu_t, start_x, start_y + START_H + 5, 170, 150, MENU_BG)
        btn1_y = start_y + START_H + 120
        menu_t.penup()
        menu_t.goto(start_x + 85, btn1_y)
        menu_t.write("Блокнот", align="center", font=("Arial", 11, "normal"))
        menu_t.goto(start_x + 85, btn1_y - 40)
        menu_t.write("Калькулятор", align="center", font=("Arial", 11, "normal"))
        menu_open = True
    else:
        menu_t.clear()
        menu_open = False
    screen.update()

# Обработка кликов по меню (приблизительно по координатам)
def menu_click(x, y):
    if menu_open:
        # Блокнот
        if start_x < x < start_x + 170 and start_y + START_H + 90 < y < start_y + START_H + 150:
            create_notepad()
            toggle_menu()
        # Калькулятор
        if start_x < x < start_x + 170 and start_y + START_H + 50 < y < start_y + START_H + 90:
            create_calculator()
            toggle_menu()

# --- Инициализация и привязки ---
# Создаем пару иконок
Icon(-400, 120, "Мой комп", lambda: create_notepad())
Icon(-280, 120, "Блокнот", create_notepad)
Icon(-160, 120, "Кальк", create_calculator)

# Слушатели
# Клик по старт-кнопке:
def start_click(x, y):
    if start_x <= x <= start_x + START_W and start_y <= y <= start_y + START_H:
        toggle_menu()

screen.onscreenclick(start_click, 1)  # левая кнопка
screen.onscreenclick(menu_click, 1)

# Инициалный рендер
update_clock()
screen.update()

# Справка клавиш
def show_help():
    help_t = turtle.Turtle(visible=False)
    help_t.hideturtle()
    help_t.penup()
    help_t.goto(0, SCREEN_H//2 - 60)
    help_t.write("Turtle OS demo — кликни по иконкам, START — меню.\nПеретаскивай окна за заголовок.", align="center", font=("Arial", 12, "normal"))

show_help()
screen.update()

# Включаем обработку клавиш (некоторые — для калькулятора)
screen.listen()
# Главное — держим окно открытым
turtle.mainloop()
