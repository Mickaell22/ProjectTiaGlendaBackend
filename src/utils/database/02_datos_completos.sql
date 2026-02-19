-- =============================================
-- CENTRO TIA GLENDA - DATOS COMPLETOS 2026
-- Archivo: 02_datos_completos.sql
-- Descripcion: Datos de prueba actualizados a febrero y marzo 2026
-- =============================================
--
-- CREDENCIALES PARA PRUEBAS (password: admin123 para todos):
--
-- ADMINISTRADORES:
--   admin.norte  (Maria Gonzalez)   - Centro Norte
--   admin.sur    (Carlos Rodriguez) - Centro Sur
--
-- TERAPEUTAS:
--   terapeuta.ana          (Ana Martinez)    - Centro Norte - Terapia del Lenguaje
--   fisioterapeuta.luis    (Luis Perez)      - Centro Norte - Fisioterapia
--   terapeuta.laura        (Laura Mendoza)   - Centro Sur   - Terapia del Lenguaje
--   terapeuta.diego        (Diego Vargas)    - Centro Sur   - Terapia Ocupacional
--
-- PEDAGOGOS:
--   pedagoga.carmen        (Carmen Flores)   - Centro Norte - Educacion Especial
--   pedagogo.sandra        (Sandra Lopez)    - Centro Sur   - Educacion Especial
--   pedagogo.miguel        (Miguel Torres)   - Centro Sur   - Desarrollo Cognitivo
--
-- SESIONES 2026 (fecha de referencia: 2026-02-18):
--   Terapeuticas activas:  ST-2026-0001 a ST-2026-0004
--   Pedagogicas activas:   SP-2026-0001 a SP-2026-0003
--   Asistencias pasadas:   2026-02-02 al 2026-02-17
--   Sesiones futuras:      2026-02-18 en adelante hasta abril/mayo 2026
--
-- DISTRIBUCION DE DATOS:
--   Centro Norte: 3 pacientes, 3 personal (2 terapeutas + 1 pedagoga)
--   Centro Sur:   2 pacientes, 4 personal (2 terapeutas + 2 pedagogos)
-- =============================================

SET search_path TO public;

-- =============================================
-- 1. CENTROS DE ATENCION
-- =============================================

INSERT INTO centros (nombre, codigo, direccion, telefono, email, horario_apertura, horario_cierre, turno_principal, observaciones) VALUES
('Centro Norte', 'NORTE', 'Av. Principal Norte #123, Sector Norte', '02-234-5678', 'norte@centrotiaglenda.com', '07:00', '15:00', 'matutino', 'Centro especializado en atencion matutina'),
('Centro Sur',   'SUR',   'Calle Central Sur #456, Sector Sur',     '02-345-6789', 'sur@centrotiaglenda.com',   '13:00', '19:00', 'vespertino', 'Centro especializado en atencion vespertina');

-- =============================================
-- 2. ROLES DEL SISTEMA
-- =============================================

INSERT INTO rol (nombre, descripcion, estado) VALUES
('Administrador', 'Acceso completo al sistema, gestion de usuarios y centros', 'activo'),
('Terapeuta',     'Personal especializado en terapias, gestion de pacientes asignados', 'activo'),
('Pedagogico',    'Personal especializado en educacion, gestion de estudiantes', 'activo');

-- =============================================
-- 3. ESPECIALIDADES
-- =============================================

-- Centro Norte
INSERT INTO especialidad (nombre, area, estado, id_centro) VALUES
('Terapia del Lenguaje', 'Especialidad terapéutica',  'activo', (SELECT id FROM centros WHERE codigo = 'NORTE')),
('Terapia Ocupacional',  'Especialidad terapéutica',  'activo', (SELECT id FROM centros WHERE codigo = 'NORTE')),
('Fisioterapia',         'Especialidad terapéutica',  'activo', (SELECT id FROM centros WHERE codigo = 'NORTE')),
('Terapia Psicologica',  'Especialidad terapéutica',  'activo', (SELECT id FROM centros WHERE codigo = 'NORTE')),
('Educacion Especial',   'Especialidad pedagógica',   'activo', (SELECT id FROM centros WHERE codigo = 'NORTE')),
('Apoyo Academico',      'Especialidad pedagógica',   'activo', (SELECT id FROM centros WHERE codigo = 'NORTE')),
('Desarrollo Cognitivo', 'Especialidad pedagógica',   'activo', (SELECT id FROM centros WHERE codigo = 'NORTE'));

-- Centro Sur
INSERT INTO especialidad (nombre, area, estado, id_centro) VALUES
('Terapia del Lenguaje', 'Especialidad terapéutica',  'activo', (SELECT id FROM centros WHERE codigo = 'SUR')),
('Terapia Ocupacional',  'Especialidad terapéutica',  'activo', (SELECT id FROM centros WHERE codigo = 'SUR')),
('Fisioterapia',         'Especialidad terapéutica',  'activo', (SELECT id FROM centros WHERE codigo = 'SUR')),
('Terapia Psicologica',  'Especialidad terapéutica',  'activo', (SELECT id FROM centros WHERE codigo = 'SUR')),
('Educacion Especial',   'Especialidad pedagógica',   'activo', (SELECT id FROM centros WHERE codigo = 'SUR')),
('Apoyo Academico',      'Especialidad pedagógica',   'activo', (SELECT id FROM centros WHERE codigo = 'SUR')),
('Desarrollo Cognitivo', 'Especialidad pedagógica',   'activo', (SELECT id FROM centros WHERE codigo = 'SUR'));

-- =============================================
-- 4. PERSONAS - CENTRO NORTE
-- =============================================

-- Administrador Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Maria',      'Gonzalez',        '1234567890', '0987654321', 'maria.gonzalez@centrotiaglenda.com',    'Av. 10 de Agosto #123', '1985-05-15', 'activo');

-- Personal terapeutico y pedagogico Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Ana',        'Martinez',        '1234567892', '0987654323', 'ana.martinez@centrotiaglenda.com',      'Av. Norte #789',        '1990-03-10', 'activo'),
('Luis',       'Perez',           '1234567893', '0987654324', 'luis.perez@centrotiaglenda.com',        'Calle Norte #012',      '1988-11-25', 'activo'),
('Carmen',     'Flores',          '1234567906', '0987654333', 'carmen.flores@centrotiaglenda.com',     'Av. Norte #345',        '1987-08-14', 'activo');

-- Tutores Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Carmen',     'Vasquez',         '1234567896', '0987654327', 'carmen.vasquez@gmail.com',              'Av. Amazonas #901',     '1978-04-12', 'activo'),
('Roberto',    'Jimenez',         '1234567897', '0987654328', 'roberto.jimenez@gmail.com',             'Calle Pichincha #234',  '1975-09-30', 'activo'),
('Maria Elena','Vega',            '1234567908', '0987654335', 'maria.vega@gmail.com',                  'Av. Norte #567',        '1981-12-05', 'activo');

-- Pacientes Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Sebastian',  'Vasquez',         '1234567900', '0987654327', NULL, 'Av. Amazonas #901',        '2018-06-15', 'activo'),
('Valentina',  'Jimenez',         '1234567901', '0987654328', NULL, 'Calle Pichincha #234',     '2017-03-08', 'activo'),
('Ana Sofia',  'Rodriguez Vega',  '1234567907', '0987654334', NULL, 'Av. Norte #567',           '2016-10-22', 'activo');

-- =============================================
-- 5. PERSONAS - CENTRO SUR
-- =============================================

-- Administrador Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Carlos',     'Rodriguez',       '1234567891', '0987654322', 'carlos.rodriguez@centrotiaglenda.com',  'Calle Bolivar #456',    '1982-08-20', 'activo');

-- Personal terapeutico y pedagogico Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Sandra',     'Lopez',           '1234567894', '0987654325', 'sandra.lopez@centrotiaglenda.com',      'Av. Sur #345',          '1987-12-03', 'activo'),
('Miguel',     'Torres',          '1234567895', '0987654326', 'miguel.torres@centrotiaglenda.com',     'Calle Sur #678',        '1985-07-18', 'activo'),
('Laura',      'Mendoza',         '1234567904', '0987654331', 'laura.mendoza@centrotiaglenda.com',     'Av. Sur #789',          '1989-04-15', 'activo'),
('Diego',      'Vargas',          '1234567905', '0987654332', 'diego.vargas@centrotiaglenda.com',      'Calle Sur #012',        '1986-09-22', 'activo');

-- Tutores Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Elena',      'Morales',         '1234567898', '0987654329', 'elena.morales@gmail.com',               'Av. Patria #567',       '1980-01-22', 'activo'),
('Patricia',   'Silva',           '1234567899', '0987654330', 'patricia.silva@gmail.com',              'Calle Sur #890',        '1983-06-18', 'activo');

-- Pacientes Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Mateo',      'Morales',         '1234567902', '0987654329', NULL, 'Av. Patria #567',          '2019-11-20', 'activo'),
('Isabella',   'Silva',           '1234567903', '0987654330', NULL, 'Calle Sur #890',            '2016-09-12', 'activo');

-- =============================================
-- 6. USUARIOS DEL SISTEMA
-- =============================================

-- Administradores (password: admin123)
INSERT INTO usuario (usuario, contrasenia, estado, id_persona, id_rol, id_centro, fecha_ultimo_acceso) VALUES
('admin.norte', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567890'),
    (SELECT id FROM rol WHERE nombre = 'Administrador'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), '2026-02-18 07:30:00'),

('admin.sur', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567891'),
    (SELECT id FROM rol WHERE nombre = 'Administrador'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), '2026-02-18 13:15:00');

-- Personal Centro Norte
INSERT INTO usuario (usuario, contrasenia, estado, id_persona, id_rol, id_centro, fecha_ultimo_acceso) VALUES
('terapeuta.ana', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567892'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), '2026-02-18 07:45:00'),

('fisioterapeuta.luis', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567893'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), '2026-02-17 08:00:00'),

('pedagoga.carmen', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567906'),
    (SELECT id FROM rol WHERE nombre = 'Pedagogico'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), '2026-02-17 08:10:00');

-- Personal Centro Sur
INSERT INTO usuario (usuario, contrasenia, estado, id_persona, id_rol, id_centro, fecha_ultimo_acceso) VALUES
('pedagogo.sandra', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567894'),
    (SELECT id FROM rol WHERE nombre = 'Pedagogico'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), '2026-02-18 13:30:00'),

('pedagogo.miguel', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567895'),
    (SELECT id FROM rol WHERE nombre = 'Pedagogico'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), '2026-02-17 14:00:00'),

('terapeuta.laura', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567904'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), '2026-02-17 14:05:00'),

('terapeuta.diego', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567905'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), '2026-02-18 13:20:00');

-- =============================================
-- 7. PERSONAL DEL CENTRO
-- =============================================

-- Personal Centro Norte
INSERT INTO personal (id_persona, id_especialidad, id_centro, fecha_ingreso, cargo, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567892'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-01-01', 'Licenciada en Terapia del Lenguaje', 'activo'),

((SELECT id FROM persona WHERE cedula = '1234567893'),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-01-01', 'Licenciado en Fisioterapia', 'activo'),

((SELECT id FROM persona WHERE cedula = '1234567906'),
 (SELECT id FROM especialidad WHERE nombre = 'Educacion Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-01-01', 'Licenciada en Educacion Especial', 'activo');

-- Personal Centro Sur
INSERT INTO personal (id_persona, id_especialidad, id_centro, fecha_ingreso, cargo, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567894'),
 (SELECT id FROM especialidad WHERE nombre = 'Educacion Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-01-01', 'Licenciada en Educacion Especial', 'activo'),

((SELECT id FROM persona WHERE cedula = '1234567895'),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-01-01', 'Licenciado en Psicologia Educativa', 'activo'),

((SELECT id FROM persona WHERE cedula = '1234567904'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-01-01', 'Licenciada en Terapia del Lenguaje', 'activo'),

((SELECT id FROM persona WHERE cedula = '1234567905'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-01-01', 'Licenciado en Terapia Ocupacional', 'activo');

-- =============================================
-- 8. ESPECIALIDADES DEL PERSONAL
-- =============================================

-- Centro Norte
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567892')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),

((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567892')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicologica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), FALSE),

((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567893')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),

((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567906')),
 (SELECT id FROM especialidad WHERE nombre = 'Educacion Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),

((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567906')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Academico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), FALSE);

-- Centro Sur
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567894')),
 (SELECT id FROM especialidad WHERE nombre = 'Educacion Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),

((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567894')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Academico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), FALSE),

((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567895')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),

((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567895')),
 (SELECT id FROM especialidad WHERE nombre = 'Educacion Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), FALSE),

((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567904')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),

((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567905')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE);

-- =============================================
-- 9. TUTORES
-- =============================================

-- Centro Norte
INSERT INTO tutor (id_persona, parentesco, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567896'), 'madre', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567897'), 'padre',  'activo'),
((SELECT id FROM persona WHERE cedula = '1234567908'), 'madre', 'activo');

-- Centro Sur
INSERT INTO tutor (id_persona, parentesco, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567898'), 'madre', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567899'), 'madre', 'activo');

-- =============================================
-- 10. PACIENTES
-- =============================================

-- Centro Norte
INSERT INTO paciente (id_persona, id_tutor, id_centro, fecha_ingreso, motivo_consulta, observaciones, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567900'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567896')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 '2024-01-15', 'Dificultades en el lenguaje expresivo',
 'Paciente colaborador, motivado por actividades ludicas. Avance sostenido en 2025.', 'activo'),

((SELECT id FROM persona WHERE cedula = '1234567901'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567897')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 '2024-01-20', 'Desarrollo motor fino',
 'Nina muy activa, responde bien a rutinas estructuradas. Continua en 2026 con nuevos objetivos.', 'activo'),

((SELECT id FROM persona WHERE cedula = '1234567907'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567908')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 '2024-02-10', 'Apoyo academico en lectoescritura',
 'Estudiante dedicada, necesita refuerzo en comprension lectora. Buen progreso reportado en 2025.', 'activo');

-- Centro Sur
INSERT INTO paciente (id_persona, id_tutor, id_centro, fecha_ingreso, motivo_consulta, observaciones, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567902'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567898')),
 (SELECT id FROM centros WHERE codigo = 'SUR'),
 '2024-02-01', 'Apoyo en lectoescritura y comunicacion oral',
 'Nino timido pero receptivo, le gustan los cuentos. Progreso notable en lenguaje expresivo.', 'activo'),

((SELECT id FROM persona WHERE cedula = '1234567903'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567899')),
 (SELECT id FROM centros WHERE codigo = 'SUR'),
 '2024-02-05', 'Refuerzo academico en matematicas y habilidades funcionales',
 'Estudiante dedicada, necesita apoyo en calculo mental. Mejora visible en autonomia funcional.', 'activo');

-- =============================================
-- 11. RELACION PACIENTE-TUTOR (tabla intermedia)
-- =============================================

INSERT INTO paciente_tutor (id_paciente, id_tutor, es_principal, tipo_relacion, puede_autorizar, puede_retirar, contacto_emergencia, prioridad_contacto) VALUES
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567900')),
 (SELECT id FROM tutor WHERE id_persona  = (SELECT id FROM persona WHERE cedula = '1234567896')),
 TRUE, 'madre', TRUE, TRUE, TRUE, 1),

((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567901')),
 (SELECT id FROM tutor WHERE id_persona  = (SELECT id FROM persona WHERE cedula = '1234567897')),
 TRUE, 'padre', TRUE, TRUE, TRUE, 1),

((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567907')),
 (SELECT id FROM tutor WHERE id_persona  = (SELECT id FROM persona WHERE cedula = '1234567908')),
 TRUE, 'madre', TRUE, TRUE, TRUE, 1),

((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567902')),
 (SELECT id FROM tutor WHERE id_persona  = (SELECT id FROM persona WHERE cedula = '1234567898')),
 TRUE, 'madre', TRUE, TRUE, TRUE, 1),

((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567903')),
 (SELECT id FROM tutor WHERE id_persona  = (SELECT id FROM persona WHERE cedula = '1234567899')),
 TRUE, 'madre', TRUE, TRUE, TRUE, 1);

-- =============================================
-- 12. ESPECIALIDADES DE PACIENTES
-- =============================================

-- Centro Norte
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal) VALUES
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567900')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),

((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567901')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),

((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567907')),
 (SELECT id FROM especialidad WHERE nombre = 'Educacion Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE);

-- Centro Sur
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal) VALUES
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567902')),
 (SELECT id FROM especialidad WHERE nombre = 'Educacion Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),

((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567902')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), FALSE),

((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567903')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Academico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),

((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567903')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), FALSE);

-- =============================================
-- 13. SESIONES TERAPEUTICAS 2026
-- =============================================

-- ST-2026-0001: Terapia del Lenguaje - Ana Martinez - Sebastian - Centro Norte
-- Lunes y Miercoles, 08:00-08:45, Feb-May 2026 (20 sesiones)
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES (
    'ST-2026-0001',
    'Terapia del Lenguaje - Comunicacion Expresiva 2026',
    'Consolidar la comunicacion expresiva y comprensiva mediante terapia ludica con material visual y tecnologico adaptado',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567892')),
    (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
    '2026-02-02', '2026-05-29',
    ARRAY['lunes', 'miercoles'], '08:00', '08:45', 45,
    20, 4, 25000.00, 500000.00,
    'individual', 'en_curso',
    (SELECT id FROM centros WHERE codigo = 'NORTE'),
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
);

-- ST-2026-0002: Fisioterapia - Luis Perez - Valentina - Centro Norte
-- Martes y Jueves, 09:00-09:45, Feb-May 2026 (16 sesiones)
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES (
    'ST-2026-0002',
    'Fisioterapia - Motricidad Fina y Coordinacion 2026',
    'Fortalecer la motricidad fina, coordinacion bimanual y equilibrio mediante ejercicios progresivos y material adaptado',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567893')),
    (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
    '2026-02-03', '2026-05-07',
    ARRAY['martes', 'jueves'], '09:00', '09:45', 45,
    16, 3, 30000.00, 480000.00,
    'individual', 'en_curso',
    (SELECT id FROM centros WHERE codigo = 'NORTE'),
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
);

-- ST-2026-0003: Terapia del Lenguaje - Laura Mendoza - Mateo - Centro Sur
-- Lunes y Miercoles, 14:00-14:45, Feb-Abr 2026 (20 sesiones)
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES (
    'ST-2026-0003',
    'Terapia del Lenguaje - Comunicacion Oral Centro Sur 2026',
    'Desarrollar habilidades de comunicacion oral, comprension auditiva y vocabulario mediante actividades interactivas',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567904')),
    (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
    '2026-02-02', '2026-04-29',
    ARRAY['lunes', 'miercoles'], '14:00', '14:45', 45,
    20, 3, 25000.00, 500000.00,
    'individual', 'en_curso',
    (SELECT id FROM centros WHERE codigo = 'SUR'),
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
);

-- ST-2026-0004: Terapia Ocupacional - Diego Vargas - Isabella - Centro Sur
-- Miercoles y Viernes, 15:00-15:45, Feb-Abr 2026 (16 sesiones)
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES (
    'ST-2026-0004',
    'Terapia Ocupacional - Independencia Funcional 2026',
    'Mejorar la independencia en actividades de la vida diaria, habilidades de autocuidado y participacion en actividades escolares',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567905')),
    (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
    '2026-02-04', '2026-04-24',
    ARRAY['miercoles', 'viernes'], '15:00', '15:45', 45,
    16, 3, 28000.00, 448000.00,
    'individual', 'en_curso',
    (SELECT id FROM centros WHERE codigo = 'SUR'),
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
);

-- =============================================
-- 14. INSCRIPCIONES EN SESIONES TERAPEUTICAS
-- =============================================

INSERT INTO sesion_paciente (id_sesion, id_paciente, fecha_inscripcion, estado, observaciones) VALUES
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2026-0001'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567900')),
 '2026-02-02', 'activo', 'Paciente motivado. Continua tratamiento exitoso de 2025'),

((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2026-0002'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567901')),
 '2026-02-03', 'activo', 'Continuacion de tratamiento. Nuevos objetivos para motricidad gruesa'),

((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2026-0003'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567902')),
 '2026-02-02', 'activo', 'Nuevo ciclo terapeutico. Enfoque en narrativa y vocabulario ampliado'),

((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2026-0004'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567903')),
 '2026-02-04', 'activo', 'Nuevo ciclo. Objetivos en actividades escolares y autonomia en el aula');

-- =============================================
-- 15. SESIONES PEDAGOGICAS 2026
-- =============================================

-- SP-2026-0001: Educacion Especial - Carmen Flores - Ana Sofia - Centro Norte
-- Martes y Jueves, 08:00-09:00, Feb-May 2026 (periodo 2026-A)
INSERT INTO sesion_pedagogica (
    codigo_sesion, id_educador, id_especialidad, nombre_clase, descripcion,
    fecha_inicio, fecha_fin, nivel_academico, adaptacion_curricular,
    duracion_minutos, frecuencia_semanal, dias_semana, hora_inicio, hora_fin,
    capacidad_maxima, modalidad, periodo_academico, costo_total, costo_por_clase,
    estado, observaciones, id_centro
) VALUES (
    'SP-2026-0001',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567906')),
    (SELECT id FROM especialidad WHERE nombre = 'Educacion Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
    'Apoyo en Lectoescritura Norte 2026',
    'Consolidacion de habilidades de lectura comprensiva y escritura funcional para el nivel primario',
    '2026-02-03', '2026-05-28', 'primaria',
    'Textos con imagenes de apoyo, tiempo extendido, uso de herramientas digitales de apoyo a la lectura',
    60, 2, ARRAY['martes', 'jueves'], '08:00', '09:00',
    4, 'presencial', '2026-A', 480.00, 24.00,
    'en_curso', 'Sesion de apoyo con enfoque en comprension lectora y produccion de textos cortos',
    (SELECT id FROM centros WHERE codigo = 'NORTE')
);

-- SP-2026-0002: Lectoescritura Inicial - Sandra Lopez - Mateo - Centro Sur
-- Lunes, Miercoles y Viernes, 14:00-15:00, Feb-Abr 2026 (periodo 2026-A)
INSERT INTO sesion_pedagogica (
    codigo_sesion, id_educador, id_especialidad, nombre_clase, descripcion,
    fecha_inicio, fecha_fin, nivel_academico, adaptacion_curricular,
    duracion_minutos, frecuencia_semanal, dias_semana, hora_inicio, hora_fin,
    capacidad_maxima, modalidad, periodo_academico, costo_total, costo_por_clase,
    estado, observaciones, id_centro
) VALUES (
    'SP-2026-0002',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567894')),
    (SELECT id FROM especialidad WHERE nombre = 'Educacion Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
    'Lectoescritura y Lenguaje Oral Sur 2026',
    'Desarrollo integrado de lectura, escritura y expresion oral con metodo fonetico-silabico',
    '2026-02-02', '2026-04-30', 'preescolar',
    'Reduccion de contenido por sesion, material visual de gran tamano, refuerzo positivo constante, pausa activa cada 15 min',
    60, 3, ARRAY['lunes', 'miercoles', 'viernes'], '14:00', '15:00',
    6, 'presencial', '2026-A', 720.00, 24.00,
    'en_curso', 'Sesion integrada de lectoescritura con componente de expresion oral coordinada con terapeuta del lenguaje',
    (SELECT id FROM centros WHERE codigo = 'SUR')
);

-- SP-2026-0003: Matematicas Basicas - Miguel Torres - Isabella - Centro Sur
-- Martes y Jueves, 15:00-16:00, Feb-Abr 2026 (periodo 2026-A)
INSERT INTO sesion_pedagogica (
    codigo_sesion, id_educador, id_especialidad, nombre_clase, descripcion,
    fecha_inicio, fecha_fin, nivel_academico, adaptacion_curricular,
    duracion_minutos, frecuencia_semanal, dias_semana, hora_inicio, hora_fin,
    capacidad_maxima, modalidad, periodo_academico, costo_total, costo_por_clase,
    estado, observaciones, id_centro
) VALUES (
    'SP-2026-0003',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567895')),
    (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
    'Matematicas y Cognicion Sur 2026',
    'Refuerzo en operaciones matematicas, pensamiento logico y resolucion de problemas con contextos cotidianos',
    '2026-02-03', '2026-04-30', 'primaria',
    'Uso de material concreto (abaco, bloques), problemas con contextos familiares, ejercicios de complejidad gradual',
    60, 2, ARRAY['martes', 'jueves'], '15:00', '16:00',
    4, 'presencial', '2026-A', 480.00, 24.00,
    'en_curso', 'Sesion de matematicas coordinada con la terapeuta ocupacional para refuerzo en autonomia escolar',
    (SELECT id FROM centros WHERE codigo = 'SUR')
);

-- =============================================
-- 16. INSCRIPCIONES EN SESIONES PEDAGOGICAS
-- =============================================

INSERT INTO sesion_estudiante (id_sesion, id_paciente, fecha_inscripcion, nivel_actual, adaptaciones_requeridas, estado, observaciones) VALUES
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2026-0001'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567907')),
 '2026-02-03', '3er grado',
 'Tiempo adicional para lectura, texto con letra grande, uso de regla como guia de lectura',
 'activo', 'Estudiante motivada. En 2025 alcanzo objetivos de decodificacion. Nuevo objetivo: comprension lectora'),

((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2026-0002'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567902')),
 '2026-02-02', 'pre-lectura avanzado',
 'Material visual ampliado, texto con imagenes, instrucciones verbales reforzadas',
 'activo', 'Buen avance en reconocimiento de letras. Ahora trabaja formacion de palabras y oraciones cortas'),

((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2026-0003'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567903')),
 '2026-02-03', '3er grado',
 'Explicaciones paso a paso, uso de calculadora para verificacion, problemas con imagenes de apoyo',
 'activo', 'Progreso en sumas y restas. Nuevo objetivo: multiplicacion y fracciones simples con material concreto');

-- =============================================
-- 17. CRONOGRAMAS TERAPEUTICOS 2026
-- =============================================

-- Cronograma ST-2026-0001 (lunes=1, miercoles=3) - 20 sesiones - Feb-May 2026
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2026-0001'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '08:00'::time, '08:45'::time,
    CASE WHEN fecha_gen::date < '2026-02-18' THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2026-02-02'::date, '2026-05-29'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3)
LIMIT 20;

-- Cronograma ST-2026-0002 (martes=2, jueves=4) - 16 sesiones - Feb-May 2026
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2026-0002'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '09:00'::time, '09:45'::time,
    CASE WHEN fecha_gen::date < '2026-02-18' THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2026-02-03'::date, '2026-05-07'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4)
LIMIT 16;

-- Cronograma ST-2026-0003 (lunes=1, miercoles=3) - 20 sesiones - Feb-Abr 2026
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2026-0003'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '14:00'::time, '14:45'::time,
    CASE WHEN fecha_gen::date < '2026-02-18' THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
FROM (
    SELECT generate_series('2026-02-02'::date, '2026-04-29'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3)
LIMIT 20;

-- Cronograma ST-2026-0004 (miercoles=3, viernes=5) - 16 sesiones - Feb-Abr 2026
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2026-0004'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '15:00'::time, '15:45'::time,
    CASE WHEN fecha_gen::date < '2026-02-18' THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
FROM (
    SELECT generate_series('2026-02-04'::date, '2026-04-24'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (3, 5)
LIMIT 16;

-- =============================================
-- 18. CRONOGRAMAS PEDAGOGICOS 2026
-- =============================================

-- Cronograma SP-2026-0001 (martes=2, jueves=4) - 24 clases - Feb-May 2026
INSERT INTO cronograma_clases (id_sesion, numero_clase_semanal, fecha_programada, hora_inicio, hora_fin, estado, tema_clase, usuario_creacion)
SELECT
    (SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2026-0001'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '08:00'::time, '09:00'::time,
    CASE WHEN fecha_gen::date < '2026-02-18' THEN 'completada' ELSE 'programada' END,
    CASE
        WHEN EXTRACT(dow FROM fecha_gen) = 2 THEN 'Comprension lectora: identificacion de ideas principales'
        ELSE 'Produccion escrita: oraciones y parrafos cortos'
    END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2026-02-03'::date, '2026-05-28'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4)
LIMIT 24;

-- Cronograma SP-2026-0002 (lunes=1, miercoles=3, viernes=5) - 36 clases - Feb-Abr 2026
INSERT INTO cronograma_clases (id_sesion, numero_clase_semanal, fecha_programada, hora_inicio, hora_fin, estado, tema_clase, usuario_creacion)
SELECT
    (SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2026-0002'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '14:00'::time, '15:00'::time,
    CASE WHEN fecha_gen::date < '2026-02-18' THEN 'completada' ELSE 'programada' END,
    CASE
        WHEN EXTRACT(dow FROM fecha_gen) = 1 THEN 'Reconocimiento de letras y sonidos'
        WHEN EXTRACT(dow FROM fecha_gen) = 3 THEN 'Formacion de silabas y palabras'
        ELSE 'Lectura de palabras y oraciones simples'
    END,
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
FROM (
    SELECT generate_series('2026-02-02'::date, '2026-04-30'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3, 5)
LIMIT 36;

-- Cronograma SP-2026-0003 (martes=2, jueves=4) - 24 clases - Feb-Abr 2026
INSERT INTO cronograma_clases (id_sesion, numero_clase_semanal, fecha_programada, hora_inicio, hora_fin, estado, tema_clase, usuario_creacion)
SELECT
    (SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2026-0003'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '15:00'::time, '16:00'::time,
    CASE WHEN fecha_gen::date < '2026-02-18' THEN 'completada' ELSE 'programada' END,
    CASE
        WHEN EXTRACT(dow FROM fecha_gen) = 2 THEN 'Operaciones de adicion y sustraccion con material concreto'
        ELSE 'Resolucion de problemas matematicos con contextos cotidianos'
    END,
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
FROM (
    SELECT generate_series('2026-02-03'::date, '2026-04-30'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4)
LIMIT 24;

-- =============================================
-- 19. ASISTENCIAS TERAPEUTICAS (sesiones pasadas: 2026-02-02 al 2026-02-17)
-- =============================================

-- Asistencias ST-2026-0001 - Sebastian (Terapia del Lenguaje)
-- Sesiones pasadas: lun 02/02, mie 04/02, lun 09/02, mie 11/02, lun 16/02
INSERT INTO asistencia_sesiones (
    id_cronograma, id_paciente, asistio, llegada_tardanza_minutos,
    estado_asistencia, observaciones_terapeuta, objetivos_trabajados, progreso_observado
)
SELECT
    cs.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567900')),
    CASE cs.fecha_programada
        WHEN '2026-02-11' THEN false
        ELSE true
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-09' THEN 10
        ELSE 0
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-11' THEN 'justificado'
        WHEN '2026-02-09' THEN 'tarde'
        ELSE 'presente'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-02' THEN 'Primer sesion del ciclo 2026. Excelente disposicion y energia del paciente.'
        WHEN '2026-02-04' THEN 'Trabajo en fonemas /r/ y /rr/. Buena concentracion, logro 4 de 5 ejercicios.'
        WHEN '2026-02-09' THEN 'Llego tarde pero se integro bien. Practica de oraciones con verbos en presente.'
        WHEN '2026-02-11' THEN 'Ausencia justificada por cita medica. Tutor notified via WhatsApp.'
        WHEN '2026-02-16' THEN 'Sesion muy productiva. Narro cuento corto con 5 oraciones completas. Avance notable.'
        ELSE 'Sesion completada satisfactoriamente.'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-02' THEN 'Evaluacion inicial del ciclo. Identificacion de logros y nuevos objetivos 2026.'
        WHEN '2026-02-04' THEN 'Articulacion de fonemas /r/ y /rr/ en posicion inicial, media y final.'
        WHEN '2026-02-09' THEN 'Construccion de oraciones con sujeto, verbo y predicado usando material visual.'
        WHEN '2026-02-11' THEN 'Sesion no realizada por ausencia justificada.'
        WHEN '2026-02-16' THEN 'Narracion de cuentos cortos, descripcion de laminas y vocabulario tematico.'
        ELSE 'Practica de objetivos de la sesion.'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-02' THEN 'Nivel inicial adecuado para el ciclo. Motivacion alta.'
        WHEN '2026-02-04' THEN 'Mejora del 30% en precision de fonema /rr/ respecto al ciclo anterior.'
        WHEN '2026-02-09' THEN 'Construye oraciones de 5-6 palabras de forma autonoma.'
        WHEN '2026-02-11' THEN 'Sin progreso registrado. Sesion recuperada en fecha acordada.'
        WHEN '2026-02-16' THEN 'Narro historia con inicio, desarrollo y desenlace. Logro superado.'
        ELSE 'Progreso continuo observado.'
    END
FROM cronograma_sesiones cs
JOIN sesion_terapia st ON cs.id_sesion = st.id
WHERE st.codigo_sesion = 'ST-2026-0001'
AND cs.fecha_programada < '2026-02-18';

-- Asistencias ST-2026-0002 - Valentina (Fisioterapia)
-- Sesiones pasadas: mar 03/02, jue 05/02, mar 10/02, jue 12/02, mar 17/02
INSERT INTO asistencia_sesiones (
    id_cronograma, id_paciente, asistio, llegada_tardanza_minutos,
    estado_asistencia, observaciones_terapeuta, objetivos_trabajados, progreso_observado
)
SELECT
    cs.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567901')),
    CASE cs.fecha_programada
        WHEN '2026-02-12' THEN false
        ELSE true
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-17' THEN 5
        ELSE 0
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-12' THEN 'ausente'
        WHEN '2026-02-17' THEN 'tarde'
        ELSE 'presente'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-03' THEN 'Inicio de ciclo 2026. Evaluacion de rango de movimiento y fuerza de manos.'
        WHEN '2026-02-05' THEN 'Ejercicios de prension y pinza. Logro completo de circuito de motricidad fina.'
        WHEN '2026-02-10' THEN 'Actividades de coordinacion bimanual. Excelente resultado en enhebrado y modelado.'
        WHEN '2026-02-12' THEN 'Ausencia sin justificacion previa. Se contacto a la madre.'
        WHEN '2026-02-17' THEN 'Llego con 5 min de retraso. Sesion productiva. Trabajo en scissors grasp.'
        ELSE 'Sesion completada.'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-03' THEN 'Evaluacion inicial: rango de movimiento, pinza digital, coordinacion oculo-manual.'
        WHEN '2026-02-05' THEN 'Prension de herramientas (lapiz, tijera). Circuito de obstaculos de motricidad fina.'
        WHEN '2026-02-10' THEN 'Enhebrado de cuentas, modelado en plastilina, laberinto con lapiz.'
        WHEN '2026-02-12' THEN 'Sesion no realizada.'
        WHEN '2026-02-17' THEN 'Scissors grasp, corte en linea recta y curva, trabajo con pincetas.'
        ELSE 'Ejercicios de motricidad fina.'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-03' THEN 'Fuerza de mano derecha: mejorada respecto a ciclo anterior. Objetivo: alcanzar nivel funcional.'
        WHEN '2026-02-05' THEN 'Completo circuito sin errores. Mejora significativa en tiempo de ejecucion.'
        WHEN '2026-02-10' THEN 'Enhebro 8 cuentas en 2 minutos. Supero objetivo de la sesion.'
        WHEN '2026-02-12' THEN 'Sin progreso registrado.'
        WHEN '2026-02-17' THEN 'Mejora en presion del lapiz. Escritura mas fluida segun reporte escolar.'
        ELSE 'Avance continuo.'
    END
FROM cronograma_sesiones cs
JOIN sesion_terapia st ON cs.id_sesion = st.id
WHERE st.codigo_sesion = 'ST-2026-0002'
AND cs.fecha_programada < '2026-02-18';

-- Asistencias ST-2026-0003 - Mateo (Terapia del Lenguaje Centro Sur)
-- Sesiones pasadas: lun 02/02, mie 04/02, lun 09/02, mie 11/02, lun 16/02
INSERT INTO asistencia_sesiones (
    id_cronograma, id_paciente, asistio, llegada_tardanza_minutos,
    estado_asistencia, observaciones_terapeuta, objetivos_trabajados, progreso_observado
)
SELECT
    cs.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567902')),
    CASE cs.fecha_programada
        WHEN '2026-02-09' THEN false
        ELSE true
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-04' THEN 8
        ELSE 0
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-09' THEN 'justificado'
        WHEN '2026-02-04' THEN 'tarde'
        ELSE 'presente'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-02' THEN 'Primera sesion 2026. Evaluacion de nivel actual en expresion oral y vocabulario.'
        WHEN '2026-02-04' THEN 'Llego un poco tarde. Trabajo en vocabulario tematico: familia y animales. Respondio bien.'
        WHEN '2026-02-09' THEN 'Ausencia justificada por malestar general segun reporte de la madre.'
        WHEN '2026-02-11' THEN 'Excelente sesion. Narro secuencia de 3 imagenes con conectores logicos.'
        WHEN '2026-02-16' THEN 'Practica de dialogos. Hizo preguntas espontaneas por primera vez en sesion.'
        ELSE 'Sesion completada.'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-02' THEN 'Evaluacion inicial: fluencia verbal, vocabulario receptivo y expresivo, narracion.'
        WHEN '2026-02-04' THEN 'Vocabulario tematico. Clasificacion de palabras por categorias. Descripcion de objetos.'
        WHEN '2026-02-09' THEN 'Sesion no realizada por ausencia justificada.'
        WHEN '2026-02-11' THEN 'Narracion con secuencia logica. Uso de conectores: primero, luego, finalmente.'
        WHEN '2026-02-16' THEN 'Practica de dialogos. Formulacion de preguntas espontaneas. Turnos de habla.'
        ELSE 'Practica de comunicacion oral.'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-02' THEN 'Vocabulario activo: 180 palabras aprox. Objetivo ciclo: 250 palabras funcionales.'
        WHEN '2026-02-04' THEN 'Identifico correctamente el 85% de vocabulario nuevo. Progreso notable.'
        WHEN '2026-02-09' THEN 'Sin progreso registrado.'
        WHEN '2026-02-11' THEN 'Primera narracion coherente con 3+ oraciones encadenadas. Logro importante.'
        WHEN '2026-02-16' THEN 'Formulo 4 preguntas espontaneas. Primera vez que lo hace sin apoyo visual.'
        ELSE 'Avance progresivo.'
    END
FROM cronograma_sesiones cs
JOIN sesion_terapia st ON cs.id_sesion = st.id
WHERE st.codigo_sesion = 'ST-2026-0003'
AND cs.fecha_programada < '2026-02-18';

-- Asistencias ST-2026-0004 - Isabella (Terapia Ocupacional Centro Sur)
-- Sesiones pasadas: mie 04/02, vie 06/02, mie 11/02, vie 13/02
INSERT INTO asistencia_sesiones (
    id_cronograma, id_paciente, asistio, llegada_tardanza_minutos,
    estado_asistencia, observaciones_terapeuta, objetivos_trabajados, progreso_observado
)
SELECT
    cs.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567903')),
    true,
    CASE cs.fecha_programada
        WHEN '2026-02-13' THEN 15
        ELSE 0
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-13' THEN 'tarde'
        ELSE 'presente'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-04' THEN 'Primera sesion del ciclo. Evaluacion funcional en AVD (actividades de vida diaria).'
        WHEN '2026-02-06' THEN 'Trabajo en organizacion del material escolar. Logro clasificar cuadernos por materia.'
        WHEN '2026-02-11' THEN 'Practica de escritura funcional. Mejora notable en presion del lapiz y postura.'
        WHEN '2026-02-13' THEN 'Llego tarde por trafico. Sesion enfocada en uso de agenda escolar y planificacion.'
        ELSE 'Sesion completada.'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-04' THEN 'Evaluacion: independencia en organizacion de mochila, uso de material escolar, escritura.'
        WHEN '2026-02-06' THEN 'Organizacion de material escolar. Uso de agenda. Clasificacion por materias.'
        WHEN '2026-02-11' THEN 'Escritura funcional: nombre completo, fecha, copiado de oraciones simples.'
        WHEN '2026-02-13' THEN 'Planificacion con agenda: como organizar tareas escolares dia a dia.'
        ELSE 'Actividades funcionales de la vida diaria.'
    END,
    CASE cs.fecha_programada
        WHEN '2026-02-04' THEN 'Nivel funcional moderado. Requiere apoyo en organizacion y escritura. Plan trazado.'
        WHEN '2026-02-06' THEN 'Organiza mochila en 4 min sin ayuda. Antes requeria 10+ minutos con ayuda.'
        WHEN '2026-02-11' THEN 'Escribe nombre completo con buena legibilidad. Presion del lapiz normalizada.'
        WHEN '2026-02-13' THEN 'Completo su agenda de la semana de forma independiente. Logro del objetivo parcial.'
        ELSE 'Progreso observado en independencia funcional.'
    END
FROM cronograma_sesiones cs
JOIN sesion_terapia st ON cs.id_sesion = st.id
WHERE st.codigo_sesion = 'ST-2026-0004'
AND cs.fecha_programada < '2026-02-18';

-- =============================================
-- 20. ASISTENCIAS PEDAGOGICAS (clases pasadas: 2026-02-02 al 2026-02-17)
-- =============================================

-- Asistencias SP-2026-0001 - Ana Sofia (Educacion Especial Norte)
-- Clases pasadas: mar 03/02, jue 05/02, mar 10/02, jue 12/02, mar 17/02
INSERT INTO asistencia_clases (
    id_cronograma, id_paciente, asistio, llegada_tardanza_minutos,
    estado_asistencia, observaciones_educador, participacion_clase,
    actividades_completadas, calificacion_clase
)
SELECT
    cc.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567907')),
    CASE cc.fecha_programada
        WHEN '2026-02-12' THEN false
        ELSE true
    END,
    0,
    CASE cc.fecha_programada
        WHEN '2026-02-12' THEN 'justificado'
        ELSE 'presente'
    END,
    CASE cc.fecha_programada
        WHEN '2026-02-03' THEN 'Inicio de ciclo 2026. Evaluacion diagnostica. Identifico ideas principales en texto breve.'
        WHEN '2026-02-05' THEN 'Excelente! Respondio preguntas inferenciales por primera vez de forma correcta.'
        WHEN '2026-02-10' THEN 'Muy buena clase. Produjo 3 oraciones sobre el texto leido con conectores logicos.'
        WHEN '2026-02-12' THEN 'Ausencia justificada. Actividades enviadas a casa con la madre.'
        WHEN '2026-02-17' THEN 'Sobresaliente. Resumio texto de 1 pagina en 4 oraciones clave. Gran avance.'
        ELSE 'Clase completada.'
    END,
    CASE cc.fecha_programada
        WHEN '2026-02-12' THEN NULL
        WHEN '2026-02-03' THEN 'regular'
        WHEN '2026-02-17' THEN 'excelente'
        ELSE 'buena'
    END,
    CASE cc.fecha_programada
        WHEN '2026-02-12' THEN false
        ELSE true
    END,
    CASE cc.fecha_programada
        WHEN '2026-02-03' THEN 8
        WHEN '2026-02-05' THEN 9
        WHEN '2026-02-10' THEN 8
        WHEN '2026-02-12' THEN NULL
        WHEN '2026-02-17' THEN 10
        ELSE 8
    END
FROM cronograma_clases cc
JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
WHERE sp.codigo_sesion = 'SP-2026-0001'
AND cc.fecha_programada < '2026-02-18';

-- Asistencias SP-2026-0002 - Mateo (Lectoescritura Sur)
-- Clases pasadas: lun 02/02, mie 04/02, vie 06/02, lun 09/02, mie 11/02, vie 13/02, lun 16/02
INSERT INTO asistencia_clases (
    id_cronograma, id_paciente, asistio, llegada_tardanza_minutos,
    estado_asistencia, observaciones_educador, participacion_clase,
    actividades_completadas, calificacion_clase
)
SELECT
    cc.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567902')),
    CASE cc.fecha_programada
        WHEN '2026-02-11' THEN false
        ELSE true
    END,
    CASE cc.fecha_programada
        WHEN '2026-02-09' THEN 5
        ELSE 0
    END,
    CASE cc.fecha_programada
        WHEN '2026-02-11' THEN 'ausente'
        WHEN '2026-02-09' THEN 'tarde'
        ELSE 'presente'
    END,
    CASE cc.fecha_programada
        WHEN '2026-02-02' THEN 'Primera clase 2026. Repaso de letras conocidas y evaluacion de avance previo.'
        WHEN '2026-02-04' THEN 'Formo palabras de 3 silabas sin ayuda. Gran logro para Mateo!'
        WHEN '2026-02-06' THEN 'Leyo su primera oracion completa: "El gato come." Emocion evidente.'
        WHEN '2026-02-09' THEN 'Llego tarde. Se integro rapido. Trabajo en lectura de palabras con digrafos.'
        WHEN '2026-02-11' THEN 'No asistio. Madre no informo. Se enviara nota en cuaderno.'
        WHEN '2026-02-13' THEN 'Compensacion de clase perdida. Repaso y refuerzo de contenidos de la semana.'
        WHEN '2026-02-16' THEN 'Lee 10 palabras de lista en 1 minuto. Velocidad lectora emergente. Excelente!'
        ELSE 'Clase completada.'
    END,
    CASE cc.fecha_programada
        WHEN '2026-02-11' THEN NULL
        WHEN '2026-02-02' THEN 'regular'
        WHEN '2026-02-06' THEN 'excelente'
        WHEN '2026-02-16' THEN 'excelente'
        ELSE 'buena'
    END,
    CASE cc.fecha_programada
        WHEN '2026-02-11' THEN false
        ELSE true
    END,
    CASE cc.fecha_programada
        WHEN '2026-02-02' THEN 7
        WHEN '2026-02-04' THEN 8
        WHEN '2026-02-06' THEN 9
        WHEN '2026-02-09' THEN 7
        WHEN '2026-02-11' THEN NULL
        WHEN '2026-02-13' THEN 7
        WHEN '2026-02-16' THEN 9
        ELSE 7
    END
FROM cronograma_clases cc
JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
WHERE sp.codigo_sesion = 'SP-2026-0002'
AND cc.fecha_programada < '2026-02-18';

-- Asistencias SP-2026-0003 - Isabella (Matematicas Sur)
-- Clases pasadas: mar 03/02, jue 05/02, mar 10/02, jue 12/02, mar 17/02
INSERT INTO asistencia_clases (
    id_cronograma, id_paciente, asistio, llegada_tardanza_minutos,
    estado_asistencia, observaciones_educador, participacion_clase,
    actividades_completadas, calificacion_clase
)
SELECT
    cc.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567903')),
    true,
    0,
    'presente',
    CASE cc.fecha_programada
        WHEN '2026-02-03' THEN 'Excelente inicio de ciclo. Demostro dominio solido de sumas y restas de 2 cifras.'
        WHEN '2026-02-05' THEN 'Resolucio 8 de 10 problemas correctamente. Uso el abaco de forma autonoma.'
        WHEN '2026-02-10' THEN 'Primera introduccion a la multiplicacion con bloques. Lo comprendio rapidamente!'
        WHEN '2026-02-12' THEN 'Consolido tablas del 2 y del 5. Empezo a ver patrones en los resultados.'
        WHEN '2026-02-17' THEN 'Resolvio problemas de contexto real con multiplicacion. Sobresaliente desempeno.'
        ELSE 'Clase completada.'
    END,
    CASE cc.fecha_programada
        WHEN '2026-02-10' THEN 'buena'
        WHEN '2026-02-17' THEN 'excelente'
        ELSE 'excelente'
    END,
    true,
    CASE cc.fecha_programada
        WHEN '2026-02-03' THEN 9
        WHEN '2026-02-05' THEN 8
        WHEN '2026-02-10' THEN 9
        WHEN '2026-02-12' THEN 10
        WHEN '2026-02-17' THEN 10
        ELSE 9
    END
FROM cronograma_clases cc
JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
WHERE sp.codigo_sesion = 'SP-2026-0003'
AND cc.fecha_programada < '2026-02-18';

-- =============================================
-- 21. ACCESO MULTI-CENTRO (usuario_centros)
-- =============================================

-- Administradores: acceso a ambos centros
INSERT INTO usuario_centros (id_usuario, id_centro, es_centro_predeterminado) VALUES
((SELECT id FROM usuario WHERE usuario = 'admin.norte'),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), TRUE),
((SELECT id FROM usuario WHERE usuario = 'admin.norte'),
 (SELECT id FROM centros WHERE codigo = 'SUR'), FALSE),
((SELECT id FROM usuario WHERE usuario = 'admin.sur'),
 (SELECT id FROM centros WHERE codigo = 'SUR'), TRUE),
((SELECT id FROM usuario WHERE usuario = 'admin.sur'),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), FALSE);

-- Personal: acceso a su centro asignado
INSERT INTO usuario_centros (id_usuario, id_centro, es_centro_predeterminado) VALUES
((SELECT id FROM usuario WHERE usuario = 'terapeuta.ana'),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), TRUE),
((SELECT id FROM usuario WHERE usuario = 'fisioterapeuta.luis'),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), TRUE),
((SELECT id FROM usuario WHERE usuario = 'pedagoga.carmen'),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), TRUE),
((SELECT id FROM usuario WHERE usuario = 'pedagogo.sandra'),
 (SELECT id FROM centros WHERE codigo = 'SUR'), TRUE),
((SELECT id FROM usuario WHERE usuario = 'pedagogo.miguel'),
 (SELECT id FROM centros WHERE codigo = 'SUR'), TRUE),
((SELECT id FROM usuario WHERE usuario = 'terapeuta.laura'),
 (SELECT id FROM centros WHERE codigo = 'SUR'), TRUE),
((SELECT id FROM usuario WHERE usuario = 'terapeuta.diego'),
 (SELECT id FROM centros WHERE codigo = 'SUR'), TRUE);

-- =============================================
-- FIN DE DATOS COMPLETOS 2026
-- =============================================
--
-- RESUMEN DE DATOS CARGADOS:
--   Centros:              2 (Norte y Sur)
--   Roles:                3 (Administrador, Terapeuta, Pedagogico)
--   Especialidades:      14 (7 por centro)
--   Personas:            19 (admin x2, personal x7, tutores x5, pacientes x5)
--   Usuarios:             9 (2 admin + 7 personal)
--   Personal:             7 (3 Norte + 4 Sur)
--   Tutores:              5 (3 Norte + 2 Sur)
--   Pacientes:            5 (3 Norte + 2 Sur)
--   Sesiones terapia:     4 (ST-2026-0001 a 0004) - todas en_curso
--   Sesiones pedagogicas: 3 (SP-2026-0001 a 0003) - todas en_curso
--   Cronograma terapia:  72 entradas (20+16+20+16 sesiones)
--   Cronograma clases:   84 entradas (24+36+24 clases)
--   Asistencias terapia: 19 registros (sesiones pasadas Feb 2-17)
--   Asistencias clases:  24 registros (clases pasadas Feb 2-17)
--   usuario_centros:     11 registros
-- =============================================
