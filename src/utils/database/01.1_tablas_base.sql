-- =============================================
-- CENTRO TÍA GLENDA - TABLAS BASE DEL SISTEMA
-- Archivo: 01.1_tablas_base.sql
-- Descripción: Tablas fundamentales del sistema
-- =============================================

-- =============================================
-- 1. TABLA: CENTROS (Centros de atención)
-- =============================================
CREATE TABLE IF NOT EXISTS centros (
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

-- =============================================
-- 2. TABLA: ROL (Catálogo de roles)
-- =============================================
CREATE TABLE IF NOT EXISTS rol (
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
-- 3. TABLA: PERSONA (Información demográfica base)
-- =============================================
CREATE TABLE IF NOT EXISTS persona (
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
-- 4. TABLA: USUARIO (Credenciales del sistema)
-- =============================================
CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasenia VARCHAR(255) NOT NULL,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'bloqueado')),
    
    -- Información de perfil
    foto_perfil VARCHAR(500), -- Ruta del archivo de foto de perfil
    
    persona_id INTEGER NOT NULL,
    rol_id INTEGER NOT NULL,
    id_centro INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_ultimo_acceso TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (rol_id) REFERENCES rol(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- =============================================
-- 5. TABLA: ESPECIALIDAD (Catálogo de especialidades)
-- =============================================
CREATE TABLE IF NOT EXISTS especialidad (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =============================================
CREATE INDEX IF NOT EXISTS idx_persona_cedula ON persona(cedula);
CREATE INDEX IF NOT EXISTS idx_usuario_usuario ON usuario(usuario);
CREATE INDEX IF NOT EXISTS idx_usuario_centro ON usuario(id_centro);
CREATE INDEX IF NOT EXISTS idx_especialidad_nombre ON especialidad(nombre);

-- =============================================
-- TRIGGERS PARA AUDITORÍA
-- =============================================

-- Función para actualizar fecha_modificacion
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para las tablas base
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

-- =============================================
-- COMENTARIOS EN TABLAS
-- =============================================
COMMENT ON TABLE centros IS 'Catálogo de centros de atención (Norte/Sur)';
COMMENT ON TABLE rol IS 'Catálogo de roles del sistema';
COMMENT ON TABLE persona IS 'Información demográfica base de todas las personas';
COMMENT ON TABLE usuario IS 'Credenciales y configuración de usuarios del sistema';
COMMENT ON TABLE especialidad IS 'Catálogo de especialidades médicas/terapéuticas';