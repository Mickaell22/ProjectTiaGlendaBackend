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
    fecha_ultimo_acceso TIMESTAMP,
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
    especialidad_id INTEGER, -- Nueva columna para especialidad asignada
    fecha_ingreso DATE NOT NULL,
    fecha_inicio_tratamiento DATE, -- Fecha de inicio del tratamiento
    fecha_fin_tratamiento DATE, -- Fecha de fin del tratamiento (opcional)
    estado_tratamiento VARCHAR(15) DEFAULT 'activo' CHECK (estado_tratamiento IN ('activo', 'completado', 'suspendido')),
    observaciones_tratamiento TEXT, -- Observaciones específicas del tratamiento
    observaciones TEXT, -- Observaciones generales del paciente
    estado VARCHAR(15) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'alta', 'derivado', 'eliminado')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (tutor_id) REFERENCES tutor(id) ON DELETE RESTRICT,
    FOREIGN KEY (especialidad_id) REFERENCES especialidad(id) ON DELETE SET NULL
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

-- Índice para la nueva columna especialidad_id en PACIENTE
CREATE INDEX idx_paciente_especialidad ON paciente(especialidad_id);

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
COMMENT ON COLUMN paciente.especialidad_id IS 'Especialidad asignada al paciente para tratamiento';
COMMENT ON COLUMN paciente.fecha_inicio_tratamiento IS 'Fecha de inicio del tratamiento con la especialidad asignada';
COMMENT ON COLUMN paciente.fecha_fin_tratamiento IS 'Fecha de finalización del tratamiento (opcional)';
COMMENT ON COLUMN paciente.estado_tratamiento IS 'Estado del tratamiento: activo, completado, suspendido';
COMMENT ON COLUMN paciente.observaciones_tratamiento IS 'Observaciones específicas del tratamiento y progreso';

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
-- 9.5 TABLA: SESION_PEDAGOGICA (Sesiones pedagógicas/educativas)
-- =============================================
CREATE TABLE sesion_pedagogica (
    id SERIAL PRIMARY KEY,
    
    -- Información básica de la sesión
    codigo_sesion VARCHAR(30) UNIQUE NOT NULL, -- Código único para identificar la sesión (ej: SP-2025-001)
    titulo VARCHAR(200) NOT NULL, -- Título descriptivo de la sesión/materia
    
    -- Relaciones principales
    pedagogo_id INTEGER NOT NULL, -- ID del personal (pedagogo/profesor)
    especialidad_id INTEGER NOT NULL, -- Materia/especialidad pedagógica
    
    -- Configuración de horarios académicos
    fecha_inicio DATE NOT NULL, -- Fecha de inicio del período académico
    fecha_fin DATE NOT NULL, -- Fecha de fin del período académico
    dias_semana VARCHAR(60) NOT NULL, -- Días de la semana separados por comas (ej: "lunes,miercoles,viernes")
    hora_inicio TIME NOT NULL, -- Hora de inicio de la clase
    duracion_minutos INTEGER DEFAULT 60 CHECK (duracion_minutos BETWEEN 30 AND 180), -- Duración en minutos
    
    -- Información académica
    numero_clases_programadas INTEGER NOT NULL CHECK (numero_clases_programadas > 0),
    nivel_academico VARCHAR(20) CHECK (nivel_academico IN ('basico', 'intermedio', 'avanzado')),
    capacidad_maxima INTEGER DEFAULT 15 CHECK (capacidad_maxima BETWEEN 1 AND 30), -- Máximo estudiantes
    modalidad VARCHAR(15) DEFAULT 'presencial' CHECK (modalidad IN ('presencial', 'virtual', 'hibrida')),
    
    -- Información financiera
    costo_total DECIMAL(10,2) NOT NULL CHECK (costo_total >= 0),
    costo_por_clase DECIMAL(10,2) GENERATED ALWAYS AS (costo_total / numero_clases_programadas) STORED,
    periodo_academico VARCHAR(20), -- Ej: "2025-1", "Verano 2025"
    
    -- Control y estado
    estado VARCHAR(15) DEFAULT 'activo' CHECK (estado IN ('activo', 'suspendido', 'completado', 'cancelado')),
    observaciones TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Claves foráneas
    FOREIGN KEY (pedagogo_id) REFERENCES personal(id) ON DELETE RESTRICT,
    FOREIGN KEY (especialidad_id) REFERENCES especialidad(id) ON DELETE RESTRICT
);

-- =============================================
-- 9.6 TABLA: SESION_ESTUDIANTE (Relación N:N sesion_pedagogica - paciente)
-- =============================================
CREATE TABLE sesion_estudiante (
    id SERIAL PRIMARY KEY,
    
    -- Relaciones principales
    sesion_pedagogica_id INTEGER NOT NULL,
    paciente_id INTEGER NOT NULL, -- Reutilizamos tabla paciente para estudiantes
    
    -- Información específica del estudiante en esta sesión
    fecha_incorporacion DATE DEFAULT CURRENT_DATE,
    costo_estudiante DECIMAL(10,2), -- Costo específico para este estudiante (puede tener descuentos)
    observaciones_estudiante TEXT,
    
    -- Estado académico
    estado VARCHAR(15) DEFAULT 'activo' CHECK (estado IN ('activo', 'retirado', 'transferido', 'completado')),
    nota_final DECIMAL(5,2), -- Calificación final (0.00 - 10.00)
    asistencia_porcentaje DECIMAL(5,2), -- Porcentaje de asistencia
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Claves foráneas
    FOREIGN KEY (sesion_pedagogica_id) REFERENCES sesion_pedagogica(id) ON DELETE CASCADE,
    FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE RESTRICT,
    
    -- Un estudiante no puede estar duplicado en la misma sesión
    UNIQUE(sesion_pedagogica_id, paciente_id)
);

-- =============================================
-- 9.7 TABLA: CRONOGRAMA_CLASES (Cronograma específico para sesiones pedagógicas)
-- =============================================
CREATE TABLE cronograma_clases (
    id SERIAL PRIMARY KEY,
    
    -- Relación principal
    sesion_pedagogica_id INTEGER NOT NULL,
    
    -- Información de la clase específica
    numero_clase INTEGER NOT NULL,
    fecha_programada DATE NOT NULL,
    hora_programada TIME NOT NULL,
    tema_clase VARCHAR(255), -- Tema específico de la clase
    
    -- Control de estado
    estado VARCHAR(15) DEFAULT 'programada' CHECK (estado IN ('programada', 'realizada', 'cancelada', 'reprogramada')),
    fecha_realizacion DATE, -- Fecha real cuando se realizó (puede diferir de la programada)
    
    -- Contenido educativo
    objetivos_clase TEXT, -- Objetivos específicos de esta clase
    material_requerido TEXT, -- Materiales necesarios para la clase
    tareas_asignadas TEXT, -- Tareas para casa
    
    -- Evaluación
    evaluacion_programada BOOLEAN DEFAULT FALSE,
    tipo_evaluacion VARCHAR(20) CHECK (tipo_evaluacion IN ('quiz', 'examen', 'proyecto', 'presentacion', 'practica')),
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Claves foráneas
    FOREIGN KEY (sesion_pedagogica_id) REFERENCES sesion_pedagogica(id) ON DELETE CASCADE,
    
    -- Una sesión no puede tener dos clases con el mismo número
    UNIQUE(sesion_pedagogica_id, numero_clase)
);

-- =============================================
-- 9.8 TABLA: ASISTENCIA_CLASES (Control de asistencia para clases pedagógicas)
-- =============================================
CREATE TABLE asistencia_clases (
    id SERIAL PRIMARY KEY,
    
    -- Relaciones principales
    cronograma_clase_id INTEGER NOT NULL,
    paciente_id INTEGER NOT NULL, -- El estudiante (usando tabla paciente)
    
    -- Control de asistencia
    asistio BOOLEAN DEFAULT FALSE,
    llegada_tardanza_minutos INTEGER DEFAULT 0,
    observaciones_asistencia TEXT,
    
    -- Evaluación académica de la clase
    participacion_clase DECIMAL(3,1) CHECK (participacion_clase >= 0 AND participacion_clase <= 10), -- 0.0 - 10.0
    tareas_entregadas BOOLEAN DEFAULT FALSE,
    notas_comportamiento TEXT,
    
    -- Evaluaciones específicas
    calificacion_evaluacion DECIMAL(5,2), -- Si hubo evaluación en esta clase
    observaciones_evaluacion TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Claves foráneas
    FOREIGN KEY (cronograma_clase_id) REFERENCES cronograma_clases(id) ON DELETE CASCADE,
    FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE RESTRICT,
    
    -- Un estudiante solo puede tener un registro de asistencia por clase
    UNIQUE(cronograma_clase_id, paciente_id)
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
-- 10.2 FUNCIÓN PARA GENERAR CRONOGRAMA PEDAGÓGICO
-- =============================================
CREATE OR REPLACE FUNCTION generar_cronograma_clases(p_sesion_pedagogica_id INTEGER)
RETURNS VOID AS $$
DECLARE
    v_sesion RECORD;
    v_fecha_actual DATE;
    v_dias_array TEXT[];
    v_dia_actual TEXT;
    v_numero_clase INTEGER := 1;
    v_clases_generadas INTEGER := 0;
BEGIN
    -- Obtener información de la sesión pedagógica
    SELECT fecha_inicio, fecha_fin, dias_semana, hora_inicio, numero_clases_programadas
    INTO v_sesion
    FROM sesion_pedagogica 
    WHERE id = p_sesion_pedagogica_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Sesión pedagógica no encontrada: %', p_sesion_pedagogica_id;
    END IF;
    
    -- Limpiar cronograma existente
    DELETE FROM cronograma_clases WHERE sesion_pedagogica_id = p_sesion_pedagogica_id;
    
    -- Convertir string de días a array
    v_dias_array := string_to_array(lower(v_sesion.dias_semana), ',');
    
    -- Generar cronograma clase por clase
    v_fecha_actual := v_sesion.fecha_inicio;
    
    WHILE v_fecha_actual <= v_sesion.fecha_fin AND v_clases_generadas < v_sesion.numero_clases_programadas LOOP
        -- Obtener nombre del día de la semana
        v_dia_actual := trim(to_char(v_fecha_actual, 'Day'));
        v_dia_actual := lower(regexp_replace(v_dia_actual, '\s+', ''));
        
        -- Mapear días en inglés a español
        CASE v_dia_actual
            WHEN 'monday' THEN v_dia_actual := 'lunes';
            WHEN 'tuesday' THEN v_dia_actual := 'martes';
            WHEN 'wednesday' THEN v_dia_actual := 'miercoles';
            WHEN 'thursday' THEN v_dia_actual := 'jueves';
            WHEN 'friday' THEN v_dia_actual := 'viernes';
            WHEN 'saturday' THEN v_dia_actual := 'sabado';
            WHEN 'sunday' THEN v_dia_actual := 'domingo';
        END CASE;
        
        -- Si el día actual está en la lista de días programados
        IF v_dia_actual = ANY(v_dias_array) THEN
            INSERT INTO cronograma_clases (
                sesion_pedagogica_id,
                numero_clase,
                fecha_programada,
                hora_programada,
                estado,
                usuario_creacion
            ) VALUES (
                p_sesion_pedagogica_id,
                v_numero_clase,
                v_fecha_actual,
                v_sesion.hora_inicio,
                'programada',
                1
            );
            
            v_numero_clase := v_numero_clase + 1;
            v_clases_generadas := v_clases_generadas + 1;
        END IF;
        
        v_fecha_actual := v_fecha_actual + 1;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 10.3 FUNCIÓN PARA GENERAR CÓDIGO DE SESIÓN PEDAGÓGICA
-- =============================================
CREATE OR REPLACE FUNCTION trigger_generar_codigo_sesion_pedagogica()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.codigo_sesion IS NULL OR NEW.codigo_sesion = '' THEN
        SELECT 'SP-' || EXTRACT(YEAR FROM CURRENT_DATE) || '-' || 
               LPAD((COUNT(*) + 1)::TEXT, 3, '0')
        INTO NEW.codigo_sesion
        FROM sesion_pedagogica
        WHERE EXTRACT(YEAR FROM fecha_creacion) = EXTRACT(YEAR FROM CURRENT_DATE);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_codigo_sesion_pedagogica
    BEFORE INSERT ON sesion_pedagogica
    FOR EACH ROW
    EXECUTE FUNCTION trigger_generar_codigo_sesion_pedagogica();

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
-- 12.2 ÍNDICES PARA SESIONES PEDAGÓGICAS
-- =============================================

-- Índices para SESION_PEDAGOGICA
CREATE INDEX idx_sesion_pedagogica_pedagogo ON sesion_pedagogica(pedagogo_id);
CREATE INDEX idx_sesion_pedagogica_especialidad ON sesion_pedagogica(especialidad_id);
CREATE INDEX idx_sesion_pedagogica_fecha_inicio ON sesion_pedagogica(fecha_inicio);
CREATE INDEX idx_sesion_pedagogica_fecha_fin ON sesion_pedagogica(fecha_fin);
CREATE INDEX idx_sesion_pedagogica_estado ON sesion_pedagogica(estado);
CREATE INDEX idx_sesion_pedagogica_codigo ON sesion_pedagogica(codigo_sesion);
CREATE INDEX idx_sesion_pedagogica_periodo ON sesion_pedagogica(periodo_academico);
CREATE INDEX idx_sesion_pedagogica_nivel ON sesion_pedagogica(nivel_academico);

-- Índices para SESION_ESTUDIANTE
CREATE INDEX idx_sesion_estudiante_sesion ON sesion_estudiante(sesion_pedagogica_id);
CREATE INDEX idx_sesion_estudiante_paciente ON sesion_estudiante(paciente_id);
CREATE INDEX idx_sesion_estudiante_estado ON sesion_estudiante(estado);
CREATE INDEX idx_sesion_estudiante_incorporacion ON sesion_estudiante(fecha_incorporacion);

-- Índices para CRONOGRAMA_CLASES
CREATE INDEX idx_cronograma_clases_sesion ON cronograma_clases(sesion_pedagogica_id);
CREATE INDEX idx_cronograma_clases_fecha ON cronograma_clases(fecha_programada);
CREATE INDEX idx_cronograma_clases_estado ON cronograma_clases(estado);
CREATE INDEX idx_cronograma_clases_numero ON cronograma_clases(numero_clase);

-- Índices para ASISTENCIA_CLASES
CREATE INDEX idx_asistencia_clases_cronograma ON asistencia_clases(cronograma_clase_id);
CREATE INDEX idx_asistencia_clases_paciente ON asistencia_clases(paciente_id);
CREATE INDEX idx_asistencia_clases_fecha ON asistencia_clases(fecha_creacion);

-- =============================================
-- 12.3 TRIGGERS DE FECHA_MODIFICACION PARA TABLAS PEDAGÓGICAS
-- =============================================

-- Triggers para SESION_PEDAGOGICA
CREATE TRIGGER trigger_sesion_pedagogica_fecha_modificacion
    BEFORE UPDATE ON sesion_pedagogica
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- Triggers para SESION_ESTUDIANTE
CREATE TRIGGER trigger_sesion_estudiante_fecha_modificacion
    BEFORE UPDATE ON sesion_estudiante
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- Triggers para CRONOGRAMA_CLASES
CREATE TRIGGER trigger_cronograma_clases_fecha_modificacion
    BEFORE UPDATE ON cronograma_clases
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- Triggers para ASISTENCIA_CLASES
CREATE TRIGGER trigger_asistencia_clases_fecha_modificacion
    BEFORE UPDATE ON asistencia_clases
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

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
-- 13.2 CONSTRAINTS DE AUDITORÍA PARA SESIONES PEDAGÓGICAS
-- =============================================

-- Constraints para SESION_PEDAGOGICA
ALTER TABLE sesion_pedagogica 
ADD CONSTRAINT fk_sesion_pedagogica_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE sesion_pedagogica 
ADD CONSTRAINT fk_sesion_pedagogica_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- Constraints para SESION_ESTUDIANTE
ALTER TABLE sesion_estudiante 
ADD CONSTRAINT fk_sesion_estudiante_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE sesion_estudiante 
ADD CONSTRAINT fk_sesion_estudiante_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- Constraints para CRONOGRAMA_CLASES
ALTER TABLE cronograma_clases 
ADD CONSTRAINT fk_cronograma_clases_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE cronograma_clases 
ADD CONSTRAINT fk_cronograma_clases_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- Constraints para ASISTENCIA_CLASES
ALTER TABLE asistencia_clases 
ADD CONSTRAINT fk_asistencia_clases_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE asistencia_clases 
ADD CONSTRAINT fk_asistencia_clases_usuario_modificacion 
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
-- 14.2 DOCUMENTACIÓN SESIONES PEDAGÓGICAS
-- =============================================
COMMENT ON TABLE sesion_pedagogica IS 'Sesiones pedagógicas/educativas con información académica, horarios y costos';
COMMENT ON TABLE sesion_estudiante IS 'Relación muchos a muchos entre sesiones pedagógicas y estudiantes (pacientes) - permite múltiples estudiantes por clase';
COMMENT ON TABLE cronograma_clases IS 'Cronograma detallado de cada clase individual programada automáticamente con contenido educativo';
COMMENT ON TABLE asistencia_clases IS 'Control de asistencia y evaluaciones académicas por estudiante y clase';

COMMENT ON COLUMN sesion_pedagogica.codigo_sesion IS 'Código único con formato SP-YYYY-NNN (SP = Sesión Pedagógica)';
COMMENT ON COLUMN sesion_pedagogica.pedagogo_id IS 'Referencia al personal con rol de pedagogo/profesor';
COMMENT ON COLUMN sesion_pedagogica.capacidad_maxima IS 'Número máximo de estudiantes permitidos en la sesión';
COMMENT ON COLUMN sesion_pedagogica.nivel_academico IS 'Nivel académico: basico, intermedio, avanzado';
COMMENT ON COLUMN sesion_pedagogica.modalidad IS 'Modalidad de enseñanza: presencial, virtual, hibrida';
COMMENT ON COLUMN sesion_pedagogica.costo_por_clase IS 'Campo calculado automáticamente: costo_total / numero_clases_programadas';

COMMENT ON COLUMN sesion_estudiante.nota_final IS 'Calificación final del estudiante (0.00 - 10.00)';
COMMENT ON COLUMN sesion_estudiante.asistencia_porcentaje IS 'Porcentaje de asistencia del estudiante';

COMMENT ON COLUMN cronograma_clases.tema_clase IS 'Tema específico a tratar en esta clase';
COMMENT ON COLUMN cronograma_clases.evaluacion_programada IS 'Indica si hay evaluación programada para esta clase';

COMMENT ON COLUMN asistencia_clases.participacion_clase IS 'Calificación de participación en la clase (0.0 - 10.0)';
COMMENT ON COLUMN asistencia_clases.calificacion_evaluacion IS 'Calificación obtenida en evaluación si la hubo';

-- =============================================
-- 15. MÓDULO DOCUMENTOS PACIENTE
-- =============================================

-- =============================================
-- 15.1 TABLA: DOCUMENTOS_PACIENTE (Documentos PDF por paciente)
-- =============================================
CREATE TABLE documentos_paciente (
    id SERIAL PRIMARY KEY,
    
    -- Relación con paciente
    paciente_id INTEGER NOT NULL,
    
    -- Información del documento
    nombre_archivo VARCHAR(255) NOT NULL,
    nombre_original VARCHAR(255) NOT NULL, -- Nombre original del archivo subido
    ruta_archivo VARCHAR(500) NOT NULL, -- Ruta completa donde se almacena el archivo
    tipo_documento VARCHAR(50) DEFAULT 'general' CHECK (tipo_documento IN (
        'general', 'historia_clinica', 'examenes_medicos', 'consentimientos', 
        'reportes_terapia', 'evaluaciones', 'otros'
    )),
    
    -- Metadatos del archivo
    tamaño_archivo BIGINT NOT NULL, -- Tamaño en bytes
    tipo_mime VARCHAR(50) DEFAULT 'application/pdf',
    
    -- Información adicional
    descripcion TEXT,
    es_confidencial BOOLEAN DEFAULT FALSE,
    fecha_vencimiento DATE, -- Para documentos que tienen fecha de vencimiento
    
    -- Control y estado
    estado VARCHAR(15) DEFAULT 'activo' CHECK (estado IN ('activo', 'archivado', 'eliminado')),
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Claves foráneas
    FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE CASCADE
);

-- =============================================
-- 15.2 FUNCIÓN PARA GENERAR RUTA DE DOCUMENTO
-- =============================================
CREATE OR REPLACE FUNCTION generar_ruta_documento(
    p_paciente_id INTEGER,
    p_nombre_archivo VARCHAR(255)
) RETURNS VARCHAR(500) AS $$
DECLARE
    v_persona RECORD;
    v_iniciales VARCHAR(10);
    v_carpeta VARCHAR(100);
    v_ruta_completa VARCHAR(500);
BEGIN
    -- Obtener información del paciente y persona
    SELECT p.nombre, p.apellido
    INTO v_persona
    FROM paciente pac
    JOIN persona p ON pac.persona_id = p.id
    WHERE pac.id = p_paciente_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Paciente no encontrado: %', p_paciente_id;
    END IF;
    
    -- Generar iniciales: Primera letra del nombre + Primera letra del apellido
    v_iniciales := UPPER(LEFT(v_persona.nombre, 1)) || UPPER(LEFT(v_persona.apellido, 1));
    
    -- Crear nombre de carpeta: Iniciales + ID del paciente
    v_carpeta := v_iniciales || '_' || p_paciente_id::TEXT;
    
    -- Generar ruta completa
    v_ruta_completa := 'documentos_pacientes/' || v_carpeta || '/' || p_nombre_archivo;
    
    RETURN v_ruta_completa;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 15.3 FUNCIÓN PARA SANITIZAR NOMBRE DE ARCHIVO
-- =============================================
CREATE OR REPLACE FUNCTION sanitizar_nombre_archivo(p_nombre_original VARCHAR(255))
RETURNS VARCHAR(255) AS $$
DECLARE
    v_nombre_limpio VARCHAR(255);
    v_timestamp VARCHAR(20);
BEGIN
    -- Obtener timestamp actual
    v_timestamp := TO_CHAR(CURRENT_TIMESTAMP, 'YYYYMMDDHH24MISS');
    
    -- Limpiar el nombre del archivo
    v_nombre_limpio := regexp_replace(p_nombre_original, '[^a-zA-Z0-9._-]', '_', 'g');
    v_nombre_limpio := regexp_replace(v_nombre_limpio, '_+', '_', 'g');
    v_nombre_limpio := trim(v_nombre_limpio, '_');
    
    -- Si el nombre está vacío, usar un nombre por defecto
    IF LENGTH(v_nombre_limpio) = 0 THEN
        v_nombre_limpio := 'documento';
    END IF;
    
    -- Asegurar que termine en .pdf
    IF NOT v_nombre_limpio ILIKE '%.pdf' THEN
        v_nombre_limpio := v_nombre_limpio || '.pdf';
    END IF;
    
    -- Agregar timestamp para evitar duplicados
    v_nombre_limpio := SPLIT_PART(v_nombre_limpio, '.pdf', 1) || '_' || v_timestamp || '.pdf';
    
    RETURN v_nombre_limpio;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 15.4 TRIGGERS PARA DOCUMENTOS PACIENTE
-- =============================================

-- Trigger para actualizar fecha_modificacion
CREATE TRIGGER trigger_documentos_paciente_fecha_modificacion
    BEFORE UPDATE ON documentos_paciente
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- =============================================
-- 15.5 ÍNDICES PARA DOCUMENTOS PACIENTE
-- =============================================

-- Índices para DOCUMENTOS_PACIENTE
CREATE INDEX idx_documentos_paciente_paciente ON documentos_paciente(paciente_id);
CREATE INDEX idx_documentos_paciente_tipo ON documentos_paciente(tipo_documento);
CREATE INDEX idx_documentos_paciente_estado ON documentos_paciente(estado);
CREATE INDEX idx_documentos_paciente_fecha_creacion ON documentos_paciente(fecha_creacion);
CREATE INDEX idx_documentos_paciente_confidencial ON documentos_paciente(es_confidencial);
CREATE INDEX idx_documentos_paciente_vencimiento ON documentos_paciente(fecha_vencimiento);

-- =============================================
-- 15.6 CONSTRAINTS DE AUDITORÍA PARA DOCUMENTOS
-- =============================================

-- Constraints para DOCUMENTOS_PACIENTE
ALTER TABLE documentos_paciente 
ADD CONSTRAINT fk_documentos_paciente_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE documentos_paciente 
ADD CONSTRAINT fk_documentos_paciente_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- =============================================
-- 15.7 DOCUMENTACIÓN DOCUMENTOS PACIENTE
-- =============================================
COMMENT ON TABLE documentos_paciente IS 'Documentos PDF asociados a pacientes con metadatos y control de versiones';
COMMENT ON COLUMN documentos_paciente.nombre_archivo IS 'Nombre del archivo sanitizado almacenado en el sistema';
COMMENT ON COLUMN documentos_paciente.nombre_original IS 'Nombre original del archivo como fue subido por el usuario';
COMMENT ON COLUMN documentos_paciente.ruta_archivo IS 'Ruta completa del archivo: documentos_pacientes/iniciales_id/archivo.pdf';
COMMENT ON COLUMN documentos_paciente.tipo_documento IS 'Categoría del documento: general, historia_clinica, examenes_medicos, etc.';
COMMENT ON COLUMN documentos_paciente.tamaño_archivo IS 'Tamaño del archivo en bytes';
COMMENT ON COLUMN documentos_paciente.es_confidencial IS 'Marca si el documento contiene información confidencial';
COMMENT ON COLUMN documentos_paciente.fecha_vencimiento IS 'Fecha de vencimiento del documento (opcional)';

-- =============================================
-- 16. MENSAJE FINAL
-- =============================================
SELECT 'Sistema completo Centro Tía Glenda creado exitosamente - Incluyendo módulo de documentos PDF' AS mensaje;