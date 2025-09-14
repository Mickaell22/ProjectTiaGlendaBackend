# src/api/Service/ConfiguracionService.py
from src.api.Components.ConfiguracionComponent import ConfiguracionComponent
from src.utils.general.response import response_success, response_error, internal_response
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
            
            # DEBUG: Log de datos recibidos
            HandleLogs.write_log(f"DEBUG - Datos recibidos del frontend para centro {centro_id}: {data}")
            
            # Los datos ya vienen mapeados desde el frontend
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
    # SERVICIOS DE CONFIGURACIÓN DE SESIONES
    # ============================================
    
    @staticmethod
    def get_configuracion_sesiones():
        """Obtener configuración de sesiones"""
        try:
            component = ConfiguracionComponent()
            result = component.get_configuracion_sesiones()
            
            if result['success']:
                return response_success(
                    result['data'], 
                    "Configuración de sesiones obtenida exitosamente"
                )
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.get_configuracion_sesiones: {str(e)}")
            return response_error("Error interno del servidor", 500)
    
    @staticmethod
    def update_configuracion_sesiones():
        """Actualizar configuración de sesiones"""
        try:
            data = request.get_json()
            
            if not data:
                return response_error("Datos requeridos", 400)
            
            # Los datos ya vienen mapeados desde el frontend
            # Validar campos numéricos con sus rangos específicos
            field_validations = {
                'duracion_sesion_terapia': {'min': 15, 'max': 300, 'name': 'Duración de sesión terapéutica'},
                'duracion_clase_pedagogica': {'min': 15, 'max': 300, 'name': 'Duración de clase pedagógica'},
                'tolerancia_llegada_tarde': {'min': 0, 'max': 60, 'name': 'Tolerancia de llegada tarde'},
                'tiempo_recordatorio': {'min': 5, 'max': 120, 'name': 'Tiempo de recordatorio'},
                'permitir_cancelacion_horas': {'min': 1, 'max': 168, 'name': 'Horas para cancelación'},
                'permitir_reprogramacion_horas': {'min': 1, 'max': 168, 'name': 'Horas para reprogramación'},
                'capacidad_maxima_clase': {'min': 1, 'max': 30, 'name': 'Capacidad máxima de clase'},
                'escala_calificacion_min': {'min': 0, 'max': 20, 'name': 'Escala mínima de calificación'},
                'escala_calificacion_max': {'min': 1, 'max': 100, 'name': 'Escala máxima de calificación'}
            }
            
            for field, validation in field_validations.items():
                if field in data and data[field] is not None:
                    value = data[field]
                    if not isinstance(value, int) or value < validation['min'] or value > validation['max']:
                        return response_error(
                            f"{validation['name']} debe estar entre {validation['min']} y {validation['max']}", 
                            400
                        )
            
            # Validar escala de calificaciones
            if (data.get('escala_calificacion_min') is not None and 
                data.get('escala_calificacion_max') is not None):
                if data['escala_calificacion_min'] >= data['escala_calificacion_max']:
                    return response_error("La escala mínima debe ser menor que la máxima", 400)
            
            # Validar sistema de calificaciones
            if data.get('sistema_calificaciones'):
                valid_systems = ['numerico', 'alfabetico', 'conceptual']
                if data['sistema_calificaciones'] not in valid_systems:
                    return response_error(f"Sistema de calificaciones debe ser uno de: {', '.join(valid_systems)}", 400)
            
            component = ConfiguracionComponent()
            result = component.update_configuracion_sesiones(data)
            
            if result['success']:
                HandleLogs.write_log(f"Configuración de sesiones actualizada por usuario: {request.current_user.get('usuario', 'unknown')}")
                return response_success(None, result['message'])
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.update_configuracion_sesiones: {str(e)}")
            return response_error("Error interno del servidor", 500)
    
    # ============================================
    # SERVICIOS DE CONFIGURACIÓN DE NOTIFICACIONES
    # ============================================
    
    @staticmethod
    def get_configuracion_notificaciones(user_id=None):
        """Obtener configuración de notificaciones"""
        try:
            # Si no se especifica user_id, obtener configuración global
            if user_id is None:
                component = ConfiguracionComponent()
                result = component.get_configuracion_notificaciones()
            else:
                # Validar que el usuario actual pueda acceder a esta configuración
                current_user_id = request.current_user.get('id')
                current_user_rol = request.current_user.get('rol')
                
                # Solo admin puede ver configuración de otros usuarios
                if user_id != current_user_id and current_user_rol != 'Administrador':
                    return response_error("No tiene permisos para acceder a esta configuración", 403)
                
                component = ConfiguracionComponent()
                result = component.get_configuracion_notificaciones(user_id)
            
            if result['success']:
                return response_success(
                    result['data'], 
                    "Configuración de notificaciones obtenida exitosamente"
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
            
            # Validar permisos
            if user_id is not None:
                current_user_id = request.current_user.get('id')
                current_user_rol = request.current_user.get('rol')
                
                # Solo admin puede modificar configuración de otros usuarios
                if user_id != current_user_id and current_user_rol != 'Administrador':
                    return response_error("No tiene permisos para modificar esta configuración", 403)
            else:
                # Solo admin puede modificar configuración global
                if request.current_user.get('rol') != 'Administrador':
                    return response_error("Solo administradores pueden modificar la configuración global", 403)
            
            # Validar campos booleanos
            boolean_fields = [
                'notificaciones_habilitadas', 'notificaciones_sesion_terapia',
                'notificaciones_clase_pedagogica', 'notificaciones_cancelaciones',
                'notificaciones_reprogramaciones', 'sonido_habilitado'
            ]
            
            for field in boolean_fields:
                if field in data and not isinstance(data[field], bool):
                    return response_error(f"El campo {field} debe ser verdadero o falso", 400)
            
            # Validar tiempo de anticipación
            if 'tiempo_anticipacion_minutos' in data:
                value = data['tiempo_anticipacion_minutos']
                valid_times = [5, 10, 15, 30, 60]
                if value not in valid_times:
                    return response_error(f"Tiempo de anticipación debe ser uno de: {', '.join(map(str, valid_times))} minutos", 400)
            
            # Validar horarios de modo silencioso (solo para usuarios específicos)
            if user_id and ('modo_silencioso_inicio' in data or 'modo_silencioso_fin' in data):
                inicio = data.get('modo_silencioso_inicio')
                fin = data.get('modo_silencioso_fin')
                
                if inicio and fin:
                    if not ConfiguracionService._validate_time_range(inicio, fin):
                        return response_error("El horario de inicio del modo silencioso debe ser anterior al horario de fin", 400)
            
            component = ConfiguracionComponent()
            result = component.update_configuracion_notificaciones(data, user_id)
            
            if result['success']:
                config_type = "usuario" if user_id else "global"
                HandleLogs.write_log(f"Configuración de notificaciones {config_type} actualizada por usuario: {request.current_user.get('usuario', 'unknown')}")
                return response_success(None, result['message'])
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.update_configuracion_notificaciones: {str(e)}")
            return response_error("Error interno del servidor", 500)
    
    # ============================================
    # SERVICIOS DE CONFIGURACIÓN DE SEGURIDAD
    # ============================================
    
    @staticmethod
    def get_configuracion_seguridad():
        """Obtener configuración de seguridad"""
        try:
            # Solo administradores pueden acceder
            if request.current_user.get('rol') != 'Administrador':
                return response_error("Solo administradores pueden acceder a la configuración de seguridad", 403)
            
            component = ConfiguracionComponent()
            result = component.get_configuracion_seguridad()
            
            if result['success']:
                return response_success(
                    result['data'], 
                    "Configuración de seguridad obtenida exitosamente"
                )
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.get_configuracion_seguridad: {str(e)}")
            return response_error("Error interno del servidor", 500)
    
    @staticmethod
    def update_configuracion_seguridad():
        """Actualizar configuración de seguridad"""
        try:
            # Solo administradores pueden modificar
            if request.current_user.get('rol') != 'Administrador':
                return response_error("Solo administradores pueden modificar la configuración de seguridad", 403)
            
            data = request.get_json()
            
            if not data:
                return response_error("Datos requeridos", 400)
            
            # Validar longitud mínima de password
            if 'longitud_minima_password' in data:
                value = data['longitud_minima_password']
                if not isinstance(value, int) or value < 6 or value > 50:
                    return response_error("La longitud mínima de contraseña debe estar entre 6 y 50 caracteres", 400)
            
            # Validar campos booleanos
            boolean_fields = [
                'requerir_mayusculas', 'requerir_minusculas', 'requerir_numeros',
                'requerir_simbolos', 'habilitar_2fa', 'audit_log_habilitado'
            ]
            
            for field in boolean_fields:
                if field in data and not isinstance(data[field], bool):
                    return response_error(f"El campo {field} debe ser verdadero o falso", 400)
            
            # Validar campos numéricos positivos
            numeric_fields = [
                'expiracion_password_dias', 'tiempo_sesion_minutos',
                'intentos_login_maximo', 'tiempo_bloqueo_minutos', 'retener_logs_dias'
            ]
            
            for field in numeric_fields:
                if field in data:
                    value = data[field]
                    if not isinstance(value, int) or value <= 0:
                        return response_error(f"El campo {field} debe ser un número entero positivo", 400)
            
            # Validaciones específicas
            if 'tiempo_sesion_minutos' in data and data['tiempo_sesion_minutos'] > 1440:  # 24 horas
                return response_error("El tiempo de sesión no puede exceder 24 horas (1440 minutos)", 400)
            
            if 'intentos_login_maximo' in data and data['intentos_login_maximo'] > 20:
                return response_error("El número máximo de intentos de login no puede exceder 20", 400)
            
            component = ConfiguracionComponent()
            result = component.update_configuracion_seguridad(data)
            
            if result['success']:
                HandleLogs.write_log(f"Configuración de seguridad actualizada por usuario: {request.current_user.get('usuario', 'unknown')}")
                return response_success(None, result['message'])
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.update_configuracion_seguridad: {str(e)}")
            return response_error("Error interno del servidor", 500)
    
    # ============================================
    # SERVICIOS DE INICIALIZACIÓN
    # ============================================
    
    @staticmethod
    def inicializar_sistema_configuracion():
        """Inicializar tablas de configuración"""
        try:
            # Solo administradores pueden inicializar
            if request.current_user.get('rol') != 'Administrador':
                return response_error("Solo administradores pueden inicializar el sistema de configuración", 403)
            
            component = ConfiguracionComponent()
            result = component.crear_tablas_configuracion()
            
            if result:
                HandleLogs.write_log(f"Sistema de configuración inicializado por usuario: {request.current_user.get('usuario', 'unknown')}")
                return response_success(None, "Sistema de configuración inicializado exitosamente")
            else:
                return response_error("Error inicializando sistema de configuración", 500)
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.inicializar_sistema_configuracion: {str(e)}")
            return response_error("Error interno del servidor", 500)
    
    @staticmethod
    def get_resumen_configuracion():
        """Obtener resumen de todas las configuraciones"""
        try:
            current_user_rol = request.current_user.get('rol')
            current_user_id = request.current_user.get('id')
            centro_id = request.current_user.get('id_centro')
            
            if not centro_id:
                return response_error("Usuario sin centro asignado", 403)
            
            component = ConfiguracionComponent()
            resumen = {}
            
            # Configuración general (todos pueden ver su centro)
            general_result = component.get_configuracion_general(centro_id)
            if general_result['success']:
                resumen['general'] = general_result['data']
            
            # Configuración de sesiones (todos pueden ver)
            sesiones_result = component.get_configuracion_sesiones()
            if sesiones_result['success']:
                resumen['sesiones'] = sesiones_result['data']
            
            # Configuración de notificaciones (usuario actual)
            notif_result = component.get_configuracion_notificaciones(current_user_id)
            if notif_result['success']:
                resumen['notificaciones_usuario'] = notif_result['data']
            
            # Configuración de notificaciones globales (solo admin)
            if current_user_rol == 'Administrador':
                notif_global_result = component.get_configuracion_notificaciones()
                if notif_global_result['success']:
                    resumen['notificaciones_global'] = notif_global_result['data']
                
                # Configuración de seguridad (solo admin)
                seguridad_result = component.get_configuracion_seguridad()
                if seguridad_result['success']:
                    resumen['seguridad'] = seguridad_result['data']
            
            return response_success(resumen, "Resumen de configuración obtenido exitosamente")
                
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.get_resumen_configuracion: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @staticmethod
    def get_resumen_configuracion_para_validacion(centro_id):
        """Obtener configuración específica para validaciones internas (sin JWT)"""
        try:
            HandleLogs.write_log(f"ConfiguracionService.get_resumen_configuracion_para_validacion - Iniciando para centro {centro_id}")
            
            component = ConfiguracionComponent()
            
            # Obtener configuración general (específica por centro)
            config_general_result = component.get_configuracion_general(centro_id)
            config_general = config_general_result.get('data') if config_general_result.get('success') else None
            
            # Obtener configuración de sesiones (global)
            config_sesiones_result = component.get_configuracion_sesiones()
            config_sesiones = config_sesiones_result.get('data') if config_sesiones_result.get('success') else None
            
            # Obtener configuración de seguridad (global)  
            config_seguridad_result = component.get_configuracion_seguridad()
            config_seguridad = config_seguridad_result.get('data') if config_seguridad_result.get('success') else None
            
            # Obtener configuración de notificaciones globales
            config_notif_global_result = component.get_configuracion_notificaciones()
            config_notif_global = config_notif_global_result.get('data') if config_notif_global_result.get('success') else None
            
            resumen = {
                'general': config_general,
                'sesiones': config_sesiones,
                'seguridad': config_seguridad, 
                'notificaciones_global': config_notif_global
            }
            
            HandleLogs.write_log("ConfiguracionService.get_resumen_configuracion_para_validacion - Resumen obtenido exitosamente")
            return internal_response(success=True, data=resumen, message="Configuración para validación obtenida exitosamente")
            
        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.get_resumen_configuracion_para_validacion: {str(e)}")
            return internal_response(success=False, message=f"Error interno del servidor: {str(e)}")
    
    # ============================================
    # MÉTODOS DE VALIDACIÓN PRIVADOS
    # ============================================
    
    @staticmethod
    def _validate_email(email):
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def _validate_phone(phone):
        """Validar formato de teléfono"""
        # Permitir números, espacios, guiones y paréntesis
        pattern = r'^[\d\s\-\(\)\+]{7,20}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def _validate_time_range(start_time, end_time):
        """Validar que el tiempo de inicio sea anterior al tiempo de fin"""
        try:
            # Convertir strings de tiempo a objetos datetime para comparar
            from datetime import datetime
            
            # Formatear strings de tiempo si es necesario
            if isinstance(start_time, str):
                if len(start_time) == 5:  # HH:MM
                    start_time += ":00"
            if isinstance(end_time, str):
                if len(end_time) == 5:  # HH:MM
                    end_time += ":00"
            
            start = datetime.strptime(str(start_time), "%H:%M:%S").time()
            end = datetime.strptime(str(end_time), "%H:%M:%S").time()
            
            return start < end
        except:
            return False
    
    # ============================================
    # MÉTODOS DE MAPEO DE DATOS
    # ============================================
    
    @staticmethod
    def _map_frontend_to_backend_general(frontend_data):
        """Mapear datos del frontend (camelCase) al backend (snake_case) para configuración general"""
        return {
            'nombre_centro': frontend_data.get('nombreCentro'),
            'direccion': frontend_data.get('direccion'),
            'telefono': frontend_data.get('telefono'),
            'email': frontend_data.get('email'),
            'logo_url': frontend_data.get('logoUrl'),
            'horario_inicio': frontend_data.get('horarioInicio'),
            'horario_fin': frontend_data.get('horarioFin'),
            'zona_horaria': frontend_data.get('zonaHoraria'),
            'formato_fecha': frontend_data.get('formatoFecha'),
            'formato_hora': frontend_data.get('formatoHora'),
            'moneda': frontend_data.get('moneda'),
            'idioma': frontend_data.get('idioma'),
            'descripcion': frontend_data.get('descripcion')
        }
    
    @staticmethod
    def _map_frontend_to_backend_sesiones(frontend_data):
        """Mapear datos del frontend (camelCase) al backend (snake_case) para configuración de sesiones"""
        return {
            'duracion_sesion_terapia': frontend_data.get('duracionSesionTerapia'),
            'duracion_clase_pedagogica': frontend_data.get('duracionClasePedagogica'),
            'tolerancia_llegada_tarde': frontend_data.get('toleranciaLlegadaTarde'),
            'tiempo_recordatorio': frontend_data.get('tiempoRecordatorio'),
            'permitir_cancelacion_horas': frontend_data.get('permitirCancelacionHoras'),
            'permitir_reprogramacion_horas': frontend_data.get('permitirReprogramacionHoras'),
            'capacidad_maxima_clase': frontend_data.get('capacidadMaximaClase'),
            'sistema_calificaciones': frontend_data.get('sistemaCalificaciones'),
            'escala_calificacion_min': frontend_data.get('escalaCalificacionMin'),
            'escala_calificacion_max': frontend_data.get('escalaCalificacionMax')
        }