import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from database.config import citas_col, servicios_col, estilistas_col
from utils.helpers import calcular_duracion_por_genero, verificar_disponibilidad_estilista, es_domingo, estilista_tiene_horario

def crear_seccion_agendar(parent, user):
    frame = ttk.Frame(parent, padding="20")
    frame.pack(fill="both", expand=True)
    
    # Título principal
    title_label = tk.Label(frame, text="Agendar Cita", font=("Helvetica", 16, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
    
    # Crear un frame para contener todos los campos del formulario
    form_frame = ttk.Frame(frame)
    form_frame.grid(row=1, column=0, sticky="ew", padx=10)
    
    # Configurar grid para que se expanda
    form_frame.columnconfigure(1, weight=1)
    
    # Servicio
    tk.Label(form_frame, text="Servicio:", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
    servicio_var = ttk.Combobox(form_frame, values=[s["nombre"] for s in servicios_col.find()], state="readonly", width=30)
    servicio_var.grid(row=0, column=1, sticky="ew", pady=5)
    
    # Estilista
    tk.Label(form_frame, text="Estilista:", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=5, padx=(0, 10))
    estilista_var = ttk.Combobox(form_frame, values=[e["nombre"] for e in estilistas_col.find()], state="readonly", width=30)
    estilista_var.grid(row=1, column=1, sticky="ew", pady=5)
    
    # Fecha
    tk.Label(form_frame, text="Fecha:", font=("Helvetica", 10)).grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
    fecha_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd", width=28)
    fecha_entry.grid(row=2, column=1, sticky="w", pady=5)
    
    # Hora
    tk.Label(form_frame, text="Hora (HH:MM):", font=("Helvetica", 10)).grid(row=3, column=0, sticky="w", pady=5, padx=(0, 10))
    hora_entry = tk.Entry(form_frame, width=32)
    hora_entry.grid(row=3, column=1, sticky="w", pady=5)
    
    # Notas
    tk.Label(form_frame, text="Notas:", font=("Helvetica", 10)).grid(row=4, column=0, sticky="w", pady=5, padx=(0, 10))
    notas_entry = tk.Entry(form_frame, width=32)
    notas_entry.grid(row=4, column=1, sticky="w", pady=5)
    
    # Duración
    lbl_duracion = tk.Label(form_frame, text="Duración: -", font=("Helvetica", 10))
    lbl_duracion.grid(row=5, column=0, columnspan=2, pady=10)
    
    # Botón de agendar
    button_frame = ttk.Frame(frame)
    button_frame.grid(row=2, column=0, pady=20)
    
    btn_agendar = tk.Button(button_frame, text="Agendar Cita", command=lambda: agendar_cita_cliente(), 
                           bg="#2ecc71", fg="white", font=("Helvetica", 10, "bold"), padx=15, pady=5)
    btn_agendar.pack()

    def actualizar_duracion_cliente(event=None):
        servicio = servicio_var.get()
        if not servicio:
            lbl_duracion.config(text="Duración: -")
            return
        sexo = user.get("sexo","")
        dur = calcular_duracion_por_genero(servicio, sexo)
        lbl_duracion.config(text=f"Duración: {dur} min")

    servicio_var.bind("<<ComboboxSelected>>", actualizar_duracion_cliente)

    def agendar_cita_cliente():
        servicio = servicio_var.get()
        estilista = estilista_var.get()
        fecha = fecha_entry.get_date()
        fecha_str = fecha.strftime("%Y-%m-%d")
        hora = hora_entry.get().strip()
        notas = notas_entry.get().strip()
        
        if not servicio or not estilista or not hora:
            messagebox.showerror("Error","Complete todos los campos")
            return
            
        if es_domingo(fecha_str):
            messagebox.showerror("Error", "No se permiten citas los domingos")
            return
            
        cliente_id = user["_id"]
        servicio_doc = servicios_col.find_one({"nombre":servicio})
        estilista_doc = estilistas_col.find_one({"nombre":estilista})
        
        if not servicio_doc or not estilista_doc:
            messagebox.showerror("Error","Datos inválidos")
            return
            
        servicio_id = servicio_doc["_id"]
        estilista_id = estilista_doc["_id"]
        
        # VERIFICAR SI EL ESTILISTA TIENE HORARIO CONFIGURADO
        if not estilista_tiene_horario(estilista_id, fecha_str):
            messagebox.showerror("Error", f"El estilista {estilista} no tiene horario configurado para el {fecha_str}. Contacte al administrador.")
            return
            
        sexo = user.get("sexo","")
        dur = calcular_duracion_por_genero(servicio, sexo)
        
        disponible = verificar_disponibilidad_estilista(estilista_id, fecha_str, hora, dur)
        if not disponible:
            # Verificar si es por el descanso
            estilista_doc = estilistas_col.find_one({"_id": estilista_id})
            horarios = estilista_doc.get("horarios", {})
            horario_fecha = horarios.get(fecha_str, {})
            
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
            
            messagebox.showerror("Error","Ese horario ya está ocupado o el estilista no está disponible")
            return
            
        cita = {
            "cliente_id": cliente_id,
            "servicio_id": servicio_id,
            "estilista_id": estilista_id,
            "fecha": fecha_str,
            "hora": hora,
            "duracion": dur,
            "estado":"pendiente",
            "notas": notas,
            "creada_en": datetime.now()
        }
        citas_col.insert_one(cita)
        messagebox.showinfo("Éxito","Cita agendada correctamente")
        hora_entry.delete(0, tk.END)
        notas_entry.delete(0, tk.END)
        lbl_duracion.config(text="Duración: -")

    return frame