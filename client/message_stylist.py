import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.config import mensajes_col

def crear_panel_mensajes(parent, user):
    frame = ttk.Frame(parent)
    
    # Título
    title_label = tk.Label(frame, text="Contactar con el Estilista/Administrador", 
                          font=("Helvetica", 16, "bold"))
    title_label.pack(pady=10)
    
    # Formulario para enviar mensaje
    form_frame = ttk.LabelFrame(frame, text="Nuevo Mensaje")
    form_frame.pack(fill="x", padx=10, pady=5)
    
    # Asunto
    tk.Label(form_frame, text="Asunto:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    asunto_var = tk.StringVar()
    asunto_entry = ttk.Entry(form_frame, textvariable=asunto_var, width=50)
    asunto_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    # Mensaje
    tk.Label(form_frame, text="Mensaje:").grid(row=1, column=0, sticky="nw", padx=5, pady=5)
    mensaje_text = tk.Text(form_frame, width=50, height=8)
    mensaje_text.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    
    # Configurar grid weights
    form_frame.columnconfigure(1, weight=1)
    
    def enviar_mensaje():
        asunto = asunto_var.get().strip()
        mensaje = mensaje_text.get("1.0", tk.END).strip()
        
        if not asunto or not mensaje:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        # Crear mensaje
        nuevo_mensaje = {
            "cliente_id": user["_id"],
            "cliente_nombre": user["nombre"],
            "asunto": asunto,
            "mensaje": mensaje,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "no_leido",
            "respuesta": "",
            "respondido_por": "",
            "fecha_respuesta": None
        }
        
        try:
            mensajes_col.insert_one(nuevo_mensaje)
            messagebox.showinfo("Éxito", "Mensaje enviado correctamente")
            asunto_var.set("")
            mensaje_text.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar el mensaje: {str(e)}")
    
    # Botón enviar
    btn_enviar = tk.Button(form_frame, text="Enviar Mensaje", command=enviar_mensaje,
                          bg="#2ecc71", fg="white", font=("Helvetica", 10))
    btn_enviar.grid(row=2, column=1, sticky="e", padx=5, pady=10)
    
    # Sección para ver respuestas
    respuestas_frame = ttk.LabelFrame(frame, text="Ver Respuestas")
    respuestas_frame.pack(fill="x", padx=10, pady=10)
    
    # Botón para ver respuestas
    def ver_respuestas():
        try:
            # Buscar mensajes con respuestas
            mensajes_con_respuesta = mensajes_col.find({
                "cliente_id": user["_id"],
                "respuesta": {"$ne": ""}
            }).sort("fecha", -1)
            
            mensajes_con_respuesta = list(mensajes_con_respuesta)
            
            if not mensajes_con_respuesta:
                messagebox.showinfo("Respuestas", "No tienes respuestas aún")
                return
            
            # Crear ventana emergente para mostrar respuestas
            ventana_respuestas = tk.Toplevel(frame)
            ventana_respuestas.title("Tus Respuestas")
            ventana_respuestas.geometry("600x500")
            ventana_respuestas.configure(bg='white')
            
            # Título
            titulo = tk.Label(ventana_respuestas, 
                             text="Respuestas a tus mensajes", 
                             font=("Helvetica", 14, "bold"),
                             bg='white')
            titulo.pack(pady=10)
            
            # Frame para contener los mensajes
            contenedor = ttk.Frame(ventana_respuestas)
            contenedor.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Canvas y scrollbar para scroll
            canvas = tk.Canvas(contenedor, bg='white')
            scrollbar = ttk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Mostrar cada mensaje con su respuesta
            for i, mensaje in enumerate(mensajes_con_respuesta):
                # Frame para cada mensaje-respuesta
                msg_frame = ttk.LabelFrame(scrollable_frame, text=f"Mensaje del {mensaje.get('fecha', '')}")
                msg_frame.pack(fill="x", pady=5, padx=5)
                
                # Asunto
                asunto_label = tk.Label(msg_frame, text=f"Asunto: {mensaje.get('asunto', '')}",
                                       font=("Helvetica", 10, "bold"), wraplength=550, justify="left")
                asunto_label.pack(anchor="w", padx=5, pady=2)
                
                # Tu mensaje
                tk.Label(msg_frame, text="Tu mensaje:", font=("Helvetica", 9, "bold")).pack(anchor="w", padx=5)
                mensaje_texto = tk.Text(msg_frame, height=3, width=60, wrap="word")
                mensaje_texto.insert("1.0", mensaje.get('mensaje', ''))
                mensaje_texto.config(state="disabled")
                mensaje_texto.pack(fill="x", padx=5, pady=2)
                
                # Respuesta
                tk.Label(msg_frame, text="Respuesta:", font=("Helvetica", 9, "bold"), fg="green").pack(anchor="w", padx=5)
                respuesta_frame = ttk.Frame(msg_frame)
                respuesta_frame.pack(fill="x", padx=5, pady=2)
                
                respuesta_texto = tk.Text(respuesta_frame, height=3, width=60, wrap="word", bg="#f0f8ff")
                respuesta_texto.insert("1.0", mensaje.get('respuesta', ''))
                respuesta_texto.config(state="disabled")
                respuesta_texto.pack(side="left", fill="x", expand=True)
                
                # Información de la respuesta
                info_frame = ttk.Frame(msg_frame)
                info_frame.pack(fill="x", padx=5, pady=2)
                
                if mensaje.get('respondido_por'):
                    tk.Label(info_frame, 
                            text=f"Respondido por: {mensaje.get('respondido_por')} - {mensaje.get('fecha_respuesta', '')}",
                            font=("Helvetica", 8), fg="gray").pack(anchor="w")
            
            # Configurar canvas y scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Configurar scroll con mouse
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            # Botón para cerrar
            btn_cerrar = tk.Button(ventana_respuestas, text="Cerrar", 
                                  command=ventana_respuestas.destroy,
                                  bg="#e74c3c", fg="white", font=("Helvetica", 10))
            btn_cerrar.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las respuestas: {str(e)}")
    
    # Botón para ver respuestas
    btn_ver_respuestas = tk.Button(respuestas_frame, text="Ver Respuestas Recibidas", 
                                  command=ver_respuestas,
                                  bg="#3498db", fg="white", font=("Helvetica", 12),
                                  width=20, height=2)
    btn_ver_respuestas.pack(pady=15)
    
    # Información adicional
    info_label = tk.Label(respuestas_frame, 
                         text="Haz clic en el botón para ver las respuestas a tus mensajes anteriores",
                         font=("Helvetica", 9), fg="gray")
    info_label.pack(pady=5)
    
    return frame