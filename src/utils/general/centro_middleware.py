from functools import wraps
from flask import request, current_app
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_error
from src.utils.general.security import SecurityUtils


class CentroMiddleware:
    """
    Middleware para filtrado automático por centro en consultas de base de datos
    """
    
    @staticmethod
    def get_current_user_centro():
        """
        Obtener el ID del centro del usuario actual desde el token JWT
        """
        try:
            # Obtener token del header Authorization
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return None
            
            # Extraer token
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return None
            
            # Verificar token y obtener datos
            token_result = SecurityUtils.verify_token(token)
            
            if token_result['success'] and token_result['data']:
                return token_result['data'].get('id_centro')
            
            return None
            
        except Exception as e:
            HandleLogs.write_error(f"CentroMiddleware.get_current_user_centro - Error: {str(e)}")
            return None
    
    @staticmethod
    def get_current_user_info():
        """
        Obtener información completa del usuario actual desde el token JWT
        """
        try:
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return None
            
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return None
            
            token_result = SecurityUtils.verify_token(token)
            
            if token_result['success'] and token_result['data']:
                return token_result['data']
            
            return None
            
        except Exception as e:
            HandleLogs.write_error(f"CentroMiddleware.get_current_user_info - Error: {str(e)}")
            return None
    
    @staticmethod
    def require_centro_access(f):
        """
        Decorador que requiere que el usuario tenga acceso a un centro válido
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                user_info = CentroMiddleware.get_current_user_info()
                
                if not user_info:
                    return response_error("Token de acceso requerido", 401)
                
                if not user_info.get('id_centro'):
                    return response_error("Usuario sin centro asignado", 403)
                
                # Agregar información del centro a los kwargs para uso en la función
                kwargs['current_user_centro'] = user_info.get('id_centro')
                kwargs['current_user_id'] = user_info.get('id')
                kwargs['current_user_rol'] = user_info.get('rol')
                
                return f(*args, **kwargs)
                
            except Exception as e:
                HandleLogs.write_error(f"CentroMiddleware.require_centro_access - Error: {str(e)}")
                return response_error("Error validando acceso al centro", 500)
        
        return decorated_function
    
    @staticmethod
    def validate_centro_param(param_name='centro_id'):
        """
        Decorador que valida que el centro especificado en los parámetros 
        coincida con el centro del usuario autenticado (excepto para administradores)
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    user_info = CentroMiddleware.get_current_user_info()
                    
                    if not user_info:
                        return response_error("Token de acceso requerido", 401)
                    
                    user_centro_id = user_info.get('id_centro')
                    user_rol = user_info.get('rol')
                    
                    if not user_centro_id:
                        return response_error("Usuario sin centro asignado", 403)
                    
                    # Los administradores pueden acceder a cualquier centro
                    if user_rol and user_rol.lower() == 'administrador':
                        kwargs['current_user_centro'] = user_centro_id
                        kwargs['current_user_id'] = user_info.get('id')
                        kwargs['current_user_rol'] = user_rol
                        kwargs['is_admin'] = True
                        return f(*args, **kwargs)
                    
                    # Para otros roles, validar que el centro solicitado coincida con el del usuario
                    requested_centro = request.args.get(param_name) or request.json.get(param_name) if request.json else None
                    
                    if requested_centro and int(requested_centro) != user_centro_id:
                        return response_error("No tiene acceso al centro especificado", 403)
                    
                    kwargs['current_user_centro'] = user_centro_id
                    kwargs['current_user_id'] = user_info.get('id')
                    kwargs['current_user_rol'] = user_rol
                    kwargs['is_admin'] = False
                    
                    return f(*args, **kwargs)
                    
                except Exception as e:
                    HandleLogs.write_error(f"CentroMiddleware.validate_centro_param - Error: {str(e)}")
                    return response_error("Error validando parámetros de centro", 500)
            
            return decorated_function
        return decorator
    
    @staticmethod
    def add_centro_filter_to_query(base_query, centro_id, table_alias=None):
        """
        Agregar filtro de centro a una consulta SQL existente
        
        Args:
            base_query (str): Consulta SQL base
            centro_id (int): ID del centro a filtrar
            table_alias (str): Alias de la tabla principal (opcional)
        
        Returns:
            tuple: (query_modificada, parametros_adicionales)
        """
        try:
            if not centro_id:
                return base_query, []
            
            # Determinar el prefijo de la tabla
            table_prefix = f"{table_alias}." if table_alias else ""
            
            # Agregar filtro de centro
            if "WHERE" in base_query.upper():
                modified_query = f"{base_query} AND {table_prefix}id_centro = %s"
            else:
                modified_query = f"{base_query} WHERE {table_prefix}id_centro = %s"
            
            return modified_query, [centro_id]
            
        except Exception as e:
            HandleLogs.write_error(f"CentroMiddleware.add_centro_filter_to_query - Error: {str(e)}")
            return base_query, []
    
    @staticmethod
    def get_centro_filtered_query(base_query, user_centro_id, table_alias=None, is_admin=False):
        """
        Obtener consulta con filtro de centro aplicado automáticamente
        
        Args:
            base_query (str): Consulta SQL base
            user_centro_id (int): ID del centro del usuario
            table_alias (str): Alias de la tabla principal
            is_admin (bool): Si el usuario es administrador (no aplica filtro)
        
        Returns:
            tuple: (query_final, parametros_adicionales)
        """
        try:
            if is_admin or not user_centro_id:
                return base_query, []
            
            return CentroMiddleware.add_centro_filter_to_query(
                base_query, user_centro_id, table_alias
            )
            
        except Exception as e:
            HandleLogs.write_error(f"CentroMiddleware.get_centro_filtered_query - Error: {str(e)}")
            return base_query, []


def require_centro_access(f):
    """
    Función decoradora independiente para requerir acceso a centro
    """
    return CentroMiddleware.require_centro_access(f)


def validate_centro_param(param_name='centro_id'):
    """
    Función decoradora independiente para validar parámetro de centro
    """
    return CentroMiddleware.validate_centro_param(param_name)