from flask import request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error
from src.utils.general.security import SecurityUtils
from src.utils.general.validators import Validators
from src.api.Components.LoginComponent import LoginComponent
from src.api.Service.CentroService import CentroService


class LoginService:

    @staticmethod
    def login():
        """Autenticar usuario y generar token"""
        try:
            data = request.get_json()
            HandleLogs.write_log("LoginService.login - Intento de autenticacion")

            # Validar datos requeridos
            required_validation = Validators.validate_required_fields(
                data, ['usuario', 'contrasenia']
            )
            if not required_validation['valid']:
                return response_error(required_validation['message'], 400)

            username = data['usuario'].strip()
            password = data['contrasenia']

            # Validar formato de usuario
            username_validation = Validators.validate_username(username)
            if not username_validation['valid']:
                return response_error(username_validation['message'], 400)

            # Buscar usuario en base de datos
            user_result = LoginComponent.get_user_for_login(username)

            if not user_result['success']:
                HandleLogs.write_error(f"LoginService.login - Error buscando usuario: {username}")
                return response_error("Error interno del servidor", 500)

            if not user_result['data']:
                HandleLogs.write_log(f"LoginService.login - Usuario no encontrado: {username}")
                return response_error("Credenciales invalidas", 401)

            user = user_result['data']

            # Verificar estado del usuario
            if user['estado'] != 'activo':
                HandleLogs.write_log(f"LoginService.login - Usuario inactivo: {username}")
                return response_error("Usuario inactivo o bloqueado", 401)

            # Verificar contraseña
            if not SecurityUtils.verify_password(password, user['contrasenia']):
                HandleLogs.write_log(f"LoginService.login - Contrasena incorrecta para: {username}")
                return response_error("Credenciales invalidas", 401)

            # Generar token JWT incluyendo información del centro
            token_data = {
                'id': user['id'],
                'usuario': user['usuario'],
                'rol': user['rol'],
                'nombre_completo': user['nombre_completo'],
                'id_centro': user['id_centro']
            }

            token = SecurityUtils.generate_token(token_data)

            if not token:
                HandleLogs.write_error("LoginService.login - Error generando token")
                return response_error("Error generando token de acceso", 500)

            # Actualizar ultimo acceso
            LoginComponent.update_last_access(user['id'])

            # Respuesta exitosa con información del centro
            response_data = {
                'token': token,
                'user': {
                    'id': user['id'],
                    'usuario': user['usuario'],
                    'nombre_completo': user['nombre_completo'],
                    'rol': user['rol'],
                    'correo': user['correo'],
                    'centro': {
                        'id': user['id_centro'],
                        'nombre': user['centro_nombre'],
                        'codigo': user['centro_codigo'],
                        'turno': user['centro_turno']
                    }
                }
            }

            HandleLogs.write_log(f"LoginService.login - Autenticacion exitosa: {username}")
            return response_success(response_data, "Autenticacion exitosa")

        except Exception as e:
            HandleLogs.write_error(f"LoginService.login - Error: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @staticmethod
    def verify_token():
        """Verificar token JWT"""
        try:
            # Obtener token del header Authorization
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                return response_error("Token de acceso requerido", 401)

            # Formato esperado: "Bearer <token>"
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return response_error("Formato de token invalido", 401)

            # Verificar token
            token_result = SecurityUtils.verify_token(token)

            if not token_result['success']:
                return response_error(token_result['message'], 401)

            # Token válido
            HandleLogs.write_log("LoginService.verify_token - Token verificado correctamente")
            return response_success(
                token_result['data'],
                "Token valido"
            )

        except Exception as e:
            HandleLogs.write_error(f"LoginService.verify_token - Error: {str(e)}")
            return response_error("Error verificando token", 500)

    @staticmethod
    def get_centros_disponibles():
        """Obtener lista de centros disponibles para el selector de login"""
        try:
            HandleLogs.write_log("LoginService.get_centros_disponibles - Solicitando centros para login")
            
            result = CentroService.get_centros_for_login()
            
            if result["success"]:
                return response_success(result["data"], result["message"])
            else:
                return response_error(result["message"], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"LoginService.get_centros_disponibles - Error: {str(e)}")
            return response_error("Error obteniendo centros disponibles", 500)