from flask import request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error, response_inserted
from src.utils.general.validators import Validators
from src.api.Components.PersonalComponent import PersonalComponent


class PersonalService:

    @staticmethod
    def get_personal():
        """Obtener lista de todo el personal"""
        try:
            HandleLogs.write_log("PersonalService.get_personal - Iniciando")

            result = PersonalComponent.get_all_personal()

            if result['success']:
                HandleLogs.write_log("PersonalService.get_personal - Personal obtenido exitosamente")
                return response_success(result['data'], "Lista del personal obtenida correctamente")
            else:
                HandleLogs.write_error(f"PersonalService.get_personal - Error: {result['message']}")
                return response_error("Error obteniendo personal", 500)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.get_personal - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_personal_by_id(personal_id):
        """Obtener un miembro del personal por ID"""
        try:
            HandleLogs.write_log(f"PersonalService.get_personal_by_id - ID: {personal_id}")

            if not personal_id or personal_id <= 0:
                return response_error("ID de personal invalido", 400)

            result = PersonalComponent.get_personal_by_id(personal_id)

            if result['success']:
                if result['data']:
                    HandleLogs.write_log(f"PersonalService.get_personal_by_id - Personal {personal_id} encontrado")
                    return response_success(result['data'], "Personal encontrado")
                else:
                    return response_error("Personal no encontrado", 404)
            else:
                HandleLogs.write_error(f"PersonalService.get_personal_by_id - Error: {result['message']}")
                return response_error("Error buscando personal", 500)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.get_personal_by_id - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def create_personal():
        """Crear un nuevo miembro del personal"""
        try:
            data = request.get_json()
            HandleLogs.write_log("PersonalService.create_personal - Iniciando")

            # Validar datos de personal
            validation_result = Validators.validate_personal_data(data, is_update=False)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Preparar datos para inserción
            personal_data = {
                'persona_id': int(data['persona_id']),
                'titulo_profesional': data.get('titulo_profesional', '').strip() if data.get('titulo_profesional') else None,
                'estado': data.get('estado', 'activo'),
                'usuario_creacion': getattr(request, 'current_user', {}).get('id', 1)
            }

            result = PersonalComponent.create_personal(personal_data)

            if result['success']:
                HandleLogs.write_log("PersonalService.create_personal - Personal creado exitosamente")
                return response_inserted(result['data'], "Personal creado exitosamente")
            else:
                HandleLogs.write_error(f"PersonalService.create_personal - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.create_personal - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def update_personal(personal_id):
        """Actualizar un miembro del personal existente"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"PersonalService.update_personal - ID: {personal_id}")

            if not personal_id or personal_id <= 0:
                return response_error("ID de personal invalido", 400)

            # Validar datos (para actualización)
            validation_result = Validators.validate_personal_data(data, is_update=True)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Agregar usuario que modifica
            data['usuario_modificacion'] = getattr(request, 'current_user', {}).get('id', 1)

            result = PersonalComponent.update_personal(personal_id, data)

            if result['success']:
                HandleLogs.write_log(f"PersonalService.update_personal - Personal {personal_id} actualizado")
                return response_success(result['data'], "Personal actualizado exitosamente")
            else:
                HandleLogs.write_error(f"PersonalService.update_personal - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.update_personal - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def delete_personal(personal_id):
        """Desactivar personal (eliminación lógica)"""
        try:
            HandleLogs.write_log(f"PersonalService.delete_personal - ID: {personal_id}")

            if not personal_id or personal_id <= 0:
                return response_error("ID de personal invalido", 400)

            result = PersonalComponent.deactivate_personal(personal_id)

            if result['success']:
                HandleLogs.write_log(f"PersonalService.delete_personal - Personal {personal_id} desactivado")
                return response_success(None, "Personal desactivado exitosamente")
            else:
                HandleLogs.write_error(f"PersonalService.delete_personal - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.delete_personal - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_personal_especialidades(personal_id):
        """Obtener especialidades asignadas a un miembro del personal"""
        try:
            HandleLogs.write_log(f"PersonalService.get_personal_especialidades - Personal ID: {personal_id}")

            if not personal_id or personal_id <= 0:
                return response_error("ID de personal invalido", 400)

            result = PersonalComponent.get_personal_by_id(personal_id)

            if result['success']:
                if result['data']:
                    especialidades = result['data'].get('especialidades', [])
                    HandleLogs.write_log(f"PersonalService.get_personal_especialidades - {len(especialidades)} especialidades encontradas")
                    return response_success(especialidades, "Especialidades del personal obtenidas")
                else:
                    return response_error("Personal no encontrado", 404)
            else:
                HandleLogs.write_error(f"PersonalService.get_personal_especialidades - Error: {result['message']}")
                return response_error("Error obteniendo especialidades", 500)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.get_personal_especialidades - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def assign_especialidad(personal_id):
        """Asignar una especialidad a un miembro del personal"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"PersonalService.assign_especialidad - Personal ID: {personal_id}")

            if not personal_id or personal_id <= 0:
                return response_error("ID de personal invalido", 400)

            # Validar datos requeridos
            required_validation = Validators.validate_required_fields(data, ['especialidad_id'])
            if not required_validation['valid']:
                return response_error(required_validation['message'], 400)

            try:
                especialidad_id = int(data['especialidad_id'])
            except (ValueError, TypeError):
                return response_error("ID de especialidad debe ser un numero entero", 400)

            if especialidad_id <= 0:
                return response_error("ID de especialidad invalido", 400)

            usuario_creacion = getattr(request, 'current_user', {}).get('id', 1)
            result = PersonalComponent.assign_especialidad(personal_id, especialidad_id, usuario_creacion)

            if result['success']:
                HandleLogs.write_log(f"PersonalService.assign_especialidad - Especialidad {especialidad_id} asignada a personal {personal_id}")
                return response_success(result['data'], "Especialidad asignada exitosamente")
            else:
                HandleLogs.write_error(f"PersonalService.assign_especialidad - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.assign_especialidad - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def remove_especialidad(personal_id, especialidad_id):
        """Quitar una especialidad de un miembro del personal"""
        try:
            HandleLogs.write_log(f"PersonalService.remove_especialidad - Personal ID: {personal_id}, Especialidad ID: {especialidad_id}")

            if not personal_id or personal_id <= 0:
                return response_error("ID de personal invalido", 400)

            if not especialidad_id or especialidad_id <= 0:
                return response_error("ID de especialidad invalido", 400)

            result = PersonalComponent.remove_especialidad(personal_id, especialidad_id)

            if result['success']:
                HandleLogs.write_log(f"PersonalService.remove_especialidad - Especialidad {especialidad_id} removida del personal {personal_id}")
                return response_success(None, "Especialidad removida exitosamente")
            else:
                HandleLogs.write_error(f"PersonalService.remove_especialidad - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.remove_especialidad - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_personal_by_area(area):
        """Obtener personal por área específica"""
        try:
            HandleLogs.write_log(f"PersonalService.get_personal_by_area - Área: {area}")

            # Validar área
            valid_areas = ['terapeutico', 'pedagogico']
            if area not in valid_areas:
                return response_error(f"Área invalida. Debe ser una de: {', '.join(valid_areas)}", 400)

            result = PersonalComponent.get_personal_by_area(area)

            if result['success']:
                HandleLogs.write_log(f"PersonalService.get_personal_by_area - Personal de {area} obtenido")
                return response_success(result['data'], f"Personal de {area} obtenido correctamente")
            else:
                HandleLogs.write_error(f"PersonalService.get_personal_by_area - Error: {result['message']}")
                return response_error("Error obteniendo personal por área", 500)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.get_personal_by_area - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_estadisticas():
        """Obtener estadísticas del personal"""
        try:
            HandleLogs.write_log("PersonalService.get_estadisticas - Iniciando")

            result = PersonalComponent.get_estadisticas_personal()

            if result['success']:
                HandleLogs.write_log("PersonalService.get_estadisticas - Estadísticas obtenidas")
                return response_success(result['data'], "Estadísticas del personal obtenidas")
            else:
                HandleLogs.write_error(f"PersonalService.get_estadisticas - Error: {result['message']}")
                return response_error("Error obteniendo estadísticas", 500)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.get_estadisticas - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)