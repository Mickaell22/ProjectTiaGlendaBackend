# src/api/Components/ConfiguracionComponent.py
from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs

class ConfiguracionComponent:

    def __init__(self):
        self.db = DataBaseHandle()

    # ============================================
    # CONFIGURACION GENERAL (tabla: centros)
    # ============================================

    def get_configuracion_general(self, centro_id):
        """Obtener configuracion del centro especifico"""
        try:
            query = """
                SELECT
                    nombre as nombre_centro,
                    direccion,
                    telefono,
                    email,
                    horario_apertura,
                    horario_cierre,
                    turno_principal,
                    observaciones as descripcion,
                    codigo
                FROM centros
                WHERE id = %s
            """

            result = self.db.getRecords(query, (centro_id,))

            if result and len(result) > 0:
                config = result[0]
                return {
                    'success': True,
                    'data': {
                        'nombre_centro': config.get('nombre_centro'),
                        'codigo': config.get('codigo'),
                        'direccion': config.get('direccion'),
                        'telefono': config.get('telefono'),
                        'email': config.get('email'),
                        'horario_apertura': str(config.get('horario_apertura')) if config.get('horario_apertura') else '07:00:00',
                        'horario_cierre': str(config.get('horario_cierre')) if config.get('horario_cierre') else '18:00:00',
                        'turno_principal': config.get('turno_principal', 'mixto'),
                        'descripcion': config.get('descripcion') or '',
                        'zona_horaria': 'America/Guayaquil',
                        'formato_fecha': 'DD/MM/YYYY',
                        'formato_hora': '24h',
                        'moneda': 'USD',
                        'idioma': 'es'
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Centro no encontrado'
                }

        except Exception as e:
            HandleLogs.write_error(f"Error en get_configuracion_general: {str(e)}")
            return {
                'success': False,
                'message': f'Error obteniendo configuracion del centro: {str(e)}'
            }

    def update_configuracion_general(self, data, centro_id, usuario_id=None):
        """Actualizar configuracion del centro especifico"""
        try:
            query = """
                UPDATE centros SET
                    nombre = %s,
                    direccion = %s,
                    telefono = %s,
                    email = %s,
                    horario_apertura = %s,
                    horario_cierre = %s,
                    turno_principal = %s,
                    observaciones = %s,
                    usuario_modificacion = %s
                WHERE id = %s
            """

            params = (
                data.get('nombre_centro'),
                data.get('direccion'),
                data.get('telefono'),
                data.get('email'),
                data.get('horario_apertura'),
                data.get('horario_cierre'),
                data.get('turno_principal'),
                data.get('descripcion'),
                usuario_id,
                centro_id
            )

            result = self.db.ExecuteNonQuery(query, params)

            if result:
                return {
                    'success': True,
                    'message': 'Configuracion general actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error actualizando configuracion general'
                }

        except Exception as e:
            HandleLogs.write_error(f"Error en update_configuracion_general: {str(e)}")
            return {
                'success': False,
                'message': f'Error actualizando configuracion general: {str(e)}'
            }

    # ============================================
    # CONFIGURACION DE NOTIFICACIONES
    # (tabla: configuracion_notificaciones_push)
    # ============================================

    def get_configuracion_notificaciones(self):
        """Obtener configuracion global de notificaciones push"""
        try:
            query = """
                SELECT
                    notificaciones_habilitadas,
                    notificar_sesiones_terapia,
                    minutos_previos_sesion_terapia,
                    notificar_clases_pedagogicas,
                    minutos_previos_clase_pedagogica,
                    notificar_cancelaciones,
                    notificar_reprogramaciones,
                    notificar_mensajes_chat,
                    notificar_solo_mensajes_urgentes,
                    horario_silencio_inicio,
                    horario_silencio_fin,
                    intervalo_verificacion_minutos
                FROM configuracion_notificaciones_push
                WHERE id = 1
            """

            result = self.db.getRecords(query)

            if result and len(result) > 0:
                config = result[0]
                return {
                    'success': True,
                    'data': {
                        'notificaciones_habilitadas': config.get('notificaciones_habilitadas', True),
                        'notificar_sesiones_terapia': config.get('notificar_sesiones_terapia', True),
                        'minutos_previos_sesion_terapia': config.get('minutos_previos_sesion_terapia', 15),
                        'notificar_clases_pedagogicas': config.get('notificar_clases_pedagogicas', True),
                        'minutos_previos_clase_pedagogica': config.get('minutos_previos_clase_pedagogica', 15),
                        'notificar_cancelaciones': config.get('notificar_cancelaciones', True),
                        'notificar_reprogramaciones': config.get('notificar_reprogramaciones', True),
                        'notificar_mensajes_chat': config.get('notificar_mensajes_chat', True),
                        'notificar_solo_mensajes_urgentes': config.get('notificar_solo_mensajes_urgentes', False),
                        'horario_silencio_inicio': str(config.get('horario_silencio_inicio')) if config.get('horario_silencio_inicio') else '22:00:00',
                        'horario_silencio_fin': str(config.get('horario_silencio_fin')) if config.get('horario_silencio_fin') else '07:00:00',
                        'intervalo_verificacion_minutos': config.get('intervalo_verificacion_minutos', 1)
                    }
                }
            else:
                return {
                    'success': True,
                    'data': {
                        'notificaciones_habilitadas': True,
                        'notificar_sesiones_terapia': True,
                        'minutos_previos_sesion_terapia': 15,
                        'notificar_clases_pedagogicas': True,
                        'minutos_previos_clase_pedagogica': 15,
                        'notificar_cancelaciones': True,
                        'notificar_reprogramaciones': True,
                        'notificar_mensajes_chat': True,
                        'notificar_solo_mensajes_urgentes': False,
                        'horario_silencio_inicio': '22:00:00',
                        'horario_silencio_fin': '07:00:00',
                        'intervalo_verificacion_minutos': 1
                    }
                }

        except Exception as e:
            HandleLogs.write_error(f"Error en get_configuracion_notificaciones: {str(e)}")
            return {
                'success': False,
                'message': f'Error obteniendo configuracion de notificaciones: {str(e)}'
            }

    def update_configuracion_notificaciones(self, data, usuario_id=None):
        """Actualizar configuracion global de notificaciones push"""
        try:
            query = """
                UPDATE configuracion_notificaciones_push SET
                    notificaciones_habilitadas = %s,
                    notificar_sesiones_terapia = %s,
                    minutos_previos_sesion_terapia = %s,
                    notificar_clases_pedagogicas = %s,
                    minutos_previos_clase_pedagogica = %s,
                    notificar_cancelaciones = %s,
                    notificar_reprogramaciones = %s,
                    notificar_mensajes_chat = %s,
                    notificar_solo_mensajes_urgentes = %s,
                    horario_silencio_inicio = %s,
                    horario_silencio_fin = %s,
                    intervalo_verificacion_minutos = %s,
                    usuario_modificacion = %s
                WHERE id = 1
            """

            params = (
                data.get('notificaciones_habilitadas'),
                data.get('notificar_sesiones_terapia'),
                data.get('minutos_previos_sesion_terapia'),
                data.get('notificar_clases_pedagogicas'),
                data.get('minutos_previos_clase_pedagogica'),
                data.get('notificar_cancelaciones'),
                data.get('notificar_reprogramaciones'),
                data.get('notificar_mensajes_chat'),
                data.get('notificar_solo_mensajes_urgentes'),
                data.get('horario_silencio_inicio'),
                data.get('horario_silencio_fin'),
                data.get('intervalo_verificacion_minutos'),
                usuario_id
            )

            result = self.db.ExecuteNonQuery(query, params)

            if result:
                return {
                    'success': True,
                    'message': 'Configuracion de notificaciones actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error actualizando configuracion de notificaciones'
                }

        except Exception as e:
            HandleLogs.write_error(f"Error en update_configuracion_notificaciones: {str(e)}")
            return {
                'success': False,
                'message': f'Error actualizando configuracion de notificaciones: {str(e)}'
            }
