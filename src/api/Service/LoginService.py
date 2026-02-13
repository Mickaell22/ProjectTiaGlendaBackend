from flask import request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error
from src.utils.general.security import SecurityUtils
from src.utils.general.validators import Validators
from src.api.Components.LoginComponent import LoginComponent
from src.api.Components.UsuarioCentrosComponent import UsuarioCentrosComponent
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

            # Obtener centros disponibles del usuario
            centros_result = UsuarioCentrosComponent.get_centros_usuario(user['id'])

            if not centros_result['success']:
                HandleLogs.write_error(f"LoginService.login - Error obteniendo centros: {username}")
                return response_error("Error obteniendo centros disponibles", 500)

            centros_disponibles = centros_result['data']

            # Si el usuario no tiene centros, retornar error
            if not centros_disponibles or len(centros_disponibles) == 0:
                HandleLogs.write_error(f"LoginService.login - Usuario sin centros asignados: {username}")
                return response_error("Usuario sin centros asignados. Contacte al administrador", 403)

            # Formatear centros para la respuesta
            centros_formatted = []
            centro_predeterminado = None
            centros_ids = []

            for centro in centros_disponibles:
                centro_obj = {
                    'id': centro['id'],
                    'nombre': centro['nombre'],
                    'codigo': centro['codigo']
                }
                centros_formatted.append(centro_obj)
                centros_ids.append(centro['id'])

                # Identificar el centro predeterminado
                if centro.get('es_predeterminado'):
                    centro_predeterminado = centro_obj

            # Si no hay centro predeterminado, usar el primero
            if not centro_predeterminado and len(centros_formatted) > 0:
                centro_predeterminado = centros_formatted[0]

            # IMPORTANTE: El usuario NO ha seleccionado un centro aun
            # El token inicial NO incluye id_centro, solo centros_disponibles
            # El usuario debe seleccionar un centro usando el endpoint /api/seleccionar-centro

            # Generar token JWT SIN centro seleccionado
            token_data = {
                'id': user['id'],
                'usuario': user['usuario'],
                'rol': user['rol'],
                'nombre_completo': user['nombre_completo'],
                'centros_disponibles': centros_ids
            }

            token = SecurityUtils.generate_token(token_data)

            if not token:
                HandleLogs.write_error("LoginService.login - Error generando token")
                return response_error("Error generando token de acceso", 500)

            # Actualizar ultimo acceso
            LoginComponent.update_last_access(user['id'])

            # Respuesta exitosa con centros disponibles
            response_data = {
                'token': token,
                'user': {
                    'id': user['id'],
                    'usuario': user['usuario'],
                    'nombre_completo': user['nombre_completo'],
                    'rol': user['rol'],
                    'id_persona': user.get('id_persona'),
                    'correo': user['correo'],
                    'centros': centros_formatted,
                    'centro_predeterminado': centro_predeterminado,
                    'centro_actual': None  # No ha seleccionado centro aun
                }
            }

            HandleLogs.write_log(f"LoginService.login - Autenticacion exitosa: {username} ({len(centros_formatted)} centros disponibles)")
            return response_success(response_data, "Autenticacion exitosa")

        except Exception as e:
            HandleLogs.write_error(f"LoginService.login - Error: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @staticmethod
    def verify_token():
        """Verificar token JWT (el middleware @token_required ya valido el token)"""
        try:
            user = request.current_user

            response_data = {
                'id': user['id'],
                'usuario': user['usuario'],
                'nombre_completo': user['nombre_completo'],
                'rol': user['rol'],
                'rol_id': user['rol_id'],
                'id_centro': user.get('id_centro'),
                'centros_disponibles': user.get('centros_disponibles', []),
                'centro': user.get('centro')
            }

            HandleLogs.write_log(f"LoginService.verify_token - Token verificado para usuario: {user['usuario']}")
            return response_success(response_data, "Token valido")

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