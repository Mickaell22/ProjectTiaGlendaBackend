# =============================================
# CENTRO TÍA GLENDA - JOB SCHEDULER PARA NOTIFICACIONES
# Archivo: NotificationScheduler.py
# Descripción: Sistema de tareas programadas para notificaciones automáticas
# =============================================

import threading
import time
import schedule
from datetime import datetime
from src.api.Service.NotificacionesService import NotificacionesJobService
from src.utils.general.HandleLogs import HandleLogs

class NotificationScheduler:
    """Sistema de tareas programadas para notificaciones automáticas"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.jobs_activos = []
        
    def iniciar_scheduler(self):
        """
        Iniciar el sistema de tareas programadas
        """
        try:
            if self.running:
                HandleLogs.write_log("Scheduler de notificaciones ya está ejecutándose")
                return True
            
            # Configurar trabajos programados
            self._configurar_jobs()
            
            # Iniciar thread del scheduler
            self.running = True
            self.thread = threading.Thread(target=self._ejecutar_scheduler, daemon=True)
            self.thread.start()
            
            HandleLogs.write_log("Scheduler de notificaciones iniciado exitosamente")
            return True
            
        except Exception as e:
            HandleLogs.write_error(f"Error iniciando scheduler de notificaciones: {str(e)}")
            return False
    
    def detener_scheduler(self):
        """
        Detener el sistema de tareas programadas
        """
        try:
            if not self.running:
                HandleLogs.write_log("Scheduler de notificaciones ya está detenido")
                return True
            
            self.running = False
            
            # Limpiar trabajos programados
            schedule.clear()
            self.jobs_activos.clear()
            
            # Esperar a que termine el thread
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5)
            
            HandleLogs.write_log("Scheduler de notificaciones detenido exitosamente")
            return True
            
        except Exception as e:
            HandleLogs.write_error(f"Error deteniendo scheduler de notificaciones: {str(e)}")
            return False
    
    def _configurar_jobs(self):
        """
        Configurar todos los trabajos programados
        """
        try:
            # Job 1: Procesar notificaciones pendientes (cada minuto)
            job1 = schedule.every(1).minutes.do(self._job_procesar_notificaciones)
            self.jobs_activos.append({
                'job': job1,
                'descripcion': 'Procesar notificaciones pendientes',
                'frecuencia': 'cada 1 minuto'
            })
            
            # Job 2: Generar notificaciones de sesiones (cada 5 minutos)
            job2 = schedule.every(5).minutes.do(self._job_generar_notificaciones_sesiones)
            self.jobs_activos.append({
                'job': job2,
                'descripcion': 'Generar notificaciones de sesiones',
                'frecuencia': 'cada 5 minutos'
            })
            
            # Job 3: Limpiar notificaciones expiradas (cada hora)
            job3 = schedule.every(1).hours.do(self._job_limpiar_notificaciones_expiradas)
            self.jobs_activos.append({
                'job': job3,
                'descripcion': 'Limpiar notificaciones expiradas',
                'frecuencia': 'cada 1 hora'
            })
            
            # Job 4: Estadísticas y mantenimiento (cada día a las 2:00 AM)
            job4 = schedule.every().day.at("02:00").do(self._job_mantenimiento_diario)
            self.jobs_activos.append({
                'job': job4,
                'descripcion': 'Mantenimiento diario del sistema',
                'frecuencia': 'diario a las 2:00 AM'
            })
            
            HandleLogs.write_log(f"Configurados {len(self.jobs_activos)} trabajos programados")
            
        except Exception as e:
            HandleLogs.write_error(f"Error configurando jobs del scheduler: {str(e)}")
            raise
    
    def _ejecutar_scheduler(self):
        """
        Bucle principal del scheduler (ejecuta en thread separado)
        """
        HandleLogs.write_log("Iniciando bucle principal del scheduler de notificaciones")
        
        while self.running:
            try:
                # Ejecutar trabajos programados
                schedule.run_pending()
                
                # Esperar 30 segundos antes de la próxima verificación
                time.sleep(30)
                
            except Exception as e:
                HandleLogs.write_error(f"Error en bucle principal del scheduler: {str(e)}")
                # Esperar más tiempo en caso de error para evitar bucle infinito
                time.sleep(60)
        
        HandleLogs.write_log("Bucle principal del scheduler terminado")
    
    def _job_procesar_notificaciones(self):
        """
        Job: Procesar notificaciones pendientes
        """
        try:
            resultado = NotificacionesJobService.procesar_notificaciones_pendientes()
            
            if resultado['success']:
                if resultado.get('procesadas', 0) > 0:
                    HandleLogs.write_log(
                        f"Job notificaciones: {resultado['procesadas']} procesadas, "
                        f"{resultado.get('fallidas', 0)} fallidas"
                    )
            else:
                HandleLogs.write_error(f"Error en job procesar notificaciones: {resultado['message']}")
                
        except Exception as e:
            HandleLogs.write_error(f"Error ejecutando job procesar_notificaciones: {str(e)}")
    
    def _job_generar_notificaciones_sesiones(self):
        """
        Job: Generar notificaciones automáticas para sesiones próximas
        """
        try:
            resultado = NotificacionesJobService.generar_notificaciones_sesiones()
            
            if resultado['success']:
                if resultado.get('notificaciones_creadas', 0) > 0:
                    HandleLogs.write_log(
                        f"Job generación: {resultado['notificaciones_creadas']} notificaciones creadas"
                    )
            else:
                HandleLogs.write_error(f"Error en job generar notificaciones: {resultado['message']}")
                
        except Exception as e:
            HandleLogs.write_error(f"Error ejecutando job generar_notificaciones_sesiones: {str(e)}")
    
    def _job_limpiar_notificaciones_expiradas(self):
        """
        Job: Limpiar notificaciones expiradas
        """
        try:
            resultado = NotificacionesJobService.limpiar_notificaciones_expiradas()
            
            if resultado['success']:
                if resultado.get('eliminadas', 0) > 0:
                    HandleLogs.write_log(
                        f"Job limpieza: {resultado['eliminadas']} notificaciones expiradas eliminadas"
                    )
            else:
                HandleLogs.write_error(f"Error en job limpiar notificaciones: {resultado['message']}")
                
        except Exception as e:
            HandleLogs.write_error(f"Error ejecutando job limpiar_notificaciones_expiradas: {str(e)}")
    
    def _job_mantenimiento_diario(self):
        """
        Job: Mantenimiento diario del sistema de notificaciones
        """
        try:
            HandleLogs.write_log("Iniciando mantenimiento diario del sistema de notificaciones")
            
            # 1. Limpiar notificaciones expiradas
            resultado_limpieza = NotificacionesJobService.limpiar_notificaciones_expiradas()
            
            # 2. Generar reporte de estadísticas (opcional)
            estadisticas = {
                'fecha_mantenimiento': datetime.now().isoformat(),
                'notificaciones_eliminadas': resultado_limpieza.get('eliminadas', 0) if resultado_limpieza['success'] else 0
            }
            
            HandleLogs.write_log(f"Mantenimiento diario completado: {estadisticas}")
            
        except Exception as e:
            HandleLogs.write_error(f"Error ejecutando job mantenimiento_diario: {str(e)}")
    
    def obtener_estado_scheduler(self):
        """
        Obtener estado actual del scheduler
        
        Returns:
            dict: Estado del scheduler
        """
        try:
            return {
                'activo': self.running,
                'jobs_configurados': len(self.jobs_activos),
                'jobs_activos': [
                    {
                        'descripcion': job['descripcion'],
                        'frecuencia': job['frecuencia'],
                        'proximo_ejecucion': str(job['job'].next_run) if job['job'].next_run else 'No programado'
                    }
                    for job in self.jobs_activos
                ],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            HandleLogs.write_error(f"Error obteniendo estado del scheduler: {str(e)}")
            return {
                'activo': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def ejecutar_job_manual(self, nombre_job):
        """
        Ejecutar un job específico manualmente
        
        Args:
            nombre_job (str): Nombre del job a ejecutar
            
        Returns:
            dict: Resultado de la ejecución
        """
        try:
            jobs_disponibles = {
                'procesar_notificaciones': self._job_procesar_notificaciones,
                'generar_notificaciones_sesiones': self._job_generar_notificaciones_sesiones,
                'limpiar_notificaciones_expiradas': self._job_limpiar_notificaciones_expiradas,
                'mantenimiento_diario': self._job_mantenimiento_diario
            }
            
            if nombre_job not in jobs_disponibles:
                return {
                    'success': False,
                    'message': f'Job no encontrado: {nombre_job}',
                    'jobs_disponibles': list(jobs_disponibles.keys())
                }
            
            HandleLogs.write_log(f"Ejecutando job manual: {nombre_job}")
            
            # Ejecutar el job
            jobs_disponibles[nombre_job]()
            
            return {
                'success': True,
                'message': f'Job {nombre_job} ejecutado exitosamente',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            HandleLogs.write_error(f"Error ejecutando job manual {nombre_job}: {str(e)}")
            return {
                'success': False,
                'message': f'Error ejecutando job: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }


# Instancia global del scheduler
_notification_scheduler = None

def obtener_scheduler():
    """
    Obtener la instancia global del scheduler (singleton)
    
    Returns:
        NotificationScheduler: Instancia del scheduler
    """
    global _notification_scheduler
    
    if _notification_scheduler is None:
        _notification_scheduler = NotificationScheduler()
    
    return _notification_scheduler

def iniciar_scheduler_global():
    """
    Iniciar el scheduler global de notificaciones
    
    Returns:
        bool: True si se inició exitosamente
    """
    try:
        scheduler = obtener_scheduler()
        return scheduler.iniciar_scheduler()
        
    except Exception as e:
        HandleLogs.write_error(f"Error iniciando scheduler global: {str(e)}")
        return False

def detener_scheduler_global():
    """
    Detener el scheduler global de notificaciones
    
    Returns:
        bool: True si se detuvo exitosamente
    """
    try:
        scheduler = obtener_scheduler()
        return scheduler.detener_scheduler()
        
    except Exception as e:
        HandleLogs.write_error(f"Error deteniendo scheduler global: {str(e)}")
        return False