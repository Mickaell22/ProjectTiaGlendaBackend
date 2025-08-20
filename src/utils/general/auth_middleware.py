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

            # Verificar token con manejo robusto de errores
            token_result = None
            user_id = None
            
            try:
                token_result = SecurityUtils.verify_token(token)
                
                if not token_result:
                    return response_error("Token verification failed", 401)
                
                # Manejar caso donde token_result es una tupla
                if isinstance(token_result, tuple):
                    HandleLogs.write_error(f"auth_middleware - token_result is tuple: {token_result}")
                    return response_error("Token format error", 401)
                
                if not isinstance(token_result, dict):
                    HandleLogs.write_error(f"auth_middleware - token_result not dict: {type(token_result)}")
                    return response_error("Invalid token response format", 401)
                    
                if not token_result.get('success'):
                    return response_error(token_result.get('message', 'Token inválido'), 401)
                
                token_data = token_result.get('data')
                if not token_data:
                    return response_error("No token data", 401)
                    
                # Manejar caso donde token_data es una tupla
                if isinstance(token_data, tuple):
                    HandleLogs.write_error(f"auth_middleware - token_data is tuple: {token_data}")
                    return response_error("Token data format error", 401)
                
                if not isinstance(token_data, dict):
                    HandleLogs.write_error(f"auth_middleware - token_data not dict: {type(token_data)}")
                    return response_error("Invalid token data format", 401)
                    
                user_id = token_data.get('user_id')
                if not user_id:
                    return response_error("ID de usuario no encontrado en token", 401)
                    
            except Exception as token_err:
                HandleLogs.write_error(f"auth_middleware.token_required - Token verification error: {str(token_err)}")
                # También registrar el stack trace para debugging
                import traceback
                HandleLogs.write_error(f"auth_middleware.token_required - Token verification traceback: {traceback.format_exc()}")
                return response_error("Error verificando token", 401)
            
            # Verificar que el usuario sigue activo con manejo robusto de errores
            try:
                user_result = LoginComponent.get_user_by_id(user_id)
                
                if not user_result:
                    return response_error("User verification failed", 401)
                
                # Manejar caso donde user_result es una tupla
                if isinstance(user_result, tuple):
                    HandleLogs.write_error(f"auth_middleware - user_result is tuple: {user_result}")
                    return response_error("User result format error", 401)
                
                if not isinstance(user_result, dict):
                    HandleLogs.write_error(f"auth_middleware - user_result not dict: {type(user_result)}")
                    return response_error("Invalid user response format", 401)
                    
                if not user_result.get('success') or not user_result.get('data'):
                    return response_error("Usuario no encontrado o inactivo", 401)

                # Obtener datos del usuario - manejar todos los casos posibles
                user_data = user_result['data']
                user_info = None
                
                if isinstance(user_data, dict) and user_data:
                    # Caso normal: dict con datos
                    user_info = user_data
                elif isinstance(user_data, list) and len(user_data) > 0:
                    # Caso lista con elementos
                    if isinstance(user_data[0], dict):
                        user_info = user_data[0]
                    else:
                        HandleLogs.write_error(f"auth_middleware - user_data[0] not dict: {type(user_data[0])}")
                        return response_error("Invalid user data item format", 401)
                elif isinstance(user_data, tuple) and len(user_data) > 0:
                    # Caso tupla (psycopg2 raw result) - convertir a dict
                    HandleLogs.write_error(f"auth_middleware - user_data is tuple: {user_data}")
                    return response_error("User data is in tuple format - database error", 500)
                else:
                    HandleLogs.write_error(f"auth_middleware - unexpected user_data format: {type(user_data)}")
                    return response_error("Unexpected user data format", 401)
                
                if not user_info or not isinstance(user_info, dict):
                    HandleLogs.write_error(f"auth_middleware - final user_info invalid: {type(user_info)}")
                    return response_error("Final user data validation failed", 401)
                    
                # Verificar que todos los campos requeridos estén presentes
                required_fields = ['id', 'usuario', 'rol', 'rol_id', 'nombre_completo']
                for field in required_fields:
                    if field not in user_info:
                        HandleLogs.write_error(f"auth_middleware - missing field: {field}")
                        return response_error(f"Campo de usuario faltante: {field}", 401)
                
            except Exception as user_err:
                HandleLogs.write_error(f"auth_middleware.token_required - User verification error: {str(user_err)}")
                # También registrar el stack trace para debugging
                import traceback
                HandleLogs.write_error(f"auth_middleware.token_required - User verification traceback: {traceback.format_exc()}")
                return response_error("Error verificando usuario", 401)

            # Agregar información del usuario al request
            request.current_user = {
                'id': user_info['id'],
                'usuario': user_info['usuario'],
                'rol': user_info['rol'],
                'rol_id': user_info['rol_id'],
                'nombre_completo': user_info['nombre_completo'],
                'estado': user_info.get('estado', 'activo'),
                'id_centro': user_info.get('id_centro')
            }

            return f(*args, **kwargs)

        except Exception as e:
            HandleLogs.write_error(f"auth_middleware.token_required - Error: {str(e)}")
            # Añadir traceback detallado para debugging
            import traceback
            HandleLogs.write_error(f"auth_middleware.token_required - Full traceback: {traceback.format_exc()}")
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