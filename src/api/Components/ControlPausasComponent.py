"""
ControlPausasComponent.py
Componente para gestionar control automatico de pausas de pacientes
Autor: Sistema Centro Tia Glenda
Fecha: 2025-10-01
"""

from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.logs import HandleLogs
from src.utils.general.response import internal_response


class ControlPausasComponent:
    """Componente para control y procesamiento de pausas de pacientes"""

    @staticmethod
    def check_paciente_exists(paciente_id):
        """Verificar si un paciente existe"""
        try:
            query = "SELECT id FROM paciente WHERE id = %s"
            result = DataBaseHandle.getRecords(query, (paciente_id,), size=1)
            return result is not None and bool(result)
        except Exception as e:
            HandleLogs.write_error(f"ControlPausasComponent.check_paciente_exists - Error: {str(e)}")
            return False

    @staticmethod
    def get_estado_pausas_paciente(paciente_id):
        """Obtener el estado completo de pausas de un paciente"""
        try:
            HandleLogs.write_log(f"ControlPausasComponent.get_estado_pausas_paciente - Paciente {paciente_id}")

            # Verificar que el paciente existe
            if not ControlPausasComponent.check_paciente_exists(paciente_id):
                return internal_response(False, None, "Paciente no encontrado")

            # Obtener pausa general del paciente
            query_general = """
            SELECT
                id,
                fecha_inicio_pausa,
                fecha_fin_pausa,
                motivo_pausa,
                estado_tratamiento
            FROM paciente
            WHERE id = %s
            """
            pausa_general = DataBaseHandle.getRecords(query_general, (paciente_id,), size=1)

            # Obtener pausas por especialidad
            query_especialidades = """
            SELECT
                pe.id,
                pe.id_especialidad,
                e.nombre as especialidad_nombre,
                pe.estado_pausa,
                pe.fecha_inicio_pausa_esp,
                pe.fecha_fin_pausa_esp,
                pe.motivo_pausa_esp
            FROM paciente_especialidades pe
            INNER JOIN especialidad e ON pe.id_especialidad = e.id
            WHERE pe.id_paciente = %s AND pe.estado = 'activo'
            AND pe.estado_pausa = 'pausado_especialidad'
            """
            pausas_especialidades = DataBaseHandle.getRecords(query_especialidades, (paciente_id,))

            resultado = {
                "paciente_id": paciente_id,
                "estado_tratamiento": pausa_general['estado_tratamiento'] if pausa_general else None,
                "pausa_general": None,
                "pausas_especialidades": []
            }

            # Procesar pausa general
            if pausa_general and pausa_general['fecha_inicio_pausa']:
                resultado["pausa_general"] = {
                    "activa": pausa_general['estado_tratamiento'] == 'pausado',
                    "fecha_inicio": pausa_general['fecha_inicio_pausa'].isoformat() if pausa_general['fecha_inicio_pausa'] else None,
                    "fecha_fin": pausa_general['fecha_fin_pausa'].isoformat() if pausa_general['fecha_fin_pausa'] else None,
                    "motivo": pausa_general['motivo_pausa']
                }

            # Procesar pausas por especialidad
            if pausas_especialidades:
                for pe in pausas_especialidades:
                    resultado["pausas_especialidades"].append({
                        "id_especialidad": pe['id_especialidad'],
                        "especialidad_nombre": pe['especialidad_nombre'],
                        "fecha_inicio": pe['fecha_inicio_pausa_esp'].isoformat() if pe['fecha_inicio_pausa_esp'] else None,
                        "fecha_fin": pe['fecha_fin_pausa_esp'].isoformat() if pe['fecha_fin_pausa_esp'] else None,
                        "motivo": pe['motivo_pausa_esp']
                    })

            return internal_response(True, resultado, "Estado de pausas obtenido exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasComponent.get_estado_pausas_paciente - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def verificar_pausa_activa(paciente_id):
        """Verificar si un paciente tiene alguna pausa activa"""
        try:
            from datetime import date

            HandleLogs.write_log(f"ControlPausasComponent.verificar_pausa_activa - Paciente {paciente_id}")

            # Verificar que el paciente existe
            if not ControlPausasComponent.check_paciente_exists(paciente_id):
                return internal_response(False, None, "Paciente no encontrado")

            # Verificar pausa general
            query_general = """
            SELECT fecha_inicio_pausa, fecha_fin_pausa, estado_tratamiento
            FROM paciente
            WHERE id = %s
            AND estado_tratamiento = 'pausado'
            AND fecha_inicio_pausa IS NOT NULL
            """
            pausa_general = DataBaseHandle.getRecords(query_general, (paciente_id,), size=1)

            tiene_pausa_general = False
            if pausa_general and bool(pausa_general):
                if pausa_general['fecha_fin_pausa'] is None or pausa_general['fecha_fin_pausa'] >= date.today():
                    tiene_pausa_general = True

            # Verificar pausas por especialidad
            query_especialidades = """
            SELECT COUNT(*) as total
            FROM paciente_especialidades
            WHERE id_paciente = %s
            AND estado = 'activo'
            AND estado_pausa = 'pausado_especialidad'
            AND fecha_inicio_pausa_esp IS NOT NULL
            AND (fecha_fin_pausa_esp IS NULL OR fecha_fin_pausa_esp >= CURRENT_DATE)
            """
            count_especialidades = DataBaseHandle.getRecords(query_especialidades, (paciente_id,), size=1)

            tiene_pausas_especialidades = count_especialidades and bool(count_especialidades) and count_especialidades['total'] > 0

            resultado = {
                "paciente_id": paciente_id,
                "tiene_pausa_activa": tiene_pausa_general or tiene_pausas_especialidades,
                "pausa_general_activa": tiene_pausa_general,
                "pausas_especialidades_activas": count_especialidades['total'] if count_especialidades and bool(count_especialidades) else 0
            }

            return internal_response(True, resultado, "Verificacion completada")

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasComponent.verificar_pausa_activa - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_historial_pausas(paciente_id):
        """Obtener historial completo de pausas de un paciente"""
        try:
            HandleLogs.write_log(f"ControlPausasComponent.get_historial_pausas - Paciente {paciente_id}")

            # Verificar que el paciente existe
            if not ControlPausasComponent.check_paciente_exists(paciente_id):
                return internal_response(False, None, "Paciente no encontrado")

            query = """
            SELECT
                hp.id,
                hp.tipo_pausa,
                hp.accion,
                hp.fecha_inicio_pausa,
                hp.fecha_fin_pausa,
                hp.motivo,
                hp.observaciones,
                hp.fecha_accion,
                hp.id_especialidad,
                e.nombre as especialidad_nombre,
                hp.usuario_accion,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_usuario
            FROM historial_pausas hp
            LEFT JOIN especialidad e ON hp.id_especialidad = e.id
            LEFT JOIN usuario u ON hp.usuario_accion = u.id
            LEFT JOIN persona p ON u.id_persona = p.id
            WHERE hp.id_paciente = %s
            ORDER BY hp.fecha_accion DESC
            """

            historial = DataBaseHandle.getRecords(query, (paciente_id,))

            if not historial:
                return internal_response(True, [], "No hay historial de pausas para este paciente")

            resultado = []
            for registro in historial:
                resultado.append({
                    "id": registro['id'],
                    "tipo_pausa": registro['tipo_pausa'],
                    "accion": registro['accion'],
                    "fecha_inicio_pausa": registro['fecha_inicio_pausa'].isoformat() if registro['fecha_inicio_pausa'] else None,
                    "fecha_fin_pausa": registro['fecha_fin_pausa'].isoformat() if registro['fecha_fin_pausa'] else None,
                    "motivo": registro['motivo'],
                    "observaciones": registro['observaciones'],
                    "fecha_accion": registro['fecha_accion'].isoformat() if registro['fecha_accion'] else None,
                    "especialidad_id": registro['id_especialidad'],
                    "especialidad_nombre": registro['especialidad_nombre'],
                    "usuario_id": registro['usuario_accion'],
                    "usuario_nombre": registro['nombre_usuario']
                })

            return internal_response(True, resultado, "Historial obtenido exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasComponent.get_historial_pausas - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_pausas_vencidas():
        """Obtener pausas que ya han vencido y deben reactivarse"""
        try:
            from datetime import date

            HandleLogs.write_log("ControlPausasComponent.get_pausas_vencidas - Iniciando")

            # Pausas generales vencidas
            query_general = """
            SELECT
                pac.id as paciente_id,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_paciente,
                pac.fecha_inicio_pausa,
                pac.fecha_fin_pausa,
                pac.motivo_pausa
            FROM paciente pac
            INNER JOIN persona p ON pac.id_persona = p.id
            WHERE pac.fecha_inicio_pausa IS NOT NULL
            AND pac.fecha_fin_pausa IS NOT NULL
            AND pac.fecha_fin_pausa < CURRENT_DATE
            AND pac.estado = 'activo'
            AND pac.estado_tratamiento = 'pausado'
            """

            pausas_generales = DataBaseHandle.getRecords(query_general, ())

            # Pausas por especialidad vencidas
            query_especialidades = """
            SELECT
                pe.id_paciente as paciente_id,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_paciente,
                pe.id_especialidad,
                e.nombre as especialidad_nombre,
                pe.fecha_inicio_pausa_esp,
                pe.fecha_fin_pausa_esp,
                pe.motivo_pausa_esp
            FROM paciente_especialidades pe
            INNER JOIN paciente pac ON pe.id_paciente = pac.id
            INNER JOIN persona p ON pac.id_persona = p.id
            INNER JOIN especialidad e ON pe.id_especialidad = e.id
            WHERE pe.fecha_inicio_pausa_esp IS NOT NULL
            AND pe.fecha_fin_pausa_esp IS NOT NULL
            AND pe.fecha_fin_pausa_esp < CURRENT_DATE
            AND pe.estado = 'activo'
            AND pe.estado_pausa = 'pausado_especialidad'
            """

            pausas_especialidades = DataBaseHandle.getRecords(query_especialidades, ())

            resultado = {
                "pausas_generales_vencidas": [],
                "pausas_especialidades_vencidas": [],
                "total_vencidas": 0
            }

            if pausas_generales:
                for pg in pausas_generales:
                    resultado["pausas_generales_vencidas"].append({
                        "paciente_id": pg['paciente_id'],
                        "nombre_paciente": pg['nombre_paciente'],
                        "fecha_inicio": pg['fecha_inicio_pausa'].isoformat() if pg['fecha_inicio_pausa'] else None,
                        "fecha_fin": pg['fecha_fin_pausa'].isoformat() if pg['fecha_fin_pausa'] else None,
                        "motivo": pg['motivo_pausa'],
                        "dias_vencida": (date.today() - pg['fecha_fin_pausa']).days if pg['fecha_fin_pausa'] else 0
                    })

            if pausas_especialidades:
                for pe in pausas_especialidades:
                    resultado["pausas_especialidades_vencidas"].append({
                        "paciente_id": pe['paciente_id'],
                        "nombre_paciente": pe['nombre_paciente'],
                        "especialidad_id": pe['id_especialidad'],
                        "especialidad_nombre": pe['especialidad_nombre'],
                        "fecha_inicio": pe['fecha_inicio_pausa_esp'].isoformat() if pe['fecha_inicio_pausa_esp'] else None,
                        "fecha_fin": pe['fecha_fin_pausa_esp'].isoformat() if pe['fecha_fin_pausa_esp'] else None,
                        "motivo": pe['motivo_pausa_esp'],
                        "dias_vencida": (date.today() - pe['fecha_fin_pausa_esp']).days if pe['fecha_fin_pausa_esp'] else 0
                    })

            resultado["total_vencidas"] = len(resultado["pausas_generales_vencidas"]) + len(resultado["pausas_especialidades_vencidas"])

            return internal_response(True, resultado, f"Se encontraron {resultado['total_vencidas']} pausas vencidas")

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasComponent.get_pausas_vencidas - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_pausas_proximas_vencer(dias=7):
        """Obtener pausas que estan proximas a vencer en los proximos N dias"""
        try:
            from datetime import date, timedelta

            HandleLogs.write_log(f"ControlPausasComponent.get_pausas_proximas_vencer - Proximos {dias} dias")

            fecha_limite = date.today() + timedelta(days=dias)

            # Pausas generales proximas a vencer
            query_general = """
            SELECT
                pac.id as paciente_id,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_paciente,
                pac.fecha_inicio_pausa,
                pac.fecha_fin_pausa,
                pac.motivo_pausa
            FROM paciente pac
            INNER JOIN persona p ON pac.id_persona = p.id
            WHERE pac.fecha_inicio_pausa IS NOT NULL
            AND pac.fecha_fin_pausa IS NOT NULL
            AND pac.fecha_fin_pausa >= CURRENT_DATE
            AND pac.fecha_fin_pausa <= %s
            AND pac.estado = 'activo'
            AND pac.estado_tratamiento = 'pausado'
            """

            pausas_generales = DataBaseHandle.getRecords(query_general, (fecha_limite,))

            # Pausas por especialidad proximas a vencer
            query_especialidades = """
            SELECT
                pe.id_paciente as paciente_id,
                CONCAT(p.nombre, ' ', p.apellido) as nombre_paciente,
                pe.id_especialidad,
                e.nombre as especialidad_nombre,
                pe.fecha_inicio_pausa_esp,
                pe.fecha_fin_pausa_esp,
                pe.motivo_pausa_esp
            FROM paciente_especialidades pe
            INNER JOIN paciente pac ON pe.id_paciente = pac.id
            INNER JOIN persona p ON pac.id_persona = p.id
            INNER JOIN especialidad e ON pe.id_especialidad = e.id
            WHERE pe.fecha_inicio_pausa_esp IS NOT NULL
            AND pe.fecha_fin_pausa_esp IS NOT NULL
            AND pe.fecha_fin_pausa_esp >= CURRENT_DATE
            AND pe.fecha_fin_pausa_esp <= %s
            AND pe.estado = 'activo'
            AND pe.estado_pausa = 'pausado_especialidad'
            """

            pausas_especialidades = DataBaseHandle.getRecords(query_especialidades, (fecha_limite,))

            resultado = {
                "pausas_generales_proximas": [],
                "pausas_especialidades_proximas": [],
                "total_proximas": 0,
                "dias_limite": dias
            }

            if pausas_generales:
                for pg in pausas_generales:
                    resultado["pausas_generales_proximas"].append({
                        "paciente_id": pg['paciente_id'],
                        "nombre_paciente": pg['nombre_paciente'],
                        "fecha_inicio": pg['fecha_inicio_pausa'].isoformat() if pg['fecha_inicio_pausa'] else None,
                        "fecha_fin": pg['fecha_fin_pausa'].isoformat() if pg['fecha_fin_pausa'] else None,
                        "motivo": pg['motivo_pausa'],
                        "dias_restantes": (pg['fecha_fin_pausa'] - date.today()).days if pg['fecha_fin_pausa'] else 0
                    })

            if pausas_especialidades:
                for pe in pausas_especialidades:
                    resultado["pausas_especialidades_proximas"].append({
                        "paciente_id": pe['paciente_id'],
                        "nombre_paciente": pe['nombre_paciente'],
                        "especialidad_id": pe['id_especialidad'],
                        "especialidad_nombre": pe['especialidad_nombre'],
                        "fecha_inicio": pe['fecha_inicio_pausa_esp'].isoformat() if pe['fecha_inicio_pausa_esp'] else None,
                        "fecha_fin": pe['fecha_fin_pausa_esp'].isoformat() if pe['fecha_fin_pausa_esp'] else None,
                        "motivo": pe['motivo_pausa_esp'],
                        "dias_restantes": (pe['fecha_fin_pausa_esp'] - date.today()).days if pe['fecha_fin_pausa_esp'] else 0
                    })

            resultado["total_proximas"] = len(resultado["pausas_generales_proximas"]) + len(resultado["pausas_especialidades_proximas"])

            return internal_response(True, resultado, f"Se encontraron {resultado['total_proximas']} pausas proximas a vencer")

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasComponent.get_pausas_proximas_vencer - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def procesar_pausas_automaticas():
        """Procesar automaticamente pausas vencidas y reactivar pacientes"""
        try:
            from datetime import date

            HandleLogs.write_log("ControlPausasComponent.procesar_pausas_automaticas - Iniciando")

            procesados = {
                "pausas_generales_reactivadas": 0,
                "pausas_especialidades_reactivadas": 0,
                "errores": []
            }

            # Contar pausas generales vencidas antes de reactivar
            query_count_general = """
            SELECT COUNT(*) as total
            FROM paciente
            WHERE fecha_inicio_pausa IS NOT NULL
            AND fecha_fin_pausa IS NOT NULL
            AND fecha_fin_pausa < CURRENT_DATE
            AND estado = 'activo'
            AND estado_tratamiento = 'pausado'
            """
            count_general = DataBaseHandle.getRecords(query_count_general, (), size=1)
            total_general = count_general['total'] if count_general and bool(count_general) else 0

            if total_general > 0:
                # Obtener IDs de pacientes a reactivar para registrar historial
                query_ids_general = """
                SELECT id, fecha_inicio_pausa, fecha_fin_pausa, motivo_pausa
                FROM paciente
                WHERE fecha_inicio_pausa IS NOT NULL
                AND fecha_fin_pausa IS NOT NULL
                AND fecha_fin_pausa < CURRENT_DATE
                AND estado = 'activo'
                AND estado_tratamiento = 'pausado'
                """
                pacientes_a_reactivar = DataBaseHandle.getRecords(query_ids_general, ())

                # Reactivar pausas generales vencidas
                query_reactivar_general = """
                UPDATE paciente
                SET fecha_inicio_pausa = NULL,
                    fecha_fin_pausa = NULL,
                    motivo_pausa = NULL,
                    estado_tratamiento = 'activo',
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE fecha_inicio_pausa IS NOT NULL
                AND fecha_fin_pausa IS NOT NULL
                AND fecha_fin_pausa < CURRENT_DATE
                AND estado = 'activo'
                AND estado_tratamiento = 'pausado'
                """

                success_general = DataBaseHandle.ExecuteNonQuery(query_reactivar_general, ())

                if success_general:
                    procesados["pausas_generales_reactivadas"] = total_general

                    # Registrar en historial de pausas
                    if pacientes_a_reactivar:
                        for pac in pacientes_a_reactivar:
                            query_historial = """
                            INSERT INTO historial_pausas (id_paciente, tipo_pausa, accion, fecha_inicio_pausa, fecha_fin_pausa, motivo, observaciones, fecha_accion)
                            VALUES (%s, 'general', 'reanudar', %s, %s, %s, 'Reactivacion automatica por vencimiento de pausa', CURRENT_TIMESTAMP)
                            """
                            DataBaseHandle.ExecuteNonQuery(query_historial, (
                                pac['id'],
                                pac['fecha_inicio_pausa'],
                                pac['fecha_fin_pausa'],
                                pac['motivo_pausa']
                            ))

            # Contar pausas de especialidades vencidas antes de reactivar
            query_count_esp = """
            SELECT COUNT(*) as total
            FROM paciente_especialidades
            WHERE fecha_inicio_pausa_esp IS NOT NULL
            AND fecha_fin_pausa_esp IS NOT NULL
            AND fecha_fin_pausa_esp < CURRENT_DATE
            AND estado = 'activo'
            AND estado_pausa = 'pausado_especialidad'
            """
            count_esp = DataBaseHandle.getRecords(query_count_esp, (), size=1)
            total_esp = count_esp['total'] if count_esp and bool(count_esp) else 0

            if total_esp > 0:
                # Obtener datos de especialidades a reactivar para registrar historial
                query_ids_esp = """
                SELECT id_paciente, id_especialidad, fecha_inicio_pausa_esp, fecha_fin_pausa_esp, motivo_pausa_esp
                FROM paciente_especialidades
                WHERE fecha_inicio_pausa_esp IS NOT NULL
                AND fecha_fin_pausa_esp IS NOT NULL
                AND fecha_fin_pausa_esp < CURRENT_DATE
                AND estado = 'activo'
                AND estado_pausa = 'pausado_especialidad'
                """
                especialidades_a_reactivar = DataBaseHandle.getRecords(query_ids_esp, ())

                # Reactivar pausas de especialidades vencidas
                query_reactivar_especialidades = """
                UPDATE paciente_especialidades
                SET estado_pausa = 'activo',
                    fecha_inicio_pausa_esp = NULL,
                    fecha_fin_pausa_esp = NULL,
                    motivo_pausa_esp = NULL,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE fecha_inicio_pausa_esp IS NOT NULL
                AND fecha_fin_pausa_esp IS NOT NULL
                AND fecha_fin_pausa_esp < CURRENT_DATE
                AND estado = 'activo'
                AND estado_pausa = 'pausado_especialidad'
                """

                success_esp = DataBaseHandle.ExecuteNonQuery(query_reactivar_especialidades, ())

                if success_esp:
                    procesados["pausas_especialidades_reactivadas"] = total_esp

                    # Registrar en historial de pausas
                    if especialidades_a_reactivar:
                        for esp in especialidades_a_reactivar:
                            query_historial = """
                            INSERT INTO historial_pausas (id_paciente, id_especialidad, tipo_pausa, accion, fecha_inicio_pausa, fecha_fin_pausa, motivo, observaciones, fecha_accion)
                            VALUES (%s, %s, 'especialidad', 'reanudar', %s, %s, %s, 'Reactivacion automatica por vencimiento de pausa de especialidad', CURRENT_TIMESTAMP)
                            """
                            DataBaseHandle.ExecuteNonQuery(query_historial, (
                                esp['id_paciente'],
                                esp['id_especialidad'],
                                esp['fecha_inicio_pausa_esp'],
                                esp['fecha_fin_pausa_esp'],
                                esp['motivo_pausa_esp']
                            ))

            # Reactivar sesiones de cronograma que estaban canceladas por pausa
            # Nota: cronograma_sesiones no tiene estado 'pausada' en su CHECK constraint,
            # por lo que las sesiones pausadas se marcan como 'cancelada' con motivo.
            # No se reactivan automaticamente para evitar conflictos de horario.

            total_procesados = procesados["pausas_generales_reactivadas"] + procesados["pausas_especialidades_reactivadas"]

            HandleLogs.write_log(f"ControlPausasComponent.procesar_pausas_automaticas - Procesados: {total_procesados}")

            return internal_response(True, procesados, f"Se procesaron {total_procesados} pausas vencidas")

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasComponent.procesar_pausas_automaticas - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")

    @staticmethod
    def get_estadisticas_pausas():
        """Obtener estadisticas generales de pausas en el sistema"""
        try:
            HandleLogs.write_log("ControlPausasComponent.get_estadisticas_pausas - Iniciando")

            # Total pausas generales activas
            query_general_activas = """
            SELECT COUNT(*) as total
            FROM paciente
            WHERE fecha_inicio_pausa IS NOT NULL
            AND estado_tratamiento = 'pausado'
            AND (fecha_fin_pausa IS NULL OR fecha_fin_pausa >= CURRENT_DATE)
            AND estado = 'activo'
            """
            general_activas = DataBaseHandle.getRecords(query_general_activas, (), size=1)

            # Total pausas especialidades activas
            query_esp_activas = """
            SELECT COUNT(*) as total
            FROM paciente_especialidades
            WHERE fecha_inicio_pausa_esp IS NOT NULL
            AND (fecha_fin_pausa_esp IS NULL OR fecha_fin_pausa_esp >= CURRENT_DATE)
            AND estado = 'activo'
            AND estado_pausa = 'pausado_especialidad'
            """
            esp_activas = DataBaseHandle.getRecords(query_esp_activas, (), size=1)

            # Motivos mas comunes
            query_motivos = """
            SELECT motivo, COUNT(*) as total
            FROM historial_pausas
            WHERE accion = 'pausar'
            AND motivo IS NOT NULL
            GROUP BY motivo
            ORDER BY total DESC
            LIMIT 5
            """
            motivos_comunes = DataBaseHandle.getRecords(query_motivos, ())

            # Pausas por mes (ultimos 6 meses)
            query_tendencia = """
            SELECT
                TO_CHAR(fecha_accion, 'YYYY-MM') as mes,
                COUNT(*) as total_pausas
            FROM historial_pausas
            WHERE accion = 'pausar'
            AND fecha_accion >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY TO_CHAR(fecha_accion, 'YYYY-MM')
            ORDER BY mes DESC
            """
            tendencia = DataBaseHandle.getRecords(query_tendencia, ())

            resultado = {
                "pausas_generales_activas": general_activas['total'] if general_activas and bool(general_activas) else 0,
                "pausas_especialidades_activas": esp_activas['total'] if esp_activas and bool(esp_activas) else 0,
                "total_pausas_activas": (general_activas['total'] if general_activas and bool(general_activas) else 0) + (esp_activas['total'] if esp_activas and bool(esp_activas) else 0),
                "motivos_mas_comunes": [],
                "tendencia_mensual": []
            }

            if motivos_comunes:
                for motivo in motivos_comunes:
                    resultado["motivos_mas_comunes"].append({
                        "motivo": motivo['motivo'],
                        "total": motivo['total']
                    })

            if tendencia:
                for mes in tendencia:
                    resultado["tendencia_mensual"].append({
                        "mes": mes['mes'],
                        "total_pausas": mes['total_pausas']
                    })

            return internal_response(True, resultado, "Estadisticas obtenidas exitosamente")

        except Exception as e:
            HandleLogs.write_error(f"ControlPausasComponent.get_estadisticas_pausas - Error: {str(e)}")
            return internal_response(False, None, f"Error: {str(e)}")
