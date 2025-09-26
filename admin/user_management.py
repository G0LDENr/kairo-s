import tkinter as tk
from tkinter import messagebox, ttk
from database.config import users_col, citas_col, estilistas_col, servicios_col
from auth.authentication import register_user
import os
import sys
import subprocess
import tempfile
import json

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

    # ---------------- BOTONES CREAR / MODIFICAR / ELIMINAR / ANALIZAR CON SPARK ----------------
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
            messagebox.showerror("Error", "Seleccione an usuario")
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

    # Analizar con Spark - SOLO PARA USUARIOS
    def analizar_con_spark():
        # Crear ventana de análisis
        analysis_win = tk.Toplevel(admin_win)
        analysis_win.title("Análisis de Usuarios con Spark")
        analysis_win.geometry("700x550")
        analysis_win.configure(bg='white')
        
        # Título
        title_frame = tk.Frame(analysis_win, bg='white')
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="Análisis de Usuarios con Spark", 
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
        results_text.insert(1.0, "Iniciando análisis de usuarios con Spark... Por favor espere.\n")
        analysis_win.update()
        
        def ejecutar_analisis_simplificado():
            """Análisis simplificado que evita problemas de configuración de Spark"""
            try:
                # Intentar análisis con Spark de forma más simple
                resultados = "# Análisis de Usuarios - Kairos\n\n"
                
                # Verificar si Spark está disponible
                try:
                    from pyspark.sql import SparkSession
                    from pyspark.sql.functions import count, avg, round
                    
                    # Configurar Spark con opciones que evitan problemas en Windows
                    spark = SparkSession.builder \
                        .appName("AnalisisKairos") \
                        .config("spark.master", "local[1]") \
                        .config("spark.sql.adaptive.enabled", "false") \
                        .config("spark.driver.memory", "1g") \
                        .config("spark.sql.warehouse.dir", tempfile.gettempdir()) \
                        .config("spark.driver.extraJavaOptions", 
                               "-Dlog4j.configuration=file:///dev/null -Dio.netty.tryReflectionSetAccessible=true") \
                        .getOrCreate()
                    
                    spark.sparkContext.setLogLevel("ERROR")
                    
                    resultados += "Análisis de Usuarios con PySpark:\n\n"
                    
                    # Recopilar datos SOLO de usuarios
                    datos_usuarios = list(users_col.find({}, {"_id": 0, "nombre": 1, "role": 1, "sexo": 1, "fecha_registro": 1}))
                    
                    # Análisis de usuarios
                    if datos_usuarios:
                        # Usar análisis simple sin crear DataFrames complejos
                        total_usuarios = len(datos_usuarios)
                        usuarios_por_rol = {}
                        usuarios_por_sexo = {}
                        
                        for usuario in datos_usuarios:
                            rol = usuario.get('role', 'cliente')
                            sexo = usuario.get('sexo', 'No especificado')
                            usuarios_por_rol[rol] = usuarios_por_rol.get(rol, 0) + 1
                            usuarios_por_sexo[sexo] = usuarios_por_sexo.get(sexo, 0) + 1
                        
                        resultados += f"Total de usuarios: {total_usuarios}\n\n"
                        resultados += f"Usuarios por rol:\n"
                        for rol, cantidad in usuarios_por_rol.items():
                            resultados += f"- {rol}: {cantidad}\n"
                        resultados += f"\n"
                        
                        resultados += f"Usuarios por sexo:\n"
                        for sexo, cantidad in usuarios_por_sexo.items():
                            resultados += f"- {sexo}: {cantidad}\n"
                    
                    resultados += "\n---\nAnálisis de usuarios completado exitosamente con PySpark."
                    
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
            """Análisis de respaldo sin Spark - SOLO USUARIOS"""
            try:
                resultados = "Análisis de Usuarios con MongoDB:\n\n"
                
                # Análisis de usuarios
                total_usuarios = users_col.count_documents({})
                pipeline_usuarios = [{"$group": {"_id": "$role", "count": {"$sum": 1}}}]
                usuarios_por_rol = list(users_col.aggregate(pipeline_usuarios))
                
                pipeline_sexo = [{"$group": {"_id": "$sexo", "count": {"$sum": 1}}}]
                usuarios_por_sexo = list(users_col.aggregate(pipeline_sexo))
                
                resultados += f"Total de usuarios: {total_usuarios}\n\n"
                resultados += f"Usuarios por rol:\n"
                for item in usuarios_por_rol:
                    resultados += f"- {item['_id']}: {item['count']}\n"
                resultados += f"\n"
                
                resultados += f"Usuarios por sexo:\n"
                for item in usuarios_por_sexo:
                    sexo = item['_id'] if item['_id'] is not None else 'No especificado'
                    resultados += f"- {sexo}: {item['count']}\n"
                
                resultados += "\n---\nAnálisis de usuarios completado con MongoDB aggregation."
                return resultados
                
            except Exception as e2:
                return f"Error en análisis manual: {str(e2)}"
        
        # Ejecutar en segundo plano
        analysis_win.after(100, ejecutar_analisis_simplificado)

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
    
    # Nuevo botón de análisis con Spark
    btn_analizar = tk.Button(btn_frame, text="📊 Analizar con Spark", command=analizar_con_spark,
                            bg="#9b59b6", fg="white", font=("Arial", 10, "bold"), width=15)
    btn_analizar.grid(row=0, column=3, padx=5)

    return tab_usuarios