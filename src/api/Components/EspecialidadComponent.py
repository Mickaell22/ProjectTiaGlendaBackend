from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class EspecialidadComponent:

    @staticmethod
    def get_all_especialidades(id_centro=None):
        """Obtener todas las especialidades, opcionalmente filtradas por centro"""
        try:
            if id_centro:
                query = """
                SELECT
                    e.id,
                    e.nombre,
                    e.area,
                    e.estado,
                    e.id_centro,
                    c.nombre as centro_nombre,
                    c.codigo as centro_codigo,
                    e.fecha_creacion,
                    e.fecha_modificacion,
                    COUNT(pe.id) as personal_asignado
                FROM especialidad e
                LEFT JOIN centros c ON e.id_centro = c.id
                LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad
                WHERE e.id_centro = %s
                GROUP BY e.id, e.nombre, e.area, e.estado, e.id_centro, c.nombre, c.codigo, e.fecha_creacion, e.fecha_modificacion
                ORDER BY e.area, e.nombre
                """
                params = (id_centro,)
            else:
                query = """
                SELECT
                    e.id,
                    e.nombre,
                    e.area,
                    e.estado,
                    e.id_centro,
                    c.nombre as centro_nombre,
                    c.codigo as centro_codigo,
                    e.fecha_creacion,
                    e.fecha_modificacion,
                    COUNT(pe.id) as personal_asignado
                FROM especialidad e
                LEFT JOIN centros c ON e.id_centro = c.id
                LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad
                GROUP BY e.id, e.nombre, e.area, e.estado, e.id_centro, c.nombre, c.codigo, e.fecha_creacion, e.fecha_modificacion
                ORDER BY c.nombre, e.area, e.nombre
                """
                params = ()

            especialidades = DataBaseHandle.getRecords(query, params)

            if especialidades is not None:
                centro_info = f" del centro {id_centro}" if id_centro else ""
                HandleLogs.write_log(f"EspecialidadComponent.get_all_especialidades - {len(especialidades)} especialidades{centro_info} encontradas")
                return internal_response(True, especialidades, f"Especialidades{centro_info} obtenidas correctamente")
            else:
                HandleLogs.write_error("EspecialidadComponent.get_all_especialidades - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.get_all_especialidades - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_especialidades_by_area(area, id_centro=None):
        """Obtener especialidades por área específica, opcionalmente filtradas por centro"""
        try:
            if id_centro:
                query = """
                SELECT
                    e.id,
                    e.nombre,
                    e.area,
                    e.estado,
                    e.id_centro,
                    c.nombre as centro_nombre,
                    c.codigo as centro_codigo,
                    e.fecha_creacion,
                    e.fecha_modificacion,
                    COUNT(pe.id) as personal_asignado
                FROM especialidad e
                LEFT JOIN centros c ON e.id_centro = c.id
                LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad
                WHERE e.area = %s AND e.estado = 'activo' AND e.id_centro = %s
                GROUP BY e.id, e.nombre, e.area, e.estado, e.id_centro, c.nombre, c.codigo, e.fecha_creacion, e.fecha_modificacion
                ORDER BY e.nombre
                """
                params = (area, id_centro)
            else:
                query = """
                SELECT
                    e.id,
                    e.nombre,
                    e.area,
                    e.estado,
                    e.id_centro,
                    c.nombre as centro_nombre,
                    c.codigo as centro_codigo,
                    e.fecha_creacion,
                    e.fecha_modificacion,
                    COUNT(pe.id) as personal_asignado
                FROM especialidad e
                LEFT JOIN centros c ON e.id_centro = c.id
                LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad
                WHERE e.area = %s AND e.estado = 'activo'
                GROUP BY e.id, e.nombre, e.area, e.estado, e.id_centro, c.nombre, c.codigo, e.fecha_creacion, e.fecha_modificacion
                ORDER BY c.nombre, e.nombre
                """
                params = (area,)

            especialidades = DataBaseHandle.getRecords(query, params)

            if especialidades is not None:
                centro_info = f" del centro {id_centro}" if id_centro else ""
                HandleLogs.write_log(f"EspecialidadComponent.get_especialidades_by_area - {len(especialidades)} especialidades de área {area}{centro_info} encontradas")
                return internal_response(True, especialidades, f"Especialidades de {area}{centro_info} obtenidas correctamente")
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
                e.area,
                e.estado,
                e.id_centro,
                c.nombre as centro_nombre,
                c.codigo as centro_codigo,
                e.fecha_creacion,
                e.fecha_modificacion,
                COUNT(pe.id) as personal_asignado
            FROM especialidad e
            LEFT JOIN centros c ON e.id_centro = c.id
            LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad
            WHERE e.id = %s
            GROUP BY e.id, e.nombre, e.area, e.estado, e.id_centro, c.nombre, c.codigo, e.fecha_creacion, e.fecha_modificacion
            """

            especialidad = DataBaseHandle.getRecords(query, (especialidad_id,), size=1)

            if especialidad:
                # Convertir fechas a string para JSON
                if especialidad.get('fecha_creacion'):
                    especialidad['fecha_creacion'] = str(especialidad['fecha_creacion'])
                if especialidad.get('fecha_modificacion'):
                    especialidad['fecha_modificacion'] = str(especialidad['fecha_modificacion'])
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
            # Verificar si el nombre ya existe en el mismo centro
            nombre_check = EspecialidadComponent.check_nombre_exists(data['nombre'], data['id_centro'])
            if nombre_check['success'] and nombre_check['data']:
                return internal_response(False, None, "Ya existe una especialidad con ese nombre en este centro")

            # Insertar nueva especialidad
            insert_query = """
                INSERT INTO especialidad (nombre, area, estado, id_centro, usuario_creacion)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """

            params = (
                data['nombre'].strip(),
                data['area'],
                data.get('estado', 'activo'),
                data['id_centro'],
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
            # Verificar si la especialidad existe y obtener id_centro actual
            check_query = "SELECT id, id_centro FROM especialidad WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (especialidad_id,), size=1)

            if not existing:
                return internal_response(False, None, "Especialidad no encontrada")

            # Verificar nombre duplicado en el mismo centro (excluyendo la especialidad actual)
            if 'nombre' in data:
                # Usar id_centro del data si viene, sino usar el actual
                id_centro_verificar = data.get('id_centro', existing['id_centro'])
                nombre_check = EspecialidadComponent.check_nombre_exists(
                    data['nombre'], id_centro_verificar, exclude_id=especialidad_id
                )
                if nombre_check['success'] and nombre_check['data']:
                    return internal_response(False, None, "Ya existe una especialidad con ese nombre en este centro")

            # Construir query de actualización dinámicamente
            update_fields = []
            params = []

            allowed_fields = ['nombre', 'area', 'estado', 'id_centro', 'usuario_modificacion']

            for field in allowed_fields:
                if field in data and data[field] is not None:
                    if field in ['nombre']:
                        if data[field].strip():
                            update_fields.append(f"{field} = %s")
                            params.append(data[field].strip())
                    else:
                        update_fields.append(f"{field} = %s")
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
    def activate_especialidad(especialidad_id):
        """Reactivar especialidad"""
        try:
            # Verificar si la especialidad existe
            check_query = "SELECT id, estado FROM especialidad WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (especialidad_id,), size=1)

            if not existing:
                return internal_response(False, None, "Especialidad no encontrada")

            if existing['estado'] == 'activo':
                return internal_response(False, None, "Especialidad ya esta activa")

            # Reactivar especialidad
            update_query = """
                UPDATE especialidad
                SET estado = 'activo', fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """

            success = DataBaseHandle.ExecuteNonQuery(update_query, (especialidad_id,))

            if success:
                HandleLogs.write_log(f"EspecialidadComponent.activate_especialidad - Especialidad {especialidad_id} reactivada")
                return internal_response(True, {"id": especialidad_id, "estado": "activo"},
                                         "Especialidad reactivada exitosamente")
            else:
                HandleLogs.write_error(f"EspecialidadComponent.activate_especialidad - Error reactivando especialidad {especialidad_id}")
                return internal_response(False, None, "Error reactivando especialidad")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.activate_especialidad - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def check_nombre_exists(nombre, id_centro, exclude_id=None):
        """Verificar si un nombre de especialidad ya existe en el mismo centro
        Nota: El constraint UNIQUE en BD es (nombre, id_centro), no incluye area
        """
        try:
            if exclude_id:
                query = "SELECT id FROM especialidad WHERE nombre = %s AND id_centro = %s AND id != %s"
                params = (nombre, id_centro, exclude_id)
            else:
                query = "SELECT id FROM especialidad WHERE nombre = %s AND id_centro = %s"
                params = (nombre, id_centro)

            existing = DataBaseHandle.getRecords(query, params, size=1)
            # getRecords devuelve dict si encuentra, None o {} si no encuentra
            exists = existing is not None and bool(existing)
            return internal_response(True, exists, "Consulta ejecutada")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.check_nombre_exists - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_estadisticas_especialidades():
        """Obtener estadísticas de especialidades"""
        try:
            query = """
            SELECT 
                area,
                COUNT(*) as total_especialidades,
                COUNT(CASE WHEN estado = 'activo' THEN 1 END) as activas,
                COUNT(CASE WHEN estado = 'inactivo' THEN 1 END) as inactivas
            FROM especialidad
            GROUP BY area
            ORDER BY area
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
                e.area,
                COUNT(DISTINCT pe.id_personal) as personal_asignado,
                COUNT(DISTINCT pac.id_paciente) as pacientes_asignados,
                (COUNT(DISTINCT pe.id_personal) + COUNT(DISTINCT pac.id_paciente)) as total_asignaciones
            FROM especialidad e
            LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad AND pe.estado = 'activo'
            LEFT JOIN paciente_especialidades pac ON e.id = pac.id_especialidad AND pac.estado = 'activo'
            WHERE e.estado = 'activo'
            GROUP BY e.id, e.nombre, e.area
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
    def get_especialidades_activas(id_centro=None):
        """Obtener solo especialidades activas (útil para combos/selects), opcionalmente filtradas por centro"""
        try:
            if id_centro:
                query = """
                SELECT
                    id,
                    nombre,
                    area,
                    id_centro
                FROM especialidad
                WHERE estado = 'activo' AND id_centro = %s
                ORDER BY area, nombre
                """
                params = (id_centro,)
            else:
                query = """
                SELECT
                    e.id,
                    e.nombre,
                    e.area,
                    e.id_centro,
                    c.nombre as centro_nombre,
                    c.codigo as centro_codigo
                FROM especialidad e
                LEFT JOIN centros c ON e.id_centro = c.id
                WHERE e.estado = 'activo'
                ORDER BY c.nombre, e.area, e.nombre
                """
                params = ()

            especialidades = DataBaseHandle.getRecords(query, params)

            if especialidades is not None:
                centro_info = f" del centro {id_centro}" if id_centro else ""
                HandleLogs.write_log(f"EspecialidadComponent.get_especialidades_activas - {len(especialidades)} especialidades activas{centro_info} encontradas")
                return internal_response(True, especialidades, f"Especialidades activas{centro_info} obtenidas")
            else:
                HandleLogs.write_error("EspecialidadComponent.get_especialidades_activas - Error en consulta")
                return internal_response(False, None, "Error ejecutando consulta")

        except Exception as e:
            HandleLogs.write_error(f"EspecialidadComponent.get_especialidades_activas - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")