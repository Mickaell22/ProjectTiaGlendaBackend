from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class UsuarioComponent:

    @staticmethod
    def get_all_usuarios():
        """Obtener todos los usuarios con informacion completa incluyendo centro"""
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
                p.fecha_nacimiento::TEXT as fecha_nacimiento,
                r.id as rol_id,
                r.nombre as rol,
                r.nombre as rol_nombre,
                u.id_persona,
                u.foto_perfil,
                u.estado,
                u.fecha_creacion::TEXT as fecha_creacion,
                u.fecha_modificacion::TEXT as fecha_modificacion,
                u.fecha_ultimo_acceso::TEXT as fecha_ultimo_acceso,
                c.id as centro_id,
                c.nombre as centro_nombre,
                c.codigo as centro_codigo,
                c.turno_principal as centro_turno,
                CASE
                    WHEN c.codigo = 'NORTE' THEN 'Centro Norte'
                    WHEN c.codigo = 'SUR' THEN 'Centro Sur'
                    ELSE c.nombre
                END as centro_display
            FROM usuario u
            INNER JOIN persona p ON u.id_persona = p.id
            INNER JOIN rol r ON u.id_rol = r.id
            INNER JOIN centros c ON u.id_centro = c.id
            ORDER BY c.codigo, u.id
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
        """Obtener un usuario por ID con informacion del centro"""
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
                p.fecha_nacimiento::TEXT as fecha_nacimiento,
                r.id as rol_id,
                r.nombre as rol,
                r.nombre as rol_nombre,
                u.id_persona,
                u.foto_perfil,
                u.estado,
                u.fecha_creacion::TEXT as fecha_creacion,
                u.fecha_modificacion::TEXT as fecha_modificacion,
                u.fecha_ultimo_acceso::TEXT as fecha_ultimo_acceso,
                c.id as centro_id,
                c.nombre as centro_nombre,
                c.codigo as centro_codigo,
                c.turno_principal as centro_turno,
                CASE
                    WHEN c.codigo = 'NORTE' THEN 'Centro Norte'
                    WHEN c.codigo = 'SUR' THEN 'Centro Sur'
                    ELSE c.nombre
                END as centro_display
            FROM usuario u
            INNER JOIN persona p ON u.id_persona = p.id
            INNER JOIN rol r ON u.id_rol = r.id
            INNER JOIN centros c ON u.id_centro = c.id
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
                INSERT INTO usuario (usuario, contrasenia, id_persona, id_rol, id_centro, estado, usuario_creacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

            params = (
                data['usuario'],
                data['contrasenia'],
                data['id_persona'],
                data['id_rol'],
                data.get('id_centro', 1),
                data.get('estado', 'activo'),
                data.get('usuario_creacion', 1)
            )

            success = DataBaseHandle.ExecuteNonQuery(insert_query, params)

            if success:
                # Obtener el ID del usuario recien creado
                id_query = "SELECT id FROM usuario WHERE usuario = %s ORDER BY id DESC LIMIT 1"
                new_user_data = DataBaseHandle.getRecords(id_query, (data['usuario'],), size=1)

                if new_user_data and new_user_data.get('id'):
                    new_id = new_user_data['id']
                    usuario_creacion = data.get('usuario_creacion', 1)

                    # Insertar registros en usuario_centros (sistema multi-centro)
                    centros_ids = data.get('centros_ids', [])
                    if centros_ids and len(centros_ids) > 0:
                        for idx, id_centro in enumerate(centros_ids):
                            es_predeterminado = (idx == 0)

                            insert_centro_query = """
                                INSERT INTO usuario_centros (id_usuario, id_centro, es_centro_predeterminado, usuario_creacion)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT (id_usuario, id_centro) DO NOTHING
                            """

                            centro_params = (new_id, id_centro, es_predeterminado, usuario_creacion)
                            DataBaseHandle.ExecuteNonQuery(insert_centro_query, centro_params)

                        HandleLogs.write_log(f"UsuarioComponent.create_usuario - {len(centros_ids)} centros asignados al usuario {new_id}")
                    else:
                        # Si no se proporcionaron centros, asignar el centro predeterminado
                        id_centro_default = data.get('id_centro', 1)
                        insert_centro_query = """
                            INSERT INTO usuario_centros (id_usuario, id_centro, es_centro_predeterminado, usuario_creacion)
                            VALUES (%s, %s, TRUE, %s)
                            ON CONFLICT (id_usuario, id_centro) DO NOTHING
                        """
                        DataBaseHandle.ExecuteNonQuery(insert_centro_query, (new_id, id_centro_default, usuario_creacion))
                        HandleLogs.write_log(f"UsuarioComponent.create_usuario - Centro predeterminado {id_centro_default} asignado al usuario {new_id}")

                    # Obtener el usuario creado con informacion completa
                    new_user = UsuarioComponent.get_usuario_by_id(new_id)
                    HandleLogs.write_log(f"UsuarioComponent.create_usuario - Usuario creado con ID: {new_id}")
                    return internal_response(True, new_user['data'], "Usuario creado exitosamente")
                else:
                    HandleLogs.write_error("UsuarioComponent.create_usuario - Error obteniendo ID del usuario creado")
                    return internal_response(False, None, "Error obteniendo usuario creado")
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

            if existing is None or not bool(existing):
                return internal_response(False, None, "Usuario no encontrado")

            # Si se cambia el username, verificar que no exista otro con ese nombre
            if 'usuario' in data and data['usuario'] is not None:
                username_check = UsuarioComponent.check_username_exists(data['usuario'], exclude_id=usuario_id)
                if username_check['success'] and username_check['data']:
                    return internal_response(False, None, "El nombre de usuario ya existe")

            # Construir query de actualizacion dinamicamente
            update_fields = []
            params = []

            allowed_fields = ['usuario', 'contrasenia', 'id_persona', 'id_rol', 'id_centro', 'estado', 'usuario_modificacion']

            for field in allowed_fields:
                if field in data and data[field] is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(data[field])

            if not update_fields:
                return internal_response(False, None, "No hay campos para actualizar")

            params.append(usuario_id)

            update_query = f"""
                UPDATE usuario
                SET {', '.join(update_fields)}
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, params)

            if success:
                # Actualizar centros del usuario si se proporciona centros_ids (sistema multi-centro)
                if 'centros_ids' in data and data['centros_ids'] is not None:
                    centros_ids = data['centros_ids']
                    usuario_modificacion = data.get('usuario_modificacion', 1)

                    # Eliminar todos los centros anteriores del usuario
                    delete_centros_query = "DELETE FROM usuario_centros WHERE id_usuario = %s"
                    DataBaseHandle.ExecuteNonQuery(delete_centros_query, (usuario_id,))

                    # Insertar los nuevos centros
                    if len(centros_ids) > 0:
                        for idx, id_centro in enumerate(centros_ids):
                            es_predeterminado = (idx == 0)

                            insert_centro_query = """
                                INSERT INTO usuario_centros (id_usuario, id_centro, es_centro_predeterminado, usuario_creacion)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT (id_usuario, id_centro) DO UPDATE
                                SET es_centro_predeterminado = EXCLUDED.es_centro_predeterminado,
                                    fecha_modificacion = CURRENT_TIMESTAMP,
                                    usuario_modificacion = %s
                            """

                            centro_params = (usuario_id, id_centro, es_predeterminado, usuario_modificacion, usuario_modificacion)
                            DataBaseHandle.ExecuteNonQuery(insert_centro_query, centro_params)

                        HandleLogs.write_log(f"UsuarioComponent.update_usuario - {len(centros_ids)} centros actualizados para usuario {usuario_id}")

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
        """Desactivar usuario (eliminacion logica)"""
        try:
            check_query = "SELECT id, estado FROM usuario WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (usuario_id,), size=1)

            if existing is None or not bool(existing):
                return internal_response(False, None, "Usuario no encontrado")

            if existing['estado'] == 'inactivo':
                return internal_response(False, None, "Usuario ya esta inactivo")

            update_query = """
                UPDATE usuario
                SET estado = 'inactivo'
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
    def reactivate_usuario(usuario_id):
        """Reactivar un usuario inactivo"""
        try:
            check_query = "SELECT id, estado FROM usuario WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (usuario_id,), size=1)

            if existing is None or not bool(existing):
                return internal_response(False, None, "Usuario no encontrado")

            if existing['estado'] == 'activo':
                return internal_response(False, None, "Usuario ya esta activo")

            update_query = """
                UPDATE usuario
                SET estado = 'activo'
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (usuario_id,))

            if success:
                HandleLogs.write_log(f"UsuarioComponent.reactivate_usuario - Usuario {usuario_id} reactivado")
                return internal_response(True, {"id": usuario_id, "estado": "activo"},
                                         "Usuario reactivado exitosamente")
            else:
                HandleLogs.write_error(f"UsuarioComponent.reactivate_usuario - Error reactivando usuario {usuario_id}")
                return internal_response(False, None, "Error reactivando usuario")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioComponent.reactivate_usuario - Error: {str(e)}")
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

            return internal_response(True, existing is not None and bool(existing), "Consulta ejecutada")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioComponent.check_username_exists - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def change_password(usuario_id, nueva_contrasenia):
        """Cambiar la contrasenia de un usuario"""
        try:
            from src.utils.general.security import SecurityUtils

            check_query = "SELECT id, estado FROM usuario WHERE id = %s"
            existing_user = DataBaseHandle.getRecords(check_query, (usuario_id,), size=1)

            if existing_user is None or not bool(existing_user):
                HandleLogs.write_error(f"UsuarioComponent.change_password - Usuario {usuario_id} no encontrado")
                return internal_response(False, None, "Usuario no encontrado")

            if existing_user['estado'] != 'activo':
                HandleLogs.write_error(f"UsuarioComponent.change_password - Usuario {usuario_id} no esta activo")
                return internal_response(False, None, "Usuario no esta activo")

            hashed_password = SecurityUtils.hash_password(nueva_contrasenia)

            update_query = """
                UPDATE usuario
                SET contrasenia = %s
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (hashed_password, usuario_id))

            if success:
                HandleLogs.write_log(f"UsuarioComponent.change_password - Contrasenia actualizada para usuario {usuario_id}")
                return internal_response(True, {"id": usuario_id}, "Contrasenia actualizada exitosamente")
            else:
                HandleLogs.write_error(f"UsuarioComponent.change_password - Error actualizando contrasenia para usuario {usuario_id}")
                return internal_response(False, None, "Error actualizando contrasenia")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioComponent.change_password - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")
