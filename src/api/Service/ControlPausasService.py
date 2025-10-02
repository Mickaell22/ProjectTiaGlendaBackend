"""
ControlPausasService.py
Servicio para gestionar control automatico de pausas de pacientes
Autor: Sistema Centro Tia Glenda
Fecha: 2025-10-01
"""

from src.api.Components.ControlPausasComponent import ControlPausasComponent
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error


class ControlPausasService:
    """Servicio para control y procesamiento de pausas de pacientes"""

    @staticmethod
    def get_estado_pausas_paciente(paciente_id):
        """Obtener el estado completo de pausas de un paciente"""
        try:
            HandleLogs.write_log(f"ControlPausasService.get_estado_pausas_paciente - Paciente {paciente_id}")

            # Validar que paciente_id sea valido
            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            # Obtener estado de pausas
            result = ControlPausasComponent.get_estado_pausas_paciente(paciente_id)

            if result['success']:
                return response_success(result['data'], result['message'])
            else:
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasService.get_estado_pausas_paciente - Error: {str(e)}")
            return response_error(f"Error: {str(e)}", 500)

    @staticmethod
    def verificar_pausa_activa(paciente_id):
        """Verificar si un paciente tiene alguna pausa activa"""
        try:
            HandleLogs.write_log(f"ControlPausasService.verificar_pausa_activa - Paciente {paciente_id}")

            # Validar que paciente_id sea valido
            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            # Verificar pausa activa
            result = ControlPausasComponent.verificar_pausa_activa(paciente_id)

            if result['success']:
                return response_success(result['data'], result['message'])
            else:
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasService.verificar_pausa_activa - Error: {str(e)}")
            return response_error(f"Error: {str(e)}", 500)

    @staticmethod
    def get_historial_pausas(paciente_id):
        """Obtener historial completo de pausas de un paciente"""
        try:
            HandleLogs.write_log(f"ControlPausasService.get_historial_pausas - Paciente {paciente_id}")

            # Validar que paciente_id sea valido
            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            # Obtener historial
            result = ControlPausasComponent.get_historial_pausas(paciente_id)

            if result['success']:
                return response_success(result['data'], result['message'])
            else:
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasService.get_historial_pausas - Error: {str(e)}")
            return response_error(f"Error: {str(e)}", 500)

    @staticmethod
    def get_pausas_vencidas():
        """Obtener pausas que ya han vencido y deben reactivarse"""
        try:
            HandleLogs.write_log("ControlPausasService.get_pausas_vencidas - Iniciando")

            # Obtener pausas vencidas
            result = ControlPausasComponent.get_pausas_vencidas()

            if result['success']:
                return response_success(result['data'], result['message'])
            else:
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasService.get_pausas_vencidas - Error: {str(e)}")
            return response_error(f"Error: {str(e)}", 500)

    @staticmethod
    def get_pausas_proximas_vencer(dias=7):
        """Obtener pausas que estan proximas a vencer en los proximos N dias"""
        try:
            HandleLogs.write_log(f"ControlPausasService.get_pausas_proximas_vencer - Proximos {dias} dias")

            # Validar que dias sea un numero positivo
            if dias <= 0:
                dias = 7

            # Obtener pausas proximas a vencer
            result = ControlPausasComponent.get_pausas_proximas_vencer(dias)

            if result['success']:
                return response_success(result['data'], result['message'])
            else:
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasService.get_pausas_proximas_vencer - Error: {str(e)}")
            return response_error(f"Error: {str(e)}", 500)

    @staticmethod
    def procesar_pausas_automaticas():
        """Procesar automaticamente pausas vencidas y reactivar pacientes"""
        try:
            HandleLogs.write_log("ControlPausasService.procesar_pausas_automaticas - Iniciando")

            # Procesar pausas automaticas
            result = ControlPausasComponent.procesar_pausas_automaticas()

            if result['success']:
                return response_success(result['data'], result['message'])
            else:
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasService.procesar_pausas_automaticas - Error: {str(e)}")
            return response_error(f"Error: {str(e)}", 500)

    @staticmethod
    def get_estadisticas_pausas():
        """Obtener estadisticas generales de pausas en el sistema"""
        try:
            HandleLogs.write_log("ControlPausasService.get_estadisticas_pausas - Iniciando")

            # Obtener estadisticas
            result = ControlPausasComponent.get_estadisticas_pausas()

            if result['success']:
                return response_success(result['data'], result['message'])
            else:
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasService.get_estadisticas_pausas - Error: {str(e)}")
            return response_error(f"Error: {str(e)}", 500)
