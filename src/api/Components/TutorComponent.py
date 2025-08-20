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
                t.nombre,
                t.apellido,
                CONCAT(t.nombre, ' ', t.apellido) as nombre_completo,
                t.cedula,
                t.telefono,
                t.email,
                t.direccion,
                t.parentesco,
                t.ocupacion,
                t.direccion_empresa,
                t.telefono_empresa,
                t.nombre_empresa,
                t.estado,
                t.fecha_creacion,
                t.fecha_modificacion,
                COUNT(pac.id) as total_pacientes,
                COUNT(CASE WHEN pac.estado = 'activo' THEN 1 END) as pacientes_activos
            FROM tutor t
            LEFT JOIN paciente pac ON t.id = pac.id_tutor
            GROUP BY t.id, t.nombre, t.apellido, t.cedula, t.telefono, t.email, 
                     t.direccion, t.parentesco, t.ocupacion, t.direccion_empresa,
                     t.telefono_empresa, t.nombre_empresa, t.estado, 
                     t.fecha_creacion, t.fecha_modificacion
            ORDER BY t.nombre, t.apellido
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
                t.nombre,
                t.apellido,
                CONCAT(t.nombre, ' ', t.apellido) as nombre_completo,
                t.cedula,
                t.telefono,
                t.email,
                t.direccion,
                t.parentesco,
                t.ocupacion,
                t.direccion_empresa,
                t.telefono_empresa,
                t.nombre_empresa,
                t.estado,
                t.fecha_creacion,
                t.fecha_modificacion
            FROM tutor t
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
                    pac.codigo_paciente,
                    pp.id as persona_id,
                    CONCAT(pp.nombre, ' ', pp.apellido) as nombre_completo,
                    pp.nombre,
                    pp.apellido,
                    pp.cedula,
                    pp.fecha_nacimiento
                FROM paciente pac
                INNER JOIN persona pp ON pac.persona_id = pp.id
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
        """Crear un nuevo tutor"""
        try:
            # Verificar si ya existe un tutor con la misma cédula
            cedula_check = DataBaseHandle.getRecords(
                "SELECT id FROM tutor WHERE cedula = %s",
                (data['cedula'],), size=1
            )
            if cedula_check:
                return internal_response(False, None, "Ya existe un tutor con esta cédula")

            # Insertar nuevo tutor
            insert_query = """
                INSERT INTO tutor (
                    nombre, apellido, cedula, telefono, email, direccion,
                    parentesco, ocupacion, direccion_empresa, telefono_empresa,
                    nombre_empresa, estado, usuario_creacion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """

            params = (
                data['nombre'],
                data['apellido'], 
                data['cedula'],
                data.get('telefono', ''),
                data.get('email', ''),
                data.get('direccion', ''),
                data['parentesco'],
                data.get('ocupacion', ''),
                data.get('direccion_empresa', ''),
                data.get('telefono_empresa', ''),
                data.get('nombre_empresa', ''),
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

            allowed_fields = ['nombre', 'apellido', 'telefono', 'email', 'direccion', 
                              'parentesco', 'ocupacion', 'direccion_empresa', 
                              'telefono_empresa', 'nombre_empresa', 'estado',
                              'usuario_modificacion']

            for field in allowed_fields:
                if field in data and data[field] is not None:
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
                WHERE id_tutor = %s AND estado = 'activo'
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
    def check_cedula_exists(cedula, exclude_id=None):
        """Verificar si ya existe un tutor con la cédula especificada"""
        try:
            if exclude_id:
                query = "SELECT id FROM tutor WHERE cedula = %s AND id != %s"
                params = (cedula, exclude_id)
            else:
                query = "SELECT id FROM tutor WHERE cedula = %s"
                params = (cedula,)

            existing = DataBaseHandle.getRecords(query, params, size=1)
            return internal_response(True, existing is not None, "Consulta ejecutada")

        except Exception as e:
            HandleLogs.write_error(f"TutorComponent.check_cedula_exists - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_tutores_activos():
        """Obtener solo tutores activos (útil para combos/selects)"""
        try:
            query = """
            SELECT 
                t.id,
                CONCAT(t.nombre, ' ', t.apellido) as nombre_completo,
                t.nombre,
                t.apellido,
                t.parentesco,
                t.telefono,
                t.email
            FROM tutor t
            WHERE t.estado = 'activo'
            ORDER BY t.nombre, t.apellido
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
                AVG(pacientes_por_tutor.total_pacientes) as promedio_pacientes_por_tutor
            FROM tutor t
            LEFT JOIN (
                SELECT id_tutor, COUNT(*) as total_pacientes
                FROM paciente
                GROUP BY id_tutor
            ) pacientes_por_tutor ON t.id = pacientes_por_tutor.id_tutor
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
        """Obtener personas que no están registradas como tutores (usando cédula)"""
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
            LEFT JOIN tutor t ON p.cedula = t.cedula
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