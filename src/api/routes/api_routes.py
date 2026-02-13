"""
Archivo simplificado de registro de rutas usando Blueprints.

Este archivo reemplaza la version monolitica de api_routes.py.
Los modulos principales estan en blueprints separados en la carpeta blueprints/.

Modulos migrados a blueprints:
- public_bp: Rutas publicas (test, test-db, sesion-publica)
- auth_bp: Autenticacion (login, logout, verify-token, me, centros)
- centro_bp: Gestion de centros
- rol_bp: Gestion de roles
- persona_bp: Gestion de personas
- especialidad_bp: Gestion de especialidades
- personal_bp: Personal y documentos de personal
- usuario_bp: Gestion de usuarios
- tutor_bp: Gestion de tutores
- paciente_bp: Pacientes, especialidades, pausas, documentos
- sesion_terapia_bp: Sesiones de terapia, cronograma, asistencia
- sesion_pedagogica_bp: Sesiones pedagogicas, cronograma, asistencia
- dashboard_bp: Dashboard, estadisticas, agenda

Modulos pendientes de migracion (se registran directamente):
- Chat
- Foto de perfil
- Observaciones
- Reportes
- Configuracion
- Notificaciones
- Admin scheduler
- Fotos de asistencia
"""
from flask import request, send_file
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error
from src.utils.general.auth_middleware import token_required, admin_required


def register_routes(app):
    """Registrar todas las rutas del API"""

    # ============================================
    # REGISTRAR BLUEPRINTS MODULARES
    # ============================================
    from src.api.routes.blueprints import register_all_blueprints
    register_all_blueprints(app)

    HandleLogs.write_log("Blueprints modulares registrados exitosamente")

    # ============================================
    # RUTAS PENDIENTES DE MIGRACION
    # Las siguientes secciones se mantienen temporalmente
    # hasta que se migren a sus respectivos blueprints
    # ============================================

    _register_chat_routes(app)
    _register_foto_perfil_routes(app)
    _register_observaciones_routes(app)
    _register_fotos_asistencia_routes(app)
    _register_reportes_routes(app)
    _register_configuracion_routes(app)
    _register_notificaciones_routes(app)
    _register_admin_routes(app)

    HandleLogs.write_log("Rutas legacy registradas exitosamente")


# ============================================
# CHAT
# ============================================
def _register_chat_routes(app):
    """Rutas del sistema de chat"""

    @app.route('/api/chat/conversaciones', methods=['GET'])
    @token_required
    def get_conversaciones():
        try:
            from src.api.Service.ChatService import ChatService

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
        try:
            from src.api.Service.ChatService import ChatService

            permisos = ChatService.validar_permisos_chat(request.current_user)
            if not permisos['success']:
                return response_error(permisos['message'], 403)

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
        try:
            from src.api.Service.ChatService import ChatService

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
        try:
            from src.api.Service.ChatService import ChatService

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
        try:
            from src.api.Service.ChatService import ChatService

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

    @app.route('/api/chat/mensajes-no-leidos/count', methods=['GET'])
    @token_required
    def get_unread_messages_count():
        try:
            from src.api.Service.ChatService import ChatService

            permisos = ChatService.validar_permisos_chat(request.current_user)
            if not permisos['success']:
                return response_error(permisos['message'], 403)

            resultado = ChatService.obtener_conteo_mensajes_no_leidos(request.current_user)

            if resultado['success']:
                return response_success({'count': resultado['count']}, "Conteo obtenido")
            else:
                return response_error(resultado['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en get_unread_messages_count: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/chat/estadisticas', methods=['GET'])
    @token_required
    def get_estadisticas_chat():
        try:
            from src.api.Service.ChatService import ChatService

            permisos = ChatService.validar_permisos_chat(request.current_user)
            if not permisos['success']:
                return response_error(permisos['message'], 403)

            resultado = ChatService.obtener_estadisticas_mensajes(request.current_user)

            if resultado['success']:
                return response_success(resultado['estadisticas'], "Estadisticas obtenidas")
            else:
                return response_error(resultado['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en get_estadisticas_chat: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/chat/buscar', methods=['GET'])
    @token_required
    def buscar_mensajes_chat():
        try:
            from src.api.Service.ChatService import ChatService

            permisos = ChatService.validar_permisos_chat(request.current_user)
            if not permisos['success']:
                return response_error(permisos['message'], 403)

            texto_busqueda = request.args.get('q')
            id_contacto = request.args.get('contacto', type=int)

            if not texto_busqueda:
                return response_error("Parametro 'q' requerido para la busqueda", 400)

            resultado = ChatService.buscar_mensajes(texto_busqueda, request.current_user, id_contacto)

            if resultado['success']:
                return response_success(resultado['mensajes'], "Busqueda realizada exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en buscar_mensajes_chat: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/chat/mensaje/<int:id_mensaje>', methods=['DELETE'])
    @token_required
    def eliminar_mensaje_chat(id_mensaje):
        try:
            from src.api.Service.ChatService import ChatService

            permisos = ChatService.validar_permisos_chat(request.current_user)
            if not permisos['success']:
                return response_error(permisos['message'], 403)

            resultado = ChatService.eliminar_mensaje(id_mensaje, request.current_user)

            if resultado['success']:
                return response_success({}, resultado['message'])
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en eliminar_mensaje_chat: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/chat/conversacion/<int:id_contacto>', methods=['DELETE'])
    @token_required
    def eliminar_conversacion_chat(id_contacto):
        try:
            from src.api.Service.ChatService import ChatService

            permisos = ChatService.validar_permisos_chat(request.current_user)
            if not permisos['success']:
                return response_error(permisos['message'], 403)

            resultado = ChatService.eliminar_conversacion(id_contacto, request.current_user)

            if resultado['success']:
                return response_success({}, resultado['message'])
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en eliminar_conversacion_chat: {str(e)}")
            return response_error("Error interno del servidor", 500)


# ============================================
# FOTOS DE PERFIL
# ============================================
def _register_foto_perfil_routes(app):
    """Rutas de fotos de perfil"""

    @app.route('/api/perfil/foto', methods=['POST'])
    @token_required
    def subir_foto_perfil():
        try:
            from src.api.Service.FotoPerfilService import FotoPerfilService

            if 'foto' not in request.files:
                return response_error("No se proporciono archivo de foto", 400)

            archivo = request.files['foto']

            resultado = FotoPerfilService.subir_foto_perfil(archivo, request.current_user)

            if resultado['success']:
                return response_success({
                    'ruta_foto': resultado['ruta_foto']
                }, resultado['message'])
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en subir_foto_perfil: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/perfil/foto', methods=['GET'])
    @token_required
    def obtener_mi_foto_perfil():
        try:
            from src.api.Service.FotoPerfilService import FotoPerfilService

            resultado = FotoPerfilService.obtener_mi_foto_perfil(request.current_user)

            if resultado['success']:
                return response_success(resultado['foto_perfil'], "Informacion de foto obtenida")
            else:
                return response_error(resultado['message'], 404)

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_mi_foto_perfil: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/perfil/foto', methods=['DELETE'])
    @token_required
    def eliminar_mi_foto_perfil():
        try:
            from src.api.Service.FotoPerfilService import FotoPerfilService

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
        try:
            from src.api.Service.FotoPerfilService import FotoPerfilService

            resultado = FotoPerfilService.obtener_foto_perfil(usuario_id, request.current_user)

            if resultado['success']:
                return response_success(resultado['foto_perfil'], "Informacion de foto obtenida")
            else:
                return response_error(resultado['message'], 404)

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_foto_perfil_usuario: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/usuarios/<int:usuario_id>/foto', methods=['POST'])
    @token_required
    def subir_foto_perfil_admin(usuario_id):
        try:
            from src.api.Service.FotoPerfilService import FotoPerfilService

            if 'foto' not in request.files:
                return response_error("No se proporciono archivo de foto", 400)

            archivo = request.files['foto']

            resultado = FotoPerfilService.subir_foto_perfil_admin(archivo, usuario_id, request.current_user)

            if resultado['success']:
                return response_success({
                    'ruta_foto': resultado['ruta_foto']
                }, resultado['message'])
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en subir_foto_perfil_admin: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/usuarios/<int:usuario_id>/foto', methods=['DELETE'])
    @token_required
    def eliminar_foto_perfil_admin(usuario_id):
        try:
            from src.api.Service.FotoPerfilService import FotoPerfilService

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
        try:
            from src.api.Service.FotoPerfilService import FotoPerfilService

            resultado = FotoPerfilService.obtener_archivo_foto(ruta_foto, request.current_user)

            if resultado['success']:
                return send_file(
                    resultado['ruta_archivo'],
                    mimetype='image/jpeg',
                    as_attachment=False
                )
            else:
                return response_error(resultado['message'], 404)

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_archivo_foto_perfil: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/fotos-perfil/estadisticas', methods=['GET'])
    @token_required
    def obtener_estadisticas_fotos_perfil():
        try:
            from src.api.Service.FotoPerfilService import FotoPerfilService

            resultado = FotoPerfilService.obtener_estadisticas_fotos(request.current_user)

            if resultado['success']:
                return response_success(resultado['estadisticas'], "Estadisticas obtenidas")
            else:
                return response_error(resultado['message'], 403)

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_estadisticas_fotos_perfil: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/fotos-perfil/formatos', methods=['GET'])
    @token_required
    def obtener_formatos_soportados_fotos():
        try:
            from src.api.Service.FotoPerfilService import FotoPerfilService

            resultado = FotoPerfilService.obtener_formatos_soportados()

            return response_success(resultado['formatos'], "Formatos soportados")

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_formatos_soportados_fotos: {str(e)}")
            return response_error("Error interno del servidor", 500)


# ============================================
# OBSERVACIONES
# ============================================
def _register_observaciones_routes(app):
    """Rutas del sistema de observaciones"""

    @app.route('/api/observaciones', methods=['POST'])
    @token_required
    def crear_observacion():
        try:
            from src.api.Service.ObservacionesService import ObservacionesService

            data = request.get_json()
            if not data:
                return response_error("Datos requeridos", 400)

            resultado = ObservacionesService.crear_observacion(data, request.current_user)

            if resultado['success']:
                return response_success({
                    'id_observacion': resultado['id_observacion'],
                    'fecha_registro': resultado['fecha_registro']
                }, "Observacion creada exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en crear_observacion: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/observaciones/sesion/<int:id_sesion>/<tipo_sesion>', methods=['GET'])
    @token_required
    def obtener_observaciones_sesion(id_sesion, tipo_sesion):
        try:
            from src.api.Service.ObservacionesService import ObservacionesService

            incluir_privadas = request.args.get('incluir_privadas', 'false').lower() == 'true'

            resultado = ObservacionesService.obtener_observaciones_sesion(
                id_sesion, tipo_sesion, request.current_user, incluir_privadas
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
    def obtener_observacion_por_id(id_observacion):
        try:
            from src.api.Service.ObservacionesService import ObservacionesService

            resultado = ObservacionesService.obtener_observacion_por_id(id_observacion, request.current_user)

            if resultado['success']:
                return response_success(resultado['observacion'], "Observacion obtenida")
            else:
                return response_error(resultado['message'], 404)

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_observacion_por_id: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/observaciones/<int:id_observacion>', methods=['PUT'])
    @token_required
    def actualizar_observacion(id_observacion):
        try:
            from src.api.Service.ObservacionesService import ObservacionesService

            data = request.get_json()
            if not data:
                return response_error("Datos requeridos", 400)

            resultado = ObservacionesService.actualizar_observacion(id_observacion, data, request.current_user)

            if resultado['success']:
                return response_success({
                    'fecha_modificacion': resultado['fecha_modificacion']
                }, "Observacion actualizada exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en actualizar_observacion: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/observaciones/<int:id_observacion>', methods=['DELETE'])
    @token_required
    def eliminar_observacion(id_observacion):
        try:
            from src.api.Service.ObservacionesService import ObservacionesService

            resultado = ObservacionesService.eliminar_observacion(id_observacion, request.current_user)

            if resultado['success']:
                return response_success({}, resultado['message'])
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en eliminar_observacion: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/observaciones/estadisticas', methods=['GET'])
    @token_required
    def obtener_estadisticas_observaciones():
        try:
            from src.api.Service.ObservacionesService import ObservacionesService

            solo_propias = request.args.get('solo_propias', 'false').lower() == 'true'

            resultado = ObservacionesService.obtener_estadisticas_observaciones(request.current_user, solo_propias)

            if resultado['success']:
                return response_success(resultado['estadisticas'], "Estadisticas obtenidas")
            else:
                return response_error(resultado['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_estadisticas_observaciones: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/observaciones/seguimientos-pendientes', methods=['GET'])
    @token_required
    def obtener_seguimientos_pendientes():
        try:
            from src.api.Service.ObservacionesService import ObservacionesService

            solo_asignados = request.args.get('solo_asignados', 'false').lower() == 'true'

            resultado = ObservacionesService.obtener_seguimientos_pendientes(request.current_user, solo_asignados)

            if resultado['success']:
                return response_success(resultado['observaciones_pendientes'], "Seguimientos pendientes obtenidos")
            else:
                return response_error(resultado['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_seguimientos_pendientes: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/observaciones/buscar', methods=['GET'])
    @token_required
    def buscar_observaciones():
        try:
            from src.api.Service.ObservacionesService import ObservacionesService

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

            resultado = ObservacionesService.buscar_observaciones(criterios, request.current_user)

            if resultado['success']:
                return response_success(resultado['observaciones'], "Busqueda realizada exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en buscar_observaciones: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/observaciones/tipos', methods=['GET'])
    @token_required
    def obtener_tipos_observacion():
        try:
            from src.api.Service.ObservacionesService import ObservacionesService

            resultado = ObservacionesService.obtener_tipos_observacion()

            return response_success(resultado, "Tipos de observacion obtenidos")

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_tipos_observacion: {str(e)}")
            return response_error("Error interno del servidor", 500)


# ============================================
# FOTOS DE ASISTENCIA
# ============================================
def _register_fotos_asistencia_routes(app):
    """Rutas del sistema de fotos de asistencia"""

    @app.route('/api/asistencias/<int:asistencia_id>/fotos', methods=['POST'])
    @token_required
    def subir_fotos_asistencia(asistencia_id):
        try:
            from src.api.Service.FotoAsistenciaService import FotoAsistenciaService
            from src.api.Components.FotoAsistenciaComponent import FotoAsistenciaComponent

            if not FotoAsistenciaComponent.verificar_asistencia_existe(asistencia_id):
                return response_error("Asistencia no encontrada", 404)

            if 'fotos' not in request.files:
                return response_error("No se recibieron archivos", 400)

            archivos = request.files.getlist('fotos')
            if not archivos or all(not archivo.filename for archivo in archivos):
                return response_error("No se seleccionaron archivos validos", 400)

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
        try:
            from src.api.Service.FotoAsistenciaService import FotoAsistenciaService
            from src.api.Components.FotoAsistenciaComponent import FotoAsistenciaComponent

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
        try:
            from src.api.Service.FotoAsistenciaService import FotoAsistenciaService
            from src.api.Components.FotoAsistenciaComponent import FotoAsistenciaComponent

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
        try:
            from src.api.Service.FotoAsistenciaService import FotoAsistenciaService

            resultado = FotoAsistenciaService.obtener_estadisticas_fotos()

            if resultado['success']:
                return response_success(resultado['data'], "Estadisticas obtenidas exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_estadisticas_fotos_asistencia: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/asistencias/con-fotos', methods=['GET'])
    @token_required
    def obtener_asistencias_con_fotos():
        try:
            from src.api.Components.FotoAsistenciaComponent import FotoAsistenciaComponent

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
        try:
            from src.api.Components.FotoAsistenciaComponent import FotoAsistenciaComponent

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
# REPORTES
# ============================================
def _register_reportes_routes(app):
    """Rutas del sistema de reportes"""

    @app.route('/api/reportes/disponibles', methods=['GET'])
    @token_required
    def get_reportes_disponibles():
        try:
            from src.api.Service.ReportesService import ReportesService

            resultado = ReportesService.get_lista_reportes_disponibles(request.current_user)

            if resultado['success']:
                return response_success(resultado, "Lista de reportes disponibles obtenida exitosamente")
            else:
                return response_error(resultado['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en get_reportes_disponibles: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/reportes/asistencia-paciente', methods=['POST'])
    @token_required
    def generate_reporte_asistencia_paciente():
        try:
            from src.api.Service.ReportesService import ReportesService

            data = request.get_json()
            if not data:
                return response_error("Datos requeridos", 400)

            filtros = data.get('filtros', data)
            resultado = ReportesService.get_reporte_asistencia_paciente(filtros, request.current_user)

            if resultado['success']:
                return response_success(resultado, "Reporte de asistencia generado exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en generate_reporte_asistencia_paciente: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/reportes/progreso-terapeutico', methods=['POST'])
    @token_required
    def generate_reporte_progreso_terapeutico():
        try:
            from src.api.Service.ReportesService import ReportesService

            data = request.get_json()
            if not data:
                return response_error("Datos requeridos", 400)

            filtros = data.get('filtros', data)
            resultado = ReportesService.get_reporte_progreso_terapeutico(filtros, request.current_user)

            if resultado['success']:
                return response_success(resultado, "Reporte de progreso terapeutico generado exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en generate_reporte_progreso_terapeutico: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/reportes/carga-trabajo-personal', methods=['POST'])
    @token_required
    def generate_reporte_carga_trabajo_personal():
        try:
            from src.api.Service.ReportesService import ReportesService

            data = request.get_json()
            filtros = data.get('filtros', data) if data else {}
            resultado = ReportesService.get_reporte_carga_trabajo_personal(filtros, request.current_user)

            if resultado['success']:
                return response_success(resultado, "Reporte de carga de trabajo generado exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en generate_reporte_carga_trabajo_personal: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/reportes/academico-estudiante', methods=['POST'])
    @token_required
    def generate_reporte_academico_estudiante():
        try:
            from src.api.Service.ReportesService import ReportesService

            data = request.get_json()
            filtros = data.get('filtros', data) if data else {}
            resultado = ReportesService.get_reporte_academico_estudiante(filtros, request.current_user)

            if resultado['success']:
                return response_success(resultado, "Reporte academico generado exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en generate_reporte_academico_estudiante: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/reportes/rendimiento-clase', methods=['POST'])
    @token_required
    def generate_reporte_rendimiento_clase():
        try:
            from src.api.Service.ReportesService import ReportesService

            data = request.get_json()
            filtros = data.get('filtros', data) if data else {}
            resultado = ReportesService.get_reporte_rendimiento_clase(filtros, request.current_user)

            if resultado['success']:
                return response_success(resultado, "Reporte de rendimiento por clase generado exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en generate_reporte_rendimiento_clase: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/reportes/utilizacion-recursos', methods=['POST'])
    @token_required
    def generate_reporte_utilizacion_recursos():
        try:
            from src.api.Service.ReportesService import ReportesService

            data = request.get_json()
            filtros = data.get('filtros', data) if data else {}
            resultado = ReportesService.get_reporte_utilizacion_recursos(filtros, request.current_user)

            if resultado['success']:
                return response_success(resultado, "Reporte de utilizacion de recursos generado exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en generate_reporte_utilizacion_recursos: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/reportes/estadisticas-generales', methods=['POST'])
    @token_required
    def generate_estadisticas_generales_reportes():
        try:
            from src.api.Service.ReportesService import ReportesService

            data = request.get_json()
            filtros = data.get('filtros', data) if data else {}
            resultado = ReportesService.get_estadisticas_generales_reportes(filtros, request.current_user)

            if resultado['success']:
                return response_success(resultado, "Estadisticas generales generadas exitosamente")
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en generate_estadisticas_generales_reportes: {str(e)}")
            return response_error("Error interno del servidor", 500)

    # Exportacion
    @app.route('/api/reportes/export/pdf', methods=['POST'])
    @token_required
    def export_reporte_pdf():
        from src.api.Service.ExportService import ExportService
        try:
            data = request.get_json()
            if not data or 'data' not in data or 'metadata' not in data:
                return response_error("Datos y metadata requeridos", 400)

            formato = data.get('formato', 'portrait')
            resultado = ExportService.export_to_pdf(data['data'], data['metadata'], formato)

            if resultado['success']:
                return send_file(
                    resultado['file_path'],
                    as_attachment=True,
                    download_name=resultado['filename'],
                    mimetype='application/pdf'
                )
            else:
                return response_error(resultado['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en export_reporte_pdf: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/reportes/export/excel', methods=['POST'])
    @token_required
    def export_reporte_excel():
        from src.api.Service.ExportService import ExportService
        try:
            data = request.get_json()
            if not data or 'data' not in data or 'metadata' not in data:
                return response_error("Datos y metadata requeridos", 400)

            resultado = ExportService.export_to_excel(data['data'], data['metadata'])

            if resultado['success']:
                return send_file(
                    resultado['file_path'],
                    as_attachment=True,
                    download_name=resultado['filename'],
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                return response_error(resultado['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en export_reporte_excel: {str(e)}")
            return response_error("Error interno del servidor", 500)


# ============================================
# CONFIGURACION
# ============================================
def _register_configuracion_routes(app):
    """Rutas de configuracion del sistema"""

    @app.route('/api/configuracion/general', methods=['GET'])
    @token_required
    def get_configuracion_general():
        from src.api.Service.ConfiguracionService import ConfiguracionService
        return ConfiguracionService.get_configuracion_general()

    @app.route('/api/configuracion/general', methods=['PUT'])
    @admin_required
    def update_configuracion_general():
        from src.api.Service.ConfiguracionService import ConfiguracionService
        return ConfiguracionService.update_configuracion_general()

    @app.route('/api/configuracion/notificaciones/global', methods=['GET'])
    @admin_required
    def get_configuracion_notificaciones_global():
        from src.api.Service.ConfiguracionService import ConfiguracionService
        return ConfiguracionService.get_configuracion_notificaciones()

    @app.route('/api/configuracion/notificaciones/global', methods=['PUT'])
    @admin_required
    def update_configuracion_notificaciones_global():
        from src.api.Service.ConfiguracionService import ConfiguracionService
        return ConfiguracionService.update_configuracion_notificaciones()

    @app.route('/api/configuracion/notificaciones/usuario', methods=['GET'])
    @token_required
    def get_configuracion_notificaciones_usuario():
        from src.api.Service.ConfiguracionService import ConfiguracionService
        user_id = request.current_user.get('id')
        return ConfiguracionService.get_configuracion_notificaciones(user_id)

    @app.route('/api/configuracion/notificaciones/usuario', methods=['PUT'])
    @token_required
    def update_configuracion_notificaciones_usuario():
        from src.api.Service.ConfiguracionService import ConfiguracionService
        user_id = request.current_user.get('id')
        return ConfiguracionService.update_configuracion_notificaciones(user_id)

    @app.route('/api/configuracion/notificaciones/usuario/<int:user_id>', methods=['GET'])
    @admin_required
    def get_configuracion_notificaciones_usuario_especifico(user_id):
        from src.api.Service.ConfiguracionService import ConfiguracionService
        return ConfiguracionService.get_configuracion_notificaciones(user_id)

    @app.route('/api/configuracion/notificaciones/usuario/<int:user_id>', methods=['PUT'])
    @admin_required
    def update_configuracion_notificaciones_usuario_especifico(user_id):
        from src.api.Service.ConfiguracionService import ConfiguracionService
        return ConfiguracionService.update_configuracion_notificaciones(user_id)

    @app.route('/api/configuracion/resumen', methods=['GET'])
    @token_required
    def get_resumen_configuracion():
        from src.api.Service.ConfiguracionService import ConfiguracionService
        return ConfiguracionService.get_resumen_configuracion()


# ============================================
# NOTIFICACIONES
# ============================================
def _register_notificaciones_routes(app):
    """Rutas del sistema de notificaciones push"""

    @app.route('/api/notificaciones', methods=['GET'])
    @token_required
    def obtener_mis_notificaciones():
        try:
            from src.api.Service.NotificacionesService import NotificacionesService

            permisos = NotificacionesService.validar_permisos_notificaciones(request.current_user)
            if not permisos['success']:
                return response_error(permisos['message'], 403)

            incluir_leidas = request.args.get('incluir_leidas', 'false').lower() == 'true'
            limite = request.args.get('limite', 50, type=int)

            resultado = NotificacionesService.obtener_notificaciones_usuario(
                request.current_user, incluir_leidas, limite
            )

            if resultado['success']:
                return response_success({
                    'notificaciones': resultado['notificaciones'],
                    'total': resultado['total']
                }, "Notificaciones obtenidas exitosamente")
            else:
                return response_error(resultado['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_mis_notificaciones: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/notificaciones/<int:id_notificacion>/leer', methods=['PUT'])
    @token_required
    def marcar_notificacion_leida(id_notificacion):
        try:
            from src.api.Service.NotificacionesService import NotificacionesService

            permisos = NotificacionesService.validar_permisos_notificaciones(request.current_user)
            if not permisos['success']:
                return response_error(permisos['message'], 403)

            resultado = NotificacionesService.marcar_notificacion_leida(
                id_notificacion, request.current_user
            )

            if resultado['success']:
                return response_success({}, resultado['message'])
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en marcar_notificacion_leida: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/notificaciones/estadisticas', methods=['GET'])
    @token_required
    def obtener_estadisticas_notificaciones():
        try:
            from src.api.Service.NotificacionesService import NotificacionesService

            permisos = NotificacionesService.validar_permisos_notificaciones(request.current_user)
            if not permisos['success']:
                return response_error(permisos['message'], 403)

            resultado = NotificacionesService.obtener_estadisticas_notificaciones(request.current_user)

            if resultado['success']:
                return response_success(resultado['estadisticas'], "Estadisticas obtenidas exitosamente")
            else:
                return response_error(resultado['message'], 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_estadisticas_notificaciones: {str(e)}")
            return response_error("Error interno del servidor", 500)


# ============================================
# ADMIN SCHEDULER
# ============================================
def _register_admin_routes(app):
    """Rutas de administracion del scheduler de notificaciones"""

    @app.route('/api/admin/scheduler/estado', methods=['GET'])
    @admin_required
    def obtener_estado_scheduler():
        try:
            from src.utils.general.NotificationScheduler import obtener_scheduler

            scheduler = obtener_scheduler()
            estado = scheduler.obtener_estado_scheduler()

            return response_success(estado, "Estado del scheduler obtenido")

        except Exception as e:
            HandleLogs.write_error(f"Error en obtener_estado_scheduler: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/admin/scheduler/iniciar', methods=['POST'])
    @admin_required
    def iniciar_scheduler():
        try:
            from src.utils.general.NotificationScheduler import iniciar_scheduler_global

            exito = iniciar_scheduler_global()

            if exito:
                return response_success({}, "Scheduler iniciado exitosamente")
            else:
                return response_error("Error al iniciar scheduler", 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en iniciar_scheduler: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/admin/scheduler/detener', methods=['POST'])
    @admin_required
    def detener_scheduler():
        try:
            from src.utils.general.NotificationScheduler import detener_scheduler_global

            exito = detener_scheduler_global()

            if exito:
                return response_success({}, "Scheduler detenido exitosamente")
            else:
                return response_error("Error al detener scheduler", 500)

        except Exception as e:
            HandleLogs.write_error(f"Error en detener_scheduler: {str(e)}")
            return response_error("Error interno del servidor", 500)

    @app.route('/api/admin/scheduler/job/<nombre_job>/ejecutar', methods=['POST'])
    @admin_required
    def ejecutar_job_manual(nombre_job):
        try:
            from src.utils.general.NotificationScheduler import obtener_scheduler

            scheduler = obtener_scheduler()
            resultado = scheduler.ejecutar_job_manual(nombre_job)

            if resultado['success']:
                return response_success({
                    'timestamp': resultado['timestamp']
                }, resultado['message'])
            else:
                return response_error(resultado['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"Error en ejecutar_job_manual: {str(e)}")
            return response_error("Error interno del servidor", 500)
