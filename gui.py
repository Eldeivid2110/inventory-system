import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3
from inventory.database import verify_user
from inventory.inventory_manager import (
    add_product,
    list_products,
    register_stock_exit,
    get_low_stock_products,
    get_movements,
    delete_product_and_related_data,
    add_supplier,
    list_suppliers,
    delete_supplier,
    update_supplier,
    get_top_selling_products,
    InventoryManager
)
class LoginWindow:
    def __init__(self, root, on_success):
     self.root = root
     self.on_success = on_success

     self.window = tk.Toplevel(root)
     self.window.title("Iniciar sesión")
     self.window.geometry("350x200")
     self.window.configure(bg="#f5f5f5")
     self.window.resizable(False, False)
     self.center_window(350, 200)
     self.window.protocol("WM_DELETE_WINDOW", root.destroy)

     # Estilo ttk
     style = ttk.Style(self.window)
     style.theme_use('clam')
     style.configure('TLabel', font=('Segoe UI', 12), background="#f5f5f5")
     style.configure('TEntry', font=('Segoe UI', 12))
     style.configure('TButton', font=('Segoe UI', 12), padding=8)
     style.map('TButton', background=[('active', '#b2dfdb')])

     frame = ttk.Frame(self.window, padding=24, style='Card.TFrame')
     frame.pack(expand=True, fill='both')

     ttk.Label(frame, text="Usuario:", anchor="w").pack(fill='x', pady=(0, 6))
     self.username_entry = ttk.Entry(frame)
     self.username_entry.pack(fill='x', pady=(0, 14))

     ttk.Label(frame, text="Contraseña:", anchor="w").pack(fill='x', pady=(0, 6))
     self.password_entry = ttk.Entry(frame, show="*")
     self.password_entry.pack(fill='x', pady=(0, 18))

     self.login_btn = ttk.Button(frame, text="Ingresar", command=self.login)
     self.login_btn.pack(pady=(6, 0), fill='x')

     # Firma con emoji, centrada y en gris claro
     firma_label = ttk.Label(
        frame,
        text="💡 by Eldeivid2110",
        font=("Segoe UI", 9, "italic"),
        anchor="center",
        foreground="#bdbdbd"
    )
     firma_label.pack(pady=(18, 0))

     self.username_entry.focus()
     self.window.bind('<Return>', lambda event: self.login())

    def center_window(self, width, height):
        self.window.update_idletasks()
        screenwidth = self.window.winfo_screenwidth()
        screenheight = self.window.winfo_screenheight()
        x = int((screenwidth / 2) - (width / 2))
        y = int((screenheight / 2) - (height / 2))
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if verify_user(username, password):
            self.window.destroy()
            self.on_success(username)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

class InventoryApp:
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.root.title("Sistema de Control de Inventarios")

        # Configurar el color de fondo
        self.root.configure(bg="#00796b")  # Color verde azulado

        # Inicializar atributos
        self.low_stock_threshold = 10  # Umbral inicial para notificaciones de bajo stock
        self.inventory_manager = InventoryManager()  # Instancia del gestor de inventario

        # Habilitar pantalla completa
        self.root.attributes("-fullscreen", True)

        # Salir del modo pantalla completa con la tecla Esc
        self.root.bind("<Escape>", lambda event: self.root.attributes("-fullscreen", False))

        # Configurar el tema de ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Arial", 14), padding=10)
        style.configure("TLabel", font=("Arial", 16), background="#00796b", foreground="white")
        style.configure("Header.TLabel", font=("Arial", 24, "bold"), background="#00796b", foreground="white")

        # Crear un marco principal para contener el menú
        self.main_frame = tk.Frame(self.root, bg="#00796b", padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        # Crear el menú principal
        self.create_main_menu()

    def create_main_menu(self):
        """Crea el menú principal con un diseño dividido en dos columnas."""
        # Limpiar cualquier contenido existente en el marco principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Título en la parte superior
        ttk.Label(
            self.main_frame,
            text="SISTEMA DE CONTROL DE INVENTARIOS",
            style="Header.TLabel",
            anchor="w"
        ).grid(row=0, column=0, columnspan=2, pady=20, sticky="w")

        # Columna izquierda: Opciones principales
        left_frame = tk.Frame(self.main_frame, bg="#00796b")
        left_frame.grid(row=1, column=0, sticky="nsw", padx=20, pady=20)

        actions_left = [
            ("📦 Agregar Producto", self.add_product_window),
            ("🗑️ Eliminar Producto", self.delete_product_window),
            ("📋 Listar Inventario", self.list_inventory_window),
            ("➖ Registrar Salida de Stock", self.register_exit_window),
        ]

        for text, command in actions_left:
            ttk.Button(left_frame, text=text, command=command, width=30).pack(pady=10)

        # Columna derecha: Opciones adicionales
        right_frame = tk.Frame(self.main_frame, bg="#00796b")
        right_frame.grid(row=1, column=1, sticky="nse", padx=20, pady=20)

        actions_right = [
            ("📜 Historial de Movimientos", self.simple_movements_window),
            ("⚙️ Configurar Umbral Bajo Stock", self.configure_low_stock_threshold),
            ("📊 Reportes y Estadísticas", self.generate_reports_window),
            ("📦 Revisar Bajo Stock", self.show_low_stock_notification),
            ("❌ Salir", self.root.quit),
        ]

        for text, command in actions_right:
            ttk.Button(right_frame, text=text, command=command, width=30).pack(pady=10)
            # Firma al pie del menú
        ttk.Label(
        self.main_frame,
        text="Desarrollado por MorettiDavid",
        style="TLabel",
        font=("Segoe UI", 10, "italic"),
        foreground="#bdbdbd",
        anchor="e"
    ).grid(row=99, column=0, columnspan=2, pady=(30, 0), sticky="e")
 

    def show_low_stock_notification(self):
        """Muestra una notificación si hay productos con bajo stock."""
        # Crear una nueva ventana para mostrar las notificaciones
        window = tk.Toplevel(self.root)
        window.title("Alertas de Bajo Stock")
        window.geometry("400x300")
        window.configure(bg="#f7f7f7")  # Color de fondo para mantener la consistencia

        # Mostrar el umbral actual
        ttk.Label(
            window,
            text=f"⚙️ Umbral de Bajo Stock: {self.low_stock_threshold}",
            style="TLabel",
            anchor="center"
        ).pack(pady=10)

        # Obtener productos con bajo stock desde el gestor de inventario
        low_stock_products = self.inventory_manager.get_low_stock_products(self.low_stock_threshold)

        if low_stock_products:
            # Mostrar mensaje de productos con bajo stock
            ttk.Label(
                window,
                text="⚠️ Productos con bajo stock:",
                style="TLabel",
                foreground="red",
                anchor="center"
            ).pack(pady=10)

            # Listar cada producto con bajo stock
            for product, quantity in low_stock_products:
                product_label = f"- {product} (Stock: {quantity})"
                ttk.Label(
                    window,
                    text=product_label,
                    style="TLabel",
                    anchor="w"
                ).pack(pady=2)
        else:
            # Definir un estilo personalizado para el mensaje
            style = ttk.Style(window)
            style.configure(
               "BlackOnGreen.TLabel",
               foreground="black",
               background="#00896b",  # verde oscuro, ajusta si usas otro color
               font=("Segoe UI", 14, "bold")
)
            # Mostrar mensaje si no hay productos con bajo stock
            tk.Label(
             window,
             text="✅ Todo el inventario está en buen estado.",
             font=("Segoe UI", 14, "bold"),
             bg="#00896b",
             fg="black",
             anchor="center"
             ).pack(fill="x", padx=10, pady=10)

        # Botón para cerrar la ventana
        ttk.Button(
            window,
            text="Cerrar",
            command=window.destroy
        ).pack(pady=10)

    def configure_low_stock_threshold(self):
        """Permitir al usuario configurar el umbral de bajo stock."""
        def save_threshold():
            try:
                new_threshold = int(threshold_entry.get())
                self.low_stock_threshold = new_threshold
                messagebox.showinfo("Configuración Guardada", f"El nuevo umbral de bajo stock es {new_threshold}.")
                config_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Por favor, ingresa un número válido.")

        config_window = tk.Toplevel(self.root)
        config_window.title("Configurar Umbral de Bajo Stock")
        config_window.geometry("300x150")
        config_window.configure(bg="#f7f7f7")

        ttk.Label(
            config_window,
            text="Configura el umbral de bajo stock:",
            style="TLabel"
        ).pack(pady=10)

        threshold_entry = ttk.Entry(config_window, width=10)
        threshold_entry.insert(0, str(self.low_stock_threshold))
        threshold_entry.pack(pady=5)

        ttk.Button(config_window, text="Guardar", command=save_threshold).pack(pady=10)

    def add_product_window(self):
        """Ventana para agregar un nuevo producto."""
        window = tk.Toplevel(self.root)
        window.title("Agregar Producto")
        window.configure(bg="#f7f7f7")

        ttk.Label(window, text="Nombre del Producto:", style="TLabel").grid(row=0, column=0, padx=10, pady=5)
        product_name_entry = ttk.Entry(window, width=30)
        product_name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(window, text="Stock Inicial:", style="TLabel").grid(row=1, column=0, padx=10, pady=5)
        stock_entry = ttk.Entry(window, width=30)
        stock_entry.grid(row=1, column=1, padx=10, pady=5)

        def save_product():
            """Guardar el producto en la base de datos y registrar un movimiento."""
            product_name = product_name_entry.get()
            try:
                stock = int(stock_entry.get())
                if stock < 0:
                    raise ValueError("El stock inicial no puede ser negativo.")
            except ValueError as e:
                messagebox.showerror("Error", f"Stock inválido: {e}")
                return

            if not product_name:
                messagebox.showerror("Error", "El nombre del producto no puede estar vacío.")
                return

            # Agregar el producto a la base de datos
            product_id = add_product(product_name, stock)

            # Registrar un movimiento 'entry' automáticamente
            self.register_movement(product_id, stock, "entry")

            # Mostrar éxito
            messagebox.showinfo("Éxito", f"Producto '{product_name}' agregado con éxito.")
            window.destroy()

        ttk.Button(window, text="Guardar", command=save_product).grid(row=2, columnspan=2, pady=10)

    def register_movement(self, product_id, quantity, movement_type):
        """Registrar un movimiento en la base de datos."""
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO movements (product_id, quantity, type, date)
            VALUES (?, ?, ?, ?)
        """, (product_id, quantity, movement_type, datetime.now()))
        connection.commit()
        connection.close()

    def configure_low_stock_threshold(self):
        """Allow the user to configure the low stock threshold."""
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
        """Refresh the main menu to update notifications."""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_main_menu()

    def simple_movements_window(self):
        """Ventana para mostrar el historial de movimientos en una tabla simple."""
        window = tk.Toplevel(self.root)
        window.title("Historial de Movimientos")

        # Tabla para mostrar los movimientos
        tree = ttk.Treeview(window, columns=("ID", "Producto", "Cantidad", "Tipo", "Fecha"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Producto", text="Producto")
        tree.heading("Cantidad", text="Cantidad")
        tree.heading("Tipo", text="Tipo")
        tree.heading("Fecha", text="Fecha")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Botón para cerrar la ventana
        ttk.Button(window, text="Cerrar", command=window.destroy).pack(pady=10)

        # Cargar movimientos desde la base de datos
        self.load_all_movements(tree)

    def load_all_movements(self, tree):
        """Carga todos los movimientos desde la base de datos y los muestra en la tabla."""
        connection = sqlite3.connect("inventory.db")
        cursor = connection.cursor()

        # Consulta para obtener los movimientos
        query = """
            SELECT movements.id, products.name, movements.quantity, movements.type, movements.date
            FROM movements
            JOIN products ON movements.product_id = products.id
        """
        cursor.execute(query)
        movements = cursor.fetchall()
        connection.close()

        # Limpiar la tabla antes de agregar nuevos datos
        for row in tree.get_children():
            tree.delete(row)

        # Agregar los movimientos a la tabla
        for movement in movements:
            tree.insert("", "end", values=movement)
    def add_product_window(self):
        """Window to add a new product."""
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
        category_entry.grid(row=2, column=1, padx=10, pady=5)

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
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar el producto: {e}")

        ttk.Button(window, text="Guardar", command=save_product).grid(row=3, columnspan=2, pady=10)

    def delete_product_window(self):
        """Window to delete a product."""
        window = tk.Toplevel(self.root)
        window.title("Eliminar Producto")

        tk.Label(window, text="ID del Producto a eliminar:").grid(row=0, column=0, padx=10, pady=5)
        product_id_entry = tk.Entry(window, width=30)
        product_id_entry.grid(row=0, column=1, padx=10, pady=5)

        def delete_product():
            try:
                product_id = int(product_id_entry.get())
                delete_product_and_related_data(product_id)
                messagebox.showinfo("Éxito", f"Producto con ID {product_id} eliminado correctamente.")
                window.destroy()
            except ValueError:
                messagebox.showerror("Error", "El ID debe ser un número entero.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el producto: {e}")

        ttk.Button(window, text="Eliminar", command=delete_product).grid(row=1, columnspan=2, pady=10)

    def list_inventory_window(self):
        """Window to list inventory."""
        window = tk.Toplevel(self.root)
        window.title("Inventario")

        # Frame for the list of products
        frame = tk.Frame(window, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Inventario de Productos", font=("Arial", 16)).pack(pady=10)

        # Create the inventory list textbox
        inventory_list = tk.Text(frame, width=50, height=20)
        inventory_list.pack(pady=10)

        def load_inventory():
            """Load inventory from the database."""
            inventory_list.delete('1.0', tk.END)  # Clear the list
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

        # Load the inventory upon opening the window
        load_inventory()

        ttk.Button(frame, text="Refrescar", command=load_inventory).pack(pady=5)
        ttk.Button(frame, text="Cerrar", command=window.destroy).pack(pady=5)

    def register_exit_window(self):
        """Window to register stock exit."""
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
        """Window to manage suppliers."""
        window = tk.Toplevel(self.root)
        window.title("Gestionar Proveedores")

        # Table to show suppliers
        suppliers = list_suppliers()

        tree = ttk.Treeview(window, columns=("ID", "Nombre", "Contacto"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Nombre", text="Nombre")
        tree.heading("Contacto", text="Contacto")
        tree.pack(fill="both", expand=True)

        for supplier in suppliers:
            tree.insert("", "end", values=supplier)

        def add_supplier_window():
            """Window to add a new supplier."""
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
            """Delete the selected supplier."""
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Advertencia", "Por favor, selecciona un proveedor para eliminar.")
                return

            # Get the ID of the selected supplier
            supplier_id = tree.item(selected_item[0])["values"][0]

            # Confirm before deleting
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

    def refresh_suppliers_table(self, tree):
        """Refresh the suppliers table."""
        for row in tree.get_children():
            tree.delete(row)

        suppliers = list_suppliers()
        for supplier in suppliers:
            tree.insert("", "end", values=supplier)

    def show_movements_window(self):
        """Enhanced window to show movements history with advanced filters."""
        window = tk.Toplevel(self.root)
        window.title("Historial de Movimientos")

        # Labels and entry fields for filters
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

        tk.Label(window, text="Fecha Inicio (YYYY-MM-DD):").grid(row=4, column=0, padx=10, pady=5)
        start_date_entry = tk.Entry(window, width=20)
        start_date_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(window, text="Fecha Fin (YYYY-MM-DD):").grid(row=5, column=0, padx=10, pady=5)
        end_date_entry = tk.Entry(window, width=20)
        end_date_entry.grid(row=5, column=1, padx=10, pady=5)

        # Table to show movements
        tree = ttk.Treeview(window, columns=("ID", "Producto", "Cantidad", "Categoría", "Proveedor", "Tipo", "Fecha"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Producto", text="Producto")
        tree.heading("Cantidad", text="Cantidad")
        tree.heading("Categoría", text="Categoría")
        tree.heading("Proveedor", text="Proveedor")
        tree.heading("Tipo", text="Tipo")
        tree.heading("Fecha", text="Fecha")
        tree.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Button to apply filters
        ttk.Button(
            window,
            text="Filtrar",
            command=lambda: self.load_movements(tree, product_id_entry, category_entry, supplier_entry, movement_type_combo, start_date_entry, end_date_entry)
        ).grid(row=6, column=0, columnspan=2, pady=10)

    def load_movements(self, tree, product_id_entry, category_entry, supplier_entry, movement_type_combo, start_date_entry, end_date_entry):
        """Filter and load movements into the table."""
        # Get values from the filters
        product_id = product_id_entry.get()
        category = category_entry.get()
        supplier = supplier_entry.get()
        movement_type = movement_type_combo.get()
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        # Validate and prepare values for the query
        try:
            product_id = int(product_id) if product_id else None
        except ValueError:
            messagebox.showerror("Error", "ID Producto debe ser un número entero.")
            return
        category = category if category else None
        supplier = supplier if supplier else None
        movement_type = movement_type if movement_type else None

        # Validate dates
        date_format = "%Y-%m-%d"
        try:
            if start_date:
                datetime.strptime(start_date, date_format)
            else:
                start_date = None
            if end_date:
                datetime.strptime(end_date, date_format)
            else:
                end_date = None
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido, use YYYY-MM-DD.")
            return

        # Get filtered movements
        movements = get_movements(
            product_id=product_id,
            category=category,
            supplier=supplier,
            movement_type=movement_type,
            start_date=start_date,
            end_date=end_date
        )

        # Clear the table before showing new data
        for row in tree.get_children():
            tree.delete(row)

        if movements:
            for movement in movements:
                id_, product_name, quantity, category_, supplier_name, movement_type_, date_ = movement
                tree.insert("", "end", values=(id_, product_name, quantity, category_, supplier_name, movement_type_, date_))
        else:
            messagebox.showinfo("Sin Resultados", "No se encontraron movimientos con los filtros seleccionados.")

    def generate_reports_window(self):
        """Window to generate reports and statistics."""
        window = tk.Toplevel(self.root)
        window.title("Reportes y Estadísticas")

        tk.Label(window, text="Selecciona el tipo de reporte:", font=("Arial", 12)).pack(pady=10)

        def show_top_selling_products():
            """Generate a graph of the top-selling products."""
            data = get_top_selling_products()
            if not data:
                messagebox.showinfo("Sin Datos", "No hay datos suficientes para generar el reporte.")
                return

            products = [item[0] for item in data]
            quantities = [item[1] for item in data]

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
    
    


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()

