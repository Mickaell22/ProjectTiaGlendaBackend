from flask import request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error, response_inserted
from src.utils.general.validators import Validators
from src.api.Components.PacienteComponent import PacienteComponent


class PacienteService:

    @staticmethod
    def get_pacientes():
        """Obtener lista de todos los pacientes"""
        try:
            HandleLogs.write_log("PacienteService.get_pacientes - Iniciando")

            result = PacienteComponent.get_all_pacientes()

            if result['success']:
                HandleLogs.write_log("PacienteService.get_pacientes - Pacientes obtenidos exitosamente")
                return response_success(result['data'], "Lista de pacientes obtenida correctamente")
            else:
                HandleLogs.write_error(f"PacienteService.get_pacientes - Error: {result['message']}")
                return response_error("Error obteniendo pacientes", 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.get_pacientes - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_paciente_by_id(paciente_id):
        """Obtener un paciente por ID"""
        try:
            HandleLogs.write_log(f"PacienteService.get_paciente_by_id - ID: {paciente_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            result = PacienteComponent.get_paciente_by_id(paciente_id)

            if result['success']:
                if result['data']:
                    HandleLogs.write_log(f"PacienteService.get_paciente_by_id - Paciente {paciente_id} encontrado")
                    return response_success(result['data'], "Paciente encontrado")
                else:
                    return response_error("Paciente no encontrado", 404)
            else:
                HandleLogs.write_error(f"PacienteService.get_paciente_by_id - Error: {result['message']}")
                return response_error("Error buscando paciente", 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.get_paciente_by_id - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def create_paciente():
        """Crear un nuevo paciente"""
        try:
            data = request.get_json()
            HandleLogs.write_log("PacienteService.create_paciente - Iniciando")

            # Validar datos de paciente
            validation_result = Validators.validate_paciente_data(data, is_update=False)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Preparar datos para inserción
            paciente_data = {
                'persona_id': int(data['persona_id']),
                'tutor_id': int(data['tutor_id']),
                'fecha_ingreso': data['fecha_ingreso'],
                'observaciones': data.get('observaciones', '').strip() if data.get('observaciones') else None,
                'estado': data.get('estado', 'activo'),
                'usuario_creacion': getattr(request, 'current_user', {}).get('id', 1)
            }

            result = PacienteComponent.create_paciente(paciente_data)

            if result['success']:
                HandleLogs.write_log("PacienteService.create_paciente - Paciente creado exitosamente")
                return response_inserted(result['data'], "Paciente creado exitosamente")
            else:
                HandleLogs.write_error(f"PacienteService.create_paciente - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.create_paciente - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def update_paciente(paciente_id):
        """Actualizar un paciente existente"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"PacienteService.update_paciente - ID: {paciente_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            # Validar datos (para actualización)
            validation_result = Validators.validate_paciente_data(data, is_update=True)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Agregar usuario que modifica
            data['usuario_modificacion'] = getattr(request, 'current_user', {}).get('id', 1)

            result = PacienteComponent.update_paciente(paciente_id, data)

            if result['success']:
                HandleLogs.write_log(f"PacienteService.update_paciente - Paciente {paciente_id} actualizado")
                return response_success(result['data'], "Paciente actualizado exitosamente")
            else:
                HandleLogs.write_error(f"PacienteService.update_paciente - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.update_paciente - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def change_estado_paciente(paciente_id):
        """Cambiar estado del paciente"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"PacienteService.change_estado_paciente - ID: {paciente_id}")

            if not paciente_id or paciente_id <= 0:
                return response_error("ID de paciente invalido", 400)

            # Validar que se proporcione el nuevo estado
            required_validation = Validators.validate_required_fields(data, ['estado'])
            if not required_validation['valid']:
                return response_error(required_validation['message'], 400)

            # Validar que el estado sea válido
            valid_states = ['activo', 'inactivo', 'alta', 'derivado']
            if data['estado'] not in valid_states:
                return response_error(f"Estado inválido. Debe ser uno de: {', '.join(valid_states)}", 400)

            result = PacienteComponent.change_estado_paciente(paciente_id, data['estado'])

            if result['success']:
                HandleLogs.write_log(f"PacienteService.change_estado_paciente - Estado del paciente {paciente_id} cambiado")
                return response_success(result['data'], result['message'])
            else:
                HandleLogs.write_error(f"PacienteService.change_estado_paciente - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.change_estado_paciente - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_pacientes_by_tutor(tutor_id):
        """Obtener pacientes de un tutor específico"""
        try:
            HandleLogs.write_log(f"PacienteService.get_pacientes_by_tutor - Tutor ID: {tutor_id}")

            if not tutor_id or tutor_id <= 0:
                return response_error("ID de tutor invalido", 400)

            result = PacienteComponent.get_pacientes_by_tutor(tutor_id)

            if result['success']:
                HandleLogs.write_log(f"PacienteService.get_pacientes_by_tutor - Pacientes del tutor {tutor_id} obtenidos")
                return response_success(result['data'], "Pacientes del tutor obtenidos correctamente")
            else:
                HandleLogs.write_error(f"PacienteService.get_pacientes_by_tutor - Error: {result['message']}")
                return response_error("Error obteniendo pacientes del tutor", 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.get_pacientes_by_tutor - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_estadisticas():
        """Obtener estadísticas de pacientes"""
        try:
            HandleLogs.write_log("PacienteService.get_estadisticas - Iniciando")

            result = PacienteComponent.get_estadisticas_pacientes()

            if result['success']:
                HandleLogs.write_log("PacienteService.get_estadisticas - Estadísticas obtenidas")
                return response_success(result['data'], "Estadísticas de pacientes obtenidas")
            else:
                HandleLogs.write_error(f"PacienteService.get_estadisticas - Error: {result['message']}")
                return response_error("Error obteniendo estadísticas", 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.get_estadisticas - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_personas_disponibles():
        """Obtener personas disponibles para crear pacientes"""
        try:
            HandleLogs.write_log("PacienteService.get_personas_disponibles - Iniciando")

            result = PacienteComponent.get_personas_disponibles_para_paciente()

            if result['success']:
                HandleLogs.write_log("PacienteService.get_personas_disponibles - Personas disponibles obtenidas")
                return response_success(result['data'], "Personas disponibles para paciente obtenidas")
            else:
                HandleLogs.write_error(f"PacienteService.get_personas_disponibles - Error: {result['message']}")
                return response_error("Error obteniendo personas disponibles", 500)

        except Exception as e:
            HandleLogs.write_error(f"PacienteService.get_personas_disponibles - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)