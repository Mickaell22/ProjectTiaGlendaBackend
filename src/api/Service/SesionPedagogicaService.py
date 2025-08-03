# src/api/Service/SesionPedagogicaService.py

from flask import request, jsonify
from src.api.Components.SesionPedagogicaComponent import SesionPedagogicaComponent
from src.utils.general.response import response_success, response_error
from src.utils.general.logs import HandleLogs
from datetime import datetime, date, time, timedelta
import re


class SesionPedagogicaService:
    """Service para lógica de negocio de sesiones pedagógicas"""

    @staticmethod
    def get_sesiones():
        """Obtener todas las sesiones pedagógicas"""
        try:
            HandleLogs.write_log("SesionPedagogicaService.get_sesiones - Iniciando")

            sesiones = SesionPedagogicaComponent.get_sesiones()

            if sesiones:
                # Formatear datos para respuesta
                sesiones_formateadas = []
                for sesion in sesiones:
                    sesion_data = {
                        'id': sesion['id'],
                        'codigo_sesion': sesion['codigo_sesion'],
                        'titulo': sesion['titulo'],
                        'pedagogo': {
                            'id': sesion['pedagogo_id'],
                            'nombre': sesion['pedagogo_nombre']
                        },
                        'especialidad': {
                            'id': sesion['especialidad_id'],
                            'nombre': sesion['especialidad_nombre'],
                            'area': sesion['especialidad_area']
                        },
                        'fecha_inicio': sesion['fecha_inicio'].isoformat() if sesion['fecha_inicio'] else None,
                        'fecha_fin': sesion['fecha_fin'].isoformat() if sesion['fecha_fin'] else None,
                        'dias_semana': sesion['dias_semana'].split(',') if sesion['dias_semana'] else [],
                        'hora_inicio': str(sesion['hora_inicio']) if sesion['hora_inicio'] else None,
                        'duracion_minutos': sesion['duracion_minutos'],
                        'numero_clases_programadas': sesion['numero_clases_programadas'],
                        'nivel_academico': sesion['nivel_academico'],
                        'capacidad_maxima': sesion['capacidad_maxima'],
                        'modalidad': sesion['modalidad'],
                        'costo_total': float(sesion['costo_total']),
                        'costo_por_clase': float(sesion['costo_por_clase']),
                        'periodo_academico': sesion['periodo_academico'],
                        'estado': sesion['estado'],
                        'observaciones': sesion['observaciones'],
                        'estadisticas': {
                            'total_estudiantes': sesion['total_estudiantes'],
                            'clases_programadas': sesion['clases_programadas'],
                            'clases_realizadas': sesion['clases_realizadas'],
                            'progreso_porcentaje': round(
                                (sesion['clases_realizadas'] / sesion['clases_programadas'] * 100), 2) if sesion[
                                                                                                                  'clases_programadas'] > 0 else 0,
                            'promedio_notas': float(sesion['promedio_notas']) if sesion['promedio_notas'] else None,
                            'promedio_asistencia': float(sesion['promedio_asistencia']) if sesion['promedio_asistencia'] else None
                        },
                        'fecha_creacion': sesion['fecha_creacion'].isoformat() if sesion['fecha_creacion'] else None
                    }
                    sesiones_formateadas.append(sesion_data)

                HandleLogs.write_log("SesionPedagogicaService.get_sesiones - Sesiones obtenidas exitosamente")
                return response_success(sesiones_formateadas, "Sesiones pedagógicas obtenidas exitosamente")
            else:
                return response_success([], "No hay sesiones pedagógicas registradas")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.get_sesiones - Error: {str(e)}")
            return response_error(f"Error al obtener sesiones pedagógicas: {str(e)}", 500)

    @staticmethod
    def get_sesion(sesion_id):
        """Obtener una sesión pedagógica específica por ID"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.get_sesion - ID: {sesion_id}")

            # Validar ID
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            sesion = SesionPedagogicaComponent.get_sesion_by_id(sesion_id)

            if sesion:
                # Formatear respuesta
                sesion_data = {
                    'id': sesion['id'],
                    'codigo_sesion': sesion['codigo_sesion'],
                    'titulo': sesion['titulo'],
                    'pedagogo': {
                        'id': sesion['pedagogo_id'],
                        'nombre': sesion['pedagogo_nombre']
                    },
                    'especialidad': {
                        'id': sesion['especialidad_id'],
                        'nombre': sesion['especialidad_nombre'],
                        'area': sesion['especialidad_area']
                    },
                    'fecha_inicio': sesion['fecha_inicio'].isoformat() if sesion['fecha_inicio'] else None,
                    'fecha_fin': sesion['fecha_fin'].isoformat() if sesion['fecha_fin'] else None,
                    'dias_semana': sesion['dias_semana'].split(',') if sesion['dias_semana'] else [],
                    'hora_inicio': str(sesion['hora_inicio']) if sesion['hora_inicio'] else None,
                    'duracion_minutos': sesion['duracion_minutos'],
                    'numero_clases_programadas': sesion['numero_clases_programadas'],
                    'nivel_academico': sesion['nivel_academico'],
                    'capacidad_maxima': sesion['capacidad_maxima'],
                    'modalidad': sesion['modalidad'],
                    'costo_total': float(sesion['costo_total']),
                    'costo_por_clase': float(sesion['costo_por_clase']),
                    'periodo_academico': sesion['periodo_academico'],
                    'estado': sesion['estado'],
                    'observaciones': sesion['observaciones'],
                    'fecha_creacion': sesion['fecha_creacion'].isoformat() if sesion['fecha_creacion'] else None,
                    'fecha_modificacion': sesion['fecha_modificacion'].isoformat() if sesion['fecha_modificacion'] else None
                }

                HandleLogs.write_log(f"SesionPedagogicaService.get_sesion - Sesión {sesion_id} encontrada")
                return response_success(sesion_data, "Sesión pedagógica obtenida exitosamente")
            else:
                return response_error(f"Sesión pedagógica con ID {sesion_id} no encontrada", 404)

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.get_sesion - Error: {str(e)}")
            return response_error(f"Error al obtener sesión pedagógica: {str(e)}", 500)

    @staticmethod
    def create_sesion():
        """Crear nueva sesión pedagógica"""
        try:
            HandleLogs.write_log("SesionPedagogicaService.create_sesion - Iniciando")

            data = request.get_json()
            if not data:
                return response_error("No se enviaron datos", 400)

            # Validaciones requeridas
            required_fields = ['titulo', 'pedagogo_id', 'especialidad_id', 'fecha_inicio', 
                             'dias_semana', 'hora_inicio', 'numero_clases_programadas', 'costo_total']
            
            for field in required_fields:
                if field not in data or not data[field]:
                    return response_error(f"El campo '{field}' es requerido", 400)

            # Validaciones específicas
            try:
                data['fecha_inicio'] = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
                if data.get('fecha_fin'):
                    data['fecha_fin'] = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
                    if data['fecha_fin'] <= data['fecha_inicio']:
                        return response_error("La fecha de fin debe ser posterior a la fecha de inicio", 400)
                
                data['hora_inicio'] = datetime.strptime(data['hora_inicio'], '%H:%M').time()
            except ValueError as e:
                return response_error(f"Formato de fecha/hora inválido: {str(e)}", 400)

            # Validar números
            if data['numero_clases_programadas'] <= 0:
                return response_error("El número de clases programadas debe ser mayor a 0", 400)
            
            if data['costo_total'] < 0:
                return response_error("El costo total no puede ser negativo", 400)

            # Validar días de la semana
            dias_validos = ['lunes', 'martes', 'miercoles', 'miércoles', 'jueves', 'viernes', 'sabado', 'sábado', 'domingo']
            dias_sesion = [dia.strip().lower() for dia in data['dias_semana'].split(',')]
            
            for dia in dias_sesion:
                if dia not in dias_validos:
                    return response_error(f"Día de la semana inválido: {dia}", 400)

            # Agregar usuario actual
            data['usuario_creacion'] = request.current_user['id']

            # Crear sesión
            result = SesionPedagogicaComponent.create_sesion(data)

            if result:
                HandleLogs.write_log(f"SesionPedagogicaService.create_sesion - Sesión creada: {result['id']}")
                return response_success({
                    'id': result['id'],
                    'codigo_sesion': result['codigo_sesion']
                }, "Sesión pedagógica creada exitosamente")
            else:
                return response_error("No se pudo crear la sesión pedagógica", 500)

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.create_sesion - Error: {str(e)}")
            return response_error(f"Error al crear sesión pedagógica: {str(e)}", 500)

    @staticmethod
    def update_sesion(sesion_id):
        """Actualizar sesión pedagógica"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.update_sesion - ID: {sesion_id}")

            # Validar ID
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            data = request.get_json()
            if not data:
                return response_error("No se enviaron datos", 400)

            # Verificar que la sesión existe
            sesion_existente = SesionPedagogicaComponent.get_sesion_by_id(sesion_id)
            if not sesion_existente:
                return response_error(f"Sesión pedagógica con ID {sesion_id} no encontrada", 404)

            # Validaciones de fechas si se proporcionan
            if 'fecha_inicio' in data:
                try:
                    data['fecha_inicio'] = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
                except ValueError:
                    return response_error("Formato de fecha de inicio inválido (YYYY-MM-DD)", 400)

            if 'fecha_fin' in data:
                try:
                    data['fecha_fin'] = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
                except ValueError:
                    return response_error("Formato de fecha de fin inválido (YYYY-MM-DD)", 400)

            if 'hora_inicio' in data:
                try:
                    data['hora_inicio'] = datetime.strptime(data['hora_inicio'], '%H:%M').time()
                except ValueError:
                    return response_error("Formato de hora inválido (HH:MM)", 400)

            # Validaciones numéricas
            if 'numero_clases_programadas' in data and data['numero_clases_programadas'] <= 0:
                return response_error("El número de clases programadas debe ser mayor a 0", 400)
            
            if 'costo_total' in data and data['costo_total'] < 0:
                return response_error("El costo total no puede ser negativo", 400)

            # Validar días de la semana si se proporcionan
            if 'dias_semana' in data:
                dias_validos = ['lunes', 'martes', 'miercoles', 'miércoles', 'jueves', 'viernes', 'sabado', 'sábado', 'domingo']
                dias_sesion = [dia.strip().lower() for dia in data['dias_semana'].split(',')]
                
                for dia in dias_sesion:
                    if dia not in dias_validos:
                        return response_error(f"Día de la semana inválido: {dia}", 400)

            # Agregar usuario de modificación
            data['usuario_modificacion'] = request.current_user['id']

            # Merge partial data with existing session data
            update_data = {
                'titulo': data.get('titulo', sesion_existente['titulo']),
                'pedagogo_id': data.get('pedagogo_id', sesion_existente['pedagogo_id']),
                'especialidad_id': data.get('especialidad_id', sesion_existente['especialidad_id']),
                'fecha_inicio': data.get('fecha_inicio', sesion_existente['fecha_inicio']),
                'fecha_fin': data.get('fecha_fin', sesion_existente['fecha_fin']),
                'dias_semana': data.get('dias_semana', sesion_existente['dias_semana']),
                'hora_inicio': data.get('hora_inicio', sesion_existente['hora_inicio']),
                'duracion_minutos': data.get('duracion_minutos', sesion_existente['duracion_minutos']),
                'numero_clases_programadas': data.get('numero_clases_programadas', sesion_existente['numero_clases_programadas']),
                'nivel_academico': data.get('nivel_academico', sesion_existente['nivel_academico']),
                'capacidad_maxima': data.get('capacidad_maxima', sesion_existente['capacidad_maxima']),
                'modalidad': data.get('modalidad', sesion_existente['modalidad']),
                'costo_total': data.get('costo_total', sesion_existente['costo_total']),
                'periodo_academico': data.get('periodo_academico', sesion_existente['periodo_academico']),
                'estado': data.get('estado', sesion_existente['estado']),
                'observaciones': data.get('observaciones', sesion_existente['observaciones']),
                'usuario_modificacion': data['usuario_modificacion']
            }

            # Actualizar sesión
            SesionPedagogicaComponent.update_sesion(sesion_id, update_data)

            HandleLogs.write_log(f"SesionPedagogicaService.update_sesion - Sesión {sesion_id} actualizada")
            return response_success({'sesion_id': sesion_id}, "Sesión pedagógica actualizada exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.update_sesion - Error: {str(e)}")
            return response_error(f"Error al actualizar sesión pedagógica: {str(e)}", 500)

    @staticmethod
    def delete_sesion(sesion_id):
        """Cancelar sesión pedagógica"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.delete_sesion - ID: {sesion_id}")

            # Validar ID
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            # Verificar que la sesión existe
            sesion_existente = SesionPedagogicaComponent.get_sesion_by_id(sesion_id)
            if not sesion_existente:
                return response_error(f"Sesión pedagógica con ID {sesion_id} no encontrada", 404)

            # Cancelar sesión
            SesionPedagogicaComponent.delete_sesion(sesion_id)

            HandleLogs.write_log(f"SesionPedagogicaService.delete_sesion - Sesión {sesion_id} cancelada")
            return response_success({'sesion_id': sesion_id}, "Sesión pedagógica cancelada exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.delete_sesion - Error: {str(e)}")
            return response_error(f"Error al cancelar sesión pedagógica: {str(e)}", 500)

    @staticmethod
    def get_estudiantes_sesion(sesion_id):
        """Obtener estudiantes de una sesión pedagógica"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.get_estudiantes_sesion - Sesión: {sesion_id}")

            estudiantes = SesionPedagogicaComponent.get_estudiantes_sesion(sesion_id)

            if estudiantes:
                # Formatear datos
                estudiantes_formateados = []
                for estudiante in estudiantes:
                    estudiante_data = {
                        'id': estudiante['id'],
                        'estudiante': {
                            'id': estudiante['paciente_id'],
                            'nombre': estudiante['estudiante_nombre'],
                            'cedula': estudiante['estudiante_cedula']
                        },
                        'tutor': {
                            'nombre': estudiante['tutor_nombre'],
                            'telefono': estudiante['tutor_telefono']
                        },
                        'fecha_incorporacion': estudiante['fecha_incorporacion'].isoformat() if estudiante['fecha_incorporacion'] else None,
                        'costo_estudiante': float(estudiante['costo_estudiante']) if estudiante['costo_estudiante'] else None,
                        'observaciones_estudiante': estudiante['observaciones_estudiante'],
                        'estado': estudiante['estado'],
                        'nota_final': float(estudiante['nota_final']) if estudiante['nota_final'] else None,
                        'asistencia_porcentaje': float(estudiante['asistencia_porcentaje']) if estudiante['asistencia_porcentaje'] else None
                    }
                    estudiantes_formateados.append(estudiante_data)

                return response_success(estudiantes_formateados, "Estudiantes obtenidos exitosamente")
            else:
                return response_success([], "No hay estudiantes en esta sesión pedagógica")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.get_estudiantes_sesion - Error: {str(e)}")
            return response_error(f"Error al obtener estudiantes: {str(e)}", 500)

    @staticmethod
    def add_estudiante_to_sesion(sesion_id):
        """Agregar estudiante a una sesión pedagógica"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.add_estudiante_to_sesion - Sesión: {sesion_id}")

            data = request.get_json()
            if not data or 'paciente_id' not in data:
                return response_error("Se requiere paciente_id", 400)

            # Agregar usuario actual
            data['usuario_creacion'] = request.current_user['id']

            # Agregar estudiante
            estudiante_id = SesionPedagogicaComponent.add_estudiante_to_sesion(sesion_id, data)

            HandleLogs.write_log(f"SesionPedagogicaService.add_estudiante_to_sesion - Estudiante agregado: {estudiante_id}")
            return response_success({
                'estudiante_id': estudiante_id,
                'sesion_id': sesion_id
            }, "Estudiante agregado a la sesión pedagógica exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.add_estudiante_to_sesion - Error: {str(e)}")
            return response_error(f"Error al agregar estudiante: {str(e)}", 500)

    @staticmethod
    def remove_estudiante_from_sesion(sesion_id, paciente_id):
        """Remover estudiante de una sesión pedagógica"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.remove_estudiante_from_sesion - Sesión: {sesion_id}, Paciente: {paciente_id}")

            # Remover estudiante
            SesionPedagogicaComponent.remove_estudiante_from_sesion(sesion_id, paciente_id)

            HandleLogs.write_log(f"SesionPedagogicaService.remove_estudiante_from_sesion - Estudiante removido")
            return response_success({
                'sesion_id': sesion_id,
                'paciente_id': paciente_id
            }, "Estudiante removido de la sesión pedagógica exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.remove_estudiante_from_sesion - Error: {str(e)}")
            return response_error(f"Error al remover estudiante: {str(e)}", 500)

    @staticmethod
    def get_cronograma_sesion(sesion_id):
        """Obtener cronograma de una sesión pedagógica"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.get_cronograma_sesion - Sesión: {sesion_id}")

            cronograma = SesionPedagogicaComponent.get_cronograma_sesion(sesion_id)

            if cronograma:
                # Formatear cronograma
                cronograma_formateado = []
                for clase in cronograma:
                    clase_data = {
                        'id': clase['id'],
                        'numero_clase': clase['numero_clase'],
                        'fecha_programada': clase['fecha_programada'].isoformat() if clase['fecha_programada'] else None,
                        'hora_programada': str(clase['hora_programada']) if clase['hora_programada'] else None,
                        'tema_clase': clase['tema_clase'],
                        'estado': clase['estado'],
                        'fecha_realizacion': clase['fecha_realizacion'].isoformat() if clase['fecha_realizacion'] else None,
                        'objetivos_clase': clase['objetivos_clase'],
                        'material_requerido': clase['material_requerido'],
                        'tareas_asignadas': clase['tareas_asignadas'],
                        'evaluacion_programada': clase['evaluacion_programada'],
                        'tipo_evaluacion': clase['tipo_evaluacion']
                    }
                    cronograma_formateado.append(clase_data)

                return response_success(cronograma_formateado, "Cronograma obtenido exitosamente")
            else:
                return response_success([], "No hay cronograma generado para esta sesión")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.get_cronograma_sesion - Error: {str(e)}")
            return response_error(f"Error al obtener cronograma: {str(e)}", 500)

    @staticmethod
    def get_estadisticas():
        """Obtener estadísticas de sesiones pedagógicas"""
        try:
            HandleLogs.write_log("SesionPedagogicaService.get_estadisticas - Iniciando")

            estadisticas = SesionPedagogicaComponent.get_estadisticas_sesiones()

            if estadisticas:
                # Función auxiliar para conversión segura
                def safe_int(value):
                    try:
                        return int(value) if value is not None else 0
                    except (ValueError, TypeError):
                        return 0

                def safe_float(value):
                    try:
                        return float(value) if value is not None else 0.0
                    except (ValueError, TypeError):
                        return 0.0

                # Formatear estadísticas
                estadisticas_formateadas = {
                    'sesiones': {
                        'total': safe_int(estadisticas.get('total_sesiones')),
                        'activas': safe_int(estadisticas.get('sesiones_activas')),
                        'completadas': safe_int(estadisticas.get('sesiones_completadas')),
                        'suspendidas': safe_int(estadisticas.get('sesiones_suspendidas')),
                        'canceladas': safe_int(estadisticas.get('sesiones_canceladas'))
                    },
                    'clases': {
                        'total_programadas': safe_int(estadisticas.get('total_clases_programadas')),
                        'realizadas': safe_int(estadisticas.get('clases_realizadas')),
                        'pendientes': safe_int(estadisticas.get('clases_pendientes')),
                        'canceladas': safe_int(estadisticas.get('clases_canceladas')),
                        'reprogramadas': safe_int(estadisticas.get('clases_reprogramadas'))
                    },
                    'financiero': {
                        'ingresos_totales': safe_float(estadisticas.get('ingresos_totales'))
                    },
                    'promedios': {
                        'duracion_promedio_minutos': safe_float(estadisticas.get('duracion_promedio'))
                    }
                }

                # Calcular porcentajes
                total_sesiones = estadisticas_formateadas['sesiones']['total']
                total_clases = estadisticas_formateadas['clases']['total_programadas']

                if total_sesiones > 0:
                    estadisticas_formateadas['porcentajes'] = {
                        'sesiones_activas': round((estadisticas_formateadas['sesiones']['activas'] / total_sesiones) * 100, 2),
                        'sesiones_completadas': round((estadisticas_formateadas['sesiones']['completadas'] / total_sesiones) * 100, 2)
                    }

                if total_clases > 0:
                    estadisticas_formateadas['porcentajes']['clases_realizadas'] = round(
                        (estadisticas_formateadas['clases']['realizadas'] / total_clases) * 100, 2)

                HandleLogs.write_log("SesionPedagogicaService.get_estadisticas - Estadísticas obtenidas")
                return response_success(estadisticas_formateadas, "Estadísticas obtenidas exitosamente")
            else:
                # Retornar estadísticas vacías
                estadisticas_vacias = {
                    'sesiones': {'total': 0, 'activas': 0, 'completadas': 0, 'suspendidas': 0, 'canceladas': 0},
                    'clases': {'total_programadas': 0, 'realizadas': 0, 'pendientes': 0, 'canceladas': 0, 'reprogramadas': 0},
                    'financiero': {'ingresos_totales': 0.0},
                    'promedios': {'duracion_promedio_minutos': 0.0},
                    'porcentajes': {'sesiones_activas': 0.0, 'sesiones_completadas': 0.0, 'clases_realizadas': 0.0}
                }
                return response_success(estadisticas_vacias, "No hay datos estadísticos disponibles")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.get_estadisticas - Error: {str(e)}")
            return response_error(f"Error al obtener estadísticas: {str(e)}", 500)

    @staticmethod
    def get_estudiantes_disponibles():
        """Obtener lista de estudiantes (pacientes) disponibles para asignar a sesiones"""
        try:
            HandleLogs.write_log("SesionPedagogicaService.get_estudiantes_disponibles - Iniciando")

            from src.api.Components.PacienteComponent import PacienteComponent
            
            # Obtener pacientes activos
            pacientes_result = PacienteComponent.get_all_pacientes()
            
            if pacientes_result['success']:
                # Filtrar solo pacientes activos
                all_pacientes = pacientes_result['data']
                pacientes = [p for p in all_pacientes if p.get('estado') == 'activo'] if all_pacientes else []
            else:
                pacientes = []

            if pacientes:
                return response_success(pacientes, "Estudiantes disponibles obtenidos")
            else:
                return response_success([], "No hay estudiantes disponibles")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.get_estudiantes_disponibles - Error: {str(e)}")
            return response_error(f"Error al obtener estudiantes disponibles: {str(e)}", 500)

    @staticmethod
    def get_pedagogos_disponibles():
        """Obtener lista de pedagogos disponibles para asignar a sesiones"""
        try:
            HandleLogs.write_log("SesionPedagogicaService.get_pedagogos_disponibles - Iniciando")

            from src.api.Components.PersonalComponent import PersonalComponent
            
            # Obtener personal del área pedagógica
            pedagogos_result = PersonalComponent.get_personal_by_area('pedagogico')
            
            if pedagogos_result['success']:
                pedagogos = pedagogos_result['data']
            else:
                pedagogos = []

            if pedagogos:
                return response_success(pedagogos, "Pedagogos disponibles obtenidos")
            else:
                return response_success([], "No hay pedagogos disponibles")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.get_pedagogos_disponibles - Error: {str(e)}")
            return response_error(f"Error al obtener pedagogos disponibles: {str(e)}", 500)