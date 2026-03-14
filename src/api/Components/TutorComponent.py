from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class TutorComponent:

    @staticmethod
    def get_all_tutores():
        """Obtener todos los tutores con informacion completa"""
        try:
            query = """
            SELECT
                t.id,
                t.id_persona,
                p.nombre,
                p.apellido,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.cedula,
                p.telefono,
                p.correo as email,
                p.direccion,
                t.parentesco,
                t.ocupacion,
                t.direccion_empresa,
                t.telefono_empresa,
                t.nombre_empresa,
                t.estado,
                t.fecha_creacion::TEXT as fecha_creacion,
                t.fecha_modificacion::TEXT as fecha_modificacion,
                COUNT(pac.id) as total_pacientes,
                COUNT(CASE WHEN pac.estado = 'activo' THEN 1 END) as pacientes_activos
            FROM tutor t
            INNER JOIN persona p ON t.id_persona = p.id
            LEFT JOIN paciente pac ON t.id = pac.id_tutor
            GROUP BY t.id, t.id_persona, p.nombre, p.apellido, p.cedula, p.telefono, p.correo,
                     p.direccion, t.parentesco, t.ocupacion, t.direccion_empresa,
                     t.telefono_empresa, t.nombre_empresa, t.estado,
                     t.fecha_creacion, t.fecha_modificacion
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
        """Obtener un tutor por ID con informacion completa y sus pacientes"""
        try:
            query_tutor = """
            SELECT
                t.id,
                t.id_persona,
                p.nombre,
                p.apellido,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.cedula,
                p.telefono,
                p.correo as email,
                p.direccion,
                t.parentesco,
                t.ocupacion,
                t.direccion_empresa,
                t.telefono_empresa,
                t.nombre_empresa,
                t.estado,
                t.fecha_creacion::TEXT as fecha_creacion,
                t.fecha_modificacion::TEXT as fecha_modificacion
            FROM tutor t
            INNER JOIN persona p ON t.id_persona = p.id
            WHERE t.id = %s
            """

            tutor = DataBaseHandle.getRecords(query_tutor, (tutor_id,), size=1)

            if tutor:
                # Obtener pacientes del tutor
                query_pacientes = """
                SELECT
                    pac.id,
                    pac.fecha_ingreso::TEXT as fecha_ingreso,
                    pac.estado,
                    pac.codigo_paciente,
                    pp.id as persona_id,
                    CONCAT(pp.nombre, ' ', pp.apellido) as nombre_completo,
                    pp.nombre,
                    pp.apellido,
                    pp.cedula,
                    pp.fecha_nacimiento::TEXT as fecha_nacimiento
                FROM paciente pac
                INNER JOIN persona pp ON pac.id_persona = pp.id
                WHERE pac.id_tutor = %s
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
        """Crear un nuevo tutor usando una persona existente"""
        try:
            if 'id_persona' not in data or not data['id_persona']:
                return internal_response(False, None, "Debe proporcionar el ID de persona")

            persona_id = data['id_persona']

            # Verificar si la persona existe y esta activa
            persona_existente = DataBaseHandle.getRecords(
                "SELECT id, nombre, apellido, cedula FROM persona WHERE id = %s AND estado = 'activo'",
                (persona_id,), size=1
            )
            if not persona_existente:
                return internal_response(False, None, "La persona especificada no existe o no esta activa")

            # Verificar si la persona ya es tutor (activo o inactivo)
            tutor_existente = DataBaseHandle.getRecords(
                "SELECT id, estado FROM tutor WHERE id_persona = %s",
                (persona_id,), size=1
            )
            if tutor_existente:
                if tutor_existente['estado'] == 'inactivo':
                    return internal_response(False, None,
                        "Esta persona ya fue registrada como tutor pero esta inactiva. Use la opcion de reactivar")
                return internal_response(False, None, "Esta persona ya esta registrada como tutor")

            # Insertar en tutor
            insert_tutor_query = """
                INSERT INTO tutor (
                    id_persona, parentesco, ocupacion, direccion_empresa,
                    telefono_empresa, nombre_empresa, estado, usuario_creacion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """

            tutor_params = (
                persona_id,
                data['parentesco'],
                data.get('ocupacion', ''),
                data.get('direccion_empresa', ''),
                data.get('telefono_empresa', ''),
                data.get('nombre_empresa', ''),
                data.get('estado', 'activo'),
                data.get('usuario_creacion', 1)
            )

            tutor_id = DataBaseHandle.ExecuteInsert(insert_tutor_query, tutor_params)

            if tutor_id:
                new_tutor = TutorComponent.get_tutor_by_id(tutor_id)
                HandleLogs.write_log(f"TutorComponent.create_tutor - Tutor creado con ID: {tutor_id} para persona ID: {persona_id}")
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
            check_query = "SELECT id, id_persona FROM tutor WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (tutor_id,), size=1)

            if not existing:
                return internal_response(False, None, "Tutor no encontrado")

            tutor_fields = []
            tutor_params = []

            tutor_allowed = ['parentesco', 'ocupacion', 'direccion_empresa',
                             'telefono_empresa', 'nombre_empresa', 'estado',
                             'usuario_modificacion']

            for field in tutor_allowed:
                if field in data and data[field] is not None:
                    tutor_fields.append(f"{field} = %s")
                    tutor_params.append(data[field])

            if not tutor_fields:
                return internal_response(False, None, "No hay campos para actualizar")

            tutor_fields.append("fecha_modificacion = CURRENT_TIMESTAMP")
            tutor_params.append(tutor_id)

            tutor_query = f"""
                UPDATE tutor
                SET {', '.join(tutor_fields)}
                WHERE id = %s
                """

            tutor_success = DataBaseHandle.ExecuteNonQuery(tutor_query, tutor_params)
            if not tutor_success:
                HandleLogs.write_error(f"TutorComponent.update_tutor - Error actualizando tutor {tutor_id}")
                return internal_response(False, None, "Error actualizando datos de tutor")

            updated_tutor = TutorComponent.get_tutor_by_id(tutor_id)
            HandleLogs.write_log(f"TutorComponent.update_tutor - Tutor {tutor_id} actualizado")
            return internal_response(True, updated_tutor['data'], "Tutor actualizado exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.update_tutor - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def deactivate_tutor(tutor_id):
        """Desactivar tutor (eliminacion logica)"""
        try:
            check_query = "SELECT id, estado FROM tutor WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (tutor_id,), size=1)

            if not existing:
                return internal_response(False, None, "Tutor no encontrado")

            if existing['estado'] == 'inactivo':
                return internal_response(False, None, "Tutor ya esta inactivo")

            # Verificar si tiene pacientes activos
            patients_check = """
                SELECT COUNT(*) as total
                FROM paciente
                WHERE id_tutor = %s AND estado = 'activo'
            """
            active_patients = DataBaseHandle.getRecords(patients_check, (tutor_id,), size=1)

            if active_patients and active_patients['total'] > 0:
                return internal_response(False, None,
                    f"No se puede desactivar el tutor porque tiene {active_patients['total']} paciente(s) activo(s)")

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
    def reactivate_tutor(tutor_id):
        """Reactivar tutor previamente desactivado"""
        try:
            check_query = "SELECT id, estado FROM tutor WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (tutor_id,), size=1)

            if not existing:
                return internal_response(False, None, "Tutor no encontrado")

            if existing['estado'] == 'activo':
                return internal_response(False, None, "El tutor ya esta activo")

            update_query = """
                UPDATE tutor
                SET estado = 'activo', fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (tutor_id,))

            if success:
                HandleLogs.write_log(f"TutorComponent.reactivate_tutor - Tutor {tutor_id} reactivado")
                return internal_response(True, {"id": tutor_id, "estado": "activo"},
                                         "Tutor reactivado exitosamente")
            else:
                HandleLogs.write_error(f"TutorComponent.reactivate_tutor - Error reactivando tutor {tutor_id}")
                return internal_response(False, None, "Error reactivando tutor")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.reactivate_tutor - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def check_persona_es_tutor(persona_id):
        """Verificar si una persona ya esta registrada como tutor"""
        try:
            query = "SELECT id, estado FROM tutor WHERE id_persona = %s"
            existing = DataBaseHandle.getRecords(query, (persona_id,), size=1)
            result = existing is not None and bool(existing)
            return internal_response(True, result, "Consulta ejecutada")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.check_persona_es_tutor - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_tutores_activos():
        """Obtener solo tutores activos (util para combos/selects)"""
        try:
            query = """
            SELECT
                t.id,
                t.id_persona,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.nombre,
                p.apellido,
                p.cedula,
                t.parentesco,
                p.telefono,
                p.correo as email
            FROM tutor t
            INNER JOIN persona p ON t.id_persona = p.id
            WHERE t.estado = 'activo'
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
        """Obtener estadisticas de tutores"""
        try:
            query = """
            SELECT
                COUNT(*) as total_tutores,
                COUNT(CASE WHEN t.estado = 'activo' THEN 1 END) as tutores_activos,
                COUNT(CASE WHEN t.estado = 'inactivo' THEN 1 END) as tutores_inactivos,
                COALESCE(AVG(pacientes_por_tutor.total_pacientes), 0) as promedio_pacientes_por_tutor
            FROM tutor t
            LEFT JOIN (
                SELECT id_tutor, COUNT(*) as total_pacientes
                FROM paciente
                GROUP BY id_tutor
            ) pacientes_por_tutor ON t.id = pacientes_por_tutor.id_tutor
            """

            estadisticas_generales = DataBaseHandle.getRecords(query, size=1)

            # Estadisticas por parentesco
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

            # Convertir promedio Decimal a float para JSON
            if estadisticas_generales and estadisticas_generales.get('promedio_pacientes_por_tutor') is not None:
                estadisticas_generales['promedio_pacientes_por_tutor'] = float(
                    estadisticas_generales['promedio_pacientes_por_tutor']
                )

            resultado = {
                "general": estadisticas_generales,
                "por_parentesco": estadisticas_parentesco if estadisticas_parentesco else []
            }

            if estadisticas_generales is not None:
                HandleLogs.write_log("TutorComponent.get_estadisticas_tutores - Estadisticas obtenidas")
                return internal_response(True, resultado, "Estadisticas de tutores obtenidas")
            else:
                HandleLogs.write_error("TutorComponent.get_estadisticas_tutores - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.get_estadisticas_tutores - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_personas_disponibles_para_tutor():
        """Obtener personas que no estan registradas como tutores activos"""
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
            LEFT JOIN tutor t ON p.id = t.id_persona AND t.estado = 'activo'
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

    @staticmethod
    def get_tutores_by_centro(centro_id):
        """Obtener tutores filtrados por centro (basado en los pacientes que atienden)"""
        try:
            query = """
            SELECT
                t.id,
                t.id_persona,
                p.nombre,
                p.apellido,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.cedula,
                p.telefono,
                p.correo as email,
                p.direccion,
                t.parentesco,
                t.ocupacion,
                t.direccion_empresa,
                t.telefono_empresa,
                t.nombre_empresa,
                t.estado,
                t.fecha_creacion::TEXT as fecha_creacion,
                t.fecha_modificacion::TEXT as fecha_modificacion,
                COUNT(pac.id) as total_pacientes,
                COUNT(CASE WHEN pac.estado = 'activo' THEN 1 END) as pacientes_activos
            FROM tutor t
            INNER JOIN persona p ON t.id_persona = p.id
            LEFT JOIN paciente pac ON t.id = pac.id_tutor AND pac.id_centro = %s
            WHERE EXISTS (
                SELECT 1 FROM paciente pac2
                WHERE pac2.id_tutor = t.id AND pac2.id_centro = %s
            )
            GROUP BY t.id, t.id_persona, p.nombre, p.apellido, p.cedula, p.telefono, p.correo,
                     p.direccion, t.parentesco, t.ocupacion, t.direccion_empresa,
                     t.telefono_empresa, t.nombre_empresa, t.estado,
                     t.fecha_creacion, t.fecha_modificacion
            ORDER BY p.nombre, p.apellido
            """

            tutores = DataBaseHandle.getRecords(query, (centro_id, centro_id))

            if tutores is not None:
                HandleLogs.write_log(f"TutorComponent.get_tutores_by_centro - {len(tutores)} tutores encontrados para centro {centro_id}")
                return internal_response(True, tutores, "Tutores del centro obtenidos correctamente")
            else:
                HandleLogs.write_error(f"TutorComponent.get_tutores_by_centro - Error en consulta para centro {centro_id}")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.get_tutores_by_centro - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_tutores_by_personal(personal_id, centro_id):
        """Obtener tutores de pacientes asignados a un personal especifico"""
        try:
            query = """
            SELECT
                t.id,
                t.id_persona,
                p.nombre,
                p.apellido,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.cedula,
                p.telefono,
                p.correo as email,
                p.direccion,
                t.parentesco,
                t.ocupacion,
                t.direccion_empresa,
                t.telefono_empresa,
                t.nombre_empresa,
                t.estado,
                t.fecha_creacion::TEXT as fecha_creacion,
                t.fecha_modificacion::TEXT as fecha_modificacion,
                COUNT(pac_all.id) as total_pacientes,
                COUNT(CASE WHEN pac_all.estado = 'activo' THEN 1 END) as pacientes_activos
            FROM tutor t
            INNER JOIN persona p ON t.id_persona = p.id
            LEFT JOIN paciente pac_all ON t.id = pac_all.id_tutor
            WHERE EXISTS (
                SELECT 1 FROM paciente pac2
                WHERE pac2.id_tutor = t.id
                AND (
                    EXISTS (
                        SELECT 1 FROM sesion_terapia st
                        INNER JOIN sesion_paciente sp ON st.id = sp.id_sesion
                        WHERE sp.id_paciente = pac2.id
                        AND st.id_terapeuta = %s
                        AND st.id_centro = %s
                    )
                    OR EXISTS (
                        SELECT 1 FROM sesion_pedagogica sped
                        INNER JOIN sesion_estudiante se ON sped.id = se.id_sesion
                        WHERE se.id_paciente = pac2.id
                        AND sped.id_educador = %s
                        AND sped.id_centro = %s
                    )
                )
            )
            GROUP BY t.id, t.id_persona, p.nombre, p.apellido, p.cedula, p.telefono, p.correo,
                     p.direccion, t.parentesco, t.ocupacion, t.direccion_empresa,
                     t.telefono_empresa, t.nombre_empresa, t.estado,
                     t.fecha_creacion, t.fecha_modificacion
            ORDER BY p.nombre, p.apellido
            """

            tutores = DataBaseHandle.getRecords(query, (personal_id, centro_id, personal_id, centro_id))

            if tutores is not None:
                HandleLogs.write_log(f"TutorComponent.get_tutores_by_personal - {len(tutores)} tutores encontrados para personal {personal_id} en centro {centro_id}")
                return internal_response(True, tutores, "Tutores del personal obtenidos correctamente")
            else:
                HandleLogs.write_error(f"TutorComponent.get_tutores_by_personal - Error en consulta para personal {personal_id}")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.get_tutores_by_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")
