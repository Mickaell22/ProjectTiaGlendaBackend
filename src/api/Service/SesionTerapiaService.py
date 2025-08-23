# src/api/Service/SesionTerapiaService.py

from flask import request, jsonify, g
from src.api.Components.SesionTerapiaComponent import SesionTerapiaComponent
from src.utils.general.response import response_success, response_error
from src.utils.general.logs import HandleLogs
from datetime import datetime, date, time, timedelta
import re


class SesionTerapiaService:
    """Service para lógica de negocio de sesiones de terapia"""

    @staticmethod
    def get_sesiones():
        """Obtener todas las sesiones de terapia"""
        try:
            HandleLogs.write_log("SesionTerapiaService.get_sesiones - Iniciando")

            sesiones = SesionTerapiaComponent.get_sesiones()

            if sesiones:
                # Formatear datos para respuesta
                sesiones_formateadas = []
                for sesion in sesiones:
                    # Obtener información de pacientes para esta sesión
                    pacientes = SesionTerapiaComponent.get_pacientes_sesion(sesion['id'])
                    pacientes_data = []
                    
                    if pacientes:
                        for paciente in pacientes:
                            pacientes_data.append({
                                'paciente_id': paciente['paciente_id'],
                                'paciente_nombre': paciente['paciente_nombre'],
                                'paciente_cedula': paciente['paciente_cedula'],
                                'fecha_asignacion': paciente['fecha_asignacion'].isoformat() if paciente.get('fecha_asignacion') else None
                            })
                    
                    # Determinar tipo de sesión basado en número de pacientes
                    tipo_sesion = 'grupal' if len(pacientes_data) > 1 else 'individual'
                    
                    sesion_data = {
                        'id': sesion['id'],
                        'codigo_sesion': sesion['codigo_sesion'],
                        'titulo': sesion['titulo'],
                        'tipo_sesion': tipo_sesion,
                        'terapeuta': {
                            'id': sesion['terapeuta_id'],
                            'nombre': sesion['terapeuta_nombre']
                        },
                        'terapeuta_id': sesion['terapeuta_id'],
                        'terapeuta_nombre': sesion['terapeuta_nombre'],
                        'especialidad': {
                            'id': sesion['especialidad_id'],
                            'nombre': sesion['especialidad_nombre'],
                            'area': sesion['especialidad_area']
                        },
                        'especialidad_id': sesion['especialidad_id'],
                        'especialidad_nombre': sesion['especialidad_nombre'],
                        'especialidad_area': sesion['especialidad_area'],
                        'pacientes': pacientes_data,
                        # Para compatibilidad con frontend, incluir datos del primer paciente como campos planos
                        'paciente_id': pacientes_data[0]['paciente_id'] if pacientes_data else None,
                        'paciente_nombre': pacientes_data[0]['paciente_nombre'] if pacientes_data else None,
                        'paciente_cedula': pacientes_data[0]['paciente_cedula'] if pacientes_data else None,
                        'fecha_inicio': sesion['fecha_inicio'].isoformat() if sesion['fecha_inicio'] else None,
                        'fecha_fin': sesion['fecha_fin'].isoformat() if sesion['fecha_fin'] else None,
                        'dias_semana': sesion['dias_semana'] if isinstance(sesion['dias_semana'], list) else (sesion['dias_semana'].split(',') if sesion['dias_semana'] else []),
                        'hora_inicio': str(sesion['hora_inicio']) if sesion['hora_inicio'] else None,
                        'hora_fin': str(sesion['hora_fin']) if sesion['hora_fin'] else None,
                        'duracion_minutos': sesion['duracion_minutos'],
                        'numero_sesiones_contratadas': sesion['numero_sesiones_contratadas'],
                        'costo_total': float(sesion['costo_total']),
                        'costo_por_sesion': float(sesion['costo_por_sesion']),
                        'meses_contrato': sesion['meses_contrato'],
                        'estado': sesion['estado'],
                        'estadisticas': {
                            'total_pacientes': sesion['total_pacientes'],
                            'sesiones_programadas': sesion['sesiones_programadas'],
                            'sesiones_realizadas': sesion['sesiones_realizadas'],
                            'progreso_porcentaje': round(
                                (sesion['sesiones_realizadas'] / sesion['sesiones_programadas'] * 100), 2) if sesion[
                                                                                                                  'sesiones_programadas'] > 0 else 0
                        },
                        'fecha_creacion': sesion['fecha_creacion'].isoformat() if sesion['fecha_creacion'] else None
                    }
                    sesiones_formateadas.append(sesion_data)

                HandleLogs.write_log("SesionTerapiaService.get_sesiones - Sesiones obtenidas exitosamente")
                return response_success(sesiones_formateadas, "Sesiones obtenidas exitosamente")
            else:
                return response_success([], "No hay sesiones registradas")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_sesiones - Error: {str(e)}")
            return response_error(f"Error al obtener sesiones: {str(e)}", 500)

    @staticmethod
    def get_sesion(sesion_id):
        """Obtener una sesión específica por ID"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.get_sesion - ID: {sesion_id}")

            # Validar ID
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            sesion = SesionTerapiaComponent.get_sesion_by_id(sesion_id)

            if sesion:
                # Obtener información adicional
                pacientes = SesionTerapiaComponent.get_pacientes_sesion(sesion_id)
                cronograma_raw = SesionTerapiaComponent.get_cronograma_sesion(sesion_id)
                
                # Formatear cronograma para serialización JSON
                cronograma = []
                if cronograma_raw:
                    for sesion_cronograma in cronograma_raw:
                        cronograma_data = {
                            'id': sesion_cronograma['id'],
                            'numero_sesion': sesion_cronograma['numero_sesion_semanal'],
                            'fecha_programada': sesion_cronograma['fecha_programada'].isoformat() if sesion_cronograma['fecha_programada'] else None,
                            'hora_programada': str(sesion_cronograma['hora_inicio']) if sesion_cronograma['hora_inicio'] else None,
                            'estado': sesion_cronograma['estado'],
                            'fecha_realizacion': sesion_cronograma['fecha_realizacion'].isoformat() if sesion_cronograma.get('fecha_realizacion') else None,
                            'observaciones_cronograma': sesion_cronograma.get('observaciones_cronograma'),
                            'estado_actual': sesion_cronograma.get('estado_actual', sesion_cronograma['estado'])
                        }
                        cronograma.append(cronograma_data)

                sesion_data = {
                    'id': sesion['id'],
                    'codigo_sesion': sesion['codigo_sesion'],
                    'titulo': sesion['titulo'],
                    'terapeuta': {
                        'id': sesion['terapeuta_id'],
                        'nombre': sesion['terapeuta_nombre']
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
                    'numero_sesiones_contratadas': sesion['numero_sesiones_contratadas'],
                    'costo_total': float(sesion['costo_total']),
                    'costo_por_sesion': float(sesion['costo_por_sesion']),
                    'meses_contrato': sesion['meses_contrato'],
                    'estado': sesion['estado'],
                    'pacientes': pacientes or [],
                    'cronograma': cronograma or [],
                    'fecha_creacion': sesion['fecha_creacion'].isoformat() if sesion['fecha_creacion'] else None
                }

                HandleLogs.write_log(f"SesionTerapiaService.get_sesion - Sesión {sesion_id} encontrada")
                return response_success(sesion_data, "Sesión encontrada")
            else:
                return response_error(f"Sesión con ID {sesion_id} no encontrada", 404)

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_sesion - Error: {str(e)}")
            return response_error(f"Error al obtener sesión: {str(e)}", 500)

    @staticmethod
    def create_sesion():
        """Crear una nueva sesión de terapia"""
        try:
            HandleLogs.write_log("SesionTerapiaService.create_sesion - Iniciando")

            data = request.get_json()
            current_user = request.current_user

            # Validar datos requeridos
            validation_result = SesionTerapiaService._validate_sesion_data(data, is_update=False)
            if validation_result:
                return validation_result

            # Preparar datos para inserción
            hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
            duracion_minutos = data.get('duracion_minutos', 45)
            
            # Calcular hora_fin basándose en hora_inicio + duración
            dt_inicio = datetime.combine(datetime.today(), hora_inicio)
            dt_fin = dt_inicio + timedelta(minutes=duracion_minutos)
            hora_fin = dt_fin.time()
            
            sesion_data = {
                'titulo': data['titulo'].strip(),
                'terapeuta_id': data['terapeuta_id'],
                'especialidad_id': data['especialidad_id'],
                'fecha_inicio': datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date(),
                'fecha_fin': datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date(),
                'dias_semana': [dia.lower().strip() for dia in data['dias_semana']],
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin,
                'duracion_minutos': duracion_minutos,
                'estado': data.get('estado', 'planificada'),
                'id_centro': current_user.get('centro', {}).get('id', 1),  # Use user's center
                'usuario_creacion': current_user['id']
            }

            # Validaciones de negocio adicionales
            business_validation = SesionTerapiaService._validate_business_rules(sesion_data)
            if business_validation:
                return business_validation

            # Crear sesión
            result = SesionTerapiaComponent.create_sesion(sesion_data)

            if result:
                sesion_id = result['id']
                codigo_sesion = result.get('codigo_sesion', f"ST-{sesion_id}")

                # Generar cronograma automático
                try:
                    SesionTerapiaComponent.generar_cronograma(sesion_id)
                except Exception as cron_error:
                    HandleLogs.write_error(f"Error generando cronograma: {str(cron_error)}")

                # Agregar paciente si es sesión individual
                if data.get('paciente_id'):
                    try:
                        paciente_info = {
                            'paciente_id': data['paciente_id'],
                            'fecha_incorporacion': sesion_data['fecha_inicio'],
                            'costo_paciente': None,
                            'observaciones_paciente': None,
                            'usuario_creacion': current_user['id']
                        }
                        SesionTerapiaComponent.add_paciente_to_sesion(sesion_id, paciente_info)
                        HandleLogs.write_log(f"SesionTerapiaService.create_sesion - Paciente {data['paciente_id']} agregado a sesión {sesion_id}")
                    except Exception as pac_error:
                        HandleLogs.write_error(f"Error agregando paciente: {str(pac_error)}")

                # Agregar pacientes adicionales si se proporcionaron
                if data.get('pacientes'):
                    for paciente_data in data['pacientes']:
                        try:
                            paciente_info = {
                                'paciente_id': paciente_data['paciente_id'],
                                'fecha_incorporacion': datetime.strptime(
                                    paciente_data.get('fecha_incorporacion', data['fecha_inicio']),
                                    '%Y-%m-%d').date() if paciente_data.get('fecha_incorporacion') else sesion_data[
                                    'fecha_inicio'],
                                'costo_paciente': paciente_data.get('costo_paciente'),
                                'observaciones_paciente': paciente_data.get('observaciones_paciente'),
                                'usuario_creacion': current_user['id']
                            }
                            SesionTerapiaComponent.add_paciente_to_sesion(sesion_id, paciente_info)
                        except Exception as pac_error:
                            HandleLogs.write_error(f"Error agregando paciente: {str(pac_error)}")

                HandleLogs.write_log(f"SesionTerapiaService.create_sesion - Sesión creada con ID: {sesion_id}")
                return response_success({
                    'id': sesion_id,
                    'codigo_sesion': codigo_sesion,
                    'mensaje': 'Sesión creada exitosamente y cronograma generado'
                }, "Sesión creada exitosamente")
            else:
                return response_error("No se pudo crear la sesión", 500)

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.create_sesion - Error: {str(e)}")
            return response_error(f"Error al crear sesión: {str(e)}", 500)

    @staticmethod
    def get_estadisticas():
        """Obtener estadísticas generales de sesiones"""
        try:
            HandleLogs.write_log("SesionTerapiaService.get_estadisticas - Iniciando")

            estadisticas = SesionTerapiaComponent.get_estadisticas_sesiones()

            if estadisticas:
                # Formatear estadísticas con validaciones adicionales
                def safe_float(value, default=0.0):
                    """Convierte a float de manera segura"""
                    try:
                        return float(value) if value is not None else default
                    except (ValueError, TypeError):
                        return default

                def safe_int(value, default=0):
                    """Convierte a int de manera segura"""
                    try:
                        return int(value) if value is not None else default
                    except (ValueError, TypeError):
                        return default

                stats_formateadas = {
                    'sesiones': {
                        'total': safe_int(estadisticas.get('total_sesiones')),
                        'activas': safe_int(estadisticas.get('sesiones_activas')),
                        'completadas': safe_int(estadisticas.get('sesiones_completadas')),
                        'suspendidas': safe_int(estadisticas.get('sesiones_suspendidas')),
                        'canceladas': safe_int(estadisticas.get('sesiones_canceladas'))
                    },
                    'cronograma': {
                        'total_programadas': safe_int(estadisticas.get('total_sesiones_programadas')),
                        'realizadas': safe_int(estadisticas.get('sesiones_realizadas')),
                        'pendientes': safe_int(estadisticas.get('sesiones_pendientes')),
                        'canceladas': safe_int(estadisticas.get('sesiones_canceladas_cronograma')),
                        'reprogramadas': safe_int(estadisticas.get('sesiones_reprogramadas'))
                    },
                    'financiero': {
                        'ingresos_totales': safe_float(estadisticas.get('ingresos_totales')),
                        'sesiones_contratadas': safe_int(estadisticas.get('total_sesiones_contratadas'))
                    },
                    'operacional': {
                        'duracion_promedio_minutos': safe_float(estadisticas.get('duracion_promedio')),
                        'porcentaje_cumplimiento': 0.0  # Calcular después
                    }
                }

                # Calcular porcentaje de cumplimiento de manera segura
                total_programadas = stats_formateadas['cronograma']['total_programadas']
                realizadas = stats_formateadas['cronograma']['realizadas']

                if total_programadas > 0:
                    porcentaje = round((realizadas / total_programadas * 100), 2)
                    stats_formateadas['operacional']['porcentaje_cumplimiento'] = porcentaje

                HandleLogs.write_log("SesionTerapiaService.get_estadisticas - Estadísticas obtenidas")
                return response_success(stats_formateadas, "Estadísticas obtenidas exitosamente")
            else:
                # Retornar estructura vacía si no hay datos
                stats_vacias = {
                    'sesiones': {'total': 0, 'activas': 0, 'completadas': 0, 'suspendidas': 0, 'canceladas': 0},
                    'cronograma': {'total_programadas': 0, 'realizadas': 0, 'pendientes': 0, 'canceladas': 0,
                                   'reprogramadas': 0},
                    'financiero': {'ingresos_totales': 0.0, 'sesiones_contratadas': 0},
                    'operacional': {'duracion_promedio_minutos': 0.0, 'porcentaje_cumplimiento': 0.0}
                }
                return response_success(stats_vacias, "No hay datos para generar estadísticas")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_estadisticas - Error: {str(e)}")
            return response_error(f"Error al obtener estadísticas: {str(e)}", 500)

    @staticmethod
    def get_sesiones_hoy():
        """Obtener sesiones programadas para hoy"""
        try:
            HandleLogs.write_log("SesionTerapiaService.get_sesiones_hoy - Iniciando")

            sesiones = SesionTerapiaComponent.get_sesiones_activas_hoy()

            # Formatear datos para evitar errores de serialización JSON
            if sesiones:
                sesiones_formateadas = []
                for sesion in sesiones:
                    sesion_formateada = {}
                    for key, value in sesion.items():
                        # Convertir objetos time a string
                        if hasattr(value, 'strftime') and hasattr(value, 'hour'):  # Es un objeto time
                            sesion_formateada[key] = str(value)
                        # Convertir objetos date a string
                        elif hasattr(value, 'isoformat') and hasattr(value, 'year'):  # Es un objeto date
                            sesion_formateada[key] = value.isoformat()
                        # Mantener otros valores como están
                        else:
                            sesion_formateada[key] = value
                    sesiones_formateadas.append(sesion_formateada)
                
                HandleLogs.write_log(
                    f"SesionTerapiaService.get_sesiones_hoy - {len(sesiones_formateadas)} sesiones hoy")
                return response_success(sesiones_formateadas, "Sesiones de hoy obtenidas exitosamente")
            else:
                return response_success([], "No hay sesiones programadas para hoy")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_sesiones_hoy - Error: {str(e)}")
            return response_error(f"Error al obtener sesiones de hoy: {str(e)}", 500)

    @staticmethod
    def get_terapeutas_disponibles():
        """Obtener terapeutas disponibles para asignar a sesiones"""
        try:
            HandleLogs.write_log("SesionTerapiaService.get_terapeutas_disponibles - Iniciando")

            terapeutas = SesionTerapiaComponent.get_terapeutas_disponibles()

            HandleLogs.write_log(
                f"SesionTerapiaService.get_terapeutas_disponibles - {len(terapeutas) if terapeutas else 0} terapeutas disponibles")
            return response_success(terapeutas or [], "Terapeutas disponibles obtenidos exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_terapeutas_disponibles - Error: {str(e)}")
            return response_error(f"Error al obtener terapeutas disponibles: {str(e)}", 500)

    @staticmethod
    def get_pacientes_disponibles():
        """Obtener pacientes disponibles para asignar a sesiones"""
        try:
            HandleLogs.write_log("SesionTerapiaService.get_pacientes_disponibles - Iniciando")

            pacientes = SesionTerapiaComponent.get_pacientes_disponibles()

            HandleLogs.write_log(
                f"SesionTerapiaService.get_pacientes_disponibles - {len(pacientes) if pacientes else 0} pacientes disponibles")
            return response_success(pacientes or [], "Pacientes disponibles obtenidos exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_pacientes_disponibles - Error: {str(e)}")
            return response_error(f"Error al obtener pacientes disponibles: {str(e)}", 500)

    @staticmethod
    def get_cronograma_sesion(sesion_id):
        """Obtener cronograma de una sesión específica"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.get_cronograma_sesion - Iniciando para sesión {sesion_id}")

            cronograma = SesionTerapiaComponent.get_cronograma_sesion(sesion_id)

            # Formatear datos para evitar errores de serialización JSON
            if cronograma:
                cronograma_formateado = []
                for sesion in cronograma:
                    sesion_formateada = {}
                    for key, value in sesion.items():
                        # Convertir objetos time a string
                        if hasattr(value, 'strftime') and hasattr(value, 'hour'):  # Es un objeto time
                            sesion_formateada[key] = str(value)
                        # Convertir objetos date a string
                        elif hasattr(value, 'isoformat') and hasattr(value, 'year'):  # Es un objeto date
                            sesion_formateada[key] = value.isoformat()
                        # Mantener otros valores como están
                        else:
                            sesion_formateada[key] = value
                    cronograma_formateado.append(sesion_formateada)

                HandleLogs.write_log(
                    f"SesionTerapiaService.get_cronograma_sesion - {len(cronograma_formateado)} sesiones programadas")
                return response_success(cronograma_formateado, "Cronograma obtenido exitosamente")
            else:
                return response_success([], "No hay sesiones programadas para esta sesión")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_cronograma_sesion - Error: {str(e)}")
            return response_error(f"Error al obtener cronograma: {str(e)}", 500)

    # ============================================
    # MÉTODOS DE VALIDACIÓN
    # ============================================

    @staticmethod
    def _validate_sesion_data(data, is_update=False):
        """Validar datos de entrada para sesión"""
        # Validar campos requeridos
        required_fields = ['titulo', 'terapeuta_id', 'especialidad_id', 'fecha_inicio',
                           'fecha_fin', 'dias_semana', 'hora_inicio']

        for field in required_fields:
            if not data.get(field):
                return response_error(f"Campo '{field}' es requerido", 400)

        # Validar tipos de datos
        try:
            terapeuta_id = int(data['terapeuta_id'])
            especialidad_id = int(data['especialidad_id'])
            duracion_minutos = int(data.get('duracion_minutos', 45))
        except (ValueError, TypeError):
            return response_error("Tipos de datos inválidos en campos numéricos", 400)

        # Validar rangos
        if terapeuta_id <= 0:
            return response_error("ID del terapeuta debe ser positivo", 400)

        if especialidad_id <= 0:
            return response_error("ID de especialidad debe ser positivo", 400)



        if duracion_minutos < 15 or duracion_minutos > 120:
            return response_error("Duración debe estar entre 15 y 120 minutos", 400)

        # Validar fechas
        try:
            fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
        except ValueError:
            return response_error("Formato de fecha inválido. Use YYYY-MM-DD", 400)

        if fecha_fin <= fecha_inicio:
            return response_error("Fecha de fin debe ser posterior a fecha de inicio", 400)

        # Validar hora
        try:
            datetime.strptime(data['hora_inicio'], '%H:%M')
        except ValueError:
            return response_error("Formato de hora inválido. Use HH:MM", 400)

        # Validar días de semana con normalización de tildes
        dias_validos = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']

        # Mapeo para normalizar nombres con tildes
        normalizacion_dias = {
            'miércoles': 'miercoles',
            'sábado': 'sabado',
            'miercoles': 'miercoles',  # ya normalizado
            'sabado': 'sabado',  # ya normalizado
            'lunes': 'lunes',
            'martes': 'martes',
            'jueves': 'jueves',
            'viernes': 'viernes',
            'domingo': 'domingo'
        }

        if not isinstance(data['dias_semana'], list) or not data['dias_semana']:
            return response_error("Días de semana debe ser una lista no vacía", 400)

        # Normalizar días antes de validar
        dias_normalizados = []
        for dia in data['dias_semana']:
            dia_lower = dia.lower().strip()
            dia_normalizado = normalizacion_dias.get(dia_lower, dia_lower)

            if dia_normalizado not in dias_validos:
                return response_error(f"Día de semana inválido: {dia}", 400)

            dias_normalizados.append(dia_normalizado)

        # Actualizar los datos con días normalizados
        data['dias_semana'] = dias_normalizados

        # Validar título
        titulo = data['titulo'].strip()
        if len(titulo) < 5 or len(titulo) > 200:
            return response_error("Título debe tener entre 5 y 200 caracteres", 400)

        return None

    @staticmethod
    def _validate_business_rules(sesion_data):
        """Validar reglas de negocio"""
        # Permitir fecha de inicio en el pasado cercano (máximo 7 días) para flexibilidad
        fecha_limite = datetime.now().date() - timedelta(days=7)
        if sesion_data['fecha_inicio'] < fecha_limite:
            return response_error("La fecha de inicio no puede ser anterior a 7 días desde hoy", 400)

        # Validar que el rango de fechas sea razonable
        dias_diferencia = (sesion_data['fecha_fin'] - sesion_data['fecha_inicio']).days
        if dias_diferencia > 365:  # Máximo 1 año
            return response_error("El período de sesiones no puede exceder 1 año", 400)

        # Validar horario de trabajo (7:00 AM a 7:00 PM)
        hora_inicio = sesion_data['hora_inicio']
        if hora_inicio < time(7, 0) or hora_inicio > time(19, 0):
            return response_error("Las sesiones deben programarse entre 7:00 AM y 7:00 PM", 400)

        return None

    @staticmethod
    def update_sesion(sesion_id):
        """Actualizar una sesión de terapia"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.update_sesion - ID: {sesion_id}")

            data = request.get_json()
            current_user = request.current_user

            # Validar ID
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            # Validar datos requeridos
            validation_result = SesionTerapiaService._validate_sesion_data(data, is_update=True)
            if validation_result:
                return validation_result

            # Preparar datos para actualización
            hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
            duracion_minutos = data.get('duracion_minutos', 45)
            
            # Calcular hora_fin basándose en hora_inicio + duración
            dt_inicio = datetime.combine(datetime.today(), hora_inicio)
            dt_fin = dt_inicio + timedelta(minutes=duracion_minutos)
            hora_fin = dt_fin.time()
            
            sesion_data = {
                'titulo': data['titulo'].strip(),
                'terapeuta_id': data['terapeuta_id'],
                'especialidad_id': data['especialidad_id'],
                'fecha_inicio': datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date(),
                'fecha_fin': datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date(),
                'dias_semana': [dia.lower().strip() for dia in data['dias_semana']],
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin,
                'duracion_minutos': duracion_minutos,
                'numero_sesiones_contratadas': data['numero_sesiones_contratadas'],
                'costo_total': float(data['costo_total']),
                'meses_contrato': data.get('meses_contrato'),
                'estado': data.get('estado', 'activo'),
                'usuario_modificacion': current_user['id']
            }

            # Obtener datos actuales de la sesión para comparar cambios
            sesion_actual = SesionTerapiaComponent.get_sesion_by_id(sesion_id)
            
            # Actualizar sesión
            result = SesionTerapiaComponent.update_sesion(sesion_id, sesion_data)

            if result:
                # Verificar si hubo cambios en horario, días o fechas que requieran actualizar cronograma
                cronograma_changed = (
                    str(sesion_actual.get('hora_inicio', '')) != str(sesion_data['hora_inicio']) or
                    sesion_actual.get('duracion_minutos') != sesion_data['duracion_minutos'] or
                    sesion_actual.get('dias_semana', '') != sesion_data['dias_semana'] or
                    str(sesion_actual.get('fecha_inicio', '')) != str(sesion_data['fecha_inicio']) or
                    str(sesion_actual.get('fecha_fin', '')) != str(sesion_data['fecha_fin'])
                )
                
                if cronograma_changed:
                    HandleLogs.write_log(f"SesionTerapiaService.update_sesion - Cambios en cronograma detectados, actualizando...")
                    try:
                        # Actualizar cronograma preservando asistencias existentes
                        SesionTerapiaComponent.actualizar_cronograma_inteligente(sesion_id, sesion_data)
                    except Exception as cron_error:
                        HandleLogs.write_error(f"Error actualizando cronograma: {str(cron_error)}")
                        # No fallar la actualización por errores de cronograma
                
                HandleLogs.write_log(f"SesionTerapiaService.update_sesion - Sesión {sesion_id} actualizada")
                return response_success({'id': sesion_id}, "Sesión actualizada exitosamente")
            else:
                return response_error("No se pudo actualizar la sesión", 500)

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.update_sesion - Error: {str(e)}")
            return response_error(f"Error al actualizar sesión: {str(e)}", 500)

    @staticmethod
    def delete_sesion(sesion_id):
        """Cancelar una sesión de terapia"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.delete_sesion - ID: {sesion_id}")

            # Validar ID
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            # Cancelar sesión
            result = SesionTerapiaComponent.delete_sesion(sesion_id)

            if result:
                HandleLogs.write_log(f"SesionTerapiaService.delete_sesion - Sesión {sesion_id} cancelada")
                return response_success({'id': sesion_id}, "Sesión cancelada exitosamente")
            else:
                return response_error("No se pudo cancelar la sesión", 500)

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.delete_sesion - Error: {str(e)}")
            return response_error(f"Error al cancelar sesión: {str(e)}", 500)

    @staticmethod
    def get_cronograma_sesion(sesion_id):
        """Obtener cronograma de una sesión"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.get_cronograma_sesion - ID: {sesion_id}")

            cronograma_raw = SesionTerapiaComponent.get_cronograma_sesion(sesion_id)
            
            # Formatear cronograma para serialización JSON
            cronograma = []
            if cronograma_raw:
                for sesion_cronograma in cronograma_raw:
                    cronograma_data = {
                        'id': sesion_cronograma['id'],
                        'numero_sesion': sesion_cronograma['numero_sesion_semanal'],
                        'fecha_programada': sesion_cronograma['fecha_programada'].isoformat() if sesion_cronograma['fecha_programada'] else None,
                        'hora_programada': str(sesion_cronograma['hora_programada']) if sesion_cronograma['hora_programada'] else None,
                        'estado': sesion_cronograma['estado'],
                        'fecha_realizacion': sesion_cronograma['fecha_realizacion'].isoformat() if sesion_cronograma.get('fecha_realizacion') else None,
                        'observaciones_cronograma': sesion_cronograma.get('observaciones_cronograma'),
                        'estado_actual': sesion_cronograma.get('estado_actual', sesion_cronograma['estado'])
                    }
                    cronograma.append(cronograma_data)

            HandleLogs.write_log(f"SesionTerapiaService.get_cronograma_sesion - Cronograma obtenido")
            return response_success(cronograma or [], "Cronograma obtenido exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_cronograma_sesion - Error: {str(e)}")
            return response_error(f"Error al obtener cronograma: {str(e)}", 500)

    @staticmethod
    def get_sesiones_by_terapeuta(terapeuta_id):
        """Obtener sesiones de un terapeuta"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.get_sesiones_by_terapeuta - ID: {terapeuta_id}")

            sesiones = SesionTerapiaComponent.get_sesiones_by_terapeuta(terapeuta_id)

            # Formatear sesiones para serialización JSON
            if sesiones:
                sesiones_formateadas = []
                for sesion in sesiones:
                    sesion_data = {
                        'id': sesion['id'],
                        'codigo_sesion': sesion['codigo_sesion'],
                        'titulo': sesion['titulo'],
                        'terapeuta_id': sesion['terapeuta_id'],
                        'especialidad_id': sesion['especialidad_id'],
                        'especialidad_nombre': sesion['especialidad_nombre'],
                        'fecha_inicio': sesion['fecha_inicio'].isoformat() if sesion['fecha_inicio'] else None,
                        'fecha_fin': sesion['fecha_fin'].isoformat() if sesion['fecha_fin'] else None,
                        'dias_semana': sesion['dias_semana'] if isinstance(sesion['dias_semana'], list) else (sesion['dias_semana'].split(',') if sesion['dias_semana'] else []),
                        'hora_inicio': str(sesion['hora_inicio']) if sesion['hora_inicio'] else None,
                        'hora_fin': str(sesion['hora_fin']) if sesion['hora_fin'] else None,
                        'duracion_minutos': sesion['duracion_minutos'],
                        'numero_sesiones_contratadas': sesion['numero_sesiones_contratadas'],
                        'costo_total': float(sesion['costo_total']) if sesion['costo_total'] else 0.0,
                        'costo_por_sesion': float(sesion['costo_por_sesion']) if sesion['costo_por_sesion'] else 0.0,
                        'meses_contrato': sesion['meses_contrato'],
                        'estado': sesion['estado'],
                        'total_pacientes': sesion['total_pacientes'] if 'total_pacientes' in sesion else 0,
                        'fecha_creacion': sesion['fecha_creacion'].isoformat() if sesion['fecha_creacion'] else None
                    }
                    sesiones_formateadas.append(sesion_data)
                sesiones = sesiones_formateadas

            HandleLogs.write_log(f"SesionTerapiaService.get_sesiones_by_terapeuta - Sesiones obtenidas")
            return response_success(sesiones or [], "Sesiones del terapeuta obtenidas exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_sesiones_by_terapeuta - Error: {str(e)}")
            return response_error(f"Error al obtener sesiones del terapeuta: {str(e)}", 500)

    # ============================================
    # MÉTODOS PARA GESTIÓN DE PACIENTES EN SESIONES
    # ============================================

    @staticmethod
    def add_paciente_to_sesion(sesion_id):
        """Agregar un paciente a una sesión"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.add_paciente_to_sesion - Sesion ID: {sesion_id}")

            data = request.get_json()
            current_user = request.current_user

            # Validar ID de sesión
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            # Validar datos requeridos
            if not data.get('paciente_id'):
                return response_error("Campo 'paciente_id' es requerido", 400)

            try:
                paciente_id = int(data['paciente_id'])
                if paciente_id <= 0:
                    return response_error("ID del paciente debe ser positivo", 400)
            except (ValueError, TypeError):
                return response_error("ID del paciente debe ser un número válido", 400)

            # Preparar datos del paciente
            paciente_data = {
                'paciente_id': paciente_id,
                'fecha_incorporacion': datetime.strptime(
                    data.get('fecha_incorporacion', datetime.now().strftime('%Y-%m-%d')), 
                    '%Y-%m-%d').date() if data.get('fecha_incorporacion') else datetime.now().date(),
                'costo_paciente': float(data['costo_paciente']) if data.get('costo_paciente') else None,
                'observaciones_paciente': data.get('observaciones_paciente', '').strip() if data.get('observaciones_paciente') else None,
                'usuario_creacion': current_user['id']
            }

            # Validar costo si se proporciona
            if paciente_data['costo_paciente'] is not None and paciente_data['costo_paciente'] < 0:
                return response_error("El costo del paciente no puede ser negativo", 400)

            # Agregar paciente a la sesión
            result = SesionTerapiaComponent.add_paciente_to_sesion(sesion_id, paciente_data)

            if result:
                HandleLogs.write_log(f"SesionTerapiaService.add_paciente_to_sesion - Paciente {paciente_id} agregado a sesión {sesion_id}")
                return response_success({
                    'id': result['id'],
                    'sesion_id': sesion_id,
                    'paciente_id': paciente_id
                }, "Paciente agregado a la sesión exitosamente")
            else:
                return response_error("No se pudo agregar el paciente a la sesión", 500)

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.add_paciente_to_sesion - Error: {str(e)}")
            return response_error(f"Error al agregar paciente a la sesión: {str(e)}", 500)

    @staticmethod
    def remove_paciente_from_sesion(sesion_id, paciente_id):
        """Remover un paciente de una sesión"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.remove_paciente_from_sesion - Sesion: {sesion_id}, Paciente: {paciente_id}")

            # Validar IDs
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            if not isinstance(paciente_id, int) or paciente_id <= 0:
                return response_error("ID de paciente debe ser un número positivo", 400)

            # Remover paciente de la sesión
            result = SesionTerapiaComponent.remove_paciente_from_sesion(sesion_id, paciente_id)

            if result:
                HandleLogs.write_log(f"SesionTerapiaService.remove_paciente_from_sesion - Paciente {paciente_id} retirado de sesión {sesion_id}")
                return response_success({
                    'sesion_id': sesion_id,
                    'paciente_id': paciente_id
                }, "Paciente retirado de la sesión exitosamente")
            else:
                return response_error("No se pudo retirar el paciente de la sesión", 500)

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.remove_paciente_from_sesion - Error: {str(e)}")
            return response_error(f"Error al retirar paciente de la sesión: {str(e)}", 500)

    # ============================================
    # MÉTODOS PARA GESTIÓN DE CRONOGRAMA
    # ============================================

    @staticmethod
    def marcar_sesion_realizada(cronograma_id):
        """Marcar una sesión como realizada"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.marcar_sesion_realizada - Cronograma ID: {cronograma_id}")

            data = request.get_json() or {}

            # Validar ID
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)

            # Obtener observaciones
            observaciones = data.get('observaciones', '').strip() if data.get('observaciones') else None

            # Marcar sesión como realizada
            result = SesionTerapiaComponent.marcar_sesion_realizada(cronograma_id, observaciones)

            if result:
                HandleLogs.write_log(f"SesionTerapiaService.marcar_sesion_realizada - Sesión {cronograma_id} marcada como realizada")
                return response_success({
                    'cronograma_id': cronograma_id
                }, "Sesión marcada como realizada exitosamente")
            else:
                return response_error("No se pudo marcar la sesión como realizada", 500)

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.marcar_sesion_realizada - Error: {str(e)}")
            return response_error(f"Error al marcar sesión como realizada: {str(e)}", 500)

    @staticmethod
    def reprogramar_sesion(cronograma_id):
        """Reprogramar una sesión específica"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.reprogramar_sesion - Cronograma ID: {cronograma_id}")

            data = request.get_json()

            # Validar ID
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)

            # Validar datos requeridos
            required_fields = ['nueva_fecha', 'nueva_hora', 'motivo']
            for field in required_fields:
                if not data.get(field):
                    return response_error(f"Campo '{field}' es requerido", 400)

            # Validar formato de fecha y hora
            try:
                nueva_fecha = datetime.strptime(data['nueva_fecha'], '%Y-%m-%d').date()
                nueva_hora = datetime.strptime(data['nueva_hora'], '%H:%M').time()
            except ValueError:
                return response_error("Formato de fecha (YYYY-MM-DD) u hora (HH:MM) inválido", 400)

            # Validar que la nueva fecha no sea en el pasado
            if nueva_fecha < datetime.now().date():
                return response_error("La nueva fecha no puede ser en el pasado", 400)

            # Validar motivo
            motivo = data['motivo'].strip()
            if len(motivo) < 10:
                return response_error("El motivo debe tener al menos 10 caracteres", 400)

            # Reprogramar sesión
            result = SesionTerapiaComponent.reprogramar_sesion(cronograma_id, nueva_fecha, nueva_hora, motivo)

            if result:
                HandleLogs.write_log(f"SesionTerapiaService.reprogramar_sesion - Sesión {cronograma_id} reprogramada")
                return response_success({
                    'cronograma_original_id': cronograma_id,
                    'cronograma_nuevo_id': result['id'],
                    'nueva_fecha': nueva_fecha.isoformat(),
                    'nueva_hora': str(nueva_hora)
                }, "Sesión reprogramada exitosamente")
            else:
                return response_error("No se pudo reprogramar la sesión", 500)

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.reprogramar_sesion - Error: {str(e)}")
            return response_error(f"Error al reprogramar sesión: {str(e)}", 500)

    # ============================================
    # MÉTODOS PARA GESTIÓN DE ASISTENCIAS
    # ============================================

    @staticmethod
    def get_asistencias_sesion(cronograma_id):
        """Obtener asistencias de una sesión"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.get_asistencias_sesion - Cronograma ID: {cronograma_id}")

            # Validar ID
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)

            # Obtener asistencias
            asistencias = SesionTerapiaComponent.get_asistencias_sesion(cronograma_id)

            HandleLogs.write_log(f"SesionTerapiaService.get_asistencias_sesion - {len(asistencias) if asistencias else 0} asistencias encontradas")
            return response_success(asistencias or [], "Asistencias obtenidas exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_asistencias_sesion - Error: {str(e)}")
            return response_error(f"Error al obtener asistencias: {str(e)}", 500)

    @staticmethod
    def registrar_asistencia(cronograma_id, paciente_id):
        """Registrar asistencia de un paciente"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.registrar_asistencia - Cronograma: {cronograma_id}, Paciente: {paciente_id}")

            data = request.get_json()
            current_user = request.current_user

            # Validar IDs
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)

            if not isinstance(paciente_id, int) or paciente_id <= 0:
                return response_error("ID de paciente debe ser un número positivo", 400)

            # Validar que el paciente exista en la base de datos
            try:
                from src.utils.database.connection_db import DataBaseHandle
                paciente_check = DataBaseHandle.getRecords("SELECT id FROM paciente WHERE id = %s", (paciente_id,))
                if not paciente_check:
                    error_msg = f"PACIENTE NO EXISTE: ID {paciente_id} no se encuentra en la tabla paciente. Pacientes válidos: 1-9"
                    HandleLogs.write_error(f"SesionTerapiaService.registrar_asistencia - {error_msg}")
                    return response_error(error_msg, 400)
                
                HandleLogs.write_log(f"SesionTerapiaService.registrar_asistencia - Paciente {paciente_id} verificado exitosamente")
            except Exception as check_error:
                HandleLogs.write_error(f"SesionTerapiaService.registrar_asistencia - Error verificando paciente: {str(check_error)}")
                return response_error(f"Error verificando paciente: {str(check_error)}", 500)

            # Preparar datos de asistencia
            asistencia_data = {
                'asistio': data.get('asistio', False),
                'llegada_tardanza_minutos': int(data.get('llegada_tardanza_minutos', 0)),
                'observaciones_asistencia': data.get('observaciones_asistencia', '').strip() if data.get('observaciones_asistencia') else None,
                'notas_progreso': data.get('notas_progreso', '').strip() if data.get('notas_progreso') else None,
                'tareas_asignadas': data.get('tareas_asignadas', '').strip() if data.get('tareas_asignadas') else None,
                'proximos_objetivos': data.get('proximos_objetivos', '').strip() if data.get('proximos_objetivos') else None,
                'usuario_creacion': current_user['id']
            }

            # Validar datos
            if asistencia_data['llegada_tardanza_minutos'] < 0:
                return response_error("Los minutos de tardanza no pueden ser negativos", 400)

            # Registrar asistencia
            result = SesionTerapiaComponent.registrar_asistencia(cronograma_id, paciente_id, asistencia_data)

            if result:
                HandleLogs.write_log(f"SesionTerapiaService.registrar_asistencia - Asistencia registrada para paciente {paciente_id}")
                return response_success({
                    'id': result['id'],
                    'cronograma_id': cronograma_id,
                    'paciente_id': paciente_id,
                    'asistio': asistencia_data['asistio']
                }, "Asistencia registrada exitosamente")
            else:
                return response_error("No se pudo registrar la asistencia", 500)

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.registrar_asistencia - Error: {str(e)}")
            return response_error(f"Error al registrar asistencia: {str(e)}", 500)

    @staticmethod
    def get_asistencias_por_sesion(sesion_id):
        """Obtener todas las asistencias de una sesión de terapia"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.get_asistencias_por_sesion - Sesion ID: {sesion_id}")

            # Validar ID
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            # Obtener asistencias de la sesión mediante cronograma
            asistencias = SesionTerapiaComponent.get_asistencias_por_sesion(sesion_id)

            HandleLogs.write_log(f"SesionTerapiaService.get_asistencias_por_sesion - {len(asistencias) if asistencias else 0} asistencias encontradas")
            return response_success(asistencias or [], "Asistencias obtenidas exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_asistencias_por_sesion - Error: {str(e)}")
            return response_error(f"Error al obtener asistencias de la sesión: {str(e)}", 500)

    @staticmethod
    def get_asistencias_por_paciente(paciente_id):
        """Obtener historial de asistencias de un paciente específico"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.get_asistencias_por_paciente - Paciente ID: {paciente_id}")

            # Validar ID
            if not isinstance(paciente_id, int) or paciente_id <= 0:
                return response_error("ID de paciente debe ser un número positivo", 400)

            # Obtener asistencias del paciente
            asistencias = SesionTerapiaComponent.get_asistencias_por_paciente(paciente_id)

            HandleLogs.write_log(f"SesionTerapiaService.get_asistencias_por_paciente - {len(asistencias) if asistencias else 0} asistencias encontradas")
            return response_success(asistencias or [], "Asistencias del paciente obtenidas exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_asistencias_por_paciente - Error: {str(e)}")
            return response_error(f"Error al obtener asistencias del paciente: {str(e)}", 500)

    @staticmethod
    def get_estadisticas_asistencia(sesion_id):
        """Obtener estadísticas de asistencia de una sesión"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.get_estadisticas_asistencia - Sesion ID: {sesion_id}")

            # Validar ID
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            # Obtener estadísticas
            estadisticas = SesionTerapiaComponent.get_estadisticas_asistencia_sesion(sesion_id)

            HandleLogs.write_log(f"SesionTerapiaService.get_estadisticas_asistencia - Estadísticas obtenidas")
            return response_success(estadisticas or {}, "Estadísticas de asistencia obtenidas exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_estadisticas_asistencia - Error: {str(e)}")
            return response_error(f"Error al obtener estadísticas de asistencia: {str(e)}", 500)

    @staticmethod
    def get_asistencia_cronograma(cronograma_id):
        """Obtener asistencia de todos los pacientes para una sesión específica del cronograma"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.get_asistencia_cronograma - Cronograma ID: {cronograma_id}")

            # Validar ID
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)

            # Obtener asistencias
            asistencias = SesionTerapiaComponent.get_asistencias_por_cronograma(cronograma_id)

            HandleLogs.write_log(f"SesionTerapiaService.get_asistencia_cronograma - {len(asistencias) if asistencias else 0} asistencias encontradas")
            return response_success(asistencias or [], "Asistencias obtenidas exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.get_asistencia_cronograma - Error: {str(e)}")
            return response_error(f"Error al obtener asistencias: {str(e)}", 500)

    @staticmethod
    def actualizar_asistencia(cronograma_id, paciente_id):
        """Actualizar asistencia existente de un paciente"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.actualizar_asistencia - Cronograma ID: {cronograma_id}, Paciente ID: {paciente_id}")

            # Validar IDs
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)
            
            if not isinstance(paciente_id, int) or paciente_id <= 0:
                return response_error("ID de paciente debe ser un número positivo", 400)

            # Obtener datos del request
            data = request.json
            if not data:
                return response_error("Datos de asistencia son requeridos", 400)

            # Obtener el usuario del token JWT
            current_user = g.get('usuario_info', {})
            usuario_modificacion = current_user.get('id', 1)

            # Actualizar asistencia
            result = SesionTerapiaComponent.actualizar_asistencia(cronograma_id, paciente_id, data, usuario_modificacion)

            HandleLogs.write_log(f"SesionTerapiaService.actualizar_asistencia - Asistencia actualizada exitosamente")
            return response_success(result, "Asistencia actualizada exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.actualizar_asistencia - Error: {str(e)}")
            return response_error(f"Error al actualizar asistencia: {str(e)}", 500)

    @staticmethod
    def reprogramar_sesion_cronograma(cronograma_id):
        """Reprogramar una sesión específica del cronograma"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.reprogramar_sesion_cronograma - Cronograma ID: {cronograma_id}")

            # Validar ID
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)

            # Obtener datos del request
            data = request.json
            if not data:
                return response_error("Datos de reprogramación son requeridos", 400)

            nueva_fecha = data.get('nueva_fecha')
            nueva_hora = data.get('nueva_hora')
            motivo_reprogramacion = data.get('motivo_reprogramacion', '')
            
            if not nueva_fecha or not nueva_hora:
                return response_error("Nueva fecha y hora son requeridas", 400)
                
            if not motivo_reprogramacion or not motivo_reprogramacion.strip():
                return response_error("Campo 'motivo_reprogramacion' es requerido", 400)

            # Obtener el usuario del token JWT
            current_user = g.get('usuario_info', {})
            usuario_modificacion = current_user.get('id', 1)  # Usar ID del usuario, fallback a 1 (admin)
            
            result = SesionTerapiaComponent.reprogramar_sesion(
                cronograma_id, 
                nueva_fecha, 
                nueva_hora, 
                motivo_reprogramacion, 
                usuario_modificacion
            )
            
            HandleLogs.write_log(f"SesionTerapiaService.reprogramar_sesion_cronograma - Sesión {cronograma_id} reprogramada exitosamente")
            return response_success(result, f"Sesión {cronograma_id} reprogramada exitosamente")
            
        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.reprogramar_sesion_cronograma - Error: {str(e)}")
            return response_error(f"Error al reprogramar sesión: {str(e)}", 500)

    @staticmethod
    def cancelar_sesion_cronograma(cronograma_id):
        """Cancelar una sesión específica del cronograma"""
        try:
            HandleLogs.write_log(f"SesionTerapiaService.cancelar_sesion_cronograma - Cronograma ID: {cronograma_id}")

            # Validar ID
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)

            # Obtener datos del request
            data = request.json or {}
            motivo_cancelacion = data.get('motivo_cancelacion', 'Cancelada por el usuario')
            
            # Obtener el usuario del token JWT
            current_user = g.get('usuario_info', {})
            usuario_modificacion = current_user.get('id', 1)  # Usar ID del usuario, fallback a 1 (admin)
            
            result = SesionTerapiaComponent.cancelar_sesion(
                cronograma_id, 
                motivo_cancelacion, 
                usuario_modificacion
            )
            
            HandleLogs.write_log(f"SesionTerapiaService.cancelar_sesion_cronograma - Sesión {cronograma_id} cancelada exitosamente")
            return response_success(result, f"Sesión {cronograma_id} cancelada exitosamente")
            
        except Exception as e:
            HandleLogs.write_error(f"SesionTerapiaService.cancelar_sesion_cronograma - Error: {str(e)}")
            return response_error(f"Error al cancelar sesión: {str(e)}", 500)