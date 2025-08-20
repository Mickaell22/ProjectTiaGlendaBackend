from flask import request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error, response_inserted
from src.utils.general.validators import Validators
from src.utils.general.security import SecurityUtils
from src.api.Components.UsuarioComponent import UsuarioComponent


class UsuarioService:

    @staticmethod
    def get_usuarios():
        """Obtener lista de todos los usuarios"""
        try:
            HandleLogs.write_log("UsuarioService.get_usuarios - Iniciando")

            result = UsuarioComponent.get_all_usuarios()

            if result['success']:
                HandleLogs.write_log("UsuarioService.get_usuarios - Usuarios obtenidos exitosamente")
                return response_success(result['data'], "Lista de usuarios obtenida correctamente")
            else:
                HandleLogs.write_error(f"UsuarioService.get_usuarios - Error: {result['message']}")
                return response_error("Error obteniendo usuarios", 500)

        except Exception as e:
            HandleLogs.write_error(f"UsuarioService.get_usuarios - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_usuario(usuario_id):
        """Obtener un usuario por ID"""
        try:
            HandleLogs.write_log(f"UsuarioService.get_usuario - ID: {usuario_id}")

            if not usuario_id or usuario_id <= 0:
                return response_error("ID de usuario invalido", 400)

            result = UsuarioComponent.get_usuario_by_id(usuario_id)

            if result['success']:
                if result['data']:
                    HandleLogs.write_log(f"UsuarioService.get_usuario - Usuario {usuario_id} encontrado")
                    return response_success(result['data'], "Usuario encontrado")
                else:
                    return response_error("Usuario no encontrado", 404)
            else:
                HandleLogs.write_error(f"UsuarioService.get_usuario - Error: {result['message']}")
                return response_error("Error buscando usuario", 500)

        except Exception as e:
            HandleLogs.write_error(f"UsuarioService.get_usuario - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def create_usuario():
        """Crear un nuevo usuario"""
        try:
            data = request.get_json()
            HandleLogs.write_log("UsuarioService.create_usuario - Iniciando")

            # Validar datos de usuario
            validation_result = Validators.validate_usuario_data(data, is_update=False)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Hashear contraseña
            hashed_password = SecurityUtils.hash_password(data['contrasenia'])
            if not hashed_password:
                return response_error("Error procesando contrasena", 500)

            # Preparar datos para inserción
            user_data = {
                'usuario': data['usuario'].strip(),
                'contrasenia': hashed_password,
                'persona_id': int(data['persona_id']),
                'rol_id': int(data['rol_id']),
                'estado': data.get('estado', 'activo'),
                'usuario_creacion': getattr(request, 'current_user', {}).get('id', 1)
            }

            result = UsuarioComponent.create_usuario(user_data)

            if result['success']:
                HandleLogs.write_log("UsuarioService.create_usuario - Usuario creado exitosamente")
                return response_inserted(result['data'], "Usuario creado exitosamente")
            else:
                HandleLogs.write_error(f"UsuarioService.create_usuario - Error: {result['message']}")
                return response_error(f"Error creando usuario: {result['message']}", 400)

        except Exception as e:
            HandleLogs.write_error(f"UsuarioService.create_usuario - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def update_usuario(usuario_id):
        """Actualizar un usuario existente"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"UsuarioService.update_usuario - ID: {usuario_id}")

            if not usuario_id or usuario_id <= 0:
                return response_error("ID de usuario invalido", 400)

            # Validar datos (para actualización)
            validation_result = Validators.validate_usuario_data(data, is_update=True)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Si se actualiza la contraseña, hashearla
            if 'contrasenia' in data and data['contrasenia']:
                hashed_password = SecurityUtils.hash_password(data['contrasenia'])
                if not hashed_password:
                    return response_error("Error procesando contrasena", 500)
                data['contrasenia'] = hashed_password

            # Agregar usuario que modifica
            data['usuario_modificacion'] = getattr(request, 'current_user', {}).get('id', 1)

            result = UsuarioComponent.update_usuario(usuario_id, data)

            if result['success']:
                HandleLogs.write_log(f"UsuarioService.update_usuario - Usuario {usuario_id} actualizado")
                return response_success(result['data'], "Usuario actualizado exitosamente")
            else:
                HandleLogs.write_error(f"UsuarioService.update_usuario - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"UsuarioService.update_usuario - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def delete_usuario(usuario_id):
        """Desactivar usuario (eliminación lógica)"""
        try:
            HandleLogs.write_log(f"UsuarioService.delete_usuario - ID: {usuario_id}")

            if not usuario_id or usuario_id <= 0:
                return response_error("ID de usuario invalido", 400)

            # No permitir eliminar usuario admin principal
            if usuario_id == 1:
                return response_error("No se puede eliminar el usuario administrador principal", 400)

            result = UsuarioComponent.deactivate_usuario(usuario_id)

            if result['success']:
                HandleLogs.write_log(f"UsuarioService.delete_usuario - Usuario {usuario_id} desactivado")
                return response_success(None, "Usuario desactivado exitosamente")
            else:
                HandleLogs.write_error(f"UsuarioService.delete_usuario - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"UsuarioService.delete_usuario - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def change_password(usuario_id, password_data):
        """Cambiar contraseña de usuario"""
        try:
            HandleLogs.write_log(f"UsuarioService.change_password - ID: {usuario_id}")
            
            if not usuario_id or usuario_id <= 0:
                return response_error("ID de usuario invalido", 400)
            
            # Validar datos de entrada
            if not password_data:
                return response_error("Datos de contraseña requeridos", 400)
            
            nueva_contrasenia = password_data.get('nueva_contrasenia')
            confirmar_contrasenia = password_data.get('confirmar_contrasenia')
            
            if not nueva_contrasenia:
                return response_error("Nueva contraseña requerida", 400)
            
            if not confirmar_contrasenia:
                return response_error("Confirmación de contraseña requerida", 400)
            
            if nueva_contrasenia != confirmar_contrasenia:
                return response_error("Las contraseñas no coinciden", 400)
            
            # Validar fortaleza de contraseña
            from src.utils.general.validators import Validators
            password_validation = Validators.validate_password(nueva_contrasenia)
            if not password_validation['valid']:
                return response_error(password_validation['message'], 400)
            
            # Cambiar contraseña
            result = UsuarioComponent.change_password(usuario_id, nueva_contrasenia)
            
            if result['success']:
                HandleLogs.write_log(f"UsuarioService.change_password - Contraseña cambiada para usuario {usuario_id}")
                return response_success(None, "Contraseña actualizada exitosamente")
            else:
                HandleLogs.write_error(f"UsuarioService.change_password - Error: {result['message']}")
                return response_error(result['message'], 400)
                
        except Exception as e:
            HandleLogs.write_error(f"UsuarioService.change_password - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)