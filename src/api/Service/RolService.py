from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error
from src.utils.general.validators import Validators
from src.api.Components.RolComponent import RolComponent


class RolService:
    """
    Servicio para la gestion de roles.
    Contiene la logica de negocio y validaciones.
    """

    @staticmethod
    def get_roles(include_inactive=False):
        """
        Obtener lista de roles.

        Args:
            include_inactive: Si es True, incluye roles inactivos

        Returns:
            Response con lista de roles o error
        """
        try:
            HandleLogs.write_log("RolService.get_roles - Iniciando")

            result = RolComponent.get_all_roles(include_inactive)

            if result.get('success'):
                roles = result.get('data', [])
                HandleLogs.write_log(f"RolService.get_roles - {len(roles)} roles encontrados")
                return response_success(roles, "Lista de roles obtenida correctamente")
            else:
                HandleLogs.write_error(f"RolService.get_roles - Error: {result.get('error')}")
                return response_error("Error obteniendo roles", 500)

        except Exception as e:
            HandleLogs.write_error(f"RolService.get_roles - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_rol_by_id(rol_id):
        """
        Obtener un rol por su ID.

        Args:
            rol_id: ID del rol

        Returns:
            Response con datos del rol o error
        """
        try:
            HandleLogs.write_log(f"RolService.get_rol_by_id - ID: {rol_id}")

            # Validar ID
            if not rol_id:
                return response_error("ID de rol requerido", 400)

            try:
                rol_id = int(rol_id)
            except (ValueError, TypeError):
                return response_error("ID de rol debe ser un numero valido", 400)

            result = RolComponent.get_rol_by_id(rol_id)

            if result.get('success'):
                rol = result.get('data')
                if rol:
                    HandleLogs.write_log(f"RolService.get_rol_by_id - Rol encontrado: {rol.get('nombre')}")
                    return response_success(rol, "Rol obtenido correctamente")
                else:
                    HandleLogs.write_log(f"RolService.get_rol_by_id - Rol no encontrado ID: {rol_id}")
                    return response_error("Rol no encontrado", 404)
            else:
                HandleLogs.write_error(f"RolService.get_rol_by_id - Error: {result.get('error')}")
                return response_error("Error obteniendo rol", 500)

        except Exception as e:
            HandleLogs.write_error(f"RolService.get_rol_by_id - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def create_rol(data, usuario_id=None):
        """
        Crear un nuevo rol.

        Args:
            data: Diccionario con datos del rol
            usuario_id: ID del usuario que crea

        Returns:
            Response con rol creado o error
        """
        try:
            HandleLogs.write_log("RolService.create_rol - Iniciando")

            # Validar campos requeridos
            required = ['nombre']
            validation = Validators.validate_required_fields(data, required)
            if not validation['valid']:
                return response_error(validation['message'], 400)

            nombre = data.get('nombre', '').strip()
            descripcion = data.get('descripcion', '').strip() if data.get('descripcion') else None

            # Validar longitud del nombre
            if len(nombre) < 2:
                return response_error("El nombre debe tener al menos 2 caracteres", 400)

            if len(nombre) > 50:
                return response_error("El nombre no puede exceder 50 caracteres", 400)

            # Verificar duplicado por nombre (UNIQUE constraint en BD)
            if RolComponent.check_nombre_exists(nombre):
                HandleLogs.write_log(f"RolService.create_rol - Nombre duplicado: {nombre}")
                return response_error("Ya existe un rol con ese nombre", 409)

            # Crear rol
            result = RolComponent.create_rol(
                nombre=nombre,
                descripcion=descripcion,
                usuario_creacion=usuario_id
            )

            if result.get('success'):
                nuevo_rol = result.get('data')
                HandleLogs.write_log(f"RolService.create_rol - Rol creado: {nombre}")
                return response_success(nuevo_rol, "Rol creado correctamente", 201)
            else:
                HandleLogs.write_error(f"RolService.create_rol - Error: {result.get('error')}")
                return response_error("Error al crear rol", 500)

        except Exception as e:
            HandleLogs.write_error(f"RolService.create_rol - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def update_rol(rol_id, data, usuario_id=None):
        """
        Actualizar un rol existente.

        Args:
            rol_id: ID del rol a actualizar
            data: Diccionario con datos a actualizar
            usuario_id: ID del usuario que modifica

        Returns:
            Response con rol actualizado o error
        """
        try:
            HandleLogs.write_log(f"RolService.update_rol - ID: {rol_id}")

            # Validar ID
            if not rol_id:
                return response_error("ID de rol requerido", 400)

            try:
                rol_id = int(rol_id)
            except (ValueError, TypeError):
                return response_error("ID de rol debe ser un numero valido", 400)

            # Verificar que el rol existe
            if not RolComponent.check_rol_exists(rol_id):
                HandleLogs.write_log(f"RolService.update_rol - Rol no existe ID: {rol_id}")
                return response_error("Rol no encontrado", 404)

            # Procesar campos a actualizar
            nombre = None
            descripcion = None

            if 'nombre' in data:
                nombre = data['nombre'].strip() if data['nombre'] else None
                if nombre:
                    # Validar longitud
                    if len(nombre) < 2:
                        return response_error("El nombre debe tener al menos 2 caracteres", 400)
                    if len(nombre) > 50:
                        return response_error("El nombre no puede exceder 50 caracteres", 400)

                    # Verificar duplicado (excluyendo el rol actual)
                    if RolComponent.check_nombre_exists(nombre, exclude_id=rol_id):
                        HandleLogs.write_log(f"RolService.update_rol - Nombre duplicado: {nombre}")
                        return response_error("Ya existe otro rol con ese nombre", 409)

            if 'descripcion' in data:
                descripcion = data['descripcion'].strip() if data['descripcion'] else ''

            # Verificar que hay algo que actualizar
            if nombre is None and descripcion is None:
                return response_error("No hay datos para actualizar", 400)

            # Actualizar rol
            result = RolComponent.update_rol(
                rol_id=rol_id,
                nombre=nombre,
                descripcion=descripcion,
                usuario_modificacion=usuario_id
            )

            if result.get('success'):
                rol_actualizado = result.get('data')
                HandleLogs.write_log(f"RolService.update_rol - Rol actualizado ID: {rol_id}")
                return response_success(rol_actualizado, "Rol actualizado correctamente")
            else:
                HandleLogs.write_error(f"RolService.update_rol - Error: {result.get('error')}")
                return response_error("Error al actualizar rol", 500)

        except Exception as e:
            HandleLogs.write_error(f"RolService.update_rol - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def delete_rol(rol_id, usuario_id=None):
        """
        Desactivar un rol (soft delete).

        Args:
            rol_id: ID del rol a desactivar
            usuario_id: ID del usuario que realiza la accion

        Returns:
            Response con confirmacion o error
        """
        try:
            HandleLogs.write_log(f"RolService.delete_rol - ID: {rol_id}")

            # Validar ID
            if not rol_id:
                return response_error("ID de rol requerido", 400)

            try:
                rol_id = int(rol_id)
            except (ValueError, TypeError):
                return response_error("ID de rol debe ser un numero valido", 400)

            # Verificar que el rol existe
            if not RolComponent.check_rol_exists(rol_id):
                HandleLogs.write_log(f"RolService.delete_rol - Rol no existe ID: {rol_id}")
                return response_error("Rol no encontrado", 404)

            # Verificar estado actual
            estado = RolComponent.get_rol_status(rol_id)
            if estado == 'inactivo':
                return response_error("El rol ya se encuentra inactivo", 400)

            # Verificar si el rol esta en uso
            if RolComponent.check_rol_in_use(rol_id):
                HandleLogs.write_log(f"RolService.delete_rol - Rol en uso ID: {rol_id}")
                return response_error("No se puede desactivar el rol porque esta asignado a usuarios activos", 409)

            # Desactivar rol
            result = RolComponent.deactivate_rol(rol_id, usuario_id)

            if result.get('success'):
                HandleLogs.write_log(f"RolService.delete_rol - Rol desactivado ID: {rol_id}")
                return response_success(None, "Rol desactivado correctamente")
            else:
                HandleLogs.write_error(f"RolService.delete_rol - Error: {result.get('error')}")
                return response_error("Error al desactivar rol", 500)

        except Exception as e:
            HandleLogs.write_error(f"RolService.delete_rol - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def reactivate_rol(rol_id, usuario_id=None):
        """
        Reactivar un rol inactivo.

        Args:
            rol_id: ID del rol a reactivar
            usuario_id: ID del usuario que realiza la accion

        Returns:
            Response con confirmacion o error
        """
        try:
            HandleLogs.write_log(f"RolService.reactivate_rol - ID: {rol_id}")

            # Validar ID
            if not rol_id:
                return response_error("ID de rol requerido", 400)

            try:
                rol_id = int(rol_id)
            except (ValueError, TypeError):
                return response_error("ID de rol debe ser un numero valido", 400)

            # Verificar que el rol existe
            if not RolComponent.check_rol_exists(rol_id):
                HandleLogs.write_log(f"RolService.reactivate_rol - Rol no existe ID: {rol_id}")
                return response_error("Rol no encontrado", 404)

            # Verificar estado actual
            estado = RolComponent.get_rol_status(rol_id)
            if estado == 'activo':
                return response_error("El rol ya se encuentra activo", 400)

            # Reactivar rol
            result = RolComponent.reactivate_rol(rol_id, usuario_id)

            if result.get('success'):
                # Obtener rol actualizado para devolver
                rol_result = RolComponent.get_rol_by_id(rol_id)
                rol_data = rol_result.get('data') if rol_result.get('success') else None

                HandleLogs.write_log(f"RolService.reactivate_rol - Rol reactivado ID: {rol_id}")
                return response_success(rol_data, "Rol reactivado correctamente")
            else:
                HandleLogs.write_error(f"RolService.reactivate_rol - Error: {result.get('error')}")
                return response_error("Error al reactivar rol", 500)

        except Exception as e:
            HandleLogs.write_error(f"RolService.reactivate_rol - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)
