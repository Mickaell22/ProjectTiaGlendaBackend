"""
Blueprint para rutas de sesiones pedagogicas.
"""
from flask import Blueprint
from src.utils.general.auth_middleware import token_required, admin_required

sesion_pedagogica_bp = Blueprint('sesion_pedagogica', __name__, url_prefix='/api')


# ============================================
# RUTAS CRUD DE SESIONES
# ============================================
@sesion_pedagogica_bp.route('/sesiones-pedagogicas', methods=['GET'])
@token_required
def get_sesiones_pedagogicas():
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.get_sesiones()


@sesion_pedagogica_bp.route('/sesiones-pedagogicas', methods=['POST'])
@token_required
def create_sesion_pedagogica():
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.create_sesion()


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>', methods=['GET'])
@token_required
def get_sesion_pedagogica(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.get_sesion(sesion_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>', methods=['PUT'])
@token_required
def update_sesion_pedagogica(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.update_sesion(sesion_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>', methods=['DELETE'])
@admin_required
def delete_sesion_pedagogica(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.delete_sesion(sesion_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/cancelar', methods=['PUT'])
@token_required
def cancelar_sesion_pedagogica(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.cancelar_sesion(sesion_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/finalizar', methods=['PUT'])
@token_required
def finalizar_sesion_pedagogica(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.finalizar_sesion(sesion_id)


# ============================================
# DATOS AUXILIARES Y ESTADISTICAS
# ============================================
@sesion_pedagogica_bp.route('/sesiones-pedagogicas/estudiantes-disponibles', methods=['GET'])
@token_required
def get_estudiantes_disponibles():
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.get_estudiantes_disponibles()


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/pedagogos-disponibles', methods=['GET'])
@token_required
def get_pedagogos_disponibles():
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.get_pedagogos_disponibles()


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/estadisticas', methods=['GET'])
@token_required
def get_estadisticas_pedagogicas():
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.get_estadisticas()


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/cronograma-general', methods=['GET'])
@token_required
def get_cronograma_general_pedagogico():
    from flask import request as req
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    filtros = {
        'especialidad': req.args.get('especialidad'),
        'pedagogo': req.args.get('pedagogo'),
        'semana': req.args.get('semana')
    }
    return SesionPedagogicaService.get_cronograma_sesiones(filtros)


# ============================================
# CRONOGRAMA
# ============================================
@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/cronograma', methods=['GET'])
@token_required
def get_cronograma_pedagogico(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.get_cronograma_sesion(sesion_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/cronograma/<int:cronograma_id>/realizar', methods=['PUT'])
@token_required
def marcar_clase_realizada(cronograma_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.marcar_clase_realizada(cronograma_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/cronograma/<int:cronograma_id>/reprogramar', methods=['PUT'])
@token_required
def reprogramar_clase(cronograma_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.reprogramar_clase(cronograma_id)


@sesion_pedagogica_bp.route('/cronograma-clases/<int:cronograma_id>', methods=['PUT'])
@token_required
def actualizar_cronograma_clase(cronograma_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.actualizar_cronograma_clase(cronograma_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/cronograma/<int:cronograma_id>/cancelar', methods=['PUT'])
@token_required
def cancelar_clase(cronograma_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.cancelar_clase(cronograma_id)


# ============================================
# ESTUDIANTES EN SESIONES
# ============================================
@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/estudiantes', methods=['GET'])
@token_required
def get_estudiantes_sesion_pedagogica(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.get_estudiantes_sesion(sesion_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/estudiantes', methods=['POST'])
@token_required
def add_estudiante_sesion_pedagogica(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.add_estudiante_to_sesion(sesion_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/estudiantes/<int:paciente_id>', methods=['DELETE'])
@token_required
def remove_estudiante_sesion_pedagogica(sesion_id, paciente_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.remove_estudiante_from_sesion(sesion_id, paciente_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/estudiantes-retirados', methods=['GET'])
@token_required
def get_estudiantes_retirados_sesion_pedagogica(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.get_estudiantes_retirados(sesion_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/estudiantes/<int:paciente_id>/reincorporar', methods=['PUT'])
@token_required
def reincorporar_estudiante_sesion_pedagogica(sesion_id, paciente_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.reincorporar_estudiante(sesion_id, paciente_id)


# ============================================
# ASISTENCIA
# ============================================
@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/asistencias', methods=['GET'])
@token_required
def get_asistencias_por_sesion_pedagogica(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.get_asistencias_por_sesion(sesion_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/cronograma/<int:cronograma_id>/control-asistencia', methods=['GET'])
@token_required
def get_control_asistencia_clase(cronograma_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.get_control_asistencia(cronograma_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/cronograma/<int:cronograma_id>/estudiantes/<int:estudiante_id>/asistencia', methods=['POST'])
@token_required
def registrar_asistencia_estudiante(cronograma_id, estudiante_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.registrar_asistencia(cronograma_id, estudiante_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/cronograma/<int:cronograma_id>/estudiantes/<int:estudiante_id>/asistencia', methods=['PUT'])
@token_required
def actualizar_asistencia_estudiante(cronograma_id, estudiante_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.actualizar_asistencia(cronograma_id, estudiante_id)


# ============================================
# ENLACES PUBLICOS
# ============================================
@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/generar-enlace-publico', methods=['POST'])
@token_required
def generar_enlace_publico_pedagogico(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.generar_enlace_publico(sesion_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/enlaces-publicos', methods=['GET'])
@token_required
def obtener_enlaces_publicos_pedagogico(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.obtener_enlaces_publicos(sesion_id)


@sesion_pedagogica_bp.route('/sesiones-pedagogicas/invalidar-enlace-publico/<string:token>', methods=['PUT'])
@token_required
def invalidar_enlace_publico_pedagogico(token):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.invalidar_enlace_publico(token)


# ============================================
# REACTIVAR SESION
# ============================================
@sesion_pedagogica_bp.route('/sesiones-pedagogicas/<int:sesion_id>/reactivar', methods=['PUT'])
@token_required
def reactivar_sesion_pedagogica(sesion_id):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.reactivar_sesion(sesion_id)


# ============================================
# VISTA PUBLICA (sin autenticacion)
# ============================================
@sesion_pedagogica_bp.route('/sesion-pedagogica-publica/<string:token>', methods=['GET'])
def ver_sesion_pedagogica_publica(token):
    from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
    return SesionPedagogicaService.ver_sesion_publica(token)
