-- =============================================
-- CENTRO TÍA GLENDA - TABLAS DE PACIENTES Y TUTORES
-- Archivo: 01.3_tablas_pacientes.sql
-- Descripción: Gestión de pacientes, tutores y especialidades múltiples
-- =============================================

-- =============================================
-- 1. TABLA: TUTOR
-- =============================================
CREATE TABLE IF NOT EXISTS tutor (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    email VARCHAR(150),
    direccion VARCHAR(255),
    parentesco VARCHAR(50) NOT NULL, -- padre, madre, abuelo, tio, etc.
    
    -- Información laboral (Fase 2)
    ocupacion VARCHAR(100),
    direccion_empresa VARCHAR(255),
    telefono_empresa VARCHAR(15),
    nombre_empresa VARCHAR(150),
    
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 2. TABLA: PACIENTE
-- =============================================
CREATE TABLE IF NOT EXISTS paciente (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL,
    id_tutor INTEGER NOT NULL,
    codigo_paciente VARCHAR(20) UNIQUE, -- Auto-generado
    fecha_ingreso DATE NOT NULL,
    motivo_consulta TEXT,
    observaciones TEXT,
    
    -- Control de pausas (Fase 2)
    fecha_inicio_pausa DATE,
    fecha_fin_pausa DATE,
    motivo_pausa TEXT,
    estado_tratamiento VARCHAR(20) DEFAULT 'activo' CHECK (estado_tratamiento IN 
        ('activo', 'pausado', 'finalizado', 'suspendido')),
    
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    id_centro INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_tutor) REFERENCES tutor(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- =============================================
-- 3. TABLA: PACIENTE_ESPECIALIDADES (Especialidades múltiples)
-- =============================================
CREATE TABLE IF NOT EXISTS paciente_especialidades (
    id SERIAL PRIMARY KEY,
    id_paciente INTEGER NOT NULL,
    id_especialidad INTEGER NOT NULL,
    es_principal BOOLEAN DEFAULT FALSE,
    prioridad VARCHAR(10) DEFAULT 'media' CHECK (prioridad IN ('baja', 'media', 'alta', 'urgente')),
    fecha_asignacion DATE DEFAULT CURRENT_DATE,
    fecha_inicio_tratamiento DATE,
    fecha_fin_tratamiento DATE,
    observaciones TEXT,
    requiere_coordinacion BOOLEAN DEFAULT FALSE,
    
    -- Control de pausas específicas por especialidad
    estado_pausa VARCHAR(20) DEFAULT 'activo' CHECK (estado_pausa IN 
        ('activo', 'pausado_general', 'pausado_especialidad', 'finalizado')),
    fecha_inicio_pausa_esp DATE,
    fecha_fin_pausa_esp DATE,
    motivo_pausa_esp TEXT,
    
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'completado')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE CASCADE,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE RESTRICT,
    
    -- Constraint para evitar duplicados
    UNIQUE (id_paciente, id_especialidad)
);

-- =============================================
-- 4. TABLA: DOCUMENTOS_PACIENTE
-- =============================================
CREATE TABLE IF NOT EXISTS documentos_paciente (
    id SERIAL PRIMARY KEY,
    id_paciente INTEGER NOT NULL,
    tipo_documento VARCHAR(50) NOT NULL CHECK (tipo_documento IN 
        ('historia_clinica', 'evaluacion_inicial', 'informe_progreso', 'alta_medica',
         'consentimiento_informado', 'autorizacion_tratamiento', 'cedula_paciente', 
         'cedula_tutor', 'otros')),
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    tamaño_archivo INTEGER,
    tipo_mime VARCHAR(100),
    descripcion TEXT,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE CASCADE
);

-- =============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =============================================
CREATE INDEX IF NOT EXISTS idx_tutor_cedula ON tutor(cedula);
CREATE INDEX IF NOT EXISTS idx_paciente_persona ON paciente(persona_id);
CREATE INDEX IF NOT EXISTS idx_paciente_tutor ON paciente(id_tutor);
CREATE INDEX IF NOT EXISTS idx_paciente_centro ON paciente(id_centro);
CREATE INDEX IF NOT EXISTS idx_paciente_codigo ON paciente(codigo_paciente);
CREATE INDEX IF NOT EXISTS idx_paciente_especialidades_paciente ON paciente_especialidades(id_paciente);
CREATE INDEX IF NOT EXISTS idx_paciente_especialidades_especialidad ON paciente_especialidades(id_especialidad);
CREATE INDEX IF NOT EXISTS idx_documentos_paciente_paciente ON documentos_paciente(id_paciente);
CREATE INDEX IF NOT EXISTS idx_documentos_paciente_tipo ON documentos_paciente(tipo_documento);

-- =============================================
-- TRIGGERS PARA AUDITORÍA
-- =============================================
CREATE TRIGGER trigger_tutor_fecha_modificacion
    BEFORE UPDATE ON tutor
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_paciente_fecha_modificacion
    BEFORE UPDATE ON paciente
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_paciente_especialidades_fecha_modificacion
    BEFORE UPDATE ON paciente_especialidades
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_documentos_paciente_fecha_modificacion
    BEFORE UPDATE ON documentos_paciente
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- =============================================
-- FUNCIONES ESPECÍFICAS PARA PACIENTES
-- =============================================

-- Función para generar código único de paciente
CREATE OR REPLACE FUNCTION generar_codigo_paciente()
RETURNS TRIGGER AS $$
DECLARE
    nuevo_codigo VARCHAR(20);
    centro_codigo VARCHAR(10);
BEGIN
    -- Obtener código del centro
    SELECT codigo INTO centro_codigo 
    FROM centros 
    WHERE id = NEW.id_centro;
    
    -- Generar código único: CENTRO-PAC-YYYY-NNNN
    nuevo_codigo := centro_codigo || '-PAC-' || 
                   TO_CHAR(CURRENT_DATE, 'YYYY') || '-' ||
                   LPAD(nextval('seq_codigo_paciente')::TEXT, 4, '0');
    
    NEW.codigo_paciente := nuevo_codigo;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Secuencia para códigos de paciente
CREATE SEQUENCE IF NOT EXISTS seq_codigo_paciente START 1;

-- Trigger para generar código automático
CREATE TRIGGER trigger_generar_codigo_paciente
    BEFORE INSERT ON paciente
    FOR EACH ROW
    WHEN (NEW.codigo_paciente IS NULL)
    EXECUTE FUNCTION generar_codigo_paciente();

-- Función para asignar especialidad principal automáticamente
CREATE OR REPLACE FUNCTION asignar_especialidad_principal_paciente()
RETURNS TRIGGER AS $$
BEGIN
    -- Si es la primera especialidad del paciente, hacerla principal
    IF NEW.es_principal = TRUE THEN
        -- Quitar principal de otras especialidades del mismo paciente
        UPDATE paciente_especialidades 
        SET es_principal = FALSE 
        WHERE id_paciente = NEW.id_paciente 
        AND id != NEW.id;
    END IF;
    
    -- Si no hay especialidad principal, hacer esta la principal
    IF NOT EXISTS (
        SELECT 1 FROM paciente_especialidades 
        WHERE id_paciente = NEW.id_paciente 
        AND es_principal = TRUE 
        AND id != COALESCE(NEW.id, 0)
    ) THEN
        NEW.es_principal = TRUE;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para especialidad principal
CREATE TRIGGER trigger_especialidad_principal_paciente
    BEFORE INSERT OR UPDATE ON paciente_especialidades
    FOR EACH ROW
    EXECUTE FUNCTION asignar_especialidad_principal_paciente();

-- =============================================
-- FUNCIONES DE CONTROL DE PAUSAS
-- =============================================

-- Función para pausar tratamiento general del paciente
CREATE OR REPLACE FUNCTION pausar_tratamiento_paciente(
    p_id_paciente INTEGER,
    p_fecha_inicio DATE DEFAULT CURRENT_DATE,
    p_fecha_fin DATE DEFAULT NULL,
    p_motivo TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    -- Verificar que el paciente no esté ya pausado
    IF EXISTS (
        SELECT 1 FROM paciente 
        WHERE id = p_id_paciente 
        AND estado_tratamiento = 'pausado'
    ) THEN
        RAISE EXCEPTION 'El paciente ya tiene el tratamiento pausado';
    END IF;
    
    -- Pausar paciente
    UPDATE paciente SET
        estado_tratamiento = 'pausado',
        fecha_inicio_pausa = p_fecha_inicio,
        fecha_fin_pausa = p_fecha_fin,
        motivo_pausa = p_motivo,
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id = p_id_paciente;
    
    -- Pausar todas las especialidades del paciente
    UPDATE paciente_especialidades SET
        estado_pausa = 'pausado_general',
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id_paciente = p_id_paciente
    AND estado = 'activo';
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Función para pausar especialidad específica
CREATE OR REPLACE FUNCTION pausar_especialidad_paciente(
    p_id_paciente INTEGER,
    p_id_especialidad INTEGER,
    p_fecha_inicio DATE DEFAULT CURRENT_DATE,
    p_fecha_fin DATE DEFAULT NULL,
    p_motivo TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    -- Verificar que la especialidad no esté ya pausada
    IF EXISTS (
        SELECT 1 FROM paciente_especialidades 
        WHERE id_paciente = p_id_paciente 
        AND id_especialidad = p_id_especialidad
        AND estado_pausa IN ('pausado_general', 'pausado_especialidad')
    ) THEN
        RAISE EXCEPTION 'Esta especialidad ya está pausada para el paciente';
    END IF;
    
    -- Pausar especialidad específica
    UPDATE paciente_especialidades SET
        estado_pausa = 'pausado_especialidad',
        fecha_inicio_pausa_esp = p_fecha_inicio,
        fecha_fin_pausa_esp = p_fecha_fin,
        motivo_pausa_esp = p_motivo,
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id_paciente = p_id_paciente
    AND id_especialidad = p_id_especialidad;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Función para reanudar tratamiento general
CREATE OR REPLACE FUNCTION reanudar_tratamiento_paciente(
    p_id_paciente INTEGER,
    p_motivo_reanudacion TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    -- Reanudar paciente
    UPDATE paciente SET
        estado_tratamiento = 'activo',
        fecha_inicio_pausa = NULL,
        fecha_fin_pausa = NULL,
        motivo_pausa = p_motivo_reanudacion,
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id = p_id_paciente;
    
    -- Reanudar especialidades que estaban pausadas por pausa general
    UPDATE paciente_especialidades SET
        estado_pausa = 'activo',
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id_paciente = p_id_paciente
    AND estado_pausa = 'pausado_general';
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Función para reanudar especialidad específica
CREATE OR REPLACE FUNCTION reanudar_especialidad_paciente(
    p_id_paciente INTEGER,
    p_id_especialidad INTEGER,
    p_motivo_reanudacion TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    -- Reanudar especialidad específica
    UPDATE paciente_especialidades SET
        estado_pausa = 'activo',
        fecha_inicio_pausa_esp = NULL,
        fecha_fin_pausa_esp = NULL,
        motivo_pausa_esp = p_motivo_reanudacion,
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id_paciente = p_id_paciente
    AND id_especialidad = p_id_especialidad;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Función para detectar pausas vencidas automáticamente
CREATE OR REPLACE FUNCTION detectar_pausas_vencidas()
RETURNS TABLE (
    id_paciente INTEGER,
    nombre_paciente VARCHAR,
    tipo_pausa VARCHAR,
    fecha_vencimiento DATE
) AS $$
BEGIN
    -- Pausas generales vencidas
    RETURN QUERY
    SELECT 
        p.id,
        pe.nombre || ' ' || pe.apellido as nombre_paciente,
        'general'::VARCHAR as tipo_pausa,
        p.fecha_fin_pausa
    FROM paciente p
    JOIN persona pe ON p.persona_id = pe.id
    WHERE p.estado_tratamiento = 'pausado'
    AND p.fecha_fin_pausa IS NOT NULL
    AND p.fecha_fin_pausa <= CURRENT_DATE
    
    UNION ALL
    
    -- Pausas de especialidades vencidas
    SELECT 
        pac.id,
        pe.nombre || ' ' || pe.apellido as nombre_paciente,
        'especialidad'::VARCHAR as tipo_pausa,
        pace.fecha_fin_pausa_esp
    FROM paciente_especialidades pace
    JOIN paciente pac ON pace.id_paciente = pac.id
    JOIN persona pe ON pac.persona_id = pe.id
    WHERE pace.estado_pausa = 'pausado_especialidad'
    AND pace.fecha_fin_pausa_esp IS NOT NULL
    AND pace.fecha_fin_pausa_esp <= CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener especialidad principal del paciente
CREATE OR REPLACE FUNCTION obtener_especialidad_principal_paciente(p_id_paciente INTEGER)
RETURNS INTEGER AS $$
DECLARE
    especialidad_id INTEGER;
BEGIN
    SELECT pe.id_especialidad INTO especialidad_id
    FROM paciente_especialidades pe
    WHERE pe.id_paciente = p_id_paciente
    AND pe.es_principal = TRUE
    AND pe.estado = 'activo';
    
    RETURN especialidad_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- COMENTARIOS EN TABLAS
-- =============================================
COMMENT ON TABLE tutor IS 'Información de tutores/responsables de pacientes';
COMMENT ON TABLE paciente IS 'Información de pacientes del centro';
COMMENT ON TABLE paciente_especialidades IS 'Especialidades múltiples asignadas a cada paciente';
COMMENT ON TABLE documentos_paciente IS 'Documentos digitales de los pacientes';

COMMENT ON COLUMN paciente.estado_tratamiento IS 'Estado actual del tratamiento del paciente';
COMMENT ON COLUMN paciente_especialidades.es_principal IS 'Indica si es la especialidad principal del paciente';
COMMENT ON COLUMN paciente_especialidades.estado_pausa IS 'Estado de pausa específico de la especialidad';
COMMENT ON COLUMN tutor.ocupacion IS 'Ocupación laboral del tutor (Fase 2)';
COMMENT ON COLUMN tutor.nombre_empresa IS 'Empresa donde trabaja el tutor (Fase 2)';