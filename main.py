import tkinter as tk
from gui import InventoryApp, LoginWindow
from inventory.database import (
    connect, migrate, check_and_add_column, update_movements, add_user,
)

def start_inventory_app(usuario):
    root.deiconify()  # Mostrar la ventana principal solo si login fue exitoso
    InventoryApp(root, usuario)
    # No crees otro mainloop aquí

if __name__ == "__main__":
    connect()
    migrate()
    check_and_add_column("inventory.db", "movements", "movement_type", "TEXT")
    update_movements()
    # add_user("admin", "1234")  # Solo la primera vez

    root = tk.Tk()
    root.withdraw()  # Oculta la ventana raíz al inicio

    def on_login_success(usuario):
        start_inventory_app(usuario)

    LoginWindow(root, on_login_success)
    root.mainloop()