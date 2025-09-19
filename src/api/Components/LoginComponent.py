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
                u.usuario,
                u.contrasenia,
                u.estado,
                u.id_centro,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.correo,
                r.nombre as rol,
                r.id as rol_id,
                c.nombre as centro_nombre,
                c.codigo as centro_codigo,
                c.turno_principal as centro_turno
            FROM usuario u
            INNER JOIN persona p ON u.id_persona = p.id
            INNER JOIN rol r ON u.id_rol = r.id
            LEFT JOIN centros c ON u.id_centro = c.id
            WHERE u.usuario = %s
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
            SET fecha_ultimo_acceso = CURRENT_TIMESTAMP
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
                u.id_centro,
                u.id_persona,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
                p.cedula,
                p.correo,
                p.telefono,
                p.direccion,
                p.fecha_nacimiento,
                r.nombre as rol,
                r.id as rol_id,
                c.nombre as centro_nombre,
                c.codigo as centro_codigo,
                c.turno_principal as centro_turno
            FROM usuario u
            INNER JOIN persona p ON u.id_persona = p.id
            INNER JOIN rol r ON u.id_rol = r.id
            LEFT JOIN centros c ON u.id_centro = c.id
            WHERE u.id = %s AND u.estado = 'activo'
            """

            user_result = DataBaseHandle.getRecords(query, (user_id,), size=1)
            
            # Validar y formatear el resultado para asegurar formato consistente
            if not user_result:
                HandleLogs.write_log(f"LoginComponent.get_user_by_id - Usuario {user_id} no encontrado")
                return internal_response(False, None, "Usuario no encontrado")
            
            # Asegurar que tenemos un formato de diccionario correcto
            user_data = None
            if isinstance(user_result, list) and len(user_result) > 0:
                first_result = user_result[0]
                if isinstance(first_result, dict):
                    user_data = first_result
                elif isinstance(first_result, tuple):
                    # Convertir tupla a diccionario usando los nombres de las columnas
                    user_data = {
                        'id': first_result[0],
                        'usuario': first_result[1],
                        'estado': first_result[2],
                        'id_centro': first_result[3],
                        'id_persona': first_result[4],
                        'nombre_completo': first_result[5],
                        'cedula': first_result[6],
                        'correo': first_result[7],
                        'telefono': first_result[8],
                        'direccion': first_result[9],
                        'fecha_nacimiento': first_result[10],
                        'rol': first_result[11],
                        'rol_id': first_result[12],
                        'centro_nombre': first_result[13] if len(first_result) > 13 else None,
                        'centro_codigo': first_result[14] if len(first_result) > 14 else None,
                        'centro_turno': first_result[15] if len(first_result) > 15 else None
                    }
                    HandleLogs.write_log(f"LoginComponent.get_user_by_id - Converted tuple to dict for user {user_id}")
            elif isinstance(user_result, dict):
                user_data = user_result
            elif isinstance(user_result, tuple):
                # Caso de tupla directa
                user_data = {
                    'id': user_result[0],
                    'usuario': user_result[1],
                    'estado': user_result[2],
                    'id_centro': user_result[3],
                    'id_persona': user_result[4],
                    'nombre_completo': user_result[5],
                    'cedula': user_result[6],
                    'correo': user_result[7],
                    'telefono': user_result[8],
                    'direccion': user_result[9],
                    'fecha_nacimiento': user_result[10],
                    'rol': user_result[11],
                    'rol_id': user_result[12],
                    'centro_nombre': user_result[13] if len(user_result) > 13 else None,
                    'centro_codigo': user_result[14] if len(user_result) > 14 else None,
                    'centro_turno': user_result[15] if len(user_result) > 15 else None
                }
                HandleLogs.write_log(f"LoginComponent.get_user_by_id - Converted direct tuple to dict for user {user_id}")
            
            if not user_data:
                HandleLogs.write_error(f"LoginComponent.get_user_by_id - Could not format user data for {user_id}: {type(user_result)}")
                return internal_response(False, None, "Error formateando datos de usuario")

            HandleLogs.write_log(f"LoginComponent.get_user_by_id - Consulta para usuario ID: {user_id}")
            return internal_response(True, user_data, "Usuario encontrado")

        except Exception as e:
            HandleLogs.write_error(f"LoginComponent.get_user_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")