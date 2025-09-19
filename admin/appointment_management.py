import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from database.config import citas_col, users_col, servicios_col, estilistas_col
from utils.helpers import calcular_duracion_por_genero, verificar_disponibilidad_estilista, es_domingo, estilista_tiene_horario

def crear_pestaña_citas(parent, admin_win, mostrar_botones=True):
    tab_citas = ttk.Frame(parent)
    
    # Frame para el árbol de citas
    tree_frame = ttk.Frame(tab_citas)
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    cols_citas = ("cliente", "servicio", "estilista", "fecha", "hora", "estado", "notas")
    tree_citas = ttk.Treeview(tree_frame, columns=cols_citas, show="headings")
    
    # Configurar columnas
    tree_citas.heading("cliente", text="Cliente")
    tree_citas.heading("servicio", text="Servicio")
    tree_citas.heading("estilista", text="Estilista")
    tree_citas.heading("fecha", text="Fecha")
    tree_citas.heading("hora", text="Hora")
    tree_citas.heading("estado", text="Estado")
    tree_citas.heading("notas", text="Notas")
    
    tree_citas.column("cliente", width=150)
    tree_citas.column("servicio", width=120)
    tree_citas.column("estilista", width=120)
    tree_citas.column("fecha", width=100)
    tree_citas.column("hora", width=80)
    tree_citas.column("estado", width=100)
    tree_citas.column("notas", width=150)
    
    # Scrollbar para el treeview
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_citas.yview)
    tree_citas.configure(yscrollcommand=scrollbar.set)
    
    tree_citas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def cargar_citas():
        for row in tree_citas.get_children():
            tree_citas.delete(row)
        for c in citas_col.find().sort("fecha", -1).sort("hora", -1):
            try:
                # Obtener información del cliente con manejo de errores
                cliente_doc = users_col.find_one({"_id": c["cliente_id"]})
                cliente_nombre = cliente_doc["nombre"] if cliente_doc else "Cliente no encontrado"
                
                # Obtener información del servicio con manejo de errores
                servicio_doc = servicios_col.find_one({"_id": c["servicio_id"]})
                servicio_nombre = servicio_doc["nombre"] if servicio_doc else "Servicio no encontrado"
                
                # Obtener información del estilista con manejo de errores
                estilista_doc = estilistas_col.find_one({"_id": c["estilista_id"]})
                estilista_nombre = estilista_doc["nombre"] if estilista_doc else "Estilista no encontrado"
                
                tree_citas.insert("", tk.END, values=(
                    cliente_nombre, 
                    servicio_nombre, 
                    estilista_nombre, 
                    c["fecha"], 
                    c["hora"], 
                    c["estado"], 
                    c.get("notas", "")
                ))
            except Exception as e:
                print(f"Error cargando cita: {e}")
                # Insertar fila con información de error
                tree_citas.insert("", tk.END, values=(
                    "Error", 
                    "Error", 
                    "Error", 
                    c.get("fecha", ""), 
                    c.get("hora", ""), 
                    c.get("estado", ""), 
                    "Datos corruptos o no encontrados"
                ))
    
    cargar_citas()

    # Frame para botones (siempre visible)
    btn_frame = tk.Frame(tab_citas)
    btn_frame.pack(pady=10)

    def crear_cita():
        form = tk.Toplevel(admin_win)
        form.title("Crear Nueva Cita")
        form.geometry("400x550")
        form.configure(bg='white')
        
        form_frame = tk.Frame(form, bg='white')
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(form_frame, text="Cliente:", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(5,2))
        cliente_var = ttk.Combobox(form_frame, values=[u["nombre"] for u in users_col.find({"role": "cliente"})], state="readonly", width=30)
        cliente_var.pack(pady=5)

        tk.Label(form_frame, text="Servicio:", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,2))
        servicio_var = ttk.Combobox(form_frame, values=[s["nombre"] for s in servicios_col.find()], state="readonly", width=30)
        servicio_var.pack(pady=5)

        tk.Label(form_frame, text="Estilista:", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,2))
        estilista_var = ttk.Combobox(form_frame, values=[e["nombre"] for e in estilistas_col.find()], state="readonly", width=30)
        estilista_var.pack(pady=5)

        tk.Label(form_frame, text="Fecha:", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,2))
        fecha_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd", width=27)
        fecha_entry.pack(pady=5)

        tk.Label(form_frame, text="Hora (HH:MM):", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,2))
        hora_entry = tk.Entry(form_frame, width=30)
        hora_entry.pack(pady=5)

        tk.Label(form_frame, text="Notas:", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,2))
        notas_entry = tk.Entry(form_frame, width=30)
        notas_entry.pack(pady=5)

        def guardar_cita():
            cliente_nombre = cliente_var.get()
            servicio_nombre = servicio_var.get()
            estilista_nombre = estilista_var.get()
            fecha = fecha_entry.get_date().strftime("%Y-%m-%d")
            hora = hora_entry.get().strip()
            notas = notas_entry.get().strip()

            if not cliente_nombre or not servicio_nombre or not estilista_nombre or not hora:
                messagebox.showerror("Error", "Complete todos los campos")
                return

            if es_domingo(fecha):
                messagebox.showerror("Error", "No se permiten citas los domingos")
                return

            cliente = users_col.find_one({"nombre": cliente_nombre})
            servicio = servicios_col.find_one({"nombre": servicio_nombre})
            estilista = estilistas_col.find_one({"nombre": estilista_nombre})

            if not cliente or not servicio or not estilista:
                messagebox.showerror("Error", "Datos inválidos")
                return

            # VERIFICAR SI EL ESTILISTA TIENE HORARIO CONFIGURADO
            if not estilista_tiene_horario(estilista["_id"], fecha):
                messagebox.showerror("Error", f"El estilista {estilista_nombre} no tiene horario configurado para el {fecha}. Contacte al administrador.")
                return

            sexo = cliente.get("sexo", "")
            duracion = calcular_duracion_por_genero(servicio_nombre, sexo)

            disponible = verificar_disponibilidad_estilista(estilista["_id"], fecha, hora, duracion)
            if not disponible:
                # Verificar si es por el descanso
                horarios = estilista.get("horarios", {})
                horario_fecha = horarios.get(fecha, {})
                
                if horario_fecha.get("descanso") != "Descanso" and horario_fecha.get("descanso"):
                    hora_descanso = horario_fecha.get("descanso")
                    try:
                        hora_descanso_dt = datetime.strptime(hora_descanso, "%H:%M")
                        fin_descanso_dt = hora_descanso_dt + timedelta(hours=1)
                        fin_descanso = fin_descanso_dt.strftime("%H:%M")
                        
                        hora_cita = datetime.strptime(hora, "%H:%M")
                        if hora_descanso_dt.time() <= hora_cita.time() < fin_descanso_dt.time():
                            messagebox.showerror("Error", f"El estilista está en descanso de {hora_descanso} a {fin_descanso}. No se pueden agendar citas durante este periodo.")
                            return
                    except:
                        pass
                
                messagebox.showerror("Error", "El estilista no está disponible a esa hora. ")
                return

            cita = {
                "cliente_id": cliente["_id"],
                "servicio_id": servicio["_id"],
                "estilista_id": estilista["_id"],
                "fecha": fecha,
                "hora": hora,
                "duracion": duracion,
                "estado": "aceptado",
                "notas": notas,
                "creada_en": datetime.now()
            }
            citas_col.insert_one(cita)
            messagebox.showinfo("Éxito", "Cita creada correctamente")
            form.destroy()
            cargar_citas()

        btn_frame_modal = tk.Frame(form_frame, bg='white')
        btn_frame_modal.pack(pady=20)
        
        tk.Button(btn_frame_modal, text="Guardar Cita", command=guardar_cita, 
                 bg="#2ecc71", fg="white", font=("Arial", 10), width=12).pack(side="left", padx=5)
        tk.Button(btn_frame_modal, text="Cancelar", command=form.destroy,
                 bg="#95a5a6", fg="white", font=("Arial", 10), width=12).pack(side="left", padx=5)

    def aceptar_cita():
        sel = tree_citas.selection()
        if not sel: 
            messagebox.showerror("Error", "Seleccione una cita")
            return
        
        item = tree_citas.item(sel[0])
        valores = item["values"]
        
        if not valores or len(valores) < 7:
            messagebox.showerror("Error", "Datos de cita incompletos")
            return
            
        cliente_nombre = valores[0]
        fecha = valores[3]
        hora = valores[4]
        
        # Buscar la cita por cliente, fecha y hora
        cliente = users_col.find_one({"nombre": cliente_nombre})
        if not cliente:
            messagebox.showerror("Error", "No se pudo encontrar el cliente")
            return
            
        citas_col.update_one({
            "cliente_id": cliente["_id"], 
            "fecha": fecha, 
            "hora": hora
        }, {"$set": {"estado": "aceptado"}})
        
        messagebox.showinfo("Éxito", "Cita aceptada")
        cargar_citas()

    def eliminar_cita():
        sel = tree_citas.selection()
        if not sel: 
            messagebox.showerror("Error", "Seleccione una cita")
            return
        
        item = tree_citas.item(sel[0])
        valores = item["values"]
        
        if not valores or len(valores) < 7:
            messagebox.showerror("Error", "Datos de cita incompletos")
            return
            
        cliente_nombre = valores[0]
        fecha = valores[3]
        hora = valores[4]
        
        if messagebox.askyesno("Confirmar Eliminación", 
                              f"¿Está seguro de eliminar esta cita?\n\nCliente: {cliente_nombre}\nFecha: {fecha}\nHora: {hora}"):
            # Buscar la cita por cliente, fecha y hora
            cliente = users_col.find_one({"nombre": cliente_nombre})
            if not cliente:
                messagebox.showerror("Error", "No se pudo encontrar el cliente")
                return
                
            result = citas_col.delete_one({
                "cliente_id": cliente["_id"], 
                "fecha": fecha, 
                "hora": hora
            })
            
            if result.deleted_count > 0:
                messagebox.showinfo("Éxito", "Cita eliminada")
                cargar_citas()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la cita")

    def editar_cita():
        sel = tree_citas.selection()
        if not sel: 
            messagebox.showerror("Error", "Seleccione una cita")
            return
        
        item = tree_citas.item(sel[0])
        valores = item["values"]
        
        if not valores or len(valores) < 7:
            messagebox.showerror("Error", "Datos de cita incompletos")
            return
            
        cliente_nombre, servicio, estilista, fecha, hora, estado, notas = valores

        form = tk.Toplevel(admin_win)
        form.title("Editar Cita")
        form.geometry("400x500")
        form.configure(bg='white')
        
        form_frame = tk.Frame(form, bg='white')
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(form_frame, text="Servicio:", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(5,2))
        servicio_var = ttk.Combobox(form_frame, values=[s["nombre"] for s in servicios_col.find()], state="readonly", width=30)
        servicio_var.set(servicio)
        servicio_var.pack(pady=5)

        tk.Label(form_frame, text="Estilista:", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,2))
        estilista_var = ttk.Combobox(form_frame, values=[e["nombre"] for e in estilistas_col.find()], state="readonly", width=30)
        estilista_var.set(estilista)
        estilista_var.pack(pady=5)

        tk.Label(form_frame, text="Fecha:", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,2))
        fecha_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd", width=27)
        fecha_entry.set_date(datetime.strptime(fecha, "%Y-%m-%d"))
        fecha_entry.pack(pady=5)

        tk.Label(form_frame, text="Hora (HH:MM):", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,2))
        hora_entry = tk.Entry(form_frame, width=30)
        hora_entry.insert(0, hora)
        hora_entry.pack(pady=5)

        tk.Label(form_frame, text="Notas:", bg='white', font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,2))
        notas_entry = tk.Entry(form_frame, width=30)
        notas_entry.insert(0, notas)
        notas_entry.pack(pady=5)

        def guardar_edicion():
            nuevo_servicio_nombre = servicio_var.get()
            nuevo_estilista_nombre = estilista_var.get()
            nueva_fecha = fecha_entry.get_date().strftime("%Y-%m-%d")
            nueva_hora = hora_entry.get().strip()
            nuevas_notas = notas_entry.get().strip()

            if not nuevo_servicio_nombre or not nuevo_estilista_nombre or not nueva_hora:
                messagebox.showerror("Error", "Complete todos los campos")
                return

            nuevo_servicio = servicios_col.find_one({"nombre": nuevo_servicio_nombre})
            nuevo_estilista = estilistas_col.find_one({"nombre": nuevo_estilista_nombre})

            if not nuevo_servicio or not nuevo_estilista:
                messagebox.showerror("Error", "Servicio o estilista no válidos")
                return

            # VERIFICAR SI EL ESTILISTA TIENE HORARIO CONFIGURADO PARA LA NUEVA FECHA
            if not estilista_tiene_horario(nuevo_estilista["_id"], nueva_fecha):
                messagebox.showerror("Error", f"El estilista {nuevo_estilista_nombre} no tiene horario configurado para el {nueva_fecha}. Contacte al administrador.")
                return

            # Buscar la cita original
            cliente = users_col.find_one({"nombre": cliente_nombre})
            if not cliente:
                messagebox.showerror("Error", "No se pudo encontrar el cliente")
                return

            citas_col.update_one(
                {
                    "cliente_id": cliente["_id"],
                    "fecha": fecha, 
                    "hora": hora
                },
                {"$set": {
                    "servicio_id": nuevo_servicio["_id"],
                    "estilista_id": nuevo_estilista["_id"],
                    "fecha": nueva_fecha,
                    "hora": nueva_hora,
                    "notas": nuevas_notas
                }}
            )
            messagebox.showinfo("Éxito", "Cita actualizada")
            form.destroy()
            cargar_citas()

        btn_frame_modal = tk.Frame(form_frame, bg='white')
        btn_frame_modal.pack(pady=20)
        
        tk.Button(btn_frame_modal, text="Guardar", command=guardar_edicion, 
                 bg="#3498db", fg="white", font=("Arial", 10), width=12).pack(side="left", padx=5)
        tk.Button(btn_frame_modal, text="Cancelar", command=form.destroy,
                 bg="#95a5a6", fg="white", font=("Arial", 10), width=12).pack(side="left", padx=5)

    # Crear botones (siempre visibles)
    btn_crear = tk.Button(btn_frame, text="➕ Crear Cita", command=crear_cita,
                         bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), width=12)
    btn_crear.grid(row=0, column=0, padx=5)
    
    btn_aceptar = tk.Button(btn_frame, text="✅ Aceptar", command=aceptar_cita,
                           bg="#27ae60", fg="white", font=("Arial", 10, "bold"), width=12)
    btn_aceptar.grid(row=0, column=1, padx=5)
    
    btn_editar = tk.Button(btn_frame, text="✏️ Editar", command=editar_cita,
                          bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=12)
    btn_editar.grid(row=0, column=2, padx=5)
    
    btn_eliminar = tk.Button(btn_frame, text="🗑️ Eliminar", command=eliminar_cita,
                            bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=12)
    btn_eliminar.grid(row=0, column=3, padx=5)

    return tab_citas