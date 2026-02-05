from flask import request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error, response_inserted
from src.utils.general.validators import Validators
from src.api.Components.EspecialidadComponent import EspecialidadComponent


class EspecialidadService:

    @staticmethod
    def get_especialidades():
        """Obtener lista de todas las especialidades, opcionalmente filtradas por centro"""
        try:
            HandleLogs.write_log("EspecialidadService.get_especialidades - Iniciando")

            # Obtener parámetro de centro de la query string
            id_centro = request.args.get('centro', type=int)

            result = EspecialidadComponent.get_all_especialidades(id_centro)

            if result['success']:
                centro_info = f" del centro {id_centro}" if id_centro else ""
                HandleLogs.write_log(f"EspecialidadService.get_especialidades - Especialidades{centro_info} obtenidas exitosamente")
                return response_success(result['data'], f"Lista de especialidades{centro_info} obtenida correctamente")
            else:
                HandleLogs.write_error(f"EspecialidadService.get_especialidades - Error: {result['message']}")
                return response_error("Error obteniendo especialidades", 500)

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadService.get_especialidades - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_especialidades_by_area(area):
        """Obtener especialidades por área específica, opcionalmente filtradas por centro"""
        try:
            HandleLogs.write_log(f"EspecialidadService.get_especialidades_by_area - Área: {area}")

            # Validar área
            valid_areas = ['Especialidad terapéutica', 'Especialidad pedagógica']
            if area not in valid_areas:
                return response_error(f"Área invalida. Debe ser una de: {', '.join(valid_areas)}", 400)

            # Obtener parámetro de centro de la query string
            id_centro = request.args.get('centro', type=int)

            result = EspecialidadComponent.get_especialidades_by_area(area, id_centro)

            if result['success']:
                centro_info = f" del centro {id_centro}" if id_centro else ""
                HandleLogs.write_log(f"EspecialidadService.get_especialidades_by_area - Especialidades de {area}{centro_info} obtenidas")
                return response_success(result['data'], f"Especialidades de {area}{centro_info} obtenidas correctamente")
            else:
                HandleLogs.write_error(f"EspecialidadService.get_especialidades_by_area - Error: {result['message']}")
                return response_error("Error obteniendo especialidades", 500)

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadService.get_especialidades_by_area - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_especialidad(especialidad_id):
        """Obtener una especialidad por ID"""
        try:
            HandleLogs.write_log(f"EspecialidadService.get_especialidad - ID: {especialidad_id}")

            if not especialidad_id or especialidad_id <= 0:
                return response_error("ID de especialidad invalido", 400)

            result = EspecialidadComponent.get_especialidad_by_id(especialidad_id)

            if result['success']:
                if result['data']:
                    HandleLogs.write_log(f"EspecialidadService.get_especialidad - Especialidad {especialidad_id} encontrada")
                    return response_success(result['data'], "Especialidad encontrada")
                else:
                    return response_error("Especialidad no encontrada", 404)
            else:
                HandleLogs.write_error(f"EspecialidadService.get_especialidad - Error: {result['message']}")
                return response_error("Error buscando especialidad", 500)

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadService.get_especialidad - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def create_especialidad():
        """Crear una nueva especialidad"""
        try:
            data = request.get_json()
            HandleLogs.write_log("EspecialidadService.create_especialidad - Iniciando")

            # Validar datos de especialidad
            validation_result = Validators.validate_especialidad_data(data, is_update=False)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Validar que id_centro este presente
            if 'id_centro' not in data or data['id_centro'] is None:
                return response_error("El campo id_centro es requerido", 400)

            # Preparar datos para insercion
            especialidad_data = {
                'nombre': data['nombre'].strip(),
                'area': data['area'],
                'id_centro': data['id_centro'],
                'estado': data.get('estado', 'activo'),
                'usuario_creacion': getattr(request, 'current_user', {}).get('id', 1)
            }

            result = EspecialidadComponent.create_especialidad(especialidad_data)

            if result['success']:
                HandleLogs.write_log("EspecialidadService.create_especialidad - Especialidad creada exitosamente")
                return response_inserted(result['data'], "Especialidad creada exitosamente")
            else:
                HandleLogs.write_error(f"EspecialidadService.create_especialidad - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadService.create_especialidad - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def update_especialidad(especialidad_id):
        """Actualizar una especialidad existente"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"EspecialidadService.update_especialidad - ID: {especialidad_id}")

            if not especialidad_id or especialidad_id <= 0:
                return response_error("ID de especialidad invalido", 400)

            # Validar datos (para actualización)
            validation_result = Validators.validate_especialidad_data(data, is_update=True)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Agregar usuario que modifica
            data['usuario_modificacion'] = getattr(request, 'current_user', {}).get('id', 1)

            result = EspecialidadComponent.update_especialidad(especialidad_id, data)

            if result['success']:
                HandleLogs.write_log(f"EspecialidadService.update_especialidad - Especialidad {especialidad_id} actualizada")
                return response_success(result['data'], "Especialidad actualizada exitosamente")
            else:
                HandleLogs.write_error(f"EspecialidadService.update_especialidad - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadService.update_especialidad - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def delete_especialidad(especialidad_id):
        """Desactivar especialidad (eliminación lógica)"""
        try:
            HandleLogs.write_log(f"EspecialidadService.delete_especialidad - ID: {especialidad_id}")

            if not especialidad_id or especialidad_id <= 0:
                return response_error("ID de especialidad invalido", 400)

            result = EspecialidadComponent.deactivate_especialidad(especialidad_id)

            if result['success']:
                HandleLogs.write_log(f"EspecialidadService.delete_especialidad - Especialidad {especialidad_id} desactivada")
                return response_success(None, "Especialidad desactivada exitosamente")
            else:
                HandleLogs.write_error(f"EspecialidadService.delete_especialidad - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadService.delete_especialidad - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def activate_especialidad(especialidad_id):
        """Reactivar especialidad"""
        try:
            HandleLogs.write_log(f"EspecialidadService.activate_especialidad - ID: {especialidad_id}")

            if especialidad_id is None or especialidad_id <= 0:
                return response_error("ID de especialidad invalido", 400)

            result = EspecialidadComponent.activate_especialidad(especialidad_id)

            if result['success']:
                HandleLogs.write_log(f"EspecialidadService.activate_especialidad - Especialidad {especialidad_id} reactivada")
                return response_success(result['data'], "Especialidad reactivada exitosamente")
            else:
                HandleLogs.write_error(f"EspecialidadService.activate_especialidad - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadService.activate_especialidad - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_especialidades_activas():
        """Obtener especialidades activas (para combos/selects), opcionalmente filtradas por centro"""
        try:
            HandleLogs.write_log("EspecialidadService.get_especialidades_activas - Iniciando")

            # Obtener parámetro de centro de la query string
            id_centro = request.args.get('centro', type=int)

            result = EspecialidadComponent.get_especialidades_activas(id_centro)

            if result['success']:
                centro_info = f" del centro {id_centro}" if id_centro else ""
                HandleLogs.write_log(f"EspecialidadService.get_especialidades_activas - Especialidades activas{centro_info} obtenidas")
                return response_success(result['data'], f"Especialidades activas{centro_info} obtenidas correctamente")
            else:
                HandleLogs.write_error(f"EspecialidadService.get_especialidades_activas - Error: {result['message']}")
                return response_error("Error obteniendo especialidades activas", 500)

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadService.get_especialidades_activas - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_estadisticas():
        """Obtener estadísticas de especialidades"""
        try:
            HandleLogs.write_log("EspecialidadService.get_estadisticas - Iniciando")

            result = EspecialidadComponent.get_estadisticas_especialidades()

            if result['success']:
                HandleLogs.write_log("EspecialidadService.get_estadisticas - Estadísticas obtenidas")
                return response_success(result['data'], "Estadísticas de especialidades obtenidas")
            else:
                HandleLogs.write_error(f"EspecialidadService.get_estadisticas - Error: {result['message']}")
                return response_error("Error obteniendo estadísticas", 500)

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadService.get_estadisticas - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def verificar_compatibilidad(personal_id, paciente_id):
        """Verificar compatibilidad de especialidades entre personal y paciente"""
        try:
            HandleLogs.write_log(f"EspecialidadService.verificar_compatibilidad - Personal: {personal_id}, Paciente: {paciente_id}")

            result = EspecialidadComponent.verificar_compatibilidad_especialidades(personal_id, paciente_id)

            if result['success']:
                HandleLogs.write_log("EspecialidadService.verificar_compatibilidad - Compatibilidad verificada")
                return response_success(result['data'], "Compatibilidad verificada exitosamente")
            else:
                HandleLogs.write_error(f"EspecialidadService.verificar_compatibilidad - Error: {result['message']}")
                return response_error("Error verificando compatibilidad", 500)

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadService.verificar_compatibilidad - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_estadisticas_multiples():
        """Obtener estadísticas de especialidades múltiples"""
        try:
            HandleLogs.write_log("EspecialidadService.get_estadisticas_multiples - Iniciando")

            result = EspecialidadComponent.get_estadisticas_especialidades_multiples()

            if result['success']:
                HandleLogs.write_log("EspecialidadService.get_estadisticas_multiples - Estadísticas obtenidas")
                return response_success(result['data'], "Estadísticas de especialidades múltiples obtenidas")
            else:
                HandleLogs.write_error(f"EspecialidadService.get_estadisticas_multiples - Error: {result['message']}")
                return response_error("Error obteniendo estadísticas múltiples", 500)

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadService.get_estadisticas_multiples - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)