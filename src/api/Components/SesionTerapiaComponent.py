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
                    COUNT(DISTINCT sp.paciente_id) as total_pacientes,
                    COUNT(DISTINCT cs.id) as sesiones_programadas,
                    COUNT(DISTINCT CASE WHEN ass.asistio = true THEN ass.cronograma_sesion_id END) as sesiones_realizadas
                FROM sesion_terapia st
                JOIN personal per ON st.terapeuta_id = per.id
                JOIN persona p_ter ON per.id_persona = p_ter.id
                JOIN especialidad e ON st.especialidad_id = e.id
                LEFT JOIN sesion_paciente sp ON st.id = sp.sesion_terapia_id AND sp.estado = 'activo'
                LEFT JOIN cronograma_sesiones cs ON st.id = cs.sesion_terapia_id
                LEFT JOIN asistencia_sesiones ass ON cs.id = ass.cronograma_sesion_id
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
                JOIN persona p_ter ON per.id_persona = p_ter.id
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
        """Generar cronograma automático para una sesión - VERSIÓN MEJORADA"""
        try:
            # Primero obtener la información de la sesión
            sesion_query = """
                SELECT fecha_inicio, fecha_fin, dias_semana, hora_inicio, numero_sesiones_contratadas, usuario_creacion
                FROM sesion_terapia 
                WHERE id = %s
            """
            sesion_data = DataBaseHandle.getRecords(sesion_query, (sesion_id,), size=1)
            
            if not sesion_data:
                raise Exception(f"Sesión {sesion_id} no encontrada")
            
            # Validar datos requeridos
            if not sesion_data['fecha_inicio']:
                raise Exception("La fecha de inicio es requerida")
            if not sesion_data['dias_semana']:
                raise Exception("Los días de la semana son requeridos")
            if not sesion_data['numero_sesiones_contratadas'] or sesion_data['numero_sesiones_contratadas'] <= 0:
                raise Exception("El número de sesiones contratadas debe ser mayor a 0")
            
            # Limpiar cronograma existente
            delete_query = "DELETE FROM cronograma_sesiones WHERE sesion_terapia_id = %s"
            DataBaseHandle.ExecuteNonQuery(delete_query, (sesion_id,))
            
            # Generar cronograma programáticamente
            from datetime import datetime, timedelta
            
            fecha_inicio = sesion_data['fecha_inicio']
            fecha_fin = sesion_data['fecha_fin']
            dias_semana_str = sesion_data['dias_semana'].strip()
            hora_inicio = sesion_data['hora_inicio']
            max_sesiones = sesion_data['numero_sesiones_contratadas']
            
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
            # Si no hay fecha_fin, calcular basándose en el número de sesiones
            if not fecha_fin:
                # Estimar fecha fin: (sesiones / días_por_semana) * 7 días + margen de 4 semanas
                dias_por_semana = len(dias_numeros)
                semanas_estimadas = (max_sesiones // dias_por_semana) + 1
                fecha_fin = fecha_inicio + timedelta(weeks=semanas_estimadas + 4)
            
            # Generar cronograma de manera eficiente
            fecha_actual = fecha_inicio
            numero_sesion = 1
            sesiones_creadas = 0
            intentos_max = 1000  # Evitar bucles infinitos
            intentos = 0
            
            while sesiones_creadas < max_sesiones and fecha_actual <= fecha_fin and intentos < intentos_max:
                dia_semana = fecha_actual.weekday()  # 0=lunes, 6=domingo
                intentos += 1
                
                if dia_semana in dias_numeros:
                    # Insertar sesión en cronograma
                    insert_query = """
                        INSERT INTO cronograma_sesiones (
                            sesion_terapia_id, numero_sesion, fecha_programada, 
                            hora_programada, estado, usuario_creacion
                        ) VALUES (%s, %s, %s, %s, 'programada', %s)
                    """
                    params = (sesion_id, numero_sesion, fecha_actual, hora_inicio, sesion_data['usuario_creacion'])
                    DataBaseHandle.ExecuteNonQuery(insert_query, params)
                    
                    numero_sesion += 1
                    sesiones_creadas += 1
                    
                    # Log progreso cada 10 sesiones
                    if sesiones_creadas % 10 == 0:
                        HandleLogs.write_log(f"Cronograma sesión {sesion_id}: {sesiones_creadas}/{max_sesiones} generadas")
                
                fecha_actual += timedelta(days=1)
            
            # Validar resultados
            if sesiones_creadas == 0:
                raise Exception("No se pudieron generar sesiones. Verificar fechas y días de la semana.")
            
            if sesiones_creadas < max_sesiones:
                HandleLogs.write_error(
                    f"Advertencia: Solo se generaron {sesiones_creadas} de {max_sesiones} sesiones solicitadas")
            
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
                JOIN persona p ON pac.id_persona = p.id
                JOIN tutor t ON pac.tutor_id = t.id
                JOIN persona p_tutor ON t.id_persona = p_tutor.id
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
            # Insertar usando ExecuteNonQuery
            insert_query = """
                INSERT INTO sesion_paciente (
                    sesion_terapia_id, paciente_id, fecha_incorporacion,
                    costo_paciente, observaciones_paciente, estado, usuario_creacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
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

            # Ejecutar el INSERT
            insert_result = DataBaseHandle.ExecuteNonQuery(insert_query, params)
            if not insert_result:
                return None
                
            # Obtener el registro insertado
            select_query = """
                SELECT id FROM sesion_paciente 
                WHERE sesion_terapia_id = %s AND paciente_id = %s 
                ORDER BY fecha_creacion DESC LIMIT 1
            """
            select_params = (sesion_id, paciente_data['paciente_id'])
            result = DataBaseHandle.getRecords(select_query, select_params, size=1)
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
        """Obtener el cronograma completo de una sesión con información de asistencias"""
        try:
            query = """
                SELECT 
                    cs.*,
                    CASE 
                        WHEN cs.fecha_programada < CURRENT_DATE THEN 'vencida'
                        WHEN cs.fecha_programada = CURRENT_DATE THEN 'hoy'
                        ELSE cs.estado
                    END as estado_actual,
                    COUNT(DISTINCT a.id) as total_asistencias,
                    COUNT(DISTINCT CASE WHEN a.asistio = true THEN a.id END) as asistencias_confirmadas,
                    STRING_AGG(DISTINCT a.observaciones_asistencia, ' | ') as observaciones_asistencias,
                    STRING_AGG(DISTINCT a.notas_progreso, ' | ') as notas_progreso_sesion
                FROM cronograma_sesiones cs
                LEFT JOIN asistencia_sesiones a ON cs.id = a.cronograma_sesion_id
                WHERE cs.sesion_terapia_id = %s
                GROUP BY cs.id
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
    def reprogramar_sesion(cronograma_id, nueva_fecha, nueva_hora, motivo_reprogramacion, usuario_modificacion):
        """Reprogramar una sesión del cronograma creando una nueva sesión en la nueva fecha"""
        try:
            HandleLogs.write_log(f"SesionTerapiaComponent.reprogramar_sesion - Iniciando reprogramación: cronograma_id={cronograma_id}, nueva_fecha={nueva_fecha}, nueva_hora={nueva_hora}, motivo={motivo_reprogramacion}, usuario={usuario_modificacion}")
            
            # Paso 1: Obtener información de la sesión original
            query_original = """
                SELECT sesion_terapia_id, numero_sesion, fecha_programada, hora_programada, observaciones_cronograma
                FROM cronograma_sesiones 
                WHERE id = %s
            """
            sesion_original = DataBaseHandle.getRecords(query_original, (cronograma_id,))
            
            if not sesion_original:
                raise Exception(f"No se encontró la sesión con ID {cronograma_id}")
            
            sesion_data = sesion_original[0]
            sesion_terapia_id = sesion_data['sesion_terapia_id']
            numero_sesion_original = sesion_data['numero_sesion']
            
            HandleLogs.write_log(f"SesionTerapiaComponent.reprogramar_sesion - Sesión original encontrada: {sesion_data}")
            
            # Paso 2: Marcar la sesión original como reprogramada (mantener fecha original)
            query_marcar_reprogramada = """
                UPDATE cronograma_sesiones 
                SET estado = 'reprogramada',
                    motivo_reprogramacion = %s,
                    usuario_modificacion = %s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            params_marcar = (motivo_reprogramacion, usuario_modificacion, cronograma_id)
            
            result_marcar = DataBaseHandle.ExecuteNonQuery(query_marcar_reprogramada, params_marcar)
            if not result_marcar:
                raise Exception("Error al marcar la sesión original como reprogramada")
            
            HandleLogs.write_log(f"SesionTerapiaComponent.reprogramar_sesion - Sesión {cronograma_id} marcada como reprogramada")
            
            # Paso 3: Obtener el siguiente número de sesión disponible
            query_max_numero = """
                SELECT COALESCE(MAX(numero_sesion), 0) + 1 as siguiente_numero
                FROM cronograma_sesiones 
                WHERE sesion_terapia_id = %s
            """
            max_result = DataBaseHandle.getRecords(query_max_numero, (sesion_terapia_id,))
            siguiente_numero = max_result[0]['siguiente_numero'] if max_result else numero_sesion_original + 1
            
            HandleLogs.write_log(f"SesionTerapiaComponent.reprogramar_sesion - Siguiente número de sesión: {siguiente_numero}")
            
            # Paso 4: Crear nueva sesión en la nueva fecha con nuevo número
            query_nueva_sesion = """
                INSERT INTO cronograma_sesiones (
                    sesion_terapia_id, 
                    numero_sesion, 
                    fecha_programada, 
                    hora_programada, 
                    estado, 
                    observaciones_cronograma,
                    usuario_creacion, 
                    fecha_creacion
                ) VALUES (%s, %s, %s, %s, 'programada', %s, %s, CURRENT_TIMESTAMP)
                RETURNING id
            """
            
            observaciones_nueva = f"Reprogramada desde #{numero_sesion_original}"
            params_nueva = (
                sesion_terapia_id, 
                siguiente_numero, 
                nueva_fecha, 
                nueva_hora, 
                observaciones_nueva,
                usuario_modificacion
            )
            
            # Usar getRecords para obtener el ID de la nueva sesión
            nueva_sesion_result = DataBaseHandle.getRecords(query_nueva_sesion, params_nueva)
            if not nueva_sesion_result:
                raise Exception("Error al crear la nueva sesión reprogramada")
            
            nueva_cronograma_id = nueva_sesion_result[0]['id']
            HandleLogs.write_log(f"SesionTerapiaComponent.reprogramar_sesion - Nueva sesión creada con ID: {nueva_cronograma_id}")
            
            # Paso 5: Verificar si la sesión original tenía pacientes asignados y copiarlos a la nueva
            try:
                query_pacientes = """
                    SELECT DISTINCT sp.paciente_id, sp.fecha_incorporacion, sp.costo_paciente, sp.observaciones_paciente
                    FROM sesion_paciente sp
                    WHERE sp.sesion_terapia_id = %s
                """
                pacientes_sesion = DataBaseHandle.getRecords(query_pacientes, (sesion_terapia_id,))
                
                if pacientes_sesion and len(pacientes_sesion) > 0:
                    HandleLogs.write_log(f"SesionTerapiaComponent.reprogramar_sesion - Copiando {len(pacientes_sesion)} pacientes a la nueva sesión")
                    # Los pacientes ya están asignados a la sesión de terapia completa, no necesitamos copiarlos
                else:
                    HandleLogs.write_log(f"SesionTerapiaComponent.reprogramar_sesion - No hay pacientes específicos para copiar")
                    
            except Exception as copy_error:
                HandleLogs.write_error(f"SesionTerapiaComponent.reprogramar_sesion - Error verificando pacientes: {str(copy_error)}")
                # No es crítico, la sesión ya se creó exitosamente
            
            HandleLogs.write_log(
                f"SesionTerapiaComponent.reprogramar_sesion - Nueva sesión #{siguiente_numero} creada exitosamente para {nueva_fecha} {nueva_hora}")
            
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.reprogramar_sesion - Error: {str(e)}")
            raise Exception(f"Error al reprogramar sesión: {str(e)}")

    @staticmethod
    def cancelar_sesion(cronograma_id, motivo_cancelacion, usuario_modificacion):
        """Cancelar una sesión del cronograma"""
        try:
            query = """
                UPDATE cronograma_sesiones 
                SET estado = 'cancelada',
                    motivo_reprogramacion = %s,
                    usuario_modificacion = %s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            params = (motivo_cancelacion, usuario_modificacion, cronograma_id)

            result = DataBaseHandle.ExecuteNonQuery(query, params)
            if not result:
                raise Exception("Error al ejecutar la cancelación")

            HandleLogs.write_log(
                f"SesionTerapiaComponent.cancelar_sesion - Sesión {cronograma_id} cancelada")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.cancelar_sesion - Error: {str(e)}")
            raise Exception(f"Error al cancelar sesión: {str(e)}")

    @staticmethod
    def get_asistencias_por_cronograma(cronograma_id):
        """Obtener todas las asistencias de una sesión específica del cronograma"""
        try:
            query = """
                SELECT 
                    a.id,
                    a.cronograma_sesion_id,
                    a.paciente_id,
                    CONCAT(p.nombre, ' ', p.apellido) as paciente_nombre,
                    p.cedula as paciente_cedula,
                    a.asistio,
                    a.llegada_tardanza_minutos,
                    a.observaciones_asistencia,
                    a.notas_progreso,
                    a.tareas_asignadas,
                    a.proximos_objetivos,
                    a.fecha_creacion as fecha_registro
                FROM asistencia_sesiones a
                JOIN paciente pac ON a.paciente_id = pac.id
                JOIN persona p ON pac.id_persona = p.id
                WHERE a.cronograma_sesion_id = %s
                ORDER BY p.nombre, p.apellido
            """
            
            result = DataBaseHandle.getRecords(query, (cronograma_id,))
            HandleLogs.write_log(f"SesionTerapiaComponent.get_asistencias_por_cronograma - {len(result) if result else 0} asistencias encontradas")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_asistencias_por_cronograma - Error: {str(e)}")
            raise Exception(f"Error al obtener asistencias: {str(e)}")

    @staticmethod
    def actualizar_asistencia(cronograma_id, paciente_id, data, usuario_modificacion):
        """Actualizar asistencia existente de un paciente"""
        try:
            query = """
                UPDATE asistencia_sesiones 
                SET asistio = %s,
                    llegada_tardanza_minutos = %s,
                    observaciones_asistencia = %s,
                    notas_progreso = %s,
                    tareas_asignadas = %s,
                    proximos_objetivos = %s,
                    usuario_modificacion = %s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE cronograma_sesion_id = %s AND paciente_id = %s
            """
            
            params = (
                data.get('asistio', False),
                data.get('llegada_tardanza_minutos', 0),
                data.get('observaciones_asistencia', ''),
                data.get('notas_progreso', ''),
                data.get('tareas_asignadas', ''),
                data.get('proximos_objetivos', ''),
                usuario_modificacion,
                cronograma_id,
                paciente_id
            )
            
            result = DataBaseHandle.ExecuteNonQuery(query, params)
            if not result:
                raise Exception("Error al actualizar la asistencia")
            
            HandleLogs.write_log(f"SesionTerapiaComponent.actualizar_asistencia - Asistencia actualizada para paciente {paciente_id}")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.actualizar_asistencia - Error: {str(e)}")
            raise Exception(f"Error al actualizar asistencia: {str(e)}")

    # ============================================
    # MÉTODOS PARA ASISTENCIA_SESIONES
    # ============================================

    @staticmethod
    def registrar_asistencia(cronograma_id, paciente_id, asistencia_data):
        """Registrar la asistencia de un paciente a una sesión"""
        try:
            # Ejecutar UPSERT usando ExecuteNonQuery
            upsert_query = """
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

            # Ejecutar el UPSERT
            upsert_result = DataBaseHandle.ExecuteNonQuery(upsert_query, params)
            if not upsert_result:
                raise Exception("Error al registrar asistencia")
            
            # Actualizar estado del cronograma si el paciente asistió
            if asistencia_data.get('asistio', False):
                # Marcar sesión como realizada si al menos un paciente asistió
                observaciones_cronograma = asistencia_data.get('observaciones_asistencia') or asistencia_data.get('notas_progreso')
                SesionTerapiaComponent.marcar_sesion_realizada(cronograma_id, observaciones_cronograma)
                HandleLogs.write_log(f"SesionTerapiaComponent.registrar_asistencia - Cronograma {cronograma_id} marcado como realizada")
                
            # Obtener el registro actualizado/insertado
            select_query = """
                SELECT id FROM asistencia_sesiones 
                WHERE cronograma_sesion_id = %s AND paciente_id = %s
            """
            result = DataBaseHandle.getRecords(select_query, (cronograma_id, paciente_id), size=1)
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
                JOIN persona p ON pac.id_persona = p.id
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
                JOIN persona p_ter ON per.id_persona = p_ter.id
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
                JOIN persona p ON pac.id_persona = p.id
                JOIN tutor t ON pac.tutor_id = t.id
                JOIN persona p_tutor ON t.id_persona = p_tutor.id
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
                JOIN persona p ON per.id_persona = p.id
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

    @staticmethod
    def get_asistencias_por_sesion(sesion_id):
        """Obtener todas las asistencias de una sesión de terapia"""
        try:
            query = """
                SELECT 
                    a.id,
                    a.cronograma_sesion_id,
                    a.paciente_id,
                    CONCAT(p.nombre, ' ', p.apellido) as paciente_nombre,
                    p.cedula as paciente_cedula,
                    a.asistio,
                    a.llegada_tardanza_minutos,
                    a.observaciones_asistencia,
                    a.notas_progreso,
                    a.tareas_asignadas,
                    a.proximos_objetivos,
                    a.fecha_creacion as fecha_registro,
                    cs.fecha_programada::DATE as fecha_programada,
                    CAST(cs.hora_programada AS TEXT) as hora_programada,
                    cs.numero_sesion,
                    cs.estado as estado_sesion
                FROM asistencia_sesiones a
                JOIN cronograma_sesiones cs ON a.cronograma_sesion_id = cs.id
                JOIN sesion_terapia st ON cs.sesion_terapia_id = st.id
                JOIN paciente pac ON a.paciente_id = pac.id
                JOIN persona p ON pac.id_persona = p.id
                WHERE st.id = %s
                ORDER BY cs.fecha_programada, cs.hora_programada, p.apellido, p.nombre
            """

            params = (sesion_id,)
            result = DataBaseHandle.getRecords(query, params)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.get_asistencias_por_sesion - {len(result) if result else 0} asistencias encontradas para sesión {sesion_id}")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_asistencias_por_sesion - Error: {str(e)}")
            raise Exception(f"Error al obtener asistencias de la sesión: {str(e)}")

    @staticmethod
    def get_asistencias_por_paciente(paciente_id):
        """Obtener historial de asistencias de un paciente específico"""
        try:
            query = """
                SELECT 
                    a.id,
                    a.cronograma_sesion_id,
                    a.paciente_id,
                    a.asistio,
                    a.llegada_tardanza_minutos,
                    a.observaciones_asistencia,
                    a.notas_progreso,
                    a.tareas_asignadas,
                    a.proximos_objetivos,
                    a.fecha_creacion as fecha_registro,
                    cs.fecha_programada,
                    cs.hora_programada,
                    cs.numero_sesion,
                    st.titulo as sesion_titulo,
                    st.codigo_sesion,
                    CONCAT(p_ter.nombre, ' ', p_ter.apellido) as terapeuta_nombre,
                    e.nombre as especialidad_nombre
                FROM asistencia_sesiones a
                JOIN cronograma_sesiones cs ON a.cronograma_sesion_id = cs.id
                JOIN sesion_terapia st ON cs.sesion_terapia_id = st.id
                JOIN personal per ON st.terapeuta_id = per.id
                JOIN persona p_ter ON per.id_persona = p_ter.id
                JOIN especialidad e ON st.especialidad_id = e.id
                WHERE a.paciente_id = %s
                ORDER BY cs.fecha_programada DESC, cs.hora_programada DESC
            """

            params = (paciente_id,)
            result = DataBaseHandle.getRecords(query, params)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.get_asistencias_por_paciente - {len(result) if result else 0} asistencias encontradas para paciente {paciente_id}")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_asistencias_por_paciente - Error: {str(e)}")
            raise Exception(f"Error al obtener asistencias del paciente: {str(e)}")

    @staticmethod
    def get_estadisticas_asistencia_sesion(sesion_id):
        """Obtener estadísticas de asistencia de una sesión"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_asistencias_registradas,
                    COUNT(CASE WHEN a.asistio = true THEN 1 END) as asistencias_confirmadas,
                    COUNT(CASE WHEN a.asistio = false THEN 1 END) as inasistencias,
                    ROUND(AVG(CASE WHEN a.asistio = true THEN a.llegada_tardanza_minutos ELSE NULL END), 2) as promedio_tardanza_minutos,
                    COUNT(CASE WHEN a.llegada_tardanza_minutos > 0 AND a.asistio = true THEN 1 END) as asistencias_con_tardanza,
                    COUNT(DISTINCT a.paciente_id) as pacientes_unicos_registrados,
                    COUNT(DISTINCT cs.id) as sesiones_con_asistencia_registrada
                FROM cronograma_sesiones cs
                LEFT JOIN asistencia_sesiones a ON cs.id = a.cronograma_sesion_id
                WHERE cs.sesion_terapia_id = %s
            """

            params = (sesion_id,)
            result = DataBaseHandle.getRecords(query, params, size=1)
            
            if result:
                # Calcular porcentajes
                total = result.get('total_asistencias_registradas', 0)
                confirmadas = result.get('asistencias_confirmadas', 0)
                
                estadisticas = {
                    'total_asistencias_registradas': total,
                    'asistencias_confirmadas': confirmadas,
                    'inasistencias': result.get('inasistencias', 0),
                    'porcentaje_asistencia': round((confirmadas / total * 100), 2) if total > 0 else 0,
                    'promedio_tardanza_minutos': float(result.get('promedio_tardanza_minutos', 0)) if result.get('promedio_tardanza_minutos') else 0,
                    'asistencias_con_tardanza': result.get('asistencias_con_tardanza', 0),
                    'pacientes_unicos_registrados': result.get('pacientes_unicos_registrados', 0),
                    'sesiones_con_asistencia_registrada': result.get('sesiones_con_asistencia_registrada', 0)
                }
                
                HandleLogs.write_log(f"SesionTerapiaComponent.get_estadisticas_asistencia_sesion - Estadísticas calculadas para sesión {sesion_id}")
                return estadisticas
            else:
                return {}

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_estadisticas_asistencia_sesion - Error: {str(e)}")
            raise Exception(f"Error al obtener estadísticas de asistencia: {str(e)}")
    
    @staticmethod
    def actualizar_cronograma_inteligente(sesion_id, sesion_data):
        """Actualizar cronograma preservando asistencias existentes"""
        try:
            from datetime import datetime, timedelta
            
            HandleLogs.write_log(f"SesionTerapiaComponent.actualizar_cronograma_inteligente - Sesión ID: {sesion_id}")
            
            # Obtener cronograma actual
            cronograma_actual = SesionTerapiaComponent.get_cronograma_sesion(sesion_id)
            
            # Determinar fecha de corte (hoy) - solo actualizar sesiones futuras
            fecha_corte = datetime.now().date()
            
            # Preservar sesiones pasadas con asistencias
            sesiones_a_preservar = []
            if cronograma_actual:
                for sesion_cron in cronograma_actual:
                    fecha_sesion = sesion_cron['fecha_programada']
                    if isinstance(fecha_sesion, str):
                        fecha_sesion = datetime.strptime(fecha_sesion, '%Y-%m-%d').date()
                    
                    # Preservar si es del pasado O si ya tiene asistencias registradas
                    tiene_asistencias = SesionTerapiaComponent._cronograma_tiene_asistencias(sesion_cron['id'])
                    
                    if fecha_sesion <= fecha_corte or tiene_asistencias:
                        sesiones_a_preservar.append(sesion_cron)
                        HandleLogs.write_log(f"Preservando sesión del {fecha_sesion} (tiene asistencias: {tiene_asistencias})")
            
            # Eliminar solo sesiones futuras sin asistencias
            if cronograma_actual:
                for sesion_cron in cronograma_actual:
                    fecha_sesion = sesion_cron['fecha_programada']
                    if isinstance(fecha_sesion, str):
                        fecha_sesion = datetime.strptime(fecha_sesion, '%Y-%m-%d').date()
                    
                    tiene_asistencias = SesionTerapiaComponent._cronograma_tiene_asistencias(sesion_cron['id'])
                    
                    if fecha_sesion > fecha_corte and not tiene_asistencias:
                        # Eliminar sesión futura sin asistencias
                        delete_query = "DELETE FROM cronograma_sesiones WHERE id = %s"
                        DataBaseHandle.ExecuteNonQuery(delete_query, (sesion_cron['id'],))
                        HandleLogs.write_log(f"Eliminada sesión futura del {fecha_sesion} sin asistencias")
            
            # Generar nuevas sesiones futuras con los nuevos parámetros
            SesionTerapiaComponent._generar_cronograma_desde_fecha(sesion_id, sesion_data, fecha_corte + timedelta(days=1))
            
            HandleLogs.write_log(f"SesionTerapiaComponent.actualizar_cronograma_inteligente - Cronograma actualizado preservando asistencias")
            return True
            
        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.actualizar_cronograma_inteligente - Error: {str(e)}")
            raise e
    
    @staticmethod
    def _cronograma_tiene_asistencias(cronograma_id):
        """Verificar si una sesión del cronograma tiene asistencias registradas"""
        try:
            query = "SELECT COUNT(*) as count FROM asistencia_sesiones WHERE cronograma_sesion_id = %s"
            result = DataBaseHandle.getRecords(query, params=(cronograma_id,), size=1)
            return result and result.get('count', 0) > 0
        except Exception:
            return False
    
    @staticmethod
    def _generar_cronograma_desde_fecha(sesion_id, sesion_data, fecha_inicio):
        """Generar cronograma desde una fecha específica"""
        try:
            from datetime import datetime, timedelta
            
            # Convertir días de la semana a números
            dias_semana_map = {
                'lunes': 0, 'martes': 1, 'miercoles': 2, 'jueves': 3,
                'viernes': 4, 'sabado': 5, 'domingo': 6
            }
            
            dias_sesion = []
            if isinstance(sesion_data['dias_semana'], str):
                dias_nombres = [d.strip().lower() for d in sesion_data['dias_semana'].split(',')]
            else:
                dias_nombres = [d.strip().lower() for d in sesion_data['dias_semana']]
            
            for dia_nombre in dias_nombres:
                if dia_nombre in dias_semana_map:
                    dias_sesion.append(dias_semana_map[dia_nombre])
            
            if not dias_sesion:
                return
            
            # Generar sesiones desde fecha_inicio hasta fecha_fin
            fecha_actual = fecha_inicio
            fecha_fin = sesion_data['fecha_fin']
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            numero_sesion = SesionTerapiaComponent._get_ultimo_numero_sesion(sesion_id) + 1
            
            while fecha_actual <= fecha_fin:
                if fecha_actual.weekday() in dias_sesion:
                    # Crear sesión en el cronograma
                    cronograma_data = {
                        'sesion_terapia_id': sesion_id,
                        'numero_sesion': numero_sesion,
                        'fecha_programada': fecha_actual,
                        'hora_programada': sesion_data['hora_inicio'],
                        'estado': 'programada',
                        'usuario_creacion': sesion_data.get('usuario_modificacion', 1)
                    }
                    
                    insert_query = """
                        INSERT INTO cronograma_sesiones 
                        (sesion_terapia_id, numero_sesion, fecha_programada, hora_programada, estado, usuario_creacion)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    
                    params = (
                        cronograma_data['sesion_terapia_id'],
                        cronograma_data['numero_sesion'],
                        cronograma_data['fecha_programada'],
                        cronograma_data['hora_programada'],
                        cronograma_data['estado'],
                        cronograma_data['usuario_creacion']
                    )
                    
                    DataBaseHandle.ExecuteNonQuery(insert_query, params)
                    numero_sesion += 1
                
                fecha_actual += timedelta(days=1)
            
        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent._generar_cronograma_desde_fecha - Error: {str(e)}")
            raise e
    
    @staticmethod
    def _get_ultimo_numero_sesion(sesion_id):
        """Obtener el último número de sesión en el cronograma"""
        try:
            query = "SELECT COALESCE(MAX(numero_sesion), 0) as max_numero FROM cronograma_sesiones WHERE sesion_terapia_id = %s"
            result = DataBaseHandle.getRecords(query, params=(sesion_id,), size=1)
            return result.get('max_numero', 0) if result else 0
        except Exception:
            return 0