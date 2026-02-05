"""
Blueprint para rutas de especialidades.
"""
from flask import Blueprint
from src.utils.general.auth_middleware import token_required, admin_required

especialidad_bp = Blueprint('especialidad', __name__, url_prefix='/api')


@especialidad_bp.route('/especialidades', methods=['GET'])
@token_required
def get_especialidades():
    from src.api.Service.EspecialidadService import EspecialidadService
    return EspecialidadService.get_especialidades()


@especialidad_bp.route('/especialidades/<area>', methods=['GET'])
@token_required
def get_especialidades_by_area(area):
    from src.api.Service.EspecialidadService import EspecialidadService
    return EspecialidadService.get_especialidades_by_area(area)


@especialidad_bp.route('/especialidades/id/<int:especialidad_id>', methods=['GET'])
@token_required
def get_especialidad(especialidad_id):
    from src.api.Service.EspecialidadService import EspecialidadService
    return EspecialidadService.get_especialidad(especialidad_id)


@especialidad_bp.route('/especialidades', methods=['POST'])
@admin_required
def create_especialidad():
    from src.api.Service.EspecialidadService import EspecialidadService
    return EspecialidadService.create_especialidad()


@especialidad_bp.route('/especialidades/id/<int:especialidad_id>', methods=['PUT'])
@admin_required
def update_especialidad(especialidad_id):
    from src.api.Service.EspecialidadService import EspecialidadService
    return EspecialidadService.update_especialidad(especialidad_id)


@especialidad_bp.route('/especialidades/id/<int:especialidad_id>', methods=['DELETE'])
@admin_required
def delete_especialidad(especialidad_id):
    from src.api.Service.EspecialidadService import EspecialidadService
    return EspecialidadService.delete_especialidad(especialidad_id)


@especialidad_bp.route('/especialidades/id/<int:especialidad_id>/reactivar', methods=['PUT'])
@admin_required
def activate_especialidad(especialidad_id):
    """Reactivar una especialidad inactiva"""
    from src.api.Service.EspecialidadService import EspecialidadService
    return EspecialidadService.activate_especialidad(especialidad_id)


@especialidad_bp.route('/especialidades/activas', methods=['GET'])
@token_required
def get_especialidades_activas():
    from src.api.Service.EspecialidadService import EspecialidadService
    return EspecialidadService.get_especialidades_activas()


@especialidad_bp.route('/especialidades/estadisticas', methods=['GET'])
@token_required
def get_especialidades_estadisticas():
    from src.api.Service.EspecialidadService import EspecialidadService
    return EspecialidadService.get_estadisticas()


@especialidad_bp.route('/compatibilidad-especialidades/<int:personal_id>/<int:paciente_id>', methods=['GET'])
@token_required
def verificar_compatibilidad_especialidades(personal_id, paciente_id):
    """Verificar compatibilidad de especialidades entre personal y paciente"""
    from src.api.Service.EspecialidadService import EspecialidadService
    return EspecialidadService.verificar_compatibilidad(personal_id, paciente_id)


@especialidad_bp.route('/especialidades-multiples/estadisticas', methods=['GET'])
@token_required
def get_estadisticas_especialidades_multiples():
    """Obtener estadisticas de especialidades multiples"""
    from src.api.Service.EspecialidadService import EspecialidadService
    return EspecialidadService.get_estadisticas_multiples()
