import customtkinter as ctk
from datetime import datetime
import sqlite3
from tkinter import messagebox

class Mesa(ctk.CTkFrame):
    def __init__(self, master, numero, es_vip=False):
        super().__init__(master, border_width=2)
        self.numero = numero
        self.es_vip = es_vip
        self.precio_hora = 45.0 if es_vip else 23.0
        self.activa = False
        self.inicio = None

        # Interfaz de la mesa
        self.lbl_titulo = ctk.CTkLabel(self, text=f"MESA {numero}" + (" (VIP)" if es_vip else ""), font=("Arial", 16, "bold"))
        self.lbl_titulo.pack(pady=5)
        
        self.lbl_status = ctk.CTkLabel(self, text="LIBRE", text_color="green", font=("Arial", 12, "bold"))
        self.lbl_status.pack()

        self.lbl_reloj = ctk.CTkLabel(self, text="00:00 | 0.00 Bs")
        self.lbl_reloj.pack(pady=5)

        self.btn = ctk.CTkButton(self, text="Abrir", command=self.click_mesa)
        self.btn.pack(pady=10, padx=10)

    def click_mesa(self):
        if not self.activa:
            self.activa = True
            self.inicio = datetime.now()
            self.configure(fg_color="#441111") # Rojo
            self.lbl_status.configure(text="JUGANDO", text_color="red")
            self.btn.configure(text="Cobrar", fg_color="darkred")
            self.actualizar()
        else:
            self.ventana_cobro()

    def actualizar(self):
        if self.activa:
            transcurrido = datetime.now() - self.inicio
            minutos = int(transcurrido.total_seconds() / 60)
            monto = (minutos / 60) * self.precio_hora
            self.lbl_reloj.configure(text=f"{minutos} min | {monto:.2f} Bs")
            self.after(30000, self.actualizar) # Actualiza cada 30 seg

    def ventana_cobro(self):
        ahora = datetime.now()
        minutos_reales = int((ahora - self.inicio).total_seconds() / 60)
        
        # LÓGICA DE REDONDEO (Decena más cercana)
        unidad = minutos_reales % 10
        minutos_redondeados = minutos_reales - unidad if unidad < 5 else minutos_reales + (10 - unidad)
        if minutos_redondeados == 0 and minutos_reales > 0: minutos_redondeados = 10
        
        monto = round((minutos_redondeados / 60) * self.precio_hora, 2)

        v_pago = ctk.CTkToplevel(self)
        v_pago.title("Cobro")
        v_pago.geometry("300x400")
        v_pago.attributes("-topmost", True)

        ctk.CTkLabel(v_pago, text=f"MESA {self.numero}", font=("Arial", 18, "bold")).pack(pady=10)
        ctk.CTkLabel(v_pago, text=f"Minutos: {minutos_reales} (Cobrados: {minutos_redondeados})").pack()
        ctk.CTkLabel(v_pago, text=f"{monto} Bs", font=("Arial", 30, "bold"), text_color="yellow").pack(pady=20)

        ctk.CTkButton(v_pago, text="Efectivo", fg_color="green", command=lambda: self.finalizar(monto, minutos_redondeados, "Efectivo", v_pago)).pack(pady=5)
        ctk.CTkButton(v_pago, text="QR", fg_color="blue", command=lambda: self.finalizar(monto, minutos_redondeados, "QR", v_pago)).pack(pady=5)

    def finalizar(self, total, minutos, metodo, ventana):
        conn = sqlite3.connect("billar.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ventas (mesa, fecha, minutos_cobrados, total, metodo_pago) VALUES (?,?,?,?,?)",
                       (f"Mesa {self.numero}", datetime.now().strftime("%Y-%m-%d %H:%M"), minutos, total, metodo))
        conn.commit()
        conn.close()
        ventana.destroy()
        self.resetear()

    def resetear(self):
        self.activa = False
        self.configure(fg_color="transparent")
        self.lbl_status.configure(text="LIBRE", text_color="green")
        self.btn.configure(text="Abrir", fg_color=["#3B8ED0", "#1F6AA5"])
        self.lbl_reloj.configure(text="00:00 | 0.00 Bs")

def abrir_dashboard():
    app = ctk.CTk()
    app.title("Dashboard Billar")
    app.geometry("1000x700")
    
    frame_mesas = ctk.CTkFrame(app)
    frame_mesas.pack(pady=20, padx=20, fill="both", expand=True)

    for i in range(1, 10):
        es_vip = (i == 9)
        m = Mesa(frame_mesas, i, es_vip)
        m.grid(row=(i-1)//3, column=(i-1)%3, padx=15, pady=15, sticky="nsew")
    
    frame_mesas.grid_columnconfigure((0,1,2), weight=1)
    app.mainloop()
