import sqlite3

def inicializar_db():
    conn = sqlite3.connect("billar.db")
    cursor = conn.cursor()
    
    # Usuarios para el Login
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        usuario TEXT UNIQUE,
        password TEXT)''')

    # Registro de ventas con método de pago
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mesa TEXT,
        fecha TEXT,
        minutos_cobrados INTEGER,
        total REAL,
        metodo_pago TEXT)''')

    # Usuario por defecto: admin / clave: 1234
    cursor.execute("INSERT OR IGNORE INTO usuarios (nombre, usuario, password) VALUES (?, ?, ?)",
                   ("Admin", "admin", "1234"))
    
    conn.commit()
    conn.close()
    print("Base de datos lista.")

if __name__ == "__main__":
    inicializar_db()
