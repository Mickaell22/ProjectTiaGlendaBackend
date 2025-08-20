-- =============================================
-- CENTRO TÍA GLENDA - DATOS INICIALES CENTRO NORTE
-- Archivo: 02.1_datos_centro_norte.sql
-- =============================================

-- =============================================
-- 1. DATOS INICIALES - CENTRO NORTE
-- =============================================
INSERT INTO centros (nombre, codigo, direccion, telefono, email, horario_apertura, horario_cierre, turno_principal, observaciones) VALUES 
('Centro Norte', 'NORTE', 'Av. Principal Norte #123, Sector Norte', '02-234-5678', 'norte@centrotiaglenda.com', '07:00', '15:00', 'matutino', 'Centro especializado en atención matutina');

-- =============================================
-- 2. DATOS INICIALES - ROLES COMUNES
-- =============================================
INSERT INTO rol (nombre, descripcion, estado) VALUES
('Administrador', 'Acceso completo al sistema, gestión de usuarios y centros', 'activo'),
('Terapeuta', 'Personal especializado en terapias, gestión de pacientes asignados', 'activo'),
('Pedagógico', 'Personal especializado en educación, gestión de estudiantes', 'activo');

-- =============================================
-- 3. DATOS INICIALES - ESPECIALIDADES COMUNES
-- =============================================
INSERT INTO especialidad (nombre, descripcion, estado) VALUES
-- Especialidades Terapéuticas
('Terapia del Lenguaje', 'Especialidad terapéutica para el desarrollo del lenguaje y comunicación', 'activo'),
('Terapia Ocupacional', 'Especialidad terapéutica para el desarrollo de habilidades ocupacionales', 'activo'),
('Fisioterapia', 'Especialidad terapéutica para el desarrollo y rehabilitación física', 'activo'),
('Terapia Psicológica', 'Especialidad terapéutica para el bienestar psicológico y emocional', 'activo'),

-- Especialidades Pedagógicas  
('Educación Especial', 'Especialidad pedagógica para la educación especializada', 'activo'),
('Apoyo Académico', 'Especialidad pedagógica para refuerzo académico', 'activo'),
('Desarrollo Cognitivo', 'Especialidad pedagógica para el desarrollo cognitivo', 'activo');

-- =============================================
-- 4. PERSONAS - ADMINISTRADOR Y PERSONAL CENTRO NORTE
-- =============================================

-- Administrador Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('María', 'González', '1234567890', '0987654321', 'maria.gonzalez@centrotiaglenda.com', 'Av. 10 de Agosto #123', '1985-05-15', 'activo');

-- Personal Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Ana', 'Martínez', '1234567892', '0987654323', 'ana.martinez@centrotiaglenda.com', 'Av. Norte #789', '1990-03-10', 'activo'),
('Luis', 'Pérez', '1234567893', '0987654324', 'luis.perez@centrotiaglenda.com', 'Calle Norte #012', '1988-11-25', 'activo');

-- =============================================
-- 5. USUARIOS DEL SISTEMA - CENTRO NORTE
-- =============================================

-- Administrador Centro Norte
INSERT INTO usuario (usuario, contrasenia, estado, persona_id, rol_id, id_centro, fecha_ultimo_acceso) VALUES
('admin.norte', '$2b$12$HGyK9EndrLNZNiG3p2t9MOBM.2xxSFC51DKePTxgM83vnz.4D2LIm', 'activo', 
    (SELECT id FROM persona WHERE cedula = '1234567890'), 
    (SELECT id FROM rol WHERE nombre = 'Administrador'), 
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL); -- password: admin123

-- Personal Centro Norte  
INSERT INTO usuario (usuario, contrasenia, estado, persona_id, rol_id, id_centro, fecha_ultimo_acceso) VALUES
('terapeuta.ana', '$2b$12$HGyK9EndrLNZNiG3p2t9MOBM.2xxSFC51DKePTxgM83vnz.4D2LIm', 'activo', 
    (SELECT id FROM persona WHERE cedula = '1234567892'), 
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'), 
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL), -- password: admin123
('terapeuta.luis', '$2b$12$HGyK9EndrLNZNiG3p2t9MOBM.2xxSFC51DKePTxgM83vnz.4D2LIm', 'activo', 
    (SELECT id FROM persona WHERE cedula = '1234567893'), 
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'), 
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL); -- password: admin123

-- =============================================
-- 6. PERSONAL DEL CENTRO NORTE
-- =============================================
INSERT INTO personal (persona_id, id_especialidad, id_centro, fecha_ingreso, cargo, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567892'), 
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'), 
 (SELECT id FROM centros WHERE codigo = 'NORTE'), 
 '2024-01-01', 'Licenciada en Terapia del Lenguaje', 'activo'), -- Ana Martínez
((SELECT id FROM persona WHERE cedula = '1234567893'), 
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia'), 
 (SELECT id FROM centros WHERE codigo = 'NORTE'), 
 '2024-01-01', 'Licenciado en Fisioterapia', 'activo'); -- Luis Pérez

-- =============================================
-- 7. ESPECIALIDADES DEL PERSONAL - CENTRO NORTE
-- =============================================

-- Ana Martínez - Terapia del Lenguaje (Centro Norte)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567892')), 
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'), 
 TRUE); -- Terapia del Lenguaje

-- Luis Pérez - Fisioterapia (Centro Norte)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567893')), 
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia'), 
 TRUE); -- Fisioterapia

-- *** FASE 2: MÚLTIPLES ESPECIALIDADES PARA PERSONAL ***
-- Ana también puede hacer Terapia Psicológica
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal, fecha_asignacion, observaciones, usuario_creacion) VALUES
((SELECT id FROM personal WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567892')), 
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica'), 
 FALSE, CURRENT_DATE, 'Especialidad secundaria en terapia psicológica', 
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'));

-- =============================================
-- 8. PERSONAS - TUTORES Y PACIENTES CENTRO NORTE
-- =============================================

-- Tutores Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Carmen', 'Vásquez', '1234567896', '0987654327', 'carmen.vasquez@gmail.com', 'Av. Amazonas #901', '1978-04-12', 'activo'),
('Roberto', 'Jiménez', '1234567897', '0987654328', 'roberto.jimenez@gmail.com', 'Calle Pichincha #234', '1975-09-30', 'activo');

-- Pacientes Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Sebastián', 'Vásquez', '1234567900', '0987654327', NULL, 'Av. Amazonas #901', '2018-06-15', 'activo'), -- 6 años
('Valentina', 'Jiménez', '1234567901', '0987654328', NULL, 'Calle Pichincha #234', '2017-03-08', 'activo'); -- 7 años

-- =============================================
-- 9. TUTORES - CENTRO NORTE
-- =============================================
INSERT INTO tutor (nombre, apellido, cedula, telefono, email, direccion, parentesco, estado) VALUES
('Carmen', 'Vásquez', '1234567896', '0987654327', 'carmen.vasquez@gmail.com', 'Av. Amazonas #901', 'madre', 'activo'),
('Roberto', 'Jiménez', '1234567897', '0987654328', 'roberto.jimenez@gmail.com', 'Calle Pichincha #234', 'padre', 'activo');

-- =============================================
-- 10. PACIENTES - CENTRO NORTE
-- =============================================

-- Pacientes Centro Norte (Horario matutino)
INSERT INTO paciente (persona_id, id_tutor, id_centro, fecha_ingreso, motivo_consulta, observaciones, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567900'), -- Sebastián
 (SELECT id FROM tutor WHERE cedula = '1234567896'), -- Carmen (madre)
 (SELECT id FROM centros WHERE codigo = 'NORTE'), 
 '2024-01-15', 'Dificultades en pronunciación y comunicación', 'Niño colaborativo y motivado', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567901'), -- Valentina
 (SELECT id FROM tutor WHERE cedula = '1234567897'), -- Roberto (padre)
 (SELECT id FROM centros WHERE codigo = 'NORTE'), 
 '2024-02-01', 'Necesidad de fortalecimiento en coordinación motora', 'Requiere refuerzo en casa', 'activo');

-- *** ESPECIALIDADES PARA PACIENTES ***
-- Sebastián - Terapia del Lenguaje (principal)
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal, fecha_asignacion, fecha_inicio_tratamiento, observaciones, usuario_creacion) VALUES
((SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567900')), -- Sebastián
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'), 
 TRUE, '2024-01-15', '2024-01-22', 'Especialidad principal - Terapia del lenguaje', 
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'));

-- Sebastián también recibe Terapia Ocupacional
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal, fecha_asignacion, fecha_inicio_tratamiento, observaciones, usuario_creacion) VALUES
((SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567900')), -- Sebastián
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional'), 
 FALSE, '2024-02-15', '2024-02-22', 'Tratamiento complementario en terapia ocupacional', 
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'));

-- Valentina - Fisioterapia (principal)
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal, fecha_asignacion, fecha_inicio_tratamiento, observaciones, usuario_creacion) VALUES
((SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567901')), -- Valentina
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia'), 
 TRUE, '2024-02-01', '2024-02-08', 'Especialidad principal - Fisioterapia', 
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'));

-- Valentina también recibe Terapia del Lenguaje  
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal, fecha_asignacion, fecha_inicio_tratamiento, observaciones, usuario_creacion) VALUES
((SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567901')), -- Valentina
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'), 
 FALSE, '2024-03-01', '2024-03-08', 'Tratamiento complementario en lenguaje', 
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'));

-- =============================================
-- 11. SESIONES DE TERAPIA - CENTRO NORTE
-- =============================================

-- Sesión Centro Norte - Terapia del Lenguaje
INSERT INTO sesion_terapia (
    id_terapeuta, id_especialidad, id_centro, fecha_inicio, fecha_fin,
    dias_semana, hora_inicio, duracion_minutos, tipo_sesion, modalidad,
    objetivo_general, costo_sesion, frecuencia_semanal, estado, usuario_creacion
) VALUES (
    (SELECT id FROM personal WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567892')), -- Ana Martínez
    (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'), 
    (SELECT id FROM centros WHERE codigo = 'NORTE'), 
    '2025-02-15',
    '2025-05-15',
    ARRAY['lunes', 'miercoles', 'viernes'],
    '09:00',
    45,
    'grupal',
    'presencial',
    'Desarrollo del lenguaje y comunicación en grupo matutino',
    12000.00,
    3,
    'planificada',
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
);

-- =============================================
-- 12. ASIGNACIÓN DE PACIENTES A SESIONES - CENTRO NORTE
-- =============================================

-- Pacientes en sesión de terapia (Centro Norte)
INSERT INTO sesion_paciente (id_sesion, id_paciente, fecha_inscripcion, observaciones, estado, usuario_creacion) VALUES
((SELECT id FROM sesion_terapia WHERE id_especialidad = (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje') AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), 
 (SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567900')), -- Sebastián
 '2025-02-15', 'Sebastián - Terapia del lenguaje matutina', 'activo', 
 (SELECT id FROM usuario WHERE usuario = 'admin.norte')),
((SELECT id FROM sesion_terapia WHERE id_especialidad = (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje') AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), 
 (SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567901')), -- Valentina
 '2025-02-22', 'Valentina - Combinado con fisioterapia', 'activo', 
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'));

-- =============================================
-- 13. GENERAR CRONOGRAMAS AUTOMÁTICOS - CENTRO NORTE
-- =============================================

-- Generar cronograma para sesión de terapia
SELECT generar_cronograma_sesion_terapia(
    (SELECT id FROM sesion_terapia WHERE id_especialidad = (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje') AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE'))
);

-- =============================================
-- 14. MENSAJE DE FINALIZACIÓN
-- =============================================
SELECT 'Datos iniciales Centro Norte insertados exitosamente' AS mensaje;

-- =============================================
-- 15. INFORMACIÓN DE USUARIOS CREADOS - CENTRO NORTE
-- =============================================
SELECT 'USUARIOS CENTRO NORTE - Contraseña para todos: admin123' AS info;
SELECT 
    u.usuario, 
    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo, 
    r.nombre as rol, 
    c.nombre as centro 
FROM usuario u
JOIN persona p ON u.persona_id = p.id  
JOIN rol r ON u.rol_id = r.id
JOIN centros c ON u.id_centro = c.id
WHERE c.codigo = 'NORTE'
ORDER BY r.nombre;

-- =============================================
-- 16. RESUMEN DE DATOS - CENTRO NORTE
-- =============================================
/*
============================================================================
DATOS CENTRO NORTE CREADOS:
============================================================================
✓ 1 Centro (Norte - Matutino)
✓ 3 Roles del sistema (compartidos)
✓ 7 Especialidades (compartidas: 4 terapéuticas, 3 pedagógicas)
✓ 3 Usuarios (1 admin, 2 terapeutas)
✓ 2 Personal profesional
✓ 2 Tutores y 2 Pacientes
✓ 1 Sesión de terapia con cronograma automático
✓ FASE 2: Especialidades múltiples implementadas

CREDENCIALES DE ACCESO CENTRO NORTE:
- admin.norte / admin123 (Administrador)
- terapeuta.ana / admin123 (Terapeuta - Lenguaje/Psicológica)
- terapeuta.luis / admin123 (Terapeuta - Fisioterapia)

PACIENTES CON ESPECIALIDADES MÚLTIPLES:
- Sebastián: Terapia del Lenguaje (principal) + Terapia Ocupacional
- Valentina: Fisioterapia (principal) + Terapia del Lenguaje
============================================================================
*/