"""
Blueprint para rutas publicas (sin autenticacion).
"""
from flask import Blueprint
from datetime import datetime
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error

public_bp = Blueprint('public', __name__, url_prefix='/api')


@public_bp.route('/test', methods=['GET'])
def test_api():
    HandleLogs.write_log("Acceso a ruta de prueba")
    return response_success({
        "message": "API Sistema Tia Glenda funcionando",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })


@public_bp.route('/sesion-publica/<string:token>', methods=['GET'])
def ver_sesion_publica(token):
    """Ver informacion publica de una sesion usando token temporal"""
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.ver_sesion_publica(token)


@public_bp.route('/sesion-pedagogica-publica/<string:token>', methods=['GET'])
def ver_sesion_pedagogica_publica(token):
    """Ver informacion publica de una sesion pedagogica usando token temporal"""
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.ver_sesion_publica(token)


@public_bp.route('/test-db', methods=['GET'])
def test_database():
    """Endpoint para probar la conexion a la base de datos"""
    try:
        from src.utils.database.connection_db import DataBaseHandle

        conn = DataBaseHandle.get_connection()
        if not conn:
            return response_error("No se pudo establecer conexion con la base de datos", 500)

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            conn.close()

            query = "SELECT COUNT(*) as total_usuarios FROM usuario"
            result = DataBaseHandle.getRecords(query, size=1)

            if result:
                HandleLogs.write_log("test_database - Conexion a base de datos exitosa")
                return response_success({
                    "database": "centro_tia_glenda",
                    "postgresql_version": version[0] if version else "Unknown",
                    "total_usuarios": result['total_usuarios'],
                    "connection": "successful"
                }, "Conexion a base de datos exitosa")
            else:
                return response_error("Error en la consulta de usuarios", 500)

        except Exception as query_error:
            conn.close()
            HandleLogs.write_error(f"test_database - Error en consulta: {str(query_error)}")
            return response_error(f"Error en consulta: {str(query_error)}", 500)

    except Exception as e:
        HandleLogs.write_error(f"test_database - Error: {str(e)}")
        return response_error(f"Error de conexion: {str(e)}", 500)


@public_bp.route('/test-db-status', methods=['GET'])
def test_database_with_status():
    """Endpoint para demostrar getRecordsWithStatus vs getRecords"""
    try:
        from src.utils.database.connection_db import DataBaseHandle

        query_valid = "SELECT COUNT(*) as total_usuarios FROM usuario"
        old_result = DataBaseHandle.getRecords(query_valid, size=1)
        new_result = DataBaseHandle.getRecordsWithStatus(query_valid, size=1)

        query_empty = "SELECT * FROM usuario WHERE id = -999"
        old_empty = DataBaseHandle.getRecords(query_empty, size=1)
        new_empty = DataBaseHandle.getRecordsWithStatus(query_empty, size=1)

        query_invalid = "SELECT * FROM tabla_inexistente"
        old_error = DataBaseHandle.getRecords(query_invalid, size=1)
        new_error = DataBaseHandle.getRecordsWithStatus(query_invalid, size=1)

        HandleLogs.write_log("test_database_with_status - Comparacion de metodos completada")
        return response_success({
            "valid_query": {"old_method": old_result, "new_method": new_result},
            "empty_result": {"old_method": old_empty, "new_method": new_empty},
            "error_query": {"old_method": old_error, "new_method": new_error}
        }, "Comparacion de metodos getRecords completada")

    except Exception as e:
        HandleLogs.write_error(f"test_database_with_status - Error: {str(e)}")
        return response_error("Error en test de metodos de base de datos", 500)
