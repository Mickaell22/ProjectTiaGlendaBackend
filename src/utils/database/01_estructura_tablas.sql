-- =============================================
-- CENTRO TÍA GLENDA - ESTRUCTURA DE TABLAS
-- Archivo: 01_estructura_tablas.sql
-- =============================================

-- =============================================
-- 1. CONFIGURACIÓN DE BASE DE DATOS
-- =============================================
DROP DATABASE IF EXISTS centro_tia_glenda;
CREATE DATABASE centro_tia_glenda 
WITH ENCODING 'UTF8' 
LC_COLLATE = 'C' 
LC_CTYPE = 'C';

\c centro_tia_glenda;

-- =============================================
-- 2. TABLAS PRINCIPALES DEL SISTEMA
-- =============================================

-- =============================================
-- 2.1 TABLA: ROL (Catálogo de roles)
-- =============================================
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
-- 2.2 TABLA: PERSONA (Información demográfica base)
-- =============================================
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
-- 2.3 TABLA: USUARIO (Credenciales del sistema)
-- =============================================
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasenia VARCHAR(255) NOT NULL,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'bloqueado')),
    persona_id INTEGER NOT NULL,
    rol_id INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (rol_id) REFERENCES rol(id) ON DELETE RESTRICT
);

-- =============================================
-- 2.4 TABLA: ESPECIALIDAD (Catálogo de especialidades)
-- =============================================
CREATE TABLE especialidad (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    area VARCHAR(20) NOT NULL CHECK (area IN ('terapeutico', 'pedagogico')),
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- 2.5 TABLA: PERSONAL (Personal del centro)
-- =============================================
CREATE TABLE personal (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL,
    titulo_profesional VARCHAR(200),
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE RESTRICT
);

-- =============================================
-- 2.6 TABLA: PERSONAL_ESPECIALIDAD (Relación N:N)
-- =============================================
CREATE TABLE personal_especialidad (
    id SERIAL PRIMARY KEY,
    personal_id INTEGER NOT NULL,
    especialidad_id INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (personal_id) REFERENCES personal(id) ON DELETE CASCADE,
    FOREIGN KEY (especialidad_id) REFERENCES especialidad(id) ON DELETE RESTRICT,
    UNIQUE(personal_id, especialidad_id)
);

-- =============================================
-- 2.7 TABLA: TUTOR (Tutores/Representantes)
-- =============================================
CREATE TABLE tutor (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL,
    parentesco VARCHAR(20) NOT NULL CHECK (parentesco IN (
        'padre', 'madre', 'abuelo', 'abuela', 'tio', 'tia', 
        'hermano', 'hermana', 'tutor_legal'
    )),
    es_contacto_emergencia BOOLEAN DEFAULT FALSE,
    observaciones_tutor TEXT,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE RESTRICT
);

-- =============================================
-- 2.8 TABLA: PACIENTE (Pacientes del centro)
-- =============================================
CREATE TABLE paciente (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL,
    tutor_id INTEGER NOT NULL,
    fecha_ingreso DATE NOT NULL,
    observaciones TEXT,
    estado VARCHAR(15) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'alta', 'derivado')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (tutor_id) REFERENCES tutor(id) ON DELETE RESTRICT
);

-- =============================================
-- 2.9 TABLA: PACIENTE_ESPECIALIDAD (Tratamientos)
-- =============================================
CREATE TABLE paciente_especialidad (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL,
    especialidad_id INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    estado VARCHAR(15) DEFAULT 'activo' CHECK (estado IN ('activo', 'completado', 'suspendido')),
    observaciones_tratamiento TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE CASCADE,
    FOREIGN KEY (especialidad_id) REFERENCES especialidad(id) ON DELETE RESTRICT,
    UNIQUE(paciente_id, especialidad_id)
);

-- =============================================
-- 3. FUNCIONES AUXILIARES
-- =============================================

-- =============================================
-- 3.1 FUNCIÓN PARA ACTUALIZAR fecha_modificacion
-- =============================================
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 4. TRIGGERS PARA AUTOMATIZACIÓN
-- =============================================
CREATE TRIGGER trigger_persona_fecha_modificacion
    BEFORE UPDATE ON persona FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_rol_fecha_modificacion
    BEFORE UPDATE ON rol FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_usuario_fecha_modificacion
    BEFORE UPDATE ON usuario FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_especialidad_fecha_modificacion
    BEFORE UPDATE ON especialidad FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_personal_fecha_modificacion
    BEFORE UPDATE ON personal FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_personal_especialidad_fecha_modificacion
    BEFORE UPDATE ON personal_especialidad FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_tutor_fecha_modificacion
    BEFORE UPDATE ON tutor FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_paciente_fecha_modificacion
    BEFORE UPDATE ON paciente FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_paciente_especialidad_fecha_modificacion
    BEFORE UPDATE ON paciente_especialidad FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- =============================================
-- 5. ÍNDICES PARA OPTIMIZACIÓN
-- =============================================

-- Índices para PERSONA
CREATE INDEX idx_persona_cedula ON persona(cedula);
CREATE INDEX idx_persona_correo ON persona(correo);
CREATE INDEX idx_persona_estado ON persona(estado);

-- Índices para USUARIO
CREATE INDEX idx_usuario_persona ON usuario(persona_id);
CREATE INDEX idx_usuario_rol ON usuario(rol_id);
CREATE INDEX idx_usuario_nombre ON usuario(usuario);
CREATE INDEX idx_usuario_estado ON usuario(estado);

-- Índices para ROL
CREATE INDEX idx_rol_nombre ON rol(nombre);
CREATE INDEX idx_rol_estado ON rol(estado);

-- Índices para ESPECIALIDAD
CREATE INDEX idx_especialidad_area ON especialidad(area);
CREATE INDEX idx_especialidad_nombre ON especialidad(nombre);
CREATE INDEX idx_especialidad_estado ON especialidad(estado);

-- Índices para PERSONAL
CREATE INDEX idx_personal_persona ON personal(persona_id);
CREATE INDEX idx_personal_estado ON personal(estado);

-- Índices para PERSONAL_ESPECIALIDAD
CREATE INDEX idx_personal_especialidad_personal ON personal_especialidad(personal_id);
CREATE INDEX idx_personal_especialidad_especialidad ON personal_especialidad(especialidad_id);

-- Índices para TUTOR
CREATE INDEX idx_tutor_persona ON tutor(persona_id);
CREATE INDEX idx_tutor_parentesco ON tutor(parentesco);
CREATE INDEX idx_tutor_contacto_emergencia ON tutor(es_contacto_emergencia);
CREATE INDEX idx_tutor_estado ON tutor(estado);

-- Índices para PACIENTE
CREATE INDEX idx_paciente_persona ON paciente(persona_id);
CREATE INDEX idx_paciente_tutor ON paciente(tutor_id);
CREATE INDEX idx_paciente_fecha_ingreso ON paciente(fecha_ingreso);
CREATE INDEX idx_paciente_estado ON paciente(estado);

-- Índices para PACIENTE_ESPECIALIDAD
CREATE INDEX idx_paciente_especialidad_paciente ON paciente_especialidad(paciente_id);
CREATE INDEX idx_paciente_especialidad_especialidad ON paciente_especialidad(especialidad_id);
CREATE INDEX idx_paciente_especialidad_fecha_inicio ON paciente_especialidad(fecha_inicio);
CREATE INDEX idx_paciente_especialidad_estado ON paciente_especialidad(estado);

-- =============================================
-- 6. CONSTRAINTS DE AUDITORÍA
-- =============================================

-- Constraints para PERSONA
ALTER TABLE persona 
ADD CONSTRAINT fk_persona_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_persona_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- Constraints para ROL
ALTER TABLE rol 
ADD CONSTRAINT fk_rol_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_rol_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- Constraints para USUARIO
ALTER TABLE usuario 
ADD CONSTRAINT fk_usuario_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_usuario_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- Constraints para ESPECIALIDAD
ALTER TABLE especialidad 
ADD CONSTRAINT fk_especialidad_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_especialidad_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- Constraints para PERSONAL
ALTER TABLE personal 
ADD CONSTRAINT fk_personal_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_personal_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- Constraints para PERSONAL_ESPECIALIDAD
ALTER TABLE personal_especialidad 
ADD CONSTRAINT fk_personal_especialidad_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_personal_especialidad_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- Constraints para TUTOR
ALTER TABLE tutor 
ADD CONSTRAINT fk_tutor_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_tutor_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- Constraints para PACIENTE
ALTER TABLE paciente 
ADD CONSTRAINT fk_paciente_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_paciente_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- Constraints para PACIENTE_ESPECIALIDAD
ALTER TABLE paciente_especialidad 
ADD CONSTRAINT fk_paciente_especialidad_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_paciente_especialidad_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- =============================================
-- 7. DOCUMENTACIÓN DE TABLAS
-- =============================================
COMMENT ON TABLE persona IS 'Tabla base con información demográfica de todas las personas del sistema';
COMMENT ON TABLE usuario IS 'Credenciales y accesos al sistema vinculados a personas';
COMMENT ON TABLE rol IS 'Roles del sistema: Administrador, Terapeuta, Pedagógico, Cliente';
COMMENT ON TABLE especialidad IS 'Catálogo de especialidades terapéuticas y pedagógicas';
COMMENT ON TABLE personal IS 'Personal del centro vinculado a personas con título profesional';
COMMENT ON TABLE personal_especialidad IS 'Relación muchos a muchos entre personal y especialidades';
COMMENT ON TABLE tutor IS 'Tutores/representantes de pacientes vinculados a personas';
COMMENT ON TABLE paciente IS 'Pacientes del centro vinculados a personas y tutores';
COMMENT ON TABLE paciente_especialidad IS 'Tratamientos/especialidades asignadas a pacientes con fechas y seguimiento';

-- =============================================
-- 8. MENSAJE DE FINALIZACIÓN
-- =============================================
SELECT 'Estructura de tablas principales creada exitosamente - Centro Tía Glenda' AS mensaje;

-- =============================================
-- 9. MÓDULO SESIONES DE TERAPIA
-- =============================================

-- =============================================
-- 9.1 TABLA: SESION_TERAPIA (Tabla principal)
-- =============================================
CREATE TABLE sesion_terapia (
    id SERIAL PRIMARY KEY,
    
    -- Información básica de la sesión
    codigo_sesion VARCHAR(30) UNIQUE NOT NULL, -- Código único para identificar la sesión (ej: ST-2025-001)
    titulo VARCHAR(200) NOT NULL, -- Título descriptivo de la sesión
    
    -- Relaciones principales
    terapeuta_id INTEGER NOT NULL, -- ID del personal (terapeuta)
    especialidad_id INTEGER NOT NULL, -- Tipo de terapia (especialidad)
    
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
    usuario_modificacion INTEGER,
    
    -- Claves foráneas
    FOREIGN KEY (terapeuta_id) REFERENCES personal(id) ON DELETE RESTRICT,
    FOREIGN KEY (especialidad_id) REFERENCES especialidad(id) ON DELETE RESTRICT
);

-- =============================================
-- 9.2 TABLA: SESION_PACIENTE (Relación muchos a muchos)
-- =============================================
CREATE TABLE sesion_paciente (
    id SERIAL PRIMARY KEY,
    
    -- Relaciones principales
    sesion_terapia_id INTEGER NOT NULL,
    paciente_id INTEGER NOT NULL,
    
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
    
    -- Claves foráneas
    FOREIGN KEY (sesion_terapia_id) REFERENCES sesion_terapia(id) ON DELETE CASCADE,
    FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE RESTRICT,
    
    -- Evitar duplicados
    UNIQUE(sesion_terapia_id, paciente_id)
);

-- =============================================
-- 9.3 TABLA: CRONOGRAMA_SESIONES (Sesiones programadas)
-- =============================================
CREATE TABLE cronograma_sesiones (
    id SERIAL PRIMARY KEY,
    
    -- Relación principal
    sesion_terapia_id INTEGER NOT NULL,
    
    -- Información de la sesión específica
    numero_sesion INTEGER NOT NULL, -- Número correlativo de la sesión (1, 2, 3...)
    fecha_programada DATE NOT NULL,
    hora_programada TIME NOT NULL,
    
    -- Control de estado
    estado VARCHAR(15) DEFAULT 'programada' CHECK (estado IN ('programada', 'realizada', 'cancelada', 'reprogramada')),
    fecha_realizacion TIMESTAMP, -- Cuando se realizó realmente
    observaciones_cronograma TEXT,
    
    -- Reprogramación
    sesion_original_id INTEGER, -- ID de la sesión original si es una reprogramación
    motivo_reprogramacion TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Claves foráneas
    FOREIGN KEY (sesion_terapia_id) REFERENCES sesion_terapia(id) ON DELETE CASCADE,
    FOREIGN KEY (sesion_original_id) REFERENCES cronograma_sesiones(id) ON DELETE SET NULL,
    
    -- Evitar duplicados de sesión-fecha
    UNIQUE(sesion_terapia_id, numero_sesion)
);

-- =============================================
-- 9.4 TABLA: ASISTENCIA_SESIONES (Control de asistencia)
-- ==============================================
CREATE TABLE asistencia_sesiones (
    id SERIAL PRIMARY KEY,
    
    -- Relaciones principales
    cronograma_sesion_id INTEGER NOT NULL,
    paciente_id INTEGER NOT NULL,
    
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
    
    -- Claves foráneas
    FOREIGN KEY (cronograma_sesion_id) REFERENCES cronograma_sesiones(id) ON DELETE CASCADE,
    FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE RESTRICT,
    
    -- Un paciente solo puede tener un registro de asistencia por sesión
    UNIQUE(cronograma_sesion_id, paciente_id)
);

-- =============================================
-- 10. FUNCIONES ESPECIALIZADAS PARA SESIONES
-- =============================================

-- =============================================
-- 10.1 FUNCIÓN PARA GENERAR CRONOGRAMA AUTOMÁTICO
-- =============================================
CREATE OR REPLACE FUNCTION generar_cronograma_sesiones(p_sesion_terapia_id INTEGER)
RETURNS VOID AS $$
DECLARE
    v_sesion RECORD;
    v_fecha_actual DATE;
    v_dias_array TEXT[];
    v_dia TEXT;
    v_contador_sesiones INTEGER := 0;
    v_numero_sesion INTEGER := 1;
BEGIN
    -- Obtener información de la sesión
    SELECT * INTO v_sesion 
    FROM sesion_terapia 
    WHERE id = p_sesion_terapia_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Sesión de terapia no encontrada: %', p_sesion_terapia_id;
    END IF;
    
    -- Convertir días de la semana a array
    v_dias_array := string_to_array(lower(v_sesion.dias_semana), ',');
    
    -- Limpiar cronograma existente
    DELETE FROM cronograma_sesiones WHERE sesion_terapia_id = p_sesion_terapia_id;
    
    -- Generar cronograma
    v_fecha_actual := v_sesion.fecha_inicio;
    
    WHILE v_fecha_actual <= v_sesion.fecha_fin AND v_contador_sesiones < v_sesion.numero_sesiones_contratadas LOOP
        -- Obtener el día de la semana en español
        SELECT CASE extract(dow from v_fecha_actual)
            WHEN 0 THEN 'domingo'
            WHEN 1 THEN 'lunes'
            WHEN 2 THEN 'martes'
            WHEN 3 THEN 'miercoles'
            WHEN 4 THEN 'jueves'
            WHEN 5 THEN 'viernes'
            WHEN 6 THEN 'sabado'
        END INTO v_dia;
        
        -- Si el día está en el array de días programados
        IF v_dia = ANY(v_dias_array) THEN
            INSERT INTO cronograma_sesiones (
                sesion_terapia_id,
                numero_sesion,
                fecha_programada,
                hora_programada,
                estado,
                usuario_creacion
            ) VALUES (
                p_sesion_terapia_id,
                v_numero_sesion,
                v_fecha_actual,
                v_sesion.hora_inicio,
                'programada',
                v_sesion.usuario_creacion
            );
            
            v_contador_sesiones := v_contador_sesiones + 1;
            v_numero_sesion := v_numero_sesion + 1;
        END IF;
        
        v_fecha_actual := v_fecha_actual + INTERVAL '1 day';
    END LOOP;
    
    RAISE NOTICE 'Cronograma generado: % sesiones programadas', v_contador_sesiones;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 10.2 FUNCIÓN PARA GENERAR CÓDIGO DE SESIÓN
-- ==============================================
CREATE OR REPLACE FUNCTION generar_codigo_sesion()
RETURNS TEXT AS $$
DECLARE
    v_year TEXT;
    v_correlativo INTEGER;
    v_codigo TEXT;
BEGIN
    v_year := extract(year from CURRENT_DATE)::TEXT;
    
    -- Obtener el próximo correlativo usando LIKE y split_part para mayor compatibilidad
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
-- 11. TRIGGERS PARA SESIONES DE TERAPIA
-- =============================================

-- Trigger para actualizar fecha_modificacion
CREATE TRIGGER trigger_sesion_terapia_fecha_modificacion
    BEFORE UPDATE ON sesion_terapia
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_sesion_paciente_fecha_modificacion
    BEFORE UPDATE ON sesion_paciente
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_cronograma_sesiones_fecha_modificacion
    BEFORE UPDATE ON cronograma_sesiones
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_asistencia_sesiones_fecha_modificacion
    BEFORE UPDATE ON asistencia_sesiones
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- Trigger para generar código automático
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
-- 12. ÍNDICES PARA SESIONES DE TERAPIA
-- ==============================================

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
-- 13. CONSTRAINTS DE AUDITORÍA PARA SESIONES
-- =============================================
ALTER TABLE sesion_terapia 
ADD CONSTRAINT fk_sesion_terapia_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE sesion_terapia 
ADD CONSTRAINT fk_sesion_terapia_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE sesion_paciente 
ADD CONSTRAINT fk_sesion_paciente_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE sesion_paciente 
ADD CONSTRAINT fk_sesion_paciente_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE cronograma_sesiones 
ADD CONSTRAINT fk_cronograma_sesiones_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE cronograma_sesiones 
ADD CONSTRAINT fk_cronograma_sesiones_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE asistencia_sesiones 
ADD CONSTRAINT fk_asistencia_sesiones_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE asistencia_sesiones 
ADD CONSTRAINT fk_asistencia_sesiones_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- =============================================
-- 14. DOCUMENTACIÓN SESIONES DE TERAPIA
-- =============================================
COMMENT ON TABLE sesion_terapia IS 'Sesiones de terapia programadas con información de contrato, horarios y costos';
COMMENT ON TABLE sesion_paciente IS 'Relación muchos a muchos entre sesiones y pacientes - permite múltiples pacientes por sesión';
COMMENT ON TABLE cronograma_sesiones IS 'Cronograma detallado de cada sesión individual programada automáticamente';
COMMENT ON TABLE asistencia_sesiones IS 'Control de asistencia y notas de progreso por paciente y sesión';

COMMENT ON COLUMN sesion_terapia.dias_semana IS 'Días de la semana separados por comas: lunes,martes,miercoles,jueves,viernes,sabado,domingo';
COMMENT ON COLUMN sesion_terapia.duracion_minutos IS 'Duración de la sesión en minutos (por defecto 45 min)';
COMMENT ON COLUMN sesion_terapia.costo_por_sesion IS 'Campo calculado automáticamente: costo_total / numero_sesiones_contratadas';

-- =============================================
-- 15. MENSAJE FINAL
-- =============================================
SELECT 'Sistema completo Centro Tía Glenda creado exitosamente' AS mensaje;