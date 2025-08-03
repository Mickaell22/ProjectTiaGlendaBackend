import os
import uuid
from flask import request
from werkzeug.utils import secure_filename
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error, response_inserted, internal_response
from src.utils.general.validators import Validators
from src.utils.general.data_utils import DataUtils
from src.api.Components.PacienteComponent import PacienteComponent
from src.api.Components.DocumentoPacienteComponent import DocumentoPacienteComponent


class PacienteService:

    @staticmethod
    def get_pacientes():
        """Obtener lista de todos los pacientes"""
        try:
            HandleLogs.write_log("PacienteService.get_pacientes - Iniciando")

            result = PacienteComponent.get_all_pacientes()

            if result['success']:
                HandleLogs.write_log("PacienteService.get_pacientes - Pacientes obtenidos exitosamente")
                return response_success(result['data'], "Lista de pacientes obtenida correctamente")
            else:
                HandleLogs.write_error(f"PacienteService.get_pacientes - Error: {result['message']}")
                return response_error("Error obteniendo pacientes", 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.get_pacientes - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_paciente_by_id(paciente_id):
        """Obtener un paciente por ID"""
        try:
            HandleLogs.write_log(f"PacienteService.get_paciente_by_id - ID: {paciente_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            result = PacienteComponent.get_paciente_by_id(paciente_id)

            if result['success']:
                if result['data']:
                    HandleLogs.write_log(f"PacienteService.get_paciente_by_id - Paciente {paciente_id} encontrado")
                    return response_success(result['data'], "Paciente encontrado")
                else:
                    return response_error("Paciente no encontrado", 404)
            else:
                HandleLogs.write_error(f"PacienteService.get_paciente_by_id - Error: {result['message']}")
                return response_error("Error buscando paciente", 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.get_paciente_by_id - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def create_paciente():
        """Crear un nuevo paciente"""
        try:
            data = request.get_json()
            HandleLogs.write_log("PacienteService.create_paciente - Iniciando")

            # Validar datos de paciente
            validation_result = Validators.validate_paciente_data(data, is_update=False)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Preparar datos para inserción usando DataUtils
            base_data = {
                'persona_id': int(data['persona_id']),
                'tutor_id': int(data['tutor_id']),
                'fecha_ingreso': data['fecha_ingreso'],
                'observaciones': data.get('observaciones'),
                'estado': data.get('estado'),
                'usuario_creacion': data.get('usuario_creacion')
            }
            
            current_user_id = getattr(request, 'current_user', {}).get('id')
            paciente_data = DataUtils.prepare_create_data(base_data, current_user_id)

            result = PacienteComponent.create_paciente(paciente_data)

            if result['success']:
                HandleLogs.write_log("PacienteService.create_paciente - Paciente creado exitosamente")
                return response_inserted(result['data'], "Paciente creado exitosamente")
            else:
                HandleLogs.write_error(f"PacienteService.create_paciente - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.create_paciente - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def update_paciente(paciente_id):
        """Actualizar un paciente existente"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"PacienteService.update_paciente - ID: {paciente_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            # Validar datos (para actualización)
            validation_result = Validators.validate_paciente_data(data, is_update=True)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Preparar datos para actualización usando DataUtils
            data['usuario_modificacion'] = data.get('usuario_modificacion')
            current_user_id = getattr(request, 'current_user', {}).get('id')
            prepared_data = DataUtils.prepare_update_data(data, current_user_id)

            result = PacienteComponent.update_paciente(paciente_id, prepared_data)

            if result['success']:
                HandleLogs.write_log(f"PacienteService.update_paciente - Paciente {paciente_id} actualizado")
                return response_success(result['data'], "Paciente actualizado exitosamente")
            else:
                HandleLogs.write_error(f"PacienteService.update_paciente - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.update_paciente - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def change_estado_paciente(paciente_id):
        """Cambiar estado del paciente"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"PacienteService.change_estado_paciente - ID: {paciente_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            # Validar que se proporcione el nuevo estado
            required_validation = Validators.validate_required_fields(data, ['estado'])
            if not required_validation['valid']:
                return response_error(required_validation['message'], 400)

            # Validar que el estado sea válido
            valid_states = ['activo', 'inactivo', 'alta', 'derivado']
            if data['estado'] not in valid_states:
                return response_error(f"Estado inválido. Debe ser uno de: {', '.join(valid_states)}", 400)

            result = PacienteComponent.change_estado_paciente(paciente_id, data['estado'])

            if result['success']:
                HandleLogs.write_log(f"PacienteService.change_estado_paciente - Estado del paciente {paciente_id} cambiado")
                return response_success(result['data'], result['message'])
            else:
                HandleLogs.write_error(f"PacienteService.change_estado_paciente - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.change_estado_paciente - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_pacientes_by_tutor(tutor_id):
        """Obtener pacientes de un tutor específico"""
        try:
            HandleLogs.write_log(f"PacienteService.get_pacientes_by_tutor - Tutor ID: {tutor_id}")

            if not tutor_id or tutor_id <= 0:
                return response_error("ID de tutor invalido", 400)

            result = PacienteComponent.get_pacientes_by_tutor(tutor_id)

            if result['success']:
                HandleLogs.write_log(f"PacienteService.get_pacientes_by_tutor - Pacientes del tutor {tutor_id} obtenidos")
                return response_success(result['data'], "Pacientes del tutor obtenidos correctamente")
            else:
                HandleLogs.write_error(f"PacienteService.get_pacientes_by_tutor - Error: {result['message']}")
                return response_error("Error obteniendo pacientes del tutor", 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.get_pacientes_by_tutor - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_estadisticas():
        """Obtener estadísticas de pacientes"""
        try:
            HandleLogs.write_log("PacienteService.get_estadisticas - Iniciando")

            result = PacienteComponent.get_estadisticas_pacientes()

            if result['success']:
                HandleLogs.write_log("PacienteService.get_estadisticas - Estadísticas obtenidas")
                return response_success(result['data'], "Estadísticas de pacientes obtenidas")
            else:
                HandleLogs.write_error(f"PacienteService.get_estadisticas - Error: {result['message']}")
                return response_error("Error obteniendo estadísticas", 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.get_estadisticas - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_personas_disponibles():
        """Obtener personas disponibles para crear pacientes"""
        try:
            HandleLogs.write_log("PacienteService.get_personas_disponibles - Iniciando")

            result = PacienteComponent.get_personas_disponibles_para_paciente()

            if result['success']:
                HandleLogs.write_log("PacienteService.get_personas_disponibles - Personas disponibles obtenidas")
                return response_success(result['data'], "Personas disponibles para paciente obtenidas")
            else:
                HandleLogs.write_error(f"PacienteService.get_personas_disponibles - Error: {result['message']}")
                return response_error("Error obteniendo personas disponibles", 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.get_personas_disponibles - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def upload_documento(paciente_id):
        """Subir documento PDF para un paciente"""
        try:
            HandleLogs.write_log(f"PacienteService.upload_documento - Paciente ID: {paciente_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente inválido", 400)

            # Verificar que el paciente existe
            paciente_result = PacienteComponent.get_paciente_by_id(paciente_id)
            if not paciente_result['success'] or not paciente_result['data']:
                return response_error("Paciente no encontrado", 404)

            # Verificar que se envió un archivo
            if 'archivo' not in request.files:
                return response_error("No se proporcionó ningún archivo", 400)

            archivo = request.files['archivo']
            if archivo.filename == '':
                return response_error("No se seleccionó ningún archivo", 400)

            # Validar tipo de archivo (solo PDF)
            if not archivo.filename.lower().endswith('.pdf'):
                return response_error("Solo se permiten archivos PDF", 400)

            # Validar tamaño de archivo (máximo 10MB)
            archivo.seek(0, os.SEEK_END)
            tamaño_archivo = archivo.tell()
            archivo.seek(0)
            
            if tamaño_archivo > 10 * 1024 * 1024:  # 10MB
                return response_error("El archivo es demasiado grande. Máximo 10MB", 400)

            # Obtener datos adicionales del formulario
            tipo_documento = request.form.get('tipo_documento', 'general')
            descripcion = request.form.get('descripcion', '')
            es_confidencial = request.form.get('es_confidencial', 'false').lower() == 'true'
            fecha_vencimiento = request.form.get('fecha_vencimiento')

            # Validar tipo de documento
            tipos_validos = ['general', 'historia_clinica', 'examenes_medicos', 'consentimientos', 
                           'reportes_terapia', 'evaluaciones', 'otros']
            if tipo_documento not in tipos_validos:
                return response_error(f"Tipo de documento inválido. Debe ser uno de: {', '.join(tipos_validos)}", 400)

            # Generar nombre único para el archivo
            nombre_original = archivo.filename
            extension = '.pdf'
            nombre_unico = f"{uuid.uuid4().hex}_{secure_filename(nombre_original)}"
            
            # Crear carpeta del paciente si no existe
            paciente_data = paciente_result['data']
            iniciales = f"{paciente_data['nombre'][0]}{paciente_data['apellido'][0]}".upper()
            carpeta_paciente = f"{iniciales}_{paciente_id}"
            ruta_carpeta = os.path.join("documentos_pacientes", carpeta_paciente)
            
            os.makedirs(ruta_carpeta, exist_ok=True)
            
            # Guardar el archivo
            ruta_archivo = os.path.join(ruta_carpeta, nombre_unico)
            archivo.save(ruta_archivo)

            # Preparar datos para la base de datos
            current_user_id = getattr(request, 'current_user', {}).get('id')
            documento_data = {
                'paciente_id': paciente_id,
                'nombre_archivo': nombre_unico,
                'nombre_original': nombre_original,
                'ruta_archivo': ruta_archivo.replace('\\', '/'),  # Normalizar separadores
                'tipo_documento': tipo_documento,
                'tamaño_archivo': tamaño_archivo,
                'tipo_mime': 'application/pdf',
                'descripcion': descripcion if descripcion else None,
                'es_confidencial': es_confidencial,
                'fecha_vencimiento': fecha_vencimiento if fecha_vencimiento else None,
                'usuario_creacion': current_user_id
            }

            documento_data = DataUtils.prepare_create_data(documento_data, current_user_id)

            # Guardar en base de datos
            result = DocumentoPacienteComponent.create_documento(documento_data)

            if result['success']:
                HandleLogs.write_log(f"PacienteService.upload_documento - Documento subido exitosamente para paciente {paciente_id}")
                return response_inserted(result['data'], "Documento subido exitosamente")
            else:
                # Si falla la BD, eliminar el archivo
                if os.path.exists(ruta_archivo):
                    os.remove(ruta_archivo)
                HandleLogs.write_error(f"PacienteService.upload_documento - Error BD: {result['message']}")
                return response_error(result['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.upload_documento - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_documentos(paciente_id):
        """Obtener lista de documentos de un paciente"""
        try:
            HandleLogs.write_log(f"PacienteService.get_documentos - Paciente ID: {paciente_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente inválido", 400)

            result = DocumentoPacienteComponent.get_documentos_by_paciente(paciente_id)

            if result['success']:
                HandleLogs.write_log(f"PacienteService.get_documentos - Documentos obtenidos para paciente {paciente_id}")
                return response_success(result['data'], "Documentos obtenidos correctamente")
            else:
                HandleLogs.write_error(f"PacienteService.get_documentos - Error: {result['message']}")
                return response_error("Error obteniendo documentos", 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.get_documentos - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def download_documento(paciente_id, documento_id):
        """Descargar un documento específico de un paciente"""
        try:
            HandleLogs.write_log(f"PacienteService.download_documento - Paciente: {paciente_id}, Documento: {documento_id}")

            if not paciente_id or paciente_id <= 0:
                return internal_response(False, None, "ID de paciente inválido")
            
            if not documento_id or documento_id <= 0:
                return internal_response(False, None, "ID de documento inválido")

            # Obtener información del documento
            result = DocumentoPacienteComponent.get_documento_by_id(documento_id, paciente_id)

            if not result['success'] or not result['data']:
                return internal_response(False, None, "Documento no encontrado")

            documento = result['data']
            ruta_archivo = documento['ruta_archivo']

            # Verificar que el archivo existe
            if not os.path.exists(ruta_archivo):
                HandleLogs.write_error(f"PacienteService.download_documento - Archivo no encontrado: {ruta_archivo}")
                return internal_response(False, None, "Archivo no encontrado en el sistema")

            # Retornar información para descarga
            return internal_response(True, {
                'ruta_archivo': ruta_archivo,
                'nombre_original': documento['nombre_original'],
                'tipo_mime': documento['tipo_mime']
            }, "Información de descarga obtenida")

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.download_documento - Error: {str(e)}")
            return internal_response(False, None, f"Error interno: {str(e)}")

    @staticmethod
    def delete_documento(paciente_id, documento_id):
        """Eliminar un documento de un paciente"""
        try:
            HandleLogs.write_log(f"PacienteService.delete_documento - Paciente: {paciente_id}, Documento: {documento_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente inválido", 400)
            
            if not documento_id or documento_id <= 0:
                return response_error("ID de documento inválido", 400)

            # Obtener información del documento antes de eliminarlo
            result = DocumentoPacienteComponent.get_documento_by_id(documento_id, paciente_id)

            if not result['success'] or not result['data']:
                return response_error("Documento no encontrado", 404)

            documento = result['data']
            ruta_archivo = documento['ruta_archivo']

            # Eliminar de la base de datos
            delete_result = DocumentoPacienteComponent.delete_documento(documento_id, paciente_id)

            if delete_result['success']:
                # Eliminar archivo físico
                try:
                    if os.path.exists(ruta_archivo):
                        os.remove(ruta_archivo)
                        HandleLogs.write_log(f"PacienteService.delete_documento - Archivo eliminado: {ruta_archivo}")
                except Exception as file_error:
                    HandleLogs.write_error(f"PacienteService.delete_documento - Error eliminando archivo: {str(file_error)}")
                
                HandleLogs.write_log(f"PacienteService.delete_documento - Documento {documento_id} eliminado exitosamente")
                return response_success(None, "Documento eliminado exitosamente")
            else:
                HandleLogs.write_error(f"PacienteService.delete_documento - Error: {delete_result['message']}")
                return response_error(delete_result['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.delete_documento - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)