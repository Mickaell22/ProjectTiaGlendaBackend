from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class PersonaComponent:

    @staticmethod
    def get_all_personas(centro_id=None):
        """Obtener todas las personas (filtradas por centro si se especifica)"""
        try:
            if centro_id:
                # Consulta filtrada por centro: incluye personas que son usuarios, personal, pacientes 
                # o tutores de pacientes del centro
                query = """
                SELECT DISTINCT
                    p.id,
                    p.nombre,
                    p.apellido,
                    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                    p.cedula,
                    p.telefono,
                    p.correo,
                    p.direccion,
                    p.fecha_nacimiento::DATE as fecha_nacimiento,
                    p.estado,
                    p.fecha_creacion::TEXT as fecha_creacion,
                    p.fecha_modificacion::TEXT as fecha_modificacion,
                    CASE
                        WHEN u.id IS NOT NULL THEN 'Si'
                        ELSE 'No'
                    END as tiene_usuario,
                    r.nombre as rol_usuario,
                    c.nombre as centro_nombre,
                    c.codigo as centro_codigo,
                    CASE
                        WHEN u.id IS NOT NULL THEN 'Usuario'
                        WHEN per.id IS NOT NULL THEN 'Personal'
                        WHEN pac.id IS NOT NULL THEN 'Paciente'
                        WHEN tut.id IS NOT NULL THEN 'Tutor'
                        ELSE 'Otro'
                    END as tipo_relacion_centro
                FROM persona p
                LEFT JOIN usuario u ON p.id = u.id_persona AND u.id_centro = %s
                LEFT JOIN rol r ON u.id_rol = r.id
                LEFT JOIN centros c ON u.id_centro = c.id
                LEFT JOIN personal per ON p.id = per.id_persona AND per.id_centro = %s
                LEFT JOIN paciente pac ON p.id = pac.id_persona AND pac.id_centro = %s
                -- Incluir personas que son tutores de pacientes del centro
                LEFT JOIN (
                    SELECT DISTINCT t.id, t.id_persona
                    FROM tutor t
                    INNER JOIN paciente pac_t ON t.id = pac_t.id_tutor
                    WHERE pac_t.id_centro = %s
                ) tut ON p.id = tut.id_persona
                WHERE (
                    u.id_centro = %s OR 
                    per.id_centro = %s OR 
                    pac.id_centro = %s OR
                    tut.id IS NOT NULL
                )
                ORDER BY p.id
                """
                
                personas = DataBaseHandle.getRecords(query, (centro_id, centro_id, centro_id, centro_id, centro_id, centro_id, centro_id))
            else:
                # Consulta sin filtro (solo para administradores de sistema)
                query = """
                SELECT
                    p.id,
                    p.nombre,
                    p.apellido,
                    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                    p.cedula,
                    p.telefono,
                    p.correo,
                    p.direccion,
                    p.fecha_nacimiento::DATE as fecha_nacimiento,
                    p.estado,
                    p.fecha_creacion::TEXT as fecha_creacion,
                    p.fecha_modificacion::TEXT as fecha_modificacion,
                    CASE
                        WHEN u.id IS NOT NULL THEN 'Si'
                        ELSE 'No'
                    END as tiene_usuario,
                    r.nombre as rol_usuario,
                    c.nombre as centro_nombre,
                    c.codigo as centro_codigo
                FROM persona p
                LEFT JOIN usuario u ON p.id = u.id_persona
                LEFT JOIN rol r ON u.id_rol = r.id
                LEFT JOIN centros c ON u.id_centro = c.id
                ORDER BY p.id
                """
                
                personas = DataBaseHandle.getRecords(query)

            if personas is not None:
                filter_msg = f" (filtradas por centro {centro_id})" if centro_id else ""
                HandleLogs.write_log(f"PersonaComponent.get_all_personas - {len(personas)} personas encontradas{filter_msg}")
                return internal_response(True, personas, "Personas obtenidas correctamente")
            else:
                HandleLogs.write_error("PersonaComponent.get_all_personas - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.get_all_personas - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_persona_by_id(id_persona):
        """Obtener una persona por ID"""
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
                p.direccion,
                p.fecha_nacimiento::DATE as fecha_nacimiento,
                p.estado,
                p.fecha_creacion::TEXT as fecha_creacion,
                p.fecha_modificacion::TEXT as fecha_modificacion,
                CASE
                    WHEN u.id IS NOT NULL THEN 'Si'
                    ELSE 'No'
                END as tiene_usuario,
                u.id as usuario_id,
                u.usuario as nombre_usuario,
                r.nombre as rol_usuario
            FROM persona p
            LEFT JOIN usuario u ON p.id = u.id_persona
            LEFT JOIN rol r ON u.id_rol = r.id
            WHERE p.id = %s
            """

            result = DataBaseHandle.getRecordsWithStatus(query, (id_persona,), size=1)

            if result['success']:
                if result['data']:
                    persona = result['data']
                    HandleLogs.write_log(f"PersonaComponent.get_persona_by_id - Persona {id_persona} encontrada")
                    return internal_response(True, persona, "Persona encontrada")
                else:
                    HandleLogs.write_log(f"PersonaComponent.get_persona_by_id - Persona {id_persona} no encontrada")
                    return internal_response(True, None, "Persona no encontrada")
            else:
                HandleLogs.write_error(f"PersonaComponent.get_persona_by_id - Error en consulta: {result['error']}")
                return internal_response(False, None, f"Error en consulta: {result['error']}")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.get_persona_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def create_persona(data):
        """Crear una nueva persona"""
        try:
            # Verificar si la cedula ya existe
            cedula_check = PersonaComponent.check_cedula_exists(data['cedula'])
            if cedula_check['success'] and cedula_check['data']:
                return internal_response(False, None, "La cedula ya existe")

            # Verificar email si se proporciona
            if data.get('correo'):
                email_check = PersonaComponent.check_email_exists(data['correo'])
                if email_check['success'] and email_check['data']:
                    return internal_response(False, None, "El correo electronico ya existe")

            # Insertar nueva persona
            insert_query = """
                INSERT INTO persona (
                    nombre, apellido, cedula, telefono, correo, 
                    direccion, fecha_nacimiento, estado, usuario_creacion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """

            params = (
                data['nombre'].strip(),
                data['apellido'].strip(),
                data['cedula'].strip(),
                data.get('telefono', '').strip() if data.get('telefono') else None,
                data.get('correo', '').strip() if data.get('correo') else None,
                data.get('direccion', '').strip() if data.get('direccion') else None,
                data.get('fecha_nacimiento') if data.get('fecha_nacimiento') else None,
                data.get('estado', 'activo'),
                data.get('usuario_creacion', 1)
            )

            new_id = DataBaseHandle.ExecuteInsert(insert_query, params)

            if new_id:
                # Obtener la persona creada con información completa
                new_persona = PersonaComponent.get_persona_by_id(new_id)
                HandleLogs.write_log(f"PersonaComponent.create_persona - Persona creada con ID: {new_id}")
                
                if new_persona and new_persona.get('success') and new_persona.get('data'):
                    return internal_response(True, new_persona['data'], "Persona creada exitosamente")
                else:
                    # Si no podemos obtener los datos, retornar al menos el ID
                    return internal_response(True, {"id": new_id}, "Persona creada exitosamente")
            else:
                HandleLogs.write_error("PersonaComponent.create_persona - Error insertando persona")
                return internal_response(False, None, "Error creando persona")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.create_persona - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def update_persona(id_persona, data):
        """Actualizar una persona existente"""
        try:
            # Verificar si la persona existe
            check_query = "SELECT id FROM persona WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (id_persona,), size=1)

            if not existing:
                return internal_response(False, None, "Persona no encontrada")

            # Verificar cedula duplicada (excluyendo la persona actual)
            if 'cedula' in data and data['cedula']:
                cedula_check = PersonaComponent.check_cedula_exists(data['cedula'], exclude_id=id_persona)
                if cedula_check['success'] and cedula_check['data']:
                    return internal_response(False, None, "La cedula ya existe")

            # Verificar email duplicado (excluyendo la persona actual)
            if 'correo' in data and data['correo']:
                email_check = PersonaComponent.check_email_exists(data['correo'], exclude_id=id_persona)
                if email_check['success'] and email_check['data']:
                    return internal_response(False, None, "El correo electronico ya existe")

            # Construir query de actualización dinámicamente
            update_fields = []
            params = []

            # Campos requeridos (no pueden ser NULL)
            required_fields = ['nombre', 'apellido', 'cedula']
            # Campos opcionales (pueden ser NULL)
            nullable_fields = ['telefono', 'correo', 'direccion', 'fecha_nacimiento']
            # Campos de control
            control_fields = ['estado', 'usuario_modificacion']

            allowed_fields = required_fields + nullable_fields + control_fields

            for field in allowed_fields:
                if field not in data:
                    continue

                value = data[field]

                if field in required_fields:
                    # Campos requeridos: solo actualizar si tienen valor
                    if value is not None and isinstance(value, str) and value.strip():
                        update_fields.append(f"{field} = %s")
                        params.append(value.strip())
                elif field in nullable_fields:
                    # Campos opcionales: permitir setear NULL con valor vacio o None
                    if value is None or (isinstance(value, str) and not value.strip()):
                        update_fields.append(f"{field} = NULL")
                    elif isinstance(value, str) and value.strip():
                        update_fields.append(f"{field} = %s")
                        params.append(value.strip())
                    else:
                        update_fields.append(f"{field} = %s")
                        params.append(value)
                else:
                    # Campos de control
                    if value is not None:
                        update_fields.append(f"{field} = %s")
                        params.append(value)

            if not update_fields:
                return internal_response(False, None, "No hay campos para actualizar")

            # Agregar fecha de modificación
            update_fields.append("fecha_modificacion = CURRENT_TIMESTAMP")

            # Agregar ID de la persona al final
            params.append(id_persona)

            update_query = f"""
                UPDATE persona 
                SET {', '.join(update_fields)}
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, params)

            if success:
                # Obtener datos actualizados
                updated_persona = PersonaComponent.get_persona_by_id(id_persona)
                HandleLogs.write_log(f"PersonaComponent.update_persona - Persona {id_persona} actualizada")
                return internal_response(True, updated_persona['data'], "Persona actualizada exitosamente")
            else:
                HandleLogs.write_error(f"PersonaComponent.update_persona - Error actualizando persona {id_persona}")
                return internal_response(False, None, "Error actualizando persona")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.update_persona - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def deactivate_persona(id_persona):
        """Desactivar persona (eliminación lógica)"""
        try:
            # Verificar si la persona existe
            check_query = "SELECT id, estado FROM persona WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (id_persona,), size=1)

            if not existing:
                return internal_response(False, None, "Persona no encontrada")

            if existing['estado'] == 'inactivo':
                return internal_response(False, None, "Persona ya esta inactiva")

            # Verificar si la persona tiene un usuario activo asociado
            user_check = "SELECT id, estado FROM usuario WHERE id_persona = %s AND estado = 'activo'"
            user_exists = DataBaseHandle.getRecords(user_check, (id_persona,), size=1)

            if user_exists:
                return internal_response(False, None,
                    "No se puede desactivar la persona porque tiene un usuario activo asociado")

            # Verificar si la persona tiene un registro de personal activo
            personal_check = "SELECT id, estado FROM personal WHERE id_persona = %s AND estado = 'activo'"
            personal_exists = DataBaseHandle.getRecords(personal_check, (id_persona,), size=1)

            if personal_exists:
                return internal_response(False, None,
                    "No se puede desactivar la persona porque tiene un registro de personal activo asociado")

            # Verificar si la persona tiene un registro de paciente activo
            paciente_check = "SELECT id, estado FROM paciente WHERE id_persona = %s AND estado = 'activo'"
            paciente_exists = DataBaseHandle.getRecords(paciente_check, (id_persona,), size=1)

            if paciente_exists:
                return internal_response(False, None,
                    "No se puede desactivar la persona porque tiene un registro de paciente activo asociado")

            # Verificar si la persona es tutor activo
            tutor_check = "SELECT id, estado FROM tutor WHERE id_persona = %s AND estado = 'activo'"
            tutor_exists = DataBaseHandle.getRecords(tutor_check, (id_persona,), size=1)

            if tutor_exists:
                return internal_response(False, None,
                    "No se puede desactivar la persona porque tiene un registro de tutor activo asociado")

            # Desactivar persona
            update_query = """
                UPDATE persona 
                SET estado = 'inactivo', fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (id_persona,))

            if success:
                HandleLogs.write_log(f"PersonaComponent.deactivate_persona - Persona {id_persona} desactivada")
                return internal_response(True, {"id": id_persona, "estado": "inactivo"},
                                         "Persona desactivada exitosamente")
            else:
                HandleLogs.write_error(f"PersonaComponent.deactivate_persona - Error desactivando persona {id_persona}")
                return internal_response(False, None, "Error desactivando persona")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.deactivate_persona - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def reactivate_persona(id_persona):
        """Reactivar persona inactiva"""
        try:
            check_query = "SELECT id, estado FROM persona WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (id_persona,), size=1)

            if not existing:
                return internal_response(False, None, "Persona no encontrada")

            if existing['estado'] == 'activo':
                return internal_response(False, None, "La persona ya esta activa")

            update_query = """
                UPDATE persona
                SET estado = 'activo', fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (id_persona,))

            if success:
                HandleLogs.write_log(f"PersonaComponent.reactivate_persona - Persona {id_persona} reactivada")
                return internal_response(True, {"id": id_persona, "estado": "activo"},
                                         "Persona reactivada exitosamente")
            else:
                HandleLogs.write_error(f"PersonaComponent.reactivate_persona - Error reactivando persona {id_persona}")
                return internal_response(False, None, "Error reactivando persona")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.reactivate_persona - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def check_cedula_exists(cedula, exclude_id=None):
        """Verificar si una cedula ya existe"""
        try:
            if exclude_id:
                query = "SELECT id FROM persona WHERE cedula = %s AND id != %s"
                params = (cedula, exclude_id)
            else:
                query = "SELECT id FROM persona WHERE cedula = %s"
                params = (cedula,)

            result = DataBaseHandle.getRecordsWithStatus(query, params, size=1)
            if result['success']:
                exists = result['data'] is not None and bool(result['data'])
                return internal_response(True, exists, "Consulta ejecutada")
            else:
                HandleLogs.write_error(f"PersonaComponent.check_cedula_exists - Error BD: {result['error']}")
                return internal_response(False, None, f"Error en consulta: {result['error']}")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.check_cedula_exists - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def check_email_exists(email, exclude_id=None):
        """Verificar si un email ya existe"""
        try:
            if exclude_id:
                query = "SELECT id FROM persona WHERE correo = %s AND id != %s"
                params = (email, exclude_id)
            else:
                query = "SELECT id FROM persona WHERE correo = %s"
                params = (email,)

            result = DataBaseHandle.getRecordsWithStatus(query, params, size=1)
            if result['success']:
                exists = result['data'] is not None and bool(result['data'])
                return internal_response(True, exists, "Consulta ejecutada")
            else:
                HandleLogs.write_error(f"PersonaComponent.check_email_exists - Error BD: {result['error']}")
                return internal_response(False, None, f"Error en consulta: {result['error']}")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.check_email_exists - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_personas_disponibles_para_usuario():
        """Obtener personas que no tienen usuario asociado"""
        try:
            query = """
            SELECT 
                p.id,
                p.nombre,
                p.apellido,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.cedula,
                p.correo
            FROM persona p
            LEFT JOIN usuario u ON p.id = u.id_persona
            WHERE u.id IS NULL AND p.estado = 'activo'
            ORDER BY p.nombre, p.apellido
            """

            result = DataBaseHandle.getRecordsWithStatus(query)

            if result['success']:
                personas = result['data'] if result['data'] else []
                HandleLogs.write_log(f"PersonaComponent.get_personas_disponibles_para_usuario - {len(personas)} personas disponibles")
                return internal_response(True, personas, "Personas disponibles obtenidas")
            else:
                HandleLogs.write_error(f"PersonaComponent.get_personas_disponibles_para_usuario - Error: {result['error']}")
                return internal_response(False, None, f"Error ejecutando consulta: {result['error']}")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.get_personas_disponibles_para_usuario - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")