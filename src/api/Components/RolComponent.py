from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs


class RolComponent:
    """
    Componente de acceso a datos para la tabla 'rol'.
    Maneja todas las operaciones CRUD de la base de datos.
    """

    @staticmethod
    def get_all_roles(include_inactive=False):
        """
        Obtiene todos los roles.

        Args:
            include_inactive: Si es True, incluye roles inactivos

        Returns:
            dict: Resultado con status, data/error, y success
        """
        try:
            if include_inactive:
                query = """
                SELECT
                    id,
                    nombre,
                    descripcion,
                    estado,
                    fecha_creacion,
                    fecha_modificacion,
                    usuario_creacion,
                    usuario_modificacion
                FROM rol
                ORDER BY id
                """
            else:
                query = """
                SELECT
                    id,
                    nombre,
                    descripcion,
                    estado,
                    fecha_creacion,
                    fecha_modificacion,
                    usuario_creacion,
                    usuario_modificacion
                FROM rol
                WHERE estado = 'activo'
                ORDER BY id
                """

            result = DataBaseHandle.getRecordsWithStatus(query)

            if result.get('success'):
                roles = result.get('data', [])
                # Convertir campos TIMESTAMP a string para JSON
                for rol in roles:
                    if rol.get('fecha_creacion'):
                        rol['fecha_creacion'] = str(rol['fecha_creacion'])
                    if rol.get('fecha_modificacion'):
                        rol['fecha_modificacion'] = str(rol['fecha_modificacion'])
                return {'success': True, 'data': roles}
            else:
                return {'success': False, 'error': result.get('error', 'Error en consulta')}

        except Exception as e:
            HandleLogs.write_error(f"RolComponent.get_all_roles - Error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_rol_by_id(rol_id):
        """
        Obtiene un rol por su ID.

        Args:
            rol_id: ID del rol

        Returns:
            dict: Resultado con status, data/error, y success
        """
        try:
            query = """
            SELECT
                id,
                nombre,
                descripcion,
                estado,
                fecha_creacion,
                fecha_modificacion,
                usuario_creacion,
                usuario_modificacion
            FROM rol
            WHERE id = %s
            """

            result = DataBaseHandle.getRecordsWithStatus(query, (rol_id,))

            if result.get('success'):
                data = result.get('data')
                if data and len(data) > 0:
                    rol = data[0]
                    # Convertir campos TIMESTAMP a string para JSON
                    if rol.get('fecha_creacion'):
                        rol['fecha_creacion'] = str(rol['fecha_creacion'])
                    if rol.get('fecha_modificacion'):
                        rol['fecha_modificacion'] = str(rol['fecha_modificacion'])
                    return {'success': True, 'data': rol}
                else:
                    return {'success': True, 'data': None}
            else:
                return {'success': False, 'error': result.get('error', 'Error en consulta')}

        except Exception as e:
            HandleLogs.write_error(f"RolComponent.get_rol_by_id - Error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def check_rol_exists(rol_id):
        """
        Verifica si un rol existe (activo o inactivo).

        Args:
            rol_id: ID del rol a verificar

        Returns:
            bool: True si existe, False si no existe o hay error
        """
        try:
            query = "SELECT id FROM rol WHERE id = %s"
            result = DataBaseHandle.getRecordsWithStatus(query, (rol_id,))

            if result.get('success'):
                data = result.get('data')
                return data is not None and len(data) > 0
            return False

        except Exception as e:
            HandleLogs.write_error(f"RolComponent.check_rol_exists - Error: {str(e)}")
            return False

    @staticmethod
    def check_nombre_exists(nombre, exclude_id=None):
        """
        Verifica si ya existe un rol con el mismo nombre.

        Args:
            nombre: Nombre a verificar
            exclude_id: ID a excluir de la busqueda (para updates)

        Returns:
            bool: True si existe duplicado, False si no
        """
        try:
            if exclude_id:
                query = """
                SELECT id FROM rol
                WHERE LOWER(nombre) = LOWER(%s) AND id != %s
                """
                params = (nombre, exclude_id)
            else:
                query = """
                SELECT id FROM rol
                WHERE LOWER(nombre) = LOWER(%s)
                """
                params = (nombre,)

            result = DataBaseHandle.getRecordsWithStatus(query, params)

            if result.get('success'):
                data = result.get('data')
                return data is not None and len(data) > 0
            return False

        except Exception as e:
            HandleLogs.write_error(f"RolComponent.check_nombre_exists - Error: {str(e)}")
            return False

    @staticmethod
    def create_rol(nombre, descripcion=None, usuario_creacion=None):
        """
        Crea un nuevo rol.

        Args:
            nombre: Nombre del rol (requerido)
            descripcion: Descripcion del rol (opcional)
            usuario_creacion: ID del usuario que crea (opcional)

        Returns:
            dict: Resultado con success y data (nuevo rol) o error
        """
        try:
            query = """
            INSERT INTO rol (nombre, descripcion, estado, usuario_creacion, usuario_modificacion)
            VALUES (%s, %s, 'activo', %s, %s)
            """
            params = (nombre, descripcion, usuario_creacion, usuario_creacion)

            insert_result = DataBaseHandle.ExecuteNonQuery(query, params)

            if insert_result:
                # Obtener el rol recien creado
                select_query = """
                SELECT
                    id,
                    nombre,
                    descripcion,
                    estado,
                    fecha_creacion,
                    fecha_modificacion,
                    usuario_creacion,
                    usuario_modificacion
                FROM rol
                WHERE nombre = %s
                ORDER BY id DESC
                LIMIT 1
                """
                result = DataBaseHandle.getRecordsWithStatus(select_query, (nombre,))

                if result.get('success') and result.get('data'):
                    nuevo_rol = result['data'][0]
                    # Convertir TIMESTAMP a string
                    if nuevo_rol.get('fecha_creacion'):
                        nuevo_rol['fecha_creacion'] = str(nuevo_rol['fecha_creacion'])
                    if nuevo_rol.get('fecha_modificacion'):
                        nuevo_rol['fecha_modificacion'] = str(nuevo_rol['fecha_modificacion'])
                    return {'success': True, 'data': nuevo_rol}
                else:
                    return {'success': True, 'data': {'nombre': nombre}}
            else:
                return {'success': False, 'error': 'Error al insertar rol'}

        except Exception as e:
            HandleLogs.write_error(f"RolComponent.create_rol - Error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def update_rol(rol_id, nombre=None, descripcion=None, usuario_modificacion=None):
        """
        Actualiza un rol existente.

        Args:
            rol_id: ID del rol a actualizar
            nombre: Nuevo nombre (opcional)
            descripcion: Nueva descripcion (opcional)
            usuario_modificacion: ID del usuario que modifica

        Returns:
            dict: Resultado con success y data (rol actualizado) o error
        """
        try:
            # Construir query dinamico solo con campos proporcionados
            updates = []
            params = []

            if nombre is not None:
                updates.append("nombre = %s")
                params.append(nombre)

            if descripcion is not None:
                updates.append("descripcion = %s")
                params.append(descripcion)

            if usuario_modificacion is not None:
                updates.append("usuario_modificacion = %s")
                params.append(usuario_modificacion)

            if not updates:
                return {'success': False, 'error': 'No hay campos para actualizar'}

            # Agregar fecha_modificacion
            updates.append("fecha_modificacion = CURRENT_TIMESTAMP")

            query = f"""
            UPDATE rol
            SET {', '.join(updates)}
            WHERE id = %s
            """
            params.append(rol_id)

            update_result = DataBaseHandle.ExecuteNonQuery(query, tuple(params))

            if update_result:
                # Obtener el rol actualizado
                return RolComponent.get_rol_by_id(rol_id)
            else:
                return {'success': False, 'error': 'Error al actualizar rol'}

        except Exception as e:
            HandleLogs.write_error(f"RolComponent.update_rol - Error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def deactivate_rol(rol_id, usuario_modificacion=None):
        """
        Desactiva un rol (soft delete).

        Args:
            rol_id: ID del rol a desactivar
            usuario_modificacion: ID del usuario que realiza la accion

        Returns:
            dict: Resultado con success y mensaje o error
        """
        try:
            query = """
            UPDATE rol
            SET estado = 'inactivo',
                fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id = %s
            """
            params = (usuario_modificacion, rol_id)

            result = DataBaseHandle.ExecuteNonQuery(query, params)

            if result:
                return {'success': True, 'message': 'Rol desactivado correctamente'}
            else:
                return {'success': False, 'error': 'Error al desactivar rol'}

        except Exception as e:
            HandleLogs.write_error(f"RolComponent.deactivate_rol - Error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def reactivate_rol(rol_id, usuario_modificacion=None):
        """
        Reactiva un rol inactivo.

        Args:
            rol_id: ID del rol a reactivar
            usuario_modificacion: ID del usuario que realiza la accion

        Returns:
            dict: Resultado con success y mensaje o error
        """
        try:
            query = """
            UPDATE rol
            SET estado = 'activo',
                fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id = %s
            """
            params = (usuario_modificacion, rol_id)

            result = DataBaseHandle.ExecuteNonQuery(query, params)

            if result:
                return {'success': True, 'message': 'Rol reactivado correctamente'}
            else:
                return {'success': False, 'error': 'Error al reactivar rol'}

        except Exception as e:
            HandleLogs.write_error(f"RolComponent.reactivate_rol - Error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_rol_status(rol_id):
        """
        Obtiene el estado actual de un rol.

        Args:
            rol_id: ID del rol

        Returns:
            str o None: 'activo', 'inactivo', o None si no existe
        """
        try:
            query = "SELECT estado FROM rol WHERE id = %s"
            result = DataBaseHandle.getRecordsWithStatus(query, (rol_id,))

            if result.get('success') and result.get('data') and len(result['data']) > 0:
                return result['data'][0].get('estado')
            return None

        except Exception as e:
            HandleLogs.write_error(f"RolComponent.get_rol_status - Error: {str(e)}")
            return None

    @staticmethod
    def check_rol_in_use(rol_id):
        """
        Verifica si un rol esta siendo usado por algun usuario.

        Args:
            rol_id: ID del rol a verificar

        Returns:
            bool: True si esta en uso, False si no
        """
        try:
            query = """
            SELECT COUNT(*) as count
            FROM usuario
            WHERE rol_id = %s AND estado = 'activo'
            """
            result = DataBaseHandle.getRecordsWithStatus(query, (rol_id,))

            if result.get('success') and result.get('data'):
                count = result['data'][0].get('count', 0)
                return count > 0
            return False

        except Exception as e:
            HandleLogs.write_error(f"RolComponent.check_rol_in_use - Error: {str(e)}")
            return False
