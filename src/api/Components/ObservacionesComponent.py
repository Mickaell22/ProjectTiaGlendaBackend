"""
ObservacionesComponent.py
Manejo de operaciones de base de datos para el sistema de observaciones
Centro Tía Glenda - Sistema de Observaciones para Sesiones
"""

from src.utils.database.database import DataBaseHandle
from src.utils.general.logger import Logger
from datetime import datetime, date
import json

logger = Logger()

class ObservacionesComponent:
    
    @staticmethod
    def crear_observacion(data, usuario_creacion):
        """
        Crear una nueva observación para una sesión
        """
        try:
            db = DataBaseHandle()
            
            query = """
                INSERT INTO observaciones_sesiones (
                    id_sesion, tipo_sesion, id_cronograma, id_usuario, observacion, 
                    tipo_observacion, es_privada, es_critica, requiere_seguimiento,
                    fecha_seguimiento, id_usuario_seguimiento, usuario_creacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, fecha_registro
            """
            
            params = (
                data['id_sesion'],
                data['tipo_sesion'], 
                data.get('id_cronograma'),
                usuario_creacion,
                data['observacion'],
                data.get('tipo_observacion', 'observacion'),
                data.get('es_privada', False),
                data.get('es_critica', False),
                data.get('requiere_seguimiento', False),
                data.get('fecha_seguimiento'),
                data.get('id_usuario_seguimiento'),
                usuario_creacion
            )
            
            resultado = db.getRecords(query, params)
            
            if resultado:
                return {
                    'success': True,
                    'id_observacion': resultado[0]['id'],
                    'fecha_registro': resultado[0]['fecha_registro'].isoformat() if resultado[0]['fecha_registro'] else None
                }
            else:
                return {'success': False, 'message': 'Error al crear observación'}
                
        except Exception as e:
            logger.log_error(f"Error en crear_observacion: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def obtener_observaciones_sesion(id_sesion, tipo_sesion, usuario_solicitante, incluir_privadas=False):
        """
        Obtener observaciones de una sesión específica
        """
        try:
            db = DataBaseHandle()
            
            query = """
                SELECT * FROM obtener_observaciones_sesion(%s, %s, %s, %s)
            """
            
            params = (id_sesion, tipo_sesion, usuario_solicitante, incluir_privadas)
            resultado = db.getRecords(query, params)
            
            if resultado:
                observaciones = []
                for obs in resultado:
                    observacion = dict(obs)
                    # Convertir fechas a string para serialización JSON
                    if 'fecha_registro' in observacion and observacion['fecha_registro']:
                        observacion['fecha_registro'] = observacion['fecha_registro'].isoformat()
                    if 'fecha_seguimiento' in observacion and observacion['fecha_seguimiento']:
                        observacion['fecha_seguimiento'] = observacion['fecha_seguimiento'].isoformat()
                    observaciones.append(observacion)
                
                return {
                    'success': True,
                    'observaciones': observaciones
                }
            else:
                return {
                    'success': True,
                    'observaciones': []
                }
                
        except Exception as e:
            logger.log_error(f"Error en obtener_observaciones_sesion: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def actualizar_observacion(id_observacion, data, usuario_modificacion):
        """
        Actualizar una observación existente
        """
        try:
            db = DataBaseHandle()
            
            # Construir query dinámicamente basado en los campos proporcionados
            campos_actualizar = []
            parametros = []
            
            if 'observacion' in data:
                campos_actualizar.append("observacion = %s")
                parametros.append(data['observacion'])
            
            if 'tipo_observacion' in data:
                campos_actualizar.append("tipo_observacion = %s")
                parametros.append(data['tipo_observacion'])
            
            if 'es_privada' in data:
                campos_actualizar.append("es_privada = %s")
                parametros.append(data['es_privada'])
            
            if 'es_critica' in data:
                campos_actualizar.append("es_critica = %s")
                parametros.append(data['es_critica'])
            
            if 'requiere_seguimiento' in data:
                campos_actualizar.append("requiere_seguimiento = %s")
                parametros.append(data['requiere_seguimiento'])
            
            if 'fecha_seguimiento' in data:
                campos_actualizar.append("fecha_seguimiento = %s")
                parametros.append(data['fecha_seguimiento'])
            
            if 'id_usuario_seguimiento' in data:
                campos_actualizar.append("id_usuario_seguimiento = %s")
                parametros.append(data['id_usuario_seguimiento'])
            
            if 'estado_seguimiento' in data:
                campos_actualizar.append("estado_seguimiento = %s")
                parametros.append(data['estado_seguimiento'])
            
            if not campos_actualizar:
                return {'success': False, 'message': 'No se proporcionaron campos para actualizar'}
            
            # Agregar campos de auditoría
            campos_actualizar.append("usuario_modificacion = %s")
            parametros.append(usuario_modificacion)
            
            # Agregar WHERE clause
            parametros.append(id_observacion)
            
            query = f"""
                UPDATE observaciones_sesiones 
                SET {', '.join(campos_actualizar)}
                WHERE id = %s
                RETURNING fecha_modificacion
            """
            
            resultado = db.getRecords(query, parametros)
            
            if resultado:
                return {
                    'success': True,
                    'fecha_modificacion': resultado[0]['fecha_modificacion'].isoformat() if resultado[0]['fecha_modificacion'] else None
                }
            else:
                return {'success': False, 'message': 'Observación no encontrada o no se pudo actualizar'}
                
        except Exception as e:
            logger.log_error(f"Error en actualizar_observacion: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def eliminar_observacion(id_observacion, usuario_modificacion):
        """
        Eliminar una observación (solo el autor o administradores)
        """
        try:
            db = DataBaseHandle()
            
            query = """
                DELETE FROM observaciones_sesiones 
                WHERE id = %s
                RETURNING id
            """
            
            resultado = db.getRecords(query, (id_observacion,))
            
            if resultado:
                return {'success': True, 'message': 'Observación eliminada exitosamente'}
            else:
                return {'success': False, 'message': 'Observación no encontrada'}
                
        except Exception as e:
            logger.log_error(f"Error en eliminar_observacion: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def obtener_observacion_por_id(id_observacion, usuario_solicitante):
        """
        Obtener una observación específica por ID
        """
        try:
            db = DataBaseHandle()
            
            query = """
                SELECT 
                    obs.id,
                    obs.id_sesion,
                    obs.tipo_sesion,
                    obs.id_cronograma,
                    obs.id_usuario,
                    obs.observacion,
                    obs.tipo_observacion,
                    obs.es_privada,
                    obs.es_critica,
                    obs.requiere_seguimiento,
                    obs.fecha_seguimiento,
                    obs.id_usuario_seguimiento,
                    obs.estado_seguimiento,
                    obs.fecha_registro,
                    obs.fecha_creacion,
                    obs.fecha_modificacion,
                    CONCAT(p_autor.nombre, ' ', p_autor.apellido) as autor_nombre,
                    CONCAT(p_seguimiento.nombre, ' ', p_seguimiento.apellido) as usuario_seguimiento_nombre
                FROM observaciones_sesiones obs
                JOIN usuario u_autor ON obs.id_usuario = u_autor.id
                JOIN persona p_autor ON u_autor.id_persona = p_autor.id
                LEFT JOIN usuario u_seguimiento ON obs.id_usuario_seguimiento = u_seguimiento.id
                LEFT JOIN persona p_seguimiento ON u_seguimiento.id_persona = p_seguimiento.id
                WHERE obs.id = %s
                AND (
                    NOT obs.es_privada 
                    OR obs.id_usuario = %s
                )
            """
            
            resultado = db.getRecords(query, (id_observacion, usuario_solicitante))
            
            if resultado:
                observacion = dict(resultado[0])
                
                # Convertir fechas a string
                for campo_fecha in ['fecha_registro', 'fecha_creacion', 'fecha_modificacion']:
                    if campo_fecha in observacion and observacion[campo_fecha]:
                        observacion[campo_fecha] = observacion[campo_fecha].isoformat()
                
                if 'fecha_seguimiento' in observacion and observacion['fecha_seguimiento']:
                    observacion['fecha_seguimiento'] = observacion['fecha_seguimiento'].isoformat()
                
                return {
                    'success': True,
                    'observacion': observacion
                }
            else:
                return {'success': False, 'message': 'Observación no encontrada o sin permisos'}
                
        except Exception as e:
            logger.log_error(f"Error en obtener_observacion_por_id: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def obtener_estadisticas_observaciones(usuario_id=None, id_centro=None):
        """
        Obtener estadísticas de observaciones
        """
        try:
            db = DataBaseHandle()
            
            query = """
                SELECT * FROM obtener_estadisticas_observaciones(%s, %s)
            """
            
            resultado = db.getRecords(query, (usuario_id, id_centro))
            
            if resultado:
                stats = dict(resultado[0])
                
                # Convertir JSONB a dict si existe
                if 'observaciones_por_tipo' in stats and stats['observaciones_por_tipo']:
                    if isinstance(stats['observaciones_por_tipo'], str):
                        stats['observaciones_por_tipo'] = json.loads(stats['observaciones_por_tipo'])
                
                return {
                    'success': True,
                    'estadisticas': stats
                }
            else:
                return {
                    'success': True,
                    'estadisticas': {
                        'total_observaciones': 0,
                        'observaciones_criticas': 0,
                        'observaciones_seguimiento_pendiente': 0,
                        'observaciones_por_tipo': {}
                    }
                }
                
        except Exception as e:
            logger.log_error(f"Error en obtener_estadisticas_observaciones: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def obtener_observaciones_seguimiento_pendiente(id_centro, usuario_id=None):
        """
        Obtener observaciones que requieren seguimiento pendiente
        """
        try:
            db = DataBaseHandle()
            
            usuario_filter = "AND obs.id_usuario_seguimiento = %s" if usuario_id else ""
            params = [id_centro]
            if usuario_id:
                params.append(usuario_id)
            
            query = f"""
                SELECT 
                    obs.id,
                    obs.id_sesion,
                    obs.tipo_sesion,
                    obs.observacion,
                    obs.tipo_observacion,
                    obs.es_critica,
                    obs.fecha_seguimiento,
                    obs.fecha_registro,
                    CONCAT(p_autor.nombre, ' ', p_autor.apellido) as autor_nombre,
                    CONCAT(p_seguimiento.nombre, ' ', p_seguimiento.apellido) as usuario_seguimiento_nombre,
                    -- Información de la sesión
                    CASE 
                        WHEN obs.tipo_sesion = 'terapeutica' THEN st.titulo
                        WHEN obs.tipo_sesion = 'pedagogica' THEN sp.titulo
                    END as titulo_sesion
                FROM observaciones_sesiones obs
                JOIN usuario u_autor ON obs.id_usuario = u_autor.id
                JOIN persona p_autor ON u_autor.id_persona = p_autor.id
                LEFT JOIN usuario u_seguimiento ON obs.id_usuario_seguimiento = u_seguimiento.id
                LEFT JOIN persona p_seguimiento ON u_seguimiento.id_persona = p_seguimiento.id
                LEFT JOIN sesion_terapia st ON (obs.tipo_sesion = 'terapeutica' AND obs.id_sesion = st.id)
                LEFT JOIN sesion_pedagogica sp ON (obs.tipo_sesion = 'pedagogica' AND obs.id_sesion = sp.id)
                WHERE obs.requiere_seguimiento = TRUE
                AND obs.estado_seguimiento = 'pendiente'
                AND u_autor.id_centro = %s
                {usuario_filter}
                ORDER BY 
                    obs.es_critica DESC,
                    obs.fecha_seguimiento ASC NULLS LAST,
                    obs.fecha_registro DESC
            """
            
            resultado = db.getRecords(query, params)
            
            if resultado:
                observaciones = []
                for obs in resultado:
                    observacion = dict(obs)
                    # Convertir fechas a string
                    if 'fecha_registro' in observacion and observacion['fecha_registro']:
                        observacion['fecha_registro'] = observacion['fecha_registro'].isoformat()
                    if 'fecha_seguimiento' in observacion and observacion['fecha_seguimiento']:
                        observacion['fecha_seguimiento'] = observacion['fecha_seguimiento'].isoformat()
                    observaciones.append(observacion)
                
                return {
                    'success': True,
                    'observaciones_pendientes': observaciones
                }
            else:
                return {
                    'success': True,
                    'observaciones_pendientes': []
                }
                
        except Exception as e:
            logger.log_error(f"Error en obtener_observaciones_seguimiento_pendiente: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}
    
    @staticmethod
    def buscar_observaciones(criterios_busqueda, id_centro, usuario_id=None):
        """
        Buscar observaciones con múltiples criterios
        """
        try:
            db = DataBaseHandle()
            
            filtros = []
            params = []
            
            # Filtro base por centro
            filtros.append("u_autor.id_centro = %s")
            params.append(id_centro)
            
            # Filtro por usuario si se proporciona
            if usuario_id:
                filtros.append("(obs.id_usuario = %s OR NOT obs.es_privada)")
                params.append(usuario_id)
            else:
                filtros.append("NOT obs.es_privada")
            
            # Filtros opcionales
            if criterios_busqueda.get('texto'):
                filtros.append("obs.observacion ILIKE %s")
                params.append(f"%{criterios_busqueda['texto']}%")
            
            if criterios_busqueda.get('tipo_observacion'):
                filtros.append("obs.tipo_observacion = %s")
                params.append(criterios_busqueda['tipo_observacion'])
            
            if criterios_busqueda.get('tipo_sesion'):
                filtros.append("obs.tipo_sesion = %s")
                params.append(criterios_busqueda['tipo_sesion'])
            
            if criterios_busqueda.get('es_critica') is not None:
                filtros.append("obs.es_critica = %s")
                params.append(criterios_busqueda['es_critica'])
            
            if criterios_busqueda.get('requiere_seguimiento') is not None:
                filtros.append("obs.requiere_seguimiento = %s")
                params.append(criterios_busqueda['requiere_seguimiento'])
            
            if criterios_busqueda.get('estado_seguimiento'):
                filtros.append("obs.estado_seguimiento = %s")
                params.append(criterios_busqueda['estado_seguimiento'])
            
            # Filtro por rango de fechas
            if criterios_busqueda.get('fecha_inicio'):
                filtros.append("obs.fecha_registro >= %s")
                params.append(criterios_busqueda['fecha_inicio'])
            
            if criterios_busqueda.get('fecha_fin'):
                filtros.append("obs.fecha_registro <= %s")
                params.append(criterios_busqueda['fecha_fin'])
            
            where_clause = " AND ".join(filtros)
            
            query = f"""
                SELECT 
                    obs.id,
                    obs.id_sesion,
                    obs.tipo_sesion,
                    obs.observacion,
                    obs.tipo_observacion,
                    obs.es_privada,
                    obs.es_critica,
                    obs.requiere_seguimiento,
                    obs.estado_seguimiento,
                    obs.fecha_registro,
                    CONCAT(p_autor.nombre, ' ', p_autor.apellido) as autor_nombre,
                    -- Información de la sesión
                    CASE 
                        WHEN obs.tipo_sesion = 'terapeutica' THEN st.titulo
                        WHEN obs.tipo_sesion = 'pedagogica' THEN sp.titulo
                    END as titulo_sesion
                FROM observaciones_sesiones obs
                JOIN usuario u_autor ON obs.id_usuario = u_autor.id
                JOIN persona p_autor ON u_autor.id_persona = p_autor.id
                LEFT JOIN sesion_terapia st ON (obs.tipo_sesion = 'terapeutica' AND obs.id_sesion = st.id)
                LEFT JOIN sesion_pedagogica sp ON (obs.tipo_sesion = 'pedagogica' AND obs.id_sesion = sp.id)
                WHERE {where_clause}
                ORDER BY obs.fecha_registro DESC
                LIMIT 100
            """
            
            resultado = db.getRecords(query, params)
            
            if resultado:
                observaciones = []
                for obs in resultado:
                    observacion = dict(obs)
                    if 'fecha_registro' in observacion and observacion['fecha_registro']:
                        observacion['fecha_registro'] = observacion['fecha_registro'].isoformat()
                    observaciones.append(observacion)
                
                return {
                    'success': True,
                    'observaciones': observaciones
                }
            else:
                return {
                    'success': True,
                    'observaciones': []
                }
                
        except Exception as e:
            logger.log_error(f"Error en buscar_observaciones: {str(e)}")
            return {'success': False, 'message': f'Error interno: {str(e)}'}