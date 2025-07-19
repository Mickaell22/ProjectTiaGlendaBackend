from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class PersonaComponent:

    @staticmethod
    def get_all_personas():
        """Obtener todas las personas"""
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
                p.fecha_nacimiento,
                p.estado,
                p.fecha_creacion,
                p.fecha_modificacion,
                CASE 
                    WHEN u.id IS NOT NULL THEN 'Si'
                    ELSE 'No'
                END as tiene_usuario,
                r.nombre as rol_usuario
            FROM persona p
            LEFT JOIN usuario u ON p.id = u.persona_id
            LEFT JOIN rol r ON u.rol_id = r.id
            ORDER BY p.id
            """

            personas = DataBaseHandle.getRecords(query)

            if personas is not None:
                HandleLogs.write_log(f"PersonaComponent.get_all_personas - {len(personas)} personas encontradas")
                return internal_response(True, personas, "Personas obtenidas correctamente")
            else:
                HandleLogs.write_error("PersonaComponent.get_all_personas - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.get_all_personas - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_persona_by_id(persona_id):
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
                p.fecha_nacimiento,
                p.estado,
                p.fecha_creacion,
                p.fecha_modificacion,
                CASE 
                    WHEN u.id IS NOT NULL THEN 'Si'
                    ELSE 'No'
                END as tiene_usuario,
                u.id as usuario_id,
                u.usuario as nombre_usuario,
                r.nombre as rol_usuario
            FROM persona p
            LEFT JOIN usuario u ON p.id = u.persona_id
            LEFT JOIN rol r ON u.rol_id = r.id
            WHERE p.id = %s
            """

            persona = DataBaseHandle.getRecords(query, (persona_id,), size=1)

            if persona is not None:
                HandleLogs.write_log(f"PersonaComponent.get_persona_by_id - Persona {persona_id} encontrada")
                return internal_response(True, persona, "Persona encontrada")
            else:
                HandleLogs.write_log(f"PersonaComponent.get_persona_by_id - Persona {persona_id} no encontrada")
                return internal_response(True, None, "Persona no encontrada")

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
                return internal_response(True, new_persona['data'], "Persona creada exitosamente")
            else:
                HandleLogs.write_error("PersonaComponent.create_persona - Error insertando persona")
                return internal_response(False, None, "Error creando persona")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.create_persona - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def update_persona(persona_id, data):
        """Actualizar una persona existente"""
        try:
            # Verificar si la persona existe
            check_query = "SELECT id FROM persona WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (persona_id,), size=1)

            if not existing:
                return internal_response(False, None, "Persona no encontrada")

            # Verificar cedula duplicada (excluyendo la persona actual)
            if 'cedula' in data and data['cedula']:
                cedula_check = PersonaComponent.check_cedula_exists(data['cedula'], exclude_id=persona_id)
                if cedula_check['success'] and cedula_check['data']:
                    return internal_response(False, None, "La cedula ya existe")

            # Verificar email duplicado (excluyendo la persona actual)
            if 'correo' in data and data['correo']:
                email_check = PersonaComponent.check_email_exists(data['correo'], exclude_id=persona_id)
                if email_check['success'] and email_check['data']:
                    return internal_response(False, None, "El correo electronico ya existe")

            # Construir query de actualización dinámicamente
            update_fields = []
            params = []

            allowed_fields = [
                'nombre', 'apellido', 'cedula', 'telefono', 'correo',
                'direccion', 'fecha_nacimiento', 'estado', 'usuario_modificacion'
            ]

            for field in allowed_fields:
                if field in data and data[field] is not None:
                    # Limpiar strings
                    if field in ['nombre', 'apellido', 'cedula', 'telefono', 'correo', 'direccion']:
                        if data[field].strip():
                            update_fields.append(f"{field} = %s")
                            params.append(data[field].strip())
                    else:
                        update_fields.append(f"{field} = %s")
                        params.append(data[field])

            if not update_fields:
                return internal_response(False, None, "No hay campos para actualizar")

            # Agregar fecha de modificación
            update_fields.append("fecha_modificacion = CURRENT_TIMESTAMP")

            # Agregar ID de la persona al final
            params.append(persona_id)

            update_query = f"""
                UPDATE persona 
                SET {', '.join(update_fields)}
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, params)

            if success:
                # Obtener datos actualizados
                updated_persona = PersonaComponent.get_persona_by_id(persona_id)
                HandleLogs.write_log(f"PersonaComponent.update_persona - Persona {persona_id} actualizada")
                return internal_response(True, updated_persona['data'], "Persona actualizada exitosamente")
            else:
                HandleLogs.write_error(f"PersonaComponent.update_persona - Error actualizando persona {persona_id}")
                return internal_response(False, None, "Error actualizando persona")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.update_persona - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def deactivate_persona(persona_id):
        """Desactivar persona (eliminación lógica)"""
        try:
            # Verificar si la persona existe
            check_query = "SELECT id, estado FROM persona WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (persona_id,), size=1)

            if not existing:
                return internal_response(False, None, "Persona no encontrada")

            if existing['estado'] == 'inactivo':
                return internal_response(False, None, "Persona ya esta inactiva")

            # Verificar si la persona tiene un usuario asociado
            user_check = "SELECT id, estado FROM usuario WHERE persona_id = %s"
            user_exists = DataBaseHandle.getRecords(user_check, (persona_id,), size=1)

            if user_exists and user_exists['estado'] == 'activo':
                return internal_response(False, None,
                    "No se puede desactivar la persona porque tiene un usuario activo asociado")

            # Desactivar persona
            update_query = """
                UPDATE persona 
                SET estado = 'inactivo', fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (persona_id,))

            if success:
                HandleLogs.write_log(f"PersonaComponent.deactivate_persona - Persona {persona_id} desactivada")
                return internal_response(True, {"id": persona_id, "estado": "inactivo"},
                                         "Persona desactivada exitosamente")
            else:
                HandleLogs.write_error(f"PersonaComponent.deactivate_persona - Error desactivando persona {persona_id}")
                return internal_response(False, None, "Error desactivando persona")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.deactivate_persona - Error: {str(e)}")
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

            existing = DataBaseHandle.getRecords(query, params, size=1)
            return internal_response(True, existing is not None, "Consulta ejecutada")

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

            existing = DataBaseHandle.getRecords(query, params, size=1)
            return internal_response(True, existing is not None, "Consulta ejecutada")

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
            LEFT JOIN usuario u ON p.id = u.persona_id
            WHERE u.id IS NULL AND p.estado = 'activo'
            ORDER BY p.nombre, p.apellido
            """

            personas = DataBaseHandle.getRecords(query)

            if personas is not None:
                HandleLogs.write_log(f"PersonaComponent.get_personas_disponibles_para_usuario - {len(personas)} personas disponibles")
                return internal_response(True, personas, "Personas disponibles obtenidas")
            else:
                HandleLogs.write_error("PersonaComponent.get_personas_disponibles_para_usuario - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"PersonaComponent.get_personas_disponibles_para_usuario - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")