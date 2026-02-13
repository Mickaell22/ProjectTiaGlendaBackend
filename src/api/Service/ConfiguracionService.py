# src/api/Service/ConfiguracionService.py
from src.api.Components.ConfiguracionComponent import ConfiguracionComponent
from src.utils.general.response import response_success, response_error, internal_response
from src.utils.general.logs import HandleLogs
from flask import request
import re

class ConfiguracionService:

    # ============================================
    # SERVICIOS DE CONFIGURACION GENERAL
    # ============================================

    @staticmethod
    def get_configuracion_general():
        """Obtener configuracion del centro del usuario actual"""
        try:
            centro_id = request.current_user.get('id_centro')
            if not centro_id:
                return response_error("Usuario sin centro asignado", 403)

            component = ConfiguracionComponent()
            result = component.get_configuracion_general(centro_id)

            if result['success']:
                return response_success(result['data'], "Configuracion del centro obtenida exitosamente")
            else:
                return response_error(result['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.get_configuracion_general: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @staticmethod
    def update_configuracion_general():
        """Actualizar configuracion del centro del usuario actual"""
        try:
            data = request.get_json()

            if not data:
                return response_error("Datos requeridos", 400)

            centro_id = request.current_user.get('id_centro')
            if not centro_id:
                return response_error("Usuario sin centro asignado", 403)

            # Validar campo requerido
            if not data.get('nombre_centro'):
                return response_error("Campo requerido: nombre_centro", 400)

            # Validar email si se proporciona
            if data.get('email') and not ConfiguracionService._validate_email(data['email']):
                return response_error("Formato de email invalido", 400)

            # Validar telefono si se proporciona
            if data.get('telefono') and not ConfiguracionService._validate_phone(data['telefono']):
                return response_error("Formato de telefono invalido", 400)

            # Validar horarios
            if data.get('horario_apertura') and data.get('horario_cierre'):
                if not ConfiguracionService._validate_time_range(data['horario_apertura'], data['horario_cierre']):
                    return response_error("El horario de apertura debe ser anterior al horario de cierre", 400)

            # Validar turno_principal
            if data.get('turno_principal'):
                turnos_validos = ['matutino', 'vespertino', 'mixto']
                if data['turno_principal'] not in turnos_validos:
                    return response_error(f"Turno principal debe ser uno de: {', '.join(turnos_validos)}", 400)

            usuario_id = request.current_user.get('id')
            component = ConfiguracionComponent()
            result = component.update_configuracion_general(data, centro_id, usuario_id)

            if result['success']:
                HandleLogs.write_log(f"Configuracion general actualizada por usuario: {request.current_user.get('usuario', 'unknown')}")
                return response_success(None, result['message'])
            else:
                return response_error(result['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.update_configuracion_general: {str(e)}")
            return response_error("Error interno del servidor", 500)

    # ============================================
    # SERVICIOS DE CONFIGURACION DE NOTIFICACIONES
    # ============================================

    @staticmethod
    def get_configuracion_notificaciones():
        """Obtener configuracion global de notificaciones"""
        try:
            component = ConfiguracionComponent()
            result = component.get_configuracion_notificaciones()

            if result['success']:
                return response_success(result['data'], "Configuracion de notificaciones obtenida exitosamente")
            else:
                return response_error(result['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.get_configuracion_notificaciones: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @staticmethod
    def update_configuracion_notificaciones():
        """Actualizar configuracion global de notificaciones"""
        try:
            data = request.get_json()

            if not data:
                return response_error("Datos requeridos", 400)

            # Validar campos booleanos
            boolean_fields = [
                'notificaciones_habilitadas', 'notificar_sesiones_terapia',
                'notificar_clases_pedagogicas', 'notificar_cancelaciones',
                'notificar_reprogramaciones', 'notificar_mensajes_chat',
                'notificar_solo_mensajes_urgentes'
            ]

            for field in boolean_fields:
                if field in data and not isinstance(data[field], bool):
                    return response_error(f"El campo {field} debe ser verdadero o falso", 400)

            # Validar campos numericos
            numeric_validations = {
                'minutos_previos_sesion_terapia': {'min': 1, 'max': 120, 'name': 'Minutos previos sesion terapia'},
                'minutos_previos_clase_pedagogica': {'min': 1, 'max': 120, 'name': 'Minutos previos clase pedagogica'},
                'intervalo_verificacion_minutos': {'min': 1, 'max': 60, 'name': 'Intervalo de verificacion'}
            }

            for field, validation in numeric_validations.items():
                if field in data and data[field] is not None:
                    value = data[field]
                    if not isinstance(value, int) or value < validation['min'] or value > validation['max']:
                        return response_error(
                            f"{validation['name']} debe estar entre {validation['min']} y {validation['max']}",
                            400
                        )

            # Validar horarios de silencio
            if data.get('horario_silencio_inicio'):
                if not ConfiguracionService._validate_time_format(data['horario_silencio_inicio']):
                    return response_error("Formato invalido para horario de silencio inicio (HH:MM o HH:MM:SS)", 400)

            if data.get('horario_silencio_fin'):
                if not ConfiguracionService._validate_time_format(data['horario_silencio_fin']):
                    return response_error("Formato invalido para horario de silencio fin (HH:MM o HH:MM:SS)", 400)

            usuario_id = request.current_user.get('id')
            component = ConfiguracionComponent()
            result = component.update_configuracion_notificaciones(data, usuario_id)

            if result['success']:
                HandleLogs.write_log(f"Configuracion de notificaciones actualizada por usuario: {request.current_user.get('usuario', 'unknown')}")
                return response_success(None, result['message'])
            else:
                return response_error(result['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.update_configuracion_notificaciones: {str(e)}")
            return response_error("Error interno del servidor", 500)

    # ============================================
    # RESUMEN DE CONFIGURACION
    # ============================================

    @staticmethod
    def get_resumen_configuracion():
        """Obtener resumen de configuraciones"""
        try:
            centro_id = request.current_user.get('id_centro')

            if not centro_id:
                return response_error("Usuario sin centro asignado", 403)

            component = ConfiguracionComponent()
            resumen = {}

            # Configuracion general del centro
            general_result = component.get_configuracion_general(centro_id)
            if general_result.get('success'):
                resumen['general'] = general_result['data']

            # Configuracion de notificaciones (global)
            notif_result = component.get_configuracion_notificaciones()
            if notif_result.get('success'):
                resumen['notificaciones'] = notif_result['data']

            return response_success(resumen, "Resumen de configuracion obtenido exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.get_resumen_configuracion: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @staticmethod
    def get_resumen_configuracion_para_validacion(centro_id):
        """Obtener configuracion para validaciones internas (sin JWT)"""
        try:
            component = ConfiguracionComponent()

            config_general_result = component.get_configuracion_general(centro_id)
            config_general = config_general_result.get('data') if config_general_result.get('success') else None

            config_notif_result = component.get_configuracion_notificaciones()
            config_notif = config_notif_result.get('data') if config_notif_result.get('success') else None

            resumen = {
                'general': config_general,
                'notificaciones': config_notif
            }

            return internal_response(success=True, data=resumen, message="Configuracion para validacion obtenida exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"Error en ConfiguracionService.get_resumen_configuracion_para_validacion: {str(e)}")
            return internal_response(success=False, message=f"Error interno del servidor: {str(e)}")

    # ============================================
    # METODOS DE VALIDACION PRIVADOS
    # ============================================

    @staticmethod
    def _validate_email(email):
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def _validate_phone(phone):
        """Validar formato de telefono"""
        pattern = r'^[\d\s\-\(\)\+]{7,20}$'
        return re.match(pattern, phone) is not None

    @staticmethod
    def _validate_time_format(time_str):
        """Validar formato de hora (HH:MM o HH:MM:SS)"""
        try:
            from datetime import datetime
            if isinstance(time_str, str):
                if len(time_str) == 5:
                    datetime.strptime(time_str, "%H:%M")
                    return True
                elif len(time_str) == 8:
                    datetime.strptime(time_str, "%H:%M:%S")
                    return True
            return False
        except ValueError:
            return False

    @staticmethod
    def _validate_time_range(start_time, end_time):
        """Validar que el tiempo de inicio sea anterior al tiempo de fin"""
        try:
            from datetime import datetime
            if isinstance(start_time, str):
                if len(start_time) == 5:
                    start_time += ":00"
            if isinstance(end_time, str):
                if len(end_time) == 5:
                    end_time += ":00"

            start = datetime.strptime(str(start_time), "%H:%M:%S").time()
            end = datetime.strptime(str(end_time), "%H:%M:%S").time()

            return start < end
        except (ValueError, TypeError):
            return False
