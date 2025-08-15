from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class UsuarioComponent:

    @staticmethod
    def get_all_usuarios():
        """Obtener todos los usuarios con información completa"""
        try:
            query = """
            SELECT 
                u.id,
                u.usuario,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.nombre,
                p.apellido,
                p.cedula,
                p.telefono,
                p.correo,
                p.direccion,
                p.fecha_nacimiento,
                r.id as rol_id,
                r.nombre as rol,
                r.nombre as rol_nombre,
                u.persona_id,
                u.estado,
                u.fecha_creacion,
                u.fecha_modificacion,
                u.fecha_ultimo_acceso
            FROM usuario u
            INNER JOIN persona p ON u.persona_id = p.id
            INNER JOIN rol r ON u.rol_id = r.id
            ORDER BY u.id
            """

            usuarios = DataBaseHandle.getRecords(query)

            if usuarios is not None:
                HandleLogs.write_log(f"UsuarioComponent.get_all_usuarios - {len(usuarios)} usuarios encontrados")
                return internal_response(True, usuarios, "Usuarios obtenidos correctamente")
            else:
                HandleLogs.write_error("UsuarioComponent.get_all_usuarios - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioComponent.get_all_usuarios - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_usuario_by_id(usuario_id):
        """Obtener un usuario por ID"""
        try:
            query = """
            SELECT 
                u.id,
                u.usuario,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.nombre,
                p.apellido,
                p.cedula,
                p.telefono,
                p.correo,
                p.fecha_nacimiento,
                r.nombre as rol,
                r.id as rol_id,
                u.estado,
                u.fecha_creacion,
                u.fecha_modificacion
            FROM usuario u
            INNER JOIN persona p ON u.persona_id = p.id
            INNER JOIN rol r ON u.rol_id = r.id
            WHERE u.id = %s
            """

            usuario = DataBaseHandle.getRecords(query, (usuario_id,), size=1)

            if usuario is not None:
                HandleLogs.write_log(f"UsuarioComponent.get_usuario_by_id - Usuario {usuario_id} encontrado")
                return internal_response(True, usuario, "Usuario encontrado")
            else:
                HandleLogs.write_log(f"UsuarioComponent.get_usuario_by_id - Usuario {usuario_id} no encontrado")
                return internal_response(True, None, "Usuario no encontrado")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioComponent.get_usuario_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def create_usuario(data):
        """Crear un nuevo usuario"""
        try:
            # Verificar si el usuario ya existe
            username_check = UsuarioComponent.check_username_exists(data['usuario'])
            if username_check['success'] and username_check['data']:
                return internal_response(False, None, "El nombre de usuario ya existe")

            # Insertar nuevo usuario
            insert_query = """
                INSERT INTO usuario (usuario, contrasenia, persona_id, rol_id, estado, usuario_creacion)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """

            params = (
                data['usuario'],
                data['contrasenia'],
                data['persona_id'],
                data['rol_id'],
                data.get('estado', 'activo'),
                data.get('usuario_creacion', 1)
            )

            new_id = DataBaseHandle.ExecuteInsert(insert_query, params)

            if new_id:
                # Obtener el usuario creado con información completa
                new_user = UsuarioComponent.get_usuario_by_id(new_id)
                HandleLogs.write_log(f"UsuarioComponent.create_usuario - Usuario creado con ID: {new_id}")
                return internal_response(True, new_user['data'], "Usuario creado exitosamente")
            else:
                HandleLogs.write_error("UsuarioComponent.create_usuario - Error insertando usuario")
                return internal_response(False, None, "Error creando usuario")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioComponent.create_usuario - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def update_usuario(usuario_id, data):
        """Actualizar un usuario existente"""
        try:
            # Verificar si el usuario existe
            check_query = "SELECT id FROM usuario WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (usuario_id,), size=1)

            if not existing:
                return internal_response(False, None, "Usuario no encontrado")

            # Construir query de actualización dinámicamente
            update_fields = []
            params = []

            allowed_fields = ['usuario', 'contrasenia', 'persona_id', 'rol_id', 'estado', 'usuario_modificacion']

            for field in allowed_fields:
                if field in data and data[field] is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(data[field])

            if not update_fields:
                return internal_response(False, None, "No hay campos para actualizar")

            # Agregar fecha de modificación
            update_fields.append("fecha_modificacion = CURRENT_TIMESTAMP")

            # Agregar ID del usuario al final
            params.append(usuario_id)

            update_query = f"""
                UPDATE usuario 
                SET {', '.join(update_fields)}
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, params)

            if success:
                # Obtener datos actualizados
                updated_user = UsuarioComponent.get_usuario_by_id(usuario_id)
                HandleLogs.write_log(f"UsuarioComponent.update_usuario - Usuario {usuario_id} actualizado")
                return internal_response(True, updated_user['data'], "Usuario actualizado exitosamente")
            else:
                HandleLogs.write_error(f"UsuarioComponent.update_usuario - Error actualizando usuario {usuario_id}")
                return internal_response(False, None, "Error actualizando usuario")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioComponent.update_usuario - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def deactivate_usuario(usuario_id):
        """Desactivar usuario (eliminación lógica)"""
        try:
            # Verificar si el usuario existe
            check_query = "SELECT id, estado FROM usuario WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (usuario_id,), size=1)

            if not existing:
                return internal_response(False, None, "Usuario no encontrado")

            if existing['estado'] == 'inactivo':
                return internal_response(False, None, "Usuario ya esta inactivo")

            # Desactivar usuario
            update_query = """
                UPDATE usuario 
                SET estado = 'inactivo', fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (usuario_id,))

            if success:
                HandleLogs.write_log(f"UsuarioComponent.deactivate_usuario - Usuario {usuario_id} desactivado")
                return internal_response(True, {"id": usuario_id, "estado": "inactivo"},
                                         "Usuario desactivado exitosamente")
            else:
                HandleLogs.write_error(f"UsuarioComponent.deactivate_usuario - Error desactivando usuario {usuario_id}")
                return internal_response(False, None, "Error desactivando usuario")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioComponent.deactivate_usuario - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def check_username_exists(username, exclude_id=None):
        """Verificar si un nombre de usuario ya existe"""
        try:
            if exclude_id:
                query = "SELECT id FROM usuario WHERE usuario = %s AND id != %s"
                params = (username, exclude_id)
            else:
                query = "SELECT id FROM usuario WHERE usuario = %s"
                params = (username,)

            existing = DataBaseHandle.getRecords(query, params, size=1)

            return internal_response(True, existing is not None, "Consulta ejecutada")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioComponent.check_username_exists - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def change_password(usuario_id, nueva_contrasenia):
        """Cambiar la contraseña de un usuario"""
        try:
            from src.utils.general.security import SecurityUtils
            
            # Verificar que el usuario existe y está activo
            check_query = "SELECT id, estado FROM usuario WHERE id = %s"
            existing_user = DataBaseHandle.getRecords(check_query, (usuario_id,), size=1)
            
            if not existing_user:
                HandleLogs.write_error(f"UsuarioComponent.change_password - Usuario {usuario_id} no encontrado")
                return internal_response(False, None, "Usuario no encontrado")
            
            if existing_user['estado'] != 'activo':
                HandleLogs.write_error(f"UsuarioComponent.change_password - Usuario {usuario_id} no está activo")
                return internal_response(False, None, "Usuario no está activo")
            
            # Hash de la nueva contraseña
            hashed_password = SecurityUtils.hash_password(nueva_contrasenia)
            
            # Actualizar la contraseña
            update_query = """
                UPDATE usuario 
                SET contrasenia = %s, fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """
            
            success = DataBaseHandle.ExecuteNonQuery(update_query, (hashed_password, usuario_id))
            
            if success:
                HandleLogs.write_log(f"UsuarioComponent.change_password - Contraseña actualizada para usuario {usuario_id}")
                return internal_response(True, {"id": usuario_id}, "Contraseña actualizada exitosamente")
            else:
                HandleLogs.write_error(f"UsuarioComponent.change_password - Error actualizando contraseña para usuario {usuario_id}")
                return internal_response(False, None, "Error actualizando contraseña")
                
        except Exception as e:
            HandleLogs.write_error(f"UsuarioComponent.change_password - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")





















