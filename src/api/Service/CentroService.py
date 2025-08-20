from src.api.Components.CentroComponent import CentroComponent
from src.utils.general.logs import HandleLogs


class CentroService:
    
    @staticmethod
    def get_all_centros():
        """Obtener lista de todos los centros activos"""
        try:
            result = CentroComponent.get_all_centros()
            
            if result["success"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": "Centros obtenidos exitosamente"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "Error al obtener centros"
                }
                
        except Exception as e:
            HandleLogs.write_error(f"CentroService.get_all_centros - Error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error del servicio: {str(e)}"
            }
    
    @staticmethod
    def get_centro_by_id(centro_id):
        """Obtener información de un centro específico"""
        try:
            # Validar ID
            if not centro_id or centro_id <= 0:
                return {
                    "success": False,
                    "data": None,
                    "message": "ID de centro inválido"
                }
            
            result = CentroComponent.get_centro_by_id(centro_id)
            
            if result["success"] and result["data"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": "Centro encontrado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "Centro no encontrado"
                }
                
        except Exception as e:
            HandleLogs.write_error(f"CentroService.get_centro_by_id - Error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error del servicio: {str(e)}"
            }
    
    @staticmethod
    def get_centro_by_codigo(codigo):
        """Obtener centro por código (NORTE/SUR)"""
        try:
            # Validar código
            if not codigo or codigo.strip() == "":
                return {
                    "success": False,
                    "data": None,
                    "message": "Código de centro requerido"
                }
            
            codigo = codigo.upper().strip()
            if codigo not in ["NORTE", "SUR"]:
                return {
                    "success": False,
                    "data": None,
                    "message": "Código de centro inválido. Debe ser NORTE o SUR"
                }
            
            result = CentroComponent.get_centro_by_codigo(codigo)
            
            if result["success"] and result["data"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": "Centro encontrado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "Centro no encontrado"
                }
                
        except Exception as e:
            HandleLogs.write_error(f"CentroService.get_centro_by_codigo - Error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error del servicio: {str(e)}"
            }
    
    @staticmethod
    def validate_user_centro_access(user_id, centro_id):
        """Validar acceso de usuario a centro específico"""
        try:
            # Validar parámetros
            if not user_id or user_id <= 0:
                return {
                    "success": False,
                    "data": None,
                    "message": "ID de usuario inválido"
                }
                
            if not centro_id or centro_id <= 0:
                return {
                    "success": False,
                    "data": None,
                    "message": "ID de centro inválido"
                }
            
            result = CentroComponent.validate_user_centro_access(user_id, centro_id)
            
            if result["success"] and result["data"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": "Usuario tiene acceso al centro"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "Usuario no tiene acceso al centro especificado"
                }
                
        except Exception as e:
            HandleLogs.write_error(f"CentroService.validate_user_centro_access - Error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error del servicio: {str(e)}"
            }
    
    @staticmethod
    def get_centro_statistics(centro_id):
        """Obtener estadísticas de un centro"""
        try:
            # Validar ID
            if not centro_id or centro_id <= 0:
                return {
                    "success": False,
                    "data": None,
                    "message": "ID de centro inválido"
                }
            
            result = CentroComponent.get_centro_statistics(centro_id)
            
            if result["success"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": "Estadísticas obtenidas exitosamente"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "Error al obtener estadísticas del centro"
                }
                
        except Exception as e:
            HandleLogs.write_error(f"CentroService.get_centro_statistics - Error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error del servicio: {str(e)}"
            }
    
    @staticmethod
    def get_centros_for_login():
        """Obtener lista simplificada de centros para selector de login"""
        try:
            result = CentroComponent.get_all_centros()
            
            if result["success"]:
                # Simplificar datos para el selector de login
                centros_login = []
                for centro in result["data"]:
                    centros_login.append({
                        "id": centro["id"],
                        "nombre": centro["nombre"],
                        "codigo": centro["codigo"],
                        "turno_principal": centro["turno_principal"]
                    })
                
                return {
                    "success": True,
                    "data": centros_login,
                    "message": "Centros para login obtenidos exitosamente"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "Error al obtener centros para login"
                }
                
        except Exception as e:
            HandleLogs.write_error(f"CentroService.get_centros_for_login - Error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error del servicio: {str(e)}"
            }