from inventory.database import connect, migrate
from gui import InventoryApp
import tkinter as tk

if __name__ == "__main__":
    connect()  # Crear la base de datos si no existe
    migrate()  # Realizar migraciones necesarias
    root = tk.Tk()
    app = InventoryApp(root)
    app.create_main_menu()
    root.mainloop()

    