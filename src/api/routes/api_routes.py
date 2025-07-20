from flask import Blueprint
from datetime import datetime
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error
from src.utils.general.auth_middleware import token_required, admin_required

# Crear blueprint para las rutas del API
api_bp = Blueprint('api', __name__)


def register_routes(app):
    """Registrar todas las rutas del API"""

    # ============================================
    # RUTAS PÚBLICAS (Sin autenticación)
    # ============================================
    @app.route('/api/test', methods=['GET'])
    def test_api():
        HandleLogs.write_log("Acceso a ruta de prueba")
        return response_success({
            "message": "API Sistema Tia Glenda funcionando",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })

    @app.route('/api/test-db', methods=['GET'])
    def test_database():
        """Endpoint para probar la conexión a la base de datos"""
        try:
            from src.utils.database.connection_db import DataBaseHandle

            # Primero probar solo la conexión
            conn = DataBaseHandle.get_connection()
            if not conn:
                return response_error("No se pudo establecer conexion con la base de datos", 500)

            # Si la conexión funciona, probar una consulta simple
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()
                conn.close()

                # Ahora probar la consulta de usuarios
                query = "SELECT COUNT(*) as total_usuarios FROM usuario"
                result = DataBaseHandle.getRecords(query, size=1)

                if result:
                    HandleLogs.write_log("test_database - Conexion a base de datos exitosa")
                    return response_success({
                        "database": "centro_tia_glenda",
                        "postgresql_version": version[0] if version else "Unknown",
                        "total_usuarios": result['total_usuarios'],
                        "connection": "successful"
                    }, "Conexion a base de datos exitosa")
                else:
                    return response_error("Error en la consulta de usuarios", 500)

            except Exception as query_error:
                conn.close()
                HandleLogs.write_error(f"test_database - Error en consulta: {str(query_error)}")
                return response_error(f"Error en consulta: {str(query_error)}", 500)

        except Exception as e:
            HandleLogs.write_error(f"test_database - Error: {str(e)}")
            return response_error(f"Error de conexion: {str(e)}", 500)

    # ============================================
    # RUTAS DE AUTENTICACIÓN
    # ============================================
    @app.route('/api/login', methods=['POST'])
    def login():
        from src.api.Service.LoginService import LoginService
        return LoginService.login()

    @app.route('/api/verify-token', methods=['GET'])
    @token_required
    def verify_token():
        from src.api.Service.LoginService import LoginService
        return LoginService.verify_token()

    @app.route('/api/logout', methods=['POST'])
    @token_required
    def logout():
        # En JWT stateless, el logout se maneja en el frontend eliminando el token
        HandleLogs.write_log("Logout solicitado")
        return response_success(None, "Sesion cerrada exitosamente")

    # ============================================
    # RUTAS DE INFORMACIÓN DEL USUARIO ACTUAL
    # ============================================
    @app.route('/api/me', methods=['GET'])
    @token_required
    def get_current_user():
        from flask import request
        HandleLogs.write_log(f"Información solicitada para usuario: {request.current_user['usuario']}")
        return response_success(request.current_user, "Informacion del usuario actual")

    # ============================================
    # RUTAS DE ROLES (Protegidas - Solo lectura)
    # ============================================
    @app.route('/api/roles', methods=['GET'])
    @token_required
    def get_roles():
        from src.api.Service.RolService import RolService
        return RolService.get_roles()

    # ============================================
    # RUTAS DE PERSONAS (Protegidas)
    # ============================================
    @app.route('/api/personas', methods=['GET'])
    @token_required
    def get_personas():
        from src.api.Service.PersonaService import PersonaService
        return PersonaService.get_personas()

    @app.route('/api/personas/<int:persona_id>', methods=['GET'])
    @token_required
    def get_persona(persona_id):
        from src.api.Service.PersonaService import PersonaService
        return PersonaService.get_persona(persona_id)

    @app.route('/api/personas', methods=['POST'])
    @token_required
    def create_persona():
        from src.api.Service.PersonaService import PersonaService
        return PersonaService.create_persona()

    @app.route('/api/personas/<int:persona_id>', methods=['PUT'])
    @token_required
    def update_persona(persona_id):
        from src.api.Service.PersonaService import PersonaService
        return PersonaService.update_persona(persona_id)

    @app.route('/api/personas/<int:persona_id>', methods=['DELETE'])
    @admin_required
    def delete_persona(persona_id):
        from src.api.Service.PersonaService import PersonaService
        return PersonaService.delete_persona(persona_id)

    @app.route('/api/personas/disponibles', methods=['GET'])
    @admin_required
    def get_personas_disponibles():
        """Endpoint específico para obtener personas sin usuario (útil para crear usuarios)"""
        from src.api.Service.PersonaService import PersonaService
        return PersonaService.get_personas_disponibles()

    # ============================================
    # RUTAS DE ESPECIALIDADES (Protegidas)
    # ============================================
    @app.route('/api/especialidades', methods=['GET'])
    @token_required
    def get_especialidades():
        from src.api.Service.EspecialidadService import EspecialidadService
        return EspecialidadService.get_especialidades()

    @app.route('/api/especialidades/<area>', methods=['GET'])
    @token_required
    def get_especialidades_by_area(area):
        from src.api.Service.EspecialidadService import EspecialidadService
        return EspecialidadService.get_especialidades_by_area(area)

    @app.route('/api/especialidades/id/<int:especialidad_id>', methods=['GET'])
    @token_required
    def get_especialidad(especialidad_id):
        from src.api.Service.EspecialidadService import EspecialidadService
        return EspecialidadService.get_especialidad(especialidad_id)

    @app.route('/api/especialidades', methods=['POST'])
    @admin_required
    def create_especialidad():
        from src.api.Service.EspecialidadService import EspecialidadService
        return EspecialidadService.create_especialidad()

    @app.route('/api/especialidades/id/<int:especialidad_id>', methods=['PUT'])
    @admin_required
    def update_especialidad(especialidad_id):
        from src.api.Service.EspecialidadService import EspecialidadService
        return EspecialidadService.update_especialidad(especialidad_id)

    @app.route('/api/especialidades/id/<int:especialidad_id>', methods=['DELETE'])
    @admin_required
    def delete_especialidad(especialidad_id):
        from src.api.Service.EspecialidadService import EspecialidadService
        return EspecialidadService.delete_especialidad(especialidad_id)

    @app.route('/api/especialidades/activas', methods=['GET'])
    @token_required
    def get_especialidades_activas():
        from src.api.Service.EspecialidadService import EspecialidadService
        return EspecialidadService.get_especialidades_activas()

    @app.route('/api/especialidades/estadisticas', methods=['GET'])
    @token_required
    def get_especialidades_estadisticas():
        from src.api.Service.EspecialidadService import EspecialidadService
        return EspecialidadService.get_estadisticas()

    # ============================================
    # RUTAS DE PERSONAL (Protegidas)
    # ============================================
    @app.route('/api/personal', methods=['GET'])
    @token_required
    def get_personal():
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.get_personal()

    @app.route('/api/personal/<int:personal_id>', methods=['GET'])
    @token_required
    def get_personal_by_id(personal_id):
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.get_personal_by_id(personal_id)

    @app.route('/api/personal', methods=['POST'])
    @admin_required
    def create_personal():
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.create_personal()

    @app.route('/api/personal/<int:personal_id>', methods=['PUT'])
    @admin_required
    def update_personal(personal_id):
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.update_personal(personal_id)

    @app.route('/api/personal/<int:personal_id>', methods=['DELETE'])
    @admin_required
    def delete_personal(personal_id):
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.delete_personal(personal_id)

    @app.route('/api/personal/area/<area>', methods=['GET'])
    @token_required
    def get_personal_by_area(area):
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.get_personal_by_area(area)

    @app.route('/api/personal/estadisticas', methods=['GET'])
    @token_required
    def get_personal_estadisticas():
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.get_estadisticas()

    # Gestión de especialidades del personal
    @app.route('/api/personal/<int:personal_id>/especialidades', methods=['GET'])
    @token_required
    def get_personal_especialidades(personal_id):
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.get_personal_especialidades(personal_id)

    @app.route('/api/personal/<int:personal_id>/especialidades', methods=['POST'])
    @admin_required
    def assign_especialidad_to_personal(personal_id):
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.assign_especialidad(personal_id)

    @app.route('/api/personal/<int:personal_id>/especialidades/<int:especialidad_id>', methods=['DELETE'])
    @admin_required
    def remove_especialidad_from_personal(personal_id, especialidad_id):
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.remove_especialidad(personal_id, especialidad_id)

    # ============================================
    # RUTAS DE USUARIOS (Protegidas)
    # ============================================
    @app.route('/api/usuarios', methods=['GET'])
    @admin_required
    def get_usuarios():
        from src.api.Service.UsuarioService import UsuarioService
        return UsuarioService.get_usuarios()

    @app.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
    @token_required
    def get_usuario(usuario_id):
        from src.api.Service.UsuarioService import UsuarioService
        return UsuarioService.get_usuario(usuario_id)

    @app.route('/api/usuarios', methods=['POST'])
    @admin_required
    def create_usuario():
        from src.api.Service.UsuarioService import UsuarioService
        return UsuarioService.create_usuario()

    @app.route('/api/usuarios/<int:usuario_id>', methods=['PUT'])
    @admin_required
    def update_usuario(usuario_id):
        from src.api.Service.UsuarioService import UsuarioService
        return UsuarioService.update_usuario(usuario_id)

    @app.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
    @admin_required
    def delete_usuario(usuario_id):
        from src.api.Service.UsuarioService import UsuarioService
        return UsuarioService.delete_usuario(usuario_id)



    # ============================================
    # RUTAS DE TUTORES (Protegidas)
    # ============================================
    @app.route('/api/tutores', methods=['GET'])
    @token_required
    def get_tutores():
        from src.api.Service.TutorService import TutorService
        return TutorService.get_tutores()

    @app.route('/api/tutores/<int:tutor_id>', methods=['GET'])
    @token_required
    def get_tutor_by_id(tutor_id):
        from src.api.Service.TutorService import TutorService
        return TutorService.get_tutor_by_id(tutor_id)

    @app.route('/api/tutores', methods=['POST'])
    @token_required
    def create_tutor():
        from src.api.Service.TutorService import TutorService
        return TutorService.create_tutor()

    @app.route('/api/tutores/<int:tutor_id>', methods=['PUT'])
    @token_required
    def update_tutor(tutor_id):
        from src.api.Service.TutorService import TutorService
        return TutorService.update_tutor(tutor_id)

    @app.route('/api/tutores/<int:tutor_id>', methods=['DELETE'])
    @admin_required
    def delete_tutor(tutor_id):
        from src.api.Service.TutorService import TutorService
        return TutorService.delete_tutor(tutor_id)

    @app.route('/api/tutores/activos', methods=['GET'])
    @token_required
    def get_tutores_activos():
        from src.api.Service.TutorService import TutorService
        return TutorService.get_tutores_activos()

    @app.route('/api/tutores/estadisticas', methods=['GET'])
    @token_required
    def get_tutores_estadisticas():
        from src.api.Service.TutorService import TutorService
        return TutorService.get_estadisticas()

    @app.route('/api/tutores/personas-disponibles', methods=['GET'])
    @token_required
    def get_personas_disponibles_tutor():
        from src.api.Service.TutorService import TutorService
        return TutorService.get_personas_disponibles()



    # ============================================
    # RUTAS DE PACIENTES (Protegidas)
    # ============================================
    @app.route('/api/pacientes', methods=['GET'])
    @token_required
    def get_pacientes():
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.get_pacientes()

    @app.route('/api/pacientes/<int:paciente_id>', methods=['GET'])
    @token_required
    def get_paciente_by_id(paciente_id):
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.get_paciente_by_id(paciente_id)

    @app.route('/api/pacientes', methods=['POST'])
    @token_required
    def create_paciente():
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.create_paciente()

    @app.route('/api/pacientes/<int:paciente_id>', methods=['PUT'])
    @token_required
    def update_paciente(paciente_id):
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.update_paciente(paciente_id)

    @app.route('/api/pacientes/<int:paciente_id>/estado', methods=['PUT'])
    @token_required
    def change_estado_paciente(paciente_id):
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.change_estado_paciente(paciente_id)

    @app.route('/api/pacientes/tutor/<int:tutor_id>', methods=['GET'])
    @token_required
    def get_pacientes_by_tutor(tutor_id):
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.get_pacientes_by_tutor(tutor_id)

    @app.route('/api/pacientes/estadisticas', methods=['GET'])
    @token_required
    def get_pacientes_estadisticas():
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.get_estadisticas()

    @app.route('/api/pacientes/personas-disponibles', methods=['GET'])
    @token_required
    def get_personas_disponibles_paciente():
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.get_personas_disponibles()