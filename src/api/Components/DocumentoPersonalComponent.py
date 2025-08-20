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
            query = """
            INSERT INTO documentos_personal (
                personal_id, tipo_documento, nombre_documento, nombre_archivo, 
                ruta_archivo, tamanio_archivo, tipo_mime, descripcion, 
                fecha_documento, fecha_vencimiento, usuario_creacion
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            success = DataBaseHandle.ExecuteNonQuery(
                query, 
                (personal_id, tipo_documento, nombre_documento, nombre_archivo,
                 ruta_archivo, tamanio_archivo, tipo_mime, descripcion,
                 fecha_documento, fecha_vencimiento, usuario_id)
            )
            
            if success:
                HandleLogs.write_log(f"DocumentoPersonalComponent.crear_documento_personal - Documento creado para personal {personal_id}")
                return internal_response(True, {
                    "personal_id": personal_id, 
                    "nombre_documento": nombre_documento,
                    "tipo_documento": tipo_documento
                }, "Documento creado exitosamente")
            else:
                HandleLogs.write_error(f"DocumentoPersonalComponent.crear_documento_personal - Error creando documento para personal {personal_id}")
                return internal_response(False, None, "Error creando documento")

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalComponent.crear_documento_personal - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_documentos_personal(personal_id):
        """Obtener todos los documentos de un miembro del personal"""
        try:
            query = """
            SELECT 
                dp.id,
                dp.tipo_documento,
                dp.nombre_documento,
                dp.nombre_archivo,
                dp.ruta_archivo,
                dp.tamanio_archivo,
                dp.tipo_mime,
                dp.descripcion,
                dp.observaciones,
                dp.fecha_documento,
                dp.fecha_vencimiento,
                dp.estado,
                dp.fecha_creacion,
                dp.fecha_modificacion,
                -- Información de vencimiento
                CASE 
                    WHEN dp.fecha_vencimiento IS NOT NULL AND dp.fecha_vencimiento < CURRENT_DATE 
                    THEN 'vencido'
                    WHEN dp.fecha_vencimiento IS NOT NULL AND dp.fecha_vencimiento <= CURRENT_DATE + INTERVAL '30 days'
                    THEN 'por_vencer'
                    ELSE 'vigente'
                END as estado_vencimiento,
                -- Días hasta vencimiento
                CASE 
                    WHEN dp.fecha_vencimiento IS NOT NULL 
                    THEN dp.fecha_vencimiento - CURRENT_DATE
                    ELSE NULL
                END as dias_hasta_vencimiento
            FROM documentos_personal dp
            WHERE dp.personal_id = %s AND dp.estado != 'eliminado'
            ORDER BY dp.tipo_documento, dp.fecha_creacion DESC
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
                dp.id,
                dp.personal_id,
                dp.tipo_documento,
                dp.nombre_documento,
                dp.nombre_archivo,
                dp.ruta_archivo,
                dp.tamanio_archivo,
                dp.tipo_mime,
                dp.descripcion,
                dp.observaciones,
                dp.fecha_documento,
                dp.fecha_vencimiento,
                dp.estado,
                dp.fecha_creacion,
                -- Información del personal
                CONCAT(pe.nombre, ' ', pe.apellido) as nombre_personal,
                p.titulo_profesional,
                c.nombre as centro_nombre
            FROM documentos_personal dp
            INNER JOIN personal p ON dp.personal_id = p.id
            INNER JOIN persona pe ON p.persona_id = pe.id
            INNER JOIN centros c ON p.id_centro = c.id
            WHERE dp.id = %s AND dp.estado != 'eliminado'
            """

            documento = DataBaseHandle.getRecords(query, (documento_id,), size=1)

            if documento:
                HandleLogs.write_log(f"DocumentoPersonalComponent.get_documento_by_id - Documento {documento_id} encontrado")
                return internal_response(True, documento, "Documento encontrado")
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
                campos_actualizar.append("nombre_documento = %s")
                valores.append(nombre_documento)
            
            if descripcion is not None:
                campos_actualizar.append("descripcion = %s")
                valores.append(descripcion)
            
            if observaciones is not None:
                campos_actualizar.append("observaciones = %s")
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
            WHERE id = %s AND estado != 'eliminado'
            """
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
            UPDATE documentos_personal 
            SET estado = 'eliminado', fecha_modificacion = CURRENT_TIMESTAMP
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
                    dp.personal_id,
                    dp.tipo_documento,
                    dp.nombre_documento,
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
                INNER JOIN personal p ON dp.personal_id = p.id
                INNER JOIN persona pe ON p.persona_id = pe.id
                INNER JOIN centros c ON p.id_centro = c.id
                WHERE dp.tipo_documento = %s AND p.id_centro = %s AND dp.estado != 'eliminado'
                ORDER BY pe.nombre, pe.apellido
                """
                params = (tipo_documento, centro_id)
            else:
                query = """
                SELECT 
                    dp.id,
                    dp.personal_id,
                    dp.tipo_documento,
                    dp.nombre_documento,
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
                INNER JOIN personal p ON dp.personal_id = p.id
                INNER JOIN persona pe ON p.persona_id = pe.id
                INNER JOIN centros c ON p.id_centro = c.id
                WHERE dp.tipo_documento = %s AND dp.estado != 'eliminado'
                ORDER BY c.nombre, pe.nombre, pe.apellido
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
                    dp.personal_id,
                    dp.tipo_documento,
                    dp.nombre_documento,
                    dp.fecha_vencimiento,
                    CONCAT(pe.nombre, ' ', pe.apellido) as nombre_personal,
                    p.titulo_profesional,
                    c.nombre as centro_nombre,
                    dp.fecha_vencimiento - CURRENT_DATE as dias_hasta_vencimiento
                FROM documentos_personal dp
                INNER JOIN personal p ON dp.personal_id = p.id
                INNER JOIN persona pe ON p.persona_id = pe.id
                INNER JOIN centros c ON p.id_centro = c.id
                WHERE dp.fecha_vencimiento IS NOT NULL 
                AND dp.fecha_vencimiento BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '%s days'
                AND p.id_centro = %s 
                AND dp.estado != 'eliminado'
                ORDER BY dp.fecha_vencimiento ASC
                """
                params = (dias_adelanto, centro_id)
            else:
                query = """
                SELECT 
                    dp.id,
                    dp.personal_id,
                    dp.tipo_documento,
                    dp.nombre_documento,
                    dp.fecha_vencimiento,
                    CONCAT(pe.nombre, ' ', pe.apellido) as nombre_personal,
                    p.titulo_profesional,
                    c.nombre as centro_nombre,
                    dp.fecha_vencimiento - CURRENT_DATE as dias_hasta_vencimiento
                FROM documentos_personal dp
                INNER JOIN personal p ON dp.personal_id = p.id
                INNER JOIN persona pe ON p.persona_id = pe.id
                INNER JOIN centros c ON p.id_centro = c.id
                WHERE dp.fecha_vencimiento IS NOT NULL 
                AND dp.fecha_vencimiento BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '%s days'
                AND dp.estado != 'eliminado'
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