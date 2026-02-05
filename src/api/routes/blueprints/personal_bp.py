"""
Blueprint para rutas de personal y sus documentos.
"""
from flask import Blueprint, request, send_file
import os
import re
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error
from src.utils.general.auth_middleware import token_required, admin_required

personal_bp = Blueprint('personal', __name__, url_prefix='/api')


# ============================================
# RUTAS CRUD DE PERSONAL
# ============================================
@personal_bp.route('/personal', methods=['GET'])
@token_required
def get_personal():
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.get_personal()


@personal_bp.route('/personal/<int:personal_id>', methods=['GET'])
@token_required
def get_personal_by_id(personal_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.get_personal_by_id(personal_id)


@personal_bp.route('/personal', methods=['POST'])
@admin_required
def create_personal():
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.create_personal()


@personal_bp.route('/personal/<int:personal_id>', methods=['PUT'])
@admin_required
def update_personal(personal_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.update_personal(personal_id)


@personal_bp.route('/personal/<int:personal_id>', methods=['DELETE'])
@admin_required
def delete_personal(personal_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.delete_personal(personal_id)


@personal_bp.route('/personal/<int:personal_id>/reactivar', methods=['PUT'])
@admin_required
def reactivate_personal(personal_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.reactivate_personal(personal_id)


@personal_bp.route('/personal/area/<area>', methods=['GET'])
@token_required
def get_personal_by_area(area):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.get_personal_by_area(area)


@personal_bp.route('/personal/estadisticas', methods=['GET'])
@token_required
def get_personal_estadisticas():
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.get_estadisticas()


# ============================================
# ESPECIALIDADES DEL PERSONAL
# ============================================
@personal_bp.route('/personal/<int:personal_id>/especialidades', methods=['GET'])
@token_required
def get_personal_especialidades(personal_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.get_personal_especialidades(personal_id)


@personal_bp.route('/personal/<int:personal_id>/especialidades', methods=['POST'])
@admin_required
def assign_especialidad_to_personal(personal_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.assign_especialidad(personal_id)


@personal_bp.route('/personal/<int:personal_id>/especialidades/<int:especialidad_id>', methods=['PUT'])
@admin_required
def update_especialidad_personal(personal_id, especialidad_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.update_especialidad(personal_id, especialidad_id)


@personal_bp.route('/personal/<int:personal_id>/especialidades/<int:especialidad_id>', methods=['DELETE'])
@admin_required
def remove_especialidad_from_personal(personal_id, especialidad_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.remove_especialidad(personal_id, especialidad_id)


@personal_bp.route('/personal/<int:personal_id>/especialidades-multiples', methods=['GET'])
@token_required
def get_personal_especialidades_multiples(personal_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.get_personal_especialidades(personal_id)


@personal_bp.route('/personal/<int:personal_id>/especialidades-multiples', methods=['POST'])
@admin_required
def agregar_especialidad_personal(personal_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.assign_especialidad(personal_id)


@personal_bp.route('/personal/<int:personal_id>/especialidades-multiples/<int:especialidad_id>', methods=['DELETE'])
@admin_required
def remover_especialidad_personal(personal_id, especialidad_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.remove_especialidad(personal_id, especialidad_id)


@personal_bp.route('/personal/por-especialidad/<int:especialidad_id>', methods=['GET'])
@token_required
def get_personal_por_especialidad(especialidad_id):
    from src.api.Service.PersonalService import PersonalService
    centro_id = request.args.get('centro_id', type=int)
    return PersonalService.get_personal_by_especialidad(especialidad_id, centro_id)


@personal_bp.route('/personal/<int:personal_id>/especialidades-disponibles', methods=['GET'])
@token_required
def get_especialidades_disponibles_personal(personal_id):
    from src.api.Service.PersonalService import PersonalService
    return PersonalService.get_especialidades_disponibles(personal_id)


# ============================================
# DOCUMENTOS DEL PERSONAL
# ============================================
@personal_bp.route('/personal/<int:personal_id>/documentos', methods=['GET'])
@token_required
def get_documentos_personal(personal_id):
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    return DocumentoPersonalService.get_documentos_personal(personal_id)


@personal_bp.route('/personal/<int:personal_id>/documentos', methods=['POST'])
@token_required
def subir_documento_personal(personal_id):
    if request.form:
        request.form = request.form.copy()
        request.form['personal_id'] = str(personal_id)
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    return DocumentoPersonalService.subir_documento()


@personal_bp.route('/personal/<int:personal_id>/documentos/<int:documento_id>', methods=['DELETE'])
@token_required
def eliminar_documento_personal_por_personal(personal_id, documento_id):
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    return DocumentoPersonalService.eliminar_documento(documento_id)


@personal_bp.route('/documentos-personal/<int:documento_id>', methods=['GET'])
@token_required
def get_documento_personal(documento_id):
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    return DocumentoPersonalService.get_documento_by_id(documento_id)


@personal_bp.route('/documentos-personal/<int:documento_id>', methods=['PUT'])
@token_required
def actualizar_documento_personal(documento_id):
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    return DocumentoPersonalService.actualizar_documento_por_id(documento_id)


@personal_bp.route('/documentos-personal/<int:documento_id>', methods=['DELETE'])
@token_required
def eliminar_documento_personal(documento_id):
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    return DocumentoPersonalService.eliminar_documento(documento_id)


@personal_bp.route('/documentos-personal/<int:documento_id>/descargar', methods=['GET'])
@token_required
def descargar_documento_personal(documento_id):
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService

    HandleLogs.write_log(f"descargar_documento_personal - Iniciando descarga documento {documento_id}")
    result = DocumentoPersonalService.descargar_documento(documento_id)

    if result['success']:
        try:
            file_path = result['data']['ruta_archivo']
            file_name = result['data']['nombre_archivo']
            mime_type = result['data']['tipo_mime']

            if not os.path.exists(file_path):
                HandleLogs.write_error(f"descargar_documento_personal - Archivo no encontrado: {file_path}")
                return response_error("Archivo no encontrado en el sistema", 404)

            # Limpiar nombre de archivo
            clean_filename = file_name
            replacements = {
                'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u',
                'A': 'A', 'E': 'E', 'I': 'I', 'O': 'O', 'U': 'U',
                'n': 'n', 'N': 'N', 'u': 'u', 'U': 'U'
            }
            for original, replacement in replacements.items():
                clean_filename = clean_filename.replace(original, replacement)
            clean_filename = re.sub(r'[^\w\s\-\.\(\)]', '', clean_filename)
            clean_filename = re.sub(r'\s+', '_', clean_filename.strip())

            try:
                response = send_file(file_path, as_attachment=True,
                                   download_name=clean_filename, mimetype=mime_type)
            except TypeError:
                response = send_file(file_path, as_attachment=True,
                                   attachment_filename=clean_filename, mimetype=mime_type)

            response.headers['Content-Disposition'] = f'attachment; filename="{clean_filename}"'
            return response

        except Exception as e:
            HandleLogs.write_error(f"descargar_documento_personal - Error: {str(e)}")
            return response_error(f"Error enviando archivo: {str(e)}", 500)
    else:
        return response_error(result['message'], 404 if 'no encontrado' in result['message'].lower() else 400)


@personal_bp.route('/documentos-personal/tipo/<tipo_documento>', methods=['GET'])
@token_required
def get_documentos_por_tipo(tipo_documento):
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    centro_id = request.args.get('centro_id')
    if centro_id:
        try:
            centro_id = int(centro_id)
        except ValueError:
            return response_error("ID de centro invalido", 400)
    return DocumentoPersonalService.get_documentos_por_tipo(tipo_documento, centro_id)


@personal_bp.route('/documentos-personal/tipos', methods=['GET'])
@token_required
def get_tipos_documentos_personal():
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    return DocumentoPersonalService.obtener_tipos_documentos()


@personal_bp.route('/documentos-personal/vencimientos', methods=['GET'])
@token_required
def get_documentos_vencimientos():
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    dias_alerta = request.args.get('dias_alerta', 90, type=int)
    return DocumentoPersonalService.obtener_documentos_vencimientos(dias_alerta)


@personal_bp.route('/documentos-personal/pendientes-validacion', methods=['GET'])
@token_required
def get_documentos_pendientes_validacion():
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    return DocumentoPersonalService.obtener_documentos_pendientes_validacion()


@personal_bp.route('/documentos-personal/estadisticas', methods=['GET'])
@token_required
def get_estadisticas_documentos_personal():
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    return DocumentoPersonalService.obtener_estadisticas_documentos()


@personal_bp.route('/documentos-personal/buscar', methods=['GET'])
@token_required
def buscar_documentos_personal():
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    return DocumentoPersonalService.buscar_documentos()


@personal_bp.route('/documentos-personal/<int:documento_id>/validar', methods=['PUT'])
@token_required
def validar_documento_personal(documento_id):
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    return DocumentoPersonalService.validar_documento(documento_id)


@personal_bp.route('/documentos-personal/por-vencer', methods=['GET'])
@token_required
def get_documentos_por_vencer():
    from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
    dias_adelanto = request.args.get('dias', 30, type=int)
    centro_id = request.args.get('centro_id', type=int)
    return DocumentoPersonalService.get_documentos_por_vencer(dias_adelanto, centro_id)
