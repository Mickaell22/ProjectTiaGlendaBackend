from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from src.api.routes.api_routes import register_routes
from src.utils.general.logs import HandleLogs
from src.utils.general.config import get_config
import os
import datetime

class CustomJSONProvider(DefaultJSONProvider):
    """Custom JSON provider to handle date serialization"""
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, datetime.time):
            return str(obj)
        return super().default(obj)

app = Flask(__name__)
app.json = CustomJSONProvider(app)

# Configurar CORS para desarrollo y producción
cors_origins = [
    'http://localhost:3000', 
    'http://localhost:5173', 
    'http://localhost:5174', 
    'http://localhost:5175',
    'http://localhost:5176'
]

# Agregar orígenes de producción desde variables de entorno
cors_env = os.getenv('CORS_ORIGINS', '')
if cors_env:
    cors_origins.extend([origin.strip() for origin in cors_env.split(',') if origin.strip()])

# Auto-detectar dominio Railway si existe
railway_domain = os.getenv('RAILWAY_STATIC_URL')
if railway_domain:
    cors_origins.append(f"https://{railway_domain}")

# Si estamos en Railway, agregar dominios específicos
if os.getenv('RAILWAY_ENVIRONMENT'):
    cors_origins.extend([
        'https://projecttiaglendafrontend-k.up.railway.app',
        'https://tiaglenda.com',
        'https://www.tiaglenda.com',
        'http://tiaglenda.com',
        'http://www.tiaglenda.com'
    ])


CORS(app, 
     origins=cors_origins,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
     supports_credentials=True)

# Configurar Swagger UI
SWAGGER_URL = '/docs'  # URL para la documentación Swagger UI
API_URL = '/static/swagger.json'  # URL del archivo swagger.json

# Crear blueprint de Swagger UI
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API Centro Tía Glenda",
        'docExpansion': 'list',
        'validatorUrl': None,
        'tryItOutEnabled': True,
        'supportedSubmitMethods': ['get', 'post', 'put', 'delete', 'patch'],
        'defaultModelsExpandDepth': 3,
        'defaultModelExpandDepth': 3,
        'displayRequestDuration': True,
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True
    }
)

# Registrar blueprint de Swagger UI
app.register_blueprint(swaggerui_blueprint)

# Registrar todas las rutas del API
register_routes(app)

# Inicializar el scheduler de notificaciones al arrancar la aplicación
def inicializar_scheduler():
    """Inicializar el scheduler de notificaciones al arranque"""
    try:
        from src.utils.general.NotificationScheduler import iniciar_scheduler_global
        HandleLogs.write_log("Iniciando scheduler de notificaciones...")
        
        exito = iniciar_scheduler_global()
        if exito:
            HandleLogs.write_log("Scheduler de notificaciones iniciado exitosamente")
        else:
            HandleLogs.write_error("Error al iniciar scheduler de notificaciones")
            
    except Exception as e:
        HandleLogs.write_error(f"Error crítico iniciando scheduler: {str(e)}")

# Inicializar scheduler (solo en producción o cuando se especifique)
AUTO_START_SCHEDULER = os.getenv('AUTO_START_SCHEDULER', 'true').lower() == 'true'
if AUTO_START_SCHEDULER:
    inicializar_scheduler()


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        return jsonify({
            "status": "healthy",
            "message": "Sistema Tía Glenda Backend está funcionando",
            "service": "tia-glenda-api",
            "version": "1.0.0"
        }), 200
    except Exception as e:
        HandleLogs.write_error(f"health_check - Error: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "message": "Error en el servicio"
        }), 500


# Ruta de bienvenida que redirige a la documentación
@app.route('/')
def welcome():
    return jsonify({
        "message": "Bienvenido al API del Centro Tía Glenda",
        "documentation": "/docs/",
        "health": "/health",
        "version": "1.0.0",
        "swagger_json": "/static/swagger.json",
        "endpoints": {
            "auth": "/api/login, /api/logout, /api/verify-token, /api/me",
            "usuarios": "/api/usuarios",
            "personas": "/api/personas",
            "personal": "/api/personal",
            "especialidades": "/api/especialidades",
            "roles": "/api/roles"
        }
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint no encontrado",
        "code": 404,
        "documentation": "/docs/"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    HandleLogs.write_error(f"internal_error - Error 500: {str(error)}")
    return jsonify({
        "status": "error",
        "message": "Error interno del servidor",
        "code": 500
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    HandleLogs.write_log("app - Iniciando Sistema Tía Glenda Backend")
    print("=" * 70)
    print("SISTEMA TIA GLENDA - BACKEND")
    print("=" * 70)
    print(f"Servidor: http://localhost:{port}")
    print(f"Documentacion Swagger: http://localhost:{port}/docs/")
    print(f"Swagger JSON: http://localhost:{port}/static/swagger.json")
    print(f"Health Check: http://localhost:{port}/health")


    app.run(host='0.0.0.0', port=port, debug=debug)