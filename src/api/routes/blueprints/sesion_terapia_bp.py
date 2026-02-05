"""
Blueprint para rutas de sesiones de terapia.
"""
from flask import Blueprint
from src.utils.general.response import response_success, response_error
from src.utils.general.auth_middleware import token_required, admin_required

sesion_terapia_bp = Blueprint('sesion_terapia', __name__, url_prefix='/api')


# ============================================
# RUTAS CRUD DE SESIONES
# ============================================
@sesion_terapia_bp.route('/sesiones-terapia', methods=['GET'])
@token_required
def get_sesiones_terapia():
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_sesiones()


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>', methods=['GET'])
@token_required
def get_sesion_terapia(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_sesion(sesion_id)


@sesion_terapia_bp.route('/sesiones-terapia', methods=['POST'])
@token_required
def create_sesion_terapia():
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.create_sesion()


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>', methods=['PUT'])
@token_required
def update_sesion_terapia(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.update_sesion(sesion_id)


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>', methods=['DELETE'])
@admin_required
def delete_sesion_terapia(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.delete_sesion(sesion_id)


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/finalizar', methods=['PUT'])
@token_required
def finalizar_sesion_terapia(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.finalizar_sesion(sesion_id)


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/cancelar', methods=['PUT'])
@token_required
def cancelar_sesion_terapia(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.cancelar_sesion(sesion_id)


# ============================================
# PACIENTES EN SESIONES
# ============================================
@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/pacientes', methods=['GET'])
@token_required
def get_pacientes_sesion(sesion_id):
    from src.api.Components.SesionTerapiaComponent import SesionTerapiaComponent
    try:
        pacientes = SesionTerapiaComponent.get_pacientes_sesion(sesion_id)
        return response_success(pacientes or [], "Pacientes de la sesion obtenidos")
    except Exception as e:
        return response_error(f"Error al obtener pacientes: {str(e)}", 500)


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/pacientes', methods=['POST'])
@token_required
def add_paciente_sesion(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.add_paciente_to_sesion(sesion_id)


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/pacientes/<int:paciente_id>', methods=['DELETE'])
@token_required
def remove_paciente_sesion(sesion_id, paciente_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.remove_paciente_from_sesion(sesion_id, paciente_id)


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/pacientes-retirados', methods=['GET'])
@token_required
def get_pacientes_retirados_sesion(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_pacientes_retirados(sesion_id)


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/pacientes/<int:paciente_id>/reincorporar', methods=['PUT'])
@token_required
def reincorporar_paciente_sesion(sesion_id, paciente_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.reincorporar_paciente(sesion_id, paciente_id)


# ============================================
# CRONOGRAMA
# ============================================
@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/cronograma', methods=['GET'])
@token_required
def get_cronograma_sesion(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_cronograma_sesion(sesion_id)


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/cronograma/generar', methods=['POST'])
@token_required
def generar_cronograma_sesion(sesion_id):
    from src.api.Components.SesionTerapiaComponent import SesionTerapiaComponent
    try:
        SesionTerapiaComponent.generar_cronograma(sesion_id)
        return response_success({'sesion_id': sesion_id}, "Cronograma generado exitosamente")
    except Exception as e:
        return response_error(f"Error al generar cronograma: {str(e)}", 500)


@sesion_terapia_bp.route('/sesiones-terapia/cronograma/<int:cronograma_id>/realizar', methods=['PUT'])
@token_required
def marcar_sesion_realizada(cronograma_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.marcar_sesion_realizada(cronograma_id)


@sesion_terapia_bp.route('/sesiones-terapia/cronograma/<int:cronograma_id>/reprogramar', methods=['PUT'])
@token_required
def reprogramar_sesion_cronograma(cronograma_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.reprogramar_sesion_cronograma(cronograma_id)


@sesion_terapia_bp.route('/sesiones-terapia/cronograma/<int:cronograma_id>/cancelar', methods=['PUT'])
@token_required
def cancelar_sesion_cronograma(cronograma_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.cancelar_sesion_cronograma(cronograma_id)


# ============================================
# CONSULTAS Y REPORTES
# ============================================
@sesion_terapia_bp.route('/sesiones-terapia/terapeuta/<int:terapeuta_id>', methods=['GET'])
@token_required
def get_sesiones_by_terapeuta(terapeuta_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_sesiones_by_terapeuta(terapeuta_id)


@sesion_terapia_bp.route('/sesiones-terapia/hoy', methods=['GET'])
@token_required
def get_sesiones_hoy():
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_sesiones_hoy()


@sesion_terapia_bp.route('/sesiones-terapia/estadisticas', methods=['GET'])
@token_required
def get_estadisticas_sesiones():
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_estadisticas()


# ============================================
# DATOS AUXILIARES
# ============================================
@sesion_terapia_bp.route('/sesiones-terapia/pacientes-disponibles', methods=['GET'])
@token_required
def get_pacientes_disponibles_sesiones():
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_pacientes_disponibles()


@sesion_terapia_bp.route('/sesiones-terapia/terapeutas-disponibles', methods=['GET'])
@token_required
def get_terapeutas_disponibles_sesiones():
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_terapeutas_disponibles()


# ============================================
# ASISTENCIA
# ============================================
@sesion_terapia_bp.route('/sesiones-terapia/cronograma/<int:cronograma_id>/pacientes/<int:paciente_id>/asistencia', methods=['POST'])
@token_required
def registrar_asistencia_sesion(cronograma_id, paciente_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.registrar_asistencia(cronograma_id, paciente_id)


@sesion_terapia_bp.route('/sesiones-terapia/cronograma/<int:cronograma_id>/pacientes/<int:paciente_id>/asistencia', methods=['PUT'])
@token_required
def actualizar_asistencia_sesion(cronograma_id, paciente_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.actualizar_asistencia(cronograma_id, paciente_id)


@sesion_terapia_bp.route('/sesiones-terapia/cronograma/<int:cronograma_id>/asistencia', methods=['GET'])
@token_required
def get_asistencia_cronograma(cronograma_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_asistencia_cronograma(cronograma_id)


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/asistencias', methods=['GET'])
@token_required
def get_asistencias_por_sesion(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_asistencias_por_sesion(sesion_id)


@sesion_terapia_bp.route('/sesiones-terapia/asistencias/paciente/<int:paciente_id>', methods=['GET'])
@token_required
def get_asistencias_por_paciente(paciente_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_asistencias_por_paciente(paciente_id)


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/estadisticas-asistencia', methods=['GET'])
@token_required
def get_estadisticas_asistencia(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_estadisticas_asistencia(sesion_id)


@sesion_terapia_bp.route('/sesiones-terapia/cronograma/<int:cronograma_id>/control-asistencia', methods=['GET'])
@token_required
def get_control_asistencia(cronograma_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.get_control_asistencia(cronograma_id)


# ============================================
# ENLACES PUBLICOS
# ============================================
@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/generar-enlace-publico', methods=['POST'])
@token_required
def generar_enlace_publico_terapia(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.generar_enlace_publico(sesion_id)


@sesion_terapia_bp.route('/sesiones-terapia/<int:sesion_id>/enlaces-publicos', methods=['GET'])
@token_required
def obtener_enlaces_publicos_terapia(sesion_id):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.obtener_enlaces_publicos(sesion_id)


@sesion_terapia_bp.route('/sesiones-terapia/enlace-publico/<string:token>/invalidar', methods=['DELETE'])
@token_required
def invalidar_enlace_publico_terapia(token):
    from src.api.Service.SesionTerapiaService import SesionTerapiaService
    return SesionTerapiaService.invalidar_enlace_publico(token)
