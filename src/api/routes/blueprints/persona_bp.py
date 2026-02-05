"""
Blueprint para rutas de personas.
"""
from flask import Blueprint
from src.utils.general.auth_middleware import token_required, admin_required

persona_bp = Blueprint('persona', __name__, url_prefix='/api')


@persona_bp.route('/personas', methods=['GET'])
@token_required
def get_personas():
    from src.api.Service.PersonaService import PersonaService
    return PersonaService.get_personas()


@persona_bp.route('/personas/<int:persona_id>', methods=['GET'])
@token_required
def get_persona(persona_id):
    from src.api.Service.PersonaService import PersonaService
    return PersonaService.get_persona(persona_id)


@persona_bp.route('/personas', methods=['POST'])
@token_required
def create_persona():
    from src.api.Service.PersonaService import PersonaService
    return PersonaService.create_persona()


@persona_bp.route('/personas/<int:persona_id>', methods=['PUT'])
@token_required
def update_persona(persona_id):
    from src.api.Service.PersonaService import PersonaService
    return PersonaService.update_persona(persona_id)


@persona_bp.route('/personas/<int:persona_id>', methods=['DELETE'])
@admin_required
def delete_persona(persona_id):
    from src.api.Service.PersonaService import PersonaService
    return PersonaService.delete_persona(persona_id)


@persona_bp.route('/personas/disponibles', methods=['GET'])
@admin_required
def get_personas_disponibles():
    """Endpoint para obtener personas sin usuario"""
    from src.api.Service.PersonaService import PersonaService
    return PersonaService.get_personas_disponibles()
