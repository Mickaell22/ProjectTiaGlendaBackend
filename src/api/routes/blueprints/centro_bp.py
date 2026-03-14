"""
Blueprint para rutas de gestion de centros.
"""
from flask import Blueprint, request
from src.utils.general.response import response_success, response_error, response_inserted
from src.utils.general.auth_middleware import token_required, admin_required

centro_bp = Blueprint('centro', __name__, url_prefix='/api')


@centro_bp.route('/centros', methods=['GET'])
@token_required
def get_centros():
    """Obtener todos los centros activos"""
    from src.api.Service.CentroService import CentroService
    result = CentroService.get_all_centros()
    if result["success"]:
        return response_success(result["data"], result["message"])
    return response_error(result["message"], 400)


@centro_bp.route('/centros/<int:centro_id>', methods=['GET'])
@token_required
def get_centro(centro_id):
    """Obtener un centro por ID"""
    from src.api.Service.CentroService import CentroService
    result = CentroService.get_centro_by_id(centro_id)
    if result["success"]:
        return response_success(result["data"], result["message"])
    return response_error(result["message"], 404)


@centro_bp.route('/centros/codigo/<string:codigo>', methods=['GET'])
@token_required
def get_centro_by_codigo(codigo):
    """Obtener un centro por codigo"""
    from src.api.Service.CentroService import CentroService
    result = CentroService.get_centro_by_codigo(codigo)
    if result["success"]:
        return response_success(result["data"], result["message"])
    return response_error(result["message"], 404)


@centro_bp.route('/centros/<int:centro_id>/estadisticas', methods=['GET'])
@token_required
def get_centro_estadisticas(centro_id):
    """Obtener estadisticas de un centro"""
    from src.api.Service.CentroService import CentroService
    result = CentroService.get_centro_statistics(centro_id)
    if result["success"]:
        return response_success(result["data"], result["message"])
    return response_error(result["message"], 400)


@centro_bp.route('/centros', methods=['POST'])
@admin_required
def create_centro():
    """Crear un nuevo centro"""
    from src.api.Service.CentroService import CentroService
    data = request.get_json()
    if not data:
        return response_error("Datos requeridos", 400)
    result = CentroService.create_centro(data)
    if result["success"]:
        return response_inserted(result["data"], result["message"])
    return response_error(result["message"], 400)


@centro_bp.route('/centros/<int:centro_id>', methods=['PUT'])
@admin_required
def update_centro(centro_id):
    """Actualizar un centro"""
    from src.api.Service.CentroService import CentroService
    data = request.get_json()
    if not data:
        return response_error("Datos requeridos", 400)
    result = CentroService.update_centro(centro_id, data)
    if result["success"]:
        return response_success(result["data"], result["message"])
    return response_error(result["message"], 400)


@centro_bp.route('/centros/<int:centro_id>', methods=['DELETE'])
@admin_required
def delete_centro(centro_id):
    """Eliminar un centro (soft delete)"""
    from src.api.Service.CentroService import CentroService
    usuario_id = request.current_user.get('id', 1)
    result = CentroService.delete_centro(centro_id, usuario_id)
    if result["success"]:
        return response_success(result["data"], result["message"])
    return response_error(result["message"], 400)


@centro_bp.route('/centros/<int:centro_id>/reactivar', methods=['PUT'])
@admin_required
def activate_centro(centro_id):
    """Reactivar un centro inactivo"""
    from src.api.Service.CentroService import CentroService
    usuario_id = request.current_user.get('id', 1)
    result = CentroService.activate_centro(centro_id, usuario_id)
    if result["success"]:
        return response_success(result["data"], result["message"])
    return response_error(result["message"], 400)
