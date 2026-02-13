# =============================================
# CENTRO TIA GLENDA - COMPONENTE DE NOTIFICACIONES PUSH
# Archivo: NotificacionesComponent.py
# Descripcion: Componente para gestion de notificaciones automaticas
# =============================================

from src.utils.database.database import DataBaseHandle
from src.utils.general.HandleLogs import HandleLogs
from datetime import datetime, timedelta
import json

class NotificacionesComponent:
    """Componente para gestion de notificaciones push automaticas"""

    def __init__(self):
        self.db = DataBaseHandle()

    # =============================================
    # HELPERS
    # =============================================

    def _procesar_contexto_jsonb(self, valor):
        """
        Procesar campo contexto JSONB de PostgreSQL.
        psycopg2 deserializa JSONB automaticamente a dict/list,
        pero si por alguna razon viene como string, lo parseamos.
        """
        if valor is None:
            return {}
        if isinstance(valor, (dict, list)):
            return valor
        if isinstance(valor, str):
            try:
                return json.loads(valor)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    def _formatear_fecha(self, valor):
        """Convertir fecha/datetime a string ISO si no es None"""
        if valor is None:
            return None
        if isinstance(valor, str):
            return valor
        return valor.isoformat()

    def _formatear_time(self, valor):
        """Convertir campo TIME a string si no es None"""
        if valor is None:
            return None
        return str(valor)

    # =============================================
    # CRUD
    # =============================================

    def crear_notificacion(self, id_usuario, id_centro, titulo, mensaje, tipo_notificacion,
                          prioridad='normal', fecha_programada=None, contexto=None,
                          url_accion=None, fecha_expiracion=None):
        """
        Crear una nueva notificacion

        Returns:
            tuple: (success, notification_id/error_message)
        """
        try:
            if fecha_programada is None:
                fecha_programada = datetime.now()

            if fecha_expiracion is None:
                fecha_expiracion = fecha_programada + timedelta(hours=24)

            # Convertir contexto a JSON string para insercion
            contexto_json = None
            if contexto:
                contexto_json = json.dumps(contexto) if isinstance(contexto, dict) else contexto

            query_insert = """
            INSERT INTO notificaciones_push (
                id_usuario, id_centro, titulo, mensaje, tipo_notificacion,
                prioridad, fecha_programada, contexto, url_accion,
                fecha_expiracion, usuario_creacion
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """

            parametros = (
                id_usuario, id_centro, titulo, mensaje, tipo_notificacion,
                prioridad, fecha_programada, contexto_json, url_accion,
                fecha_expiracion, id_usuario
            )

            self.db.ExecuteNonQuery(query_insert, parametros)

            # Obtener el ID de la notificacion recien creada
            query_id = """
            SELECT id FROM notificaciones_push
            WHERE id_usuario = %s AND titulo = %s AND fecha_programada = %s
            ORDER BY id DESC LIMIT 1
            """
            resultado = self.db.getRecords(query_id, (id_usuario, titulo, fecha_programada))

            if resultado and len(resultado) > 0:
                notificacion_id = resultado[0]['id']
                HandleLogs.write_log(f"Notificacion creada exitosamente. ID: {notificacion_id}")
                return True, notificacion_id
            else:
                HandleLogs.write_log("Notificacion creada exitosamente (ID no recuperado)")
                return True, 0

        except Exception as e:
            error_msg = f"Error al crear notificacion: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def obtener_notificaciones_pendientes(self):
        """
        Obtener notificaciones pendientes para envio

        Returns:
            tuple: (success, notifications/error_message)
        """
        try:
            query = """
            SELECT
                n.id,
                n.id_usuario,
                n.id_centro,
                n.titulo,
                n.mensaje,
                n.tipo_notificacion,
                n.prioridad,
                n.contexto,
                n.url_accion,
                n.fecha_programada,
                n.fecha_expiracion,
                n.intentos_envio,
                n.max_intentos,
                p.nombre as nombre_usuario,
                p.apellido as apellido_usuario,
                p.correo as email_usuario,
                u.username
            FROM notificaciones_push n
            INNER JOIN usuario u ON n.id_usuario = u.id
            INNER JOIN persona p ON u.id_persona = p.id
            WHERE n.estado = 'pendiente'
                AND n.fecha_programada <= CURRENT_TIMESTAMP
                AND n.intentos_envio < n.max_intentos
                AND (n.fecha_expiracion IS NULL OR n.fecha_expiracion > CURRENT_TIMESTAMP)
            ORDER BY
                CASE n.prioridad
                    WHEN 'urgente' THEN 1
                    WHEN 'alta' THEN 2
                    WHEN 'normal' THEN 3
                    WHEN 'baja' THEN 4
                    ELSE 5
                END ASC,
                n.fecha_programada ASC
            LIMIT 100
            """

            resultado = self.db.getRecords(query)

            if resultado:
                for notif in resultado:
                    notif['contexto'] = self._procesar_contexto_jsonb(notif.get('contexto'))
                    notif['fecha_programada'] = self._formatear_fecha(notif.get('fecha_programada'))
                    notif['fecha_expiracion'] = self._formatear_fecha(notif.get('fecha_expiracion'))

                return True, resultado
            else:
                return True, []

        except Exception as e:
            error_msg = f"Error al obtener notificaciones pendientes: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def marcar_notificacion_enviada(self, id_notificacion):
        """
        Marcar una notificacion como enviada

        Returns:
            tuple: (success, message/error_message)
        """
        try:
            query = """
            UPDATE notificaciones_push
            SET estado = 'enviada',
                fecha_envio = CURRENT_TIMESTAMP,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s AND estado = 'pendiente'
            """

            filas_afectadas = self.db.ExecuteNonQuery(query, (id_notificacion,))

            if filas_afectadas and filas_afectadas > 0:
                HandleLogs.write_log(f"Notificacion {id_notificacion} marcada como enviada")
                return True, "Notificacion marcada como enviada"
            else:
                return False, "Notificacion no encontrada o ya procesada"

        except Exception as e:
            error_msg = f"Error al marcar notificacion como enviada: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def marcar_notificacion_fallida(self, id_notificacion, error_mensaje):
        """
        Marcar una notificacion como fallida e incrementar intentos

        Returns:
            tuple: (success, message/error_message)
        """
        try:
            query = """
            UPDATE notificaciones_push
            SET intentos_envio = intentos_envio + 1,
                ultimo_error = %s,
                estado = CASE
                    WHEN intentos_envio + 1 >= max_intentos THEN 'fallida'
                    ELSE 'pendiente'
                END,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s
            """

            self.db.ExecuteNonQuery(query, (error_mensaje, id_notificacion))

            HandleLogs.write_log(f"Notificacion {id_notificacion} marcada como fallida: {error_mensaje}")
            return True, "Notificacion marcada como fallida"

        except Exception as e:
            error_msg = f"Error al marcar notificacion como fallida: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def obtener_notificaciones_usuario(self, id_usuario, incluir_leidas=False, limite=50):
        """
        Obtener notificaciones de un usuario especifico

        Returns:
            tuple: (success, notifications/error_message)
        """
        try:
            estado_filter = "AND n.estado IN ('enviada', 'leida')" if incluir_leidas else "AND n.estado = 'enviada'"

            query = f"""
            SELECT
                n.id,
                n.titulo,
                n.mensaje,
                n.tipo_notificacion,
                n.prioridad,
                n.contexto,
                n.url_accion,
                n.fecha_envio,
                n.fecha_lectura,
                n.estado
            FROM notificaciones_push n
            WHERE n.id_usuario = %s
                {estado_filter}
            ORDER BY
                CASE n.prioridad
                    WHEN 'urgente' THEN 1
                    WHEN 'alta' THEN 2
                    WHEN 'normal' THEN 3
                    WHEN 'baja' THEN 4
                    ELSE 5
                END ASC,
                n.fecha_envio DESC
            LIMIT %s
            """

            resultado = self.db.getRecords(query, (id_usuario, limite))

            if resultado:
                for notif in resultado:
                    notif['contexto'] = self._procesar_contexto_jsonb(notif.get('contexto'))
                    notif['fecha_envio'] = self._formatear_fecha(notif.get('fecha_envio'))
                    notif['fecha_lectura'] = self._formatear_fecha(notif.get('fecha_lectura'))

                return True, resultado
            else:
                return True, []

        except Exception as e:
            error_msg = f"Error al obtener notificaciones del usuario: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def marcar_notificacion_leida(self, id_notificacion, id_usuario):
        """
        Marcar una notificacion como leida por el usuario

        Returns:
            tuple: (success, message/error_message)
        """
        try:
            query = """
            UPDATE notificaciones_push
            SET estado = 'leida',
                fecha_lectura = CURRENT_TIMESTAMP,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s
                AND id_usuario = %s
                AND estado = 'enviada'
            """

            filas_afectadas = self.db.ExecuteNonQuery(query, (id_notificacion, id_usuario))

            if filas_afectadas and filas_afectadas > 0:
                HandleLogs.write_log(f"Notificacion {id_notificacion} marcada como leida por usuario {id_usuario}")
                return True, "Notificacion marcada como leida"
            else:
                return False, "Notificacion no encontrada o ya leida"

        except Exception as e:
            error_msg = f"Error al marcar notificacion como leida: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def marcar_todas_leidas(self, id_usuario):
        """
        Marcar todas las notificaciones enviadas como leidas para un usuario

        Returns:
            tuple: (success, count/error_message)
        """
        try:
            query = """
            UPDATE notificaciones_push
            SET estado = 'leida',
                fecha_lectura = CURRENT_TIMESTAMP,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_usuario = %s
                AND estado = 'enviada'
            """

            filas_afectadas = self.db.ExecuteNonQuery(query, (id_usuario,))
            count = filas_afectadas if filas_afectadas else 0

            HandleLogs.write_log(f"Marcadas {count} notificaciones como leidas para usuario {id_usuario}")
            return True, count

        except Exception as e:
            error_msg = f"Error al marcar todas las notificaciones como leidas: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def eliminar_notificacion(self, id_notificacion, id_usuario):
        """
        Eliminar (marcar como expirada) una notificacion del usuario

        Returns:
            tuple: (success, message/error_message)
        """
        try:
            query = """
            UPDATE notificaciones_push
            SET estado = 'expirada',
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s
                AND id_usuario = %s
                AND estado IN ('enviada', 'leida')
            """

            filas_afectadas = self.db.ExecuteNonQuery(query, (id_notificacion, id_usuario))

            if filas_afectadas and filas_afectadas > 0:
                HandleLogs.write_log(f"Notificacion {id_notificacion} eliminada por usuario {id_usuario}")
                return True, "Notificacion eliminada exitosamente"
            else:
                return False, "Notificacion no encontrada"

        except Exception as e:
            error_msg = f"Error al eliminar notificacion: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def contar_no_leidas(self, id_usuario):
        """
        Contar notificaciones no leidas de un usuario (para badge)

        Returns:
            tuple: (success, count/error_message)
        """
        try:
            query = """
            SELECT COUNT(*) as total
            FROM notificaciones_push
            WHERE id_usuario = %s AND estado = 'enviada'
            """

            resultado = self.db.getRecords(query, (id_usuario,))

            if resultado and len(resultado) > 0:
                return True, resultado[0]['total']
            else:
                return True, 0

        except Exception as e:
            error_msg = f"Error al contar notificaciones no leidas: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def obtener_estadisticas_usuario(self, id_usuario):
        """
        Obtener estadisticas de notificaciones con una sola query eficiente

        Returns:
            tuple: (success, stats/error_message)
        """
        try:
            query = """
            SELECT
                COUNT(*) FILTER (WHERE estado IN ('enviada', 'leida')) as total_notificaciones,
                COUNT(*) FILTER (WHERE estado = 'enviada') as no_leidas,
                COUNT(*) FILTER (WHERE estado = 'leida') as leidas,
                COUNT(*) FILTER (WHERE tipo_notificacion = 'sesion_terapia' AND estado IN ('enviada', 'leida')) as tipo_sesion_terapia,
                COUNT(*) FILTER (WHERE tipo_notificacion = 'clase_pedagogica' AND estado IN ('enviada', 'leida')) as tipo_clase_pedagogica,
                COUNT(*) FILTER (WHERE tipo_notificacion = 'cancelacion' AND estado IN ('enviada', 'leida')) as tipo_cancelacion,
                COUNT(*) FILTER (WHERE tipo_notificacion = 'reprogramacion' AND estado IN ('enviada', 'leida')) as tipo_reprogramacion,
                COUNT(*) FILTER (WHERE tipo_notificacion = 'mensaje_chat' AND estado IN ('enviada', 'leida')) as tipo_mensaje_chat,
                COUNT(*) FILTER (WHERE tipo_notificacion = 'recordatorio_general' AND estado IN ('enviada', 'leida')) as tipo_recordatorio_general,
                COUNT(*) FILTER (WHERE prioridad = 'urgente' AND estado IN ('enviada', 'leida')) as prioridad_urgente,
                COUNT(*) FILTER (WHERE prioridad = 'alta' AND estado IN ('enviada', 'leida')) as prioridad_alta,
                COUNT(*) FILTER (WHERE prioridad = 'normal' AND estado IN ('enviada', 'leida')) as prioridad_normal,
                COUNT(*) FILTER (WHERE prioridad = 'baja' AND estado IN ('enviada', 'leida')) as prioridad_baja
            FROM notificaciones_push
            WHERE id_usuario = %s
            """

            resultado = self.db.getRecords(query, (id_usuario,))

            if resultado and len(resultado) > 0:
                row = resultado[0]
                stats = {
                    'total_notificaciones': row['total_notificaciones'] or 0,
                    'notificaciones_no_leidas': row['no_leidas'] or 0,
                    'notificaciones_leidas': row['leidas'] or 0,
                    'por_tipo': {
                        'sesion_terapia': row['tipo_sesion_terapia'] or 0,
                        'clase_pedagogica': row['tipo_clase_pedagogica'] or 0,
                        'cancelacion': row['tipo_cancelacion'] or 0,
                        'reprogramacion': row['tipo_reprogramacion'] or 0,
                        'mensaje_chat': row['tipo_mensaje_chat'] or 0,
                        'recordatorio_general': row['tipo_recordatorio_general'] or 0
                    },
                    'por_prioridad': {
                        'urgente': row['prioridad_urgente'] or 0,
                        'alta': row['prioridad_alta'] or 0,
                        'normal': row['prioridad_normal'] or 0,
                        'baja': row['prioridad_baja'] or 0
                    }
                }
                return True, stats
            else:
                return True, {
                    'total_notificaciones': 0,
                    'notificaciones_no_leidas': 0,
                    'notificaciones_leidas': 0,
                    'por_tipo': {},
                    'por_prioridad': {}
                }

        except Exception as e:
            error_msg = f"Error al obtener estadisticas de notificaciones: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    # =============================================
    # CONFIGURACION
    # =============================================

    def obtener_configuracion_notificaciones(self):
        """
        Obtener configuracion del sistema de notificaciones

        Returns:
            tuple: (success, config/error_message)
        """
        try:
            query = """
            SELECT
                id,
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
                intervalo_verificacion_minutos,
                fecha_creacion,
                fecha_modificacion
            FROM configuracion_notificaciones_push WHERE id = 1
            """

            resultado = self.db.getRecords(query)

            if resultado and len(resultado) > 0:
                config = resultado[0]

                # Formatear campos TIME
                config['horario_silencio_inicio'] = self._formatear_time(config.get('horario_silencio_inicio'))
                config['horario_silencio_fin'] = self._formatear_time(config.get('horario_silencio_fin'))

                # Formatear campos TIMESTAMP
                config['fecha_creacion'] = self._formatear_fecha(config.get('fecha_creacion'))
                config['fecha_modificacion'] = self._formatear_fecha(config.get('fecha_modificacion'))

                return True, config
            else:
                config_default = {
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
                return True, config_default

        except Exception as e:
            error_msg = f"Error al obtener configuracion de notificaciones: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def actualizar_configuracion_notificaciones(self, datos, usuario_id=None):
        """
        Actualizar configuracion del sistema de notificaciones

        Returns:
            tuple: (success, message/error_message)
        """
        try:
            campos_permitidos = [
                'notificaciones_habilitadas',
                'notificar_sesiones_terapia',
                'minutos_previos_sesion_terapia',
                'notificar_clases_pedagogicas',
                'minutos_previos_clase_pedagogica',
                'notificar_cancelaciones',
                'notificar_reprogramaciones',
                'notificar_mensajes_chat',
                'notificar_solo_mensajes_urgentes',
                'horario_silencio_inicio',
                'horario_silencio_fin',
                'intervalo_verificacion_minutos'
            ]

            sets = []
            params = []
            for campo in campos_permitidos:
                if campo in datos:
                    sets.append(f"{campo} = %s")
                    params.append(datos[campo])

            if not sets:
                return False, "No se proporcionaron campos para actualizar"

            if usuario_id:
                sets.append("usuario_modificacion = %s")
                params.append(usuario_id)

            query = f"""
            UPDATE configuracion_notificaciones_push
            SET {', '.join(sets)},
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = 1
            """

            self.db.ExecuteNonQuery(query, tuple(params))

            HandleLogs.write_log("Configuracion de notificaciones actualizada")
            return True, "Configuracion actualizada exitosamente"

        except Exception as e:
            error_msg = f"Error al actualizar configuracion de notificaciones: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    # =============================================
    # NOTIFICACIONES ESPECIFICAS
    # =============================================

    def crear_notificacion_sesion_terapia(self, sesion_info):
        """
        Crear notificacion para sesion de terapia proxima

        Returns:
            tuple: (success, notification_id/error_message)
        """
        try:
            success, config = self.obtener_configuracion_notificaciones()
            if not success or not config.get('notificar_sesiones_terapia'):
                return False, "Notificaciones de sesiones terapeuticas deshabilitadas"

            minutos_previos = config.get('minutos_previos_sesion_terapia', 15)

            fecha_sesion = datetime.fromisoformat(sesion_info['fecha_inicio'].replace('Z', '+00:00'))
            fecha_notificacion = fecha_sesion - timedelta(minutes=minutos_previos)

            contexto = {
                'sesion_id': sesion_info['id'],
                'tipo_sesion': 'terapia',
                'fecha_sesion': sesion_info['fecha_inicio'],
                'paciente': sesion_info.get('paciente_nombre', ''),
                'consultorio': sesion_info.get('consultorio', '')
            }

            titulo = "Sesion de Terapia Proxima"
            mensaje = f"Sesion con {sesion_info.get('paciente_nombre', 'paciente')} en {minutos_previos} minutos"
            if sesion_info.get('consultorio'):
                mensaje += f" - {sesion_info['consultorio']}"

            return self.crear_notificacion(
                id_usuario=sesion_info['terapeuta_id'],
                id_centro=sesion_info['id_centro'],
                titulo=titulo,
                mensaje=mensaje,
                tipo_notificacion='sesion_terapia',
                prioridad='alta',
                fecha_programada=fecha_notificacion,
                contexto=contexto,
                url_accion=f"/sesiones-terapia/{sesion_info['id']}"
            )

        except Exception as e:
            error_msg = f"Error al crear notificacion de sesion terapeutica: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def crear_notificacion_clase_pedagogica(self, clase_info):
        """
        Crear notificacion para clase pedagogica proxima

        Returns:
            tuple: (success, notification_id/error_message)
        """
        try:
            success, config = self.obtener_configuracion_notificaciones()
            if not success or not config.get('notificar_clases_pedagogicas'):
                return False, "Notificaciones de clases pedagogicas deshabilitadas"

            minutos_previos = config.get('minutos_previos_clase_pedagogica', 15)

            fecha_clase = datetime.fromisoformat(clase_info['fecha_inicio'].replace('Z', '+00:00'))
            fecha_notificacion = fecha_clase - timedelta(minutes=minutos_previos)

            contexto = {
                'clase_id': clase_info['id'],
                'tipo_sesion': 'pedagogica',
                'fecha_clase': clase_info['fecha_inicio'],
                'materia': clase_info.get('materia', ''),
                'aula': clase_info.get('aula', '')
            }

            titulo = "Clase Pedagogica Proxima"
            mensaje = f"Clase de {clase_info.get('materia', 'materia')} en {minutos_previos} minutos"
            if clase_info.get('aula'):
                mensaje += f" - {clase_info['aula']}"

            return self.crear_notificacion(
                id_usuario=clase_info['pedagogo_id'],
                id_centro=clase_info['id_centro'],
                titulo=titulo,
                mensaje=mensaje,
                tipo_notificacion='clase_pedagogica',
                prioridad='alta',
                fecha_programada=fecha_notificacion,
                contexto=contexto,
                url_accion=f"/sesiones-pedagogicas/{clase_info['id']}"
            )

        except Exception as e:
            error_msg = f"Error al crear notificacion de clase pedagogica: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def crear_notificacion_mensaje_chat(self, mensaje_info):
        """
        Crear notificacion para nuevo mensaje de chat

        Returns:
            tuple: (success, notification_id/error_message)
        """
        try:
            success, config = self.obtener_configuracion_notificaciones()
            if not success or not config.get('notificar_mensajes_chat'):
                return False, "Notificaciones de mensajes de chat deshabilitadas"

            if config.get('notificar_solo_mensajes_urgentes') and mensaje_info.get('prioridad') != 'urgente':
                return False, "Solo se notifican mensajes urgentes"

            contexto = {
                'mensaje_id': mensaje_info['id'],
                'remitente_id': mensaje_info['id_remitente'],
                'tipo_mensaje': mensaje_info.get('tipo_mensaje', 'texto')
            }

            titulo = "Nuevo Mensaje"
            mensaje = f"Mensaje de {mensaje_info.get('remitente_nombre', 'usuario')}"
            if mensaje_info.get('prioridad') == 'urgente':
                titulo = "Mensaje Urgente"
                mensaje = f"Mensaje urgente de {mensaje_info.get('remitente_nombre', 'usuario')}"

            prioridad_notif = 'urgente' if mensaje_info.get('prioridad') == 'urgente' else 'normal'

            return self.crear_notificacion(
                id_usuario=mensaje_info['id_destinatario'],
                id_centro=mensaje_info['id_centro'],
                titulo=titulo,
                mensaje=mensaje,
                tipo_notificacion='mensaje_chat',
                prioridad=prioridad_notif,
                fecha_programada=datetime.now(),
                contexto=contexto,
                url_accion=f"/chat/{mensaje_info['id_remitente']}"
            )

        except Exception as e:
            error_msg = f"Error al crear notificacion de mensaje de chat: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    # =============================================
    # MANTENIMIENTO
    # =============================================

    def limpiar_notificaciones_expiradas(self):
        """
        Limpiar notificaciones expiradas usando funcion de BD

        Returns:
            tuple: (success, count/error_message)
        """
        try:
            query = "SELECT limpiar_notificaciones_expiradas()"

            resultado = self.db.getRecords(query)

            if resultado and len(resultado) > 0:
                count = resultado[0]['limpiar_notificaciones_expiradas']
                HandleLogs.write_log(f"Notificaciones expiradas limpiadas: {count}")
                return True, count
            else:
                return True, 0

        except Exception as e:
            error_msg = f"Error al limpiar notificaciones expiradas: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg

    def verificar_horario_silencio(self):
        """
        Verificar si estamos en horario de silencio

        Returns:
            tuple: (success, is_silent_hours/error_message)
        """
        try:
            query = "SELECT esta_en_horario_silencio()"

            resultado = self.db.getRecords(query)

            if resultado and len(resultado) > 0:
                es_horario_silencio = resultado[0]['esta_en_horario_silencio']
                return True, bool(es_horario_silencio)
            else:
                return True, False

        except Exception as e:
            error_msg = f"Error al verificar horario de silencio: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg
