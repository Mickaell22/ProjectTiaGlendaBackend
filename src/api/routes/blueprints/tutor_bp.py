"""
Blueprint para rutas de tutores.
"""
from flask import Blueprint
from src.utils.general.auth_middleware import token_required, admin_required

tutor_bp = Blueprint('tutor', __name__, url_prefix='/api')


@tutor_bp.route('/tutores', methods=['GET'])
@token_required
def get_tutores():
    from src.api.Service.TutorService import TutorService
    return TutorService.get_tutores()


@tutor_bp.route('/tutores/<int:tutor_id>', methods=['GET'])
@token_required
def get_tutor_by_id(tutor_id):
    from src.api.Service.TutorService import TutorService
    return TutorService.get_tutor_by_id(tutor_id)


@tutor_bp.route('/tutores', methods=['POST'])
@token_required
def create_tutor():
    from src.api.Service.TutorService import TutorService
    return TutorService.create_tutor()


@tutor_bp.route('/tutores/<int:tutor_id>', methods=['PUT'])
@token_required
def update_tutor(tutor_id):
    from src.api.Service.TutorService import TutorService
    return TutorService.update_tutor(tutor_id)


@tutor_bp.route('/tutores/<int:tutor_id>', methods=['DELETE'])
@admin_required
def delete_tutor(tutor_id):
    from src.api.Service.TutorService import TutorService
    return TutorService.delete_tutor(tutor_id)


@tutor_bp.route('/tutores/activos', methods=['GET'])
@token_required
def get_tutores_activos():
    from src.api.Service.TutorService import TutorService
    return TutorService.get_tutores_activos()


@tutor_bp.route('/tutores/estadisticas', methods=['GET'])
@token_required
def get_tutores_estadisticas():
    from src.api.Service.TutorService import TutorService
    return TutorService.get_estadisticas()


@tutor_bp.route('/tutores/personas-disponibles', methods=['GET'])
@token_required
def get_personas_disponibles_tutor():
    from src.api.Service.TutorService import TutorService
    return TutorService.get_personas_disponibles()
