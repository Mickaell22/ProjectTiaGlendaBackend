import os
import uuid
from flask import request
from werkzeug.utils import secure_filename
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error, response_inserted, internal_response
from src.utils.general.validators import Validators
from src.api.Components.DocumentoPacienteComponent import DocumentoPacienteComponent
from src.api.Components.PacienteComponent import PacienteComponent


class DocumentoPacienteService:

    # Tipos validos segun el CHECK constraint de la BD
    TIPOS_VALIDOS = [
        'historia_clinica', 'evaluacion_inicial', 'informe_progreso', 'alta_medica',
        'consentimiento_informado', 'autorizacion_tratamiento', 'cedula_paciente',
        'cedula_tutor', 'otros'
    ]

    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    # En Railway: STORAGE_BASE_PATH = /data/documentos (mount del volume)
    # En local: usa el directorio del proyecto (vacio = relativo)
    STORAGE_BASE_PATH = os.environ.get('STORAGE_BASE_PATH', '')
    UPLOAD_FOLDER = os.path.join(STORAGE_BASE_PATH, 'documentos_pacientes') if STORAGE_BASE_PATH else 'documentos_pacientes'

    @staticmethod
    def upload_documento(paciente_id):
        """Subir documento PDF para un paciente"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteService.upload_documento - Paciente ID: {paciente_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            # Verificar que el paciente existe
            paciente_result = PacienteComponent.get_paciente_by_id(paciente_id)
            if not paciente_result['success'] or not paciente_result['data']:
                return response_error("Paciente no encontrado", 404)

            # Verificar que se envio un archivo
            if 'archivo' not in request.files:
                return response_error("No se proporciono ningun archivo", 400)

            archivo = request.files['archivo']
            if archivo.filename == '':
                return response_error("No se selecciono ningun archivo", 400)

            # Validar tipo de archivo (solo PDF)
            nombre_original = archivo.filename
            if not nombre_original.lower().endswith('.pdf'):
                return response_error("Solo se permiten archivos PDF", 400)

            # Validar tamano de archivo
            archivo.seek(0, os.SEEK_END)
            tamaño_archivo = archivo.tell()
            archivo.seek(0)

            if tamaño_archivo > DocumentoPacienteService.MAX_FILE_SIZE:
                return response_error("El archivo es demasiado grande. Maximo 10MB", 400)

            # Obtener datos adicionales del formulario
            tipo_documento = request.form.get('tipo_documento', 'otros')
            descripcion = request.form.get('descripcion', '')

            # Validar tipo de documento contra la BD
            if tipo_documento not in DocumentoPacienteService.TIPOS_VALIDOS:
                return response_error(
                    f"Tipo de documento invalido. Debe ser uno de: {', '.join(DocumentoPacienteService.TIPOS_VALIDOS)}",
                    400
                )

            # Generar nombre unico para el archivo
            nombre_unico = f"{uuid.uuid4().hex}_{secure_filename(nombre_original)}"

            # Crear carpeta del paciente si no existe
            paciente_data = paciente_result['data']
            nombre = paciente_data.get('nombre', 'X')
            apellido = paciente_data.get('apellido', 'X')
            iniciales = f"{nombre[0]}{apellido[0]}".upper()
            carpeta_paciente = f"{iniciales}_{paciente_id}"
            ruta_carpeta = os.path.join(DocumentoPacienteService.UPLOAD_FOLDER, carpeta_paciente)

            os.makedirs(ruta_carpeta, exist_ok=True)

            # Guardar el archivo
            ruta_archivo = os.path.join(ruta_carpeta, nombre_unico)
            archivo.save(ruta_archivo)

            # Preparar datos para la base de datos
            current_user_id = getattr(request, 'current_user', {}).get('id')
            documento_data = {
                'id_paciente': paciente_id,
                'nombre_archivo': nombre_unico,
                'ruta_archivo': ruta_archivo.replace('\\', '/'),
                'tipo_documento': tipo_documento,
                'tamaño_archivo': tamaño_archivo,
                'tipo_mime': 'application/pdf',
                'descripcion': descripcion if descripcion else None,
                'usuario_creacion': current_user_id
            }

            # Guardar en base de datos
            result = DocumentoPacienteComponent.create_documento(documento_data)

            if result['success']:
                HandleLogs.write_log(f"DocumentoPacienteService.upload_documento - Documento subido exitosamente para paciente {paciente_id}")
                return response_inserted(result['data'], "Documento subido exitosamente")
            else:
                # Si falla la BD, eliminar el archivo fisico
                if os.path.exists(ruta_archivo):
                    os.remove(ruta_archivo)
                HandleLogs.write_error(f"DocumentoPacienteService.upload_documento - Error BD: {result['message']}")
                return response_error(result['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteService.upload_documento - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_documentos(paciente_id):
        """Obtener lista de documentos de un paciente"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteService.get_documentos - Paciente ID: {paciente_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            result = DocumentoPacienteComponent.get_documentos_by_paciente(paciente_id)

            if result['success']:
                return response_success(result['data'], "Documentos obtenidos correctamente")
            else:
                HandleLogs.write_error(f"DocumentoPacienteService.get_documentos - Error: {result['message']}")
                return response_error("Error obteniendo documentos", 500)

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteService.get_documentos - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def download_documento(paciente_id, documento_id):
        """Descargar un documento especifico de un paciente"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteService.download_documento - Paciente: {paciente_id}, Documento: {documento_id}")

            if not paciente_id or paciente_id <= 0:
                return internal_response(False, None, "ID de paciente invalido")

            if not documento_id or documento_id <= 0:
                return internal_response(False, None, "ID de documento invalido")

            # Obtener informacion del documento
            result = DocumentoPacienteComponent.get_documento_by_id(documento_id, paciente_id)

            if not result['success'] or not result['data']:
                return internal_response(False, None, "Documento no encontrado")

            documento = result['data']
            ruta_archivo = documento['ruta_archivo']

            # Verificar que el archivo existe
            if not os.path.exists(ruta_archivo):
                HandleLogs.write_error(f"DocumentoPacienteService.download_documento - Archivo no encontrado: {ruta_archivo}")
                return internal_response(False, None, "Archivo no encontrado en el sistema")

            # Retornar informacion para descarga
            return internal_response(True, {
                'ruta_archivo': ruta_archivo,
                'nombre_archivo': documento['nombre_archivo'],
                'tipo_mime': documento.get('tipo_mime', 'application/pdf')
            }, "Informacion de descarga obtenida")

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteService.download_documento - Error: {str(e)}")
            return internal_response(False, None, f"Error interno: {str(e)}")

    @staticmethod
    def update_documento(paciente_id, documento_id):
        """Actualizar informacion de un documento"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteService.update_documento - Paciente: {paciente_id}, Documento: {documento_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            if not documento_id or documento_id <= 0:
                return response_error("ID de documento invalido", 400)

            data = request.get_json()
            if not data:
                return response_error("No se proporcionaron datos", 400)

            # Validar tipo_documento si se envia
            tipo_documento = data.get('tipo_documento')
            if tipo_documento and tipo_documento not in DocumentoPacienteService.TIPOS_VALIDOS:
                return response_error(
                    f"Tipo de documento invalido. Debe ser uno de: {', '.join(DocumentoPacienteService.TIPOS_VALIDOS)}",
                    400
                )

            current_user_id = getattr(request, 'current_user', {}).get('id')
            datos_update = {
                'usuario_modificacion': current_user_id
            }
            if 'tipo_documento' in data:
                datos_update['tipo_documento'] = data['tipo_documento']
            if 'descripcion' in data:
                datos_update['descripcion'] = data['descripcion']

            result = DocumentoPacienteComponent.update_documento(documento_id, paciente_id, datos_update)

            if result['success']:
                return response_success(result['data'], result['message'])
            return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteService.update_documento - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def delete_documento(paciente_id, documento_id):
        """Eliminar un documento de un paciente"""
        try:
            HandleLogs.write_log(f"DocumentoPacienteService.delete_documento - Paciente: {paciente_id}, Documento: {documento_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            if not documento_id or documento_id <= 0:
                return response_error("ID de documento invalido", 400)

            # Eliminar de la base de datos (el component ya verifica existencia)
            delete_result = DocumentoPacienteComponent.delete_documento(documento_id, paciente_id)

            if delete_result['success']:
                # Eliminar archivo fisico
                ruta_archivo = delete_result['data'].get('ruta_archivo')
                if ruta_archivo:
                    try:
                        if os.path.exists(ruta_archivo):
                            os.remove(ruta_archivo)
                            HandleLogs.write_log(f"DocumentoPacienteService.delete_documento - Archivo eliminado: {ruta_archivo}")
                    except Exception as file_error:
                        HandleLogs.write_error(f"DocumentoPacienteService.delete_documento - Error eliminando archivo: {str(file_error)}")

                return response_success(None, "Documento eliminado exitosamente")
            else:
                if 'no encontrado' in delete_result.get('message', '').lower():
                    return response_error(delete_result['message'], 404)
                return response_error(delete_result['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteService.delete_documento - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_estadisticas():
        """Obtener estadisticas de documentos"""
        try:
            result = DocumentoPacienteComponent.get_estadisticas_documentos()
            if result['success']:
                return response_success(result['data'], result['message'])
            return response_error(result['message'], 500)
        except Exception as e:
            HandleLogs.write_error(f"DocumentoPacienteService.get_estadisticas - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_tipos_documentos():
        """Obtener lista de tipos de documentos validos"""
        return response_success(DocumentoPacienteService.TIPOS_VALIDOS, "Tipos de documentos obtenidos")
