import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
# Importamos la clase Dashboard del archivo dashboard.py
from dashboard import Dashboard
from database import inicializar_db

class Login(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Acceso - Control de Billar")
        self.geometry("400x500")
        self.eval('tk::PlaceWindow . center') # Centrar ventana

        # Diseño
        ctk.CTkLabel(self, text="🎱", font=("Arial", 60)).pack(pady=(40, 10))
        ctk.CTkLabel(self, text="CONTROL DE BILLAR", font=("Arial", 24, "bold")).pack(pady=10)
        
        self.ent_user = ctk.CTkEntry(self, placeholder_text="Usuario", width=250, height=40)
        self.ent_user.pack(pady=20)
        
        self.ent_pass = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*", width=250, height=40)
        self.ent_pass.pack(pady=5)
        
        self.btn_login = ctk.CTkButton(self, text="ENTRAR", width=250, height=45, font=("Arial", 14, "bold"),
                                       command=self.intentar_login)
        self.btn_login.pack(pady=40)

    def intentar_login(self):
        u = self.ent_user.get()
        p = self.ent_pass.get()
        
        try:
            conn = sqlite3.connect("billar.db")
            cursor = conn.cursor()
            # Buscamos el nombre real del usuario que coincide con el login
            cursor.execute("SELECT nombre FROM usuarios WHERE usuario=? AND password=?", (u, p))
            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                nombre_usuario = resultado[0]
                self.destroy() # Cerramos el login
                # Abrimos el Dashboard pasando el nombre de quien entró
                app_dash = Dashboard(nombre_usuario)
                app_dash.mainloop()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        except Exception as e:
            messagebox.showerror("Error de DB", f"No se pudo conectar a la base de datos: {e}")

if __name__ == "__main__":
    # 1. Aseguramos que la base de datos exista antes de empezar
    inicializar_db()
    
    # 2. Iniciamos el Login
    app = Login()
    app.mainloop()
