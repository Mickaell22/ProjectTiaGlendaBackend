"""
ObservacionesService.py
Lógica de negocio para el sistema de observaciones
Centro Tía Glenda - Sistema de Observaciones para Sesiones
"""

from src.api.Components.ObservacionesComponent import ObservacionesComponent
from src.utils.general.logger import Logger
from datetime import datetime, date
import re

logger = Logger()

class ObservacionesService:
    
    TIPOS_OBSERVACION_VALIDOS = [
        'observacion', 'falta', 'nota', 'incidente', 'progreso', 'recomendacion'
    ]
    
    ESTADOS_SEGUIMIENTO_VALIDOS = [
        'pendiente', 'en_proceso', 'completado', 'cancelado'
    ]
    
    @staticmethod
    def crear_observacion(data, usuario_autenticado):
        """
        Crear una nueva observación
        """
        try:
            # Validar datos requeridos
            validacion = ObservacionesService._validar_datos_observacion(data)
            if not validacion['success']:
                return validacion
            
            # Validar permisos para crear observación en la sesión
            permisos = ObservacionesService._validar_permisos_sesion(
                data['id_sesion'], 
                data['tipo_sesion'], 
                usuario_autenticado
            )
            if not permisos['success']:
                return permisos
            
            # Sanitizar contenido
            data_sanitizada = ObservacionesService._sanitizar_datos_observacion(data)
            
            # Crear observación
            resultado = ObservacionesComponent.crear_observacion(data_sanitizada, usuario_autenticado['id'])
            
            return resultado
            
        except Exception as e:
            logger.log_error(f"Error en crear_observacion: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def obtener_observaciones_sesion(id_sesion, tipo_sesion, usuario_autenticado, incluir_privadas=False):
        """
        Obtener observaciones de una sesión
        """
        try:
            # Validar parámetros
            if not isinstance(id_sesion, int) or id_sesion <= 0:
                return {'success': False, 'message': 'ID de sesión inválido'}
            
            if tipo_sesion not in ['terapeutica', 'pedagogica']:
                return {'success': False, 'message': 'Tipo de sesión inválido'}
            
            # Validar permisos para ver observaciones de la sesión
            permisos = ObservacionesService._validar_permisos_ver_sesion(
                id_sesion, 
                tipo_sesion, 
                usuario_autenticado
            )
            if not permisos['success']:
                return permisos
            
            # Solo administradores pueden ver observaciones privadas de otros
            if incluir_privadas and usuario_autenticado.get('rol') != 'administrador':
                incluir_privadas = False
            
            resultado = ObservacionesComponent.obtener_observaciones_sesion(
                id_sesion, 
                tipo_sesion, 
                usuario_autenticado['id'], 
                incluir_privadas
            )
            
            return resultado
            
        except Exception as e:
            logger.log_error(f"Error en obtener_observaciones_sesion: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def actualizar_observacion(id_observacion, data, usuario_autenticado):
        """
        Actualizar una observación existente
        """
        try:
            # Validar que la observación existe y el usuario tiene permisos
            permisos = ObservacionesService._validar_permisos_modificar_observacion(
                id_observacion, 
                usuario_autenticado
            )
            if not permisos['success']:
                return permisos
            
            # Validar datos de actualización
            if 'observacion' in data:
                if not data['observacion'] or not data['observacion'].strip():
                    return {'success': False, 'message': 'El contenido de la observación no puede estar vacío'}
                
                if len(data['observacion'].strip()) > 2000:
                    return {'success': False, 'message': 'El contenido no puede exceder 2000 caracteres'}
            
            if 'tipo_observacion' in data:
                if data['tipo_observacion'] not in ObservacionesService.TIPOS_OBSERVACION_VALIDOS:
                    return {'success': False, 'message': 'Tipo de observación inválido'}
            
            if 'estado_seguimiento' in data:
                if data['estado_seguimiento'] not in ObservacionesService.ESTADOS_SEGUIMIENTO_VALIDOS:
                    return {'success': False, 'message': 'Estado de seguimiento inválido'}
            
            if 'fecha_seguimiento' in data and data['fecha_seguimiento']:
                try:
                    fecha_seguimiento = datetime.strptime(data['fecha_seguimiento'], '%Y-%m-%d').date()
                    if fecha_seguimiento < date.today():
                        return {'success': False, 'message': 'La fecha de seguimiento no puede ser anterior a hoy'}
                    data['fecha_seguimiento'] = fecha_seguimiento
                except ValueError:
                    return {'success': False, 'message': 'Formato de fecha de seguimiento inválido (use YYYY-MM-DD)'}
            
            # Sanitizar datos
            data_sanitizada = {}
            for key, value in data.items():
                if key == 'observacion' and isinstance(value, str):
                    data_sanitizada[key] = ObservacionesService._sanitizar_texto(value)
                else:
                    data_sanitizada[key] = value
            
            resultado = ObservacionesComponent.actualizar_observacion(
                id_observacion, 
                data_sanitizada, 
                usuario_autenticado['id']
            )
            
            return resultado
            
        except Exception as e:
            logger.log_error(f"Error en actualizar_observacion: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def eliminar_observacion(id_observacion, usuario_autenticado):
        """
        Eliminar una observación
        """
        try:
            # Validar permisos para eliminar
            permisos = ObservacionesService._validar_permisos_modificar_observacion(
                id_observacion, 
                usuario_autenticado
            )
            if not permisos['success']:
                return permisos
            
            resultado = ObservacionesComponent.eliminar_observacion(
                id_observacion, 
                usuario_autenticado['id']
            )
            
            return resultado
            
        except Exception as e:
            logger.log_error(f"Error en eliminar_observacion: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def obtener_observacion_por_id(id_observacion, usuario_autenticado):
        """
        Obtener una observación específica por ID
        """
        try:
            if not isinstance(id_observacion, int) or id_observacion <= 0:
                return {'success': False, 'message': 'ID de observación inválido'}
            
            resultado = ObservacionesComponent.obtener_observacion_por_id(
                id_observacion, 
                usuario_autenticado['id']
            )
            
            return resultado
            
        except Exception as e:
            logger.log_error(f"Error en obtener_observacion_por_id: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def obtener_estadisticas_observaciones(usuario_autenticado, solo_propias=False):
        """
        Obtener estadísticas de observaciones
        """
        try:
            usuario_filtro = usuario_autenticado['id'] if solo_propias else None
            
            # Solo administradores pueden ver estadísticas globales del centro
            if not solo_propias and usuario_autenticado.get('rol') != 'administrador':
                usuario_filtro = usuario_autenticado['id']
            
            resultado = ObservacionesComponent.obtener_estadisticas_observaciones(
                usuario_filtro, 
                usuario_autenticado['id_centro']
            )
            
            return resultado
            
        except Exception as e:
            logger.log_error(f"Error en obtener_estadisticas_observaciones: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def obtener_seguimientos_pendientes(usuario_autenticado, solo_asignados=False):
        """
        Obtener observaciones con seguimiento pendiente
        """
        try:
            usuario_filtro = usuario_autenticado['id'] if solo_asignados else None
            
            resultado = ObservacionesComponent.obtener_observaciones_seguimiento_pendiente(
                usuario_autenticado['id_centro'],
                usuario_filtro
            )
            
            return resultado
            
        except Exception as e:
            logger.log_error(f"Error en obtener_seguimientos_pendientes: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def buscar_observaciones(criterios, usuario_autenticado):
        """
        Buscar observaciones con criterios específicos
        """
        try:
            # Validar criterios de búsqueda
            if not isinstance(criterios, dict):
                return {'success': False, 'message': 'Criterios de búsqueda inválidos'}
            
            # Sanitizar texto de búsqueda
            if 'texto' in criterios and criterios['texto']:
                if len(criterios['texto'].strip()) < 3:
                    return {'success': False, 'message': 'El texto de búsqueda debe tener al menos 3 caracteres'}
                criterios['texto'] = ObservacionesService._sanitizar_busqueda(criterios['texto'])
            
            # Validar tipos si se proporcionan
            if 'tipo_observacion' in criterios and criterios['tipo_observacion']:
                if criterios['tipo_observacion'] not in ObservacionesService.TIPOS_OBSERVACION_VALIDOS:
                    return {'success': False, 'message': 'Tipo de observación inválido'}
            
            if 'tipo_sesion' in criterios and criterios['tipo_sesion']:
                if criterios['tipo_sesion'] not in ['terapeutica', 'pedagogica']:
                    return {'success': False, 'message': 'Tipo de sesión inválido'}
            
            if 'estado_seguimiento' in criterios and criterios['estado_seguimiento']:
                if criterios['estado_seguimiento'] not in ObservacionesService.ESTADOS_SEGUIMIENTO_VALIDOS:
                    return {'success': False, 'message': 'Estado de seguimiento inválido'}
            
            # Validar fechas
            for campo_fecha in ['fecha_inicio', 'fecha_fin']:
                if campo_fecha in criterios and criterios[campo_fecha]:
                    try:
                        datetime.strptime(criterios[campo_fecha], '%Y-%m-%d')
                    except ValueError:
                        return {'success': False, 'message': f'Formato de {campo_fecha} inválido (use YYYY-MM-DD)'}
            
            # Solo administradores pueden buscar observaciones privadas de otros
            usuario_filtro = usuario_autenticado['id'] if usuario_autenticado.get('rol') != 'administrador' else None
            
            resultado = ObservacionesComponent.buscar_observaciones(
                criterios,
                usuario_autenticado['id_centro'],
                usuario_filtro
            )
            
            return resultado
            
        except Exception as e:
            logger.log_error(f"Error en buscar_observaciones: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}
    
    @staticmethod
    def _validar_datos_observacion(data):
        """
        Validar datos para crear observación
        """
        required_fields = ['id_sesion', 'tipo_sesion', 'observacion']
        for field in required_fields:
            if field not in data or not data[field]:
                return {'success': False, 'message': f'Campo requerido: {field}'}
        
        # Validar tipos
        if data['tipo_sesion'] not in ['terapeutica', 'pedagogica']:
            return {'success': False, 'message': 'Tipo de sesión inválido'}
        
        if not isinstance(data['id_sesion'], int) or data['id_sesion'] <= 0:
            return {'success': False, 'message': 'ID de sesión inválido'}
        
        # Validar contenido
        observacion = data['observacion'].strip()
        if len(observacion) == 0:
            return {'success': False, 'message': 'El contenido de la observación no puede estar vacío'}
        
        if len(observacion) > 2000:
            return {'success': False, 'message': 'El contenido no puede exceder 2000 caracteres'}
        
        # Validar tipo de observación si se proporciona
        if 'tipo_observacion' in data and data['tipo_observacion']:
            if data['tipo_observacion'] not in ObservacionesService.TIPOS_OBSERVACION_VALIDOS:
                return {'success': False, 'message': 'Tipo de observación inválido'}
        
        # Validar fecha de seguimiento si se proporciona
        if 'fecha_seguimiento' in data and data['fecha_seguimiento']:
            try:
                fecha_seguimiento = datetime.strptime(data['fecha_seguimiento'], '%Y-%m-%d').date()
                if fecha_seguimiento < date.today():
                    return {'success': False, 'message': 'La fecha de seguimiento no puede ser anterior a hoy'}
            except ValueError:
                return {'success': False, 'message': 'Formato de fecha de seguimiento inválido (use YYYY-MM-DD)'}
        
        return {'success': True}
    
    @staticmethod
    def _sanitizar_datos_observacion(data):
        """
        Sanitizar datos de observación
        """
        data_sanitizada = data.copy()
        
        # Sanitizar texto de observación
        data_sanitizada['observacion'] = ObservacionesService._sanitizar_texto(data['observacion'])
        
        return data_sanitizada
    
    @staticmethod
    def _sanitizar_texto(texto):
        """
        Sanitizar texto para prevenir ataques
        """
        # Remover caracteres de control
        texto = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', texto)
        
        # Normalizar espacios
        texto = re.sub(r'\s+', ' ', texto)
        
        # Remover HTML básico
        texto = re.sub(r'<[^>]*>', '', texto)
        
        return texto.strip()
    
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
    def _validar_permisos_sesion(id_sesion, tipo_sesion, usuario):
        """
        Validar permisos para crear observación en una sesión
        """
        try:
            from src.utils.database.database import DataBaseHandle
            
            db = DataBaseHandle()
            
            # Administradores pueden crear observaciones en cualquier sesión
            if usuario.get('rol') == 'administrador':
                return {'success': True}
            
            # Verificar que el usuario tiene relación con la sesión
            if tipo_sesion == 'terapeutica':
                # Debe ser el terapeuta de la sesión o tener pacientes en la sesión
                query = """
                    SELECT EXISTS(
                        SELECT 1 FROM sesion_terapia st
                        WHERE st.id = %s 
                        AND st.id_centro = %s
                        AND (
                            st.terapeuta_id = (
                                SELECT id FROM personal 
                                WHERE persona_id = (
                                    SELECT persona_id FROM usuario WHERE id = %s
                                )
                            )
                            OR EXISTS(
                                SELECT 1 FROM sesion_paciente sp
                                WHERE sp.sesion_terapia_id = st.id
                            )
                        )
                    ) as tiene_permisos
                """
            else:  # pedagogica
                # Debe ser el pedagogo de la sesión
                query = """
                    SELECT EXISTS(
                        SELECT 1 FROM sesion_pedagogica sp
                        WHERE sp.id = %s 
                        AND sp.id_centro = %s
                        AND sp.pedagogo_id = (
                            SELECT id FROM personal 
                            WHERE persona_id = (
                                SELECT persona_id FROM usuario WHERE id = %s
                            )
                        )
                    ) as tiene_permisos
                """
            
            resultado = db.getRecords(query, (id_sesion, usuario['id_centro'], usuario['id']))
            
            if resultado and resultado[0]['tiene_permisos']:
                return {'success': True}
            else:
                return {'success': False, 'message': 'No tienes permisos para crear observaciones en esta sesión'}
            
        except Exception as e:
            logger.log_error(f"Error validando permisos de sesión: {str(e)}")
            return {'success': False, 'message': 'Error validando permisos'}
    
    @staticmethod
    def _validar_permisos_ver_sesion(id_sesion, tipo_sesion, usuario):
        """
        Validar permisos para ver observaciones de una sesión
        """
        # Todos los usuarios del sistema pueden ver observaciones no privadas
        # La lógica de filtrado de privadas se maneja en el componente
        return {'success': True}
    
    @staticmethod
    def _validar_permisos_modificar_observacion(id_observacion, usuario):
        """
        Validar permisos para modificar/eliminar una observación
        """
        try:
            from src.utils.database.database import DataBaseHandle
            
            db = DataBaseHandle()
            
            # Verificar que la observación existe y obtener información
            query = """
                SELECT 
                    obs.id_usuario,
                    u.id_centro
                FROM observaciones_sesiones obs
                JOIN usuario u ON obs.id_usuario = u.id
                WHERE obs.id = %s
            """
            
            resultado = db.getRecords(query, (id_observacion,))
            
            if not resultado:
                return {'success': False, 'message': 'Observación no encontrada'}
            
            observacion_info = resultado[0]
            
            # Administradores pueden modificar cualquier observación de su centro
            if usuario.get('rol') == 'administrador' and observacion_info['id_centro'] == usuario['id_centro']:
                return {'success': True}
            
            # El autor puede modificar su propia observación
            if observacion_info['id_usuario'] == usuario['id']:
                return {'success': True}
            
            return {'success': False, 'message': 'No tienes permisos para modificar esta observación'}
            
        except Exception as e:
            logger.log_error(f"Error validando permisos de modificación: {str(e)}")
            return {'success': False, 'message': 'Error validando permisos'}
    
    @staticmethod
    def obtener_tipos_observacion():
        """
        Obtener tipos de observación disponibles
        """
        return {
            'success': True,
            'tipos_observacion': [
                {'valor': 'observacion', 'etiqueta': 'Observación General'},
                {'valor': 'falta', 'etiqueta': 'Falta/Ausencia'},
                {'valor': 'nota', 'etiqueta': 'Nota Importante'},
                {'valor': 'incidente', 'etiqueta': 'Incidente'},
                {'valor': 'progreso', 'etiqueta': 'Nota de Progreso'},
                {'valor': 'recomendacion', 'etiqueta': 'Recomendación'}
            ],
            'estados_seguimiento': [
                {'valor': 'pendiente', 'etiqueta': 'Pendiente'},
                {'valor': 'en_proceso', 'etiqueta': 'En Proceso'},
                {'valor': 'completado', 'etiqueta': 'Completado'},
                {'valor': 'cancelado', 'etiqueta': 'Cancelado'}
            ]
        }