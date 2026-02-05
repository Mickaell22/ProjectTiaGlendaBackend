"""
Blueprint para rutas de pacientes, especialidades, pausas y documentos.
"""
from flask import Blueprint, request, send_file
import os
import re
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error
from src.utils.general.auth_middleware import token_required, admin_required

paciente_bp = Blueprint('paciente', __name__, url_prefix='/api')


# ============================================
# RUTAS CRUD DE PACIENTES
# ============================================
@paciente_bp.route('/pacientes', methods=['GET'])
@token_required
def get_pacientes():
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.get_pacientes()


@paciente_bp.route('/pacientes/<int:paciente_id>', methods=['GET'])
@token_required
def get_paciente_by_id(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.get_paciente_by_id(paciente_id)


@paciente_bp.route('/pacientes', methods=['POST'])
@token_required
def create_paciente():
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.create_paciente()


@paciente_bp.route('/pacientes/<int:paciente_id>', methods=['PUT'])
@token_required
def update_paciente(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.update_paciente(paciente_id)


@paciente_bp.route('/pacientes/<int:paciente_id>/estado', methods=['PUT'])
@token_required
def change_estado_paciente(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.change_estado_paciente(paciente_id)


@paciente_bp.route('/pacientes/tutor/<int:tutor_id>', methods=['GET'])
@token_required
def get_pacientes_by_tutor(tutor_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.get_pacientes_by_tutor(tutor_id)


@paciente_bp.route('/pacientes/estadisticas', methods=['GET'])
@token_required
def get_pacientes_estadisticas():
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.get_estadisticas()


@paciente_bp.route('/pacientes/personas-disponibles', methods=['GET'])
@token_required
def get_personas_disponibles_paciente():
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.get_personas_disponibles()


@paciente_bp.route('/pacientes/<int:paciente_id>', methods=['DELETE'])
@admin_required
def delete_paciente(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.delete_paciente(paciente_id)


@paciente_bp.route('/pacientes/por-especialidad/<int:especialidad_id>', methods=['GET'])
@token_required
def get_pacientes_por_especialidad(especialidad_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.get_pacientes_por_especialidad(especialidad_id)


# ============================================
# ESPECIALIDADES DE PACIENTES
# ============================================
@paciente_bp.route('/pacientes/<int:paciente_id>/especialidades', methods=['POST'])
@token_required
def assign_especialidad_paciente(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.agregar_especialidad_paciente(paciente_id)


@paciente_bp.route('/pacientes/<int:paciente_id>/especialidades', methods=['GET'])
@token_required
def get_paciente_especialidades(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.get_especialidades_paciente(paciente_id)


@paciente_bp.route('/pacientes/<int:paciente_id>/especialidades/<int:especialidad_id>', methods=['DELETE'])
@token_required
def remove_especialidad_paciente(paciente_id, especialidad_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.remover_especialidad_paciente(paciente_id, especialidad_id)


@paciente_bp.route('/pacientes/<int:paciente_id>/especialidad-principal', methods=['PUT'])
@token_required
def cambiar_especialidad_principal_paciente(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.cambiar_especialidad_principal(paciente_id)


@paciente_bp.route('/pacientes/<int:paciente_id>/especialidades-multiples', methods=['GET'])
@token_required
def get_paciente_especialidades_multiples(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.get_especialidades_paciente(paciente_id)


@paciente_bp.route('/pacientes/<int:paciente_id>/especialidades-multiples', methods=['POST'])
@token_required
def agregar_especialidad_paciente(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.agregar_especialidad_paciente(paciente_id)


@paciente_bp.route('/pacientes/<int:paciente_id>/especialidades-multiples/<int:especialidad_id>', methods=['DELETE'])
@token_required
def remover_especialidad_paciente_multiple(paciente_id, especialidad_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.remover_especialidad_paciente(paciente_id, especialidad_id)


# ============================================
# CONTROL DE PAUSAS
# ============================================
@paciente_bp.route('/pacientes/<int:paciente_id>/pausar', methods=['PUT'])
@token_required
def pausar_paciente_general(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    usuario_actual = request.current_user
    return PacienteService.pausar_paciente_general(paciente_id, usuario_actual)


@paciente_bp.route('/pacientes/<int:paciente_id>/reactivar', methods=['PUT'])
@token_required
def reactivar_paciente_general(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    usuario_actual = request.current_user
    return PacienteService.reactivar_paciente_general(paciente_id, usuario_actual)


@paciente_bp.route('/pacientes/<int:paciente_id>/especialidades-multiples/<int:especialidad_id>/pausar', methods=['PUT'])
@token_required
def pausar_especialidad_paciente(paciente_id, especialidad_id):
    from src.api.Service.PacienteService import PacienteService
    usuario_actual = request.current_user
    return PacienteService.pausar_especialidad_paciente(paciente_id, especialidad_id, usuario_actual)


@paciente_bp.route('/pacientes/<int:paciente_id>/especialidades-multiples/<int:especialidad_id>/reactivar', methods=['PUT'])
@token_required
def reactivar_especialidad_paciente(paciente_id, especialidad_id):
    from src.api.Service.PacienteService import PacienteService
    usuario_actual = request.current_user
    return PacienteService.reactivar_especialidad_paciente(paciente_id, especialidad_id, usuario_actual)


@paciente_bp.route('/pacientes/pausados', methods=['GET'])
@token_required
def get_pacientes_pausados():
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.get_pacientes_pausados()


@paciente_bp.route('/pacientes/<int:paciente_id>/pausas', methods=['GET'])
@token_required
def get_estado_pausas_paciente(paciente_id):
    from src.api.Service.ControlPausasService import ControlPausasService
    return ControlPausasService.get_estado_pausas_paciente(paciente_id)


@paciente_bp.route('/pacientes/<int:paciente_id>/pausa-activa', methods=['GET'])
@token_required
def verificar_pausa_activa(paciente_id):
    from src.api.Service.ControlPausasService import ControlPausasService
    return ControlPausasService.verificar_pausa_activa(paciente_id)


@paciente_bp.route('/pacientes/<int:paciente_id>/historial-pausas', methods=['GET'])
@token_required
def get_historial_pausas(paciente_id):
    from src.api.Service.ControlPausasService import ControlPausasService
    return ControlPausasService.get_historial_pausas(paciente_id)


@paciente_bp.route('/control-pausas/vencidas', methods=['GET'])
@token_required
def get_pausas_vencidas():
    from src.api.Service.ControlPausasService import ControlPausasService
    return ControlPausasService.get_pausas_vencidas()


@paciente_bp.route('/control-pausas/proximas-vencer', methods=['GET'])
@token_required
def get_pausas_proximas_vencer():
    from src.api.Service.ControlPausasService import ControlPausasService
    dias = request.args.get('dias', default=7, type=int)
    return ControlPausasService.get_pausas_proximas_vencer(dias)


@paciente_bp.route('/control-pausas/procesar-automaticas', methods=['POST'])
@token_required
def procesar_pausas_automaticas():
    from src.api.Service.ControlPausasService import ControlPausasService
    return ControlPausasService.procesar_pausas_automaticas()


@paciente_bp.route('/control-pausas/estadisticas', methods=['GET'])
@token_required
def get_estadisticas_pausas():
    from src.api.Service.ControlPausasService import ControlPausasService
    return ControlPausasService.get_estadisticas_pausas()


# ============================================
# DOCUMENTOS DE PACIENTES
# ============================================
@paciente_bp.route('/pacientes/<int:paciente_id>/documentos', methods=['POST'])
@token_required
def upload_documento_paciente(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.upload_documento(paciente_id)


@paciente_bp.route('/pacientes/<int:paciente_id>/documentos', methods=['GET'])
@token_required
def get_documentos_paciente(paciente_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.get_documentos(paciente_id)


@paciente_bp.route('/pacientes/<int:paciente_id>/documentos/<int:documento_id>', methods=['GET'])
@token_required
def download_documento_paciente(paciente_id, documento_id):
    from src.api.Service.PacienteService import PacienteService

    result = PacienteService.download_documento(paciente_id, documento_id)

    if result['success']:
        try:
            file_path = result['data']['ruta_archivo']
            file_name = result['data']['nombre_original']
            mime_type = result['data']['tipo_mime']

            if not os.path.exists(file_path):
                HandleLogs.write_error(f"download_documento_paciente - File not found: {file_path}")
                return response_error("Archivo no encontrado en el sistema", 404)

            # Limpiar nombre de archivo
            replacements = {
                'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u',
                'A': 'A', 'E': 'E', 'I': 'I', 'O': 'O', 'U': 'U',
                'n': 'n', 'N': 'N', 'u': 'u', 'U': 'U'
            }

            clean_filename = file_name
            for original, replacement in replacements.items():
                clean_filename = clean_filename.replace(original, replacement)
            clean_filename = re.sub(r'[^\w\s\-\.\(\)]', '', clean_filename)
            clean_filename = re.sub(r'\s+', '_', clean_filename.strip())
            if not clean_filename.lower().endswith('.pdf'):
                clean_filename += '.pdf'

            try:
                response = send_file(file_path, as_attachment=True,
                                   download_name=clean_filename, mimetype=mime_type)
            except TypeError:
                response = send_file(file_path, as_attachment=True,
                                   attachment_filename=clean_filename, mimetype=mime_type)

            response.headers['Content-Disposition'] = f'attachment; filename="{clean_filename}"'
            return response

        except Exception as e:
            HandleLogs.write_error(f"download_documento_paciente - Error: {str(e)}")
            return response_error(f"Error enviando archivo: {str(e)}", 500)
    else:
        error_message = result.get('message', 'Error descargando documento')
        if 'no encontrado' in error_message.lower():
            return response_error(error_message, 404)
        return response_error(error_message, 400)


@paciente_bp.route('/pacientes/<int:paciente_id>/documentos/<int:documento_id>', methods=['PUT'])
@token_required
def update_documento_paciente(paciente_id, documento_id):
    from src.api.Components.DocumentoPacienteComponent import DocumentoPacienteComponent
    from src.utils.general.data_utils import DataUtils

    try:
        data = request.get_json()
        current_user_id = getattr(request, 'current_user', {}).get('id')

        if 'usuario_modificacion' not in data and current_user_id:
            data['usuario_modificacion'] = current_user_id

        prepared_data = DataUtils.prepare_update_data(data, current_user_id)
        result = DocumentoPacienteComponent.update_documento(documento_id, paciente_id, prepared_data)

        if result['success']:
            return response_success(result['data'], result['message'])
        return response_error(result['message'], 400)

    except Exception as e:
        HandleLogs.write_error(f"update_documento_paciente - Error: {str(e)}")
        return response_error(f"Error interno: {str(e)}", 500)


@paciente_bp.route('/pacientes/<int:paciente_id>/documentos/<int:documento_id>', methods=['DELETE'])
@token_required
def delete_documento_paciente(paciente_id, documento_id):
    from src.api.Service.PacienteService import PacienteService
    return PacienteService.delete_documento(paciente_id, documento_id)


@paciente_bp.route('/documentos/estadisticas', methods=['GET'])
@token_required
def get_estadisticas_documentos():
    from src.api.Components.DocumentoPacienteComponent import DocumentoPacienteComponent
    result = DocumentoPacienteComponent.get_estadisticas_documentos()
    if result['success']:
        return response_success(result['data'], result['message'])
    return response_error(result['message'], 500)


# ============================================
# GESTION DE TUTORES DE PACIENTES
# ============================================
@paciente_bp.route('/pacientes/<int:paciente_id>/tutores', methods=['GET'])
@token_required
def get_tutores_paciente(paciente_id):
    from src.api.Components.PacienteComponent import PacienteComponent
    result = PacienteComponent.get_tutores_paciente(paciente_id)
    if result['success']:
        return response_success(result['data'], result['message'])
    return response_error(result['message'], 500)


@paciente_bp.route('/pacientes/<int:paciente_id>/tutores', methods=['POST'])
@token_required
def agregar_tutor_paciente(paciente_id):
    from src.api.Components.PacienteComponent import PacienteComponent
    data = request.get_json()
    tutor_id = data.get('tutor_id') or data.get('id_tutor')
    if not tutor_id:
        return response_error("Campo requerido faltante: tutor_id", 400)
    result = PacienteComponent.agregar_tutor_paciente(paciente_id, int(tutor_id), data)
    if result['success']:
        return response_success(result['data'], result['message'])
    return response_error(result['message'], 400)


@paciente_bp.route('/pacientes/<int:paciente_id>/tutores/<int:tutor_id>', methods=['PUT'])
@token_required
def actualizar_relacion_tutor(paciente_id, tutor_id):
    from src.api.Components.PacienteComponent import PacienteComponent
    data = request.get_json()
    usuario_id = getattr(request, 'current_user', {}).get('id')
    result = PacienteComponent.actualizar_relacion_tutor(paciente_id, tutor_id, data, usuario_id)
    if result['success']:
        return response_success(result['data'], result['message'])
    return response_error(result['message'], 400)


@paciente_bp.route('/pacientes/<int:paciente_id>/tutores/<int:tutor_id>', methods=['DELETE'])
@token_required
def remover_tutor_paciente(paciente_id, tutor_id):
    from src.api.Components.PacienteComponent import PacienteComponent
    usuario_id = getattr(request, 'current_user', {}).get('id')
    result = PacienteComponent.remover_tutor_paciente(paciente_id, tutor_id, usuario_id)
    if result['success']:
        return response_success(result['data'], result['message'])
    return response_error(result['message'], 400)


@paciente_bp.route('/pacientes/<int:paciente_id>/tutor-principal', methods=['PUT'])
@token_required
def cambiar_tutor_principal(paciente_id):
    from src.api.Components.PacienteComponent import PacienteComponent
    data = request.get_json()
    nuevo_tutor_id = data.get('nuevo_tutor_id') or data.get('tutor_id')
    if not nuevo_tutor_id:
        return response_error("Campo requerido faltante: nuevo_tutor_id", 400)
    usuario_id = getattr(request, 'current_user', {}).get('id')
    result = PacienteComponent.cambiar_tutor_principal(paciente_id, int(nuevo_tutor_id), usuario_id)
    if result['success']:
        return response_success(result['data'], result['message'])
    return response_error(result['message'], 400)
