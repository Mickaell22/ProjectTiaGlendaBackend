# src/api/Service/ReportesService.py
from src.api.Components.ReportesComponent import ReportesComponent
from src.utils.general.logs import HandleLogs
from datetime import datetime, date
import logging

class ReportesService:

    @staticmethod
    def get_reporte_asistencia_paciente(filtros, usuario_autenticado):
        """
        Obtener reporte de asistencia por paciente
        """
        try:
            filtros_validados = ReportesService._validar_filtros_comunes(filtros)
            if not filtros_validados['success']:
                return filtros_validados

            # Si no es admin, limitar a los pacientes del terapeuta
            if usuario_autenticado.get('rol') != 'Administrador':
                personal_id = usuario_autenticado.get('personal_id')
                if not personal_id:
                    return {'success': False, 'message': 'Solo personal autorizado puede generar reportes'}
                filtros_validados['data']['id_terapeuta'] = personal_id

            reporte_component = ReportesComponent()
            resultado = reporte_component.get_reporte_asistencia_paciente(**filtros_validados['data'])

            if resultado['success']:
                return {
                    'success': True,
                    'data': resultado['data'],
                    'metadata': {
                        'tipo_reporte': 'asistencia_paciente',
                        'total_registros': resultado['total_registros'],
                        'filtros_aplicados': ReportesService._serializar_filtros(filtros_validados['data']),
                        'fecha_generacion': datetime.now().isoformat(),
                        'generado_por': usuario_autenticado.get('usuario', 'Sistema')
                    }
                }
            else:
                return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en ReportesService.get_reporte_asistencia_paciente: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def get_reporte_progreso_terapeutico(filtros, usuario_autenticado):
        """
        Obtener reporte de progreso terapeutico
        """
        try:
            filtros_validados = ReportesService._validar_filtros_comunes(filtros)
            if not filtros_validados['success']:
                return filtros_validados

            # Si no es admin, limitar a los pacientes del terapeuta
            if usuario_autenticado.get('rol') != 'Administrador':
                personal_id = usuario_autenticado.get('personal_id')
                if not personal_id:
                    return {'success': False, 'message': 'Solo personal autorizado puede generar reportes'}
                filtros_validados['data']['id_terapeuta'] = personal_id

            reporte_component = ReportesComponent()
            resultado = reporte_component.get_reporte_progreso_terapeutico(**filtros_validados['data'])

            if resultado['success']:
                return {
                    'success': True,
                    'data': resultado['data'],
                    'metadata': {
                        'tipo_reporte': 'progreso_terapeutico',
                        'total_registros': resultado['total_registros'],
                        'filtros_aplicados': ReportesService._serializar_filtros(filtros_validados['data']),
                        'fecha_generacion': datetime.now().isoformat(),
                        'generado_por': usuario_autenticado.get('usuario', 'Sistema')
                    }
                }
            else:
                return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en ReportesService.get_reporte_progreso_terapeutico: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def get_reporte_carga_trabajo_personal(filtros, usuario_autenticado):
        """
        Obtener reporte de carga de trabajo del personal
        """
        try:
            # Solo administradores pueden ver carga de trabajo general
            if usuario_autenticado.get('rol') != 'Administrador':
                return {'success': False, 'message': 'Solo administradores pueden acceder a este reporte'}

            filtros_validados = ReportesService._validar_filtros_fechas(filtros)
            if not filtros_validados['success']:
                return filtros_validados

            # Agregar filtro de especialidad si existe
            if 'id_especialidad' in filtros and filtros['id_especialidad']:
                try:
                    id_esp = int(filtros['id_especialidad'])
                    if id_esp > 0:
                        filtros_validados['data']['id_especialidad'] = id_esp
                except (ValueError, TypeError):
                    pass

            reporte_component = ReportesComponent()
            resultado = reporte_component.get_reporte_carga_trabajo_personal(**filtros_validados['data'])

            if resultado['success']:
                return {
                    'success': True,
                    'data': resultado['data'],
                    'metadata': {
                        'tipo_reporte': 'carga_trabajo_personal',
                        'total_registros': resultado['total_registros'],
                        'filtros_aplicados': ReportesService._serializar_filtros(filtros_validados['data']),
                        'fecha_generacion': datetime.now().isoformat(),
                        'generado_por': usuario_autenticado.get('usuario', 'Sistema')
                    }
                }
            else:
                return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en ReportesService.get_reporte_carga_trabajo_personal: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def get_reporte_academico_estudiante(filtros, usuario_autenticado):
        """
        Obtener reporte academico por estudiante
        """
        try:
            filtros_validados = ReportesService._validar_filtros_academicos(filtros)
            if not filtros_validados['success']:
                return filtros_validados

            # Si no es admin, limitar a los estudiantes del pedagogo
            if usuario_autenticado.get('rol') != 'Administrador':
                personal_id = usuario_autenticado.get('personal_id')
                if not personal_id:
                    return {'success': False, 'message': 'Solo personal autorizado puede generar reportes'}
                filtros_validados['data']['id_educador'] = personal_id

            reporte_component = ReportesComponent()
            resultado = reporte_component.get_reporte_academico_estudiante(**filtros_validados['data'])

            if resultado['success']:
                return {
                    'success': True,
                    'data': resultado['data'],
                    'metadata': {
                        'tipo_reporte': 'academico_estudiante',
                        'total_registros': resultado['total_registros'],
                        'filtros_aplicados': ReportesService._serializar_filtros(filtros_validados['data']),
                        'fecha_generacion': datetime.now().isoformat(),
                        'generado_por': usuario_autenticado.get('usuario', 'Sistema')
                    }
                }
            else:
                return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en ReportesService.get_reporte_academico_estudiante: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def get_reporte_rendimiento_clase(filtros, usuario_autenticado):
        """
        Obtener reporte de rendimiento por clase
        """
        try:
            filtros_validados = ReportesService._validar_filtros_fechas(filtros)
            if not filtros_validados['success']:
                return filtros_validados

            # Agregar filtros adicionales
            if 'id_sesion' in filtros and filtros['id_sesion']:
                try:
                    id_ses = int(filtros['id_sesion'])
                    if id_ses > 0:
                        filtros_validados['data']['id_sesion'] = id_ses
                except (ValueError, TypeError):
                    pass

            if 'id_especialidad' in filtros and filtros['id_especialidad']:
                try:
                    id_esp = int(filtros['id_especialidad'])
                    if id_esp > 0:
                        filtros_validados['data']['id_especialidad'] = id_esp
                except (ValueError, TypeError):
                    pass

            reporte_component = ReportesComponent()
            resultado = reporte_component.get_reporte_rendimiento_clase(**filtros_validados['data'])

            if resultado['success']:
                return {
                    'success': True,
                    'data': resultado['data'],
                    'metadata': {
                        'tipo_reporte': 'rendimiento_clase',
                        'total_registros': resultado['total_registros'],
                        'filtros_aplicados': ReportesService._serializar_filtros(filtros_validados['data']),
                        'fecha_generacion': datetime.now().isoformat(),
                        'generado_por': usuario_autenticado.get('usuario', 'Sistema')
                    }
                }
            else:
                return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en ReportesService.get_reporte_rendimiento_clase: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def get_reporte_utilizacion_recursos(filtros, usuario_autenticado):
        """
        Obtener reporte de utilizacion de recursos
        """
        try:
            # Solo administradores pueden ver utilizacion de recursos
            if usuario_autenticado.get('rol') != 'Administrador':
                return {'success': False, 'message': 'Solo administradores pueden acceder a este reporte'}

            filtros_validados = ReportesService._validar_filtros_fechas(filtros)
            if not filtros_validados['success']:
                return filtros_validados

            reporte_component = ReportesComponent()
            resultado = reporte_component.get_reporte_utilizacion_recursos(**filtros_validados['data'])

            if resultado['success']:
                return {
                    'success': True,
                    'data': resultado['data'],
                    'metadata': {
                        'tipo_reporte': 'utilizacion_recursos',
                        'total_registros': resultado['total_registros'],
                        'filtros_aplicados': ReportesService._serializar_filtros(filtros_validados['data']),
                        'fecha_generacion': datetime.now().isoformat(),
                        'generado_por': usuario_autenticado.get('usuario', 'Sistema')
                    }
                }
            else:
                return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en ReportesService.get_reporte_utilizacion_recursos: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def get_estadisticas_generales_reportes(filtros, usuario_autenticado):
        """
        Obtener estadisticas generales para reportes administrativos
        """
        try:
            # Solo administradores pueden ver estadisticas generales
            if usuario_autenticado.get('rol') != 'Administrador':
                return {'success': False, 'message': 'Solo administradores pueden acceder a este reporte'}

            filtros_validados = ReportesService._validar_filtros_fechas(filtros)
            if not filtros_validados['success']:
                return filtros_validados

            reporte_component = ReportesComponent()
            resultado = reporte_component.get_estadisticas_generales_reportes(**filtros_validados['data'])

            if resultado['success']:
                return {
                    'success': True,
                    'data': resultado['data'],
                    'metadata': {
                        'tipo_reporte': 'estadisticas_generales',
                        'total_registros': resultado['total_registros'],
                        'filtros_aplicados': ReportesService._serializar_filtros(filtros_validados['data']),
                        'fecha_generacion': datetime.now().isoformat(),
                        'generado_por': usuario_autenticado.get('usuario', 'Sistema')
                    }
                }
            else:
                return resultado

        except Exception as e:
            HandleLogs.write_error(f"Error en ReportesService.get_estadisticas_generales_reportes: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    @staticmethod
    def get_lista_reportes_disponibles(usuario_autenticado):
        """
        Obtener lista de reportes disponibles segun el rol del usuario
        """
        try:
            reportes_admin = [
                {
                    'id': 'asistencia_paciente',
                    'nombre': 'Reporte de Asistencia por Paciente',
                    'descripcion': 'Analisis detallado de asistencia de pacientes a sesiones terapeuticas',
                    'categoria': 'Terapeutico',
                    'requiere_filtros': ['fecha_inicio', 'fecha_fin'],
                    'filtros_opcionales': ['id_paciente', 'id_terapeuta']
                },
                {
                    'id': 'progreso_terapeutico',
                    'nombre': 'Reporte de Progreso Terapeutico',
                    'descripcion': 'Evaluacion del progreso de pacientes en tratamiento',
                    'categoria': 'Terapeutico',
                    'requiere_filtros': [],
                    'filtros_opcionales': ['id_paciente', 'id_terapeuta', 'fecha_inicio', 'fecha_fin']
                },
                {
                    'id': 'carga_trabajo_personal',
                    'nombre': 'Reporte de Carga de Trabajo del Personal',
                    'descripcion': 'Analisis de carga laboral y productividad del personal terapeutico',
                    'categoria': 'Administrativo',
                    'requiere_filtros': [],
                    'filtros_opcionales': ['fecha_inicio', 'fecha_fin', 'id_especialidad']
                },
                {
                    'id': 'academico_estudiante',
                    'nombre': 'Reporte Academico por Estudiante',
                    'descripcion': 'Rendimiento academico y asistencia de estudiantes',
                    'categoria': 'Pedagogico',
                    'requiere_filtros': [],
                    'filtros_opcionales': ['id_estudiante', 'id_educador', 'fecha_inicio', 'fecha_fin']
                },
                {
                    'id': 'rendimiento_clase',
                    'nombre': 'Reporte de Rendimiento por Clase',
                    'descripcion': 'Analisis de efectividad y rendimiento de clases pedagogicas',
                    'categoria': 'Pedagogico',
                    'requiere_filtros': [],
                    'filtros_opcionales': ['id_sesion', 'id_especialidad', 'fecha_inicio', 'fecha_fin']
                },
                {
                    'id': 'utilizacion_recursos',
                    'nombre': 'Reporte de Utilizacion de Recursos',
                    'descripcion': 'Uso y eficiencia por especialidad',
                    'categoria': 'Administrativo',
                    'requiere_filtros': [],
                    'filtros_opcionales': ['fecha_inicio', 'fecha_fin']
                },
                {
                    'id': 'estadisticas_generales',
                    'nombre': 'Estadisticas Generales del Centro',
                    'descripcion': 'Resumen ejecutivo de indicadores clave',
                    'categoria': 'Administrativo',
                    'requiere_filtros': [],
                    'filtros_opcionales': ['fecha_inicio', 'fecha_fin']
                }
            ]

            reportes_personal = [
                {
                    'id': 'asistencia_paciente',
                    'nombre': 'Mis Pacientes - Reporte de Asistencia',
                    'descripcion': 'Asistencia de mis pacientes asignados',
                    'categoria': 'Terapeutico',
                    'requiere_filtros': [],
                    'filtros_opcionales': ['id_paciente', 'fecha_inicio', 'fecha_fin']
                },
                {
                    'id': 'progreso_terapeutico',
                    'nombre': 'Mis Pacientes - Progreso Terapeutico',
                    'descripcion': 'Progreso de mis pacientes en tratamiento',
                    'categoria': 'Terapeutico',
                    'requiere_filtros': [],
                    'filtros_opcionales': ['id_paciente', 'fecha_inicio', 'fecha_fin']
                },
                {
                    'id': 'academico_estudiante',
                    'nombre': 'Mis Estudiantes - Reporte Academico',
                    'descripcion': 'Rendimiento de estudiantes en mis clases',
                    'categoria': 'Pedagogico',
                    'requiere_filtros': [],
                    'filtros_opcionales': ['id_estudiante', 'fecha_inicio', 'fecha_fin']
                }
            ]

            if usuario_autenticado.get('rol') == 'Administrador':
                reportes_disponibles = reportes_admin
            else:
                reportes_disponibles = reportes_personal

            return {
                'success': True,
                'data': reportes_disponibles,
                'total_reportes': len(reportes_disponibles)
            }

        except Exception as e:
            HandleLogs.write_error(f"Error en ReportesService.get_lista_reportes_disponibles: {str(e)}")
            return {'success': False, 'message': 'Error interno del servidor'}

    # ============================================
    # METODOS AUXILIARES PRIVADOS
    # ============================================

    @staticmethod
    def _validar_filtros_comunes(filtros):
        """Validar filtros comunes para reportes terapeuticos"""
        try:
            filtros_validados = {}

            # Validar ID de paciente
            if 'id_paciente' in filtros and filtros['id_paciente']:
                try:
                    id_paciente = int(filtros['id_paciente'])
                    if id_paciente > 0:
                        filtros_validados['id_paciente'] = id_paciente
                    else:
                        return {'success': False, 'message': 'ID de paciente debe ser mayor a 0'}
                except (ValueError, TypeError):
                    return {'success': False, 'message': 'ID de paciente invalido'}

            # Validar ID de terapeuta
            if 'id_terapeuta' in filtros and filtros['id_terapeuta']:
                try:
                    id_terapeuta = int(filtros['id_terapeuta'])
                    if id_terapeuta > 0:
                        filtros_validados['id_terapeuta'] = id_terapeuta
                    else:
                        return {'success': False, 'message': 'ID de terapeuta debe ser mayor a 0'}
                except (ValueError, TypeError):
                    return {'success': False, 'message': 'ID de terapeuta invalido'}

            # Validar fechas
            filtros_fechas = ReportesService._validar_filtros_fechas(filtros)
            if filtros_fechas['success']:
                filtros_validados.update(filtros_fechas['data'])
            else:
                return filtros_fechas

            return {'success': True, 'data': filtros_validados}

        except Exception as e:
            return {'success': False, 'message': f'Error validando filtros: {str(e)}'}

    @staticmethod
    def _validar_filtros_academicos(filtros):
        """Validar filtros para reportes academicos/pedagogicos"""
        try:
            filtros_validados = {}

            # Validar ID de estudiante (mapeado desde id_estudiante o id_paciente)
            id_estudiante_raw = filtros.get('id_estudiante') or filtros.get('id_paciente')
            if id_estudiante_raw:
                try:
                    id_estudiante = int(id_estudiante_raw)
                    if id_estudiante > 0:
                        filtros_validados['id_estudiante'] = id_estudiante
                    else:
                        return {'success': False, 'message': 'ID de estudiante debe ser mayor a 0'}
                except (ValueError, TypeError):
                    return {'success': False, 'message': 'ID de estudiante invalido'}

            # Validar ID de educador
            id_educador_raw = filtros.get('id_educador') or filtros.get('id_terapeuta')
            if id_educador_raw:
                try:
                    id_educador = int(id_educador_raw)
                    if id_educador > 0:
                        filtros_validados['id_educador'] = id_educador
                    else:
                        return {'success': False, 'message': 'ID de educador debe ser mayor a 0'}
                except (ValueError, TypeError):
                    return {'success': False, 'message': 'ID de educador invalido'}

            # Validar fechas
            filtros_fechas = ReportesService._validar_filtros_fechas(filtros)
            if filtros_fechas['success']:
                filtros_validados.update(filtros_fechas['data'])
            else:
                return filtros_fechas

            return {'success': True, 'data': filtros_validados}

        except Exception as e:
            return {'success': False, 'message': f'Error validando filtros: {str(e)}'}

    @staticmethod
    def _validar_filtros_fechas(filtros):
        """Validar filtros de fechas"""
        try:
            filtros_validados = {}

            if 'fecha_inicio' in filtros and filtros['fecha_inicio']:
                try:
                    if isinstance(filtros['fecha_inicio'], str):
                        fecha_inicio = datetime.strptime(filtros['fecha_inicio'], '%Y-%m-%d').date()
                    elif isinstance(filtros['fecha_inicio'], date):
                        fecha_inicio = filtros['fecha_inicio']
                    else:
                        return {'success': False, 'message': 'Formato de fecha de inicio invalido'}
                    filtros_validados['fecha_inicio'] = fecha_inicio
                except ValueError:
                    return {'success': False, 'message': 'Formato de fecha de inicio invalido (use YYYY-MM-DD)'}

            if 'fecha_fin' in filtros and filtros['fecha_fin']:
                try:
                    if isinstance(filtros['fecha_fin'], str):
                        fecha_fin = datetime.strptime(filtros['fecha_fin'], '%Y-%m-%d').date()
                    elif isinstance(filtros['fecha_fin'], date):
                        fecha_fin = filtros['fecha_fin']
                    else:
                        return {'success': False, 'message': 'Formato de fecha de fin invalido'}
                    filtros_validados['fecha_fin'] = fecha_fin
                except ValueError:
                    return {'success': False, 'message': 'Formato de fecha de fin invalido (use YYYY-MM-DD)'}

            if 'fecha_inicio' in filtros_validados and 'fecha_fin' in filtros_validados:
                if filtros_validados['fecha_inicio'] > filtros_validados['fecha_fin']:
                    return {'success': False, 'message': 'La fecha de inicio no puede ser mayor a la fecha de fin'}

            return {'success': True, 'data': filtros_validados}

        except Exception as e:
            return {'success': False, 'message': f'Error validando fechas: {str(e)}'}

    @staticmethod
    def _serializar_filtros(filtros):
        """Convierte filtros a formato serializable para JSON"""
        resultado = {}
        for key, value in filtros.items():
            if isinstance(value, date):
                resultado[key] = value.isoformat()
            else:
                resultado[key] = value
        return resultado
