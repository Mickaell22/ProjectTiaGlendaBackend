# =============================================
# CENTRO TÍA GLENDA - SERVICIO DE NOTIFICACIONES PUSH
# Archivo: NotificacionesService.py
# Descripción: Lógica de negocio para notificaciones automáticas
# =============================================

from src.api.Components.NotificacionesComponent import NotificacionesComponent
from src.utils.general.HandleLogs import HandleLogs
import json
from datetime import datetime

class NotificacionesService:
    """Servicio para gestión de notificaciones push"""
    
    @staticmethod
    def obtener_notificaciones_usuario(usuario_autenticado, incluir_leidas=False, limite=50):
        """
        Obtener notificaciones para el usuario autenticado
        
        Args:
            usuario_autenticado (dict): Información del usuario
            incluir_leidas (bool): Si incluir notificaciones leídas
            limite (int): Cantidad máxima de notificaciones
            
        Returns:
            dict: Resultado con notificaciones
        """
        try:
            # Validar parámetros
            if not isinstance(limite, int) or limite <= 0 or limite > 100:
                limite = 50
            
            component = NotificacionesComponent()
            success, resultado = component.obtener_notificaciones_usuario(
                usuario_autenticado['id'], incluir_leidas, limite
            )
            
            if success:
                return {
                    'success': True,
                    'notificaciones': resultado,
                    'total': len(resultado)
                }
            else:
                return {'success': False, 'message': resultado}
                
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_notificaciones_usuario: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def marcar_notificacion_leida(id_notificacion, usuario_autenticado):
        """
        Marcar una notificación como leída
        
        Args:
            id_notificacion (int): ID de la notificación
            usuario_autenticado (dict): Información del usuario
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validar parámetros
            if not isinstance(id_notificacion, int) or id_notificacion <= 0:
                return {'success': False, 'message': 'ID de notificación inválido'}
            
            component = NotificacionesComponent()
            success, mensaje = component.marcar_notificacion_leida(
                id_notificacion, usuario_autenticado['id']
            )
            
            if success:
                return {'success': True, 'message': mensaje}
            else:
                return {'success': False, 'message': mensaje}
                
        except Exception as e:
            HandleLogs.write_error(f"Error en marcar_notificacion_leida: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def obtener_estadisticas_notificaciones(usuario_autenticado):
        """
        Obtener estadísticas de notificaciones para el usuario
        
        Args:
            usuario_autenticado (dict): Información del usuario
            
        Returns:
            dict: Estadísticas de notificaciones
        """
        try:
            component = NotificacionesComponent()
            
            # Obtener notificaciones no leídas
            success_no_leidas, notificaciones_no_leidas = component.obtener_notificaciones_usuario(
                usuario_autenticado['id'], incluir_leidas=False, limite=1000
            )
            
            # Obtener todas las notificaciones
            success_todas, todas_notificaciones = component.obtener_notificaciones_usuario(
                usuario_autenticado['id'], incluir_leidas=True, limite=1000
            )
            
            if success_no_leidas and success_todas:
                # Contar por tipo
                conteos_tipo = {}
                conteos_prioridad = {}
                
                for notif in todas_notificaciones:
                    tipo = notif.get('tipo_notificacion', 'desconocido')
                    prioridad = notif.get('prioridad', 'normal')
                    
                    conteos_tipo[tipo] = conteos_tipo.get(tipo, 0) + 1
                    conteos_prioridad[prioridad] = conteos_prioridad.get(prioridad, 0) + 1
                
                estadisticas = {
                    'total_notificaciones': len(todas_notificaciones),
                    'notificaciones_no_leidas': len(notificaciones_no_leidas),
                    'notificaciones_leidas': len(todas_notificaciones) - len(notificaciones_no_leidas),
                    'por_tipo': conteos_tipo,
                    'por_prioridad': conteos_prioridad
                }
                
                return {'success': True, 'estadisticas': estadisticas}
            else:
                error_msg = notificaciones_no_leidas if not success_no_leidas else todas_notificaciones
                return {'success': False, 'message': error_msg}
                
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_estadisticas_notificaciones: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def validar_permisos_notificaciones(usuario_autenticado):
        """
        Validar que el usuario tiene permisos para gestionar notificaciones
        
        Args:
            usuario_autenticado (dict): Información del usuario
            
        Returns:
            dict: Resultado de la validación
        """
        try:
            if not usuario_autenticado:
                return {'success': False, 'message': 'Usuario no autenticado'}
            
            if usuario_autenticado.get('estado') != 'activo':
                return {'success': False, 'message': 'Usuario inactivo'}
            
            return {'success': True, 'message': 'Permisos validados'}
            
        except Exception as e:
            HandleLogs.write_error(f"Error en validar_permisos_notificaciones: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}


class NotificacionesJobService:
    """Servicio para el job scheduler de notificaciones automáticas"""
    
    @staticmethod
    def procesar_notificaciones_pendientes():
        """
        Procesar todas las notificaciones pendientes
        
        Returns:
            dict: Resultado del procesamiento
        """
        try:
            component = NotificacionesComponent()
            
            # Verificar si estamos en horario de silencio
            success_silencio, es_horario_silencio = component.verificar_horario_silencio()
            if success_silencio and es_horario_silencio:
                HandleLogs.write_log("Procesamiento de notificaciones omitido: horario de silencio")
                return {
                    'success': True, 
                    'procesadas': 0, 
                    'message': 'Horario de silencio activo'
                }
            
            # Obtener notificaciones pendientes
            success, notificaciones = component.obtener_notificaciones_pendientes()
            if not success:
                return {'success': False, 'message': notificaciones}
            
            if not notificaciones:
                return {'success': True, 'procesadas': 0, 'message': 'No hay notificaciones pendientes'}
            
            procesadas = 0
            fallidas = 0
            
            for notif in notificaciones:
                try:
                    # Simular envío de notificación (aquí se integraría con servicio real de push)
                    exito_envio = NotificacionesJobService._enviar_notificacion_push(notif)
                    
                    if exito_envio:
                        success_marcado, _ = component.marcar_notificacion_enviada(notif['id'])
                        if success_marcado:
                            procesadas += 1
                        else:
                            fallidas += 1
                    else:
                        component.marcar_notificacion_fallida(
                            notif['id'], 
                            "Error al enviar notificación push"
                        )
                        fallidas += 1
                        
                except Exception as e:
                    component.marcar_notificacion_fallida(
                        notif['id'], 
                        f"Error en procesamiento: {str(e)}"
                    )
                    fallidas += 1
                    HandleLogs.write_error(f"Error procesando notificación {notif['id']}: {str(e)}")
            
            HandleLogs.write_log(f"Notificaciones procesadas: {procesadas}, fallidas: {fallidas}")
            
            return {
                'success': True,
                'procesadas': procesadas,
                'fallidas': fallidas,
                'total': len(notificaciones)
            }
            
        except Exception as e:
            HandleLogs.write_error(f"Error en procesar_notificaciones_pendientes: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def _enviar_notificacion_push(notificacion):
        """
        Enviar notificación push (simulado)
        En una implementación real, aquí se integraría con:
        - Firebase Cloud Messaging (FCM)
        - Apple Push Notification Service (APNS)
        - Web Push API
        - Servicios de email como backup
        
        Args:
            notificacion (dict): Datos de la notificación
            
        Returns:
            bool: True si el envío fue exitoso
        """
        try:
            # Por ahora, simular envío exitoso para testing
            # En producción, implementar llamadas a servicios reales
            
            HandleLogs.write_log(
                f"NOTIFICACIÓN ENVIADA [SIMULADO] - "
                f"Usuario: {notificacion['id_usuario']}, "
                f"Tipo: {notificacion['tipo_notificacion']}, "
                f"Título: {notificacion['titulo']}"
            )
            
            # Simular tasa de éxito del 95%
            import random
            return random.random() < 0.95
            
        except Exception as e:
            HandleLogs.write_error(f"Error enviando notificación push: {str(e)}")
            return False
    
    @staticmethod
    def limpiar_notificaciones_expiradas():
        """
        Limpiar notificaciones expiradas
        
        Returns:
            dict: Resultado de la limpieza
        """
        try:
            component = NotificacionesComponent()
            success, count = component.limpiar_notificaciones_expiradas()
            
            if success:
                if count > 0:
                    HandleLogs.write_log(f"Limpieza completada: {count} notificaciones expiradas eliminadas")
                
                return {
                    'success': True,
                    'eliminadas': count,
                    'message': f'{count} notificaciones expiradas eliminadas'
                }
            else:
                return {'success': False, 'message': count}
                
        except Exception as e:
            HandleLogs.write_error(f"Error en limpiar_notificaciones_expiradas: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def generar_notificaciones_sesiones():
        """
        Generar notificaciones automáticas para sesiones próximas
        Esta función debe ser llamada periódicamente para revisar cronogramas
        
        Returns:
            dict: Resultado de la generación
        """
        try:
            from src.api.Components.SesionTerapiaComponent import SesionTerapiaComponent
            from src.api.Components.SesionPedagogicaComponent import SesionPedagogicaComponent
            
            component_notif = NotificacionesComponent()
            component_terapia = SesionTerapiaComponent()
            component_pedagogica = SesionPedagogicaComponent()
            
            # Obtener configuración
            success_config, config = component_notif.obtener_configuracion_notificaciones()
            if not success_config:
                return {'success': False, 'message': 'Error obteniendo configuración'}
            
            notificaciones_creadas = 0
            
            # Generar notificaciones para sesiones terapéuticas
            if config.get('notificar_sesiones_terapia'):
                try:
                    # Obtener sesiones próximas (implementar lógica específica según cronograma)
                    sesiones_proximas = NotificacionesJobService._obtener_sesiones_terapia_proximas(
                        config.get('minutos_previos_sesion_terapia', 15)
                    )
                    
                    for sesion in sesiones_proximas:
                        success, _ = component_notif.crear_notificacion_sesion_terapia(sesion)
                        if success:
                            notificaciones_creadas += 1
                            
                except Exception as e:
                    HandleLogs.write_error(f"Error generando notificaciones de sesiones terapéuticas: {str(e)}")
            
            # Generar notificaciones para clases pedagógicas
            if config.get('notificar_clases_pedagogicas'):
                try:
                    # Obtener clases próximas (implementar lógica específica según cronograma)
                    clases_proximas = NotificacionesJobService._obtener_clases_pedagogicas_proximas(
                        config.get('minutos_previos_clase_pedagogica', 15)
                    )
                    
                    for clase in clases_proximas:
                        success, _ = component_notif.crear_notificacion_clase_pedagogica(clase)
                        if success:
                            notificaciones_creadas += 1
                            
                except Exception as e:
                    HandleLogs.write_error(f"Error generando notificaciones de clases pedagógicas: {str(e)}")
            
            if notificaciones_creadas > 0:
                HandleLogs.write_log(f"Generadas {notificaciones_creadas} notificaciones automáticas")
            
            return {
                'success': True,
                'notificaciones_creadas': notificaciones_creadas,
                'message': f'{notificaciones_creadas} notificaciones generadas'
            }
            
        except Exception as e:
            HandleLogs.write_error(f"Error en generar_notificaciones_sesiones: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def _obtener_sesiones_terapia_proximas(minutos_previos):
        """
        Obtener sesiones de terapia que necesitan notificación
        
        Args:
            minutos_previos (int): Minutos de anticipación
            
        Returns:
            list: Lista de sesiones próximas
        """
        try:
            # Esta función debe implementarse según la lógica específica del cronograma
            # Por ahora retorna lista vacía para evitar errores
            
            # TODO: Implementar consulta real al cronograma de sesiones
            # Ejemplo de lo que debería retornar:
            # [
            #     {
            #         'id': 123,
            #         'terapeuta_id': 456,
            #         'id_centro': 1,
            #         'fecha_inicio': '2025-01-15T10:00:00',
            #         'paciente_nombre': 'Juan Pérez',
            #         'consultorio': 'Consultorio 1'
            #     }
            # ]
            
            return []
            
        except Exception as e:
            HandleLogs.write_error(f"Error obteniendo sesiones terapéuticas próximas: {str(e)}")
            return []
    
    @staticmethod
    def _obtener_clases_pedagogicas_proximas(minutos_previos):
        """
        Obtener clases pedagógicas que necesitan notificación
        
        Args:
            minutos_previos (int): Minutos de anticipación
            
        Returns:
            list: Lista de clases próximas
        """
        try:
            # Esta función debe implementarse según la lógica específica del cronograma
            # Por ahora retorna lista vacía para evitar errores
            
            # TODO: Implementar consulta real al cronograma de clases
            # Ejemplo de lo que debería retornar:
            # [
            #     {
            #         'id': 789,
            #         'pedagogo_id': 101,
            #         'id_centro': 1,
            #         'fecha_inicio': '2025-01-15T14:00:00',
            #         'materia': 'Matemáticas',
            #         'aula': 'Aula 2'
            #     }
            # ]
            
            return []
            
        except Exception as e:
            HandleLogs.write_error(f"Error obteniendo clases pedagógicas próximas: {str(e)}")
            return []