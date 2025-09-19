import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.config import citas_col, servicios_col, estilistas_col

def crear_panel_servicios(parent, user):
    frame = ttk.Frame(parent)
    
    # Título
    title_label = tk.Label(frame, text="Mis Citas Agendadas", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=10)
    
    # Treeview para mostrar las citas
    columns = ("Servicio", "Estilista", "Fecha", "Hora", "Duración", "Estado", "Notas")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
    
    # Configurar columnas
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
    
    tree.column("Servicio", width=150)
    tree.column("Estilista", width=120)
    tree.column("Notas", width=200)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")
    
    def cargar_citas():
        # Limpiar treeview
        for item in tree.get_children():
            tree.delete(item)
        
        # Obtener citas del usuario
        citas = citas_col.find({"cliente_id": user["_id"]})
        
        for cita in citas:
            # Obtener nombres del servicio y estilista
            servicio = servicios_col.find_one({"_id": cita["servicio_id"]})
            estilista = estilistas_col.find_one({"_id": cita["estilista_id"]})
            
            servicio_nombre = servicio["nombre"] if servicio else "No encontrado"
            estilista_nombre = estilista["nombre"] if estilista else "No encontrado"
            
            # Insertar en treeview
            tree.insert("", "end", values=(
                servicio_nombre,
                estilista_nombre,
                cita["fecha"],
                cita["hora"],
                f"{cita['duracion']} min",
                cita["estado"],
                cita.get("notas", "")
            ))
    
    # Botón para refrescar
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(pady=5)
    
    btn_refrescar = tk.Button(btn_frame, text="Refrescar", command=cargar_citas, 
                                bg="#3498db", fg="white", font=("Helvetica", 10))
    btn_refrescar.pack(side="left", padx=5)
    
    # Cargar citas inicialmente
    cargar_citas()
    
    return frame