-- =============================================
-- CENTRO TIA GLENDA - DATOS INICIALES PRODUCCION
-- Archivo: 01-1_datos.sql
-- Descripcion: Datos minimos necesarios para inicializar el sistema en produccion
-- =============================================

-- Configurar esquema por defecto
SET search_path TO public;

-- =============================================
-- 1. CENTROS DE ATENCION
-- =============================================

INSERT INTO centros (nombre, codigo, direccion, telefono, email, horario_apertura, horario_cierre, turno_principal, observaciones) VALUES
('Centro Norte', 'NORTE', 'Av. Principal Norte #123, Sector Norte', '02-234-5678', 'norte@centrotiaglenda.com', '07:00', '15:00', 'matutino', 'Centro especializado en atencion matutina'),
('Centro Sur', 'SUR', 'Calle Central Sur #456, Sector Sur', '02-345-6789', 'sur@centrotiaglenda.com', '13:00', '19:00', 'vespertino', 'Centro especializado en atencion vespertina');

-- =============================================
-- 2. ROLES DEL SISTEMA
-- =============================================

INSERT INTO rol (nombre, descripcion, estado) VALUES
('Administrador', 'Acceso completo al sistema, gestion de usuarios y centros', 'activo'),
('Terapeuta', 'Personal especializado en terapias, gestion de pacientes asignados', 'activo'),
('Pedagogico', 'Personal especializado en educacion, gestion de estudiantes', 'activo');


-- =============================================
-- 3. ADMINISTRADORES DEL SISTEMA
-- =============================================

-- Personas administradoras
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Admin', 'Norte', '1111111111', '0999999991', 'admin.norte@centrotiaglenda.com', 'Av. Principal Norte #123', '1980-01-01', 'activo'),
('Admin', 'Sur', '2222222222', '0999999992', 'admin.sur@centrotiaglenda.com', 'Calle Central Sur #456', '1980-01-01', 'activo');

-- Usuarios administradores (password: admin123)
INSERT INTO usuario (usuario, contrasenia, estado, id_persona, id_rol, id_centro, fecha_ultimo_acceso) VALUES
('admin.norte', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1111111111'),
    (SELECT id FROM rol WHERE nombre = 'Administrador'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('admin.sur', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '2222222222'),
    (SELECT id FROM rol WHERE nombre = 'Administrador'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL);

-- =============================================
-- 4. VERIFICACION FINAL
-- =============================================

DO $$
DECLARE
    centros_count INTEGER;
    roles_count INTEGER;
    usuarios_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO centros_count FROM centros;
    SELECT COUNT(*) INTO roles_count FROM rol;
    SELECT COUNT(*) INTO usuarios_count FROM usuario;

    RAISE NOTICE '=== RESUMEN DE DATOS INICIALES ===';
    RAISE NOTICE 'Centros: %', centros_count;
    RAISE NOTICE 'Roles: %', roles_count;
    RAISE NOTICE 'Usuarios administradores: %', usuarios_count;
    RAISE NOTICE '=== SISTEMA LISTO PARA PRODUCCION ===';
END $$;
