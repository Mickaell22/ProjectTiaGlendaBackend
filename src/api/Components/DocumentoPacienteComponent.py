from src.utils.general.logs import HandleLogs
from src.utils.database.database import DataBaseHandle


class DocumentoPacienteComponent:

    @staticmethod
    def create_documento(documento_data):
        """Crear un nuevo documento para un paciente"""
        try:
            HandleLogs.write_log("DocumentoPacienteComponent.create_documento - Iniciando")

            db = DataBaseHandle()
            
            query = """
                INSERT INTO documentos_paciente (
                    paciente_id, nombre_archivo, nombre_original, ruta_archivo,
                    tipo_documento, tamaño_archivo, tipo_mime, descripcion,
                    es_confidencial, fecha_vencimiento, usuario_creacion
                ) VALUES (
                    %(paciente_id)s, %(nombre_archivo)s, %(nombre_original)s, %(ruta_archivo)s,
                    %(tipo_documento)s, %(tamaño_archivo)s, %(tipo_mime)s, %(descripcion)s,
                    %(es_confidencial)s, %(fecha_vencimiento)s, %(usuario_creacion)s
                ) RETURNING id
            """

            result = db.ExecuteNonQuery(query, documento_data)
            db.close()

            if result:
                HandleLogs.write_log("DocumentoPacienteComponent.create_documento - Documento creado exitosamente")
                # Obtener el ID del documento insertado
                query_id = "SELECT id FROM documentos_paciente WHERE paciente_id = %(paciente_id)s AND nombre_archivo = %(nombre_archivo)s ORDER BY fecha_creacion DESC LIMIT 1"
                db_id = DataBaseHandle()
                id_result = db_id.getRecords(query_id, {'paciente_id': documento_data['paciente_id'], 'nombre_archivo': documento_data['nombre_archivo']})
                db_id.close()
                
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

            db = DataBaseHandle()
            
            query = """
                SELECT 
                    dp.id,
                    dp.paciente_id,
                    dp.nombre_archivo,
                    dp.nombre_original,
                    dp.ruta_archivo,
                    dp.tipo_documento,
                    dp.tamaño_archivo,
                    dp.tipo_mime,
                    dp.descripcion,
                    dp.es_confidencial,
                    dp.fecha_vencimiento,
                    dp.estado,
                    dp.fecha_creacion,
                    dp.fecha_modificacion,
                    u_creacion.usuario as usuario_creacion_nombre,
                    u_modificacion.usuario as usuario_modificacion_nombre
                FROM documentos_paciente dp
                LEFT JOIN usuario u_creacion ON dp.usuario_creacion = u_creacion.id
                LEFT JOIN usuario u_modificacion ON dp.usuario_modificacion = u_modificacion.id
                WHERE dp.paciente_id = %(paciente_id)s 
                  AND dp.estado != 'eliminado'
                ORDER BY dp.fecha_creacion DESC
            """

            result = db.getRecordsWithStatus(query, {'paciente_id': paciente_id})
            db.close()

            if result['success']:
                # Formatear datos para JSON
                documentos = []
                for doc in result['data']:
                    documento_formateado = dict(doc)
                    # Convertir campos de fecha y hora a string para JSON
                    if documento_formateado.get('fecha_creacion'):
                        documento_formateado['fecha_creacion'] = str(documento_formateado['fecha_creacion'])
                    if documento_formateado.get('fecha_modificacion'):
                        documento_formateado['fecha_modificacion'] = str(documento_formateado['fecha_modificacion'])
                    if documento_formateado.get('fecha_vencimiento'):
                        documento_formateado['fecha_vencimiento'] = str(documento_formateado['fecha_vencimiento'])
                    
                    documentos.append(documento_formateado)

                HandleLogs.write_log(f"DocumentoPacienteComponent.get_documentos_by_paciente - {len(documentos)} documentos encontrados")
                return {
                    'success': True,
                    'data': documentos,
                    'message': 'Documentos obtenidos correctamente'
                }
            else:
                return result

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteComponent.get_documentos_by_paciente - Error: {str(e)}")
            return {
                'success': False,
                'data': None,
                'message': f'Error interno: {str(e)}'
            }

    @staticmethod
    def get_documento_by_id(documento_id, paciente_id):
        """Obtener un documento específico por ID y paciente"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteComponent.get_documento_by_id - Doc ID: {documento_id}, Paciente: {paciente_id}")

            db = DataBaseHandle()
            
            query = """
                SELECT 
                    dp.id,
                    dp.paciente_id,
                    dp.nombre_archivo,
                    dp.nombre_original,
                    dp.ruta_archivo,
                    dp.tipo_documento,
                    dp.tamaño_archivo,
                    dp.tipo_mime,
                    dp.descripcion,
                    dp.es_confidencial,
                    dp.fecha_vencimiento,
                    dp.estado,
                    dp.fecha_creacion,
                    dp.fecha_modificacion
                FROM documentos_paciente dp
                WHERE dp.id = %(documento_id)s 
                  AND dp.paciente_id = %(paciente_id)s
                  AND dp.estado != 'eliminado'
            """

            result = db.getRecordsWithStatus(query, {
                'documento_id': documento_id,
                'paciente_id': paciente_id
            })
            db.close()

            if result['success'] and result['data']:
                documento = dict(result['data'][0])
                # Convertir campos de fecha y hora a string para JSON
                if documento.get('fecha_creacion'):
                    documento['fecha_creacion'] = str(documento['fecha_creacion'])
                if documento.get('fecha_modificacion'):
                    documento['fecha_modificacion'] = str(documento['fecha_modificacion'])
                if documento.get('fecha_vencimiento'):
                    documento['fecha_vencimiento'] = str(documento['fecha_vencimiento'])

                HandleLogs.write_log(f"DocumentoPacienteComponent.get_documento_by_id - Documento encontrado")
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
    def update_documento(documento_id, paciente_id, documento_data):
        """Actualizar información de un documento"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteComponent.update_documento - Doc ID: {documento_id}, Paciente: {paciente_id}")

            db = DataBaseHandle()
            
            # Construir query dinámicamente basado en los campos proporcionados
            campos_update = []
            parametros = {'documento_id': documento_id, 'paciente_id': paciente_id}
            
            campos_permitidos = ['tipo_documento', 'descripcion', 'es_confidencial', 'fecha_vencimiento', 'estado']
            
            for campo in campos_permitidos:
                if campo in documento_data:
                    campos_update.append(f"{campo} = %({campo})s")
                    parametros[campo] = documento_data[campo]
            
            if 'usuario_modificacion' in documento_data:
                campos_update.append("usuario_modificacion = %(usuario_modificacion)s")
                parametros['usuario_modificacion'] = documento_data['usuario_modificacion']
            
            if not campos_update:
                return {
                    'success': False,
                    'data': None,
                    'message': 'No hay campos para actualizar'
                }

            query = f"""
                UPDATE documentos_paciente 
                SET {', '.join(campos_update)}
                WHERE id = %(documento_id)s 
                  AND paciente_id = %(paciente_id)s
                  AND estado != 'eliminado'
            """

            result = db.ExecuteNonQuery(query, parametros)
            db.close()

            if result:
                HandleLogs.write_log(f"DocumentoPacienteComponent.update_documento - Documento actualizado")
                return {
                    'success': True,
                    'data': {'id': documento_id, **documento_data},
                    'message': 'Documento actualizado correctamente'
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': 'Error actualizando documento o documento no encontrado'
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
            HandleLogs.write_log(f"DocumentoPacienteComponent.delete_documento - Doc ID: {documento_id}, Paciente: {paciente_id}")

            db = DataBaseHandle()
            
            query = """
                UPDATE documentos_paciente 
                SET estado = 'eliminado'
                WHERE id = %(documento_id)s 
                  AND paciente_id = %(paciente_id)s
                  AND estado != 'eliminado'
            """

            result = db.ExecuteNonQuery(query, {
                'documento_id': documento_id,
                'paciente_id': paciente_id
            })
            db.close()

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
                    'message': 'Error eliminando documento o documento no encontrado'
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
        """Obtener estadísticas de documentos por tipo"""
        try:
            HandleLogs.write_log("DocumentoPacienteComponent.get_estadisticas_documentos - Iniciando")

            db = DataBaseHandle()
            
            query = """
                SELECT 
                    tipo_documento,
                    COUNT(*) as total_documentos,
                    SUM(tamaño_archivo) as total_tamaño,
                    COUNT(CASE WHEN es_confidencial = true THEN 1 END) as documentos_confidenciales,
                    COUNT(CASE WHEN estado = 'activo' THEN 1 END) as documentos_activos
                FROM documentos_paciente
                WHERE estado != 'eliminado'
                GROUP BY tipo_documento
                ORDER BY total_documentos DESC
            """

            result = db.getRecordsWithStatus(query, {})
            db.close()

            if result['success']:
                estadisticas = []
                for stat in result['data']:
                    estadistica = dict(stat)
                    estadisticas.append(estadistica)

                HandleLogs.write_log("DocumentoPacienteComponent.get_estadisticas_documentos - Estadísticas obtenidas")
                return {
                    'success': True,
                    'data': estadisticas,
                    'message': 'Estadísticas obtenidas correctamente'
                }
            else:
                return result

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteComponent.get_estadisticas_documentos - Error: {str(e)}")
            return {
                'success': False,
                'data': None,
                'message': f'Error interno: {str(e)}'
            }