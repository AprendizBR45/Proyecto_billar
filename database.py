import sqlite3

def inicializar_db():
    conn = sqlite3.connect("billar.db")
    cursor = conn.cursor()
    
    # Tabla de Usuarios: id, nombre, usuario, contraseña
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        usuario TEXT UNIQUE,
        password TEXT)''')

    # Tabla de Ventas: Guardamos quién hizo la venta (vendedor)
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mesa TEXT,
        fecha TEXT,
        minutos_reales INTEGER,
        minutos_cobrados INTEGER,
        total REAL,
        metodo_pago TEXT,
        vendedor TEXT)''')

    # Usuario administrador por defecto
    cursor.execute("INSERT OR IGNORE INTO usuarios (nombre, usuario, password) VALUES (?, ?, ?)",
                   ("Administrador", "admin", "1234"))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    inicializar_db()
