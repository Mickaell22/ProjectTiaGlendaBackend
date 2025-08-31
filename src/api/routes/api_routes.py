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


