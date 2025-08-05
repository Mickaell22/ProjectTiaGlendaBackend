from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class PacienteComponent:

    @staticmethod
    def get_all_pacientes():
        """Obtener todos los pacientes con información completa"""
        try:
            query = """
            SELECT 
                pac.id,
                pac.fecha_ingreso,
                pac.observaciones,
                pac.estado,
                pac.fecha_creacion,
                pac.fecha_modificacion,
                -- Información del paciente (persona)
                p.id as persona_id,
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
                t.es_contacto_emergencia,
                CONCAT(pt.nombre, ' ', pt.apellido) as nombre_tutor,
                pt.telefono as telefono_tutor,
                pt.correo as correo_tutor,
                -- Estadísticas
                COUNT(pe.id) as total_especialidades,
                COUNT(CASE WHEN pe.estado = 'activo' THEN 1 END) as especialidades_activas
            FROM paciente pac
            INNER JOIN persona p ON pac.persona_id = p.id
            INNER JOIN tutor t ON pac.tutor_id = t.id
            INNER JOIN persona pt ON t.persona_id = pt.id
            LEFT JOIN paciente_especialidad pe ON pac.id = pe.paciente_id
            GROUP BY pac.id, pac.fecha_ingreso, pac.observaciones, pac.estado, 
                     pac.fecha_creacion, pac.fecha_modificacion,
                     p.id, p.nombre, p.apellido, p.cedula, p.telefono, p.correo, 
                     p.direccion, p.fecha_nacimiento,
                     t.id, t.parentesco, t.es_contacto_emergencia,
                     pt.nombre, pt.apellido, pt.telefono, pt.correo
            ORDER BY p.nombre, p.apellido
            """

            pacientes = DataBaseHandle.getRecords(query)

            if pacientes is not None:
                HandleLogs.write_log(f"PacienteComponent.get_all_pacientes - {len(pacientes)} pacientes encontrados")
                return internal_response(True, pacientes, "Pacientes obtenidos correctamente")
            else:
                HandleLogs.write_error("PacienteComponent.get_all_pacientes - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_all_pacientes - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_paciente_by_id(paciente_id):
        """Obtener un paciente por ID con información completa y especialidades"""
        try:
            # Obtener información básica del paciente
            query_paciente = """
            SELECT 
                pac.id,
                pac.fecha_ingreso,
                pac.observaciones,
                pac.estado,
                pac.fecha_creacion,
                pac.fecha_modificacion,
                -- Información del paciente (persona)
                p.id as persona_id,
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
                t.es_contacto_emergencia,
                t.observaciones_tutor,
                CONCAT(pt.nombre, ' ', pt.apellido) as nombre_tutor,
                pt.telefono as telefono_tutor,
                pt.correo as correo_tutor
            FROM paciente pac
            INNER JOIN persona p ON pac.persona_id = p.id
            INNER JOIN tutor t ON pac.tutor_id = t.id
            INNER JOIN persona pt ON t.persona_id = pt.id
            WHERE pac.id = %s
            """

            paciente = DataBaseHandle.getRecords(query_paciente, (paciente_id,), size=1)

            if paciente:
                # Obtener especialidades del paciente
                query_especialidades = """
                SELECT 
                    pe.id,
                    pe.fecha_inicio,
                    pe.fecha_fin,
                    pe.estado,
                    pe.observaciones_tratamiento,
                    pe.fecha_creacion as fecha_asignacion,
                    e.id as especialidad_id,
                    e.nombre as especialidad_nombre,
                    e.area
                FROM paciente_especialidad pe
                INNER JOIN especialidad e ON pe.especialidad_id = e.id
                WHERE pe.paciente_id = %s
                ORDER BY pe.fecha_inicio DESC
                """

                especialidades = DataBaseHandle.getRecords(query_especialidades, (paciente_id,))
                paciente['especialidades'] = especialidades if especialidades else []

                HandleLogs.write_log(f"PacienteComponent.get_paciente_by_id - Paciente {paciente_id} encontrado")
                return internal_response(True, paciente, "Paciente encontrado")
            else:
                HandleLogs.write_log(f"PacienteComponent.get_paciente_by_id - Paciente {paciente_id} no encontrado")
                return internal_response(True, None, "Paciente no encontrado")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_paciente_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def create_paciente(data):
        """Crear un nuevo paciente"""
        try:
            # Verificar si la persona ya está registrada como paciente
            persona_check = PacienteComponent.check_persona_is_paciente(data['persona_id'])
            if persona_check['success'] and persona_check['data']:
                return internal_response(False, None, "Esta persona ya está registrada como paciente")

            # Verificar que la persona existe y está activa
            persona_exists = DataBaseHandle.getRecords(
                "SELECT id, estado FROM persona WHERE id = %s",
                (data['persona_id'],), size=1
            )

            if not persona_exists:
                return internal_response(False, None, "La persona especificada no existe")

            if persona_exists['estado'] != 'activo':
                return internal_response(False, None, "La persona debe estar activa para ser registrada como paciente")

            # Verificar que el tutor existe y está activo
            tutor_exists = DataBaseHandle.getRecords(
                "SELECT id, estado FROM tutor WHERE id = %s",
                (data['tutor_id'],), size=1
            )

            if not tutor_exists:
                return internal_response(False, None, "El tutor especificado no existe")

            if tutor_exists['estado'] != 'activo':
                return internal_response(False, None, "El tutor debe estar activo para asignar pacientes")

            # Insertar nuevo paciente
            insert_query = """
                INSERT INTO paciente (
                    persona_id, tutor_id, fecha_ingreso, 
                    observaciones, estado, usuario_creacion
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """

            params = (
                data['persona_id'],
                data['tutor_id'],
                data['fecha_ingreso'],
                data['observaciones'],
                data['estado'],
                data['usuario_creacion']
            )

            new_id = DataBaseHandle.ExecuteInsert(insert_query, params)

            if new_id:
                # Obtener el paciente creado con información completa
                new_paciente = PacienteComponent.get_paciente_by_id(new_id)
                HandleLogs.write_log(f"PacienteComponent.create_paciente - Paciente creado con ID: {new_id}")
                return internal_response(True, new_paciente['data'], "Paciente creado exitosamente")
            else:
                HandleLogs.write_error("PacienteComponent.create_paciente - Error insertando paciente")
                return internal_response(False, None, "Error creando paciente")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.create_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def update_paciente(paciente_id, data):
        """Actualizar un paciente existente"""
        try:
            # Verificar si el paciente existe
            check_query = "SELECT id FROM paciente WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (paciente_id,), size=1)

            if not existing:
                return internal_response(False, None, "Paciente no encontrado")

            # Si se cambia el tutor, verificar que esté activo
            if 'tutor_id' in data and data['tutor_id']:
                tutor_exists = DataBaseHandle.getRecords(
                    "SELECT id, estado FROM tutor WHERE id = %s",
                    (data['tutor_id'],), size=1
                )

                if not tutor_exists:
                    return internal_response(False, None, "El tutor especificado no existe")

                if tutor_exists['estado'] != 'activo':
                    return internal_response(False, None, "El tutor debe estar activo")

            # Construir query de actualización dinámicamente
            update_fields = []
            params = []

            allowed_fields = ['tutor_id', 'fecha_ingreso', 'observaciones', 'estado', 'usuario_modificacion']

            for field in allowed_fields:
                if field in data and data[field] is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(data[field])

            if not update_fields:
                return internal_response(False, None, "No hay campos para actualizar")

            # Agregar fecha de modificación
            update_fields.append("fecha_modificacion = CURRENT_TIMESTAMP")

            # Agregar ID del paciente al final
            params.append(paciente_id)

            update_query = f"""
                UPDATE paciente 
                SET {', '.join(update_fields)}
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, params)

            if success:
                # Obtener datos actualizados
                updated_paciente = PacienteComponent.get_paciente_by_id(paciente_id)
                HandleLogs.write_log(f"PacienteComponent.update_paciente - Paciente {paciente_id} actualizado")
                return internal_response(True, updated_paciente['data'], "Paciente actualizado exitosamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.update_paciente - Error actualizando paciente {paciente_id}")
                return internal_response(False, None, "Error actualizando paciente")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.update_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def change_estado_paciente(paciente_id, nuevo_estado):
        """Cambiar estado del paciente (activo, inactivo, alta, derivado)"""
        try:
            # Verificar si el paciente existe
            check_query = "SELECT id, estado FROM paciente WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (paciente_id,), size=1)

            if not existing:
                return internal_response(False, None, "Paciente no encontrado")

            # Verificar estados válidos
            valid_states = ['activo', 'inactivo', 'alta', 'derivado']
            if nuevo_estado not in valid_states:
                return internal_response(False, None, f"Estado inválido. Debe ser uno de: {', '.join(valid_states)}")

            if existing['estado'] == nuevo_estado:
                return internal_response(False, None, f"Paciente ya está en estado {nuevo_estado}")

            # Si se da de alta o se deriva, finalizar especialidades activas
            if nuevo_estado in ['alta', 'derivado']:
                finalize_query = """
                    UPDATE paciente_especialidad 
                    SET estado = 'completado', fecha_fin = CURRENT_DATE, fecha_modificacion = CURRENT_TIMESTAMP
                    WHERE paciente_id = %s AND estado = 'activo'
                    """
                DataBaseHandle.ExecuteNonQuery(finalize_query, (paciente_id,))

            # Cambiar estado del paciente
            update_query = """
                UPDATE paciente 
                SET estado = %s, fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (nuevo_estado, paciente_id))

            if success:
                HandleLogs.write_log(
                    f"PacienteComponent.change_estado_paciente - Paciente {paciente_id} cambió a estado {nuevo_estado}")
                return internal_response(True, {"id": paciente_id, "estado": nuevo_estado},
                                         f"Estado del paciente cambiado a {nuevo_estado}")
            else:
                HandleLogs.write_error(
                    f"PacienteComponent.change_estado_paciente - Error cambiando estado del paciente {paciente_id}")
                return internal_response(False, None, "Error cambiando estado del paciente")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.change_estado_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def check_persona_is_paciente(persona_id, exclude_id=None):
        """Verificar si una persona ya está registrada como paciente"""
        try:
            if exclude_id:
                query = "SELECT id FROM paciente WHERE persona_id = %s AND id != %s"
                params = (persona_id, exclude_id)
            else:
                query = "SELECT id FROM paciente WHERE persona_id = %s"
                params = (persona_id,)

            existing = DataBaseHandle.getRecords(query, params, size=1)
            return internal_response(True, existing is not None, "Consulta ejecutada")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.check_persona_is_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_pacientes_by_tutor(tutor_id):
        """Obtener pacientes de un tutor específico"""
        try:
            query = """
            SELECT 
                pac.id,
                pac.fecha_ingreso,
                pac.estado,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.nombre,
                p.apellido,
                p.fecha_nacimiento,
                COUNT(pe.id) as total_especialidades,
                COUNT(CASE WHEN pe.estado = 'activo' THEN 1 END) as especialidades_activas
            FROM paciente pac
            INNER JOIN persona p ON pac.persona_id = p.id
            LEFT JOIN paciente_especialidad pe ON pac.id = pe.paciente_id
            WHERE pac.tutor_id = %s
            GROUP BY pac.id, pac.fecha_ingreso, pac.estado, p.nombre, p.apellido, p.fecha_nacimiento
            ORDER BY p.nombre, p.apellido
            """

            pacientes = DataBaseHandle.getRecords(query, (tutor_id,))

            if pacientes is not None:
                HandleLogs.write_log(
                    f"PacienteComponent.get_pacientes_by_tutor - {len(pacientes)} pacientes del tutor {tutor_id} encontrados")
                return internal_response(True, pacientes, f"Pacientes del tutor obtenidos")
            else:
                HandleLogs.write_error(
                    f"PacienteComponent.get_pacientes_by_tutor - Error en consulta para tutor {tutor_id}")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_pacientes_by_tutor - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_estadisticas_pacientes():
        """Obtener estadísticas de pacientes"""
        try:
            query = """
            SELECT 
                COUNT(*) as total_pacientes,
                COUNT(CASE WHEN pac.estado = 'activo' THEN 1 END) as pacientes_activos,
                COUNT(CASE WHEN pac.estado = 'inactivo' THEN 1 END) as pacientes_inactivos,
                COUNT(CASE WHEN pac.estado = 'alta' THEN 1 END) as pacientes_alta,
                COUNT(CASE WHEN pac.estado = 'derivado' THEN 1 END) as pacientes_derivados,
                AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.fecha_nacimiento))) as edad_promedio
            FROM paciente pac
            INNER JOIN persona p ON pac.persona_id = p.id
            """

            estadisticas_generales = DataBaseHandle.getRecords(query, size=1)

            # Estadísticas por estado
            query_estados = """
            SELECT 
                estado,
                COUNT(*) as total
            FROM paciente
            GROUP BY estado
            ORDER BY total DESC
            """

            estadisticas_estados = DataBaseHandle.getRecords(query_estados)

            # Estadísticas por rangos de edad
            query_edades = """
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.fecha_nacimiento)) < 5 THEN '0-4 años'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.fecha_nacimiento)) < 10 THEN '5-9 años'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.fecha_nacimiento)) < 15 THEN '10-14 años'
                    WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.fecha_nacimiento)) < 20 THEN '15-19 años'
                    ELSE '20+ años'
                END as rango_edad,
                COUNT(*) as total
            FROM paciente pac
            INNER JOIN persona p ON pac.persona_id = p.id
            GROUP BY rango_edad
            ORDER BY rango_edad
            """

            estadisticas_edades = DataBaseHandle.getRecords(query_edades)

            resultado = {
                "general": estadisticas_generales,
                "por_estado": estadisticas_estados if estadisticas_estados else [],
                "por_edad": estadisticas_edades if estadisticas_edades else []
            }

            if estadisticas_generales is not None:
                HandleLogs.write_log("PacienteComponent.get_estadisticas_pacientes - Estadísticas obtenidas")
                return internal_response(True, resultado, "Estadísticas de pacientes obtenidas")
            else:
                HandleLogs.write_error("PacienteComponent.get_estadisticas_pacientes - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_estadisticas_pacientes - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_personas_disponibles_para_paciente():
        """Obtener personas que no están registradas como pacientes"""
        try:
            query = """
            SELECT 
                p.id,
                p.nombre,
                p.apellido,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.cedula,
                p.telefono,
                p.correo,
                p.fecha_nacimiento
            FROM persona p
            LEFT JOIN paciente pac ON p.id = pac.persona_id
            WHERE pac.id IS NULL AND p.estado = 'activo'
            ORDER BY p.nombre, p.apellido
            """

            personas = DataBaseHandle.getRecords(query)

            if personas is not None:
                HandleLogs.write_log(
                    f"PacienteComponent.get_personas_disponibles_para_paciente - {len(personas)} personas disponibles")
                return internal_response(True, personas, "Personas disponibles para paciente obtenidas")
            else:
                HandleLogs.write_error("PacienteComponent.get_personas_disponibles_para_paciente - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_personas_disponibles_para_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    # =============================================
    # MÉTODOS PARA GESTIÓN DE ESPECIALIDADES DE PACIENTES
    # =============================================

    @staticmethod
    def get_paciente_especialidades(paciente_id):
        """Obtener todas las especialidades asignadas a un paciente"""
        try:
            query = """
            SELECT 
                pe.id,
                pe.paciente_id,
                pe.especialidad_id,
                pe.fecha_inicio,
                pe.fecha_fin,
                pe.estado,
                pe.observaciones_tratamiento,
                pe.fecha_creacion,
                pe.fecha_modificacion,
                -- Información de la especialidad
                e.nombre as especialidad_nombre,
                e.area
            FROM paciente_especialidad pe
            INNER JOIN especialidad e ON pe.especialidad_id = e.id
            WHERE pe.paciente_id = %s
            ORDER BY pe.fecha_inicio DESC, pe.fecha_creacion DESC
            """

            especialidades = DataBaseHandle.getRecords(query, (paciente_id,))

            if especialidades is not None:
                HandleLogs.write_log(f"PacienteComponent.get_paciente_especialidades - {len(especialidades)} especialidades encontradas para paciente {paciente_id}")
                return internal_response(True, especialidades, "Especialidades del paciente obtenidas correctamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.get_paciente_especialidades - Error en consulta para paciente {paciente_id}")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_paciente_especialidades - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def create_paciente_especialidad(paciente_id, data):
        """Asignar una especialidad a un paciente"""
        try:
            # Verificar que el paciente existe
            paciente_check = DataBaseHandle.getRecords(
                "SELECT id, estado FROM paciente WHERE id = %s",
                (paciente_id,), size=1
            )

            if not paciente_check:
                return internal_response(False, None, "Paciente no encontrado")

            # Verificar que la especialidad existe y está activa
            especialidad_check = DataBaseHandle.getRecords(
                "SELECT id, estado FROM especialidad WHERE id = %s",
                (data['especialidad_id'],), size=1
            )

            if not especialidad_check:
                return internal_response(False, None, "Especialidad no encontrada")

            if especialidad_check['estado'] != 'activo':
                return internal_response(False, None, "La especialidad debe estar activa")

            # Verificar que el paciente no tenga ya esta especialidad activa
            existing_check = DataBaseHandle.getRecords(
                "SELECT id FROM paciente_especialidad WHERE paciente_id = %s AND especialidad_id = %s AND estado != 'completado'",
                (paciente_id, data['especialidad_id']), size=1
            )

            if existing_check:
                return internal_response(False, None, "El paciente ya tiene esta especialidad asignada (activa o suspendida)")

            # Insertar nueva asignación
            insert_query = """
                INSERT INTO paciente_especialidad (
                    paciente_id, especialidad_id, fecha_inicio, fecha_fin,
                    estado, observaciones_tratamiento, usuario_creacion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """

            params = (
                paciente_id,
                data['especialidad_id'],
                data['fecha_inicio'],
                data.get('fecha_fin'),
                data.get('estado', 'activo'),
                data.get('observaciones_tratamiento'),
                data.get('usuario_creacion')
            )

            new_id = DataBaseHandle.ExecuteInsert(insert_query, params)

            if new_id:
                # Obtener el registro creado con información completa
                new_especialidad = PacienteComponent.get_paciente_especialidad_by_id(new_id)
                HandleLogs.write_log(f"PacienteComponent.create_paciente_especialidad - Especialidad asignada con ID: {new_id}")
                return internal_response(True, new_especialidad['data'], "Especialidad asignada exitosamente")
            else:
                HandleLogs.write_error("PacienteComponent.create_paciente_especialidad - Error insertando asignación")
                return internal_response(False, None, "Error asignando especialidad")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.create_paciente_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_paciente_especialidad_by_id(tratamiento_id):
        """Obtener una asignación específica de especialidad por ID"""
        try:
            query = """
            SELECT 
                pe.id,
                pe.paciente_id,
                pe.especialidad_id,
                pe.fecha_inicio,
                pe.fecha_fin,
                pe.estado,
                pe.observaciones_tratamiento,
                pe.fecha_creacion,
                pe.fecha_modificacion,
                -- Información de la especialidad
                e.nombre as especialidad_nombre,
                e.area,
                -- Información del paciente
                CONCAT(p.nombre, ' ', p.apellido) as paciente_nombre
            FROM paciente_especialidad pe
            INNER JOIN especialidad e ON pe.especialidad_id = e.id
            INNER JOIN paciente pac ON pe.paciente_id = pac.id
            INNER JOIN persona p ON pac.persona_id = p.id
            WHERE pe.id = %s
            """

            especialidad = DataBaseHandle.getRecords(query, (tratamiento_id,), size=1)

            if especialidad:
                HandleLogs.write_log(f"PacienteComponent.get_paciente_especialidad_by_id - Tratamiento {tratamiento_id} encontrado")
                return internal_response(True, especialidad, "Tratamiento encontrado")
            else:
                HandleLogs.write_log(f"PacienteComponent.get_paciente_especialidad_by_id - Tratamiento {tratamiento_id} no encontrado")
                return internal_response(True, None, "Tratamiento no encontrado")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_paciente_especialidad_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def update_paciente_especialidad(tratamiento_id, data):
        """Actualizar una asignación de especialidad"""
        try:
            # Verificar que la asignación existe
            check_query = "SELECT id, paciente_id, especialidad_id FROM paciente_especialidad WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (tratamiento_id,), size=1)

            if not existing:
                return internal_response(False, None, "Tratamiento no encontrado")

            # Construir query de actualización dinámicamente
            update_fields = []
            params = []

            allowed_fields = ['fecha_inicio', 'fecha_fin', 'estado', 'observaciones_tratamiento', 'usuario_modificacion']

            for field in allowed_fields:
                if field in data and data[field] is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(data[field])

            if not update_fields:
                return internal_response(False, None, "No hay campos para actualizar")

            # Agregar fecha de modificación
            update_fields.append("fecha_modificacion = CURRENT_TIMESTAMP")

            # Agregar ID del tratamiento al final
            params.append(tratamiento_id)

            update_query = f"""
                UPDATE paciente_especialidad 
                SET {', '.join(update_fields)}
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, params)

            if success:
                # Obtener datos actualizados
                updated_especialidad = PacienteComponent.get_paciente_especialidad_by_id(tratamiento_id)
                HandleLogs.write_log(f"PacienteComponent.update_paciente_especialidad - Tratamiento {tratamiento_id} actualizado")
                return internal_response(True, updated_especialidad['data'], "Tratamiento actualizado exitosamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.update_paciente_especialidad - Error actualizando tratamiento {tratamiento_id}")
                return internal_response(False, None, "Error actualizando tratamiento")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.update_paciente_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def delete_paciente_especialidad(tratamiento_id):
        """Eliminar una asignación de especialidad"""
        try:
            # Verificar que la asignación existe
            check_query = "SELECT id, paciente_id, especialidad_id FROM paciente_especialidad WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (tratamiento_id,), size=1)

            if not existing:
                return internal_response(False, None, "Tratamiento no encontrado")

            # Eliminar la asignación
            delete_query = "DELETE FROM paciente_especialidad WHERE id = %s"
            success = DataBaseHandle.ExecuteNonQuery(delete_query, (tratamiento_id,))

            if success:
                HandleLogs.write_log(f"PacienteComponent.delete_paciente_especialidad - Tratamiento {tratamiento_id} eliminado")
                return internal_response(True, {"id": tratamiento_id}, "Tratamiento eliminado exitosamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.delete_paciente_especialidad - Error eliminando tratamiento {tratamiento_id}")
                return internal_response(False, None, "Error eliminando tratamiento")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.delete_paciente_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_pacientes_by_especialidad(especialidad_id):
        """Obtener pacientes que tienen una especialidad específica"""
        try:
            query = """
            SELECT 
                pac.id as paciente_id,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.cedula,
                pac.estado as estado_paciente,
                pe.id as tratamiento_id,
                pe.fecha_inicio,
                pe.fecha_fin,
                pe.estado as estado_tratamiento,
                pe.observaciones_tratamiento
            FROM paciente_especialidad pe
            INNER JOIN paciente pac ON pe.paciente_id = pac.id
            INNER JOIN persona p ON pac.persona_id = p.id
            WHERE pe.especialidad_id = %s
            ORDER BY pe.fecha_inicio DESC
            """

            pacientes = DataBaseHandle.getRecords(query, (especialidad_id,))

            if pacientes is not None:
                HandleLogs.write_log(f"PacienteComponent.get_pacientes_by_especialidad - {len(pacientes)} pacientes encontrados para especialidad {especialidad_id}")
                return internal_response(True, pacientes, "Pacientes con la especialidad obtenidos correctamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.get_pacientes_by_especialidad - Error en consulta para especialidad {especialidad_id}")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_pacientes_by_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_estadisticas_paciente_especialidades():
        """Obtener estadísticas de especialidades de pacientes"""
        try:
            query = """
            SELECT 
                COUNT(*) as total_asignaciones,
                COUNT(CASE WHEN pe.estado = 'activo' THEN 1 END) as tratamientos_activos,
                COUNT(CASE WHEN pe.estado = 'completado' THEN 1 END) as tratamientos_completados,
                COUNT(CASE WHEN pe.estado = 'suspendido' THEN 1 END) as tratamientos_suspendidos,
                COUNT(DISTINCT pe.paciente_id) as pacientes_con_especialidades,
                COUNT(DISTINCT pe.especialidad_id) as especialidades_asignadas
            FROM paciente_especialidad pe
            """

            estadisticas_generales = DataBaseHandle.getRecords(query, size=1)

            # Estadísticas por especialidad
            query_especialidades = """
            SELECT 
                e.nombre as especialidad,
                e.area,
                COUNT(*) as total_asignaciones,
                COUNT(CASE WHEN pe.estado = 'activo' THEN 1 END) as activos,
                COUNT(CASE WHEN pe.estado = 'completado' THEN 1 END) as completados
            FROM paciente_especialidad pe
            INNER JOIN especialidad e ON pe.especialidad_id = e.id
            GROUP BY e.id, e.nombre, e.area
            ORDER BY total_asignaciones DESC
            """

            estadisticas_especialidades = DataBaseHandle.getRecords(query_especialidades)

            # Estadísticas por estado
            query_estados = """
            SELECT 
                estado,
                COUNT(*) as total
            FROM paciente_especialidad
            GROUP BY estado
            ORDER BY total DESC
            """

            estadisticas_estados = DataBaseHandle.getRecords(query_estados)

            resultado = {
                "general": estadisticas_generales,
                "por_especialidad": estadisticas_especialidades if estadisticas_especialidades else [],
                "por_estado": estadisticas_estados if estadisticas_estados else []
            }

            if estadisticas_generales is not None:
                HandleLogs.write_log("PacienteComponent.get_estadisticas_paciente_especialidades - Estadísticas obtenidas")
                return internal_response(True, resultado, "Estadísticas de especialidades obtenidas")
            else:
                HandleLogs.write_error("PacienteComponent.get_estadisticas_paciente_especialidades - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_estadisticas_paciente_especialidades - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_tratamientos_by_estado(paciente_id, estado):
        """Obtener tratamientos de un paciente por estado específico"""
        try:
            query = """
            SELECT 
                pe.id,
                pe.fecha_inicio,
                pe.fecha_fin,
                pe.estado,
                pe.observaciones_tratamiento,
                pe.fecha_creacion,
                e.nombre as especialidad_nombre,
                e.area
            FROM paciente_especialidad pe
            INNER JOIN especialidad e ON pe.especialidad_id = e.id
            WHERE pe.paciente_id = %s AND pe.estado = %s
            ORDER BY pe.fecha_inicio DESC
            """

            tratamientos = DataBaseHandle.getRecords(query, (paciente_id, estado))

            if tratamientos is not None:
                HandleLogs.write_log(f"PacienteComponent.get_tratamientos_by_estado - {len(tratamientos)} tratamientos {estado} encontrados para paciente {paciente_id}")
                return internal_response(True, tratamientos, f"Tratamientos {estado} obtenidos correctamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.get_tratamientos_by_estado - Error en consulta para paciente {paciente_id}")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_tratamientos_by_estado - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")