import tkinter as tk
import sys
from tkinter import messagebox, ttk
from auth.authentication import authenticate_user, register_user
from admin.admin_panel import open_admin_panel
from client.client_panel import open_cliente_panel

def center_window(window, width, height):
    """Centra una ventana en la pantalla"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")

def main():
    root = tk.Tk()
    root.title("Kairo's - Sistema de Gestión de Citas")
    root.configure(bg="#f5f5f5")
    root.resizable(False, False)
    
    # Centrar la ventana principal
    center_window(root, 500, 500)

    # Estilo para widgets
    style = ttk.Style()
    style.configure("TFrame", background="#f5f5f5")
    style.configure("TLabel", background="#f5f5f5", font=("Helvetica", 10))
    style.configure("TButton", font=("Helvetica", 10))
    style.configure("Title.TLabel", font=("Helvetica", 18, "bold"), foreground="#2c3e50")

    def mostrar_login():
        # Mostrar la ventana principal de login
        root.deiconify()
        # Re-centrar la ventana principal al mostrarse de nuevo
        center_window(root, 500, 500)

    def login():
        correo = correo_entry.get().strip()
        password = password_entry.get().strip()
        
        if not correo or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
            
        user = authenticate_user(correo, password)
        if not user:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            return
            
        messagebox.showinfo("Éxito", f"Bienvenido {user['nombre']}")
        root.withdraw()
        if user.get("role") == "admin":
            open_admin_panel(user, mostrar_login)  # Pasar la función de callback
        else:
            open_cliente_panel(user, mostrar_login)  # Pasar la función de callback

    # Frame principal
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill="both", expand=True)

    # Logo/Título
    title_frame = ttk.Frame(main_frame)
    title_frame.pack(pady=(20, 10), fill="x")
    
    title_label = ttk.Label(title_frame, text="Kairos", style="Title.TLabel")
    title_label.pack()
    
    subtitle_label = ttk.Label(title_frame, text="Sistema de Gestión de Citas", font=("Helvetica", 12))
    subtitle_label.pack(pady=(0, 30))

    # Frame de formulario
    form_frame = ttk.Frame(main_frame)
    form_frame.pack(expand=True)  # Centrar verticalmente

    # Campos de entrada
    ttk.Label(form_frame, text="Correo electrónico:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(10, 5))
    correo_entry = ttk.Entry(form_frame, width=30, font=("Helvetica", 10))
    correo_entry.grid(row=1, column=0, sticky="ew", pady=(0, 15))
    
    ttk.Label(form_frame, text="Contraseña:", font=("Helvetica", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 5))
    password_entry = ttk.Entry(form_frame, show="•", width=30, font=("Helvetica", 10))
    password_entry.grid(row=3, column=0, sticky="ew", pady=(0, 20))

    # Botón de login
    login_btn = tk.Button(form_frame, text="Iniciar Sesión", command=login, 
                         bg="#3498db", fg="white", font=("Helvetica", 10, "bold"),
                         width=20, height=2, bd=0, cursor="hand2")
    login_btn.grid(row=4, column=0, pady=10)
    
    # Separador
    separator = ttk.Separator(form_frame, orient="horizontal")
    separator.grid(row=5, column=0, sticky="ew", pady=20)

    # Registro rápido de cliente
    def register_window():
        reg_win = tk.Toplevel(root)
        reg_win.title("Registro de Cliente - Kairos")
        reg_win.configure(bg="#f5f5f5")
        reg_win.resizable(False, False)
        
        # Centrar la ventana de registro
        center_window(reg_win, 400, 500)
        
        reg_win.transient(root)
        reg_win.grab_set()
        
        reg_frame = ttk.Frame(reg_win, padding="20")
        reg_frame.pack(fill="both", expand=True)
        
        ttk.Label(reg_frame, text="Registro de Nuevo Cliente", style="Title.TLabel").pack(pady=(10, 20))
        
        # Formulario de registro
        reg_form = ttk.Frame(reg_frame)
        reg_form.pack(fill="x", padx=30, expand=True)
        
        # Campos de registro
        fields = [
            ("Nombre:", "entry_nombre"),
            ("Correo:", "entry_correo"),
            ("Contraseña:", "entry_pass"),
            ("Teléfono:", "entry_tel")
        ]
        
        entries = {}
        for i, (label, name) in enumerate(fields):
            ttk.Label(reg_form, text=label).grid(row=i, column=0, sticky="w", pady=5)
            entry = ttk.Entry(reg_form, width=25, font=("Helvetica", 10))
            entry.grid(row=i, column=1, sticky="ew", pady=5, padx=(10, 0))
            if "pass" in name:
                entry.configure(show="•")
            entries[name] = entry
        
        # Campo de sexo
        ttk.Label(reg_form, text="Sexo:").grid(row=len(fields), column=0, sticky="w", pady=5)
        sexo_var = tk.StringVar(value="F")
        sexo_menu = ttk.OptionMenu(reg_form, sexo_var, "F", "F", "M", "Otro")
        sexo_menu.grid(row=len(fields), column=1, sticky="w", pady=5, padx=(10, 0))
        
        def save_cliente():
            data = {
                'nombre': entries['entry_nombre'].get(),
                'correo': entries['entry_correo'].get(),
                'password': entries['entry_pass'].get(),
                'telefono': entries['entry_tel'].get(),
                'sexo': sexo_var.get()
            }
            
            # Validar campos vacíos
            for field, value in data.items():
                if not value and field != 'telefono':  # Teléfono puede ser opcional
                    messagebox.showerror("Error", f"Por favor complete el campo: {field}")
                    return
                    
            success, msg = register_user(data['nombre'], data['correo'], data['password'], 
                                        data['telefono'], data['sexo'], "cliente")
            if success:
                messagebox.showinfo("Éxito", msg)
                reg_win.destroy()
            else:
                messagebox.showerror("Error", msg)
        
        # Botones
        btn_frame = ttk.Frame(reg_frame)
        btn_frame.pack(pady=20)
        
        register_btn = tk.Button(btn_frame, text="Registrar", command=save_cliente, 
                                bg="#2ecc71", fg="white", font=("Helvetica", 10, "bold"),
                                width=12, height=1, bd=0, cursor="hand2")
        register_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancelar", command=reg_win.destroy,
                              bg="#e74c3c", fg="white", font=("Helvetica", 10),
                              width=12, height=1, bd=0, cursor="hand2")
        cancel_btn.pack(side="left", padx=5)

    # Botón de registrarse
    register_btn = tk.Button(form_frame, text="Crear Nueva Cuenta", command=register_window,
                            bg="#2ecc71", fg="white", font=("Helvetica", 10),
                            width=20, height=1, bd=0, cursor="hand2")
    register_btn.grid(row=6, column=0, pady=10)

    # Manejar el cierre de la aplicación
    def on_closing():
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Enfocar el primer campo de entrada
    correo_entry.focus_set()
    
    # Configurar la tecla Enter para iniciar sesión
    root.bind('<Return>', lambda event: login())
    
    root.mainloop()

if __name__ == "__main__":
    main()