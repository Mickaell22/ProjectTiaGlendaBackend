-- =============================================
-- CENTRO TÍA GLENDA - ÍNDICES DE OPTIMIZACIÓN PARA SESIONES DE TERAPIA
-- Archivo: 03_indices_optimizacion.sql
-- Descripción: Índices adicionales para mejorar el rendimiento de consultas
-- =============================================

-- =============================================
-- ÍNDICES PARA OPTIMIZACIÓN DE SESIONES DE TERAPIA
-- =============================================

-- Índice para búsquedas por fecha de inicio en sesiones
CREATE INDEX IF NOT EXISTS idx_sesion_terapia_fecha_inicio
    ON sesion_terapia(fecha_inicio);

-- Índice para búsquedas por estado y centro
CREATE INDEX IF NOT EXISTS idx_sesion_terapia_estado_centro
    ON sesion_terapia(estado, id_centro);

-- Índice para búsquedas por terapeuta y estado
CREATE INDEX IF NOT EXISTS idx_sesion_terapia_terapeuta_estado
    ON sesion_terapia(id_terapeuta, estado);

-- Índice para búsquedas de sesiones activas por fecha
CREATE INDEX IF NOT EXISTS idx_sesion_terapia_activas_fecha
    ON sesion_terapia(fecha_inicio, fecha_fin)
    WHERE estado IN ('planificada', 'en_curso');

-- =============================================
-- ÍNDICES PARA CRONOGRAMA DE SESIONES
-- =============================================

-- Índice compuesto para cronograma por fecha y estado (consultas más frecuentes)
CREATE INDEX IF NOT EXISTS idx_cronograma_fecha_estado
    ON cronograma_sesiones(fecha_programada, estado);

-- Índice para sesiones de hoy
CREATE INDEX IF NOT EXISTS idx_cronograma_sesiones_hoy
    ON cronograma_sesiones(fecha_programada, estado, id_sesion)
    WHERE fecha_programada = CURRENT_DATE;

-- Índice para búsquedas por sesión y estado
CREATE INDEX IF NOT EXISTS idx_cronograma_sesion_estado
    ON cronograma_sesiones(id_sesion, estado);

-- Índice para reprogramaciones
CREATE INDEX IF NOT EXISTS idx_cronograma_reprogramaciones
    ON cronograma_sesiones(fecha_original, estado)
    WHERE fecha_original IS NOT NULL;

-- =============================================
-- ÍNDICES PARA ASISTENCIAS
-- =============================================

-- Índice compuesto para asistencias por cronograma y paciente
CREATE INDEX IF NOT EXISTS idx_asistencia_cronograma_paciente
    ON asistencia_sesiones(id_cronograma, id_paciente);

-- Índice para búsquedas de asistencias por paciente
CREATE INDEX IF NOT EXISTS idx_asistencia_paciente_fecha
    ON asistencia_sesiones(id_paciente, fecha_creacion);

-- Índice para estadísticas de asistencia
CREATE INDEX IF NOT EXISTS idx_asistencia_estado_asistio
    ON asistencia_sesiones(estado_asistencia, asistio);

-- =============================================
-- ÍNDICES PARA SESION_PACIENTE
-- =============================================

-- Índice para pacientes activos en sesiones
CREATE INDEX IF NOT EXISTS idx_sesion_paciente_activos
    ON sesion_paciente(id_sesion, estado)
    WHERE estado = 'activo';

-- Índice para búsquedas por paciente y estado
CREATE INDEX IF NOT EXISTS idx_sesion_paciente_estado
    ON sesion_paciente(id_paciente, estado, fecha_inscripcion);

-- =============================================
-- ÍNDICES PARA PERSONAL (mejorar consultas de terapeutas)
-- =============================================

-- Índice para terapeutas activos por centro
CREATE INDEX IF NOT EXISTS idx_personal_centro_estado
    ON personal(id_centro, estado)
    WHERE estado = 'activo';

-- Índice para personal por especialidad y centro
CREATE INDEX IF NOT EXISTS idx_personal_especialidad_centro
    ON personal(id_especialidad, id_centro, estado);

-- =============================================
-- ÍNDICES PARA PACIENTES
-- =============================================

-- Índice para pacientes activos por centro
CREATE INDEX IF NOT EXISTS idx_paciente_centro_estado
    ON paciente(id_centro, estado)
    WHERE estado = 'activo';

-- Índice para búsquedas por estado de tratamiento
CREATE INDEX IF NOT EXISTS idx_paciente_estado_tratamiento
    ON paciente(estado_tratamiento, id_centro);

-- =============================================
-- ÍNDICES FUNCIONALES PARA OPTIMIZACIÓN
-- =============================================

-- Índice funcional para búsquedas por mes/año en cronograma
CREATE INDEX IF NOT EXISTS idx_cronograma_mes_año
    ON cronograma_sesiones(EXTRACT(YEAR FROM fecha_programada), EXTRACT(MONTH FROM fecha_programada));

-- Índice funcional para días de la semana en sesiones
CREATE INDEX IF NOT EXISTS idx_sesion_terapia_dias_semana_gin
    ON sesion_terapia USING gin(dias_semana);

-- =============================================
-- ÍNDICES PARA CONSULTAS DE ESTADÍSTICAS
-- =============================================

-- Índice para cálculos de ingresos
CREATE INDEX IF NOT EXISTS idx_sesion_terapia_costos
    ON sesion_terapia(costo_total, costo_sesion, estado, fecha_creacion);

-- Índice para estadísticas por fecha de creación
CREATE INDEX IF NOT EXISTS idx_sesion_terapia_fecha_creacion_mes
    ON sesion_terapia(DATE_TRUNC('month', fecha_creacion), estado);

-- =============================================
-- COMENTARIOS Y DOCUMENTACIÓN
-- =============================================

COMMENT ON INDEX idx_sesion_terapia_fecha_inicio IS 'Optimiza búsquedas por rango de fechas en sesiones';
COMMENT ON INDEX idx_cronograma_fecha_estado IS 'Optimiza consultas de cronograma por fecha y estado';
COMMENT ON INDEX idx_asistencia_cronograma_paciente IS 'Optimiza consultas de asistencia por cronograma y paciente';
COMMENT ON INDEX idx_sesion_terapia_dias_semana_gin IS 'Optimiza búsquedas por días de la semana usando GIN index';

-- =============================================
-- ESTADÍSTICAS Y MANTENIMIENTO
-- =============================================

-- Analizar las tablas después de crear los índices
ANALYZE sesion_terapia;
ANALYZE cronograma_sesiones;
ANALYZE asistencia_sesiones;
ANALYZE sesion_paciente;
ANALYZE personal;
ANALYZE paciente;

-- Log de creación de índices
DO $$
BEGIN
    RAISE NOTICE 'Índices de optimización para sesiones de terapia creados exitosamente';
    RAISE NOTICE 'Tablas analizadas para estadísticas actualizadas';
    RAISE NOTICE 'Total de índices nuevos: 20';
END $$;