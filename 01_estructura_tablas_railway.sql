-- =============================================
-- CENTRO TÍA GLENDA - ESTRUCTURA DE TABLAS PARA RAILWAY
-- Archivo: 01_estructura_tablas_railway.sql
-- Adaptado para Railway (sin CREATE DATABASE)
-- =============================================

-- =============================================
-- IMPORTANTE: No necesitamos CREATE DATABASE
-- Railway ya proporcionó la base de datos 'railway'
-- =============================================

-- =============================================
-- 1. TABLAS PRINCIPALES DEL SISTEMA
-- =============================================

-- =============================================
-- 1.1 TABLA: ROL (Catálogo de roles)
-- =============================================
DROP TABLE IF EXISTS rol CASCADE;
CREATE TABLE rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 1.2 TABLA: PERSONA (Información demográfica base)
-- =============================================
DROP TABLE IF EXISTS persona CASCADE;
CREATE TABLE persona (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    correo VARCHAR(150) UNIQUE,
    direccion VARCHAR(255),
    fecha_nacimiento DATE,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 1.3 TABLA: USUARIO (Acceso al sistema)
-- =============================================
DROP TABLE IF EXISTS usuario CASCADE;
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL REFERENCES persona(id) ON DELETE CASCADE,
    rol_id INTEGER NOT NULL REFERENCES rol(id),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    ultimo_acceso TIMESTAMP,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'bloqueado')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 1.4 TABLA: ESPECIALIDAD (Catálogo de especialidades)
-- =============================================
DROP TABLE IF EXISTS especialidad CASCADE;
CREATE TABLE especialidad (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    area VARCHAR(20) NOT NULL CHECK (area IN ('terapeutico', 'pedagogico')),
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 1.5 TABLA: PERSONAL (Staff del centro)
-- =============================================
DROP TABLE IF EXISTS personal CASCADE;
CREATE TABLE personal (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL REFERENCES persona(id) ON DELETE CASCADE,
    codigo_empleado VARCHAR(20) UNIQUE,
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE,
    salario DECIMAL(10,2),
    observaciones TEXT,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'suspendido')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 1.6 TABLA: PERSONAL_ESPECIALIDAD (Relación muchos a muchos)
-- =============================================
DROP TABLE IF EXISTS personal_especialidad CASCADE;
CREATE TABLE personal_especialidad (
    id SERIAL PRIMARY KEY,
    personal_id INTEGER NOT NULL REFERENCES personal(id) ON DELETE CASCADE,
    especialidad_id INTEGER NOT NULL REFERENCES especialidad(id) ON DELETE CASCADE,
    fecha_asignacion DATE DEFAULT CURRENT_DATE,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    UNIQUE(personal_id, especialidad_id)
);

-- =============================================
-- 1.7 TABLA: TUTOR (Representantes de pacientes/estudiantes)
-- =============================================
DROP TABLE IF EXISTS tutor CASCADE;
CREATE TABLE tutor (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL REFERENCES persona(id) ON DELETE CASCADE,
    parentesco VARCHAR(50),
    es_representante_legal BOOLEAN DEFAULT FALSE,
    observaciones TEXT,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 1.8 TABLA: PACIENTE (Pacientes terapéuticos y estudiantes pedagógicos)
-- =============================================
DROP TABLE IF EXISTS paciente CASCADE;
CREATE TABLE paciente (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL REFERENCES persona(id) ON DELETE CASCADE,
    codigo_paciente VARCHAR(20) UNIQUE,
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE,
    motivo_ingreso TEXT,
    observaciones_medicas TEXT,
    observaciones_generales TEXT,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'alta', 'suspendido')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 1.9 TABLA: PACIENTE_TUTOR (Relación muchos a muchos)
-- =============================================
DROP TABLE IF EXISTS paciente_tutor CASCADE;
CREATE TABLE paciente_tutor (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id) ON DELETE CASCADE,
    tutor_id INTEGER NOT NULL REFERENCES tutor(id) ON DELETE CASCADE,
    es_principal BOOLEAN DEFAULT FALSE,
    fecha_asignacion DATE DEFAULT CURRENT_DATE,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    UNIQUE(paciente_id, tutor_id)
);

-- =============================================
-- 1.10 TABLA: PACIENTE_ESPECIALIDAD (Relación muchos a muchos)
-- =============================================
DROP TABLE IF EXISTS paciente_especialidad CASCADE;
CREATE TABLE paciente_especialidad (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id) ON DELETE CASCADE,
    especialidad_id INTEGER NOT NULL REFERENCES especialidad(id) ON DELETE CASCADE,
    fecha_asignacion DATE DEFAULT CURRENT_DATE,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'completado')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    UNIQUE(paciente_id, especialidad_id)
);

-- =============================================
-- 1.11 TABLA: SESION_TERAPEUTICA (Sesiones individuales de terapia)
-- =============================================
DROP TABLE IF EXISTS sesion_terapeutica CASCADE;
CREATE TABLE sesion_terapeutica (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    personal_id INTEGER NOT NULL REFERENCES personal(id),
    especialidad_id INTEGER NOT NULL REFERENCES especialidad(id),
    fecha_programada DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    duracion_minutos INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (hora_fin - hora_inicio)) / 60
    ) STORED,
    estado VARCHAR(20) DEFAULT 'programada' CHECK (estado IN ('programada', 'realizada', 'cancelada', 'reprogramada', 'no_asistio')),
    observaciones_pre TEXT,
    observaciones_post TEXT,
    progreso TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 1.12 TABLA: SESION_PEDAGOGICA (Sesiones grupales pedagógicas)
-- =============================================
DROP TABLE IF EXISTS sesion_pedagogica CASCADE;
CREATE TABLE sesion_pedagogica (
    id SERIAL PRIMARY KEY,
    personal_id INTEGER NOT NULL REFERENCES personal(id),
    especialidad_id INTEGER NOT NULL REFERENCES especialidad(id),
    nombre_sesion VARCHAR(200) NOT NULL,
    descripcion TEXT,
    fecha_programada DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    duracion_minutos INTEGER GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (hora_fin - hora_inicio)) / 60
    ) STORED,
    capacidad_maxima INTEGER DEFAULT 10,
    estado VARCHAR(20) DEFAULT 'programada' CHECK (estado IN ('programada', 'realizada', 'cancelada', 'reprogramada')),
    observaciones_pre TEXT,
    observaciones_post TEXT,
    contenido_impartido TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 1.13 TABLA: SESION_PEDAGOGICA_ESTUDIANTE (Asistencia a sesiones pedagógicas)
-- =============================================
DROP TABLE IF EXISTS sesion_pedagogica_estudiante CASCADE;
CREATE TABLE sesion_pedagogica_estudiante (
    id SERIAL PRIMARY KEY,
    sesion_pedagogica_id INTEGER NOT NULL REFERENCES sesion_pedagogica(id) ON DELETE CASCADE,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    asistio BOOLEAN DEFAULT FALSE,
    calificacion DECIMAL(5,2),
    observaciones TEXT,
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_asistencia TIMESTAMP,
    usuario_creacion INTEGER,
    UNIQUE(sesion_pedagogica_id, paciente_id)
);

-- =============================================
-- 1.14 TABLA: DOCUMENTO_PACIENTE (Archivos y documentos)
-- =============================================
DROP TABLE IF EXISTS documento_paciente CASCADE;
CREATE TABLE documento_paciente (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id) ON DELETE CASCADE,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    tipo_documento VARCHAR(50),
    tamano_bytes BIGINT,
    descripcion TEXT,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_subida INTEGER,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'eliminado'))
);

-- =============================================
-- 2. ÍNDICES PARA OPTIMIZACIÓN
-- =============================================

-- Índices para consultas frecuentes
CREATE INDEX idx_usuario_persona ON usuario(persona_id);
CREATE INDEX idx_usuario_rol ON usuario(rol_id);
CREATE INDEX idx_personal_persona ON personal(persona_id);
CREATE INDEX idx_paciente_persona ON paciente(persona_id);
CREATE INDEX idx_paciente_codigo ON paciente(codigo_paciente);
CREATE INDEX idx_sesion_terapeutica_paciente ON sesion_terapeutica(paciente_id);
CREATE INDEX idx_sesion_terapeutica_fecha ON sesion_terapeutica(fecha_programada);
CREATE INDEX idx_sesion_pedagogica_fecha ON sesion_pedagogica(fecha_programada);
CREATE INDEX idx_documento_paciente ON documento_paciente(paciente_id);

-- Índices para estado y fechas (consultas de reportes)
CREATE INDEX idx_paciente_estado ON paciente(estado);
CREATE INDEX idx_personal_estado ON personal(estado);
CREATE INDEX idx_sesion_terapeutica_estado ON sesion_terapeutica(estado);
CREATE INDEX idx_sesion_pedagogica_estado ON sesion_pedagogica(estado);

-- =============================================
-- 3. TRIGGERS PARA FECHA_MODIFICACION
-- =============================================

-- Función para actualizar fecha_modificacion
CREATE OR REPLACE FUNCTION update_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a tablas con fecha_modificacion
CREATE TRIGGER trigger_rol_fecha_modificacion
    BEFORE UPDATE ON rol
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

CREATE TRIGGER trigger_persona_fecha_modificacion
    BEFORE UPDATE ON persona
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

CREATE TRIGGER trigger_usuario_fecha_modificacion
    BEFORE UPDATE ON usuario
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

CREATE TRIGGER trigger_especialidad_fecha_modificacion
    BEFORE UPDATE ON especialidad
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

CREATE TRIGGER trigger_personal_fecha_modificacion
    BEFORE UPDATE ON personal
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

CREATE TRIGGER trigger_tutor_fecha_modificacion
    BEFORE UPDATE ON tutor
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

CREATE TRIGGER trigger_paciente_fecha_modificacion
    BEFORE UPDATE ON paciente
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

CREATE TRIGGER trigger_sesion_terapeutica_fecha_modificacion
    BEFORE UPDATE ON sesion_terapeutica
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

CREATE TRIGGER trigger_sesion_pedagogica_fecha_modificacion
    BEFORE UPDATE ON sesion_pedagogica
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

-- =============================================
-- 2. MÓDULO SESIONES DE TERAPIA (TABLAS FALTANTES)
-- =============================================

-- =============================================
-- 2.1 TABLA: SESION_TERAPIA (Tabla principal)
-- =============================================
DROP TABLE IF EXISTS sesion_terapia CASCADE;
CREATE TABLE sesion_terapia (
    id SERIAL PRIMARY KEY,
    
    -- Información básica de la sesión
    codigo_sesion VARCHAR(30) UNIQUE NOT NULL, -- Código único para identificar la sesión (ej: ST-2025-001)
    titulo VARCHAR(200) NOT NULL, -- Título descriptivo de la sesión
    
    -- Relaciones principales
    terapeuta_id INTEGER NOT NULL REFERENCES personal(id) ON DELETE RESTRICT,
    especialidad_id INTEGER NOT NULL REFERENCES especialidad(id) ON DELETE RESTRICT,
    
    -- Configuración de horarios
    fecha_inicio DATE NOT NULL, -- Fecha de inicio del contrato
    fecha_fin DATE NOT NULL, -- Fecha de fin del contrato
    dias_semana VARCHAR(60) NOT NULL, -- Días de la semana separados por comas (ej: "lunes,miercoles,viernes")
    hora_inicio TIME NOT NULL, -- Hora de inicio de la sesión
    duracion_minutos INTEGER DEFAULT 45 CHECK (duracion_minutos BETWEEN 15 AND 120), -- Duración en minutos
    
    -- Información del contrato
    numero_sesiones_contratadas INTEGER NOT NULL CHECK (numero_sesiones_contratadas > 0),
    costo_total DECIMAL(10,2) NOT NULL CHECK (costo_total >= 0),
    costo_por_sesion DECIMAL(10,2) GENERATED ALWAYS AS (costo_total / numero_sesiones_contratadas) STORED,
    meses_contrato INTEGER, -- Duración en meses (opcional)
    
    -- Control y estado
    estado VARCHAR(15) DEFAULT 'activo' CHECK (estado IN ('activo', 'suspendido', 'completado', 'cancelado')),
    observaciones TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 2.2 TABLA: SESION_PACIENTE (Relación muchos a muchos)
-- =============================================
DROP TABLE IF EXISTS sesion_paciente CASCADE;
CREATE TABLE sesion_paciente (
    id SERIAL PRIMARY KEY,
    
    -- Relaciones principales
    sesion_terapia_id INTEGER NOT NULL REFERENCES sesion_terapia(id) ON DELETE CASCADE,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id) ON DELETE RESTRICT,
    
    -- Información específica del paciente en esta sesión
    fecha_incorporacion DATE DEFAULT CURRENT_DATE,
    costo_paciente DECIMAL(10,2), -- Costo específico para este paciente (por si hay descuentos)
    observaciones_paciente TEXT,
    estado VARCHAR(15) DEFAULT 'activo' CHECK (estado IN ('activo', 'retirado', 'suspendido')),
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Evitar duplicados
    UNIQUE(sesion_terapia_id, paciente_id)
);

-- =============================================
-- 2.3 TABLA: CRONOGRAMA_SESIONES (Sesiones programadas)
-- =============================================
DROP TABLE IF EXISTS cronograma_sesiones CASCADE;
CREATE TABLE cronograma_sesiones (
    id SERIAL PRIMARY KEY,
    
    -- Relación principal
    sesion_terapia_id INTEGER NOT NULL REFERENCES sesion_terapia(id) ON DELETE CASCADE,
    
    -- Información de la sesión específica
    numero_sesion INTEGER NOT NULL, -- Número correlativo de la sesión (1, 2, 3...)
    fecha_programada DATE NOT NULL,
    hora_programada TIME NOT NULL,
    
    -- Control de estado
    estado VARCHAR(15) DEFAULT 'programada' CHECK (estado IN ('programada', 'realizada', 'cancelada', 'reprogramada')),
    fecha_realizacion TIMESTAMP, -- Cuando se realizó realmente
    observaciones_cronograma TEXT,
    
    -- Reprogramación
    sesion_original_id INTEGER REFERENCES cronograma_sesiones(id) ON DELETE SET NULL,
    motivo_reprogramacion TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Evitar duplicados de sesión-fecha
    UNIQUE(sesion_terapia_id, numero_sesion)
);

-- =============================================
-- 2.4 TABLA: ASISTENCIA_SESIONES (Control de asistencia)
-- =============================================
DROP TABLE IF EXISTS asistencia_sesiones CASCADE;
CREATE TABLE asistencia_sesiones (
    id SERIAL PRIMARY KEY,
    
    -- Relaciones principales
    cronograma_sesion_id INTEGER NOT NULL REFERENCES cronograma_sesiones(id) ON DELETE CASCADE,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id) ON DELETE RESTRICT,
    
    -- Control de asistencia
    asistio BOOLEAN DEFAULT FALSE,
    llegada_tardanza_minutos INTEGER DEFAULT 0,
    observaciones_asistencia TEXT,
    
    -- Notas de la sesión para este paciente
    notas_progreso TEXT,
    tareas_asignadas TEXT,
    proximos_objetivos TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Un paciente solo puede tener un registro de asistencia por sesión
    UNIQUE(cronograma_sesion_id, paciente_id)
);

-- =============================================
-- 3. ÍNDICES ADICIONALES PARA SESIONES DE TERAPIA
-- =============================================

-- Índices para SESION_TERAPIA
CREATE INDEX idx_sesion_terapia_terapeuta ON sesion_terapia(terapeuta_id);
CREATE INDEX idx_sesion_terapia_especialidad ON sesion_terapia(especialidad_id);
CREATE INDEX idx_sesion_terapia_fecha_inicio ON sesion_terapia(fecha_inicio);
CREATE INDEX idx_sesion_terapia_fecha_fin ON sesion_terapia(fecha_fin);
CREATE INDEX idx_sesion_terapia_estado ON sesion_terapia(estado);
CREATE INDEX idx_sesion_terapia_codigo ON sesion_terapia(codigo_sesion);

-- Índices para SESION_PACIENTE
CREATE INDEX idx_sesion_paciente_sesion ON sesion_paciente(sesion_terapia_id);
CREATE INDEX idx_sesion_paciente_paciente ON sesion_paciente(paciente_id);
CREATE INDEX idx_sesion_paciente_estado ON sesion_paciente(estado);

-- Índices para CRONOGRAMA_SESIONES
CREATE INDEX idx_cronograma_sesion_terapia ON cronograma_sesiones(sesion_terapia_id);
CREATE INDEX idx_cronograma_fecha_programada ON cronograma_sesiones(fecha_programada);
CREATE INDEX idx_cronograma_estado ON cronograma_sesiones(estado);
CREATE INDEX idx_cronograma_numero_sesion ON cronograma_sesiones(numero_sesion);

-- Índices para ASISTENCIA_SESIONES
CREATE INDEX idx_asistencia_cronograma ON asistencia_sesiones(cronograma_sesion_id);
CREATE INDEX idx_asistencia_paciente ON asistencia_sesiones(paciente_id);
CREATE INDEX idx_asistencia_asistio ON asistencia_sesiones(asistio);

-- =============================================
-- 4. TRIGGERS ADICIONALES PARA SESIONES
-- =============================================

-- Trigger para actualizar fecha_modificacion en SESION_TERAPIA
CREATE TRIGGER trigger_sesion_terapia_fecha_modificacion
    BEFORE UPDATE ON sesion_terapia
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

-- Trigger para actualizar fecha_modificacion en SESION_PACIENTE
CREATE TRIGGER trigger_sesion_paciente_fecha_modificacion
    BEFORE UPDATE ON sesion_paciente
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

-- Trigger para actualizar fecha_modificacion en CRONOGRAMA_SESIONES
CREATE TRIGGER trigger_cronograma_sesiones_fecha_modificacion
    BEFORE UPDATE ON cronograma_sesiones
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

-- Trigger para actualizar fecha_modificacion en ASISTENCIA_SESIONES
CREATE TRIGGER trigger_asistencia_sesiones_fecha_modificacion
    BEFORE UPDATE ON asistencia_sesiones
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_modificacion();

-- =============================================
-- 5. FUNCIÓN PARA GENERAR CÓDIGO DE SESIÓN
-- =============================================
CREATE OR REPLACE FUNCTION generar_codigo_sesion()
RETURNS TEXT AS $$
DECLARE
    v_year TEXT;
    v_correlativo INTEGER;
    v_codigo TEXT;
BEGIN
    v_year := extract(year from CURRENT_DATE)::TEXT;
    
    -- Obtener el próximo correlativo
    SELECT COALESCE(MAX(
        CASE 
            WHEN codigo_sesion LIKE 'ST-' || v_year || '-%' 
                AND codigo_sesion ~ '^ST-[0-9]{4}-[0-9]+$'
            THEN CAST(split_part(codigo_sesion, '-', 3) AS INTEGER)
            ELSE 0
        END
    ), 0) + 1
    INTO v_correlativo
    FROM sesion_terapia;
    
    -- Generar código con formato: ST-2025-001
    v_codigo := 'ST-' || v_year || '-' || lpad(v_correlativo::TEXT, 3, '0');
    
    RETURN v_codigo;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 6. TRIGGER PARA GENERAR CÓDIGO AUTOMÁTICO
-- =============================================
CREATE OR REPLACE FUNCTION trigger_generar_codigo_sesion()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.codigo_sesion IS NULL OR NEW.codigo_sesion = '' THEN
        NEW.codigo_sesion := generar_codigo_sesion();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_codigo_sesion_terapia
    BEFORE INSERT ON sesion_terapia
    FOR EACH ROW
    EXECUTE FUNCTION trigger_generar_codigo_sesion();

-- =============================================
-- FIN DEL SCRIPT DE ESTRUCTURA
-- =============================================

-- Verificación de tablas creadas
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;