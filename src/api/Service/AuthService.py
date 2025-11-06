from flask import request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error
from src.utils.general.security import SecurityUtils
from src.utils.general.validators import Validators
from src.api.Components.UsuarioCentrosComponent import UsuarioCentrosComponent
from src.api.Components.LoginComponent import LoginComponent


class AuthService:

    @staticmethod
    def seleccionar_centro():
        """Seleccionar centro despues del login"""
        try:
            # Obtener datos del usuario desde el token
            user = request.current_user
            user_id = user['id']

            # Obtener datos del request
            data = request.get_json()

            # Validar datos requeridos
            required_validation = Validators.validate_required_fields(data, ['id_centro'])
            if not required_validation['valid']:
                return response_error(required_validation['message'], 400)

            id_centro = data['id_centro']

            # Validar que el id_centro sea un numero
            if not isinstance(id_centro, int) or id_centro <= 0:
                return response_error("El id_centro debe ser un numero entero positivo", 400)

            # Validar que el usuario tenga acceso a ese centro
            validacion = UsuarioCentrosComponent.validar_acceso_centro(user_id, id_centro)

            if not validacion['success']:
                HandleLogs.write_error(f"AuthService.seleccionar_centro - Error validando acceso: Usuario {user_id}, Centro {id_centro}")
                return response_error("Error validando acceso al centro", 500)

            if not validacion['data']:
                HandleLogs.write_log(f"AuthService.seleccionar_centro - Usuario {user_id} NO tiene acceso al centro {id_centro}")
                return response_error("No tiene acceso al centro seleccionado", 403)

            # Obtener informacion del centro seleccionado
            centros_result = UsuarioCentrosComponent.get_centros_usuario(user_id)

            if not centros_result['success']:
                return response_error("Error obteniendo informacion del centro", 500)

            centro_seleccionado = None
            centros_ids = []

            for centro in centros_result['data']:
                centros_ids.append(centro['id'])
                if centro['id'] == id_centro:
                    centro_seleccionado = {
                        'id': centro['id'],
                        'nombre': centro['nombre'],
                        'codigo': centro['codigo']
                    }

            if not centro_seleccionado:
                return response_error("Centro no encontrado", 404)

            # Generar NUEVO token con el centro seleccionado
            token_data = {
                'id': user['id'],
                'usuario': user['usuario'],
                'rol': user['rol'],
                'nombre_completo': user['nombre_completo'],
                'id_centro': id_centro,
                'centros_disponibles': centros_ids
            }

            nuevo_token = SecurityUtils.generate_token(token_data)

            if not nuevo_token:
                HandleLogs.write_error("AuthService.seleccionar_centro - Error generando token")
                return response_error("Error generando token de acceso", 500)

            # Respuesta exitosa
            response_data = {
                'token': nuevo_token,
                'centro_seleccionado': centro_seleccionado,
                'user': {
                    'id': user['id'],
                    'usuario': user['usuario'],
                    'nombre_completo': user['nombre_completo'],
                    'rol': user['rol'],
                    'id_centro': id_centro
                }
            }

            HandleLogs.write_log(f"AuthService.seleccionar_centro - Usuario {user['usuario']} selecciono centro {centro_seleccionado['nombre']}")
            return response_success(response_data, "Centro seleccionado correctamente")

        except Exception as e:
            HandleLogs.write_error(f"AuthService.seleccionar_centro - Error: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @staticmethod
    def cambiar_centro():
        """Cambiar de centro sin hacer logout"""
        try:
            # Obtener datos del usuario desde el token
            user = request.current_user
            user_id = user['id']

            # Validar que el usuario tenga un centro actual
            if not user.get('id_centro'):
                HandleLogs.write_log(f"AuthService.cambiar_centro - Usuario {user_id} no tiene centro seleccionado")
                return response_error("Debe seleccionar un centro primero usando /api/seleccionar-centro", 400)

            # Obtener datos del request
            data = request.get_json()

            # Validar datos requeridos
            required_validation = Validators.validate_required_fields(data, ['id_centro'])
            if not required_validation['valid']:
                return response_error(required_validation['message'], 400)

            id_centro_nuevo = data['id_centro']

            # Validar que el id_centro sea un numero
            if not isinstance(id_centro_nuevo, int) or id_centro_nuevo <= 0:
                return response_error("El id_centro debe ser un numero entero positivo", 400)

            # Validar que no sea el mismo centro actual
            if id_centro_nuevo == user['id_centro']:
                return response_error("Ya esta trabajando en ese centro", 400)

            # Validar que el usuario tenga acceso al nuevo centro
            validacion = UsuarioCentrosComponent.validar_acceso_centro(user_id, id_centro_nuevo)

            if not validacion['success']:
                HandleLogs.write_error(f"AuthService.cambiar_centro - Error validando acceso: Usuario {user_id}, Centro {id_centro_nuevo}")
                return response_error("Error validando acceso al centro", 500)

            if not validacion['data']:
                HandleLogs.write_log(f"AuthService.cambiar_centro - Usuario {user_id} NO tiene acceso al centro {id_centro_nuevo}")
                return response_error("No tiene acceso al centro seleccionado", 403)

            # Obtener informacion del nuevo centro
            centros_result = UsuarioCentrosComponent.get_centros_usuario(user_id)

            if not centros_result['success']:
                return response_error("Error obteniendo informacion del centro", 500)

            centro_nuevo = None
            centros_ids = []

            for centro in centros_result['data']:
                centros_ids.append(centro['id'])
                if centro['id'] == id_centro_nuevo:
                    centro_nuevo = {
                        'id': centro['id'],
                        'nombre': centro['nombre'],
                        'codigo': centro['codigo']
                    }

            if not centro_nuevo:
                return response_error("Centro no encontrado", 404)

            # Generar NUEVO token con el centro actualizado
            token_data = {
                'id': user['id'],
                'usuario': user['usuario'],
                'rol': user['rol'],
                'nombre_completo': user['nombre_completo'],
                'id_centro': id_centro_nuevo,
                'centros_disponibles': centros_ids
            }

            nuevo_token = SecurityUtils.generate_token(token_data)

            if not nuevo_token:
                HandleLogs.write_error("AuthService.cambiar_centro - Error generando token")
                return response_error("Error generando token de acceso", 500)

            # Respuesta exitosa
            response_data = {
                'token': nuevo_token,
                'user': {
                    'id': user['id'],
                    'usuario': user['usuario'],
                    'nombre_completo': user['nombre_completo'],
                    'rol': user['rol'],
                    'id_centro': id_centro_nuevo,
                    'centro': centro_nuevo
                }
            }

            HandleLogs.write_log(f"AuthService.cambiar_centro - Usuario {user['usuario']} cambio al centro {centro_nuevo['nombre']}")
            return response_success(response_data, "Centro cambiado correctamente")

        except Exception as e:
            HandleLogs.write_error(f"AuthService.cambiar_centro - Error: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @staticmethod
    def get_centros_disponibles():
        """Obtener centros disponibles del usuario actual"""
        try:
            # Obtener datos del usuario desde el token
            user = request.current_user
            user_id = user['id']

            # Obtener centros del usuario
            centros_result = UsuarioCentrosComponent.get_centros_usuario(user_id)

            if not centros_result['success']:
                return response_error("Error obteniendo centros disponibles", 500)

            # Formatear respuesta
            centros_formatted = []
            for centro in centros_result['data']:
                centros_formatted.append({
                    'id': centro['id'],
                    'nombre': centro['nombre'],
                    'codigo': centro['codigo'],
                    'direccion': centro.get('direccion'),
                    'telefono': centro.get('telefono'),
                    'es_predeterminado': centro.get('es_predeterminado', False)
                })

            response_data = {
                'centros': centros_formatted,
                'centro_actual_id': user.get('id_centro'),
                'total': len(centros_formatted)
            }

            HandleLogs.write_log(f"AuthService.get_centros_disponibles - {len(centros_formatted)} centros para usuario {user['usuario']}")
            return response_success(response_data, "Centros obtenidos correctamente")

        except Exception as e:
            HandleLogs.write_error(f"AuthService.get_centros_disponibles - Error: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @staticmethod
    def get_me():
        """Obtener informacion del usuario actual (similar a /api/me)"""
        try:
            # Obtener datos del usuario desde el token
            user = request.current_user

            # Obtener informacion adicional del usuario
            user_result = LoginComponent.get_user_by_id(user['id'])

            if not user_result['success'] or not user_result['data']:
                return response_error("Error obteniendo informacion del usuario", 500)

            user_data = user_result['data']

            # Obtener centros disponibles
            centros_result = UsuarioCentrosComponent.get_centros_usuario(user['id'])
            centros_formatted = []

            if centros_result['success'] and centros_result['data']:
                for centro in centros_result['data']:
                    centros_formatted.append({
                        'id': centro['id'],
                        'nombre': centro['nombre'],
                        'codigo': centro['codigo'],
                        'es_predeterminado': centro.get('es_predeterminado', False)
                    })

            # Preparar respuesta
            response_data = {
                'id': user_data['id'],
                'usuario': user_data['usuario'],
                'nombre_completo': user_data['nombre_completo'],
                'rol': user_data['rol'],
                'correo': user_data.get('correo'),
                'telefono': user_data.get('telefono'),
                'id_centro_actual': user.get('id_centro'),
                'centros_disponibles': centros_formatted
            }

            HandleLogs.write_log(f"AuthService.get_me - Informacion obtenida para usuario {user['usuario']}")
            return response_success(response_data, "Informacion del usuario obtenida")

        except Exception as e:
            HandleLogs.write_error(f"AuthService.get_me - Error: {str(e)}")
            return response_error("Error interno del servidor", 500)
