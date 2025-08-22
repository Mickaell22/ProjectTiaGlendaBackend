from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response
from src.utils.general.centro_middleware import CentroMiddleware


class PacienteComponent:

    @staticmethod
    def get_all_pacientes():
        """Obtener todos los pacientes con información completa incluyendo especialidad"""
        try:
            query = """
            SELECT 
                pac.id,
                pac.fecha_ingreso,
                pac.estado_tratamiento,
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
                CONCAT(pt.nombre, ' ', pt.apellido) as nombre_tutor,
                pt.telefono as telefono_tutor,
                pt.correo as correo_tutor
                -- Sin especialidad directa (se maneja por tabla paciente_especialidades)
            FROM paciente pac
            INNER JOIN persona p ON pac.id_persona = p.id
            INNER JOIN tutor t ON pac.id_tutor = t.id
            INNER JOIN persona pt ON t.id_persona = pt.id
            WHERE pac.estado != 'eliminado'
            ORDER BY p.nombre, p.apellido
            """

            pacientes = DataBaseHandle.getRecords(query)

            if pacientes is not None:
                # Formatear los datos para mantener compatibilidad con el frontend
                for paciente in pacientes:
                    # Temporarily commented out especialidad logic
                    if False:  # paciente['especialidad_id']:
                        paciente['especialidades'] = [{
                            'id': paciente['especialidad_id'],
                            'nombre': paciente['especialidad_nombre'],
                            'area': paciente['especialidad_area'],
                            'estado_tratamiento': paciente['estado_tratamiento'],
                            'fecha_inicio': paciente['fecha_inicio_tratamiento'],
                            'fecha_fin': paciente['fecha_fin_tratamiento']
                        }]
                        paciente['total_especialidades'] = 1
                        paciente['especialidades_activas'] = 1 if paciente['estado_tratamiento'] == 'activo' else 0
                    else:
                        paciente['especialidades'] = []
                        paciente['total_especialidades'] = 0
                        paciente['especialidades_activas'] = 0

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
        """Obtener un paciente por ID con información completa y especialidad"""
        try:
            # Obtener información básica del paciente con especialidad
            query_paciente = """
            SELECT 
                pac.id,
                pac.fecha_ingreso,
                pac.estado_tratamiento,
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
                CONCAT(pt.nombre, ' ', pt.apellido) as nombre_tutor,
                pt.telefono as telefono_tutor,
                pt.correo as correo_tutor
                -- Sin especialidad directa (se maneja por tabla paciente_especialidades)
            FROM paciente pac
            INNER JOIN persona p ON pac.id_persona = p.id
            INNER JOIN tutor t ON pac.id_tutor = t.id
            INNER JOIN persona pt ON t.id_persona = pt.id
            WHERE pac.id = %s
            """

            paciente = DataBaseHandle.getRecords(query_paciente, (paciente_id,), size=1)

            if paciente:
                # Formatear especialidades para mantener compatibilidad con el frontend
                paciente['especialidades'] = []
                paciente['total_especialidades'] = 0
                paciente['especialidades_activas'] = 0

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
            persona_check = PacienteComponent.check_persona_is_paciente(data['id_persona'])
            if persona_check['success'] and persona_check['data']:
                return internal_response(False, None, "Esta persona ya está registrada como paciente")

            # Verificar que la persona existe y está activa
            persona_exists = DataBaseHandle.getRecords(
                "SELECT id, estado FROM persona WHERE id = %s",
                (data['id_persona'],), size=1
            )

            if not persona_exists:
                return internal_response(False, None, "La persona especificada no existe")

            if persona_exists['estado'] != 'activo':
                return internal_response(False, None, "La persona debe estar activa para ser registrada como paciente")

            # Verificar que el tutor existe y está activo
            tutor_exists = DataBaseHandle.getRecords(
                "SELECT id, estado FROM tutor WHERE id = %s",
                (data['id_tutor'],), size=1
            )

            if not tutor_exists:
                return internal_response(False, None, "El tutor especificado no existe")

            if tutor_exists['estado'] != 'activo':
                return internal_response(False, None, "El tutor debe estar activo para asignar pacientes")

            # Verificar que la especialidad existe y está activa (si se proporciona)
            if data.get('especialidad_id'):
                especialidad_exists = DataBaseHandle.getRecords(
                    "SELECT id, estado FROM especialidad WHERE id = %s",
                    (data['especialidad_id'],), size=1
                )

                if not especialidad_exists:
                    return internal_response(False, None, "La especialidad especificada no existe")

                if especialidad_exists['estado'] != 'activo':
                    return internal_response(False, None, "La especialidad debe estar activa")

            # Insertar nuevo paciente (sin especialidad - se maneja en tabla separada)
            insert_query = """
                INSERT INTO paciente (
                    id_persona, id_tutor, fecha_ingreso, motivo_consulta,
                    estado_tratamiento, observaciones, estado, id_centro, usuario_creacion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """

            # Obtener centro del usuario actual (fallback a centro 1 - Norte)
            id_centro = CentroMiddleware.get_current_user_centro() or 1

            params = (
                data['id_persona'],
                data['id_tutor'],
                data['fecha_ingreso'],
                data.get('observaciones_tratamiento'),  # usar como motivo_consulta temporalmente
                data.get('estado_tratamiento', 'activo'),
                data.get('observaciones'),
                data.get('estado', 'activo'),
                id_centro,
                data.get('usuario_creacion')
            )

            new_id = DataBaseHandle.ExecuteInsert(insert_query, params)

            if new_id:
                # Si se proporciona especialidad, crear relación en paciente_especialidades
                if data.get('especialidad_id'):
                    especialidad_query = """
                        INSERT INTO paciente_especialidades (
                            id_paciente, id_especialidad, es_principal, fecha_inicio_tratamiento,
                            observaciones, estado, usuario_creacion
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    especialidad_params = (
                        new_id,
                        data['especialidad_id'],
                        True,  # es_principal = True para la primera especialidad
                        data.get('fecha_inicio_tratamiento'),
                        data.get('observaciones_tratamiento'),
                        'activo',
                        data.get('usuario_creacion')
                    )
                    
                    especialidad_success = DataBaseHandle.ExecuteNonQuery(especialidad_query, especialidad_params)
                    if not especialidad_success:
                        HandleLogs.write_error(f"PacienteComponent.create_paciente - Error asignando especialidad al paciente {new_id}")
                        # No fallar completamente, solo logar el error

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
            if 'id_tutor' in data and data['id_tutor']:
                tutor_exists = DataBaseHandle.getRecords(
                    "SELECT id, estado FROM tutor WHERE id = %s",
                    (data['id_tutor'],), size=1
                )

                if not tutor_exists:
                    return internal_response(False, None, "El tutor especificado no existe")

                if tutor_exists['estado'] != 'activo':
                    return internal_response(False, None, "El tutor debe estar activo")

            # Specialties are now managed in paciente_especialidades table separately

            # Construir query de actualización dinámicamente
            update_fields = []
            params = []

            allowed_fields = ['id_tutor', 'fecha_ingreso', 'motivo_consulta',
                            'estado_tratamiento', 'observaciones', 'estado', 'usuario_modificacion']

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
            valid_states = ['activo', 'inactivo', 'alta', 'derivado', 'eliminado']
            if nuevo_estado not in valid_states:
                return internal_response(False, None, f"Estado inválido. Debe ser uno de: {', '.join(valid_states)}")

            if existing['estado'] == nuevo_estado:
                return internal_response(False, None, f"Paciente ya está en estado {nuevo_estado}")

            # Si se da de alta o se deriva, finalizar tratamiento activo
            if nuevo_estado in ['alta', 'derivado']:
                finalize_query = """
                    UPDATE paciente 
                    SET estado_tratamiento = 'completado', fecha_fin_tratamiento = CURRENT_DATE, fecha_modificacion = CURRENT_TIMESTAMP
                    WHERE id = %s AND estado_tratamiento = 'activo'
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
    def check_persona_is_paciente(id_persona, exclude_id=None):
        """Verificar si una persona ya está registrada como paciente"""
        try:
            if exclude_id:
                query = "SELECT id FROM paciente WHERE id_persona = %s AND id != %s"
                params = (id_persona, exclude_id)
            else:
                query = "SELECT id FROM paciente WHERE id_persona = %s"
                params = (id_persona,)

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
                pac.estado_tratamiento,
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
                CONCAT(pt.nombre, ' ', pt.apellido) as nombre_tutor,
                pt.telefono as telefono_tutor,
                pt.correo as correo_tutor,
                pac.observaciones
            FROM paciente pac
            INNER JOIN persona p ON pac.id_persona = p.id
            INNER JOIN tutor t ON pac.id_tutor = t.id
            INNER JOIN persona pt ON t.id_persona = pt.id
            WHERE pac.id_tutor = %s AND pac.estado != 'eliminado'
            ORDER BY p.nombre, p.apellido
            """

            pacientes = DataBaseHandle.getRecords(query, (tutor_id,))

            if pacientes is not None:
                # Formatear los datos para mantener compatibilidad con el frontend
                for paciente in pacientes:
                    # Agregar especialidades vacías por ahora (se pueden cargar por separado si es necesario)
                    paciente['especialidades'] = []
                    paciente['total_especialidades'] = 0
                    paciente['especialidades_activas'] = 0

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
            INNER JOIN persona p ON pac.id_persona = p.id
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
            INNER JOIN persona p ON pac.id_persona = p.id
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
            LEFT JOIN paciente pac ON p.id = pac.id_persona
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

    @staticmethod
    def delete_paciente(paciente_id):
        """Eliminar un paciente (soft delete - cambiar estado a eliminado)"""
        try:
            # Verificar si el paciente existe
            check_query = "SELECT id, estado FROM paciente WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (paciente_id,), size=1)

            if not existing:
                return internal_response(False, None, "Paciente no encontrado")

            # En lugar de eliminar físicamente, cambiar estado a 'eliminado'
            update_query = """
                UPDATE paciente 
                SET estado = 'eliminado', fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (paciente_id,))

            if success:
                HandleLogs.write_log(f"PacienteComponent.delete_paciente - Paciente {paciente_id} marcado como eliminado")
                return internal_response(True, {"id": paciente_id, "estado": "eliminado"}, "Paciente eliminado exitosamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.delete_paciente - Error eliminando paciente {paciente_id}")
                return internal_response(False, None, "Error eliminando paciente")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.delete_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_all_pacientes_by_centro(centro_id):
        """Obtener todos los pacientes de un centro específico"""
        try:
            query = """
            SELECT 
                pac.id,
                pac.id_centro,
                pac.fecha_ingreso,
                pac.estado_tratamiento,
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
                CONCAT(pt.nombre, ' ', pt.apellido) as nombre_tutor,
                pt.telefono as telefono_tutor,
                pt.correo as correo_tutor
                -- Sin especialidad directa (se maneja por tabla paciente_especialidades),
                -- Información del centro
                c.nombre as centro_nombre,
                c.codigo as centro_codigo
            FROM paciente pac
            INNER JOIN persona p ON pac.id_persona = p.id
            INNER JOIN tutor t ON pac.id_tutor = t.id
            INNER JOIN persona pt ON t.id_persona = pt.id
            LEFT JOIN centros c ON pac.id_centro = c.id
            WHERE pac.estado != 'eliminado' AND pac.id_centro = %s
            ORDER BY p.nombre, p.apellido
            """

            pacientes = DataBaseHandle.getRecords(query, (centro_id,))

            if pacientes is not None:
                # Formatear los datos para mantener compatibilidad con el frontend
                for paciente in pacientes:
                    # Temporarily commented out especialidad logic
                    if False:  # paciente['especialidad_id']:
                        paciente['especialidades'] = [{
                            'id': paciente['especialidad_id'],
                            'nombre': paciente['especialidad_nombre'],
                            'area': paciente['especialidad_area'],
                            'estado_tratamiento': paciente['estado_tratamiento'],
                            'fecha_inicio': paciente['fecha_inicio_tratamiento'],
                            'fecha_fin': paciente['fecha_fin_tratamiento']
                        }]
                        paciente['total_especialidades'] = 1
                        paciente['especialidades_activas'] = 1 if paciente['estado_tratamiento'] == 'activo' else 0
                    else:
                        paciente['especialidades'] = []
                        paciente['total_especialidades'] = 0
                        paciente['especialidades_activas'] = 0

                HandleLogs.write_log(f"PacienteComponent.get_all_pacientes_by_centro - {len(pacientes)} pacientes encontrados para centro {centro_id}")
                return internal_response(True, pacientes, "Pacientes obtenidos correctamente")
            else:
                HandleLogs.write_error("PacienteComponent.get_all_pacientes_by_centro - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_all_pacientes_by_centro - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_paciente_by_id_and_centro(paciente_id, centro_id):
        """Obtener un paciente específico validando que pertenezca al centro"""
        try:
            query = """
            SELECT 
                pac.id,
                pac.id_centro,
                pac.fecha_ingreso,
                pac.estado_tratamiento,
                pac.observaciones,
                pac.estado,
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
                CONCAT(pt.nombre, ' ', pt.apellido) as nombre_tutor,
                pt.telefono as telefono_tutor,
                pt.correo as correo_tutor
                -- Sin especialidad directa (se maneja por tabla paciente_especialidades),
                -- Información del centro
                c.nombre as centro_nombre,
                c.codigo as centro_codigo
            FROM paciente pac
            INNER JOIN persona p ON pac.id_persona = p.id
            INNER JOIN tutor t ON pac.id_tutor = t.id
            INNER JOIN persona pt ON t.id_persona = pt.id
            LEFT JOIN centros c ON pac.id_centro = c.id
            WHERE pac.id = %s AND pac.id_centro = %s AND pac.estado != 'eliminado'
            """

            paciente = DataBaseHandle.getRecords(query, (paciente_id, centro_id), size=1)

            if paciente:
                if paciente['especialidad_id']:
                    paciente['especialidades'] = [{
                        'id': paciente['especialidad_id'],
                        'nombre': paciente['especialidad_nombre'],
                        'area': paciente['especialidad_area'],
                        'estado_tratamiento': paciente['estado_tratamiento'],
                        'fecha_inicio': paciente['fecha_inicio_tratamiento'],
                        'fecha_fin': paciente['fecha_fin_tratamiento']
                    }]
                    paciente['total_especialidades'] = 1
                    paciente['especialidades_activas'] = 1 if paciente['estado_tratamiento'] == 'activo' else 0
                else:
                    paciente['especialidades'] = []
                    paciente['total_especialidades'] = 0
                    paciente['especialidades_activas'] = 0

                HandleLogs.write_log(f"PacienteComponent.get_paciente_by_id_and_centro - Paciente {paciente_id} encontrado en centro {centro_id}")
                return internal_response(True, paciente, "Paciente encontrado")
            else:
                HandleLogs.write_log(f"PacienteComponent.get_paciente_by_id_and_centro - Paciente {paciente_id} no encontrado en centro {centro_id}")
                return internal_response(False, None, "Paciente no encontrado en el centro especificado")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_paciente_by_id_and_centro - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def agregar_especialidad_paciente(paciente_id, especialidad_id, fecha_inicio_tratamiento=None, observaciones=None, usuario_id=None):
        """Agregar una especialidad a un paciente"""
        try:
            # Verificar que no exista ya la asociación activa
            query_check = """
            SELECT id FROM paciente_especialidades 
            WHERE id_paciente = %s AND id_especialidad = %s AND estado = 'activo'
            """
            
            existing = DataBaseHandle.getRecords(query_check, (paciente_id, especialidad_id), size=1)
            
            if existing:
                HandleLogs.write_log(f"PacienteComponent.agregar_especialidad_paciente - Especialidad {especialidad_id} ya existe para paciente {paciente_id}")
                return internal_response(False, None, "La especialidad ya está asignada a este paciente")
            
            # Insertar nueva especialidad
            query_insert = """
            INSERT INTO paciente_especialidades (
                id_paciente, id_especialidad, fecha_inicio_tratamiento, 
                observaciones, usuario_creacion
            )
            VALUES (%s, %s, %s, %s, %s)
            """
            
            success = DataBaseHandle.ExecuteNonQuery(
                query_insert, 
                (paciente_id, especialidad_id, fecha_inicio_tratamiento, observaciones, usuario_id)
            )
            
            if success:
                HandleLogs.write_log(f"PacienteComponent.agregar_especialidad_paciente - Especialidad {especialidad_id} agregada a paciente {paciente_id}")
                return internal_response(True, {"paciente_id": paciente_id, "especialidad_id": especialidad_id}, "Especialidad agregada exitosamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.agregar_especialidad_paciente - Error agregando especialidad {especialidad_id} a paciente {paciente_id}")
                return internal_response(False, None, "Error agregando especialidad")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.agregar_especialidad_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def cambiar_especialidad_principal(paciente_id, nueva_especialidad_id, usuario_id=None):
        """Cambiar especialidad principal de un paciente"""
        try:
            # Verificar que la nueva especialidad esté asignada al paciente
            query_check = """
            SELECT id FROM paciente_especialidades 
            WHERE id_paciente = %s AND id_especialidad = %s AND estado = 'activo'
            """
            
            existing = DataBaseHandle.getRecords(query_check, (paciente_id, nueva_especialidad_id), size=1)
            
            if not existing:
                HandleLogs.write_error(f"PacienteComponent.cambiar_especialidad_principal - Especialidad {nueva_especialidad_id} no está asignada al paciente {paciente_id}")
                return internal_response(False, None, "La especialidad debe estar asignada al paciente antes de ser principal")
            
            # Quitar el flag de principal de todas las especialidades del paciente
            query_update_all = """
            UPDATE paciente_especialidades 
            SET es_principal = FALSE, usuario_modificacion = %s, fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_paciente = %s AND estado = 'activo'
            """
            
            success_all = DataBaseHandle.ExecuteNonQuery(query_update_all, (usuario_id, paciente_id))
            
            if not success_all:
                HandleLogs.write_error(f"PacienteComponent.cambiar_especialidad_principal - Error removiendo flags principales del paciente {paciente_id}")
                return internal_response(False, None, "Error actualizando especialidades")
            
            # Marcar la nueva especialidad como principal
            query_update_principal = """
            UPDATE paciente_especialidades 
            SET es_principal = TRUE, usuario_modificacion = %s, fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_paciente = %s AND id_especialidad = %s AND estado = 'activo'
            """
            
            success_principal = DataBaseHandle.ExecuteNonQuery(
                query_update_principal, 
                (usuario_id, paciente_id, nueva_especialidad_id)
            )
            
            if success_principal:
                HandleLogs.write_log(f"PacienteComponent.cambiar_especialidad_principal - Especialidad {nueva_especialidad_id} marcada como principal para paciente {paciente_id}")
                return internal_response(True, {
                    "paciente_id": paciente_id, 
                    "nueva_especialidad_principal": nueva_especialidad_id
                }, "Especialidad principal cambiada exitosamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.cambiar_especialidad_principal - Error marcando especialidad {nueva_especialidad_id} como principal")
                return internal_response(False, None, "Error cambiando especialidad principal")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.cambiar_especialidad_principal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def remover_especialidad_paciente(paciente_id, especialidad_id):
        """Remover una especialidad de un paciente (marcándola como eliminada)"""
        try:
            query_update = """
            UPDATE paciente_especialidades 
            SET estado = 'eliminado', fecha_modificacion = CURRENT_TIMESTAMP
            WHERE paciente_id = %s AND especialidad_id = %s AND estado = 'activo'
            """
            
            success = DataBaseHandle.ExecuteNonQuery(query_update, (paciente_id, especialidad_id))
            
            if success:
                HandleLogs.write_log(f"PacienteComponent.remover_especialidad_paciente - Especialidad {especialidad_id} removida de paciente {paciente_id}")
                return internal_response(True, {"paciente_id": paciente_id, "especialidad_id": especialidad_id}, "Especialidad removida exitosamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.remover_especialidad_paciente - Error removiendo especialidad {especialidad_id} de paciente {paciente_id}")
                return internal_response(False, None, "Error removiendo especialidad")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.remover_especialidad_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def pausar_especialidad_paciente(paciente_id, especialidad_id, fecha_inicio_pausa, fecha_fin_pausa=None, motivo_pausa=None, observaciones_pausa=None, usuario_id=None):
        """Pausar una especialidad específica de un paciente"""
        try:
            query_update = """
            UPDATE paciente_especialidades 
            SET estado_tratamiento = 'pausado',
                fecha_inicio_pausa = %s,
                fecha_fin_pausa = %s,
                motivo_pausa = %s,
                observaciones_pausa = %s,
                usuario_modificacion = %s,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE paciente_id = %s AND especialidad_id = %s AND estado = 'activo'
            """
            
            success = DataBaseHandle.ExecuteNonQuery(
                query_update, 
                (fecha_inicio_pausa, fecha_fin_pausa, motivo_pausa, observaciones_pausa, usuario_id, paciente_id, especialidad_id)
            )
            
            if success:
                HandleLogs.write_log(f"PacienteComponent.pausar_especialidad_paciente - Especialidad {especialidad_id} pausada para paciente {paciente_id}")
                return internal_response(True, {"paciente_id": paciente_id, "especialidad_id": especialidad_id}, "Especialidad pausada exitosamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.pausar_especialidad_paciente - Error pausando especialidad {especialidad_id} de paciente {paciente_id}")
                return internal_response(False, None, "Error pausando especialidad")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.pausar_especialidad_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def reactivar_especialidad_paciente(paciente_id, especialidad_id, usuario_id=None):
        """Reactivar una especialidad pausada de un paciente"""
        try:
            query_update = """
            UPDATE paciente_especialidades 
            SET estado_tratamiento = 'activo',
                fecha_inicio_pausa = NULL,
                fecha_fin_pausa = NULL,
                motivo_pausa = NULL,
                observaciones_pausa = NULL,
                usuario_modificacion = %s,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE paciente_id = %s AND especialidad_id = %s AND estado = 'activo'
            """
            
            success = DataBaseHandle.ExecuteNonQuery(query_update, (usuario_id, paciente_id, especialidad_id))
            
            if success:
                HandleLogs.write_log(f"PacienteComponent.reactivar_especialidad_paciente - Especialidad {especialidad_id} reactivada para paciente {paciente_id}")
                return internal_response(True, {"paciente_id": paciente_id, "especialidad_id": especialidad_id}, "Especialidad reactivada exitosamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.reactivar_especialidad_paciente - Error reactivando especialidad {especialidad_id} de paciente {paciente_id}")
                return internal_response(False, None, "Error reactivando especialidad")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.reactivar_especialidad_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_especialidades_paciente(paciente_id):
        """Obtener todas las especialidades de un paciente"""
        try:
            query = """
            SELECT 
                pe.id,
                pe.id_especialidad,
                e.nombre as especialidad_nombre,
                e.descripcion as especialidad_area,
                pe.fecha_asignacion,
                pe.fecha_inicio_tratamiento,
                pe.fecha_fin_tratamiento,
                pe.estado_pausa,
                pe.fecha_inicio_pausa_esp,
                pe.fecha_fin_pausa_esp,
                pe.motivo_pausa_esp,
                pe.observaciones,
                pe.estado
            FROM paciente_especialidades pe
            INNER JOIN especialidad e ON pe.id_especialidad = e.id
            WHERE pe.id_paciente = %s AND pe.estado != 'eliminado'
            ORDER BY e.descripcion, e.nombre
            """

            especialidades = DataBaseHandle.getRecords(query, (paciente_id,))

            if especialidades is not None:
                HandleLogs.write_log(f"PacienteComponent.get_especialidades_paciente - {len(especialidades)} especialidades encontradas para paciente {paciente_id}")
                return internal_response(True, especialidades, "Especialidades del paciente obtenidas correctamente")
            else:
                HandleLogs.write_error("PacienteComponent.get_especialidades_paciente - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_especialidades_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_pacientes_con_especialidades_multiples():
        """Obtener pacientes usando la vista de especialidades múltiples"""
        try:
            query = """
            SELECT * FROM vista_pacientes_especialidades
            ORDER BY centro_codigo, nombre_paciente
            """

            pacientes = DataBaseHandle.getRecords(query)

            if pacientes is not None:
                HandleLogs.write_log(f"PacienteComponent.get_pacientes_con_especialidades_multiples - {len(pacientes)} pacientes encontrados")
                return internal_response(True, pacientes, "Pacientes con especialidades múltiples obtenidos correctamente")
            else:
                HandleLogs.write_error("PacienteComponent.get_pacientes_con_especialidades_multiples - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.get_pacientes_con_especialidades_multiples - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def pausar_paciente_general(paciente_id, fecha_inicio_pausa, fecha_fin_pausa=None, motivo_pausa=None, observaciones_pausa=None, usuario_id=None):
        """Pausar todas las especialidades de un paciente (pausa general)"""
        try:
            query_update = """
            UPDATE paciente 
            SET estado = 'pausado',
                fecha_inicio_pausa_general = %s,
                fecha_fin_pausa_general = %s,
                motivo_pausa_general = %s,
                observaciones_pausa_general = %s,
                usuario_modificacion = %s,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            
            success = DataBaseHandle.ExecuteNonQuery(
                query_update, 
                (fecha_inicio_pausa, fecha_fin_pausa, motivo_pausa, observaciones_pausa, usuario_id, paciente_id)
            )
            
            if success:
                HandleLogs.write_log(f"PacienteComponent.pausar_paciente_general - Paciente {paciente_id} pausado generalmente")
                return internal_response(True, {"paciente_id": paciente_id}, "Paciente pausado exitosamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.pausar_paciente_general - Error pausando paciente {paciente_id}")
                return internal_response(False, None, "Error pausando paciente")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.pausar_paciente_general - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def reactivar_paciente_general(paciente_id, usuario_id=None):
        """Reactivar un paciente pausado generalmente"""
        try:
            query_update = """
            UPDATE paciente 
            SET estado = 'activo',
                fecha_inicio_pausa_general = NULL,
                fecha_fin_pausa_general = NULL,
                motivo_pausa_general = NULL,
                observaciones_pausa_general = NULL,
                usuario_modificacion = %s,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            
            success = DataBaseHandle.ExecuteNonQuery(query_update, (usuario_id, paciente_id))
            
            if success:
                HandleLogs.write_log(f"PacienteComponent.reactivar_paciente_general - Paciente {paciente_id} reactivado")
                return internal_response(True, {"paciente_id": paciente_id}, "Paciente reactivado exitosamente")
            else:
                HandleLogs.write_error(f"PacienteComponent.reactivar_paciente_general - Error reactivando paciente {paciente_id}")
                return internal_response(False, None, "Error reactivando paciente")

        except Exception as e:
            HandleLogs.write_error(f"PacienteComponent.reactivar_paciente_general - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

