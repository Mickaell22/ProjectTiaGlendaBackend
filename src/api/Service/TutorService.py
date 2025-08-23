from flask import request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error, response_inserted
from src.utils.general.validators import Validators
from src.api.Components.TutorComponent import TutorComponent


class TutorService:

    @staticmethod
    def get_tutores():
        """Obtener lista de todos los tutores"""
        try:
            HandleLogs.write_log("TutorService.get_tutores - Iniciando")

            result = TutorComponent.get_all_tutores()

            if result['success']:
                HandleLogs.write_log("TutorService.get_tutores - Tutores obtenidos exitosamente")
                return response_success(result['data'], "Lista de tutores obtenida correctamente")
            else:
                HandleLogs.write_error(f"TutorService.get_tutores - Error: {result['message']}")
                return response_error("Error obteniendo tutores", 500)

        except Exception as e:
            HandleLogs.write_error(f"TutorService.get_tutores - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_tutor_by_id(tutor_id):
        """Obtener un tutor por ID"""
        try:
            HandleLogs.write_log(f"TutorService.get_tutor_by_id - ID: {tutor_id}")

            if not tutor_id or tutor_id <= 0:
                return response_error("ID de tutor invalido", 400)

            result = TutorComponent.get_tutor_by_id(tutor_id)

            if result['success']:
                if result['data']:
                    HandleLogs.write_log(f"TutorService.get_tutor_by_id - Tutor {tutor_id} encontrado")
                    return response_success(result['data'], "Tutor encontrado")
                else:
                    return response_error("Tutor no encontrado", 404)
            else:
                HandleLogs.write_error(f"TutorService.get_tutor_by_id - Error: {result['message']}")
                return response_error("Error buscando tutor", 500)

        except Exception as e:
            HandleLogs.write_error(f"TutorService.get_tutor_by_id - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def create_tutor():
        """Crear un nuevo tutor"""
        try:
            data = request.get_json()
            HandleLogs.write_log("TutorService.create_tutor - Iniciando")

            # Validar datos de tutor
            validation_result = Validators.validate_tutor_data(data, is_update=False)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Preparar datos para inserción
            tutor_data = {
                'id_persona': data['id_persona'],
                'parentesco': data['parentesco'],
                'ocupacion': data.get('ocupacion', '').strip(),
                'direccion_empresa': data.get('direccion_empresa', '').strip(),
                'telefono_empresa': data.get('telefono_empresa', '').strip(),
                'nombre_empresa': data.get('nombre_empresa', '').strip(),
                'estado': data.get('estado', 'activo'),
                'usuario_creacion': getattr(request, 'current_user', {}).get('id', 1)
            }

            result = TutorComponent.create_tutor(tutor_data)

            if result['success']:
                HandleLogs.write_log("TutorService.create_tutor - Tutor creado exitosamente")
                return response_inserted(result['data'], "Tutor creado exitosamente")
            else:
                HandleLogs.write_error(f"TutorService.create_tutor - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"TutorService.create_tutor - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def update_tutor(tutor_id):
        """Actualizar un tutor existente"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"TutorService.update_tutor - ID: {tutor_id}")

            if not tutor_id or tutor_id <= 0:
                return response_error("ID de tutor invalido", 400)

            # Validar datos (para actualización)
            validation_result = Validators.validate_tutor_data(data, is_update=True)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Agregar usuario que modifica
            data['usuario_modificacion'] = getattr(request, 'current_user', {}).get('id', 1)

            result = TutorComponent.update_tutor(tutor_id, data)

            if result['success']:
                HandleLogs.write_log(f"TutorService.update_tutor - Tutor {tutor_id} actualizado")
                return response_success(result['data'], "Tutor actualizado exitosamente")
            else:
                HandleLogs.write_error(f"TutorService.update_tutor - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"TutorService.update_tutor - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def delete_tutor(tutor_id):
        """Desactivar tutor (eliminación lógica)"""
        try:
            HandleLogs.write_log(f"TutorService.delete_tutor - ID: {tutor_id}")

            if not tutor_id or tutor_id <= 0:
                return response_error("ID de tutor invalido", 400)

            result = TutorComponent.deactivate_tutor(tutor_id)

            if result['success']:
                HandleLogs.write_log(f"TutorService.delete_tutor - Tutor {tutor_id} desactivado")
                return response_success(None, "Tutor desactivado exitosamente")
            else:
                HandleLogs.write_error(f"TutorService.delete_tutor - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"TutorService.delete_tutor - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_tutores_activos():
        """Obtener tutores activos (para combos/selects)"""
        try:
            HandleLogs.write_log("TutorService.get_tutores_activos - Iniciando")

            result = TutorComponent.get_tutores_activos()

            if result['success']:
                HandleLogs.write_log("TutorService.get_tutores_activos - Tutores activos obtenidos")
                return response_success(result['data'], "Tutores activos obtenidos correctamente")
            else:
                HandleLogs.write_error(f"TutorService.get_tutores_activos - Error: {result['message']}")
                return response_error("Error obteniendo tutores activos", 500)

        except Exception as e:
            HandleLogs.write_error(f"TutorService.get_tutores_activos - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_estadisticas():
        """Obtener estadísticas de tutores"""
        try:
            HandleLogs.write_log("TutorService.get_estadisticas - Iniciando")

            result = TutorComponent.get_estadisticas_tutores()

            if result['success']:
                HandleLogs.write_log("TutorService.get_estadisticas - Estadísticas obtenidas")
                return response_success(result['data'], "Estadísticas de tutores obtenidas")
            else:
                HandleLogs.write_error(f"TutorService.get_estadisticas - Error: {result['message']}")
                return response_error("Error obteniendo estadísticas", 500)

        except Exception as e:
            HandleLogs.write_error(f"TutorService.get_estadisticas - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_personas_disponibles():
        """Obtener personas disponibles para crear tutores"""
        try:
            HandleLogs.write_log("TutorService.get_personas_disponibles - Iniciando")

            result = TutorComponent.get_personas_disponibles_para_tutor()

            if result['success']:
                HandleLogs.write_log("TutorService.get_personas_disponibles - Personas disponibles obtenidas")
                return response_success(result['data'], "Personas disponibles para tutor obtenidas")
            else:
                HandleLogs.write_error(f"TutorService.get_personas_disponibles - Error: {result['message']}")
                return response_error("Error obteniendo personas disponibles", 500)

        except Exception as e:
            HandleLogs.write_error(f"TutorService.get_personas_disponibles - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)