import customtkinter as ctk
from datetime import datetime
import sqlite3
from tkinter import messagebox

class Mesa(ctk.CTkFrame):
    def __init__(self, master, numero, es_vip, usuario_actual):
        super().__init__(master, border_width=2)
        self.numero = numero
        self.es_vip = es_vip
        self.usuario_actual = usuario_actual
        self.precio_hora = 45.0 if es_vip else 23.0
        self.activa = False
        self.inicio = None

        self.lbl_titulo = ctk.CTkLabel(self, text=f"MESA {numero}" + (" (VIP)" if es_vip else ""), font=("Arial", 16, "bold"))
        self.lbl_titulo.pack(pady=5)
        self.lbl_status = ctk.CTkLabel(self, text="LIBRE", text_color="green", font=("Arial", 12, "bold"))
        self.lbl_status.pack()
        self.lbl_reloj = ctk.CTkLabel(self, text="00:00 | 0.00 Bs")
        self.lbl_reloj.pack(pady=5)
        self.btn = ctk.CTkButton(self, text="Abrir Mesa", command=self.click_mesa)
        self.btn.pack(pady=10, padx=10)

    def click_mesa(self):
        if not self.activa:
            self.activa = True
            self.inicio = datetime.now()
            self.configure(fg_color="#441111")
            self.lbl_status.configure(text="JUGANDO", text_color="red")
            self.btn.configure(text="Cobrar", fg_color="darkred")
            self.actualizar_tiempo()
        else:
            self.ventana_cobro()

    def actualizar_tiempo(self):
        if self.activa:
            transcurrido = datetime.now() - self.inicio
            minutos = int(transcurrido.total_seconds() / 60)
            monto = (minutos / 60) * self.precio_hora
            self.lbl_reloj.configure(text=f"{minutos} min | {monto:.2f} Bs")
            self.after(30000, self.actualizar_tiempo)

    def ventana_cobro(self):
        ahora = datetime.now()
        minutos_reales = int((ahora - self.inicio).total_seconds() / 60)
        
        # Lógica de Redondeo 5 min
        unidad = minutos_reales % 10
        min_cobrados = minutos_reales - unidad if unidad < 5 else minutos_reales + (10 - unidad)
        if min_cobrados == 0 and minutos_reales > 0: min_cobrados = 10
        
        monto = round((min_cobrados / 60) * self.precio_hora, 2)

        v = ctk.CTkToplevel(self)
        v.title("Finalizar")
        v.geometry("300x400")
        v.attributes("-topmost", True)

        ctk.CTkLabel(v, text=f"COBRO MESA {self.numero}", font=("Arial", 18, "bold")).pack(pady=10)
        ctk.CTkLabel(v, text=f"Tiempo Real: {minutos_reales} min").pack()
        ctk.CTkLabel(v, text=f"Cobrando: {min_cobrados} min", text_color="cyan").pack()
        ctk.CTkLabel(v, text=f"{monto} Bs", font=("Arial", 35, "bold"), text_color="yellow").pack(pady=20)

        ctk.CTkButton(v, text="Efectivo 💵", fg_color="green", command=lambda: self.finalizar(monto, minutos_reales, min_cobrados, "Efectivo", v)).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(v, text="Pago QR 📱", fg_color="blue", command=lambda: self.finalizar(monto, minutos_reales, min_cobrados, "QR", v)).pack(pady=5, padx=20, fill="x")

    def finalizar(self, total, m_real, m_cobro, metodo, ventana):
        conn = sqlite3.connect("billar.db")
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO ventas (mesa, fecha, minutos_reales, minutos_cobrados, total, metodo_pago, vendedor) 
                          VALUES (?,?,?,?,?,?,?)""",
                       (f"Mesa {self.numero}", datetime.now().strftime("%Y-%m-%d %H:%M"), m_real, m_cobro, total, metodo, self.usuario_actual))
        conn.commit()
        conn.close()
        ventana.destroy()
        self.resetear()

    def resetear(self):
        self.activa = False
        self.configure(fg_color="transparent")
        self.lbl_status.configure(text="LIBRE", text_color="green")
        self.btn.configure(text="Abrir Mesa", fg_color=["#3B8ED0", "#1F6AA5"])
        self.lbl_reloj.configure(text="00:00 | 0.00 Bs")

class Dashboard(ctk.CTk):
    def __init__(self, usuario_nombre):
        super().__init__()
        self.usuario_nombre = usuario_nombre
        self.title(f"Billar Pro - Sesión: {usuario_nombre}")
        self.geometry("1100x750")

        # BARRA SUPERIOR
        self.top_bar = ctk.CTkFrame(self, height=50)
        self.top_bar.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(self.top_bar, text=f"👤 {usuario_nombre}", font=("Arial", 14, "bold")).pack(side="left", padx=20)
        
        ctk.CTkButton(self.top_bar, text="Cerrar Sesión", fg_color="#c0392b", width=100, command=self.logout).pack(side="right", padx=5)
        ctk.CTkButton(self.top_bar, text="Reporte", fg_color="#2980b9", width=100, command=self.ver_reporte).pack(side="right", padx=5)
        ctk.CTkButton(self.top_bar, text="Usuarios", fg_color="#8e44ad", width=100, command=self.gestionar_usuarios).pack(side="right", padx=5)

        # GRID DE MESAS
        self.grid_mesas = ctk.CTkFrame(self)
        self.grid_mesas.pack(expand=True, fill="both", padx=20, pady=20)

        for i in range(1, 10):
            m = Mesa(self.grid_mesas, i, (i==9), self.usuario_nombre)
            m.grid(row=(i-1)//3, column=(i-1)%3, padx=15, pady=15, sticky="nsew")
        self.grid_mesas.grid_columnconfigure((0,1,2), weight=1)

    def logout(self):
        self.destroy()
        from main import Login
        Login().mainloop()

    def ver_reporte(self):
        v = ctk.CTkToplevel(self)
        v.title("Caja del Día")
        v.geometry("400x450")
        v.attributes("-topmost", True)

        conn = sqlite3.connect("billar.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total) FROM ventas WHERE metodo_pago='Efectivo'")
        efectivo = cursor.fetchone()[0] or 0.0
        cursor.execute("SELECT SUM(total) FROM ventas WHERE metodo_pago='QR'")
        qr = cursor.fetchone()[0] or 0.0
        conn.close()

        ctk.CTkLabel(v, text="RESUMEN DE CAJA", font=("Arial", 20, "bold")).pack(pady=20)
        ctk.CTkLabel(v, text=f"Efectivo: {efectivo:.2f} Bs", font=("Arial", 16)).pack(pady=10)
        ctk.CTkLabel(v, text=f"Pago QR: {qr:.2f} Bs", font=("Arial", 16)).pack(pady=10)
        ctk.CTkLabel(v, text=f"TOTAL: {efectivo+qr:.2f} Bs", font=("Arial", 22, "bold"), text_color="green").pack(pady=30)

    def gestionar_usuarios(self):
        v = ctk.CTkToplevel(self)
        v.title("Crear Usuario")
        v.geometry("300x400")
        v.attributes("-topmost", True)

        ctk.CTkLabel(v, text="NUEVO USUARIO", font=("Arial", 16, "bold")).pack(pady=20)
        nom = ctk.CTkEntry(v, placeholder_text="Nombre Real")
        nom.pack(pady=5)
        user = ctk.CTkEntry(v, placeholder_text="Usuario Login")
        user.pack(pady=5)
        pas = ctk.CTkEntry(v, placeholder_text="Contraseña", show="*")
        pas.pack(pady=5)

        def guardar():
            try:
                conn = sqlite3.connect("billar.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO usuarios (nombre, usuario, password) VALUES (?,?,?)", (nom.get(), user.get(), pas.get()))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Usuario creado")
                v.destroy()
            except: messagebox.showerror("Error", "El usuario ya existe")

        ctk.CTkButton(v, text="Guardar", command=guardar).pack(pady=20)        
