# src/api/Service/DashboardService.py
from src.api.Components.DashboardComponent import DashboardComponent
import logging

class DashboardService:
    def __init__(self):
        self.dashboard_component = DashboardComponent()
        self.logger = logging.getLogger(__name__)

    def get_estadisticas_generales(self):
        """
        Obtiene estadísticas generales del dashboard
        """
        try:
            return self.dashboard_component.get_estadisticas_generales()
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_estadisticas_generales: {e}")
            raise

    def get_usuarios_activos(self):
        """
        Obtiene el conteo de usuarios activos
        """
        try:
            stats = self.dashboard_component.get_estadisticas_generales()
            return {'usuarios_activos': stats['usuarios_activos']}
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_usuarios_activos: {e}")
            raise

    def get_contador_pacientes(self):
        """
        Obtiene el conteo total de pacientes
        """
        try:
            stats = self.dashboard_component.get_estadisticas_generales()
            return {'total_pacientes': stats['total_pacientes']}
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_contador_pacientes: {e}")
            raise

    def get_resumen_personal(self):
        """
        Obtiene resumen del personal (terapeutas, pedagogos, especialidades)
        """
        try:
            stats = self.dashboard_component.get_estadisticas_generales()
            return {
                'terapeutas': stats['terapeutas'],
                'pedagogos': stats['pedagogos'],
                'especialidades': stats['especialidades']
            }
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_resumen_personal: {e}")
            raise

    def get_sesiones_hoy(self):
        """
        Obtiene estadísticas de sesiones programadas para hoy
        """
        try:
            return self.dashboard_component.get_sesiones_hoy()
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_sesiones_hoy: {e}")
            raise

    def get_actividad_reciente(self, limite=10):
        """
        Obtiene la actividad reciente del sistema
        """
        try:
            return self.dashboard_component.get_actividad_reciente(limite)
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_actividad_reciente: {e}")
            raise

    def get_alertas_sistema(self):
        """
        Obtiene alertas del sistema
        """
        try:
            return self.dashboard_component.get_alertas_sistema()
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_alertas_sistema: {e}")
            raise

    def get_metricas_asistencia(self):
        """
        Obtiene métricas de asistencia general
        """
        try:
            return self.dashboard_component.get_metricas_asistencia()
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_metricas_asistencia: {e}")
            raise

    def get_rendimiento_semanal(self):
        """
        Obtiene datos de rendimiento semanal
        """
        try:
            return self.dashboard_component.get_rendimiento_semanal()
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_rendimiento_semanal: {e}")
            raise

    def get_todas_estadisticas(self):
        """
        Obtiene todas las estadísticas del dashboard en una sola llamada
        """
        try:
            estadisticas_generales = self.get_estadisticas_generales()
            sesiones_hoy = self.get_sesiones_hoy()
            actividad_reciente = self.get_actividad_reciente(5)
            alertas = self.get_alertas_sistema()
            metricas_asistencia = self.get_metricas_asistencia()
            rendimiento_semanal = self.get_rendimiento_semanal()

            return {
                **estadisticas_generales,
                'sesiones_hoy': sesiones_hoy['total'],
                'sesiones_terapeuticas_hoy': sesiones_hoy['sesiones_terapeuticas'],
                'sesiones_pedagogicas_hoy': sesiones_hoy['sesiones_pedagogicas'],
                'actividad_reciente': actividad_reciente,
                'alertas_sistema': alertas,
                'asistencia_promedio': metricas_asistencia['promedio'],
                'rendimiento_semanal': rendimiento_semanal
            }
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_todas_estadisticas: {e}")
            raise

    def get_mis_sesiones_hoy(self, id_personal):
        """
        Obtiene las sesiones de hoy para un terapeuta específico
        """
        try:
            return self.dashboard_component.get_mis_sesiones_hoy(id_personal)
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_mis_sesiones_hoy: {e}")
            raise

    def get_mis_clases_hoy(self, id_personal):
        """
        Obtiene las clases de hoy para un pedagogo específico
        """
        try:
            return self.dashboard_component.get_mis_clases_hoy(id_personal)
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_mis_clases_hoy: {e}")
            raise

    def get_mis_pacientes(self, id_personal):
        """
        Obtiene los pacientes asignados a un terapeuta
        """
        try:
            return self.dashboard_component.get_mis_pacientes(id_personal)
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_mis_pacientes: {e}")
            raise

    def get_mis_estudiantes(self, id_personal):
        """
        Obtiene los estudiantes de las clases de un pedagogo
        """
        try:
            return self.dashboard_component.get_mis_estudiantes(id_personal)
        except Exception as e:
            self.logger.error(f"Error en DashboardService.get_mis_estudiantes: {e}")
            raise