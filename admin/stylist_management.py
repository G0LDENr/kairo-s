import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar
from database.config import estilistas_col
from utils.helpers import generar_horas_disponibles, validar_horario, es_domingo

def crear_pestaña_estilistas(parent, admin_win, mostrar_botones=True):
    tab_estilistas = ttk.Frame(parent)
    
    # Variables de paginación
    ROWS_PER_PAGE = 50
    current_page = tk.IntVar(value=1)
    total_pages = tk.IntVar(value=1)
    all_estilistas = []  # lista de estilistas cargados de DB
    filtered_estilistas = []  # lista filtrada según búsqueda

    # ---------------- BUSQUEDA ----------------
    search_frame = tk.Frame(tab_estilistas)
    search_frame.pack(fill="x", padx=20, pady=5)

    tk.Label(search_frame, text="Buscar:").pack(side="left")
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=5)

    def filtrar_estilistas(*args):
        query = search_var.get().lower()
        nonlocal filtered_estilistas, current_page, total_pages
        filtered_estilistas = [
            e for e in all_estilistas
            if query in e.get("nombre", "").lower() 
            or query in e.get("telefono", "").lower()
        ]
        current_page.set(1)
        total_pages.set(max(1, (len(filtered_estilistas) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE))
        cargar_estilistas()

    search_var.trace_add("write", filtrar_estilistas)

    # ---------------- TREEVIEW ----------------
    tree_frame = ttk.Frame(tab_estilistas)
    tree_frame.pack(fill="both", expand=True, padx=20, pady=5)

    cols_estilistas = ("nombre", "telefono")
    tree_est = ttk.Treeview(tree_frame, columns=cols_estilistas, show="headings")

    # Configurar columnas
    tree_est.heading("nombre", text="Nombre")
    tree_est.heading("telefono", text="Teléfono")
    
    tree_est.column("nombre", width=200)
    tree_est.column("telefono", width=150)

    # Scrollbar para el treeview
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_est.yview)
    tree_est.configure(yscrollcommand=scrollbar.set)
    
    tree_est.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ---------------- PAGINACION ----------------
    pagination_frame = tk.Frame(tab_estilistas)
    pagination_frame.pack(pady=5)

    btn_prev = tk.Button(pagination_frame, text="⏮ Anterior")
    btn_prev.pack(side="left", padx=5)
    lbl_page = tk.Label(pagination_frame, textvariable=current_page)
    lbl_page.pack(side="left")
    lbl_total = tk.Label(pagination_frame, textvariable=total_pages)
    lbl_total.pack(side="left", padx=5)
    btn_next = tk.Button(pagination_frame, text="⏭ Siguiente")
    btn_next.pack(side="left", padx=5)

    def cargar_estilistas():
        for row in tree_est.get_children():
            tree_est.delete(row)
        
        start = (current_page.get() - 1) * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE
        for e in filtered_estilistas[start:end]:
            tree_est.insert("", tk.END, values=(e["nombre"], e.get("telefono", "")))

    def pagina_siguiente():
        if current_page.get() < total_pages.get():
            current_page.set(current_page.get() + 1)
            cargar_estilistas()

    def pagina_anterior():
        if current_page.get() > 1:
            current_page.set(current_page.get() - 1)
            cargar_estilistas()

    btn_next.config(command=pagina_siguiente)
    btn_prev.config(command=pagina_anterior)

    # ---------------- CARGAR ESTILISTAS ----------------
    def cargar_todos_estilistas():
        nonlocal all_estilistas, filtered_estilistas
        all_estilistas = list(estilistas_col.find())
        filtered_estilistas = all_estilistas.copy()
        total_pages.set(max(1, (len(filtered_estilistas) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE))
        cargar_estilistas()

    cargar_todos_estilistas()

    # Frame para botones (siempre visible)
    btn_frame = tk.Frame(tab_estilistas)
    btn_frame.pack(pady=10)

    def crear_estilista():
        def save_estilista():
            n = entry_nombre.get().strip()
            t = entry_telefono.get().strip()
            if not n:
                messagebox.showerror("Error", "Nombre requerido")
                return
            estilistas_col.insert_one({"nombre": n, "telefono": t, "horarios": {}})
            messagebox.showinfo("Éxito", "Estilista agregado")
            new_win.destroy()
            cargar_todos_estilistas()

        new_win = tk.Toplevel(admin_win)
        new_win.title("Crear Estilista")
        new_win.geometry("300x200")
        new_win.configure(bg='white')
        
        form_frame = tk.Frame(new_win, bg='white')
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        tk.Label(form_frame, text="Nombre", bg='white').pack(anchor="w")
        entry_nombre = tk.Entry(form_frame, width=30)
        entry_nombre.pack(pady=5)
        
        tk.Label(form_frame, text="Teléfono", bg='white').pack(anchor="w")
        entry_telefono = tk.Entry(form_frame, width=30)
        entry_telefono.pack(pady=5)
        
        btn_frame_modal = tk.Frame(form_frame, bg='white')
        btn_frame_modal.pack(pady=20)
        
        tk.Button(btn_frame_modal, text="Guardar", command=save_estilista, 
                 bg="#2ecc71", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame_modal, text="Cancelar", command=new_win.destroy,
                 bg="#95a5a6", fg="white", width=10).pack(side="left", padx=5)

    def editar_estilista():
        sel = tree_est.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione un estilista")
            return
        item = tree_est.item(sel[0])
        nombre_actual = item["values"][0]
        telefono_actual = item["values"][1] if len(item["values"]) > 1 else ""

        def guardar_edicion():
            nuevo_nombre = entry_nombre.get().strip()
            nuevo_telefono = entry_telefono.get().strip()
            
            if not nuevo_nombre:
                messagebox.showerror("Error", "Nombre requerido")
                return
                
            estilistas_col.update_one(
                {"nombre": nombre_actual},
                {"$set": {"nombre": nuevo_nombre, "telefono": nuevo_telefono}}
            )
            messagebox.showinfo("Éxito", "Estilista actualizado")
            edit_win.destroy()
            cargar_todos_estilistas()

        edit_win = tk.Toplevel(admin_win)
        edit_win.title("Editar Estilista")
        edit_win.geometry("300x200")
        edit_win.configure(bg='white')
        
        form_frame = tk.Frame(edit_win, bg='white')
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        tk.Label(form_frame, text="Nombre", bg='white').pack(anchor="w")
        entry_nombre = tk.Entry(form_frame, width=30)
        entry_nombre.insert(0, nombre_actual)
        entry_nombre.pack(pady=5)
        
        tk.Label(form_frame, text="Teléfono", bg='white').pack(anchor="w")
        entry_telefono = tk.Entry(form_frame, width=30)
        entry_telefono.insert(0, telefono_actual)
        entry_telefono.pack(pady=5)
        
        btn_frame_modal = tk.Frame(form_frame, bg='white')
        btn_frame_modal.pack(pady=20)
        
        tk.Button(btn_frame_modal, text="Guardar", command=guardar_edicion, 
                 bg="#3498db", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(btn_frame_modal, text="Cancelar", command=edit_win.destroy,
                 bg="#95a5a6", fg="white", width=10).pack(side="left", padx=5)

    def eliminar_estilista():
        sel = tree_est.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione un estilista")
            return
            
        item = tree_est.item(sel[0])
        nombre = item["values"][0]
        telefono = item["values"][1] if len(item["values"]) > 1 else ""
        
        if messagebox.askyesno("Confirmar Eliminación", 
                              f"¿Está seguro de eliminar al estilista?\n\nNombre: {nombre}\nTeléfono: {telefono}"):
            result = estilistas_col.delete_one({"nombre": nombre})
            if result.deleted_count > 0:
                messagebox.showinfo("Éxito", "Estilista eliminado")
                cargar_todos_estilistas()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el estilista")

    def editar_horario():
        sel = tree_est.selection()
        if not sel:
            messagebox.showerror("Error", "Seleccione un estilista")
            return
        item = tree_est.item(sel[0])
        nombre = item["values"][0]
        estilista = estilistas_col.find_one({"nombre": nombre})
        if not estilista:
            messagebox.showerror("Error", "No se encontró el estilista")
            return

        edit_win = tk.Toplevel(admin_win)
        edit_win.title(f"Editar Horario - {nombre}")
        edit_win.geometry("500x500")
        edit_win.configure(bg='white')

        horarios_actuales = estilista.get("horarios", {})
        
        tk.Label(edit_win, text="Seleccione una fecha:", font=("Helvetica", 10, "bold"), bg='white').pack(pady=5)
        cal = Calendar(edit_win, selectmode='day', date_pattern='y-mm-dd')
        cal.pack(pady=5)

        control_frame = tk.Frame(edit_win, bg='white')
        control_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(control_frame, text="Hora inicio:", bg='white').grid(row=0, column=0, padx=5, pady=5)
        inicio_var = tk.StringVar(value="11:00")
        inicio_cb = ttk.Combobox(control_frame, textvariable=inicio_var, values=generar_horas_disponibles(), width=8, state="readonly")
        inicio_cb.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(control_frame, text="Hora fin:", bg='white').grid(row=0, column=2, padx=5, pady=5)
        fin_var = tk.StringVar(value="20:00")
        fin_cb = ttk.Combobox(control_frame, textvariable=fin_var, values=generar_horas_disponibles(), width=8, state="readonly")
        fin_cb.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(control_frame, text="Descanso:", bg='white').grid(row=0, column=4, padx=5, pady=5)
        descanso_var = tk.StringVar(value="14:00")
        descanso_cb = ttk.Combobox(control_frame, textvariable=descanso_var, 
        values=generar_horas_disponibles() + ["Descanso"], width=8, state="readonly")
        descanso_cb.grid(row=0, column=5, padx=5, pady=5)

        def actualizar_controles_por_fecha():
            fecha_seleccionada = cal.get_date()
            
            # Verificar si es domingo
            if es_domingo(fecha_seleccionada):
                # Domingo: forzar modo "Descanso" y deshabilitar controles
                descanso_var.set("Descanso")
                inicio_var.set("")
                fin_var.set("")
                inicio_cb.config(state="disabled")
                fin_cb.config(state="disabled")
                descanso_cb.config(state="readonly")
                tk.Label(control_frame, text="Domingo - Descanso obligatorio", fg="red", bg='white').grid(row=1, column=0, columnspan=6, pady=5)
            else:
                # No es domingo: cargar horario normal
                horario_fecha = horarios_actuales.get(fecha_seleccionada, {})
                
                if horario_fecha.get("descanso") == "Descanso":
                    descanso_var.set("Descanso")
                    inicio_var.set("")
                    fin_var.set("")
                    inicio_cb.config(state="disabled")
                    fin_cb.config(state="disabled")
                else:
                    inicio_var.set(horario_fecha.get("inicio", "11:00"))
                    fin_var.set(horario_fecha.get("fin", "20:00"))
                    descanso_var.set(horario_fecha.get("descanso", "14:00"))
                    inicio_cb.config(state="readonly")
                    fin_cb.config(state="readonly")
                
                # Limpiar mensaje de domingo si existe
                for widget in control_frame.grid_slaves():
                    if widget.grid_info()["row"] == 1:
                        widget.destroy()

        def toggle_horas_habilitadas():
            fecha_seleccionada = cal.get_date()
            
            # No permitir cambiar de Descanso si es domingo
            if es_domingo(fecha_seleccionada):
                descanso_var.set("Descanso")
                messagebox.showinfo("Información", "Los domingos son automáticamente días de descanso")
                return
                
            if descanso_var.get() == "Descanso":
                inicio_cb.config(state="disabled")
                fin_cb.config(state="disabled")
                inicio_var.set("")
                fin_var.set("")
            else:
                inicio_cb.config(state="readonly")
                fin_cb.config(state="readonly")
                if not inicio_var.get():
                    inicio_var.set("11:00")
                if not fin_var.get():
                    fin_var.set("20:00")

        descanso_cb.bind("<<ComboboxSelected>>", lambda e: toggle_horas_habilitadas())
        cal.bind("<<CalendarSelected>>", lambda e: actualizar_controles_por_fecha())

        def cargar_horario_fecha():
            fecha_seleccionada = cal.get_date()
            
            # Verificar si es domingo
            if es_domingo(fecha_seleccionada):
                # Domingo: forzar modo "Descanso"
                descanso_var.set("Descanso")
                inicio_var.set("")
                fin_var.set("")
                inicio_cb.config(state="disabled")
                fin_cb.config(state="disabled")
                return
                
            horario_fecha = horarios_actuales.get(fecha_seleccionada, {})
            
            if horario_fecha.get("descanso") == "Descanso":
                descanso_var.set("Descanso")
                inicio_var.set("")
                fin_var.set("")
                inicio_cb.config(state="disabled")
                fin_cb.config(state="disabled")
            else:
                inicio_var.set(horario_fecha.get("inicio", "11:00"))
                fin_var.set(horario_fecha.get("fin", "20:00"))
                descanso_var.set(horario_fecha.get("descanso", "14:00"))
                inicio_cb.config(state="readonly")
                fin_cb.config(state="readonly")

        def guardar_horario_fecha():
            fecha_seleccionada = cal.get_date()
            
            # Si es domingo, forzar guardar como descanso
            if es_domingo(fecha_seleccionada):
                horarios_actuales[fecha_seleccionada] = {
                    "descanso": "Descanso",
                    "inicio": "",
                    "fin": ""
                }
                messagebox.showinfo("Éxito", f"Domingo automáticamente marcado como descanso para {fecha_seleccionada}")
                return
            
            if descanso_var.get() != "Descanso":
                valido, mensaje = validar_horario(inicio_var.get(), fin_var.get(), descanso_var.get())
                if not valido:
                    messagebox.showerror("Error", mensaje)
                    return
            
            if descanso_var.get() == "Descanso":
                horarios_actuales[fecha_seleccionada] = {
                    "descanso": "Descanso",
                    "inicio": "",
                    "fin": ""
                }
            else:
                horarios_actuales[fecha_seleccionada] = {
                    "inicio": inicio_var.get(),
                    "fin": fin_var.get(),
                    "descanso": descanso_var.get()
                }
            
            messagebox.showinfo("Éxito", f"Horario guardado para {fecha_seleccionada}")

        def guardar_todos_horarios():
            for fecha, horario in horarios_actuales.items():
                # Los domingos siempre deben ser descanso
                if es_domingo(fecha):
                    if horario.get("descanso") != "Descanso":
                        horarios_actuales[fecha] = {
                            "descanso": "Descanso",
                            "inicio": "",
                            "fin": ""
                        }
                    continue
                    
                if horario.get("descanso") != "Descanso":
                    valido, mensaje = validar_horario(
                        horario.get("inicio"), 
                        horario.get("fin"), 
                        horario.get("descanso")
                    )
                    if not valido:
                        messagebox.showerror("Error", f"Error en fecha {fecha}: {mensaje}")
                        return
            
            estilistas_col.update_one({"_id": estilista["_id"]}, {"$set": {"horarios": horarios_actuales}})
            messagebox.showinfo("Éxito", "Todos los horarios guardados")
            edit_win.destroy()
            cargar_todos_estilistas()

        btn_frame_modal = tk.Frame(edit_win, bg='white')
        btn_frame_modal.pack(fill="x", padx=10, pady=10)
        
        tk.Button(btn_frame_modal, text="Cargar horario", command=cargar_horario_fecha, 
                 bg="#3498db", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame_modal, text="Guardar horario", command=guardar_horario_fecha, 
                 bg="#2ecc71", fg="white", width=12).pack(side="left", padx=5)
        tk.Button(btn_frame_modal, text="Guardar Todos", command=guardar_todos_horarios, 
                 bg="#2ecc71", fg="white", width=12).pack(side="right", padx=5)
        tk.Button(btn_frame_modal, text="Cancelar", command=edit_win.destroy, 
                 bg="#e74c3c", fg="white", width=12).pack(side="right", padx=5)

        cargar_horario_fecha()

    # Crear botones (siempre visibles)
    btn_crear = tk.Button(btn_frame, text="➕ Crear Estilista", command=crear_estilista,
                         bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_crear.grid(row=0, column=0, padx=5)
    
    btn_editar = tk.Button(btn_frame, text="✏️ Editar Estilista", command=editar_estilista,
                          bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_editar.grid(row=0, column=1, padx=5)
    
    btn_eliminar = tk.Button(btn_frame, text="🗑️ Eliminar Estilista", command=eliminar_estilista,
                            bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_eliminar.grid(row=0, column=2, padx=5)
    
    btn_horario = tk.Button(btn_frame, text="⏰ Editar Horario", command=editar_horario,
                           bg="#f39c12", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_horario.grid(row=0, column=3, padx=5)

    return tab_estilistas