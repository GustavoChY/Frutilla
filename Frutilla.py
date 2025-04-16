import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from numpy.polynomial.polynomial import Polynomial
from sklearn.linear_model import LinearRegression
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ===============================
# FUNCIONES DE INTERPOLACIÓN
# ===============================

def newton_interpolation(x, y, x_interp):
    n = len(x)
    coef = np.copy(y)
    for j in range(1, n):
        coef[j:] = (coef[j:] - coef[j - 1:-1]) / (x[j:] - x[:n - j])
    
    def newton_poly(x0):
        result = coef[0]
        product = 1.0
        for i in range(1, n):
            product *= (x0 - x[i - 1])
            result += coef[i] * product
        return result

    return np.array([newton_poly(x0) for x0 in x_interp])

def lagrange_interpolation(x, y, x_interp):
    def lagrange_single(x0):
        total = 0
        n = len(x)
        for i in range(n):
            term = y[i]
            for j in range(n):
                if i != j:
                    term *= (x0 - x[j]) / (x[i] - x[j])
            total += term
        return total
    return np.array([lagrange_single(x0) for x0 in x_interp])

def spline_interpolation(x, y, x_interp):
    cs = CubicSpline(x, y)
    return cs(x_interp)

def linear_regression(x, y, x_interp):
    coeffs = np.polyfit(x, y, 1)
    return np.polyval(coeffs, x_interp)



# Initialize global variables with default data

dias_validos = np.array([1, 3, 6, 12,13,14,16, 18, 20,24])  # Excluye 9 y 15
alturas_validos = np.array([0.5, 1.2, 3.0, 7.5,8.2,8.8,9.7, 10.6, 11.3,12.2])  # Solo datos conocidos

dias_estimados = np.array([9, 15])  # Aquí pedimos estimar
# Datos completos para mostrar al usuario
datos_completos = [
    (1, 0.5), (2, 0.8), (3, 1.2), (4, 1.7), (5, 2.3),
    (6, 3.0), (7, 3.8), (8, 4.5), (9, 5.3), (10, 6.0),
    (11, 6.8), (12, 7.5), (13, 8.2), (14, 8.8), (15, 9.3),
    (16, 9.7), (17, 10.2), (18, 10.6), (19, 11.0), (20, 11.3),
    (21, 11.6), (22, 11.8), (23, 12), (24, 12.2)
]

def mostrar_datos_completos():
    texto = "Día\tAltura (cm)\n" + "\n".join(f"{dia}\t{altura}" for dia, altura in datos_completos)
    messagebox.showinfo("Datos Originales", texto)

def ejecutar_interpolacion():
    global dias_validos, alturas_validos, dias_estimados

    try:
        dias_str = entry_dias.get().split(',')
        alturas_str = entry_alturas.get().split(',')
        estimar_str = entry_estimar.get().split(',')

        dias_validos = np.array([float(d.strip()) for d in dias_str])
        alturas_validos = np.array([float(a.strip()) for a in alturas_str])
        dias_estimados = np.array([float(e.strip()) for e in estimar_str])

        if len(dias_validos) != len(alturas_validos):
            messagebox.showerror("Error", "La cantidad de días y alturas debe ser la misma.")
            return

        # Aplicar métodos
        newton_result = newton_interpolation(dias_validos, alturas_validos, dias_estimados)
        lagrange_result = lagrange_interpolation(dias_validos, alturas_validos, dias_estimados)
        spline_result = spline_interpolation(dias_validos, alturas_validos, dias_estimados)
        regression_result = linear_regression(dias_validos, alturas_validos, dias_estimados)

        # Mostrar resultados en la tabla
        resultados = {
            "Newton": newton_result,
            "Lagrange": lagrange_result,
            "Spline": spline_result,
            "Regresión Lineal": regression_result
        }
        actualizar_tabla(resultados)
        actualizar_grafico()

    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese números válidos separados por comas.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

def actualizar_tabla(resultados):
    tabla.heading("Día 1", text=f"Día {int(dias_estimados[0])}" if len(dias_estimados) > 0 else "Día 1")
    tabla.heading("Día 2", text=f"Día {int(dias_estimados[1])}" if len(dias_estimados) > 1 else "Día 2")

    # Limpiar tabla anterior
    for item in tabla.get_children():
        tabla.delete(item)

    # Insertar nuevos resultados
    for metodo, valores in resultados.items():
        row = [metodo] + [f"{v:.2f}" for v in valores]
        tabla.insert("", tk.END, values=row)

def actualizar_grafico():
    global dias_validos, alturas_validos, dias_estimados
    if not hasattr(actualizar_grafico, 'fig') or not plt.fignum_exists(actualizar_grafico.fig.number):
        actualizar_grafico.fig, actualizar_grafico.ax = plt.subplots(figsize=(10, 6))
    else:
        actualizar_grafico.ax.clear()

    if len(dias_validos) > 1: # Ensure there are enough points for linspace
        dias_todos = np.linspace(np.min(dias_validos), np.max(dias_validos), 200)

        # Calcular curvas interpoladas para graficar
        newton_curve = newton_interpolation(dias_validos, alturas_validos, dias_todos)
        lagrange_curve = lagrange_interpolation(dias_validos, alturas_validos, dias_todos)
        spline_curve = spline_interpolation(dias_validos, alturas_validos, dias_todos)
        regression_curve = linear_regression(dias_validos, alturas_validos, dias_todos)

        # Graficar
        actualizar_grafico.ax.plot(dias_validos, alturas_validos, 'o', label='Datos conocidos')
        actualizar_grafico.ax.plot(dias_estimados, newton_interpolation(dias_validos, alturas_validos, dias_estimados), 's', label='Newton (Estimado)')
       # actualizar_grafico.ax.plot(dias_todos, newton_curve, '--', label='Newton (Curva)')
        actualizar_grafico.ax.plot(dias_estimados, lagrange_interpolation(dias_validos, alturas_validos, dias_estimados), '^', label='Lagrange (Estimado)')
        #actualizar_grafico.ax.plot(dias_todos, lagrange_curve, '--', label='Lagrange (Curva)')
        actualizar_grafico.ax.plot(dias_estimados, spline_interpolation(dias_validos, alturas_validos, dias_estimados), 'x', label='Spline (Estimado)')
        #actualizar_grafico.ax.plot(dias_todos, spline_curve, '--', label='Spline (Curva)')
        actualizar_grafico.ax.plot(dias_estimados, linear_regression(dias_validos, alturas_validos, dias_estimados), 'd', label='Regresión (Estimado)')
        #actualizar_grafico.ax.plot(dias_todos, regression_curve, '--', label='Regresión (Línea)')

        actualizar_grafico.ax.set_title("Interpolación de crecimiento de planta de frutilla")
        actualizar_grafico.ax.set_xlabel("Día")
        actualizar_grafico.ax.set_ylabel("Altura (cm)")
        actualizar_grafico.ax.legend()
        actualizar_grafico.ax.grid(True)
        actualizar_grafico.fig.tight_layout()
        plt.draw()
    else:
        # Handle the case where there are not enough data points to plot
        actualizar_grafico.ax.clear()
        actualizar_grafico.ax.text(0.5, 0.5, "Ingrese al menos dos datos conocidos para graficar.", ha='center', va='center')
        plt.draw()


# ===============================
# CONFIGURACIÓN DE LA VENTANA PRINCIPAL
# ===============================

ventana = tk.Tk()
ventana.title("Interpolación de Crecimiento")

# Etiquetas y campos de entrada (USING GRID)
ttk.Label(ventana, text="Días conocidos (separados por coma):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_dias = ttk.Entry(ventana, width=50)
entry_dias.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
entry_dias.insert(0, ", ".join(map(str, dias_validos))) # Set default values

ttk.Label(ventana, text="Alturas conocidas (separadas por coma):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
entry_alturas = ttk.Entry(ventana, width=50)
entry_alturas.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
entry_alturas.insert(0, ", ".join(map(str, alturas_validos))) # Set default values

ttk.Label(ventana, text="Días a estimar (separados por coma):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_estimar = ttk.Entry(ventana, width=50)
entry_estimar.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
entry_estimar.insert(0, ", ".join(map(str, dias_estimados))) # Set default values

# Botón para ejecutar la interpolación (USING GRID)
btn_ejecutar = ttk.Button(ventana, text="Ejecutar Interpolación", command=ejecutar_interpolacion)
btn_mostrar_datos = ttk.Button(ventana, text="Ver Datos Completos", command=mostrar_datos_completos)
btn_mostrar_datos.grid(row=3, column=1, sticky="e", padx=5)

btn_ejecutar.grid(row=3, column=0, columnspan=2, pady=10)

# ===============================
# TABLA DE RESULTADOS (USING GRID)
# ===============================

ttk.Label(ventana, text="Resultados de Interpolación:").grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")

tabla = ttk.Treeview(ventana, columns=("Método", "Día 1", "Día 2"))
tabla.heading("#0", text="")
tabla.heading("Método", text="Método")

tabla.column("#0", width=0, stretch=tk.NO)
tabla.column("Método", anchor=tk.W, width=150)
tabla.column("Día 1", anchor=tk.CENTER, width=100)
tabla.column("Día 2", anchor=tk.CENTER, width=100)
tabla.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# ===============================
# GRÁFICO MATPLOTLIB (USING GRID)
# ===============================

fig, ax = plt.subplots(figsize=(10, 6))
canvas = FigureCanvasTkAgg(fig, master=ventana)  # Use FigureCanvasTkAgg
widget_canvas = canvas.get_tk_widget()
widget_canvas.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

# Configurar el comportamiento de expansión de la grilla
ventana.grid_columnconfigure(1, weight=1)
ventana.grid_rowconfigure(5, weight=1)
ventana.grid_rowconfigure(6, weight=1) # Make the plot area expandable

actualizar_grafico.fig = fig # Store the figure for the update function
actualizar_grafico.ax = ax




# Initialize the plot with the default data
actualizar_grafico()

# Ejecutar la interfaz gráfica
ventana.mainloop()
