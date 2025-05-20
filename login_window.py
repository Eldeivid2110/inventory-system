import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.root = tk.Tk()
        self.root.title("Iniciar Sesión")
        self.root.geometry("320x220")
        self.root.resizable(False, False)
        self.root.configure(bg='#f5f5f5')
        self.center_window(320, 220)

        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TLabel', font=('Segoe UI', 12))
        style.configure('TEntry', font=('Segoe UI', 12))
        style.configure('TButton', font=('Segoe UI', 12), padding=6)
        style.map('TButton', foreground=[('pressed', '#fff'), ('active', '#00796b')], background=[('active', '#b2dfdb')])

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill='both')

        ttk.Label(frame, text="Usuario:", anchor="w").pack(fill='x', pady=(0, 5))
        self.username_entry = ttk.Entry(frame)
        self.username_entry.pack(fill='x', pady=(0, 15))

        ttk.Label(frame, text="Contraseña:", anchor="w").pack(fill='x', pady=(0, 5))
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.pack(fill='x', pady=(0, 15))

        self.login_btn = ttk.Button(frame, text="Ingresar", command=self.login)
        self.login_btn.pack(pady=(10, 0), fill='x')

        self.root.bind('<Return>', lambda event: self.login())
        self.username_entry.focus()

    def center_window(self, width, height):
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        x = int((screenwidth / 2) - (width / 2))
        y = int((screenheight / 2) - (height / 2))
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def login(self):
        usuario = self.username_entry.get()
        contraseña = self.password_entry.get()
        # Aquí conectas con tu lógica real de verificación, por ejemplo:
        from database import verify_user
        if verify_user(usuario, contraseña):
            self.root.destroy()
            self.on_login_success(usuario)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def run(self):
        self.root.mainloop()