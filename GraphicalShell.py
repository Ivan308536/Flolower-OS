"""
Mini-OS Turtle Pro (версія 2.0)
Автор: ChatGPT
Оновлення: Контекстне меню, панель швидкого доступу, кілька робочих столів, збереження нотаток, історія калькулятора.
Запуск: python mini_os_turtle_pro.py
"""
import turtle
import time
import os

# ==================== НАЛАШТУВАННЯ ====================
screen = turtle.Screen()
screen.title("Mini-OS Turtle Pro")
screen.setup(1000, 700)
screen.bgcolor('#1b2430')
screen.tracer(0)

# ==================== ГЛОБАЛЬНІ ЗМІННІ ====================
DESKTOPS = [[], []]  # два робочих столи
current_desktop = 0
notes_file = 'notes.txt'
calc_history_file = 'calc_history.txt'

# ==================== ДОПОМІЖНІ ФУНКЦІЇ ====================

def draw_rounded_rect(t, x, y, w, h, r=10):
    t.penup()
    t.goto(x + r, y)
    t.pendown()
    for _ in range(2):
        t.forward(w - 2 * r)
        t.circle(r, 90)
        t.forward(h - 2 * r)
        t.circle(r, 90)


def safe_eval(expr):
    allowed = set('0123456789+-*/(). ')
    if set(expr) - allowed:
        raise ValueError('Недопустимі символи')
    return eval(expr)


# ==================== КЛАСИ ====================

class Icon:
    def __init__(self, x, y, label, callback):
        self.x, self.y, self.label, self.callback = x, y, label, callback
        self.t = turtle.Turtle(visible=False)
        self.t.penup()
        self.draw()

    def draw(self):
        self.t.goto(self.x, self.y)
        self.t.shape('square')
        self.t.shapesize(2, 2)
        self.t.color('white')
        self.t.showturtle()
        text = turtle.Turtle(visible=False)
        text.penup()
        text.goto(self.x, self.y - 25)
        text.color('white')
        text.write(self.label, align='center', font=('Arial', 10, 'normal'))

    def hit_test(self, x, y):
        return self.x - 20 < x < self.x + 20 and self.y - 20 < y < self.y + 20


class Window:
    instances = []

    def __init__(self, title, w=400, h=300):
        self.title, self.w, self.h = title, w, h
        self.x, self.y = -w//2 + 50, h//2 - 50
        self.t = turtle.Turtle(visible=False)
        self.t.hideturtle()
        Window.instances.append(self)
        self.draw()

    def draw(self):
        self.t.clear()
        self.t.penup()
        self.t.goto(self.x, self.y)
        self.t.pendown()
        self.t.fillcolor('white')
        self.t.begin_fill()
        draw_rounded_rect(self.t, self.x, self.y - self.h, self.w, self.h, 10)
        self.t.end_fill()
        # Заголовок
        self.t.penup()
        self.t.goto(self.x + 10, self.y - 25)
        self.t.color('black')
        self.t.write(self.title, font=('Arial', 12, 'bold'))
        # Кнопка закрити
        self.t.goto(self.x + self.w - 30, self.y - 18)
        self.t.color('red')
        self.t.begin_fill()
        for _ in range(4):
            self.t.forward(16)
            self.t.right(90)
        self.t.end_fill()

    def close(self):
        self.t.clear()
        if self in Window.instances:
            Window.instances.remove(self)


# ==================== ПРОГРАМИ ====================

def app_clock():
    win = Window('Годинник', 300, 120)
    t = turtle.Turtle(visible=False)

    def update():
        if win not in Window.instances:
            t.clear()
            return
        t.clear()
        t.penup()
        t.goto(win.x + 10, win.y - 60)
        t.color('black')
        t.write(time.strftime('%H:%M:%S'), font=('Arial', 24, 'bold'))
        screen.update()
        screen.ontimer(update, 500)
    update()


def app_calc():
    win = Window('Калькулятор', 360, 220)
    t = turtle.Turtle(visible=False)

    expr = screen.textinput('Калькулятор', 'Введіть вираз:')
    if expr is None:
        win.close()
        return
    try:
        result = safe_eval(expr)
        with open(calc_history_file, 'a', encoding='utf-8') as f:
            f.write(f'{expr} = {result}\n')
        t.penup()
        t.goto(win.x + 10, win.y - 80)
        t.color('black')
        t.write(f'{expr} = {result}', font=('Arial', 16, 'normal'))
    except Exception:
        t.penup()
        t.goto(win.x + 10, win.y - 80)
        t.color('black')
        t.write('Помилка у виразі', font=('Arial', 16, 'normal'))


def app_notes():
    win = Window('Нотатки', 500, 300)
    t = turtle.Turtle(visible=False)

    if not os.path.exists(notes_file):
        open(notes_file, 'w', encoding='utf-8').close()

    text = screen.textinput('Нотатки', 'Введіть текст (або залиште порожнім для перегляду):')
    if text:
        with open(notes_file, 'a', encoding='utf-8') as f:
            f.write(text + '\n')

    with open(notes_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    t.penup()
    t.goto(win.x + 10, win.y - 60)
    t.color('black')
    for i, line in enumerate(lines[-10:]):
        t.goto(win.x + 10, win.y - 60 - i * 20)
        t.write(line.strip(), font=('Arial', 12, 'normal'))


def app_paint():
    win = Window('Paint', 600, 400)
    painter = turtle.Turtle(visible=False)
    painter.pensize(3)
    drawing = {'down': False}

    def start(x, y):
        drawing['down'] = True
        painter.penup()
        painter.goto(x, y)
        painter.pendown()

    def stop(x, y):
        drawing['down'] = False
        painter.penup()

    def draw(x, y):
        if drawing['down']:
            painter.goto(x, y)

    screen.onclick(start)
    screen.onrelease(stop)
    screen.ondrag(draw)


# ==================== ПАНЕЛЬ ШВИДКОГО ДОСТУПУ ====================

def draw_taskbar():
    bar = turtle.Turtle(visible=False)
    bar.penup()
    bar.goto(-500, -320)
    bar.color('#0f1720')
    bar.begin_fill()
    for _ in range(2):
        bar.forward(1000)
        bar.right(90)
        bar.forward(40)
        bar.right(90)
    bar.end_fill()

    quick = turtle.Turtle(visible=False)
    quick.penup()
    quick.color('white')
    quick.goto(-480, -340)
    quick.write('[1] 🕒  [2] 🧮  [3] 📝  [4] 🎨', font=('Arial', 14, 'bold'))


def switch_desktop():
    global current_desktop
    for ic in DESKTOPS[current_desktop]:
        ic.t.hideturtle()
    current_desktop = 1 - current_desktop
    for ic in DESKTOPS[current_desktop]:
        ic.t.showturtle()
    screen.update()


# ==================== КОНТЕКСТНЕ МЕНЮ ====================
menu_t = turtle.Turtle(visible=False)
menu_visible = False

def show_context_menu(x, y):
    global menu_visible
    if menu_visible:
        menu_t.clear()
        menu_visible = False
        return
    menu_t.clear()
    menu_t.penup()
    menu_t.goto(x, y)
    menu_t.color('white', '#333')
    menu_t.begin_fill()
    for _ in range(2):
        menu_t.forward(160)
        menu_t.right(90)
        menu_t.forward(100)
        menu_t.right(90)
    menu_t.end_fill()
    menu_t.penup()
    menu_t.goto(x + 10, y - 20)
    menu_t.write('1) Про систему\n2) Перемкнути Desktop\n3) Закрити меню', font=('Arial', 12, 'normal'))
    menu_visible = True


# ==================== ІНІЦІАЛІЗАЦІЯ ====================
icons1 = [
    Icon(-420, 250, 'Годинник', app_clock),
    Icon(-420, 180, 'Калькулятор', app_calc),
    Icon(-420, 110, 'Нотатки', app_notes),
    Icon(-420, 40, 'Paint', app_paint)
]
DESKTOPS[0] = icons1
DESKTOPS[1] = [Icon(-420, 250, 'Калькулятор', app_calc)]

draw_taskbar()

# ==================== ПОДІЇ ====================

def on_click(x, y):
    global menu_visible
    if menu_visible:
        menu_t.clear()
        menu_visible = False
    for ic in DESKTOPS[current_desktop]:
        if ic.hit_test(x, y):
            ic.callback()
            return
    for win in list(Window.instances):
        bx, by = win.x + win.w - 30, win.y - 18
        if bx < x < bx + 16 and by - win.h < y < by:
            win.close()
            return


def on_right_click(x, y):
    show_context_menu(x, y)


def on_key(key):
    if key == '1':
        app_clock()
    elif key == '2':
        app_calc()
    elif key == '3':
        app_notes()
    elif key == '4':
        app_paint()
    elif key == 'space':
        switch_desktop()


screen.onclick(on_click)
screen.onscreenclick(on_right_click, btn=3)
for key in ['1', '2', '3', '4', 'space']:
    screen.onkey(lambda k=key: on_key(k), key)
screen.listen()

print('Mini-OS Turtle Pro запущено! ПКМ — контекстне меню, цифри 1–4 — швидкий доступ, пробіл — зміна Desktop.')
screen.update()
turtle.mainloop()
