# src/api/Components/SesionPedagogicaComponent.py

from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from datetime import datetime, date, time
import json


class SesionPedagogicaComponent:
    """Component para manejo de sesiones pedagógicas en la base de datos"""

    @staticmethod
    def get_sesiones():
        """Obtener todas las sesiones pedagógicas con información completa"""
        try:
            query = """
                SELECT 
                    sp.id,
                    sp.codigo_sesion,
                    sp.nombre_clase as titulo,
                    sp.id_educador as pedagogo_id,
                    CONCAT(p_ped.nombre, ' ', p_ped.apellido) as pedagogo_nombre,
                    sp.id_especialidad as especialidad_id,
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area,
                    sp.fecha_inicio,
                    sp.fecha_fin,
                    sp.dias_semana,
                    sp.hora_inicio,
                    sp.duracion_minutos,
                    20 as numero_clases_programadas,
                    sp.nivel_academico,
                    sp.capacidad_maxima,
                    'presencial' as modalidad,
                    sp.costo_total,
                    sp.costo_por_clase,
                    sp.periodo_academico,
                    sp.estado,
                    sp.observaciones,
                    sp.fecha_creacion,
                    sp.fecha_modificacion,
                    COUNT(DISTINCT se.paciente_id) as total_estudiantes,
                    COUNT(DISTINCT cc.id) as clases_programadas,
                    COUNT(DISTINCT CASE WHEN cc.estado = 'realizada' THEN cc.id END) as clases_realizadas,
                    ROUND(AVG(se.nota_final), 2) as promedio_notas,
                    ROUND(AVG(se.asistencia_porcentaje), 2) as promedio_asistencia
                FROM sesion_pedagogica sp
                JOIN personal per ON sp.id_educador = per.id
                JOIN persona p_ped ON per.id_persona = p_ped.id
                JOIN especialidad e ON sp.id_especialidad = e.id
                LEFT JOIN sesion_estudiante se ON sp.id = se.id_sesion AND se.estado = 'activo'
                LEFT JOIN cronograma_clases cc ON sp.id = cc.id_sesion
                GROUP BY sp.id, p_ped.nombre, p_ped.apellido, e.nombre, e.area
                ORDER BY sp.fecha_creacion DESC
            """

            result = DataBaseHandle.getRecords(query)
            HandleLogs.write_log("SesionPedagogicaComponent.get_sesiones - Sesiones obtenidas exitosamente")
            return result
        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.get_sesiones - Error: {str(e)}")
            raise Exception(f"Error al obtener sesiones pedagógicas: {str(e)}")

    @staticmethod
    def get_sesion_by_id(sesion_id):
        """Obtener una sesión pedagógica específica por ID con toda su información"""
        try:
            query = """
                SELECT 
                    sp.*,
                    CONCAT(p_ped.nombre, ' ', p_ped.apellido) as pedagogo_nombre,
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area
                FROM sesion_pedagogica sp
                JOIN personal per ON sp.id_educador = per.id
                JOIN persona p_ped ON per.id_persona = p_ped.id
                JOIN especialidad e ON sp.id_especialidad = e.id
                WHERE sp.id = %s
            """

            params = (sesion_id,)
            result = DataBaseHandle.getRecords(query, params, size=1)

            if result:
                HandleLogs.write_log(f"SesionPedagogicaComponent.get_sesion_by_id - Sesión {sesion_id} encontrada")
            else:
                HandleLogs.write_log(f"SesionPedagogicaComponent.get_sesion_by_id - Sesión {sesion_id} no encontrada")

            return result
        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.get_sesion_by_id - Error: {str(e)}")
            raise Exception(f"Error al obtener sesión pedagógica: {str(e)}")

    @staticmethod
    def create_sesion(sesion_data):
        """Crear nueva sesión pedagógica"""
        try:
            # Primero insertar la sesión
            insert_query = """
                INSERT INTO sesion_pedagogica (
                    codigo_sesion, nombre_clase, id_educador, id_especialidad, fecha_inicio, fecha_fin,
                    dias_semana, hora_inicio, duracion_minutos, nivel_academico,
                    estado, id_centro, usuario_creacion
                ) VALUES (
                    NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            params = (
                sesion_data['titulo'],  # nombre_clase
                sesion_data['pedagogo_id'],  # id_educador
                sesion_data['especialidad_id'],  # id_especialidad
                sesion_data['fecha_inicio'],
                sesion_data['fecha_fin'],
                sesion_data['dias_semana'],
                sesion_data['hora_inicio'],
                sesion_data.get('duracion_minutos', 60),
                sesion_data.get('nivel_academico', 'primaria'),
                sesion_data.get('estado', 'planificada'),
                sesion_data.get('id_centro', 1),
                sesion_data['usuario_creacion']
            )

            DataBaseHandle.ExecuteNonQuery(insert_query, params)
            
            # Obtener la sesión recién creada
            select_query = """
                SELECT id, codigo_sesion 
                FROM sesion_pedagogica 
                WHERE nombre_clase = %s AND id_educador = %s AND fecha_inicio = %s
                ORDER BY id DESC 
                LIMIT 1
            """
            select_params = (sesion_data['titulo'], sesion_data['pedagogo_id'], sesion_data['fecha_inicio'])
            result = DataBaseHandle.getRecords(select_query, select_params, size=1)

            if result:
                sesion_id = result['id']
                HandleLogs.write_log(f"SesionPedagogicaComponent.create_sesion - Sesión {sesion_id} creada exitosamente")
                
                # Generar cronograma automáticamente
                SesionPedagogicaComponent.generar_cronograma(sesion_id)
                
                return result
            else:
                raise Exception("No se pudo crear la sesión pedagógica")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.create_sesion - Error: {str(e)}")
            raise Exception(f"Error al crear sesión pedagógica: {str(e)}")

    @staticmethod
    def update_sesion(sesion_id, sesion_data):
        """Actualizar información de una sesión pedagógica"""
        try:
            query = """
                UPDATE sesion_pedagogica SET
                    nombre_clase = %s,
                    id_educador = %s,
                    id_especialidad = %s,
                    fecha_inicio = %s,
                    fecha_fin = %s,
                    dias_semana = %s,
                    hora_inicio = %s,
                    duracion_minutos = %s,
                    numero_clases_programadas = %s,
                    nivel_academico = %s,
                    capacidad_maxima = %s,
                    modalidad = %s,
                    costo_total = %s,
                    periodo_academico = %s,
                    estado = %s,
                    observaciones = %s,
                    usuario_modificacion = %s
                WHERE id = %s
            """

            params = (
                sesion_data['titulo'],
                sesion_data['pedagogo_id'],
                sesion_data['especialidad_id'],
                sesion_data['fecha_inicio'],
                sesion_data['fecha_fin'],
                sesion_data['dias_semana'],
                sesion_data['hora_inicio'],
                sesion_data.get('duracion_minutos', 60),
                sesion_data['numero_clases_programadas'],
                sesion_data.get('nivel_academico'),
                sesion_data.get('capacidad_maxima'),
                sesion_data.get('modalidad'),
                sesion_data['costo_total'],
                sesion_data.get('periodo_academico'),
                sesion_data.get('estado'),
                sesion_data.get('observaciones'),
                sesion_data['usuario_modificacion'],
                sesion_id
            )

            DataBaseHandle.ExecuteNonQuery(query, params)
            HandleLogs.write_log(f"SesionPedagogicaComponent.update_sesion - Sesión {sesion_id} actualizada")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.update_sesion - Error: {str(e)}")
            raise Exception(f"Error al actualizar sesión pedagógica: {str(e)}")

    @staticmethod
    def delete_sesion(sesion_id):
        """Eliminar una sesión pedagógica (eliminación lógica)"""
        try:
            query = "UPDATE sesion_pedagogica SET estado = 'cancelado' WHERE id = %s"
            params = (sesion_id,)

            DataBaseHandle.ExecuteNonQuery(query, params)
            HandleLogs.write_log(f"SesionPedagogicaComponent.delete_sesion - Sesión {sesion_id} cancelada")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.delete_sesion - Error: {str(e)}")
            raise Exception(f"Error al cancelar sesión pedagógica: {str(e)}")

    @staticmethod
    def generar_cronograma(sesion_id):
        """Generar cronograma automático para una sesión pedagógica - VERSIÓN MEJORADA"""
        try:
            # Primero obtener la información de la sesión
            sesion_query = """
                SELECT fecha_inicio, fecha_fin, dias_semana, hora_inicio, 20 as numero_clases_programadas, usuario_creacion
                FROM sesion_pedagogica 
                WHERE id = %s
            """
            sesion_data = DataBaseHandle.getRecords(sesion_query, (sesion_id,), size=1)
            
            if not sesion_data:
                raise Exception(f"Sesión pedagógica {sesion_id} no encontrada")
            
            # Validar datos requeridos
            if not sesion_data['fecha_inicio']:
                raise Exception("La fecha de inicio es requerida")
            if not sesion_data['dias_semana']:
                raise Exception("Los días de la semana son requeridos")
            # Use default number of classes since this field may not exist in database
            max_clases = sesion_data['numero_clases_programadas'] if sesion_data.get('numero_clases_programadas') else 20
            if max_clases <= 0:
                raise Exception("El número de clases programadas debe ser mayor a 0")
            
            # Limpiar cronograma existente
            delete_query = "DELETE FROM cronograma_clases WHERE id_sesion = %s"
            DataBaseHandle.ExecuteNonQuery(delete_query, (sesion_id,))
            
            # Generar cronograma programáticamente
            from datetime import datetime, timedelta
            
            fecha_inicio = sesion_data['fecha_inicio']
            fecha_fin = sesion_data['fecha_fin']
            
            # Handle dias_semana - could be string or array from database
            dias_semana_raw = sesion_data['dias_semana']
            if isinstance(dias_semana_raw, str):
                # Remove array brackets if present and clean
                dias_semana_str = dias_semana_raw.strip('{}').strip()
            elif isinstance(dias_semana_raw, list):
                # Join list elements
                dias_semana_str = ','.join(dias_semana_raw)
            else:
                dias_semana_str = str(dias_semana_raw).strip('{}').strip()
            
            hora_inicio = sesion_data['hora_inicio']
            # max_clases already set above
            
            # Mapeo de días (asegurar consistencia)
            dias_map = {
                'lunes': 0, 'martes': 1, 'miercoles': 2, 'miércoles': 2,
                'jueves': 3, 'viernes': 4, 'sabado': 5, 'sábado': 5, 'domingo': 6
            }
            
            # Procesar días de la semana con mejor validación
            dias_semana_list = [dia.strip().lower() for dia in dias_semana_str.split(',') if dia.strip()]
            dias_numeros = []
            
            for dia in dias_semana_list:
                if dia in dias_map:
                    dias_numeros.append(dias_map[dia])
                else:
                    HandleLogs.write_error(f"Día de semana no reconocido: {dia}")
            
            if not dias_numeros:
                raise Exception(f"No se pudieron procesar los días de la semana: {dias_semana_str}")
            
            # Remover duplicados y ordenar
            dias_numeros = sorted(list(set(dias_numeros)))
            
            # Calcular fecha límite inteligente
            if not fecha_fin:
                # Estimar fecha fin: (clases / días_por_semana) * 7 días + margen de 4 semanas
                dias_por_semana = len(dias_numeros)
                semanas_estimadas = (max_clases // dias_por_semana) + 1
                fecha_fin = fecha_inicio + timedelta(weeks=semanas_estimadas + 4)
            
            # Generar cronograma de manera eficiente
            fecha_actual = fecha_inicio
            numero_clase = 1
            clases_creadas = 0
            intentos_max = 1000  # Evitar bucles infinitos
            intentos = 0
            
            while clases_creadas < max_clases and fecha_actual <= fecha_fin and intentos < intentos_max:
                dia_semana = fecha_actual.weekday()  # 0=lunes, 6=domingo
                intentos += 1
                
                if dia_semana in dias_numeros:
                    # Insertar clase en cronograma
                    insert_query = """
                        INSERT INTO cronograma_clases (
                            id_sesion, fecha_programada, hora_inicio, hora_fin,
                            numero_clase_semanal, estado, usuario_creacion
                        ) VALUES (%s, %s, %s, %s, %s, 'programada', %s)
                    """
                    # Calculate hora_fin based on duration (default 60 minutes)
                    from datetime import timedelta
                    hora_fin = (datetime.combine(fecha_actual, hora_inicio) + timedelta(minutes=60)).time()
                    params = (sesion_id, fecha_actual, hora_inicio, hora_fin, numero_clase, sesion_data['usuario_creacion'])
                    DataBaseHandle.ExecuteNonQuery(insert_query, params)
                    
                    numero_clase += 1
                    clases_creadas += 1
                    
                    # Log progreso cada 10 clases
                    if clases_creadas % 10 == 0:
                        HandleLogs.write_log(f"Cronograma sesión pedagógica {sesion_id}: {clases_creadas}/{max_clases} generadas")
                
                fecha_actual += timedelta(days=1)
            
            # Validar resultados
            if clases_creadas == 0:
                raise Exception("No se pudieron generar clases. Verificar fechas y días de la semana.")
            
            if clases_creadas < max_clases:
                HandleLogs.write_error(
                    f"Advertencia: Solo se generaron {clases_creadas} de {max_clases} clases solicitadas")
            
            HandleLogs.write_log(
                f"SesionPedagogicaComponent.generar_cronograma - {clases_creadas} clases programadas para sesión {sesion_id}")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.generar_cronograma - Error: {str(e)}")
            raise Exception(f"Error al generar cronograma: {str(e)}")

    # ============================================
    # MÉTODOS PARA SESION_ESTUDIANTE
    # ============================================

    @staticmethod
    def get_estudiantes_sesion(sesion_id):
        """Obtener todos los estudiantes asignados a una sesión pedagógica"""
        try:
            query = """
                SELECT
                    se.id,
                    se.id_paciente as paciente_id,
                    CONCAT(p.nombre, ' ', p.apellido) as estudiante_nombre,
                    p.cedula as estudiante_cedula,
                    se.fecha_inscripcion as fecha_incorporacion,
                    se.nivel_actual as costo_estudiante,
                    se.observaciones as observaciones_estudiante,
                    se.estado,
                    NULL as nota_final,
                    NULL as asistencia_porcentaje,
                    CONCAT(p_tutor.nombre, ' ', p_tutor.apellido) as tutor_nombre,
                    p_tutor.telefono as tutor_telefono
                FROM sesion_estudiante se
                LEFT JOIN paciente pac ON se.id_paciente = pac.id
                LEFT JOIN persona p ON pac.id_persona = p.id
                LEFT JOIN tutor t ON pac.id_tutor = t.id
                LEFT JOIN persona p_tutor ON t.id_persona = p_tutor.id
                WHERE se.id_sesion = %s AND se.estado != 'retirado'
                ORDER BY se.fecha_inscripcion
            """

            params = (sesion_id,)
            result = DataBaseHandle.getRecords(query, params)
            HandleLogs.write_log(
                f"SesionPedagogicaComponent.get_estudiantes_sesion - {len(result) if result else 0} estudiantes encontrados")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.get_estudiantes_sesion - Error: {str(e)}")
            raise Exception(f"Error al obtener estudiantes de la sesión pedagógica: {str(e)}")

    @staticmethod
    def add_estudiante_to_sesion(sesion_id, estudiante_data):
        """Agregar un estudiante a una sesión pedagógica"""
        try:
            # Usar ExecuteNonQuery para INSERT (según buenas prácticas de CLAUDE.md)
            query = """
                INSERT INTO sesion_estudiante (
                    id_sesion, id_paciente, fecha_inscripcion,
                    nivel_actual, observaciones, estado, usuario_creacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            params = (
                sesion_id,
                estudiante_data['paciente_id'],
                estudiante_data.get('fecha_incorporacion', datetime.now().date()),
                estudiante_data.get('nivel_actual', 'basico'),
                estudiante_data.get('observaciones_estudiante', ''),
                estudiante_data.get('estado', 'activo'),
                estudiante_data['usuario_creacion']
            )

            # Ejecutar el INSERT
            DataBaseHandle.ExecuteNonQuery(query, params)
            
            # Obtener el ID insertado con una consulta separada
            id_query = """
                SELECT id FROM sesion_estudiante 
                WHERE id_sesion = %s AND id_paciente = %s
                ORDER BY fecha_creacion DESC LIMIT 1
            """
            id_params = (sesion_id, estudiante_data['paciente_id'])
            id_result = DataBaseHandle.getRecords(id_query, id_params)
            
            if id_result and len(id_result) > 0:
                estudiante_id = id_result[0]['id']
                HandleLogs.write_log(f"SesionPedagogicaComponent.add_estudiante_to_sesion - Estudiante agregado a sesión {sesion_id}")
                return estudiante_id
            else:
                raise Exception("No se pudo obtener el ID del estudiante agregado")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.add_estudiante_to_sesion - Error: {str(e)}")
            raise Exception(f"Error al agregar estudiante: {str(e)}")

    @staticmethod
    def remove_estudiante_from_sesion(sesion_id, paciente_id):
        """Remover estudiante de una sesión pedagógica"""
        try:
            query = """
                UPDATE sesion_estudiante 
                SET estado = 'retirado'
                WHERE id_sesion = %s AND id_paciente = %s
            """
            params = (sesion_id, paciente_id)

            DataBaseHandle.ExecuteNonQuery(query, params)
            HandleLogs.write_log(f"SesionPedagogicaComponent.remove_estudiante_from_sesion - Estudiante removido de sesión {sesion_id}")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.remove_estudiante_from_sesion - Error: {str(e)}")
            raise Exception(f"Error al remover estudiante: {str(e)}")

    # ============================================
    # MÉTODOS PARA CRONOGRAMA DE CLASES
    # ============================================

    @staticmethod
    def get_cronograma_sesion(sesion_id):
        """Obtener cronograma completo de una sesión pedagógica"""
        try:
            query = """
                SELECT 
                    cc.id,
                    cc.numero_clase_semanal as numero_clase,
                    cc.fecha_programada,
                    cc.hora_inicio as hora_programada,
                    cc.tema_clase,
                    cc.estado,
                    NULL as fecha_realizacion,
                    cc.objetivos_clase,
                    cc.material_requerido,
                    cc.tareas_asignadas,
                    cc.evaluacion_programada,
                    cc.tipo_evaluacion
                FROM cronograma_clases cc
                WHERE cc.id_sesion = %s
                ORDER BY cc.numero_clase_semanal
            """

            params = (sesion_id,)
            result = DataBaseHandle.getRecords(query, params)
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_cronograma_sesion - Cronograma obtenido para sesión {sesion_id}")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.get_cronograma_sesion - Error: {str(e)}")
            raise Exception(f"Error al obtener cronograma: {str(e)}")

    @staticmethod
    def get_sesiones_by_pedagogo(pedagogo_id):
        """Obtener sesiones pedagógicas de un pedagogo específico"""
        try:
            query = """
                SELECT 
                    sp.id,
                    sp.codigo_sesion,
                    sp.nombre_clase as titulo,
                    sp.id_educador as pedagogo_id,
                    CONCAT(p_ped.nombre, ' ', p_ped.apellido) as pedagogo_nombre,
                    sp.id_especialidad as especialidad_id,
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area,
                    sp.fecha_inicio,
                    sp.fecha_fin,
                    sp.dias_semana,
                    sp.hora_inicio,
                    sp.duracion_minutos,
                    20 as numero_clases_programadas,
                    sp.nivel_academico,
                    sp.capacidad_maxima,
                    'presencial' as modalidad,
                    sp.costo_total,
                    sp.costo_por_clase,
                    sp.periodo_academico,
                    sp.estado,
                    sp.observaciones,
                    sp.fecha_creacion,
                    sp.fecha_modificacion
                FROM sesion_pedagogica sp
                JOIN personal per ON sp.id_educador = per.id
                JOIN persona p_ped ON per.id_persona = p_ped.id
                JOIN especialidad e ON sp.id_especialidad = e.id
                WHERE sp.id_educador = %s
                ORDER BY sp.fecha_creacion DESC
            """

            params = (pedagogo_id,)
            result = DataBaseHandle.getRecords(query, params)
            
            # Convert time objects to strings for JSON serialization
            if result:
                for sesion in result:
                    if sesion.get('hora_inicio'):
                        sesion['hora_inicio'] = str(sesion['hora_inicio'])
                    if sesion.get('fecha_creacion'):
                        sesion['fecha_creacion'] = sesion['fecha_creacion'].isoformat()
                    if sesion.get('fecha_modificacion'):
                        sesion['fecha_modificacion'] = sesion['fecha_modificacion'].isoformat()
                    if sesion.get('fecha_inicio'):
                        sesion['fecha_inicio'] = sesion['fecha_inicio'].isoformat() 
                    if sesion.get('fecha_fin'):
                        sesion['fecha_fin'] = sesion['fecha_fin'].isoformat()
                        
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_sesiones_by_pedagogo - {len(result) if result else 0} sesiones encontradas para pedagogo {pedagogo_id}")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.get_sesiones_by_pedagogo - Error: {str(e)}")
            raise Exception(f"Error al obtener sesiones del pedagogo: {str(e)}")

    @staticmethod
    def get_estadisticas_sesiones():
        """Obtener estadísticas generales de sesiones pedagógicas"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_sesiones,
                    COUNT(CASE WHEN estado = 'activo' THEN 1 END) as sesiones_activas,
                    COUNT(CASE WHEN estado = 'completado' THEN 1 END) as sesiones_completadas,
                    COUNT(CASE WHEN estado = 'suspendido' THEN 1 END) as sesiones_suspendidas,
                    COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as sesiones_canceladas,
                    COALESCE(SUM(numero_clases_programadas), 0) as total_clases_programadas,
                    COALESCE(SUM(costo_total), 0) as ingresos_totales,
                    ROUND(AVG(duracion_minutos), 0) as duracion_promedio
                FROM sesion_pedagogica
            """

            query_clases = """
                SELECT 
                    COUNT(*) as total_clases_programadas,
                    COUNT(CASE WHEN estado = 'realizada' THEN 1 END) as clases_realizadas,
                    COUNT(CASE WHEN estado = 'programada' THEN 1 END) as clases_pendientes,
                    COUNT(CASE WHEN estado = 'cancelada' THEN 1 END) as clases_canceladas,
                    COUNT(CASE WHEN estado = 'reprogramada' THEN 1 END) as clases_reprogramadas
                FROM cronograma_clases
            """

            estadisticas_generales = DataBaseHandle.getRecords(query, size=1)
            estadisticas_clases = DataBaseHandle.getRecords(query_clases, size=1)

            # Combinar estadísticas
            estadisticas_finales = {}
            
            if estadisticas_generales:
                for key, value in estadisticas_generales.items():
                    estadisticas_finales[key] = value if value is not None else 0
            
            if estadisticas_clases:
                for key, value in estadisticas_clases.items():
                    estadisticas_finales[key] = value if value is not None else 0

            if not estadisticas_finales:
                estadisticas_finales = {
                    'total_sesiones': 0,
                    'sesiones_activas': 0,
                    'sesiones_completadas': 0,
                    'sesiones_suspendidas': 0,
                    'sesiones_canceladas': 0,
                    'total_clases_programadas': 0,
                    'clases_realizadas': 0,
                    'clases_pendientes': 0,
                    'clases_canceladas': 0,
                    'clases_reprogramadas': 0,
                    'ingresos_totales': 0,
                    'duracion_promedio': 0
                }

            HandleLogs.write_log("SesionPedagogicaComponent.get_estadisticas_sesiones - Estadísticas obtenidas")
            return estadisticas_finales

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.get_estadisticas_sesiones - Error: {str(e)}")
            raise Exception(f"Error al obtener estadísticas: {str(e)}")