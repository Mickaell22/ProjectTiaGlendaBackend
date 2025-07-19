-- =============================================
-- BASE DE DATOS CENTRO TIA GLENDA - PostgreSQL
-- =============================================

-- Crear base de datos
DROP DATABASE IF EXISTS centro_tia_glenda;
CREATE DATABASE centro_tia_glenda 
WITH ENCODING 'UTF8' 
LC_COLLATE = 'es_ES.UTF-8' 
LC_CTYPE = 'es_ES.UTF-8';

\c centro_tia_glenda;

-- =============================================
-- TABLA: ROL (Se crea primero para las relaciones)
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
-- TABLA: PERSONA
-- =============================================
CREATE TABLE persona (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    correo VARCHAR(150) UNIQUE,
    fecha_nacimiento DATE,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- =============================================
-- TABLA: USUARIO
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
    
    -- Claves foráneas principales
    FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (rol_id) REFERENCES rol(id) ON DELETE RESTRICT
);

-- =============================================
-- FUNCIÓN PARA ACTUALIZAR fecha_modificacion
-- =============================================
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear triggers para actualización automática
CREATE TRIGGER trigger_persona_fecha_modificacion
    BEFORE UPDATE ON persona
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_rol_fecha_modificacion
    BEFORE UPDATE ON rol
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_usuario_fecha_modificacion
    BEFORE UPDATE ON usuario
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();
-- =============================================
-- CLAVES FORÁNEAS DE AUDITORÍA
-- =============================================
ALTER TABLE persona 
ADD CONSTRAINT fk_persona_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE persona 
ADD CONSTRAINT fk_persona_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE rol 
ADD CONSTRAINT fk_rol_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE rol 
ADD CONSTRAINT fk_rol_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE usuario 
ADD CONSTRAINT fk_usuario_usuario_creacion 
FOREIGN KEY (usuario_creacion) REFERENCES usuario(id) ON DELETE SET NULL;

ALTER TABLE usuario 
ADD CONSTRAINT fk_usuario_usuario_modificacion 
FOREIGN KEY (usuario_modificacion) REFERENCES usuario(id) ON DELETE SET NULL;

-- =============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =============================================
CREATE INDEX idx_persona_cedula ON persona(cedula);
CREATE INDEX idx_persona_correo ON persona(correo);
CREATE INDEX idx_persona_estado ON persona(estado);
CREATE INDEX idx_usuario_persona ON usuario(persona_id);
CREATE INDEX idx_usuario_rol ON usuario(rol_id);
CREATE INDEX idx_usuario_nombre ON usuario(usuario);
CREATE INDEX idx_usuario_estado ON usuario(estado);
CREATE INDEX idx_rol_nombre ON rol(nombre);
CREATE INDEX idx_rol_estado ON rol(estado);

-- =============================================
-- DATOS INICIALES - ROLES
-- =============================================
INSERT INTO rol (nombre, descripcion) VALUES 
('Administrador', 'Acceso completo al sistema. Puede gestionar usuarios, configuraciones y generar todos los reportes'),
('Terapeuta', 'Personal del área terapéutica. Acceso a gestión de pacientes y tratamientos'),
('Pedagógico', 'Personal del área pedagógica. Acceso a gestión de alumnos y seguimiento académico'),
('Cliente', 'Cliente externo. Solo consulta de información pública e horarios disponibles');

-- =============================================
-- DATOS INICIALES - PERSONA ADMINISTRADOR
-- =============================================
INSERT INTO persona (
    nombre, 
    apellido, 
    cedula, 
    telefono, 
    correo, 
    fecha_nacimiento, 
    estado
) VALUES (
    'Admin',
    'Sistema',
    '00000000',
    '+1234567890',
    'admin@centro-tia-glenda.com',
    '1990-01-01',
    'activo'
);

-- =============================================
-- DATOS INICIALES - PERSONAL DEL CENTRO
-- =============================================
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, fecha_nacimiento, estado) VALUES
-- Dueña del centro (será administradora)
('María Glenda', 'Rodríguez', '12345678', '+50612345678', 'glenda@centro-tia-glenda.com', '1975-03-15', 'activo'),

-- Personal Terapéutico
('Ana Patricia', 'González', '23456789', '+50623456789', 'ana.gonzalez@centro-tia-glenda.com', '1985-07-22', 'activo'),
('Carlos Manuel', 'Jiménez', '34567890', '+50634567890', 'carlos.jimenez@centro-tia-glenda.com', '1988-11-10', 'activo'),
('Sofía Elena', 'Morales', '45678901', '+50645678901', 'sofia.morales@centro-tia-glenda.com', '1992-04-18', 'activo'),

-- Personal Pedagógico
('Roberto Luis', 'Vargas', '56789012', '+50656789012', 'roberto.vargas@centro-tia-glenda.com', '1980-09-25', 'activo'),
('Laura María', 'Castillo', '67890123', '+50667890123', 'laura.castillo@centro-tia-glenda.com', '1987-12-08', 'activo'),
('Diego Andrés', 'Hernández', '78901234', '+50678901234', 'diego.hernandez@centro-tia-glenda.com', '1990-06-14', 'activo');

-- =============================================
-- DATOS INICIALES - USUARIOS DEL SISTEMA
-- =============================================
-- Usuario Admin (ID persona: 1, ID rol: 1-Administrador)
INSERT INTO usuario (usuario, contrasenia, persona_id, rol_id, estado) VALUES
('admin', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 1, 1, 'activo');

-- Obtener el ID del usuario admin para auditoría (en PostgreSQL)
-- Nota: En PostgreSQL usamos currval para obtener el último valor de la secuencia

-- Actualizar auditoría de la persona admin
UPDATE persona SET usuario_creacion = currval('usuario_id_seq') WHERE id = 1;
UPDATE rol SET usuario_creacion = currval('usuario_id_seq') WHERE id IN (1,2,3,4);
UPDATE usuario SET usuario_creacion = currval('usuario_id_seq') WHERE id = currval('usuario_id_seq');

-- Usuarios del personal (contraseña: "password123" para todos)
INSERT INTO usuario (usuario, contrasenia, persona_id, rol_id, estado, usuario_creacion) VALUES
('glenda.rodriguez', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 2, 1, 'activo', currval('usuario_id_seq')),
('ana.gonzalez', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 3, 2, 'activo', currval('usuario_id_seq')),
('carlos.jimenez', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 4, 2, 'activo', currval('usuario_id_seq')),
('sofia.morales', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 5, 2, 'activo', currval('usuario_id_seq')),
('roberto.vargas', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 6, 3, 'activo', currval('usuario_id_seq')),
('laura.castillo', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 7, 3, 'activo', currval('usuario_id_seq')),
('diego.hernandez', '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 8, 3, 'activo', currval('usuario_id_seq'));

-- =============================================
-- DATOS DE EJEMPLO - PACIENTES/ALUMNOS
-- =============================================
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, fecha_nacimiento, estado, usuario_creacion) VALUES
-- Pacientes área terapéutica
('María José', 'Ramírez', '11111111', '+50611111111', 'mariajose.ramirez@email.com', '2015-03-20', 'activo', 1),
('Pedro Antonio', 'López', '22222222', '+50622222222', 'pedro.lopez@email.com', '2012-08-15', 'activo', 1),
('Valentina', 'Sánchez', '33333333', '+50633333333', 'valentina.sanchez@email.com', '2018-11-02', 'activo', 1),

-- Alumnos área pedagógica
('Santiago', 'Torres', '44444444', '+50644444444', 'santiago.torres@email.com', '2014-05-10', 'activo', 1),
('Isabella', 'Rojas', '55555555', '+50655555555', 'isabella.rojas@email.com', '2016-09-25', 'activo', 1),
('Sebastián', 'Mendoza', '66666666', '+50666666666', 'sebastian.mendoza@email.com', '2013-12-18', 'activo', 1);

-- =============================================
-- CONSULTAS DE VERIFICACIÓN
-- =============================================

-- Ver todos los roles
SELECT 
    id,
    nombre,
    descripcion,
    estado,
    fecha_creacion
FROM rol 
ORDER BY id;

-- Ver todas las personas
SELECT 
    p.id,
    p.nombre,
    p.apellido,
    p.cedula,
    p.telefono,
    p.correo,
    p.estado,
    p.fecha_creacion
FROM persona p
ORDER BY p.id;

-- Ver todos los usuarios con información completa
SELECT 
    u.id,
    u.usuario,
    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
    r.nombre as rol,
    u.estado,
    u.fecha_creacion
FROM usuario u
INNER JOIN persona p ON u.persona_id = p.id
INNER JOIN rol r ON u.rol_id = r.id
ORDER BY u.id;

-- Ver estadísticas generales
SELECT 
    'Total Personas' as concepto,
    COUNT(*) as cantidad
FROM persona
UNION ALL
SELECT 
    'Total Usuarios',
    COUNT(*)
FROM usuario
UNION ALL
SELECT 
    'Usuarios Activos',
    COUNT(*)
FROM usuario WHERE estado = 'activo'
UNION ALL
SELECT 
    'Total Roles',
    COUNT(*)
FROM rol;

-- =============================================
-- INFORMACIÓN DE CREDENCIALES
-- =============================================
/*
CREDENCIALES DE ACCESO INICIAL:

Usuario Administrador:
- Usuario: admin
- Contraseña: admin
- Persona: Admin Sistema
- Rol: Administrador

Usuarios del Personal (todos con contraseña: "password123"):
- glenda.rodriguez (Administrador - Dueña del centro)
- ana.gonzalez (Terapeuta)  
- carlos.jimenez (Terapeuta)
- sofia.morales (Terapeuta)
- roberto.vargas (Pedagógico)
- laura.castillo (Pedagógico) 
- diego.hernandez (Pedagógico)

NOTA: 
- Las contraseñas están hasheadas con bcrypt (PostgreSQL compatible)
- La contraseña real para usuarios de personal es: "password123"
- La contraseña para admin es: "admin"
- Cambiar todas las contraseñas en producción
- Script adaptado para PostgreSQL con SERIAL en lugar de AUTO_INCREMENT
*/