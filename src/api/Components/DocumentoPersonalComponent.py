import os
import uuid
from datetime import datetime
from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class DocumentoPersonalComponent:

    @staticmethod
    def crear_documento_personal(personal_id, tipo_documento, nombre_documento, nombre_archivo, 
                                ruta_archivo, tamanio_archivo=None, tipo_mime=None, descripcion=None, 
                                fecha_documento=None, fecha_vencimiento=None, usuario_id=None):
        """Crear un nuevo documento para un miembro del personal"""
        try:
            # Primero hacer INSERT
            insert_query = """
            INSERT INTO documentos_personal (
                id_personal, tipo_documento, nombre_archivo, 
                ruta_archivo, tamaño_archivo, tipo_mime, descripcion, 
                fecha_vencimiento, usuario_creacion
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            success = DataBaseHandle.ExecuteNonQuery(
                insert_query, 
                (personal_id, tipo_documento, nombre_archivo,
                 ruta_archivo, tamanio_archivo, tipo_mime, descripcion,
                 fecha_vencimiento, usuario_id)
            )
            
            if success:
                # Luego obtener el ID del documento recién insertado
                select_query = """
                SELECT id FROM documentos_personal 
                WHERE id_personal = %s AND nombre_archivo = %s AND ruta_archivo = %s
                ORDER BY fecha_creacion DESC LIMIT 1
                """
                result = DataBaseHandle.getRecords(select_query, (personal_id, nombre_archivo, ruta_archivo))
                
                if result and len(result) > 0:
                    documento_id = result[0]['id']
                    HandleLogs.write_log(f"DocumentoPersonalComponent.crear_documento_personal - Documento creado para personal {personal_id} con ID {documento_id}")
                    return internal_response(True, {
                        "id": documento_id,
                        "personal_id": personal_id, 
                        "nombre_archivo": nombre_archivo,
                        "tipo_documento": tipo_documento,
                        "ruta_archivo": ruta_archivo
                    }, "Documento creado exitosamente")
                else:
                    HandleLogs.write_error(f"DocumentoPersonalComponent.crear_documento_personal - Error obteniendo ID del documento creado")
                    return internal_response(False, None, "Error obteniendo ID del documento creado")
            else:
                HandleLogs.write_error(f"DocumentoPersonalComponent.crear_documento_personal - Error insertando documento para personal {personal_id}")
                return internal_response(False, None, "Error creando documento")

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.crear_documento_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_documentos_personal(personal_id):
        """Obtener todos los documentos de un miembro del personal"""
        try:
            query = """
            SELECT dp.*
            FROM documentos_personal dp
            WHERE dp.id_personal = %s
            ORDER BY dp.fecha_creacion DESC
            """

            documentos = DataBaseHandle.getRecords(query, (personal_id,))

            if documentos is not None:
                HandleLogs.write_log(f"DocumentoPersonalComponent.get_documentos_personal - {len(documentos)} documentos encontrados para personal {personal_id}")
                return internal_response(True, documentos, "Documentos obtenidos correctamente")
            else:
                HandleLogs.write_error("DocumentoPersonalComponent.get_documentos_personal - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.get_documentos_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_documento_by_id(documento_id):
        """Obtener un documento específico por ID"""
        try:
            query = """
            SELECT 
                dp.*
            FROM documentos_personal dp
            WHERE dp.id = %s
            """

            HandleLogs.write_log(f"DocumentoPersonalComponent.get_documento_by_id - Ejecutando query para ID: {documento_id} (type: {type(documento_id)})")
            documento = DataBaseHandle.getRecords(query, (documento_id,))
            HandleLogs.write_log(f"DocumentoPersonalComponent.get_documento_by_id - Query result: {documento}")

            if documento and len(documento) > 0:
                HandleLogs.write_log(f"DocumentoPersonalComponent.get_documento_by_id - Documento {documento_id} encontrado")
                return internal_response(True, documento[0], "Documento encontrado")
            else:
                HandleLogs.write_log(f"DocumentoPersonalComponent.get_documento_by_id - Documento {documento_id} no encontrado")
                return internal_response(False, None, "Documento no encontrado")

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.get_documento_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def actualizar_documento_personal(documento_id, tipo_documento=None, nombre_documento=None, 
                                     descripcion=None, observaciones=None, fecha_documento=None, 
                                     fecha_vencimiento=None, usuario_id=None):
        """Actualizar información de un documento"""
        try:
            # Construir query dinámicamente solo con campos a actualizar
            campos_actualizar = []
            valores = []
            
            if tipo_documento is not None:
                campos_actualizar.append("tipo_documento = %s")
                valores.append(tipo_documento)
            
            if nombre_documento is not None:
                campos_actualizar.append("descripcion = %s")
                valores.append(nombre_documento)
            
            if descripcion is not None:
                campos_actualizar.append("descripcion = %s")
                valores.append(descripcion)
            
            if observaciones is not None:
                campos_actualizar.append("observaciones_validacion = %s")
                valores.append(observaciones)
            
            if fecha_documento is not None:
                campos_actualizar.append("fecha_documento = %s")
                valores.append(fecha_documento)
            
            if fecha_vencimiento is not None:
                campos_actualizar.append("fecha_vencimiento = %s")
                valores.append(fecha_vencimiento)
            
            if usuario_id is not None:
                campos_actualizar.append("usuario_modificacion = %s")
                valores.append(usuario_id)
            
            campos_actualizar.append("fecha_modificacion = CURRENT_TIMESTAMP")
            
            if not campos_actualizar:
                return internal_response(False, None, "No hay campos para actualizar")
            
            query = f"""
            UPDATE documentos_personal 
            SET {', '.join(campos_actualizar)}
            WHERE id = %s            """
            valores.append(documento_id)
            
            success = DataBaseHandle.ExecuteNonQuery(query, tuple(valores))
            
            if success:
                HandleLogs.write_log(f"DocumentoPersonalComponent.actualizar_documento_personal - Documento {documento_id} actualizado")
                return internal_response(True, {"documento_id": documento_id}, "Documento actualizado exitosamente")
            else:
                HandleLogs.write_error(f"DocumentoPersonalComponent.actualizar_documento_personal - Error actualizando documento {documento_id}")
                return internal_response(False, None, "Error actualizando documento")

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.actualizar_documento_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def eliminar_documento_personal(documento_id):
        """Eliminar un documento (marcarlo como eliminado)"""
        try:
            query = """
            DELETE FROM documentos_personal 
            WHERE id = %s
            """
            
            success = DataBaseHandle.ExecuteNonQuery(query, (documento_id,))
            
            if success:
                HandleLogs.write_log(f"DocumentoPersonalComponent.eliminar_documento_personal - Documento {documento_id} eliminado")
                return internal_response(True, {"documento_id": documento_id}, "Documento eliminado exitosamente")
            else:
                HandleLogs.write_error(f"DocumentoPersonalComponent.eliminar_documento_personal - Error eliminando documento {documento_id}")
                return internal_response(False, None, "Error eliminando documento")

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.eliminar_documento_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_documentos_por_tipo(tipo_documento, centro_id=None):
        """Obtener documentos por tipo, opcionalmente filtrado por centro"""
        try:
            if centro_id:
                query = """
                SELECT 
                    dp.id,
                    dp.id_personal,
                    dp.tipo_documento,
                    dp.descripcion,
                    dp.fecha_documento,
                    dp.fecha_vencimiento,
                    dp.estado,
                    CONCAT(pe.nombre, ' ', pe.apellido) as nombre_personal,
                    p.titulo_profesional,
                    c.nombre as centro_nombre,
                    -- Estado de vencimiento
                    CASE 
                        WHEN dp.fecha_vencimiento IS NOT NULL AND dp.fecha_vencimiento < CURRENT_DATE 
                        THEN 'vencido'
                        WHEN dp.fecha_vencimiento IS NOT NULL AND dp.fecha_vencimiento <= CURRENT_DATE + INTERVAL '30 days'
                        THEN 'por_vencer'
                        ELSE 'vigente'
                    END as estado_vencimiento
                FROM documentos_personal dp
                INNER JOIN personal p ON dp.id_personal = p.id
                INNER JOIN persona pe ON p.id_persona = pe.id
                INNER JOIN centros c ON p.id_centro = c.id
                WHERE dp.tipo_documento = %s AND p.id_centro = %s                ORDER BY pe.nombre, pe.apellido
                """
                params = (tipo_documento, centro_id)
            else:
                query = """
                SELECT 
                    dp.id,
                    dp.id_personal,
                    dp.tipo_documento,
                    dp.descripcion,
                    dp.fecha_documento,
                    dp.fecha_vencimiento,
                    dp.estado,
                    CONCAT(pe.nombre, ' ', pe.apellido) as nombre_personal,
                    p.titulo_profesional,
                    c.nombre as centro_nombre,
                    -- Estado de vencimiento
                    CASE 
                        WHEN dp.fecha_vencimiento IS NOT NULL AND dp.fecha_vencimiento < CURRENT_DATE 
                        THEN 'vencido'
                        WHEN dp.fecha_vencimiento IS NOT NULL AND dp.fecha_vencimiento <= CURRENT_DATE + INTERVAL '30 days'
                        THEN 'por_vencer'
                        ELSE 'vigente'
                    END as estado_vencimiento
                FROM documentos_personal dp
                INNER JOIN personal p ON dp.id_personal = p.id
                INNER JOIN persona pe ON p.id_persona = pe.id
                INNER JOIN centros c ON p.id_centro = c.id
                WHERE dp.tipo_documento = %s                ORDER BY c.nombre, pe.nombre, pe.apellido
                """
                params = (tipo_documento,)

            documentos = DataBaseHandle.getRecords(query, params)

            if documentos is not None:
                HandleLogs.write_log(f"DocumentoPersonalComponent.get_documentos_por_tipo - {len(documentos)} documentos tipo {tipo_documento} encontrados")
                return internal_response(True, documentos, "Documentos obtenidos correctamente")
            else:
                HandleLogs.write_error("DocumentoPersonalComponent.get_documentos_por_tipo - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.get_documentos_por_tipo - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_documentos_por_vencer(dias_adelanto=30, centro_id=None):
        """Obtener documentos que están por vencer en los próximos X días"""
        try:
            if centro_id:
                query = """
                SELECT 
                    dp.id,
                    dp.id_personal,
                    dp.tipo_documento,
                    dp.descripcion,
                    dp.fecha_vencimiento,
                    CONCAT(pe.nombre, ' ', pe.apellido) as nombre_personal,
                    p.titulo_profesional,
                    c.nombre as centro_nombre,
                    dp.fecha_vencimiento - CURRENT_DATE as dias_hasta_vencimiento
                FROM documentos_personal dp
                INNER JOIN personal p ON dp.id_personal = p.id
                INNER JOIN persona pe ON p.id_persona = pe.id
                INNER JOIN centros c ON p.id_centro = c.id
                WHERE dp.fecha_vencimiento IS NOT NULL 
                AND dp.fecha_vencimiento BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '%s days'
                AND p.id_centro = %s 
                               ORDER BY dp.fecha_vencimiento ASC
                """
                params = (dias_adelanto, centro_id)
            else:
                query = """
                SELECT 
                    dp.id,
                    dp.id_personal,
                    dp.tipo_documento,
                    dp.descripcion,
                    dp.fecha_vencimiento,
                    CONCAT(pe.nombre, ' ', pe.apellido) as nombre_personal,
                    p.titulo_profesional,
                    c.nombre as centro_nombre,
                    dp.fecha_vencimiento - CURRENT_DATE as dias_hasta_vencimiento
                FROM documentos_personal dp
                INNER JOIN personal p ON dp.id_personal = p.id
                INNER JOIN persona pe ON p.id_persona = pe.id
                INNER JOIN centros c ON p.id_centro = c.id
                WHERE dp.fecha_vencimiento IS NOT NULL 
                AND dp.fecha_vencimiento BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '%s days'
                               ORDER BY dp.fecha_vencimiento ASC
                """
                params = (dias_adelanto,)

            documentos = DataBaseHandle.getRecords(query, params)

            if documentos is not None:
                HandleLogs.write_log(f"DocumentoPersonalComponent.get_documentos_por_vencer - {len(documentos)} documentos por vencer encontrados")
                return internal_response(True, documentos, "Documentos por vencer obtenidos correctamente")
            else:
                HandleLogs.write_error("DocumentoPersonalComponent.get_documentos_por_vencer - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.get_documentos_por_vencer - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def generar_nombre_archivo_unico(nombre_original):
        """Generar un nombre de archivo único manteniendo la extensión original"""
        try:
            nombre_base, extension = os.path.splitext(nombre_original)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            uuid_corto = str(uuid.uuid4())[:8]
            nombre_unico = f"{timestamp}_{uuid_corto}{extension}"
            
            HandleLogs.write_log(f"DocumentoPersonalComponent.generar_nombre_archivo_unico - Nombre generado: {nombre_unico}")
            return nombre_unico
            
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.generar_nombre_archivo_unico - Error: {str(e)}")
            return f"documento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"

    @staticmethod
    def obtener_documentos_vencimientos(dias_alerta=90):
        """Obtener documentos próximos a vencer"""
        try:
            query = """
            SELECT dp.*, p.nombre, p.apellido, p.cedula
            FROM documentos_personal dp
            JOIN personal per ON dp.id_personal = per.id
            JOIN persona p ON per.id_persona = p.id
            WHERE dp.fecha_vencimiento IS NOT NULL 
            AND dp.fecha_vencimiento <= CURRENT_DATE + INTERVAL '%s days'
            ORDER BY dp.fecha_vencimiento ASC
            """
            
            result = DataBaseHandle.getRecords(query, (dias_alerta,))
            
            if result is not None:
                HandleLogs.write_log(f"DocumentoPersonalComponent.obtener_documentos_vencimientos - {len(result)} documentos próximos a vencer")
                return internal_response(True, result, "Documentos próximos a vencer obtenidos")
            else:
                return internal_response(True, [], "No hay documentos próximos a vencer")
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.obtener_documentos_vencimientos - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def obtener_documentos_pendientes_validacion():
        """Obtener documentos pendientes de validación"""
        try:
            query = """
            SELECT dp.*, p.nombre, p.apellido, p.cedula
            FROM documentos_personal dp
            JOIN personal per ON dp.id_personal = per.id
            JOIN persona p ON per.id_persona = p.id
            WHERE (dp.estado_validacion IS NULL OR dp.estado_validacion = 'pendiente')
            ORDER BY dp.fecha_creacion ASC
            """
            
            result = DataBaseHandle.getRecords(query)
            
            if result is not None:
                HandleLogs.write_log(f"DocumentoPersonalComponent.obtener_documentos_pendientes_validacion - {len(result)} documentos pendientes")
                return internal_response(True, result, "Documentos pendientes de validación obtenidos")
            else:
                return internal_response(True, [], "No hay documentos pendientes de validación")
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.obtener_documentos_pendientes_validacion - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def obtener_estadisticas_documentos():
        """Obtener estadísticas de documentos de personal"""
        try:
            query = """
            SELECT 
                tipo_documento,
                COUNT(*) as total,
                COUNT(CASE WHEN estado_validacion = 'aprobado' THEN 1 END) as aprobados,
                COUNT(CASE WHEN estado_validacion = 'rechazado' THEN 1 END) as rechazados,
                COUNT(CASE WHEN estado_validacion IS NULL OR estado_validacion = 'pendiente' THEN 1 END) as pendientes,
                COUNT(CASE WHEN fecha_vencimiento <= CURRENT_DATE + INTERVAL '90 days' THEN 1 END) as por_vencer
            FROM documentos_personal 
            WHERE TRUE
            GROUP BY tipo_documento
            ORDER BY total DESC
            """
            
            result = DataBaseHandle.getRecords(query)
            
            if result is not None:
                HandleLogs.write_log(f"DocumentoPersonalComponent.obtener_estadisticas_documentos - Estadísticas obtenidas")
                return internal_response(True, result, "Estadísticas de documentos obtenidas")
            else:
                return internal_response(True, [], "No hay estadísticas disponibles")
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.obtener_estadisticas_documentos - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def buscar_documentos(tipo_documento=None, estado_validacion=None, texto_busqueda=None):
        """Buscar documentos con filtros avanzados"""
        try:
            query = """
            SELECT dp.*, p.nombre, p.apellido, p.cedula
            FROM documentos_personal dp
            JOIN personal per ON dp.id_personal = per.id
            JOIN persona p ON per.id_persona = p.id
            WHERE TRUE
            """
            params = []
            
            if tipo_documento:
                query += " AND dp.tipo_documento = %s"
                params.append(tipo_documento)
            
            if estado_validacion:
                if estado_validacion == 'pendiente':
                    query += " AND (dp.estado_validacion IS NULL OR dp.estado_validacion = 'pendiente')"
                else:
                    query += " AND dp.estado_validacion = %s"
                    params.append(estado_validacion)
            
            if texto_busqueda:
                query += " AND (dp.descripcion ILIKE %s OR p.nombre ILIKE %s OR p.apellido ILIKE %s)"
                like_param = f"%{texto_busqueda}%"
                params.extend([like_param, like_param, like_param])
            
            query += " ORDER BY dp.fecha_creacion DESC"
            
            result = DataBaseHandle.getRecords(query, params if params else None)
            
            if result is not None:
                HandleLogs.write_log(f"DocumentoPersonalComponent.buscar_documentos - {len(result)} documentos encontrados")
                return internal_response(True, result, "Búsqueda completada")
            else:
                return internal_response(True, [], "No se encontraron documentos")
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.buscar_documentos - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def validar_documento(documento_id, estado_validacion, observaciones_validacion=None, validado_por=None):
        """Validar documento de personal"""
        try:
            query = """
            UPDATE documentos_personal 
            SET estado_validacion = %s, 
                observaciones_validacion = %s,
                validado_por = %s,
                fecha_validacion = CURRENT_TIMESTAMP,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            
            success = DataBaseHandle.ExecuteNonQuery(
                query, 
                (estado_validacion, observaciones_validacion, validado_por, documento_id)
            )
            
            if success:
                # Obtener el documento actualizado
                result = DocumentoPersonalComponent.get_documento_by_id(documento_id)
                if result['success']:
                    HandleLogs.write_log(f"DocumentoPersonalComponent.validar_documento - Documento {documento_id} validado como {estado_validacion}")
                    return internal_response(True, result['data'], f"Documento {estado_validacion} exitosamente")
                else:
                    return internal_response(True, {"documento_id": documento_id, "estado": estado_validacion}, f"Documento {estado_validacion}")
            else:
                HandleLogs.write_error(f"DocumentoPersonalComponent.validar_documento - Error validando documento {documento_id}")
                return internal_response(False, None, "Error validando documento")
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.validar_documento - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")