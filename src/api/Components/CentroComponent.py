from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class CentroComponent:

    @staticmethod
    def get_all_centros():
        """Obtener todos los centros activos"""
        try:
            query = """
            SELECT 
                id,
                nombre,
                codigo,
                direccion,
                telefono,
                email,
                turno_principal,
                horario_apertura,
                horario_cierre,
                estado,
                observaciones
            FROM centros
            WHERE estado = 'activo'
            ORDER BY nombre ASC
            """

            centros = DataBaseHandle.getRecords(query)

            HandleLogs.write_log("CentroComponent.get_all_centros - Consulta ejecutada correctamente")
            return internal_response(True, centros, "Centros obtenidos correctamente")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.get_all_centros - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_centro_by_id(centro_id):
        """Obtener información de un centro específico"""
        try:
            query = """
            SELECT 
                id,
                nombre,
                codigo,
                direccion,
                telefono,
                email,
                turno_principal,
                horario_apertura,
                horario_cierre,
                estado,
                observaciones
            FROM centros
            WHERE id = %s AND estado = 'activo'
            """

            centro = DataBaseHandle.getRecords(query, (centro_id,), size=1)

            HandleLogs.write_log(f"CentroComponent.get_centro_by_id - Consulta para centro ID: {centro_id}")
            return internal_response(True, centro, "Centro encontrado")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.get_centro_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_centro_by_codigo(codigo):
        """Obtener centro por código (NORTE/SUR)"""
        try:
            query = """
            SELECT 
                id,
                nombre,
                codigo,
                direccion,
                telefono,
                email,
                turno_principal,
                horario_apertura,
                horario_cierre,
                estado,
                observaciones
            FROM centros
            WHERE codigo = %s AND estado = 'activo'
            """

            centro = DataBaseHandle.getRecords(query, (codigo,), size=1)

            HandleLogs.write_log(f"CentroComponent.get_centro_by_codigo - Consulta para código: {codigo}")
            return internal_response(True, centro, "Centro encontrado")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.get_centro_by_codigo - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def validate_user_centro_access(user_id, centro_id):
        """Validar que un usuario tenga acceso al centro especificado"""
        try:
            query = """
            SELECT 
                u.id,
                u.id_centro,
                c.nombre as centro_nombre,
                c.codigo as centro_codigo
            FROM usuario u
            INNER JOIN centros c ON u.id_centro = c.id
            WHERE u.id = %s AND u.id_centro = %s AND u.estado = 'activo' AND c.estado = 'activo'
            """

            access = DataBaseHandle.getRecords(query, (user_id, centro_id), size=1)

            HandleLogs.write_log(f"CentroComponent.validate_user_centro_access - Usuario {user_id}, Centro {centro_id}")
            return internal_response(True, access, "Validación completada")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.validate_user_centro_access - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_centro_statistics(centro_id):
        """Obtener estadísticas de un centro específico"""
        try:
            query = """
            SELECT 
                (SELECT COUNT(*) FROM usuario WHERE id_centro = %s AND estado = 'activo') as total_usuarios,
                (SELECT COUNT(*) FROM personal WHERE id_centro = %s AND estado = 'activo') as total_personal,
                (SELECT COUNT(*) FROM paciente WHERE id_centro = %s AND estado = 'activo') as total_pacientes,
                (SELECT COUNT(*) FROM sesion_terapia WHERE id_centro = %s AND estado = 'activo') as total_sesiones_terapia,
                (SELECT COUNT(*) FROM sesion_pedagogica WHERE id_centro = %s AND estado = 'activo') as total_sesiones_pedagogicas
            """

            stats = DataBaseHandle.getRecords(query, (centro_id, centro_id, centro_id, centro_id, centro_id), size=1)

            HandleLogs.write_log(f"CentroComponent.get_centro_statistics - Estadísticas para centro {centro_id}")
            return internal_response(True, stats, "Estadísticas obtenidas correctamente")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.get_centro_statistics - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")