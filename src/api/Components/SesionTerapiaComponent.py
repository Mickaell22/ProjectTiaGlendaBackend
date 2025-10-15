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
                    st.objetivo_general,
                    st.id_terapeuta as terapeuta_id,
                    CONCAT(p_ter.nombre, ' ', p_ter.apellido) as terapeuta_nombre,
                    st.id_especialidad as especialidad_id,
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area,
                    st.fecha_inicio,
                    st.fecha_fin,
                    st.dias_semana,
                    TO_CHAR(st.hora_inicio, 'HH24:MI') as hora_inicio,
                    TO_CHAR(st.hora_fin, 'HH24:MI') as hora_fin,
                    st.duracion_minutos,
                    st.numero_sesiones_contratadas,
                    st.costo_total,
                    st.costo_sesion as costo_por_sesion,
                    st.meses_contrato,
                    st.tipo_sesion,
                    st.estado,
                    st.observaciones,
                    st.fecha_creacion,
                    st.fecha_modificacion,
                    COUNT(DISTINCT sp.id_paciente) as total_pacientes,
                    COUNT(DISTINCT cs.id) as sesiones_programadas,
                    COUNT(DISTINCT CASE WHEN ass.asistio = true THEN ass.id_cronograma END) as sesiones_realizadas
                FROM sesion_terapia st
                JOIN personal per ON st.id_terapeuta = per.id
                JOIN persona p_ter ON per.id_persona = p_ter.id
                JOIN especialidad e ON st.id_especialidad = e.id
                LEFT JOIN sesion_paciente sp ON st.id = sp.id_sesion AND sp.estado = 'activo'
                LEFT JOIN cronograma_sesiones cs ON st.id = cs.id_sesion
                LEFT JOIN asistencia_sesiones ass ON cs.id = ass.id_cronograma
                WHERE e.area = 'Especialidad terapéutica'
                    AND st.estado != 'cancelada'
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
                    st.id,
                    st.codigo_sesion,
                    st.titulo,
                    st.objetivo_general,
                    st.id_terapeuta as terapeuta_id,
                    st.id_especialidad as especialidad_id,
                    st.fecha_inicio,
                    st.fecha_fin,
                    st.dias_semana,
                    TO_CHAR(st.hora_inicio, 'HH24:MI') as hora_inicio,
                    TO_CHAR(st.hora_fin, 'HH24:MI') as hora_fin,
                    st.duracion_minutos,
                    st.costo_sesion as costo_por_sesion,
                    st.numero_sesiones_contratadas,
                    st.costo_total,
                    st.meses_contrato,
                    st.tipo_sesion,
                    st.estado,
                    st.observaciones,
                    st.fecha_creacion,
                    st.fecha_modificacion,
                    CONCAT(p_ter.nombre, ' ', p_ter.apellido) as terapeuta_nombre,
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area
                FROM sesion_terapia st
                JOIN personal per ON st.id_terapeuta = per.id
                JOIN persona p_ter ON per.id_persona = p_ter.id
                JOIN especialidad e ON st.id_especialidad = e.id
                WHERE st.id = %s
                    AND e.area = 'Especialidad terapéutica'
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
        """Crear una nueva sesión de terapia - VERSIÓN CORREGIDA SIN RACE CONDITION"""
        try:
            # CORRECCIÓN: Usar INSERT RETURNING directamente para evitar race condition
            query = """
                INSERT INTO sesion_terapia (
                    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
                    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
                    numero_sesiones_contratadas, meses_contrato, costo_total,
                    tipo_sesion, estado, observaciones, id_centro, usuario_creacion
                ) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, codigo_sesion, costo_total, costo_sesion
            """

            params = (
                sesion_data['titulo'],
                sesion_data.get('objetivo_general', ''),
                sesion_data['terapeuta_id'],
                sesion_data['especialidad_id'],
                sesion_data['fecha_inicio'],
                sesion_data['fecha_fin'],
                sesion_data['dias_semana'],  # PostgreSQL array, no JSON
                sesion_data['hora_inicio'],
                sesion_data.get('hora_fin'),
                sesion_data.get('duracion_minutos', 45),
                sesion_data.get('numero_sesiones_contratadas', 20),
                sesion_data.get('meses_contrato', 3),
                sesion_data.get('costo_total', 0),  # El trigger calculará costo_sesion desde este valor
                sesion_data.get('tipo_sesion', 'individual'),
                sesion_data.get('estado', 'planificada'),
                sesion_data.get('observaciones'),
                sesion_data.get('id_centro', 1),
                sesion_data['usuario_creacion']
            )

            # Usar getRecords con INSERT RETURNING para obtener datos atomicamente
            result = DataBaseHandle.getRecords(query, params, size=1)

            if result:
                sesion_id = result['id']
                codigo_sesion = result.get('codigo_sesion', f"ST-TEMP-{sesion_id}")
                costo_total = result.get('costo_total', 0)

                HandleLogs.write_log(f"SesionTerapiaComponent.create_sesion - Sesión creada con ID: {sesion_id}, Código: {codigo_sesion}, Costo Total: {costo_total}")

                # Generar cronograma automáticamente
                try:
                    SesionTerapiaComponent.generar_cronograma(sesion_id)
                    HandleLogs.write_log(f"SesionTerapiaComponent.create_sesion - Cronograma generado para sesión {sesion_id}")
                except Exception as cronograma_error:
                    HandleLogs.write_error(f"SesionTerapiaComponent.create_sesion - Error generando cronograma: {str(cronograma_error)}")
                    # No fallar el método completo si falla el cronograma

                return {
                    'id': sesion_id,
                    'codigo_sesion': codigo_sesion,
                    'costo_total': float(costo_total) if costo_total else 0.0
                }
            else:
                HandleLogs.write_error("SesionTerapiaComponent.create_sesion - No se pudo obtener result de INSERT RETURNING")
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
                    titulo = %s, objetivo_general = %s, id_terapeuta = %s, id_especialidad = %s,
                    fecha_inicio = %s, fecha_fin = %s, dias_semana = %s,
                    hora_inicio = %s, hora_fin = %s, duracion_minutos = %s,
                    numero_sesiones_contratadas = %s, meses_contrato = %s, costo_sesion = %s,
                    tipo_sesion = %s, estado = %s, observaciones = %s,
                    usuario_modificacion = %s
                WHERE id = %s
            """

            params = (
                sesion_data['titulo'],
                sesion_data.get('objetivo_general', ''),
                sesion_data['terapeuta_id'],
                sesion_data['especialidad_id'],
                sesion_data['fecha_inicio'],
                sesion_data['fecha_fin'],
                sesion_data['dias_semana'],
                sesion_data['hora_inicio'],
                sesion_data.get('hora_fin'),
                sesion_data.get('duracion_minutos', 45),
                sesion_data.get('numero_sesiones_contratadas', 20),
                sesion_data.get('meses_contrato', 3),
                sesion_data.get('costo_sesion', 25000.0),
                sesion_data.get('tipo_sesion', 'individual'),
                sesion_data.get('estado', 'planificada'),
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
        """Generar cronograma automático para una sesión - VERSIÓN CORREGIDA Y MEJORADA"""
        try:
            # Primero obtener la información de la sesión
            sesion_query = """
                SELECT fecha_inicio, fecha_fin, dias_semana, hora_inicio, duracion_minutos,
                       numero_sesiones_contratadas, meses_contrato, usuario_creacion
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
            delete_query = "DELETE FROM cronograma_sesiones WHERE id_sesion = %s"
            DataBaseHandle.ExecuteNonQuery(delete_query, (sesion_id,))

            # Generar cronograma programáticamente
            from datetime import datetime, timedelta

            fecha_inicio = sesion_data['fecha_inicio']
            fecha_fin = sesion_data['fecha_fin']

            # MEJORA: Procesamiento robusto de dias_semana
            dias_semana_raw = sesion_data['dias_semana']
            if isinstance(dias_semana_raw, str):
                dias_semana_str = dias_semana_raw.strip('{}').strip()
            elif isinstance(dias_semana_raw, list):
                dias_semana_str = ','.join(dias_semana_raw)
            else:
                dias_semana_str = str(dias_semana_raw).strip('{}').strip()

            hora_inicio = sesion_data['hora_inicio']
            max_sesiones = sesion_data['numero_sesiones_contratadas']
            meses_contrato = sesion_data.get('meses_contrato', 3)

            # CORRECCIÓN: Mapeo simplificado de días
            dias_map = {
                'lunes': 0, 'martes': 1, 'miercoles': 2, 'miércoles': 2,
                'jueves': 3, 'viernes': 4, 'sabado': 5, 'sábado': 5, 'domingo': 6
            }

            # Procesar días de la semana
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

            # CORRECCIÓN: Calcular fecha límite sin modificar automáticamente
            dias_por_semana = len(dias_numeros)
            semanas_necesarias = (max_sesiones + dias_por_semana - 1) // dias_por_semana  # Ceil division

            # Usar meses_contrato si fecha_fin no está definida
            if not fecha_fin:
                fecha_fin_calculada = fecha_inicio + timedelta(weeks=semanas_necesarias + 2)  # +2 semanas margen
                fecha_fin_por_meses = fecha_inicio + timedelta(days=meses_contrato * 30)  # Aproximado
                fecha_fin = max(fecha_fin_calculada, fecha_fin_por_meses)
                HandleLogs.write_log(f"Fecha fin calculada automáticamente: {fecha_fin} (basado en {semanas_necesarias} semanas y {meses_contrato} meses)")

            # CORRECCIÓN: Validar si la fecha fin es suficiente ANTES de generar
            fecha_minima_necesaria = fecha_inicio + timedelta(weeks=semanas_necesarias + 1)
            fecha_fin_original = fecha_fin
            if fecha_fin < fecha_minima_necesaria:
                # Extender automáticamente la fecha fin
                fecha_fin = fecha_minima_necesaria
                HandleLogs.write_log(f"Fecha fin extendida automáticamente de {fecha_fin_original} a {fecha_fin} para generar {max_sesiones} sesiones")

                # Actualizar la fecha_fin en la base de datos
                update_query = "UPDATE sesion_terapia SET fecha_fin = %s WHERE id = %s"
                DataBaseHandle.ExecuteNonQuery(update_query, (fecha_fin, sesion_id))

            # Generar cronograma de manera eficiente
            fecha_actual = fecha_inicio
            sesiones_creadas = 0
            semana_actual = 1

            HandleLogs.write_log(f"Iniciando generación: {max_sesiones} sesiones desde {fecha_inicio} hasta {fecha_fin}, días: {dias_numeros}")

            # MEJORA: Algoritmo más eficiente que busca solo días válidos
            while sesiones_creadas < max_sesiones and fecha_actual <= fecha_fin:
                dia_semana = fecha_actual.weekday()  # 0=lunes, 6=domingo

                if dia_semana in dias_numeros:
                    # Insertar sesión en cronograma
                    insert_query = """
                        INSERT INTO cronograma_sesiones (
                            id_sesion, semana_numero, numero_sesion_semanal, fecha_programada,
                            hora_inicio, hora_fin, estado, usuario_creacion
                        ) VALUES (%s, %s, %s, %s, %s, %s, 'programada', %s)
                    """

                    # Calcular hora_fin basada en duración
                    hora_fin = (datetime.combine(fecha_actual, hora_inicio) +
                               timedelta(minutes=sesion_data.get('duracion_minutos', 45))).time()

                    numero_en_semana = dias_numeros.index(dia_semana) + 1

                    params = (sesion_id, semana_actual, numero_en_semana, fecha_actual,
                             hora_inicio, hora_fin, sesion_data['usuario_creacion'])
                    DataBaseHandle.ExecuteNonQuery(insert_query, params)

                    sesiones_creadas += 1

                    # Log progreso cada 10 sesiones
                    if sesiones_creadas % 10 == 0:
                        HandleLogs.write_log(f"Cronograma sesión {sesion_id}: {sesiones_creadas}/{max_sesiones} generadas")

                fecha_actual += timedelta(days=1)

                # Incrementar semana cuando sea lunes
                if fecha_actual.weekday() == 0:
                    semana_actual += 1

            # Validar resultados
            if sesiones_creadas == 0:
                raise Exception("No se pudieron generar sesiones. Verificar fechas y días de la semana.")

            # MEJORA: Reporte más detallado
            if sesiones_creadas < max_sesiones:
                HandleLogs.write_log(
                    f"ADVERTENCIA: Solo se generaron {sesiones_creadas} de {max_sesiones} sesiones solicitadas. Última fecha procesada: {fecha_actual}")

            HandleLogs.write_log(
                f"Cronograma generado exitosamente: {sesiones_creadas} sesiones para sesión {sesion_id}")
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
                    sp.id_paciente as paciente_id,
                    CONCAT(p.nombre, ' ', p.apellido) as paciente_nombre,
                    p.cedula as paciente_cedula,
                    sp.fecha_inscripcion as fecha_asignacion,
                    sp.observaciones,
                    sp.estado,
                    CONCAT(p_tutor.nombre, ' ', p_tutor.apellido) as tutor_nombre,
                    p_tutor.telefono as tutor_telefono
                FROM sesion_paciente sp
                JOIN paciente pac ON sp.id_paciente = pac.id
                JOIN persona p ON pac.id_persona = p.id
                LEFT JOIN tutor t ON pac.id_tutor = t.id
                LEFT JOIN persona p_tutor ON t.id_persona = p_tutor.id
                WHERE sp.id_sesion = %s
                ORDER BY sp.estado DESC, sp.fecha_inscripcion
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
    def get_pacientes_multiple_sesiones(sesion_ids):
        """Obtener pacientes de multiples sesiones en una sola query (optimizacion N+1)"""
        try:
            if not sesion_ids:
                return []

            placeholders = ','.join(['%s'] * len(sesion_ids))
            query = f"""
                SELECT
                    sp.id_sesion,
                    sp.id,
                    sp.id_paciente as paciente_id,
                    CONCAT(p.nombre, ' ', p.apellido) as paciente_nombre,
                    p.cedula as paciente_cedula,
                    sp.fecha_inscripcion as fecha_asignacion,
                    sp.observaciones,
                    sp.estado,
                    CONCAT(p_tutor.nombre, ' ', p_tutor.apellido) as tutor_nombre,
                    p_tutor.telefono as tutor_telefono
                FROM sesion_paciente sp
                JOIN paciente pac ON sp.id_paciente = pac.id
                JOIN persona p ON pac.id_persona = p.id
                LEFT JOIN tutor t ON pac.id_tutor = t.id
                LEFT JOIN persona p_tutor ON t.id_persona = p_tutor.id
                WHERE sp.id_sesion IN ({placeholders})
                ORDER BY sp.id_sesion, sp.estado DESC, sp.fecha_inscripcion
            """

            result = DataBaseHandle.getRecords(query, tuple(sesion_ids))
            HandleLogs.write_log(
                f"SesionTerapiaComponent.get_pacientes_multiple_sesiones - {len(result) if result else 0} pacientes encontrados para {len(sesion_ids)} sesiones")
            return result or []

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_pacientes_multiple_sesiones - Error: {str(e)}")
            raise Exception(f"Error al obtener pacientes de multiples sesiones: {str(e)}")

    @staticmethod
    def add_paciente_to_sesion(sesion_id, paciente_data):
        """Agregar un paciente a una sesión"""
        try:
            # Insertar usando ExecuteNonQuery
            insert_query = """
                INSERT INTO sesion_paciente (
                    id_sesion, id_paciente, fecha_inscripcion, observaciones, estado, usuario_creacion
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """

            params = (
                sesion_id,
                paciente_data['paciente_id'],
                paciente_data.get('fecha_inscripcion', datetime.now().date()),
                paciente_data.get('observaciones'),
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
                WHERE id_sesion = %s AND id_paciente = %s 
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
                WHERE id_sesion = %s AND id_paciente = %s
            """
            params = (sesion_id, paciente_id)

            DataBaseHandle.ExecuteNonQuery(query, params)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.remove_paciente_from_sesion - Paciente {paciente_id} retirado de sesión {sesion_id}")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.remove_paciente_from_sesion - Error: {str(e)}")
            raise Exception(f"Error al retirar paciente de la sesión: {str(e)}")

    @staticmethod
    def get_pacientes_retirados_sesion(sesion_id):
        """Obtener pacientes retirados de una sesión terapéutica"""
        try:
            query = """
                SELECT
                    sp.id,
                    sp.id_paciente as paciente_id,
                    CONCAT(p.nombre, ' ', p.apellido) as paciente_nombre,
                    p.cedula as paciente_cedula,
                    sp.fecha_inscripcion as fecha_asignacion,
                    sp.observaciones,
                    sp.estado,
                    CONCAT(p_tutor.nombre, ' ', p_tutor.apellido) as tutor_nombre,
                    p_tutor.telefono as tutor_telefono
                FROM sesion_paciente sp
                JOIN paciente pac ON sp.id_paciente = pac.id
                JOIN persona p ON pac.id_persona = p.id
                LEFT JOIN tutor t ON pac.id_tutor = t.id
                LEFT JOIN persona p_tutor ON t.id_persona = p_tutor.id
                WHERE sp.id_sesion = %s AND sp.estado = 'retirado'
                ORDER BY sp.fecha_inscripcion
            """
            params = (sesion_id,)
            result = DataBaseHandle.getRecords(query, params)
            HandleLogs.write_log(
                f"SesionTerapiaComponent.get_pacientes_retirados_sesion - {len(result) if result else 0} pacientes retirados encontrados")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_pacientes_retirados_sesion - Error: {str(e)}")
            raise Exception(f"Error al obtener pacientes retirados: {str(e)}")

    @staticmethod
    def reincorporar_paciente_sesion(sesion_id, paciente_id):
        """Reincorporar un paciente previamente retirado a una sesión terapéutica"""
        try:
            query = """
                UPDATE sesion_paciente
                SET estado = 'activo'
                WHERE id_sesion = %s AND id_paciente = %s AND estado = 'retirado'
            """
            params = (sesion_id, paciente_id)

            DataBaseHandle.ExecuteNonQuery(query, params)
            HandleLogs.write_log(f"SesionTerapiaComponent.reincorporar_paciente_sesion - Paciente reincorporado a sesión {sesion_id}")
            return True

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.reincorporar_paciente_sesion - Error: {str(e)}")
            raise Exception(f"Error al reincorporar paciente: {str(e)}")

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
                    ROW_NUMBER() OVER (ORDER BY cs.fecha_programada, cs.hora_inicio) as numero_sesion,
                    CASE
                        WHEN cs.fecha_programada < CURRENT_DATE THEN 'vencida'
                        WHEN cs.fecha_programada = CURRENT_DATE THEN 'hoy'
                        ELSE cs.estado
                    END as estado_actual,
                    COUNT(DISTINCT a.id) as total_asistencias,
                    COUNT(DISTINCT CASE WHEN a.asistio = true THEN a.id END) as asistencias_confirmadas,
                    STRING_AGG(DISTINCT a.observaciones_terapeuta, ' | ') as observaciones_asistencias,
                    STRING_AGG(DISTINCT a.progreso_observado, ' | ') as notas_progreso_sesion
                FROM cronograma_sesiones cs
                LEFT JOIN asistencia_sesiones a ON cs.id = a.id_cronograma
                WHERE cs.id_sesion = %s
                GROUP BY cs.id
                ORDER BY cs.fecha_programada, cs.hora_inicio
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
                SET estado = 'completada', 
                    observaciones = %s,
                    fecha_realizacion = CURRENT_TIMESTAMP,
                    fecha_modificacion = CURRENT_TIMESTAMP
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
            
            # Paso 1: Obtener información de la sesión original y duración de la sesión de terapia
            query_original = """
                SELECT 
                    cs.id_sesion, 
                    cs.numero_sesion_semanal, 
                    cs.fecha_programada, 
                    cs.hora_inicio, 
                    cs.observaciones,
                    st.duracion_minutos
                FROM cronograma_sesiones cs
                JOIN sesion_terapia st ON cs.id_sesion = st.id
                WHERE cs.id = %s
            """
            sesion_original = DataBaseHandle.getRecords(query_original, (cronograma_id,))
            
            if not sesion_original:
                raise Exception(f"No se encontró la sesión con ID {cronograma_id}")
            
            sesion_data = sesion_original[0]
            id_sesion = sesion_data['id_sesion']
            numero_sesion_semanal_original = sesion_data['numero_sesion_semanal']
            
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
                SELECT COALESCE(MAX(numero_sesion_semanal), 0) + 1 as siguiente_numero
                FROM cronograma_sesiones 
                WHERE id_sesion = %s
            """
            max_result = DataBaseHandle.getRecords(query_max_numero, (id_sesion,))
            siguiente_numero = max_result[0]['siguiente_numero'] if max_result else numero_sesion_semanal_original + 1
            
            HandleLogs.write_log(f"SesionTerapiaComponent.reprogramar_sesion - Siguiente número de sesión: {siguiente_numero}")
            
            # Paso 4: Crear nueva sesión en la nueva fecha con nuevo número
            query_nueva_sesion = """
                INSERT INTO cronograma_sesiones (
                    id_sesion, 
                    numero_sesion_semanal, 
                    fecha_programada, 
                    hora_inicio, 
                    hora_fin,
                    estado, 
                    observaciones,
                    usuario_creacion, 
                    fecha_creacion
                ) VALUES (%s, %s, %s, %s, %s, 'programada', %s, %s, CURRENT_TIMESTAMP)
            """
            
            observaciones_nueva = f"Reprogramada desde #{numero_sesion_semanal_original}"
            
            # Calcular hora_fin basándose en la duración
            from datetime import datetime, timedelta
            duracion_minutos = sesion_data.get('duracion_minutos', 45)  # default 45 minutos
            if isinstance(nueva_hora, str):
                hora_inicio_dt = datetime.strptime(nueva_hora, '%H:%M').time()
            else:
                hora_inicio_dt = nueva_hora
                
            # Convertir a datetime para hacer el cálculo
            dt_temp = datetime.combine(datetime.today(), hora_inicio_dt)
            dt_fin = dt_temp + timedelta(minutes=duracion_minutos)
            hora_fin = dt_fin.time()
            
            params_nueva = (
                id_sesion, 
                siguiente_numero, 
                nueva_fecha, 
                nueva_hora, 
                hora_fin,
                observaciones_nueva,
                usuario_modificacion
            )
            
            # Usar ExecuteNonQuery para el INSERT y luego obtener el último ID insertado
            insert_result = DataBaseHandle.ExecuteNonQuery(query_nueva_sesion, params_nueva)
            if not insert_result:
                raise Exception("Error al crear la nueva sesión reprogramada")
            
            # Obtener el ID de la sesión recién creada
            query_ultimo_id = """
                SELECT id FROM cronograma_sesiones 
                WHERE id_sesion = %s AND numero_sesion_semanal = %s 
                ORDER BY fecha_creacion DESC 
                LIMIT 1
            """
            id_result = DataBaseHandle.getRecords(query_ultimo_id, (id_sesion, siguiente_numero), size=1)
            if not id_result:
                raise Exception("Error al obtener ID de la nueva sesión creada")
            
            nueva_cronograma_id = id_result['id']
            HandleLogs.write_log(f"SesionTerapiaComponent.reprogramar_sesion - Nueva sesión creada con ID: {nueva_cronograma_id}")
            
            # Paso 5: Verificar si la sesión original tenía pacientes asignados y copiarlos a la nueva
            try:
                query_pacientes = """
                    SELECT DISTINCT sp.id_paciente, sp.fecha_inscripcion, sp.observaciones
                    FROM sesion_paciente sp
                    WHERE sp.id_sesion = %s
                """
                pacientes_sesion = DataBaseHandle.getRecords(query_pacientes, (id_sesion,))
                
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
            # Query que incluye TODOS los pacientes asignados a la sesión, 
            # incluso si no tienen registro de asistencia todavía
            query = """
                SELECT
                    COALESCE(a.id, NULL) as id,
                    %s as id_cronograma,
                    sp.id_paciente,
                    CONCAT(p.nombre, ' ', p.apellido) as paciente_nombre,
                    p.cedula as paciente_cedula,
                    COALESCE(a.asistio, false) as asistio,
                    COALESCE(a.llegada_tardanza_minutos, 0) as llegada_tardanza_minutos,
                    a.observaciones_terapeuta,
                    a.progreso_observado,
                    a.tareas_asignadas,
                    a.objetivos_trabajados,
                    a.fecha_creacion as fecha_registro,
                    cs.fecha_programada,
                    CAST(cs.hora_inicio AS TEXT) as hora_inicio,
                    cs.numero_sesion_semanal,
                    cs.estado as estado_sesion
                FROM cronograma_sesiones cs
                JOIN sesion_terapia st ON cs.id_sesion = st.id
                JOIN sesion_paciente sp ON st.id = sp.id_sesion AND sp.estado = 'activo'
                JOIN paciente pac ON sp.id_paciente = pac.id
                JOIN persona p ON pac.id_persona = p.id
                LEFT JOIN asistencia_sesiones a ON cs.id = a.id_cronograma AND sp.id_paciente = a.id_paciente
                WHERE cs.id = %s
                ORDER BY p.nombre, p.apellido
            """
            
            result = DataBaseHandle.getRecords(query, (cronograma_id, cronograma_id))
            HandleLogs.write_log(f"SesionTerapiaComponent.get_asistencias_por_cronograma - {len(result) if result else 0} asistencias encontradas")
            return result

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_asistencias_por_cronograma - Error: {str(e)}")
            raise Exception(f"Error al obtener asistencias: {str(e)}")

    @staticmethod
    def get_control_asistencia_completo(cronograma_id):
        """Obtener todos los pacientes de la sesión con su estado de asistencia para un cronograma específico"""
        try:
            query = """
                SELECT
                    cs.id as cronograma_id,
                    cs.numero_sesion_semanal,
                    cs.fecha_programada,
                    cs.hora_inicio,
                    cs.hora_fin,
                    cs.estado as estado_cronograma,
                    st.id as sesion_id,
                    st.titulo as sesion_titulo,
                    -- Información de pacientes asignados a la sesión
                    sp.id_paciente,
                    CONCAT(p.nombre, ' ', p.apellido) as paciente_nombre,
                    p.cedula as paciente_cedula,
                    -- Información de asistencia (si existe)
                    COALESCE(a.asistio, false) as asistio,
                    COALESCE(a.llegada_tardanza_minutos, 0) as llegada_tardanza_minutos,
                    a.observaciones_terapeuta,
                    a.progreso_observado,
                    a.tareas_asignadas,
                    a.objetivos_trabajados,
                    CASE
                        WHEN a.id IS NOT NULL THEN 'registrada'
                        ELSE 'pendiente'
                    END as estado_asistencia
                FROM cronograma_sesiones cs
                JOIN sesion_terapia st ON cs.id_sesion = st.id
                LEFT JOIN sesion_paciente sp ON st.id = sp.id_sesion AND sp.estado = 'activo'
                LEFT JOIN paciente pac ON sp.id_paciente = pac.id
                LEFT JOIN persona p ON pac.id_persona = p.id
                LEFT JOIN asistencia_sesiones a ON cs.id = a.id_cronograma AND sp.id_paciente = a.id_paciente
                WHERE cs.id = %s
                ORDER BY p.nombre, p.apellido
            """
            
            result = DataBaseHandle.getRecords(query, (cronograma_id,))
            
            if not result:
                # Si no hay resultados, puede ser que no haya pacientes asignados
                # Devolver información básica del cronograma
                query_cronograma = """
                    SELECT 
                        cs.id as cronograma_id,
                        cs.numero_sesion_semanal,
                        cs.fecha_programada,
                        cs.hora_inicio,
                        cs.hora_fin,
                        cs.estado as estado_cronograma,
                        st.id as sesion_id,
                        st.titulo as sesion_titulo
                    FROM cronograma_sesiones cs
                    JOIN sesion_terapia st ON cs.id_sesion = st.id
                    WHERE cs.id = %s
                """
                cronograma_info = DataBaseHandle.getRecords(query_cronograma, (cronograma_id,), size=1)
                
                if cronograma_info:
                    HandleLogs.write_log(f"SesionTerapiaComponent.get_control_asistencia_completo - Cronograma encontrado pero sin pacientes asignados")
                    return {
                        'cronograma': cronograma_info,
                        'pacientes': [],
                        'mensaje': 'No hay pacientes asignados a esta sesión'
                    }
                else:
                    HandleLogs.write_log(f"SesionTerapiaComponent.get_control_asistencia_completo - Cronograma {cronograma_id} no encontrado")
                    return {
                        'cronograma': None,
                        'pacientes': [],
                        'mensaje': 'Cronograma no encontrado'
                    }
            
            # Organizar los datos
            cronograma_info = {
                'cronograma_id': result[0]['cronograma_id'],
                'numero_sesion_semanal': result[0]['numero_sesion_semanal'],
                'fecha_programada': result[0]['fecha_programada'].isoformat() if result[0]['fecha_programada'] else None,
                'hora_inicio': str(result[0]['hora_inicio']) if result[0]['hora_inicio'] else None,
                'hora_fin': str(result[0]['hora_fin']) if result[0]['hora_fin'] else None,
                'estado_cronograma': result[0]['estado_cronograma'],
                'sesion_id': result[0]['sesion_id'],
                'sesion_titulo': result[0]['sesion_titulo']
            }
            
            pacientes = []
            for row in result:
                if row['id_paciente']:  # Solo incluir si hay paciente
                    pacientes.append({
                        'paciente_id': row['id_paciente'],
                        'paciente_nombre': row['paciente_nombre'],
                        'paciente_cedula': row['paciente_cedula'],
                        'asistio': row['asistio'],
                        'llegada_tardanza_minutos': row['llegada_tardanza_minutos'],
                        'observaciones_terapeuta': row['observaciones_terapeuta'],
                        'progreso_observado': row['progreso_observado'],
                        'tareas_asignadas': row['tareas_asignadas'],
                        'objetivos_trabajados': row['objetivos_trabajados'],
                        'estado_asistencia': row['estado_asistencia']
                    })
            
            HandleLogs.write_log(f"SesionTerapiaComponent.get_control_asistencia_completo - {len(pacientes)} pacientes encontrados para cronograma {cronograma_id}")
            return {
                'cronograma': cronograma_info,
                'pacientes': pacientes,
                'mensaje': f'Control de asistencia cargado correctamente - {len(pacientes)} pacientes'
            }

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_control_asistencia_completo - Error: {str(e)}")
            raise Exception(f"Error al obtener control de asistencia: {str(e)}")

    @staticmethod
    def actualizar_asistencia(cronograma_id, paciente_id, data, usuario_modificacion):
        """Actualizar asistencia existente de un paciente"""
        try:
            query = """
                UPDATE asistencia_sesiones
                SET asistio = %s,
                    llegada_tardanza_minutos = %s,
                    estado_asistencia = %s,
                    observaciones_terapeuta = %s,
                    progreso_observado = %s,
                    tareas_asignadas = %s,
                    objetivos_trabajados = %s,
                    usuario_modificacion = %s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id_cronograma = %s AND id_paciente = %s
            """

            # Limpiar campos de texto para UTF-8
            from src.utils.general.utf8_helper import UTF8Helper

            params = (
                data.get('asistio', False),
                data.get('llegada_tardanza_minutos', 0),
                data.get('estado_asistencia', 'pendiente'),
                UTF8Helper.clean_observaciones(data.get('observaciones_terapeuta', '')),
                UTF8Helper.clean_observaciones(data.get('progreso_observado', '')),
                UTF8Helper.clean_observaciones(data.get('tareas_asignadas', '')),
                UTF8Helper.clean_observaciones(data.get('objetivos_trabajados', '')),
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
                    id_cronograma, id_paciente, asistio, llegada_tardanza_minutos, estado_asistencia,
                    observaciones_terapeuta, progreso_observado, tareas_asignadas,
                    objetivos_trabajados, usuario_creacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_cronograma, id_paciente)
                DO UPDATE SET
                    asistio = EXCLUDED.asistio,
                    llegada_tardanza_minutos = EXCLUDED.llegada_tardanza_minutos,
                    estado_asistencia = EXCLUDED.estado_asistencia,
                    observaciones_terapeuta = EXCLUDED.observaciones_terapeuta,
                    progreso_observado = EXCLUDED.progreso_observado,
                    tareas_asignadas = EXCLUDED.tareas_asignadas,
                    objetivos_trabajados = EXCLUDED.objetivos_trabajados,
                    usuario_modificacion = EXCLUDED.usuario_creacion
            """

            # Limpiar campos de texto para UTF-8
            from src.utils.general.utf8_helper import UTF8Helper

            # Determinar estado de asistencia
            estado_asistencia = 'pendiente'
            if asistencia_data.get('asistio', False):
                if asistencia_data.get('llegada_tardanza_minutos', 0) > 0:
                    estado_asistencia = 'tarde'
                else:
                    estado_asistencia = 'presente'
            else:
                estado_asistencia = asistencia_data.get('estado_asistencia', 'ausente')

            params = (
                cronograma_id,
                paciente_id,
                asistencia_data.get('asistio', False),
                asistencia_data.get('llegada_tardanza_minutos', 0),
                estado_asistencia,
                UTF8Helper.clean_observaciones(asistencia_data.get('observaciones_terapeuta')),
                UTF8Helper.clean_observaciones(asistencia_data.get('progreso_observado')),
                UTF8Helper.clean_observaciones(asistencia_data.get('tareas_asignadas')),
                UTF8Helper.clean_observaciones(asistencia_data.get('objetivos_trabajados')),
                asistencia_data['usuario_creacion']
            )

            # Ejecutar el UPSERT
            upsert_result = DataBaseHandle.ExecuteNonQuery(upsert_query, params)
            if not upsert_result:
                raise Exception("Error al registrar asistencia")
            
            # Actualizar estado del cronograma si el paciente asistió
            if asistencia_data.get('asistio', False):
                # Marcar sesión como realizada si al menos un paciente asistió
                observaciones_cronograma = asistencia_data.get('observaciones_terapeuta') or asistencia_data.get('progreso_observado')
                SesionTerapiaComponent.marcar_sesion_realizada(cronograma_id, observaciones_cronograma)
                HandleLogs.write_log(f"SesionTerapiaComponent.registrar_asistencia - Cronograma {cronograma_id} marcado como realizada")
                
            # Obtener el registro actualizado/insertado
            select_query = """
                SELECT id FROM asistencia_sesiones 
                WHERE id_cronograma = %s AND id_paciente = %s
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
                JOIN paciente pac ON a.id_paciente = pac.id
                JOIN persona p ON pac.id_persona = p.id
                WHERE a.id_cronograma = %s
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
                    st.id,
                    st.codigo_sesion,
                    st.titulo,
                    st.objetivo_general,
                    st.id_terapeuta as terapeuta_id,
                    st.id_especialidad as especialidad_id,
                    e.nombre as especialidad_nombre,
                    st.fecha_inicio,
                    st.fecha_fin,
                    st.dias_semana,
                    TO_CHAR(st.hora_inicio, 'HH24:MI') as hora_inicio,
                    TO_CHAR(st.hora_fin, 'HH24:MI') as hora_fin,
                    st.duracion_minutos,
                    st.numero_sesiones_contratadas,
                    st.costo_total,
                    st.costo_sesion as costo_por_sesion,
                    st.meses_contrato,
                    st.tipo_sesion,
                    st.estado,
                    st.fecha_creacion,
                    COUNT(sp.id_paciente) as total_pacientes
                FROM sesion_terapia st
                JOIN especialidad e ON st.id_especialidad = e.id
                LEFT JOIN sesion_paciente sp ON st.id = sp.id_sesion AND sp.estado = 'activo'
                WHERE st.id_terapeuta = %s 
                    AND st.estado != 'cancelada'
                    AND e.area = 'Especialidad terapéutica'
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
                    cs.numero_sesion_semanal,
                    cs.hora_inicio,
                    st.titulo,
                    st.codigo_sesion,
                    CONCAT(p_ter.nombre, ' ', p_ter.apellido) as terapeuta_nombre,
                    e.nombre as especialidad_nombre,
                    COUNT(sp.id_paciente) as total_pacientes,
                    cs.estado
                FROM cronograma_sesiones cs
                JOIN sesion_terapia st ON cs.id_sesion = st.id
                JOIN personal per ON st.id_terapeuta = per.id
                JOIN persona p_ter ON per.id_persona = p_ter.id
                JOIN especialidad e ON st.id_especialidad = e.id
                LEFT JOIN sesion_paciente sp ON st.id = sp.id_sesion AND sp.estado = 'activo'
                WHERE cs.fecha_programada = CURRENT_DATE 
                    AND st.estado IN ('planificada', 'en_curso')
                    AND cs.estado IN ('programada', 'completada')
                    AND e.area = 'Especialidad terapéutica'
                GROUP BY cs.id, st.id, p_ter.nombre, p_ter.apellido, e.nombre
                ORDER BY cs.hora_inicio
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
                    COALESCE(COUNT(*) * 20, 0) as total_sesiones_contratadas,
                    COALESCE(SUM(costo_sesion * 20), 0) as ingresos_totales,
                    COALESCE(AVG(duracion_minutos), 0) as duracion_promedio
                FROM sesion_terapia
            """

            result = DataBaseHandle.getRecords(query, size=1)

            # Estadísticas adicionales de cronograma
            query_cronograma = """
                SELECT 
                    COUNT(*) as total_sesiones_programadas,
                    COUNT(CASE WHEN estado = 'completada' THEN 1 END) as sesiones_realizadas,
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
                LEFT JOIN tutor t ON pac.id_tutor = t.id
                LEFT JOIN persona p_tutor ON t.id_persona = p_tutor.id
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
        """Obtener terapeutas que pueden ser asignados a sesiones terapéuticas"""
        try:
            HandleLogs.write_log("SesionTerapiaComponent.get_terapeutas_disponibles - Iniciando")
            
            # Query optimizada para obtener solo personal con especialidades terapéuticas
            query = """
            SELECT DISTINCT
                p.id,
                p.id_persona,
                CONCAT(pe.nombre, ' ', pe.apellido) as nombre_completo,
                pe.nombre,
                pe.apellido,
                pe.cedula,
                pe.telefono,
                pe.correo,
                p.cargo as titulo_profesional,
                p.cargo,
                p.estado,
                p.id_centro,
                c.nombre as centro_nombre,
                u.id as usuario_id,
                r.nombre as rol_usuario,
                -- Especialidad principal
                e.id as especialidad_id,
                e.nombre as especialidad_nombre
            FROM personal p
            INNER JOIN persona pe ON p.id_persona = pe.id
            LEFT JOIN usuario u ON pe.id = u.id_persona
            LEFT JOIN rol r ON u.id_rol = r.id
            LEFT JOIN centros c ON p.id_centro = c.id
            INNER JOIN personal_especialidades pes ON p.id = pes.id_personal
            INNER JOIN especialidad e ON pes.id_especialidad = e.id
            WHERE p.estado = 'activo' 
            AND pes.estado = 'activo'
            AND e.area = 'Especialidad terapéutica'
            ORDER BY pe.nombre, pe.apellido
            """
            
            result = DataBaseHandle.getRecords(query)
            
            if result:
                terapeutas = []
                if isinstance(result, dict):
                    result = [result]
                
                for persona in result:
                    terapeutas.append({
                        'id': persona['id'],
                        'id_persona': persona['id_persona'],
                        'nombre_completo': persona['nombre_completo'],
                        'nombre': persona['nombre'],
                        'apellido': persona['apellido'],
                        'cedula': persona['cedula'],
                        'telefono': persona.get('telefono', ''),
                        'correo': persona.get('correo', ''),
                        'titulo_profesional': persona.get('titulo_profesional', ''),
                        'cargo': persona.get('cargo', ''),
                        'estado': persona['estado'],
                        'id_centro': persona.get('id_centro'),
                        'centro_nombre': persona.get('centro_nombre', ''),
                        'usuario_id': persona.get('usuario_id'),
                        'rol_usuario': persona.get('rol_usuario', ''),
                        'especialidad_id': persona.get('especialidad_id'),
                        'especialidad_nombre': persona.get('especialidad_nombre', '')
                    })
                
                HandleLogs.write_log(f"SesionTerapiaComponent.get_terapeutas_disponibles - Obtenidos {len(terapeutas)} terapeutas con especialidades terapéuticas")
                return terapeutas
            else:
                HandleLogs.write_log("SesionTerapiaComponent.get_terapeutas_disponibles - No se encontraron terapeutas")
                return []

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
                    a.id_cronograma,
                    a.id_paciente,
                    CONCAT(p.nombre, ' ', p.apellido) as paciente_nombre,
                    p.cedula as paciente_cedula,
                    a.asistio,
                    a.llegada_tardanza_minutos,
                    a.estado_asistencia,
                    a.observaciones_terapeuta,
                    a.progreso_observado,
                    a.tareas_asignadas,
                    a.objetivos_trabajados,
                    a.fecha_creacion as fecha_registro,
                    cs.fecha_programada::DATE as fecha_programada,
                    CAST(cs.hora_inicio AS TEXT) as hora_inicio,
                    cs.numero_sesion_semanal,
                    cs.estado as estado_sesion
                FROM asistencia_sesiones a
                JOIN cronograma_sesiones cs ON a.id_cronograma = cs.id
                JOIN sesion_terapia st ON cs.id_sesion = st.id
                JOIN paciente pac ON a.id_paciente = pac.id
                JOIN persona p ON pac.id_persona = p.id
                WHERE st.id = %s
                ORDER BY cs.fecha_programada, cs.hora_inicio, p.apellido, p.nombre
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
                    a.id_cronograma,
                    a.id_paciente,
                    a.asistio,
                    a.llegada_tardanza_minutos,
                    a.estado_asistencia,
                    a.observaciones_terapeuta,
                    a.progreso_observado,
                    a.tareas_asignadas,
                    a.objetivos_trabajados,
                    a.fecha_creacion as fecha_registro,
                    cs.fecha_programada,
                    CAST(cs.hora_inicio AS TEXT) as hora_inicio,
                    cs.numero_sesion_semanal,
                    st.objetivo_general as sesion_titulo,
                    st.codigo_sesion,
                    CONCAT(p_ter.nombre, ' ', p_ter.apellido) as terapeuta_nombre,
                    e.nombre as especialidad_nombre
                FROM asistencia_sesiones a
                JOIN cronograma_sesiones cs ON a.id_cronograma = cs.id
                JOIN sesion_terapia st ON cs.id_sesion = st.id
                JOIN personal per ON st.id_terapeuta = per.id
                JOIN persona p_ter ON per.id_persona = p_ter.id
                JOIN especialidad e ON st.id_especialidad = e.id
                WHERE a.id_paciente = %s
                ORDER BY cs.fecha_programada DESC, cs.hora_inicio DESC
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
                    COUNT(DISTINCT a.id_paciente) as pacientes_unicos_registrados,
                    COUNT(DISTINCT cs.id) as sesiones_con_asistencia_registrada
                FROM cronograma_sesiones cs
                LEFT JOIN asistencia_sesiones a ON cs.id = a.id_cronograma
                WHERE cs.id_sesion = %s
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
            query = "SELECT COUNT(*) as count FROM asistencia_sesiones WHERE id_cronograma = %s"
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
            
            numero_sesion_semanal = SesionTerapiaComponent._get_ultimo_numero_sesion_semanal(sesion_id) + 1
            
            while fecha_actual <= fecha_fin:
                if fecha_actual.weekday() in dias_sesion:
                    # Crear sesión en el cronograma
                    cronograma_data = {
                        'id_sesion': sesion_id,
                        'numero_sesion_semanal': numero_sesion_semanal,
                        'fecha_programada': fecha_actual,
                        'hora_inicio': sesion_data['hora_inicio'],
                        'estado': 'programada',
                        'usuario_creacion': sesion_data.get('usuario_modificacion', 1)
                    }
                    
                    insert_query = """
                        INSERT INTO cronograma_sesiones 
                        (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    # Calculate hora_fin based on hora_inicio + duracion
                    from datetime import datetime, timedelta
                    hora_inicio = cronograma_data['hora_inicio']
                    duracion_minutos = sesion_data.get('duracion_minutos', 45)
                    
                    if isinstance(hora_inicio, str):
                        hora_inicio_dt = datetime.strptime(hora_inicio, '%H:%M:%S').time()
                    else:
                        hora_inicio_dt = hora_inicio
                        
                    # Convert to datetime to add minutes
                    dt_inicio = datetime.combine(datetime.today(), hora_inicio_dt)
                    dt_fin = dt_inicio + timedelta(minutes=duracion_minutos)
                    hora_fin = dt_fin.time()
                    
                    params = (
                        cronograma_data['id_sesion'],
                        cronograma_data['numero_sesion_semanal'],
                        cronograma_data['fecha_programada'],
                        cronograma_data['hora_inicio'],
                        hora_fin,
                        cronograma_data['estado'],
                        cronograma_data['usuario_creacion']
                    )
                    
                    DataBaseHandle.ExecuteNonQuery(insert_query, params)
                    numero_sesion_semanal += 1
                
                fecha_actual += timedelta(days=1)
            
        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent._generar_cronograma_desde_fecha - Error: {str(e)}")
            raise e
    
    @staticmethod
    def _get_ultimo_numero_sesion_semanal(sesion_id):
        """Obtener el último número de sesión en el cronograma"""
        try:
            query = "SELECT COALESCE(MAX(numero_sesion_semanal), 0) as max_numero FROM cronograma_sesiones WHERE id_sesion = %s"
            result = DataBaseHandle.getRecords(query, params=(sesion_id,), size=1)
            return result.get('max_numero', 0) if result else 0
        except Exception:
            return 0

    @staticmethod
    def get_sesiones_by_centro(centro_id):
        """Obtener todas las sesiones de terapia de un centro específico"""
        try:
            query = """
                SELECT
                    st.id,
                    st.codigo_sesion,
                    st.titulo,
                    st.objetivo_general,
                    st.id_terapeuta as terapeuta_id,
                    CONCAT(p_ter.nombre, ' ', p_ter.apellido) as terapeuta_nombre,
                    st.id_especialidad as especialidad_id,
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area,
                    st.fecha_inicio,
                    st.fecha_fin,
                    st.dias_semana,
                    TO_CHAR(st.hora_inicio, 'HH24:MI') as hora_inicio,
                    TO_CHAR(st.hora_fin, 'HH24:MI') as hora_fin,
                    st.duracion_minutos,
                    st.numero_sesiones_contratadas,
                    st.costo_total,
                    st.costo_sesion as costo_por_sesion,
                    st.meses_contrato,
                    st.tipo_sesion,
                    st.estado,
                    st.fecha_creacion,
                    st.fecha_modificacion,
                    COUNT(DISTINCT sp.id_paciente) as total_pacientes,
                    COUNT(DISTINCT cs.id) as sesiones_programadas,
                    COUNT(DISTINCT CASE WHEN ass.asistio = true THEN ass.id_cronograma END) as sesiones_realizadas
                FROM sesion_terapia st
                JOIN personal per ON st.id_terapeuta = per.id
                JOIN persona p_ter ON per.id_persona = p_ter.id
                JOIN especialidad e ON st.id_especialidad = e.id
                LEFT JOIN sesion_paciente sp ON st.id = sp.id_sesion AND sp.estado = 'activo'
                LEFT JOIN cronograma_sesiones cs ON st.id = cs.id_sesion
                LEFT JOIN asistencia_sesiones ass ON cs.id = ass.id_cronograma
                WHERE st.estado != 'eliminado' AND st.id_centro = %s
                GROUP BY st.id, st.codigo_sesion, st.titulo, st.objetivo_general,
                        st.id_terapeuta, p_ter.nombre, p_ter.apellido,
                        st.id_especialidad, e.nombre, e.area,
                        st.fecha_inicio, st.fecha_fin, st.dias_semana,
                        st.hora_inicio, st.hora_fin, st.duracion_minutos,
                        st.numero_sesiones_contratadas, st.costo_total, st.costo_sesion,
                        st.meses_contrato, st.tipo_sesion, st.estado,
                        st.fecha_creacion, st.fecha_modificacion
                ORDER BY st.fecha_creacion DESC
            """

            result = DataBaseHandle.getRecords(query, (centro_id,))

            if result is not None:
                HandleLogs.write_log(f"SesionTerapiaComponent.get_sesiones_by_centro - {len(result)} sesiones encontradas para centro {centro_id}")
                return result
            else:
                HandleLogs.write_error("SesionTerapiaComponent.get_sesiones_by_centro - Error en consulta")
                return []

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_sesiones_by_centro - Error: {str(e)}")
            return []

    @staticmethod
    def get_sesiones_by_terapeuta(terapeuta_id, centro_id):
        """Obtener sesiones de terapia asignadas a un terapeuta específico"""
        try:
            query = """
                SELECT
                    st.id,
                    st.codigo_sesion,
                    st.titulo,
                    st.objetivo_general,
                    st.id_terapeuta as terapeuta_id,
                    CONCAT(p_ter.nombre, ' ', p_ter.apellido) as terapeuta_nombre,
                    st.id_especialidad as especialidad_id,
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area,
                    st.fecha_inicio,
                    st.fecha_fin,
                    st.dias_semana,
                    TO_CHAR(st.hora_inicio, 'HH24:MI') as hora_inicio,
                    TO_CHAR(st.hora_fin, 'HH24:MI') as hora_fin,
                    st.duracion_minutos,
                    st.numero_sesiones_contratadas,
                    st.costo_total,
                    st.costo_sesion as costo_por_sesion,
                    st.meses_contrato,
                    st.tipo_sesion,
                    st.estado,
                    st.fecha_creacion,
                    st.fecha_modificacion,
                    COUNT(DISTINCT sp.id_paciente) as total_pacientes,
                    COUNT(DISTINCT cs.id) as sesiones_programadas,
                    COUNT(DISTINCT CASE WHEN ass.asistio = true THEN ass.id_cronograma END) as sesiones_realizadas
                FROM sesion_terapia st
                JOIN personal per ON st.id_terapeuta = per.id
                JOIN persona p_ter ON per.id_persona = p_ter.id
                JOIN especialidad e ON st.id_especialidad = e.id
                LEFT JOIN sesion_paciente sp ON st.id = sp.id_sesion AND sp.estado = 'activo'
                LEFT JOIN cronograma_sesiones cs ON st.id = cs.id_sesion
                LEFT JOIN asistencia_sesiones ass ON cs.id = ass.id_cronograma
                WHERE st.estado != 'eliminado'
                    AND st.id_terapeuta = %s
                    AND st.id_centro = %s
                GROUP BY st.id, st.codigo_sesion, st.titulo, st.objetivo_general,
                        st.id_terapeuta, p_ter.nombre, p_ter.apellido,
                        st.id_especialidad, e.nombre, e.area,
                        st.fecha_inicio, st.fecha_fin, st.dias_semana,
                        st.hora_inicio, st.hora_fin, st.duracion_minutos,
                        st.numero_sesiones_contratadas, st.costo_total, st.costo_sesion,
                        st.meses_contrato, st.tipo_sesion, st.estado,
                        st.fecha_creacion, st.fecha_modificacion
                ORDER BY st.fecha_creacion DESC
            """

            result = DataBaseHandle.getRecords(query, (terapeuta_id, centro_id))

            if result is not None:
                HandleLogs.write_log(f"SesionTerapiaComponent.get_sesiones_by_terapeuta - {len(result)} sesiones encontradas para terapeuta {terapeuta_id} en centro {centro_id}")
                return result
            else:
                HandleLogs.write_error("SesionTerapiaComponent.get_sesiones_by_terapeuta - Error en consulta")
                return []

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_sesiones_by_terapeuta - Error: {str(e)}")
            return []

    @staticmethod
    def get_terapeutas_disponibles_by_centro(centro_id):
        """Obtener terapeutas disponibles filtrados por centro específico"""
        try:
            HandleLogs.write_log(f"SesionTerapiaComponent.get_terapeutas_disponibles_by_centro - Iniciando para centro {centro_id}")

            query = """
            SELECT DISTINCT
                p.id,
                p.id_persona,
                CONCAT(pe.nombre, ' ', pe.apellido) as nombre_completo,
                pe.nombre,
                pe.apellido,
                pe.cedula,
                pe.telefono,
                pe.correo,
                p.cargo as titulo_profesional,
                p.cargo,
                p.estado,
                p.id_centro,
                c.nombre as centro_nombre,
                u.id as usuario_id,
                r.nombre as rol_usuario,
                -- Especialidad principal
                e.id as especialidad_id,
                e.nombre as especialidad_nombre
            FROM personal p
            INNER JOIN persona pe ON p.id_persona = pe.id
            LEFT JOIN usuario u ON pe.id = u.id_persona
            LEFT JOIN rol r ON u.id_rol = r.id
            LEFT JOIN centros c ON p.id_centro = c.id
            INNER JOIN personal_especialidades pes ON p.id = pes.id_personal
            INNER JOIN especialidad e ON pes.id_especialidad = e.id
            WHERE p.estado = 'activo'
            AND pes.estado = 'activo'
            AND e.area = 'Especialidad terapéutica'
            AND p.id_centro = %s
            ORDER BY pe.nombre, pe.apellido
            """

            result = DataBaseHandle.getRecords(query, (centro_id,))

            if result:
                terapeutas = []
                if isinstance(result, dict):
                    result = [result]

                for persona in result:
                    terapeuta = {
                        'id': persona['id'],
                        'id_persona': persona['id_persona'],
                        'nombre_completo': persona['nombre_completo'],
                        'nombre': persona['nombre'],
                        'apellido': persona['apellido'],
                        'cedula': persona['cedula'],
                        'telefono': persona['telefono'],
                        'correo': persona['correo'],
                        'titulo_profesional': persona['titulo_profesional'],
                        'cargo': persona['cargo'],
                        'estado': persona['estado'],
                        'id_centro': persona['id_centro'],
                        'centro_nombre': persona['centro_nombre'],
                        'usuario_id': persona['usuario_id'],
                        'rol_usuario': persona['rol_usuario'],
                        'especialidad_id': persona['especialidad_id'],
                        'especialidad_nombre': persona['especialidad_nombre']
                    }
                    terapeutas.append(terapeuta)

                HandleLogs.write_log(f"SesionTerapiaComponent.get_terapeutas_disponibles_by_centro - {len(terapeutas)} terapeutas encontrados para centro {centro_id}")
                return terapeutas
            else:
                HandleLogs.write_log(f"SesionTerapiaComponent.get_terapeutas_disponibles_by_centro - No se encontraron terapeutas para centro {centro_id}")
                return []

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_terapeutas_disponibles_by_centro - Error: {str(e)}")
            raise Exception(f"Error al obtener terapeutas del centro: {str(e)}")

    @staticmethod
    def get_pacientes_disponibles_by_centro(centro_id):
        """Obtener pacientes disponibles filtrados por centro específico"""
        try:
            HandleLogs.write_log(f"SesionTerapiaComponent.get_pacientes_disponibles_by_centro - Iniciando para centro {centro_id}")

            query = """
            SELECT DISTINCT
                pac.id,
                pac.id_persona,
                pac.fecha_ingreso,
                pac.estado_tratamiento,
                pac.observaciones,
                pac.estado,
                pac.id_centro,
                -- Información del paciente (persona)
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.nombre,
                p.apellido,
                p.cedula,
                p.telefono,
                p.correo,
                p.direccion,
                p.fecha_nacimiento,
                -- Información del tutor
                t.id as tutor_id,
                t.parentesco,
                CONCAT(pt.nombre, ' ', pt.apellido) as nombre_tutor,
                pt.telefono as telefono_tutor,
                pt.correo as correo_tutor,
                -- Información del centro
                c.nombre as centro_nombre
            FROM paciente pac
            INNER JOIN persona p ON pac.id_persona = p.id
            INNER JOIN tutor t ON pac.id_tutor = t.id
            INNER JOIN persona pt ON t.id_persona = pt.id
            LEFT JOIN centros c ON pac.id_centro = c.id
            WHERE pac.estado = 'activo'
            AND pac.id_centro = %s
            ORDER BY p.nombre, p.apellido
            """

            result = DataBaseHandle.getRecords(query, (centro_id,))

            if result:
                pacientes = []
                if isinstance(result, dict):
                    result = [result]

                for paciente_data in result:
                    paciente = {
                        'id': paciente_data['id'],
                        'id_persona': paciente_data['id_persona'],
                        'nombre_completo': paciente_data['nombre_completo'],
                        'nombre': paciente_data['nombre'],
                        'apellido': paciente_data['apellido'],
                        'cedula': paciente_data['cedula'],
                        'telefono': paciente_data['telefono'],
                        'correo': paciente_data['correo'],
                        'direccion': paciente_data['direccion'],
                        'fecha_nacimiento': paciente_data['fecha_nacimiento'].isoformat() if paciente_data['fecha_nacimiento'] else None,
                        'fecha_ingreso': paciente_data['fecha_ingreso'].isoformat() if paciente_data['fecha_ingreso'] else None,
                        'estado_tratamiento': paciente_data['estado_tratamiento'],
                        'observaciones': paciente_data['observaciones'],
                        'estado': paciente_data['estado'],
                        'id_centro': paciente_data['id_centro'],
                        'centro_nombre': paciente_data['centro_nombre'],
                        'tutor': {
                            'id': paciente_data['tutor_id'],
                            'parentesco': paciente_data['parentesco'],
                            'nombre_completo': paciente_data['nombre_tutor'],
                            'telefono': paciente_data['telefono_tutor'],
                            'correo': paciente_data['correo_tutor']
                        }
                    }
                    pacientes.append(paciente)

                HandleLogs.write_log(f"SesionTerapiaComponent.get_pacientes_disponibles_by_centro - {len(pacientes)} pacientes encontrados para centro {centro_id}")
                return pacientes
            else:
                HandleLogs.write_log(f"SesionTerapiaComponent.get_pacientes_disponibles_by_centro - No se encontraron pacientes para centro {centro_id}")
                return []

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_pacientes_disponibles_by_centro - Error: {str(e)}")
            raise Exception(f"Error al obtener pacientes del centro: {str(e)}")

    # ============================================
    # MÉTODOS PARA ENLACES PÚBLICOS
    # ============================================

    @staticmethod
    def generar_token_publico(sesion_id, duracion_horas, descripcion, usuario_creacion):
        """Generar un token público temporal para acceder a información de la sesión"""
        try:
            import secrets
            from datetime import datetime, timedelta

            # Generar token seguro - 48 bytes = ~64 caracteres en base64url
            token = secrets.token_urlsafe(48)

            # Calcular fecha de expiración
            fecha_expiracion = datetime.now() + timedelta(hours=duracion_horas)

            # Generar nombre de enlace
            nombre_enlace = f"Enlace-{sesion_id}-{datetime.now().strftime('%Y%m%d')}"

            # Insertar el token incluyendo nombre_enlace (campo NOT NULL)
            insert_query = """
                INSERT INTO tokens_publicos_sesion
                (token, id_sesion, nombre_enlace, descripcion, fecha_expiracion, usuario_creacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (token, sesion_id, nombre_enlace, descripcion, fecha_expiracion, usuario_creacion)

            # Usar ExecuteNonQuery para INSERT
            rows_affected = DataBaseHandle.ExecuteNonQuery(insert_query, params)
            HandleLogs.write_log(f"SesionTerapiaComponent.generar_token_publico - rows_affected: {rows_affected}")

            # Verificar si el token se insertó correctamente
            verify_query = """
                SELECT COUNT(*) as count FROM tokens_publicos_sesion WHERE token = %s
            """
            verify_result = DataBaseHandle.getRecords(verify_query, (token,))
            token_exists = verify_result and verify_result[0]['count'] > 0

            HandleLogs.write_log(f"SesionTerapiaComponent.generar_token_publico - Token exists: {token_exists}")

            if token_exists:
                # Obtener el token recién insertado
                select_query = """
                    SELECT token, nombre_enlace, descripcion, fecha_expiracion, estado
                    FROM tokens_publicos_sesion
                    WHERE token = %s
                """
                result = DataBaseHandle.getRecords(select_query, (token,))
                if result:
                    token_data = result[0]
                    HandleLogs.write_log(f"SesionTerapiaComponent.generar_token_publico - Token generado para sesión {sesion_id}")

                    return {
                        'token': token_data['token'],
                        'nombre_enlace': token_data['nombre_enlace'],
                        'descripcion': token_data['descripcion'],
                        'url_publica': f"/api/sesion-publica/{token_data['token']}",
                        'fecha_expiracion': token_data['fecha_expiracion'].isoformat() if isinstance(token_data['fecha_expiracion'], datetime) else str(token_data['fecha_expiracion']),
                        'estado': token_data['estado'],
                        'duracion_horas': duracion_horas
                    }
                else:
                    raise Exception("Error al obtener el token creado")
            else:
                raise Exception("Error al crear el token en la base de datos")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.generar_token_publico - Error: {str(e)}")
            raise Exception(f"Error al generar token público: {str(e)}")

    @staticmethod
    def obtener_tokens_publicos(sesion_id):
        """Obtener tokens públicos activos para una sesión"""
        try:
            HandleLogs.write_log(f"SesionTerapiaComponent.obtener_tokens_publicos - Iniciando para sesión {sesion_id}")

            query = """
                SELECT
                    token,
                    descripcion,
                    fecha_creacion,
                    fecha_expiracion,
                    estado,
                    CASE
                        WHEN fecha_expiracion < CURRENT_TIMESTAMP THEN 'expirado'
                        WHEN estado = 'inactivo' THEN 'inactivo'
                        ELSE 'vigente'
                    END as estado_calculado
                FROM tokens_publicos_sesion
                WHERE id_sesion = %s AND estado = 'activo'
                ORDER BY fecha_creacion DESC
            """
            params = (sesion_id,)

            HandleLogs.write_log(f"SesionTerapiaComponent.obtener_tokens_publicos - Ejecutando query para sesión {sesion_id}")
            result = DataBaseHandle.getRecords(query, params)
            HandleLogs.write_log(f"SesionTerapiaComponent.obtener_tokens_publicos - Query ejecutado, result: {result}")

            if result:
                enlaces = []
                for i, row in enumerate(result):
                    try:
                        # Formatear fechas de manera segura
                        fecha_creacion_str = str(row['fecha_creacion'])
                        fecha_expiracion_str = str(row['fecha_expiracion'])

                        # Intentar formato ISO si es datetime
                        try:
                            if isinstance(row['fecha_creacion'], datetime):
                                fecha_creacion_str = row['fecha_creacion'].isoformat()
                        except:
                            pass

                        try:
                            if isinstance(row['fecha_expiracion'], datetime):
                                fecha_expiracion_str = row['fecha_expiracion'].isoformat()
                        except:
                            pass

                        enlace = {
                            'token': str(row['token']),
                            'nombre_enlace': f"Enlace-{sesion_id}-{i+1}",
                            'url_publica': f"/api/sesion-publica/{row['token']}",
                            'descripcion': str(row['descripcion'] or 'Sin descripción'),
                            'fecha_creacion': fecha_creacion_str,
                            'fecha_expiracion': fecha_expiracion_str,
                            'estado': str(row['estado']),
                            'estado_calculado': str(row['estado_calculado'])
                        }
                        enlaces.append(enlace)
                        HandleLogs.write_log(f"SesionTerapiaComponent.obtener_tokens_publicos - Procesado enlace {i+1}: {enlace['descripcion']}")
                    except Exception as row_error:
                        HandleLogs.write_error(f"SesionTerapiaComponent.obtener_tokens_publicos - Error procesando fila {i}: {str(row_error)}")
                        continue

                HandleLogs.write_log(f"SesionTerapiaComponent.obtener_tokens_publicos - {len(enlaces)} tokens encontrados para sesión {sesion_id}")
                return enlaces
            else:
                HandleLogs.write_log(f"SesionTerapiaComponent.obtener_tokens_publicos - No se encontraron tokens para sesión {sesion_id}")
                return []

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.obtener_tokens_publicos - Error: {str(e)}")
            return []  # Retornar lista vacía en lugar de lanzar excepción

    @staticmethod
    def invalidar_token_publico(token, usuario_modificacion):
        """Invalidar un token público específico"""
        try:
            # Primero verificar que el token existe y está activo
            check_query = """
                SELECT id, token
                FROM tokens_publicos_sesion
                WHERE token = %s AND estado = 'activo'
            """
            existing_token = DataBaseHandle.getRecords(check_query, (token,))

            if not existing_token:
                HandleLogs.write_log(f"SesionTerapiaComponent.invalidar_token_publico - Token no encontrado o ya inactivo: {token[:10]}...")
                raise Exception("Token no encontrado o ya está inactivo")

            # Usar ExecuteNonQuery para el UPDATE (patrón correcto del proyecto)
            update_query = """
                UPDATE tokens_publicos_sesion
                SET estado = 'inactivo',
                    usuario_modificacion = %s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE token = %s AND estado = 'activo'
            """
            params = (usuario_modificacion, token)

            rows_affected = DataBaseHandle.ExecuteNonQuery(update_query, params)
            if rows_affected and rows_affected > 0:
                HandleLogs.write_log(f"SesionTerapiaComponent.invalidar_token_publico - Token invalidado: {token[:10]}...")
                return {'success': True, 'message': 'Token invalidado exitosamente'}
            else:
                HandleLogs.write_log(f"SesionTerapiaComponent.invalidar_token_publico - No se pudo invalidar el token: {token[:10]}...")
                raise Exception("No se pudo invalidar el token")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.invalidar_token_publico - Error: {str(e)}")
            raise Exception(f"Error al invalidar token: {str(e)}")

    @staticmethod
    def obtener_sesion_por_token_publico(token):
        """Obtener información pública de una sesión usando un token válido"""
        try:
            # Verificar token y obtener información de la sesión
            query = """
                SELECT
                    st.id as sesion_id,
                    st.codigo_sesion,
                    st.titulo,
                    st.objetivo_general,
                    CONCAT(p_ter.nombre, ' ', p_ter.apellido) as terapeuta_nombre,
                    e.nombre as especialidad_nombre,
                    e.area as especialidad_area,
                    st.fecha_inicio,
                    st.fecha_fin,
                    st.dias_semana,
                    TO_CHAR(st.hora_inicio, 'HH24:MI') as hora_inicio,
                    TO_CHAR(st.hora_fin, 'HH24:MI') as hora_fin,
                    st.duracion_minutos,
                    st.tipo_sesion,
                    st.estado,
                    tps.descripcion as enlace_descripcion,
                    tps.fecha_expiracion,
                    COUNT(DISTINCT sp.id_paciente) as total_pacientes,
                    COUNT(DISTINCT cs.id) as sesiones_programadas,
                    COUNT(DISTINCT CASE WHEN ass.asistio = true THEN ass.id_cronograma END) as sesiones_realizadas,
                    ROUND(
                        (COUNT(DISTINCT CASE WHEN ass.asistio = true THEN ass.id_cronograma END) * 100.0) /
                        NULLIF(COUNT(DISTINCT cs.id), 0), 2
                    ) as porcentaje_asistencia
                FROM tokens_publicos_sesion tps
                JOIN sesion_terapia st ON tps.id_sesion = st.id
                JOIN personal per ON st.id_terapeuta = per.id
                JOIN persona p_ter ON per.id_persona = p_ter.id
                JOIN especialidad e ON st.id_especialidad = e.id
                LEFT JOIN sesion_paciente sp ON st.id = sp.id_sesion AND sp.estado = 'activo'
                LEFT JOIN cronograma_sesiones cs ON st.id = cs.id_sesion
                LEFT JOIN asistencia_sesiones ass ON cs.id = ass.id_cronograma
                WHERE tps.token = %s
                    AND tps.activo = TRUE
                    AND tps.fecha_expiracion > CURRENT_TIMESTAMP
                GROUP BY st.id, st.codigo_sesion, st.titulo, st.objetivo_general,
                        p_ter.nombre, p_ter.apellido, e.nombre, e.area, st.fecha_inicio,
                        st.fecha_fin, st.dias_semana, st.hora_inicio, st.hora_fin,
                        st.duracion_minutos, st.tipo_sesion, st.estado, tps.descripcion, tps.fecha_expiracion
            """
            params = (token,)

            result = DataBaseHandle.getRecords(query, params)
            if result:
                sesion_data = result[0]

                # Obtener cronograma de sesiones (información pública)
                cronograma_query = """
                    SELECT
                        cs.fecha_programada,
                        cs.hora_inicio,
                        cs.hora_fin,
                        cs.estado,
                        cs.semana_numero,
                        cs.numero_sesion_semanal,
                        CASE
                            WHEN EXISTS (
                                SELECT 1 FROM asistencia_sesiones ass
                                WHERE ass.id_cronograma = cs.id AND ass.asistio = true
                            ) THEN 'realizada'
                            ELSE 'pendiente'
                        END as estado_asistencia
                    FROM cronograma_sesiones cs
                    WHERE cs.id_sesion = %s
                    ORDER BY cs.fecha_programada ASC, cs.hora_inicio ASC
                """
                cronograma_result = DataBaseHandle.getRecords(cronograma_query, (sesion_data['sesion_id'],))

                # Formatear cronograma
                cronograma = []
                if cronograma_result:
                    for row in cronograma_result:
                        sesion = {
                            'fecha': row['fecha_programada'].isoformat() if isinstance(row['fecha_programada'], (date, datetime)) else str(row['fecha_programada']),
                            'hora_inicio': str(row['hora_inicio']) if row['hora_inicio'] else None,
                            'hora_fin': str(row['hora_fin']) if row['hora_fin'] else None,
                            'estado': row['estado'],
                            'estado_asistencia': row['estado_asistencia'],
                            'semana': row['semana_numero'],
                            'sesion_semanal': row['numero_sesion_semanal']
                        }
                        cronograma.append(sesion)

                # Formatear respuesta pública (sin información sensible)
                response_data = {
                    'sesion': {
                        'titulo': sesion_data['titulo'],
                        'objetivo_general': sesion_data['objetivo_general'],
                        'terapeuta': sesion_data['terapeuta_nombre'],
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
                        'total_pacientes': int(sesion_data['total_pacientes']) if sesion_data['total_pacientes'] else 0,
                        'sesiones_programadas': int(sesion_data['sesiones_programadas']) if sesion_data['sesiones_programadas'] else 0,
                        'sesiones_realizadas': int(sesion_data['sesiones_realizadas']) if sesion_data['sesiones_realizadas'] else 0,
                        'porcentaje_asistencia': float(sesion_data['porcentaje_asistencia']) if sesion_data['porcentaje_asistencia'] else 0
                    },
                    'cronograma': cronograma,
                    'enlace_info': {
                        'descripcion': sesion_data['enlace_descripcion'],
                        'fecha_expiracion': sesion_data['fecha_expiracion'].isoformat() if isinstance(sesion_data['fecha_expiracion'], datetime) else str(sesion_data['fecha_expiracion'])
                    }
                }

                HandleLogs.write_log(f"SesionTerapiaComponent.obtener_sesion_por_token_publico - Información obtenida para sesión {sesion_data['sesion_id']}")
                return response_data
            else:
                HandleLogs.write_log(f"SesionTerapiaComponent.obtener_sesion_por_token_publico - Token inválido o expirado: {token[:10]}...")
                return None

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.obtener_sesion_por_token_publico - Error: {str(e)}")
            raise Exception(f"Error al obtener sesión por token: {str(e)}")

    @staticmethod
    def get_estadisticas_sesion(sesion_id):
        """Obtener estadisticas de cronogramas de una sesion"""
        try:
            query = """
                SELECT
                    COUNT(*) as total_cronogramas,
                    COUNT(CASE WHEN estado = 'completada' THEN 1 END) as cronogramas_completados,
                    COUNT(CASE WHEN estado = 'programada' THEN 1 END) as cronogramas_programados,
                    COUNT(CASE WHEN estado = 'en_curso' THEN 1 END) as cronogramas_en_curso,
                    COUNT(CASE WHEN estado = 'cancelada' THEN 1 END) as cronogramas_cancelados,
                    COUNT(CASE WHEN estado = 'reprogramada' THEN 1 END) as cronogramas_reprogramados,
                    COUNT(CASE WHEN estado NOT IN ('completada', 'cancelada', 'reprogramada') THEN 1 END) as cronogramas_pendientes
                FROM cronograma_sesiones
                WHERE id_sesion = %s
                  AND estado NOT IN ('cancelada', 'reprogramada')
            """
            result = DataBaseHandle.getRecords(query, (sesion_id,))

            if result and len(result) > 0:
                stats = result[0]
                HandleLogs.write_log(f"SesionTerapiaComponent.get_estadisticas_sesion - Estadisticas de sesion {sesion_id}: {stats}")
                return stats
            else:
                return {
                    'total_cronogramas': 0,
                    'cronogramas_completados': 0,
                    'cronogramas_programados': 0,
                    'cronogramas_en_curso': 0,
                    'cronogramas_cancelados': 0,
                    'cronogramas_reprogramados': 0,
                    'cronogramas_pendientes': 0
                }

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.get_estadisticas_sesion - Error: {str(e)}")
            raise Exception(f"Error al obtener estadisticas de sesion: {str(e)}")

    @staticmethod
    def finalizar_sesion(sesion_id):
        """Finalizar manualmente una sesion de terapia"""
        try:
            # Verificar que la sesion existe y obtener su estado actual
            query_verificar = """
                SELECT id, estado, codigo_sesion
                FROM sesion_terapia
                WHERE id = %s
            """
            sesion = DataBaseHandle.getRecords(query_verificar, (sesion_id,))

            if not sesion or len(sesion) == 0:
                raise Exception(f"No se encontro la sesion con ID {sesion_id}")

            estado_actual = sesion[0]['estado']
            codigo_sesion = sesion[0]['codigo_sesion']

            # No permitir finalizar si ya esta finalizada o cancelada
            if estado_actual == 'finalizada':
                HandleLogs.write_log(f"SesionTerapiaComponent.finalizar_sesion - Sesion {codigo_sesion} ya esta finalizada")
                return {'ya_finalizada': True, 'mensaje': 'La sesion ya esta finalizada'}

            if estado_actual == 'cancelada':
                raise Exception("No se puede finalizar una sesion cancelada")

            # Actualizar estado a finalizada
            query_finalizar = """
                UPDATE sesion_terapia
                SET estado = 'finalizada',
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            DataBaseHandle.ExecuteNonQuery(query_finalizar, (sesion_id,))

            HandleLogs.write_log(f"SesionTerapiaComponent.finalizar_sesion - Sesion {codigo_sesion} (ID: {sesion_id}) marcada como finalizada manualmente")
            return {'finalizada': True, 'codigo_sesion': codigo_sesion}

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaComponent.finalizar_sesion - Error: {str(e)}")
            raise Exception(f"Error al finalizar sesion: {str(e)}")