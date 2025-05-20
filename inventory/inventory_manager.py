import sqlite3
import tkinter as tk
from tkinter import ttk

def get_connection():
    """Devuelve una conexión a la base de datos."""
    return sqlite3.connect("inventory.db")
def get_low_stock_products(threshold):
    """
    Devuelve una lista de tuplas (nombre_producto, stock)
    con productos cuyo stock es menor que 'threshold'.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT name, stock FROM products WHERE stock < ?"
        cursor.execute(query, (threshold,))
        results = cursor.fetchall()
        return results
    finally:
        conn.close()

class InventoryManager:

    def __init__(self):
        pass  # Ya no necesitas mantener un inventario simulado

    def get_low_stock_products(self, threshold):
        """
        Devuelve una lista de tuplas (nombre_producto, stock)
        con productos cuyo stock es menor que 'threshold', usando la base de datos real.
        """
        conn = sqlite3.connect("inventory.db")
        try:
            cursor = conn.cursor()
            query = "SELECT name, stock FROM products WHERE stock < ?"
            cursor.execute(query, (threshold,))
            results = cursor.fetchall()
            return results
        finally:
            conn.close()

def add_supplier(name, contact):
    """
    Añade un nuevo proveedor a la base de datos.
    """
    if not name or not contact:
        raise ValueError("El nombre y contacto del proveedor son obligatorios.")
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "INSERT INTO suppliers (name, contact) VALUES (?, ?)"
        cursor.execute(query, (name, contact))
        conn.commit()
    finally:
        conn.close()

def list_suppliers():
    """
    Devuelve una lista de todos los proveedores.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT id, name, contact FROM suppliers"
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()

def delete_supplier(supplier_id):
    """
    Elimina un proveedor de la base de datos basado en su ID.
    """
    if not isinstance(supplier_id, int):
        raise ValueError("El ID del proveedor debe ser un entero.")
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "DELETE FROM suppliers WHERE id = ?"
        cursor.execute(query, (supplier_id,))
        conn.commit()
    finally:
        conn.close()

def update_supplier(supplier_id, name, contact):
    """
    Actualiza la información de un proveedor.
    """
    if not isinstance(supplier_id, int) or not name or not contact:
        raise ValueError("ID, nombre y contacto son obligatorios y deben ser válidos.")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "UPDATE suppliers SET name = ?, contact = ? WHERE id = ?"
        cursor.execute(query, (name, contact, supplier_id))
        conn.commit()
    finally:
        conn.close()

def delete_product(product_id):
    """
    Elimina un producto del inventario basado en su ID.
    """
    if not isinstance(product_id, int):
        raise ValueError("El ID del producto debe ser un entero.")
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "DELETE FROM products WHERE id = ?"
        cursor.execute(query, (product_id,))
        conn.commit()
    finally:
        conn.close()

def list_products():
    """
    Devuelve una lista de todos los productos en el inventario.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT id, name, stock, category FROM products"
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()

def add_product(name, stock, category):
    """
    Agrega un nuevo producto a la base de datos.
    """
    if not name or not category or not isinstance(stock, int) or stock < 0:
        raise ValueError("Nombre, categoría y stock deben ser válidos y no vacíos.")
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, stock, category)
            VALUES (?, ?, ?)
        """, (name, stock, category))
        conn.commit()
    finally:
        conn.close()

def register_stock_exit(product_id, quantity):
    """
    Registra la salida de stock de un producto.
    """
    if not isinstance(product_id, int) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("ID y cantidad deben ser enteros válidos y cantidad mayor a cero.")

    conn = get_connection()
    try:
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
    finally:
        conn.close()

def get_movements_in_date_range(start_date, end_date):
    """
    Obtiene los movimientos entre un rango de fechas.
    """
    if not start_date or not end_date:
        raise ValueError("Fecha de inicio y fecha fin son requeridas en formato YYYY-MM-DD.")
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, p.name, m.quantity, m.type, m.date
            FROM movements m
            JOIN products p ON m.product_id = p.id
            WHERE date(m.date) BETWEEN date(?) AND date(?)
            ORDER BY m.date
        """, (start_date, end_date))
        return cursor.fetchall()
    finally:
        conn.close()

def get_top_selling_products(limit=5):
    """
    Obtiene los productos más vendidos limitando el número de resultados.
    """
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("El límite debe ser un entero positivo.")
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT products.name, SUM(movements.quantity) as total_vendida
            FROM movements
            JOIN products ON movements.product_id = products.id
            WHERE movements.type = 'exit'
            GROUP BY products.name
            ORDER BY total_vendida DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    finally:
        conn.close()

def show_top_selling_products(self):
    """
    Muestra una ventana con los productos más vendidos.
    """
    top_products = get_top_selling_products()

    window = tk.Toplevel(self.root)
    window.title("Productos Más Vendidos")
    window.configure(bg="#00796b")

    ttk.Label(window, text="📊 Productos Más Vendidos", style="Header.TLabel").pack(pady=20)

    for nombre, cantidad in top_products:
        ttk.Label(window, text=f"{nombre} - Vendidos: {cantidad}", style="TLabel").pack(pady=5)

    ttk.Button(window, text="Cerrar", command=window.destroy).pack(pady=20)

def get_movements(product_id=None, category=None, supplier=None, movement_type=None, start_date=None, end_date=None):
    """
    Obtiene movimientos con filtros avanzados, mostrando nombres reales de proveedores.
    """
    connection = None
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

        cursor.execute(query, parameters)
        return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return []
    finally:
        if connection:
            connection.close()

def initialize_database():
    """
    Crea las tablas necesarias si no existen.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Crear tabla 'suppliers' si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL
        );
        """)
        # Crear tabla 'products' si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            category TEXT NOT NULL
        );
        """)
        # Crear tabla 'movements' si no existe
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            movement_type TEXT NOT NULL CHECK(movement_type IN ('entry', 'exit')),
            supplier_id INTEGER,
            date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id),
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
        );
        """)
        conn.commit()
    finally:
        conn.close()

def delete_product_and_related_data(product_id):
    """
    Elimina un producto del inventario y todos los datos relacionados (stock y movimientos).
    """
    if not isinstance(product_id, int):
        raise ValueError("El ID del producto debe ser un entero.")

    conn = get_connection()
    try:
        cursor = conn.cursor()

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
        conn.commit()
        print(f"Producto con ID {product_id} y sus datos relacionados eliminados correctamente.")
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
    finally:
        conn.close()

# Inicializar la base de datos al cargar el módulo
initialize_database()

