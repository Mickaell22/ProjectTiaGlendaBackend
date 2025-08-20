from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response
from src.utils.general.centro_middleware import CentroMiddleware


class PersonalComponent:

    @staticmethod
    def get_all_personal():
        """Obtener todo el personal con información completa incluyendo especialidades"""
        try:
            # Obtener información básica del personal con información del centro
            query = """
            SELECT 
                p.id,
                p.cargo as titulo_profesional,
                p.id_centro,
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
                c.nombre as centro_nombre,
                c.codigo as centro_codigo,
                c.turno_principal as centro_turno
            FROM personal p
            INNER JOIN persona pe ON p.persona_id = pe.id
            LEFT JOIN usuario u ON pe.id = u.persona_id
            LEFT JOIN rol r ON u.rol_id = r.id
            LEFT JOIN centros c ON p.id_centro = c.id
            WHERE p.estado != 'eliminado'
            ORDER BY c.nombre, pe.nombre, pe.apellido
            """

            personal = DataBaseHandle.getRecords(query)

            if personal is not None:
                # Para cada miembro del personal, obtener sus especialidades
                for i, personal_item in enumerate(personal):
                    query_especialidades = """
                    SELECT 
                        e.id,
                        e.nombre,
                        e.descripcion as area,
                        ps.fecha_creacion as fecha_asignacion
                    FROM personal_especialidades ps
                    INNER JOIN especialidad e ON ps.id_especialidad = e.id
                    WHERE ps.id_personal = %s AND e.estado = 'activo'
                    ORDER BY e.descripcion as area, e.nombre
                    """
                    
                    especialidades = DataBaseHandle.getRecords(query_especialidades, (personal_item['id'],))
                    personal[i]['especialidades'] = especialidades if especialidades else []

                HandleLogs.write_log(f"PersonalComponent.get_all_personal - {len(personal)} miembros del personal encontrados con especialidades")
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
                p.cargo as titulo_profesional,
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
                    e.descripcion as area,
                    ps.fecha_creacion as fecha_asignacion
                FROM personal_especialidades ps
                INNER JOIN especialidad e ON ps.id_especialidad = e.id
                WHERE ps.id_personal = %s AND e.estado = 'activo'
                ORDER BY e.descripcion as area, e.nombre
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
                INSERT INTO personal (persona_id, id_especialidad, id_centro, fecha_ingreso, cargo, estado, usuario_creacion)
                VALUES (%s, %s, %s, CURRENT_DATE, %s, %s, %s)
                """

            # Get default specialty ID if not provided
            default_especialidad_id = data.get('id_especialidad')
            if not default_especialidad_id:
                # Try to get the first available specialty
                especialidad_query = "SELECT id FROM especialidad WHERE estado = 'activo' ORDER BY id LIMIT 1"
                especialidad_result = DataBaseHandle.getRecords(especialidad_query, size=1)
                default_especialidad_id = especialidad_result['id'] if especialidad_result else 1

            params = (
                data['persona_id'],
                default_especialidad_id,
                data.get('id_centro', 13),  # Default to Centro Norte (id=13)
                data.get('titulo_profesional', '').strip() if data.get('titulo_profesional') else None,
                data.get('estado', 'activo'),
                data.get('usuario_creacion', 1)
            )

            success = DataBaseHandle.ExecuteNonQuery(insert_query, params)

            if success:
                # Obtener el ID del personal recién creado
                id_query = "SELECT id FROM personal WHERE persona_id = %s ORDER BY id DESC LIMIT 1"
                new_personal_data = DataBaseHandle.getRecords(id_query, (data['persona_id'],), size=1)
                
                if new_personal_data and new_personal_data.get('id'):
                    new_id = new_personal_data['id']
                    # Obtener el personal creado con información completa
                    new_personal = PersonalComponent.get_personal_by_id(new_id)
                    HandleLogs.write_log(f"PersonalComponent.create_personal - Personal creado con ID: {new_id}")
                    return internal_response(True, new_personal['data'], "Personal creado exitosamente")
                else:
                    HandleLogs.write_error("PersonalComponent.create_personal - Error obteniendo ID del personal creado")
                    return internal_response(False, None, "Error obteniendo personal creado")
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
                SELECT id FROM personal_especialidades 
                WHERE id_personal = %s AND id_especialidad = %s
            """
            existing = DataBaseHandle.getRecords(assignment_check, (personal_id, especialidad_id), size=1)

            if existing:
                return internal_response(False, None, "Esta especialidad ya está asignada a este personal")

            # Asignar especialidad
            insert_query = """
                INSERT INTO personal_especialidades (id_personal, id_especialidad, usuario_creacion)
                VALUES (%s, %s, %s)
            """

            success = DataBaseHandle.ExecuteNonQuery(insert_query, (personal_id, especialidad_id, usuario_creacion))

            if success:
                # Get the assignment ID for confirmation
                id_query = "SELECT id FROM personal_especialidades WHERE id_personal = %s AND id_especialidad = %s ORDER BY id DESC LIMIT 1"
                assignment_data = DataBaseHandle.getRecords(id_query, (personal_id, especialidad_id), size=1)
                assignment_id = assignment_data['id'] if assignment_data else personal_id
                
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
                SELECT id FROM personal_especialidades 
                WHERE personal_id = %s AND especialidad_id = %s
            """
            existing = DataBaseHandle.getRecords(assignment_check, (personal_id, especialidad_id), size=1)

            if not existing:
                return internal_response(False, None, "Esta especialidad no está asignada a este personal")

            # Quitar asignación
            delete_query = """
                DELETE FROM personal_especialidades 
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
                p.cargo as titulo_profesional,
                p.estado,
                pe.id as persona_id,
                CONCAT(pe.nombre, ' ', pe.apellido) as nombre_completo,
                pe.nombre,
                pe.apellido,
                pe.correo,
                COUNT(ps.id_especialidad) as especialidades_en_area
            FROM personal p
            INNER JOIN persona pe ON p.persona_id = pe.id
            INNER JOIN personal_especialidades ps ON p.id = ps.id_personal
            INNER JOIN especialidad e ON ps.id_especialidad = e.id
            WHERE e.descripcion LIKE %s AND p.estado = 'activo' AND e.estado = 'activo'
            GROUP BY p.id, p.cargo, p.estado, pe.id, pe.nombre, pe.apellido, pe.correo
            ORDER BY pe.nombre, pe.apellido
            """

            # Convert area parameter to search pattern
            search_pattern = f"%{area}%"
            if area == "terapeutico":
                search_pattern = "%terapéutica%"
            elif area == "pedagogico":
                search_pattern = "%pedagógica%"
                
            personal = DataBaseHandle.getRecords(query, (search_pattern,))

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
                e.descripcion as area,
                COUNT(DISTINCT p.id) as personal_por_area
            FROM personal p
            INNER JOIN personal_especialidades ps ON p.id = ps.id_personal
            INNER JOIN especialidad e ON ps.id_especialidad = e.id
            WHERE p.estado = 'activo' AND e.estado = 'activo'
            GROUP BY e.descripcion as area
            ORDER BY e.descripcion as area
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

    @staticmethod
    def get_personal_by_centro(centro_id):
        """Obtener personal filtrado por centro"""
        try:
            query = """
            SELECT 
                p.id,
                p.cargo as titulo_profesional,
                p.id_centro,
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
                c.nombre as centro_nombre,
                c.codigo as centro_codigo,
                c.turno_principal as centro_turno
            FROM personal p
            INNER JOIN persona pe ON p.persona_id = pe.id
            LEFT JOIN usuario u ON pe.id = u.persona_id
            LEFT JOIN rol r ON u.rol_id = r.id
            INNER JOIN centros c ON p.id_centro = c.id
            WHERE p.estado != 'eliminado' AND p.id_centro = %s
            ORDER BY pe.nombre, pe.apellido
            """

            personal = DataBaseHandle.getRecords(query, (centro_id,))

            if personal is not None:
                # Para cada miembro del personal, obtener sus especialidades
                for i, personal_item in enumerate(personal):
                    query_especialidades = """
                    SELECT 
                        e.id,
                        e.nombre,
                        e.descripcion as area,
                        ps.fecha_creacion as fecha_asignacion
                    FROM personal_especialidades ps
                    INNER JOIN especialidad e ON ps.id_especialidad = e.id
                    WHERE ps.id_personal = %s AND e.estado = 'activo'
                    ORDER BY e.descripcion as area, e.nombre
                    """
                    
                    especialidades = DataBaseHandle.getRecords(query_especialidades, (personal_item['id'],))
                    personal[i]['especialidades'] = especialidades if especialidades else []
                    personal[i]['total_especialidades'] = len(personal[i]['especialidades'])

                HandleLogs.write_log(f"PersonalComponent.get_personal_by_centro - {len(personal)} miembros del personal encontrados para centro {centro_id}")
                return internal_response(True, personal, "Personal obtenido correctamente")
            else:
                HandleLogs.write_error("PersonalComponent.get_personal_by_centro - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.get_personal_by_centro - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def agregar_especialidad_personal(personal_id, especialidad_id, usuario_id):
        """Agregar una especialidad a un miembro del personal"""
        try:
            # Verificar que no exista ya la asociación
            query_check = """
            SELECT id FROM personal_especialidades 
            WHERE personal_id = %s AND especialidad_id = %s
            """
            
            existing = DataBaseHandle.getRecords(query_check, (personal_id, especialidad_id), size=1)
            
            if existing:
                HandleLogs.write_log(f"PersonalComponent.agregar_especialidad_personal - Especialidad {especialidad_id} ya existe para personal {personal_id}")
                return internal_response(False, None, "La especialidad ya está asignada a este personal")
            
            # Insertar nueva especialidad
            query_insert = """
            INSERT INTO personal_especialidades (personal_id, especialidad_id, usuario_creacion)
            VALUES (%s, %s, %s)
            """
            
            success = DataBaseHandle.ExecuteNonQuery(query_insert, (personal_id, especialidad_id, usuario_id))
            
            if success:
                HandleLogs.write_log(f"PersonalComponent.agregar_especialidad_personal - Especialidad {especialidad_id} agregada a personal {personal_id}")
                return internal_response(True, {"personal_id": personal_id, "especialidad_id": especialidad_id}, "Especialidad agregada exitosamente")
            else:
                HandleLogs.write_error(f"PersonalComponent.agregar_especialidad_personal - Error agregando especialidad {especialidad_id} a personal {personal_id}")
                return internal_response(False, None, "Error agregando especialidad")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.agregar_especialidad_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def remover_especialidad_personal(personal_id, especialidad_id):
        """Remover una especialidad de un miembro del personal"""
        try:
            query_delete = """
            DELETE FROM personal_especialidades 
            WHERE personal_id = %s AND especialidad_id = %s
            """
            
            success = DataBaseHandle.ExecuteNonQuery(query_delete, (personal_id, especialidad_id))
            
            if success:
                HandleLogs.write_log(f"PersonalComponent.remover_especialidad_personal - Especialidad {especialidad_id} removida de personal {personal_id}")
                return internal_response(True, {"personal_id": personal_id, "especialidad_id": especialidad_id}, "Especialidad removida exitosamente")
            else:
                HandleLogs.write_error(f"PersonalComponent.remover_especialidad_personal - Error removiendo especialidad {especialidad_id} de personal {personal_id}")
                return internal_response(False, None, "Error removiendo especialidad")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.remover_especialidad_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_personal_by_especialidad(especialidad_id, centro_id=None):
        """Obtener personal por especialidad, opcionalmente filtrado por centro"""
        try:
            if centro_id:
                query = """
                SELECT 
                    p.id,
                    p.cargo as titulo_profesional,
                    p.id_centro,
                    pe.id as persona_id,
                    CONCAT(pe.nombre, ' ', pe.apellido) as nombre_completo,
                    pe.nombre,
                    pe.apellido,
                    c.nombre as centro_nombre,
                    c.codigo as centro_codigo,
                    e.nombre as especialidad_nombre,
                    e.descripcion as area as especialidad_area
                FROM personal p
                INNER JOIN persona pe ON p.persona_id = pe.id
                INNER JOIN personal_especialidades ps ON p.id = ps.id_personal
                INNER JOIN especialidad e ON ps.id_especialidad = e.id
                INNER JOIN centros c ON p.id_centro = c.id
                WHERE ps.id_especialidad = %s AND p.id_centro = %s AND p.estado = 'activo'
                ORDER BY pe.nombre, pe.apellido
                """
                params = (especialidad_id, centro_id)
            else:
                query = """
                SELECT 
                    p.id,
                    p.cargo as titulo_profesional,
                    p.id_centro,
                    pe.id as persona_id,
                    CONCAT(pe.nombre, ' ', pe.apellido) as nombre_completo,
                    pe.nombre,
                    pe.apellido,
                    c.nombre as centro_nombre,
                    c.codigo as centro_codigo,
                    e.nombre as especialidad_nombre,
                    e.descripcion as area as especialidad_area
                FROM personal p
                INNER JOIN persona pe ON p.persona_id = pe.id
                INNER JOIN personal_especialidades ps ON p.id = ps.id_personal
                INNER JOIN especialidad e ON ps.id_especialidad = e.id
                INNER JOIN centros c ON p.id_centro = c.id
                WHERE ps.id_especialidad = %s AND p.estado = 'activo'
                ORDER BY c.nombre, pe.nombre, pe.apellido
                """
                params = (especialidad_id,)

            personal = DataBaseHandle.getRecords(query, params)

            if personal is not None:
                HandleLogs.write_log(f"PersonalComponent.get_personal_by_especialidad - {len(personal)} miembros del personal encontrados para especialidad {especialidad_id}")
                return internal_response(True, personal, "Personal obtenido correctamente")
            else:
                HandleLogs.write_error("PersonalComponent.get_personal_by_especialidad - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.get_personal_by_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_especialidades_disponibles(personal_id):
        """Obtener especialidades que no están asignadas a un personal específico"""
        try:
            query = """
            SELECT 
                e.id,
                e.nombre,
                e.descripcion as area,
                e.descripcion
            FROM especialidad e
            WHERE e.estado = 'activo' 
            AND e.id NOT IN (
                SELECT ps.id_especialidad 
                FROM personal_especialidades ps 
                WHERE ps.id_personal = %s
            )
            ORDER BY e.descripcion as area, e.nombre
            """

            especialidades = DataBaseHandle.getRecords(query, (personal_id,))

            if especialidades is not None:
                HandleLogs.write_log(f"PersonalComponent.get_especialidades_disponibles - {len(especialidades)} especialidades disponibles para personal {personal_id}")
                return internal_response(True, especialidades, "Especialidades disponibles obtenidas correctamente")
            else:
                HandleLogs.write_error("PersonalComponent.get_especialidades_disponibles - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.get_especialidades_disponibles - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")