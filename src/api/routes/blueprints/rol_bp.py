"""
Blueprint para rutas de roles.
"""
from flask import Blueprint, request
from src.utils.general.auth_middleware import token_required, admin_required

rol_bp = Blueprint('rol', __name__, url_prefix='/api')


@rol_bp.route('/roles', methods=['GET'])
@token_required
def get_roles():
    from src.api.Service.RolService import RolService
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    return RolService.get_roles(include_inactive)


@rol_bp.route('/roles/<int:rol_id>', methods=['GET'])
@token_required
def get_rol(rol_id):
    from src.api.Service.RolService import RolService
    return RolService.get_rol_by_id(rol_id)


@rol_bp.route('/roles', methods=['POST'])
@admin_required
def create_rol():
    from src.api.Service.RolService import RolService
    data = request.get_json() or {}
    usuario_id = request.current_user.get('id') if hasattr(request, 'current_user') else None
    return RolService.create_rol(data, usuario_id)


@rol_bp.route('/roles/<int:rol_id>', methods=['PUT'])
@admin_required
def update_rol(rol_id):
    from src.api.Service.RolService import RolService
    data = request.get_json() or {}
    usuario_id = request.current_user.get('id') if hasattr(request, 'current_user') else None
    return RolService.update_rol(rol_id, data, usuario_id)


@rol_bp.route('/roles/<int:rol_id>', methods=['DELETE'])
@admin_required
def delete_rol(rol_id):
    from src.api.Service.RolService import RolService
    usuario_id = request.current_user.get('id') if hasattr(request, 'current_user') else None
    return RolService.delete_rol(rol_id, usuario_id)


@rol_bp.route('/roles/<int:rol_id>/reactivar', methods=['PUT'])
@admin_required
def reactivate_rol(rol_id):
    from src.api.Service.RolService import RolService
    usuario_id = request.current_user.get('id') if hasattr(request, 'current_user') else None
    return RolService.reactivate_rol(rol_id, usuario_id)
