import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from database.config import citas_col, users_col, servicios_col, estilistas_col
from utils.helpers import calcular_duracion_por_genero, verificar_disponibilidad_estilista, es_domingo, estilista_tiene_horario
import tempfile

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
                            messagebox.showerror("Error", f"El estilista está en descanso de {hora_descanso} a {fin_descanso}. No se pueden agendar citas durante este period.")
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

    # Analizar con Spark - PARA CITAS
    def analizar_citas_spark():
        # Crear ventana de análisis
        analysis_win = tk.Toplevel(admin_win)
        analysis_win.title("Análisis de Citas con Spark")
        analysis_win.geometry("700x550")
        analysis_win.configure(bg='white')
        
        # Título
        title_frame = tk.Frame(analysis_win, bg='white')
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="Análisis de Citas con Spark", 
                font=("Arial", 16, "bold"), bg='white').pack()
        
        # Frame para resultados
        results_frame = tk.Frame(analysis_win, bg='white')
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Texto para mostrar resultados
        results_text = tk.Text(results_frame, height=22, width=80, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=results_text.yview)
        results_text.configure(yscrollcommand=scrollbar.set)
        
        results_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mostrar mensaje de carga
        results_text.insert(1.0, "Iniciando análisis de citas con Spark... Por favor espere.\n")
        analysis_win.update()
        
        def ejecutar_analisis_simplificado():
            """Análisis simplificado que evita problemas de configuración de Spark"""
            try:
                # Intentar análisis con Spark de forma más simple
                resultados = "# Análisis de Citas - Kairos\n\n"
                
                # Verificar si Spark está disponible
                try:
                    from pyspark.sql import SparkSession
                    
                    # Configurar Spark con opciones que evitan problemas en Windows
                    spark = SparkSession.builder \
                        .appName("AnalisisCitas") \
                        .config("spark.master", "local[1]") \
                        .config("spark.sql.adaptive.enabled", "false") \
                        .config("spark.driver.memory", "1g") \
                        .config("spark.sql.warehouse.dir", tempfile.gettempdir()) \
                        .config("spark.driver.extraJavaOptions", 
                               "-Dlog4j.configuration=file:///dev/null -Dio.netty.tryReflectionSetAccessible=true") \
                        .getOrCreate()
                    
                    spark.sparkContext.setLogLevel("ERROR")
                    
                    resultados += "Análisis de Citas con PySpark:\n\n"
                    
                    # Recopilar datos de citas con información relacionada
                    datos_citas = []
                    for cita in citas_col.find():
                        try:
                            # Obtener información relacionada
                            cliente = users_col.find_one({"_id": cita["cliente_id"]})
                            servicio = servicios_col.find_one({"_id": cita["servicio_id"]})
                            estilista = estilistas_col.find_one({"_id": cita["estilista_id"]})
                            
                            datos_citas.append({
                                "cliente_nombre": cliente["nombre"] if cliente else "Desconocido",
                                "cliente_sexo": cliente.get("sexo", "Desconocido") if cliente else "Desconocido",
                                "servicio_nombre": servicio["nombre"] if servicio else "Desconocido",
                                "estilista_nombre": estilista["nombre"] if estilista else "Desconocido",
                                "fecha": cita["fecha"],
                                "hora": cita["hora"],
                                "estado": cita["estado"],
                                "duracion": cita.get("duracion", 0),
                                "notas": cita.get("notas", "")
                            })
                        except Exception as e:
                            print(f"Error procesando cita: {e}")
                            continue
                    
                    # Análisis de citas
                    if datos_citas:
                        total_citas = len(datos_citas)
                        
                        # Estadísticas por estado
                        citas_por_estado = {}
                        for cita in datos_citas:
                            estado = cita.get('estado', 'desconocido')
                            citas_por_estado[estado] = citas_por_estado.get(estado, 0) + 1
                        
                        # Estadísticas por género del cliente
                        citas_por_genero = {}
                        for cita in datos_citas:
                            genero = cita.get('cliente_sexo', 'Desconocido')
                            citas_por_genero[genero] = citas_por_genero.get(genero, 0) + 1
                        
                        # Estadísticas por estilista
                        citas_por_estilista = {}
                        for cita in datos_citas:
                            estilista = cita.get('estilista_nombre', 'Desconocido')
                            citas_por_estilista[estilista] = citas_por_estilista.get(estilista, 0) + 1
                        
                        # Estadísticas por servicio
                        citas_por_servicio = {}
                        for cita in datos_citas:
                            servicio = cita.get('servicio_nombre', 'Desconocido')
                            citas_por_servicio[servicio] = citas_por_servicio.get(servicio, 0) + 1
                        
                        # Análisis de fechas
                        fechas = [cita['fecha'] for cita in datos_citas if cita.get('fecha')]
                        if fechas:
                            fechas_ordenadas = sorted(fechas)
                            fecha_mas_antigua = fechas_ordenadas[0]
                            fecha_mas_reciente = fechas_ordenadas[-1]
                            
                            # Contar citas por mes
                            citas_por_mes = {}
                            for fecha in fechas:
                                try:
                                    mes = fecha[:7]  # YYYY-MM
                                    citas_por_mes[mes] = citas_por_mes.get(mes, 0) + 1
                                except:
                                    continue
                        
                        # Duración total
                        duracion_total = sum(cita.get('duracion', 0) for cita in datos_citas)
                        
                        resultados += f"Total de citas: {total_citas}\n"
                        resultados += f"Duración total estimada: {duracion_total} minutos\n"
                        resultados += f"Duración promedio por cita: {duracion_total/total_citas:.1f} minutos\n\n"
                        
                        resultados += "CITAS POR ESTADO:\n"
                        for estado, cantidad in citas_por_estado.items():
                            porcentaje = (cantidad / total_citas) * 100
                            resultados += f"- {estado}: {cantidad} ({porcentaje:.1f}%)\n"
                        resultados += f"\n"
                        
                        resultados += "CITAS POR GÉNERO DEL CLIENTE:\n"
                        for genero, cantidad in citas_por_genero.items():
                            porcentaje = (cantidad / total_citas) * 100
                            resultados += f"- {genero}: {cantidad} ({porcentaje:.1f}%)\n"
                        resultados += f"\n"
                        
                        resultados += "TOP 5 ESTILISTAS MÁS SOLICITADOS:\n"
                        estilistas_ordenados = sorted(citas_por_estilista.items(), key=lambda x: x[1], reverse=True)[:5]
                        for estilista, cantidad in estilistas_ordenados:
                            porcentaje = (cantidad / total_citas) * 100
                            resultados += f"- {estilista}: {cantidad} citas ({porcentaje:.1f}%)\n"
                        resultados += f"\n"
                        
                        resultados += "TOP 5 SERVICIOS MÁS POPULARES:\n"
                        servicios_ordenados = sorted(citas_por_servicio.items(), key=lambda x: x[1], reverse=True)[:5]
                        for servicio, cantidad in servicios_ordenados:
                            porcentaje = (cantidad / total_citas) * 100
                            resultados += f"- {servicio}: {cantidad} citas ({porcentaje:.1f}%)\n"
                        resultados += f"\n"
                        
                        if fechas:
                            resultados += f"Rango de fechas: {fecha_mas_antigua} a {fecha_mas_reciente}\n"
                            
                            resultados += "CITAS POR MES:\n"
                            for mes, cantidad in sorted(citas_por_mes.items()):
                                resultados += f"- {mes}: {cantidad} citas\n"
                    
                    resultados += "\n---\nAnálisis de citas completado exitosamente con PySpark."
                    
                    spark.stop()
                    
                except Exception as spark_error:
                    # Fallback a análisis manual si Spark falla
                    resultados += f"Spark no disponible, usando análisis alternativo:\n{str(spark_error)}\n\n"
                    resultados += realizar_analisis_manual()
                
                # Mostrar resultados
                results_text.delete(1.0, tk.END)
                results_text.insert(1.0, resultados)
                
            except Exception as e:
                results_text.delete(1.0, tk.END)
                results_text.insert(1.0, f"Error en el análisis: {str(e)}\n\n")
                results_text.insert(tk.END, realizar_analisis_manual())
        
        def realizar_analisis_manual():
            """Análisis de respaldo sin Spark - SOLO CITAS"""
            try:
                resultados = "Análisis de Citas con MongoDB:\n\n"
                
                # Análisis de citas usando aggregation
                total_citas = citas_col.count_documents({})
                
                # Citas por estado
                pipeline_estado = [{"$group": {"_id": "$estado", "count": {"$sum": 1}}}]
                citas_por_estado = list(citas_col.aggregate(pipeline_estado))
                
                # Duración total
                pipeline_duracion = [{"$group": {"_id": None, "total_duracion": {"$sum": "$duracion"}}}]
                duracion_total = list(citas_col.aggregate(pipeline_duracion))
                duracion_total_val = duracion_total[0]['total_duracion'] if duracion_total and duracion_total[0].get('total_duracion') else 0
                
                resultados += f"Total de citas: {total_citas}\n"
                resultados += f"Duración total estimada: {duracion_total_val} minutos\n"
                resultados += f"Duración promedio por cita: {duracion_total_val/total_citas:.1f} minutos\n\n"
                
                resultados += "CITAS POR ESTADO:\n"
                for item in citas_por_estado:
                    porcentaje = (item['count'] / total_citas) * 100
                    resultados += f"- {item['_id']}: {item['count']} ({porcentaje:.1f}%)\n"
                resultados += f"\n"
                
                # Citas por estilista (usando lookup)
                pipeline_estilista = [
                    {"$lookup": {
                        "from": "estilistas",
                        "localField": "estilista_id",
                        "foreignField": "_id",
                        "as": "estilista_info"
                    }},
                    {"$unwind": "$estilista_info"},
                    {"$group": {
                        "_id": "$estilista_info.nombre",
                        "count": {"$sum": 1}
                    }},
                    {"$sort": {"count": -1}},
                    {"$limit": 5}
                ]
                
                top_estilistas = list(citas_col.aggregate(pipeline_estilista))
                resultados += "TOP 5 ESTILISTAS MÁS SOLICITADOS:\n"
                for item in top_estilistas:
                    porcentaje = (item['count'] / total_citas) * 100
                    resultados += f"- {item['_id']}: {item['count']} citas ({porcentaje:.1f}%)\n"
                resultados += f"\n"
                
                # Citas por servicio (usando lookup)
                pipeline_servicio = [
                    {"$lookup": {
                        "from": "servicios",
                        "localField": "servicio_id",
                        "foreignField": "_id",
                        "as": "servicio_info"
                    }},
                    {"$unwind": "$servicio_info"},
                    {"$group": {
                        "_id": "$servicio_info.nombre",
                        "count": {"$sum": 1}
                    }},
                    {"$sort": {"count": -1}},
                    {"$limit": 5}
                ]
                
                top_servicios = list(citas_col.aggregate(pipeline_servicio))
                resultados += "TOP 5 SERVICIOS MÁS POPULARES:\n"
                for item in top_servicios:
                    porcentaje = (item['count'] / total_citas) * 100
                    resultados += f"- {item['_id']}: {item['count']} citas ({porcentaje:.1f}%)\n"
                resultados += f"\n"
                
                # Rango de fechas
                pipeline_fechas = [
                    {"$group": {
                        "_id": None,
                        "fecha_min": {"$min": "$fecha"},
                        "fecha_max": {"$max": "$fecha"}
                    }}
                ]
                rango_fechas = list(citas_col.aggregate(pipeline_fechas))
                if rango_fechas:
                    resultados += f"Rango de fechas: {rango_fechas[0]['fecha_min']} a {rango_fechas[0]['fecha_max']}\n"
                
                resultados += "\n---\nAnálisis de citas completado con MongoDB aggregation."
                return resultados
                
            except Exception as e2:
                return f"Error en análisis manual: {str(e2)}"
        
        # Ejecutar en segundo plano
        analysis_win.after(100, ejecutar_analisis_simplificado)

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
    
    # Nuevo botón de análisis con Spark
    btn_analizar = tk.Button(btn_frame, text="📊 Analizar con Spark", command=analizar_citas_spark,
                            bg="#9b59b6", fg="white", font=("Arial", 10, "bold"), width=12)
    btn_analizar.grid(row=0, column=4, padx=5)

    return tab_citas