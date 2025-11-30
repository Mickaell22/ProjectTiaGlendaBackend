from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response
from src.utils.general.centro_middleware import CentroMiddleware


class PersonalComponent:

    @staticmethod
    def get_all_personal(centro_id=None):
        """Obtener todo el personal con información completa incluyendo especialidades (filtrado por centro si se especifica)

        IMPORTANTE: Si un usuario tiene acceso a múltiples centros (tabla usuario_centros),
        el personal asociado a ese usuario aparecerá en todos los centros a los que tenga acceso.
        """
        try:
            # Construir query con filtro opcional por centro
            # La lógica es: mostrar personal si:
            # 1. Su id_centro coincide con el centro filtrado, O
            # 2. Su usuario asociado tiene acceso al centro filtrado (en usuario_centros)
            base_query = """
            SELECT DISTINCT
                p.id,
                p.id_persona,
                p.id_especialidad,
                p.numero_registro,
                p.fecha_ingreso,
                p.fecha_salida,
                p.cargo as titulo_profesional,
                p.cargo,
                p.tipo_contrato,
                p.salario,
                p.observaciones,
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
            INNER JOIN persona pe ON p.id_persona = pe.id
            LEFT JOIN usuario u ON pe.id = u.id_persona
            LEFT JOIN rol r ON u.id_rol = r.id
            LEFT JOIN centros c ON p.id_centro = c.id
            LEFT JOIN usuario_centros uc ON u.id = uc.id_usuario
            WHERE p.estado != 'eliminado'"""

            if centro_id:
                # Filtrar por centro: mostrar si el personal pertenece al centro O si su usuario tiene acceso al centro
                query = base_query + """
                AND (p.id_centro = %s OR uc.id_centro = %s)
                ORDER BY c.nombre, pe.nombre, pe.apellido"""
                personal = DataBaseHandle.getRecords(query, (centro_id, centro_id))
            else:
                query = base_query + " ORDER BY c.nombre, pe.nombre, pe.apellido"
                personal = DataBaseHandle.getRecords(query)

            if personal is not None:
                # Para cada miembro del personal, obtener sus especialidades
                for i, personal_item in enumerate(personal):
                    # Combinar especialidad principal + especialidades adicionales
                    query_especialidades = """
                    SELECT DISTINCT
                        e.id,
                        e.nombre,
                        e.area,
                        CASE
                            WHEN e.id = p.id_especialidad THEN p.fecha_creacion
                            ELSE ps.fecha_creacion
                        END as fecha_asignacion,
                        CASE
                            WHEN e.id = p.id_especialidad THEN TRUE
                            ELSE FALSE
                        END as es_principal
                    FROM especialidad e
                    LEFT JOIN personal p ON e.id = p.id_especialidad AND p.id = %s
                    LEFT JOIN personal_especialidades ps ON e.id = ps.id_especialidad AND ps.id_personal = %s
                    WHERE (p.id = %s OR ps.id_personal = %s) AND e.estado = 'activo'
                    ORDER BY es_principal DESC, e.area, e.nombre
                    """

                    especialidades = DataBaseHandle.getRecords(query_especialidades, (personal_item['id'], personal_item['id'], personal_item['id'], personal_item['id']))
                    personal[i]['especialidades'] = especialidades if especialidades else []

                filter_msg = f" (filtrados por centro {centro_id})" if centro_id else ""
                HandleLogs.write_log(f"PersonalComponent.get_all_personal - {len(personal)} miembros del personal encontrados con especialidades{filter_msg}")
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
            INNER JOIN persona pe ON p.id_persona = pe.id
            LEFT JOIN usuario u ON pe.id = u.id_persona
            LEFT JOIN rol r ON u.id_rol = r.id
            WHERE p.id = %s
            """

            personal = DataBaseHandle.getRecords(query_personal, (personal_id,), size=1)

            if personal:
                # Obtener especialidades del personal (principal + adicionales)
                query_especialidades = """
                SELECT DISTINCT
                    e.id,
                    e.nombre,
                    e.area,
                    CASE
                        WHEN e.id = p.id_especialidad THEN p.fecha_creacion
                        ELSE ps.fecha_creacion
                    END as fecha_asignacion,
                    CASE
                        WHEN e.id = p.id_especialidad THEN TRUE
                        ELSE FALSE
                    END as es_principal
                FROM especialidad e
                LEFT JOIN personal p ON e.id = p.id_especialidad AND p.id = %s
                LEFT JOIN personal_especialidades ps ON e.id = ps.id_especialidad AND ps.id_personal = %s
                WHERE (p.id = %s OR ps.id_personal = %s) AND e.estado = 'activo'
                ORDER BY es_principal DESC, e.area, e.nombre
                """

                especialidades = DataBaseHandle.getRecords(query_especialidades, (personal_id, personal_id, personal_id, personal_id))
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
            persona_check = PersonalComponent.check_persona_is_personal(data['id_persona'])
            if persona_check['success'] and persona_check['data']:
                return internal_response(False, None, "Esta persona ya está registrada como personal")

            # Insertar nuevo personal con TODOS los campos que el servicio envía
            insert_query = """
                INSERT INTO personal (
                    id_persona,
                    id_especialidad,
                    id_centro,
                    fecha_ingreso,
                    fecha_salida,
                    titulo_profesional,
                    cargo,
                    tipo_contrato,
                    observaciones,
                    estado,
                    usuario_creacion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

            params = (
                data['id_persona'],
                data['id_especialidad'],
                data['id_centro'],
                data['fecha_ingreso'],  # Usar la fecha que viene del frontend
                data.get('fecha_salida'),  # Puede ser NULL
                data.get('titulo_profesional'),  # Puede ser NULL
                data.get('cargo'),  # Puede ser NULL
                data.get('tipo_contrato'),
                data.get('observaciones'),  # Puede ser NULL
                data.get('estado', 'activo'),
                data.get('usuario_creacion', 1)
            )

            success = DataBaseHandle.ExecuteNonQuery(insert_query, params)

            if success:
                # Obtener el ID del personal recién creado
                id_query = "SELECT id FROM personal WHERE id_persona = %s ORDER BY id DESC LIMIT 1"
                new_personal_data = DataBaseHandle.getRecords(id_query, (data['id_persona'],), size=1)
                
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

            allowed_fields = ['id_persona', 'id_especialidad', 'numero_registro', 'fecha_ingreso', 'fecha_salida', 'titulo_profesional', 'cargo', 'tipo_contrato', 'salario', 'observaciones', 'id_centro', 'estado', 'usuario_modificacion']

            for field in allowed_fields:
                if field in data and data[field] is not None:
                    if field in ['titulo_profesional', 'cargo', 'observaciones'] and isinstance(data[field], str):
                        # Campos de texto que necesitan strip
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
    def check_persona_is_personal(id_persona, exclude_id=None):
        """Verificar si una persona ya está registrada como personal"""
        try:
            if exclude_id:
                query = "SELECT id FROM personal WHERE id_persona = %s AND id != %s"
                params = (id_persona, exclude_id)
            else:
                query = "SELECT id FROM personal WHERE id_persona = %s"
                params = (id_persona,)

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
    def update_especialidad(personal_id, especialidad_id, data, usuario_modificacion=1):
        """Actualizar una especialidad de un miembro del personal"""
        try:
            # Verificar que la asignación existe
            assignment_check = """
                SELECT id FROM personal_especialidades 
                WHERE id_personal = %s AND id_especialidad = %s
            """
            existing = DataBaseHandle.getRecords(assignment_check, (personal_id, especialidad_id), size=1)

            if not existing:
                return internal_response(False, None, "Asignación de especialidad no encontrada")

            # Construir la consulta de actualización dinámicamente
            update_fields = []
            update_values = []
            
            # Campos permitidos para actualizar
            allowed_fields = {
                'nivel_competencia': 'nivel_competencia',
                'es_principal': 'es_principal', 
                'certificacion': 'certificacion',
                'observaciones': 'observaciones'
            }
            
            for field, db_field in allowed_fields.items():
                if field in data:
                    update_fields.append(f"{db_field} = %s")
                    update_values.append(data[field])
            
            if not update_fields:
                return internal_response(False, None, "No hay campos válidos para actualizar")
            
            # Agregar campos de auditoría
            update_fields.append("usuario_modificacion = %s")
            update_fields.append("fecha_modificacion = CURRENT_TIMESTAMP")
            update_values.append(usuario_modificacion)
            
            # Agregar condiciones WHERE
            update_values.extend([personal_id, especialidad_id])
            
            update_query = f"""
                UPDATE personal_especialidades 
                SET {', '.join(update_fields)}
                WHERE id_personal = %s AND id_especialidad = %s
            """

            success = DataBaseHandle.ExecuteNonQuery(update_query, tuple(update_values))

            if success:
                HandleLogs.write_log(f"PersonalComponent.update_especialidad - Especialidad {especialidad_id} actualizada para personal {personal_id}")
                return internal_response(True, {"personal_id": personal_id, "especialidad_id": especialidad_id}, "Especialidad actualizada exitosamente")
            else:
                HandleLogs.write_error(f"PersonalComponent.update_especialidad - Error actualizando especialidad")
                return internal_response(False, None, "Error actualizando especialidad")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.update_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def remove_especialidad(personal_id, especialidad_id):
        """Quitar una especialidad de un miembro del personal"""
        try:
            # Verificar que la asignación existe
            assignment_check = """
                SELECT id FROM personal_especialidades 
                WHERE id_personal = %s AND id_especialidad = %s
            """
            existing = DataBaseHandle.getRecords(assignment_check, (personal_id, especialidad_id), size=1)

            if not existing:
                return internal_response(False, None, "Esta especialidad no está asignada a este personal")

            # Quitar asignación
            delete_query = """
                DELETE FROM personal_especialidades 
                WHERE id_personal = %s AND id_especialidad = %s
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
            INNER JOIN persona pe ON p.id_persona = pe.id
            INNER JOIN personal_especialidades ps ON p.id = ps.id_personal
            INNER JOIN especialidad e ON ps.id_especialidad = e.id
            WHERE e.area LIKE %s AND p.estado = 'activo' AND e.estado = 'activo'
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
            INNER JOIN persona pe ON p.id_persona = pe.id
            LEFT JOIN usuario u ON pe.id = u.id_persona
            """

            estadisticas_generales = DataBaseHandle.getRecords(query, size=1)

            # Estadísticas por área
            query_areas = """
            SELECT 
                e.area,
                COUNT(DISTINCT p.id) as personal_por_area
            FROM personal p
            INNER JOIN personal_especialidades ps ON p.id = ps.id_personal
            INNER JOIN especialidad e ON ps.id_especialidad = e.id
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

    @staticmethod
    def get_personal_by_centro(centro_id):
        """Obtener personal filtrado por centro

        IMPORTANTE: Si un usuario tiene acceso a múltiples centros (tabla usuario_centros),
        el personal asociado a ese usuario aparecerá en todos los centros a los que tenga acceso.
        """
        try:
            query = """
            SELECT DISTINCT
                p.id,
                p.id_persona,
                p.id_especialidad,
                p.numero_registro,
                p.fecha_ingreso,
                p.fecha_salida,
                p.cargo as titulo_profesional,
                p.cargo,
                p.tipo_contrato,
                p.salario,
                p.observaciones,
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
            INNER JOIN persona pe ON p.id_persona = pe.id
            LEFT JOIN usuario u ON pe.id = u.id_persona
            LEFT JOIN rol r ON u.id_rol = r.id
            INNER JOIN centros c ON p.id_centro = c.id
            LEFT JOIN usuario_centros uc ON u.id = uc.id_usuario
            WHERE p.estado != 'eliminado'
            AND (p.id_centro = %s OR uc.id_centro = %s)
            ORDER BY pe.nombre, pe.apellido
            """

            personal = DataBaseHandle.getRecords(query, (centro_id, centro_id))

            if personal is not None:
                # Para cada miembro del personal, obtener sus especialidades
                for i, personal_item in enumerate(personal):
                    query_especialidades = """
                    SELECT 
                        e.id,
                        e.nombre,
                        e.area,
                        ps.fecha_creacion as fecha_asignacion
                    FROM personal_especialidades ps
                    INNER JOIN especialidad e ON ps.id_especialidad = e.id
                    WHERE ps.id_personal = %s AND e.estado = 'activo'
                    ORDER BY e.area, e.nombre
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
            WHERE id_personal = %s AND id_especialidad = %s
            """
            
            existing = DataBaseHandle.getRecords(query_check, (personal_id, especialidad_id), size=1)
            
            if existing:
                HandleLogs.write_log(f"PersonalComponent.agregar_especialidad_personal - Especialidad {especialidad_id} ya existe para personal {personal_id}")
                return internal_response(False, None, "La especialidad ya está asignada a este personal")
            
            # Insertar nueva especialidad
            query_insert = """
            INSERT INTO personal_especialidades (id_personal, id_especialidad, usuario_creacion)
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
            WHERE id_personal = %s AND id_especialidad = %s
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
        """Obtener personal por especialidad, opcionalmente filtrado por centro

        IMPORTANTE: Si un usuario tiene acceso a múltiples centros (tabla usuario_centros),
        el personal asociado a ese usuario aparecerá en todos los centros a los que tenga acceso.
        """
        try:
            if centro_id:
                query = """
                SELECT DISTINCT
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
                    e.area as especialidad_area
                FROM personal p
                INNER JOIN persona pe ON p.id_persona = pe.id
                INNER JOIN personal_especialidades ps ON p.id = ps.id_personal
                INNER JOIN especialidad e ON ps.id_especialidad = e.id
                INNER JOIN centros c ON p.id_centro = c.id
                LEFT JOIN usuario u ON pe.id = u.id_persona
                LEFT JOIN usuario_centros uc ON u.id = uc.id_usuario
                WHERE ps.id_especialidad = %s
                AND (p.id_centro = %s OR uc.id_centro = %s)
                AND p.estado = 'activo'
                ORDER BY pe.nombre, pe.apellido
                """
                params = (especialidad_id, centro_id, centro_id)
            else:
                query = """
                SELECT DISTINCT
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
                    e.area as especialidad_area
                FROM personal p
                INNER JOIN persona pe ON p.id_persona = pe.id
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
                e.area
            FROM especialidad e
            WHERE e.estado = 'activo' 
            AND e.id NOT IN (
                SELECT ps.id_especialidad 
                FROM personal_especialidades ps 
                WHERE ps.id_personal = %s
            )
            ORDER BY e.area, e.nombre
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

    @staticmethod
    def get_personal_by_area_and_centro(area, centro_id):
        """Obtener personal por área y centro específico

        IMPORTANTE: Si un usuario tiene acceso a múltiples centros (tabla usuario_centros),
        el personal asociado a ese usuario aparecerá en todos los centros a los que tenga acceso.
        """
        try:
            HandleLogs.write_log(f"PersonalComponent.get_personal_by_area_and_centro - Área: {area}, Centro: {centro_id}")

            query = """
            SELECT DISTINCT
                p.id,
                p.id_persona,
                p.cargo,
                p.estado,
                p.id_centro,
                -- Información personal
                CONCAT(pe.nombre, ' ', pe.apellido) as nombre_completo,
                pe.nombre,
                pe.apellido,
                pe.cedula,
                pe.telefono,
                pe.correo,
                pe.direccion,
                pe.fecha_nacimiento,
                -- Información del centro
                c.nombre as centro_nombre,
                c.codigo as centro_codigo,
                -- Información de usuario si existe
                u.id as usuario_id,
                u.usuario as username,
                r.nombre as rol_nombre,
                -- Información de especialidades
                STRING_AGG(DISTINCT e.nombre, ', ') as especialidades,
                COUNT(DISTINCT e.id) as total_especialidades
            FROM personal p
            INNER JOIN persona pe ON p.id_persona = pe.id
            LEFT JOIN centros c ON p.id_centro = c.id
            LEFT JOIN usuario u ON pe.id = u.id_persona
            LEFT JOIN rol r ON u.id_rol = r.id
            LEFT JOIN usuario_centros uc ON u.id = uc.id_usuario
            LEFT JOIN personal_especialidades pes ON p.id = pes.id_personal AND pes.estado = 'activo'
            LEFT JOIN especialidad e ON pes.id_especialidad = e.id
            WHERE p.estado = 'activo'
            AND (p.id_centro = %s OR uc.id_centro = %s)
            AND LOWER(e.area) LIKE LOWER(%s)
            GROUP BY p.id, p.id_persona, p.cargo, p.estado, p.id_centro,
                     pe.nombre, pe.apellido, pe.cedula, pe.telefono, pe.correo,
                     pe.direccion, pe.fecha_nacimiento, c.nombre, c.codigo,
                     u.id, u.usuario, r.nombre
            ORDER BY pe.nombre, pe.apellido
            """

            area_pattern = f'%{area}%'
            result = DataBaseHandle.getRecords(query, (centro_id, centro_id, area_pattern))

            if result is not None:
                # Formatear fechas para JSON serialization
                for personal in result:
                    if personal.get('fecha_nacimiento'):
                        personal['fecha_nacimiento'] = personal['fecha_nacimiento'].isoformat()

                HandleLogs.write_log(f"PersonalComponent.get_personal_by_area_and_centro - {len(result)} registros encontrados para área '{area}' en centro {centro_id}")
                return internal_response(True, result, "Personal por área y centro obtenido correctamente")
            else:
                HandleLogs.write_error(f"PersonalComponent.get_personal_by_area_and_centro - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PersonalComponent.get_personal_by_area_and_centro - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")