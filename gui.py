import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from datetime import datetime  # Para manejar fechas
from inventory.inventory_manager import (
    add_product,
    list_products,
    register_stock_exit,
    get_low_stock_products,
    get_top_selling_products,
    get_movements,
    delete_product_and_related_data,
    add_supplier,
    list_suppliers,
    delete_supplier,
    update_supplier
)

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control de Inventarios")
        self.low_stock_threshold = 10  # Umbral inicial para notificaciones de bajo stock

    def create_main_menu(self):
        """Crea el menú principal con botones para cada operación."""
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Sistema de Control de Inventarios", font=("Arial", 16)).pack(pady=10)

        # Mostrar notificaciones de bajo stock
        self.show_low_stock_notification(frame)

        ttk.Button(frame, text="Agregar Producto", command=self.add_product_window, width=20).pack(pady=5)
        ttk.Button(frame, text="Eliminar Producto", command=self.delete_product_window, width=20).pack(pady=5)
        ttk.Button(frame, text="Listar Inventario", command=self.list_inventory_window, width=20).pack(pady=5)
        ttk.Button(frame, text="Registrar Salida de Stock", command=self.register_exit_window, width=20).pack(pady=5)
        ttk.Button(frame, text="Gestionar Proveedores", command=self.manage_suppliers_window, width=20).pack(pady=5)
        ttk.Button(frame, text="Historial de Movimientos", command=self.show_movements_window, width=20).pack(pady=5)
        ttk.Button(frame, text="Configurar Umbral Bajo Stock", command=self.configure_low_stock_threshold, width=25).pack(pady=5)
        ttk.Button(frame, text="Reportes y Estadísticas", command=self.generate_reports_window, width=20).pack(pady=5)
        ttk.Button(frame, text="Salir", command=self.root.quit, width=20).pack(pady=10)
     
def list_inventory_window(self):
    """Ventana para listar el inventario."""
    window = tk.Toplevel(self.root)
    window.title("Inventario")

    # Frame para la lista de productos
    frame = tk.Frame(window, padx=20, pady=20)
    frame.pack()

    tk.Label(frame, text="Inventario de Productos", font=("Arial", 16)).pack(pady=10)

    # Crear la tabla de inventario
    inventory_list = tk.Text(frame, width=50, height=20)
    inventory_list.pack(pady=10)

    def load_inventory():
        """Carga el inventario desde la base de datos."""
        inventory_list.delete('1.0', tk.END)  # Limpia la lista
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()

        cursor.execute("SELECT id, name, stock FROM products;")
        products = cursor.fetchall()
        connection.close()

        if products:
            for product in products:
                inventory_list.insert(tk.END, f"ID: {product[0]} | Nombre: {product[1]} | Stock: {product[2]}\n")
        else:
            inventory_list.insert(tk.END, "No hay productos en el inventario.\n")

    # Cargar el inventario al abrir la ventana
    load_inventory()

    ttk.Button(frame, text="Refrescar", command=load_inventory).pack(pady=5)
    ttk.Button(frame, text="Cerrar", command=window.destroy).pack(pady=5)


    def show_low_stock_notification(self, parent_frame):
        """Muestra una notificación si hay productos con bajo stock."""
        low_stock_products = get_low_stock_products(self.low_stock_threshold)
        tk.Label(parent_frame, text=f"⚙️ Umbral de Bajo Stock: {self.low_stock_threshold}", fg="blue").pack(pady=5)
        if low_stock_products:
            tk.Label(parent_frame, text="⚠️ Productos con bajo stock:", fg="red").pack(pady=5)
            for product in low_stock_products:
                product_label = f"- {product[1]} (Stock: {product[2]})"
                tk.Label(parent_frame, text=product_label, fg="red").pack(pady=2)
        else:
            tk.Label(parent_frame, text="✅ Todo el inventario está en buen estado.", fg="green").pack(pady=5)

    def configure_low_stock_threshold(self):
        """Permite al usuario configurar el umbral de stock bajo."""
        window = tk.Toplevel(self.root)
        window.title("Configurar Umbral de Stock Bajo")

        tk.Label(window, text="Umbral Actual:").grid(row=0, column=0, padx=10, pady=5)
        current_threshold_label = tk.Label(window, text=str(self.low_stock_threshold))
        current_threshold_label.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(window, text="Nuevo Umbral:").grid(row=1, column=0, padx=10, pady=5)
        new_threshold_entry = tk.Entry(window, width=10)
        new_threshold_entry.grid(row=1, column=1, padx=10, pady=5)

        def save_threshold():
            try:
                new_threshold = int(new_threshold_entry.get())
                if new_threshold < 1:
                    raise ValueError("El umbral debe ser mayor a 0.")
                self.low_stock_threshold = new_threshold
                messagebox.showinfo("Éxito", f"Umbral actualizado a {new_threshold}.")
                window.destroy()
                self.refresh_main_menu()
            except ValueError as e:
                messagebox.showerror("Error", f"Valor inválido: {e}")

        ttk.Button(window, text="Guardar", command=save_threshold).grid(row=2, columnspan=2, pady=10)

    def refresh_main_menu(self):
        """Refresca el menú principal para actualizar las notificaciones."""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_main_menu()

    def add_product_window(self):
        """Ventana para agregar un nuevo producto."""
        window = tk.Toplevel(self.root)
        window.title("Agregar Producto")

        tk.Label(window, text="Nombre del Producto:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(window, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(window, text="Stock Inicial:").grid(row=1, column=0, padx=10, pady=5)
        stock_entry = tk.Entry(window, width=30)
        stock_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(window, text="Categoría:").grid(row=2, column=0, padx=10, pady=5)
        category_entry = tk.Entry(window, width=30)
        category_entry.grid(row=2, column=1, padx=10, pady=5),

        
    
    

        def save_product():
            name = name_entry.get()
            stock = stock_entry.get()
            category = category_entry.get()
            if not name or not stock or not category:
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return

            try:
                stock = int(stock)
                add_product(name, stock, category)
                messagebox.showinfo("Éxito", f"Producto '{name}' agregado correctamente.")
                window.destroy()
            except ValueError:
                messagebox.showerror("Error", "El stock debe ser un número entero.")

        ttk.Button(window, text="Guardar", command=save_product).grid(row=3, columnspan=2, pady=10)

    def list_inventory_window(self):
        """Ventana para listar el inventario."""
        window = tk.Toplevel(self.root)
        window.title("Inventario")

        # Obtener los productos desde la base de datos
        products = list_products()

        # Crear la tabla para mostrar los productos
        tree = ttk.Treeview(window, columns=("ID", "Nombre", "Stock", "Categoría"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Stock", text="Stock")
        tree.heading("Categoría", text="Categoría")
        tree.pack(fill="both", expand=True)

        # Insertar los productos en la tabla
        for product in products:
            tree.insert("", "end", values=product)

        # Botón para cerrar la ventana
        ttk.Button(window, text="Cerrar", command=window.destroy).pack(pady=10)

    

    def register_exit_window(self):
        """Ventana para registrar salida de stock."""
        window = tk.Toplevel(self.root)
        window.title("Registrar Salida de Stock")

        tk.Label(window, text="ID del Producto:").grid(row=0, column=0, padx=10, pady=5)
        product_id_entry = tk.Entry(window, width=30)
        product_id_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(window, text="Cantidad:").grid(row=1, column=0, padx=10, pady=5)
        quantity_entry = tk.Entry(window, width=30)
        quantity_entry.grid(row=1, column=1, padx=10, pady=5)

        def save_exit():
            product_id = product_id_entry.get()
            quantity = quantity_entry.get()
            try:
                product_id = int(product_id)
                quantity = int(quantity)
                register_stock_exit(product_id, quantity)
                messagebox.showinfo("Éxito", f"Salida de {quantity} unidades registrada correctamente.")
                window.destroy()
            except ValueError:
                messagebox.showerror("Error", "ID y cantidad deben ser números enteros.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(window, text="Registrar", command=save_exit).grid(row=2, columnspan=2, pady=10)

    def manage_suppliers_window(self):
        """Ventana para gestionar proveedores."""
        window = tk.Toplevel(self.root)
        window.title("Gestionar Proveedores")

        # Tabla para mostrar los proveedores
        suppliers = list_suppliers()

        tree = ttk.Treeview(window, columns=("ID", "Nombre", "Contacto"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Contacto", text="Contacto")
        tree.pack(fill="both", expand=True)

        for supplier in suppliers:
            tree.insert("", "end", values=supplier)

        def add_supplier_window():
            """Ventana para añadir un nuevo proveedor."""
            supplier_window = tk.Toplevel(window)
            supplier_window.title("Añadir Proveedor")

            tk.Label(supplier_window, text="Nombre del Proveedor:").grid(row=0, column=0, padx=10, pady=5)
            name_entry = tk.Entry(supplier_window, width=30)
            name_entry.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(supplier_window, text="Contacto:").grid(row=1, column=0, padx=10, pady=5)
            contact_entry = tk.Entry(supplier_window, width=30)
            contact_entry.grid(row=1, column=1, padx=10, pady=5)

            def save_supplier():
                name = name_entry.get()
                contact = contact_entry.get()
                if not name or not contact:
                    messagebox.showerror("Error", "Todos los campos son obligatorios.")
                    return

                try:
                    add_supplier(name, contact)
                    messagebox.showinfo("Éxito", f"Proveedor '{name}' agregado correctamente.")
                    supplier_window.destroy()
                    self.refresh_suppliers_table(tree)
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo añadir el proveedor: {e}")

            ttk.Button(supplier_window, text="Guardar", command=save_supplier).grid(row=2, columnspan=2, pady=10)

        def delete_selected_supplier():
            """Elimina el proveedor seleccionado."""
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Advertencia", "Por favor, selecciona un proveedor para eliminar.")
                return

            # Obtener el ID del proveedor seleccionado
            supplier_id = tree.item(selected_item[0])["values"][0]

            # Confirmar antes de eliminar
            confirm = messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que deseas eliminar el proveedor con ID {supplier_id}?")
            if confirm:
                try:
                    delete_supplier(supplier_id)
                    tree.delete(selected_item)
                    messagebox.showinfo("Éxito", "Proveedor eliminado correctamente.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar el proveedor: {e}")

        ttk.Button(window, text="Añadir Proveedor", command=add_supplier_window).pack(side="left", padx=5, pady=10)
        ttk.Button(window, text="Eliminar Proveedor", command=delete_selected_supplier).pack(side="left", padx=5, pady=10)
        ttk.Button(window, text="Cerrar", command=window.destroy).pack(side="right", padx=5, pady=10)
        
         
    def show_movements_window(self):
        """Ventana mejorada para mostrar el historial de movimientos con filtros avanzados."""
        window = tk.Toplevel(self.root)
        window.title("Historial de Movimientos")

        # Etiquetas y campos de entrada para los filtros
        tk.Label(window, text="ID Producto:").grid(row=0, column=0, padx=10, pady=5)
        product_id_entry = tk.Entry(window, width=20)
        product_id_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(window, text="Categoría:").grid(row=1, column=0, padx=10, pady=5)
        category_entry = tk.Entry(window, width=20)
        category_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(window, text="Proveedor:").grid(row=2, column=0, padx=10, pady=5)
        supplier_entry = tk.Entry(window, width=20)
        supplier_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(window, text="Tipo Movimiento:").grid(row=3, column=0, padx=10, pady=5)
        movement_type_combo = ttk.Combobox(window, values=["", "entry", "exit"], width=18)
        movement_type_combo.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(window, text="Fecha Inicio:").grid(row=4, column=0, padx=10, pady=5)
        start_date_entry = tk.Entry(window, width=20)
        start_date_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(window, text="Fecha Fin:").grid(row=5, column=0, padx=10, pady=5)
        end_date_entry = tk.Entry(window, width=20)
        end_date_entry.grid(row=5, column=1, padx=10, pady=5)

        # Tabla para mostrar movimientos
        tree = ttk.Treeview(window, columns=("ID", "Producto", "Cantidad", "Categoría", "Proveedor", "Tipo", "Fecha"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Producto", text="Producto")
        tree.heading("Cantidad", text="Cantidad")
        tree.heading("Categoría", text="Categoría")
        tree.heading("Proveedor", text="Proveedor")
        tree.heading("Tipo", text="Tipo")
        tree.heading("Fecha", text="Fecha")
        tree.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Botón para aplicar filtros
        ttk.Button(
            window,
            text="Filtrar",
            command=lambda: self.load_movements(tree, product_id_entry, category_entry, supplier_entry, movement_type_combo, start_date_entry, end_date_entry)
        ).grid(row=6, column=0, columnspan=2, pady=10)

    def list_inventory_window(self):
     """Ventana para listar el inventario."""
    window = tk.Toplevel(self.root)
    window.title("Inventario")

    # Frame para la lista de productos
    frame = tk.Frame(window, padx=20, pady=20)
    frame.pack()

    tk.Label(frame, text="Inventario de Productos", font=("Arial", 16)).pack(pady=10)

    # Crear la tabla de inventario
    inventory_list = tk.Text(frame, width=50, height=20)
    inventory_list.pack(pady=10)

    def load_inventory():
        """Carga el inventario desde la base de datos."""
        inventory_list.delete('1.0', tk.END)  # Limpia la lista
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()

        cursor.execute("SELECT id, name, stock FROM products;")
        products = cursor.fetchall()
        connection.close()

        if products:
            for product in products:
                inventory_list.insert(tk.END, f"ID: {product[0]} | Nombre: {product[1]} | Stock: {product[2]}\n")
        else:
            inventory_list.insert(tk.END, "No hay productos en el inventario.\n")

    # Cargar el inventario al abrir la ventana
    load_inventory()

    ttk.Button(frame, text="Refrescar", command=load_inventory).pack(pady=5)
    ttk.Button(frame, text="Cerrar", command=window.destroy).pack(pady=5)

    def load_movements(self, tree, product_id_entry, category_entry, supplier_entry, movement_type_combo, start_date_entry, end_date_entry):
        """Filtra y carga los movimientos en la tabla."""
        # Obtener los valores de los filtros
        product_id = product_id_entry.get()
        category = category_entry.get()
        supplier = supplier_entry.get()
        movement_type = movement_type_combo.get()  # Puede ser "entry" o "exit"
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        # Validar y preparar los valores para la consulta
        product_id = int(product_id) if product_id else None
        category = category if category else None
        supplier = supplier if supplier else None
        movement_type = movement_type if movement_type else None
        start_date = start_date if start_date else None
        end_date = end_date if end_date else None

        # Llamar a la función para obtener movimientos desde el sistema
        movements = get_movements(
            product_id=product_id,
            category=category,
            supplier=supplier,
            movement_type=movement_type,
            start_date=start_date,
            end_date=end_date
        )

        # Limpiar la tabla antes de cargar nuevos datos
        for row in tree.get_children():
            tree.delete(row)

        # Mostrar movimientos en la tabla
        if movements:
            for movement in movements:
                # Desempaquetar los valores del movimiento
                id, product_name, quantity, category, supplier_name, movement_type, date = movement
                # Insertar los valores en la tabla
                tree.insert("", "end", values=(id, product_name, quantity, category, supplier_name, movement_type, date))
        else:
            # Mostrar un mensaje si no hay resultados
            messagebox.showinfo("Sin Resultados", "No se encontraron movimientos con los filtros seleccionados.")  
            
    def generate_reports_window(self):
        """Ventana para generar reportes y estadísticas."""
        window = tk.Toplevel(self.root)
        window.title("Reportes y Estadísticas")

        tk.Label(window, text="Selecciona el tipo de reporte:", font=("Arial", 12)).pack(pady=10)

        def show_top_selling_products():
            """Generar gráfico de los productos más vendidos."""
            data = get_top_selling_products()  # Obtiene los productos más vendidos
            if not data:
                messagebox.showinfo("Sin Datos", "No hay datos suficientes para generar el reporte.")
                return

            # Separar nombres y cantidades
            products = [item[0] for item in data]  # Nombres de productos
            quantities = [item[1] for item in data]  # Cantidades vendidas

            # Crear gráfico
            plt.figure(figsize=(8, 5))
            plt.bar(products, quantities, color='blue')
            plt.title("Productos Más Vendidos")
            plt.xlabel("Productos")
            plt.ylabel("Cantidad Vendida")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()

        ttk.Button(window, text="Productos Más Vendidos", command=show_top_selling_products).pack(pady=10)

        ttk.Button(window, text="Cerrar", command=window.destroy).pack(pady=10)    
     

    def refresh_suppliers_table(self, tree):
        """Refresca la tabla de proveedores."""
        for row in tree.get_children():
            tree.delete(row)

        suppliers = list_suppliers()
        for supplier in suppliers:
            tree.insert("", "end", values=supplier)

    # Los demás métodos permanecen igual...

    
    
    

