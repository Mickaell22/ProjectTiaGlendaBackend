# =============================================
# CENTRO TÍA GLENDA - COMPONENTE DE NOTIFICACIONES PUSH
# Archivo: NotificacionesComponent.py
# Descripción: Componente para gestión de notificaciones automáticas
# =============================================

from src.utils.database.database import DataBaseHandle
from src.utils.general.HandleLogs import HandleLogs
from datetime import datetime, timedelta
import json

class NotificacionesComponent:
    """Componente para gestión de notificaciones push automáticas"""
    
    def __init__(self):
        self.db = DataBaseHandle()
    
    def crear_notificacion(self, id_usuario, id_centro, titulo, mensaje, tipo_notificacion, 
                          prioridad='normal', fecha_programada=None, contexto=None, 
                          url_accion=None, fecha_expiracion=None):
        """
        Crear una nueva notificación
        
        Args:
            id_usuario (int): ID del usuario destinatario
            id_centro (int): ID del centro
            titulo (str): Título de la notificación
            mensaje (str): Contenido de la notificación
            tipo_notificacion (str): Tipo de notificación
            prioridad (str): Prioridad ('baja', 'normal', 'alta', 'urgente')
            fecha_programada (datetime): Cuándo enviar la notificación
            contexto (dict): Información adicional en formato JSON
            url_accion (str): URL de acción opcional
            fecha_expiracion (datetime): Cuándo expira la notificación
            
        Returns:
            tuple: (success, notification_id/error_message)
        """
        try:
            # Si no se especifica fecha programada, usar el momento actual
            if fecha_programada is None:
                fecha_programada = datetime.now()
            
            # Si no se especifica expiración, usar 24 horas después de la fecha programada
            if fecha_expiracion is None:
                fecha_expiracion = fecha_programada + timedelta(hours=24)
            
            # Convertir contexto a JSON si es un diccionario
            contexto_json = None
            if contexto:
                contexto_json = json.dumps(contexto) if isinstance(contexto, dict) else contexto
            
            query = """
            INSERT INTO notificaciones_push (
                id_usuario, id_centro, titulo, mensaje, tipo_notificacion,
                prioridad, fecha_programada, contexto, url_accion,
                fecha_expiracion, usuario_creacion
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
            """
            
            parametros = (
                id_usuario, id_centro, titulo, mensaje, tipo_notificacion,
                prioridad, fecha_programada, contexto_json, url_accion,
                fecha_expiracion, id_usuario
            )
            
            resultado = self.db.getRecords(query, parametros)
            
            if resultado and len(resultado) > 0:
                notificacion_id = resultado[0]['id']
                HandleLogs.write_log(f"Notificación creada exitosamente. ID: {notificacion_id}")
                return True, notificacion_id
            else:
                return False, "Error al crear notificación"
                
        except Exception as e:
            error_msg = f"Error al crear notificación: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg
    
    def obtener_notificaciones_pendientes(self):
        """
        Obtener notificaciones pendientes para envío
        
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
            ORDER BY n.prioridad DESC, n.fecha_programada ASC
            LIMIT 100
            """
            
            resultado = self.db.getRecords(query)
            
            if resultado:
                # Procesar contexto JSON
                for notif in resultado:
                    if notif.get('contexto'):
                        try:
                            notif['contexto'] = json.loads(notif['contexto'])
                        except:
                            notif['contexto'] = {}
                    else:
                        notif['contexto'] = {}
                    
                    # Formatear fechas
                    if notif.get('fecha_programada'):
                        notif['fecha_programada'] = notif['fecha_programada'].isoformat()
                    if notif.get('fecha_expiracion'):
                        notif['fecha_expiracion'] = notif['fecha_expiracion'].isoformat()
                
                return True, resultado
            else:
                return True, []
                
        except Exception as e:
            error_msg = f"Error al obtener notificaciones pendientes: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg
    
    def marcar_notificacion_enviada(self, id_notificacion):
        """
        Marcar una notificación como enviada
        
        Args:
            id_notificacion (int): ID de la notificación
            
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
            
            if filas_afectadas > 0:
                HandleLogs.write_log(f"Notificación {id_notificacion} marcada como enviada")
                return True, "Notificación marcada como enviada"
            else:
                return False, "Notificación no encontrada o ya procesada"
                
        except Exception as e:
            error_msg = f"Error al marcar notificación como enviada: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg
    
    def marcar_notificacion_fallida(self, id_notificacion, error_mensaje):
        """
        Marcar una notificación como fallida e incrementar intentos
        
        Args:
            id_notificacion (int): ID de la notificación
            error_mensaje (str): Mensaje de error
            
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
            
            HandleLogs.write_log(f"Notificación {id_notificacion} marcada como fallida: {error_mensaje}")
            return True, "Notificación marcada como fallida"
            
        except Exception as e:
            error_msg = f"Error al marcar notificación como fallida: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg
    
    def obtener_notificaciones_usuario(self, id_usuario, incluir_leidas=False, limite=50):
        """
        Obtener notificaciones de un usuario específico
        
        Args:
            id_usuario (int): ID del usuario
            incluir_leidas (bool): Si incluir notificaciones leídas
            limite (int): Cantidad máxima de notificaciones
            
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
            ORDER BY n.fecha_envio DESC
            LIMIT %s
            """
            
            resultado = self.db.getRecords(query, (id_usuario, limite))
            
            if resultado:
                # Procesar contexto JSON y fechas
                for notif in resultado:
                    if notif.get('contexto'):
                        try:
                            notif['contexto'] = json.loads(notif['contexto'])
                        except:
                            notif['contexto'] = {}
                    else:
                        notif['contexto'] = {}
                    
                    # Formatear fechas
                    if notif.get('fecha_envio'):
                        notif['fecha_envio'] = notif['fecha_envio'].isoformat()
                    if notif.get('fecha_lectura'):
                        notif['fecha_lectura'] = notif['fecha_lectura'].isoformat()
                
                return True, resultado
            else:
                return True, []
                
        except Exception as e:
            error_msg = f"Error al obtener notificaciones del usuario: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg
    
    def marcar_notificacion_leida(self, id_notificacion, id_usuario):
        """
        Marcar una notificación como leída por el usuario
        
        Args:
            id_notificacion (int): ID de la notificación
            id_usuario (int): ID del usuario
            
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
            
            if filas_afectadas > 0:
                HandleLogs.write_log(f"Notificación {id_notificacion} marcada como leída por usuario {id_usuario}")
                return True, "Notificación marcada como leída"
            else:
                return False, "Notificación no encontrada o ya leída"
                
        except Exception as e:
            error_msg = f"Error al marcar notificación como leída: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg
    
    def obtener_configuracion_notificaciones(self):
        """
        Obtener configuración del sistema de notificaciones
        
        Returns:
            tuple: (success, config/error_message)
        """
        try:
            query = """
            SELECT * FROM configuracion_notificaciones_push WHERE id = 1
            """
            
            resultado = self.db.getRecords(query)
            
            if resultado and len(resultado) > 0:
                config = resultado[0]
                
                # Formatear campos de tiempo
                if config.get('horario_silencio_inicio'):
                    config['horario_silencio_inicio'] = str(config['horario_silencio_inicio'])
                if config.get('horario_silencio_fin'):
                    config['horario_silencio_fin'] = str(config['horario_silencio_fin'])
                
                return True, config
            else:
                # Retornar configuración por defecto si no existe
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
            error_msg = f"Error al obtener configuración de notificaciones: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg
    
    def crear_notificacion_sesion_terapia(self, sesion_info):
        """
        Crear notificación para sesión de terapia próxima
        
        Args:
            sesion_info (dict): Información de la sesión
            
        Returns:
            tuple: (success, notification_id/error_message)
        """
        try:
            # Obtener configuración
            success, config = self.obtener_configuracion_notificaciones()
            if not success or not config.get('notificar_sesiones_terapia'):
                return False, "Notificaciones de sesiones terapéuticas deshabilitadas"
            
            minutos_previos = config.get('minutos_previos_sesion_terapia', 15)
            
            # Calcular fecha de envío
            fecha_sesion = datetime.fromisoformat(sesion_info['fecha_inicio'].replace('Z', '+00:00'))
            fecha_notificacion = fecha_sesion - timedelta(minutes=minutos_previos)
            
            # Crear contexto
            contexto = {
                'sesion_id': sesion_info['id'],
                'tipo_sesion': 'terapia',
                'fecha_sesion': sesion_info['fecha_inicio'],
                'paciente': sesion_info.get('paciente_nombre', ''),
                'consultorio': sesion_info.get('consultorio', '')
            }
            
            titulo = "Sesión de Terapia Próxima"
            mensaje = f"Sesión con {sesion_info.get('paciente_nombre', 'paciente')} en {minutos_previos} minutos"
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
            error_msg = f"Error al crear notificación de sesión terapéutica: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg
    
    def crear_notificacion_clase_pedagogica(self, clase_info):
        """
        Crear notificación para clase pedagógica próxima
        
        Args:
            clase_info (dict): Información de la clase
            
        Returns:
            tuple: (success, notification_id/error_message)
        """
        try:
            # Obtener configuración
            success, config = self.obtener_configuracion_notificaciones()
            if not success or not config.get('notificar_clases_pedagogicas'):
                return False, "Notificaciones de clases pedagógicas deshabilitadas"
            
            minutos_previos = config.get('minutos_previos_clase_pedagogica', 15)
            
            # Calcular fecha de envío
            fecha_clase = datetime.fromisoformat(clase_info['fecha_inicio'].replace('Z', '+00:00'))
            fecha_notificacion = fecha_clase - timedelta(minutes=minutos_previos)
            
            # Crear contexto
            contexto = {
                'clase_id': clase_info['id'],
                'tipo_sesion': 'pedagogica',
                'fecha_clase': clase_info['fecha_inicio'],
                'materia': clase_info.get('materia', ''),
                'aula': clase_info.get('aula', '')
            }
            
            titulo = "Clase Pedagógica Próxima"
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
            error_msg = f"Error al crear notificación de clase pedagógica: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg
    
    def crear_notificacion_mensaje_chat(self, mensaje_info):
        """
        Crear notificación para nuevo mensaje de chat
        
        Args:
            mensaje_info (dict): Información del mensaje
            
        Returns:
            tuple: (success, notification_id/error_message)
        """
        try:
            # Obtener configuración
            success, config = self.obtener_configuracion_notificaciones()
            if not success or not config.get('notificar_mensajes_chat'):
                return False, "Notificaciones de mensajes de chat deshabilitadas"
            
            # Verificar si solo notificar mensajes urgentes
            if config.get('notificar_solo_mensajes_urgentes') and mensaje_info.get('prioridad') != 'urgente':
                return False, "Solo se notifican mensajes urgentes"
            
            # Crear contexto
            contexto = {
                'mensaje_id': mensaje_info['id'],
                'remitente_id': mensaje_info['id_remitente'],
                'tipo_mensaje': mensaje_info.get('tipo_mensaje', 'texto')
            }
            
            titulo = "Nuevo Mensaje"
            mensaje = f"Mensaje de {mensaje_info.get('remitente_nombre', 'usuario')}"
            if mensaje_info.get('prioridad') == 'urgente':
                titulo = "¡Mensaje Urgente!"
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
            error_msg = f"Error al crear notificación de mensaje de chat: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg
    
    def limpiar_notificaciones_expiradas(self):
        """
        Limpiar notificaciones expiradas
        
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
                return True, es_horario_silencio
            else:
                return True, False
                
        except Exception as e:
            error_msg = f"Error al verificar horario de silencio: {str(e)}"
            HandleLogs.write_error(error_msg)
            return False, error_msg