import tkinter as tk
from tkinter import ttk
from admin.user_management import crear_pestaña_usuarios
from admin.stylist_management import crear_pestaña_estilistas
from admin.service_management import crear_pestaña_servicios
from admin.appointment_management import crear_pestaña_citas
from admin.message_management import crear_panel_mensajes

def open_admin_panel(user, login_callback):
    admin_win = tk.Toplevel()
    admin_win.title("Panel Administrador - kairo's")
    admin_win.geometry("1200x650")
    admin_win.configure(bg='#1a1a1a')

    # Configurar grid para el layout principal
    admin_win.grid_columnconfigure(1, weight=1)
    admin_win.grid_rowconfigure(1, weight=1)

    # Frame superior con bienvenida - MÁS ANCHO
    header_frame = tk.Frame(admin_win, bg="#1a1a1a", height=80)  # Aumentado de 60 a 80
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
    header_frame.grid_propagate(False)
    
    # Contenedor para los textos en el header
    text_container = tk.Frame(header_frame, bg='#1a1a1a')
    text_container.pack(side="left", padx=20, pady=10)
    
    # Título KAIRO'S
    tk.Label(text_container, text="KAIRO'S", 
             font=("Helvetica", 20, "bold"), bg='#1a1a1a', fg='#ecf0f1').pack(anchor="w")
    
    # Texto de bienvenida debajo del título
    tk.Label(text_container, text=f"Bienvenido, {user['nombre']} (Administrador)", 
             font=("Helvetica", 12), bg='#1a1a1a', fg='#b8b8b8').pack(anchor="w")

    # Frame del menú lateral izquierdo
    menu_frame = tk.Frame(admin_win, bg='#1a1a1a', width=200)
    menu_frame.grid(row=1, column=0, sticky="ns")
    menu_frame.grid_propagate(False)
    
    # Título del menú
    tk.Label(menu_frame, text="MENÚ", font=("Helvetica", 14, "bold"), 
             bg='#1a1a1a', fg='#b8b8b8').pack(pady=(20, 30))
    
    # Frame principal para el contenido
    content_frame = tk.Frame(admin_win, bg='#ecf0f1')
    content_frame.grid(row=1, column=1, sticky="nsew")
    content_frame.grid_propagate(True)
    
    # Crear un frame contenedor para todas las secciones
    container = tk.Frame(content_frame, bg='#ecf0f1')
    container.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Crear todas las secciones pero mantenerlas ocultas inicialmente
    sections = {}
    
    # Crear sección de usuarios (SIN botones)
    user_section = crear_pestaña_usuarios(container, admin_win, mostrar_botones=False)
    sections["usuarios"] = user_section
    
    # Crear sección de estilistas (SIN botones)
    stylist_section = crear_pestaña_estilistas(container, admin_win, mostrar_botones=False)
    sections["estilistas"] = stylist_section
    
    # Crear sección de servicios (SIN botones)
    service_section = crear_pestaña_servicios(container, admin_win, mostrar_botones=False)
    sections["servicios"] = service_section
    
    # Crear sección de citas (SIN botones)
    appointment_section = crear_pestaña_citas(container, admin_win, mostrar_botones=False)
    sections["citas"] = appointment_section
    
    # Crear sección de mensajes (SIN botones) - ¡AHORA SÍ después de crear el container!
    message_section = crear_panel_mensajes(container)
    sections["mensajes"] = message_section
    
    # Ocultar todas las secciones inicialmente
    for section in sections.values():
        section.pack_forget()
    
    # Función para mostrar una sección específica
    def show_section(section_name):
        # Ocultar todas las secciones
        for section in sections.values():
            section.pack_forget()
        
        # Mostrar la sección seleccionada
        sections[section_name].pack(fill="both", expand=True)
    
    # Botones del menú
    menu_options = [
        ("Usuarios", lambda: show_section("usuarios")),
        ("Estilistas", lambda: show_section("estilistas")),
        ("Servicios", lambda: show_section("servicios")),
        ("Citas", lambda: show_section("citas")),
        ("Mensajes", lambda: show_section("mensajes")),
        ("", None),
        ("Cerrar Sesión", lambda: cerrar_sesion(admin_win, login_callback))
    ]
    
    for text, command in menu_options:
        if text == "":  # Separador
            tk.Frame(menu_frame, height=2, bg='#444').pack(fill="x", pady=10, padx=20)
        else:
            btn = tk.Button(menu_frame, text=text, command=command,
                           bg='#1a1a1a', fg='#b8b8b8', font=("Helvetica", 12),
                           relief="flat", bd=0, anchor="w", padx=20)
            btn.pack(fill="x", pady=5)
            # Efecto hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#1a1a1a", fg='white'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#1a1a1a', fg='#b8b8b8'))

    # Mostrar la primera sección por defecto
    show_section("mensajes")

    def cerrar_sesion(ventana, callback):
        ventana.destroy()
        callback()

    # Manejar el cierre de la ventana
    admin_win.protocol("WM_DELETE_WINDOW", lambda: cerrar_sesion(admin_win, login_callback))