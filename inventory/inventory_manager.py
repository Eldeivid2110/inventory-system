from inventory.database import get_connection
import sqlite3


# Conexión a la base de datos
connection = sqlite3.connect("inventory.db")
cursor = connection.cursor()

def add_supplier(name, contact):
    """
    Añade un nuevo proveedor a la base de datos.
    """
    query = "INSERT INTO suppliers (name, contact) VALUES (?, ?)"
    cursor.execute(query, (name, contact))
    connection.commit()

def list_suppliers():
    """
    Devuelve una lista de todos los proveedores.
    """
    query = "SELECT id, name, contact FROM suppliers"
    cursor.execute(query)
    return cursor.fetchall()

def delete_supplier(supplier_id):
    """
    Elimina un proveedor de la base de datos basado en su ID.
    """
    query = "DELETE FROM suppliers WHERE id = ?"
    cursor.execute(query, (supplier_id,))
    connection.commit()

def update_supplier(supplier_id, name, contact):
    """
    Actualiza la información de un proveedor.
    """
    query = "UPDATE suppliers SET name = ?, contact = ? WHERE id = ?"
    cursor.execute(query, (name, contact, supplier_id))
    connection.commit()

# Conexión a la base de datos
connection = sqlite3.connect("inventory.db")
cursor = connection.cursor()

def delete_product(product_id):
    """
    Elimina un producto del inventario basado en su ID.
    """
    query = "DELETE FROM products WHERE id = ?"
    cursor.execute(query, (product_id,))
    connection.commit()

def list_products():
    """
    Devuelve una lista de todos los productos en el inventario.
    """
    query = "SELECT id, name, stock, category FROM products"
    cursor.execute(query)
    return cursor.fetchall()

# Otros métodos como add_product, register_stock_exit, etc., permanecen igual...

def add_product(name, stock, category):
    """Agrega un nuevo producto a la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO products (name, stock, category)
        VALUES (?, ?, ?)
    """, (name, stock, category))

    conn.commit()
    conn.close()

def list_products():
    """Obtiene todos los productos de la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, stock, category FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def register_stock_exit(product_id, quantity):
    """Registra la salida de stock de un producto."""
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar el stock actual del producto
    cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    if not result:
        raise ValueError("El producto no existe.")
    
    current_stock = result[0]
    if quantity > current_stock:
        raise ValueError("No hay suficiente stock disponible.")

    # Actualizar el stock del producto
    new_stock = current_stock - quantity
    cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))

    # Registrar el movimiento de salida
    cursor.execute("""
        INSERT INTO movements (product_id, quantity, type)
        VALUES (?, ?, 'exit')
    """, (product_id, quantity))

    conn.commit()
    conn.close()

def get_movements_in_date_range(start_date, end_date):
    """Obtiene los movimientos entre un rango de fechas."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.id, p.name, m.quantity, m.type, m.date
        FROM movements m
        JOIN products p ON m.product_id = p.id
        WHERE date(m.date) BETWEEN date(?) AND date(?)
        ORDER BY m.date
    """, (start_date, end_date))

    movements = cursor.fetchall()
    conn.close()
    return movements

def get_top_selling_products(limit=5):
    """Obtiene los productos más vendidos (mayor cantidad de salidas)."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.name, SUM(m.quantity) as total_sold
        FROM movements m
        JOIN products p ON m.product_id = p.id
        WHERE m.type = 'exit'
        GROUP BY p.id
        ORDER BY total_sold DESC
        LIMIT ?
    """, (limit,))

    top_products = cursor.fetchall()
    conn.close()
    return top_products

def get_low_stock_products(threshold=10):
    """Obtiene los productos con un stock por debajo del umbral."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, stock
        FROM products
        WHERE stock < ?
        ORDER BY stock
    """, (threshold,))

    low_stock_products = cursor.fetchall()
    conn.close()
    return low_stock_products

def get_movements(product_id=None, category=None, supplier=None, movement_type=None, start_date=None, end_date=None):
    """
    Obtiene movimientos con filtros avanzados, mostrando nombres reales de proveedores.
    
    Parámetros:
        - product_id (int or None): ID del producto para filtrar (opcional).
        - category (str or None): Categoría del producto para filtrar (opcional).
        - supplier (str or None): Nombre del proveedor para filtrar (opcional).
        - movement_type (str or None): Tipo de movimiento ("entry" o "exit") para filtrar (opcional).
        - start_date (str or None): Fecha de inicio para filtrar movimientos (formato YYYY-MM-DD, opcional).
        - end_date (str or None): Fecha de fin para filtrar movimientos (formato YYYY-MM-DD, opcional).
    
    Retorna:
        - List[Tuple]: Una lista de tuplas donde cada tupla representa un movimiento.
    """
    try:
        # Conectar a la base de datos
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()

        # Construir la consulta SQL con JOIN
        query = """
        SELECT m.id, p.name AS product_name, m.quantity, p.category, s.name AS supplier_name, 
               m.movement_type, m.date
        FROM movements AS m
        JOIN products AS p ON m.product_id = p.id
        JOIN suppliers AS s ON m.supplier_id = s.id
        WHERE 1=1
        """
        parameters = []

        # Aplicar filtros opcionales
        if product_id:
            query += " AND m.product_id = ?"
            parameters.append(product_id)
        if category:
            query += " AND LOWER(p.category) LIKE LOWER(?)"
            parameters.append(f"%{category}%")
        if supplier:
            query += " AND LOWER(s.name) LIKE LOWER(?)"
            parameters.append(f"%{supplier}%")
        if movement_type:
            query += " AND m.movement_type = ?"
            parameters.append(movement_type)
        if start_date:
            query += " AND m.date >= ?"
            parameters.append(start_date)
        if end_date:
            query += " AND m.date <= ?"
            parameters.append(end_date)

        # Ejecutar la consulta
        cursor.execute(query, parameters)
        movements = cursor.fetchall()
        return movements

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return []
    finally:
        # Asegurarse de cerrar la conexión
        if connection:
            connection.close()

def initialize_database():
    """Crea las tablas necesarias si no existen."""
    connection = sqlite3.connect("inventory.db")
    cursor = connection.cursor()

    # Crear tabla 'suppliers' si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT NOT NULL
    );
    """)

    # Puedes agregar otras tablas aquí si es necesario

    connection.commit()
    connection.close()

# Llama a esta función al inicio del programa
initialize_database()

def delete_product_and_related_data(product_id):
    """
    Elimina un producto del inventario y todos los datos relacionados (stock y movimientos).
    """
    try:
        # Conectar a la base de datos
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()

        # Verificar si el producto existe
        cursor.execute("SELECT * FROM products WHERE id = ?;", (product_id,))
        product = cursor.fetchone()

        if not product:
            print(f"El producto con ID {product_id} no existe.")
            return

        # Verificar si hay movimientos relacionados
        cursor.execute("SELECT COUNT(*) FROM movements WHERE product_id = ?;", (product_id,))
        movement_count = cursor.fetchone()[0]

        if movement_count > 0:
            print(f"El producto tiene {movement_count} movimientos relacionados. Estos serán eliminados.")

        # Eliminar movimientos relacionados
        cursor.execute("DELETE FROM movements WHERE product_id = ?;", (product_id,))

        # Eliminar el producto
        cursor.execute("DELETE FROM products WHERE id = ?;", (product_id,))

        # Confirmar los cambios
        connection.commit()
        print(f"Producto con ID {product_id} y sus datos relacionados eliminados correctamente.")

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
    finally:
        # Asegurarse de cerrar la conexión
        if connection:
            connection.close()