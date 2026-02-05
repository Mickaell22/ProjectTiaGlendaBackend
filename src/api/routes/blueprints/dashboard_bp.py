"""
Blueprint para rutas de dashboard, estadisticas y reportes.
"""
from flask import Blueprint, request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error
from src.utils.general.auth_middleware import token_required, admin_required

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')


# ============================================
# ESTADISTICAS GENERALES
# ============================================
@dashboard_bp.route('/dashboard/estadisticas', methods=['GET'])
@token_required
def get_estadisticas_dashboard():
    try:
        from src.api.Service.DashboardService import DashboardService
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_todas_estadisticas()
        return response_success(resultado, "Estadisticas del dashboard obtenidas exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_estadisticas_dashboard: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/usuarios-activos', methods=['GET'])
@token_required
def get_usuarios_activos_dashboard():
    try:
        from src.api.Service.DashboardService import DashboardService
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_usuarios_activos()
        return response_success(resultado, "Usuarios activos obtenidos exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_usuarios_activos_dashboard: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/contador-pacientes', methods=['GET'])
@token_required
def get_contador_pacientes_dashboard():
    try:
        from src.api.Service.DashboardService import DashboardService
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_contador_pacientes()
        return response_success(resultado, "Contador de pacientes obtenido exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_contador_pacientes_dashboard: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/resumen-personal', methods=['GET'])
@token_required
def get_resumen_personal_dashboard():
    try:
        from src.api.Service.DashboardService import DashboardService
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_resumen_personal()
        return response_success(resultado, "Resumen del personal obtenido exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_resumen_personal_dashboard: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/actividad-reciente', methods=['GET'])
@token_required
def get_actividad_reciente_dashboard():
    try:
        from src.api.Service.DashboardService import DashboardService
        limite = request.args.get('limite', 10, type=int)
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_actividad_reciente(limite)
        return response_success(resultado, "Actividad reciente obtenida exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_actividad_reciente_dashboard: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/alertas', methods=['GET'])
@token_required
def get_alertas_dashboard():
    try:
        from src.api.Service.DashboardService import DashboardService
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_alertas_sistema()
        return response_success(resultado, "Alertas del sistema obtenidas exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_alertas_dashboard: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/rendimiento-semanal', methods=['GET'])
@token_required
def get_rendimiento_semanal_dashboard():
    try:
        from src.api.Service.DashboardService import DashboardService
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_rendimiento_semanal()
        return response_success(resultado, "Rendimiento semanal obtenido exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_rendimiento_semanal_dashboard: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/metricas-asistencia', methods=['GET'])
@token_required
def get_metricas_asistencia_dashboard():
    try:
        from src.api.Service.DashboardService import DashboardService
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_metricas_asistencia()
        return response_success(resultado, "Metricas de asistencia obtenidas exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_metricas_asistencia_dashboard: {str(e)}")
        return response_error("Error interno del servidor", 500)


# ============================================
# DASHBOARD POR ROL
# ============================================
@dashboard_bp.route('/dashboard/mis-sesiones-hoy', methods=['GET'])
@token_required
def get_mis_sesiones_hoy():
    try:
        from src.api.Service.DashboardService import DashboardService
        if not hasattr(request, 'current_user') or not request.current_user.get('personal_id'):
            return response_error("Solo personal autorizado puede acceder", 403)
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_mis_sesiones_hoy(request.current_user.get('personal_id'))
        return response_success(resultado, "Mis sesiones de hoy obtenidas exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_mis_sesiones_hoy: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/mis-clases-hoy', methods=['GET'])
@token_required
def get_mis_clases_hoy():
    try:
        from src.api.Service.DashboardService import DashboardService
        if not hasattr(request, 'current_user') or not request.current_user.get('personal_id'):
            return response_error("Solo personal autorizado puede acceder", 403)
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_mis_clases_hoy(request.current_user.get('personal_id'))
        return response_success(resultado, "Mis clases de hoy obtenidas exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_mis_clases_hoy: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/mis-pacientes', methods=['GET'])
@token_required
def get_mis_pacientes():
    try:
        from src.api.Service.DashboardService import DashboardService
        if not hasattr(request, 'current_user') or not request.current_user.get('personal_id'):
            return response_error("Solo personal autorizado puede acceder", 403)
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_mis_pacientes(request.current_user.get('personal_id'))
        return response_success(resultado, "Mis pacientes obtenidos exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_mis_pacientes: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/mis-estudiantes', methods=['GET'])
@token_required
def get_mis_estudiantes():
    try:
        from src.api.Service.DashboardService import DashboardService
        if not hasattr(request, 'current_user') or not request.current_user.get('personal_id'):
            return response_error("Solo personal autorizado puede acceder", 403)
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_mis_estudiantes(request.current_user.get('personal_id'))
        return response_success(resultado, "Mis estudiantes obtenidos exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_mis_estudiantes: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/admin', methods=['GET'])
@admin_required
def get_dashboard_admin():
    try:
        from src.api.Service.DashboardService import DashboardService
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_dashboard_admin()
        return response_success(resultado, "Dashboard admin obtenido exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_dashboard_admin: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/therapist', methods=['GET'])
@token_required
def get_dashboard_therapist():
    try:
        from src.api.Service.DashboardService import DashboardService
        if not hasattr(request, 'current_user') or not request.current_user.get('personal_id'):
            return response_error("Solo terapeutas pueden acceder", 403)
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_dashboard_therapist(request.current_user.get('personal_id'))
        return response_success(resultado, "Dashboard terapeuta obtenido exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_dashboard_therapist: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/dashboard/pedagogue', methods=['GET'])
@token_required
def get_dashboard_pedagogue():
    try:
        from src.api.Service.DashboardService import DashboardService
        if not hasattr(request, 'current_user') or not request.current_user.get('personal_id'):
            return response_error("Solo pedagogos pueden acceder", 403)
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_dashboard_pedagogue(request.current_user.get('personal_id'))
        return response_success(resultado, "Dashboard pedagogo obtenido exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_dashboard_pedagogue: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/stats/general', methods=['GET'])
@token_required
def get_stats_general():
    try:
        from src.api.Service.DashboardService import DashboardService
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_stats_general()
        return response_success(resultado, "Estadisticas generales obtenidas exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_stats_general: {str(e)}")
        return response_error("Error interno del servidor", 500)


@dashboard_bp.route('/agenda/personal', methods=['GET'])
@token_required
def get_agenda_personal():
    try:
        from src.api.Service.DashboardService import DashboardService
        if not hasattr(request, 'current_user') or not request.current_user.get('personal_id'):
            return response_error("Solo personal puede acceder", 403)
        fecha = request.args.get('fecha')
        dashboard_service = DashboardService()
        resultado = dashboard_service.get_agenda_personal(request.current_user.get('personal_id'), fecha)
        return response_success(resultado, "Agenda personal obtenida exitosamente")
    except Exception as e:
        HandleLogs.write_error(f"Error en get_agenda_personal: {str(e)}")
        return response_error("Error interno del servidor", 500)
