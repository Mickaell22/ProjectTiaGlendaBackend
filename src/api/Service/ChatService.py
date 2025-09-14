"""
ChatService.py
Lógica de negocio para el sistema de chat
Centro Tía Glenda - Sistema de Mensajería Interna
"""

from src.api.Components.ChatComponent import ChatComponent
from src.utils.general.logs import HandleLogs
import validators
import re

class ChatService:
    
    @staticmethod
    def enviar_mensaje(data, usuario_autenticado):
        """
        Procesar y enviar un nuevo mensaje
        """
        try:
            # Validar datos requeridos
            required_fields = ['id_destinatario', 'mensaje']
            for field in required_fields:
                if field not in data or not data[field]:
                    return {'success': False, 'message': f'Campo requerido: {field}'}
            
            # Validar contenido del mensaje
            mensaje = data['mensaje'].strip()
            if len(mensaje) == 0:
                return {'success': False, 'message': 'El mensaje no puede estar vacío'}
            
            if len(mensaje) > 1000:
                return {'success': False, 'message': 'El mensaje no puede exceder 1000 caracteres'}
            
            # Validar destinatario
            id_destinatario = data['id_destinatario']
            if not isinstance(id_destinatario, int) or id_destinatario <= 0:
                return {'success': False, 'message': 'ID de destinatario inválido'}
            
            # No permitir envío a sí mismo
            if id_destinatario == usuario_autenticado['id']:
                return {'success': False, 'message': 'No puedes enviarte mensajes a ti mismo'}
            
            # Validar que el destinatario existe
            resultado_destinatario = ChatComponent.obtener_usuarios_disponibles(
                usuario_autenticado['id'], 
                None,  # No filtrar por centro
                solo_activos=True
            )
            
            if not resultado_destinatario['success']:
                return {'success': False, 'message': 'Error al validar destinatario'}
            
            destinatarios_validos = [u['id'] for u in resultado_destinatario['usuarios']]
            if id_destinatario not in destinatarios_validos:
                return {'success': False, 'message': 'Destinatario no válido o no pertenece al mismo centro'}
            
            # Validar tipo de mensaje
            tipo_mensaje = data.get('tipo_mensaje', 'texto')
            if tipo_mensaje not in ['texto', 'archivo', 'imagen']:
                return {'success': False, 'message': 'Tipo de mensaje inválido'}
            
            # Validar prioridad
            prioridad = data.get('prioridad', 'normal')
            if prioridad not in ['baja', 'normal', 'alta', 'urgente']:
                return {'success': False, 'message': 'Prioridad inválida'}
            
            # Sanitizar mensaje (remover caracteres peligrosos)
            mensaje_sanitizado = ChatService._sanitizar_mensaje(mensaje)
            
            # Enviar mensaje
            resultado = ChatComponent.enviar_mensaje(
                id_remitente=usuario_autenticado['id'],
                id_destinatario=id_destinatario,
                mensaje=mensaje_sanitizado,
                id_centro=usuario_autenticado['id_centro'],
                tipo_mensaje=tipo_mensaje,
                prioridad=prioridad,
                usuario_creacion=usuario_autenticado['id']
            )
            
            return resultado
            
        except Exception as e:
            HandleLogs.write_error(f"Error en enviar_mensaje: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def obtener_conversaciones(usuario_autenticado):
        """
        Obtener conversaciones del usuario autenticado
        """
        try:
            resultado = ChatComponent.obtener_conversaciones(
                usuario_autenticado['id'], 
                usuario_autenticado['id_centro']
            )
            
            return resultado
            
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_conversaciones: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def obtener_mensajes_conversacion(id_contacto, usuario_autenticado, limite=50):
        """
        Obtener mensajes de una conversación específica
        """
        try:
            # Validar parámetros
            if not isinstance(id_contacto, int) or id_contacto <= 0:
                return {'success': False, 'message': 'ID de contacto inválido'}
            
            if not isinstance(limite, int) or limite <= 0 or limite > 200:
                limite = 50
            
            # Verificar que el contacto es válido
            resultado_usuarios = ChatComponent.obtener_usuarios_disponibles(
                usuario_autenticado['id'],
                None,  # No filtrar por centro
                solo_activos=True
            )
            
            if not resultado_usuarios['success']:
                return {'success': False, 'message': 'Error al validar contacto'}
            
            contactos_validos = [u['id'] for u in resultado_usuarios['usuarios']]
            if id_contacto not in contactos_validos:
                return {'success': False, 'message': 'Contacto no válido'}
            
            # Obtener mensajes
            resultado = ChatComponent.obtener_mensajes_conversacion(
                usuario_autenticado['id'],
                id_contacto,
                usuario_autenticado['id_centro'],
                limite
            )
            
            # Si hay mensajes, marcar los no leídos como leídos
            if resultado['success'] and resultado['mensajes']:
                ChatComponent.marcar_conversacion_leida(
                    usuario_autenticado['id'],
                    id_contacto,
                    usuario_autenticado['id_centro']
                )
            
            return resultado
            
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_mensajes_conversacion: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def marcar_mensaje_leido(id_mensaje, usuario_autenticado):
        """
        Marcar un mensaje específico como leído
        """
        try:
            if not isinstance(id_mensaje, int) or id_mensaje <= 0:
                return {'success': False, 'message': 'ID de mensaje inválido'}
            
            resultado = ChatComponent.marcar_mensaje_leido(
                id_mensaje, 
                usuario_autenticado['id']
            )
            
            return resultado
            
        except Exception as e:
            HandleLogs.write_error(f"Error en marcar_mensaje_leido: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def obtener_usuarios_disponibles(usuario_autenticado):
        """
        Obtener lista de usuarios disponibles para chat
        """
        try:
            resultado = ChatComponent.obtener_usuarios_disponibles(
                usuario_autenticado['id'],
                None,  # No filtrar por centro - mostrar todos los usuarios
                solo_activos=True
            )
            
            return resultado
            
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_usuarios_disponibles: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def obtener_estadisticas_mensajes(usuario_autenticado):
        """
        Obtener estadísticas de mensajes del usuario
        """
        try:
            resultado = ChatComponent.obtener_estadisticas_mensajes(
                usuario_autenticado['id'],
                usuario_autenticado['id_centro']
            )
            
            return resultado
            
        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_estadisticas_mensajes: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def buscar_mensajes(texto_busqueda, usuario_autenticado, id_contacto=None):
        """
        Buscar mensajes por contenido
        """
        try:
            # Validar texto de búsqueda
            if not texto_busqueda or not texto_busqueda.strip():
                return {'success': False, 'message': 'Texto de búsqueda requerido'}
            
            texto_busqueda = texto_busqueda.strip()
            if len(texto_busqueda) < 3:
                return {'success': False, 'message': 'El texto de búsqueda debe tener al menos 3 caracteres'}
            
            if len(texto_busqueda) > 100:
                return {'success': False, 'message': 'El texto de búsqueda no puede exceder 100 caracteres'}
            
            # Validar contacto si se proporciona
            if id_contacto is not None:
                if not isinstance(id_contacto, int) or id_contacto <= 0:
                    return {'success': False, 'message': 'ID de contacto inválido'}
                
                # Verificar que el contacto es válido
                resultado_usuarios = ChatComponent.obtener_usuarios_disponibles(
                    usuario_autenticado['id'],
                    None,  # No filtrar por centro
                    solo_activos=True
                )
                
                if not resultado_usuarios['success']:
                    return {'success': False, 'message': 'Error al validar contacto'}
                
                contactos_validos = [u['id'] for u in resultado_usuarios['usuarios']]
                if id_contacto not in contactos_validos:
                    return {'success': False, 'message': 'Contacto no válido'}
            
            # Sanitizar texto de búsqueda
            texto_sanitizado = ChatService._sanitizar_busqueda(texto_busqueda)
            
            resultado = ChatComponent.buscar_mensajes(
                usuario_autenticado['id'],
                usuario_autenticado['id_centro'],
                texto_sanitizado,
                id_contacto
            )
            
            return resultado
            
        except Exception as e:
            HandleLogs.write_error(f"Error en buscar_mensajes: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def _sanitizar_mensaje(mensaje):
        """
        Sanitizar contenido del mensaje
        """
        # Remover caracteres de control peligrosos
        mensaje = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', mensaje)
        
        # Normalizar espacios en blanco
        mensaje = re.sub(r'\s+', ' ', mensaje)
        
        # Remover HTML tags básicos (por seguridad)
        mensaje = re.sub(r'<[^>]*>', '', mensaje)
        
        return mensaje.strip()
    
    @staticmethod
    def _sanitizar_busqueda(texto):
        """
        Sanitizar texto de búsqueda
        """
        # Remover caracteres especiales de SQL
        texto = re.sub(r'[\'\"\\;]', '', texto)
        
        # Normalizar espacios
        texto = re.sub(r'\s+', ' ', texto)
        
        return texto.strip()
    
    @staticmethod
    def validar_permisos_chat(usuario_autenticado):
        """
        Validar que el usuario tiene permisos para usar el chat
        """
        try:
            # Todos los usuarios autenticados pueden usar el chat
            # Se puede expandir para validaciones específicas por rol
            
            if not usuario_autenticado:
                return {'success': False, 'message': 'Usuario no autenticado'}
            
            if usuario_autenticado.get('estado') != 'activo':
                return {'success': False, 'message': 'Usuario inactivo'}
            
            if not usuario_autenticado.get('id_centro'):
                return {'success': False, 'message': 'Usuario sin centro asignado'}
            
            return {'success': True, 'message': 'Permisos validados'}
            
        except Exception as e:
            HandleLogs.write_error(f"Error en validar_permisos_chat: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}