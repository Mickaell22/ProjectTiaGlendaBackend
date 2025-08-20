from src.utils.general.logs import HandleLogs
from src.utils.database.connection_db import DataBaseHandle


class DocumentoPacienteComponent:

    @staticmethod
    def create_documento(documento_data):
        """Crear un nuevo documento para un paciente"""
        try:
            HandleLogs.write_log("DocumentoPacienteComponent.create_documento - Iniciando")
            
            query = """
                INSERT INTO documentos_paciente (
                    id_paciente, nombre_archivo, ruta_archivo,
                    tipo_documento, tamaño_archivo, tipo_mime, descripcion, 
                    usuario_creacion
                ) VALUES (
                    %(id_paciente)s, %(nombre_archivo)s, %(ruta_archivo)s,
                    %(tipo_documento)s, %(tamaño_archivo)s, %(tipo_mime)s, %(descripcion)s,
                    %(usuario_creacion)s
                )
            """

            result = DataBaseHandle.ExecuteNonQuery(query, documento_data)

            if result:
                HandleLogs.write_log("DocumentoPacienteComponent.create_documento - Documento creado exitosamente")
                # Obtener el ID del documento insertado
                query_id = "SELECT id FROM documentos_paciente WHERE id_paciente = %(id_paciente)s AND nombre_archivo = %(nombre_archivo)s ORDER BY fecha_creacion DESC LIMIT 1"
                id_result = DataBaseHandle.getRecords(query_id, {'id_paciente': documento_data['id_paciente'], 'nombre_archivo': documento_data['nombre_archivo']})
                
                documento_id = id_result[0]['id'] if id_result else None
                return {
                    'success': True,
                    'data': {'id': documento_id, **documento_data},
                    'message': 'Documento creado correctamente'
                }
            else:
                HandleLogs.write_error("DocumentoPacienteComponent.create_documento - Error en inserción")
                return {
                    'success': False,
                    'data': None,
                    'message': 'Error creando documento'
                }

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteComponent.create_documento - Error: {str(e)}")
            return {
                'success': False,
                'data': None,
                'message': f'Error interno: {str(e)}'
            }

    @staticmethod
    def get_documentos_by_paciente(paciente_id):
        """Obtener todos los documentos de un paciente"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteComponent.get_documentos_by_paciente - Paciente ID: {paciente_id}")
            
            query = """
                SELECT 
                    dp.id,
                    dp.id_paciente,
                    dp.nombre_archivo,
                    dp.nombre_archivo as nombre_original,
                    dp.ruta_archivo,
                    dp.tipo_documento,
                    dp.tamaño_archivo,
                    dp.tipo_mime,
                    dp.descripcion,
                    dp.fecha_creacion,
                    dp.fecha_modificacion,
                    u_creacion.usuario as usuario_creacion_nombre,
                    u_modificacion.usuario as usuario_modificacion_nombre
                FROM documentos_paciente dp
                LEFT JOIN usuario u_creacion ON dp.usuario_creacion = u_creacion.id
                LEFT JOIN usuario u_modificacion ON dp.usuario_modificacion = u_modificacion.id
                WHERE dp.id_paciente = %(paciente_id)s 
                ORDER BY dp.fecha_creacion DESC
            """

            result = DataBaseHandle.getRecordsWithStatus(query, {'paciente_id': paciente_id})

            if result['success']:
                # Formatear datos para JSON
                documentos = []
                for doc in result['data']:
                    documento = dict(doc)
                    # Convertir tipos Python a formatos JSON
                    if documento.get('fecha_vencimiento'):
                        documento['fecha_vencimiento'] = documento['fecha_vencimiento'].isoformat()
                    if documento.get('fecha_creacion'):
                        documento['fecha_creacion'] = documento['fecha_creacion'].isoformat()
                    if documento.get('fecha_modificacion'):
                        documento['fecha_modificacion'] = documento['fecha_modificacion'].isoformat()
                    
                    documentos.append(documento)

                HandleLogs.write_log(f"DocumentoPacienteComponent.get_documentos_by_paciente - {len(documentos)} documentos encontrados")
                return {
                    'success': True,
                    'data': documentos,
                    'message': f'Documentos obtenidos correctamente'
                }
            else:
                HandleLogs.write_log(f"DocumentoPacienteComponent.get_documentos_by_paciente - Sin documentos para paciente {paciente_id}")
                return {
                    'success': True,
                    'data': [],
                    'message': 'No se encontraron documentos'
                }

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteComponent.get_documentos_by_paciente - Error: {str(e)}")
            return {
                'success': False,
                'data': [],
                'message': f'Error interno: {str(e)}'
            }

    @staticmethod
    def get_documento_by_id(documento_id, paciente_id):
        """Obtener un documento específico por ID"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteComponent.get_documento_by_id - ID: {documento_id}")
            
            query = """
                SELECT 
                    dp.id,
                    dp.id_paciente,
                    dp.nombre_archivo,
                    dp.nombre_archivo as nombre_original,
                    dp.ruta_archivo,
                    dp.tipo_documento,
                    dp.tamaño_archivo,
                    dp.tipo_mime,
                    dp.descripcion,
                    dp.fecha_creacion,
                    dp.fecha_modificacion
                FROM documentos_paciente dp
                WHERE dp.id = %(documento_id)s 
                  AND dp.id_paciente = %(paciente_id)s
            """

            result = DataBaseHandle.getRecordsWithStatus(query, {
                'documento_id': documento_id,
                'paciente_id': paciente_id
            })

            if result['success'] and result['data']:
                documento = dict(result['data'][0])
                # Convertir fechas a formato ISO
                if documento.get('fecha_vencimiento'):
                    documento['fecha_vencimiento'] = documento['fecha_vencimiento'].isoformat()
                if documento.get('fecha_creacion'):
                    documento['fecha_creacion'] = documento['fecha_creacion'].isoformat()
                if documento.get('fecha_modificacion'):
                    documento['fecha_modificacion'] = documento['fecha_modificacion'].isoformat()
                
                return {
                    'success': True,
                    'data': documento,
                    'message': 'Documento encontrado'
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': 'Documento no encontrado'
                }

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteComponent.get_documento_by_id - Error: {str(e)}")
            return {
                'success': False,
                'data': None,
                'message': f'Error interno: {str(e)}'
            }

    @staticmethod
    def update_documento(documento_id, paciente_id, datos):
        """Actualizar información de un documento"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteComponent.update_documento - ID: {documento_id}")
            
            query = """
                UPDATE documentos_paciente 
                SET 
                    tipo_documento = %(tipo_documento)s,
                    descripcion = %(descripcion)s,
                    usuario_modificacion = %(usuario_modificacion)s,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %(documento_id)s 
                  AND id_paciente = %(paciente_id)s
            """
            
            parametros = {
                'documento_id': documento_id,
                'paciente_id': paciente_id,
                **datos
            }

            result = DataBaseHandle.ExecuteNonQuery(query, parametros)

            if result:
                HandleLogs.write_log(f"DocumentoPacienteComponent.update_documento - Documento actualizado")
                return {
                    'success': True,
                    'data': {'id': documento_id},
                    'message': 'Documento actualizado correctamente'
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': 'Error actualizando documento'
                }

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteComponent.update_documento - Error: {str(e)}")
            return {
                'success': False,
                'data': None,
                'message': f'Error interno: {str(e)}'
            }

    @staticmethod
    def delete_documento(documento_id, paciente_id):
        """Eliminar (marcar como eliminado) un documento"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteComponent.delete_documento - ID: {documento_id}")
            
            query = """
                UPDATE documentos_paciente 
                SET 
                    estado = 'eliminado',
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %(documento_id)s 
                  AND id_paciente = %(paciente_id)s
            """

            result = DataBaseHandle.ExecuteNonQuery(query, {
                'documento_id': documento_id,
                'paciente_id': paciente_id
            })

            if result:
                HandleLogs.write_log(f"DocumentoPacienteComponent.delete_documento - Documento eliminado")
                return {
                    'success': True,
                    'data': {'id': documento_id},
                    'message': 'Documento eliminado correctamente'
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': 'Error eliminando documento'
                }

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteComponent.delete_documento - Error: {str(e)}")
            return {
                'success': False,
                'data': None,
                'message': f'Error interno: {str(e)}'
            }

    @staticmethod
    def get_estadisticas_documentos():
        """Obtener estadísticas de documentos"""
        try:
            HandleLogs.write_log("DocumentoPacienteComponent.get_estadisticas_documentos - Iniciando")
            
            query = """
                SELECT 
                    COUNT(*) as total_documentos,
                    COUNT(*) as documentos_activos,
                    0 as documentos_confidenciales,
                    tipo_documento,
                    COUNT(*) as cantidad_por_tipo
                FROM documentos_paciente dp
                GROUP BY tipo_documento
            """

            result = DataBaseHandle.getRecordsWithStatus(query, {})

            if result['success']:
                estadisticas = []
                for row in result['data']:
                    estadisticas.append(dict(row))

                return {
                    'success': True,
                    'data': estadisticas,
                    'message': 'Estadísticas obtenidas correctamente'
                }
            else:
                return {
                    'success': True,
                    'data': [],
                    'message': 'Sin datos de estadísticas'
                }

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteComponent.get_estadisticas_documentos - Error: {str(e)}")
            return {
                'success': False,
                'data': [],
                'message': f'Error interno: {str(e)}'
            }