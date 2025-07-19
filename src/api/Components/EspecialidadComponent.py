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
                e.area,
                e.estado,
                e.fecha_creacion,
                e.fecha_modificacion,
                COUNT(pe.id) as personal_asignado
            FROM especialidad e
            LEFT JOIN personal_especialidad pe ON e.id = pe.especialidad_id
            GROUP BY e.id, e.nombre, e.area, e.estado, e.fecha_creacion, e.fecha_modificacion
            ORDER BY e.area, e.nombre
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
                e.area,
                e.estado,
                e.fecha_creacion,
                e.fecha_modificacion,
                COUNT(pe.id) as personal_asignado
            FROM especialidad e
            LEFT JOIN personal_especialidad pe ON e.id = pe.especialidad_id
            WHERE e.area = %s AND e.estado = 'activo'
            GROUP BY e.id, e.nombre, e.area, e.estado, e.fecha_creacion, e.fecha_modificacion
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
                e.area,
                e.estado,
                e.fecha_creacion,
                e.fecha_modificacion,
                COUNT(pe.id) as personal_asignado
            FROM especialidad e
            LEFT JOIN personal_especialidad pe ON e.id = pe.especialidad_id
            WHERE e.id = %s
            GROUP BY e.id, e.nombre, e.area, e.estado, e.fecha_creacion, e.fecha_modificacion
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
                INSERT INTO especialidad (nombre, area, estado, usuario_creacion)
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
                FROM personal_especialidad 
                WHERE especialidad_id = %s
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
                query = "SELECT id FROM especialidad WHERE nombre = %s AND area = %s AND id != %s"
                params = (nombre, area, exclude_id)
            else:
                query = "SELECT id FROM especialidad WHERE nombre = %s AND area = %s"
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
    def get_especialidades_activas():
        """Obtener solo especialidades activas (útil para combos/selects)"""
        try:
            query = """
            SELECT 
                id,
                nombre,
                area
            FROM especialidad
            WHERE estado = 'activo'
            ORDER BY area, nombre
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