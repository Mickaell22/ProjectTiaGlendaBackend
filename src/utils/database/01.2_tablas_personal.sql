-- =============================================
-- CENTRO TÍA GLENDA - TABLAS DE PERSONAL
-- Archivo: 01.2_tablas_personal.sql
-- Descripción: Gestión de personal y sus especialidades
-- =============================================

-- =============================================
-- 1. TABLA: PERSONAL
-- =============================================
CREATE TABLE IF NOT EXISTS personal (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL,
    id_especialidad INTEGER NOT NULL, -- Especialidad principal
    numero_registro VARCHAR(50) UNIQUE,
    fecha_ingreso DATE NOT NULL,
    fecha_salida DATE,
    cargo VARCHAR(100),
    tipo_contrato VARCHAR(20) CHECK (tipo_contrato IN ('indefinido', 'temporal', 'honorarios', 'practicante')),
    salario DECIMAL(10,2),
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'vacaciones', 'licencia')),
    observaciones TEXT,
    id_centro INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- =============================================
-- 2. TABLA: PERSONAL_ESPECIALIDADES (Especialidades múltiples)
-- =============================================
CREATE TABLE IF NOT EXISTS personal_especialidades (
    id SERIAL PRIMARY KEY,
    id_personal INTEGER NOT NULL,
    id_especialidad INTEGER NOT NULL,
    es_principal BOOLEAN DEFAULT FALSE,
    nivel_competencia VARCHAR(20) DEFAULT 'basico' CHECK (nivel_competencia IN ('basico', 'intermedio', 'avanzado', 'experto')),
    certificacion VARCHAR(255),
    fecha_asignacion DATE DEFAULT CURRENT_DATE,
    fecha_vencimiento_certificacion DATE,
    observaciones TEXT,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'suspendido')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_personal) REFERENCES personal(id) ON DELETE CASCADE,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE RESTRICT,
    
    -- Constraint para evitar duplicados
    UNIQUE (id_personal, id_especialidad)
);

-- =============================================
-- 3. TABLA: DOCUMENTOS_PERSONAL
-- =============================================
CREATE TABLE IF NOT EXISTS documentos_personal (
    id SERIAL PRIMARY KEY,
    id_personal INTEGER NOT NULL,
    tipo_documento VARCHAR(50) NOT NULL CHECK (tipo_documento IN 
        ('cedula', 'curriculum', 'titulo_profesional', 'certificacion', 'contrato', 
         'acuerdo_confidencialidad', 'referencias', 'antecedentes_penales', 'record_policial', 'otros')),
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    tamaño_archivo INTEGER,
    tipo_mime VARCHAR(100),
    descripcion TEXT,
    es_obligatorio BOOLEAN DEFAULT FALSE,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATE,
    
    -- Control de validación (solo admin puede validar)
    estado_validacion VARCHAR(20) DEFAULT 'pendiente' CHECK (estado_validacion IN 
        ('pendiente', 'en_revision', 'aprobado', 'rechazado', 'vencido')),
    validado_por INTEGER, -- ID del usuario que validó
    fecha_validacion TIMESTAMP,
    observaciones_validacion TEXT,
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_personal) REFERENCES personal(id) ON DELETE CASCADE,
    FOREIGN KEY (validado_por) REFERENCES usuario(id)
);

-- =============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =============================================
CREATE INDEX IF NOT EXISTS idx_personal_persona ON personal(persona_id);
CREATE INDEX IF NOT EXISTS idx_personal_especialidad ON personal(id_especialidad);
CREATE INDEX IF NOT EXISTS idx_personal_centro ON personal(id_centro);
CREATE INDEX IF NOT EXISTS idx_personal_especialidades_personal ON personal_especialidades(id_personal);
CREATE INDEX IF NOT EXISTS idx_personal_especialidades_especialidad ON personal_especialidades(id_especialidad);
CREATE INDEX IF NOT EXISTS idx_documentos_personal_personal ON documentos_personal(id_personal);
CREATE INDEX IF NOT EXISTS idx_documentos_personal_tipo ON documentos_personal(tipo_documento);
CREATE INDEX IF NOT EXISTS idx_documentos_personal_estado ON documentos_personal(estado_validacion);

-- =============================================
-- TRIGGERS PARA AUDITORÍA
-- =============================================
CREATE TRIGGER trigger_personal_fecha_modificacion
    BEFORE UPDATE ON personal
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_personal_especialidades_fecha_modificacion
    BEFORE UPDATE ON personal_especialidades
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_documentos_personal_fecha_modificacion
    BEFORE UPDATE ON documentos_personal
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- =============================================
-- FUNCIONES DE VALIDACIÓN PERSONAL
-- =============================================

-- Función para asignar especialidad principal automáticamente
CREATE OR REPLACE FUNCTION asignar_especialidad_principal_personal()
RETURNS TRIGGER AS $$
BEGIN
    -- Si es la primera especialidad del personal, hacerla principal
    IF NEW.es_principal = TRUE THEN
        -- Quitar principal de otras especialidades del mismo personal
        UPDATE personal_especialidades 
        SET es_principal = FALSE 
        WHERE id_personal = NEW.id_personal 
        AND id != NEW.id;
    END IF;
    
    -- Si no hay especialidad principal, hacer esta la principal
    IF NOT EXISTS (
        SELECT 1 FROM personal_especialidades 
        WHERE id_personal = NEW.id_personal 
        AND es_principal = TRUE 
        AND id != COALESCE(NEW.id, 0)
    ) THEN
        NEW.es_principal = TRUE;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para especialidad principal
CREATE TRIGGER trigger_especialidad_principal_personal
    BEFORE INSERT OR UPDATE ON personal_especialidades
    FOR EACH ROW
    EXECUTE FUNCTION asignar_especialidad_principal_personal();

-- Función para validar competencias
CREATE OR REPLACE FUNCTION validar_competencia_personal(
    p_id_personal INTEGER,
    p_id_especialidad INTEGER
) RETURNS BOOLEAN AS $$
BEGIN
    -- Verificar si el personal tiene la especialidad asignada
    RETURN EXISTS (
        SELECT 1 FROM personal_especialidades pe
        WHERE pe.id_personal = p_id_personal
        AND pe.id_especialidad = p_id_especialidad
        AND pe.estado = 'activo'
    );
END;
$$ LANGUAGE plpgsql;

-- Función para obtener especialidad principal del personal
CREATE OR REPLACE FUNCTION obtener_especialidad_principal_personal(p_id_personal INTEGER)
RETURNS INTEGER AS $$
DECLARE
    especialidad_id INTEGER;
BEGIN
    SELECT pe.id_especialidad INTO especialidad_id
    FROM personal_especialidades pe
    WHERE pe.id_personal = p_id_personal
    AND pe.es_principal = TRUE
    AND pe.estado = 'activo';
    
    RETURN especialidad_id;
END;
$$ LANGUAGE plpgsql;

-- Función para alertas de documentos vencidos
CREATE OR REPLACE FUNCTION obtener_documentos_personal_vencidos(dias_alerta INTEGER DEFAULT 30)
RETURNS TABLE (
    id_personal INTEGER,
    nombre_personal VARCHAR,
    tipo_documento VARCHAR,
    fecha_vencimiento DATE,
    dias_para_vencer INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dp.id_personal,
        p.nombre || ' ' || p.apellido as nombre_personal,
        dp.tipo_documento,
        dp.fecha_vencimiento,
        (dp.fecha_vencimiento - CURRENT_DATE) as dias_para_vencer
    FROM documentos_personal dp
    JOIN personal per ON dp.id_personal = per.id
    JOIN persona p ON per.persona_id = p.id
    WHERE dp.fecha_vencimiento IS NOT NULL
    AND dp.fecha_vencimiento <= CURRENT_DATE + INTERVAL '1 day' * dias_alerta
    AND dp.estado_validacion = 'aprobado'
    ORDER BY dp.fecha_vencimiento ASC;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- COMENTARIOS EN TABLAS
-- =============================================
COMMENT ON TABLE personal IS 'Información del personal del centro';
COMMENT ON TABLE personal_especialidades IS 'Especialidades múltiples asignadas al personal';
COMMENT ON TABLE documentos_personal IS 'Documentos digitales del personal con validación administrativa';

COMMENT ON COLUMN personal.id_especialidad IS 'Especialidad principal del personal';
COMMENT ON COLUMN personal_especialidades.es_principal IS 'Indica si es la especialidad principal del personal';
COMMENT ON COLUMN personal_especialidades.nivel_competencia IS 'Nivel de competencia en la especialidad';
COMMENT ON COLUMN documentos_personal.es_obligatorio IS 'Indica si el documento es obligatorio para el puesto';
COMMENT ON COLUMN documentos_personal.estado_validacion IS 'Estado de validación del documento por administradores';