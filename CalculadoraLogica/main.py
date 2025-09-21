import itertools
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import sys
import os

# -----------------------
# Helpers para recursos
# -----------------------
def resource_path(relative_path):
    try:
        # si estamos dentro de un onefile exe, PyInstaller extrae en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# -----------------------------------------------

#-----------------------------------------------
#Esta función realiza el cambio de los operadores lógicos a valores que el lenguaje de programación (en este caso, Python) los entienda y pueda realizar las operaciones sin ningún problema.
def normalizar(expr):
    expr = expr.replace("¬", " not ")
    expr = expr.replace("∧", " and ")
    expr = expr.replace("∨", " or ")
    expr = expr.replace("→", " <= ")
    expr = expr.replace("↔", " == ")
    return expr

#--------------------------------------------------
#Esta función hace que lo que el usuario haya puesto entre paréntesis lo determina como subexpresiones y asi poder mostrarlas antes en la tabla de expresiones.
def extraer_subexpresiones(expr): 
    expr_norm = normalizar(expr)
    variables = sorted(set(filter(str.isupper, expr)))

    subexpresiones = variables[:]  # Crea una copia de la lista Variables

    stack = []
    for i, c in enumerate(expr):
        if c == "(":
            stack.append(i)
        elif c == ")":
            inicio = stack.pop()
            sub = expr[inicio:i+1].strip()
            # quitamos paréntesis externos para la visualización
            sub_sin_par = sub
            while sub_sin_par.startswith("(") and sub_sin_par.endswith(")"):
                sub_sin_par = sub_sin_par[1:-1].strip()
            if sub_sin_par not in subexpresiones:
                subexpresiones.append(sub_sin_par)

    expr_sin_par = expr
    while expr_sin_par.startswith("(") and expr_sin_par.endswith(")"):
        expr_sin_par = expr_sin_par[1:-1].strip()

    if expr_sin_par not in subexpresiones:
        subexpresiones.append(expr_sin_par)

    return variables, subexpresiones

def generar_imagen_tabla(proposicion, valores_usuario=None):
    variables, subexpresiones = extraer_subexpresiones(proposicion)
    filas = []
    indices_filas = []

    for idx, valores in enumerate(itertools.product([True, False], repeat=len(variables))):
        env = dict(zip(variables, valores))
        fila = []
        for sub in subexpresiones:
            try:
                res = eval(normalizar(sub), {}, env)
                fila.append("V" if res else "F")
            except:
                fila.append("Error")
        filas.append(fila)

        if valores_usuario:
            coincide = all(env[v] == valores_usuario.get(v, None) for v in variables)
            if coincide:
                indices_filas.append(idx)

    # Fuente
    try:
        font = ImageFont.truetype(resource_path("assets/cambria.ttc"), 16)
    except:
        font = ImageFont.load_default()

    cell_w = 100
    cell_h = 25
    img_w = cell_w * len(subexpresiones)
    img_h = cell_h * (len(filas) + 1)

    img = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(img)

    for j, col in enumerate(subexpresiones):
        x0 = j * cell_w
        draw.rectangle([x0, 0, x0+cell_w, cell_h], outline="black", fill="#d9d9d9")
        draw.text((x0+5, 5), col, font=font, fill="black")

    # Filas
    for i, fila in enumerate(filas):
        for j, val in enumerate(fila):
            x0 = j * cell_w
            y0 = (i+1) * cell_h

            if i in indices_filas:
                fill_color = "#FFD966" 
            else:
                fill_color = "white"

            draw.rectangle([x0, y0, x0+cell_w, y0+cell_h], outline="black", fill=fill_color)
            draw.text((x0+20, y0+5), val, font=font, fill="black")

    return img

def mostrar_tabla(proposicion, tree_tabla):
    variables, subexpresiones = extraer_subexpresiones(proposicion)

    for item in tree_tabla.get_children():
        tree_tabla.delete(item)

    tree_tabla["columns"] = subexpresiones
    tree_tabla["show"] = "headings"

    for col in subexpresiones:
        tree_tabla.heading(col, text=col)
        tree_tabla.column(col, width=80, anchor="center")

    for valores in itertools.product([True, False], repeat=len(variables)):
        env = dict(zip(variables, valores))
        fila = []
        for sub in subexpresiones:
            try:
                res = eval(normalizar(sub), {}, env)
                fila.append("V" if res else "F")
            except:
                fila.append("Error")
        tree_tabla.insert("", "end", values=fila)

def pedir_valores(root):
    ventana = tk.Toplevel(root)
    ventana.title("Valores de verdad")
    ventana.geometry("230x140")
    ventana.iconbitmap(resource_path("assets/calculadora.ico"))

    imagen_fondo = Image.open(resource_path("assets/fondo.jpg"))
    imagen_fondo = imagen_fondo.resize((230,140))
    imagen_fondo = ImageTk.PhotoImage(imagen_fondo)

    fondo = tk.Label(ventana, image=imagen_fondo)
    fondo.place(x=0)

    ventana.grab_set()

    valores = {}
    variables = {}

    for i, prop in enumerate(["A", "B", "C"]):
        tk.Label(ventana, text=f"Valor de {prop}:").grid(row=i, column=0, padx=8, pady=6, sticky="w")
        var = tk.StringVar(value="F")
        tk.Radiobutton(ventana, text="Verdadero", variable=var, value="V").grid(row=i, column=1)
        tk.Radiobutton(ventana, text="Falso", variable=var, value="F").grid(row=i, column=2)
        variables[prop] = var

    def confirmar():
        for prop, var in variables.items():
            valores[prop] = (var.get() == "V")
        ventana.destroy()

    tk.Button(ventana, text="Aceptar", command=confirmar).grid(row=3, column=0, columnspan=3, pady=10)
    ventana.wait_window()
    return valores

def calculadora():
    root = tk.Tk()
    root.title("Calculadora Lógica")
    root.geometry("310x560")
    root.iconbitmap(resource_path("assets/calculadora.ico"))
    root.configure(bg="#CAB4EF")

    pantalla_var = tk.StringVar()
    pantalla = tk.Label(root, textvariable=pantalla_var, bg="#BDF4E3",
                    font=("Arial", 18), anchor="e", width=18, relief="sunken")
    pantalla.grid(row=0, column=0, columnspan=4, pady=10, padx=10, ipadx=10, ipady=15, sticky="we")

    resultado_label = tk.Label(root, text="", font=("Arial", 16), fg="#7756AF", bg="#CAB4EF")
    resultado_label.grid(row=4, column=0, columnspan=4, pady=10)
    
    frame_tabla = tk.Frame(root, width=280, height=220, bg="white")
    frame_tabla.grid(row=5, column=0, columnspan=4, padx=15, pady=15, sticky="nsew")
    
    frame_tabla.grid_propagate(False)


    def insertar(texto):
        pantalla_var.set(pantalla_var.get() + texto)

    def evaluar():
        expresion = pantalla_var.get()
        valores = pedir_valores(root)
        
        try:
            expr_norm = normalizar(expresion)
            resultado = eval(expr_norm, {}, valores)
            resultado_text = "Verdadero" if resultado else "Falso"
            resultado_label.config(text=f"Solución: {resultado_text}", bg="#CAB4EF")
        except Exception:
            resultado_label.config(text="Expresión inválida", bg="#CAB4EF")

        img = generar_imagen_tabla(expresion, valores_usuario=valores)

        frame_tabla.update_idletasks()
        frame_w = frame_tabla.winfo_width() or 280
        frame_h = frame_tabla.winfo_height() or 200
        img = img.resize((frame_w, frame_h), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        for widget in frame_tabla.winfo_children():
            widget.destroy()

        lbl_tabla = tk.Label(frame_tabla, image=img_tk, bg="white")
        lbl_tabla.image = img_tk
        lbl_tabla.grid(row=0, column=0, sticky="nsew")
 
    botones = [
        ("A", 1, 0), ("B", 1, 1), ("C", 1, 2), ("Borrar", 2, 3),
        ("¬", 1, 3), ("∧", 2, 1), ("∨", 2, 2), ("(", 3, 1),
        (")", 3, 2), ("→", 2, 0), ("↔", 3, 0), ("Evaluar", 3, 3)
    ]

    for (texto, fila, col) in botones:
        if texto == "Evaluar":
            tk.Button(root, bg="#EF8BBD", font=("Arial", 11), text=texto, width=5, height=2, command=evaluar).grid(row=fila, column=col, pady=5)
        elif texto == "Borrar":
            tk.Button(root, bg="#A183E2", font=("Arial", 11), text=texto, width=6, height=2, command=lambda: pantalla_var.set("")).grid(row=fila, column=col, pady=5)
        else:
            tk.Button(root, bg="#A183E2", font=("Arial", 11), text=texto, width=6, height=2, command=lambda t=texto: insertar(t)).grid(row=fila, column=col, pady=5)

    root.mainloop()

calculadora()