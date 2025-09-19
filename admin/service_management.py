import tkinter as tk
from tkinter import messagebox, ttk
from database.config import servicios_col

def crear_pestaña_servicios(parent, admin_win, mostrar_botones=True):
    tab_servicios = ttk.Frame(parent)
    
    # Variables de paginación
    ROWS_PER_PAGE = 50
    current_page = tk.IntVar(value=1)
    total_pages = tk.IntVar(value=1)
    all_servicios = []  # lista de servicios cargados de DB
    filtered_servicios = []  # lista filtrada según búsqueda

    # ---------------- BUSQUEDA ----------------
    search_frame = tk.Frame(tab_servicios)
    search_frame.pack(fill="x", padx=20, pady=5)

    tk.Label(search_frame, text="Buscar:").pack(side="left")
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=5)

    def filtrar_servicios(*args):
        query = search_var.get().lower()
        nonlocal filtered_servicios, current_page, total_pages
        filtered_servicios = [
            s for s in all_servicios
            if query in s.get("nombre", "").lower()
        ]
        current_page.set(1)
        total_pages.set(max(1, (len(filtered_servicios) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE))
        cargar_servicios()

    search_var.trace_add("write", filtrar_servicios)

    # ---------------- TREEVIEW ----------------
    tree_frame = ttk.Frame(tab_servicios)
    tree_frame.pack(fill="both", expand=True, padx=20, pady=5)
    
    cols_servicios = ("nombre", "tiempo_M", "tiempo_F")
    tree_serv = ttk.Treeview(tree_frame, columns=cols_servicios, show="headings")
    
    # Configurar columnas
    tree_serv.heading("nombre", text="Nombre")
    tree_serv.heading("tiempo_M", text="Tiempo H (min)")
    tree_serv.heading("tiempo_F", text="Tiempo M (min)")
    
    tree_serv.column("nombre", width=250)
    tree_serv.column("tiempo_M", width=100)
    tree_serv.column("tiempo_F", width=100)
    
    # Scrollbar para el treeview
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_serv.yview)
    tree_serv.configure(yscrollcommand=scrollbar.set)
    
    tree_serv.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ---------------- PAGINACION ----------------
    pagination_frame = tk.Frame(tab_servicios)
    pagination_frame.pack(pady=5)

    btn_prev = tk.Button(pagination_frame, text="⏮ Anterior")
    btn_prev.pack(side="left", padx=5)
    lbl_page = tk.Label(pagination_frame, textvariable=current_page)
    lbl_page.pack(side="left")
    lbl_total = tk.Label(pagination_frame, textvariable=total_pages)
    lbl_total.pack(side="left", padx=5)
    btn_next = tk.Button(pagination_frame, text="⏭ Siguiente")
    btn_next.pack(side="left", padx=5)

    def cargar_servicios():
        for row in tree_serv.get_children():
            tree_serv.delete(row)
        
        start = (current_page.get() - 1) * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE
        for s in filtered_servicios[start:end]:
            tree_serv.insert("", tk.END, values=(
                s["nombre"], 
                s.get("tiempo_M", 30),
                s.get("tiempo_F", 60)
            ))

    def pagina_siguiente():
        if current_page.get() < total_pages.get():
            current_page.set(current_page.get() + 1)
            cargar_servicios()

    def pagina_anterior():
        if current_page.get() > 1:
            current_page.set(current_page.get() - 1)
            cargar_servicios()

    btn_next.config(command=pagina_siguiente)
    btn_prev.config(command=pagina_anterior)

    # ---------------- CARGAR SERVICIOS ----------------
    def cargar_todos_servicios():
        nonlocal all_servicios, filtered_servicios
        all_servicios = list(servicios_col.find())
        filtered_servicios = all_servicios.copy()
        total_pages.set(max(1, (len(filtered_servicios) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE))
        cargar_servicios()

    cargar_todos_servicios()

    # Frame para botones (siempre visible)
    btn_frame = tk.Frame(tab_servicios)
    btn_frame.pack(pady=10)

    def crear_servicio():
        def save_servicio():
            n = entry_nombre.get().strip()
            tiempo_m = entry_tiempo_M.get().strip()
            tiempo_f = entry_tiempo_F.get().strip()
            
            # Validar campos
            if not n:
                messagebox.showerror("Error", "Nombre requerido")
                return
            
            try:
                tiempo_m = int(tiempo_m)
                if tiempo_m <= 0:
                    messagebox.showerror("Error", "El tiempo para hombres debe ser mayor a 0")
                    return
            except:
                messagebox.showerror("Error", "Tiempo para hombres inválido")
                return
                
            try:
                tiempo_f = int(tiempo_f)
                if tiempo_f <= 0:
                    messagebox.showerror("Error", "El tiempo para mujeres debe ser mayor a 0")
                    return
            except:
                messagebox.showerror("Error", "Tiempo para mujeres inválido")
                return
            
            # Verificar si el servicio ya existe
            servicio_existente = servicios_col.find_one({"nombre": n})
            if servicio_existente:
                messagebox.showerror("Error", "Ya existe un servicio con ese nombre")
                return
            
            servicios_col.insert_one({
                "nombre": n, 
                "tiempo_M": tiempo_m, 
                "tiempo_F": tiempo_f, 
                "activo": True
            })
            messagebox.showinfo("Éxito", "Servicio agregado")
            new_win.destroy()
            cargar_todos_servicios()

        new_win = tk.Toplevel(admin_win)
        new_win.title("Crear Servicio")
        new_win.geometry("350x300")
        new_win.configure(bg='white')
        
        form_frame = tk.Frame(new_win, bg='white')
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        tk.Label(form_frame, text="Nombre del servicio", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(0,5))
        entry_nombre = tk.Entry(form_frame, width=30, font=("Arial", 10))
        entry_nombre.pack(pady=5)
        
        tk.Label(form_frame, text="Tiempo para Hombres (minutos)", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,5))
        entry_tiempo_M = tk.Entry(form_frame, width=30, font=("Arial", 10))
        entry_tiempo_M.insert(0, "30")
        entry_tiempo_M.pack(pady=5)
        
        tk.Label(form_frame, text="Tiempo para Mujeres (minutos)", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,5))
        entry_tiempo_F = tk.Entry(form_frame, width=30, font=("Arial", 10))
        entry_tiempo_F.insert(0, "60")
        entry_tiempo_F.pack(pady=5)
        
        btn_frame_modal = tk.Frame(form_frame, bg='white')
        btn_frame_modal.pack(pady=20)
        
        tk.Button(btn_frame_modal, text="Guardar", command=save_servicio, 
                 bg="#2ecc71", fg="white", font=("Arial", 10), width=10).pack(side="left", padx=5)
        tk.Button(btn_frame_modal, text="Cancelar", command=new_win.destroy,
                 bg="#95a5a6", fg="white", font=("Arial", 10), width=10).pack(side="left", padx=5)

    def editar_servicio():
        sel = tree_serv.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione un servicio")
            return
            
        item = tree_serv.item(sel[0])
        nombre_actual = item["values"][0]
        tiempo_m_actual = item["values"][1] if len(item["values"]) > 1 else 30
        tiempo_f_actual = item["values"][2] if len(item["values"]) > 2 else 60
        
        servicio = servicios_col.find_one({"nombre": nombre_actual})
        if not servicio:
            messagebox.showerror("Error", "Servicio no encontrado")
            return

        def guardar_edicion():
            nuevo_nombre = entry_nombre.get().strip()
            nuevo_tiempo_m = entry_tiempo_M.get().strip()
            nuevo_tiempo_f = entry_tiempo_F.get().strip()
            
            # Validar campos
            if not nuevo_nombre:
                messagebox.showerror("Error", "Nombre requerido")
                return
            
            try:
                nuevo_tiempo_m = int(nuevo_tiempo_m)
                if nuevo_tiempo_m <= 0:
                    messagebox.showerror("Error", "El tiempo para hombres debe ser mayor a 0")
                    return
            except:
                messagebox.showerror("Error", "Tiempo para hombres inválido")
                return
                
            try:
                nuevo_tiempo_f = int(nuevo_tiempo_f)
                if nuevo_tiempo_f <= 0:
                    messagebox.showerror("Error", "El tiempo para mujeres debe ser mayor a 0")
                    return
            except:
                messagebox.showerror("Error", "Tiempo para mujeres inválido")
                return
            
            # Verificar si el nuevo nombre ya existe (y no es el mismo servicio)
            if nuevo_nombre != nombre_actual:
                servicio_existente = servicios_col.find_one({"nombre": nuevo_nombre})
                if servicio_existente:
                    messagebox.showerror("Error", "Ya existe un servicio con ese nombre")
                    return
            
            servicios_col.update_one(
                {"nombre": nombre_actual},
                {"$set": {
                    "nombre": nuevo_nombre, 
                    "tiempo_M": nuevo_tiempo_m, 
                    "tiempo_F": nuevo_tiempo_f
                }}
            )
            messagebox.showinfo("Éxito", "Servicio actualizado")
            edit_win.destroy()
            cargar_todos_servicios()

        edit_win = tk.Toplevel(admin_win)
        edit_win.title("Editar Servicio")
        edit_win.geometry("350x300")
        edit_win.configure(bg='white')
        
        form_frame = tk.Frame(edit_win, bg='white')
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        tk.Label(form_frame, text="Nombre del servicio", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(0,5))
        entry_nombre = tk.Entry(form_frame, width=30, font=("Arial", 10))
        entry_nombre.insert(0, nombre_actual)
        entry_nombre.pack(pady=5)
        
        tk.Label(form_frame, text="Tiempo para Hombres (minutos)", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,5))
        entry_tiempo_M = tk.Entry(form_frame, width=30, font=("Arial", 10))
        entry_tiempo_M.insert(0, str(tiempo_m_actual))
        entry_tiempo_M.pack(pady=5)
        
        tk.Label(form_frame, text="Tiempo para Mujeres (minutos)", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,5))
        entry_tiempo_F = tk.Entry(form_frame, width=30, font=("Arial", 10))
        entry_tiempo_F.insert(0, str(tiempo_f_actual))
        entry_tiempo_F.pack(pady=5)
        
        btn_frame_modal = tk.Frame(form_frame, bg='white')
        btn_frame_modal.pack(pady=20)
        
        tk.Button(btn_frame_modal, text="Guardar", command=guardar_edicion, 
                 bg="#3498db", fg="white", font=("Arial", 10), width=10).pack(side="left", padx=5)
        tk.Button(btn_frame_modal, text="Cancelar", command=edit_win.destroy,
                 bg="#95a5a6", fg="white", font=("Arial", 10), width=10).pack(side="left", padx=5)

    def eliminar_servicio():
        sel = tree_serv.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione un servicio")
            return
            
        item = tree_serv.item(sel[0])
        nombre = item["values"][0]
        tiempo_m = item["values"][1] if len(item["values"]) > 1 else 30
        tiempo_f = item["values"][2] if len(item["values"]) > 2 else 60
        
        if messagebox.askyesno("Confirmar Eliminación", 
                              f"¿Está seguro de eliminar el servicio?\n\nNombre: {nombre}\nTiempo H: {tiempo_m} min\nTiempo M: {tiempo_f} min"):
            result = servicios_col.delete_one({"nombre": nombre})
            if result.deleted_count > 0:
                messagebox.showinfo("Éxito", "Servicio eliminado")
                cargar_todos_servicios()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el servicio")

    # Crear botones (siempre visibles)
    btn_crear = tk.Button(btn_frame, text="➕ Crear Servicio", command=crear_servicio,
                         bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_crear.grid(row=0, column=0, padx=5)
    
    btn_editar = tk.Button(btn_frame, text="✏️ Editar Servicio", command=editar_servicio,
                          bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_editar.grid(row=0, column=1, padx=5)
    
    btn_eliminar = tk.Button(btn_frame, text="🗑️ Eliminar Servicio", command=eliminar_servicio,
                            bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_eliminar.grid(row=0, column=2, padx=5)

    return tab_servicios