import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from database import inicializar_db
from dashboard import Dashboard

class Login(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Acceso al Sistema")
        self.geometry("400x450")
        
        ctk.CTkLabel(self, text="SISTEMA BILLAR", font=("Arial", 24, "bold")).pack(pady=40)
        
        self.ent_user = ctk.CTkEntry(self, placeholder_text="Usuario", width=200)
        self.ent_user.pack(pady=10)
        
        self.ent_pass = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*", width=200)
        self.ent_pass.pack(pady=10)
        
        ctk.CTkButton(self, text="Entrar", width=200, command=self.intentar_login).pack(pady=40)

    def intentar_login(self):
        u = self.ent_user.get()
        p = self.ent_pass.get()
        
        conn = sqlite3.connect("billar.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM usuarios WHERE usuario=? AND password=?", (u, p))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            self.destroy()
            # Pasamos el nombre real del usuario al Dashboard
            Dashboard(resultado[0]).mainloop()
        else:
            messagebox.showerror("Error", "Usuario o clave incorrectos")

if __name__ == "__main__":
    inicializar_db()
    app = Login()
    app.mainloop()
