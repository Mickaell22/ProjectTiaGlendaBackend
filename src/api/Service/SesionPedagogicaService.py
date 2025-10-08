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
        """Obtener sesiones pedagógicas filtradas según rol y centro del usuario"""
        try:
            HandleLogs.write_log("SesionPedagogicaService.get_sesiones - Iniciando")

            # Obtener información del usuario actual
            current_user = getattr(request, 'current_user', {})
            user_role = current_user.get('rol', '').lower()
            user_centro_id = current_user.get('id_centro')
            personal_id = current_user.get('personal_id')

            # Filtrado basado en rol
            if user_role == 'administrador':
                # Administradores ven todas las sesiones de su centro
                if user_centro_id:
                    sesiones = SesionPedagogicaComponent.get_sesiones_by_centro(user_centro_id)
                    HandleLogs.write_log(f"SesionPedagogicaService.get_sesiones - Admin obteniendo sesiones del centro {user_centro_id}")
                else:
                    # Fallback si no tiene centro asignado
                    sesiones = SesionPedagogicaComponent.get_sesiones()
                    HandleLogs.write_log("SesionPedagogicaService.get_sesiones - Admin obteniendo todas las sesiones (sin centro)")
            elif user_role in ['pedagógico', 'pedagogo']:
                # Pedagogos ven solo sesiones donde están asignados como responsables
                if personal_id and user_centro_id:
                    sesiones = SesionPedagogicaComponent.get_sesiones_by_pedagogo(personal_id, user_centro_id)
                    HandleLogs.write_log(f"SesionPedagogicaService.get_sesiones - {user_role} obteniendo sesiones asignadas (personal_id: {personal_id}, centro: {user_centro_id})")
                else:
                    # Si no tiene personal_id, mostrar sesiones del centro
                    if user_centro_id:
                        sesiones = SesionPedagogicaComponent.get_sesiones_by_centro(user_centro_id)
                        HandleLogs.write_log(f"SesionPedagogicaService.get_sesiones - {user_role} obteniendo sesiones del centro {user_centro_id} (fallback)")
                    else:
                        sesiones = []
                        HandleLogs.write_log(f"SesionPedagogicaService.get_sesiones - {user_role} sin centro asignado - lista vacía")
            else:
                # Otros roles - acceso limitado solo a su centro
                if user_centro_id:
                    sesiones = SesionPedagogicaComponent.get_sesiones_by_centro(user_centro_id)
                    HandleLogs.write_log(f"SesionPedagogicaService.get_sesiones - Rol {user_role} obteniendo sesiones del centro {user_centro_id}")
                else:
                    sesiones = []
                    HandleLogs.write_log(f"SesionPedagogicaService.get_sesiones - Rol {user_role} sin centro - lista vacía")

            if sesiones:
                # Formatear datos para respuesta
                sesiones_formateadas = []
                for sesion in sesiones:
                    sesion_data = {
                        'id': sesion['id'],
                        'codigo_sesion': sesion['codigo_sesion'],
                        'titulo': sesion.get('titulo', sesion.get('nombre_clase', '')),
                        'pedagogo': {
                            'id': sesion['pedagogo_id'],
                            'nombre': sesion.get('pedagogo_nombre', 'No asignado')
                        },
                        'pedagogo_nombre': sesion.get('pedagogo_nombre', 'No asignado'),
                        'especialidad': {
                            'id': sesion['especialidad_id'],
                            'nombre': sesion.get('especialidad_nombre', 'No asignada'),
                            'area': sesion.get('especialidad_area', 'No especificada')
                        },
                        'especialidad_nombre': sesion.get('especialidad_nombre', 'No asignada'),
                        'especialidad_area': sesion.get('especialidad_area', 'No especificada'),
                        'fecha_inicio': sesion['fecha_inicio'].isoformat() if hasattr(sesion['fecha_inicio'], 'isoformat') else sesion['fecha_inicio'],
                        'fecha_fin': sesion['fecha_fin'].isoformat() if hasattr(sesion['fecha_fin'], 'isoformat') else sesion['fecha_fin'],
                        'dias_semana': sesion['dias_semana'] if isinstance(sesion['dias_semana'], list) else (sesion['dias_semana'].split(',') if sesion['dias_semana'] else []),
                        'hora_inicio': str(sesion['hora_inicio'])[0:5] if sesion['hora_inicio'] else None,  # Solo HH:MM
                        'duracion_minutos': sesion['duracion_minutos'],
                        'numero_clases_programadas': sesion.get('numero_clases_programadas', 20),
                        'nivel_academico': sesion['nivel_academico'],
                        'capacidad_maxima': sesion['capacidad_maxima'],
                        'modalidad': sesion.get('modalidad', 'presencial'),
                        'costo_total': float(sesion.get('costo_total', 0)),
                        'costo_por_clase': float(sesion.get('costo_por_clase', 0)),
                        'periodo_academico': sesion.get('periodo_academico', ''),
                        'adaptacion_curricular': sesion.get('adaptacion_curricular', ''),
                        'estado': sesion['estado'],
                        'observaciones': sesion.get('observaciones', ''),
                        'total_estudiantes': sesion.get('total_estudiantes', 0),
                        'clases_programadas': sesion.get('clases_programadas', 0),
                        'clases_realizadas': sesion.get('clases_realizadas', 0),
                        'progreso_porcentaje': round(
                            (sesion.get('clases_realizadas', 0) / sesion.get('clases_programadas', 1) * 100), 2) if sesion.get('clases_programadas', 0) > 0 else 0,
                        'fecha_creacion': sesion['fecha_creacion'].isoformat() if hasattr(sesion['fecha_creacion'], 'isoformat') else sesion['fecha_creacion']
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
    def get_cronograma_sesiones(filtros=None):
        """Obtener cronograma de sesiones pedagógicas con filtros"""
        try:
            HandleLogs.write_log("SesionPedagogicaService.get_cronograma_sesiones - Iniciando")

            # Convertir filtros de query params si es necesario
            filtros_procesados = {}
            if filtros:
                if 'especialidad' in filtros and filtros['especialidad']:
                    filtros_procesados['especialidad'] = filtros['especialidad']
                if 'pedagogo' in filtros and filtros['pedagogo']:
                    filtros_procesados['pedagogo'] = filtros['pedagogo']
                if 'semana' in filtros and filtros['semana']:
                    filtros_procesados['semana'] = filtros['semana']

            sesiones = SesionPedagogicaComponent.get_cronograma_sesiones(filtros_procesados)

            if sesiones:
                # Formatear datos para cronograma
                sesiones_cronograma = []
                for sesion in sesiones:
                    # Formatear hora_fin si no existe
                    hora_fin = sesion.get('hora_fin')
                    if not hora_fin and sesion.get('hora_inicio') and sesion.get('duracion_minutos'):
                        try:
                            from datetime import datetime, timedelta
                            hora_inicio_obj = datetime.strptime(str(sesion['hora_inicio']), '%H:%M:%S')
                            hora_fin_obj = hora_inicio_obj + timedelta(minutes=sesion['duracion_minutos'])
                            hora_fin = hora_fin_obj.strftime('%H:%M:%S')
                        except:
                            hora_fin = None

                    sesion_data = {
                        'id': sesion['id'],
                        'codigo_sesion': sesion['codigo_sesion'],
                        'titulo': sesion.get('titulo', sesion.get('nombre_clase', '')),
                        'pedagogo': {
                            'id': sesion['pedagogo_id'],
                            'nombre': sesion['pedagogo_nombre']
                        },
                        'pedagogo_nombre': sesion['pedagogo_nombre'],  # Para compatibilidad
                        'especialidad': {
                            'id': sesion['especialidad_id'],
                            'nombre': sesion['especialidad_nombre'],
                            'area': sesion['especialidad_area']
                        },
                        'dias_programados': sesion.get('dias_programados', []),
                        'hora_inicio': str(sesion['hora_inicio'])[0:5] if sesion['hora_inicio'] else None,  # Solo HH:MM
                        'hora_fin': str(hora_fin)[0:5] if hora_fin else None,  # Solo HH:MM
                        'duracion_minutos': sesion['duracion_minutos'],
                        'nivel_academico': sesion['nivel_academico'],
                        'capacidad_maxima': sesion['capacidad_maxima'],
                        'modalidad': sesion.get('modalidad', 'presencial'),
                        'estado': sesion['estado'],
                        'total_estudiantes': sesion['total_estudiantes'],
                        'fecha_inicio': sesion['fecha_inicio'].isoformat() if sesion['fecha_inicio'] else None,
                        'fecha_fin': sesion['fecha_fin'].isoformat() if sesion['fecha_fin'] else None
                    }
                    sesiones_cronograma.append(sesion_data)

                HandleLogs.write_log(f"SesionPedagogicaService.get_cronograma_sesiones - {len(sesiones_cronograma)} sesiones obtenidas")
                return response_success(sesiones_cronograma, "Cronograma de sesiones obtenido exitosamente")
            else:
                return response_success([], "No hay sesiones pedagógicas activas para el cronograma")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.get_cronograma_sesiones - Error: {str(e)}")
            return response_error(f"Error al obtener cronograma de sesiones: {str(e)}", 500)

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
                    'titulo': sesion.get('titulo', sesion.get('nombre_clase', '')),
                    'pedagogo': {
                        'id': sesion.get('pedagogo_id', sesion.get('id_educador')),
                        'nombre': sesion['pedagogo_nombre']
                    },
                    'especialidad': {
                        'id': sesion.get('especialidad_id', sesion.get('id_especialidad')),
                        'nombre': sesion['especialidad_nombre'],
                        'area': sesion['especialidad_area']
                    },
                    'fecha_inicio': sesion['fecha_inicio'].isoformat() if sesion['fecha_inicio'] else None,
                    'fecha_fin': sesion['fecha_fin'].isoformat() if sesion['fecha_fin'] else None,
                    'dias_semana': sesion['dias_semana'] if isinstance(sesion['dias_semana'], list) else (sesion['dias_semana'].split(',') if sesion['dias_semana'] else []),
                    'hora_inicio': str(sesion['hora_inicio'])[0:5] if sesion['hora_inicio'] else None,  # Solo HH:MM
                    'duracion_minutos': sesion['duracion_minutos'],
                    'numero_clases_programadas': sesion.get('numero_clases_programadas', 20),
                    'nivel_academico': sesion['nivel_academico'],
                    'capacidad_maxima': sesion['capacidad_maxima'],
                    'modalidad': sesion.get('modalidad', 'presencial'),
                    'costo_total': float(sesion.get('costo_total', 0)),
                    'costo_por_clase': float(sesion.get('costo_por_clase', 0)),
                    'periodo_academico': sesion.get('periodo_academico', ''),
                    'adaptacion_curricular': sesion.get('adaptacion_curricular', ''),
                    'estado': sesion['estado'],
                    'observaciones': sesion.get('observaciones', ''),
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
                             'dias_semana', 'hora_inicio']
            
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

            # Validaciones básicas
            if 'numero_clases_programadas' in data and data['numero_clases_programadas'] <= 0:
                return response_error("El número de clases programadas debe ser mayor a 0", 400)
            
            if 'capacidad_maxima' in data and data['capacidad_maxima'] <= 0:
                return response_error("La capacidad máxima debe ser mayor a 0", 400)
                
            if 'costo_total' in data and data['costo_total'] < 0:
                return response_error("El costo total no puede ser negativo", 400)

            # Validar relacion entre costo_total y costo_por_clase
            if 'costo_total' in data and 'costo_por_clase' in data and 'numero_clases_programadas' in data:
                if data['costo_total'] > 0 and data['costo_por_clase'] > 0 and data['numero_clases_programadas'] > 0:
                    costo_calculado = data['costo_total'] / data['numero_clases_programadas']
                    diferencia = abs(costo_calculado - data['costo_por_clase'])
                    if diferencia > 0.01:  # Tolerancia de 1 centavo
                        return response_error(
                            f"El costo por clase ({data['costo_por_clase']}) no coincide con el costo total "
                            f"({data['costo_total']}) dividido por el numero de clases ({data['numero_clases_programadas']}). "
                            f"Costo esperado por clase: {costo_calculado:.2f}",
                            400
                        )

            # Validar días de la semana
            dias_validos = ['lunes', 'martes', 'miercoles', 'miércoles', 'jueves', 'viernes', 'sabado', 'sábado', 'domingo']
            dias_sesion = [dia.strip().lower() for dia in data['dias_semana']] if isinstance(data['dias_semana'], list) else [dia.strip().lower() for dia in data['dias_semana'].split(',')]
            
            for dia in dias_sesion:
                if dia not in dias_validos:
                    return response_error(f"Día de la semana inválido: {dia}", 400)

            # Agregar usuario actual
            data['usuario_creacion'] = request.current_user['id']
            data['id_centro'] = request.current_user.get('centro', {}).get('id', 1)
            
            # Convert dias_semana to array format for database
            if isinstance(data['dias_semana'], list):
                data['dias_semana'] = '{' + ','.join(data['dias_semana']) + '}'
            elif isinstance(data['dias_semana'], str):
                dias_list = [dia.strip().lower() for dia in data['dias_semana'].split(',')]
                data['dias_semana'] = '{' + ','.join(dias_list) + '}'

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

            # Validaciones básicas
            if 'duracion_minutos' in data and data['duracion_minutos'] <= 0:
                return response_error("La duración en minutos debe ser mayor a 0", 400)
            
            if 'capacidad_maxima' in data and data['capacidad_maxima'] <= 0:
                return response_error("La capacidad máxima debe ser mayor a 0", 400)

            # Validar días de la semana si se proporcionan
            if 'dias_semana' in data:
                dias_validos = ['lunes', 'martes', 'miercoles', 'miércoles', 'jueves', 'viernes', 'sabado', 'sábado', 'domingo']
                dias_sesion = [dia.strip().lower() for dia in data['dias_semana']] if isinstance(data['dias_semana'], list) else [dia.strip().lower() for dia in data['dias_semana'].split(',')]
                
                for dia in dias_sesion:
                    if dia not in dias_validos:
                        return response_error(f"Día de la semana inválido: {dia}", 400)

            # Agregar usuario de modificación
            data['usuario_modificacion'] = request.current_user['id']

            # Merge partial data with existing session data
            update_data = {
                'titulo': data.get('titulo', sesion_existente.get('titulo', sesion_existente.get('nombre_clase', ''))),
                'pedagogo_id': data.get('pedagogo_id', sesion_existente.get('pedagogo_id', sesion_existente.get('id_educador'))),
                'especialidad_id': data.get('especialidad_id', sesion_existente.get('especialidad_id', sesion_existente.get('id_especialidad'))),
                'fecha_inicio': data.get('fecha_inicio', sesion_existente['fecha_inicio']),
                'fecha_fin': data.get('fecha_fin', sesion_existente['fecha_fin']),
                'dias_semana': data.get('dias_semana', sesion_existente['dias_semana']),
                'hora_inicio': data.get('hora_inicio', sesion_existente['hora_inicio']),
                'duracion_minutos': data.get('duracion_minutos', sesion_existente['duracion_minutos']),
                'nivel_academico': data.get('nivel_academico', sesion_existente['nivel_academico']),
                'capacidad_maxima': data.get('capacidad_maxima', sesion_existente['capacidad_maxima']),
                'adaptacion_curricular': data.get('adaptacion_curricular', sesion_existente.get('adaptacion_curricular', '')),
                'estado': data.get('estado', sesion_existente['estado']),
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

            # Verificar capacidad máxima
            sesion_info = SesionPedagogicaComponent.get_sesion_by_id(sesion_id)
            if not sesion_info:
                return response_error(f"Sesión pedagógica con ID {sesion_id} no encontrada", 404)
            
            capacidad_maxima = sesion_info.get('capacidad_maxima', 0)
            if capacidad_maxima > 0:
                estudiantes_actuales = SesionPedagogicaComponent.get_estudiantes_sesion(sesion_id)
                if estudiantes_actuales and len(estudiantes_actuales) >= capacidad_maxima:
                    return response_error(f"La sesión ha alcanzado su capacidad máxima de {capacidad_maxima} estudiantes", 400)

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
    def get_estudiantes_retirados(sesion_id):
        """Obtener estudiantes retirados de una sesión pedagógica"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.get_estudiantes_retirados - Sesión: {sesion_id}")

            estudiantes = SesionPedagogicaComponent.get_estudiantes_retirados_sesion(sesion_id)

            if estudiantes:
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
                        'observaciones_estudiante': estudiante['observaciones_estudiante'],
                        'estado': estudiante['estado']
                    }
                    estudiantes_formateados.append(estudiante_data)

                return response_success(estudiantes_formateados, "Estudiantes retirados obtenidos exitosamente")
            else:
                return response_success([], "No hay estudiantes retirados en esta sesión")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.get_estudiantes_retirados - Error: {str(e)}")
            return response_error(f"Error al obtener estudiantes retirados: {str(e)}", 500)

    @staticmethod
    def reincorporar_estudiante(sesion_id, paciente_id):
        """Reincorporar un estudiante retirado a una sesión pedagógica"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.reincorporar_estudiante - Sesión: {sesion_id}, Paciente: {paciente_id}")

            # Reincorporar estudiante
            SesionPedagogicaComponent.reincorporar_estudiante_sesion(sesion_id, paciente_id)

            HandleLogs.write_log(f"SesionPedagogicaService.reincorporar_estudiante - Estudiante reincorporado")
            return response_success({
                'sesion_id': sesion_id,
                'paciente_id': paciente_id
            }, "Estudiante reincorporado a la sesión pedagógica exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.reincorporar_estudiante - Error: {str(e)}")
            return response_error(f"Error al reincorporar estudiante: {str(e)}", 500)

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
                        'hora_fin': str(clase['hora_fin']) if clase['hora_fin'] else None,
                        'tema_clase': clase['tema_clase'],
                        'estado': clase['estado'],
                        'fecha_realizacion': clase['fecha_realizacion'].isoformat() if clase['fecha_realizacion'] else None,
                        'objetivos_clase': clase['objetivos_clase'],
                        'material_requerido': clase['material_requerido'],
                        'observaciones': clase['observaciones'],
                        'motivo_reprogramacion': clase.get('motivo_reprogramacion'),
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
        """Obtener lista de pedagogos disponibles para asignar a sesiones (filtrados por centro del usuario)"""
        try:
            HandleLogs.write_log("SesionPedagogicaService.get_pedagogos_disponibles - Iniciando")

            from src.api.Components.PersonalComponent import PersonalComponent

            # Obtener información del usuario actual para filtrado por centro
            current_user = getattr(request, 'current_user', {})
            user_centro_id = current_user.get('id_centro')

            # Obtener personal del área pedagógica filtrado por centro
            if user_centro_id:
                pedagogos_result = PersonalComponent.get_personal_by_area_and_centro('pedagogico', user_centro_id)
                HandleLogs.write_log(f"SesionPedagogicaService.get_pedagogos_disponibles - Filtrando por centro {user_centro_id}")
            else:
                pedagogos_result = PersonalComponent.get_personal_by_area('pedagogico')
                HandleLogs.write_log("SesionPedagogicaService.get_pedagogos_disponibles - Sin filtro de centro")

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

    # ============================================
    # MÉTODOS PARA SISTEMA DE ASISTENCIAS
    # ============================================

    @staticmethod
    def registrar_asistencia(cronograma_id, estudiante_id):
        """Registrar nueva asistencia de estudiante"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.registrar_asistencia - Cronograma: {cronograma_id}, Estudiante: {estudiante_id}")

            # Obtener y validar datos UTF-8
            from src.utils.general.utf8_helper import UTF8Helper
            data, error_msg = UTF8Helper.safe_get_json()
            if error_msg:
                return response_error(error_msg, 400)

            if not data:
                return response_error("No se enviaron datos de asistencia", 400)

            # Validar IDs
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)
            
            if not isinstance(estudiante_id, int) or estudiante_id <= 0:
                return response_error("ID de estudiante debe ser un número positivo", 400)

            # Agregar usuario actual
            data['usuario_creacion'] = request.current_user['id']

            # Registrar asistencia
            asistencia_id = SesionPedagogicaComponent.registrar_asistencia(cronograma_id, estudiante_id, data)

            HandleLogs.write_log(f"SesionPedagogicaService.registrar_asistencia - Asistencia {asistencia_id} registrada exitosamente")
            return response_success({
                'asistencia_id': asistencia_id,
                'cronograma_id': cronograma_id,
                'estudiante_id': estudiante_id
            }, "Asistencia registrada exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.registrar_asistencia - Error: {str(e)}")
            return response_error(f"Error al registrar asistencia: {str(e)}", 500)

    @staticmethod
    def actualizar_asistencia(cronograma_id, estudiante_id):
        """Actualizar asistencia existente"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.actualizar_asistencia - Cronograma: {cronograma_id}, Estudiante: {estudiante_id}")

            # Obtener y validar datos UTF-8
            from src.utils.general.utf8_helper import UTF8Helper
            data, error_msg = UTF8Helper.safe_get_json()
            if error_msg:
                return response_error(error_msg, 400)

            if not data:
                return response_error("No se enviaron datos para actualizar", 400)

            # Validar IDs
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)
            
            if not isinstance(estudiante_id, int) or estudiante_id <= 0:
                return response_error("ID de estudiante debe ser un número positivo", 400)

            # Agregar usuario de modificación
            data['usuario_modificacion'] = request.current_user['id']

            # Actualizar asistencia
            SesionPedagogicaComponent.actualizar_asistencia(cronograma_id, estudiante_id, data)

            HandleLogs.write_log(f"SesionPedagogicaService.actualizar_asistencia - Asistencia actualizada exitosamente")
            return response_success({
                'cronograma_id': cronograma_id,
                'estudiante_id': estudiante_id
            }, "Asistencia actualizada exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.actualizar_asistencia - Error: {str(e)}")
            return response_error(f"Error al actualizar asistencia: {str(e)}", 500)

    @staticmethod
    def get_asistencias_por_sesion(sesion_id):
        """Obtener todas las asistencias de una sesión"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.get_asistencias_por_sesion - Sesión: {sesion_id}")

            # Validar ID
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            asistencias = SesionPedagogicaComponent.get_asistencias_por_sesion(sesion_id)

            # Formatear asistencias
            asistencias_formateadas = []
            for asistencia in asistencias:
                asistencia_data = {
                    'id': asistencia['id'],
                    'cronograma_id': asistencia['id_cronograma'],
                    'estudiante_id': asistencia['id_paciente'],
                    'fecha_programada': asistencia['fecha_programada'].isoformat() if asistencia.get('fecha_programada') else None,
                    'hora_programada': str(asistencia['hora_programada']) if asistencia.get('hora_programada') else None,
                    'numero_clase': asistencia.get('numero_clase_semanal'),
                    'estudiante_nombre': asistencia.get('estudiante_nombre'),
                    'estudiante_cedula': asistencia.get('estudiante_cedula'),
                    'estudiante': {
                        'nombre': asistencia.get('estudiante_nombre'),
                        'cedula': asistencia.get('estudiante_cedula')
                    },
                    'asistio': asistencia.get('asistio'),
                    'llegada_tardanza_minutos': asistencia.get('llegada_tardanza_minutos', 0),
                    'estado_asistencia': asistencia.get('estado_asistencia'),
                    'observaciones_educador': asistencia.get('observaciones_educador'),
                    'objetivos_trabajados': asistencia.get('objetivos_trabajados'),
                    'participacion_clase': asistencia.get('participacion_clase'),
                    'actividades_completadas': asistencia.get('actividades_completadas'),
                    'tareas_asignadas': asistencia.get('tareas_asignadas'),
                    'calificacion_clase': asistencia.get('calificacion_clase'),
                    'fecha_registro': asistencia['fecha_registro'].isoformat() if asistencia.get('fecha_registro') else None
                }
                asistencias_formateadas.append(asistencia_data)

            HandleLogs.write_log(f"SesionPedagogicaService.get_asistencias_por_sesion - {len(asistencias_formateadas)} asistencias encontradas")
            return response_success(asistencias_formateadas, "Asistencias obtenidas exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.get_asistencias_por_sesion - Error: {str(e)}")
            return response_error(f"Error al obtener asistencias: {str(e)}", 500)

    @staticmethod
    def get_control_asistencia(cronograma_id):
        """Obtener control de asistencia completo para una clase"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.get_control_asistencia - Cronograma: {cronograma_id}")

            # Validar ID
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)

            control_data = SesionPedagogicaComponent.get_control_asistencia(cronograma_id)

            if not control_data:
                return response_error(f"Cronograma con ID {cronograma_id} no encontrado", 404)

            # Formatear datos de control
            clase_info = None
            estudiantes = []

            for registro in control_data:
                # Información de la clase (solo una vez)
                if not clase_info:
                    clase_info = {
                        'cronograma_id': registro['cronograma_id'],
                        'numero_clase': registro['numero_clase_semanal'],
                        'fecha_programada': registro['fecha_programada'].isoformat() if registro['fecha_programada'] else None,
                        'hora_inicio': str(registro['hora_inicio']) if registro['hora_inicio'] else None,
                        'tema_clase': registro['tema_clase'],
                        'sesion': {
                            'titulo': registro['sesion_titulo'],
                            'codigo_sesion': registro['codigo_sesion']
                        },
                        'educador_nombre': registro['educador_nombre']
                    }

                # Información de estudiantes y asistencias
                if registro['estudiante_id']:
                    estudiante_data = {
                        'estudiante_id': registro['estudiante_id'],
                        'estudiante_nombre': registro['estudiante_nombre'],
                        'estudiante_cedula': registro['estudiante_cedula'],
                        'nombre': registro['estudiante_nombre'],
                        'cedula': registro['estudiante_cedula'],
                        'asistio': registro['asistio'],
                        'llegada_tardanza_minutos': registro['llegada_tardanza_minutos'],
                        'tardanza_minutos': registro['llegada_tardanza_minutos'],  # Mantener ambos nombres
                        'estado_asistencia': registro['estado_asistencia'],
                        'observaciones_educador': registro['observaciones_educador'],
                        'observaciones': registro['observaciones_educador'],  # Mantener ambos nombres
                        'calificacion_clase': registro['calificacion_clase'],
                        'calificacion': registro['calificacion_clase'],  # Mantener ambos nombres
                        'fecha_registro': registro['fecha_registro'].isoformat() if registro.get('fecha_registro') else None,
                        'objetivos_trabajados': registro['objetivos_trabajados'],
                        'participacion_clase': registro['participacion_clase'],
                        'tareas_asignadas': registro['tareas_asignadas'],
                        'actividades_completadas': registro['actividades_completadas']
                    }
                    estudiantes.append(estudiante_data)

            control_completo = {
                'clase': clase_info,
                'estudiantes': estudiantes,
                'resumen': {
                    'total_estudiantes': len(estudiantes),
                    'presentes': len([e for e in estudiantes if e['asistio']]),
                    'ausentes': len([e for e in estudiantes if not e['asistio']]),
                    'con_tardanza': len([e for e in estudiantes if e['tardanza_minutos'] and e['tardanza_minutos'] > 0])
                }
            }

            return response_success(control_completo, "Control de asistencia obtenido exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.get_control_asistencia - Error: {str(e)}")
            return response_error(f"Error al obtener control de asistencia: {str(e)}", 500)

    @staticmethod
    def marcar_clase_realizada(cronograma_id):
        """Marcar clase como realizada con observaciones"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.marcar_clase_realizada - Cronograma: {cronograma_id}")

            # Validar ID
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)

            # Obtener las observaciones del request JSON
            data = request.get_json()
            observaciones = data.get('observaciones', '') if data else ''

            # Marcar como realizada con observaciones
            SesionPedagogicaComponent.marcar_clase_realizada(cronograma_id, request.current_user['id'], observaciones)

            return response_success({
                'cronograma_id': cronograma_id,
                'observaciones': observaciones
            }, "Clase marcada como realizada exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.marcar_clase_realizada - Error: {str(e)}")
            return response_error(f"Error al marcar clase como realizada: {str(e)}", 500)

    @staticmethod
    def reprogramar_clase(cronograma_id):
        """Reprogramar una clase - CREAR NUEVA CLASE EN LUGAR DE ACTUALIZAR LA EXISTENTE"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.reprogramar_clase - Cronograma: {cronograma_id}")

            data = request.get_json()
            if not data:
                return response_error("No se enviaron datos para reprogramar", 400)

            # Validar campos requeridos
            if 'nueva_fecha' not in data or 'nueva_hora' not in data:
                return response_error("Se requieren nueva_fecha y nueva_hora", 400)

            try:
                nueva_fecha = datetime.strptime(data['nueva_fecha'], '%Y-%m-%d').date()
                nueva_hora = datetime.strptime(data['nueva_hora'], '%H:%M').time()
            except ValueError:
                return response_error("Formato de fecha u hora inválido", 400)

            motivo = data.get('motivo_reprogramacion', data.get('motivo', 'Reprogramación solicitada'))

            # Reprogramar clase - ahora retorna el ID de la nueva clase creada
            nueva_clase_id = SesionPedagogicaComponent.reprogramar_clase(cronograma_id, nueva_fecha, nueva_hora, motivo, request.current_user['id'])

            return response_success({
                'cronograma_id_original': cronograma_id,
                'cronograma_id_nuevo': nueva_clase_id,
                'nueva_fecha': nueva_fecha.isoformat(),
                'nueva_hora': str(nueva_hora),
                'motivo': motivo
            }, "Clase reprogramada exitosamente. Se creó una nueva clase programada.")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.reprogramar_clase - Error: {str(e)}")
            return response_error(f"Error al reprogramar clase: {str(e)}", 500)

    @staticmethod
    def cancelar_clase(cronograma_id):
        """Cancelar una clase"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.cancelar_clase - Cronograma: {cronograma_id}")

            data = request.get_json()
            motivo = data.get('motivo', 'Cancelación solicitada') if data else 'Cancelación solicitada'

            # Cancelar clase
            SesionPedagogicaComponent.cancelar_clase(cronograma_id, motivo, request.current_user['id'])

            return response_success({
                'cronograma_id': cronograma_id
            }, "Clase cancelada exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.cancelar_clase - Error: {str(e)}")
            return response_error(f"Error al cancelar clase: {str(e)}", 500)

    @staticmethod
    def actualizar_cronograma_clase(cronograma_id):
        """Actualizar información de cronograma de clase (tema, objetivos, materiales)"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.actualizar_cronograma_clase - Cronograma: {cronograma_id}")

            # Validar ID
            if not isinstance(cronograma_id, int) or cronograma_id <= 0:
                return response_error("ID de cronograma debe ser un número positivo", 400)

            # Obtener datos JSON
            data = request.get_json()
            if not data:
                return response_error("Datos de actualización son requeridos", 400)

            # Preparar datos de actualización (solo campos permitidos)
            update_data = {}

            if 'tema_clase' in data:
                update_data['tema_clase'] = data['tema_clase'].strip() if data['tema_clase'] else None

            if 'objetivos_clase' in data:
                update_data['objetivos_clase'] = data['objetivos_clase'].strip() if data['objetivos_clase'] else None

            if 'materiales_necesarios' in data:
                update_data['materiales_necesarios'] = data['materiales_necesarios'].strip() if data['materiales_necesarios'] else None

            if not update_data:
                return response_error("No se proporcionaron campos válidos para actualizar", 400)

            # Actualizar en base de datos
            from src.utils.database.connection_db import DataBaseHandle

            # Construir query dinámica
            set_clauses = []
            params = []

            for field, value in update_data.items():
                set_clauses.append(f"{field} = %s")
                params.append(value)

            # Agregar fecha de modificación y usuario
            set_clauses.append("fecha_modificacion = CURRENT_TIMESTAMP")
            set_clauses.append("usuario_modificacion = %s")
            params.append(request.current_user['id'])

            # Agregar cronograma_id al final
            params.append(cronograma_id)

            query = f"""
                UPDATE cronograma_clases
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """

            result = DataBaseHandle.ExecuteNonQuery(query, tuple(params))

            if not result:
                return response_error("No se pudo actualizar el cronograma de clase", 500)

            HandleLogs.write_log(f"SesionPedagogicaService.actualizar_cronograma_clase - Actualizado exitosamente")
            return response_success({
                'cronograma_id': cronograma_id,
                'campos_actualizados': list(update_data.keys())
            }, "Cronograma de clase actualizado exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.actualizar_cronograma_clase - Error: {str(e)}")
            return response_error(f"Error al actualizar cronograma de clase: {str(e)}", 500)

    # ============================================
    # MÉTODOS DE ENLACES PÚBLICOS PEDAGÓGICOS
    # ============================================

    @staticmethod
    def generar_enlace_publico(sesion_id):
        """Generar un enlace público para una sesión pedagógica"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.generar_enlace_publico - Sesión: {sesion_id}")

            data = request.get_json()
            current_user = request.current_user

            # Validar ID de sesión
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            # Validar datos de entrada
            if not data:
                return response_error("Datos requeridos", 400)

            descripcion = data.get('description', '').strip()
            duracion_horas = data.get('duration_hours', 168)  # 7 días por defecto

            if not descripcion:
                return response_error("La descripción es requerida", 400)

            try:
                duracion_horas = int(duracion_horas)
                if duracion_horas <= 0:
                    return response_error("La duración debe ser mayor a 0 horas", 400)
            except (ValueError, TypeError):
                return response_error("La duración debe ser un número válido", 400)

            # Preparar datos del enlace
            enlace_data = {
                'sesion_id': sesion_id,
                'descripcion': descripcion,
                'duracion_horas': duracion_horas,
                'usuario_creacion': current_user['id']
            }

            # Generar enlace público
            result = SesionPedagogicaComponent.generar_token_publico(enlace_data)

            if result:
                HandleLogs.write_log(f"SesionPedagogicaService.generar_enlace_publico - Enlace generado para sesión {sesion_id}")
                return response_success(result, "Enlace público generado exitosamente")
            else:
                return response_error("No se pudo generar el enlace público", 500)

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.generar_enlace_publico - Error: {str(e)}")
            return response_error(f"Error al generar enlace público: {str(e)}", 500)

    @staticmethod
    def obtener_enlaces_publicos(sesion_id):
        """Obtener enlaces públicos activos para una sesión pedagógica"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.obtener_enlaces_publicos - Sesión: {sesion_id}")

            # Validar ID de sesión
            if not isinstance(sesion_id, int) or sesion_id <= 0:
                return response_error("ID de sesión debe ser un número positivo", 400)

            # Obtener enlaces públicos
            enlaces = SesionPedagogicaComponent.obtener_tokens_publicos(sesion_id)

            HandleLogs.write_log(f"SesionPedagogicaService.obtener_enlaces_publicos - {len(enlaces)} enlaces encontrados")
            return response_success({
                'enlaces': enlaces,
                'total': len(enlaces)
            }, "Enlaces públicos obtenidos exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.obtener_enlaces_publicos - Error: {str(e)}")
            return response_error(f"Error al obtener enlaces públicos: {str(e)}", 500)

    @staticmethod
    def invalidar_enlace_publico(token):
        """Invalidar un enlace público específico"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.invalidar_enlace_publico - Token: {token[:10]}...")

            # Validar token
            if not token or len(token) < 10:
                return response_error("Token inválido", 400)

            # Obtener el usuario del token JWT
            current_user = getattr(request, 'current_user', {})
            usuario_modificacion = current_user.get('id', 1)

            # Invalidar el token
            result = SesionPedagogicaComponent.invalidar_token_publico(token, usuario_modificacion)

            HandleLogs.write_log(f"SesionPedagogicaService.invalidar_enlace_publico - Token invalidado exitosamente")
            return response_success(result, "Enlace público invalidado exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.invalidar_enlace_publico - Error: {str(e)}")
            return response_error(f"Error al invalidar enlace público: {str(e)}", 500)

    @staticmethod
    def ver_sesion_publica(token):
        """Ver información pública de una sesión pedagógica usando token (sin autenticación)"""
        try:
            HandleLogs.write_log(f"SesionPedagogicaService.ver_sesion_publica - Token: {token[:10]}...")

            # Validar token
            if not token or len(token) < 10:
                return response_error("Token inválido", 400)

            # Verificar y obtener información de la sesión usando el token
            result = SesionPedagogicaComponent.obtener_sesion_por_token_publico(token)

            if not result:
                return response_error("Token inválido o expirado", 401)

            HandleLogs.write_log(f"SesionPedagogicaService.ver_sesion_publica - Información de sesión obtenida exitosamente")
            return response_success(result, "Información de sesión obtenida exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"SesionPedagogicaService.ver_sesion_publica - Error: {str(e)}")
            return response_error(f"Error al obtener información de sesión: {str(e)}", 500)