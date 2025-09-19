from datetime import datetime, timedelta
from database.config import servicios_col, citas_col, estilistas_col

def calcular_duracion_por_genero(servicio_nombre: str, sexo_cliente: str) -> int:
    s = servicios_col.find_one({"nombre": servicio_nombre})
    if not s:
        return 30
    
    if sexo_cliente == "F":
        return s.get("tiempo_F", 60)
    elif sexo_cliente == "M":
        return s.get("tiempo_M", 30)
    else:
        return s.get("tiempo_M", 30)

def generar_horas_disponibles():
    horas = []
    for h in range(9, 21):
        for m in [0, 30]:
            hora_str = f"{h:02d}:{m:02d}"
            horas.append(hora_str)
    return horas

def es_domingo(fecha_str):
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        return fecha.weekday() == 6
    except:
        return False

def validar_horario(hora_inicio, hora_fin, hora_descanso):
    try:
        if hora_inicio and hora_fin:
            inicio = datetime.strptime(hora_inicio, "%H:%M")
            fin = datetime.strptime(hora_fin, "%H:%M")
            
            if inicio >= fin:
                return False, "La hora de inicio debe ser antes que la hora de fin"
            
            if hora_descanso and hora_descanso != "Descanso":
                descanso = datetime.strptime(hora_descanso, "%H:%M")
                if descanso <= inicio or descanso >= fin:
                    return False, "La hora de descanso debe estar entre la hora de inicio y fin"
        
        return True, "Horario válido"
    except:
        return False, "Formato de hora inválido"

def verificar_disponibilidad_estilista(estilista_id, fecha, hora, duracion):
    if es_domingo(fecha):
        return False
    
    estilista = estilistas_col.find_one({"_id": estilista_id})
    if not estilista:
        return False
        
    horarios = estilista.get("horarios", {})
    horario_fecha = horarios.get(fecha, {})
    
    if horario_fecha.get("descanso") == "Descanso":
        return False
        
    hora_inicio = horario_fecha.get("inicio", "11:00")
    hora_fin = horario_fecha.get("fin", "20:00")
    hora_descanso = horario_fecha.get("descanso", "14:00")
    
    try:
        hora_obj = datetime.strptime(hora, "%H:%M").time()
        inicio_obj = datetime.strptime(hora_inicio, "%H:%M").time()
        fin_obj = datetime.strptime(hora_fin, "%H:%M").time()
        
        # Verificar si la hora está fuera del horario laboral
        if hora_obj < inicio_obj or hora_obj >= fin_obj:
            return False
        
        # Verificar si la cita cae dentro del horario de descanso (1 HORA COMPLETA)
        if hora_descanso and hora_descanso != "Descanso":
            descanso_obj = datetime.strptime(hora_descanso, "%H:%M")
            fin_descanso_obj = descanso_obj + timedelta(hours=1)
            
            descanso_time = descanso_obj.time()
            fin_descanso_time = fin_descanso_obj.time()
            
            # Verificar si la cita se superpone con el descanso
            hora_cita = datetime.strptime(hora, "%H:%M")
            fin_cita = hora_cita + timedelta(minutes=duracion)
            
            # Convertir a time para comparación
            fin_cita_time = fin_cita.time()
            
            # Si la cita empieza durante el descanso
            if (descanso_time <= hora_obj < fin_descanso_time):
                return False
            # Si la cita termina durante el descanso
            if (descanso_time < fin_cita_time <= fin_descanso_time):
                return False
            # Si la cita cubre completamente el periodo de descanso
            if (hora_obj <= descanso_time and fin_cita_time >= fin_descanso_time):
                return False
                
    except Exception as e:
        print(f"Error en verificación de disponibilidad: {e}")
        return False
    
    citas_existentes = citas_col.find({
        "estilista_id": estilista_id,
        "fecha": fecha,
        "estado": {"$ne": "cancelado"}
    })
    
    hora_cita = datetime.strptime(hora, "%H:%M")
    
    for cita in citas_existentes:
        hora_existente = datetime.strptime(cita["hora"], "%H:%M")
        duracion_existente = timedelta(minutes=cita.get("duracion", 30))
        
        fin_existente = hora_existente + duracion_existente
        fin_cita = hora_cita + timedelta(minutes=duracion)
        
        if (hora_cita < fin_existente) and (fin_cita > hora_existente):
            return False
    
    return True

def estilista_tiene_horario(estilista_id, fecha):
    """
    Verifica si el estilista tiene horario configurado para una fecha específica
    """
    estilista = estilistas_col.find_one({"_id": estilista_id})
    if not estilista:
        return False
    
    horarios = estilista.get("horarios", {})
    horario_fecha = horarios.get(fecha, {})
    
    # Verificar si tiene horario configurado completo
    if horario_fecha.get("descanso") == "Descanso":
        return True  # Tiene horario de descanso configurado
    elif (horario_fecha.get("inicio") and 
            horario_fecha.get("fin") and 
            horario_fecha.get("descanso")):
        return True  # Tiene horario completo configurado
    
    return False  # No tiene horario configurado