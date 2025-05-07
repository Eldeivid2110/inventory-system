import sqlite3

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

    # Crear tabla de movimientos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            type TEXT NOT NULL, -- 'entry' o 'exit'
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
        # Agregar la columna 'category' si no existe
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN category TEXT DEFAULT 'General'")
            print("Columna 'category' añadida a la tabla 'products'.")
        except sqlite3.OperationalError as e:
            print(f"Error al añadir la columna 'category': {e}")

    conn.commit()
    conn.close()

def check_and_add_column(db_path, table_name, column_name, column_definition):
    """Verifica si la columna existe y, si no, la agrega."""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Obtener las columnas existentes de la tabla
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]

    # Si la columna no existe, agregarla
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition};")
        print(f"Columna '{column_name}' agregada a la tabla '{table_name}'.")

    connection.commit()
    connection.close()

# Llamar a la función para agregar la columna 'movement_type'
check_and_add_column("inventory.db", "movements", "movement_type", "TEXT")

def update_movements():
    """
    Actualiza datos faltantes en la tabla movements.
    """
    try:
        # Conectar a la base de datos
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()

        # Actualizar valores faltantes en la columna category
        cursor.execute("UPDATE movements SET category = 'Electronics' WHERE category IS NULL;")

        # Obtener el ID del proveedor predeterminado
        cursor.execute("SELECT id FROM suppliers WHERE name = 'Default Supplier';")
        default_supplier = cursor.fetchone()
        
        if default_supplier is None:
            raise ValueError("El proveedor 'Default Supplier' no existe en la tabla suppliers.")

        default_supplier_id = default_supplier[0]

        # Actualizar valores faltantes en la columna supplier_id
        cursor.execute("UPDATE movements SET supplier_id = ? WHERE supplier_id IS NULL;", (default_supplier_id,))

        # Actualizar valores faltantes en la columna movement_type
        cursor.execute("UPDATE movements SET movement_type = 'entry' WHERE movement_type IS NULL;")

        # Confirmar los cambios
        connection.commit()
        print("Datos actualizados correctamente.")

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
    except ValueError as ve:
        print(f"Error: {ve}")
    finally:
        # Asegurarse de cerrar la conexión
        if connection:
            connection.close()

# Ejecutar la función
update_movements()

def update_product_names():
    """Rellena la columna 'product_name' en la tabla 'movements'."""
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    # Suponiendo que tienes una tabla 'products' con 'id' y 'name'
    cursor.execute("""
    UPDATE movements
    SET product_name = (
        SELECT name
        FROM products
        WHERE products.id = movements.product_id
    )
    WHERE product_name IS NULL;
    """)

    connection.commit()
    connection.close()
    print("Nombres de productos actualizados correctamente.")

# Ejecutar la función
update_product_names()

import sqlite3

def add_default_supplier():
    """
    Agrega un proveedor predeterminado si no existe en la tabla suppliers.
    """
    try:
        # Conectar a la base de datos
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()

        # Verificar si el proveedor predeterminado ya existe
        cursor.execute("SELECT id FROM suppliers WHERE name = 'Default Supplier';")
        supplier = cursor.fetchone()

        if supplier is None:
            # Insertar el proveedor predeterminado con un valor válido para contact
            cursor.execute("""
                INSERT INTO suppliers (name, contact) VALUES ('Default Supplier', 'No contact provided');
            """)
            connection.commit()
            print("Proveedor predeterminado agregado correctamente.")
        else:
            print("El proveedor predeterminado ya existe.")

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
    finally:
        # Asegurarse de cerrar la conexión
        if connection:
            connection.close()

# Ejecutar la función
add_default_supplier()

def update_movements_with_existing_supplier():
    """
    Asigna un proveedor existente a los movimientos con supplier_id NULL.
    """
    try:
        # Conectar a la base de datos
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()

        # Verificar si existe el proveedor deseado
        cursor.execute("SELECT id FROM suppliers WHERE name = 'Electronics Inc';")
        supplier = cursor.fetchone()

        if supplier is None:
            raise ValueError("El proveedor 'Electronics Inc' no existe en la tabla suppliers.")

        supplier_id = supplier[0]

        # Actualizar movimientos con supplier_id NULL
        cursor.execute("""
            UPDATE movements
            SET supplier_id = ?
            WHERE supplier_id IS NULL;
        """, (supplier_id,))

        # Confirmar los cambios
        connection.commit()
        print("Movimientos actualizados correctamente.")

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
    except ValueError as ve:
        print(f"Error: {ve}")
    finally:
        # Asegurarse de cerrar la conexión
        if connection:
            connection.close()

# Ejecutar la función
update_movements_with_existing_supplier()