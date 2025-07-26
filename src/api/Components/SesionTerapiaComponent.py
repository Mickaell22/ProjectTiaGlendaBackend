# src/api/Components/SesionTerapiaComponent.py

from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from datetime import datetime, date, time
import json


class SesionTerapiaComponent:
    """Component para manejo de sesiones de terapia en la base de datos"""

    @staticmethod
    def get_sesiones():
        """Obtener todas las sesiones de terapia con información completa"""
        try:
            query = """
                SELECT 
                    st.id,
                    st.codigo_sesion,
                    st.titulo,
                    st.terapeuta_id,
                    CONCAT(p_ter.nombre, ' ', p_ter.apellido) as terapeuta_nombre,
                    st.especialidad_id,
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area,
                    st.fecha_inicio,
                    st.fecha_fin,
                    st.dias_semana,
                    st.hora_inicio,
                    st.duracion_minutos,
                    st.numero_sesiones_contratadas,
                    st.costo_total,
                    st.costo_por_sesion,
                    st.meses_contrato,
                    st.estado,
                    st.observaciones,
                    st.fecha_creacion,
                    st.fecha_modificacion,
                    COUNT(sp.paciente_id) as total_pacientes,
                    COUNT(cs.id) as sesiones_programadas,
                    COUNT(CASE WHEN cs.estado = 'realizada' THEN 1 END) as sesiones_realizadas
                FROM sesion_terapia st
                JOIN personal per ON st.terapeuta_id = per.id
                JOIN persona p_ter ON per.persona_id = p_ter.id
                JOIN especialidad e ON st.especialidad_id = e.id
                LEFT JOIN sesion_paciente sp ON st.id = sp.sesion_terapia_id AND sp.estado = 'activo'
                LEFT JOIN cronograma_sesiones cs ON st.id = cs.sesion_terapia_id
                GROUP BY st.id, p_ter.nombre, p_ter.apellido, e.nombre, e.area
                ORDER BY st.fecha_creacion DESC
            """

            result = DataBaseHandle.getRecords(query)
            HandleLogs.write_log("SesionTerapiaComponent.get_sesiones - Sesiones obtenidas exitosamente")
            return result
        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_sesiones - Error: {str(e)}")
            raise Exception(f"Error al obtener sesiones: {str(e)}")

    @staticmethod
    def get_sesion_by_id(sesion_id):
        """Obtener una sesión específica por ID con toda su información"""
        try:
            query = """
                SELECT 
                    st.*,
                    CONCAT(p_ter.nombre, ' ', p_ter.apellido) as terapeuta_nombre,
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area
                FROM sesion_terapia st
                JOIN personal per ON st.terapeuta_id = per.id
                JOIN persona p_ter ON per.persona_id = p_ter.id
                JOIN especialidad e ON st.especialidad_id = e.id
                WHERE st.id = %s
            """

            params = (sesion_id,)
            result = DataBaseHandle.getRecords(query, params, size=1)

            if result:
                HandleLogs.write_log(f"SesionTerapiaComponent.get_sesion_by_id - Sesión {sesion_id} encontrada")
                return result
            else:
                HandleLogs.write_log(f"SesionTerapiaComponent.get_sesion_by_id - Sesión {sesion_id} no encontrada")
                return None

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_sesion_by_id - Error: {str(e)}")
            raise Exception(f"Error al obtener sesión: {str(e)}")

    @staticmethod
    def create_sesion(sesion_data):
        """Crear una nueva sesión de terapia"""
        try:
            # Insertar con codigo_sesion NULL para que el trigger lo genere automáticamente
            query = """
                INSERT INTO sesion_terapia (
                    codigo_sesion, titulo, terapeuta_id, especialidad_id, fecha_inicio, fecha_fin,
                    dias_semana, hora_inicio, duracion_minutos, numero_sesiones_contratadas,
                    costo_total, meses_contrato, estado, observaciones, usuario_creacion
                ) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, codigo_sesion
            """

            params = (
                sesion_data['titulo'],
                sesion_data['terapeuta_id'],
                sesion_data['especialidad_id'],
                sesion_data['fecha_inicio'],
                sesion_data['fecha_fin'],
                sesion_data['dias_semana'],
                sesion_data['hora_inicio'],
                sesion_data.get('duracion_minutos', 45),
                sesion_data['numero_sesiones_contratadas'],
                sesion_data['costo_total'],
                sesion_data.get('meses_contrato'),
                sesion_data.get('estado', 'activo'),
                sesion_data.get('observaciones'),
                sesion_data['usuario_creacion']
            )

            # Usar ExecuteNonQuery para el INSERT y luego buscar la sesión creada
            insert_query = query.replace("RETURNING id, codigo_sesion", "")
            
            # Ejecutar el INSERT
            result = DataBaseHandle.ExecuteNonQuery(insert_query, params)
            
            if result:
                # Buscar la sesión recién creada por titulo y terapeuta_id (campos únicos para buscar)
                select_query = """
                    SELECT id, codigo_sesion 
                    FROM sesion_terapia 
                    WHERE titulo = %s AND terapeuta_id = %s 
                    ORDER BY fecha_creacion DESC 
                    LIMIT 1
                """
                select_params = (sesion_data['titulo'], sesion_data['terapeuta_id'])
                result = DataBaseHandle.getRecords(select_query, select_params, size=1)
                
                if result:
                    sesion_id = result['id']
                    codigo_sesion = result.get('codigo_sesion', f"ST-TEMP-{sesion_id}")
                    HandleLogs.write_log(f"SesionTerapiaComponent.create_sesion - Sesión creada con ID: {sesion_id}, Código: {codigo_sesion}")
                    
                    # Generar cronograma automáticamente
                    try:
                        SesionTerapiaComponent.generar_cronograma(sesion_id)
                        HandleLogs.write_log(f"SesionTerapiaComponent.create_sesion - Cronograma generado para sesión {sesion_id}")
                    except Exception as cronograma_error:
                        HandleLogs.write_error(f"SesionTerapiaComponent.create_sesion - Error generando cronograma: {str(cronograma_error)}")
                        # No fallar el método completo si falla el cronograma
                    
                    return {
                        'id': sesion_id,
                        'codigo_sesion': codigo_sesion
                    }
                else:
                    raise Exception("No se pudo recuperar la sesión creada")
            else:
                HandleLogs.write_error("SesionTerapiaComponent.create_sesion - ExecuteNonQuery falló")
                raise Exception("No se pudo crear la sesión")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.create_sesion - Error: {str(e)}")
            raise Exception(f"Error al crear sesión: {str(e)}")

    @staticmethod
    def update_sesion(sesion_id, sesion_data):
        """Actualizar una sesión de terapia"""
        try:
            query = """
                UPDATE sesion_terapia SET
                    titulo = %s, terapeuta_id = %s, especialidad_id = %s,
                    fecha_inicio = %s, fecha_fin = %s, dias_semana = %s,
                    hora_inicio = %s, duracion_minutos = %s, numero_sesiones_contratadas = %s,
                    costo_total = %s, meses_contrato = %s, estado = %s,
                    observaciones = %s, usuario_modificacion = %s
                WHERE id = %s
            """

            params = (
                sesion_data['titulo'],
                sesion_data['terapeuta_id'],
                sesion_data['especialidad_id'],
                sesion_data['fecha_inicio'],
                sesion_data['fecha_fin'],
                sesion_data['dias_semana'],
                sesion_data['hora_inicio'],
                sesion_data.get('duracion_minutos', 45),
                sesion_data['numero_sesiones_contratadas'],
                sesion_data['costo_total'],
                sesion_data.get('meses_contrato'),
                sesion_data.get('estado', 'activo'),
                sesion_data.get('observaciones'),
                sesion_data['usuario_modificacion'],
                sesion_id
            )

            DataBaseHandle.ExecuteNonQuery(query, params)
            HandleLogs.write_log(f"SesionTerapiaComponent.update_sesion - Sesión {sesion_id} actualizada")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.update_sesion - Error: {str(e)}")
            raise Exception(f"Error al actualizar sesión: {str(e)}")

    @staticmethod
    def delete_sesion(sesion_id):
        """Eliminar una sesión de terapia (eliminación lógica)"""
        try:
            query = "UPDATE sesion_terapia SET estado = 'cancelado' WHERE id = %s"
            params = (sesion_id,)

            DataBaseHandle.ExecuteNonQuery(query, params)
            HandleLogs.write_log(f"SesionTerapiaComponent.delete_sesion - Sesión {sesion_id} cancelada")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.delete_sesion - Error: {str(e)}")
            raise Exception(f"Error al cancelar sesión: {str(e)}")

    @staticmethod
    def generar_cronograma(sesion_id):
        """Generar cronograma automático para una sesión"""
        try:
            # Primero obtener la información de la sesión
            sesion_query = """
                SELECT fecha_inicio, fecha_fin, dias_semana, hora_inicio, numero_sesiones_contratadas
                FROM sesion_terapia 
                WHERE id = %s
            """
            sesion_data = DataBaseHandle.getRecords(sesion_query, (sesion_id,), size=1)
            
            if not sesion_data:
                raise Exception(f"Sesión {sesion_id} no encontrada")
            
            # Limpiar cronograma existente
            delete_query = "DELETE FROM cronograma_sesiones WHERE sesion_terapia_id = %s"
            DataBaseHandle.ExecuteNonQuery(delete_query, (sesion_id,))
            
            # Generar cronograma programáticamente
            from datetime import datetime, timedelta
            
            fecha_inicio = sesion_data['fecha_inicio']
            fecha_fin = sesion_data['fecha_fin']
            dias_semana = sesion_data['dias_semana'].split(',') if sesion_data['dias_semana'] else []
            hora_inicio = sesion_data['hora_inicio']
            max_sesiones = sesion_data['numero_sesiones_contratadas']
            
            # Mapeo de días
            dias_map = {
                'lunes': 0, 'martes': 1, 'miercoles': 2, 'jueves': 3, 
                'viernes': 4, 'sabado': 5, 'domingo': 6
            }
            
            dias_numeros = [dias_map.get(dia.strip().lower(), -1) for dia in dias_semana if dia.strip().lower() in dias_map]
            
            fecha_actual = fecha_inicio
            numero_sesion = 1
            sesiones_creadas = 0
            
            while fecha_actual <= fecha_fin and sesiones_creadas < max_sesiones:
                dia_semana = fecha_actual.weekday()  # 0=lunes, 6=domingo
                
                if dia_semana in dias_numeros:
                    # Insertar sesión en cronograma
                    insert_query = """
                        INSERT INTO cronograma_sesiones (
                            sesion_terapia_id, numero_sesion, fecha_programada, 
                            hora_programada, estado, usuario_creacion
                        ) VALUES (%s, %s, %s, %s, 'programada', 1)
                    """
                    params = (sesion_id, numero_sesion, fecha_actual, hora_inicio)
                    DataBaseHandle.ExecuteNonQuery(insert_query, params)
                    
                    numero_sesion += 1
                    sesiones_creadas += 1
                
                fecha_actual += timedelta(days=1)
            
            HandleLogs.write_log(
                f"SesionTerapiaComponent.generar_cronograma - {sesiones_creadas} sesiones programadas para sesión {sesion_id}")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.generar_cronograma - Error: {str(e)}")
            raise Exception(f"Error al generar cronograma: {str(e)}")

    # ============================================
    # MÉTODOS PARA SESION_PACIENTE
    # ============================================

    @staticmethod
    def get_pacientes_sesion(sesion_id):
        """Obtener todos los pacientes asignados a una sesión"""
        try:
            query = """
                SELECT
                    sp.id,
                    sp.paciente_id,
                    CONCAT(p.nombre, ' ', p.apellido) as paciente_nombre,
                    p.cedula as paciente_cedula,
                    sp.fecha_incorporacion,
                    sp.costo_paciente,
                    sp.observaciones_paciente,
                    sp.estado,
                    CONCAT(p_tutor.nombre, ' ', p_tutor.apellido) as tutor_nombre,
                    p_tutor.telefono as tutor_telefono
                FROM sesion_paciente sp
                JOIN paciente pac ON sp.paciente_id = pac.id
                JOIN persona p ON pac.persona_id = p.id
                JOIN tutor t ON pac.tutor_id = t.id
                JOIN persona p_tutor ON t.persona_id = p_tutor.id
                WHERE sp.sesion_terapia_id = %s
                ORDER BY sp.fecha_incorporacion
            """

            params = (sesion_id,)
            result = DataBaseHandle.getRecords(query, params)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.get_pacientes_sesion - {len(result) if result else 0} pacientes encontrados")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_pacientes_sesion - Error: {str(e)}")
            raise Exception(f"Error al obtener pacientes de la sesión: {str(e)}")

    @staticmethod
    def add_paciente_to_sesion(sesion_id, paciente_data):
        """Agregar un paciente a una sesión"""
        try:
            query = """
                INSERT INTO sesion_paciente (
                    sesion_terapia_id, paciente_id, fecha_incorporacion,
                    costo_paciente, observaciones_paciente, estado, usuario_creacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            params = (
                sesion_id,
                paciente_data['paciente_id'],
                paciente_data.get('fecha_incorporacion', datetime.now().date()),
                paciente_data.get('costo_paciente'),
                paciente_data.get('observaciones_paciente'),
                paciente_data.get('estado', 'activo'),
                paciente_data['usuario_creacion']
            )

            result = DataBaseHandle.getRecords(query, params, size=1)
            if result:
                HandleLogs.write_log(
                    f"SesionTerapiaComponent.add_paciente_to_sesion - Paciente {paciente_data['paciente_id']} agregado a sesión {sesion_id}")
                return result
            else:
                raise Exception("No se pudo agregar el paciente a la sesión")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.add_paciente_to_sesion - Error: {str(e)}")
            raise Exception(f"Error al agregar paciente a la sesión: {str(e)}")

    @staticmethod
    def remove_paciente_from_sesion(sesion_id, paciente_id):
        """Remover un paciente de una sesión (cambiar estado a retirado)"""
        try:
            query = """
                UPDATE sesion_paciente 
                SET estado = 'retirado' 
                WHERE sesion_terapia_id = %s AND paciente_id = %s
            """
            params = (sesion_id, paciente_id)

            DataBaseHandle.ExecuteNonQuery(query, params)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.remove_paciente_from_sesion - Paciente {paciente_id} retirado de sesión {sesion_id}")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.remove_paciente_from_sesion - Error: {str(e)}")
            raise Exception(f"Error al retirar paciente de la sesión: {str(e)}")

    # ============================================
    # MÉTODOS PARA CRONOGRAMA_SESIONES
    # ============================================

    @staticmethod
    def get_cronograma_sesion(sesion_id):
        """Obtener el cronograma completo de una sesión"""
        try:
            query = """
                SELECT 
                    cs.*,
                    CASE 
                        WHEN cs.fecha_programada < CURRENT_DATE THEN 'vencida'
                        WHEN cs.fecha_programada = CURRENT_DATE THEN 'hoy'
                        ELSE cs.estado
                    END as estado_actual
                FROM cronograma_sesiones cs
                WHERE cs.sesion_terapia_id = %s
                ORDER BY cs.numero_sesion
            """

            params = (sesion_id,)
            result = DataBaseHandle.getRecords(query, params)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.get_cronograma_sesion - {len(result) if result else 0} sesiones programadas")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_cronograma_sesion - Error: {str(e)}")
            raise Exception(f"Error al obtener cronograma: {str(e)}")

    @staticmethod
    def marcar_sesion_realizada(cronograma_id, observaciones=None):
        """Marcar una sesión como realizada"""
        try:
            query = """
                UPDATE cronograma_sesiones 
                SET estado = 'realizada', 
                    fecha_realizacion = CURRENT_TIMESTAMP,
                    observaciones_cronograma = %s
                WHERE id = %s
            """
            params = (observaciones, cronograma_id)

            DataBaseHandle.ExecuteNonQuery(query, params)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.marcar_sesion_realizada - Sesión {cronograma_id} marcada como realizada")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.marcar_sesion_realizada - Error: {str(e)}")
            raise Exception(f"Error al marcar sesión como realizada: {str(e)}")

    @staticmethod
    def reprogramar_sesion(cronograma_id, nueva_fecha, nueva_hora, motivo):
        """Reprogramar una sesión específica"""
        try:
            # Primero obtener los datos de la sesión original
            query_original = "SELECT * FROM cronograma_sesiones WHERE id = %s"
            sesion_original = DataBaseHandle.getRecords(query_original, (cronograma_id,), size=1)

            if not sesion_original:
                raise Exception("Sesión original no encontrada")

            # Marcar la sesión original como reprogramada
            query_update = """
                UPDATE cronograma_sesiones 
                SET estado = 'reprogramada' 
                WHERE id = %s
            """
            DataBaseHandle.ExecuteNonQuery(query_update, (cronograma_id,))

            # Crear nueva sesión programada
            query_nueva = """
                INSERT INTO cronograma_sesiones (
                    sesion_terapia_id, numero_sesion, fecha_programada, hora_programada,
                    estado, sesion_original_id, motivo_reprogramacion, usuario_creacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            params_nueva = (
                sesion_original['sesion_terapia_id'],
                sesion_original['numero_sesion'],
                nueva_fecha,
                nueva_hora,
                'programada',
                cronograma_id,
                motivo,
                sesion_original['usuario_creacion']
            )

            result = DataBaseHandle.getRecords(query_nueva, params_nueva, size=1)
            HandleLogs.write_log(f"SesionTerapiaComponent.reprogramar_sesion - Sesión {cronograma_id} reprogramada")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.reprogramar_sesion - Error: {str(e)}")
            raise Exception(f"Error al reprogramar sesión: {str(e)}")

    # ============================================
    # MÉTODOS PARA ASISTENCIA_SESIONES
    # ============================================

    @staticmethod
    def registrar_asistencia(cronograma_id, paciente_id, asistencia_data):
        """Registrar la asistencia de un paciente a una sesión"""
        try:
            query = """
                INSERT INTO asistencia_sesiones (
                    cronograma_sesion_id, paciente_id, asistio, llegada_tardanza_minutos,
                    observaciones_asistencia, notas_progreso, tareas_asignadas,
                    proximos_objetivos, usuario_creacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cronograma_sesion_id, paciente_id) 
                DO UPDATE SET
                    asistio = EXCLUDED.asistio,
                    llegada_tardanza_minutos = EXCLUDED.llegada_tardanza_minutos,
                    observaciones_asistencia = EXCLUDED.observaciones_asistencia,
                    notas_progreso = EXCLUDED.notas_progreso,
                    tareas_asignadas = EXCLUDED.tareas_asignadas,
                    proximos_objetivos = EXCLUDED.proximos_objetivos,
                    usuario_modificacion = EXCLUDED.usuario_creacion
                RETURNING id
            """

            params = (
                cronograma_id,
                paciente_id,
                asistencia_data.get('asistio', False),
                asistencia_data.get('llegada_tardanza_minutos', 0),
                asistencia_data.get('observaciones_asistencia'),
                asistencia_data.get('notas_progreso'),
                asistencia_data.get('tareas_asignadas'),
                asistencia_data.get('proximos_objetivos'),
                asistencia_data['usuario_creacion']
            )

            result = DataBaseHandle.getRecords(query, params, size=1)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.registrar_asistencia - Asistencia registrada para paciente {paciente_id}")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.registrar_asistencia - Error: {str(e)}")
            raise Exception(f"Error al registrar asistencia: {str(e)}")

    @staticmethod
    def get_asistencias_sesion(cronograma_id):
        """Obtener todas las asistencias registradas para una sesión"""
        try:
            query = """
                SELECT 
                    a.*,
                    CONCAT(p.nombre, ' ', p.apellido) as paciente_nombre,
                    p.cedula as paciente_cedula
                FROM asistencia_sesiones a
                JOIN paciente pac ON a.paciente_id = pac.id
                JOIN persona p ON pac.persona_id = p.id
                WHERE a.cronograma_sesion_id = %s
                ORDER BY p.nombre, p.apellido
            """

            params = (cronograma_id,)
            result = DataBaseHandle.getRecords(query, params)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.get_asistencias_sesion - {len(result) if result else 0} asistencias encontradas")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_asistencias_sesion - Error: {str(e)}")
            raise Exception(f"Error al obtener asistencias: {str(e)}")

    # ============================================
    # MÉTODOS DE CONSULTA Y ESTADÍSTICAS
    # ============================================

    @staticmethod
    def get_sesiones_by_terapeuta(terapeuta_id):
        """Obtener sesiones de un terapeuta específico"""
        try:
            query = """
                SELECT 
                    st.*,
                    e.nombre as especialidad_nombre,
                    COUNT(sp.paciente_id) as total_pacientes
                FROM sesion_terapia st
                JOIN especialidad e ON st.especialidad_id = e.id
                LEFT JOIN sesion_paciente sp ON st.id = sp.sesion_terapia_id AND sp.estado = 'activo'
                WHERE st.terapeuta_id = %s AND st.estado != 'cancelado'
                GROUP BY st.id, e.nombre
                ORDER BY st.fecha_inicio DESC
            """

            params = (terapeuta_id,)
            result = DataBaseHandle.getRecords(query, params)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.get_sesiones_by_terapeuta - {len(result) if result else 0} sesiones encontradas")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_sesiones_by_terapeuta - Error: {str(e)}")
            raise Exception(f"Error al obtener sesiones del terapeuta: {str(e)}")

    @staticmethod
    def get_sesiones_activas_hoy():
        """Obtener sesiones programadas para hoy"""
        try:
            query = """
                SELECT 
                    cs.id as cronograma_id,
                    cs.numero_sesion,
                    cs.hora_programada,
                    st.titulo,
                    st.codigo_sesion,
                    CONCAT(p_ter.nombre, ' ', p_ter.apellido) as terapeuta_nombre,
                    e.nombre as especialidad_nombre,
                    COUNT(sp.paciente_id) as total_pacientes,
                    cs.estado
                FROM cronograma_sesiones cs
                JOIN sesion_terapia st ON cs.sesion_terapia_id = st.id
                JOIN personal per ON st.terapeuta_id = per.id
                JOIN persona p_ter ON per.persona_id = p_ter.id
                JOIN especialidad e ON st.especialidad_id = e.id
                LEFT JOIN sesion_paciente sp ON st.id = sp.sesion_terapia_id AND sp.estado = 'activo'
                WHERE cs.fecha_programada = CURRENT_DATE 
                    AND st.estado = 'activo'
                    AND cs.estado IN ('programada', 'realizada')
                GROUP BY cs.id, st.id, p_ter.nombre, p_ter.apellido, e.nombre
                ORDER BY cs.hora_programada
            """

            result = DataBaseHandle.getRecords(query)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.get_sesiones_activas_hoy - {len(result) if result else 0} sesiones hoy")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_sesiones_activas_hoy - Error: {str(e)}")
            raise Exception(f"Error al obtener sesiones de hoy: {str(e)}")

    @staticmethod
    def get_estadisticas_sesiones():
        """Obtener estadísticas generales de sesiones"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_sesiones,
                    COUNT(CASE WHEN estado = 'activo' THEN 1 END) as sesiones_activas,
                    COUNT(CASE WHEN estado = 'completado' THEN 1 END) as sesiones_completadas,
                    COUNT(CASE WHEN estado = 'suspendido' THEN 1 END) as sesiones_suspendidas,
                    COUNT(CASE WHEN estado = 'cancelado' THEN 1 END) as sesiones_canceladas,
                    COALESCE(SUM(numero_sesiones_contratadas), 0) as total_sesiones_contratadas,
                    COALESCE(SUM(costo_total), 0) as ingresos_totales,
                    COALESCE(AVG(duracion_minutos), 0) as duracion_promedio
                FROM sesion_terapia
            """

            result = DataBaseHandle.getRecords(query, size=1)

            # Estadísticas adicionales de cronograma
            query_cronograma = """
                SELECT 
                    COUNT(*) as total_sesiones_programadas,
                    COUNT(CASE WHEN estado = 'realizada' THEN 1 END) as sesiones_realizadas,
                    COUNT(CASE WHEN estado = 'programada' THEN 1 END) as sesiones_pendientes,
                    COUNT(CASE WHEN estado = 'cancelada' THEN 1 END) as sesiones_canceladas_cronograma,
                    COUNT(CASE WHEN estado = 'reprogramada' THEN 1 END) as sesiones_reprogramadas
                FROM cronograma_sesiones
            """

            cronograma_stats = DataBaseHandle.getRecords(query_cronograma, size=1)

            # Combinar estadísticas con valores por defecto para evitar None
            estadisticas_finales = {}

            if result:
                for key, value in result.items():
                    estadisticas_finales[key] = value if value is not None else 0

            if cronograma_stats:
                for key, value in cronograma_stats.items():
                    estadisticas_finales[key] = value if value is not None else 0

            # Si no hay datos, retornar estructura vacía
            if not estadisticas_finales:
                estadisticas_finales = {
                    'total_sesiones': 0,
                    'sesiones_activas': 0,
                    'sesiones_completadas': 0,
                    'sesiones_suspendidas': 0,
                    'sesiones_canceladas': 0,
                    'total_sesiones_contratadas': 0,
                    'ingresos_totales': 0,
                    'duracion_promedio': 0,
                    'total_sesiones_programadas': 0,
                    'sesiones_realizadas': 0,
                    'sesiones_pendientes': 0,
                    'sesiones_canceladas_cronograma': 0,
                    'sesiones_reprogramadas': 0
                }

            HandleLogs.write_log("SesionTerapiaComponent.get_estadisticas_sesiones - Estadísticas obtenidas")
            return estadisticas_finales

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_estadisticas_sesiones - Error: {str(e)}")
            raise Exception(f"Error al obtener estadísticas: {str(e)}")

    @staticmethod
    def get_pacientes_disponibles():
        """Obtener pacientes que pueden ser asignados a sesiones"""
        try:
            query = """
                SELECT 
                    pac.id,
                    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                    p.cedula,
                    p.fecha_nacimiento,
                    pac.fecha_ingreso,
                    CONCAT(p_tutor.nombre, ' ', p_tutor.apellido) as tutor_nombre,
                    p_tutor.telefono as tutor_telefono,
                    pac.estado
                FROM paciente pac
                JOIN persona p ON pac.persona_id = p.id
                JOIN tutor t ON pac.tutor_id = t.id
                JOIN persona p_tutor ON t.persona_id = p_tutor.id
                WHERE pac.estado = 'activo' AND p.estado = 'activo'
                ORDER BY p.nombre, p.apellido
            """

            result = DataBaseHandle.getRecords(query)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.get_pacientes_disponibles - {len(result) if result else 0} pacientes disponibles")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_pacientes_disponibles - Error: {str(e)}")
            raise Exception(f"Error al obtener pacientes disponibles: {str(e)}")

    @staticmethod
    def get_terapeutas_disponibles():
        """Obtener terapeutas que pueden ser asignados a sesiones"""
        try:
            query = """
                SELECT 
                    per.id,
                    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                    per.titulo_profesional,
                    COUNT(pe.especialidad_id) as total_especialidades,
                    STRING_AGG(e.nombre, ', ') as especialidades
                FROM personal per
                JOIN persona p ON per.persona_id = p.id
                LEFT JOIN personal_especialidad pe ON per.id = pe.personal_id
                LEFT JOIN especialidad e ON pe.especialidad_id = e.id
                WHERE per.estado = 'activo' AND p.estado = 'activo'
                GROUP BY per.id, p.nombre, p.apellido, per.titulo_profesional
                ORDER BY p.nombre, p.apellido
            """

            result = DataBaseHandle.getRecords(query)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.get_terapeutas_disponibles - {len(result) if result else 0} terapeutas disponibles")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_terapeutas_disponibles - Error: {str(e)}")
            raise Exception(f"Error al obtener terapeutas disponibles: {str(e)}")