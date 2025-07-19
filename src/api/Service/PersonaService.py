from flask import request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error, response_inserted
from src.utils.general.validators import Validators
from src.api.Components.PersonaComponent import PersonaComponent


class PersonaService:

    @staticmethod
    def get_personas():
        """Obtener lista de todas las personas"""
        try:
            HandleLogs.write_log("PersonaService.get_personas - Iniciando")

            result = PersonaComponent.get_all_personas()

            if result['success']:
                HandleLogs.write_log("PersonaService.get_personas - Personas obtenidas exitosamente")
                return response_success(result['data'], "Lista de personas obtenida correctamente")
            else:
                HandleLogs.write_error(f"PersonaService.get_personas - Error: {result['message']}")
                return response_error("Error obteniendo personas", 500)

        except Exception as e:
            HandleLogs.write_error(f"PersonaService.get_personas - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_persona(persona_id):
        """Obtener una persona por ID"""
        try:
            HandleLogs.write_log(f"PersonaService.get_persona - ID: {persona_id}")

            if not persona_id or persona_id <= 0:
                return response_error("ID de persona invalido", 400)

            result = PersonaComponent.get_persona_by_id(persona_id)

            if result['success']:
                if result['data']:
                    HandleLogs.write_log(f"PersonaService.get_persona - Persona {persona_id} encontrada")
                    return response_success(result['data'], "Persona encontrada")
                else:
                    return response_error("Persona no encontrada", 404)
            else:
                HandleLogs.write_error(f"PersonaService.get_persona - Error: {result['message']}")
                return response_error("Error buscando persona", 500)

        except Exception as e:
            HandleLogs.write_error(f"PersonaService.get_persona - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def create_persona():
        """Crear una nueva persona"""
        try:
            data = request.get_json()
            HandleLogs.write_log("PersonaService.create_persona - Iniciando")

            # Validar datos de persona
            validation_result = Validators.validate_persona_data(data, is_update=False)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Preparar datos para inserción
            persona_data = {
                'nombre': data['nombre'].strip(),
                'apellido': data['apellido'].strip(),
                'cedula': data['cedula'].strip(),
                'telefono': data.get('telefono', '').strip() if data.get('telefono') else None,
                'correo': data.get('correo', '').strip() if data.get('correo') else None,
                'direccion': data.get('direccion', '').strip() if data.get('direccion') else None,
                'fecha_nacimiento': data.get('fecha_nacimiento') if data.get('fecha_nacimiento') else None,
                'estado': data.get('estado', 'activo'),
                'usuario_creacion': getattr(request, 'current_user', {}).get('id', 1)
            }

            result = PersonaComponent.create_persona(persona_data)

            if result['success']:
                HandleLogs.write_log("PersonaService.create_persona - Persona creada exitosamente")
                return response_inserted(result['data'], "Persona creada exitosamente")
            else:
                HandleLogs.write_error(f"PersonaService.create_persona - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PersonaService.create_persona - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def update_persona(persona_id):
        """Actualizar una persona existente"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"PersonaService.update_persona - ID: {persona_id}")

            if not persona_id or persona_id <= 0:
                return response_error("ID de persona invalido", 400)

            # Validar datos (para actualización)
            validation_result = Validators.validate_persona_data(data, is_update=True)
            if not validation_result['valid']:
                return response_error(validation_result['message'], 400)

            # Agregar usuario que modifica
            data['usuario_modificacion'] = getattr(request, 'current_user', {}).get('id', 1)

            result = PersonaComponent.update_persona(persona_id, data)

            if result['success']:
                HandleLogs.write_log(f"PersonaService.update_persona - Persona {persona_id} actualizada")
                return response_success(result['data'], "Persona actualizada exitosamente")
            else:
                HandleLogs.write_error(f"PersonaService.update_persona - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PersonaService.update_persona - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def delete_persona(persona_id):
        """Desactivar persona (eliminación lógica)"""
        try:
            HandleLogs.write_log(f"PersonaService.delete_persona - ID: {persona_id}")

            if not persona_id or persona_id <= 0:
                return response_error("ID de persona invalido", 400)

            # No permitir eliminar personas con ID 1 (admin del sistema)
            if persona_id == 1:
                return response_error("No se puede eliminar la persona administrador principal", 400)

            result = PersonaComponent.deactivate_persona(persona_id)

            if result['success']:
                HandleLogs.write_log(f"PersonaService.delete_persona - Persona {persona_id} desactivada")
                return response_success(None, "Persona desactivada exitosamente")
            else:
                HandleLogs.write_error(f"PersonaService.delete_persona - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PersonaService.delete_persona - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_personas_disponibles():
        """Obtener personas disponibles para crear usuarios"""
        try:
            HandleLogs.write_log("PersonaService.get_personas_disponibles - Iniciando")

            result = PersonaComponent.get_personas_disponibles_para_usuario()

            if result['success']:
                HandleLogs.write_log("PersonaService.get_personas_disponibles - Personas disponibles obtenidas")
                return response_success(result['data'], "Personas disponibles para crear usuario")
            else:
                HandleLogs.write_error(f"PersonaService.get_personas_disponibles - Error: {result['message']}")
                return response_error("Error obteniendo personas disponibles", 500)

        except Exception as e:
            HandleLogs.write_error(f"PersonaService.get_personas_disponibles - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)