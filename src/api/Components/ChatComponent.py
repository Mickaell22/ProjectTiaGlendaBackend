"""
ChatComponent.py
Manejo de operaciones de base de datos para el sistema de chat
Centro Tía Glenda - Sistema de Mensajería Interna
"""

from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from datetime import datetime
import json

class ChatComponent:
    
    @staticmethod
    def enviar_mensaje(id_remitente, id_destinatario, mensaje, id_centro, tipo_mensaje='texto', prioridad='normal', usuario_creacion=None):
        """
        Enviar un nuevo mensaje en el chat
        """
        try:
            db = DataBaseHandle()

            # Step 1: Insert the message using ExecuteInsert
            insert_query = """
                INSERT INTO mensajes_chat
                (id_remitente, id_destinatario, mensaje, id_centro, tipo_mensaje, prioridad, usuario_creacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """

            params = (id_remitente, id_destinatario, mensaje, id_centro, tipo_mensaje, prioridad, usuario_creacion or id_remitente)
            HandleLogs.write_log(f"[ChatComponent] Enviando mensaje - Parámetros: {params}")

            mensaje_id = db.ExecuteInsert(insert_query, params)

            if mensaje_id:
                # Step 2: Get the fecha_envio for the inserted message
                select_query = "SELECT fecha_envio FROM mensajes_chat WHERE id = %s"
                resultado = db.getRecords(select_query, (mensaje_id,))

                fecha_envio = resultado[0]['fecha_envio'] if resultado else None
                HandleLogs.write_log(f"[ChatComponent] Mensaje enviado exitosamente - ID: {mensaje_id}")

                return {
                    'success': True,
                    'id_mensaje': mensaje_id,
                    'fecha_envio': fecha_envio.isoformat() if fecha_envio else None
                }
            else:
                HandleLogs.write_error("[ChatComponent] Error al insertar mensaje - ExecuteInsert retornó None")
                return {'success': False, 'message': 'Error al enviar mensaje'}

        except Exception as e:
            HandleLogs.write_error(f"Error en enviar_mensaje: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def obtener_conversaciones(id_usuario, id_centro):
        """
        Obtener lista de conversaciones del usuario
        """
        try:
            db = DataBaseHandle()
            
            query = """
                WITH conversaciones AS (
                    SELECT
                        CASE
                            WHEN mc.id_remitente = %s THEN mc.id_destinatario
                            ELSE mc.id_remitente
                        END as id_contacto,
                        CASE
                            WHEN mc.id_remitente = %s THEN
                                CONCAT(p_dest.nombre, ' ', p_dest.apellido)
                            ELSE
                                CONCAT(p_rem.nombre, ' ', p_rem.apellido)
                        END as nombre_contacto,
                        mc.fecha_envio,
                        mc.mensaje,
                        ROW_NUMBER() OVER (
                            PARTITION BY (
                                CASE
                                    WHEN mc.id_remitente = %s THEN mc.id_destinatario
                                    ELSE mc.id_remitente
                                END
                            )
                            ORDER BY mc.fecha_envio DESC
                        ) as rn
                    FROM mensajes_chat mc
                    LEFT JOIN usuario u_rem ON mc.id_remitente = u_rem.id
                    LEFT JOIN persona p_rem ON u_rem.id_persona = p_rem.id
                    LEFT JOIN usuario u_dest ON mc.id_destinatario = u_dest.id
                    LEFT JOIN persona p_dest ON u_dest.id_persona = p_dest.id
                    WHERE (mc.id_remitente = %s OR mc.id_destinatario = %s)
                )
                SELECT
                    id_contacto,
                    nombre_contacto,
                    fecha_envio as fecha_ultimo_mensaje,
                    LEFT(mensaje, 50) as ultimo_mensaje,
                    0 as mensajes_no_leidos
                FROM conversaciones
                WHERE rn = 1
                ORDER BY fecha_ultimo_mensaje DESC
            """
            
            resultado = db.getRecords(query, (id_usuario, id_usuario, id_usuario, id_usuario, id_usuario))
            
            if resultado:
                # Convertir fechas a string para serialización JSON
                conversaciones = []
                for conv in resultado:
                    conversacion = dict(conv)
                    if 'fecha_ultimo_mensaje' in conversacion and conversacion['fecha_ultimo_mensaje']:
                        conversacion['fecha_ultimo_mensaje'] = conversacion['fecha_ultimo_mensaje'].isoformat()
                    conversaciones.append(conversacion)
                
                return {
                    'success': True,
                    'conversaciones': conversaciones
                }
            else:
                return {
                    'success': True,
                    'conversaciones': []
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_conversaciones: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def obtener_mensajes_conversacion(id_usuario, id_contacto, id_centro, limite=50):
        """
        Obtener mensajes de una conversación específica
        """
        try:
            db = DataBaseHandle()
            
            HandleLogs.write_log(f"🔍 [ChatComponent] obtener_mensajes_conversacion - Parámetros: id_usuario={id_usuario}, id_contacto={id_contacto}, id_centro={id_centro}, limite={limite}")
            
            query = """
                SELECT 
                    mc.id,
                    mc.id_remitente,
                    mc.id_destinatario,
                    mc.mensaje,
                    mc.fecha_envio,
                    mc.leido,
                    mc.fecha_lectura,
                    mc.tipo_mensaje,
                    mc.prioridad,
                    pr.nombre as nombre_remitente,
                    pr.apellido as apellido_remitente,
                    pd.nombre as nombre_destinatario,
                    pd.apellido as apellido_destinatario,
                    mc.id_remitente = %s as es_remitente
                FROM mensajes_chat mc
                JOIN usuario ur ON mc.id_remitente = ur.id
                JOIN persona pr ON ur.id_persona = pr.id
                JOIN usuario ud ON mc.id_destinatario = ud.id
                JOIN persona pd ON ud.id_persona = pd.id
                WHERE ((mc.id_remitente = %s AND mc.id_destinatario = %s)
                    OR (mc.id_remitente = %s AND mc.id_destinatario = %s))
                ORDER BY mc.fecha_envio DESC
                LIMIT %s
            """
            
            params = (id_usuario, id_usuario, id_contacto, id_contacto, id_usuario, limite)
            HandleLogs.write_log(f"📝 [ChatComponent] Query params: {params}")
            resultado = db.getRecords(query, params)
            HandleLogs.write_log(f"📊 [ChatComponent] Resultado de getRecords: {len(resultado) if resultado else 0} registros encontrados")
            
            if resultado:
                # Convertir fechas a string y organizar mensajes
                mensajes = []
                for msg in resultado:
                    mensaje = dict(msg)
                    if 'fecha_envio' in mensaje and mensaje['fecha_envio']:
                        mensaje['fecha_envio'] = mensaje['fecha_envio'].isoformat()
                    if 'fecha_lectura' in mensaje and mensaje['fecha_lectura']:
                        mensaje['fecha_lectura'] = mensaje['fecha_lectura'].isoformat()
                    mensajes.append(mensaje)
                
                # Revertir orden para mostrar mensajes más antiguos primero
                mensajes.reverse()
                
                return {
                    'success': True,
                    'mensajes': mensajes
                }
            else:
                return {
                    'success': True,
                    'mensajes': []
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_mensajes_conversacion: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def marcar_mensaje_leido(id_mensaje, id_usuario):
        """
        Marcar un mensaje como leído
        """
        try:
            db = DataBaseHandle()
            
            query = """
                UPDATE mensajes_chat 
                SET leido = TRUE,
                    fecha_lectura = CURRENT_TIMESTAMP,
                    fecha_modificacion = CURRENT_TIMESTAMP,
                    usuario_modificacion = %s
                WHERE id = %s 
                AND id_destinatario = %s
                AND leido = FALSE
            """
            
            rows_affected = db.ExecuteNonQuery(query, (id_usuario, id_mensaje, id_usuario))
            
            if rows_affected > 0:
                return {'success': True, 'message': 'Mensaje marcado como leído'}
            else:
                return {'success': False, 'message': 'Mensaje no encontrado o ya estaba leído'}
                
        except Exception as e:
            HandleLogs.write_error(f"Error en marcar_mensaje_leido: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def marcar_conversacion_leida(id_usuario, id_contacto, id_centro):
        """
        Marcar todos los mensajes no leídos de una conversación como leídos
        """
        try:
            db = DataBaseHandle()
            
            query = """
                UPDATE mensajes_chat 
                SET leido = TRUE,
                    fecha_lectura = CURRENT_TIMESTAMP,
                    fecha_modificacion = CURRENT_TIMESTAMP,
                    usuario_modificacion = %s
                WHERE id_remitente = %s 
                AND id_destinatario = %s
                AND leido = FALSE
            """
            
            rows_affected = db.ExecuteNonQuery(query, (id_usuario, id_contacto, id_usuario))
            
            return {
                'success': True, 
                'message': f'{rows_affected} mensajes marcados como leídos'
            }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en marcar_conversacion_leida: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def obtener_usuarios_disponibles(id_usuario, id_centro, solo_activos=True):
        """
        Obtener lista de usuarios disponibles para iniciar conversación
        """
        try:
            db = DataBaseHandle()
            
            estado_filter = "AND u.estado = 'activo'" if solo_activos else ""
            
            query = f"""
                SELECT 
                    u.id,
                    p.nombre,
                    p.apellido,
                    r.nombre as rol,
                    u.estado
                FROM usuario u
                JOIN persona p ON u.id_persona = p.id
                JOIN rol r ON u.id_rol = r.id
                WHERE u.id != %s
                {estado_filter}
                ORDER BY p.nombre, p.apellido
            """
            
            resultado = db.getRecords(query, (id_usuario,))
            
            if resultado:
                usuarios = [dict(user) for user in resultado]
                return {
                    'success': True,
                    'usuarios': usuarios
                }
            else:
                return {
                    'success': True,
                    'usuarios': []
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_usuarios_disponibles: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def obtener_estadisticas_mensajes(id_usuario, id_centro):
        """
        Obtener estadísticas de mensajes para el usuario
        """
        try:
            db = DataBaseHandle()
            
            # Simplificar la consulta para evitar problemas con FILTER
            query = """
                SELECT 
                    COUNT(*) as total_mensajes,
                    SUM(CASE WHEN id_destinatario = %s AND leido = FALSE THEN 1 ELSE 0 END) as mensajes_no_leidos,
                    SUM(CASE WHEN id_remitente = %s THEN 1 ELSE 0 END) as mensajes_enviados,
                    SUM(CASE WHEN id_destinatario = %s THEN 1 ELSE 0 END) as mensajes_recibidos
                FROM mensajes_chat 
                WHERE (id_remitente = %s OR id_destinatario = %s)
            """
            
            params = (id_usuario, id_usuario, id_usuario, id_usuario, id_usuario)
            resultado = db.getRecords(query, params)
            
            # Contar conversaciones activas por separado
            query_conversaciones = """
                SELECT COUNT(DISTINCT 
                    CASE 
                        WHEN id_remitente = %s THEN id_destinatario
                        ELSE id_remitente
                    END
                ) as conversaciones_activas
                FROM mensajes_chat 
                WHERE (id_remitente = %s OR id_destinatario = %s)
            """
            
            resultado_conv = db.getRecords(query_conversaciones, (id_usuario, id_usuario, id_usuario))
            
            if resultado and len(resultado) > 0:
                stats = dict(resultado[0])
                if resultado_conv and len(resultado_conv) > 0:
                    stats['conversaciones_activas'] = resultado_conv[0]['conversaciones_activas'] or 0
                else:
                    stats['conversaciones_activas'] = 0
                
                return {
                    'success': True,
                    'estadisticas': stats
                }
            else:
                return {
                    'success': True,
                    'estadisticas': {
                        'total_mensajes': 0,
                        'mensajes_no_leidos': 0,
                        'mensajes_enviados': 0,
                        'mensajes_recibidos': 0,
                        'conversaciones_activas': 0
                    }
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_estadisticas_mensajes: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def buscar_mensajes(id_usuario, id_centro, texto_busqueda, id_contacto=None):
        """
        Buscar mensajes por contenido
        """
        try:
            db = DataBaseHandle()
            
            contacto_filter = "AND ((mc.id_remitente = %s AND mc.id_destinatario = %s) OR (mc.id_remitente = %s AND mc.id_destinatario = %s))" if id_contacto else ""
            params_base = (id_usuario, id_usuario, id_usuario, f"%{texto_busqueda}%")
            
            if id_contacto:
                params_base += (id_usuario, id_contacto, id_contacto, id_usuario)
            
            query = f"""
                SELECT 
                    mc.id,
                    mc.id_remitente,
                    mc.id_destinatario,
                    mc.mensaje,
                    mc.fecha_envio,
                    mc.tipo_mensaje,
                    pr.nombre as nombre_remitente,
                    pr.apellido as apellido_remitente,
                    pd.nombre as nombre_destinatario,
                    pd.apellido as apellido_destinatario,
                    mc.id_remitente = %s as es_remitente
                FROM mensajes_chat mc
                JOIN usuario ur ON mc.id_remitente = ur.id
                JOIN persona pr ON ur.id_persona = pr.id
                JOIN usuario ud ON mc.id_destinatario = ud.id
                JOIN persona pd ON ud.id_persona = pd.id
                WHERE (mc.id_remitente = %s OR mc.id_destinatario = %s)
                AND mc.mensaje ILIKE %s
                {contacto_filter}
                ORDER BY mc.fecha_envio DESC
                LIMIT 100
            """
            
            resultado = db.getRecords(query, params_base)
            
            if resultado:
                mensajes = []
                for msg in resultado:
                    mensaje = dict(msg)
                    if 'fecha_envio' in mensaje and mensaje['fecha_envio']:
                        mensaje['fecha_envio'] = mensaje['fecha_envio'].isoformat()
                    mensajes.append(mensaje)
                
                return {
                    'success': True,
                    'mensajes': mensajes
                }
            else:
                return {
                    'success': True,
                    'mensajes': []
                }
                
        except Exception as e:
            HandleLogs.write_error(f"Error en buscar_mensajes: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}

    @staticmethod
    def obtener_conteo_mensajes_no_leidos(id_usuario):
        """
        Obtener el conteo de mensajes no leídos para un usuario
        """
        try:
            from src.utils.database.connection_db import DataBaseHandle as db

            # Query para contar mensajes no leídos
            query = """
                SELECT COUNT(*) as count
                FROM mensajes_chat mc
                WHERE mc.id_destinatario = %s
                AND mc.leido = false
                AND mc.eliminado_destinatario = false
            """

            resultado = db.getRecords(query, (id_usuario,), size=1)

            if resultado:
                count = resultado.get('count', 0)
                return {
                    'success': True,
                    'count': count
                }
            else:
                return {
                    'success': True,
                    'count': 0
                }

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_conteo_mensajes_no_leidos: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}