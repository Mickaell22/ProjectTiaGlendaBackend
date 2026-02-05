"""
Blueprint para rutas de usuarios.
"""
from flask import Blueprint, request
from src.utils.general.response import response_error
from src.utils.general.auth_middleware import token_required, admin_required

usuario_bp = Blueprint('usuario', __name__, url_prefix='/api')


@usuario_bp.route('/usuarios', methods=['GET'])
@admin_required
def get_usuarios():
    from src.api.Service.UsuarioService import UsuarioService
    return UsuarioService.get_usuarios()


@usuario_bp.route('/usuarios/<int:usuario_id>', methods=['GET'])
@token_required
def get_usuario(usuario_id):
    from src.api.Service.UsuarioService import UsuarioService
    return UsuarioService.get_usuario(usuario_id)


@usuario_bp.route('/usuarios', methods=['POST'])
@admin_required
def create_usuario():
    from src.api.Service.UsuarioService import UsuarioService
    return UsuarioService.create_usuario()


@usuario_bp.route('/usuarios/<int:usuario_id>', methods=['PUT'])
@admin_required
def update_usuario(usuario_id):
    from src.api.Service.UsuarioService import UsuarioService
    return UsuarioService.update_usuario(usuario_id)


@usuario_bp.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
@admin_required
def delete_usuario(usuario_id):
    from src.api.Service.UsuarioService import UsuarioService
    return UsuarioService.delete_usuario(usuario_id)


@usuario_bp.route('/usuarios/<int:usuario_id>/cambiar-contrasenia', methods=['PUT'])
@token_required
def change_user_password(usuario_id):
    try:
        from src.api.Service.UsuarioService import UsuarioService
        return UsuarioService.change_password(usuario_id, request.json)
    except Exception as e:
        return response_error(f"Error en cambio de contrasenia: {str(e)}", 500)
