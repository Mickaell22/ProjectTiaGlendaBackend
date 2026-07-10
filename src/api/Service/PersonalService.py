from flask import request
from src.utils.general.logs import HandleLogs
from src.utils.general.response import response_success, response_error, response_inserted
from src.utils.general.validators import Validators
from src.api.Components.PersonalComponent import PersonalComponent


class PersonalService:

    @staticmethod
    def get_personal():
        """Obtener lista de todo el personal (filtrado por centro del usuario logueado)"""
        try:
            HandleLogs.write_log("PersonalService.get_personal - Iniciando")
            
            # Obtener centro del usuario actual
            current_user = getattr(request, 'current_user', {})
            centro_id = current_user.get('id_centro')
            
            # Solo filtrar por centro si el usuario no es administrador de sistema
            # o si tiene un centro asignado específico
            filter_centro = centro_id if centro_id else None
            
            result = PersonalComponent.get_all_personal(filter_centro)

            if result['success']:
                filter_msg = f" (filtrado por centro {centro_id})" if filter_centro else ""
                HandleLogs.write_log(f"PersonalService.get_personal - Personal obtenido exitosamente{filter_msg}")
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
                    # Aislamiento multi-centro: un no-admin solo puede ver
                    # personal de su propio centro. Sin esto, cualquier
                    # autenticado leia personal de otro centro enumerando IDs.
                    current_user = getattr(request, 'current_user', {})
                    es_admin = current_user.get('rol', '').lower() == 'administrador'
                    if not es_admin and current_user.get('id_centro'):
                        if result['data'].get('id_centro') != current_user.get('id_centro'):
                            return response_error("No tiene acceso a este personal", 403)
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

            # Preparar datos para inserción (SOLO los campos que el frontend envía)
            current_user = getattr(request, 'current_user', {})
            personal_data = {
                'id_persona': int(data['id_persona']),
                'id_especialidad': int(data['id_especialidad']),
                'fecha_ingreso': data['fecha_ingreso'],
                'titulo_profesional': data['titulo_profesional'].strip() if data.get('titulo_profesional') else None,
                'cargo': data['cargo'].strip() if data.get('cargo') else None,
                'tipo_contrato': data['tipo_contrato'],
                'id_centro': int(data['id_centro']),
                'estado': 'activo',  # Siempre activo al crear
                'usuario_creacion': current_user.get('id', 1)
            }

            # Campos opcionales que el frontend puede enviar
            if data.get('fecha_salida'):
                personal_data['fecha_salida'] = data['fecha_salida']
            if data.get('observaciones'):
                personal_data['observaciones'] = data['observaciones'].strip()

            result = PersonalComponent.create_personal(personal_data)

            if result['success']:
                personal_id = result['data']['id']
                
                # Obtener el personal creado 
                updated_result = PersonalComponent.get_personal_by_id(personal_id)
                HandleLogs.write_log("PersonalService.create_personal - Personal creado exitosamente")
                return response_inserted(updated_result['data'], "Personal creado exitosamente")
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
                # Actualizar especialidades si fueron proporcionadas
                if 'especialidades' in data:
                    # Obtener especialidades actuales
                    current_personal = PersonalComponent.get_personal_by_id(personal_id)
                    if current_personal['success']:
                        current_especialidades = current_personal['data'].get('especialidades', [])
                        current_esp_ids = [esp['id'] for esp in current_especialidades]
                        
                        # Nuevas especialidades del frontend
                        new_especialidades = data['especialidades']
                        new_esp_ids = []
                        for esp in new_especialidades:
                            if isinstance(esp, dict) and 'id' in esp:
                                new_esp_ids.append(esp['id'])
                            elif isinstance(esp, int):
                                new_esp_ids.append(esp)
                        
                        # Remover especialidades que ya no estan
                        for esp_id in current_esp_ids:
                            if esp_id not in new_esp_ids:
                                PersonalComponent.remove_especialidad(personal_id, esp_id)
                        
                        # Agregar nuevas especialidades
                        usuario_creacion = getattr(request, 'current_user', {}).get('id', 1)
                        for esp_id in new_esp_ids:
                            if esp_id not in current_esp_ids:
                                PersonalComponent.assign_especialidad(personal_id, esp_id, usuario_creacion)
                
                # Obtener datos actualizados con especialidades
                updated_result = PersonalComponent.get_personal_by_id(personal_id)
                HandleLogs.write_log(f"PersonalService.update_personal - Personal {personal_id} actualizado")
                return response_success(updated_result['data'], "Personal actualizado exitosamente")
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

            # Validar datos requeridos - aceptar ambos formatos de campos
            especialidad_id = data.get('especialidad_id') or data.get('id_especialidad')
            
            if not especialidad_id:
                return response_error("Campo requerido faltante: especialidad_id o id_especialidad", 400)

            try:
                especialidad_id = int(especialidad_id)
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
    def update_especialidad(personal_id, especialidad_id):
        """Actualizar una especialidad de un miembro del personal"""
        try:
            data = request.get_json()
            HandleLogs.write_log(f"PersonalService.update_especialidad - Personal ID: {personal_id}, Especialidad ID: {especialidad_id}")

            if not personal_id or personal_id <= 0:
                return response_error("ID de personal invalido", 400)

            if not especialidad_id or especialidad_id <= 0:
                return response_error("ID de especialidad invalido", 400)

            usuario_modificacion = getattr(request, 'current_user', {}).get('id', 1)
            result = PersonalComponent.update_especialidad(personal_id, especialidad_id, data, usuario_modificacion)

            if result['success']:
                HandleLogs.write_log(f"PersonalService.update_especialidad - Especialidad {especialidad_id} actualizada para personal {personal_id}")
                return response_success(result['data'], "Especialidad actualizada exitosamente")
            else:
                HandleLogs.write_error(f"PersonalService.update_especialidad - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.update_especialidad - Error: {str(e)}")
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

    @staticmethod
    def get_personal_by_centro(centro_id):
        """Obtener personal filtrado por centro"""
        try:
            HandleLogs.write_log(f"PersonalService.get_personal_by_centro - Centro ID: {centro_id}")

            if not centro_id or centro_id <= 0:
                return response_error("ID de centro inválido", 400)

            result = PersonalComponent.get_personal_by_centro(centro_id)

            if result['success']:
                HandleLogs.write_log(f"PersonalService.get_personal_by_centro - Personal del centro {centro_id} obtenido exitosamente")
                return response_success(result['data'], "Personal del centro obtenido correctamente")
            else:
                HandleLogs.write_error(f"PersonalService.get_personal_by_centro - Error: {result['message']}")
                return response_error("Error obteniendo personal del centro", 500)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.get_personal_by_centro - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def agregar_especialidad_personal():
        """Agregar una especialidad a un miembro del personal"""
        try:
            data = request.get_json()
            HandleLogs.write_log("PersonalService.agregar_especialidad_personal - Iniciando")

            # Validar datos requeridos
            required_validation = Validators.validate_required_fields(
                data, ['personal_id', 'especialidad_id']
            )
            if not required_validation['valid']:
                return response_error(required_validation['message'], 400)

            personal_id = data['personal_id']
            especialidad_id = data['especialidad_id']
            usuario_id = data.get('usuario_id', 1)  # TODO: Obtener del token

            # Validar IDs
            if not isinstance(personal_id, int) or personal_id <= 0:
                return response_error("ID de personal inválido", 400)

            if not isinstance(especialidad_id, int) or especialidad_id <= 0:
                return response_error("ID de especialidad inválido", 400)

            result = PersonalComponent.agregar_especialidad_personal(personal_id, especialidad_id, usuario_id)

            if result['success']:
                HandleLogs.write_log(f"PersonalService.agregar_especialidad_personal - Especialidad {especialidad_id} agregada a personal {personal_id}")
                return response_success(result['data'], result['message'])
            else:
                HandleLogs.write_error(f"PersonalService.agregar_especialidad_personal - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.agregar_especialidad_personal - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def remover_especialidad_personal():
        """Remover una especialidad de un miembro del personal"""
        try:
            data = request.get_json()
            HandleLogs.write_log("PersonalService.remover_especialidad_personal - Iniciando")

            # Validar datos requeridos
            required_validation = Validators.validate_required_fields(
                data, ['personal_id', 'especialidad_id']
            )
            if not required_validation['valid']:
                return response_error(required_validation['message'], 400)

            personal_id = data['personal_id']
            especialidad_id = data['especialidad_id']

            # Validar IDs
            if not isinstance(personal_id, int) or personal_id <= 0:
                return response_error("ID de personal inválido", 400)

            if not isinstance(especialidad_id, int) or especialidad_id <= 0:
                return response_error("ID de especialidad inválido", 400)

            result = PersonalComponent.remover_especialidad_personal(personal_id, especialidad_id)

            if result['success']:
                HandleLogs.write_log(f"PersonalService.remover_especialidad_personal - Especialidad {especialidad_id} removida de personal {personal_id}")
                return response_success(result['data'], result['message'])
            else:
                HandleLogs.write_error(f"PersonalService.remover_especialidad_personal - Error: {result['message']}")
                return response_error(result['message'], 400)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.remover_especialidad_personal - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_personal_by_especialidad(especialidad_id, centro_id=None):
        """Obtener personal por especialidad"""
        try:
            HandleLogs.write_log(f"PersonalService.get_personal_by_especialidad - Especialidad ID: {especialidad_id}, Centro ID: {centro_id}")

            if not especialidad_id or especialidad_id <= 0:
                return response_error("ID de especialidad inválido", 400)

            if centro_id and centro_id <= 0:
                return response_error("ID de centro inválido", 400)

            result = PersonalComponent.get_personal_by_especialidad(especialidad_id, centro_id)

            if result['success']:
                HandleLogs.write_log(f"PersonalService.get_personal_by_especialidad - Personal encontrado para especialidad {especialidad_id}")
                return response_success(result['data'], "Personal por especialidad obtenido correctamente")
            else:
                HandleLogs.write_error(f"PersonalService.get_personal_by_especialidad - Error: {result['message']}")
                return response_error("Error obteniendo personal por especialidad", 500)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.get_personal_by_especialidad - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)

    @staticmethod
    def get_especialidades_disponibles(personal_id):
        """Obtener especialidades disponibles para asignar a un personal"""
        try:
            HandleLogs.write_log(f"PersonalService.get_especialidades_disponibles - Personal ID: {personal_id}")

            if not personal_id or personal_id <= 0:
                return response_error("ID de personal inválido", 400)

            result = PersonalComponent.get_especialidades_disponibles(personal_id)

            if result['success']:
                HandleLogs.write_log(f"PersonalService.get_especialidades_disponibles - Especialidades disponibles obtenidas para personal {personal_id}")
                return response_success(result['data'], "Especialidades disponibles obtenidas correctamente")
            else:
                HandleLogs.write_error(f"PersonalService.get_especialidades_disponibles - Error: {result['message']}")
                return response_error("Error obteniendo especialidades disponibles", 500)

        except Exception as e:
            HandleLogs.write_error(f"PersonalService.get_especialidades_disponibles - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)