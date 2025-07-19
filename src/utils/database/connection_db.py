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
            return None

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