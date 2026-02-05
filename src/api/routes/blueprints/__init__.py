"""
Registro central de todos los blueprints de la API.
"""
from .public_bp import public_bp
from .auth_bp import auth_bp
from .centro_bp import centro_bp
from .rol_bp import rol_bp
from .persona_bp import persona_bp
from .especialidad_bp import especialidad_bp
from .personal_bp import personal_bp
from .usuario_bp import usuario_bp
from .tutor_bp import tutor_bp
from .paciente_bp import paciente_bp
from .sesion_terapia_bp import sesion_terapia_bp
from .sesion_pedagogica_bp import sesion_pedagogica_bp
from .dashboard_bp import dashboard_bp


# Lista de todos los blueprints disponibles
ALL_BLUEPRINTS = [
    public_bp,
    auth_bp,
    centro_bp,
    rol_bp,
    persona_bp,
    especialidad_bp,
    personal_bp,
    usuario_bp,
    tutor_bp,
    paciente_bp,
    sesion_terapia_bp,
    sesion_pedagogica_bp,
    dashboard_bp,
]


def register_all_blueprints(app):
    """
    Registra todos los blueprints en la aplicacion Flask.

    Args:
        app: Instancia de Flask
    """
    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)
