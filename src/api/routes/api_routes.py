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

    @app.route('/api/test-db-status', methods=['GET'])
    def test_database_with_status():
        """Endpoint para demostrar getRecordsWithStatus vs getRecords"""
        try:
            from src.utils.database.connection_db import DataBaseHandle
            
            # Probar con consulta que retorna datos
            query_valid = "SELECT COUNT(*) as total_usuarios FROM usuario"
            
            # Método antiguo
            old_result = DataBaseHandle.getRecords(query_valid, size=1)
            
            # Método nuevo
            new_result = DataBaseHandle.getRecordsWithStatus(query_valid, size=1)
            
            # Probar con consulta que no retorna datos
            query_empty = "SELECT * FROM usuario WHERE id = -999"
            old_empty = DataBaseHandle.getRecords(query_empty, size=1)
            new_empty = DataBaseHandle.getRecordsWithStatus(query_empty, size=1)
            
            # Probar con consulta inválida
            query_invalid = "SELECT * FROM tabla_inexistente"
            old_error = DataBaseHandle.getRecords(query_invalid, size=1)  
            new_error = DataBaseHandle.getRecordsWithStatus(query_invalid, size=1)
            
            HandleLogs.write_log("test_database_with_status - Comparación de métodos completada")
            return response_success({
                "valid_query": {
                    "old_method": old_result,
                    "new_method": new_result
                },
                "empty_result": {
                    "old_method": old_empty,
                    "new_method": new_empty
                },
                "error_query": {
                    "old_method": old_error,
                    "new_method": new_error
                }
            }, "Comparacion de metodos getRecords completada")
            
        except Exception as e:
            HandleLogs.write_error(f"test_database_with_status - Error: {str(e)}")
            return response_error("Error en test de metodos de base de datos", 500)

    # ============================================
    # RUTAS DE AUTENTICACIÓN
    # ============================================
    @app.route('/api/login', methods=['POST'])
    def login():
        from src.api.Service.LoginService import LoginService
        return LoginService.login()

    @app.route('/api/centros-disponibles', methods=['GET'])
    def get_centros_disponibles():
        """Obtener centros disponibles para selector de login"""
        from src.api.Service.LoginService import LoginService
        return LoginService.get_centros_disponibles()

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
    # RUTAS DE ESPECIALIDADES MÚLTIPLES - COMPATIBILIDAD Y ESTADÍSTICAS
    # ============================================
    @app.route('/api/compatibilidad-especialidades/<int:personal_id>/<int:paciente_id>', methods=['GET'])
    @token_required
    def verificar_compatibilidad_especialidades(personal_id, paciente_id):
        """Verificar compatibilidad de especialidades entre personal y paciente"""
        from src.api.Service.EspecialidadService import EspecialidadService
        return EspecialidadService.verificar_compatibilidad(personal_id, paciente_id)

    @app.route('/api/especialidades-multiples/estadisticas', methods=['GET'])
    @token_required
    def get_estadisticas_especialidades_multiples():
        """Obtener estadísticas de especialidades múltiples"""
        from src.api.Service.EspecialidadService import EspecialidadService
        return EspecialidadService.get_estadisticas_multiples()

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

    @app.route('/api/personal/<int:personal_id>/especialidades/<int:especialidad_id>', methods=['PUT'])
    @token_required
    @admin_required
    def update_especialidad_personal(personal_id, especialidad_id):
        """Actualizar especialidad de personal"""
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.update_especialidad(personal_id, especialidad_id)

    @app.route('/api/personal/<int:personal_id>/especialidades/<int:especialidad_id>', methods=['DELETE'])
    @admin_required
    def remove_especialidad_from_personal(personal_id, especialidad_id):
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.remove_especialidad(personal_id, especialidad_id)

    # Nuevas rutas para especialidades múltiples - Fase 2
    @app.route('/api/personal/<int:personal_id>/especialidades-multiples', methods=['GET'])
    @token_required
    def get_personal_especialidades_multiples(personal_id):
        """Obtener todas las especialidades asignadas a un personal"""
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.get_especialidades_personal(personal_id)

    @app.route('/api/personal/<int:personal_id>/especialidades-multiples', methods=['POST'])
    @admin_required
    def agregar_especialidad_personal(personal_id):
        """Agregar especialidad a un personal (especialidades múltiples)"""
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.agregar_especialidad_personal(personal_id)

    @app.route('/api/personal/<int:personal_id>/especialidades-multiples/<int:especialidad_id>', methods=['DELETE'])
    @admin_required
    def remover_especialidad_personal(personal_id, especialidad_id):
        """Remover especialidad de un personal (especialidades múltiples)"""
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.remover_especialidad_personal(personal_id, especialidad_id)

    @app.route('/api/personal/por-especialidad/<int:especialidad_id>', methods=['GET'])
    @token_required
    def get_personal_por_especialidad(especialidad_id):
        """Obtener personal que maneja una especialidad específica"""
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.get_personal_por_especialidad(especialidad_id)

    @app.route('/api/personal/especialidades-disponibles', methods=['GET'])
    @token_required
    def get_especialidades_disponibles_personal():
        """Obtener especialidades disponibles para asignar al personal"""
        from src.api.Service.PersonalService import PersonalService
        return PersonalService.get_especialidades_disponibles()

    # ============================================
    # RUTAS DE DOCUMENTOS DE PERSONAL - Fase 2
    # ============================================
    @app.route('/api/personal/<int:personal_id>/documentos', methods=['GET'])
    @token_required
    def get_documentos_personal(personal_id):
        """Obtener documentos de un miembro del personal"""
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        return DocumentoPersonalService.get_documentos_personal(personal_id)

    @app.route('/api/personal/<int:personal_id>/documentos', methods=['POST'])
    @token_required
    def subir_documento_personal(personal_id):
        """Subir documento para un miembro del personal"""
        from flask import request
        # Agregar personal_id al form data
        if request.form:
            request.form = request.form.copy()
            request.form['personal_id'] = str(personal_id)
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        return DocumentoPersonalService.subir_documento()

    @app.route('/api/documentos-personal/<int:documento_id>', methods=['GET'])
    @token_required
    def get_documento_personal(documento_id):
        """Obtener información específica de un documento del personal"""
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        return DocumentoPersonalService.get_documento_by_id(documento_id)

    @app.route('/api/documentos-personal/<int:documento_id>', methods=['PUT'])
    @token_required
    def actualizar_documento_personal(documento_id):
        """Actualizar información de un documento del personal"""
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        return DocumentoPersonalService.actualizar_documento_por_id(documento_id)

    @app.route('/api/documentos-personal/<int:documento_id>', methods=['DELETE'])
    @token_required
    def eliminar_documento_personal(documento_id):
        """Eliminar un documento del personal"""
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        return DocumentoPersonalService.eliminar_documento(documento_id)

    @app.route('/api/documentos-personal/<int:documento_id>/descargar', methods=['GET'])
    @token_required
    def descargar_documento_personal(documento_id):
        """Descargar archivo de documento del personal"""
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        from flask import send_file
        from src.utils.general.logs import HandleLogs
        
        HandleLogs.write_log(f"descargar_documento_personal - Iniciando descarga documento {documento_id}")
        result = DocumentoPersonalService.descargar_documento(documento_id)
        
        HandleLogs.write_log(f"descargar_documento_personal - Service result: {result['success']}")
        if result['success']:
            try:
                HandleLogs.write_log("descargar_documento_personal - Comenzando procesamiento de descarga")
                import os
                
                file_path = result['data']['ruta_archivo']
                file_name = result['data']['nombre_archivo']
                mime_type = result['data']['tipo_mime']
                
                HandleLogs.write_log(f"descargar_documento_personal - Datos extraídos: {file_path}, {file_name}, {mime_type}")
                
                # Verificar que el archivo existe
                if not os.path.exists(file_path):
                    HandleLogs.write_error(f"descargar_documento_personal - Archivo no encontrado: {file_path}")
                    return response_error("Archivo no encontrado en el sistema", 404)
                
                HandleLogs.write_log(f"descargar_documento_personal - Archivo verificado exitosamente")
                
                # Limpiar nombre de archivo
                import urllib.parse
                import re
                
                clean_filename = file_name
                # Reemplazar caracteres acentuados
                replacements = {
                    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
                    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
                    'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
                }
                
                for original, replacement in replacements.items():
                    clean_filename = clean_filename.replace(original, replacement)
                
                # Remover caracteres especiales
                clean_filename = re.sub(r'[^\w\s\-\.\(\)]', '', clean_filename)
                clean_filename = re.sub(r'\s+', '_', clean_filename.strip())
                
                HandleLogs.write_log(f"descargar_documento_personal - Descargando: {clean_filename}")
                
                try:
                    HandleLogs.write_log("descargar_documento_personal - Intentando send_file Flask 2.x+")
                    # Flask 2.x+
                    response = send_file(
                        file_path,
                        as_attachment=True,
                        download_name=clean_filename,
                        mimetype=mime_type
                    )
                    HandleLogs.write_log("descargar_documento_personal - send_file Flask 2.x+ exitoso")
                except TypeError as te:
                    HandleLogs.write_log(f"descargar_documento_personal - TypeError en Flask 2.x+, probando 1.x: {str(te)}")
                    # Flask 1.x
                    response = send_file(
                        file_path,
                        as_attachment=True,
                        attachment_filename=clean_filename,
                        mimetype=mime_type
                    )
                    HandleLogs.write_log("descargar_documento_personal - send_file Flask 1.x exitoso")
                
                HandleLogs.write_log("descargar_documento_personal - Configurando headers")
                response.headers['Content-Disposition'] = f'attachment; filename="{clean_filename}"'
                HandleLogs.write_log("descargar_documento_personal - Retornando response")
                return response
                        
            except Exception as e:
                HandleLogs.write_error(f"descargar_documento_personal - Error: {str(e)}")
                return response_error(f"Error enviando archivo: {str(e)}", 500)
        else:
            return response_error(result['message'], 404 if 'no encontrado' in result['message'].lower() else 400)

    @app.route('/api/documentos-personal/tipo/<tipo_documento>', methods=['GET'])
    @token_required
    def get_documentos_por_tipo(tipo_documento):
        """Obtener documentos por tipo"""
        from flask import request
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        
        centro_id = request.args.get('centro_id')
        if centro_id:
            try:
                centro_id = int(centro_id)
            except ValueError:
                return response_error("ID de centro inválido", 400)
        
        return DocumentoPersonalService.get_documentos_por_tipo(tipo_documento, centro_id)

    @app.route('/api/documentos-personal/tipos', methods=['GET'])
    @token_required
    def get_tipos_documentos_personal():
        """Obtener tipos de documentos soportados para personal"""
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        return DocumentoPersonalService.obtener_tipos_documentos()

    @app.route('/api/documentos-personal/vencimientos', methods=['GET'])
    @token_required
    def get_documentos_vencimientos():
        """Obtener documentos próximos a vencer"""
        from flask import request
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        
        dias_alerta = request.args.get('dias_alerta', 90, type=int)
        return DocumentoPersonalService.obtener_documentos_vencimientos(dias_alerta)

    @app.route('/api/documentos-personal/pendientes-validacion', methods=['GET'])
    @token_required
    def get_documentos_pendientes_validacion():
        """Obtener documentos pendientes de validación"""
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        return DocumentoPersonalService.obtener_documentos_pendientes_validacion()

    @app.route('/api/documentos-personal/estadisticas', methods=['GET'])
    @token_required
    def get_estadisticas_documentos_personal():
        """Obtener estadísticas de documentos de personal"""
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        return DocumentoPersonalService.obtener_estadisticas_documentos()

    @app.route('/api/documentos-personal/buscar', methods=['GET'])
    @token_required
    def buscar_documentos_personal():
        """Buscar documentos con filtros avanzados"""
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        return DocumentoPersonalService.buscar_documentos()

    @app.route('/api/documentos-personal/<int:documento_id>/validar', methods=['PUT'])
    @token_required
    def validar_documento_personal(documento_id):
        """Validar documento de personal"""
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        return DocumentoPersonalService.validar_documento(documento_id)

    @app.route('/api/documentos-personal/por-vencer', methods=['GET'])
    @token_required
    def get_documentos_por_vencer():
        """Obtener documentos que están por vencer"""
        from flask import request
        from src.api.Service.DocumentoPersonalService import DocumentoPersonalService
        
        dias_adelanto = request.args.get('dias', 30, type=int)
        centro_id = request.args.get('centro_id', type=int)
        
        return DocumentoPersonalService.get_documentos_por_vencer(dias_adelanto, centro_id)

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

    @app.route('/api/usuarios/<int:usuario_id>/cambiar-contrasenia', methods=['PUT'])
    @token_required
    def change_user_password(usuario_id):
        try:
            from flask import request
            from src.api.Service.UsuarioService import UsuarioService
            return UsuarioService.change_password(usuario_id, request.json)
        except Exception as e:
            from src.utils.general.response import response_error
            return response_error(f"Error en cambio de contraseña: {str(e)}", 500)



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

    @app.route('/api/pacientes/<int:paciente_id>', methods=['DELETE'])
    @token_required
    @admin_required
    def delete_paciente(paciente_id):
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.delete_paciente(paciente_id)

    # ============================================
    # RUTAS DE ESPECIALIDADES PARA PACIENTES
    # ============================================
    @app.route('/api/pacientes/<int:paciente_id>/especialidades', methods=['POST'])
    @token_required
    def assign_especialidad_paciente(paciente_id):
        """Asignar especialidad a un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.agregar_especialidad_paciente()

    @app.route('/api/pacientes/<int:paciente_id>/especialidades', methods=['GET'])
    @token_required
    def get_paciente_especialidades(paciente_id):
        """Obtener especialidades de un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.get_especialidades_paciente(paciente_id)

    @app.route('/api/pacientes/<int:paciente_id>/especialidades/<int:especialidad_id>', methods=['DELETE'])
    @token_required
    def remove_especialidad_paciente(paciente_id, especialidad_id):
        """Remover especialidad de un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.remover_especialidad_paciente()

    @app.route('/api/pacientes/<int:paciente_id>/especialidad-principal', methods=['PUT'])
    @token_required
    def cambiar_especialidad_principal_paciente(paciente_id):
        """Cambiar especialidad principal de un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.cambiar_especialidad_principal(paciente_id)

    # ============================================
    # RUTAS DE ESPECIALIDADES MÚLTIPLES PARA PACIENTES - Fase 2
    # ============================================
    @app.route('/api/pacientes/<int:paciente_id>/especialidades-multiples', methods=['GET'])
    @token_required
    def get_paciente_especialidades_multiples(paciente_id):
        """Obtener especialidades asignadas a un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.get_especialidades_paciente(paciente_id)

    @app.route('/api/pacientes/<int:paciente_id>/especialidades-multiples', methods=['POST'])
    @token_required
    def agregar_especialidad_paciente(paciente_id):
        """Agregar especialidad a un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.agregar_especialidad_paciente(paciente_id)

    @app.route('/api/pacientes/<int:paciente_id>/especialidades-multiples/<int:especialidad_id>', methods=['DELETE'])
    @token_required
    def remover_especialidad_paciente(paciente_id, especialidad_id):
        """Remover especialidad de un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.remover_especialidad_paciente(paciente_id, especialidad_id)

    # ============================================
    # RUTAS DE CONTROL DE PAUSAS PARA PACIENTES - Fase 2
    # ============================================
    @app.route('/api/pacientes/<int:paciente_id>/pausar', methods=['PUT'])
    @token_required
    def pausar_paciente_general(paciente_id):
        """Pausar paciente de forma general (todas las especialidades)"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.pausar_paciente_general(paciente_id)

    @app.route('/api/pacientes/<int:paciente_id>/reactivar', methods=['PUT'])
    @token_required
    def reactivar_paciente_general(paciente_id):
        """Reactivar paciente de forma general"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.reactivar_paciente_general(paciente_id)

    @app.route('/api/pacientes/<int:paciente_id>/especialidades-multiples/<int:especialidad_id>/pausar', methods=['PUT'])
    @token_required
    def pausar_especialidad_paciente(paciente_id, especialidad_id):
        """Pausar tratamiento de especialidad específica para un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.pausar_especialidad_paciente(paciente_id, especialidad_id)

    @app.route('/api/pacientes/<int:paciente_id>/especialidades-multiples/<int:especialidad_id>/reactivar', methods=['PUT'])
    @token_required
    def reactivar_especialidad_paciente(paciente_id, especialidad_id):
        """Reactivar tratamiento de especialidad específica para un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.reactivar_especialidad_paciente(paciente_id, especialidad_id)

    @app.route('/api/pacientes/pausados', methods=['GET'])
    @token_required
    def get_pacientes_pausados():
        """Obtener lista de pacientes pausados (general y por especialidad)"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.get_pacientes_pausados()

    @app.route('/api/pacientes/por-especialidad/<int:especialidad_id>', methods=['GET'])
    @token_required
    def get_pacientes_por_especialidad(especialidad_id):
        """Obtener pacientes que reciben tratamiento en una especialidad específica"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.get_pacientes_por_especialidad(especialidad_id)

    # ============================================
    # RUTAS DE DOCUMENTOS DE PACIENTES (Protegidas)
    # ============================================
    @app.route('/api/pacientes/<int:paciente_id>/documentos', methods=['POST'])
    @token_required
    def upload_documento_paciente(paciente_id):
        """Subir documento PDF para un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.upload_documento(paciente_id)

    @app.route('/api/pacientes/<int:paciente_id>/documentos', methods=['GET'])
    @token_required
    def get_documentos_paciente(paciente_id):
        """Obtener lista de documentos de un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.get_documentos(paciente_id)

    @app.route('/api/pacientes/<int:paciente_id>/documentos/<int:documento_id>', methods=['GET'])
    @token_required
    def download_documento_paciente(paciente_id, documento_id):
        """Descargar un documento específico de un paciente"""
        from src.api.Service.PacienteService import PacienteService
        from flask import send_file
        from src.utils.general.logs import HandleLogs
        
        result = PacienteService.download_documento(paciente_id, documento_id)
        
        if result['success']:
            try:
                import os
                
                file_path = result['data']['ruta_archivo']
                file_name = result['data']['nombre_original']
                mime_type = result['data']['tipo_mime']
                
                # Check if file exists
                if not os.path.exists(file_path):
                    HandleLogs.write_error(f"download_documento_paciente - File not found: {file_path}")
                    return response_error("Archivo no encontrado en el sistema", 404)
                
                # Clean and prepare filename
                import urllib.parse
                import re
                
                # Limpiar nombre de archivo de caracteres problemáticos
                # Reemplazar caracteres acentuados comunes
                replacements = {
                    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
                    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
                    'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
                }
                
                clean_filename = file_name
                for original, replacement in replacements.items():
                    clean_filename = clean_filename.replace(original, replacement)
                
                # Remover caracteres especiales problemáticos y espacios múltiples
                clean_filename = re.sub(r'[^\w\s\-\.\(\)]', '', clean_filename)
                clean_filename = re.sub(r'\s+', '_', clean_filename.strip())
                
                # Asegurar que tenga extensión .pdf
                if not clean_filename.lower().endswith('.pdf'):
                    clean_filename += '.pdf'
                
                # Log para debugging
                HandleLogs.write_log(f"download_documento_paciente - Original filename: {file_name}")
                HandleLogs.write_log(f"download_documento_paciente - Clean filename: {clean_filename}")
                
                # Try different Flask send_file approaches for compatibility
                try:
                    # Flask 2.x+ approach
                    response = send_file(
                        file_path,
                        as_attachment=True,
                        download_name=clean_filename,
                        mimetype=mime_type
                    )
                except TypeError:
                    # Flask 1.x approach
                    response = send_file(
                        file_path,
                        as_attachment=True,
                        attachment_filename=clean_filename,
                        mimetype=mime_type
                    )
                
                # Asegurar que el Content-Disposition header esté correctamente formateado
                response.headers['Content-Disposition'] = f'attachment; filename="{clean_filename}"'
                
                return response
                        
            except Exception as e:
                HandleLogs.write_error(f"download_documento_paciente - Error: {str(e)}")
                import traceback
                HandleLogs.write_error(f"download_documento_paciente - Traceback: {traceback.format_exc()}")
                return response_error(f"Error enviando archivo: {str(e)}", 500)
        else:
            HandleLogs.write_error(f"download_documento_paciente - Service error: {result.get('message', 'Unknown error')}")
            error_message = result.get('message', 'Error descargando documento')
            if 'no encontrado' in error_message.lower():
                return response_error(error_message, 404)
            else:
                return response_error(error_message, 400)

    @app.route('/api/pacientes/<int:paciente_id>/documentos/<int:documento_id>', methods=['PUT'])
    @token_required
    def update_documento_paciente(paciente_id, documento_id):
        """Actualizar información de un documento (no el archivo físico)"""
        from src.api.Service.PacienteService import PacienteService
        from flask import request
        from src.utils.general.logs import HandleLogs
        from src.api.Components.DocumentoPacienteComponent import DocumentoPacienteComponent
        from src.utils.general.data_utils import DataUtils
        
        try:
            data = request.get_json()
            current_user_id = getattr(request, 'current_user', {}).get('id')
            
            # Ensure usuario_modificacion is included for the update
            if 'usuario_modificacion' not in data and current_user_id:
                data['usuario_modificacion'] = current_user_id
            
            prepared_data = DataUtils.prepare_update_data(data, current_user_id)
            
            result = DocumentoPacienteComponent.update_documento(documento_id, paciente_id, prepared_data)
            
            if result['success']:
                return response_success(result['data'], result['message'])
            else:
                return response_error(result['message'], 400)
                
        except Exception as e:
            HandleLogs.write_error(f"update_documento_paciente - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @app.route('/api/pacientes/<int:paciente_id>/documentos/<int:documento_id>', methods=['DELETE'])
    @token_required
    def delete_documento_paciente(paciente_id, documento_id):
        """Eliminar un documento de un paciente"""
        from src.api.Service.PacienteService import PacienteService
        return PacienteService.delete_documento(paciente_id, documento_id)

    @app.route('/api/documentos/estadisticas', methods=['GET'])
    @token_required
    def get_estadisticas_documentos():
        """Obtener estadísticas de documentos por tipo"""
        from src.api.Components.DocumentoPacienteComponent import DocumentoPacienteComponent
        
        result = DocumentoPacienteComponent.get_estadisticas_documentos()
        
        if result['success']:
            return response_success(result['data'], result['message'])
        else:
            return response_error(result['message'], 500)


    # Agregar estas rutas al archivo src/api/routes/api_routes.py

    def register_sesiones_routes(app):
        """Registrar rutas para el módulo de Sesiones de Terapia"""

        # ============================================
        # RUTAS DE SESIONES DE TERAPIA (Protegidas)
        # ============================================

        @app.route('/api/sesiones-terapia', methods=['GET'])
        @token_required
        def get_sesiones_terapia():
            """Obtener todas las sesiones de terapia"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_sesiones()

        @app.route('/api/sesiones-terapia/<int:sesion_id>', methods=['GET'])
        @token_required
        def get_sesion_terapia(sesion_id):
            """Obtener una sesión de terapia específica"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_sesion(sesion_id)

        @app.route('/api/sesiones-terapia', methods=['POST'])
        @token_required  # Tanto admin como terapeuta pueden crear
        def create_sesion_terapia():
            """Crear nueva sesión de terapia"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.create_sesion()

        @app.route('/api/sesiones-terapia/<int:sesion_id>', methods=['PUT'])
        @token_required  # Tanto admin como terapeuta pueden editar
        def update_sesion_terapia(sesion_id):
            """Actualizar sesión de terapia"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.update_sesion(sesion_id)

        @app.route('/api/sesiones-terapia/<int:sesion_id>', methods=['DELETE'])
        @admin_required  # Solo admin puede cancelar
        def delete_sesion_terapia(sesion_id):
            """Cancelar sesión de terapia"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.delete_sesion(sesion_id)

        # ============================================
        # RUTAS DE GESTIÓN DE PACIENTES EN SESIONES
        # ============================================

        @app.route('/api/sesiones-terapia/<int:sesion_id>/pacientes', methods=['GET'])
        @token_required
        def get_pacientes_sesion(sesion_id):
            """Obtener pacientes asignados a una sesión"""
            from src.api.Components.SesionTerapiaComponent import SesionTerapiaComponent
            try:
                pacientes = SesionTerapiaComponent.get_pacientes_sesion(sesion_id)
                from src.utils.general.response import response_success
                return response_success(pacientes or [], "Pacientes de la sesión obtenidos")
            except Exception as e:
                from src.utils.general.response import response_error
                return response_error(f"Error al obtener pacientes: {str(e)}", 500)

        @app.route('/api/sesiones-terapia/<int:sesion_id>/pacientes', methods=['POST'])
        @token_required
        def add_paciente_sesion(sesion_id):
            """Agregar paciente a una sesión"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.add_paciente_to_sesion(sesion_id)

        @app.route('/api/sesiones-terapia/<int:sesion_id>/pacientes/<int:paciente_id>', methods=['DELETE'])
        @token_required
        def remove_paciente_sesion(sesion_id, paciente_id):
            """Remover paciente de una sesión"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.remove_paciente_from_sesion(sesion_id, paciente_id)

        # ============================================
        # RUTAS DE GESTIÓN DE CRONOGRAMA
        # ============================================

        @app.route('/api/sesiones-terapia/<int:sesion_id>/cronograma', methods=['GET'])
        @token_required
        def get_cronograma_sesion(sesion_id):
            """Obtener cronograma de una sesión"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_cronograma_sesion(sesion_id)

        @app.route('/api/sesiones-terapia/<int:sesion_id>/cronograma/generar', methods=['POST'])
        @token_required
        def generar_cronograma_sesion(sesion_id):
            """Regenerar cronograma de una sesión"""
            from src.api.Components.SesionTerapiaComponent import SesionTerapiaComponent
            try:
                SesionTerapiaComponent.generar_cronograma(sesion_id)
                from src.utils.general.response import response_success
                return response_success({'sesion_id': sesion_id}, "Cronograma generado exitosamente")
            except Exception as e:
                from src.utils.general.response import response_error
                return response_error(f"Error al generar cronograma: {str(e)}", 500)



        # ============================================
        # RUTAS DE ASISTENCIA
        # ============================================


        # ============================================
        # RUTAS DE CONSULTAS Y REPORTES
        # ============================================

        @app.route('/api/sesiones-terapia/terapeuta/<int:terapeuta_id>', methods=['GET'])
        @token_required
        def get_sesiones_by_terapeuta(terapeuta_id):
            """Obtener sesiones de un terapeuta específico"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_sesiones_by_terapeuta(terapeuta_id)

        @app.route('/api/sesiones-terapia/hoy', methods=['GET'])
        @token_required
        def get_sesiones_hoy():
            """Obtener sesiones programadas para hoy"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_sesiones_hoy()

        @app.route('/api/sesiones-terapia/estadisticas', methods=['GET'])
        @token_required
        def get_estadisticas_sesiones():
            """Obtener estadísticas de sesiones"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_estadisticas()

        # ============================================
        # RUTAS DE DATOS AUXILIARES
        # ============================================

        @app.route('/api/sesiones-terapia/pacientes-disponibles', methods=['GET'])
        @token_required
        def get_pacientes_disponibles_sesiones():
            """Obtener pacientes disponibles para asignar a sesiones"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_pacientes_disponibles()

        @app.route('/api/sesiones-terapia/terapeutas-disponibles', methods=['GET'])
        @token_required
        def get_terapeutas_disponibles_sesiones():
            """Obtener terapeutas disponibles para asignar a sesiones"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_terapeutas_disponibles()

        # ============================================
        # RUTAS DE ASISTENCIA DE SESIONES TERAPÉUTICAS
        # ============================================

        @app.route('/api/sesiones-terapia/cronograma/<int:cronograma_id>/pacientes/<int:paciente_id>/asistencia', methods=['POST'])
        @token_required
        def registrar_asistencia_sesion(cronograma_id, paciente_id):
            """Registrar asistencia de un paciente a una sesión específica del cronograma"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.registrar_asistencia(cronograma_id, paciente_id)

        @app.route('/api/sesiones-terapia/cronograma/<int:cronograma_id>/pacientes/<int:paciente_id>/asistencia', methods=['PUT'])
        @token_required
        def actualizar_asistencia_sesion(cronograma_id, paciente_id):
            """Actualizar asistencia existente de un paciente"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.actualizar_asistencia(cronograma_id, paciente_id)

        @app.route('/api/sesiones-terapia/cronograma/<int:cronograma_id>/asistencia', methods=['GET'])
        @token_required
        def get_asistencia_cronograma(cronograma_id):
            """Obtener asistencia de todos los pacientes para una sesión específica del cronograma"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_asistencia_cronograma(cronograma_id)

        @app.route('/api/sesiones-terapia/<int:sesion_id>/asistencias', methods=['GET'])
        @token_required
        def get_asistencias_por_sesion(sesion_id):
            """Obtener todas las asistencias de una sesión de terapia"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_asistencias_por_sesion(sesion_id)

        @app.route('/api/sesiones-terapia/asistencias/paciente/<int:paciente_id>', methods=['GET'])
        @token_required
        def get_asistencias_por_paciente(paciente_id):
            """Obtener historial de asistencias de un paciente específico"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_asistencias_por_paciente(paciente_id)

        @app.route('/api/sesiones-terapia/<int:sesion_id>/estadisticas-asistencia', methods=['GET'])
        @token_required
        def get_estadisticas_asistencia(sesion_id):
            """Obtener estadísticas de asistencia de una sesión"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_estadisticas_asistencia(sesion_id)

        @app.route('/api/sesiones-terapia/cronograma/<int:cronograma_id>/control-asistencia', methods=['GET'])
        @token_required
        def get_control_asistencia(cronograma_id):
            """Obtener control de asistencia completo para una sesión del cronograma"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.get_control_asistencia(cronograma_id)

        # ============================================
        # RUTAS PARA GESTIÓN DE CRONOGRAMA
        # ============================================

        @app.route('/api/sesiones-terapia/cronograma/<int:cronograma_id>/realizar', methods=['PUT'])
        @token_required
        def marcar_sesion_realizada(cronograma_id):
            """Marcar sesión como realizada"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.marcar_sesion_realizada(cronograma_id)

        @app.route('/api/sesiones-terapia/cronograma/<int:cronograma_id>/reprogramar', methods=['PUT'])
        @token_required
        def reprogramar_sesion_cronograma(cronograma_id):
            """Reprogramar una sesión específica del cronograma"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.reprogramar_sesion_cronograma(cronograma_id)

        @app.route('/api/sesiones-terapia/cronograma/<int:cronograma_id>/cancelar', methods=['PUT'])
        @token_required
        def cancelar_sesion_cronograma(cronograma_id):
            """Cancelar una sesión específica del cronograma"""
            from src.api.Service.SesionTerapiaService import SesionTerapiaService
            return SesionTerapiaService.cancelar_sesion_cronograma(cronograma_id)


    # ============================================
    # REGISTRAR RUTAS DE SESIONES DE TERAPIA
    # ============================================
    register_sesiones_routes(app)

    def register_sesiones_pedagogicas_routes(app):
        """Registrar rutas para el módulo de Sesiones Pedagógicas"""

        # ============================================
        # RUTAS DE SESIONES PEDAGÓGICAS (Protegidas)
        # ============================================

        @app.route('/api/sesiones-pedagogicas', methods=['GET'])
        @token_required
        def get_sesiones_pedagogicas():
            """Obtener todas las sesiones pedagógicas"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.get_sesiones()
        
        # Temporary debug endpoint without authentication
        @app.route('/api/sesiones-pedagogicas-debug', methods=['GET'])
        def get_sesiones_pedagogicas_debug():
            """Debug endpoint - obtener todas las sesiones pedagógicas sin autenticación"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.get_sesiones()

        # Debug endpoints for cronograma without authentication
        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>/cronograma-debug', methods=['GET'])
        def get_cronograma_sesion_pedagogica_debug(sesion_id):
            """Debug endpoint - obtener cronograma de una sesión pedagógica sin autenticación"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.get_cronograma_sesion(sesion_id)

        @app.route('/api/debug/cronograma-component/<int:sesion_id>', methods=['GET'])
        def debug_cronograma_component(sesion_id):
            """Debug endpoint - llamar directamente al componente"""
            try:
                from src.api.Components.SesionPedagogicaComponent import SesionPedagogicaComponent
                from src.utils.general.response import response_success
                
                # Llamar directamente al componente
                result = SesionPedagogicaComponent.get_cronograma_sesion(sesion_id)
                
                return response_success({
                    'raw_component_result': result,
                    'result_type': type(result).__name__,
                    'result_length': len(result) if result else 0,
                    'is_none': result is None,
                    'is_empty_list': result == []
                }, f"Debug componente para sesión {sesion_id}")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"debug_cronograma_component - Error: {str(e)}")
                return response_error(f"Error en debug componente: {str(e)}", 500)

        @app.route('/api/cronograma-clases/<int:cronograma_id>/asistencias-debug', methods=['GET'])
        def get_asistencias_clase_debug(cronograma_id):
            """Debug endpoint - obtener asistencias de una clase sin autenticación"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success
                
                query = """
                    SELECT 
                        ac.id,
                        ac.paciente_id,
                        CONCAT(p.nombre, ' ', p.apellido) as estudiante_nombre,
                        ac.asistio,
                        ac.llegada_tardanza_minutos,
                        ac.observaciones_asistencia,
                        ac.participacion_clase,
                        ac.tareas_entregadas,
                        ac.notas_comportamiento,
                        ac.calificacion_evaluacion,
                        ac.observaciones_evaluacion,
                        ac.fecha_registro
                    FROM asistencia_clases ac
                    LEFT JOIN paciente pac ON ac.paciente_id = pac.id
                    LEFT JOIN persona p ON pac.id_persona = p.id
                    WHERE ac.cronograma_clases_id = %s
                    ORDER BY p.nombre, p.apellido
                """
                
                result = DataBaseHandle.getRecords(query, (cronograma_id,))
                
                if result is None:
                    result = []
                
                return response_success(result, f"Asistencias obtenidas para la clase {cronograma_id}")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"get_asistencias_clase_debug - Error: {str(e)}")
                return response_error(f"Error al obtener asistencias: {str(e)}", 500)

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>/cronograma/generar-debug', methods=['POST'])
        def generar_cronograma_sesion_pedagogica_debug(sesion_id):
            """Debug endpoint - generar cronograma de una sesión pedagógica sin autenticación"""
            from src.api.Components.SesionPedagogicaComponent import SesionPedagogicaComponent
            try:
                SesionPedagogicaComponent.generar_cronograma(sesion_id)
                from src.utils.general.response import response_success
                return response_success({'sesion_id': sesion_id}, "Cronograma de clases generado exitosamente")
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"generar_cronograma_sesion_pedagogica_debug - Error: {str(e)}")
                return response_error(f"Error al generar cronograma: {str(e)}", 500)

        @app.route('/api/debug/cronograma-clases/<int:sesion_id>', methods=['GET'])
        def debug_cronograma_clases(sesion_id):
            """Debug endpoint - verificar cronograma directamente en base de datos"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success
                
                # Query directo a la tabla
                query = """
                    SELECT cc.*, sp.titulo as sesion_titulo
                    FROM cronograma_clases cc
                    LEFT JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
                    WHERE cc.id_sesion = %s
                    ORDER BY cc.numero_clase_semanal
                """
                
                result = DataBaseHandle.getRecords(query, (sesion_id,))
                
                if result is None:
                    result = []
                
                # También check basic de la sesión
                sesion_query = "SELECT id, titulo, estado FROM sesion_pedagogica WHERE id = %s"
                sesion = DataBaseHandle.getRecords(sesion_query, (sesion_id,), size=1)
                
                return response_success({
                    'sesion': sesion,
                    'cronograma_count': len(result) if result else 0,
                    'cronograma': result
                }, f"Debug query para sesión {sesion_id}")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"debug_cronograma_clases - Error: {str(e)}")
                return response_error(f"Error en debug: {str(e)}", 500)

        @app.route('/api/debug/all-sesiones-pedagogicas', methods=['GET'])
        def debug_all_sesiones_pedagogicas():
            """Debug endpoint - verificar todas las sesiones directamente en base de datos"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success
                
                # Query directo a la tabla
                query = "SELECT id, titulo, codigo_sesion, estado, fecha_creacion FROM sesion_pedagogica ORDER BY id"
                
                result = DataBaseHandle.getRecords(query)
                
                if result is None:
                    result = []
                
                return response_success({
                    'total_sesiones': len(result) if result else 0,
                    'sesiones': result
                }, f"Debug query - todas las sesiones")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"debug_all_sesiones_pedagogicas - Error: {str(e)}")
                return response_error(f"Error en debug: {str(e)}", 500)

        @app.route('/api/debug/create-sample-sessions', methods=['POST'])
        def create_sample_sessions_debug():
            """Debug endpoint - crear sesiones pedagógicas de ejemplo sin autenticación"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success
                from datetime import datetime
                
                # Crear 2 sesiones pedagógicas de ejemplo
                sessions_data = [
                    {
                        'nombre_clase': 'Lectoescritura Inicial',
                        'id_educador': 1,
                        'id_especialidad': 1,
                        'fecha_inicio': '2025-01-10',
                        'fecha_fin': '2025-06-10',
                        'dias_semana': '{lunes,miercoles,viernes}',
                        'hora_inicio': '14:00:00',
                        'duracion_minutos': 60,
                        'nivel_academico': 'preescolar',
                        'capacidad_maxima': 6,
                        'estado': 'en_curso',
                        'usuario_creacion': 1
                    },
                    {
                        'nombre_clase': 'Matemáticas Básicas',
                        'id_educador': 1,
                        'id_especialidad': 1,
                        'fecha_inicio': '2025-01-15',
                        'fecha_fin': '2025-06-15',
                        'dias_semana': '{martes,jueves}',
                        'hora_inicio': '15:00:00',
                        'duracion_minutos': 60,
                        'nivel_academico': 'primaria',
                        'capacidad_maxima': 4,
                        'estado': 'en_curso',
                        'usuario_creacion': 1
                    }
                ]
                
                created_sessions = []
                for session in sessions_data:
                    query = """
                        INSERT INTO sesion_pedagogica 
                        (nombre_clase, id_educador, id_especialidad, fecha_inicio, fecha_fin, 
                         dias_semana, hora_inicio, duracion_minutos, nivel_academico, 
                         capacidad_maxima, estado, usuario_creacion, fecha_creacion)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id, codigo_sesion
                    """
                    
                    params = (
                        session['nombre_clase'], session['id_educador'], session['id_especialidad'],
                        session['fecha_inicio'], session['fecha_fin'], session['dias_semana'],
                        session['hora_inicio'], session['duracion_minutos'], session['nivel_academico'],
                        session['capacidad_maxima'], session['estado'], session['usuario_creacion'],
                        datetime.now()
                    )
                    
                    result = DataBaseHandle.getRecords(query, params, size=1)
                    if result:
                        created_sessions.append(result)
                
                return response_success({
                    'created_sessions': created_sessions,
                    'total_created': len(created_sessions)
                }, "Sesiones pedagógicas de ejemplo creadas exitosamente")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"create_sample_sessions_debug - Error: {str(e)}")
                return response_error(f"Error creando sesiones: {str(e)}", 500)

        @app.route('/api/cronograma-clases/<int:clase_id>/realizar-debug', methods=['PUT'])
        def marcar_clase_realizada_debug(clase_id):
            """Debug endpoint - marcar clase como realizada sin autenticación"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success, response_error
                from datetime import datetime
                
                # Marcar la clase como completada (usando el estado correcto de la tabla)
                fecha_realizacion = datetime.now()
                update_query = """
                    UPDATE cronograma_clases 
                    SET estado = 'completada', 
                        fecha_confirmacion = %s,
                        fecha_modificacion = NOW(),
                        usuario_modificacion = 'debug_user'
                    WHERE id = %s
                """
                
                # Ejecutar la actualización (sin verificar resultado, como otros endpoints)
                DataBaseHandle.ExecuteNonQuery(update_query, (fecha_realizacion, clase_id))
                
                return response_success({
                    'clase_id': clase_id,
                    'estado': 'completada',
                    'fecha_confirmacion': fecha_realizacion.isoformat()
                }, "Clase marcada como completada exitosamente")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"marcar_clase_realizada_debug - Error: {str(e)}")
                return response_error(f"Error marcando clase como realizada: {str(e)}", 500)

        @app.route('/api/debug/cronograma-table/<int:clase_id>', methods=['GET'])
        def debug_cronograma_table_direct(clase_id):
            """Debug endpoint - consultar directamente la tabla cronograma_clases"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success, response_error
                
                query = "SELECT id, estado, fecha_confirmacion, fecha_modificacion FROM cronograma_clases WHERE id = %s"
                result = DataBaseHandle.getRecords(query, (clase_id,))
                
                if not result:
                    return response_error(f"Clase {clase_id} no encontrada", 404)
                
                return response_success({
                    'clase_data': result[0],
                    'query_used': query
                }, f"Debug directo para clase {clase_id}")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"debug_cronograma_table_direct - Error: {str(e)}")
                return response_error(f"Error en debug directo: {str(e)}", 500)

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>/estudiantes-debug', methods=['GET'])
        def get_estudiantes_sesion_pedagogica_debug(sesion_id):
            """Debug endpoint - obtener estudiantes de una sesión pedagógica sin autenticación"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success
                
                query = """
                    SELECT 
                        se.id,
                        se.id_paciente,
                        se.fecha_inscripcion as fecha_asignacion,
                        se.estado as estado_asignacion,
                        CONCAT(p.nombre, ' ', p.apellido) as estudiante_nombre,
                        p.cedula as estudiante_cedula,
                        p.fecha_nacimiento as estudiante_fecha_nacimiento
                    FROM sesion_estudiante se
                    JOIN paciente pac ON se.id_paciente = pac.id
                    JOIN persona p ON pac.id_persona = p.id
                    WHERE se.id_sesion = %s AND se.estado = 'activo'
                    ORDER BY p.nombre, p.apellido
                """
                
                result = DataBaseHandle.getRecords(query, (sesion_id,))
                
                return response_success(result if result else [], "Estudiantes de la sesión obtenidos exitosamente")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"get_estudiantes_sesion_pedagogica_debug - Error: {str(e)}")
                return response_error(f"Error obteniendo estudiantes: {str(e)}", 500)

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>/estudiantes-debug', methods=['POST'])
        def add_estudiante_sesion_pedagogica_debug(sesion_id):
            """Debug endpoint - agregar estudiante a sesión pedagógica sin autenticación"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success, response_error
                from flask import request
                import json
                from datetime import date
                
                data = request.get_json() if request.is_json else {}
                
                # Validar datos requeridos
                if not data.get('paciente_id'):
                    return response_error("Campo paciente_id es requerido", 400)
                
                # Preparar datos para insertar
                insert_data = {
                    'id_sesion': sesion_id,
                    'id_paciente': int(data['paciente_id']),
                    'fecha_inscripcion': data.get('fecha_inscripcion', str(date.today())),
                    'nivel_actual': data.get('nivel_actual', 'basico'),
                    'estado': 'activo',
                    'observaciones': data.get('observaciones', ''),
                    'usuario_creacion': 1  # Usuario debug
                }
                
                # Insertar en la base de datos
                insert_query = """
                    INSERT INTO sesion_estudiante 
                    (id_sesion, id_paciente, fecha_inscripcion, nivel_actual, estado, observaciones, usuario_creacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                DataBaseHandle.ExecuteNonQuery(insert_query, (
                    insert_data['id_sesion'],
                    insert_data['id_paciente'],
                    insert_data['fecha_inscripcion'],
                    insert_data['nivel_actual'],
                    insert_data['estado'],
                    insert_data['observaciones'],
                    insert_data['usuario_creacion']
                ))
                
                return response_success(insert_data, "Estudiante agregado exitosamente a la sesión")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"add_estudiante_sesion_pedagogica_debug - Error: {str(e)}")
                return response_error(f"Error agregando estudiante: {str(e)}", 500)

        @app.route('/api/pacientes-disponibles-debug', methods=['GET'])
        def get_pacientes_disponibles_debug():
            """Debug endpoint - obtener pacientes disponibles para agregar a sesiones sin autenticación"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success
                
                query = """
                    SELECT 
                        p.id,
                        p.id_persona,
                        CONCAT(per.nombre, ' ', per.apellido) as nombre_completo,
                        per.cedula,
                        per.fecha_nacimiento,
                        p.estado
                    FROM paciente p
                    JOIN persona per ON p.id_persona = per.id
                    WHERE p.estado = 'activo'
                    ORDER BY per.nombre, per.apellido
                """
                
                result = DataBaseHandle.getRecords(query)
                
                return response_success(result if result else [], "Pacientes disponibles obtenidos exitosamente")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"get_pacientes_disponibles_debug - Error: {str(e)}")
                return response_error(f"Error obteniendo pacientes: {str(e)}", 500)

        @app.route('/api/debug/create-patients-from-existing-personas', methods=['POST'])
        def create_patients_from_existing_personas_debug():
            """Debug endpoint - crear pacientes desde personas existentes con IDs específicos"""
            try:
                from src.api.Components.PacienteComponent import PacienteComponent
                from src.utils.general.response import response_success, response_error
                from datetime import date
                
                # IDs de personas que ya existen (obtenidas del intento anterior)
                personas_ids = [15, 16, 17]
                nombres = ["Emma López Vásquez", "Diego Castro Morales", "Valeria Herrera Jiménez"]
                
                created_patients = []
                
                for i, persona_id in enumerate(personas_ids):
                    try:
                        # Crear paciente usando el componente con el ID de persona existente
                        paciente_data = {
                            'id_persona': persona_id,
                            'id_centro': 1,  # Usar centro 1 por defecto
                            'fecha_ingreso': date.today().isoformat(),
                            'motivo_consulta': f"Sesión pedagógica para estudiante {nombres[i]}",
                            'observaciones': 'Paciente creado para pruebas pedagógicas',
                            'estado': 'activo',
                            'usuario_creacion': 1
                        }
                        
                        paciente_result = PacienteComponent.create_paciente(paciente_data)
                        
                        created_patients.append({
                            'persona_id': persona_id,
                            'nombre': nombres[i],
                            'paciente_result': paciente_result
                        })
                    
                    except Exception as person_error:
                        print(f"Error creating patient for persona {persona_id}: {person_error}")
                        continue
                
                return response_success({
                    'created_patients': created_patients,
                    'total_created': len(created_patients)
                }, f"Attempted to create {len(created_patients)} patients from existing personas")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"create_patients_from_existing_personas_debug - Error: {str(e)}")
                return response_error(f"Error creando pacientes: {str(e)}", 500)

        @app.route('/api/debug/load-initial-data', methods=['POST'])
        def load_initial_data_debug():
            """Debug endpoint - cargar datos iniciales completos desde el archivo SQL"""
            try:
                import os
                from src.utils.general.response import response_success, response_error
                from src.utils.general.logs import HandleLogs
                
                # Ejecutar el archivo de datos iniciales
                sql_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'utils', 'database', '02_datos_completos.sql')
                
                if os.path.exists(sql_file_path):
                    try:
                        # Leer el archivo SQL
                        with open(sql_file_path, 'r', encoding='utf-8') as file:
                            sql_content = file.read()
                        
                        # Ejecutar usando psycopg2 directamente
                        from src.utils.database.connection_db import DataBaseHandle
                        import psycopg2
                        
                        # Obtener conexión directa para ejecutar múltiples statements
                        connection = DataBaseHandle.get_connection()
                        if connection:
                            cursor = connection.cursor()
                            cursor.execute(sql_content)
                            connection.commit()
                            cursor.close()
                            connection.close()
                            
                            HandleLogs.write_log("Datos iniciales cargados exitosamente")
                            return response_success({
                                'loaded': True,
                                'file_path': sql_file_path
                            }, "Datos iniciales cargados exitosamente desde archivo SQL")
                        else:
                            return response_error("No se pudo obtener conexión a la base de datos", 500)
                            
                    except Exception as sql_error:
                        HandleLogs.write_error(f"Error ejecutando SQL: {str(sql_error)}")
                        return response_error(f"Error ejecutando SQL: {str(sql_error)}", 500)
                else:
                    return response_error(f"Archivo SQL no encontrado: {sql_file_path}", 404)
                
            except Exception as e:
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"load_initial_data_debug - Error: {str(e)}")
                return response_error(f"Error cargando datos iniciales: {str(e)}", 500)

        @app.route('/api/cronograma-clases/<int:clase_id>/marcar-realizada-working', methods=['PUT'])
        def marcar_clase_realizada_working_debug(clase_id):
            """Debug endpoint - marcar clase como realizada con método que funciona"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success, response_error
                from datetime import datetime
                import psycopg2
                
                # Usar conexión directa para asegurar que se persistan los cambios
                connection = DataBaseHandle.get_connection()
                if not connection:
                    return response_error("No se pudo conectar a la base de datos", 500)
                
                try:
                    cursor = connection.cursor()
                    
                    # Marcar la clase como completada usando conexión directa
                    fecha_realizacion = datetime.now()
                    update_query = """
                        UPDATE cronograma_clases 
                        SET estado = 'completada', 
                            fecha_confirmacion = %s,
                            fecha_modificacion = NOW(),
                            usuario_modificacion = 1
                        WHERE id = %s
                    """
                    
                    cursor.execute(update_query, (fecha_realizacion, clase_id))
                    
                    # Verificar que se actualizó al menos una fila
                    if cursor.rowcount > 0:
                        connection.commit()
                        cursor.close()
                        connection.close()
                        
                        return response_success({
                            'clase_id': clase_id,
                            'estado': 'completada',
                            'fecha_confirmacion': fecha_realizacion.isoformat(),
                            'rows_affected': cursor.rowcount
                        }, "Clase marcada como completada exitosamente")
                    else:
                        connection.rollback()
                        cursor.close()
                        connection.close()
                        return response_error(f"No se encontró la clase con ID {clase_id}", 404)
                        
                except Exception as db_error:
                    connection.rollback()
                    cursor.close()
                    connection.close()
                    return response_error(f"Error en base de datos: {str(db_error)}", 500)
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"marcar_clase_realizada_working_debug - Error: {str(e)}")
                return response_error(f"Error marcando clase como completada: {str(e)}", 500)

        @app.route('/api/debug/create-sample-patients', methods=['POST'])
        def create_sample_patients_debug():
            """Debug endpoint - crear pacientes de ejemplo usando componentes existentes"""
            try:
                from src.api.Components.PacienteComponent import PacienteComponent
                from src.api.Components.PersonaComponent import PersonaComponent
                from src.utils.general.response import response_success, response_error
                from datetime import date
                
                # Datos de personas de ejemplo para pacientes (usando cédulas únicas)
                personas_data = [
                    {
                        'nombre': 'Emma',
                        'apellido': 'López Vásquez',
                        'cedula': '1750123456',
                        'fecha_nacimiento': '2015-03-15',
                        'telefono': '0987654321',
                        'email': 'emma.lopez@email.com'
                    },
                    {
                        'nombre': 'Diego',
                        'apellido': 'Castro Morales',
                        'cedula': '1750123457',
                        'fecha_nacimiento': '2014-07-22',
                        'telefono': '0987654322',
                        'email': 'diego.castro@email.com'
                    },
                    {
                        'nombre': 'Valeria',
                        'apellido': 'Herrera Jiménez',
                        'cedula': '1750123458',
                        'fecha_nacimiento': '2016-01-10',
                        'telefono': '0987654323',
                        'email': 'valeria.herrera@email.com'
                    }
                ]
                
                created_patients = []
                
                for persona_data in personas_data:
                    try:
                        # Crear persona usando el componente
                        persona_id = PersonaComponent.create_persona(persona_data)
                        
                        if persona_id:
                            # Crear paciente usando el componente
                            paciente_data = {
                                'id_persona': persona_id,
                                'id_centro': 1,  # Usar centro 1 por defecto
                                'fecha_ingreso': date.today().isoformat(),
                                'motivo_consulta': f"Sesión pedagógica para estudiante {persona_data['nombre']}",
                                'observaciones': 'Paciente creado para pruebas pedagógicas',
                                'estado': 'activo',
                                'usuario_creacion': 1
                            }
                            
                            paciente_id = PacienteComponent.create_paciente(paciente_data)
                            
                            if paciente_id:
                                created_patients.append({
                                    'paciente_id': paciente_id,
                                    'persona_id': persona_id,
                                    'nombre': f"{persona_data['nombre']} {persona_data['apellido']}",
                                    'cedula': persona_data['cedula']
                                })
                    
                    except Exception as person_error:
                        print(f"Error creating patient for {persona_data['nombre']}: {person_error}")
                        continue
                
                return response_success({
                    'created_patients': created_patients,
                    'total_created': len(created_patients)
                }, f"{len(created_patients)} pacientes de ejemplo creados exitosamente")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"create_sample_patients_debug - Error: {str(e)}")
                return response_error(f"Error creando pacientes: {str(e)}", 500)

        @app.route('/api/debug/database-status', methods=['GET'])
        def debug_database_status():
            """Debug endpoint - verificar estado completo de la base de datos"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success
                
                # Contar registros en tablas principales
                queries = {
                    'sesiones_pedagogicas': "SELECT COUNT(*) as count FROM sesion_pedagogica",
                    'cronograma_clases': "SELECT COUNT(*) as count FROM cronograma_clases", 
                    'asistencia_clases': "SELECT COUNT(*) as count FROM asistencia_clases",
                    'personal': "SELECT COUNT(*) as count FROM personal",
                    'especialidades': "SELECT COUNT(*) as count FROM especialidad"
                }
                
                results = {}
                for table, query in queries.items():
                    result = DataBaseHandle.getRecords(query, size=1)
                    results[table] = result['count'] if result else 0
                
                # También obtener las sesiones con detalles
                sesiones_query = """
                    SELECT id, codigo_sesion, nombre_clase, estado, fecha_creacion
                    FROM sesion_pedagogica 
                    ORDER BY id
                """
                sesiones = DataBaseHandle.getRecords(sesiones_query)
                
                # Y cronogramas
                cronograma_query = """
                    SELECT cc.id, cc.id_sesion, cc.numero_clase_semanal, cc.fecha_programada, cc.estado,
                           sp.codigo_sesion, sp.nombre_clase
                    FROM cronograma_clases cc
                    LEFT JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
                    ORDER BY cc.id_sesion, cc.numero_clase_semanal
                    LIMIT 10
                """
                cronogramas = DataBaseHandle.getRecords(cronograma_query)
                
                return response_success({
                    'table_counts': results,
                    'sesiones_sample': sesiones or [],
                    'cronogramas_sample': cronogramas or []
                }, "Estado de la base de datos")
                
            except Exception as e:
                from src.utils.general.response import response_error
                from src.utils.general.logs import HandleLogs
                HandleLogs.write_error(f"debug_database_status - Error: {str(e)}")
                return response_error(f"Error verificando estado: {str(e)}", 500)

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>', methods=['GET'])
        @token_required
        def get_sesion_pedagogica(sesion_id):
            """Obtener una sesión pedagógica específica"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.get_sesion(sesion_id)

        @app.route('/api/sesiones-pedagogicas', methods=['POST'])
        @token_required  # Tanto admin como pedagogo pueden crear
        def create_sesion_pedagogica():
            """Crear nueva sesión pedagógica"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.create_sesion()

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>', methods=['PUT'])
        @token_required  # Tanto admin como pedagogo pueden editar
        def update_sesion_pedagogica(sesion_id):
            """Actualizar sesión pedagógica"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.update_sesion(sesion_id)

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>', methods=['DELETE'])
        @admin_required  # Solo admin puede cancelar
        def delete_sesion_pedagogica(sesion_id):
            """Cancelar sesión pedagógica"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.delete_sesion(sesion_id)

        # ============================================
        # RUTAS DE GESTIÓN DE ESTUDIANTES EN SESIONES
        # ============================================

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>/estudiantes', methods=['GET'])
        @token_required
        def get_estudiantes_sesion_pedagogica(sesion_id):
            """Obtener estudiantes asignados a una sesión pedagógica"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.get_estudiantes_sesion(sesion_id)

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>/estudiantes', methods=['POST'])
        @token_required
        def add_estudiante_sesion_pedagogica(sesion_id):
            """Agregar estudiante a una sesión pedagógica"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.add_estudiante_to_sesion(sesion_id)

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>/estudiantes/<int:paciente_id>', methods=['DELETE'])
        @token_required
        def remove_estudiante_sesion_pedagogica(sesion_id, paciente_id):
            """Remover estudiante de una sesión pedagógica"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.remove_estudiante_from_sesion(sesion_id, paciente_id)

        # ============================================
        # RUTAS DE GESTIÓN DE CRONOGRAMA DE CLASES
        # ============================================

        @app.route('/api/sesiones-pedagogicas/cronograma', methods=['GET'])
        @token_required
        def get_cronograma_sesiones_pedagogicas():
            """Obtener cronograma general de sesiones pedagógicas"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            from flask import request
            
            # Obtener filtros de query parameters
            filtros = {
                'especialidad': request.args.get('especialidad'),
                'pedagogo': request.args.get('pedagogo'), 
                'semana': request.args.get('semana', 'actual')
            }
            
            return SesionPedagogicaService.get_cronograma_sesiones(filtros)

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>/cronograma', methods=['GET'])
        @token_required
        def get_cronograma_sesion_pedagogica(sesion_id):
            """Obtener cronograma de una sesión pedagógica"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.get_cronograma_sesion(sesion_id)

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>/cronograma/generar', methods=['POST'])
        @token_required
        def generar_cronograma_sesion_pedagogica(sesion_id):
            """Regenerar cronograma de una sesión pedagógica"""
            from src.api.Components.SesionPedagogicaComponent import SesionPedagogicaComponent
            try:
                SesionPedagogicaComponent.generar_cronograma(sesion_id)
                from src.utils.general.response import response_success
                return response_success({'sesion_id': sesion_id}, "Cronograma de clases generado exitosamente")
            except Exception as e:
                from src.utils.general.response import response_error
                return response_error(f"Error al generar cronograma: {str(e)}", 500)

        @app.route('/api/cronograma-clases/<int:cronograma_id>/realizar', methods=['PUT'])
        @token_required
        def marcar_clase_realizada(cronograma_id):
            """Marcar clase como realizada"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success, response_error
                from datetime import datetime
                
                # Marcar clase como realizada
                query = """
                    UPDATE cronograma_clases 
                    SET estado = 'realizada', fecha_realizacion = %s
                    WHERE id = %s
                """
                params = (datetime.now().date(), cronograma_id)
                DataBaseHandle.ExecuteNonQuery(query, params)
                
                return response_success({'cronograma_id': cronograma_id}, "Clase marcada como realizada exitosamente")
            except Exception as e:
                return response_error(f"Error al marcar clase como realizada: {str(e)}", 500)

        @app.route('/api/cronograma-clases/<int:cronograma_id>/reprogramar', methods=['PUT'])
        @token_required
        def reprogramar_clase(cronograma_id):
            """Reprogramar una clase específica"""
            try:
                from flask import request
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success, response_error
                from datetime import datetime
                
                data = request.get_json()
                if not data or 'nueva_fecha' not in data:
                    return response_error("Se requiere nueva_fecha", 400)
                
                try:
                    nueva_fecha = datetime.strptime(data['nueva_fecha'], '%Y-%m-%d').date()
                except ValueError:
                    return response_error("Formato de fecha inválido (YYYY-MM-DD)", 400)
                
                # Reprogramar clase
                query = """
                    UPDATE cronograma_clases 
                    SET estado = 'reprogramada', fecha_programada = %s
                    WHERE id = %s
                """
                params = (nueva_fecha, cronograma_id)
                DataBaseHandle.ExecuteNonQuery(query, params)
                
                return response_success({'cronograma_id': cronograma_id}, "Clase reprogramada exitosamente")
            except Exception as e:
                return response_error(f"Error al reprogramar clase: {str(e)}", 500)

        @app.route('/api/cronograma-clases/<int:cronograma_id>', methods=['PUT'])
        @token_required
        def update_clase_cronograma(cronograma_id):
            """Actualizar información de una clase del cronograma"""
            try:
                from flask import request
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success, response_error
                
                data = request.get_json()
                if not data:
                    return response_error("No se proporcionaron datos para actualizar", 400)
                
                # Construir query dinámicamente basado en los campos proporcionados
                allowed_fields = ['tema_clase', 'objetivos_clase', 'material_requerido', 'tareas_asignadas', 'evaluacion_programada', 'tipo_evaluacion']
                update_fields = []
                params = []
                
                for field in allowed_fields:
                    if field in data:
                        update_fields.append(f"{field} = %s")
                        params.append(data[field])
                
                if not update_fields:
                    return response_error("No se proporcionaron campos válidos para actualizar", 400)
                
                # Agregar usuario_modificacion y fecha_modificacion
                update_fields.append("usuario_modificacion = %s")
                update_fields.append("fecha_modificacion = CURRENT_TIMESTAMP")
                params.append(request.current_user['id'])
                
                # Agregar ID al final
                params.append(cronograma_id)
                
                query = f"""
                    UPDATE cronograma_clases 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """
                
                DataBaseHandle.ExecuteNonQuery(query, params)
                
                return response_success({'cronograma_id': cronograma_id}, "Clase actualizada exitosamente")
            except Exception as e:
                return response_error(f"Error al actualizar clase: {str(e)}", 500)

        # ============================================
        # RUTAS DE ASISTENCIA DE CLASES
        # ============================================

        @app.route('/api/cronograma-clases/<int:cronograma_id>/asistencias', methods=['GET'])
        @token_required
        def get_asistencias_clase(cronograma_id):
            """Obtener asistencias de una clase"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success
                
                query = """
                    SELECT 
                        ac.id,
                        ac.paciente_id,
                        CONCAT(p.nombre, ' ', p.apellido) as estudiante_nombre,
                        ac.asistio,
                        ac.llegada_tardanza_minutos,
                        ac.observaciones_asistencia,
                        ac.participacion_clase,
                        ac.tareas_entregadas,
                        ac.notas_comportamiento,
                        ac.calificacion_evaluacion,
                        ac.observaciones_evaluacion
                    FROM asistencia_clases ac
                    JOIN paciente pac ON ac.paciente_id = pac.id
                    JOIN persona p ON pac.persona_id = p.id
                    WHERE ac.cronograma_clase_id = %s
                    ORDER BY p.apellido, p.nombre
                """
                
                params = (cronograma_id,)
                result = DataBaseHandle.getRecords(query, params)
                
                return response_success(result or [], "Asistencias obtenidas")
            except Exception as e:
                from src.utils.general.response import response_error
                return response_error(f"Error al obtener asistencias: {str(e)}", 500)

        @app.route('/api/cronograma-clases/<int:cronograma_id>/asistencias/<int:paciente_id>', methods=['POST'])
        @token_required
        def registrar_asistencia_estudiante(cronograma_id, paciente_id):
            """Registrar asistencia de un estudiante a una clase"""
            try:
                from flask import request
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success, response_error
                
                data = request.get_json() or {}
                
                query = """
                    INSERT INTO asistencia_clases (
                        cronograma_clase_id, paciente_id, asistio, llegada_tardanza_minutos,
                        observaciones_asistencia, participacion_clase, tareas_entregadas,
                        notas_comportamiento, calificacion_evaluacion, observaciones_evaluacion,
                        usuario_creacion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (cronograma_clase_id, paciente_id)
                    DO UPDATE SET
                        asistio = EXCLUDED.asistio,
                        llegada_tardanza_minutos = EXCLUDED.llegada_tardanza_minutos,
                        observaciones_asistencia = EXCLUDED.observaciones_asistencia,
                        participacion_clase = EXCLUDED.participacion_clase,
                        tareas_entregadas = EXCLUDED.tareas_entregadas,
                        notas_comportamiento = EXCLUDED.notas_comportamiento,
                        calificacion_evaluacion = EXCLUDED.calificacion_evaluacion,
                        observaciones_evaluacion = EXCLUDED.observaciones_evaluacion
                """
                
                params = (
                    cronograma_id,
                    paciente_id,
                    data.get('asistio', False),
                    data.get('llegada_tardanza_minutos', 0),
                    data.get('observaciones_asistencia'),
                    data.get('participacion_clase'),
                    data.get('tareas_entregadas', False),
                    data.get('notas_comportamiento'),
                    data.get('calificacion_evaluacion'),
                    data.get('observaciones_evaluacion'),
                    request.current_user['id']
                )
                
                DataBaseHandle.ExecuteNonQuery(query, params)
                
                return response_success({
                    'cronograma_id': cronograma_id,
                    'paciente_id': paciente_id
                }, "Asistencia registrada exitosamente")
            except Exception as e:
                return response_error(f"Error al registrar asistencia: {str(e)}", 500)

        # ============================================
        # RUTAS DE CONSULTAS Y REPORTES
        # ============================================

        @app.route('/api/sesiones-pedagogicas/pedagogo/<int:pedagogo_id>', methods=['GET'])
        @token_required
        def get_sesiones_by_pedagogo(pedagogo_id):
            """Obtener sesiones de un pedagogo específico"""
            try:
                from src.api.Components.SesionPedagogicaComponent import SesionPedagogicaComponent
                from src.utils.general.response import response_success
                
                result = SesionPedagogicaComponent.get_sesiones_by_pedagogo(pedagogo_id)
                return response_success(result or [], "Sesiones del pedagogo obtenidas")
            except Exception as e:
                from src.utils.general.response import response_error
                return response_error(f"Error al obtener sesiones: {str(e)}", 500)

        @app.route('/api/sesiones-pedagogicas/hoy', methods=['GET'])
        @token_required
        def get_clases_hoy():
            """Obtener clases programadas para hoy"""
            try:
                from src.utils.database.connection_db import DataBaseHandle
                from src.utils.general.response import response_success
                from datetime import datetime, date, time
                
                query = """
                    SELECT 
                        cc.id,
                        cc.numero_clase,
                        cc.fecha_programada,
                        cc.hora_programada,
                        cc.tema_clase,
                        cc.estado,
                        sp.titulo as sesion_titulo,
                        sp.id as sesion_id,
                        CONCAT(p.nombre, ' ', p.apellido) as pedagogo_nombre
                    FROM cronograma_clases cc
                    JOIN sesion_pedagogica sp ON cc.sesion_pedagogica_id = sp.id
                    JOIN personal per ON sp.pedagogo_id = per.id
                    JOIN persona p ON per.persona_id = p.id
                    WHERE cc.fecha_programada = %s
                    ORDER BY cc.hora_programada
                """
                
                params = (datetime.now().date(),)
                result = DataBaseHandle.getRecords(query, params)
                
                # Convert datetime objects to strings for JSON serialization
                if result:
                    for row in result:
                        if 'fecha_programada' in row and isinstance(row['fecha_programada'], date):
                            row['fecha_programada'] = row['fecha_programada'].isoformat()
                        if 'hora_programada' in row and isinstance(row['hora_programada'], time):
                            row['hora_programada'] = str(row['hora_programada'])
                
                return response_success(result or [], "Clases de hoy obtenidas")
            except Exception as e:
                from src.utils.general.response import response_error
                return response_error(f"Error al obtener clases de hoy: {str(e)}", 500)

        @app.route('/api/sesiones-pedagogicas/estadisticas', methods=['GET'])
        @token_required
        def get_estadisticas_sesiones_pedagogicas():
            """Obtener estadísticas de sesiones pedagógicas"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.get_estadisticas()

        # ============================================
        # RUTAS DE DATOS AUXILIARES
        # ============================================

        @app.route('/api/sesiones-pedagogicas/estudiantes-disponibles', methods=['GET'])
        @token_required
        def get_estudiantes_disponibles_pedagogicas():
            """Obtener estudiantes disponibles para asignar a sesiones pedagógicas"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.get_estudiantes_disponibles()

        @app.route('/api/sesiones-pedagogicas/pedagogos-disponibles', methods=['GET'])
        @token_required
        def get_pedagogos_disponibles_pedagogicas():
            """Obtener pedagogos disponibles para asignar a sesiones"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.get_pedagogos_disponibles()

        # ============================================
        # ENDPOINTS DEL SISTEMA DE ASISTENCIAS
        # ============================================

        @app.route('/api/sesiones-pedagogicas/cronograma/<int:cronograma_id>/estudiantes/<int:estudiante_id>/asistencia', methods=['POST'])
        @token_required
        def registrar_asistencia_pedagogica(cronograma_id, estudiante_id):
            """Registrar asistencia de estudiante a una clase"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.registrar_asistencia(cronograma_id, estudiante_id)

        @app.route('/api/sesiones-pedagogicas/cronograma/<int:cronograma_id>/estudiantes/<int:estudiante_id>/asistencia', methods=['PUT'])
        @token_required
        def actualizar_asistencia_pedagogica(cronograma_id, estudiante_id):
            """Actualizar asistencia existente de estudiante"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.actualizar_asistencia(cronograma_id, estudiante_id)

        @app.route('/api/sesiones-pedagogicas/<int:sesion_id>/asistencias', methods=['GET'])
        @token_required
        def get_asistencias_pedagogicas(sesion_id):
            """Obtener todas las asistencias de una sesión pedagógica"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.get_asistencias_por_sesion(sesion_id)

        @app.route('/api/sesiones-pedagogicas/cronograma/<int:cronograma_id>/control-asistencia', methods=['GET'])
        @token_required
        def get_control_asistencia_pedagogica(cronograma_id):
            """Obtener control de asistencia completo para una clase"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.get_control_asistencia(cronograma_id)

        # ============================================
        # ENDPOINTS DE GESTIÓN DE CRONOGRAMA
        # ============================================

        @app.route('/api/sesiones-pedagogicas/cronograma/<int:cronograma_id>/realizar', methods=['PUT'])
        @token_required
        def marcar_clase_realizada_pedagogica(cronograma_id):
            """Marcar clase como realizada"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.marcar_clase_realizada(cronograma_id)

        @app.route('/api/sesiones-pedagogicas/cronograma/<int:cronograma_id>/reprogramar', methods=['PUT'])
        @token_required
        def reprogramar_clase_pedagogica(cronograma_id):
            """Reprogramar una clase"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.reprogramar_clase(cronograma_id)

        @app.route('/api/sesiones-pedagogicas/cronograma/<int:cronograma_id>/cancelar', methods=['PUT'])
        @token_required
        def cancelar_clase_pedagogica(cronograma_id):
            """Cancelar una clase"""
            from src.api.Service.SesionPedagogicaService import SesionPedagogicaService
            return SesionPedagogicaService.cancelar_clase(cronograma_id)

        # Endpoint temporal para debug de asistencias
        @app.route('/api/debug-asistencia/<int:cronograma_id>/<int:estudiante_id>', methods=['GET'])
        def debug_asistencia(cronograma_id, estudiante_id):
            """Debug endpoint para verificar asistencias"""
            try:
                from src.utils.database.DataBaseHandle import DataBaseHandle
                from src.utils.general.response_handler import response_success, response_error
                
                # Verificar si existe registro de asistencia
                asistencia_query = """
                    SELECT * FROM asistencia_clases 
                    WHERE id_cronograma = %s AND id_paciente = %s
                """
                asistencia = DataBaseHandle.getRecords(asistencia_query, (cronograma_id, estudiante_id))
                
                # Verificar si existe cronograma
                cronograma_query = "SELECT * FROM cronograma_clases WHERE id = %s"
                cronograma = DataBaseHandle.getRecords(cronograma_query, (cronograma_id,))
                
                # Verificar si existe estudiante
                estudiante_query = "SELECT * FROM paciente WHERE id = %s"
                estudiante = DataBaseHandle.getRecords(estudiante_query, (estudiante_id,))
                
                return response_success({
                    'asistencia_exists': bool(asistencia),
                    'asistencia_data': asistencia,
                    'cronograma_exists': bool(cronograma),
                    'estudiante_exists': bool(estudiante),
                    'cronograma_id': cronograma_id,
                    'estudiante_id': estudiante_id
                }, "Debug data retrieved")
                
            except Exception as e:
                from src.utils.general.response_handler import response_error
                return response_error(f"Debug error: {str(e)}", 500)

    # ============================================
    # REGISTRAR RUTAS DE SESIONES PEDAGÓGICAS
    # ============================================
    register_sesiones_pedagogicas_routes(app)

    # ============================================
    # RUTAS DEL SISTEMA DE CHAT
    # ============================================
    def register_chat_routes(app):
        """Registrar rutas del sistema de chat"""
        
        @app.route('/api/chat/conversaciones', methods=['GET'])
        @token_required
        def get_conversaciones():
            """Obtener lista de conversaciones del usuario"""
            try:
                from flask import request
                from src.api.Service.ChatService import ChatService
                from src.utils.general.response import response_success, response_error
                
                # Validar permisos
                permisos = ChatService.validar_permisos_chat(request.current_user)
                if not permisos['success']:
                    return response_error(permisos['message'], 403)
                
                resultado = ChatService.obtener_conversaciones(request.current_user)
                
                if resultado['success']:
                    return response_success(resultado['conversaciones'], "Conversaciones obtenidas exitosamente")
                else:
                    return response_error(resultado['message'], 500)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_conversaciones: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/chat/mensajes/<int:id_contacto>', methods=['GET'])
        @token_required
        def get_mensajes_conversacion(id_contacto):
            """Obtener mensajes de una conversación específica"""
            try:
                from flask import request
                from src.api.Service.ChatService import ChatService
                from src.utils.general.response import response_success, response_error
                
                # Validar permisos
                permisos = ChatService.validar_permisos_chat(request.current_user)
                if not permisos['success']:
                    return response_error(permisos['message'], 403)
                
                # Obtener límite de mensajes (opcional)
                limite = request.args.get('limite', 50, type=int)
                
                resultado = ChatService.obtener_mensajes_conversacion(id_contacto, request.current_user, limite)
                
                if resultado['success']:
                    return response_success(resultado['mensajes'], "Mensajes obtenidos exitosamente")
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_mensajes_conversacion: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/chat/enviar', methods=['POST'])
        @token_required
        def enviar_mensaje():
            """Enviar un nuevo mensaje"""
            try:
                from flask import request
                from src.api.Service.ChatService import ChatService
                from src.utils.general.response import response_success, response_error
                
                # Validar permisos
                permisos = ChatService.validar_permisos_chat(request.current_user)
                if not permisos['success']:
                    return response_error(permisos['message'], 403)
                
                data = request.get_json()
                if not data:
                    return response_error("Datos requeridos", 400)
                
                resultado = ChatService.enviar_mensaje(data, request.current_user)
                
                if resultado['success']:
                    return response_success({
                        'id_mensaje': resultado['id_mensaje'],
                        'fecha_envio': resultado['fecha_envio']
                    }, "Mensaje enviado exitosamente")
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en enviar_mensaje: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/chat/marcar-leido/<int:id_mensaje>', methods=['PUT'])
        @token_required
        def marcar_mensaje_leido(id_mensaje):
            """Marcar un mensaje como leído"""
            try:
                from flask import request
                from src.api.Service.ChatService import ChatService
                from src.utils.general.response import response_success, response_error
                
                # Validar permisos
                permisos = ChatService.validar_permisos_chat(request.current_user)
                if not permisos['success']:
                    return response_error(permisos['message'], 403)
                
                resultado = ChatService.marcar_mensaje_leido(id_mensaje, request.current_user)
                
                if resultado['success']:
                    return response_success({}, resultado['message'])
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en marcar_mensaje_leido: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/chat/usuarios-disponibles', methods=['GET'])
        @token_required
        def get_usuarios_disponibles_chat():
            """Obtener usuarios disponibles para iniciar conversación"""
            try:
                from flask import request
                from src.api.Service.ChatService import ChatService
                from src.utils.general.response import response_success, response_error
                
                # Validar permisos
                permisos = ChatService.validar_permisos_chat(request.current_user)
                if not permisos['success']:
                    return response_error(permisos['message'], 403)
                
                resultado = ChatService.obtener_usuarios_disponibles(request.current_user)
                
                if resultado['success']:
                    return response_success(resultado['usuarios'], "Usuarios disponibles obtenidos")
                else:
                    return response_error(resultado['message'], 500)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_usuarios_disponibles_chat: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/chat/estadisticas', methods=['GET'])
        @token_required
        def get_estadisticas_chat():
            """Obtener estadísticas de mensajes del usuario"""
            try:
                from flask import request
                from src.api.Service.ChatService import ChatService
                from src.utils.general.response import response_success, response_error
                
                # Validar permisos
                permisos = ChatService.validar_permisos_chat(request.current_user)
                if not permisos['success']:
                    return response_error(permisos['message'], 403)
                
                resultado = ChatService.obtener_estadisticas_mensajes(request.current_user)
                
                if resultado['success']:
                    return response_success(resultado['estadisticas'], "Estadísticas obtenidas")
                else:
                    return response_error(resultado['message'], 500)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_estadisticas_chat: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/chat/buscar', methods=['GET'])
        @token_required
        def buscar_mensajes_chat():
            """Buscar mensajes por contenido"""
            try:
                from flask import request
                from src.api.Service.ChatService import ChatService
                from src.utils.general.response import response_success, response_error
                
                # Validar permisos
                permisos = ChatService.validar_permisos_chat(request.current_user)
                if not permisos['success']:
                    return response_error(permisos['message'], 403)
                
                # Obtener parámetros de búsqueda
                texto_busqueda = request.args.get('q')
                id_contacto = request.args.get('contacto', type=int)
                
                if not texto_busqueda:
                    return response_error("Parámetro 'q' requerido para la búsqueda", 400)
                
                resultado = ChatService.buscar_mensajes(texto_busqueda, request.current_user, id_contacto)
                
                if resultado['success']:
                    return response_success(resultado['mensajes'], "Búsqueda realizada exitosamente")
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en buscar_mensajes_chat: {str(e)}")
                return response_error("Error interno del servidor", 500)

    # ============================================
    # REGISTRAR RUTAS DE CHAT
    # ============================================
    register_chat_routes(app)

    # ============================================
    # RUTAS DE FOTOS DE PERFIL
    # ============================================
    def register_foto_perfil_routes(app):
        """Registrar rutas de fotos de perfil"""
        
        @app.route('/api/perfil/foto', methods=['POST'])
        @token_required
        def subir_foto_perfil():
            """Subir foto de perfil del usuario autenticado"""
            try:
                from src.api.Service.FotoPerfilService import FotoPerfilService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                # Validar que se envió un archivo
                if 'foto' not in request.files:
                    return response_error("No se proporcionó archivo de foto", 400)
                
                archivo = request.files['foto']
                
                resultado = FotoPerfilService.subir_foto_perfil(archivo, request.current_user)
                
                if resultado['success']:
                    return response_success({
                        'ruta_foto': resultado['ruta_foto']
                    }, resultado['mensaje'])
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en subir_foto_perfil: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/perfil/foto', methods=['GET'])
        @token_required
        def obtener_mi_foto_perfil():
            """Obtener información de foto de perfil del usuario autenticado"""
            try:
                from src.api.Service.FotoPerfilService import FotoPerfilService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                resultado = FotoPerfilService.obtener_mi_foto_perfil(request.current_user)
                
                if resultado['success']:
                    return response_success(resultado['foto_perfil'], "Información de foto obtenida")
                else:
                    return response_error(resultado['message'], 404)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_mi_foto_perfil: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/perfil/foto', methods=['DELETE'])
        @token_required
        def eliminar_mi_foto_perfil():
            """Eliminar foto de perfil del usuario autenticado"""
            try:
                from src.api.Service.FotoPerfilService import FotoPerfilService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                resultado = FotoPerfilService.eliminar_foto_perfil(request.current_user)
                
                if resultado['success']:
                    return response_success({}, resultado['message'])
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en eliminar_mi_foto_perfil: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/usuarios/<int:usuario_id>/foto', methods=['GET'])
        @token_required
        def obtener_foto_perfil_usuario(usuario_id):
            """Obtener información de foto de perfil de un usuario específico"""
            try:
                from src.api.Service.FotoPerfilService import FotoPerfilService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                resultado = FotoPerfilService.obtener_foto_perfil(usuario_id, request.current_user)
                
                if resultado['success']:
                    return response_success(resultado['foto_perfil'], "Información de foto obtenida")
                else:
                    return response_error(resultado['message'], 404)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_foto_perfil_usuario: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/usuarios/<int:usuario_id>/foto', methods=['POST'])
        @token_required
        def subir_foto_perfil_admin(usuario_id):
            """Subir foto de perfil para otro usuario (solo admin)"""
            try:
                from src.api.Service.FotoPerfilService import FotoPerfilService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                # Validar que se envió un archivo
                if 'foto' not in request.files:
                    return response_error("No se proporcionó archivo de foto", 400)
                
                archivo = request.files['foto']
                
                resultado = FotoPerfilService.subir_foto_perfil_admin(archivo, usuario_id, request.current_user)
                
                if resultado['success']:
                    return response_success({
                        'ruta_foto': resultado['ruta_foto']
                    }, resultado['mensaje'])
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en subir_foto_perfil_admin: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/usuarios/<int:usuario_id>/foto', methods=['DELETE'])
        @token_required
        def eliminar_foto_perfil_admin(usuario_id):
            """Eliminar foto de perfil de otro usuario (solo admin)"""
            try:
                from src.api.Service.FotoPerfilService import FotoPerfilService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                resultado = FotoPerfilService.eliminar_foto_perfil_admin(usuario_id, request.current_user)
                
                if resultado['success']:
                    return response_success({}, resultado['message'])
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en eliminar_foto_perfil_admin: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/fotos-perfil/archivo/<path:ruta_foto>', methods=['GET'])
        @token_required
        def obtener_archivo_foto_perfil(ruta_foto):
            """Obtener archivo físico de foto de perfil"""
            try:
                from src.api.Service.FotoPerfilService import FotoPerfilService
                from src.utils.general.response import response_error
                from flask import send_file, request
                
                resultado = FotoPerfilService.obtener_archivo_foto(ruta_foto, request.current_user)
                
                if resultado['success']:
                    return send_file(
                        resultado['ruta_archivo'],
                        mimetype='image/jpeg',
                        as_attachment=False,
                        download_name=f"perfil_{request.current_user['id']}.jpg"
                    )
                else:
                    return response_error(resultado['message'], 404)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_archivo_foto_perfil: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/fotos-perfil/estadisticas', methods=['GET'])
        @token_required
        def obtener_estadisticas_fotos_perfil():
            """Obtener estadísticas de fotos de perfil (solo admin)"""
            try:
                from src.api.Service.FotoPerfilService import FotoPerfilService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                resultado = FotoPerfilService.obtener_estadisticas_fotos(request.current_user)
                
                if resultado['success']:
                    return response_success(resultado['estadisticas'], "Estadísticas obtenidas")
                else:
                    return response_error(resultado['message'], 403)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_estadisticas_fotos_perfil: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/fotos-perfil/formatos', methods=['GET'])
        @token_required
        def obtener_formatos_soportados_fotos():
            """Obtener información sobre formatos soportados"""
            try:
                from src.api.Service.FotoPerfilService import FotoPerfilService
                from src.utils.general.response import response_success
                
                resultado = FotoPerfilService.obtener_formatos_soportados()
                
                return response_success(resultado['formatos'], "Formatos soportados")
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_formatos_soportados_fotos: {str(e)}")
                return response_error("Error interno del servidor", 500)

    # ============================================
    # REGISTRAR RUTAS DE FOTOS DE PERFIL
    # ============================================
    register_foto_perfil_routes(app)

    # ============================================
    # RUTAS DEL SISTEMA DE OBSERVACIONES
    # ============================================
    def register_observaciones_routes(app):
        """Registrar rutas del sistema de observaciones"""
        
        @app.route('/api/observaciones', methods=['POST'])
        @token_required
        def crear_observacion(current_user):
            """Crear una nueva observación"""
            try:
                from src.api.Service.ObservacionesService import ObservacionesService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                data = request.get_json()
                if not data:
                    return response_error("Datos requeridos", 400)
                
                resultado = ObservacionesService.crear_observacion(data, current_user)
                
                if resultado['success']:
                    return response_success({
                        'id_observacion': resultado['id_observacion'],
                        'fecha_registro': resultado['fecha_registro']
                    }, "Observación creada exitosamente")
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en crear_observacion: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/observaciones/sesion/<int:id_sesion>/<tipo_sesion>', methods=['GET'])
        @token_required
        def obtener_observaciones_sesion(current_user, id_sesion, tipo_sesion):
            """Obtener observaciones de una sesión específica"""
            try:
                from src.api.Service.ObservacionesService import ObservacionesService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                incluir_privadas = request.args.get('incluir_privadas', 'false').lower() == 'true'
                
                resultado = ObservacionesService.obtener_observaciones_sesion(
                    id_sesion, tipo_sesion, current_user, incluir_privadas
                )
                
                if resultado['success']:
                    return response_success(resultado['observaciones'], "Observaciones obtenidas")
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_observaciones_sesion: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/observaciones/<int:id_observacion>', methods=['GET'])
        @token_required
        def obtener_observacion_por_id(current_user, id_observacion):
            """Obtener una observación específica"""
            try:
                from src.api.Service.ObservacionesService import ObservacionesService
                from src.utils.general.response import response_success, response_error
                
                resultado = ObservacionesService.obtener_observacion_por_id(id_observacion, current_user)
                
                if resultado['success']:
                    return response_success(resultado['observacion'], "Observación obtenida")
                else:
                    return response_error(resultado['message'], 404)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_observacion_por_id: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/observaciones/<int:id_observacion>', methods=['PUT'])
        @token_required
        def actualizar_observacion(current_user, id_observacion):
            """Actualizar una observación existente"""
            try:
                from src.api.Service.ObservacionesService import ObservacionesService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                data = request.get_json()
                if not data:
                    return response_error("Datos requeridos", 400)
                
                resultado = ObservacionesService.actualizar_observacion(id_observacion, data, current_user)
                
                if resultado['success']:
                    return response_success({
                        'fecha_modificacion': resultado['fecha_modificacion']
                    }, "Observación actualizada exitosamente")
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en actualizar_observacion: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/observaciones/<int:id_observacion>', methods=['DELETE'])
        @token_required
        def eliminar_observacion(current_user, id_observacion):
            """Eliminar una observación"""
            try:
                from src.api.Service.ObservacionesService import ObservacionesService
                from src.utils.general.response import response_success, response_error
                
                resultado = ObservacionesService.eliminar_observacion(id_observacion, current_user)
                
                if resultado['success']:
                    return response_success({}, resultado['message'])
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en eliminar_observacion: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/observaciones/estadisticas', methods=['GET'])
        @token_required
        def obtener_estadisticas_observaciones(current_user):
            """Obtener estadísticas de observaciones"""
            try:
                from src.api.Service.ObservacionesService import ObservacionesService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                solo_propias = request.args.get('solo_propias', 'false').lower() == 'true'
                
                resultado = ObservacionesService.obtener_estadisticas_observaciones(current_user, solo_propias)
                
                if resultado['success']:
                    return response_success(resultado['estadisticas'], "Estadísticas obtenidas")
                else:
                    return response_error(resultado['message'], 500)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_estadisticas_observaciones: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/observaciones/seguimientos-pendientes', methods=['GET'])
        @token_required
        def obtener_seguimientos_pendientes(current_user):
            """Obtener observaciones con seguimiento pendiente"""
            try:
                from src.api.Service.ObservacionesService import ObservacionesService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                solo_asignados = request.args.get('solo_asignados', 'false').lower() == 'true'
                
                resultado = ObservacionesService.obtener_seguimientos_pendientes(current_user, solo_asignados)
                
                if resultado['success']:
                    return response_success(resultado['observaciones_pendientes'], "Seguimientos pendientes obtenidos")
                else:
                    return response_error(resultado['message'], 500)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_seguimientos_pendientes: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/observaciones/buscar', methods=['GET'])
        @token_required
        def buscar_observaciones(current_user):
            """Buscar observaciones con criterios específicos"""
            try:
                from src.api.Service.ObservacionesService import ObservacionesService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                # Recoger criterios de búsqueda de los query parameters
                criterios = {}
                
                if request.args.get('texto'):
                    criterios['texto'] = request.args.get('texto')
                    
                if request.args.get('tipo_observacion'):
                    criterios['tipo_observacion'] = request.args.get('tipo_observacion')
                    
                if request.args.get('tipo_sesion'):
                    criterios['tipo_sesion'] = request.args.get('tipo_sesion')
                    
                if request.args.get('es_critica'):
                    criterios['es_critica'] = request.args.get('es_critica').lower() == 'true'
                    
                if request.args.get('requiere_seguimiento'):
                    criterios['requiere_seguimiento'] = request.args.get('requiere_seguimiento').lower() == 'true'
                    
                if request.args.get('estado_seguimiento'):
                    criterios['estado_seguimiento'] = request.args.get('estado_seguimiento')
                    
                if request.args.get('fecha_inicio'):
                    criterios['fecha_inicio'] = request.args.get('fecha_inicio')
                    
                if request.args.get('fecha_fin'):
                    criterios['fecha_fin'] = request.args.get('fecha_fin')
                
                resultado = ObservacionesService.buscar_observaciones(criterios, current_user)
                
                if resultado['success']:
                    return response_success(resultado['observaciones'], "Búsqueda realizada exitosamente")
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en buscar_observaciones: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/observaciones/tipos', methods=['GET'])
        @token_required
        def obtener_tipos_observacion(current_user):
            """Obtener tipos de observación disponibles"""
            try:
                from src.api.Service.ObservacionesService import ObservacionesService
                from src.utils.general.response import response_success
                
                resultado = ObservacionesService.obtener_tipos_observacion()
                
                return response_success(resultado, "Tipos de observación obtenidos")
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_tipos_observacion: {str(e)}")
                return response_error("Error interno del servidor", 500)

    # ============================================
    # REGISTRAR RUTAS DE OBSERVACIONES
    # ============================================
    register_observaciones_routes(app)

    # ============================================
    # RUTAS DEL SISTEMA DE FOTOS DE ASISTENCIA
    # ============================================
    def register_fotos_asistencia_routes(app):
        """Registrar rutas del sistema de fotos de asistencia"""
        
        @app.route('/api/asistencias/<int:asistencia_id>/fotos', methods=['POST'])
        @token_required
        def subir_fotos_asistencia(asistencia_id):
            """Subir fotos a una asistencia (máximo 3 fotos)"""
            try:
                from src.api.Service.FotoAsistenciaService import FotoAsistenciaService
                from src.api.Components.FotoAsistenciaComponent import FotoAsistenciaComponent
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                # Verificar que la asistencia existe
                if not FotoAsistenciaComponent.verificar_asistencia_existe(asistencia_id):
                    return response_error("Asistencia no encontrada", 404)
                
                # Verificar que se recibieron archivos
                if 'fotos' not in request.files:
                    return response_error("No se recibieron archivos", 400)
                
                archivos = request.files.getlist('fotos')
                if not archivos or all(not archivo.filename for archivo in archivos):
                    return response_error("No se seleccionaron archivos válidos", 400)
                
                # Procesar fotos
                resultado = FotoAsistenciaService.agregar_fotos_asistencia(asistencia_id, archivos)
                
                if resultado['success']:
                    return response_success(
                        resultado.get('fotos', []), 
                        resultado['message']
                    )
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en subir_fotos_asistencia: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/asistencias/<int:asistencia_id>/fotos', methods=['GET'])
        @token_required
        def obtener_fotos_asistencia(asistencia_id):
            """Obtener todas las fotos de una asistencia"""
            try:
                from src.api.Service.FotoAsistenciaService import FotoAsistenciaService
                from src.api.Components.FotoAsistenciaComponent import FotoAsistenciaComponent
                from src.utils.general.response import response_success, response_error
                
                # Verificar que la asistencia existe
                if not FotoAsistenciaComponent.verificar_asistencia_existe(asistencia_id):
                    return response_error("Asistencia no encontrada", 404)
                
                resultado = FotoAsistenciaService.obtener_fotos_asistencia(asistencia_id)
                
                if resultado['success']:
                    return response_success(
                        {
                            'fotos': resultado['data'],
                            'total': resultado['total_fotos']
                        },
                        "Fotos obtenidas exitosamente"
                    )
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_fotos_asistencia: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/asistencias/<int:asistencia_id>/fotos/<int:indice_foto>', methods=['DELETE'])
        @token_required
        def eliminar_foto_asistencia(asistencia_id, indice_foto):
            """Eliminar una foto específica de una asistencia"""
            try:
                from src.api.Service.FotoAsistenciaService import FotoAsistenciaService
                from src.api.Components.FotoAsistenciaComponent import FotoAsistenciaComponent
                from src.utils.general.response import response_success, response_error
                
                # Verificar que la asistencia existe
                if not FotoAsistenciaComponent.verificar_asistencia_existe(asistencia_id):
                    return response_error("Asistencia no encontrada", 404)
                
                resultado = FotoAsistenciaService.eliminar_foto_asistencia(asistencia_id, indice_foto)
                
                if resultado['success']:
                    return response_success(None, resultado['message'])
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en eliminar_foto_asistencia: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/asistencias/fotos/estadisticas', methods=['GET'])
        @token_required
        def obtener_estadisticas_fotos_asistencia():
            """Obtener estadísticas generales de fotos de asistencia"""
            try:
                from src.api.Service.FotoAsistenciaService import FotoAsistenciaService
                from src.utils.general.response import response_success, response_error
                
                resultado = FotoAsistenciaService.obtener_estadisticas_fotos()
                
                if resultado['success']:
                    return response_success(resultado['data'], "Estadísticas obtenidas exitosamente")
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_estadisticas_fotos_asistencia: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/asistencias/con-fotos', methods=['GET'])
        @token_required
        def obtener_asistencias_con_fotos():
            """Obtener asistencias que tienen fotos adjuntas"""
            try:
                from src.api.Components.FotoAsistenciaComponent import FotoAsistenciaComponent
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                # Obtener filtros opcionales
                sesion_id = request.args.get('sesion_id', type=int)
                paciente_id = request.args.get('paciente_id', type=int)
                fecha_desde = request.args.get('fecha_desde')
                fecha_hasta = request.args.get('fecha_hasta')
                
                asistencias = FotoAsistenciaComponent.obtener_asistencias_con_fotos(
                    sesion_id=sesion_id,
                    paciente_id=paciente_id,
                    fecha_desde=fecha_desde,
                    fecha_hasta=fecha_hasta
                )
                
                return response_success(
                    {
                        'asistencias': asistencias,
                        'total': len(asistencias)
                    },
                    "Asistencias con fotos obtenidas exitosamente"
                )
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en obtener_asistencias_con_fotos: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/asistencias/<int:asistencia_id>/fotos/todas', methods=['DELETE'])
        @token_required
        def eliminar_todas_fotos_asistencia(asistencia_id):
            """Eliminar todas las fotos de una asistencia"""
            try:
                from src.api.Components.FotoAsistenciaComponent import FotoAsistenciaComponent
                from src.utils.general.response import response_success, response_error
                
                # Verificar que la asistencia existe
                if not FotoAsistenciaComponent.verificar_asistencia_existe(asistencia_id):
                    return response_error("Asistencia no encontrada", 404)
                
                resultado = FotoAsistenciaComponent.eliminar_todas_fotos_asistencia(asistencia_id)
                
                if resultado['success']:
                    return response_success(None, resultado['message'])
                else:
                    return response_error(resultado['message'], 400)
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en eliminar_todas_fotos_asistencia: {str(e)}")
                return response_error("Error interno del servidor", 500)

    # ============================================
    # REGISTRAR RUTAS DE FOTOS DE ASISTENCIA
    # ============================================
    register_fotos_asistencia_routes(app)

    # ============================================
    # RUTAS DEL DASHBOARD
    # ============================================
    def register_dashboard_routes(app):
        """Registrar rutas del dashboard"""
        
        @app.route('/api/dashboard/estadisticas', methods=['GET'])
        @token_required
        def get_estadisticas_dashboard():
            """Obtener estadísticas generales del dashboard"""
            try:
                from src.api.Service.DashboardService import DashboardService
                from src.utils.general.response import response_success, response_error
                
                dashboard_service = DashboardService()
                resultado = dashboard_service.get_todas_estadisticas()
                
                return response_success(resultado, "Estadísticas del dashboard obtenidas exitosamente")
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_estadisticas_dashboard: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/dashboard/usuarios-activos', methods=['GET'])
        @token_required
        def get_usuarios_activos_dashboard():
            """Obtener conteo de usuarios activos"""
            try:
                from src.api.Service.DashboardService import DashboardService
                from src.utils.general.response import response_success, response_error
                
                dashboard_service = DashboardService()
                resultado = dashboard_service.get_usuarios_activos()
                
                return response_success(resultado, "Usuarios activos obtenidos exitosamente")
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_usuarios_activos_dashboard: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/dashboard/contador-pacientes', methods=['GET'])
        @token_required
        def get_contador_pacientes_dashboard():
            """Obtener conteo total de pacientes"""
            try:
                from src.api.Service.DashboardService import DashboardService
                from src.utils.general.response import response_success, response_error
                
                dashboard_service = DashboardService()
                resultado = dashboard_service.get_contador_pacientes()
                
                return response_success(resultado, "Contador de pacientes obtenido exitosamente")
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_contador_pacientes_dashboard: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/dashboard/resumen-personal', methods=['GET'])
        @token_required
        def get_resumen_personal_dashboard():
            """Obtener resumen del personal (terapeutas, pedagogos, especialidades)"""
            try:
                from src.api.Service.DashboardService import DashboardService
                from src.utils.general.response import response_success, response_error
                
                dashboard_service = DashboardService()
                resultado = dashboard_service.get_resumen_personal()
                
                return response_success(resultado, "Resumen del personal obtenido exitosamente")
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_resumen_personal_dashboard: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/dashboard/actividad-reciente', methods=['GET'])
        @token_required
        def get_actividad_reciente_dashboard():
            """Obtener actividad reciente del sistema"""
            try:
                from src.api.Service.DashboardService import DashboardService
                from src.utils.general.response import response_success, response_error
                from flask import request
                
                limite = request.args.get('limite', 10, type=int)
                
                dashboard_service = DashboardService()
                resultado = dashboard_service.get_actividad_reciente(limite)
                
                return response_success(resultado, "Actividad reciente obtenida exitosamente")
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_actividad_reciente_dashboard: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/dashboard/alertas', methods=['GET'])
        @token_required
        def get_alertas_dashboard():
            """Obtener alertas del sistema"""
            try:
                from src.api.Service.DashboardService import DashboardService
                from src.utils.general.response import response_success, response_error
                
                dashboard_service = DashboardService()
                resultado = dashboard_service.get_alertas_sistema()
                
                return response_success(resultado, "Alertas del sistema obtenidas exitosamente")
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_alertas_dashboard: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/dashboard/rendimiento-semanal', methods=['GET'])
        @token_required
        def get_rendimiento_semanal_dashboard():
            """Obtener rendimiento semanal"""
            try:
                from src.api.Service.DashboardService import DashboardService
                from src.utils.general.response import response_success, response_error
                
                dashboard_service = DashboardService()
                resultado = dashboard_service.get_rendimiento_semanal()
                
                return response_success(resultado, "Rendimiento semanal obtenido exitosamente")
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_rendimiento_semanal_dashboard: {str(e)}")
                return response_error("Error interno del servidor", 500)

        @app.route('/api/dashboard/metricas-asistencia', methods=['GET'])
        @token_required
        def get_metricas_asistencia_dashboard():
            """Obtener métricas de asistencia"""
            try:
                from src.api.Service.DashboardService import DashboardService
                from src.utils.general.response import response_success, response_error
                
                dashboard_service = DashboardService()
                resultado = dashboard_service.get_metricas_asistencia()
                
                return response_success(resultado, "Métricas de asistencia obtenidas exitosamente")
                    
            except Exception as e:
                HandleLogs.write_error(f"Error en get_metricas_asistencia_dashboard: {str(e)}")
                return response_error("Error interno del servidor", 500)

    # ============================================
    # REGISTRAR RUTAS DEL DASHBOARD
    # ============================================
    register_dashboard_routes(app)


