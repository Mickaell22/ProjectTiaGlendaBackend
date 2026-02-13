"""
Blueprint para rutas de autenticacion y manejo de centros del usuario.
"""
from flask import Blueprint
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success
from src.utils.general.auth_middleware import token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/login', methods=['POST'])
def login():
    from src.api.Service.LoginService import LoginService
    return LoginService.login()


@auth_bp.route('/centros-disponibles', methods=['GET'])
def get_centros_disponibles():
    """Obtener centros disponibles para selector de login"""
    from src.api.Service.LoginService import LoginService
    return LoginService.get_centros_disponibles()


@auth_bp.route('/verify-token', methods=['GET'])
@token_required
def verify_token():
    from src.api.Service.LoginService import LoginService
    return LoginService.verify_token()


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    HandleLogs.write_log("Logout solicitado")
    return response_success(None, "Sesion cerrada exitosamente")


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    from src.api.Service.AuthService import AuthService
    return AuthService.get_me()


@auth_bp.route('/seleccionar-centro', methods=['POST'])
@token_required
def seleccionar_centro():
    """Seleccionar centro despues del login"""
    from src.api.Service.AuthService import AuthService
    return AuthService.seleccionar_centro()


@auth_bp.route('/cambiar-centro', methods=['POST'])
@token_required
def cambiar_centro():
    """Cambiar de centro sin hacer logout"""
    from src.api.Service.AuthService import AuthService
    return AuthService.cambiar_centro()


@auth_bp.route('/mis-centros', methods=['GET'])
@token_required
def get_mis_centros():
    """Obtener centros disponibles del usuario autenticado"""
    from src.api.Service.AuthService import AuthService
    return AuthService.get_centros_disponibles()
