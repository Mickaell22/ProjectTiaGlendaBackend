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
            # First, let's try a simple query to see if the table has data
            simple_query = "SELECT COUNT(*) as total FROM sesion_pedagogica"
            count_result = DataBaseHandle.getRecords(simple_query, size=1)
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_sesiones - Total sessions in DB: {count_result}")
            
            # If there are no sessions, return empty result
            if not count_result or count_result.get('total', 0) == 0:
                HandleLogs.write_log("SesionPedagogicaComponent.get_sesiones - No sessions found in database")
                return []
            
            # Query completa con información de pedagogo y especialidad
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
                    COALESCE(sp.numero_clases_programadas, 20) as numero_clases_programadas,
                    sp.nivel_academico,
                    sp.capacidad_maxima,
                    COALESCE(sp.modalidad, 'presencial') as modalidad,
                    COALESCE(sp.costo_total, 0) as costo_total,
                    COALESCE(sp.costo_por_clase, 0) as costo_por_clase,
                    COALESCE(sp.periodo_academico, '') as periodo_academico,
                    sp.estado,
                    sp.fecha_creacion,
                    COALESCE(COUNT(DISTINCT se.id_paciente), 0) as total_estudiantes,
                    COALESCE(COUNT(DISTINCT cc.id), 0) as clases_programadas,
                    COALESCE(COUNT(DISTINCT CASE WHEN cc.estado = 'realizada' THEN cc.id END), 0) as clases_realizadas
                FROM sesion_pedagogica sp
                JOIN personal per ON sp.id_educador = per.id
                JOIN persona p_ped ON per.id_persona = p_ped.id
                JOIN especialidad e ON sp.id_especialidad = e.id
                LEFT JOIN sesion_estudiante se ON sp.id = se.id_sesion AND se.estado = 'activo'
                LEFT JOIN cronograma_clases cc ON sp.id = cc.id_sesion
                GROUP BY sp.id, sp.codigo_sesion, sp.nombre_clase, sp.id_educador, sp.id_especialidad,
                         sp.fecha_inicio, sp.fecha_fin, sp.dias_semana, sp.hora_inicio, sp.duracion_minutos,
                         sp.numero_clases_programadas, sp.nivel_academico, sp.capacidad_maxima, sp.modalidad,
                         sp.costo_total, sp.costo_por_clase, sp.periodo_academico, sp.estado, sp.fecha_creacion,
                         p_ped.nombre, p_ped.apellido, e.nombre, e.area
                ORDER BY sp.fecha_creacion DESC
            """

            result = DataBaseHandle.getRecords(query)
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_sesiones - Query result count: {len(result) if result else 0}")
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
                    sp.id_educador as pedagogo_id,
                    sp.id_especialidad as especialidad_id,
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
    def get_cronograma_sesiones(filtros=None):
        """Obtener cronograma de sesiones pedagógicas con filtros opcionales"""
        try:
            # Query base para obtener sesiones con cronograma - corregido estado
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
                    sp.dias_semana,
                    sp.hora_inicio,
                    sp.duracion_minutos,
                    (sp.hora_inicio + (sp.duracion_minutos || ' minutes')::interval) as hora_fin,
                    sp.nivel_academico,
                    sp.capacidad_maxima,
                    'presencial' as modalidad,
                    sp.estado,
                    sp.fecha_inicio,
                    sp.fecha_fin,
                    COUNT(DISTINCT se.id_paciente) as total_estudiantes
                FROM sesion_pedagogica sp
                JOIN personal per ON sp.id_educador = per.id
                JOIN persona p_ped ON per.id_persona = p_ped.id
                JOIN especialidad e ON sp.id_especialidad = e.id
                LEFT JOIN sesion_estudiante se ON sp.id = se.id_sesion AND se.estado = 'activo'
                WHERE sp.estado IN ('en_curso', 'activa', 'activo')
            """
            
            params = []
            
            # Aplicar filtros si se proporcionan
            if filtros:
                if filtros.get('especialidad'):
                    query += " AND e.nombre LIKE %s"
                    params.append(f"%{filtros['especialidad']}%")
                
                if filtros.get('pedagogo'):
                    query += " AND CONCAT(p_ped.nombre, ' ', p_ped.apellido) LIKE %s"
                    params.append(f"%{filtros['pedagogo']}%")
                
                if filtros.get('semana'):
                    # Filtro por semana (se puede expandir según necesidades)
                    if filtros['semana'] == 'actual':
                        query += " AND sp.fecha_inicio <= CURRENT_DATE AND (sp.fecha_fin >= CURRENT_DATE OR sp.fecha_fin IS NULL)"
            
            query += " GROUP BY sp.id, p_ped.nombre, p_ped.apellido, e.nombre, e.area ORDER BY sp.hora_inicio"
            
            result = DataBaseHandle.getRecords(query, tuple(params) if params else None)
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_cronograma_sesiones - Query executed, raw result: {result}")
            
            # Verificar si result es None o vacío
            if result is None:
                HandleLogs.write_log("SesionPedagogicaComponent.get_cronograma_sesiones - Result is None, returning empty list")
                return []
            
            if not isinstance(result, list):
                HandleLogs.write_log(f"SesionPedagogicaComponent.get_cronograma_sesiones - Result is not list, type: {type(result)}")
                return []
            
            # Procesar los días de la semana para cada sesión
            for sesion in result:
                if sesion.get('dias_semana'):
                    try:
                        # Si dias_semana es JSON string, parsearlo
                        if isinstance(sesion['dias_semana'], str):
                            # Limpiar string de array de PostgreSQL
                            dias_str = sesion['dias_semana'].strip('{}').strip()
                            if dias_str:
                                sesion['dias_programados'] = [dia.strip() for dia in dias_str.split(',')]
                            else:
                                sesion['dias_programados'] = []
                        elif isinstance(sesion['dias_semana'], list):
                            sesion['dias_programados'] = sesion['dias_semana']
                        else:
                            sesion['dias_programados'] = []
                    except Exception as parse_error:
                        HandleLogs.write_error(f"Error parsing dias_semana: {parse_error}")
                        sesion['dias_programados'] = []
                else:
                    sesion['dias_programados'] = []
            
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_cronograma_sesiones - {len(result)} sesiones obtenidas")
            return result
            
        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.get_cronograma_sesiones - Error: {str(e)}")
            raise Exception(f"Error al obtener cronograma de sesiones: {str(e)}")

    @staticmethod
    def create_sesion(sesion_data):
        """Crear nueva sesión pedagógica"""
        try:
            # Primero insertar la sesión - usar campos correctos y estado 'en_curso'
            insert_query = """
                INSERT INTO sesion_pedagogica (
                    codigo_sesion, nombre_clase, id_educador, id_especialidad, fecha_inicio, fecha_fin,
                    dias_semana, hora_inicio, duracion_minutos, nivel_academico,
                    capacidad_maxima, costo_total, costo_por_clase, periodo_academico,
                    adaptacion_curricular, estado, id_centro, usuario_creacion
                ) VALUES (
                    NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            params = (
                sesion_data['titulo'],  # nombre_clase
                sesion_data['pedagogo_id'],  # id_educador
                sesion_data['especialidad_id'],  # id_especialidad
                sesion_data['fecha_inicio'],
                sesion_data.get('fecha_fin'),  # puede ser None
                sesion_data['dias_semana'],
                sesion_data['hora_inicio'],
                sesion_data.get('duracion_minutos', 60),
                sesion_data.get('nivel_academico', 'primaria'),
                sesion_data.get('capacidad_maxima', 10),
                sesion_data.get('costo_total', 0),
                sesion_data.get('costo_por_clase', 0),
                sesion_data.get('periodo_academico', ''),
                sesion_data.get('adaptacion_curricular', ''),  # Nuevo campo para adaptaciones curriculares
                sesion_data.get('estado', 'en_curso'),  # Estado por defecto correcto
                sesion_data.get('id_centro', 1),
                sesion_data['usuario_creacion']
            )

            # Ejecutar INSERT
            DataBaseHandle.ExecuteNonQuery(insert_query, params)
            HandleLogs.write_log("SesionPedagogicaComponent.create_sesion - INSERT ejecutado exitosamente")
            
            # Obtener la sesión recién creada con mejor query
            select_query = """
                SELECT id, codigo_sesion 
                FROM sesion_pedagogica 
                WHERE nombre_clase = %s AND id_educador = %s AND usuario_creacion = %s
                ORDER BY fecha_creacion DESC 
                LIMIT 1
            """
            select_params = (sesion_data['titulo'], sesion_data['pedagogo_id'], sesion_data['usuario_creacion'])
            result = DataBaseHandle.getRecords(select_query, select_params, size=1)
            HandleLogs.write_log(f"SesionPedagogicaComponent.create_sesion - SELECT result: {result}")

            if result:
                sesion_id = result['id']
                HandleLogs.write_log(f"SesionPedagogicaComponent.create_sesion - Sesión {sesion_id} creada exitosamente")
                
                # Generar cronograma automáticamente
                try:
                    SesionPedagogicaComponent.generar_cronograma(sesion_id)
                    HandleLogs.write_log(f"SesionPedagogicaComponent.create_sesion - Cronograma generado para sesión {sesion_id}")
                except Exception as cronograma_error:
                    HandleLogs.write_error(f"Error generando cronograma: {str(cronograma_error)}")
                    # No fallar por error de cronograma, solo registrar
                
                return result
            else:
                HandleLogs.write_error("SesionPedagogicaComponent.create_sesion - No se pudo obtener la sesión creada")
                raise Exception("No se pudo obtener la sesión pedagógica creada")

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
                    nivel_academico = %s,
                    capacidad_maxima = %s,
                    costo_total = %s,
                    costo_por_clase = %s,
                    periodo_academico = %s,
                    adaptacion_curricular = %s,
                    estado = %s,
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
                sesion_data.get('nivel_academico'),
                sesion_data.get('capacidad_maxima'),
                sesion_data.get('costo_total', 0),
                sesion_data.get('costo_por_clase', 0),
                sesion_data.get('periodo_academico', ''),
                sesion_data.get('adaptacion_curricular', ''),  # Incluir adaptacion_curricular en UPDATE
                sesion_data.get('estado'),
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
                SELECT fecha_inicio, fecha_fin, dias_semana, hora_inicio, 
                       COALESCE(numero_clases_programadas, 20) as numero_clases_programadas, 
                       usuario_creacion
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
            # Get number of classes (default 20 if not specified)
            max_clases = sesion_data['numero_clases_programadas']
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
            
            # NUEVO: Crear registros de asistencia para todos los estudiantes inscritos
            try:
                SesionPedagogicaComponent._crear_registros_asistencia_cronograma(sesion_id)
                HandleLogs.write_log(f"Registros de asistencia creados para cronograma de sesión {sesion_id}")
            except Exception as asistencia_error:
                HandleLogs.write_error(f"Error creando registros de asistencia: {str(asistencia_error)}")
                # No fallar por este error, el cronograma ya está creado
            
            HandleLogs.write_log(
                f"SesionPedagogicaComponent.generar_cronograma - {clases_creadas} clases programadas para sesión {sesion_id}")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.generar_cronograma - Error: {str(e)}")
            raise Exception(f"Error al generar cronograma: {str(e)}")

    @staticmethod
    def _crear_registros_asistencia_cronograma(sesion_id):
        """Crear registros de asistencia para todos los estudiantes de todas las clases del cronograma"""
        try:
            # Obtener todas las clases del cronograma
            cronograma_query = """
                SELECT id FROM cronograma_clases 
                WHERE id_sesion = %s 
                ORDER BY fecha_programada, hora_inicio
            """
            clases = DataBaseHandle.getRecords(cronograma_query, (sesion_id,))
            
            if not clases:
                HandleLogs.write_log(f"No hay clases en el cronograma para sesión {sesion_id}")
                return
            
            # Obtener todos los estudiantes inscritos en la sesión
            estudiantes_query = """
                SELECT id_paciente FROM sesion_estudiante 
                WHERE id_sesion = %s AND estado = 'activo'
            """
            estudiantes = DataBaseHandle.getRecords(estudiantes_query, (sesion_id,))
            
            if not estudiantes:
                HandleLogs.write_log(f"No hay estudiantes inscritos en sesión {sesion_id}")
                return
            
            # Crear registros de asistencia para cada combinación clase-estudiante
            registros_creados = 0
            for clase in clases:
                for estudiante in estudiantes:
                    try:
                        # Verificar si ya existe el registro
                        check_query = """
                            SELECT id FROM asistencia_clases 
                            WHERE id_cronograma = %s AND id_paciente = %s
                        """
                        existing = DataBaseHandle.getRecords(check_query, (clase['id'], estudiante['id_paciente']), size=1)
                        
                        if not existing:
                            # Crear nuevo registro de asistencia (sin marcar asistencia por defecto)
                            insert_query = """
                                INSERT INTO asistencia_clases (
                                    id_cronograma, id_paciente, asistio, llegada_tardanza_minutos,
                                    estado_asistencia, fecha_creacion, usuario_creacion
                                ) VALUES (%s, %s, NULL, 0, 'pendiente', CURRENT_TIMESTAMP, 1)
                            """
                            DataBaseHandle.ExecuteNonQuery(insert_query, (clase['id'], estudiante['id_paciente']))
                            registros_creados += 1
                    
                    except Exception as registro_error:
                        HandleLogs.write_error(f"Error creando registro asistencia clase {clase['id']}, estudiante {estudiante['id_paciente']}: {str(registro_error)}")
                        continue
            
            HandleLogs.write_log(f"Creados {registros_creados} registros de asistencia para sesión {sesion_id}")
            
        except Exception as e:
            HandleLogs.write_error(f"Error en _crear_registros_asistencia_cronograma: {str(e)}")
            raise Exception(f"Error creando registros de asistencia: {str(e)}")

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
                    0 as costo_estudiante,
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
            # Primero verificar si el estudiante ya está asignado a esta sesión
            check_query = """
                SELECT id FROM sesion_estudiante 
                WHERE id_sesion = %s AND id_paciente = %s AND estado = 'activo'
            """
            check_params = (sesion_id, estudiante_data['paciente_id'])
            existing = DataBaseHandle.getRecords(check_query, check_params)
            
            if existing and len(existing) > 0:
                raise Exception("El estudiante ya está asignado a esta sesión pedagógica")
            
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
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_cronograma_sesion - Iniciando para sesión {sesion_id}")
            
            query = """
                SELECT 
                    cc.id,
                    cc.numero_clase_semanal as numero_clase,
                    cc.fecha_programada,
                    cc.hora_inicio as hora_programada,
                    cc.hora_fin,
                    cc.tema_clase,
                    CASE 
                        WHEN cc.estado = 'completada' THEN 'realizada'
                        ELSE cc.estado
                    END as estado,
                    cc.fecha_confirmacion as fecha_realizacion,
                    cc.objetivos_clase,
                    cc.materiales_necesarios as material_requerido,
                    cc.observaciones,
                    cc.motivo_reprogramacion,
                    cc.fecha_original,
                    cc.motivo_cancelacion,
                    '' as tareas_asignadas,
                    '' as evaluacion_programada,
                    '' as tipo_evaluacion
                FROM cronograma_clases cc
                WHERE cc.id_sesion = %s
                ORDER BY cc.numero_clase_semanal
            """

            params = (sesion_id,)
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_cronograma_sesion - Ejecutando query con sesion_id: {sesion_id}")
            
            # Usar getRecordsWithStatus para mejor debugging
            result_with_status = DataBaseHandle.getRecordsWithStatus(query, params)
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_cronograma_sesion - Result with status: {result_with_status}")
            
            if result_with_status and 'data' in result_with_status:
                result = result_with_status['data']
                HandleLogs.write_log(f"SesionPedagogicaComponent.get_cronograma_sesion - Cronograma obtenido para sesión {sesion_id}, registros: {len(result) if result else 0}")
                
                # Convert None values to empty strings for consistency
                if result:
                    for record in result:
                        if record.get('observaciones') is None:
                            record['observaciones'] = ''
                
                return result if result is not None else []
            else:
                HandleLogs.write_log(f"SesionPedagogicaComponent.get_cronograma_sesion - No data returned or error in query for session {sesion_id}")
                return []

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
                    COALESCE(sp.numero_clases_programadas, 20) as numero_clases_programadas,
                    sp.nivel_academico,
                    sp.capacidad_maxima,
                    'presencial' as modalidad,
                    0 as costo_total,
                    0 as costo_por_clase,
                    '' as periodo_academico,
                    sp.estado,
                    '' as observaciones,
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
                    COUNT(CASE WHEN estado IN ('en_curso', 'activo', 'activa') THEN 1 END) as sesiones_activas,
                    COUNT(CASE WHEN estado IN ('completada', 'completado') THEN 1 END) as sesiones_completadas,
                    COUNT(CASE WHEN estado IN ('suspendida', 'suspendido') THEN 1 END) as sesiones_suspendidas,
                    COUNT(CASE WHEN estado IN ('cancelada', 'cancelado') THEN 1 END) as sesiones_canceladas,
                    0 as total_clases_programadas,
                    0 as ingresos_totales,
                    ROUND(AVG(duracion_minutos), 0) as duracion_promedio
                FROM sesion_pedagogica
            """

            query_clases = """
                SELECT 
                    COUNT(*) as total_clases_programadas,
                    COUNT(CASE WHEN estado IN ('realizada', 'completada') THEN 1 END) as clases_realizadas,
                    COUNT(CASE WHEN estado = 'programada' THEN 1 END) as clases_pendientes,
                    COUNT(CASE WHEN estado IN ('cancelada', 'cancelado') THEN 1 END) as clases_canceladas,
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

    # ============================================
    # MÉTODOS PARA SISTEMA DE ASISTENCIAS
    # ============================================

    @staticmethod
    def registrar_asistencia(cronograma_id, estudiante_id, asistencia_data):
        """Registrar asistencia de un estudiante a una clase"""
        try:
            # Verificar que la clase existe
            verificar_query = """
                SELECT cc.id, cc.fecha_programada, cc.hora_inicio, cc.id_sesion
                FROM cronograma_clases cc
                WHERE cc.id = %s
            """
            clase_info = DataBaseHandle.getRecords(verificar_query, (cronograma_id,), size=1)
            
            if not clase_info:
                raise Exception(f"Clase con ID {cronograma_id} no encontrada")

            # Insertar asistencia
            insert_query = """
                INSERT INTO asistencia_clases (
                    id_cronograma, id_paciente, asistio, hora_llegada, hora_salida,
                    llegada_tardanza_minutos, estado_asistencia, observaciones_educador,
                    objetivos_trabajados, calificacion_clase,
                    usuario_creacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            params = (
                cronograma_id,
                estudiante_id,
                asistencia_data.get('asistio', False),
                asistencia_data.get('hora_llegada'),
                asistencia_data.get('hora_salida'),
                asistencia_data.get('llegada_tardanza_minutos', 0),
                asistencia_data.get('estado_asistencia', 'presente' if asistencia_data.get('asistio') else 'ausente'),
                asistencia_data.get('observaciones_educador') or asistencia_data.get('observaciones_asistencia'),
                asistencia_data.get('objetivos_trabajados') or asistencia_data.get('proximos_objetivos'),
                asistencia_data.get('calificacion_evaluacion') or asistencia_data.get('calificacion_clase'),
                asistencia_data.get('usuario_creacion', 1)
            )

            DataBaseHandle.ExecuteNonQuery(insert_query, params)

            # Obtener el ID de asistencia creado
            select_query = """
                SELECT id FROM asistencia_clases 
                WHERE id_cronograma = %s AND id_paciente = %s
                ORDER BY fecha_creacion DESC LIMIT 1
            """
            result = DataBaseHandle.getRecords(select_query, (cronograma_id, estudiante_id), size=1)

            if result:
                asistencia_id = result['id']
                HandleLogs.write_log(f"SesionPedagogicaComponent.registrar_asistencia - Asistencia {asistencia_id} registrada")
                return asistencia_id
            else:
                raise Exception("No se pudo obtener el ID de asistencia creado")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.registrar_asistencia - Error: {str(e)}")
            raise Exception(f"Error al registrar asistencia: {str(e)}")

    @staticmethod
    def actualizar_asistencia(cronograma_id, estudiante_id, asistencia_data):
        """Actualizar asistencia existente o crear nueva si no existe (UPSERT)"""
        try:
            # PostgreSQL UPSERT: INSERT ... ON CONFLICT DO UPDATE
            upsert_query = """
                INSERT INTO asistencia_clases (
                    id_cronograma, id_paciente, asistio, hora_llegada, hora_salida,
                    llegada_tardanza_minutos, estado_asistencia, observaciones_educador,
                    objetivos_trabajados, calificacion_clase,
                    usuario_creacion, usuario_modificacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_cronograma, id_paciente) 
                DO UPDATE SET
                    asistio = EXCLUDED.asistio,
                    hora_llegada = EXCLUDED.hora_llegada,
                    hora_salida = EXCLUDED.hora_salida,
                    llegada_tardanza_minutos = EXCLUDED.llegada_tardanza_minutos,
                    estado_asistencia = EXCLUDED.estado_asistencia,
                    observaciones_educador = EXCLUDED.observaciones_educador,
                    objetivos_trabajados = EXCLUDED.objetivos_trabajados,
                    calificacion_clase = EXCLUDED.calificacion_clase,
                    usuario_modificacion = EXCLUDED.usuario_modificacion,
                    fecha_modificacion = CURRENT_TIMESTAMP
            """

            params = (
                cronograma_id,
                estudiante_id,
                asistencia_data.get('asistio', False),
                asistencia_data.get('hora_llegada'),
                asistencia_data.get('hora_salida'),
                asistencia_data.get('llegada_tardanza_minutos', 0),
                asistencia_data.get('estado_asistencia', 'presente' if asistencia_data.get('asistio') else 'ausente'),
                asistencia_data.get('observaciones_educador'),
                asistencia_data.get('objetivos_trabajados'),
                asistencia_data.get('calificacion_evaluacion'),
                asistencia_data.get('usuario_creacion', 1),
                asistencia_data.get('usuario_modificacion', 1)
            )

            DataBaseHandle.ExecuteNonQuery(upsert_query, params)
            HandleLogs.write_log(f"SesionPedagogicaComponent.actualizar_asistencia - Asistencia upserted para clase {cronograma_id}, estudiante {estudiante_id}")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.actualizar_asistencia - Error: {str(e)}")
            raise Exception(f"Error al actualizar asistencia: {str(e)}")

    @staticmethod
    def get_asistencias_por_sesion(sesion_id):
        """Obtener todas las asistencias de una sesión pedagógica"""
        try:
            query = """
                SELECT 
                    ac.id,
                    ac.id_cronograma,
                    ac.id_paciente,
                    cc.fecha_programada,
                    cc.hora_inicio as hora_programada,
                    cc.numero_clase_semanal,
                    CONCAT(p.nombre, ' ', p.apellido) as estudiante_nombre,
                    p.cedula as estudiante_cedula,
                    ac.asistio,
                    ac.hora_llegada,
                    ac.hora_salida,
                    ac.llegada_tardanza_minutos,
                    ac.estado_asistencia,
                    ac.observaciones_educador,
                    ac.objetivos_trabajados,
                    ac.progreso_observado,
                    ac.calificacion_clase,
                    ac.fecha_creacion as fecha_registro
                FROM asistencia_clases ac
                JOIN cronograma_clases cc ON ac.id_cronograma = cc.id
                JOIN paciente pac ON ac.id_paciente = pac.id
                JOIN persona p ON pac.id_persona = p.id
                WHERE cc.id_sesion = %s
                ORDER BY cc.fecha_programada DESC, p.nombre
            """

            result = DataBaseHandle.getRecords(query, (sesion_id,))
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_asistencias_por_sesion - {len(result) if result else 0} asistencias encontradas")
            return result or []

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.get_asistencias_por_sesion - Error: {str(e)}")
            raise Exception(f"Error al obtener asistencias: {str(e)}")

    @staticmethod
    def get_control_asistencia(cronograma_id):
        """Obtener control de asistencia completo para una clase específica"""
        try:
            query = """
                SELECT 
                    cc.id as cronograma_id,
                    cc.numero_clase_semanal,
                    cc.fecha_programada,
                    cc.hora_inicio,
                    cc.tema_clase,
                    sp.nombre_clase as sesion_titulo,
                    sp.codigo_sesion,
                    CONCAT(p_edu.nombre, ' ', p_edu.apellido) as educador_nombre,
                    -- Información de estudiantes y sus asistencias
                    se.id_paciente as estudiante_id,
                    CONCAT(p_est.nombre, ' ', p_est.apellido) as nombre,
                    CONCAT(p_est.nombre, ' ', p_est.apellido) as estudiante_nombre,
                    p_est.cedula as estudiante_cedula,
                    ac.asistio,
                    ac.hora_llegada,
                    ac.hora_salida,
                    ac.llegada_tardanza_minutos,
                    ac.estado_asistencia,
                    ac.observaciones_educador,
                    ac.objetivos_trabajados,
                    ac.calificacion_clase,
                    ac.evaluacion_comportamiento,
                    ac.tareas_asignadas,
                    ac.actividades_completadas,
                    ac.fecha_creacion as fecha_registro,
                    ac.fecha_modificacion
                FROM cronograma_clases cc
                JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
                JOIN personal per ON sp.id_educador = per.id
                JOIN persona p_edu ON per.id_persona = p_edu.id
                LEFT JOIN sesion_estudiante se ON sp.id = se.id_sesion AND se.estado = 'activo'
                LEFT JOIN paciente pac ON se.id_paciente = pac.id
                LEFT JOIN persona p_est ON pac.id_persona = p_est.id
                LEFT JOIN asistencia_clases ac ON cc.id = ac.id_cronograma AND se.id_paciente = ac.id_paciente
                WHERE cc.id = %s
                ORDER BY p_est.nombre
            """

            result = DataBaseHandle.getRecords(query, (cronograma_id,))
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_control_asistencia - Control obtenido para clase {cronograma_id}")
            return result or []

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.get_control_asistencia - Error: {str(e)}")
            raise Exception(f"Error al obtener control de asistencia: {str(e)}")

    @staticmethod
    def marcar_clase_realizada(cronograma_id, usuario_id, observaciones=''):
        """Marcar una clase como realizada con observaciones"""
        try:
            # Actualizar el registro con las observaciones
            update_query = """
                UPDATE cronograma_clases SET
                    estado = 'realizada',
                    fecha_confirmacion = CURRENT_TIMESTAMP,
                    observaciones = %s,
                    usuario_modificacion = %s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            params = (observaciones, usuario_id, cronograma_id)
            DataBaseHandle.ExecuteNonQuery(update_query, params)
            
            HandleLogs.write_log(f"SesionPedagogicaComponent.marcar_clase_realizada - Clase {cronograma_id} marcada como realizada con observaciones: '{observaciones[:50]}{'...' if len(observaciones) > 50 else ''}'")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.marcar_clase_realizada - Error: {str(e)}")
            raise Exception(f"Error al marcar clase como realizada: {str(e)}")

    @staticmethod
    def reprogramar_clase(cronograma_id, nueva_fecha, nueva_hora, motivo, usuario_id):
        """Reprogramar una clase - CREAR NUEVA CLASE EN LUGAR DE ACTUALIZAR LA EXISTENTE"""
        try:
            # Primero, obtener información de la clase original
            get_original_query = """
                SELECT cc.*, sp.id as sesion_id, sp.duracion_minutos
                FROM cronograma_clases cc
                JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
                WHERE cc.id = %s
            """
            
            original_class = DataBaseHandle.getRecords(get_original_query, (cronograma_id,), size=1)
            
            if not original_class:
                raise Exception(f"Clase con ID {cronograma_id} no encontrada")
            
            # Marcar la clase original como reprogramada (para histórico)
            update_original_query = """
                UPDATE cronograma_clases SET
                    estado = 'reprogramada',
                    motivo_reprogramacion = %s,
                    usuario_modificacion = %s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            params_update = (f"Reprogramada: {motivo}", usuario_id, cronograma_id)
            DataBaseHandle.ExecuteNonQuery(update_original_query, params_update)
            
            # Calcular hora_fin para la nueva clase
            from datetime import datetime, timedelta
            duracion_minutos = original_class.get('duracion_minutos', 60)
            hora_fin = (datetime.combine(nueva_fecha, nueva_hora) + timedelta(minutes=duracion_minutos)).time()
            
            # Obtener el próximo número de clase disponible para evitar duplicados
            next_class_number_query = """
                SELECT COALESCE(MAX(numero_clase_semanal), 0) + 1 as next_number
                FROM cronograma_clases 
                WHERE id_sesion = %s
            """
            next_number_result = DataBaseHandle.getRecords(next_class_number_query, (original_class['id_sesion'],), size=1)
            next_class_number = next_number_result['next_number'] if next_number_result else 1
            
            # Crear observaciones detalladas con fecha actual
            from datetime import datetime
            fecha_hoy = datetime.now().strftime('%d/%m/%Y')
            
            # Preservar observaciones existentes si las hay
            observaciones_existentes = original_class.get('observaciones', '')
            observaciones_reprogramacion = f"REPROGRAMADA el {fecha_hoy}: Clase original #{original_class['numero_clase_semanal']} programada para {original_class['fecha_programada']} fue reprogramada para {nueva_fecha}. Motivo: {motivo}"
            
            if observaciones_existentes and observaciones_existentes.strip():
                observaciones_detalladas = f"{observaciones_existentes}\n\n{observaciones_reprogramacion}"
            else:
                observaciones_detalladas = observaciones_reprogramacion
            
            # Crear nueva entrada en cronograma con la nueva fecha/hora
            insert_new_query = """
                INSERT INTO cronograma_clases (
                    id_sesion, fecha_programada, hora_inicio, hora_fin,
                    numero_clase_semanal, tema_clase, objetivos_clase, 
                    materiales_necesarios, estado, observaciones,
                    motivo_reprogramacion, fecha_original,
                    usuario_creacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'programada', %s, %s, %s, %s)
            """
            
            # Usar nuevo número de clase y contenido de la original
            params_insert = (
                original_class['id_sesion'],           # sesion_id
                nueva_fecha,                           # nueva fecha
                nueva_hora,                            # nueva hora
                hora_fin,                              # hora fin calculada
                next_class_number,                     # NUEVO número de clase
                original_class.get('tema_clase', ''),  # mismo tema
                original_class.get('objetivos_clase', ''), # mismos objetivos
                original_class.get('materiales_necesarios', ''), # mismos materiales
                observaciones_detalladas,              # observaciones detalladas
                motivo,                                # motivo de reprogramación
                original_class['fecha_programada'],    # fecha original para referencia
                usuario_id                             # usuario que reprograma
            )
            
            DataBaseHandle.ExecuteNonQuery(insert_new_query, params_insert)
            
            # Obtener el ID de la nueva clase creada - usando el nuevo número de clase
            get_new_id_query = """
                SELECT id FROM cronograma_clases 
                WHERE id_sesion = %s AND fecha_programada = %s AND hora_inicio = %s 
                AND numero_clase_semanal = %s AND estado = 'programada' AND usuario_creacion = %s
                ORDER BY fecha_creacion DESC LIMIT 1
            """
            
            new_class_params = (
                original_class['id_sesion'],
                nueva_fecha, 
                nueva_hora,
                next_class_number,
                usuario_id
            )
            
            new_class_result = DataBaseHandle.getRecords(get_new_id_query, new_class_params, size=1)
            
            if new_class_result:
                nueva_clase_id = new_class_result['id']
                
                # Crear registros de asistencia para la nueva clase (para todos los estudiantes inscritos)
                try:
                    estudiantes_query = """
                        SELECT id_paciente FROM sesion_estudiante 
                        WHERE id_sesion = %s AND estado = 'activo'
                    """
                    estudiantes = DataBaseHandle.getRecords(estudiantes_query, (original_class['id_sesion'],))
                    
                    if estudiantes:
                        for estudiante in estudiantes:
                            # Verificar que no existe ya un registro de asistencia
                            check_asistencia_query = """
                                SELECT id FROM asistencia_clases 
                                WHERE id_cronograma = %s AND id_paciente = %s
                            """
                            existing = DataBaseHandle.getRecords(check_asistencia_query, (nueva_clase_id, estudiante['id_paciente']), size=1)
                            
                            if not existing:
                                # Crear registro de asistencia pendiente
                                insert_asistencia_query = """
                                    INSERT INTO asistencia_clases (
                                        id_cronograma, id_paciente, asistio, llegada_tardanza_minutos,
                                        estado_asistencia, fecha_creacion, usuario_creacion
                                    ) VALUES (%s, %s, NULL, 0, 'pendiente', CURRENT_TIMESTAMP, %s)
                                """
                                DataBaseHandle.ExecuteNonQuery(insert_asistencia_query, (nueva_clase_id, estudiante['id_paciente'], usuario_id))
                    
                    HandleLogs.write_log(f"SesionPedagogicaComponent.reprogramar_clase - Registros de asistencia creados para nueva clase {nueva_clase_id}")
                
                except Exception as asistencia_error:
                    HandleLogs.write_error(f"Error creando registros de asistencia para clase reprogramada: {str(asistencia_error)}")
                    # No fallar por este error, la clase ya fue creada exitosamente
                
                HandleLogs.write_log(f"SesionPedagogicaComponent.reprogramar_clase - Clase {cronograma_id} (#{original_class['numero_clase_semanal']}) reprogramada. Nueva clase creada: {nueva_clase_id} (#{next_class_number})")
                return nueva_clase_id
            else:
                raise Exception("No se pudo obtener el ID de la nueva clase creada")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.reprogramar_clase - Error: {str(e)}")
            raise Exception(f"Error al reprogramar clase: {str(e)}")

    @staticmethod
    def cancelar_clase(cronograma_id, motivo, usuario_id):
        """Cancelar una clase"""
        try:
            update_query = """
                UPDATE cronograma_clases SET
                    estado = 'cancelada',
                    motivo_cancelacion = %s,
                    usuario_modificacion = %s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            params = (motivo, usuario_id, cronograma_id)
            DataBaseHandle.ExecuteNonQuery(update_query, params)
            HandleLogs.write_log(f"SesionPedagogicaComponent.cancelar_clase - Clase {cronograma_id} cancelada")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.cancelar_clase - Error: {str(e)}")
            raise Exception(f"Error al cancelar clase: {str(e)}")

    @staticmethod
    def get_sesiones_by_centro(centro_id):
        """Obtener todas las sesiones pedagógicas de un centro específico"""
        try:
            query = """
                SELECT
                    sp.id,
                    sp.codigo_sesion,
                    sp.nombre_clase as titulo,
                    sp.id_educador as pedagogo_id,
                    sp.id_especialidad as especialidad_id,
                    sp.fecha_inicio,
                    sp.fecha_fin,
                    sp.dias_semana,
                    sp.hora_inicio,
                    sp.duracion_minutos,
                    COALESCE(sp.numero_clases_programadas, 20) as numero_clases_programadas,
                    sp.nivel_academico,
                    sp.capacidad_maxima,
                    'presencial' as modalidad,
                    0 as costo_total,
                    0 as costo_por_clase,
                    '' as periodo_academico,
                    sp.estado,
                    '' as observaciones,
                    sp.fecha_creacion,
                    sp.fecha_modificacion,
                    sp.id_centro,
                    -- Información del pedagogo
                    CONCAT(p_ped.nombre, ' ', p_ped.apellido) as pedagogo_nombre,
                    -- Información de la especialidad
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area,
                    -- Estadísticas básicas
                    COALESCE(COUNT(DISTINCT se.id_paciente), 0) as total_estudiantes,
                    COALESCE(COUNT(DISTINCT cc.id), 0) as clases_programadas,
                    COALESCE(COUNT(DISTINCT CASE WHEN cc.estado = 'realizada' THEN cc.id END), 0) as clases_realizadas,
                    0 as promedio_notas,
                    0 as promedio_asistencia
                FROM sesion_pedagogica sp
                JOIN personal per ON sp.id_educador = per.id
                JOIN persona p_ped ON per.id_persona = p_ped.id
                JOIN especialidad e ON sp.id_especialidad = e.id
                LEFT JOIN sesion_estudiante se ON sp.id = se.id_sesion AND se.estado = 'activo'
                LEFT JOIN cronograma_clases cc ON sp.id = cc.id_sesion
                WHERE sp.id_centro = %s
                GROUP BY sp.id, sp.codigo_sesion, sp.nombre_clase, sp.id_educador, sp.id_especialidad,
                         sp.fecha_inicio, sp.fecha_fin, sp.dias_semana, sp.hora_inicio, sp.duracion_minutos,
                         sp.nivel_academico, sp.capacidad_maxima, sp.estado, sp.fecha_creacion, sp.fecha_modificacion,
                         sp.id_centro, p_ped.nombre, p_ped.apellido, e.nombre, e.area
                ORDER BY sp.fecha_creacion DESC
            """

            result = DataBaseHandle.getRecords(query, (centro_id,))

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

            HandleLogs.write_log(f"SesionPedagogicaComponent.get_sesiones_by_centro - {len(result) if result else 0} sesiones encontradas para centro {centro_id}")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.get_sesiones_by_centro - Error: {str(e)}")
            raise Exception(f"Error al obtener sesiones del centro: {str(e)}")

    @staticmethod
    def get_sesiones_by_pedagogo(pedagogo_id, centro_id=None):
        """Obtener sesiones pedagógicas de un pedagogo específico, opcionalmente filtradas por centro"""
        try:
            # Base query
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
                    COALESCE(sp.numero_clases_programadas, 20) as numero_clases_programadas,
                    sp.nivel_academico,
                    sp.capacidad_maxima,
                    'presencial' as modalidad,
                    0 as costo_total,
                    0 as costo_por_clase,
                    '' as periodo_academico,
                    sp.estado,
                    '' as observaciones,
                    sp.fecha_creacion,
                    sp.fecha_modificacion,
                    sp.id_centro,
                    -- Estadísticas básicas
                    COALESCE(COUNT(DISTINCT se.id_paciente), 0) as total_estudiantes,
                    COALESCE(COUNT(DISTINCT cc.id), 0) as clases_programadas,
                    COALESCE(COUNT(DISTINCT CASE WHEN cc.estado = 'realizada' THEN cc.id END), 0) as clases_realizadas,
                    0 as promedio_notas,
                    0 as promedio_asistencia
                FROM sesion_pedagogica sp
                JOIN personal per ON sp.id_educador = per.id
                JOIN persona p_ped ON per.id_persona = p_ped.id
                JOIN especialidad e ON sp.id_especialidad = e.id
                LEFT JOIN sesion_estudiante se ON sp.id = se.id_sesion AND se.estado = 'activo'
                LEFT JOIN cronograma_clases cc ON sp.id = cc.id_sesion
                WHERE sp.id_educador = %s
            """

            params = [pedagogo_id]

            # Add center filter if provided
            if centro_id:
                query += " AND sp.id_centro = %s"
                params.append(centro_id)

            query += """
                GROUP BY sp.id, sp.codigo_sesion, sp.nombre_clase, sp.id_educador, sp.id_especialidad,
                         sp.fecha_inicio, sp.fecha_fin, sp.dias_semana, sp.hora_inicio, sp.duracion_minutos,
                         sp.nivel_academico, sp.capacidad_maxima, sp.estado, sp.fecha_creacion, sp.fecha_modificacion,
                         sp.id_centro, p_ped.nombre, p_ped.apellido, e.nombre, e.area
                ORDER BY sp.fecha_creacion DESC
            """

            result = DataBaseHandle.getRecords(query, tuple(params))

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

            centro_str = f" en centro {centro_id}" if centro_id else ""
            HandleLogs.write_log(f"SesionPedagogicaComponent.get_sesiones_by_pedagogo - {len(result) if result else 0} sesiones encontradas para pedagogo {pedagogo_id}{centro_str}")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.get_sesiones_by_pedagogo - Error: {str(e)}")
            raise Exception(f"Error al obtener sesiones del pedagogo: {str(e)}")

    # ============================================
    # MÉTODOS DE ENLACES PÚBLICOS PEDAGÓGICOS
    # ============================================

    @staticmethod
    def generar_token_publico(enlace_data):
        """Generar un token público para una sesión pedagógica"""
        try:
            import secrets
            from datetime import datetime, timedelta

            # Generar token único - 48 bytes = ~64 caracteres en base64url
            token = secrets.token_urlsafe(48)

            # Calcular fecha de expiración
            fecha_expiracion = datetime.now() + timedelta(hours=enlace_data['duracion_horas'])

            # Insertar en la base de datos - estructura real sin nombre_enlace ni estado
            insert_query = """
                INSERT INTO tokens_publicos_sesion_pedagogica
                (token, id_sesion, descripcion, fecha_expiracion, usuario_creacion)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (
                token,
                enlace_data['sesion_id'],
                enlace_data['descripcion'],
                fecha_expiracion,
                enlace_data['usuario_creacion']
            )

            rows_affected = DataBaseHandle.ExecuteNonQuery(insert_query, params)
            HandleLogs.write_log(f"SesionPedagogicaComponent.generar_token_publico - rows_affected: {rows_affected}")

            # En algunos casos ExecuteNonQuery puede devolver None aunque la inserción sea exitosa
            # Vamos a verificar si el token se insertó correctamente
            verify_query = """
                SELECT COUNT(*) as count FROM tokens_publicos_sesion_pedagogica WHERE token = %s
            """
            verify_result = DataBaseHandle.getRecords(verify_query, (token,))
            token_exists = verify_result and verify_result[0]['count'] > 0

            HandleLogs.write_log(f"SesionPedagogicaComponent.generar_token_publico - Token exists: {token_exists}")

            if token_exists:
                # Obtener los datos del token creado - usando estructura real
                select_query = """
                    SELECT token, descripcion, fecha_expiracion, activo
                    FROM tokens_publicos_sesion_pedagogica
                    WHERE token = %s
                """
                result = DataBaseHandle.getRecords(select_query, (token,))

                if result:
                    token_data = result[0]
                    nombre_enlace = f"Enlace-{enlace_data['sesion_id']}-{datetime.now().strftime('%Y%m%d')}"
                    response_data = {
                        'token': token_data['token'],
                        'nombre_enlace': nombre_enlace,
                        'descripcion': token_data['descripcion'],
                        'duracion_horas': enlace_data['duracion_horas'],
                        'fecha_expiracion': token_data['fecha_expiracion'].isoformat() if isinstance(token_data['fecha_expiracion'], datetime) else str(token_data['fecha_expiracion']),
                        'estado': 'activo' if token_data['activo'] else 'inactivo',
                        'url_publica': f"/api/sesion-pedagogica-publica/{token_data['token']}"
                    }

                    HandleLogs.write_log(f"SesionPedagogicaComponent.generar_token_publico - Token generado para sesión {enlace_data['sesion_id']}")
                    return response_data
                else:
                    raise Exception("No se pudo obtener el token generado")
            else:
                raise Exception("No se pudo insertar el token en la base de datos")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.generar_token_publico - Error: {str(e)}")
            raise Exception(f"Error al generar token público: {str(e)}")

    @staticmethod
    def obtener_tokens_publicos(sesion_id):
        """Obtener tokens públicos activos para una sesión pedagógica"""
        try:
            query = """
                SELECT
                    token,
                    descripcion,
                    fecha_creacion,
                    fecha_expiracion,
                    activo,
                    CASE
                        WHEN fecha_expiracion < CURRENT_TIMESTAMP THEN 'expirado'
                        WHEN activo = false THEN 'inactivo'
                        ELSE 'vigente'
                    END as estado_calculado
                FROM tokens_publicos_sesion_pedagogica
                WHERE id_sesion = %s AND activo = true
                ORDER BY fecha_creacion DESC
            """
            params = (sesion_id,)

            result = DataBaseHandle.getRecords(query, params)
            if result:
                # Formatear datos para la respuesta
                tokens_formateados = []
                for idx, token in enumerate(result):
                    nombre_enlace = f"Enlace-{sesion_id}-{idx+1}"
                    token_data = {
                        'token': token['token'],
                        'nombre_enlace': nombre_enlace,
                        'descripcion': token['descripcion'],
                        'fecha_creacion': token['fecha_creacion'].isoformat() if isinstance(token['fecha_creacion'], datetime) else str(token['fecha_creacion']),
                        'fecha_expiracion': token['fecha_expiracion'].isoformat() if isinstance(token['fecha_expiracion'], datetime) else str(token['fecha_expiracion']),
                        'estado': 'activo' if token['activo'] else 'inactivo',
                        'estado_calculado': token['estado_calculado'],
                        'url_publica': f"/api/sesion-pedagogica-publica/{token['token']}"
                    }
                    tokens_formateados.append(token_data)

                HandleLogs.write_log(f"SesionPedagogicaComponent.obtener_tokens_publicos - {len(tokens_formateados)} tokens encontrados para sesión {sesion_id}")
                return tokens_formateados
            else:
                HandleLogs.write_log(f"SesionPedagogicaComponent.obtener_tokens_publicos - No se encontraron tokens para sesión {sesion_id}")
                return []

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.obtener_tokens_publicos - Error: {str(e)}")
            return []  # Retornar lista vacía en lugar de lanzar excepción

    @staticmethod
    def invalidar_token_publico(token, usuario_modificacion):
        """Invalidar un token público específico"""
        try:
            # Primero verificar que el token existe y está activo
            check_query = """
                SELECT id, token
                FROM tokens_publicos_sesion_pedagogica
                WHERE token = %s AND activo = true
            """
            existing_token = DataBaseHandle.getRecords(check_query, (token,))

            if not existing_token:
                HandleLogs.write_log(f"SesionPedagogicaComponent.invalidar_token_publico - Token no encontrado o ya inactivo: {token[:10]}...")
                raise Exception("Token no encontrado o ya está inactivo")

            # Usar ExecuteNonQuery para el UPDATE (patrón correcto del proyecto)
            update_query = """
                UPDATE tokens_publicos_sesion_pedagogica
                SET activo = false,
                    usuario_modificacion = %s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE token = %s AND activo = true
            """
            params = (usuario_modificacion, token)

            rows_affected = DataBaseHandle.ExecuteNonQuery(update_query, params)
            if rows_affected and rows_affected > 0:
                HandleLogs.write_log(f"SesionPedagogicaComponent.invalidar_token_publico - Token invalidado: {token[:10]}...")
                return {'success': True, 'message': 'Token invalidado exitosamente'}
            else:
                HandleLogs.write_log(f"SesionPedagogicaComponent.invalidar_token_publico - No se pudo invalidar el token: {token[:10]}...")
                raise Exception("No se pudo invalidar el token")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.invalidar_token_publico - Error: {str(e)}")
            raise Exception(f"Error al invalidar token: {str(e)}")

    @staticmethod
    def obtener_sesion_por_token_publico(token):
        """Obtener información pública de una sesión pedagógica usando un token válido"""
        try:
            # Verificar token y obtener información de la sesión
            query = """
                SELECT
                    sp.id as sesion_id,
                    sp.codigo_sesion,
                    sp.nombre_clase as titulo,
                    sp.competencias_objetivo as objetivo_general,
                    CONCAT(p_ped.nombre, ' ', p_ped.apellido) as pedagogo_nombre,
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area,
                    sp.fecha_inicio,
                    sp.fecha_fin,
                    sp.dias_semana,
                    sp.hora_inicio,
                    sp.hora_fin,
                    sp.duracion_minutos,
                    'grupal' as tipo_sesion,
                    sp.estado,
                    tps.descripcion as enlace_descripcion,
                    tps.fecha_expiracion,
                    COUNT(DISTINCT se.id_paciente) as total_estudiantes,
                    COUNT(DISTINCT cc.id) as clases_programadas,
                    COUNT(DISTINCT CASE WHEN ac.asistio = true THEN ac.id_cronograma END) as clases_realizadas,
                    ROUND(
                        (COUNT(DISTINCT CASE WHEN ac.asistio = true THEN ac.id_cronograma END) * 100.0) /
                        NULLIF(COUNT(DISTINCT cc.id), 0), 2
                    ) as porcentaje_asistencia
                FROM tokens_publicos_sesion_pedagogica tps
                JOIN sesion_pedagogica sp ON tps.id_sesion = sp.id
                JOIN personal per ON sp.id_educador = per.id
                JOIN persona p_ped ON per.id_persona = p_ped.id
                JOIN especialidad e ON sp.id_especialidad = e.id
                LEFT JOIN sesion_estudiante se ON sp.id = se.id_sesion AND se.estado = 'activo'
                LEFT JOIN cronograma_clases cc ON sp.id = cc.id_sesion
                LEFT JOIN asistencia_clases ac ON cc.id = ac.id_cronograma
                WHERE tps.token = %s
                    AND tps.activo = true
                    AND tps.fecha_expiracion > CURRENT_TIMESTAMP
                GROUP BY sp.id, sp.codigo_sesion, sp.nombre_clase, sp.competencias_objetivo,
                        p_ped.nombre, p_ped.apellido, e.nombre, e.area, sp.fecha_inicio,
                        sp.fecha_fin, sp.dias_semana, sp.hora_inicio, sp.hora_fin,
                        sp.duracion_minutos, sp.estado, tps.descripcion, tps.fecha_expiracion
            """
            params = (token,)

            result = DataBaseHandle.getRecords(query, params)
            if result:
                sesion_data = result[0]

                # Obtener cronograma de clases (información pública)
                cronograma_query = """
                    SELECT
                        cc.fecha_programada,
                        cc.hora_inicio,
                        cc.hora_fin,
                        cc.estado,
                        cc.semana_numero,
                        cc.numero_clase_semanal,
                        CASE
                            WHEN EXISTS (
                                SELECT 1 FROM asistencia_clases ac
                                WHERE ac.id_cronograma = cc.id AND ac.asistio = true
                            ) THEN 'realizada'
                            ELSE 'pendiente'
                        END as estado_asistencia
                    FROM cronograma_clases cc
                    WHERE cc.id_sesion = %s
                    ORDER BY cc.fecha_programada ASC, cc.hora_inicio ASC
                """
                cronograma_result = DataBaseHandle.getRecords(cronograma_query, (sesion_data['sesion_id'],))

                # Formatear cronograma
                cronograma = []
                if cronograma_result:
                    for row in cronograma_result:
                        clase = {
                            'fecha': row['fecha_programada'].isoformat() if isinstance(row['fecha_programada'], (date, datetime)) else str(row['fecha_programada']),
                            'hora_inicio': str(row['hora_inicio']) if row['hora_inicio'] else None,
                            'hora_fin': str(row['hora_fin']) if row['hora_fin'] else None,
                            'estado': row['estado'],
                            'estado_asistencia': row['estado_asistencia'],
                            'semana': row['semana_numero'],
                            'clase_semanal': row['numero_clase_semanal']
                        }
                        cronograma.append(clase)

                # Formatear respuesta pública (sin información sensible)
                response_data = {
                    'sesion': {
                        'titulo': sesion_data['titulo'],
                        'objetivo_general': sesion_data['objetivo_general'],
                        'pedagogo': sesion_data['pedagogo_nombre'],
                        'especialidad': {
                            'nombre': sesion_data['especialidad_nombre'],
                            'area': sesion_data['especialidad_area']
                        },
                        'periodo': {
                            'inicio': sesion_data['fecha_inicio'].isoformat() if isinstance(sesion_data['fecha_inicio'], (date, datetime)) else str(sesion_data['fecha_inicio']),
                            'fin': sesion_data['fecha_fin'].isoformat() if isinstance(sesion_data['fecha_fin'], (date, datetime)) else str(sesion_data['fecha_fin'])
                        },
                        'horario': {
                            'dias': sesion_data['dias_semana'],
                            'hora_inicio': str(sesion_data['hora_inicio']) if sesion_data['hora_inicio'] else None,
                            'hora_fin': str(sesion_data['hora_fin']) if sesion_data['hora_fin'] else None,
                            'duracion_minutos': sesion_data['duracion_minutos']
                        },
                        'tipo': sesion_data['tipo_sesion'],
                        'estado': sesion_data['estado']
                    },
                    'estadisticas': {
                        'total_estudiantes': int(sesion_data['total_estudiantes']) if sesion_data['total_estudiantes'] else 0,
                        'clases_programadas': int(sesion_data['clases_programadas']) if sesion_data['clases_programadas'] else 0,
                        'clases_realizadas': int(sesion_data['clases_realizadas']) if sesion_data['clases_realizadas'] else 0,
                        'porcentaje_asistencia': float(sesion_data['porcentaje_asistencia']) if sesion_data['porcentaje_asistencia'] else 0
                    },
                    'cronograma': cronograma,
                    'enlace_info': {
                        'descripcion': sesion_data['enlace_descripcion'],
                        'fecha_expiracion': sesion_data['fecha_expiracion'].isoformat() if isinstance(sesion_data['fecha_expiracion'], datetime) else str(sesion_data['fecha_expiracion'])
                    }
                }

                HandleLogs.write_log(f"SesionPedagogicaComponent.obtener_sesion_por_token_publico - Información obtenida para sesión {sesion_data['sesion_id']}")
                return response_data
            else:
                HandleLogs.write_log(f"SesionPedagogicaComponent.obtener_sesion_por_token_publico - Token inválido o expirado: {token[:10]}...")
                return None

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaComponent.obtener_sesion_por_token_publico - Error: {str(e)}")
            raise Exception(f"Error al obtener sesión por token: {str(e)}")