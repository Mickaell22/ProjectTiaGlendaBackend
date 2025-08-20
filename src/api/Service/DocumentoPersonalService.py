import os
import uuid
from flask import request
from werkzeug.utils import secure_filename
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error, internal_response
from src.utils.general.validators import Validators
from src.api.Components.DocumentoPersonalComponent import DocumentoPersonalComponent


class DocumentoPersonalService:
    
    # Configuración de documentos
    UPLOAD_FOLDER = 'documentos_personal'
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    TIPOS_DOCUMENTO_VALIDOS = [
        'cedula', 'curriculum', 'titulo', 'certificado', 
        'contrato', 'foto', 'otro'
    ]

    @staticmethod
    def _allowed_file(filename):
        """Verificar si el archivo tiene una extensión permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in DocumentoPersonalService.ALLOWED_EXTENSIONS

    @staticmethod
    def _get_upload_path(personal_id):
        """Obtener la ruta de subida para un personal específico"""
        base_path = os.path.join(os.getcwd(), DocumentoPersonalService.UPLOAD_FOLDER)
        personal_path = os.path.join(base_path, f"personal_{personal_id}")
        
        # Crear directorio si no existe
        os.makedirs(personal_path, exist_ok=True)
        
        return personal_path

    @staticmethod
    def subir_documento():
        """Subir un documento para un miembro del personal"""
        try:
            HandleLogs.write_log("DocumentoPersonalService.subir_documento - Iniciando")
            
            # Verificar que se recibió un archivo
            if 'documento' not in request.files and 'archivo' not in request.files:
                return response_error("No se encontró archivo en la solicitud", 400)
            
            archivo = request.files.get('documento') or request.files.get('archivo')
            if archivo.filename == '':
                return response_error("No se seleccionó ningún archivo", 400)
            
            # Obtener datos del formulario
            personal_id = request.form.get('personal_id')
            tipo_documento = request.form.get('tipo_documento')
            nombre_documento = request.form.get('nombre_documento')
            descripcion = request.form.get('descripcion')
            fecha_documento = request.form.get('fecha_documento')
            fecha_vencimiento = request.form.get('fecha_vencimiento')
            usuario_id = request.form.get('usuario_id', 1)  # TODO: Obtener del token
            
            # Validaciones
            if not personal_id:
                return response_error("ID de personal requerido", 400)
            
            try:
                personal_id = int(personal_id)
                usuario_id = int(usuario_id)
            except ValueError:
                return response_error("ID de personal o usuario inválido", 400)
            
            if not tipo_documento or tipo_documento not in DocumentoPersonalService.TIPOS_DOCUMENTO_VALIDOS:
                return response_error(f"Tipo de documento inválido. Debe ser uno de: {', '.join(DocumentoPersonalService.TIPOS_DOCUMENTO_VALIDOS)}", 400)
            
            # Si no se proporciona nombre_documento, usar el nombre del archivo
            if not nombre_documento:
                nombre_documento = archivo.filename
            
            # Validar archivo
            if not DocumentoPersonalService._allowed_file(archivo.filename):
                return response_error(f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(DocumentoPersonalService.ALLOWED_EXTENSIONS)}", 400)
            
            # Verificar tamaño del archivo
            archivo.seek(0, os.SEEK_END)
            tamanio_archivo = archivo.tell()
            archivo.seek(0)
            
            if tamanio_archivo > DocumentoPersonalService.MAX_FILE_SIZE:
                return response_error(f"El archivo es demasiado grande. Tamaño máximo: {DocumentoPersonalService.MAX_FILE_SIZE / (1024*1024):.1f}MB", 400)
            
            # Generar nombre único para el archivo
            nombre_archivo_original = secure_filename(archivo.filename)
            nombre_archivo_unico = DocumentoPersonalComponent.generar_nombre_archivo_unico(nombre_archivo_original)
            
            # Obtener ruta de destino
            upload_path = DocumentoPersonalService._get_upload_path(personal_id)
            ruta_completa = os.path.join(upload_path, nombre_archivo_unico)
            
            # Guardar archivo
            archivo.save(ruta_completa)
            
            # Guardar información en base de datos
            result = DocumentoPersonalComponent.crear_documento_personal(
                personal_id=personal_id,
                tipo_documento=tipo_documento,
                nombre_documento=nombre_documento,
                nombre_archivo=nombre_archivo_unico,
                ruta_archivo=ruta_completa,
                tamanio_archivo=tamanio_archivo,
                tipo_mime=archivo.content_type,
                descripcion=descripcion,
                fecha_documento=fecha_documento if fecha_documento else None,
                fecha_vencimiento=fecha_vencimiento if fecha_vencimiento else None,
                usuario_id=usuario_id
            )
            
            if result['success']:
                HandleLogs.write_log(f"DocumentoPersonalService.subir_documento - Documento subido exitosamente para personal {personal_id}")
                return response_success({
                    **result['data'],
                    'tamanio_archivo': tamanio_archivo,
                    'nombre_archivo_original': nombre_archivo_original
                }, "Documento subido exitosamente")
            else:
                # Si falla la BD, eliminar el archivo
                try:
                    os.remove(ruta_completa)
                except:
                    pass
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.subir_documento - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_documentos_personal(personal_id):
        """Obtener documentos de un miembro del personal"""
        try:
            HandleLogs.write_log(f"DocumentoPersonalService.get_documentos_personal - Personal ID: {personal_id}")
            
            if not personal_id or personal_id <= 0:
                return response_error("ID de personal inválido", 400)
            
            result = DocumentoPersonalComponent.get_documentos_personal(personal_id)
            
            if result['success']:
                return response_success(result['data'], "Documentos obtenidos correctamente")
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.get_documentos_personal - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_documento_by_id(documento_id):
        """Obtener un documento específico por ID"""
        try:
            HandleLogs.write_log(f"DocumentoPersonalService.get_documento_by_id - Documento ID: {documento_id}")
            
            if not documento_id or documento_id <= 0:
                return response_error("ID de documento inválido", 400)
            
            result = DocumentoPersonalComponent.get_documento_by_id(documento_id)
            
            if result['success']:
                return response_success(result['data'], "Documento encontrado")
            else:
                return response_error(result['message'], 404)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.get_documento_by_id - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def actualizar_documento():
        """Actualizar información de un documento"""
        try:
            data = request.get_json()
            HandleLogs.write_log("DocumentoPersonalService.actualizar_documento - Iniciando")
            
            # Validar datos requeridos
            required_validation = Validators.validate_required_fields(data, ['documento_id'])
            if not required_validation['valid']:
                return response_error(required_validation['message'], 400)
            
            documento_id = data['documento_id']
            tipo_documento = data.get('tipo_documento')
            nombre_documento = data.get('nombre_documento')
            descripcion = data.get('descripcion')
            observaciones = data.get('observaciones')
            fecha_documento = data.get('fecha_documento')
            fecha_vencimiento = data.get('fecha_vencimiento')
            usuario_id = data.get('usuario_id', 1)  # TODO: Obtener del token
            
            # Validar ID
            if not isinstance(documento_id, int) or documento_id <= 0:
                return response_error("ID de documento inválido", 400)
            
            # Validar tipo de documento si se proporciona
            if tipo_documento and tipo_documento not in DocumentoPersonalService.TIPOS_DOCUMENTO_VALIDOS:
                return response_error(f"Tipo de documento inválido. Debe ser uno de: {', '.join(DocumentoPersonalService.TIPOS_DOCUMENTO_VALIDOS)}", 400)
            
            result = DocumentoPersonalComponent.actualizar_documento_personal(
                documento_id=documento_id,
                tipo_documento=tipo_documento,
                nombre_documento=nombre_documento,
                descripcion=descripcion,
                observaciones=observaciones,
                fecha_documento=fecha_documento,
                fecha_vencimiento=fecha_vencimiento,
                usuario_id=usuario_id
            )
            
            if result['success']:
                HandleLogs.write_log(f"DocumentoPersonalService.actualizar_documento - Documento {documento_id} actualizado")
                return response_success(result['data'], result['message'])
            else:
                return response_error(result['message'], 400)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.actualizar_documento - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod  
    def actualizar_documento_por_id(documento_id):
        """Actualizar información de un documento específico por ID"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"DocumentoPersonalService.actualizar_documento_por_id - Iniciando para documento {documento_id}")
            
            # Validar ID
            if not isinstance(documento_id, int) or documento_id <= 0:
                return response_error("ID de documento inválido", 400)
            
            descripcion = data.get('descripcion')
            observaciones = data.get('observaciones')
            fecha_documento = data.get('fecha_documento')
            fecha_vencimiento = data.get('fecha_vencimiento')
            tipo_documento = data.get('tipo_documento')
            nombre_documento = data.get('nombre_documento')
            usuario_id = data.get('usuario_id', 1)  # TODO: Obtener del token
            
            # Validar tipo de documento si se proporciona
            if tipo_documento and tipo_documento not in DocumentoPersonalService.TIPOS_DOCUMENTO_VALIDOS:
                return response_error(f"Tipo de documento inválido. Debe ser uno de: {', '.join(DocumentoPersonalService.TIPOS_DOCUMENTO_VALIDOS)}", 400)
            
            result = DocumentoPersonalComponent.actualizar_documento_personal(
                documento_id=documento_id,
                tipo_documento=tipo_documento,
                nombre_documento=nombre_documento,
                descripcion=descripcion,
                observaciones=observaciones,
                fecha_documento=fecha_documento,
                fecha_vencimiento=fecha_vencimiento,
                usuario_id=usuario_id
            )
            
            if result['success']:
                HandleLogs.write_log(f"DocumentoPersonalService.actualizar_documento_por_id - Documento {documento_id} actualizado")
                return response_success(result['data'], result['message'])
            else:
                return response_error(result['message'], 400)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.actualizar_documento_por_id - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def eliminar_documento(documento_id):
        """Eliminar un documento"""
        try:
            HandleLogs.write_log(f"DocumentoPersonalService.eliminar_documento - Documento ID: {documento_id}")
            
            if not documento_id or documento_id <= 0:
                return response_error("ID de documento inválido", 400)
            
            result = DocumentoPersonalComponent.eliminar_documento_personal(documento_id)
            
            if result['success']:
                HandleLogs.write_log(f"DocumentoPersonalService.eliminar_documento - Documento {documento_id} eliminado")
                return response_success(result['data'], result['message'])
            else:
                return response_error(result['message'], 400)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.eliminar_documento - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_documentos_por_tipo(tipo_documento, centro_id=None):
        """Obtener documentos por tipo"""
        try:
            HandleLogs.write_log(f"DocumentoPersonalService.get_documentos_por_tipo - Tipo: {tipo_documento}, Centro: {centro_id}")
            
            if not tipo_documento or tipo_documento not in DocumentoPersonalService.TIPOS_DOCUMENTO_VALIDOS:
                return response_error(f"Tipo de documento inválido. Debe ser uno de: {', '.join(DocumentoPersonalService.TIPOS_DOCUMENTO_VALIDOS)}", 400)
            
            if centro_id and centro_id <= 0:
                return response_error("ID de centro inválido", 400)
            
            result = DocumentoPersonalComponent.get_documentos_por_tipo(tipo_documento, centro_id)
            
            if result['success']:
                return response_success(result['data'], "Documentos obtenidos correctamente")
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.get_documentos_por_tipo - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_documentos_por_vencer(dias_adelanto=30, centro_id=None):
        """Obtener documentos que están por vencer"""
        try:
            HandleLogs.write_log(f"DocumentoPersonalService.get_documentos_por_vencer - Días: {dias_adelanto}, Centro: {centro_id}")
            
            if dias_adelanto <= 0 or dias_adelanto > 365:
                return response_error("Días de adelanto debe estar entre 1 y 365", 400)
            
            if centro_id and centro_id <= 0:
                return response_error("ID de centro inválido", 400)
            
            result = DocumentoPersonalComponent.get_documentos_por_vencer(dias_adelanto, centro_id)
            
            if result['success']:
                return response_success(result['data'], "Documentos por vencer obtenidos correctamente")
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.get_documentos_por_vencer - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def descargar_documento(documento_id):
        """Obtener la ruta del archivo para descarga"""
        try:
            HandleLogs.write_log(f"DocumentoPersonalService.descargar_documento - Documento ID: {documento_id}")
            
            if not documento_id or documento_id <= 0:
                return internal_response(False, None, "ID de documento inválido")
            
            result = DocumentoPersonalComponent.get_documento_by_id(documento_id)
            
            if result['success'] and result['data']:
                documento = result['data']
                HandleLogs.write_log(f"DocumentoPersonalService.descargar_documento - Documento encontrado: {documento}")
                
                ruta_archivo = documento.get('ruta_archivo')
                if not ruta_archivo:
                    HandleLogs.write_error(f"DocumentoPersonalService.descargar_documento - No hay ruta_archivo en documento: {documento}")
                    return internal_response(False, None, "Ruta de archivo no encontrada")
                
                HandleLogs.write_log(f"DocumentoPersonalService.descargar_documento - Verificando archivo: {ruta_archivo}")
                
                # Verificar que el archivo existe
                if not os.path.exists(ruta_archivo):
                    HandleLogs.write_error(f"DocumentoPersonalService.descargar_documento - Archivo no encontrado: {ruta_archivo}")
                    return internal_response(False, None, "Archivo no encontrado en el servidor")
                
                return internal_response(True, {
                    'documento_id': documento_id,
                    'ruta_archivo': ruta_archivo,
                    'nombre_archivo': documento['nombre_archivo'],
                    'descripcion': documento.get('descripcion', 'Documento'),
                    'tipo_mime': documento.get('tipo_mime', 'application/pdf')
                }, "Información del archivo obtenida")
            else:
                return internal_response(False, None, "Documento no encontrado")
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.descargar_documento - Error: {str(e)}")
            return internal_response(False, None, f"Error interno: {str(e)}")

    @staticmethod
    def obtener_tipos_documentos():
        """Obtener tipos de documentos soportados"""
        try:
            HandleLogs.write_log("DocumentoPersonalService.obtener_tipos_documentos - Iniciando")
            
            tipos_data = {
                'tipos_documento': DocumentoPersonalService.TIPOS_DOCUMENTO_VALIDOS,
                'extensiones_permitidas': list(DocumentoPersonalService.ALLOWED_EXTENSIONS),
                'tamanio_maximo_mb': DocumentoPersonalService.MAX_FILE_SIZE / (1024*1024)
            }
            
            return response_success(tipos_data, "Tipos de documentos obtenidos exitosamente")
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.obtener_tipos_documentos - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def obtener_documentos_vencimientos(dias_alerta=90):
        """Obtener documentos próximos a vencer"""
        try:
            HandleLogs.write_log("DocumentoPersonalService.obtener_documentos_vencimientos - Iniciando")
            
            result = DocumentoPersonalComponent.obtener_documentos_vencimientos(dias_alerta)
            
            if result['success']:
                return response_success(result['data'], f"Documentos próximos a vencer obtenidos ({dias_alerta} días)")
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.obtener_documentos_vencimientos - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def obtener_documentos_pendientes_validacion():
        """Obtener documentos pendientes de validación"""
        try:
            HandleLogs.write_log("DocumentoPersonalService.obtener_documentos_pendientes_validacion - Iniciando")
            
            result = DocumentoPersonalComponent.obtener_documentos_pendientes_validacion()
            
            if result['success']:
                return response_success(result['data'], "Documentos pendientes de validación obtenidos")
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.obtener_documentos_pendientes_validacion - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def obtener_estadisticas_documentos():
        """Obtener estadísticas de documentos de personal"""
        try:
            HandleLogs.write_log("DocumentoPersonalService.obtener_estadisticas_documentos - Iniciando")
            
            result = DocumentoPersonalComponent.obtener_estadisticas_documentos()
            
            if result['success']:
                return response_success(result['data'], "Estadísticas de documentos obtenidas")
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.obtener_estadisticas_documentos - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def buscar_documentos():
        """Buscar documentos con filtros avanzados"""
        try:
            HandleLogs.write_log("DocumentoPersonalService.buscar_documentos - Iniciando")
            
            tipo_documento = request.args.get('tipo_documento')
            estado_validacion = request.args.get('estado_validacion')
            q = request.args.get('q')  # texto de búsqueda
            
            result = DocumentoPersonalComponent.buscar_documentos(
                tipo_documento=tipo_documento,
                estado_validacion=estado_validacion,
                texto_busqueda=q
            )
            
            if result['success']:
                return response_success(result['data'], "Búsqueda de documentos completada")
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.buscar_documentos - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def validar_documento(documento_id):
        """Validar documento de personal"""
        try:
            HandleLogs.write_log(f"DocumentoPersonalService.validar_documento - Iniciando para documento {documento_id}")
            
            data = request.get_json()
            estado_validacion = data.get('estado_validacion')
            observaciones_validacion = data.get('observaciones_validacion')
            validado_por_raw = data.get('validado_por')
            
            # Convertir validado_por a entero o usar usuario por defecto
            try:
                validado_por = int(validado_por_raw) if validado_por_raw and validado_por_raw.isdigit() else 25
            except (ValueError, AttributeError):
                validado_por = 25  # Usuario admin existente por defecto
            
            if not estado_validacion or estado_validacion not in ['aprobado', 'rechazado', 'pendiente']:
                return response_error("Estado de validación inválido", 400)
            
            result = DocumentoPersonalComponent.validar_documento(
                documento_id=documento_id,
                estado_validacion=estado_validacion,
                observaciones_validacion=observaciones_validacion,
                validado_por=validado_por
            )
            
            if result['success']:
                return response_success(result['data'], f"Documento {estado_validacion} exitosamente")
            else:
                return response_error(result['message'], 500)
                
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPersonalService.validar_documento - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)