# This cell creates and launches an advanced calculator GUI using tkinter.
# Features: standard ops, parentheses, percentage, memory (MC/MR/M+/M-), scientific funcs,
# keyboard input, expression history, and error handling. Uses eval on a sanitized namespace.

import tkinter as tk
from tkinter import ttk
import math

# Create safe eval environment with math
safe_names = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
# Common aliases
safe_names.update({
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'asin': math.asin,
    'acos': math.acos,
    'atan': math.atan,
    'sqrt': math.sqrt,
    'log': math.log10,
    'ln': math.log,
    'log10': math.log10,
    'pi': math.pi,
    'e': math.e,
    'pow': pow,
    'abs': abs,
    'round': round
})

# Calculator state
memory_val = 0.0
history_list = []

root = tk.Tk()
root.title("Jitin Advanced Calculator")
root.geometry("420x540")
root.minsize(380, 520)

# Styling
style = ttk.Style()
try:
    style.theme_use('clam')
except Exception:
    pass

mainframe = ttk.Frame(root, padding=8)
mainframe.pack(fill=tk.BOTH, expand=True)

# Display and history
display_var = tk.StringVar()
entry = ttk.Entry(mainframe, textvariable=display_var, font=("Segoe UI", 20), justify='right')
entry.grid(row=0, column=0, columnspan=6, sticky='nsew', pady=(0, 6))
entry.focus_set()

hist_label = ttk.Label(mainframe, text="History", anchor='w')
hist_label.grid(row=1, column=0, columnspan=6, sticky='w')

hist_box = tk.Listbox(mainframe, height=5)
hist_box.grid(row=2, column=0, columnspan=6, sticky='nsew')

# Configure grid weights
for r in range(3, 12):
    mainframe.rowconfigure(r, weight=1)
for c in range(6):
    mainframe.columnconfigure(c, weight=1)
mainframe.rowconfigure(2, weight=1)

# Helpers

def insert_text(txt):
    pos = entry.index(tk.INSERT)
    entry.insert(pos, txt)


def clear_entry():
    display_var.set("")


def backspace():
    current = display_var.get()
    if len(current) > 0:
        display_var.set(current[:-1])


def percent_transform(expr):
    # Convert a% into (a/100)
    # Handle numbers followed by % possibly chained like 50%*200
    # Replace occurrences of number% with (number/100)
    out = ""
    i = 0
    while i < len(expr):
        if expr[i].isdigit() or (expr[i] == '.' and i+1 < len(expr) and expr[i+1].isdigit()):
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            if j < len(expr) and expr[j] == '%':
                num = expr[i:j]
                out += '(' + num + '/100)'
                i = j + 1
                continue
            else:
                out += expr[i:j]
                i = j
                continue
        else:
            out += expr[i]
            i += 1
    return out


def sanitize(expr):
    # Replace unicode operators and power caret, allow safe functions
    s = expr.replace('\u00d7', '*').replace('\u00f7', '/').replace('^', '**')
    s = s.replace('π', 'pi')
    s = s.replace('√', 'sqrt')
    # Percent
    s = percent_transform(s)
    return s


def evaluate():
    expr = display_var.get().strip()
    if len(expr) == 0:
        return
    try:
        s = sanitize(expr)
        # Prevent names not in safe_names
        result = eval(s, {"__builtins__": {}}, safe_names)
        # Nicely format floats
        if isinstance(result, float):
            if abs(result) < 1e-12:
                result = 0.0
            disp = ("{:.12g}").format(result)
        else:
            disp = str(result)
        hist_box.insert(tk.END, expr + " = " + disp)
        history_list.append((expr, disp))
        display_var.set(disp)
        entry.icursor(tk.END)
    except Exception:
        display_var.set("Error")
        entry.icursor(tk.END)


def use_from_history(event):
    sel = hist_box.curselection()
    if not sel:
        return
    val = hist_box.get(sel[0])
    if ' = ' in val:
        left = val.split(' = ')[0]
        display_var.set(left)
        entry.icursor(tk.END)

# Memory ops

def mem_clear():
    global memory_val
    memory_val = 0.0

def mem_recall():
    display_var.set(display_var.get() + str(memory_val))
    entry.icursor(tk.END)


def mem_add():
    global memory_val
    try:
        s = sanitize(display_var.get())
        val = eval(s, {"__builtins__": {}}, safe_names)
        memory_val += float(val)
    except Exception:
        pass


def mem_sub():
    global memory_val
    try:
        s = sanitize(display_var.get())
        val = eval(s, {"__builtins__": {}}, safe_names)
        memory_val -= float(val)
    except Exception:
        pass

# Button factory

def make_btn(text, r, c, cmd=None, span=1):
    b = ttk.Button(mainframe, text=text, command=cmd)
    b.grid(row=r, column=c, columnspan=span, sticky='nsew', padx=2, pady=2)
    return b

# Row 3: Memory, clear, backspace, divide
make_btn('MC', 3, 0, mem_clear)
make_btn('MR', 3, 1, mem_recall)
make_btn('M+', 3, 2, mem_add)
make_btn('M-', 3, 3, mem_sub)
make_btn('C', 3, 4, clear_entry)
make_btn('⌫', 3, 5, backspace)

# Row 4: functions
make_btn('(', 4, 0, lambda: insert_text('('))
make_btn(')', 4, 1, lambda: insert_text(')'))
make_btn('%', 4, 2, lambda: insert_text('%'))
make_btn('√', 4, 3, lambda: insert_text('√('))
make_btn('x^y', 4, 4, lambda: insert_text('^'))
make_btn('÷', 4, 5, lambda: insert_text('÷'))

# Row 5
make_btn('7', 5, 0, lambda: insert_text('7'))
make_btn('8', 5, 1, lambda: insert_text('8'))
make_btn('9', 5, 2, lambda: insert_text('9'))
make_btn('sin', 5, 3, lambda: insert_text('sin('))
make_btn('cos', 5, 4, lambda: insert_text('cos('))
make_btn('×', 5, 5, lambda: insert_text('×'))

# Row 6
make_btn('4', 6, 0, lambda: insert_text('4'))
make_btn('5', 6, 1, lambda: insert_text('5'))
make_btn('6', 6, 2, lambda: insert_text('6'))
make_btn('tan', 6, 3, lambda: insert_text('tan('))
make_btn('log', 6, 4, lambda: insert_text('log('))
make_btn('-', 6, 5, lambda: insert_text('-'))

# Row 7
make_btn('1', 7, 0, lambda: insert_text('1'))
make_btn('2', 7, 1, lambda: insert_text('2'))
make_btn('3', 7, 2, lambda: insert_text('3'))
make_btn('ln', 7, 3, lambda: insert_text('ln('))
make_btn('π', 7, 4, lambda: insert_text('π'))
make_btn('+', 7, 5, lambda: insert_text('+'))

# Row 8
make_btn('0', 8, 0, lambda: insert_text('0'))
make_btn('.', 8, 1, lambda: insert_text('.'))
make_btn('00', 8, 2, lambda: insert_text('00'))
make_btn('abs', 8, 3, lambda: insert_text('abs('))
make_btn('Ans', 8, 4, lambda: insert_text(history_list[-1][1] if history_list else ''))
make_btn('=', 8, 5, evaluate)

# Row 9: extra funcs
make_btn('x^2', 9, 0, lambda: insert_text('^2'))
make_btn('x^3', 9, 1, lambda: insert_text('^3'))
make_btn('1/x', 9, 2, lambda: insert_text('**-1'))
make_btn('exp', 9, 3, lambda: insert_text('exp('))
make_btn('mod', 9, 4, lambda: insert_text('%'))
make_btn(',', 9, 5, lambda: insert_text(','))

# Bind history double-click
hist_box.bind('<Double-1>', use_from_history)

# Keyboard bindings

def on_key(event):
    key = event.keysym
    ch = event.char
    if key == 'Return':
        evaluate()
        return 'break'
    if key == 'BackSpace':
        backspace()
        return 'break'
    if key == 'Escape':
        clear_entry()
        return 'break'
    # Allow typical characters
    if ch in '0123456789.+-*/()%^,' or ch.isalpha():
        insert_text(ch)
        return 'break'
    if key in ['KP_Add', 'KP_Subtract', 'KP_Multiply', 'KP_Divide']:
        mapping = {
            'KP_Add': '+',
            'KP_Subtract': '-',
            'KP_Multiply': '*',
            'KP_Divide': '/'
        }
        insert_text(mapping.get(key, ''))
        return 'break'

entry.bind('<Key>', on_key)

root.mainloop()