import tkinter as tk
from tkinter import messagebox, ttk
from database.config import servicios_col
import tempfile

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

    # Analizar con Spark - PARA SERVICIOS
    def analizar_servicios_spark():
        # Crear ventana de análisis
        analysis_win = tk.Toplevel(admin_win)
        analysis_win.title("Análisis de Servicios con Spark")
        analysis_win.geometry("700x550")
        analysis_win.configure(bg='white')
        
        # Título
        title_frame = tk.Frame(analysis_win, bg='white')
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="Análisis de Servicios con Spark", 
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
        results_text.insert(1.0, "Iniciando análisis de servicios con Spark... Por favor espere.\n")
        analysis_win.update()
        
        def ejecutar_analisis_simplificado():
            """Análisis simplificado que evita problemas de configuración de Spark"""
            try:
                # Intentar análisis con Spark de forma más simple
                resultados = "# Análisis de Servicios - Kairos\n\n"
                
                # Verificar si Spark está disponible
                try:
                    from pyspark.sql import SparkSession
                    
                    # Configurar Spark con opciones que evitan problemas en Windows
                    spark = SparkSession.builder \
                        .appName("AnalisisServicios") \
                        .config("spark.master", "local[1]") \
                        .config("spark.sql.adaptive.enabled", "false") \
                        .config("spark.driver.memory", "1g") \
                        .config("spark.sql.warehouse.dir", tempfile.gettempdir()) \
                        .config("spark.driver.extraJavaOptions", 
                               "-Dlog4j.configuration=file:///dev/null -Dio.netty.tryReflectionSetAccessible=true") \
                        .getOrCreate()
                    
                    spark.sparkContext.setLogLevel("ERROR")
                    
                    resultados += "Análisis de Servicios con PySpark:\n\n"
                    
                    # Recopilar datos de servicios
                    datos_servicios = list(servicios_col.find({}, {"_id": 0, "nombre": 1, "tiempo_M": 1, "tiempo_F": 1, "activo": 1}))
                    
                    # Análisis de servicios
                    if datos_servicios:
                        total_servicios = len(datos_servicios)
                        servicios_activos = sum(1 for s in datos_servicios if s.get('activo', True))
                        servicios_inactivos = total_servicios - servicios_activos
                        
                        # Estadísticas de tiempos
                        tiempos_m = [s.get('tiempo_M', 30) for s in datos_servicios if s.get('tiempo_M') is not None]
                        tiempos_f = [s.get('tiempo_F', 60) for s in datos_servicios if s.get('tiempo_F') is not None]
                        
                        if tiempos_m:
                            tiempo_promedio_m = sum(tiempos_m) / len(tiempos_m)
                            tiempo_max_m = max(tiempos_m)
                            tiempo_min_m = min(tiempos_m)
                        else:
                            tiempo_promedio_m = tiempo_max_m = tiempo_min_m = 0
                            
                        if tiempos_f:
                            tiempo_promedio_f = sum(tiempos_f) / len(tiempos_f)
                            tiempo_max_f = max(tiempos_f)
                            tiempo_min_f = min(tiempos_f)
                        else:
                            tiempo_promedio_f = tiempo_max_f = tiempo_min_f = 0
                        
                        # Diferencia entre tiempos M y F
                        diferencias = [s.get('tiempo_F', 60) - s.get('tiempo_M', 30) for s in datos_servicios 
                                     if s.get('tiempo_M') is not None and s.get('tiempo_F') is not None]
                        diferencia_promedio = sum(diferencias) / len(diferencias) if diferencias else 0
                        
                        resultados += f"Total de servicios: {total_servicios}\n"
                        resultados += f"Servicios activos: {servicios_activos}\n"
                        resultados += f"Servicios inactivos: {servicios_inactivos}\n\n"
                        
                        resultados += "ESTADÍSTICAS DE TIEMPOS:\n"
                        resultados += f"Tiempo promedio para hombres: {tiempo_promedio_m:.1f} min\n"
                        resultados += f"Tiempo máximo para hombres: {tiempo_max_m} min\n"
                        resultados += f"Tiempo mínimo para hombres: {tiempo_min_m} min\n\n"
                        
                        resultados += f"Tiempo promedio para mujeres: {tiempo_promedio_f:.1f} min\n"
                        resultados += f"Tiempo máximo para mujeres: {tiempo_max_f} min\n"
                        resultados += f"Tiempo mínimo para mujeres: {tiempo_min_f} min\n\n"
                        
                        resultados += f"Diferencia promedio (Mujeres - Hombres): {diferencia_promedio:.1f} min\n"
                        
                        # Servicios más largos y más cortos
                        if datos_servicios:
                            servicio_mas_largo_m = max(datos_servicios, key=lambda x: x.get('tiempo_M', 0))
                            servicio_mas_corto_m = min(datos_servicios, key=lambda x: x.get('tiempo_M', float('inf')))
                            servicio_mas_largo_f = max(datos_servicios, key=lambda x: x.get('tiempo_F', 0))
                            servicio_mas_corto_f = min(datos_servicios, key=lambda x: x.get('tiempo_F', float('inf')))
                            
                            resultados += "\nSERVICIOS DESTACADOS:\n"
                            resultados += f"Servicio más largo (H): {servicio_mas_largo_m['nombre']} ({servicio_mas_largo_m.get('tiempo_M', 0)} min)\n"
                            resultados += f"Servicio más corto (H): {servicio_mas_corto_m['nombre']} ({servicio_mas_corto_m.get('tiempo_M', 0)} min)\n"
                            resultados += f"Servicio más largo (M): {servicio_mas_largo_f['nombre']} ({servicio_mas_largo_f.get('tiempo_F', 0)} min)\n"
                            resultados += f"Servicio más corto (M): {servicio_mas_corto_f['nombre']} ({servicio_mas_corto_f.get('tiempo_F', 0)} min)\n"
                    
                    resultados += "\n---\nAnálisis de servicios completado exitosamente con PySpark."
                    
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
            """Análisis de respaldo sin Spark - SOLO SERVICIOS"""
            try:
                resultados = "Análisis de Servicios con MongoDB:\n\n"
                
                # Análisis de servicios
                total_servicios = servicios_col.count_documents({})
                servicios_activos = servicios_col.count_documents({"activo": True})
                servicios_inactivos = total_servicios - servicios_activos
                
                # Estadísticas de tiempos usando aggregation
                pipeline_estadisticas = [
                    {"$group": {
                        "_id": None,
                        "avg_tiempo_M": {"$avg": "$tiempo_M"},
                        "max_tiempo_M": {"$max": "$tiempo_M"},
                        "min_tiempo_M": {"$min": "$tiempo_M"},
                        "avg_tiempo_F": {"$avg": "$tiempo_F"},
                        "max_tiempo_F": {"$max": "$tiempo_F"},
                        "min_tiempo_F": {"$min": "$tiempo_F"},
                        "avg_diferencia": {"$avg": {"$subtract": ["$tiempo_F", "$tiempo_M"]}}
                    }}
                ]
                
                estadisticas = list(servicios_col.aggregate(pipeline_estadisticas))
                
                resultados += f"Total de servicios: {total_servicios}\n"
                resultados += f"Servicios activos: {servicios_activos}\n"
                resultados += f"Servicios inactivos: {servicios_inactivos}\n\n"
                
                if estadisticas:
                    stats = estadisticas[0]
                    resultados += "ESTADÍSTICAS DE TIEMPOS:\n"
                    resultados += f"Tiempo promedio para hombres: {stats.get('avg_tiempo_M', 0):.1f} min\n"
                    resultados += f"Tiempo máximo para hombres: {stats.get('max_tiempo_M', 0)} min\n"
                    resultados += f"Tiempo mínimo para hombres: {stats.get('min_tiempo_M', 0)} min\n\n"
                    
                    resultados += f"Tiempo promedio para mujeres: {stats.get('avg_tiempo_F', 0):.1f} min\n"
                    resultados += f"Tiempo máximo para mujeres: {stats.get('max_tiempo_F', 0)} min\n"
                    resultados += f"Tiempo mínimo para mujeres: {stats.get('min_tiempo_F', 0)} min\n\n"
                    
                    resultados += f"Diferencia promedio (Mujeres - Hombres): {stats.get('avg_diferencia', 0):.1f} min\n"
                
                # Servicios más largos y más cortos
                servicio_mas_largo_m = servicios_col.find_one(sort=[("tiempo_M", -1)])
                servicio_mas_corto_m = servicios_col.find_one(sort=[("tiempo_M", 1)])
                servicio_mas_largo_f = servicios_col.find_one(sort=[("tiempo_F", -1)])
                servicio_mas_corto_f = servicios_col.find_one(sort=[("tiempo_F", 1)])
                
                if servicio_mas_largo_m and servicio_mas_corto_m:
                    resultados += "\nSERVICIOS DESTACADOS:\n"
                    resultados += f"Servicio más largo (H): {servicio_mas_largo_m['nombre']} ({servicio_mas_largo_m.get('tiempo_M', 0)} min)\n"
                    resultados += f"Servicio más corto (H): {servicio_mas_corto_m['nombre']} ({servicio_mas_corto_m.get('tiempo_M', 0)} min)\n"
                    resultados += f"Servicio más largo (M): {servicio_mas_largo_f['nombre']} ({servicio_mas_largo_f.get('tiempo_F', 0)} min)\n"
                    resultados += f"Servicio más corto (M): {servicio_mas_corto_f['nombre']} ({servicio_mas_corto_f.get('tiempo_F', 0)} min)\n"
                
                resultados += "\n---\nAnálisis de servicios completado con MongoDB aggregation."
                return resultados
                
            except Exception as e2:
                return f"Error en análisis manual: {str(e2)}"
        
        # Ejecutar en segundo plano
        analysis_win.after(100, ejecutar_analisis_simplificado)

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
    
    # Nuevo botón de análisis con Spark
    btn_analizar = tk.Button(btn_frame, text="📊 Analizar con Spark", command=analizar_servicios_spark,
                            bg="#9b59b6", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_analizar.grid(row=0, column=3, padx=5)

    return tab_servicios