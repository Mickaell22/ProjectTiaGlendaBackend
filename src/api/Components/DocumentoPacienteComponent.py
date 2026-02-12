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

            # Filtrar solo los campos que usa el INSERT para evitar errores de psycopg2
            campos_insert = [
                'id_paciente', 'nombre_archivo', 'ruta_archivo',
                'tipo_documento', 'tamaño_archivo', 'tipo_mime', 'descripcion',
                'usuario_creacion'
            ]
            datos_filtrados = {k: documento_data.get(k) for k in campos_insert}

            result = DataBaseHandle.ExecuteNonQuery(query, datos_filtrados)

            if result:
                HandleLogs.write_log("DocumentoPacienteComponent.create_documento - Documento creado exitosamente")
                # Obtener el documento recien insertado
                query_id = """
                    SELECT id FROM documentos_paciente
                    WHERE id_paciente = %(id_paciente)s
                      AND nombre_archivo = %(nombre_archivo)s
                    ORDER BY fecha_creacion DESC LIMIT 1
                """
                id_result = DataBaseHandle.getRecords(query_id, {
                    'id_paciente': datos_filtrados['id_paciente'],
                    'nombre_archivo': datos_filtrados['nombre_archivo']
                })

                documento_id = id_result[0]['id'] if id_result and len(id_result) > 0 else None
                return {
                    'success': True,
                    'data': {'id': documento_id, **datos_filtrados},
                    'message': 'Documento creado correctamente'
                }
            else:
                HandleLogs.write_error("DocumentoPacienteComponent.create_documento - Error en insercion")
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
                    dp.ruta_archivo,
                    dp.tipo_documento,
                    dp.tamaño_archivo,
                    dp.tipo_mime,
                    dp.descripcion,
                    dp.fecha_subida,
                    dp.fecha_creacion,
                    dp.fecha_modificacion,
                    dp.usuario_creacion,
                    dp.usuario_modificacion,
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
                documentos = []
                if result['data']:
                    for doc in result['data']:
                        documento = dict(doc)
                        # Convertir TIMESTAMP a string para JSON
                        if documento.get('fecha_subida'):
                            documento['fecha_subida'] = documento['fecha_subida'].isoformat()
                        if documento.get('fecha_creacion'):
                            documento['fecha_creacion'] = documento['fecha_creacion'].isoformat()
                        if documento.get('fecha_modificacion'):
                            documento['fecha_modificacion'] = documento['fecha_modificacion'].isoformat()

                        documentos.append(documento)

                HandleLogs.write_log(f"DocumentoPacienteComponent.get_documentos_by_paciente - {len(documentos)} documentos encontrados")
                return {
                    'success': True,
                    'data': documentos,
                    'message': 'Documentos obtenidos correctamente'
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
        """Obtener un documento especifico por ID"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteComponent.get_documento_by_id - ID: {documento_id}")

            query = """
                SELECT
                    dp.id,
                    dp.id_paciente,
                    dp.nombre_archivo,
                    dp.ruta_archivo,
                    dp.tipo_documento,
                    dp.tamaño_archivo,
                    dp.tipo_mime,
                    dp.descripcion,
                    dp.fecha_subida,
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

            if result['success'] and result['data'] and len(result['data']) > 0:
                documento = dict(result['data'][0])
                # Convertir TIMESTAMP a string para JSON
                if documento.get('fecha_subida'):
                    documento['fecha_subida'] = documento['fecha_subida'].isoformat()
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
        """Actualizar informacion de un documento"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteComponent.update_documento - ID: {documento_id}")

            # Verificar que el documento existe antes de actualizar
            check = DocumentoPacienteComponent.get_documento_by_id(documento_id, paciente_id)
            if not check['success'] or not check['data']:
                return {
                    'success': False,
                    'data': None,
                    'message': 'Documento no encontrado'
                }

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
                'tipo_documento': datos.get('tipo_documento', check['data']['tipo_documento']),
                'descripcion': datos.get('descripcion', check['data']['descripcion']),
                'usuario_modificacion': datos.get('usuario_modificacion')
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
        """Eliminar un documento"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteComponent.delete_documento - ID: {documento_id}")

            # Verificar que existe antes de eliminar
            check = DocumentoPacienteComponent.get_documento_by_id(documento_id, paciente_id)
            if not check['success'] or not check['data']:
                return {
                    'success': False,
                    'data': None,
                    'message': 'Documento no encontrado'
                }

            query = """
                DELETE FROM documentos_paciente
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
                    'data': {'id': documento_id, 'ruta_archivo': check['data'].get('ruta_archivo')},
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
        """Obtener estadisticas de documentos"""
        try:
            HandleLogs.write_log("DocumentoPacienteComponent.get_estadisticas_documentos - Iniciando")

            query = """
                SELECT
                    tipo_documento,
                    COUNT(*) as cantidad
                FROM documentos_paciente
                GROUP BY tipo_documento
                ORDER BY cantidad DESC
            """

            result = DataBaseHandle.getRecordsWithStatus(query, {})

            if result['success']:
                tipos = []
                total = 0
                if result['data']:
                    for row in result['data']:
                        fila = dict(row)
                        tipos.append(fila)
                        total += fila['cantidad']

                estadisticas = {
                    'total_documentos': total,
                    'por_tipo': tipos
                }

                return {
                    'success': True,
                    'data': estadisticas,
                    'message': 'Estadisticas obtenidas correctamente'
                }
            else:
                return {
                    'success': True,
                    'data': {'total_documentos': 0, 'por_tipo': []},
                    'message': 'Sin datos de estadisticas'
                }

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteComponent.get_estadisticas_documentos - Error: {str(e)}")
            return {
                'success': False,
                'data': {'total_documentos': 0, 'por_tipo': []},
                'message': f'Error interno: {str(e)}'
            }

    @staticmethod
    def check_documento_exists(documento_id, paciente_id):
        """Verificar si un documento existe"""
        try:
            query = """
                SELECT id FROM documentos_paciente
                WHERE id = %(documento_id)s
                  AND id_paciente = %(paciente_id)s
            """
            result = DataBaseHandle.getRecords(query, {
                'documento_id': documento_id,
                'paciente_id': paciente_id
            })
            return result is not None and bool(result)
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteComponent.check_documento_exists - Error: {str(e)}")
            return False
