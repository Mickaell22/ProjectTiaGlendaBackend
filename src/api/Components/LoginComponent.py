from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response
from datetime import datetime


class LoginComponent:

    @staticmethod
    def get_user_for_login(username):
        """Obtener datos de usuario para autenticación"""
        try:
            query = """
            SELECT 
                u.id,
                u.username as usuario,
                u.password_hash as contrasenia,
                u.estado,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.correo,
                r.nombre as rol,
                r.id as rol_id
            FROM usuario u
            INNER JOIN persona p ON u.persona_id = p.id
            INNER JOIN rol r ON u.rol_id = r.id
            WHERE u.username = %s
            """

            user = DataBaseHandle.getRecords(query, (username,), size=1)

            HandleLogs.write_log(f"LoginComponent.get_user_for_login - Busqueda para usuario: {username}")
            return internal_response(True, user, "Consulta ejecutada correctamente")

        except Exception as e:
            HandleLogs.write_error(f"LoginComponent.get_user_for_login - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def update_last_access(user_id):
        """Actualizar fecha de último acceso del usuario"""
        try:
            query = """
            UPDATE usuario 
            SET fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s
            """

            success = DataBaseHandle.ExecuteNonQuery(query, (user_id,))

            if success:
                HandleLogs.write_log(f"LoginComponent.update_last_access - Actualizado para usuario ID: {user_id}")
                return internal_response(True, None, "Ultimo acceso actualizado")
            else:
                HandleLogs.write_error(f"LoginComponent.update_last_access - Error actualizando usuario ID: {user_id}")
                return internal_response(False, None, "Error actualizando ultimo acceso")

        except Exception as e:
            HandleLogs.write_error(f"LoginComponent.update_last_access - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_user_by_id(user_id):
        """Obtener usuario por ID (para verificación de token)"""
        try:
            query = """
            SELECT 
                u.id,
                u.usuario,
                u.estado,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.correo,
                r.nombre as rol,
                r.id as rol_id
            FROM usuario u
            INNER JOIN persona p ON u.persona_id = p.id
            INNER JOIN rol r ON u.rol_id = r.id
            WHERE u.id = %s AND u.estado = 'activo'
            """

            user = DataBaseHandle.getRecords(query, (user_id,), size=1)

            HandleLogs.write_log(f"LoginComponent.get_user_by_id - Consulta para usuario ID: {user_id}")
            return internal_response(True, user, "Usuario encontrado")

        except Exception as e:
            HandleLogs.write_error(f"LoginComponent.get_user_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")