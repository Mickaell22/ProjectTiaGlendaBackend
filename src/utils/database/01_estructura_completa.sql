-- =============================================
-- CENTRO TÍA GLENDA - ESTRUCTURA COMPLETA DE BASE DE DATOS
-- Archivo: 01_estructura_completa.sql
-- Descripción: Creación completa de todas las tablas, funciones y triggers
-- =============================================

-- =============================================
-- CONFIGURACIÓN INICIAL
-- =============================================

-- Eliminar tablas existentes en orden correcto (si existen)
DROP TABLE IF EXISTS asistencia_clases CASCADE;
DROP TABLE IF EXISTS cronograma_clases CASCADE;
DROP TABLE IF EXISTS sesion_estudiante CASCADE;
DROP TABLE IF EXISTS asistencia_sesiones CASCADE;
DROP TABLE IF EXISTS cronograma_sesiones CASCADE;
DROP TABLE IF EXISTS sesion_paciente CASCADE;
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
    nombre VARCHAR(100) UNIQUE NOT NULL,
    area VARCHAR(100) NOT NULL CHECK (area IN ('Especialidad terapéutica', 'Especialidad pedagógica')),
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
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
    grado_escolar VARCHAR(20),
    materia VARCHAR(100),
    competencias_objetivo TEXT,
    metodologia_ensenanza TEXT,
    
    -- Programación
    duracion_minutos INTEGER DEFAULT 60 CHECK (duracion_minutos > 0),
    frecuencia_semanal INTEGER DEFAULT 2 CHECK (frecuencia_semanal > 0 AND frecuencia_semanal <= 7),
    dias_semana TEXT[] CHECK (array_length(dias_semana, 1) > 0), -- Array: ['martes', 'jueves']
    hora_inicio TIME DEFAULT '09:00',
    hora_fin TIME DEFAULT '10:00',
    aula VARCHAR(50),
    capacidad_maxima INTEGER DEFAULT 8 CHECK (capacidad_maxima > 0),
    
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

-- 20. TABLA: ASISTENCIA_CLASES (Registro de asistencia pedagógica)
CREATE TABLE asistencia_clases (
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
-- TABLAS DE COMUNICACIÓN
-- =============================================

-- 21. TABLA: MENSAJES_CHAT (Sistema de chat interno)
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

-- 22. TABLA: OBSERVACIONES_SESIONES (Observaciones de sesiones)
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

-- Triggers para comunicación
CREATE TRIGGER trigger_mensajes_chat_fecha_modificacion
    BEFORE UPDATE ON mensajes_chat
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_observaciones_sesiones_fecha_modificacion
    BEFORE UPDATE ON observaciones_sesiones
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

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

-- Función para calcular costo total automáticamente
CREATE OR REPLACE FUNCTION calcular_costo_total_sesion_terapia()
RETURNS TRIGGER AS $$
BEGIN
    -- Calcular costo total basado en costo por sesión y número de sesiones contratadas
    NEW.costo_total := COALESCE(NEW.costo_sesion, 0) * COALESCE(NEW.numero_sesiones_contratadas, 0);
    
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
COMMENT ON TABLE sesion_pedagogica IS 'Configuración y gestión de sesiones pedagógicas/educativas';
COMMENT ON TABLE sesion_estudiante IS 'Inscripción de pacientes como estudiantes en sesiones pedagógicas';
COMMENT ON TABLE cronograma_clases IS 'Programación de clases pedagógicas';
COMMENT ON TABLE asistencia_clases IS 'Registro de asistencia y evaluación en clases pedagógicas';
COMMENT ON TABLE mensajes_chat IS 'Sistema de mensajería interna entre usuarios del centro';
COMMENT ON TABLE observaciones_sesiones IS 'Observaciones y notas sobre sesiones terapéuticas y pedagógicas';


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