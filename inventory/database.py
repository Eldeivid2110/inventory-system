import sqlite3
import hashlib

def connect():
    """Conecta a la base de datos y crea las tablas si no existen."""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    # Crear tabla de productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock INTEGER NOT NULL,
            category TEXT DEFAULT 'General'
        )
    """)

    # Crear tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Crear tabla de movimientos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            type TEXT NOT NULL, -- 'entry' o 'exit'
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            movement_type TEXT DEFAULT 'entry',
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)

    conn.commit()
    conn.close()

def get_connection():
    """Devuelve una conexión a la base de datos."""
    return sqlite3.connect("inventory.db")

def migrate():
    """Realiza migraciones necesarias en la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar si la columna 'category' existe en la tabla 'products'
    cursor.execute("PRAGMA table_info(products)")
    columns = [column[1] for column in cursor.fetchall()]
    if "category" not in columns:
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN category TEXT DEFAULT 'General'")
            print("Columna 'category' añadida a la tabla 'products'.")
        except sqlite3.OperationalError as e:
            print(f"Error al añadir la columna 'category': {e}")

    # Verificar si la columna 'movement_type' existe en la tabla 'movements'
    cursor.execute("PRAGMA table_info(movements)")
    columns = [column[1] for column in cursor.fetchall()]
    if "movement_type" not in columns:
        try:
            cursor.execute("ALTER TABLE movements ADD COLUMN movement_type TEXT DEFAULT 'entry'")
            print("Columna 'movement_type' añadida a la tabla 'movements'.")
        except sqlite3.OperationalError as e:
            print(f"Error al añadir la columna 'movement_type': {e}")

    conn.commit()
    conn.close()

def check_and_add_column(db_path, table_name, column_name, column_definition):
    """Verifica si la columna existe y, si no, la agrega."""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition};")
        print(f"Columna '{column_name}' agregada a la tabla '{table_name}'.")
    connection.commit()
    connection.close()

def update_movements():
    """
    Actualiza datos faltantes en la tabla movements.
    """
    try:
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()
        # Actualizar valores faltantes en la columna type
        cursor.execute("UPDATE movements SET type = 'entry' WHERE type IS NULL;")
        # Actualizar valores faltantes en la columna movement_type
        cursor.execute("UPDATE movements SET movement_type = 'entry' WHERE movement_type IS NULL;")
        connection.commit()
        print("Datos actualizados correctamente.")
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
    finally:
        if connection:
            connection.close()

def verify_user(username, password):
    """Verifica si el usuario y contraseña son correctos."""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def add_user(username, password):
    """Añade un usuario nuevo con la contraseña cifrada (SHA256)."""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        print(f"Usuario '{username}' añadido correctamente.")
    except sqlite3.IntegrityError:
        print("Usuario ya existe")
    conn.close()
    




def get_movements_with_product_names():
    """Devuelve movimientos junto al nombre del producto (usando JOIN)."""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            movements.id, 
            products.name, 
            movements.quantity, 
            movements.type, 
            movements.movement_type,
            movements.date
        FROM movements
        JOIN products ON movements.product_id = products.id
        ORDER BY movements.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows