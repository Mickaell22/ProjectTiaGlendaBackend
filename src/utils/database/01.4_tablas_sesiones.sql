-- =============================================
-- CENTRO TÍA GLENDA - TABLAS DE SESIONES
-- Archivo: 01.4_tablas_sesiones.sql
-- Descripción: Gestión de sesiones terapéuticas y pedagógicas
-- =============================================

-- =============================================
-- 1. TABLA: SESION_TERAPIA
-- =============================================
CREATE TABLE IF NOT EXISTS sesion_terapia (
    id SERIAL PRIMARY KEY,
    codigo_sesion VARCHAR(20) UNIQUE NOT NULL,
    id_terapeuta INTEGER NOT NULL,
    id_especialidad INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    tipo_sesion VARCHAR(20) DEFAULT 'individual' CHECK (tipo_sesion IN ('individual', 'grupal', 'familiar')),
    modalidad VARCHAR(20) DEFAULT 'presencial' CHECK (modalidad IN ('presencial', 'virtual', 'mixta')),
    objetivo_general TEXT,
    objetivos_especificos TEXT,
    metodologia TEXT,
    duracion_minutos INTEGER DEFAULT 45,
    costo_sesion DECIMAL(10,2),
    
    -- Programación
    frecuencia_semanal INTEGER DEFAULT 1,
    dias_semana TEXT[], -- Array: ['lunes', 'miércoles', 'viernes']
    hora_inicio TIME DEFAULT '08:00',
    hora_fin TIME DEFAULT '08:45',
    
    -- Control de estado
    estado VARCHAR(20) DEFAULT 'planificada' CHECK (estado IN 
        ('planificada', 'en_curso', 'pausada', 'finalizada', 'cancelada')),
    motivo_finalizacion TEXT,
    fecha_finalizacion_real DATE,
    
    id_centro INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_terapeuta) REFERENCES personal(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- =============================================
-- 2. TABLA: SESION_PACIENTE (Inscripción en sesiones terapéuticas)
-- =============================================
CREATE TABLE IF NOT EXISTS sesion_paciente (
    id SERIAL PRIMARY KEY,
    id_sesion INTEGER NOT NULL,
    id_paciente INTEGER NOT NULL,
    fecha_inscripcion DATE DEFAULT CURRENT_DATE,
    fecha_baja DATE,
    motivo_baja TEXT,
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'completado', 'retirado')),
    observaciones TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_sesion) REFERENCES sesion_terapia(id) ON DELETE CASCADE,
    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE RESTRICT,
    
    -- Constraint para evitar duplicados
    UNIQUE (id_sesion, id_paciente)
);

-- =============================================
-- 3. TABLA: CRONOGRAMA_SESIONES (Programación de citas terapéuticas)
-- =============================================
CREATE TABLE IF NOT EXISTS cronograma_sesiones (
    id SERIAL PRIMARY KEY,
    id_sesion INTEGER NOT NULL,
    fecha_programada DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    semana_numero INTEGER,
    numero_sesion_semanal INTEGER,
    
    -- Control de estado de la cita
    estado VARCHAR(20) DEFAULT 'programada' CHECK (estado IN 
        ('programada', 'confirmada', 'en_curso', 'completada', 'cancelada', 'reprogramada', 'no_asistio')),
    fecha_confirmacion TIMESTAMP,
    motivo_cancelacion TEXT,
    
    -- Reprogramación
    fecha_original DATE,
    motivo_reprogramacion TEXT,
    reprogramada_por INTEGER, -- ID del usuario que reprogramó
    
    observaciones TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_sesion) REFERENCES sesion_terapia(id) ON DELETE CASCADE,
    FOREIGN KEY (reprogramada_por) REFERENCES usuario(id)
);

-- =============================================
-- 4. TABLA: ASISTENCIA_SESIONES (Registro de asistencia terapéutica)
-- =============================================
CREATE TABLE IF NOT EXISTS asistencia_sesiones (
    id SERIAL PRIMARY KEY,
    id_cronograma INTEGER NOT NULL,
    id_paciente INTEGER NOT NULL,
    
    -- Registro de asistencia
    asistio BOOLEAN DEFAULT FALSE,
    hora_llegada TIME,
    hora_salida TIME,
    estado_asistencia VARCHAR(20) DEFAULT 'pendiente' CHECK (estado_asistencia IN 
        ('pendiente', 'presente', 'ausente', 'tarde', 'justificado', 'cancelado')),
    
    -- Observaciones de la sesión
    observaciones_terapeuta TEXT,
    objetivos_trabajados TEXT,
    actividades_realizadas TEXT,
    progreso_observado TEXT,
    tareas_asignadas TEXT,
    
    -- Evaluación de la sesión
    calificacion_sesion INTEGER CHECK (calificacion_sesion BETWEEN 1 AND 5),
    requiere_seguimiento BOOLEAN DEFAULT FALSE,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_cronograma) REFERENCES cronograma_sesiones(id) ON DELETE CASCADE,
    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE RESTRICT,
    
    -- Constraint para evitar duplicados
    UNIQUE (id_cronograma, id_paciente)
);

-- =============================================
-- 5. TABLA: SESION_PEDAGOGICA
-- =============================================
CREATE TABLE IF NOT EXISTS sesion_pedagogica (
    id SERIAL PRIMARY KEY,
    codigo_sesion VARCHAR(20) UNIQUE NOT NULL,
    id_educador INTEGER NOT NULL,
    id_especialidad INTEGER NOT NULL,
    nombre_clase VARCHAR(150) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    
    -- Configuración académica
    nivel_academico VARCHAR(50), -- preescolar, primaria, secundaria
    grado_escolar VARCHAR(20),
    materia VARCHAR(100),
    competencias_objetivo TEXT,
    metodologia_ensenanza TEXT,
    
    -- Programación
    duracion_minutos INTEGER DEFAULT 60,
    frecuencia_semanal INTEGER DEFAULT 2,
    dias_semana TEXT[], -- Array: ['martes', 'jueves']
    hora_inicio TIME DEFAULT '09:00',
    hora_fin TIME DEFAULT '10:00',
    aula VARCHAR(50),
    capacidad_maxima INTEGER DEFAULT 8,
    
    -- Control de estado
    estado VARCHAR(20) DEFAULT 'planificada' CHECK (estado IN 
        ('planificada', 'en_curso', 'pausada', 'finalizada', 'cancelada')),
    motivo_finalizacion TEXT,
    fecha_finalizacion_real DATE,
    
    id_centro INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_educador) REFERENCES personal(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- =============================================
-- 6. TABLA: SESION_ESTUDIANTE (Inscripción en sesiones pedagógicas)
-- =============================================
CREATE TABLE IF NOT EXISTS sesion_estudiante (
    id SERIAL PRIMARY KEY,
    id_sesion INTEGER NOT NULL,
    id_paciente INTEGER NOT NULL, -- Paciente como estudiante
    fecha_inscripcion DATE DEFAULT CURRENT_DATE,
    fecha_baja DATE,
    motivo_baja TEXT,
    
    -- Información académica
    nivel_actual VARCHAR(50),
    necesidades_especiales TEXT,
    adaptaciones_requeridas TEXT,
    
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'completado', 'retirado')),
    observaciones TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_sesion) REFERENCES sesion_pedagogica(id) ON DELETE CASCADE,
    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE RESTRICT,
    
    -- Constraint para evitar duplicados
    UNIQUE (id_sesion, id_paciente)
);

-- =============================================
-- 7. TABLA: CRONOGRAMA_CLASES (Programación de clases pedagógicas)
-- =============================================
CREATE TABLE IF NOT EXISTS cronograma_clases (
    id SERIAL PRIMARY KEY,
    id_sesion INTEGER NOT NULL,
    fecha_programada DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    semana_numero INTEGER,
    numero_clase_semanal INTEGER,
    
    -- Contenido de la clase
    tema_clase VARCHAR(200),
    objetivos_clase TEXT,
    materiales_necesarios TEXT,
    
    -- Control de estado de la clase
    estado VARCHAR(20) DEFAULT 'programada' CHECK (estado IN 
        ('programada', 'preparada', 'en_curso', 'completada', 'cancelada', 'reprogramada')),
    fecha_confirmacion TIMESTAMP,
    motivo_cancelacion TEXT,
    
    -- Reprogramación
    fecha_original DATE,
    motivo_reprogramacion TEXT,
    reprogramada_por INTEGER, -- ID del usuario que reprogramó
    
    observaciones TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_sesion) REFERENCES sesion_pedagogica(id) ON DELETE CASCADE,
    FOREIGN KEY (reprogramada_por) REFERENCES usuario(id)
);

-- =============================================
-- 8. TABLA: ASISTENCIA_CLASES (Registro de asistencia pedagógica)
-- =============================================
CREATE TABLE IF NOT EXISTS asistencia_clases (
    id SERIAL PRIMARY KEY,
    id_cronograma INTEGER NOT NULL,
    id_paciente INTEGER NOT NULL,
    
    -- Registro de asistencia
    asistio BOOLEAN DEFAULT FALSE,
    hora_llegada TIME,
    hora_salida TIME,
    estado_asistencia VARCHAR(20) DEFAULT 'pendiente' CHECK (estado_asistencia IN 
        ('pendiente', 'presente', 'ausente', 'tarde', 'justificado', 'cancelado')),
    
    -- Observaciones académicas
    observaciones_educador TEXT,
    participacion_clase VARCHAR(20) CHECK (participacion_clase IN ('excelente', 'buena', 'regular', 'deficiente')),
    comprension_tema VARCHAR(20) CHECK (comprension_tema IN ('excelente', 'buena', 'regular', 'deficiente')),
    actividades_completadas BOOLEAN DEFAULT FALSE,
    tareas_asignadas TEXT,
    
    -- Evaluación académica
    calificacion_clase INTEGER CHECK (calificacion_clase BETWEEN 1 AND 10),
    evaluacion_comportamiento VARCHAR(20) CHECK (evaluacion_comportamiento IN ('excelente', 'bueno', 'regular', 'necesita_apoyo')),
    requiere_refuerzo BOOLEAN DEFAULT FALSE,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_cronograma) REFERENCES cronograma_clases(id) ON DELETE CASCADE,
    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE RESTRICT,
    
    -- Constraint para evitar duplicados
    UNIQUE (id_cronograma, id_paciente)
);

-- =============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =============================================
CREATE INDEX IF NOT EXISTS idx_sesion_terapia_terapeuta ON sesion_terapia(id_terapeuta);
CREATE INDEX IF NOT EXISTS idx_sesion_terapia_especialidad ON sesion_terapia(id_especialidad);
CREATE INDEX IF NOT EXISTS idx_sesion_terapia_centro ON sesion_terapia(id_centro);
CREATE INDEX IF NOT EXISTS idx_sesion_terapia_codigo ON sesion_terapia(codigo_sesion);

CREATE INDEX IF NOT EXISTS idx_sesion_paciente_sesion ON sesion_paciente(id_sesion);
CREATE INDEX IF NOT EXISTS idx_sesion_paciente_paciente ON sesion_paciente(id_paciente);

CREATE INDEX IF NOT EXISTS idx_cronograma_sesiones_sesion ON cronograma_sesiones(id_sesion);
CREATE INDEX IF NOT EXISTS idx_cronograma_sesiones_fecha ON cronograma_sesiones(fecha_programada);

CREATE INDEX IF NOT EXISTS idx_asistencia_sesiones_cronograma ON asistencia_sesiones(id_cronograma);
CREATE INDEX IF NOT EXISTS idx_asistencia_sesiones_paciente ON asistencia_sesiones(id_paciente);

CREATE INDEX IF NOT EXISTS idx_sesion_pedagogica_educador ON sesion_pedagogica(id_educador);
CREATE INDEX IF NOT EXISTS idx_sesion_pedagogica_especialidad ON sesion_pedagogica(id_especialidad);
CREATE INDEX IF NOT EXISTS idx_sesion_pedagogica_codigo ON sesion_pedagogica(codigo_sesion);

CREATE INDEX IF NOT EXISTS idx_sesion_estudiante_sesion ON sesion_estudiante(id_sesion);
CREATE INDEX IF NOT EXISTS idx_sesion_estudiante_paciente ON sesion_estudiante(id_paciente);

CREATE INDEX IF NOT EXISTS idx_cronograma_clases_sesion ON cronograma_clases(id_sesion);
CREATE INDEX IF NOT EXISTS idx_cronograma_clases_fecha ON cronograma_clases(fecha_programada);

CREATE INDEX IF NOT EXISTS idx_asistencia_clases_cronograma ON asistencia_clases(id_cronograma);
CREATE INDEX IF NOT EXISTS idx_asistencia_clases_paciente ON asistencia_clases(id_paciente);

-- =============================================
-- TRIGGERS PARA AUDITORÍA
-- =============================================
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

CREATE TRIGGER trigger_sesion_pedagogica_fecha_modificacion
    BEFORE UPDATE ON sesion_pedagogica
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_sesion_estudiante_fecha_modificacion
    BEFORE UPDATE ON sesion_estudiante
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_cronograma_clases_fecha_modificacion
    BEFORE UPDATE ON cronograma_clases
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_asistencia_clases_fecha_modificacion
    BEFORE UPDATE ON asistencia_clases
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- =============================================
-- FUNCIONES PARA GESTIÓN DE SESIONES
-- =============================================

-- Función para generar código único de sesión terapéutica
CREATE OR REPLACE FUNCTION generar_codigo_sesion_terapia()
RETURNS TRIGGER AS $$
DECLARE
    nuevo_codigo VARCHAR(20);
BEGIN
    nuevo_codigo := 'ST-' || TO_CHAR(CURRENT_DATE, 'YYYY') || '-' ||
                   LPAD(nextval('seq_codigo_sesion_terapia')::TEXT, 4, '0');
    
    NEW.codigo_sesion := nuevo_codigo;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Función para generar código único de sesión pedagógica
CREATE OR REPLACE FUNCTION generar_codigo_sesion_pedagogica()
RETURNS TRIGGER AS $$
DECLARE
    nuevo_codigo VARCHAR(20);
BEGIN
    nuevo_codigo := 'SP-' || TO_CHAR(CURRENT_DATE, 'YYYY') || '-' ||
                   LPAD(nextval('seq_codigo_sesion_pedagogica')::TEXT, 4, '0');
    
    NEW.codigo_sesion := nuevo_codigo;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Secuencias para códigos
CREATE SEQUENCE IF NOT EXISTS seq_codigo_sesion_terapia START 1;
CREATE SEQUENCE IF NOT EXISTS seq_codigo_sesion_pedagogica START 1;

-- Triggers para generar códigos automáticos
CREATE TRIGGER trigger_generar_codigo_sesion_terapia
    BEFORE INSERT ON sesion_terapia
    FOR EACH ROW
    WHEN (NEW.codigo_sesion IS NULL OR NEW.codigo_sesion = '')
    EXECUTE FUNCTION generar_codigo_sesion_terapia();

CREATE TRIGGER trigger_generar_codigo_sesion_pedagogica
    BEFORE INSERT ON sesion_pedagogica
    FOR EACH ROW
    WHEN (NEW.codigo_sesion IS NULL OR NEW.codigo_sesion = '')
    EXECUTE FUNCTION generar_codigo_sesion_pedagogica();

-- =============================================
-- FUNCIONES PARA CRONOGRAMAS
-- =============================================

-- Función para generar cronograma automático de sesiones terapéuticas
CREATE OR REPLACE FUNCTION generar_cronograma_sesion_terapia(p_id_sesion INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    sesion_rec RECORD;
    fecha_actual DATE;
    fecha_limite DATE;
    dia_semana TEXT;
    hora_sesion TIME;
    contador_semana INTEGER := 1;
    contador_sesion INTEGER;
BEGIN
    -- Obtener datos de la sesión
    SELECT * INTO sesion_rec FROM sesion_terapia WHERE id = p_id_sesion;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Sesión terapéutica no encontrada';
    END IF;
    
    fecha_actual := sesion_rec.fecha_inicio;
    fecha_limite := COALESCE(sesion_rec.fecha_fin, fecha_actual + INTERVAL '3 months');
    hora_sesion := sesion_rec.hora_inicio;
    
    -- Generar cronograma
    WHILE fecha_actual <= fecha_limite LOOP
        contador_sesion := 1;
        
        -- Iterar por los días de la semana configurados
        FOREACH dia_semana IN ARRAY sesion_rec.dias_semana LOOP
            DECLARE
                fecha_dia DATE;
                num_dia INTEGER;
            BEGIN
                -- Convertir día de texto a número
                num_dia := CASE LOWER(dia_semana)
                    WHEN 'lunes' THEN 1
                    WHEN 'martes' THEN 2
                    WHEN 'miércoles' THEN 3
                    WHEN 'jueves' THEN 4
                    WHEN 'viernes' THEN 5
                    WHEN 'sábado' THEN 6
                    WHEN 'domingo' THEN 0
                    ELSE 1
                END;
                
                -- Calcular fecha del día
                fecha_dia := fecha_actual + (num_dia - EXTRACT(DOW FROM fecha_actual))::INTEGER;
                
                -- Ajustar si la fecha es anterior a la fecha actual
                IF fecha_dia < fecha_actual THEN
                    fecha_dia := fecha_dia + INTERVAL '7 days';
                END IF;
                
                -- Verificar que esté dentro del rango
                IF fecha_dia <= fecha_limite THEN
                    INSERT INTO cronograma_sesiones (
                        id_sesion, fecha_programada, hora_inicio, hora_fin,
                        semana_numero, numero_sesion_semanal, estado
                    ) VALUES (
                        p_id_sesion, fecha_dia, hora_sesion, 
                        hora_sesion + (sesion_rec.duracion_minutos || ' minutes')::INTERVAL,
                        contador_semana, contador_sesion, 'programada'
                    );
                    
                    contador_sesion := contador_sesion + 1;
                END IF;
            END;
        END LOOP;
        
        fecha_actual := fecha_actual + INTERVAL '7 days';
        contador_semana := contador_semana + 1;
    END LOOP;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Función similar para sesiones pedagógicas
CREATE OR REPLACE FUNCTION generar_cronograma_sesion_pedagogica(p_id_sesion INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    sesion_rec RECORD;
    fecha_actual DATE;
    fecha_limite DATE;
    dia_semana TEXT;
    hora_clase TIME;
    contador_semana INTEGER := 1;
    contador_clase INTEGER;
BEGIN
    -- Obtener datos de la sesión
    SELECT * INTO sesion_rec FROM sesion_pedagogica WHERE id = p_id_sesion;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Sesión pedagógica no encontrada';
    END IF;
    
    fecha_actual := sesion_rec.fecha_inicio;
    fecha_limite := COALESCE(sesion_rec.fecha_fin, fecha_actual + INTERVAL '4 months');
    hora_clase := sesion_rec.hora_inicio;
    
    -- Generar cronograma
    WHILE fecha_actual <= fecha_limite LOOP
        contador_clase := 1;
        
        -- Iterar por los días de la semana configurados
        FOREACH dia_semana IN ARRAY sesion_rec.dias_semana LOOP
            DECLARE
                fecha_dia DATE;
                num_dia INTEGER;
            BEGIN
                -- Convertir día de texto a número
                num_dia := CASE LOWER(dia_semana)
                    WHEN 'lunes' THEN 1
                    WHEN 'martes' THEN 2
                    WHEN 'miércoles' THEN 3
                    WHEN 'jueves' THEN 4
                    WHEN 'viernes' THEN 5
                    WHEN 'sábado' THEN 6
                    WHEN 'domingo' THEN 0
                    ELSE 1
                END;
                
                -- Calcular fecha del día
                fecha_dia := fecha_actual + (num_dia - EXTRACT(DOW FROM fecha_actual))::INTEGER;
                
                -- Ajustar si la fecha es anterior a la fecha actual
                IF fecha_dia < fecha_actual THEN
                    fecha_dia := fecha_dia + INTERVAL '7 days';
                END IF;
                
                -- Verificar que esté dentro del rango
                IF fecha_dia <= fecha_limite THEN
                    INSERT INTO cronograma_clases (
                        id_sesion, fecha_programada, hora_inicio, hora_fin,
                        semana_numero, numero_clase_semanal, estado
                    ) VALUES (
                        p_id_sesion, fecha_dia, hora_clase, 
                        hora_clase + (sesion_rec.duracion_minutos || ' minutes')::INTERVAL,
                        contador_semana, contador_clase, 'programada'
                    );
                    
                    contador_clase := contador_clase + 1;
                END IF;
            END;
        END LOOP;
        
        fecha_actual := fecha_actual + INTERVAL '7 days';
        contador_semana := contador_semana + 1;
    END LOOP;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- COMENTARIOS EN TABLAS
-- =============================================
COMMENT ON TABLE sesion_terapia IS 'Configuración y gestión de sesiones terapéuticas';
COMMENT ON TABLE sesion_paciente IS 'Inscripción de pacientes en sesiones terapéuticas';
COMMENT ON TABLE cronograma_sesiones IS 'Programación de citas individuales de terapia';
COMMENT ON TABLE asistencia_sesiones IS 'Registro de asistencia y progreso en sesiones terapéuticas';
COMMENT ON TABLE sesion_pedagogica IS 'Configuración y gestión de sesiones pedagógicas/educativas';
COMMENT ON TABLE sesion_estudiante IS 'Inscripción de pacientes como estudiantes en sesiones pedagógicas';
COMMENT ON TABLE cronograma_clases IS 'Programación de clases pedagógicas';
COMMENT ON TABLE asistencia_clases IS 'Registro de asistencia y evaluación en clases pedagógicas';