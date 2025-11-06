from flask import request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error, response_inserted
from src.utils.general.validators import Validators
from src.utils.general.security import SecurityUtils
from src.api.Components.UsuarioComponent import UsuarioComponent
from src.api.Components.UsuarioCentrosComponent import UsuarioCentrosComponent


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
            try:
                # Obtener centros_ids del payload (nuevo campo para multi-centro)
                centros_ids = data.get('centros_ids', [])

                # Si no se proporciona centros_ids, usar id_centro (compatibilidad)
                if not centros_ids and data.get('id_centro'):
                    centros_ids = [int(data['id_centro'])]

                # Si no hay centros, usar centro por defecto (Norte = 1)
                if not centros_ids:
                    centros_ids = [1]

                # Validar que centros_ids sea una lista
                if not isinstance(centros_ids, list):
                    return response_error("centros_ids debe ser una lista de IDs de centros", 400)

                # Validar que todos los IDs sean numeros enteros positivos
                try:
                    centros_ids = [int(c) for c in centros_ids]
                    if any(c <= 0 for c in centros_ids):
                        return response_error("Los IDs de centros deben ser numeros positivos", 400)
                except (ValueError, TypeError):
                    return response_error("Los IDs de centros deben ser numeros enteros", 400)

                # Usar el primer centro como id_centro predeterminado en tabla usuario (compatibilidad)
                id_centro_predeterminado = centros_ids[0]

                user_data = {
                    'usuario': data['usuario'].strip(),
                    'contrasenia': hashed_password,
                    'id_persona': int(data['id_persona']),
                    'id_rol': int(data['id_rol']),
                    'id_centro': id_centro_predeterminado,
                    'estado': data.get('estado', 'activo'),
                    'usuario_creacion': getattr(request, 'current_user', {}).get('id', 1),
                    'centros_ids': centros_ids  # Pasar centros_ids al component
                }
            except KeyError as e:
                missing_field = str(e).replace("'", "")
                if missing_field in ['id_persona', 'id_rol']:
                    return response_error(f"Campos requeridos faltantes: {missing_field}", 400)
                return response_error(f"Campo requerido faltante: {missing_field}", 400)
            except ValueError as e:
                return response_error(f"Valor invalido en campo numerico: {str(e)}", 400)

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

            # Preparar datos para actualización
            update_data = {}

            # Solo agregar campos que están presentes en el request
            if 'usuario' in data and data['usuario']:
                update_data['usuario'] = data['usuario'].strip()
            if 'contrasenia' in data and data['contrasenia']:
                update_data['contrasenia'] = data['contrasenia']  # Ya hasheada arriba
            if 'id_persona' in data:
                update_data['id_persona'] = int(data['id_persona'])
            if 'id_rol' in data:
                update_data['id_rol'] = int(data['id_rol'])
            if 'id_centro' in data:
                update_data['id_centro'] = int(data['id_centro'])
            if 'estado' in data:
                update_data['estado'] = data['estado']

            # Procesar centros_ids si está presente (sistema multi-centro)
            if 'centros_ids' in data:
                centros_ids = data.get('centros_ids', [])

                # Validar que centros_ids sea una lista
                if not isinstance(centros_ids, list):
                    return response_error("centros_ids debe ser una lista de IDs de centros", 400)

                # Validar que todos los IDs sean numeros enteros positivos
                try:
                    centros_ids = [int(c) for c in centros_ids]
                    if any(c <= 0 for c in centros_ids):
                        return response_error("Los IDs de centros deben ser numeros positivos", 400)
                except (ValueError, TypeError):
                    return response_error("Los IDs de centros deben ser numeros enteros", 400)

                # Si se proporcionan centros, actualizar id_centro con el primero (compatibilidad)
                if len(centros_ids) > 0:
                    update_data['id_centro'] = centros_ids[0]

                update_data['centros_ids'] = centros_ids

            # Agregar usuario que modifica
            update_data['usuario_modificacion'] = getattr(request, 'current_user', {}).get('id', 1)

            result = UsuarioComponent.update_usuario(usuario_id, update_data)

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
            HandleLogs.write_log(f"Datos recibidos en password_data: {password_data}")

            if not usuario_id or usuario_id <= 0:
                return response_error("ID de usuario invalido", 400)

            # Validar datos de entrada
            if not password_data:
                HandleLogs.write_error("No se recibió password_data")
                return response_error("Datos de contraseña requeridos", 400)

            nueva_contrasenia = password_data.get('nueva_contrasenia')
            confirmar_contrasenia = password_data.get('confirmar_contrasenia')

            HandleLogs.write_log(
                f"nueva_contrasenia: {nueva_contrasenia}, confirmar_contrasenia: {confirmar_contrasenia}")

            if not nueva_contrasenia:
                HandleLogs.write_error("No se recibió nueva_contrasenia")
                return response_error("Nueva contraseña requerida", 400)

            if not confirmar_contrasenia:
                HandleLogs.write_error("No se recibió confirmar_contrasenia")
                return response_error("Confirmación de contraseña requerida", 400)

            if nueva_contrasenia != confirmar_contrasenia:
                HandleLogs.write_error("Las contraseñas no coinciden")
                return response_error("Las contraseñas no coinciden", 400)

            # Validar fortaleza de contraseña
            from src.utils.general.validators import Validators
            password_validation = Validators.validate_password(nueva_contrasenia)
            HandleLogs.write_log(f"Resultado validación: {password_validation}")
            if not password_validation['valid']:
                HandleLogs.write_error(f"Validación fallida: {password_validation['message']}")
                return response_error(password_validation['message'], 400)

            # Cambiar contraseña
            result = UsuarioComponent.change_password(usuario_id, nueva_contrasenia)
            HandleLogs.write_log(f"Resultado cambio: {result}")

            if result['success']:
                HandleLogs.write_log(f"UsuarioService.change_password - Contraseña cambiada para usuario {usuario_id}")
                return response_success(None, "Contraseña actualizada exitosamente")
            else:
                HandleLogs.write_error(f"UsuarioService.change_password - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"UsuarioService.change_password - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)