from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class UsuarioCentrosComponent:

    @staticmethod
    def get_centros_usuario(id_usuario):
        """Obtener todos los centros a los que un usuario tiene acceso"""
        try:
            query = """
            SELECT
                c.id,
                c.nombre,
                c.codigo,
                c.direccion,
                c.telefono,
                c.turno_principal as turno,
                uc.es_centro_predeterminado as es_predeterminado
            FROM usuario_centros uc
            INNER JOIN centros c ON uc.id_centro = c.id
            WHERE uc.id_usuario = %s
            AND c.estado = 'activo'
            ORDER BY uc.es_centro_predeterminado DESC, c.nombre ASC
            """

            centros = DataBaseHandle.getRecords(query, (id_usuario,))

            if centros is None:
                HandleLogs.write_error(f"UsuarioCentrosComponent.get_centros_usuario - Error obteniendo centros para usuario {id_usuario}")
                return internal_response(False, [], "Error obteniendo centros del usuario")

            HandleLogs.write_log(f"UsuarioCentrosComponent.get_centros_usuario - {len(centros)} centros encontrados para usuario {id_usuario}")
            return internal_response(True, centros, "Centros obtenidos correctamente")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioCentrosComponent.get_centros_usuario - Error: {str(e)}")
            return internal_response(False, [], f"Error: {str(e)}")

    @staticmethod
    def validar_acceso_centro(id_usuario, id_centro):
        """Validar si un usuario tiene acceso a un centro especifico"""
        try:
            query = """
            SELECT EXISTS(
                SELECT 1
                FROM usuario_centros
                WHERE id_usuario = %s
                AND id_centro = %s
            ) as tiene_acceso
            """

            result = DataBaseHandle.getRecords(query, (id_usuario, id_centro), size=1)

            if result is None:
                HandleLogs.write_error(f"UsuarioCentrosComponent.validar_acceso_centro - Error validando acceso")
                return internal_response(False, False, "Error validando acceso al centro")

            tiene_acceso = result.get('tiene_acceso', False) if isinstance(result, dict) else False

            HandleLogs.write_log(f"UsuarioCentrosComponent.validar_acceso_centro - Usuario {id_usuario} {'tiene' if tiene_acceso else 'NO tiene'} acceso al centro {id_centro}")
            return internal_response(True, tiene_acceso, "Validacion completada")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioCentrosComponent.validar_acceso_centro - Error: {str(e)}")
            return internal_response(False, False, f"Error: {str(e)}")

    @staticmethod
    def get_centro_predeterminado(id_usuario):
        """Obtener el centro predeterminado de un usuario"""
        try:
            query = """
            SELECT
                c.id,
                c.nombre,
                c.codigo,
                c.direccion,
                c.telefono,
                c.turno_principal as turno
            FROM usuario_centros uc
            INNER JOIN centros c ON uc.id_centro = c.id
            WHERE uc.id_usuario = %s
            AND uc.es_centro_predeterminado = TRUE
            AND c.estado = 'activo'
            LIMIT 1
            """

            result = DataBaseHandle.getRecordsWithStatus(query, (id_usuario,), size=1)

            if not result['success']:
                HandleLogs.write_error(f"UsuarioCentrosComponent.get_centro_predeterminado - Error en consulta para usuario {id_usuario}")
                return internal_response(False, None, "Error obteniendo centro predeterminado")

            centro = result['data']

            if not centro or not bool(centro):
                HandleLogs.write_log(f"UsuarioCentrosComponent.get_centro_predeterminado - No se encontro centro predeterminado para usuario {id_usuario}")
                return internal_response(True, None, "No se encontro centro predeterminado")

            HandleLogs.write_log(f"UsuarioCentrosComponent.get_centro_predeterminado - Centro predeterminado obtenido para usuario {id_usuario}")
            return internal_response(True, centro, "Centro predeterminado obtenido")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioCentrosComponent.get_centro_predeterminado - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def establecer_centro_predeterminado(id_usuario, id_centro, usuario_modificacion=None):
        """Establecer el centro predeterminado de un usuario"""
        try:
            # Primero validar que el usuario tenga acceso a ese centro
            validacion = UsuarioCentrosComponent.validar_acceso_centro(id_usuario, id_centro)
            if not validacion['success'] or not validacion['data']:
                HandleLogs.write_error(f"UsuarioCentrosComponent.establecer_centro_predeterminado - Usuario {id_usuario} no tiene acceso al centro {id_centro}")
                return internal_response(False, None, "El usuario no tiene acceso al centro especificado")

            # Quitar el flag de predeterminado de todos los centros del usuario
            query_remove = """
            UPDATE usuario_centros
            SET es_centro_predeterminado = FALSE,
                fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id_usuario = %s
            """

            success_remove = DataBaseHandle.ExecuteNonQuery(query_remove, (usuario_modificacion, id_usuario))

            if not success_remove:
                HandleLogs.write_error(f"UsuarioCentrosComponent.establecer_centro_predeterminado - Error removiendo flags anteriores")
                return internal_response(False, None, "Error actualizando centro predeterminado")

            # Establecer el nuevo centro predeterminado
            query_set = """
            UPDATE usuario_centros
            SET es_centro_predeterminado = TRUE,
                fecha_modificacion = CURRENT_TIMESTAMP,
                usuario_modificacion = %s
            WHERE id_usuario = %s
            AND id_centro = %s
            """

            success_set = DataBaseHandle.ExecuteNonQuery(query_set, (usuario_modificacion, id_usuario, id_centro))

            if success_set:
                HandleLogs.write_log(f"UsuarioCentrosComponent.establecer_centro_predeterminado - Centro {id_centro} establecido como predeterminado para usuario {id_usuario}")
                return internal_response(True, True, "Centro predeterminado actualizado correctamente")
            else:
                HandleLogs.write_error(f"UsuarioCentrosComponent.establecer_centro_predeterminado - Error estableciendo nuevo centro predeterminado")
                return internal_response(False, None, "Error estableciendo centro predeterminado")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioCentrosComponent.establecer_centro_predeterminado - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def agregar_centro_usuario(id_usuario, id_centro, es_predeterminado=False, usuario_creacion=None):
        """Agregar un centro a la lista de centros de un usuario"""
        try:
            query = """
            INSERT INTO usuario_centros (id_usuario, id_centro, es_centro_predeterminado, usuario_creacion)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id_usuario, id_centro) DO NOTHING
            """

            success = DataBaseHandle.ExecuteNonQuery(query, (id_usuario, id_centro, es_predeterminado, usuario_creacion))

            if success:
                HandleLogs.write_log(f"UsuarioCentrosComponent.agregar_centro_usuario - Centro {id_centro} agregado al usuario {id_usuario}")
                return internal_response(True, True, "Centro agregado correctamente")
            else:
                HandleLogs.write_error(f"UsuarioCentrosComponent.agregar_centro_usuario - Error agregando centro")
                return internal_response(False, None, "Error agregando centro al usuario")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioCentrosComponent.agregar_centro_usuario - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def remover_centro_usuario(id_usuario, id_centro):
        """Remover un centro de la lista de centros de un usuario"""
        try:
            # Verificar que no sea el unico centro del usuario
            query_count = """
            SELECT COUNT(*) as total_centros
            FROM usuario_centros
            WHERE id_usuario = %s
            """

            count_result = DataBaseHandle.getRecords(query_count, (id_usuario,), size=1)

            if count_result is None or not isinstance(count_result, dict):
                HandleLogs.write_error(f"UsuarioCentrosComponent.remover_centro_usuario - Error contando centros para usuario {id_usuario}")
                return internal_response(False, None, "Error verificando centros del usuario")

            total_centros = count_result.get('total_centros', 0)

            if total_centros <= 1:
                HandleLogs.write_log(f"UsuarioCentrosComponent.remover_centro_usuario - No se puede remover el unico centro del usuario {id_usuario}")
                return internal_response(False, None, "No se puede remover el unico centro del usuario")

            # Verificar si el centro a remover es el predeterminado
            query_es_predeterminado = """
            SELECT es_centro_predeterminado
            FROM usuario_centros
            WHERE id_usuario = %s AND id_centro = %s
            """
            pred_result = DataBaseHandle.getRecords(query_es_predeterminado, (id_usuario, id_centro), size=1)
            era_predeterminado = pred_result.get('es_centro_predeterminado', False) if isinstance(pred_result, dict) else False

            # Remover el centro
            query_delete = """
            DELETE FROM usuario_centros
            WHERE id_usuario = %s
            AND id_centro = %s
            """

            success = DataBaseHandle.ExecuteNonQuery(query_delete, (id_usuario, id_centro))

            if success:
                # Si era el predeterminado, reasignar al primer centro restante
                if era_predeterminado:
                    query_reasignar = """
                    UPDATE usuario_centros
                    SET es_centro_predeterminado = TRUE
                    WHERE id_usuario = %s
                    AND id = (
                        SELECT id FROM usuario_centros
                        WHERE id_usuario = %s
                        ORDER BY id ASC
                        LIMIT 1
                    )
                    """
                    DataBaseHandle.ExecuteNonQuery(query_reasignar, (id_usuario, id_usuario))
                    HandleLogs.write_log(f"UsuarioCentrosComponent.remover_centro_usuario - Centro predeterminado reasignado para usuario {id_usuario}")

                HandleLogs.write_log(f"UsuarioCentrosComponent.remover_centro_usuario - Centro {id_centro} removido del usuario {id_usuario}")
                return internal_response(True, True, "Centro removido correctamente")
            else:
                HandleLogs.write_error(f"UsuarioCentrosComponent.remover_centro_usuario - Error removiendo centro")
                return internal_response(False, None, "Error removiendo centro del usuario")

        except Exception as e:
            HandleLogs.write_error(f"UsuarioCentrosComponent.remover_centro_usuario - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")
