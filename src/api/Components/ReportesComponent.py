# src/api/Components/ReportesComponent.py
from src.utils.database.connection_db import DataBaseHandle
from datetime import datetime, timedelta, date, time
import logging

class ReportesComponent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # ============================================
    # UTILIDADES
    # ============================================

    def _serialize_dates(self, data):
        """Convierte campos date/time/datetime a string para JSON"""
        if not data:
            return data
        serialized = []
        for row in data:
            new_row = {}
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    new_row[key] = value.isoformat()
                elif isinstance(value, time):
                    new_row[key] = str(value)
                elif isinstance(value, timedelta):
                    total_seconds = int(value.total_seconds())
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    new_row[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    new_row[key] = value
            serialized.append(new_row)
        return serialized

    # ============================================
    # REPORTES DE SESIONES TERAPEUTICAS
    # ============================================

    def get_reporte_asistencia_paciente(self, id_paciente=None, fecha_inicio=None, fecha_fin=None, id_terapeuta=None):
        """Obtiene reporte de asistencia por paciente(s)"""
        try:
            query = """
                SELECT
                    p.nombre || ' ' || p.apellido as paciente_nombre,
                    pac.id as paciente_id,
                    p.cedula,
                    st.titulo as sesion_titulo,
                    e.nombre as especialidad,
                    pers.nombre || ' ' || pers.apellido as terapeuta_nombre,
                    COUNT(cs.id) as total_sesiones_programadas,
                    COUNT(CASE WHEN asist.asistio = true THEN 1 END) as sesiones_asistidas,
                    COUNT(CASE WHEN asist.asistio = false THEN 1 END) as sesiones_perdidas,
                    COUNT(CASE WHEN cs.estado = 'cancelada' THEN 1 END) as sesiones_canceladas,
                    ROUND(
                        (COUNT(CASE WHEN asist.asistio = true THEN 1 END) * 100.0 /
                         NULLIF(COUNT(cs.id), 0)), 2
                    ) as porcentaje_asistencia
                FROM paciente pac
                JOIN persona p ON pac.id_persona = p.id
                JOIN sesion_paciente sp ON pac.id = sp.id_paciente
                JOIN sesion_terapia st ON sp.id_sesion = st.id
                JOIN especialidad e ON st.id_especialidad = e.id
                JOIN personal pers_table ON st.id_terapeuta = pers_table.id
                JOIN persona pers ON pers_table.id_persona = pers.id
                LEFT JOIN cronograma_sesiones cs ON st.id = cs.id_sesion
                LEFT JOIN asistencia_sesiones asist ON cs.id = asist.id_cronograma AND asist.id_paciente = pac.id
                WHERE pac.estado = 'activo'
            """

            params = []

            if id_paciente:
                query += " AND pac.id = %s"
                params.append(id_paciente)

            if id_terapeuta:
                query += " AND st.id_terapeuta = %s"
                params.append(id_terapeuta)

            if fecha_inicio:
                query += " AND cs.fecha_programada >= %s"
                params.append(fecha_inicio)

            if fecha_fin:
                query += " AND cs.fecha_programada <= %s"
                params.append(fecha_fin)

            query += """
                GROUP BY pac.id, p.nombre, p.apellido, p.cedula, st.titulo, e.nombre,
                         pers.nombre, pers.apellido
                ORDER BY p.nombre, p.apellido
            """

            result = DataBaseHandle.getRecords(query, tuple(params) if params else None)
            result = self._serialize_dates(result) if result else []

            return {
                'success': True,
                'data': result,
                'total_registros': len(result)
            }

        except Exception as e:
            self.logger.error(f"Error en get_reporte_asistencia_paciente: {e}")
            return {
                'success': False,
                'message': f'Error generando reporte: {str(e)}',
                'data': []
            }

    def get_reporte_progreso_terapeutico(self, id_paciente=None, id_terapeuta=None, fecha_inicio=None, fecha_fin=None):
        """Obtiene reporte de progreso terapeutico"""
        try:
            query = """
                SELECT
                    p.nombre || ' ' || p.apellido as paciente_nombre,
                    pac.id as paciente_id,
                    st.titulo as sesion_titulo,
                    st.objetivo_general,
                    e.nombre as especialidad,
                    pers.nombre || ' ' || pers.apellido as terapeuta_nombre,
                    pac.fecha_ingreso,
                    pac.estado_tratamiento,
                    COUNT(cs.id) as total_sesiones,
                    MIN(cs.fecha_programada) as fecha_primera_sesion,
                    MAX(cs.fecha_programada) as fecha_ultima_sesion,
                    COUNT(CASE WHEN asist.asistio = true THEN 1 END) as sesiones_completadas,
                    ROUND(
                        (COUNT(CASE WHEN asist.asistio = true THEN 1 END) * 100.0 /
                         NULLIF(COUNT(cs.id), 0)), 2
                    ) as porcentaje_completado
                FROM paciente pac
                JOIN persona p ON pac.id_persona = p.id
                JOIN sesion_paciente sp ON pac.id = sp.id_paciente
                JOIN sesion_terapia st ON sp.id_sesion = st.id
                JOIN especialidad e ON st.id_especialidad = e.id
                JOIN personal pers_table ON st.id_terapeuta = pers_table.id
                JOIN persona pers ON pers_table.id_persona = pers.id
                LEFT JOIN cronograma_sesiones cs ON st.id = cs.id_sesion
                LEFT JOIN asistencia_sesiones asist ON cs.id = asist.id_cronograma AND asist.id_paciente = pac.id
                WHERE pac.estado = 'activo'
            """

            params = []

            if id_paciente:
                query += " AND pac.id = %s"
                params.append(id_paciente)

            if id_terapeuta:
                query += " AND st.id_terapeuta = %s"
                params.append(id_terapeuta)

            if fecha_inicio:
                query += " AND cs.fecha_programada >= %s"
                params.append(fecha_inicio)

            if fecha_fin:
                query += " AND cs.fecha_programada <= %s"
                params.append(fecha_fin)

            query += """
                GROUP BY pac.id, p.nombre, p.apellido, st.titulo, st.objetivo_general,
                         e.nombre, pers.nombre, pers.apellido, pac.fecha_ingreso, pac.estado_tratamiento
                ORDER BY p.nombre, p.apellido
            """

            result = DataBaseHandle.getRecords(query, tuple(params) if params else None)
            result = self._serialize_dates(result) if result else []

            return {
                'success': True,
                'data': result,
                'total_registros': len(result)
            }

        except Exception as e:
            self.logger.error(f"Error en get_reporte_progreso_terapeutico: {e}")
            return {
                'success': False,
                'message': f'Error generando reporte: {str(e)}',
                'data': []
            }

    def get_reporte_carga_trabajo_personal(self, fecha_inicio=None, fecha_fin=None, id_especialidad=None):
        """Obtiene reporte de carga de trabajo del personal terapeutico"""
        try:
            query = """
                SELECT
                    pers.nombre || ' ' || pers.apellido as terapeuta_nombre,
                    pers_table.id as personal_id,
                    e.nombre as especialidad,
                    COUNT(DISTINCT st.id) as total_sesiones_activas,
                    COUNT(DISTINCT sp.id_paciente) as total_pacientes,
                    COUNT(DISTINCT cs.id) as sesiones_programadas,
                    COUNT(DISTINCT CASE WHEN asist.asistio = true THEN cs.id END) as sesiones_realizadas,
                    COUNT(DISTINCT CASE WHEN cs.estado = 'cancelada' THEN cs.id END) as sesiones_canceladas,
                    ROUND(AVG(EXTRACT(EPOCH FROM (cs.hora_fin - cs.hora_inicio))/3600), 2) as horas_promedio_sesion,
                    SUM(CASE WHEN asist.asistio = true THEN
                        EXTRACT(EPOCH FROM (cs.hora_fin - cs.hora_inicio))/3600
                        ELSE 0 END) as total_horas_trabajadas
                FROM personal pers_table
                JOIN persona pers ON pers_table.id_persona = pers.id
                JOIN personal_especialidades pe ON pers_table.id = pe.id_personal
                JOIN especialidad e ON pe.id_especialidad = e.id
                LEFT JOIN sesion_terapia st ON pers_table.id = st.id_terapeuta
                LEFT JOIN sesion_paciente sp ON st.id = sp.id_sesion
                LEFT JOIN cronograma_sesiones cs ON st.id = cs.id_sesion
                LEFT JOIN asistencia_sesiones asist ON cs.id = asist.id_cronograma
                WHERE pers_table.activo = TRUE
                AND e.area = 'Especialidad terapéutica'
            """

            params = []

            if fecha_inicio:
                query += " AND cs.fecha_programada >= %s"
                params.append(fecha_inicio)

            if fecha_fin:
                query += " AND cs.fecha_programada <= %s"
                params.append(fecha_fin)

            if id_especialidad:
                query += " AND e.id = %s"
                params.append(id_especialidad)

            query += """
                GROUP BY pers_table.id, pers.nombre, pers.apellido, e.nombre
                ORDER BY total_horas_trabajadas DESC NULLS LAST, pers.nombre
            """

            result = DataBaseHandle.getRecords(query, tuple(params) if params else None)
            result = self._serialize_dates(result) if result else []

            return {
                'success': True,
                'data': result,
                'total_registros': len(result)
            }

        except Exception as e:
            self.logger.error(f"Error en get_reporte_carga_trabajo_personal: {e}")
            return {
                'success': False,
                'message': f'Error generando reporte: {str(e)}',
                'data': []
            }

    # ============================================
    # REPORTES DE SESIONES PEDAGOGICAS
    # ============================================

    def get_reporte_academico_estudiante(self, id_estudiante=None, fecha_inicio=None, fecha_fin=None, id_educador=None):
        """Obtiene reporte academico por estudiante"""
        try:
            query = """
                SELECT
                    p.nombre || ' ' || p.apellido as estudiante_nombre,
                    pac.id as estudiante_id,
                    p.cedula,
                    sped.nombre_clase,
                    e.nombre as especialidad,
                    pers.nombre || ' ' || pers.apellido as educador_nombre,
                    COUNT(cc.id) as total_clases_programadas,
                    COUNT(CASE WHEN asist.asistio = true THEN 1 END) as clases_asistidas,
                    COUNT(CASE WHEN asist.asistio = false THEN 1 END) as clases_perdidas,
                    ROUND(
                        (COUNT(CASE WHEN asist.asistio = true THEN 1 END) * 100.0 /
                         NULLIF(COUNT(cc.id), 0)), 2
                    ) as porcentaje_asistencia,
                    ROUND(AVG(asist.calificacion_clase)::numeric, 2) as calificacion_promedio,
                    COUNT(CASE WHEN asist.calificacion_clase >= 7 THEN 1 END) as evaluaciones_aprobadas,
                    COUNT(CASE WHEN asist.calificacion_clase < 7 AND asist.calificacion_clase IS NOT NULL THEN 1 END) as evaluaciones_reprobadas
                FROM paciente pac
                JOIN persona p ON pac.id_persona = p.id
                JOIN sesion_estudiante se ON pac.id = se.id_estudiante
                JOIN sesion_pedagogica sped ON se.id_sesion = sped.id
                JOIN especialidad e ON sped.id_especialidad = e.id
                JOIN personal pers_table ON sped.id_educador = pers_table.id
                JOIN persona pers ON pers_table.id_persona = pers.id
                LEFT JOIN cronograma_clases cc ON sped.id = cc.id_sesion
                LEFT JOIN asistencia_clases asist ON cc.id = asist.id_cronograma AND asist.id_paciente = pac.id
                WHERE pac.estado = 'activo'
            """

            params = []

            if id_estudiante:
                query += " AND pac.id = %s"
                params.append(id_estudiante)

            if id_educador:
                query += " AND sped.id_educador = %s"
                params.append(id_educador)

            if fecha_inicio:
                query += " AND cc.fecha_programada >= %s"
                params.append(fecha_inicio)

            if fecha_fin:
                query += " AND cc.fecha_programada <= %s"
                params.append(fecha_fin)

            query += """
                GROUP BY pac.id, p.nombre, p.apellido, p.cedula, sped.nombre_clase,
                         e.nombre, pers.nombre, pers.apellido
                ORDER BY p.nombre, p.apellido
            """

            result = DataBaseHandle.getRecords(query, tuple(params) if params else None)
            result = self._serialize_dates(result) if result else []

            return {
                'success': True,
                'data': result,
                'total_registros': len(result)
            }

        except Exception as e:
            self.logger.error(f"Error en get_reporte_academico_estudiante: {e}")
            return {
                'success': False,
                'message': f'Error generando reporte: {str(e)}',
                'data': []
            }

    def get_reporte_rendimiento_clase(self, id_sesion=None, fecha_inicio=None, fecha_fin=None, id_especialidad=None):
        """Obtiene reporte de rendimiento por clase"""
        try:
            query = """
                SELECT
                    sped.nombre_clase,
                    sped.codigo_sesion,
                    sped.id as sesion_id,
                    e.nombre as especialidad,
                    pers.nombre || ' ' || pers.apellido as educador_nombre,
                    sped.fecha_inicio,
                    sped.fecha_fin,
                    COUNT(DISTINCT se.id_estudiante) as total_estudiantes,
                    COUNT(DISTINCT cc.id) as total_clases_programadas,
                    COUNT(CASE WHEN asist.asistio = true THEN 1 END) as total_asistencias,
                    ROUND(
                        (COUNT(CASE WHEN asist.asistio = true THEN 1 END) * 100.0 /
                         NULLIF(COUNT(DISTINCT cc.id) * COUNT(DISTINCT se.id_estudiante), 0)), 2
                    ) as porcentaje_asistencia_global,
                    ROUND(AVG(asist.calificacion_clase)::numeric, 2) as calificacion_promedio_clase,
                    COUNT(CASE WHEN asist.calificacion_clase >= 7 THEN 1 END) as evaluaciones_aprobadas,
                    COUNT(CASE WHEN asist.calificacion_clase < 7 AND asist.calificacion_clase IS NOT NULL THEN 1 END) as evaluaciones_reprobadas
                FROM sesion_pedagogica sped
                JOIN especialidad e ON sped.id_especialidad = e.id
                JOIN personal pers_table ON sped.id_educador = pers_table.id
                JOIN persona pers ON pers_table.id_persona = pers.id
                LEFT JOIN sesion_estudiante se ON sped.id = se.id_sesion
                LEFT JOIN cronograma_clases cc ON sped.id = cc.id_sesion
                LEFT JOIN asistencia_clases asist ON cc.id = asist.id_cronograma
                WHERE sped.estado IN ('en_curso', 'finalizada')
            """

            params = []

            if id_sesion:
                query += " AND sped.id = %s"
                params.append(id_sesion)

            if id_especialidad:
                query += " AND e.id = %s"
                params.append(id_especialidad)

            if fecha_inicio:
                query += " AND cc.fecha_programada >= %s"
                params.append(fecha_inicio)

            if fecha_fin:
                query += " AND cc.fecha_programada <= %s"
                params.append(fecha_fin)

            query += """
                GROUP BY sped.id, sped.nombre_clase, sped.codigo_sesion, e.nombre,
                         pers.nombre, pers.apellido, sped.fecha_inicio, sped.fecha_fin
                ORDER BY sped.nombre_clase
            """

            result = DataBaseHandle.getRecords(query, tuple(params) if params else None)
            result = self._serialize_dates(result) if result else []

            return {
                'success': True,
                'data': result,
                'total_registros': len(result)
            }

        except Exception as e:
            self.logger.error(f"Error en get_reporte_rendimiento_clase: {e}")
            return {
                'success': False,
                'message': f'Error generando reporte: {str(e)}',
                'data': []
            }

    # ============================================
    # REPORTES ADMINISTRATIVOS
    # ============================================

    def get_reporte_utilizacion_recursos(self, fecha_inicio=None, fecha_fin=None):
        """Obtiene reporte de utilizacion de recursos (sesiones por especialidad)"""
        try:
            # Reporte de utilizacion basado en sesiones por especialidad y estado
            query_terapia = """
                SELECT
                    'Sesiones Terapeuticas' as tipo_recurso,
                    e.nombre as recurso,
                    COUNT(cs.id) as total_ocupacion,
                    COUNT(CASE WHEN cs.estado = 'completada' THEN 1 END) as ocupacion_efectiva,
                    COUNT(CASE WHEN cs.estado = 'cancelada' THEN 1 END) as ocupacion_cancelada,
                    ROUND(
                        (COUNT(CASE WHEN cs.estado = 'completada' THEN 1 END) * 100.0 /
                         NULLIF(COUNT(cs.id), 0)), 2
                    ) as porcentaje_utilizacion
                FROM cronograma_sesiones cs
                JOIN sesion_terapia st ON cs.id_sesion = st.id
                JOIN especialidad e ON st.id_especialidad = e.id
                WHERE 1=1
            """

            params_terapia = []

            if fecha_inicio:
                query_terapia += " AND cs.fecha_programada >= %s"
                params_terapia.append(fecha_inicio)

            if fecha_fin:
                query_terapia += " AND cs.fecha_programada <= %s"
                params_terapia.append(fecha_fin)

            query_terapia += " GROUP BY e.nombre"

            query_pedagogia = """
                SELECT
                    'Sesiones Pedagogicas' as tipo_recurso,
                    e.nombre as recurso,
                    COUNT(cc.id) as total_ocupacion,
                    COUNT(CASE WHEN cc.estado = 'completada' OR cc.estado = 'realizada' THEN 1 END) as ocupacion_efectiva,
                    COUNT(CASE WHEN cc.estado = 'cancelada' THEN 1 END) as ocupacion_cancelada,
                    ROUND(
                        (COUNT(CASE WHEN cc.estado IN ('completada', 'realizada') THEN 1 END) * 100.0 /
                         NULLIF(COUNT(cc.id), 0)), 2
                    ) as porcentaje_utilizacion
                FROM cronograma_clases cc
                JOIN sesion_pedagogica sped ON cc.id_sesion = sped.id
                JOIN especialidad e ON sped.id_especialidad = e.id
                WHERE 1=1
            """

            params_pedagogia = []

            if fecha_inicio:
                query_pedagogia += " AND cc.fecha_programada >= %s"
                params_pedagogia.append(fecha_inicio)

            if fecha_fin:
                query_pedagogia += " AND cc.fecha_programada <= %s"
                params_pedagogia.append(fecha_fin)

            query_pedagogia += " GROUP BY e.nombre"

            result_terapia = DataBaseHandle.getRecords(query_terapia, tuple(params_terapia) if params_terapia else None)
            result_pedagogia = DataBaseHandle.getRecords(query_pedagogia, tuple(params_pedagogia) if params_pedagogia else None)

            data = []
            if result_terapia:
                data.extend(result_terapia)
            if result_pedagogia:
                data.extend(result_pedagogia)

            return {
                'success': True,
                'data': data,
                'total_registros': len(data)
            }

        except Exception as e:
            self.logger.error(f"Error en get_reporte_utilizacion_recursos: {e}")
            return {
                'success': False,
                'message': f'Error generando reporte: {str(e)}',
                'data': []
            }

    def get_estadisticas_generales_reportes(self, fecha_inicio=None, fecha_fin=None):
        """Obtiene estadisticas generales para reportes administrativos"""
        try:
            query_terapeuticas = """
                SELECT
                    'Sesiones Terapeuticas' as categoria,
                    COUNT(DISTINCT cs.id) as total_programadas,
                    COUNT(DISTINCT CASE WHEN asist.asistio = true THEN cs.id END) as total_realizadas,
                    COUNT(DISTINCT CASE WHEN cs.estado = 'cancelada' THEN cs.id END) as total_canceladas,
                    ROUND(
                        (COUNT(DISTINCT CASE WHEN asist.asistio = true THEN cs.id END) * 100.0 /
                         NULLIF(COUNT(DISTINCT cs.id), 0)), 2
                    ) as porcentaje_efectividad
                FROM cronograma_sesiones cs
                LEFT JOIN asistencia_sesiones asist ON cs.id = asist.id_cronograma
                WHERE 1=1
            """

            query_pedagogicas = """
                SELECT
                    'Sesiones Pedagogicas' as categoria,
                    COUNT(DISTINCT cc.id) as total_programadas,
                    COUNT(DISTINCT CASE WHEN asist.asistio = true THEN cc.id END) as total_realizadas,
                    COUNT(DISTINCT CASE WHEN cc.estado = 'cancelada' THEN cc.id END) as total_canceladas,
                    ROUND(
                        (COUNT(DISTINCT CASE WHEN asist.asistio = true THEN cc.id END) * 100.0 /
                         NULLIF(COUNT(DISTINCT cc.id), 0)), 2
                    ) as porcentaje_efectividad
                FROM cronograma_clases cc
                LEFT JOIN asistencia_clases asist ON cc.id = asist.id_cronograma
                WHERE 1=1
            """

            params = []

            if fecha_inicio:
                query_terapeuticas += " AND cs.fecha_programada >= %s"
                query_pedagogicas += " AND cc.fecha_programada >= %s"
                params.append(fecha_inicio)

            if fecha_fin:
                query_terapeuticas += " AND cs.fecha_programada <= %s"
                query_pedagogicas += " AND cc.fecha_programada <= %s"
                params.append(fecha_fin)

            result_terapeuticas = DataBaseHandle.getRecords(query_terapeuticas, tuple(params) if params else None)
            result_pedagogicas = DataBaseHandle.getRecords(query_pedagogicas, tuple(params) if params else None)

            data = []
            if result_terapeuticas:
                data.extend(result_terapeuticas)
            if result_pedagogicas:
                data.extend(result_pedagogicas)

            return {
                'success': True,
                'data': data,
                'total_registros': len(data)
            }

        except Exception as e:
            self.logger.error(f"Error en get_estadisticas_generales_reportes: {e}")
            return {
                'success': False,
                'message': f'Error generando reporte: {str(e)}',
                'data': []
            }