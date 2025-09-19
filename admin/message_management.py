import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from database.config import mensajes_col
from bson import ObjectId

def crear_panel_mensajes(parent):
    frame = ttk.Frame(parent)
    
    # Título
    title_label = tk.Label(frame, text="Gestión de Mensajes de Clientes", 
                          font=("Helvetica", 16, "bold"))
    title_label.pack(pady=10)
    
    # Frame para filtros
    filter_frame = ttk.Frame(frame)
    filter_frame.pack(fill="x", padx=10, pady=(0, 10))
    
    tk.Label(filter_frame, text="Filtrar por estado:").pack(side="left", padx=(0, 10))
    
    # Variable para el filtro seleccionado
    filtro_estado = tk.StringVar(value="todos")
    
    # Opciones de filtro
    opciones_filtro = [
        ("Todos", "todos"),
        ("No leídos", "no_leido"),
        ("Leídos", "leido"),
        ("Respondidos", "respondido"),
        ("No Respondidos", "no_respondido")
    ]
    
    for texto, valor in opciones_filtro:
        ttk.Radiobutton(filter_frame, text=texto, variable=filtro_estado, 
                       value=valor, command=lambda: cargar_mensajes()).pack(side="left", padx=5)
    
    # Frame principal para dividir la interfaz
    main_frame = ttk.Frame(frame)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Treeview para mostrar mensajes
    columns = ("Cliente", "Asunto", "Fecha", "Estado")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
    
    tree.column("Cliente", width=150)
    tree.column("Asunto", width=200)
    
    # Scrollbar para el treeview
    tree_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=tree_scrollbar.set)
    
    # Empaquetar treeview y scrollbar
    tree.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
    tree_scrollbar.grid(row=0, column=1, sticky="ns")
    
    # Frame para detalles y respuesta
    detail_frame = ttk.LabelFrame(main_frame, text="Detalles del Mensaje")
    detail_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
    
    # Configurar pesos de las columnas
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(2, weight=1)
    main_frame.rowconfigure(0, weight=1)
    
    # Campos de detalles
    tk.Label(detail_frame, text="Cliente:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
    cliente_var = tk.StringVar()
    tk.Label(detail_frame, textvariable=cliente_var, wraplength=300).grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    tk.Label(detail_frame, text="Fecha:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
    fecha_var = tk.StringVar()
    tk.Label(detail_frame, textvariable=fecha_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)
    
    tk.Label(detail_frame, text="Asunto:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
    asunto_var = tk.StringVar()
    tk.Label(detail_frame, textvariable=asunto_var, wraplength=300).grid(row=2, column=1, sticky="w", padx=5, pady=2)
    
    tk.Label(detail_frame, text="Mensaje:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
    mensaje_text = scrolledtext.ScrolledText(detail_frame, width=40, height=6, state="disabled")
    mensaje_text.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
    
    tk.Label(detail_frame, text="Respuesta:").grid(row=4, column=0, sticky="nw", padx=5, pady=5)
    respuesta_text = scrolledtext.ScrolledText(detail_frame, width=40, height=4)
    respuesta_text.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
    
    # Botones
    btn_frame = ttk.Frame(detail_frame)
    btn_frame.grid(row=5, column=1, sticky="e", pady=10)
    
    btn_responder = tk.Button(btn_frame, text="Responder", bg="#3498db", fg="white")
    btn_eliminar = tk.Button(btn_frame, text="Eliminar", bg="#e74c3c", fg="white")
    
    btn_responder.pack(side="left", padx=5)
    btn_eliminar.pack(side="left", padx=5)
    
    # Configurar el grid para que se expanda correctamente
    detail_frame.columnconfigure(1, weight=1)
    detail_frame.rowconfigure(3, weight=1)
    detail_frame.rowconfigure(4, weight=1)
    
    # Variable para almacenar el mensaje seleccionado
    mensaje_actual = None
    
    # Diccionario para mapear IDs de items del treeview a IDs de MongoDB
    id_mapping = {}
    
    def cargar_mensajes():
        # Limpiar treeview y mapping
        for item in tree.get_children():
            tree.delete(item)
        id_mapping.clear()
        
        # Construir query según el filtro seleccionado
        filtro = filtro_estado.get()
        
        # Obtener todos los mensajes primero
        todos_los_mensajes = list(mensajes_col.find().sort("fecha", -1))
        
        # Filtrar manualmente según la selección
        mensajes_filtrados = []
        for msg in todos_los_mensajes:
            tiene_respuesta = "respuesta" in msg and msg["respuesta"]
            
            if filtro == "todos":
                mensajes_filtrados.append(msg)
            elif filtro == "no_leido":
                if msg.get("estado") == "no_leido" and not tiene_respuesta:
                    mensajes_filtrados.append(msg)
            elif filtro == "leido":
                if msg.get("estado") == "leido" and not tiene_respuesta:
                    mensajes_filtrados.append(msg)
            elif filtro == "respondido":
                if tiene_respuesta:
                    mensajes_filtrados.append(msg)
            elif filtro == "no_respondido":
                if not tiene_respuesta:
                    mensajes_filtrados.append(msg)
        
        # Insertar mensajes en el treeview
        for msg in mensajes_filtrados:
            # Determinar el estado a mostrar
            if "respuesta" in msg and msg["respuesta"]:
                estado = "✓ Respondido"
            elif msg.get("estado") == "leido":
                estado = "✓ Leído"
            else:
                estado = "✗ No leído"
                
            # Insertar item en el treeview
            item_id = tree.insert("", "end", 
                       values=(
                           msg["cliente_nombre"],
                           msg["asunto"],
                           msg["fecha"],
                           estado
                       ))
            # Guardar el mapeo entre el ID del item y el ID de MongoDB
            id_mapping[item_id] = str(msg["_id"])
    
    def mostrar_detalles(event):
        nonlocal mensaje_actual
        selection = tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        # Obtener el ID de MongoDB desde el mapeo
        mongo_id_str = id_mapping.get(item_id)
        
        if not mongo_id_str:
            return
        
        # Convertir el string a ObjectId para buscar en la base de datos
        try:
            mensaje_actual = mensajes_col.find_one({"_id": ObjectId(mongo_id_str)})
        except:
            messagebox.showerror("Error", "ID de mensaje inválido")
            return
        
        if mensaje_actual:
            # Mostrar detalles del mensaje
            cliente_var.set(mensaje_actual["cliente_nombre"])
            fecha_var.set(mensaje_actual["fecha"])
            asunto_var.set(mensaje_actual["asunto"])
            
            # Mostrar mensaje
            mensaje_text.config(state="normal")
            mensaje_text.delete("1.0", tk.END)
            mensaje_text.insert("1.0", mensaje_actual["mensaje"])
            mensaje_text.config(state="disabled")
            
            # Mostrar respuesta si existe
            respuesta_text.delete("1.0", tk.END)
            if "respuesta" in mensaje_actual and mensaje_actual["respuesta"]:
                respuesta_text.insert("1.0", mensaje_actual["respuesta"])
            
            # Marcar como leído si no lo está y no tiene respuesta
            if (mensaje_actual.get("estado") == "no_leido" and 
                not mensaje_actual.get("respuesta")):
                try:
                    mensajes_col.update_one(
                        {"_id": ObjectId(mongo_id_str)}, 
                        {"$set": {"estado": "leido"}}
                    )
                    cargar_mensajes()  # Recargar para actualizar estado
                except:
                    messagebox.showerror("Error", "No se pudo actualizar el estado del mensaje")
    
    def responder_mensaje():
        if not mensaje_actual:
            messagebox.showerror("Error", "Seleccione un mensaje primero")
            return
        
        respuesta = respuesta_text.get("1.0", tk.END).strip()
        if not respuesta:
            messagebox.showerror("Error", "Escriba una respuesta")
            return
        
        try:
            # Actualizar mensaje con la respuesta
            mensajes_col.update_one(
                {"_id": mensaje_actual["_id"]},
                {"$set": {
                    "respuesta": respuesta,
                    "respondido_por": "Administrador",
                    "fecha_respuesta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "estado": "leido"
                }}
            )
            messagebox.showinfo("Éxito", "Respuesta enviada correctamente")
            cargar_mensajes()  # Recargar mensajes
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar la respuesta: {str(e)}")
    
    def eliminar_mensaje():
        if not mensaje_actual:
            messagebox.showerror("Error", "Seleccione un mensaje primero")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este mensaje?"):
            try:
                mensajes_col.delete_one({"_id": mensaje_actual["_id"]})
                messagebox.showinfo("Éxito", "Mensaje eliminado")
                
                # Limpiar detalles
                cliente_var.set("")
                fecha_var.set("")
                asunto_var.set("")
                mensaje_text.config(state="normal")
                mensaje_text.delete("1.0", tk.END)
                mensaje_text.config(state="disabled")
                respuesta_text.delete("1.0", tk.END)
                
                # Recargar mensajes
                cargar_mensajes()
                
                # Limpiar mensaje actual
                mensaje_actual = None
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el mensaje: {str(e)}")
    
    # Configurar eventos y botones
    tree.bind("<<TreeviewSelect>>", mostrar_detalles)
    btn_responder.config(command=responder_mensaje)
    btn_eliminar.config(command=eliminar_mensaje)
    
    # Cargar mensajes inicialmente
    cargar_mensajes()
    
    return frame