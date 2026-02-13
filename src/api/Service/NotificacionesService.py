# =============================================
# CENTRO TIA GLENDA - SERVICIO DE NOTIFICACIONES PUSH
# Archivo: NotificacionesService.py
# Descripcion: Logica de negocio para notificaciones automaticas
# =============================================

from src.api.Components.NotificacionesComponent import NotificacionesComponent
from src.utils.general.HandleLogs import HandleLogs
from datetime import datetime

class NotificacionesService:
    """Servicio para gestion de notificaciones push"""

    @staticmethod
    def obtener_notificaciones_usuario(usuario_autenticado, incluir_leidas=False, limite=50):
        """
        Obtener notificaciones para el usuario autenticado
        """
        try:
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
        Marcar una notificacion como leida
        """
        try:
            if not isinstance(id_notificacion, int) or id_notificacion <= 0:
                return {'success': False, 'message': 'ID de notificacion invalido'}

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
    def marcar_todas_leidas(usuario_autenticado):
        """
        Marcar todas las notificaciones como leidas
        """
        try:
            component = NotificacionesComponent()
            success, resultado = component.marcar_todas_leidas(usuario_autenticado['id'])

            if success:
                return {
                    'success': True,
                    'message': f'{resultado} notificaciones marcadas como leidas',
                    'total_marcadas': resultado
                }
            else:
                return {'success': False, 'message': resultado}

        except Exception as e:
            HandleLogs.write_error(f"Error en marcar_todas_leidas: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def eliminar_notificacion(id_notificacion, usuario_autenticado):
        """
        Eliminar una notificacion del usuario
        """
        try:
            if not isinstance(id_notificacion, int) or id_notificacion <= 0:
                return {'success': False, 'message': 'ID de notificacion invalido'}

            component = NotificacionesComponent()
            success, mensaje = component.eliminar_notificacion(
                id_notificacion, usuario_autenticado['id']
            )

            if success:
                return {'success': True, 'message': mensaje}
            else:
                return {'success': False, 'message': mensaje}

        except Exception as e:
            HandleLogs.write_error(f"Error en eliminar_notificacion: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def contar_no_leidas(usuario_autenticado):
        """
        Contar notificaciones no leidas (para badge)
        """
        try:
            component = NotificacionesComponent()
            success, resultado = component.contar_no_leidas(usuario_autenticado['id'])

            if success:
                return {
                    'success': True,
                    'no_leidas': resultado
                }
            else:
                return {'success': False, 'message': resultado}

        except Exception as e:
            HandleLogs.write_error(f"Error en contar_no_leidas: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def obtener_estadisticas_notificaciones(usuario_autenticado):
        """
        Obtener estadisticas de notificaciones para el usuario
        """
        try:
            component = NotificacionesComponent()
            success, resultado = component.obtener_estadisticas_usuario(usuario_autenticado['id'])

            if success:
                return {'success': True, 'estadisticas': resultado}
            else:
                return {'success': False, 'message': resultado}

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_estadisticas_notificaciones: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def validar_permisos_notificaciones(usuario_autenticado):
        """
        Validar que el usuario tiene permisos para gestionar notificaciones
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
    """Servicio para el job scheduler de notificaciones automaticas"""

    @staticmethod
    def procesar_notificaciones_pendientes():
        """
        Procesar todas las notificaciones pendientes
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
                            "Error al enviar notificacion push"
                        )
                        fallidas += 1

                except Exception as e:
                    component.marcar_notificacion_fallida(
                        notif['id'],
                        f"Error en procesamiento: {str(e)}"
                    )
                    fallidas += 1
                    HandleLogs.write_error(f"Error procesando notificacion {notif['id']}: {str(e)}")

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
        Enviar notificacion push (simulado).
        En una implementacion real, aqui se integraria con:
        - Firebase Cloud Messaging (FCM)
        - Apple Push Notification Service (APNS)
        - Web Push API
        - Servicios de email como backup

        Returns:
            bool: True si el envio fue exitoso
        """
        try:
            # Simulacion: marcar siempre como exitoso
            # En produccion, implementar llamadas a servicios reales
            HandleLogs.write_log(
                f"NOTIFICACION ENVIADA [SIMULADO] - "
                f"Usuario: {notificacion['id_usuario']}, "
                f"Tipo: {notificacion['tipo_notificacion']}, "
                f"Titulo: {notificacion['titulo']}"
            )

            return True

        except Exception as e:
            HandleLogs.write_error(f"Error enviando notificacion push: {str(e)}")
            return False

    @staticmethod
    def limpiar_notificaciones_expiradas():
        """
        Limpiar notificaciones expiradas
        """
        try:
            component = NotificacionesComponent()
            success, count = component.limpiar_notificaciones_expiradas()

            if success:
                if count and count > 0:
                    HandleLogs.write_log(f"Limpieza completada: {count} notificaciones expiradas eliminadas")

                return {
                    'success': True,
                    'eliminadas': count if count else 0,
                    'message': f'{count if count else 0} notificaciones expiradas eliminadas'
                }
            else:
                return {'success': False, 'message': count}

        except Exception as e:
            HandleLogs.write_error(f"Error en limpiar_notificaciones_expiradas: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}

    @staticmethod
    def generar_notificaciones_sesiones():
        """
        Generar notificaciones automaticas para sesiones proximas.
        Esta funcion debe ser llamada periodicamente para revisar cronogramas.
        """
        try:
            component_notif = NotificacionesComponent()

            # Obtener configuracion
            success_config, config = component_notif.obtener_configuracion_notificaciones()
            if not success_config:
                return {'success': False, 'message': 'Error obteniendo configuracion'}

            notificaciones_creadas = 0

            # Generar notificaciones para sesiones terapeuticas
            if config.get('notificar_sesiones_terapia'):
                try:
                    sesiones_proximas = NotificacionesJobService._obtener_sesiones_terapia_proximas(
                        config.get('minutos_previos_sesion_terapia', 15)
                    )

                    for sesion in sesiones_proximas:
                        success, _ = component_notif.crear_notificacion_sesion_terapia(sesion)
                        if success:
                            notificaciones_creadas += 1

                except Exception as e:
                    HandleLogs.write_error(f"Error generando notificaciones de sesiones terapeuticas: {str(e)}")

            # Generar notificaciones para clases pedagogicas
            if config.get('notificar_clases_pedagogicas'):
                try:
                    clases_proximas = NotificacionesJobService._obtener_clases_pedagogicas_proximas(
                        config.get('minutos_previos_clase_pedagogica', 15)
                    )

                    for clase in clases_proximas:
                        success, _ = component_notif.crear_notificacion_clase_pedagogica(clase)
                        if success:
                            notificaciones_creadas += 1

                except Exception as e:
                    HandleLogs.write_error(f"Error generando notificaciones de clases pedagogicas: {str(e)}")

            if notificaciones_creadas > 0:
                HandleLogs.write_log(f"Generadas {notificaciones_creadas} notificaciones automaticas")

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
        Obtener sesiones de terapia que necesitan notificacion.
        TODO: Implementar consulta real al cronograma de sesiones.
        """
        try:
            return []

        except Exception as e:
            HandleLogs.write_error(f"Error obteniendo sesiones terapeuticas proximas: {str(e)}")
            return []

    @staticmethod
    def _obtener_clases_pedagogicas_proximas(minutos_previos):
        """
        Obtener clases pedagogicas que necesitan notificacion.
        TODO: Implementar consulta real al cronograma de clases.
        """
        try:
            return []

        except Exception as e:
            HandleLogs.write_error(f"Error obteniendo clases pedagogicas proximas: {str(e)}")
            return []
