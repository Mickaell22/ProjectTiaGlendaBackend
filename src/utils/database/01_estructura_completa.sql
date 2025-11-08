-- =============================================
-- CENTRO TÍA GLENDA - ESTRUCTURA COMPLETA DE BASE DE DATOS
-- Archivo: 01_estructura_completa.sql
-- Descripción: Creación completa de todas las tablas, funciones y triggers
-- =============================================

-- =============================================
-- CONFIGURACIÓN INICIAL
-- =============================================

-- Configurar esquema por defecto
SET search_path TO public;

-- Crear esquema public si no existe
CREATE SCHEMA IF NOT EXISTS public;

-- Asegurar permisos en esquema public
GRANT ALL ON SCHEMA public TO public;

-- Eliminar tablas existentes en orden correcto (si existen)
DROP TABLE IF EXISTS historial_pausas CASCADE;
DROP TABLE IF EXISTS asistencia_clases CASCADE;
DROP TABLE IF EXISTS cronograma_clases CASCADE;
DROP TABLE IF EXISTS sesion_estudiante CASCADE;
DROP TABLE IF EXISTS asistencia_sesiones CASCADE;
DROP TABLE IF EXISTS cronograma_sesiones CASCADE;
DROP TABLE IF EXISTS sesion_paciente CASCADE;
DROP TABLE IF EXISTS tokens_publicos_sesion_pedagogica CASCADE;
DROP TABLE IF EXISTS tokens_publicos_sesion CASCADE;
DROP TABLE IF EXISTS sesion_pedagogica CASCADE;
DROP TABLE IF EXISTS sesion_terapia CASCADE;
DROP TABLE IF EXISTS observaciones_sesiones CASCADE;
DROP TABLE IF EXISTS mensajes_chat CASCADE;
DROP TABLE IF EXISTS documentos_paciente CASCADE;
DROP TABLE IF EXISTS paciente_especialidades CASCADE;
DROP TABLE IF EXISTS paciente CASCADE;
DROP TABLE IF EXISTS tutor CASCADE;
DROP TABLE IF EXISTS documentos_personal CASCADE;
DROP TABLE IF EXISTS personal_especialidades CASCADE;
DROP TABLE IF EXISTS personal CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;
DROP TABLE IF EXISTS especialidad CASCADE;
DROP TABLE IF EXISTS persona CASCADE;
DROP TABLE IF EXISTS rol CASCADE;
DROP TABLE IF EXISTS centros CASCADE;

-- Eliminar secuencias si existen
DROP SEQUENCE IF EXISTS seq_codigo_paciente CASCADE;
DROP SEQUENCE IF EXISTS seq_codigo_sesion_terapia CASCADE;
DROP SEQUENCE IF EXISTS seq_codigo_sesion_pedagogica CASCADE;

-- =============================================
-- TABLAS BASE DEL SISTEMA
-- =============================================

-- 1. TABLA: CENTROS (Centros de atención)
CREATE TABLE centros (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(10) NOT NULL UNIQUE, -- Norte/Sur
    direccion VARCHAR(255),
    telefono VARCHAR(15),
    email VARCHAR(150),
    
    -- Configuración de horarios
    horario_apertura TIME DEFAULT '07:00',
    horario_cierre TIME DEFAULT '18:00',
    
    -- Configuración de turnos
    turno_principal VARCHAR(20) DEFAULT 'mixto' CHECK (turno_principal IN ('matutino', 'vespertino', 'mixto')),
    
    -- Estado y control
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'mantenimiento')),
    observaciones TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- 2. TABLA: ROL (Catálogo de roles)
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

-- 3. TABLA: PERSONA (Información demográfica base)
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

-- 4. TABLA: ESPECIALIDAD (Catálogo de especialidades)
CREATE TABLE especialidad (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    area VARCHAR(100) NOT NULL CHECK (area IN ('Especialidad terapéutica', 'Especialidad pedagógica')),
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    id_centro INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,

    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT,
    UNIQUE (nombre, id_centro)  -- Permitir mismas especialidades en diferentes centros
);

-- 5. TABLA: USUARIO (Credenciales del sistema)
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasenia VARCHAR(255) NOT NULL,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'bloqueado')),
    
    -- Información de perfil
    foto_perfil VARCHAR(500), -- Ruta del archivo de foto de perfil
    
    id_persona INTEGER NOT NULL,
    id_rol INTEGER NOT NULL,
    id_centro INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultimo_acceso TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_persona) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_rol) REFERENCES rol(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- =============================================
-- TABLAS DE PERSONAL
-- =============================================

-- 6. TABLA: PERSONAL
CREATE TABLE personal (
    id SERIAL PRIMARY KEY,
    id_persona INTEGER NOT NULL,
    id_especialidad INTEGER NOT NULL, -- Especialidad principal
    numero_registro VARCHAR(50) UNIQUE,
    fecha_ingreso DATE NOT NULL,
    fecha_salida DATE,
    cargo VARCHAR(100),
    titulo_profesional VARCHAR(100),
    tipo_contrato VARCHAR(20) CHECK (tipo_contrato IN ('indefinido', 'temporal', 'honorarios', 'practicante')),
    salario DECIMAL(10,2) CHECK (salario >= 0),
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'vacaciones', 'licencia')),
    observaciones TEXT,
    id_centro INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_persona) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- 7. TABLA: PERSONAL_ESPECIALIDADES (Especialidades múltiples)
CREATE TABLE personal_especialidades (
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

-- 8. TABLA: DOCUMENTOS_PERSONAL
CREATE TABLE documentos_personal (
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
-- TABLAS DE PACIENTES Y TUTORES
-- =============================================

-- 9. TABLA: TUTOR
CREATE TABLE tutor (
    id SERIAL PRIMARY KEY,
    id_persona INTEGER NOT NULL,
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
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_persona) REFERENCES persona(id) ON DELETE RESTRICT
);

-- 10. TABLA: PACIENTE
CREATE TABLE paciente (
    id SERIAL PRIMARY KEY,
    id_persona INTEGER NOT NULL,
    id_tutor INTEGER NOT NULL,
    codigo_paciente VARCHAR(20) UNIQUE, -- Auto-generado
    fecha_ingreso DATE NOT NULL,
    motivo_consulta TEXT,
    observaciones TEXT,

    -- Información médica adicional
      alergias TEXT,
      medicina TEXT,

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
    
    FOREIGN KEY (id_persona) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_tutor) REFERENCES tutor(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- 11. TABLA: PACIENTE_ESPECIALIDADES (Especialidades múltiples)
CREATE TABLE paciente_especialidades (
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

-- 12. TABLA: DOCUMENTOS_PACIENTE
CREATE TABLE documentos_paciente (
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
-- TABLAS DE SESIONES
-- =============================================

-- 13. TABLA: SESION_TERAPIA
CREATE TABLE sesion_terapia (
    id SERIAL PRIMARY KEY,
    codigo_sesion VARCHAR(20) UNIQUE NOT NULL,
    id_terapeuta INTEGER NOT NULL,
    id_especialidad INTEGER NOT NULL,
    
    -- Información básica de la sesión
    titulo VARCHAR(200) NOT NULL, -- Campo agregado para título de la sesión
    objetivo_general TEXT,


    
    -- Fechas y programación
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    dias_semana TEXT[] CHECK (array_length(dias_semana, 1) > 0), -- Array: ['lunes', 'miércoles', 'viernes']
    hora_inicio TIME DEFAULT '08:00',
    hora_fin TIME DEFAULT '08:45',
    duracion_minutos INTEGER DEFAULT 45 CHECK (duracion_minutos > 0),

    
    -- Configuración del contrato
    numero_sesiones_contratadas INTEGER DEFAULT 20 CHECK (numero_sesiones_contratadas > 0), -- Campo agregado
    meses_contrato INTEGER DEFAULT 3 CHECK (meses_contrato > 0), -- Campo agregado
    costo_sesion DECIMAL(10,2) DEFAULT 0.00 CHECK (costo_sesion >= 0),
    costo_total DECIMAL(10,2) DEFAULT 0.00 CHECK (costo_total >= 0), -- Campo agregado para costo total calculado
    
    -- Configuración de modalidad
    tipo_sesion VARCHAR(20) DEFAULT 'individual' CHECK (tipo_sesion IN ('individual', 'grupal', 'familiar')),

    
    -- Control de estado
    estado VARCHAR(20) DEFAULT 'planificada' CHECK (estado IN
        ('planificada', 'en_curso', 'pausada', 'finalizada', 'cancelada')),
    motivo_finalizacion TEXT,
    fecha_finalizacion_real DATE,
    observaciones TEXT,

    -- Control de auditoría
    id_centro INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_terapeuta) REFERENCES personal(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- 14. TABLA: SESION_PACIENTE (Inscripción en sesiones terapéuticas)
CREATE TABLE sesion_paciente (
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

-- 15. TABLA: CRONOGRAMA_SESIONES (Programación de citas terapéuticas)
CREATE TABLE cronograma_sesiones (
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
    fecha_realizacion TIMESTAMP DEFAULT NULL,
    
    observaciones TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_sesion) REFERENCES sesion_terapia(id) ON DELETE CASCADE,
    FOREIGN KEY (reprogramada_por) REFERENCES usuario(id)
);

-- 16. TABLA: ASISTENCIA_SESIONES (Registro de asistencia terapéutica)
CREATE TABLE asistencia_sesiones (
    id SERIAL PRIMARY KEY,
    id_cronograma INTEGER NOT NULL,
    id_paciente INTEGER NOT NULL,

    -- Registro de asistencia
    asistio BOOLEAN DEFAULT FALSE,
    llegada_tardanza_minutos INTEGER DEFAULT 0,
    estado_asistencia VARCHAR(20) DEFAULT 'pendiente' CHECK (estado_asistencia IN
        ('pendiente', 'presente', 'ausente', 'tarde', 'justificado', 'cancelado')),

    -- Observaciones de la sesión
    observaciones_terapeuta TEXT,
    objetivos_trabajados TEXT,
    actividades_realizadas TEXT,
    progreso_observado TEXT,
    tareas_asignadas TEXT,

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

-- 17. TABLA: SESION_PEDAGOGICA
CREATE TABLE sesion_pedagogica (
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
    adaptacion_curricular TEXT,

    -- Programación
    duracion_minutos INTEGER DEFAULT 60 CHECK (duracion_minutos > 0),
    frecuencia_semanal INTEGER DEFAULT 2 CHECK (frecuencia_semanal > 0 AND frecuencia_semanal <= 7),
    numero_clases_programadas INTEGER DEFAULT 20 CHECK (numero_clases_programadas > 0),
    dias_semana TEXT[] CHECK (array_length(dias_semana, 1) > 0),
    hora_inicio TIME DEFAULT '09:00',
    hora_fin TIME DEFAULT '10:00',
    capacidad_maxima INTEGER DEFAULT 8 CHECK (capacidad_maxima > 0),

    -- Modalidad y periodo académico
    modalidad VARCHAR(20) DEFAULT 'presencial' CHECK (modalidad IN ('presencial', 'virtual', 'hibrida')),
    periodo_academico VARCHAR(50),

    -- Costos
    costo_total DECIMAL(10,2) DEFAULT 0.00 CHECK (costo_total >= 0),
    costo_por_clase DECIMAL(10,2) DEFAULT 0.00 CHECK (costo_por_clase >= 0),

    -- Control de estado
    estado VARCHAR(20) DEFAULT 'planificada' CHECK (estado IN
        ('planificada', 'en_curso', 'pausada', 'finalizada', 'cancelada')),
    motivo_finalizacion TEXT,
    fecha_finalizacion_real DATE,
    observaciones TEXT,

    id_centro INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,

    FOREIGN KEY (id_educador) REFERENCES personal(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- 18. TABLA: SESION_ESTUDIANTE (Inscripción en sesiones pedagógicas)
CREATE TABLE sesion_estudiante (
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

-- 19. TABLA: CRONOGRAMA_CLASES (Programación de clases pedagógicas)
CREATE TABLE cronograma_clases (
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
        ('programada', 'preparada', 'en_curso', 'completada', 'cancelada', 'reprogramada', 'realizada')),
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

-- 20. TABLA: ASISTENCIA_CLASES (Registro de asistencia pedagógica)
CREATE TABLE asistencia_clases (
    id SERIAL PRIMARY KEY,
    id_cronograma INTEGER NOT NULL,
    id_paciente INTEGER NOT NULL,

    -- Registro de asistencia
    asistio BOOLEAN DEFAULT FALSE,
    llegada_tardanza_minutos INTEGER DEFAULT 0 CHECK (llegada_tardanza_minutos >= 0),
    estado_asistencia VARCHAR(20) DEFAULT 'pendiente' CHECK (estado_asistencia IN
        ('pendiente', 'presente', 'ausente', 'tarde', 'justificado', 'cancelado')),

    -- Observaciones académicas
    observaciones_educador TEXT,
    objetivos_trabajados TEXT,
    participacion_clase VARCHAR(20) CHECK (participacion_clase IN ('excelente', 'buena', 'regular', 'deficiente')),
    actividades_completadas BOOLEAN DEFAULT FALSE,
    tareas_asignadas TEXT,

    -- Evaluación académica
    calificacion_clase INTEGER CHECK (calificacion_clase BETWEEN 1 AND 10),

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
-- TABLAS DE TOKENS PÚBLICOS PARA COMPARTIR SESIONES
-- =============================================

-- 21. TABLA: TOKENS_PUBLICOS_SESION (Enlaces públicos para sesiones terapéuticas)
CREATE TABLE tokens_publicos_sesion (
    id SERIAL PRIMARY KEY,
    id_sesion INTEGER NOT NULL,
    token VARCHAR(128) UNIQUE NOT NULL,
    nombre_enlace VARCHAR(100) NOT NULL,
    descripcion TEXT,
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'expirado')),
    fecha_expiracion TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,

    FOREIGN KEY (id_sesion) REFERENCES sesion_terapia(id) ON DELETE CASCADE
);

-- 22. TABLA: TOKENS_PUBLICOS_SESION_PEDAGOGICA (Enlaces públicos para sesiones pedagógicas)
CREATE TABLE tokens_publicos_sesion_pedagogica (
    id SERIAL PRIMARY KEY,
    id_sesion INTEGER NOT NULL,
    token VARCHAR(128) UNIQUE NOT NULL,
    nombre_enlace VARCHAR(100) NOT NULL,
    descripcion TEXT,
    estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'expirado')),
    fecha_expiracion TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,

    FOREIGN KEY (id_sesion) REFERENCES sesion_pedagogica(id) ON DELETE CASCADE
);

-- =============================================
-- TABLAS DE COMUNICACIÓN
-- =============================================

-- 23. TABLA: MENSAJES_CHAT (Sistema de chat interno)
CREATE TABLE mensajes_chat (
    id SERIAL PRIMARY KEY,
    id_remitente INTEGER NOT NULL,
    id_destinatario INTEGER NOT NULL,
    mensaje TEXT NOT NULL,
    
    -- Control de lectura
    leido BOOLEAN DEFAULT FALSE,
    fecha_lectura TIMESTAMP,
    
    -- Metadatos del mensaje
    tipo_mensaje VARCHAR(20) DEFAULT 'texto' CHECK (tipo_mensaje IN ('texto', 'archivo', 'imagen', 'urgente')),
    prioridad VARCHAR(10) DEFAULT 'normal' CHECK (prioridad IN ('baja', 'normal', 'alta', 'urgente')),
    es_privado BOOLEAN DEFAULT FALSE,
    
    -- Archivos adjuntos
    ruta_archivo VARCHAR(500),
    nombre_archivo VARCHAR(255),
    tamaño_archivo INTEGER,
    tipo_mime VARCHAR(100),
    
    -- Control por centro
    id_centro INTEGER NOT NULL,
    
    -- Control de eliminación
    eliminado_remitente BOOLEAN DEFAULT FALSE,
    eliminado_destinatario BOOLEAN DEFAULT FALSE,
    fecha_eliminacion_remitente TIMESTAMP,
    fecha_eliminacion_destinatario TIMESTAMP,
    
    -- Auditoría
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_remitente) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_destinatario) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- 24. TABLA: OBSERVACIONES_SESIONES (Observaciones de sesiones)
CREATE TABLE observaciones_sesiones (
    id SERIAL PRIMARY KEY,
    id_sesion INTEGER NOT NULL, -- Puede ser terapéutica o pedagógica
    tipo_sesion VARCHAR(20) NOT NULL CHECK (tipo_sesion IN ('terapeutica', 'pedagogica')),
    id_usuario INTEGER NOT NULL, -- Quien hace la observación
    
    -- Contenido de la observación
    observacion TEXT NOT NULL,
    tipo_observacion VARCHAR(20) DEFAULT 'observacion' CHECK (tipo_observacion IN 
        ('observacion', 'nota', 'alerta', 'progreso', 'falta', 'incidente', 'logro', 'preocupacion')),
    
    -- Control de privacidad
    es_privada BOOLEAN DEFAULT FALSE, -- Solo visible para admin y quien la creó
    es_seguimiento BOOLEAN DEFAULT FALSE, -- Requiere seguimiento
    fecha_seguimiento DATE,
    seguimiento_completado BOOLEAN DEFAULT FALSE,
    
    -- Categorización
    categoria VARCHAR(50), -- comportamiento, academico, social, familiar, etc.
    nivel_importancia VARCHAR(10) DEFAULT 'medio' CHECK (nivel_importancia IN ('bajo', 'medio', 'alto', 'critico')),
    
    -- Archivos adjuntos
    ruta_archivo VARCHAR(500),
    nombre_archivo VARCHAR(255),
    tipo_mime VARCHAR(100),
    
    -- Etiquetas para búsqueda
    etiquetas TEXT[], -- Array de etiquetas
    
    -- Relaciones
    id_paciente INTEGER, -- Paciente específico (si aplica)
    observacion_padre INTEGER, -- Para respuestas o seguimientos
    
    -- Auditoría
    fecha_observacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE SET NULL,
    FOREIGN KEY (observacion_padre) REFERENCES observaciones_sesiones(id) ON DELETE SET NULL
);

-- =============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =============================================

-- Índices para tablas base
CREATE INDEX IF NOT EXISTS idx_persona_cedula ON persona(cedula);
CREATE INDEX IF NOT EXISTS idx_usuario_usuario ON usuario(usuario);
CREATE INDEX IF NOT EXISTS idx_usuario_centro ON usuario(id_centro);
CREATE INDEX IF NOT EXISTS idx_especialidad_nombre ON especialidad(nombre);
CREATE INDEX IF NOT EXISTS idx_especialidad_centro ON especialidad(id_centro);

-- Índices para personal
CREATE INDEX IF NOT EXISTS idx_personal_persona ON personal(id_persona);
CREATE INDEX IF NOT EXISTS idx_personal_especialidad ON personal(id_especialidad);
CREATE INDEX IF NOT EXISTS idx_personal_centro ON personal(id_centro);
CREATE INDEX IF NOT EXISTS idx_personal_especialidades_personal ON personal_especialidades(id_personal);
CREATE INDEX IF NOT EXISTS idx_personal_especialidades_especialidad ON personal_especialidades(id_especialidad);
CREATE INDEX IF NOT EXISTS idx_documentos_personal_personal ON documentos_personal(id_personal);
CREATE INDEX IF NOT EXISTS idx_documentos_personal_tipo ON documentos_personal(tipo_documento);
CREATE INDEX IF NOT EXISTS idx_documentos_personal_estado ON documentos_personal(estado_validacion);

-- Índices para pacientes
CREATE INDEX IF NOT EXISTS idx_tutor_persona ON tutor(id_persona);
CREATE INDEX IF NOT EXISTS idx_paciente_persona ON paciente(id_persona);
CREATE INDEX IF NOT EXISTS idx_paciente_tutor ON paciente(id_tutor);
CREATE INDEX IF NOT EXISTS idx_paciente_centro ON paciente(id_centro);
CREATE INDEX IF NOT EXISTS idx_paciente_codigo ON paciente(codigo_paciente);
CREATE INDEX IF NOT EXISTS idx_paciente_especialidades_paciente ON paciente_especialidades(id_paciente);
CREATE INDEX IF NOT EXISTS idx_paciente_especialidades_especialidad ON paciente_especialidades(id_especialidad);
CREATE INDEX IF NOT EXISTS idx_documentos_paciente_paciente ON documentos_paciente(id_paciente);
CREATE INDEX IF NOT EXISTS idx_documentos_paciente_tipo ON documentos_paciente(tipo_documento);

-- Índices para sesiones terapéuticas
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

-- Índices para sesiones pedagógicas
CREATE INDEX IF NOT EXISTS idx_sesion_pedagogica_educador ON sesion_pedagogica(id_educador);
CREATE INDEX IF NOT EXISTS idx_sesion_pedagogica_especialidad ON sesion_pedagogica(id_especialidad);
CREATE INDEX IF NOT EXISTS idx_sesion_pedagogica_codigo ON sesion_pedagogica(codigo_sesion);
CREATE INDEX IF NOT EXISTS idx_sesion_estudiante_sesion ON sesion_estudiante(id_sesion);
CREATE INDEX IF NOT EXISTS idx_sesion_estudiante_paciente ON sesion_estudiante(id_paciente);
CREATE INDEX IF NOT EXISTS idx_cronograma_clases_sesion ON cronograma_clases(id_sesion);
CREATE INDEX IF NOT EXISTS idx_cronograma_clases_fecha ON cronograma_clases(fecha_programada);
CREATE INDEX IF NOT EXISTS idx_asistencia_clases_cronograma ON asistencia_clases(id_cronograma);
CREATE INDEX IF NOT EXISTS idx_asistencia_clases_paciente ON asistencia_clases(id_paciente);

-- Índices para tokens públicos
CREATE INDEX IF NOT EXISTS idx_tokens_publicos_sesion_sesion ON tokens_publicos_sesion(id_sesion);
CREATE INDEX IF NOT EXISTS idx_tokens_publicos_sesion_token ON tokens_publicos_sesion(token);
CREATE INDEX IF NOT EXISTS idx_tokens_publicos_sesion_estado ON tokens_publicos_sesion(estado);
CREATE INDEX IF NOT EXISTS idx_tokens_publicos_sesion_pedagogica_sesion ON tokens_publicos_sesion_pedagogica(id_sesion);
CREATE INDEX IF NOT EXISTS idx_tokens_publicos_sesion_pedagogica_token ON tokens_publicos_sesion_pedagogica(token);
CREATE INDEX IF NOT EXISTS idx_tokens_publicos_sesion_pedagogica_estado ON tokens_publicos_sesion_pedagogica(estado);

-- Índices para comunicación
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_remitente ON mensajes_chat(id_remitente);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_destinatario ON mensajes_chat(id_destinatario);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_centro ON mensajes_chat(id_centro);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_fecha ON mensajes_chat(fecha_envio);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_leido ON mensajes_chat(leido);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_conversacion ON mensajes_chat(id_remitente, id_destinatario, fecha_envio);
CREATE INDEX IF NOT EXISTS idx_observaciones_sesion ON observaciones_sesiones(id_sesion, tipo_sesion);
CREATE INDEX IF NOT EXISTS idx_observaciones_usuario ON observaciones_sesiones(id_usuario);
CREATE INDEX IF NOT EXISTS idx_observaciones_paciente ON observaciones_sesiones(id_paciente);
CREATE INDEX IF NOT EXISTS idx_observaciones_tipo ON observaciones_sesiones(tipo_observacion);
CREATE INDEX IF NOT EXISTS idx_observaciones_fecha ON observaciones_sesiones(fecha_observacion);
CREATE INDEX IF NOT EXISTS idx_observaciones_seguimiento ON observaciones_sesiones(es_seguimiento, seguimiento_completado);
CREATE INDEX IF NOT EXISTS idx_observaciones_privada ON observaciones_sesiones(es_privada);
CREATE INDEX IF NOT EXISTS idx_observaciones_etiquetas ON observaciones_sesiones USING gin(etiquetas);

-- =============================================
-- SECUENCIAS
-- =============================================

-- Secuencias para códigos únicos
CREATE SEQUENCE seq_codigo_paciente START 1;
CREATE SEQUENCE seq_codigo_sesion_terapia START 1;
CREATE SEQUENCE seq_codigo_sesion_pedagogica START 1;

-- =============================================
-- FUNCIONES AUXILIARES
-- =============================================

-- Función para actualizar fecha_modificacion
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- TRIGGERS PARA AUDITORÍA
-- =============================================

-- Triggers para tablas base
CREATE TRIGGER trigger_centros_fecha_modificacion
    BEFORE UPDATE ON centros
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_rol_fecha_modificacion
    BEFORE UPDATE ON rol
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_persona_fecha_modificacion
    BEFORE UPDATE ON persona
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_usuario_fecha_modificacion
    BEFORE UPDATE ON usuario
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_especialidad_fecha_modificacion
    BEFORE UPDATE ON especialidad
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- Triggers para personal
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

-- Triggers para pacientes
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

-- Triggers para sesiones
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

-- Triggers para tokens públicos
CREATE TRIGGER trigger_tokens_publicos_sesion_fecha_modificacion
    BEFORE UPDATE ON tokens_publicos_sesion
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_tokens_publicos_sesion_pedagogica_fecha_modificacion
    BEFORE UPDATE ON tokens_publicos_sesion_pedagogica
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- Triggers para comunicación
CREATE TRIGGER trigger_mensajes_chat_fecha_modificacion
    BEFORE UPDATE ON mensajes_chat
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_observaciones_sesiones_fecha_modificacion
    BEFORE UPDATE ON observaciones_sesiones
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- Trigger para calcular tardanza se define después de la función (ver línea 1314+)

-- =============================================
-- FUNCIONES DE NEGOCIO
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

-- Trigger para generar código automático de paciente
CREATE TRIGGER trigger_generar_codigo_paciente
    BEFORE INSERT ON paciente
    FOR EACH ROW
    WHEN (NEW.codigo_paciente IS NULL)
    EXECUTE FUNCTION generar_codigo_paciente();

-- Función para generar código único de sesión terapéutica
CREATE OR REPLACE FUNCTION generar_codigo_sesion_terapia()
RETURNS TRIGGER AS $$
DECLARE
    nuevo_codigo VARCHAR(20);
    max_numero INTEGER;
    anio_actual VARCHAR(4);
BEGIN
    -- Obtener año actual
    anio_actual := TO_CHAR(CURRENT_DATE, 'YYYY');

    -- Obtener el máximo número de sesión para este año
    SELECT COALESCE(MAX(
        CAST(
            SUBSTRING(codigo_sesion FROM 'ST-\d{4}-(\d+)') AS INTEGER
        )
    ), 0) INTO max_numero
    FROM sesion_terapia
    WHERE codigo_sesion LIKE 'ST-' || anio_actual || '-%';

    -- Generar nuevo código con el siguiente número
    nuevo_codigo := 'ST-' || anio_actual || '-' || LPAD((max_numero + 1)::TEXT, 4, '0');

    -- Asignar el nuevo código
    NEW.codigo_sesion := nuevo_codigo;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Función para generar código único de sesión pedagógica
CREATE OR REPLACE FUNCTION generar_codigo_sesion_pedagogica()
RETURNS TRIGGER AS $$
DECLARE
    nuevo_codigo VARCHAR(20);
    max_numero INTEGER;
    anio_actual VARCHAR(4);
BEGIN
    -- Obtener año actual
    anio_actual := TO_CHAR(CURRENT_DATE, 'YYYY');

    -- Obtener el máximo número de sesión para este año
    SELECT COALESCE(MAX(
        CAST(
            SUBSTRING(codigo_sesion FROM 'SP-\d{4}-(\d+)') AS INTEGER
        )
    ), 0) INTO max_numero
    FROM sesion_pedagogica
    WHERE codigo_sesion LIKE 'SP-' || anio_actual || '-%';

    -- Generar nuevo código con el siguiente número
    nuevo_codigo := 'SP-' || anio_actual || '-' || LPAD((max_numero + 1)::TEXT, 4, '0');

    -- Asignar el nuevo código
    NEW.codigo_sesion := nuevo_codigo;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Función para calcular costo total automáticamente
-- LÓGICA: costo_total es la fuente de verdad
CREATE OR REPLACE FUNCTION calcular_costo_total_sesion_terapia()
RETURNS TRIGGER AS $$
BEGIN
    -- Estrategia: costo_total es la fuente de verdad
    -- Si costo_total tiene un valor significativo (> 0), calcular costo_sesion desde él
    -- Si no, calcular costo_total desde costo_sesion

    IF NEW.costo_total IS NOT NULL AND NEW.costo_total > 0 THEN
        -- Hay un costo_total definido, es la fuente de verdad
        -- Recalcular costo_sesion para que sea consistente
        IF NEW.numero_sesiones_contratadas > 0 THEN
            NEW.costo_sesion := NEW.costo_total / NEW.numero_sesiones_contratadas;
        END IF;
    ELSIF NEW.costo_sesion IS NOT NULL AND NEW.costo_sesion > 0 THEN
        -- No hay costo_total pero sí costo_sesion, calcular total desde sesión
        NEW.costo_total := COALESCE(NEW.costo_sesion, 0) * COALESCE(NEW.numero_sesiones_contratadas, 0);
    ELSE
        -- No hay ninguno, dejar los defaults (probablemente 0)
        NEW.costo_total := COALESCE(NEW.costo_total, 0);
        NEW.costo_sesion := COALESCE(NEW.costo_sesion, 0);
    END IF;

    -- Si no hay título, usar objetivo_general como título por defecto
    IF NEW.titulo IS NULL OR NEW.titulo = '' THEN
        NEW.titulo := COALESCE(NEW.objetivo_general, 'Sesión de Terapia');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para generar códigos automáticos de sesiones
CREATE TRIGGER trigger_generar_codigo_sesion_terapia
    BEFORE INSERT ON sesion_terapia
    FOR EACH ROW
    WHEN (NEW.codigo_sesion IS NULL OR NEW.codigo_sesion = '')
    EXECUTE FUNCTION generar_codigo_sesion_terapia();

-- Trigger para calcular costo total automáticamente
CREATE TRIGGER trigger_calcular_costo_total_sesion_terapia
    BEFORE INSERT OR UPDATE ON sesion_terapia
    FOR EACH ROW
    EXECUTE FUNCTION calcular_costo_total_sesion_terapia();

CREATE TRIGGER trigger_generar_codigo_sesion_pedagogica
    BEFORE INSERT ON sesion_pedagogica
    FOR EACH ROW
    WHEN (NEW.codigo_sesion IS NULL OR NEW.codigo_sesion = '')
    EXECUTE FUNCTION generar_codigo_sesion_pedagogica();

-- Función para asignar especialidad principal automáticamente (Personal)
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

-- Trigger para especialidad principal del personal
CREATE TRIGGER trigger_especialidad_principal_personal
    BEFORE INSERT OR UPDATE ON personal_especialidades
    FOR EACH ROW
    EXECUTE FUNCTION asignar_especialidad_principal_personal();

-- Función para asignar especialidad principal automáticamente (Paciente)
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

-- Trigger para especialidad principal del paciente
CREATE TRIGGER trigger_especialidad_principal_paciente
    BEFORE INSERT OR UPDATE ON paciente_especialidades
    FOR EACH ROW
    EXECUTE FUNCTION asignar_especialidad_principal_paciente();

-- Función para validar que id_sesion existe según tipo_sesion (usada en observaciones_sesiones)
CREATE OR REPLACE FUNCTION validar_sesion_observacion()
RETURNS TRIGGER AS $$
BEGIN
    -- Validar que la sesión existe según el tipo
    IF NEW.tipo_sesion = 'terapeutica' THEN
        IF NOT EXISTS (SELECT 1 FROM sesion_terapia WHERE id = NEW.id_sesion) THEN
            RAISE EXCEPTION 'La sesión terapéutica con ID % no existe', NEW.id_sesion;
        END IF;
    ELSIF NEW.tipo_sesion = 'pedagogica' THEN
        IF NOT EXISTS (SELECT 1 FROM sesion_pedagogica WHERE id = NEW.id_sesion) THEN
            RAISE EXCEPTION 'La sesión pedagógica con ID % no existe', NEW.id_sesion;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para validar sesiones en observaciones (aplicado en 01.5_tablas_comunicacion.sql)
CREATE TRIGGER trigger_validar_sesion_observacion
    BEFORE INSERT OR UPDATE ON observaciones_sesiones
    FOR EACH ROW
    EXECUTE FUNCTION validar_sesion_observacion();

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

-- Función para validar y establecer el estado de asistencia automáticamente
CREATE OR REPLACE FUNCTION establecer_estado_asistencia()
RETURNS TRIGGER AS $$
BEGIN
    -- Si no se especifica estado_asistencia, calcularlo automáticamente
    IF NEW.estado_asistencia IS NULL OR NEW.estado_asistencia = 'pendiente' THEN
        IF NEW.asistio = TRUE THEN
            IF NEW.llegada_tardanza_minutos > 0 THEN
                NEW.estado_asistencia := 'tarde';
            ELSE
                NEW.estado_asistencia := 'presente';
            END IF;
        ELSE
            NEW.estado_asistencia := 'ausente';
        END IF;
    END IF;

    -- Asegurar que llegada_tardanza_minutos no sea NULL
    IF NEW.llegada_tardanza_minutos IS NULL THEN
        NEW.llegada_tardanza_minutos := 0;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para establecer el estado de asistencia automáticamente (sesiones terapéuticas)
CREATE TRIGGER trigger_estado_asistencia
    BEFORE INSERT OR UPDATE ON asistencia_sesiones
    FOR EACH ROW
    EXECUTE FUNCTION establecer_estado_asistencia();

-- Trigger para establecer el estado de asistencia automáticamente (clases pedagógicas)
CREATE TRIGGER trigger_estado_asistencia_clases
    BEFORE INSERT OR UPDATE ON asistencia_clases
    FOR EACH ROW
    EXECUTE FUNCTION establecer_estado_asistencia();

-- =============================================
-- COMENTARIOS EN TABLAS
-- =============================================

COMMENT ON TABLE centros IS 'Catálogo de centros de atención (Norte/Sur)';
COMMENT ON TABLE rol IS 'Catálogo de roles del sistema';
COMMENT ON TABLE persona IS 'Información demográfica base de todas las personas';
COMMENT ON TABLE usuario IS 'Credenciales y configuración de usuarios del sistema';
COMMENT ON TABLE especialidad IS 'Catálogo de especialidades médicas/terapéuticas';
COMMENT ON TABLE personal IS 'Información del personal del centro';
COMMENT ON TABLE personal_especialidades IS 'Especialidades múltiples asignadas al personal';
COMMENT ON TABLE documentos_personal IS 'Documentos digitales del personal con validación administrativa';
COMMENT ON TABLE tutor IS 'Información de tutores/responsables de pacientes';
COMMENT ON TABLE paciente IS 'Información de pacientes del centro';
COMMENT ON TABLE paciente_especialidades IS 'Especialidades múltiples asignadas a cada paciente';
COMMENT ON TABLE documentos_paciente IS 'Documentos digitales de los pacientes';
COMMENT ON TABLE sesion_terapia IS 'Configuración y gestión de sesiones terapéuticas';
COMMENT ON TABLE sesion_paciente IS 'Inscripción de pacientes en sesiones terapéuticas';
COMMENT ON TABLE cronograma_sesiones IS 'Programación de citas individuales de terapia';
COMMENT ON TABLE asistencia_sesiones IS 'Registro de asistencia y progreso en sesiones terapéuticas';
COMMENT ON COLUMN asistencia_sesiones.llegada_tardanza_minutos IS 'Minutos de tardanza del paciente (manual con prioridad, o calculado automáticamente)';
COMMENT ON COLUMN cronograma_sesiones.fecha_realizacion IS 'Fecha y hora cuando se marcó la sesión como completada';
COMMENT ON TABLE sesion_pedagogica IS 'Configuración y gestión de sesiones pedagógicas/educativas';
COMMENT ON TABLE sesion_estudiante IS 'Inscripción de pacientes como estudiantes en sesiones pedagógicas';
COMMENT ON TABLE cronograma_clases IS 'Programación de clases pedagógicas';
COMMENT ON TABLE asistencia_clases IS 'Registro de asistencia y evaluación en clases pedagógicas';
COMMENT ON TABLE tokens_publicos_sesion IS 'Enlaces públicos para compartir sesiones terapéuticas sin autenticación';
COMMENT ON TABLE tokens_publicos_sesion_pedagogica IS 'Enlaces públicos para compartir sesiones pedagógicas sin autenticación';
COMMENT ON TABLE mensajes_chat IS 'Sistema de mensajería interna entre usuarios del centro';
COMMENT ON TABLE observaciones_sesiones IS 'Observaciones y notas sobre sesiones terapéuticas y pedagógicas';


-- =============================================
-- SISTEMA DE NOTIFICACIONES PUSH
-- =============================================

-- Eliminar tablas si existen
DROP TABLE IF EXISTS notificaciones_push CASCADE;
DROP TABLE IF EXISTS configuracion_notificaciones_push CASCADE;

-- =============================================
-- TABLA: CONFIGURACION_NOTIFICACIONES_PUSH
-- =============================================
CREATE TABLE configuracion_notificaciones_push (
    id INTEGER PRIMARY KEY DEFAULT 1,

    -- Configuración general
    notificaciones_habilitadas BOOLEAN DEFAULT TRUE,

    -- Configuración de sesiones terapéuticas
    notificar_sesiones_terapia BOOLEAN DEFAULT TRUE,
    minutos_previos_sesion_terapia INTEGER DEFAULT 15,

    -- Configuración de clases pedagógicas
    notificar_clases_pedagogicas BOOLEAN DEFAULT TRUE,
    minutos_previos_clase_pedagogica INTEGER DEFAULT 15,

    -- Configuración de cancelaciones y reprogramaciones
    notificar_cancelaciones BOOLEAN DEFAULT TRUE,
    notificar_reprogramaciones BOOLEAN DEFAULT TRUE,

    -- Configuración de mensajes de chat
    notificar_mensajes_chat BOOLEAN DEFAULT TRUE,
    notificar_solo_mensajes_urgentes BOOLEAN DEFAULT FALSE,

    -- Configuración de horarios de silencio
    horario_silencio_inicio TIME DEFAULT '22:00:00',
    horario_silencio_fin TIME DEFAULT '07:00:00',

    -- Configuración de frecuencia de verificación
    intervalo_verificacion_minutos INTEGER DEFAULT 1,

    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- Insertar configuración por defecto
INSERT INTO configuracion_notificaciones_push DEFAULT VALUES;

-- =============================================
-- TABLA: NOTIFICACIONES_PUSH
-- =============================================
CREATE TABLE notificaciones_push (
    id SERIAL PRIMARY KEY,

    -- Usuario destinatario
    id_usuario INTEGER NOT NULL,
    id_centro INTEGER NOT NULL,

    -- Contenido de la notificación
    titulo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,

    -- Tipo de notificación
    tipo_notificacion VARCHAR(30) NOT NULL CHECK (tipo_notificacion IN (
        'sesion_terapia', 'clase_pedagogica', 'cancelacion',
        'reprogramacion', 'mensaje_chat', 'recordatorio_general'
    )),

    -- Prioridad
    prioridad VARCHAR(10) DEFAULT 'normal' CHECK (prioridad IN ('baja', 'normal', 'alta', 'urgente')),

    -- Estado de envío
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN (
        'pendiente', 'enviada', 'leida', 'expirada', 'fallida'
    )),

    -- Información de contexto (JSON)
    contexto JSONB,

    -- URL de acción (opcional)
    url_accion VARCHAR(255),

    -- Control de tiempo
    fecha_programada TIMESTAMP NOT NULL,
    fecha_envio TIMESTAMP,
    fecha_lectura TIMESTAMP,
    fecha_expiracion TIMESTAMP,

    -- Intentos de envío
    intentos_envio INTEGER DEFAULT 0,
    max_intentos INTEGER DEFAULT 3,
    ultimo_error TEXT,

    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,

    -- Claves foráneas
    CONSTRAINT fk_notif_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE CASCADE,
    CONSTRAINT fk_notif_centro FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE CASCADE
);

-- =============================================
-- ÍNDICES ADICIONALES PARA NOTIFICACIONES
-- =============================================

-- Índices para búsquedas frecuentes
CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON notificaciones_push(id_usuario);
CREATE INDEX IF NOT EXISTS idx_notificaciones_centro ON notificaciones_push(id_centro);
CREATE INDEX IF NOT EXISTS idx_notificaciones_estado ON notificaciones_push(estado);
CREATE INDEX IF NOT EXISTS idx_notificaciones_tipo ON notificaciones_push(tipo_notificacion);
CREATE INDEX IF NOT EXISTS idx_notificaciones_fecha_programada ON notificaciones_push(fecha_programada);

-- Índice compuesto para el job scheduler
CREATE INDEX IF NOT EXISTS idx_notificaciones_pendientes ON notificaciones_push(estado, fecha_programada)
WHERE estado = 'pendiente';

-- Índice para notificaciones por usuario y estado
CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_estado ON notificaciones_push(id_usuario, estado, fecha_programada);

-- =============================================
-- TRIGGERS ADICIONALES PARA NOTIFICACIONES
-- =============================================

-- Trigger para actualizar fecha_modificacion en configuracion_notificaciones_push
CREATE OR REPLACE FUNCTION trigger_notif_config_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_configuracion_notificaciones_push_fecha_modificacion
    BEFORE UPDATE ON configuracion_notificaciones_push
    FOR EACH ROW
    EXECUTE FUNCTION trigger_notif_config_fecha_modificacion();

-- Trigger para actualizar fecha_modificacion en notificaciones_push
CREATE OR REPLACE FUNCTION trigger_notif_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_notificaciones_push_fecha_modificacion
    BEFORE UPDATE ON notificaciones_push
    FOR EACH ROW
    EXECUTE FUNCTION trigger_notif_fecha_modificacion();

-- =============================================
-- FUNCIONES AUXILIARES PARA NOTIFICACIONES
-- =============================================

-- Función para verificar si está en horario de silencio
CREATE OR REPLACE FUNCTION esta_en_horario_silencio()
RETURNS BOOLEAN AS $$
DECLARE
    config RECORD;
    hora_actual TIME;
BEGIN
    SELECT horario_silencio_inicio, horario_silencio_fin
    INTO config
    FROM configuracion_notificaciones_push
    WHERE id = 1;

    hora_actual := CURRENT_TIME;

    -- Si el horario de silencio cruza medianoche
    IF config.horario_silencio_inicio > config.horario_silencio_fin THEN
        RETURN hora_actual >= config.horario_silencio_inicio OR hora_actual <= config.horario_silencio_fin;
    ELSE
        RETURN hora_actual >= config.horario_silencio_inicio AND hora_actual <= config.horario_silencio_fin;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Función para limpiar notificaciones expiradas
CREATE OR REPLACE FUNCTION limpiar_notificaciones_expiradas()
RETURNS INTEGER AS $$
DECLARE
    notificaciones_eliminadas INTEGER;
BEGIN
    -- Marcar como expiradas las notificaciones pendientes que han superado su fecha de expiración
    UPDATE notificaciones_push
    SET estado = 'expirada',
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE estado = 'pendiente'
        AND fecha_expiracion IS NOT NULL
        AND fecha_expiracion < CURRENT_TIMESTAMP;

    GET DIAGNOSTICS notificaciones_eliminadas = ROW_COUNT;

    -- Eliminar físicamente notificaciones expiradas o leídas de más de 30 días
    DELETE FROM notificaciones_push
    WHERE estado IN ('expirada', 'leida')
        AND fecha_modificacion < CURRENT_TIMESTAMP - INTERVAL '30 days';

    RETURN notificaciones_eliminadas;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- COMENTARIOS ADICIONALES
-- =============================================

COMMENT ON TABLE configuracion_notificaciones_push IS 'Configuración global del sistema de notificaciones push';
COMMENT ON TABLE notificaciones_push IS 'Cola de notificaciones push para usuarios del sistema';

COMMENT ON COLUMN notificaciones_push.contexto IS 'Información adicional en formato JSON (IDs de sesiones, etc.)';
COMMENT ON COLUMN notificaciones_push.url_accion IS 'URL para redireccionar cuando el usuario hace clic en la notificación';
COMMENT ON COLUMN notificaciones_push.fecha_programada IS 'Momento en que debe enviarse la notificación';
COMMENT ON COLUMN notificaciones_push.fecha_expiracion IS 'Momento después del cual la notificación ya no es relevante';

-- =============================================
-- DATOS INICIALES DE CONFIGURACIÓN
-- =============================================

-- Verificar que la configuración por defecto existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM configuracion_notificaciones_push WHERE id = 1) THEN
        INSERT INTO configuracion_notificaciones_push (
            notificaciones_habilitadas,
            notificar_sesiones_terapia,
            minutos_previos_sesion_terapia,
            notificar_clases_pedagogicas,
            minutos_previos_clase_pedagogica,
            notificar_cancelaciones,
            notificar_reprogramaciones,
            notificar_mensajes_chat,
            notificar_solo_mensajes_urgentes,
            horario_silencio_inicio,
            horario_silencio_fin,
            intervalo_verificacion_minutos
        ) VALUES (
            TRUE,    -- notificaciones_habilitadas
            TRUE,    -- notificar_sesiones_terapia
            15,      -- minutos_previos_sesion_terapia
            TRUE,    -- notificar_clases_pedagogicas
            15,      -- minutos_previos_clase_pedagogica
            TRUE,    -- notificar_cancelaciones
            TRUE,    -- notificar_reprogramaciones
            TRUE,    -- notificar_mensajes_chat
            FALSE,   -- notificar_solo_mensajes_urgentes
            '22:00:00', -- horario_silencio_inicio
            '07:00:00', -- horario_silencio_fin
            1        -- intervalo_verificacion_minutos
        );
    END IF;
END $$;

-- =============================================
-- TABLA DE HISTORIAL DE PAUSAS
-- =============================================

CREATE TABLE IF NOT EXISTS historial_pausas (
    id SERIAL PRIMARY KEY,
    id_paciente INTEGER NOT NULL,
    id_especialidad INTEGER,
    tipo_pausa VARCHAR(20) NOT NULL CHECK (tipo_pausa IN ('general', 'especialidad')),
    accion VARCHAR(20) NOT NULL CHECK (accion IN ('pausar', 'reanudar')),
    fecha_inicio_pausa DATE,
    fecha_fin_pausa DATE,
    motivo TEXT,
    observaciones TEXT,
    fecha_accion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_accion INTEGER,
    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE CASCADE,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE SET NULL,
    FOREIGN KEY (usuario_accion) REFERENCES usuario(id) ON DELETE SET NULL
);

-- Indices para mejorar el rendimiento de historial_pausas
CREATE INDEX IF NOT EXISTS idx_historial_pausas_paciente ON historial_pausas(id_paciente);
CREATE INDEX IF NOT EXISTS idx_historial_pausas_especialidad ON historial_pausas(id_especialidad);
CREATE INDEX IF NOT EXISTS idx_historial_pausas_fecha_accion ON historial_pausas(fecha_accion);
CREATE INDEX IF NOT EXISTS idx_historial_pausas_tipo_pausa ON historial_pausas(tipo_pausa);
CREATE INDEX IF NOT EXISTS idx_historial_pausas_accion ON historial_pausas(accion);

-- Indices adicionales para optimizar consultas de pausas
CREATE INDEX IF NOT EXISTS idx_paciente_fecha_inicio_pausa ON paciente(fecha_inicio_pausa) WHERE fecha_inicio_pausa IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_paciente_fecha_fin_pausa ON paciente(fecha_fin_pausa) WHERE fecha_fin_pausa IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_paciente_especialidades_estado_pausa ON paciente_especialidades(estado_pausa);
CREATE INDEX IF NOT EXISTS idx_paciente_especialidades_fecha_pausa ON paciente_especialidades(fecha_inicio_pausa_esp) WHERE fecha_inicio_pausa_esp IS NOT NULL;

-- Comentarios en la tabla historial_pausas
COMMENT ON TABLE historial_pausas IS 'Historial completo de pausas y reactivaciones de pacientes';
COMMENT ON COLUMN historial_pausas.id_paciente IS 'ID del paciente afectado';
COMMENT ON COLUMN historial_pausas.id_especialidad IS 'ID de la especialidad (NULL si es pausa general)';
COMMENT ON COLUMN historial_pausas.tipo_pausa IS 'Tipo de pausa: general o especialidad';
COMMENT ON COLUMN historial_pausas.accion IS 'Accion realizada: pausar o reanudar';
COMMENT ON COLUMN historial_pausas.fecha_inicio_pausa IS 'Fecha de inicio de la pausa';
COMMENT ON COLUMN historial_pausas.fecha_fin_pausa IS 'Fecha de fin de la pausa (puede ser NULL)';
COMMENT ON COLUMN historial_pausas.motivo IS 'Motivo de la pausa';
COMMENT ON COLUMN historial_pausas.observaciones IS 'Observaciones adicionales';
COMMENT ON COLUMN historial_pausas.fecha_accion IS 'Fecha y hora en que se realizo la accion';
COMMENT ON COLUMN historial_pausas.usuario_accion IS 'Usuario que realizo la accion';

-- =====================================================
-- TRIGGER: Actualizacion automatica de estado de sesion
-- =====================================================
-- Este trigger actualiza automaticamente el estado de una sesion de terapia
-- a 'finalizada' cuando todos sus cronogramas estan completados.
--
-- Se ejecuta despues de cada actualizacion en cronograma_sesiones
-- cuando un cronograma cambia a estado 'completada'.
-- =====================================================

-- Eliminar trigger y funcion si ya existen (para poder recrearlos)
DROP TRIGGER IF EXISTS trigger_actualizar_estado_sesion ON cronograma_sesiones;
DROP FUNCTION IF EXISTS actualizar_estado_sesion_terapia();

-- =====================================================
-- FUNCION: actualizar_estado_sesion_terapia
-- =====================================================
CREATE OR REPLACE FUNCTION actualizar_estado_sesion_terapia()
RETURNS TRIGGER AS $$
DECLARE
    v_sesion_id INTEGER;
    v_total_cronogramas INTEGER;
    v_cronogramas_completados INTEGER;
    v_estado_actual VARCHAR(20);
BEGIN
    -- Obtener el ID de la sesion del cronograma actualizado
    v_sesion_id := NEW.id_sesion;

    -- Obtener el estado actual de la sesion
    SELECT estado INTO v_estado_actual
    FROM sesion_terapia
    WHERE id = v_sesion_id;

    -- Solo proceder si la sesion no esta ya finalizada o cancelada
    IF v_estado_actual NOT IN ('finalizada', 'cancelada') THEN

        -- Contar total de cronogramas de esta sesion
        -- (excluyendo los cancelados y reprogramados que no cuentan para el total)
        SELECT COUNT(*) INTO v_total_cronogramas
        FROM cronograma_sesiones
        WHERE id_sesion = v_sesion_id
          AND estado NOT IN ('cancelada', 'reprogramada');

        -- Contar cronogramas completados
        SELECT COUNT(*) INTO v_cronogramas_completados
        FROM cronograma_sesiones
        WHERE id_sesion = v_sesion_id
          AND estado = 'completada';

        -- Verificar si todos los cronogramas validos estan completados
        IF v_total_cronogramas > 0 AND v_cronogramas_completados = v_total_cronogramas THEN

            -- Actualizar el estado de la sesion a 'finalizada'
            UPDATE sesion_terapia
            SET estado = 'finalizada',
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = v_sesion_id;

            -- Mensaje de log (opcional, para debug en PostgreSQL)
            RAISE NOTICE 'Sesion % marcada como finalizada automaticamente (% de % cronogramas completados)',
                v_sesion_id, v_cronogramas_completados, v_total_cronogramas;
        END IF;

    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGER: trigger_actualizar_estado_sesion
-- =====================================================
-- Se ejecuta DESPUES de cada UPDATE en cronograma_sesiones
-- Solo cuando el estado cambia a 'completada'
CREATE TRIGGER trigger_actualizar_estado_sesion
    AFTER UPDATE ON cronograma_sesiones
    FOR EACH ROW
    WHEN (NEW.estado = 'completada' AND OLD.estado != 'completada')
    EXECUTE FUNCTION actualizar_estado_sesion_terapia();

-- =====================================================
-- COMENTARIOS
-- =====================================================
COMMENT ON FUNCTION actualizar_estado_sesion_terapia() IS
'Funcion que actualiza automaticamente el estado de una sesion de terapia a finalizada cuando todos sus cronogramas estan completados';

COMMENT ON TRIGGER trigger_actualizar_estado_sesion ON cronograma_sesiones IS
'Trigger que ejecuta la actualizacion automatica del estado de sesion cuando un cronograma se marca como completada';

-- =====================================================
-- TRIGGER: Actualizacion automatica de estado de sesion pedagogica
-- =====================================================
-- Este trigger actualiza automaticamente el estado de una sesion pedagogica
-- a 'finalizada' cuando todas sus clases del cronograma estan completadas.
--
-- Se ejecuta despues de cada INSERT, UPDATE o DELETE en cronograma_clases
-- cuando todas las clases tienen estado 'realizada'.
-- =====================================================

-- Eliminar trigger y funcion si ya existen (para poder recrearlos)
DROP TRIGGER IF EXISTS trigger_actualizar_estado_sesion_pedagogica ON cronograma_clases;
DROP FUNCTION IF EXISTS actualizar_estado_sesion_pedagogica();

-- =====================================================
-- FUNCION: actualizar_estado_sesion_pedagogica
-- =====================================================
CREATE OR REPLACE FUNCTION actualizar_estado_sesion_pedagogica()
RETURNS TRIGGER AS $$
DECLARE
    total_clases INTEGER;
    clases_completadas INTEGER;
    sesion_id_actual INTEGER;
    estado_actual VARCHAR(50);
BEGIN
    -- Obtener el ID de la sesion (NEW para INSERT/UPDATE, OLD para DELETE)
    IF TG_OP = 'DELETE' THEN
        sesion_id_actual := OLD.id_sesion;
    ELSE
        sesion_id_actual := NEW.id_sesion;
    END IF;

    -- Obtener el estado actual de la sesion
    SELECT estado INTO estado_actual
    FROM sesion_pedagogica
    WHERE id = sesion_id_actual;

    -- Solo proceder si la sesion no esta cancelada o ya finalizada
    IF estado_actual NOT IN ('cancelada', 'finalizada') THEN
        -- Contar total de clases programadas para esta sesion
        SELECT COUNT(*) INTO total_clases
        FROM cronograma_clases
        WHERE id_sesion = sesion_id_actual;

        -- Contar clases completadas (estado = 'realizada')
        SELECT COUNT(*) INTO clases_completadas
        FROM cronograma_clases
        WHERE id_sesion = sesion_id_actual
          AND estado = 'realizada';

        -- Si todas las clases estan completadas y hay al menos una clase
        IF total_clases > 0 AND clases_completadas = total_clases THEN
            -- Actualizar el estado de la sesion a 'finalizada'
            UPDATE sesion_pedagogica
            SET estado = 'finalizada',
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = sesion_id_actual;

            RAISE NOTICE 'Sesion pedagogica % finalizada automaticamente: % de % clases completadas',
                         sesion_id_actual, clases_completadas, total_clases;
        END IF;
    END IF;

    -- Retornar el registro apropiado segun la operacion
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGER: trigger_actualizar_estado_sesion_pedagogica
-- =====================================================
-- Se ejecuta DESPUES de cada INSERT, UPDATE o DELETE en cronograma_clases
CREATE TRIGGER trigger_actualizar_estado_sesion_pedagogica
AFTER INSERT OR UPDATE OR DELETE ON cronograma_clases
FOR EACH ROW
EXECUTE FUNCTION actualizar_estado_sesion_pedagogica();

-- =====================================================
-- COMENTARIOS
-- =====================================================
COMMENT ON FUNCTION actualizar_estado_sesion_pedagogica() IS
'Funcion que verifica si todas las clases de una sesion pedagogica estan completadas y actualiza el estado de la sesion a finalizada';

COMMENT ON TRIGGER trigger_actualizar_estado_sesion_pedagogica ON cronograma_clases IS
'Trigger que actualiza automaticamente el estado de una sesion pedagogica a finalizada cuando todas sus clases estan completadas';

-- =============================================
-- SISTEMA MULTI-CENTRO PARA USUARIOS
-- =============================================

-- Crear tabla de relacion usuario-centros
CREATE TABLE IF NOT EXISTS usuario_centros (
    id SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    id_centro INTEGER NOT NULL,

    -- Control de centro predeterminado
    es_centro_predeterminado BOOLEAN DEFAULT FALSE,

    -- Auditoría
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,

    -- Claves foráneas
    FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE CASCADE,

    -- Constraint para evitar duplicados
    UNIQUE(id_usuario, id_centro)
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_usuario_centros_usuario ON usuario_centros(id_usuario);
CREATE INDEX IF NOT EXISTS idx_usuario_centros_centro ON usuario_centros(id_centro);
CREATE INDEX IF NOT EXISTS idx_usuario_centros_predeterminado ON usuario_centros(id_usuario, es_centro_predeterminado);

-- Trigger para actualizar fecha_modificacion
CREATE TRIGGER trigger_usuario_centros_fecha_modificacion
    BEFORE UPDATE ON usuario_centros
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- Comentarios
COMMENT ON TABLE usuario_centros IS 'Relacion de usuarios con multiples centros de atencion';
COMMENT ON COLUMN usuario_centros.es_centro_predeterminado IS 'Indica si este es el centro predeterminado del usuario al iniciar sesion';

-- Funcion para obtener centros de un usuario
CREATE OR REPLACE FUNCTION get_centros_usuario(p_id_usuario INTEGER)
RETURNS TABLE (
    id INTEGER,
    nombre VARCHAR(100),
    codigo VARCHAR(10),
    direccion VARCHAR(255),
    telefono VARCHAR(15),
    es_predeterminado BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.nombre,
        c.codigo,
        c.direccion,
        c.telefono,
        uc.es_centro_predeterminado as es_predeterminado
    FROM usuario_centros uc
    INNER JOIN centros c ON uc.id_centro = c.id
    WHERE uc.id_usuario = p_id_usuario
    AND c.estado = 'activo'
    ORDER BY uc.es_centro_predeterminado DESC, c.nombre ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_centros_usuario(INTEGER) IS 'Obtiene la lista de centros disponibles para un usuario';

-- Funcion para validar acceso a centro
CREATE OR REPLACE FUNCTION validar_acceso_centro(
    p_id_usuario INTEGER,
    p_id_centro INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_tiene_acceso BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1
        FROM usuario_centros
        WHERE id_usuario = p_id_usuario
        AND id_centro = p_id_centro
    ) INTO v_tiene_acceso;

    RETURN v_tiene_acceso;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validar_acceso_centro(INTEGER, INTEGER) IS 'Valida si un usuario tiene acceso a un centro especifico';

-- Funcion para establecer centro predeterminado
CREATE OR REPLACE FUNCTION establecer_centro_predeterminado(
    p_id_usuario INTEGER,
    p_id_centro INTEGER
) RETURNS BOOLEAN AS $$
BEGIN
    IF NOT validar_acceso_centro(p_id_usuario, p_id_centro) THEN
        RAISE EXCEPTION 'El usuario no tiene acceso al centro especificado';
    END IF;

    UPDATE usuario_centros
    SET es_centro_predeterminado = FALSE
    WHERE id_usuario = p_id_usuario;

    UPDATE usuario_centros
    SET es_centro_predeterminado = TRUE
    WHERE id_usuario = p_id_usuario
    AND id_centro = p_id_centro;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION establecer_centro_predeterminado(INTEGER, INTEGER) IS 'Establece el centro predeterminado para un usuario';

-- Trigger para garantizar un centro predeterminado
CREATE OR REPLACE FUNCTION garantizar_centro_predeterminado()
RETURNS TRIGGER AS $$
DECLARE
    v_count_centros INTEGER;
    v_count_predeterminados INTEGER;
BEGIN
    IF TG_OP = 'INSERT' THEN
        SELECT COUNT(*) INTO v_count_centros
        FROM usuario_centros
        WHERE id_usuario = NEW.id_usuario;

        IF v_count_centros = 1 THEN
            NEW.es_centro_predeterminado = TRUE;
        END IF;

        IF NEW.es_centro_predeterminado = TRUE THEN
            UPDATE usuario_centros
            SET es_centro_predeterminado = FALSE
            WHERE id_usuario = NEW.id_usuario
            AND id != NEW.id;
        END IF;
    END IF;

    IF TG_OP = 'UPDATE' AND OLD.es_centro_predeterminado = TRUE AND NEW.es_centro_predeterminado = FALSE THEN
        SELECT COUNT(*) INTO v_count_predeterminados
        FROM usuario_centros
        WHERE id_usuario = NEW.id_usuario
        AND es_centro_predeterminado = TRUE
        AND id != NEW.id;

        IF v_count_predeterminados = 0 THEN
            NEW.es_centro_predeterminado = TRUE;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_garantizar_centro_predeterminado
    BEFORE INSERT OR UPDATE ON usuario_centros
    FOR EACH ROW
    EXECUTE FUNCTION garantizar_centro_predeterminado();

COMMENT ON FUNCTION garantizar_centro_predeterminado() IS 'Garantiza que cada usuario tenga al menos un centro predeterminado';

-- =============================================
-- FINALIZACIÓN
-- =============================================

-- Verificar que la estructura fue creada correctamente
DO $$
BEGIN
    RAISE NOTICE 'Estructura de base de datos creada exitosamente';
    RAISE NOTICE 'Tablas creadas: %', (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public');
    RAISE NOTICE 'Funciones creadas: %', (SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema = 'public');
    RAISE NOTICE 'Triggers creados: %', (SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema = 'public');
END $$;