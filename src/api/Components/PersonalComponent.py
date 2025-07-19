from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class PersonalComponent:

    @staticmethod
    def get_all_personal():
        """Obtener todo el personal con información completa"""
        try:
            query = """
            SELECT 
                p.id,
                p.titulo_profesional,
                p.estado,
                p.fecha_creacion,
                p.fecha_modificacion,
                pe.id as persona_id,
                CONCAT(pe.nombre, ' ', pe.apellido) as nombre_completo,
                pe.nombre,
                pe.apellido,
                pe.cedula,
                pe.telefono,
                pe.correo,
                pe.direccion,
                u.id as usuario_id,
                u.usuario as nombre_usuario,
                r.nombre as rol_usuario,
                COUNT(ps.especialidad_id) as total_especialidades
            FROM personal p
            INNER JOIN persona pe ON p.persona_id = pe.id
            LEFT JOIN usuario u ON pe.id = u.persona_id
            LEFT JOIN rol r ON u.rol_id = r.id
            LEFT JOIN personal_especialidad ps ON p.id = ps.personal_id
            GROUP BY p.id, p.titulo_profesional, p.estado, p.fecha_creacion, p.fecha_modificacion,
                     pe.id, pe.nombre, pe.apellido, pe.cedula, pe.telefono, pe.correo, pe.direccion,
                     u.id, u.usuario, r.nombre
            ORDER BY pe.nombre, pe.apellido
            """

            personal = DataBaseHandle.getRecords(query)

            if personal is not None:
                HandleLogs.write_log(f"PersonalComponent.get_all_personal - {len(personal)} miembros del personal encontrados")
                return internal_response(True, personal, "Personal obtenido correctamente")
            else:
                HandleLogs.write_error("PersonalComponent.get_all_personal - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.get_all_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_personal_by_id(personal_id):
        """Obtener un miembro del personal por ID con todas sus especialidades"""
        try:
            # Obtener información básica del personal
            query_personal = """
            SELECT 
                p.id,
                p.titulo_profesional,
                p.estado,
                p.fecha_creacion,
                p.fecha_modificacion,
                pe.id as persona_id,
                CONCAT(pe.nombre, ' ', pe.apellido) as nombre_completo,
                pe.nombre,
                pe.apellido,
                pe.cedula,
                pe.telefono,
                pe.correo,
                pe.direccion,
                pe.fecha_nacimiento,
                u.id as usuario_id,
                u.usuario as nombre_usuario,
                r.nombre as rol_usuario
            FROM personal p
            INNER JOIN persona pe ON p.persona_id = pe.id
            LEFT JOIN usuario u ON pe.id = u.persona_id
            LEFT JOIN rol r ON u.rol_id = r.id
            WHERE p.id = %s
            """

            personal = DataBaseHandle.getRecords(query_personal, (personal_id,), size=1)

            if personal:
                # Obtener especialidades del personal
                query_especialidades = """
                SELECT 
                    e.id,
                    e.nombre,
                    e.area,
                    ps.fecha_creacion as fecha_asignacion
                FROM personal_especialidad ps
                INNER JOIN especialidad e ON ps.especialidad_id = e.id
                WHERE ps.personal_id = %s AND e.estado = 'activo'
                ORDER BY e.area, e.nombre
                """

                especialidades = DataBaseHandle.getRecords(query_especialidades, (personal_id,))
                personal['especialidades'] = especialidades if especialidades else []

                HandleLogs.write_log(f"PersonalComponent.get_personal_by_id - Personal {personal_id} encontrado")
                return internal_response(True, personal, "Personal encontrado")
            else:
                HandleLogs.write_log(f"PersonalComponent.get_personal_by_id - Personal {personal_id} no encontrado")
                return internal_response(True, None, "Personal no encontrado")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.get_personal_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def create_personal(data):
        """Crear un nuevo miembro del personal"""
        try:
            # Verificar si la persona ya está registrada como personal
            persona_check = PersonalComponent.check_persona_is_personal(data['persona_id'])
            if persona_check['success'] and persona_check['data']:
                return internal_response(False, None, "Esta persona ya está registrada como personal")

            # Insertar nuevo personal
            insert_query = """
                INSERT INTO personal (persona_id, titulo_profesional, estado, usuario_creacion)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """

            params = (
                data['persona_id'],
                data.get('titulo_profesional', '').strip() if data.get('titulo_profesional') else None,
                data.get('estado', 'activo'),
                data.get('usuario_creacion', 1)
            )

            new_id = DataBaseHandle.ExecuteInsert(insert_query, params)

            if new_id:
                # Obtener el personal creado con información completa
                new_personal = PersonalComponent.get_personal_by_id(new_id)
                HandleLogs.write_log(f"PersonalComponent.create_personal - Personal creado con ID: {new_id}")
                return internal_response(True, new_personal['data'], "Personal creado exitosamente")
            else:
                HandleLogs.write_error("PersonalComponent.create_personal - Error insertando personal")
                return internal_response(False, None, "Error creando personal")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.create_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def update_personal(personal_id, data):
        """Actualizar un miembro del personal existente"""
        try:
            # Verificar si el personal existe
            check_query = "SELECT id FROM personal WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (personal_id,), size=1)

            if not existing:
                return internal_response(False, None, "Personal no encontrado")

            # Construir query de actualización dinámicamente
            update_fields = []
            params = []

            allowed_fields = ['titulo_profesional', 'estado', 'usuario_modificacion']

            for field in allowed_fields:
                if field in data and data[field] is not None:
                    if field == 'titulo_profesional':
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

            # Agregar ID del personal al final
            params.append(personal_id)

            update_query = f"""
                UPDATE personal 
                SET {', '.join(update_fields)}
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, params)

            if success:
                # Obtener datos actualizados
                updated_personal = PersonalComponent.get_personal_by_id(personal_id)
                HandleLogs.write_log(f"PersonalComponent.update_personal - Personal {personal_id} actualizado")
                return internal_response(True, updated_personal['data'], "Personal actualizado exitosamente")
            else:
                HandleLogs.write_error(f"PersonalComponent.update_personal - Error actualizando personal {personal_id}")
                return internal_response(False, None, "Error actualizando personal")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.update_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def deactivate_personal(personal_id):
        """Desactivar personal (eliminación lógica)"""
        try:
            # Verificar si el personal existe
            check_query = "SELECT id, estado FROM personal WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (personal_id,), size=1)

            if not existing:
                return internal_response(False, None, "Personal no encontrado")

            if existing['estado'] == 'inactivo':
                return internal_response(False, None, "Personal ya esta inactivo")

            # Desactivar personal
            update_query = """
                UPDATE personal 
                SET estado = 'inactivo', fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (personal_id,))

            if success:
                HandleLogs.write_log(f"PersonalComponent.deactivate_personal - Personal {personal_id} desactivado")
                return internal_response(True, {"id": personal_id, "estado": "inactivo"},
                                         "Personal desactivado exitosamente")
            else:
                HandleLogs.write_error(f"PersonalComponent.deactivate_personal - Error desactivando personal {personal_id}")
                return internal_response(False, None, "Error desactivando personal")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.deactivate_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def check_persona_is_personal(persona_id, exclude_id=None):
        """Verificar si una persona ya está registrada como personal"""
        try:
            if exclude_id:
                query = "SELECT id FROM personal WHERE persona_id = %s AND id != %s"
                params = (persona_id, exclude_id)
            else:
                query = "SELECT id FROM personal WHERE persona_id = %s"
                params = (persona_id,)

            existing = DataBaseHandle.getRecords(query, params, size=1)
            return internal_response(True, existing is not None, "Consulta ejecutada")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.check_persona_is_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def assign_especialidad(personal_id, especialidad_id, usuario_creacion=1):
        """Asignar una especialidad a un miembro del personal"""
        try:
            # Verificar que el personal existe y está activo
            personal_check = "SELECT id, estado FROM personal WHERE id = %s"
            personal = DataBaseHandle.getRecords(personal_check, (personal_id,), size=1)

            if not personal:
                return internal_response(False, None, "Personal no encontrado")

            if personal['estado'] != 'activo':
                return internal_response(False, None, "El personal debe estar activo para asignar especialidades")

            # Verificar que la especialidad existe y está activa
            esp_check = "SELECT id, estado FROM especialidad WHERE id = %s"
            especialidad = DataBaseHandle.getRecords(esp_check, (especialidad_id,), size=1)

            if not especialidad:
                return internal_response(False, None, "Especialidad no encontrada")

            if especialidad['estado'] != 'activo':
                return internal_response(False, None, "La especialidad debe estar activa para ser asignada")

            # Verificar que no esté ya asignada
            assignment_check = """
                SELECT id FROM personal_especialidad 
                WHERE personal_id = %s AND especialidad_id = %s
            """
            existing = DataBaseHandle.getRecords(assignment_check, (personal_id, especialidad_id), size=1)

            if existing:
                return internal_response(False, None, "Esta especialidad ya está asignada a este personal")

            # Asignar especialidad
            insert_query = """
                INSERT INTO personal_especialidad (personal_id, especialidad_id, usuario_creacion)
                VALUES (%s, %s, %s)
                RETURNING id
            """

            assignment_id = DataBaseHandle.ExecuteInsert(insert_query, (personal_id, especialidad_id, usuario_creacion))

            if assignment_id:
                HandleLogs.write_log(f"PersonalComponent.assign_especialidad - Especialidad {especialidad_id} asignada a personal {personal_id}")
                return internal_response(True, {"assignment_id": assignment_id}, "Especialidad asignada exitosamente")
            else:
                HandleLogs.write_error(f"PersonalComponent.assign_especialidad - Error asignando especialidad")
                return internal_response(False, None, "Error asignando especialidad")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.assign_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def remove_especialidad(personal_id, especialidad_id):
        """Quitar una especialidad de un miembro del personal"""
        try:
            # Verificar que la asignación existe
            assignment_check = """
                SELECT id FROM personal_especialidad 
                WHERE personal_id = %s AND especialidad_id = %s
            """
            existing = DataBaseHandle.getRecords(assignment_check, (personal_id, especialidad_id), size=1)

            if not existing:
                return internal_response(False, None, "Esta especialidad no está asignada a este personal")

            # Quitar asignación
            delete_query = """
                DELETE FROM personal_especialidad 
                WHERE personal_id = %s AND especialidad_id = %s
            """

            success = DataBaseHandle.ExecuteNonQuery(delete_query, (personal_id, especialidad_id))

            if success:
                HandleLogs.write_log(f"PersonalComponent.remove_especialidad - Especialidad {especialidad_id} removida del personal {personal_id}")
                return internal_response(True, None, "Especialidad removida exitosamente")
            else:
                HandleLogs.write_error(f"PersonalComponent.remove_especialidad - Error removiendo especialidad")
                return internal_response(False, None, "Error removiendo especialidad")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.remove_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_personal_by_area(area):
        """Obtener personal que tiene especialidades en un área específica"""
        try:
            query = """
            SELECT DISTINCT
                p.id,
                p.titulo_profesional,
                p.estado,
                pe.id as persona_id,
                CONCAT(pe.nombre, ' ', pe.apellido) as nombre_completo,
                pe.nombre,
                pe.apellido,
                pe.correo,
                COUNT(ps.especialidad_id) as especialidades_en_area
            FROM personal p
            INNER JOIN persona pe ON p.persona_id = pe.id
            INNER JOIN personal_especialidad ps ON p.id = ps.personal_id
            INNER JOIN especialidad e ON ps.especialidad_id = e.id
            WHERE e.area = %s AND p.estado = 'activo' AND e.estado = 'activo'
            GROUP BY p.id, p.titulo_profesional, p.estado, pe.id, pe.nombre, pe.apellido, pe.correo
            ORDER BY pe.nombre, pe.apellido
            """

            personal = DataBaseHandle.getRecords(query, (area,))

            if personal is not None:
                HandleLogs.write_log(f"PersonalComponent.get_personal_by_area - {len(personal)} personal de área {area} encontrado")
                return internal_response(True, personal, f"Personal de {area} obtenido correctamente")
            else:
                HandleLogs.write_error(f"PersonalComponent.get_personal_by_area - Error en consulta para área {area}")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.get_personal_by_area - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_estadisticas_personal():
        """Obtener estadísticas del personal"""
        try:
            query = """
            SELECT 
                COUNT(*) as total_personal,
                COUNT(CASE WHEN p.estado = 'activo' THEN 1 END) as personal_activo,
                COUNT(CASE WHEN p.estado = 'inactivo' THEN 1 END) as personal_inactivo,
                COUNT(CASE WHEN u.id IS NOT NULL THEN 1 END) as con_usuario,
                COUNT(CASE WHEN u.id IS NULL THEN 1 END) as sin_usuario
            FROM personal p
            INNER JOIN persona pe ON p.persona_id = pe.id
            LEFT JOIN usuario u ON pe.id = u.persona_id
            """

            estadisticas_generales = DataBaseHandle.getRecords(query, size=1)

            # Estadísticas por área
            query_areas = """
            SELECT 
                e.area,
                COUNT(DISTINCT p.id) as personal_por_area
            FROM personal p
            INNER JOIN personal_especialidad ps ON p.id = ps.personal_id
            INNER JOIN especialidad e ON ps.especialidad_id = e.id
            WHERE p.estado = 'activo' AND e.estado = 'activo'
            GROUP BY e.area
            ORDER BY e.area
            """

            estadisticas_areas = DataBaseHandle.getRecords(query_areas)

            resultado = {
                "general": estadisticas_generales,
                "por_area": estadisticas_areas if estadisticas_areas else []
            }

            if estadisticas_generales is not None:
                HandleLogs.write_log("PersonalComponent.get_estadisticas_personal - Estadísticas obtenidas")
                return internal_response(True, resultado, "Estadísticas del personal obtenidas")
            else:
                HandleLogs.write_error("PersonalComponent.get_estadisticas_personal - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.get_estadisticas_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")