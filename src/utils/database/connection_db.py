import psycopg2
import psycopg2.extras
from src.utils.general.logs import HandleLogs
from src.utils.general.config import get_config


class DataBaseHandle:
    """Manejo de base de datos PostgreSQL - Centro Tía Glenda"""

    @staticmethod
    def get_connection():
        """Obtener conexión a la base de datos PostgreSQL"""
        try:
            config = get_config()

            conn = psycopg2.connect(
                host=config.get('db_host', 'localhost'),
                port=config.get('db_port', '5432'),
                database=config.get('db_name', 'centro_tia_glenda'),
                user=config.get('db_user', 'postgres'),
                password=config.get('db_pass', 'password')
            )
            return conn
        except Exception as e:
            HandleLogs.write_error(f"get_connection - Error: {str(e)}")
            return None

    @staticmethod
    def getRecords(query, params=None, size=0):
        """
        Obtener registros de la base de datos
        size=0: todos los registros
        size=1: un solo registro
        size=N: N registros
        """
        try:
            conn = DataBaseHandle.get_connection()
            if not conn:
                return None

            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if size == 1:
                result = cursor.fetchone()
                result = dict(result) if result else None
            elif size > 1:
                result = cursor.fetchmany(size)
                result = [dict(row) for row in result]
            else:
                result = cursor.fetchall()
                result = [dict(row) for row in result]

            conn.close()
            return result

        except Exception as e:
            HandleLogs.write_error(f"getRecords - Error: {str(e)}")
            if 'conn' in locals():
                conn.close()
            return None

    @staticmethod
    def getRecordsWithStatus(query, params=None, size=0):
        """
        Obtener registros de la base de datos con estado detallado
        
        Diferencias con getRecords():
        - Distingue entre "sin resultados" y "error de consulta"
        - Proporciona mensaje de error específico
        - Indica si el error es de conexión
        
        Casos de uso:
        - Validaciones críticas donde se necesita distinguir error vs sin datos
        - Operaciones donde el error específico es importante para el usuario
        - Logging detallado de problemas de BD
        
        Retorna: {
            "success": bool,           # True si la consulta se ejecutó correctamente
            "data": list/dict/None,    # Datos resultado (None si no hay registros)
            "error": str/None,         # Mensaje de error específico (None si success=True)
            "connection_error": bool   # True si el error fue de conexión a BD
        }
        
        Ejemplos:
        - Consulta exitosa con datos: {"success": True, "data": [...], "error": None}
        - Consulta exitosa sin datos: {"success": True, "data": None, "error": None}
        - Error de sintaxis SQL: {"success": False, "data": None, "error": "syntax error...", "connection_error": False}
        - Error de conexión: {"success": False, "data": None, "error": "connection failed", "connection_error": True}
        """
        try:
            conn = DataBaseHandle.get_connection()
            if not conn:
                return {
                    "success": False,
                    "data": None,
                    "error": "No se pudo establecer conexión con la base de datos",
                    "connection_error": True
                }

            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if size == 1:
                result = cursor.fetchone()
                result = dict(result) if result else None
            elif size > 1:
                result = cursor.fetchmany(size)
                result = [dict(row) for row in result]
            else:
                result = cursor.fetchall()
                result = [dict(row) for row in result]

            conn.close()
            return {
                "success": True,
                "data": result,
                "error": None,
                "connection_error": False
            }

        except Exception as e:
            error_msg = f"getRecordsWithStatus - Error: {str(e)}"
            HandleLogs.write_error(error_msg)
            if 'conn' in locals():
                conn.close()
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "connection_error": False
            }

    @staticmethod
    def ExecuteNonQuery(query, params=None):
        """Ejecutar INSERT, UPDATE, DELETE"""
        try:
            conn = DataBaseHandle.get_connection()
            if not conn:
                return False

            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            HandleLogs.write_error(f"ExecuteNonQuery - Error: {str(e)}")
            if 'conn' in locals():
                conn.close()
            return False

    @staticmethod
    def ExecuteInsert(query, params=None):
        """Ejecutar INSERT y retornar el ID insertado"""
        try:
            conn = DataBaseHandle.get_connection()
            if not conn:
                return None

            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Para PostgreSQL, obtener el ID insertado
            inserted_id = cursor.fetchone()
            if inserted_id:
                inserted_id = inserted_id[0]

            conn.commit()
            conn.close()
            return inserted_id

        except Exception as e:
            HandleLogs.write_error(f"ExecuteInsert - Error: {str(e)}")
            if 'conn' in locals():
                conn.close()
            return None