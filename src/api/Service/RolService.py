from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error
from src.utils.database.connection_db import DataBaseHandle


class RolService:

    @staticmethod
    def get_roles():
        """Obtener lista de todos los roles activos"""
        try:
            HandleLogs.write_log("RolService.get_roles - Iniciando")

            query = """
            SELECT 
                id,
                nombre,
                descripcion,
                estado,
                fecha_creacion
            FROM rol 
            WHERE estado = 'activo'
            ORDER BY id
            """

            roles = DataBaseHandle.getRecords(query)

            if roles is not None:
                HandleLogs.write_log(f"RolService.get_roles - {len(roles)} roles encontrados")
                return response_success(roles, "Lista de roles obtenida correctamente")
            else:
                HandleLogs.write_error("RolService.get_roles - Error en consulta")
                return response_error("Error obteniendo roles", 500)

        except Exception as e:
            HandleLogs.write_error(f"RolService.get_roles - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)