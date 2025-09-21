import os
import configparser
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def get_config():
    """Obtener configuración del sistema"""
    config = configparser.ConfigParser()

    # Intentar cargar archivo de configuración
    config_file = "src/utils/general/config.cfg"
    if os.path.exists(config_file):
        config.read(config_file)

    # Obtener ambiente actual
    ambiente = os.getenv('AMBIENTE', 'DEVELOPMENT')

    # Configuración por defecto
    default_config = {
        'db_host': 'localhost',
        'db_port': '5432',
        'db_name': 'tia_glenda_db',
        'db_user': 'tia_glenda_user',
        'db_pass': 'tia_glenda_password',
        'secret_jwt': 'tia-glenda-jwt-secret-key-very-secure-2024',
        'api_base_url': 'http://localhost:5000'
    }

    # Si existe la sección en el archivo, usar esos valores
    if config.has_section(ambiente):
        for key in default_config:
            if config.has_option(ambiente, key):
                default_config[key] = config.get(ambiente, key)

    # Railway provee DATABASE_URL, parsearlo si existe
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        try:
            import urllib.parse as urlparse
            parsed = urlparse.urlparse(database_url)
            default_config['db_host'] = parsed.hostname
            default_config['db_port'] = str(parsed.port) if parsed.port else '5432'
            default_config['db_name'] = parsed.path[1:]  # Remover el '/' inicial
            default_config['db_user'] = parsed.username
            default_config['db_pass'] = parsed.password
        except Exception as e:
            # No podemos usar HandleLogs aquí por dependencia circular
            pass

    # Las variables de entorno tienen prioridad
    env_mapping = {
        'db_host': 'DB_HOST',
        'db_port': 'DB_PORT',
        'db_name': 'DB_NAME',
        'db_user': 'DB_USER',
        'db_pass': 'DB_PASSWORD',
        'secret_jwt': 'JWT_SECRET',
        'api_base_url': 'API_BASE_URL'
    }

    for config_key, env_key in env_mapping.items():
        env_value = os.getenv(env_key)
        if env_value:
            default_config[config_key] = env_value

    return default_config