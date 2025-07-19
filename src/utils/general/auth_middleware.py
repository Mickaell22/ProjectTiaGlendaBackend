from functools import wraps
from flask import request
from src.utils.general.security import SecurityUtils
from src.utils.general.response import response_error
from src.utils.general.logs import HandleLogs
from src.api.Components.LoginComponent import LoginComponent


def token_required(f):
    """Decorador para requerir token JWT en endpoints"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Obtener token del header Authorization
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                return response_error("Token de acceso requerido", 401)

            # Formato esperado: "Bearer <token>"
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return response_error("Formato de token invalido. Use: Bearer <token>", 401)

            # Verificar token
            token_result = SecurityUtils.verify_token(token)

            if not token_result['success']:
                return response_error(token_result['message'], 401)

            # Verificar que el usuario sigue activo
            user_result = LoginComponent.get_user_by_id(token_result['data']['user_id'])

            if not user_result['success'] or not user_result['data']:
                return response_error("Usuario no encontrado o inactivo", 401)

            # Agregar información del usuario al request
            request.current_user = {
                'id': user_result['data']['id'],
                'usuario': user_result['data']['usuario'],
                'rol': user_result['data']['rol'],
                'rol_id': user_result['data']['rol_id'],
                'nombre_completo': user_result['data']['nombre_completo']
            }

            return f(*args, **kwargs)

        except Exception as e:
            HandleLogs.write_error(f"auth_middleware.token_required - Error: {str(e)}")
            return response_error("Error verificando autenticacion", 500)

    return decorated_function


def admin_required(f):
    """Decorador para requerir rol de administrador"""

    @wraps(f)
    @token_required
    def decorated_function(*args, **kwargs):
        try:
            user = request.current_user

            if user['rol'].lower() != 'administrador':
                HandleLogs.write_log(
                    f"auth_middleware.admin_required - Acceso denegado para usuario: {user['usuario']}")
                return response_error("Acceso denegado. Se requieren permisos de administrador", 403)

            return f(*args, **kwargs)

        except Exception as e:
            HandleLogs.write_error(f"auth_middleware.admin_required - Error: {str(e)}")
            return response_error("Error verificando permisos", 500)

    return decorated_function