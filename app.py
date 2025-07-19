from flask import Flask, jsonify
from flask_cors import CORS
from src.api.routes.api_routes import register_routes
from src.utils.general.logs import HandleLogs
from src.utils.general.config import get_config
import os

app = Flask(__name__)

# Configurar CORS
CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'])

# Registrar todas las rutas
register_routes(app)


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


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint no encontrado",
        "code": 404
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
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    HandleLogs.write_log("app - Iniciando Sistema Tía Glenda Backend")
    app.run(host='0.0.0.0', port=port, debug=debug)