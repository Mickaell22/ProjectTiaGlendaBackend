from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class CentroComponent:

    @staticmethod
    def get_all_centros():
        """Obtener todos los centros activos"""
        try:
            query = """
            SELECT
                id,
                nombre,
                codigo,
                direccion,
                telefono,
                email,
                turno_principal,
                horario_apertura,
                horario_cierre,
                estado,
                observaciones,
                fecha_creacion,
                fecha_modificacion
            FROM centros
            WHERE estado = 'activo'
            ORDER BY nombre ASC
            """

            centros = DataBaseHandle.getRecords(query)

            # Convertir campos TIME y TIMESTAMP a string para JSON
            if centros:
                for centro in centros:
                    if centro.get('horario_apertura'):
                        centro['horario_apertura'] = str(centro['horario_apertura'])
                    if centro.get('horario_cierre'):
                        centro['horario_cierre'] = str(centro['horario_cierre'])
                    if centro.get('fecha_creacion'):
                        centro['fecha_creacion'] = str(centro['fecha_creacion'])
                    if centro.get('fecha_modificacion'):
                        centro['fecha_modificacion'] = str(centro['fecha_modificacion'])

            HandleLogs.write_log("CentroComponent.get_all_centros - Consulta ejecutada correctamente")
            return internal_response(True, centros, "Centros obtenidos correctamente")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.get_all_centros - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_centro_by_id(centro_id):
        """Obtener informacion de un centro especifico"""
        try:
            query = """
            SELECT
                id,
                nombre,
                codigo,
                direccion,
                telefono,
                email,
                turno_principal,
                horario_apertura,
                horario_cierre,
                estado,
                observaciones,
                fecha_creacion,
                fecha_modificacion
            FROM centros
            WHERE id = %s
            """

            centro = DataBaseHandle.getRecords(query, (centro_id,), size=1)

            # Convertir campos TIME y TIMESTAMP a string para JSON
            if centro:
                if centro.get('horario_apertura'):
                    centro['horario_apertura'] = str(centro['horario_apertura'])
                if centro.get('horario_cierre'):
                    centro['horario_cierre'] = str(centro['horario_cierre'])
                if centro.get('fecha_creacion'):
                    centro['fecha_creacion'] = str(centro['fecha_creacion'])
                if centro.get('fecha_modificacion'):
                    centro['fecha_modificacion'] = str(centro['fecha_modificacion'])

            HandleLogs.write_log(f"CentroComponent.get_centro_by_id - Consulta para centro ID: {centro_id}")
            return internal_response(True, centro, "Centro encontrado")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.get_centro_by_id - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_centro_by_codigo(codigo):
        """Obtener centro por codigo"""
        try:
            query = """
            SELECT
                id,
                nombre,
                codigo,
                direccion,
                telefono,
                email,
                turno_principal,
                horario_apertura,
                horario_cierre,
                estado,
                observaciones,
                fecha_creacion,
                fecha_modificacion
            FROM centros
            WHERE codigo = %s AND estado = 'activo'
            """

            centro = DataBaseHandle.getRecords(query, (codigo,), size=1)

            # Convertir campos TIME y TIMESTAMP a string para JSON
            if centro:
                if centro.get('horario_apertura'):
                    centro['horario_apertura'] = str(centro['horario_apertura'])
                if centro.get('horario_cierre'):
                    centro['horario_cierre'] = str(centro['horario_cierre'])
                if centro.get('fecha_creacion'):
                    centro['fecha_creacion'] = str(centro['fecha_creacion'])
                if centro.get('fecha_modificacion'):
                    centro['fecha_modificacion'] = str(centro['fecha_modificacion'])

            HandleLogs.write_log(f"CentroComponent.get_centro_by_codigo - Consulta para codigo: {codigo}")
            return internal_response(True, centro, "Centro encontrado")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.get_centro_by_codigo - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def validate_user_centro_access(user_id, centro_id):
        """Validar que un usuario tenga acceso al centro especificado"""
        try:
            query = """
            SELECT 
                u.id,
                u.id_centro,
                c.nombre as centro_nombre,
                c.codigo as centro_codigo
            FROM usuario u
            INNER JOIN centros c ON u.id_centro = c.id
            WHERE u.id = %s AND u.id_centro = %s AND u.estado = 'activo' AND c.estado = 'activo'
            """

            access = DataBaseHandle.getRecords(query, (user_id, centro_id), size=1)

            HandleLogs.write_log(f"CentroComponent.validate_user_centro_access - Usuario {user_id}, Centro {centro_id}")
            return internal_response(True, access, "Validación completada")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.validate_user_centro_access - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_centro_statistics(centro_id):
        """Obtener estadísticas de un centro específico"""
        try:
            query = """
            SELECT 
                (SELECT COUNT(*) FROM usuario WHERE id_centro = %s AND estado = 'activo') as total_usuarios,
                (SELECT COUNT(*) FROM personal WHERE id_centro = %s AND estado = 'activo') as total_personal,
                (SELECT COUNT(*) FROM paciente WHERE id_centro = %s AND estado = 'activo') as total_pacientes,
                (SELECT COUNT(*) FROM sesion_terapia WHERE id_centro = %s AND estado = 'activo') as total_sesiones_terapia,
                (SELECT COUNT(*) FROM sesion_pedagogica WHERE id_centro = %s AND estado = 'activo') as total_sesiones_pedagogicas
            """

            stats = DataBaseHandle.getRecords(query, (centro_id, centro_id, centro_id, centro_id, centro_id), size=1)

            HandleLogs.write_log(f"CentroComponent.get_centro_statistics - Estadísticas para centro {centro_id}")
            return internal_response(True, stats, "Estadísticas obtenidas correctamente")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.get_centro_statistics - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def create_centro(data):
        """Crear un nuevo centro"""
        try:
            # Verificar si el codigo ya existe
            codigo_check = CentroComponent.check_codigo_exists(data.get('codigo'))
            if codigo_check['success'] and codigo_check['data']:
                return internal_response(False, None, "Ya existe un centro con ese codigo")

            # Verificar si el nombre ya existe
            nombre_check = CentroComponent.check_nombre_exists(data.get('nombre'))
            if nombre_check['success'] and nombre_check['data']:
                return internal_response(False, None, "Ya existe un centro con ese nombre")

            query = """
            INSERT INTO centros (
                nombre, codigo, direccion, telefono, email,
                turno_principal, horario_apertura, horario_cierre,
                estado, observaciones, usuario_creacion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'activo', %s, %s)
            """

            params = (
                data.get('nombre'),
                data.get('codigo'),
                data.get('direccion'),
                data.get('telefono'),
                data.get('email'),
                data.get('turno_principal', 'mixto'),
                data.get('horario_apertura', '07:00'),
                data.get('horario_cierre', '18:00'),
                data.get('observaciones'),
                data.get('usuario_creacion', 1)
            )

            DataBaseHandle.ExecuteNonQuery(query, params)

            # Obtener el centro recien creado
            select_query = "SELECT id FROM centros WHERE codigo = %s ORDER BY id DESC LIMIT 1"
            nuevo_centro = DataBaseHandle.getRecords(select_query, (data.get('codigo'),), size=1)

            if nuevo_centro:
                # Obtener datos completos
                centro_completo = CentroComponent.get_centro_by_id(nuevo_centro['id'])
                HandleLogs.write_log(f"CentroComponent.create_centro - Centro creado: {data.get('nombre')}")
                return internal_response(True, centro_completo['data'], "Centro creado correctamente")
            else:
                return internal_response(False, None, "Error obteniendo centro creado")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.create_centro - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def update_centro(centro_id, data):
        """Actualizar un centro existente"""
        try:
            # Verificar si el centro existe
            check_query = "SELECT id, nombre, codigo FROM centros WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (centro_id,), size=1)

            if not existing:
                return internal_response(False, None, "Centro no encontrado")

            # Verificar duplicado de codigo si se esta cambiando
            if 'codigo' in data and data['codigo'] != existing['codigo']:
                codigo_check = CentroComponent.check_codigo_exists(data['codigo'], exclude_id=centro_id)
                if codigo_check['success'] and codigo_check['data']:
                    return internal_response(False, None, "Ya existe un centro con ese codigo")

            # Verificar duplicado de nombre si se esta cambiando
            if 'nombre' in data and data['nombre'] != existing['nombre']:
                nombre_check = CentroComponent.check_nombre_exists(data['nombre'], exclude_id=centro_id)
                if nombre_check['success'] and nombre_check['data']:
                    return internal_response(False, None, "Ya existe un centro con ese nombre")

            # Construir query dinamicamente solo con campos proporcionados
            update_fields = []
            params = []

            allowed_fields = ['nombre', 'codigo', 'direccion', 'telefono', 'email',
                              'turno_principal', 'horario_apertura', 'horario_cierre', 'observaciones']

            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    params.append(data[field])

            if not update_fields:
                return internal_response(False, None, "No hay campos para actualizar")

            # Agregar campos de auditoria
            update_fields.append("usuario_modificacion = %s")
            params.append(data.get('usuario_modificacion', 1))
            update_fields.append("fecha_modificacion = CURRENT_TIMESTAMP")

            params.append(centro_id)

            query = f"""
            UPDATE centros SET
                {', '.join(update_fields)}
            WHERE id = %s
            """

            DataBaseHandle.ExecuteNonQuery(query, tuple(params))

            # Obtener datos actualizados
            centro_actualizado = CentroComponent.get_centro_by_id(centro_id)

            HandleLogs.write_log(f"CentroComponent.update_centro - Centro actualizado ID: {centro_id}")
            return internal_response(True, centro_actualizado['data'], "Centro actualizado correctamente")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.update_centro - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def delete_centro(centro_id, usuario_id):
        """Eliminar (soft delete) un centro"""
        try:
            query = """
            UPDATE centros SET
                estado = 'inactivo',
                usuario_modificacion = %s,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s AND estado = 'activo'
            """

            DataBaseHandle.ExecuteNonQuery(query, (usuario_id, centro_id))

            HandleLogs.write_log(f"CentroComponent.delete_centro - Centro eliminado ID: {centro_id}")
            return internal_response(True, {"id": centro_id}, "Centro eliminado correctamente")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.delete_centro - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def check_codigo_exists(codigo, exclude_id=None):
        """Verificar si un codigo de centro ya existe"""
        try:
            if exclude_id:
                query = "SELECT id FROM centros WHERE codigo = %s AND id != %s"
                params = (codigo, exclude_id)
            else:
                query = "SELECT id FROM centros WHERE codigo = %s"
                params = (codigo,)

            result = DataBaseHandle.getRecords(query, params, size=1)
            exists = result is not None and bool(result)

            return internal_response(True, exists, "Verificacion completada")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.check_codigo_exists - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def check_nombre_exists(nombre, exclude_id=None):
        """Verificar si un nombre de centro ya existe"""
        try:
            if exclude_id:
                query = "SELECT id FROM centros WHERE nombre = %s AND id != %s"
                params = (nombre, exclude_id)
            else:
                query = "SELECT id FROM centros WHERE nombre = %s"
                params = (nombre,)

            result = DataBaseHandle.getRecords(query, params, size=1)
            exists = result is not None and bool(result)

            return internal_response(True, exists, "Verificacion completada")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.check_nombre_exists - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def activate_centro(centro_id, usuario_id):
        """Reactivar un centro inactivo"""
        try:
            # Verificar si existe y su estado actual
            check_query = "SELECT id, estado FROM centros WHERE id = %s"
            existing = DataBaseHandle.getRecords(check_query, (centro_id,), size=1)

            if not existing:
                return internal_response(False, None, "Centro no encontrado")

            if existing['estado'] == 'activo':
                return internal_response(False, None, "El centro ya esta activo")

            query = """
            UPDATE centros SET
                estado = 'activo',
                usuario_modificacion = %s,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = %s
            """

            DataBaseHandle.ExecuteNonQuery(query, (usuario_id, centro_id))

            HandleLogs.write_log(f"CentroComponent.activate_centro - Centro reactivado ID: {centro_id}")
            return internal_response(True, {"id": centro_id, "estado": "activo"}, "Centro reactivado correctamente")

        except Exception as e:
            HandleLogs.write_error(f"CentroComponent.activate_centro - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")