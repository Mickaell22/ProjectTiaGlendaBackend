from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class EspecialidadComponent:

    @staticmethod
    def get_all_especialidades():
        """Obtener todas las especialidades"""
        try:
            query = """
            SELECT 
                e.id,
                e.nombre,
                e.descripcion as area,
                e.estado,
                e.fecha_creacion,
                e.fecha_modificacion,
                COUNT(pe.id) as personal_asignado
            FROM especialidad e
            LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad
            GROUP BY e.id, e.nombre, e.descripcion, e.estado, e.fecha_creacion, e.fecha_modificacion
            ORDER BY e.descripcion, e.nombre
            """

            especialidades = DataBaseHandle.getRecords(query)

            if especialidades is not None:
                HandleLogs.write_log(f"EspecialidadComponent.get_all_especialidades - {len(especialidades)} especialidades encontradas")
                return internal_response(True, especialidades, "Especialidades obtenidas correctamente")
            else:
                HandleLogs.write_error("EspecialidadComponent.get_all_especialidades - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.get_all_especialidades - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_especialidades_by_area(area):
        """Obtener especialidades por área específica"""
        try:
            query = """
            SELECT 
                e.id,
                e.nombre,
                e.descripcion as area,
                e.estado,
                e.fecha_creacion,
                e.fecha_modificacion,
                COUNT(pe.id) as personal_asignado
            FROM especialidad e
            LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad
            WHERE e.descripcion = %s AND e.estado = 'activo'
            GROUP BY e.id, e.nombre, e.descripcion, e.estado, e.fecha_creacion, e.fecha_modificacion
            ORDER BY e.nombre
            """

            especialidades = DataBaseHandle.getRecords(query, (area,))

            if especialidades is not None:
                HandleLogs.write_log(f"EspecialidadComponent.get_especialidades_by_area - {len(especialidades)} especialidades de área {area} encontradas")
                return internal_response(True, especialidades, f"Especialidades de {area} obtenidas correctamente")
            else:
                HandleLogs.write_error(f"EspecialidadComponent.get_especialidades_by_area - Error en consulta para área {area}")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.get_especialidades_by_area - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_especialidad_by_id(especialidad_id):
        """Obtener una especialidad por ID"""
        try:
            query = """
            SELECT 
                e.id,
                e.nombre,
                e.descripcion as area,
                e.estado,
                e.fecha_creacion,
                e.fecha_modificacion,
                COUNT(pe.id) as personal_asignado
            FROM especialidad e
            LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad
            WHERE e.id = %s
            GROUP BY e.id, e.nombre, e.descripcion, e.estado, e.fecha_creacion, e.fecha_modificacion
            """

            especialidad = DataBaseHandle.getRecords(query, (especialidad_id,), size=1)

            if especialidad is not None:
                HandleLogs.write_log(f"EspecialidadComponent.get_especialidad_by_id - Especialidad {especialidad_id} encontrada")
                return internal_response(True, especialidad, "Especialidad encontrada")
            else:
                HandleLogs.write_log(f"EspecialidadComponent.get_especialidad_by_id - Especialidad {especialidad_id} no encontrada")
                return internal_response(True, None, "Especialidad no encontrada")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.get_especialidad_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def create_especialidad(data):
        """Crear una nueva especialidad"""
        try:
            # Verificar si el nombre ya existe en la misma área
            nombre_check = EspecialidadComponent.check_nombre_exists(data['nombre'], data['area'])
            if nombre_check['success'] and nombre_check['data']:
                return internal_response(False, None, f"Ya existe una especialidad con ese nombre en el área {data['area']}")

            # Insertar nueva especialidad
            insert_query = """
                INSERT INTO especialidad (nombre, descripcion, estado, usuario_creacion)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """

            params = (
                data['nombre'].strip(),
                data['area'],
                data.get('estado', 'activo'),
                data.get('usuario_creacion', 1)
            )

            new_id = DataBaseHandle.ExecuteInsert(insert_query, params)

            if new_id:
                # Obtener la especialidad creada con información completa
                new_especialidad = EspecialidadComponent.get_especialidad_by_id(new_id)
                HandleLogs.write_log(f"EspecialidadComponent.create_especialidad - Especialidad creada con ID: {new_id}")
                return internal_response(True, new_especialidad['data'], "Especialidad creada exitosamente")
            else:
                HandleLogs.write_error("EspecialidadComponent.create_especialidad - Error insertando especialidad")
                return internal_response(False, None, "Error creando especialidad")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.create_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def update_especialidad(especialidad_id, data):
        """Actualizar una especialidad existente"""
        try:
            # Verificar si la especialidad existe
            check_query = "SELECT id FROM especialidad WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (especialidad_id,), size=1)

            if not existing:
                return internal_response(False, None, "Especialidad no encontrada")

            # Verificar nombre duplicado en la misma área (excluyendo la especialidad actual)
            if 'nombre' in data and 'area' in data:
                nombre_check = EspecialidadComponent.check_nombre_exists(
                    data['nombre'], data['area'], exclude_id=especialidad_id
                )
                if nombre_check['success'] and nombre_check['data']:
                    return internal_response(False, None, f"Ya existe una especialidad con ese nombre en el área {data['area']}")

            # Construir query de actualización dinámicamente
            update_fields = []
            params = []

            allowed_fields = ['nombre', 'area', 'estado', 'usuario_modificacion']
            # Mapear 'area' a 'descripcion' para la base de datos
            field_mapping = {'area': 'descripcion'}

            for field in allowed_fields:
                if field in data and data[field] is not None:
                    # Usar el mapeo de campos para la base de datos
                    db_field = field_mapping.get(field, field)
                    if field in ['nombre']:
                        if data[field].strip():
                            update_fields.append(f"{db_field} = %s")
                            params.append(data[field].strip())
                    else:
                        update_fields.append(f"{db_field} = %s")
                        params.append(data[field])

            if not update_fields:
                return internal_response(False, None, "No hay campos para actualizar")

            # Agregar fecha de modificación
            update_fields.append("fecha_modificacion = CURRENT_TIMESTAMP")

            # Agregar ID de la especialidad al final
            params.append(especialidad_id)

            update_query = f"""
                UPDATE especialidad 
                SET {', '.join(update_fields)}
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, params)

            if success:
                # Obtener datos actualizados
                updated_especialidad = EspecialidadComponent.get_especialidad_by_id(especialidad_id)
                HandleLogs.write_log(f"EspecialidadComponent.update_especialidad - Especialidad {especialidad_id} actualizada")
                return internal_response(True, updated_especialidad['data'], "Especialidad actualizada exitosamente")
            else:
                HandleLogs.write_error(f"EspecialidadComponent.update_especialidad - Error actualizando especialidad {especialidad_id}")
                return internal_response(False, None, "Error actualizando especialidad")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.update_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def deactivate_especialidad(especialidad_id):
        """Desactivar especialidad (eliminación lógica)"""
        try:
            # Verificar si la especialidad existe
            check_query = "SELECT id, estado FROM especialidad WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (especialidad_id,), size=1)

            if not existing:
                return internal_response(False, None, "Especialidad no encontrada")

            if existing['estado'] == 'inactivo':
                return internal_response(False, None, "Especialidad ya esta inactiva")

            # Verificar si hay personal asignado a esta especialidad
            personal_check = """
                SELECT COUNT(*) as total 
                FROM personal_especialidades 
                WHERE id_especialidad = %s
            """
            personal_count = DataBaseHandle.getRecords(personal_check, (especialidad_id,), size=1)

            if personal_count and personal_count['total'] > 0:
                return internal_response(False, None,
                    f"No se puede desactivar la especialidad porque tiene {personal_count['total']} miembro(s) del personal asignado(s)")

            # Desactivar especialidad
            update_query = """
                UPDATE especialidad 
                SET estado = 'inactivo', fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (especialidad_id,))

            if success:
                HandleLogs.write_log(f"EspecialidadComponent.deactivate_especialidad - Especialidad {especialidad_id} desactivada")
                return internal_response(True, {"id": especialidad_id, "estado": "inactivo"},
                                         "Especialidad desactivada exitosamente")
            else:
                HandleLogs.write_error(f"EspecialidadComponent.deactivate_especialidad - Error desactivando especialidad {especialidad_id}")
                return internal_response(False, None, "Error desactivando especialidad")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.deactivate_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def check_nombre_exists(nombre, area, exclude_id=None):
        """Verificar si un nombre de especialidad ya existe en la misma área"""
        try:
            if exclude_id:
                query = "SELECT id FROM especialidad WHERE nombre = %s AND descripcion = %s AND id != %s"
                params = (nombre, area, exclude_id)
            else:
                query = "SELECT id FROM especialidad WHERE nombre = %s AND descripcion = %s"
                params = (nombre, area)

            existing = DataBaseHandle.getRecords(query, params, size=1)
            return internal_response(True, existing is not None, "Consulta ejecutada")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.check_nombre_exists - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_estadisticas_especialidades():
        """Obtener estadísticas de especialidades"""
        try:
            query = """
            SELECT 
                descripcion as area,
                COUNT(*) as total_especialidades,
                COUNT(CASE WHEN estado = 'activo' THEN 1 END) as activas,
                COUNT(CASE WHEN estado = 'inactivo' THEN 1 END) as inactivas
            FROM especialidad
            GROUP BY descripcion
            ORDER BY descripcion
            """

            estadisticas = DataBaseHandle.getRecords(query)

            if estadisticas is not None:
                HandleLogs.write_log("EspecialidadComponent.get_estadisticas_especialidades - Estadísticas obtenidas")
                return internal_response(True, estadisticas, "Estadísticas de especialidades obtenidas")
            else:
                HandleLogs.write_error("EspecialidadComponent.get_estadisticas_especialidades - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.get_estadisticas_especialidades - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def verificar_compatibilidad_especialidades(personal_id, paciente_id):
        """Verificar compatibilidad de especialidades entre personal y paciente"""
        try:
            # Obtener especialidades del personal
            query_personal = """
            SELECT pe.id_especialidad, e.nombre
            FROM personal_especialidades pe
            INNER JOIN especialidad e ON pe.id_especialidad = e.id
            WHERE pe.id_personal = %s AND pe.estado = 'activo'
            """
            
            especialidades_personal = DataBaseHandle.getRecords(query_personal, (personal_id,))
            
            # Obtener especialidades del paciente
            query_paciente = """
            SELECT pe.id_especialidad, e.nombre
            FROM paciente_especialidades pe
            INNER JOIN especialidad e ON pe.id_especialidad = e.id
            WHERE pe.id_paciente = %s AND pe.estado = 'activo'
            """
            
            especialidades_paciente = DataBaseHandle.getRecords(query_paciente, (paciente_id,))
            
            if especialidades_personal is None or especialidades_paciente is None:
                return internal_response(False, None, "Error obteniendo especialidades")
            
            # Encontrar especialidades en común
            especialidades_personal_ids = {esp['id_especialidad'] for esp in especialidades_personal} if especialidades_personal else set()
            especialidades_paciente_ids = {esp['id_especialidad'] for esp in especialidades_paciente} if especialidades_paciente else set()
            
            especialidades_comunes = especialidades_personal_ids.intersection(especialidades_paciente_ids)
            
            # Calcular compatibilidad
            total_especialidades_paciente = len(especialidades_paciente_ids)
            total_compatibles = len(especialidades_comunes)
            
            porcentaje_compatibilidad = (total_compatibles / total_especialidades_paciente * 100) if total_especialidades_paciente > 0 else 0
            
            compatibilidad_data = {
                "personal_id": personal_id,
                "paciente_id": paciente_id,
                "especialidades_personal": len(especialidades_personal_ids),
                "especialidades_paciente": len(especialidades_paciente_ids),
                "especialidades_comunes": total_compatibles,
                "porcentaje_compatibilidad": round(porcentaje_compatibilidad, 2),
                "es_compatible": porcentaje_compatibilidad > 0,
                "recomendacion": "Asignación recomendada" if porcentaje_compatibilidad >= 50 else "Revisar asignación" if porcentaje_compatibilidad > 0 else "No compatible"
            }
            
            HandleLogs.write_log(f"EspecialidadComponent.verificar_compatibilidad_especialidades - Personal {personal_id} y Paciente {paciente_id}: {porcentaje_compatibilidad}% compatible")
            return internal_response(True, compatibilidad_data, "Compatibilidad verificada")
            
        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.verificar_compatibilidad_especialidades - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_estadisticas_especialidades_multiples():
        """Obtener estadísticas detalladas de especialidades múltiples"""
        try:
            # Estadísticas de personal con especialidades múltiples
            query_personal = """
            SELECT 
                COUNT(DISTINCT id_personal) as personal_con_especialidades,
                COUNT(*) as total_asignaciones_personal,
                AVG(especialidades_por_personal) as promedio_especialidades_personal
            FROM (
                SELECT id_personal, COUNT(*) as especialidades_por_personal
                FROM personal_especialidades
                WHERE estado = 'activo'
                GROUP BY id_personal
            ) subq
            """
            
            # Estadísticas de pacientes con especialidades múltiples
            query_pacientes = """
            SELECT 
                COUNT(DISTINCT id_paciente) as pacientes_con_especialidades,
                COUNT(*) as total_asignaciones_pacientes,
                AVG(especialidades_por_paciente) as promedio_especialidades_paciente
            FROM (
                SELECT id_paciente, COUNT(*) as especialidades_por_paciente
                FROM paciente_especialidades
                WHERE estado = 'activo'
                GROUP BY id_paciente
            ) subq
            """
            
            # Especialidades más asignadas
            query_mas_asignadas = """
            SELECT 
                e.nombre,
                e.descripcion,
                COUNT(DISTINCT pe.id_personal) as personal_asignado,
                COUNT(DISTINCT pac.id_paciente) as pacientes_asignados,
                (COUNT(DISTINCT pe.id_personal) + COUNT(DISTINCT pac.id_paciente)) as total_asignaciones
            FROM especialidad e
            LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad AND pe.estado = 'activo'
            LEFT JOIN paciente_especialidades pac ON e.id = pac.id_especialidad AND pac.estado = 'activo'
            WHERE e.estado = 'activo'
            GROUP BY e.id, e.nombre, e.descripcion
            ORDER BY total_asignaciones DESC
            LIMIT 5
            """
            
            stats_personal = DataBaseHandle.getRecords(query_personal, size=1)
            stats_pacientes = DataBaseHandle.getRecords(query_pacientes, size=1)
            mas_asignadas = DataBaseHandle.getRecords(query_mas_asignadas)
            
            if stats_personal is None or stats_pacientes is None:
                return internal_response(False, None, "Error obteniendo estadísticas")
            
            estadisticas = {
                "resumen": {
                    "personal_con_especialidades": stats_personal.get('personal_con_especialidades', 0) if stats_personal else 0,
                    "pacientes_con_especialidades": stats_pacientes.get('pacientes_con_especialidades', 0) if stats_pacientes else 0,
                    "total_asignaciones_personal": stats_personal.get('total_asignaciones_personal', 0) if stats_personal else 0,
                    "total_asignaciones_pacientes": stats_pacientes.get('total_asignaciones_pacientes', 0) if stats_pacientes else 0,
                    "promedio_especialidades_personal": round(float(stats_personal.get('promedio_especialidades_personal', 0) or 0), 2) if stats_personal else 0,
                    "promedio_especialidades_paciente": round(float(stats_pacientes.get('promedio_especialidades_paciente', 0) or 0), 2) if stats_pacientes else 0
                },
                "especialidades_mas_asignadas": mas_asignadas if mas_asignadas else []
            }
            
            HandleLogs.write_log("EspecialidadComponent.get_estadisticas_especialidades_multiples - Estadísticas obtenidas")
            return internal_response(True, estadisticas, "Estadísticas de especialidades múltiples obtenidas")
            
        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.get_estadisticas_especialidades_multiples - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_especialidades_activas():
        """Obtener solo especialidades activas (útil para combos/selects)"""
        try:
            query = """
            SELECT 
                id,
                nombre,
                descripcion as area
            FROM especialidad
            WHERE estado = 'activo'
            ORDER BY descripcion, nombre
            """

            especialidades = DataBaseHandle.getRecords(query)

            if especialidades is not None:
                HandleLogs.write_log(f"EspecialidadComponent.get_especialidades_activas - {len(especialidades)} especialidades activas encontradas")
                return internal_response(True, especialidades, "Especialidades activas obtenidas")
            else:
                HandleLogs.write_error("EspecialidadComponent.get_especialidades_activas - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.get_especialidades_activas - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")