import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.config import citas_col, users_col, servicios_col, estilistas_col
from datetime import datetime, timedelta

def crear_pestaña_estadisticas(parent, admin_win):
    tab_estadisticas = ttk.Frame(parent)
    
    # Frame principal dividido en dos partes
    main_frame = ttk.Frame(tab_estadisticas)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Frame para botones a la izquierda
    btn_frame = ttk.Frame(main_frame, width=200)
    btn_frame.pack(side="left", fill="y", padx=(0, 10))
    btn_frame.pack_propagate(False)
    
    # Frame para gráficos a la derecha
    graph_frame = ttk.Frame(main_frame)
    graph_frame.pack(side="right", fill="both", expand=True)
    
    # Variable para almacenar el gráfico actual
    current_canvas = None
    
    def clear_graph():
        """Limpiar el gráfico actual"""
        nonlocal current_canvas
        if current_canvas:
            current_canvas.get_tk_widget().destroy()
            current_canvas = None
    
    def mostrar_grafico(fig):
        """Mostrar un nuevo gráfico en el frame"""
        nonlocal current_canvas
        clear_graph()
        
        current_canvas = FigureCanvasTkAgg(fig, graph_frame)
        current_canvas.draw()
        current_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    # ========== FUNCIONES DE ESTADÍSTICAS ==========
    
    def cortes_mas_pedidos():
        """Mostrar los servicios más populares"""
        pipeline = [
            {"$lookup": {
                "from": "servicios",
                "localField": "servicio_id",
                "foreignField": "_id",
                "as": "servicio_info"
            }},
            {"$unwind": "$servicio_info"},
            {"$group": {
                "_id": "$servicio_info.nombre",
                "total": {"$sum": 1}
            }},
            {"$sort": {"total": -1}},
            {"$limit": 7}
        ]
        
        resultados = list(citas_col.aggregate(pipeline))
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        servicios = [item['_id'] for item in resultados]
        cantidades = [item['total'] for item in resultados]
        
        bars = ax.bar(servicios, cantidades, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF'])
        ax.set_title('Cortes Más Pedidos', fontsize=16, fontweight='bold')
        ax.set_xlabel('Servicios')
        ax.set_ylabel('Número de Citas')
        ax.tick_params(axis='x', rotation=45)
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        mostrar_grafico(fig)
    
    def estilistas_mas_solicitados():
        """Mostrar los estilistas más populares"""
        pipeline = [
            {"$lookup": {
                "from": "estilistas",
                "localField": "estilista_id",
                "foreignField": "_id",
                "as": "estilista_info"
            }},
            {"$unwind": "$estilista_info"},
            {"$group": {
                "_id": "$estilista_info.nombre",
                "total": {"$sum": 1}
            }},
            {"$sort": {"total": -1}},
            {"$limit": 7}
        ]
        
        resultados = list(citas_col.aggregate(pipeline))
        
        # Crear gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        estilistas = [item['_id'] for item in resultados]
        cantidades = [item['total'] for item in resultados]
        
        bars = ax.bar(estilistas, cantidades, color=['#FF9AA2', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7', '#C7CEEA', '#F8B195'])
        ax.set_title('Estilistas Más Solicitados', fontsize=16, fontweight='bold')
        ax.set_xlabel('Estilistas')
        ax.set_ylabel('Número de Citas')
        ax.tick_params(axis='x', rotation=45)
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        mostrar_grafico(fig)
    
    def citas_por_estado():
        """Mostrar distribución de citas por estado"""
        pipeline = [
            {"$group": {
                "_id": "$estado",
                "total": {"$sum": 1}
            }},
            {"$sort": {"total": -1}}
        ]
        
        resultados = list(citas_col.aggregate(pipeline))
        
        # Crear gráfico de pastel
        fig, ax = plt.subplots(figsize=(8, 8))
        estados = [item['_id'] for item in resultados]
        cantidades = [item['total'] for item in resultados]
        colores = ['#4CAF50', '#FFC107', '#F44336', '#2196F3', '#9C27B0']
        
        ax.pie(cantidades, labels=estados, autopct='%1.1f%%', colors=colores, startangle=90)
        ax.set_title('Distribución de Citas por Estado', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        mostrar_grafico(fig)
    
    def citas_por_mes():
        """Mostrar evolución de citas por mes"""
        pipeline = [
            {"$group": {
                "_id": {"$substr": ["$fecha", 0, 7]},  # Extraer YYYY-MM
                "total": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}},
            {"$limit": 12}  # Últimos 12 meses
        ]
        
        resultados = list(citas_col.aggregate(pipeline))
        
        # Crear gráfico de línea
        fig, ax = plt.subplots(figsize=(10, 6))
        meses = [item['_id'] for item in resultados]
        cantidades = [item['total'] for item in resultados]
        
        ax.plot(meses, cantidades, marker='o', linewidth=2, markersize=8, color='#2196F3')
        ax.fill_between(meses, cantidades, alpha=0.3, color='#2196F3')
        ax.set_title('Evolución de Citas por Mes', fontsize=16, fontweight='bold')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Número de Citas')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        mostrar_grafico(fig)
    
    def clientes_por_genero():
        """Mostrar distribución de clientes por género"""
        pipeline = [
            {"$match": {"role": "cliente"}},
            {"$group": {
                "_id": "$sexo",
                "total": {"$sum": 1}
            }}
        ]
        
        resultados = list(users_col.aggregate(pipeline))
        
        # Crear gráfico de pastel
        fig, ax = plt.subplots(figsize=(8, 8))
        generos = [item['_id'] for item in resultados]
        cantidades = [item['total'] for item in resultados]
        colores = ['#FF6B9D', '#4ECDC4', '#FFD166']
        
        ax.pie(cantidades, labels=generos, autopct='%1.1f%%', colors=colores, startangle=90)
        ax.set_title('Distribución de Clientes por Género', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        mostrar_grafico(fig)
    
    def horarios_mas_populares():
        """Mostrar los horarios más populares para citas"""
        pipeline = [
            {"$group": {
                "_id": {"$substr": ["$hora", 0, 2]},  # Extraer la hora
                "total": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}},
            {"$limit": 10}
        ]
        
        resultados = list(citas_col.aggregate(pipeline))
        
        # Crear gráfico de barras
        fig, ax = plt.subplots(figsize=(10, 6))
        horas = [f"{item['_id']}:00" for item in resultados]
        cantidades = [item['total'] for item in resultados]
        
        bars = ax.bar(horas, cantidades, color='#6A0572')
        ax.set_title('Horarios Más Populares', fontsize=16, fontweight='bold')
        ax.set_xlabel('Hora del Día')
        ax.set_ylabel('Número de Citas')
        ax.tick_params(axis='x', rotation=45)
        
        # Añadir valores en las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        mostrar_grafico(fig)
    
    def duracion_promedio_servicios():
        """Mostrar duración promedio de servicios"""
        servicios = list(servicios_col.find())
        
        # Crear gráfico de barras doble
        fig, ax = plt.subplots(figsize=(10, 6))
        
        nombres = [s['nombre'] for s in servicios]
        tiempos_h = [s.get('tiempo_M', 0) for s in servicios]
        tiempos_m = [s.get('tiempo_F', 0) for s in servicios]
        
        x = range(len(nombres))
        width = 0.35
        
        bars1 = ax.bar([i - width/2 for i in x], tiempos_h, width, label='Hombres', color='#4A90E2')
        bars2 = ax.bar([i + width/2 for i in x], tiempos_m, width, label='Mujeres', color='#E2A4A4')
        
        ax.set_title('Duración Promedio de Servicios (minutos)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Servicios')
        ax.set_ylabel('Duración (minutos)')
        ax.set_xticks(x)
        ax.set_xticklabels(nombres, rotation=45)
        ax.legend()
        
        # Añadir valores en las barras
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        mostrar_grafico(fig)
    
    # ========== BOTONES DE ESTADÍSTICAS ==========
    
    # Configurar estilo de botones
    button_style = {
        "font": ("Arial", 10, "bold"),
        "width": 18,
        "height": 2,
        "cursor": "hand2"
    }
    
    # Lista de botones con sus funciones
    botones_estadisticas = [
        ("✂️ Cortes Más Pedidos", cortes_mas_pedidos, "#FF6B6B"),
        ("💇 Estilistas Más Solicitados", estilistas_mas_solicitados, "#4ECDC4"),
        ("📊 Citas por Estado", citas_por_estado, "#45B7D1"),
        ("📅 Citas por Mes", citas_por_mes, "#96CEB4"),
        ("👥 Clientes por Género", clientes_por_genero, "#FECA57"),
        ("⏰ Horarios Populares", horarios_mas_populares, "#FF9FF3"),
        ("⏱️ Duración Servicios", duracion_promedio_servicios, "#54A0FF")
    ]
    
    # Crear botones
    for i, (texto, comando, color) in enumerate(botones_estadisticas):
        btn = tk.Button(
            btn_frame, 
            text=texto, 
            command=comando,
            bg=color,
            fg="white",
            **button_style
        )
        btn.pack(fill="x", pady=5)
    
    # Botón para limpiar gráfico
    btn_limpiar = tk.Button(
        btn_frame,
        text="🗑️ Limpiar Gráfico",
        command=clear_graph,
        bg="#95a5a6",
        fg="white",
        **button_style
    )
    btn_limpiar.pack(fill="x", pady=5)
    
    # Mensaje inicial
    fig_inicial, ax_inicial = plt.subplots(figsize=(10, 6))
    ax_inicial.text(0.5, 0.5, 'Selecciona una estadística\npara ver el gráfico', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax_inicial.transAxes, fontsize=16, fontweight='bold')
    ax_inicial.axis('off')
    mostrar_grafico(fig_inicial)
    
    return tab_estadisticas