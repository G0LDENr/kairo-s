import tkinter as tk
from tkinter import messagebox, ttk
from database.config import users_col
from auth.authentication import register_user

def crear_pestaña_usuarios(parent, admin_win, mostrar_botones=True):
    tab_usuarios = ttk.Frame(parent)

    # Variables de paginación
    ROWS_PER_PAGE = 50
    current_page = tk.IntVar(value=1)
    total_pages = tk.IntVar(value=1)
    all_users = []  # lista de usuarios cargados de DB
    filtered_users = []  # lista filtrada según búsqueda

    # ---------------- BUSQUEDA ----------------
    search_frame = tk.Frame(tab_usuarios)
    search_frame.pack(fill="x", padx=20, pady=5)

    tk.Label(search_frame, text="Buscar:").pack(side="left")
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=5)

    def filtrar_usuarios(*args):
        query = search_var.get().lower()
        nonlocal filtered_users, current_page, total_pages
        filtered_users = [
            u for u in all_users
            if query in u.get("nombre", "").lower() 
            or query in u.get("correo", "").lower() 
            or query in u.get("telefono", "").lower()
        ]
        current_page.set(1)
        total_pages.set(max(1, (len(filtered_users) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE))
        cargar_usuarios()

    search_var.trace_add("write", filtrar_usuarios)

    # ---------------- TREEVIEW ----------------
    tree_frame = ttk.Frame(tab_usuarios)
    tree_frame.pack(fill="both", expand=True, padx=20, pady=5)

    columns = ("nombre", "correo", "telefono", "sexo", "role")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

    for col, width in zip(columns, [150, 150, 100, 80, 100]):
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=width)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ---------------- PAGINACION ----------------
    pagination_frame = tk.Frame(tab_usuarios)
    pagination_frame.pack(pady=5)

    btn_prev = tk.Button(pagination_frame, text="⏮ Anterior")
    btn_prev.pack(side="left", padx=5)
    lbl_page = tk.Label(pagination_frame, textvariable=current_page)
    lbl_page.pack(side="left")
    lbl_total = tk.Label(pagination_frame, textvariable=total_pages)
    lbl_total.pack(side="left", padx=5)
    btn_next = tk.Button(pagination_frame, text="⏭ Siguiente")
    btn_next.pack(side="left", padx=5)

    def cargar_usuarios():
        tree.delete(*tree.get_children())
        start = (current_page.get() - 1) * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE
        for u in filtered_users[start:end]:
            tree.insert("", tk.END, values=(
                u.get("nombre", ""),
                u.get("correo", ""),
                u.get("telefono", ""),
                u.get("sexo", ""),
                u.get("role", "cliente")
            ))

    def pagina_siguiente():
        if current_page.get() < total_pages.get():
            current_page.set(current_page.get() + 1)
            cargar_usuarios()

    def pagina_anterior():
        if current_page.get() > 1:
            current_page.set(current_page.get() - 1)
            cargar_usuarios()

    btn_next.config(command=pagina_siguiente)
    btn_prev.config(command=pagina_anterior)

    # ---------------- CARGAR USUARIOS ----------------
    all_users = list(users_col.find())
    filtered_users = all_users.copy()
    total_pages.set(max(1, (len(filtered_users) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE))
    cargar_usuarios()

    # ---------------- BOTONES CREAR / MODIFICAR / ELIMINAR ----------------
    btn_frame = tk.Frame(tab_usuarios)
    btn_frame.pack(pady=10)

    # Crear usuario
    def crear_usuario():
        def save_new_user():
            n = entry_nombre.get().strip()
            c = entry_correo.get().strip()
            p = entry_password.get().strip()
            t = entry_telefono.get().strip()
            s = sexo_var.get()
            r = role_var.get()
            
            success, msg = register_user(n, c, p, t, s, r)
            if success:
                messagebox.showinfo("Éxito", msg)
                new_win.destroy()
                # recargar
                all_users[:] = list(users_col.find())
                filtrar_usuarios()
            else:
                messagebox.showerror("Error", msg)

        new_win = tk.Toplevel(admin_win)
        new_win.title("Crear Nuevo Usuario")
        new_win.geometry("300x400")
        new_win.configure(bg='white')
        
        form_frame = tk.Frame(new_win, bg='white')
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        tk.Label(form_frame, text="Nombre", bg='white').pack(anchor="w")
        entry_nombre = tk.Entry(form_frame, width=30)
        entry_nombre.pack(pady=5)
        
        tk.Label(form_frame, text="Correo", bg='white').pack(anchor="w")
        entry_correo = tk.Entry(form_frame, width=30)
        entry_correo.pack(pady=5)
        
        tk.Label(form_frame, text="Contraseña", bg='white').pack(anchor="w")
        entry_password = tk.Entry(form_frame, show="*", width=30)
        entry_password.pack(pady=5)
        
        tk.Label(form_frame, text="Teléfono", bg='white').pack(anchor="w")
        entry_telefono = tk.Entry(form_frame, width=30)
        entry_telefono.pack(pady=5)
        
        tk.Label(form_frame, text="Sexo", bg='white').pack(anchor="w")
        sexo_var = tk.StringVar(value="F")
        sexo_menu = ttk.Combobox(form_frame, textvariable=sexo_var, values=["F", "M"], state="readonly", width=27)
        sexo_menu.pack(pady=5)
        
        tk.Label(form_frame, text="Rol", bg='white').pack(anchor="w")
        role_var = tk.StringVar(value="cliente")
        role_menu = ttk.Combobox(form_frame, textvariable=role_var, values=["cliente", "admin"], state="readonly", width=27)
        role_menu.pack(pady=5)
        
        btn_frame_modal = tk.Frame(form_frame, bg='white')
        btn_frame_modal.pack(pady=20)
        
        tk.Button(btn_frame_modal, text="Guardar", command=save_new_user, 
                 bg="#2ecc71", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame_modal, text="Cancelar", command=new_win.destroy,
                 bg="#95a5a6", fg="white", width=10).pack(side="left", padx=5)

    # Modificar usuario
    def modificar_usuario():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione un usuario")
            return
        item = tree.item(sel[0])
        correo_original = item["values"][1]
        u = users_col.find_one({"correo": correo_original})
        if not u:
            messagebox.showerror("Error", "Usuario no encontrado")
            return

        def save_changes():
            n = entry_nombre.get().strip()
            c = entry_correo.get().strip()
            t = entry_telefono.get().strip()
            s = sexo_var.get()
            r = role_var.get()
            
            if c != correo_original:
                if users_col.find_one({"correo": c}):
                    messagebox.showerror("Error", "El correo ya está en uso por otro usuario")
                    return
            
            users_col.update_one(
                {"correo": correo_original},
                {"$set": {"nombre": n, "correo": c, "telefono": t, "sexo": s, "role": r}}
            )
            messagebox.showinfo("Éxito", "Usuario modificado correctamente")
            edit_win.destroy()
            all_users[:] = list(users_col.find())
            filtrar_usuarios()

        edit_win = tk.Toplevel(admin_win)
        edit_win.title("Modificar Usuario")
        edit_win.geometry("300x350")
        edit_win.configure(bg='white')
        
        form_frame = tk.Frame(edit_win, bg='white')
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        tk.Label(form_frame, text="Nombre", bg='white').pack(anchor="w")
        entry_nombre = tk.Entry(form_frame, width=30)
        entry_nombre.insert(0, u["nombre"])
        entry_nombre.pack(pady=5)
        
        tk.Label(form_frame, text="Correo", bg='white').pack(anchor="w")
        entry_correo = tk.Entry(form_frame, width=30)
        entry_correo.insert(0, u["correo"])
        entry_correo.pack(pady=5)
        
        tk.Label(form_frame, text="Teléfono", bg='white').pack(anchor="w")
        entry_telefono = tk.Entry(form_frame, width=30)
        entry_telefono.insert(0, u.get("telefono", ""))
        entry_telefono.pack(pady=5)
        
        tk.Label(form_frame, text="Sexo", bg='white').pack(anchor="w")
        sexo_var = tk.StringVar(value=u.get("sexo", "F"))
        sexo_menu = ttk.Combobox(form_frame, textvariable=sexo_var, values=["F", "M"], state="readonly", width=27)
        sexo_menu.pack(pady=5)
        
        tk.Label(form_frame, text="Rol", bg='white').pack(anchor="w")
        role_var = tk.StringVar(value=u.get("role", "cliente"))
        role_menu = ttk.Combobox(form_frame, textvariable=role_var, values=["cliente", "admin"], state="readonly", width=27)
        role_menu.pack(pady=5)
        
        btn_frame_modal = tk.Frame(form_frame, bg='white')
        btn_frame_modal.pack(pady=20)
        
        tk.Button(btn_frame_modal, text="Guardar", command=save_changes, 
                 bg="#3498db", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame_modal, text="Cancelar", command=edit_win.destroy,
                 bg="#95a5a6", fg="white", width=10).pack(side="left", padx=5)

    # Eliminar usuario
    def eliminar_usuario():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione un usuario")
            return
        item = tree.item(sel[0])
        correo = item["values"][1]
        nombre = item["values"][0]
        
        if messagebox.askyesno("Confirmar Eliminación", 
                              f"¿Está seguro de que desea eliminar al usuario:\n\n{nombre}\n{correo}?"):
            result = users_col.delete_one({"correo": correo})
            if result.deleted_count > 0:
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                all_users[:] = list(users_col.find())
                filtrar_usuarios()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario")

    # Botones principales
    btn_crear = tk.Button(btn_frame, text="➕ Crear Usuario", command=crear_usuario,
                         bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_crear.grid(row=0, column=0, padx=5)
    
    btn_modificar = tk.Button(btn_frame, text="✏️ Modificar Usuario", command=modificar_usuario,
                             bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_modificar.grid(row=0, column=1, padx=5)
    
    btn_eliminar = tk.Button(btn_frame, text="🗑️ Eliminar Usuario", command=eliminar_usuario,
                            bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_eliminar.grid(row=0, column=2, padx=5)

    return tab_usuarios
