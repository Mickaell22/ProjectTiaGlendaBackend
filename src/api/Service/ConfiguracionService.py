# src/api/Service/ConfiguracionService.py
from src.api.Components.ConfiguracionComponent import ConfiguracionComponent
from src.utils.general.response import response_success, response_error
from src.utils.general.logs import HandleLogs
from flask import request
import re

class ConfiguracionService:
    
    # ============================================
    # SERVICIOS DE CONFIGURACIÓN GENERAL
    # ============================================
    
    @staticmethod
    def get_configuracion_general():
        """Obtener configuración del centro del usuario actual"""
        try:
            # Obtener centro_id del usuario actual
            centro_id = request.current_user.get('id_centro')
            if not centro_id:
                return response_error("Usuario sin centro asignado", 403)
            
            component = ConfiguracionComponent()
            result = component.get_configuracion_general(centro_id)
            
            if result['success']:
                return response_success(
                    result['data'], 
                    f"Configuración del centro obtenida exitosamente"
                )
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.get_configuracion_general: {str(e)}")
            return response_error("Error interno del servidor", 500)
    
    @staticmethod
    def update_configuracion_general():
        """Actualizar configuración del centro del usuario actual"""
        try:
            data = request.get_json()
            
            if not data:
                return response_error("Datos requeridos", 400)
            
            # Obtener centro_id del usuario actual
            centro_id = request.current_user.get('id_centro')
            if not centro_id:
                return response_error("Usuario sin centro asignado", 403)
            
            # Validar campos requeridos
            required_fields = ['nombre_centro']
            for field in required_fields:
                if field not in data or not data[field]:
                    return response_error(f"Campo requerido: {field}", 400)
            
            # Validar email si se proporciona
            if data.get('email') and not ConfiguracionService._validate_email(data['email']):
                return response_error("Formato de email inválido", 400)
            
            # Validar teléfono si se proporciona
            if data.get('telefono') and not ConfiguracionService._validate_phone(data['telefono']):
                return response_error("Formato de teléfono inválido", 400)
            
            # Validar horarios
            if data.get('horario_inicio') and data.get('horario_fin'):
                if not ConfiguracionService._validate_time_range(data['horario_inicio'], data['horario_fin']):
                    return response_error("El horario de inicio debe ser anterior al horario de fin", 400)
            
            component = ConfiguracionComponent()
            result = component.update_configuracion_general(data, centro_id)
            
            if result['success']:
                HandleLogs.write_log(f"Configuración general actualizada por usuario: {request.current_user.get('usuario', 'unknown')}")
                return response_success(None, result['message'])
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.update_configuracion_general: {str(e)}")
            return response_error("Error interno del servidor", 500)
    
    # ============================================
    # SERVICIOS DE CONFIGURACIÓN DE NOTIFICACIONES
    # ============================================
    
    @staticmethod
    def get_configuracion_notificaciones(user_id=None):
        """Obtener configuración de notificaciones (global o por usuario)"""
        try:
            component = ConfiguracionComponent()
            result = component.get_configuracion_notificaciones(user_id)
            
            if result['success']:
                return response_success(
                    result['data'], 
                    f"Configuración de notificaciones obtenida exitosamente"
                )
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.get_configuracion_notificaciones: {str(e)}")
            return response_error("Error interno del servidor", 500)
    
    @staticmethod
    def update_configuracion_notificaciones(user_id=None):
        """Actualizar configuración de notificaciones"""
        try:
            data = request.get_json()
            
            if not data:
                return response_error("Datos requeridos", 400)
            
            # Validar datos de notificaciones
            boolean_fields = [
                'notificaciones_habilitadas', 'notificaciones_sesion_terapia', 
                'notificaciones_clase_pedagogica', 'notificaciones_cancelaciones',
                'notificaciones_reprogramaciones', 'sonido_habilitado'
            ]
            
            for field in boolean_fields:
                if field in data and not isinstance(data[field], bool):
                    return response_error(f"El campo {field} debe ser true o false", 400)
            
            # Validar tiempo de anticipación
            if 'tiempo_anticipacion_minutos' in data:
                tiempo = data['tiempo_anticipacion_minutos']
                if not isinstance(tiempo, int) or tiempo < 0 or tiempo > 120:
                    return response_error("El tiempo de anticipación debe ser entre 0 y 120 minutos", 400)
            
            component = ConfiguracionComponent()
            result = component.update_configuracion_notificaciones(data, user_id)
            
            if result['success']:
                HandleLogs.write_log(f"Configuración de notificaciones actualizada por usuario: {request.current_user.get('usuario', 'unknown')}")
                return response_success(None, result['message'])
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.update_configuracion_notificaciones: {str(e)}")
            return response_error("Error interno del servidor", 500)

    # ============================================
    # SERVICIOS SIMPLIFICADOS
    # ============================================

    @staticmethod
    def get_resumen_configuracion():
        """Obtener resumen de configuraciones básicas (solo general y notificaciones)"""
        try:
            current_user_id = request.current_user.get('id')
            centro_id = request.current_user.get('id_centro')
            
            if not centro_id:
                return response_error("Usuario sin centro asignado", 403)
            
            component = ConfiguracionComponent()
            
            # Obtener configuración general
            general_result = component.get_configuracion_general(centro_id)
            general_config = general_result.get('data') if general_result.get('success') else None
            
            # Obtener configuración de notificaciones del usuario
            notif_user_result = component.get_configuracion_notificaciones(current_user_id)
            notif_user_config = notif_user_result.get('data') if notif_user_result.get('success') else None
            
            # Obtener configuración de notificaciones globales
            notif_global_result = component.get_configuracion_notificaciones()
            notif_global_config = notif_global_result.get('data') if notif_global_result.get('success') else None
            
            resumen = {
                'general': general_config,
                'notificaciones_usuario': notif_user_config,
                'notificaciones_global': notif_global_config
            }
            
            return response_success(resumen, "Resumen de configuración obtenido exitosamente")
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.get_resumen_configuracion: {str(e)}")
            return response_error("Error interno del servidor", 500)

    # ============================================
    # MÉTODOS DE VALIDACIÓN PRIVADOS
    # ============================================
    
    @staticmethod
    def _validate_email(email):
        """Validar formato de email"""
        try:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        except:
            return False
    
    @staticmethod
    def _validate_phone(phone):
        """Validar formato de teléfono"""
        try:
            # Permite números con espacios, guiones, paréntesis y el símbolo +
            pattern = r'^[\d\s\-\(\)\+]{7,20}$'
            return bool(re.match(pattern, phone))
        except:
            return False
    
    @staticmethod
    def _validate_time_range(start_time, end_time):
        """Validar que el horario de inicio sea anterior al horario de fin"""
        try:
            return start_time < end_time
        except:
            return False

    # ============================================
    # MÉTODOS DE MAPEO DE DATOS (para compatibilidad frontend)
    # ============================================
    
    @staticmethod
    def mapGeneralConfigToFrontend(backend_data):
        """Mapear datos del backend al formato esperado por el frontend"""
        if not backend_data:
            return {}
        
        return {
            'nombreCentro': backend_data.get('nombre_centro', ''),
            'direccion': backend_data.get('direccion', ''),
            'telefono': backend_data.get('telefono', ''),
            'email': backend_data.get('email', ''),
            'horarioInicio': backend_data.get('horario_inicio', '08:00'),
            'horarioFin': backend_data.get('horario_fin', '17:00'),
            'zonaHoraria': backend_data.get('zona_horaria', 'America/Guayaquil'),
            'formatoFecha': backend_data.get('formato_fecha', 'DD/MM/YYYY'),
            'formatoHora': backend_data.get('formato_hora', '24h'),
            'moneda': backend_data.get('moneda', 'USD'),
            'idioma': backend_data.get('idioma', 'es'),
            'descripcion': backend_data.get('descripcion', '')
        }