from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class TutorComponent:

    @staticmethod
    def get_all_tutores():
        """Obtener todos los tutores con información completa"""
        try:
            query = """
            SELECT 
                t.id,
                t.parentesco,
                t.es_contacto_emergencia,
                t.observaciones_tutor,
                t.estado,
                t.fecha_creacion,
                t.fecha_modificacion,
                p.id as persona_id,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.nombre,
                p.apellido,
                p.cedula,
                p.telefono,
                p.correo,
                p.direccion,
                p.fecha_nacimiento,
                COUNT(pac.id) as total_pacientes,
                COUNT(CASE WHEN pac.estado = 'activo' THEN 1 END) as pacientes_activos
            FROM tutor t
            INNER JOIN persona p ON t.persona_id = p.id
            LEFT JOIN paciente pac ON t.id = pac.tutor_id
            GROUP BY t.id, t.parentesco, t.es_contacto_emergencia, t.observaciones_tutor, 
                     t.estado, t.fecha_creacion, t.fecha_modificacion,
                     p.id, p.nombre, p.apellido, p.cedula, p.telefono, p.correo, 
                     p.direccion, p.fecha_nacimiento
            ORDER BY p.nombre, p.apellido
            """

            tutores = DataBaseHandle.getRecords(query)

            if tutores is not None:
                HandleLogs.write_log(f"TutorComponent.get_all_tutores - {len(tutores)} tutores encontrados")
                return internal_response(True, tutores, "Tutores obtenidos correctamente")
            else:
                HandleLogs.write_error("TutorComponent.get_all_tutores - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.get_all_tutores - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_tutor_by_id(tutor_id):
        """Obtener un tutor por ID con información completa y sus pacientes"""
        try:
            # Obtener información básica del tutor
            query_tutor = """
            SELECT 
                t.id,
                t.parentesco,
                t.es_contacto_emergencia,
                t.observaciones_tutor,
                t.estado,
                t.fecha_creacion,
                t.fecha_modificacion,
                p.id as persona_id,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.nombre,
                p.apellido,
                p.cedula,
                p.telefono,
                p.correo,
                p.direccion,
                p.fecha_nacimiento
            FROM tutor t
            INNER JOIN persona p ON t.persona_id = p.id
            WHERE t.id = %s
            """

            tutor = DataBaseHandle.getRecords(query_tutor, (tutor_id,), size=1)

            if tutor:
                # Obtener pacientes del tutor
                query_pacientes = """
                SELECT 
                    pac.id,
                    pac.fecha_ingreso,
                    pac.estado,
                    pp.id as persona_id,
                    CONCAT(pp.nombre, ' ', pp.apellido) as nombre_completo,
                    pp.nombre,
                    pp.apellido,
                    pp.cedula,
                    pp.fecha_nacimiento
                FROM paciente pac
                INNER JOIN persona pp ON pac.persona_id = pp.id
                WHERE pac.tutor_id = %s
                ORDER BY pp.nombre, pp.apellido
                """

                pacientes = DataBaseHandle.getRecords(query_pacientes, (tutor_id,))
                tutor['pacientes'] = pacientes if pacientes else []

                HandleLogs.write_log(f"TutorComponent.get_tutor_by_id - Tutor {tutor_id} encontrado")
                return internal_response(True, tutor, "Tutor encontrado")
            else:
                HandleLogs.write_log(f"TutorComponent.get_tutor_by_id - Tutor {tutor_id} no encontrado")
                return internal_response(True, None, "Tutor no encontrado")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.get_tutor_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def create_tutor(data):
        """Crear un nuevo tutor"""
        try:
            # Verificar si la persona ya está registrada como tutor
            persona_check = TutorComponent.check_persona_is_tutor(data['persona_id'])
            if persona_check['success'] and persona_check['data']:
                return internal_response(False, None, "Esta persona ya está registrada como tutor")

            # Verificar que la persona existe y está activa
            persona_exists = DataBaseHandle.getRecords(
                "SELECT id, estado FROM persona WHERE id = %s",
                (data['persona_id'],), size=1
            )

            if not persona_exists:
                return internal_response(False, None, "La persona especificada no existe")

            if persona_exists['estado'] != 'activo':
                return internal_response(False, None, "La persona debe estar activa para ser registrada como tutor")

            # Insertar nuevo tutor
            insert_query = """
                INSERT INTO tutor (
                    persona_id, parentesco, es_contacto_emergencia, 
                    observaciones_tutor, estado, usuario_creacion
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """

            params = (
                data['persona_id'],
                data['parentesco'],
                data.get('es_contacto_emergencia', False),
                data.get('observaciones_tutor', '').strip() if data.get('observaciones_tutor') else None,
                data.get('estado', 'activo'),
                data.get('usuario_creacion', 1)
            )

            new_id = DataBaseHandle.ExecuteInsert(insert_query, params)

            if new_id:
                # Obtener el tutor creado con información completa
                new_tutor = TutorComponent.get_tutor_by_id(new_id)
                HandleLogs.write_log(f"TutorComponent.create_tutor - Tutor creado con ID: {new_id}")
                return internal_response(True, new_tutor['data'], "Tutor creado exitosamente")
            else:
                HandleLogs.write_error("TutorComponent.create_tutor - Error insertando tutor")
                return internal_response(False, None, "Error creando tutor")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.create_tutor - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def update_tutor(tutor_id, data):
        """Actualizar un tutor existente"""
        try:
            # Verificar si el tutor existe
            check_query = "SELECT id FROM tutor WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (tutor_id,), size=1)

            if not existing:
                return internal_response(False, None, "Tutor no encontrado")

            # Construir query de actualización dinámicamente
            update_fields = []
            params = []

            allowed_fields = ['parentesco', 'es_contacto_emergencia', 'observaciones_tutor', 'estado',
                              'usuario_modificacion']

            for field in allowed_fields:
                if field in data and data[field] is not None:
                    if field == 'observaciones_tutor':
                        if data[field].strip():
                            update_fields.append(f"{field} = %s")
                            params.append(data[field].strip())
                        else:
                            update_fields.append(f"{field} = %s")
                            params.append(None)
                    else:
                        update_fields.append(f"{field} = %s")
                        params.append(data[field])

            if not update_fields:
                return internal_response(False, None, "No hay campos para actualizar")

            # Agregar fecha de modificación
            update_fields.append("fecha_modificacion = CURRENT_TIMESTAMP")

            # Agregar ID del tutor al final
            params.append(tutor_id)

            update_query = f"""
                UPDATE tutor 
                SET {', '.join(update_fields)}
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, params)

            if success:
                # Obtener datos actualizados
                updated_tutor = TutorComponent.get_tutor_by_id(tutor_id)
                HandleLogs.write_log(f"TutorComponent.update_tutor - Tutor {tutor_id} actualizado")
                return internal_response(True, updated_tutor['data'], "Tutor actualizado exitosamente")
            else:
                HandleLogs.write_error(f"TutorComponent.update_tutor - Error actualizando tutor {tutor_id}")
                return internal_response(False, None, "Error actualizando tutor")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.update_tutor - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def deactivate_tutor(tutor_id):
        """Desactivar tutor (eliminación lógica)"""
        try:
            # Verificar si el tutor existe
            check_query = "SELECT id, estado FROM tutor WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (tutor_id,), size=1)

            if not existing:
                return internal_response(False, None, "Tutor no encontrado")

            if existing['estado'] == 'inactivo':
                return internal_response(False, None, "Tutor ya está inactivo")

            # Verificar si tiene pacientes activos
            patients_check = """
                SELECT COUNT(*) as total 
                FROM paciente 
                WHERE tutor_id = %s AND estado = 'activo'
            """
            active_patients = DataBaseHandle.getRecords(patients_check, (tutor_id,), size=1)

            if active_patients and active_patients['total'] > 0:
                return internal_response(False, None,
                                         f"No se puede desactivar el tutor porque tiene {active_patients['total']} paciente(s) activo(s)")

            # Desactivar tutor
            update_query = """
                UPDATE tutor 
                SET estado = 'inactivo', fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (tutor_id,))

            if success:
                HandleLogs.write_log(f"TutorComponent.deactivate_tutor - Tutor {tutor_id} desactivado")
                return internal_response(True, {"id": tutor_id, "estado": "inactivo"},
                                         "Tutor desactivado exitosamente")
            else:
                HandleLogs.write_error(f"TutorComponent.deactivate_tutor - Error desactivando tutor {tutor_id}")
                return internal_response(False, None, "Error desactivando tutor")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.deactivate_tutor - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def check_persona_is_tutor(persona_id, exclude_id=None):
        """Verificar si una persona ya está registrada como tutor"""
        try:
            if exclude_id:
                query = "SELECT id FROM tutor WHERE persona_id = %s AND id != %s"
                params = (persona_id, exclude_id)
            else:
                query = "SELECT id FROM tutor WHERE persona_id = %s"
                params = (persona_id,)

            existing = DataBaseHandle.getRecords(query, params, size=1)
            return internal_response(True, existing is not None, "Consulta ejecutada")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.check_persona_is_tutor - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_tutores_activos():
        """Obtener solo tutores activos (útil para combos/selects)"""
        try:
            query = """
            SELECT 
                t.id,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                t.parentesco,
                p.telefono,
                p.correo,
                t.es_contacto_emergencia
            FROM tutor t
            INNER JOIN persona p ON t.persona_id = p.id
            WHERE t.estado = 'activo' AND p.estado = 'activo'
            ORDER BY p.nombre, p.apellido
            """

            tutores = DataBaseHandle.getRecords(query)

            if tutores is not None:
                HandleLogs.write_log(f"TutorComponent.get_tutores_activos - {len(tutores)} tutores activos encontrados")
                return internal_response(True, tutores, "Tutores activos obtenidos")
            else:
                HandleLogs.write_error("TutorComponent.get_tutores_activos - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.get_tutores_activos - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_estadisticas_tutores():
        """Obtener estadísticas de tutores"""
        try:
            query = """
            SELECT 
                COUNT(*) as total_tutores,
                COUNT(CASE WHEN t.estado = 'activo' THEN 1 END) as tutores_activos,
                COUNT(CASE WHEN t.estado = 'inactivo' THEN 1 END) as tutores_inactivos,
                COUNT(CASE WHEN t.es_contacto_emergencia = true THEN 1 END) as contactos_emergencia,
                AVG(pacientes_por_tutor.total_pacientes) as promedio_pacientes_por_tutor
            FROM tutor t
            LEFT JOIN (
                SELECT tutor_id, COUNT(*) as total_pacientes
                FROM paciente
                GROUP BY tutor_id
            ) pacientes_por_tutor ON t.id = pacientes_por_tutor.tutor_id
            """

            estadisticas_generales = DataBaseHandle.getRecords(query, size=1)

            # Estadísticas por parentesco
            query_parentesco = """
            SELECT 
                parentesco,
                COUNT(*) as total,
                COUNT(CASE WHEN estado = 'activo' THEN 1 END) as activos
            FROM tutor
            GROUP BY parentesco
            ORDER BY total DESC
            """

            estadisticas_parentesco = DataBaseHandle.getRecords(query_parentesco)

            resultado = {
                "general": estadisticas_generales,
                "por_parentesco": estadisticas_parentesco if estadisticas_parentesco else []
            }

            if estadisticas_generales is not None:
                HandleLogs.write_log("TutorComponent.get_estadisticas_tutores - Estadísticas obtenidas")
                return internal_response(True, resultado, "Estadísticas de tutores obtenidas")
            else:
                HandleLogs.write_error("TutorComponent.get_estadisticas_tutores - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.get_estadisticas_tutores - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_personas_disponibles_para_tutor():
        """Obtener personas que no están registradas como tutores"""
        try:
            query = """
            SELECT 
                p.id,
                p.nombre,
                p.apellido,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.cedula,
                p.telefono,
                p.correo
            FROM persona p
            LEFT JOIN tutor t ON p.id = t.persona_id
            WHERE t.id IS NULL AND p.estado = 'activo'
            ORDER BY p.nombre, p.apellido
            """

            personas = DataBaseHandle.getRecords(query)

            if personas is not None:
                HandleLogs.write_log(
                    f"TutorComponent.get_personas_disponibles_para_tutor - {len(personas)} personas disponibles")
                return internal_response(True, personas, "Personas disponibles para tutor obtenidas")
            else:
                HandleLogs.write_error("TutorComponent.get_personas_disponibles_para_tutor - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.get_personas_disponibles_para_tutor - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")