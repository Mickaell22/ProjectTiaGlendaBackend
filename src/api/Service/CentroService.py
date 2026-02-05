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
            
            if result["success"] and result["data"]:
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

    @staticmethod
    def create_centro(data):
        """Crear un nuevo centro"""
        try:
            # Validar campos requeridos
            if not data.get('nombre') or data.get('nombre').strip() == "":
                return {
                    "success": False,
                    "data": None,
                    "message": "El nombre del centro es requerido"
                }

            if not data.get('codigo') or data.get('codigo').strip() == "":
                return {
                    "success": False,
                    "data": None,
                    "message": "El codigo del centro es requerido"
                }

            # Normalizar codigo
            data['codigo'] = data['codigo'].upper().strip()
            data['nombre'] = data['nombre'].strip()

            # Verificar que el codigo no exista
            check_result = CentroComponent.check_codigo_exists(data['codigo'])
            if check_result["success"] and check_result["data"]:
                return {
                    "success": False,
                    "data": None,
                    "message": f"Ya existe un centro con el codigo {data['codigo']}"
                }

            result = CentroComponent.create_centro(data)

            if result["success"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": "Centro creado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "Error al crear el centro"
                }

        except Exception as e:
            HandleLogs.write_error(f"CentroService.create_centro - Error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error del servicio: {str(e)}"
            }

    @staticmethod
    def update_centro(centro_id, data):
        """Actualizar un centro existente"""
        try:
            # Validar ID
            if not centro_id or centro_id <= 0:
                return {
                    "success": False,
                    "data": None,
                    "message": "ID de centro invalido"
                }

            # Validar campos requeridos
            if not data.get('nombre') or data.get('nombre').strip() == "":
                return {
                    "success": False,
                    "data": None,
                    "message": "El nombre del centro es requerido"
                }

            if not data.get('codigo') or data.get('codigo').strip() == "":
                return {
                    "success": False,
                    "data": None,
                    "message": "El codigo del centro es requerido"
                }

            # Normalizar codigo
            data['codigo'] = data['codigo'].upper().strip()
            data['nombre'] = data['nombre'].strip()

            # Verificar que el centro exista
            centro_existente = CentroComponent.get_centro_by_id(centro_id)
            if not centro_existente["success"] or not centro_existente["data"]:
                return {
                    "success": False,
                    "data": None,
                    "message": "Centro no encontrado"
                }

            # Verificar que el codigo no exista en otro centro
            check_result = CentroComponent.check_codigo_exists(data['codigo'], centro_id)
            if check_result["success"] and check_result["data"]:
                return {
                    "success": False,
                    "data": None,
                    "message": f"Ya existe otro centro con el codigo {data['codigo']}"
                }

            result = CentroComponent.update_centro(centro_id, data)

            if result["success"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": "Centro actualizado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "Error al actualizar el centro"
                }

        except Exception as e:
            HandleLogs.write_error(f"CentroService.update_centro - Error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error del servicio: {str(e)}"
            }

    @staticmethod
    def delete_centro(centro_id, usuario_id):
        """Eliminar un centro (soft delete)"""
        try:
            # Validar ID
            if not centro_id or centro_id <= 0:
                return {
                    "success": False,
                    "data": None,
                    "message": "ID de centro invalido"
                }

            # Verificar que el centro exista
            centro_existente = CentroComponent.get_centro_by_id(centro_id)
            if not centro_existente["success"] or not centro_existente["data"]:
                return {
                    "success": False,
                    "data": None,
                    "message": "Centro no encontrado"
                }

            # Verificar que no tenga datos asociados activos
            stats = CentroComponent.get_centro_statistics(centro_id)
            if stats["success"] and stats["data"]:
                total = (
                    stats["data"].get("total_usuarios", 0) +
                    stats["data"].get("total_personal", 0) +
                    stats["data"].get("total_pacientes", 0)
                )
                if total > 0:
                    return {
                        "success": False,
                        "data": None,
                        "message": "No se puede eliminar el centro porque tiene usuarios, personal o pacientes asociados"
                    }

            result = CentroComponent.delete_centro(centro_id, usuario_id)

            if result["success"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": "Centro eliminado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "Error al eliminar el centro"
                }

        except Exception as e:
            HandleLogs.write_error(f"CentroService.delete_centro - Error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error del servicio: {str(e)}"
            }

    @staticmethod
    def activate_centro(centro_id, usuario_id):
        """Reactivar un centro inactivo"""
        try:
            # Validar ID
            if not centro_id or centro_id <= 0:
                return {
                    "success": False,
                    "data": None,
                    "message": "ID de centro invalido"
                }

            result = CentroComponent.activate_centro(centro_id, usuario_id)

            if result["success"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": "Centro reactivado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": result.get("message", "Error al reactivar el centro")
                }

        except Exception as e:
            HandleLogs.write_error(f"CentroService.activate_centro - Error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error del servicio: {str(e)}"
            }