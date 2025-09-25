-- =============================================
-- CENTRO TÍA GLENDA - DATOS COMPLETOS DEL SISTEMA
-- Archivo: 02_datos_completos.sql
-- Descripción: Inserción completa de datos iniciales para ambos centros
-- =============================================
--
-- 🔑 CREDENCIALES PARA PRUEBAS (password: admin123 para todos):
--
-- 👨‍💼 ADMINISTRADORES:
--   • admin.norte  (María González)   - Centro Norte
--   • admin.sur    (Carlos Rodríguez) - Centro Sur
--
-- 🩺 TERAPEUTAS:
--   • terapeuta.ana          (Ana Martínez)    - Centro Norte - Terapia del Lenguaje
--   • fisioterapeuta.luis    (Luis Pérez)      - Centro Norte - Fisioterapia
--   • terapeuta.laura        (Laura Mendoza)   - Centro Sur   - Terapia del Lenguaje
--   • terapeuta.diego        (Diego Vargas)    - Centro Sur   - Terapia Ocupacional
--
-- 👩‍🏫 PEDAGOGOS:
--   • pedagoga.carmen        (Carmen Flores)   - Centro Norte - Educación Especial
--   • pedagogo.sandra        (Sandra López)    - Centro Sur   - Educación Especial
--   • pedagogo.miguel        (Miguel Torres)   - Centro Sur   - Desarrollo Cognitivo
--
-- 📊 DISTRIBUCIÓN DE DATOS PARA PRUEBAS RBAC:
--   Centro Norte: 3 pacientes, 3 personal (2 terapeutas + 1 pedagoga)
--   Centro Sur:   2 pacientes, 4 personal (2 terapeutas + 2 pedagogos)
--
-- =============================================

-- =============================================
-- CONFIGURACIÓN INICIAL
-- =============================================

-- Configurar esquema por defecto
SET search_path TO public;

-- =============================================
-- 1. CENTROS DE ATENCIÓN
-- =============================================

INSERT INTO centros (nombre, codigo, direccion, telefono, email, horario_apertura, horario_cierre, turno_principal, observaciones) VALUES 
('Centro Norte', 'NORTE', 'Av. Principal Norte #123, Sector Norte', '02-234-5678', 'norte@centrotiaglenda.com', '07:00', '15:00', 'matutino', 'Centro especializado en atención matutina'),
('Centro Sur', 'SUR', 'Calle Central Sur #456, Sector Sur', '02-345-6789', 'sur@centrotiaglenda.com', '13:00', '19:00', 'vespertino', 'Centro especializado en atención vespertina');

-- =============================================
-- 2. ROLES DEL SISTEMA
-- =============================================

INSERT INTO rol (nombre, descripcion, estado) VALUES
('Administrador', 'Acceso completo al sistema, gestión de usuarios y centros', 'activo'),
('Terapeuta', 'Personal especializado en terapias, gestión de pacientes asignados', 'activo'),
('Pedagógico', 'Personal especializado en educación, gestión de estudiantes', 'activo');

-- =============================================
-- 3. ESPECIALIDADES
-- =============================================

INSERT INTO especialidad (nombre, area, estado) VALUES
-- Especialidades Terapéuticas
('Terapia del Lenguaje', 'Especialidad terapéutica', 'activo'),
('Terapia Ocupacional', 'Especialidad terapéutica', 'activo'),
('Fisioterapia', 'Especialidad terapéutica', 'activo'),
('Terapia Psicológica', 'Especialidad terapéutica', 'activo'),

-- Especialidades Pedagógicas  
('Educación Especial', 'Especialidad pedagógica', 'activo'),
('Apoyo Académico', 'Especialidad pedagógica', 'activo'),
('Desarrollo Cognitivo', 'Especialidad pedagógica', 'activo');

-- =============================================
-- 4. PERSONAS - CENTRO NORTE
-- =============================================

-- Administrador Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('María', 'González', '1234567890', '0987654321', 'maria.gonzalez@centrotiaglenda.com', 'Av. 10 de Agosto #123', '1985-05-15', 'activo');

-- Personal Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Ana', 'Martínez', '1234567892', '0987654323', 'ana.martinez@centrotiaglenda.com', 'Av. Norte #789', '1990-03-10', 'activo'),
('Luis', 'Pérez', '1234567893', '0987654324', 'luis.perez@centrotiaglenda.com', 'Calle Norte #012', '1988-11-25', 'activo'),
('Carmen', 'Flores', '1234567906', '0987654333', 'carmen.flores@centrotiaglenda.com', 'Av. Norte #345', '1987-08-14', 'activo');

-- Tutores Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Carmen', 'Vásquez', '1234567896', '0987654327', 'carmen.vasquez@gmail.com', 'Av. Amazonas #901', '1978-04-12', 'activo'),
('Roberto', 'Jiménez', '1234567897', '0987654328', 'roberto.jimenez@gmail.com', 'Calle Pichincha #234', '1975-09-30', 'activo'),
('María Elena', 'Vega', '1234567908', '0987654335', 'maria.vega@gmail.com', 'Av. Norte #567', '1981-12-05', 'activo');

-- Pacientes Centro Norte
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Sebastián', 'Vásquez', '1234567900', '0987654327', NULL, 'Av. Amazonas #901', '2018-06-15', 'activo'), -- 6 años
('Valentina', 'Jiménez', '1234567901', '0987654328', NULL, 'Calle Pichincha #234', '2017-03-08', 'activo'), -- 7 años
('Ana Sofía', 'Rodríguez Vega', '1234567907', '0987654334', NULL, 'Av. Norte #567', '2016-10-22', 'activo'); -- 8 años

-- =============================================
-- 5. PERSONAS - CENTRO SUR
-- =============================================

-- Administrador Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Carlos', 'Rodríguez', '1234567891', '0987654322', 'carlos.rodriguez@centrotiaglenda.com', 'Calle Bolívar #456', '1982-08-20', 'activo');

-- Personal Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Sandra', 'López', '1234567894', '0987654325', 'sandra.lopez@centrotiaglenda.com', 'Av. Sur #345', '1987-12-03', 'activo'),
('Miguel', 'Torres', '1234567895', '0987654326', 'miguel.torres@centrotiaglenda.com', 'Calle Sur #678', '1985-07-18', 'activo'),
('Laura', 'Mendoza', '1234567904', '0987654331', 'laura.mendoza@centrotiaglenda.com', 'Av. Sur #789', '1989-04-15', 'activo'),
('Diego', 'Vargas', '1234567905', '0987654332', 'diego.vargas@centrotiaglenda.com', 'Calle Sur #012', '1986-09-22', 'activo');

-- Tutores Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Elena', 'Morales', '1234567898', '0987654329', 'elena.morales@gmail.com', 'Av. Patria #567', '1980-01-22', 'activo'),
('Patricia', 'Silva', '1234567899', '0987654330', 'patricia.silva@gmail.com', 'Calle Sur #890', '1983-06-18', 'activo');

-- Pacientes Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Mateo', 'Morales', '1234567902', '0987654329', NULL, 'Av. Patria #567', '2019-11-20', 'activo'), -- 5 años
('Isabella', 'Silva', '1234567903', '0987654330', NULL, 'Calle Sur #890', '2016-09-12', 'activo'); -- 8 años

-- =============================================
-- 6. USUARIOS DEL SISTEMA
-- =============================================

-- Administradores
INSERT INTO usuario (usuario, contrasenia, estado, id_persona, id_rol, id_centro, fecha_ultimo_acceso) VALUES
('admin.norte', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567890'), 
    (SELECT id FROM rol WHERE nombre = 'Administrador'), 
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL), -- password: admin123

('admin.sur', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567891'), 
    (SELECT id FROM rol WHERE nombre = 'Administrador'), 
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL); -- password: admin123

-- Personal Centro Norte
INSERT INTO usuario (usuario, contrasenia, estado, id_persona, id_rol, id_centro, fecha_ultimo_acceso) VALUES
('terapeuta.ana', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567892'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL), -- password: admin123
('fisioterapeuta.luis', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567893'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL), -- password: admin123
('pedagoga.carmen', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567906'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL); -- password: admin123

-- Personal Centro Sur
INSERT INTO usuario (usuario, contrasenia, estado, id_persona, id_rol, id_centro, fecha_ultimo_acceso) VALUES
('pedagogo.sandra', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567894'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL), -- password: admin123
('pedagogo.miguel', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567895'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL), -- password: admin123
('terapeuta.laura', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567904'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL), -- password: admin123
('terapeuta.diego', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567905'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL); -- password: admin123

-- =============================================
-- 7. PERSONAL DEL CENTRO
-- =============================================

-- Personal Centro Norte
INSERT INTO personal (id_persona, id_especialidad, id_centro, fecha_ingreso, cargo, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567892'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'),
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 '2024-01-01', 'Licenciada en Terapia del Lenguaje', 'activo'), -- Ana Martínez
((SELECT id FROM persona WHERE cedula = '1234567893'),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia'),
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 '2024-01-01', 'Licenciado en Fisioterapia', 'activo'), -- Luis Pérez
((SELECT id FROM persona WHERE cedula = '1234567906'),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'),
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 '2024-01-01', 'Licenciada en Educación Especial', 'activo'); -- Carmen Flores

-- Personal Centro Sur
INSERT INTO personal (id_persona, id_especialidad, id_centro, fecha_ingreso, cargo, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567894'),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'),
 (SELECT id FROM centros WHERE codigo = 'SUR'),
 '2024-01-01', 'Licenciada en Educación Especial', 'activo'), -- Sandra López
((SELECT id FROM persona WHERE cedula = '1234567895'),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo'),
 (SELECT id FROM centros WHERE codigo = 'SUR'),
 '2024-01-01', 'Licenciado en Psicología Educativa', 'activo'), -- Miguel Torres
((SELECT id FROM persona WHERE cedula = '1234567904'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'),
 (SELECT id FROM centros WHERE codigo = 'SUR'),
 '2024-01-01', 'Licenciada en Terapia del Lenguaje', 'activo'), -- Laura Mendoza
((SELECT id FROM persona WHERE cedula = '1234567905'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional'),
 (SELECT id FROM centros WHERE codigo = 'SUR'),
 '2024-01-01', 'Licenciado en Terapia Ocupacional', 'activo'); -- Diego Vargas

-- =============================================
-- 8. ESPECIALIDADES DEL PERSONAL
-- =============================================

-- Centro Norte - Ana Martínez (Terapia del Lenguaje)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567892')), 
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'), 
 TRUE); -- Terapia del Lenguaje

-- Centro Norte - Luis Pérez (Fisioterapia)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567893')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia'),
 TRUE); -- Fisioterapia

-- Centro Norte - Carmen Flores (Educación Especial)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567906')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'),
 TRUE); -- Educación Especial

-- Centro Norte - Especialidades adicionales (Fase 2)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal, fecha_asignacion, observaciones, usuario_creacion) VALUES
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567892')), 
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica'), 
 FALSE, CURRENT_DATE, 'Especialidad secundaria en terapia psicológica', 
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'));

-- Centro Sur - Sandra López (Educación Especial)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567894')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'),
 TRUE); -- Educación Especial

-- Centro Sur - Miguel Torres (Desarrollo Cognitivo)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567895')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo'),
 TRUE); -- Desarrollo Cognitivo

-- Centro Sur - Laura Mendoza (Terapia del Lenguaje)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567904')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'),
 TRUE); -- Terapia del Lenguaje

-- Centro Sur - Diego Vargas (Terapia Ocupacional)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567905')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional'),
 TRUE); -- Terapia Ocupacional

-- Centro Sur - Especialidades adicionales (Fase 2)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal, fecha_asignacion, observaciones, usuario_creacion) VALUES
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567894')), 
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico'), 
 FALSE, CURRENT_DATE, 'Especialidad secundaria en apoyo académico', 
 (SELECT id FROM usuario WHERE usuario = 'admin.sur')),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567895')), 
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'), 
 FALSE, CURRENT_DATE, 'Especialidad secundaria en educación especial', 
 (SELECT id FROM usuario WHERE usuario = 'admin.sur'));

-- =============================================
-- 9. TUTORES
-- =============================================

-- Centro Norte
INSERT INTO tutor (id_persona, parentesco, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567896'), 'madre', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567897'), 'padre', 'activo'),
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
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567896')), -- Carmen (madre)
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 '2024-01-15', 'Dificultades en el lenguaje expresivo', 'Paciente colaborador, motivado por actividades lúdicas', 'activo'),

((SELECT id FROM persona WHERE cedula = '1234567901'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567897')), -- Roberto (padre)
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 '2024-01-20', 'Desarrollo motor fino', 'Niña muy activa, responde bien a rutinas estructuradas', 'activo'),

((SELECT id FROM persona WHERE cedula = '1234567907'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567908')), -- María Elena (madre)
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 '2024-02-10', 'Apoyo académico en lectoescritura', 'Estudiante dedicada, necesita refuerzo en comprensión lectora', 'activo');

-- Centro Sur
INSERT INTO paciente (id_persona, id_tutor, id_centro, fecha_ingreso, motivo_consulta, observaciones, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567902'), 
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567898')), -- Elena (madre)
 (SELECT id FROM centros WHERE codigo = 'SUR'), 
 '2024-02-01', 'Apoyo en lectoescritura', 'Niño tímido pero receptivo, le gustan los cuentos', 'activo'),

((SELECT id FROM persona WHERE cedula = '1234567903'), 
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567899')), -- Patricia (madre)
 (SELECT id FROM centros WHERE codigo = 'SUR'), 
 '2024-02-05', 'Refuerzo académico en matemáticas', 'Estudiante dedicada, necesita apoyo en cálculo mental', 'activo');

-- =============================================
-- 11. ESPECIALIDADES DE PACIENTES
-- =============================================

-- Centro Norte - Sebastián (Terapia del Lenguaje)
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal) VALUES
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567900')), -- Sebastián
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'), 
 TRUE);

-- Centro Norte - Valentina (Fisioterapia)
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal) VALUES
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567901')), -- Valentina
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia'),
 TRUE);

-- Centro Norte - Ana Sofía (Educación Especial)
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal) VALUES
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567907')), -- Ana Sofía
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'),
 TRUE);

-- Centro Sur - Mateo (Educación Especial)
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal) VALUES
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567902')), -- Mateo
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'), 
 TRUE);

-- Centro Sur - Isabella (Apoyo Académico)
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal) VALUES
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567903')), -- Isabella
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico'), 
 TRUE);

-- =============================================
-- 12. SESIONES TERAPÉUTICAS
-- =============================================

-- Sesión de Terapia del Lenguaje - Centro Norte
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad, 
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES (
    'ST-2025-0001',
    'Terapia del Lenguaje - Comunicación Expresiva',
    'Mejorar la comunicación expresiva y comprensiva del paciente mediante terapia lúdica con actividades interactivas y material visual',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567892')), -- Ana Martínez
    (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'),
    '2025-01-15', '2025-06-15',
    ARRAY['lunes', 'miercoles'], '08:00', '08:45', 45,
    24, 5, 25000.00, 600000.00,
    'individual', 'en_curso', 
    (SELECT id FROM centros WHERE codigo = 'NORTE'),
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
);

-- Sesión de Fisioterapia - Centro Norte
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES (
    'ST-2025-0002',
    'Fisioterapia - Motricidad Fina',
    'Fortalecer la motricidad fina y coordinación mediante ejercicios progresivos con material adaptado y juegos motores',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567893')), -- Luis Pérez
    (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia'),
    '2025-01-20', '2025-07-20',
    ARRAY['martes', 'jueves'], '09:00', '09:45', 45,
    16, 6, 30000.00, 480000.00,
    'individual', 'en_curso',
    (SELECT id FROM centros WHERE codigo = 'NORTE'),
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
);

-- Sesión de Terapia del Lenguaje - Centro Sur
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES (
    'ST-2025-0003',
    'Terapia del Lenguaje Centro Sur',
    'Desarrollar habilidades de comunicación oral y comprensión mediante actividades interactivas y material visual',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567904')), -- Laura Mendoza
    (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'),
    '2025-02-01', '2025-08-01',
    ARRAY['lunes', 'miercoles'], '14:00', '14:45', 45,
    20, 6, 25000.00, 500000.00,
    'individual', 'planificada',
    (SELECT id FROM centros WHERE codigo = 'SUR'),
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
);

-- Sesión de Terapia Ocupacional - Centro Sur
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES (
    'ST-2025-0004',
    'Terapia Ocupacional Centro Sur',
    'Mejorar la independencia funcional y habilidades de la vida diaria mediante actividades terapéuticas estructuradas',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567905')), -- Diego Vargas
    (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional'),
    '2025-02-03', '2025-09-03',
    ARRAY['martes', 'viernes'], '15:00', '15:45', 45,
    18, 7, 28000.00, 504000.00,
    'individual', 'planificada',
    (SELECT id FROM centros WHERE codigo = 'SUR'),
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
);

-- =============================================
-- 13. SESIONES PEDAGÓGICAS
-- =============================================

-- Sesión de Educación Especial - Centro Norte
INSERT INTO sesion_pedagogica (
    codigo_sesion, id_educador, id_especialidad, nombre_clase, descripcion,
    fecha_inicio, fecha_fin, nivel_academico, grado_escolar, materia,
    competencias_objetivo, metodologia_ensenanza, duracion_minutos,
    frecuencia_semanal, dias_semana, hora_inicio, hora_fin, aula,
    capacidad_maxima, estado, id_centro
) VALUES (
    'SP-2025-0003',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567906')), -- Carmen Flores
    (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'),
    'Apoyo en Lectoescritura Norte', 'Desarrollo de habilidades de lectura y escritura para estudiantes del Centro Norte',
    '2025-01-08', '2025-07-08', 'primaria', '2do', 'Lenguaje',
    'Comprensión lectora, escritura creativa, vocabulario básico',
    'Método multisensorial con apoyo visual y actividades lúdicas', 60,
    2, ARRAY['martes', 'jueves'], '08:00', '09:00', 'Aula Norte 1',
    4, 'en_curso', (SELECT id FROM centros WHERE codigo = 'NORTE')
);

-- Sesión de Educación Especial - Centro Sur
INSERT INTO sesion_pedagogica (
    codigo_sesion, id_educador, id_especialidad, nombre_clase, descripcion,
    fecha_inicio, fecha_fin, nivel_academico, grado_escolar, materia,
    competencias_objetivo, metodologia_ensenanza, duracion_minutos,
    frecuencia_semanal, dias_semana, hora_inicio, hora_fin, aula,
    capacidad_maxima, estado, id_centro
) VALUES (
    'SP-2025-0004',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567894')), -- Sandra López
    (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'),
    'Lectoescritura Inicial', 'Desarrollo de habilidades básicas de lectura y escritura',
    '2025-01-10', '2025-08-10', 'preescolar', 'preparatoria', 'Lenguaje',
    'Reconocimiento de letras, formación de palabras, comprensión lectora básica',
    'Método fonético con apoyo visual y material manipulativo', 60,
    3, ARRAY['lunes', 'miércoles', 'viernes'], '14:00', '15:00', 'Aula 1',
    6, 'en_curso', (SELECT id FROM centros WHERE codigo = 'SUR')
);

-- Sesión de Apoyo Académico - Centro Sur
INSERT INTO sesion_pedagogica (
    codigo_sesion, id_educador, id_especialidad, nombre_clase, descripcion,
    fecha_inicio, fecha_fin, nivel_academico, grado_escolar, materia,
    competencias_objetivo, metodologia_ensenanza, duracion_minutos,
    frecuencia_semanal, dias_semana, hora_inicio, hora_fin, aula,
    capacidad_maxima, estado, id_centro
) VALUES (
    'SP-2025-0005',
    (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567895')), -- Miguel Torres
    (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo'),
    'Matemáticas Básicas', 'Refuerzo en operaciones matemáticas fundamentales',
    '2025-01-15', '2025-09-15', 'primaria', '3ero', 'Matemáticas',
    'Suma, resta, multiplicación básica, resolución de problemas simples',
    'Aprendizaje con material concreto y juegos matemáticos', 60,
    2, ARRAY['martes', 'jueves'], '15:00', '16:00', 'Aula 2',
    4, 'en_curso', (SELECT id FROM centros WHERE codigo = 'SUR')
);

-- =============================================
-- 14. INSCRIPCIONES EN SESIONES
-- =============================================

-- Inscripciones en Sesiones Terapéuticas
INSERT INTO sesion_paciente (id_sesion, id_paciente, fecha_inscripcion, estado, observaciones) VALUES
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2025-0001'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567900')), -- Sebastián
 '2025-01-15', 'activo', 'Paciente motivado y colaborador'),

((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2025-0002'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567901')), -- Valentina
 '2025-01-20', 'activo', 'Requiere motivación adicional para actividades');

-- Inscripciones en Sesiones Pedagógicas
INSERT INTO sesion_estudiante (id_sesion, id_paciente, fecha_inscripcion, nivel_actual, adaptaciones_requeridas, estado, observaciones) VALUES
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2025-0003'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567907')), -- Ana Sofía
 '2025-01-08', '2do grado', 'Refuerzo visual, tiempo adicional para lectura', 'activo', 'Estudiante motivada, le gustan las actividades grupales'),

((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2025-0004'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567902')), -- Mateo
 '2025-01-10', 'pre-lectura', 'Material visual ampliado, tiempo adicional', 'activo', 'Responde bien a estímulos visuales'),

((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2025-0005'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567903')), -- Isabella
 '2025-01-15', '3er grado', 'Explicaciones paso a paso, ejercicios graduales', 'activo', 'Estudiante persistente, necesita refuerzo positivo');

-- =============================================
-- 15. CRONOGRAMAS (GENERACIÓN AUTOMÁTICA)
-- =============================================

-- NOTA: Los cronogramas se generan automáticamente cuando se crean las sesiones
-- a través del SesionTerapiaComponent.create_sesion() y SesionPedagogicaComponent.create_sesion()
-- en el código Python. No es necesario generar cronogramas manualmente aquí.
-- 
-- Para generar cronogramas manualmente (opcional), usar las APIs:
-- POST /api/sesiones-terapia/{id}/cronograma/generar
-- POST /api/sesiones-pedagogicas/{id}/cronograma/generar

-- Cronogramas de ejemplo generados automáticamente:

-- Cronograma para ST-2025-0001 (24 sesiones, lunes y miércoles)
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT 
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2025-0001'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '08:00'::time,
    '08:45'::time,
    'programada',
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series(
        '2025-01-15'::date,
        '2025-06-15'::date,
        '1 day'::interval
    ) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3) -- lunes=1, miércoles=3
LIMIT 24;

-- Cronograma para ST-2025-0002 (16 sesiones, martes y jueves)
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2025-0002'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '09:00'::time,
    '09:45'::time,
    'programada',
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series(
        '2025-01-20'::date,
        '2025-07-20'::date,
        '1 day'::interval
    ) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4) -- martes=2, jueves=4
LIMIT 16;

-- Cronograma para ST-2025-0003 (20 sesiones, lunes y miércoles) - Centro Sur
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2025-0003'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '14:00'::time,
    '14:45'::time,
    'programada',
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
FROM (
    SELECT generate_series(
        '2025-02-01'::date,
        '2025-08-01'::date,
        '1 day'::interval
    ) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3) -- lunes=1, miércoles=3
LIMIT 20;

-- Cronograma para ST-2025-0004 (18 sesiones, martes y viernes) - Centro Sur
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2025-0004'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '15:00'::time,
    '15:45'::time,
    'programada',
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
FROM (
    SELECT generate_series(
        '2025-02-03'::date,
        '2025-09-03'::date,
        '1 day'::interval
    ) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 5) -- martes=2, viernes=5
LIMIT 18;

-- Cronograma para SP-2025-0003 (Apoyo en Lectoescritura Norte, martes y jueves)
INSERT INTO cronograma_clases (id_sesion, numero_clase_semanal, fecha_programada, hora_inicio, hora_fin, estado, tema_clase, usuario_creacion)
SELECT
    (SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2025-0003'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '08:00'::time,
    '09:00'::time,
    'programada',
    'Desarrollo de habilidades de lectura y escritura',
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series(
        '2025-01-08'::date,
        '2025-07-08'::date,
        '1 day'::interval
    ) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4) -- martes=2, jueves=4
LIMIT 48; -- 2 clases por semana durante 6 meses

-- Cronograma para SP-2025-0004 (Lectoescritura Inicial Centro Sur, lunes, miércoles, viernes)
INSERT INTO cronograma_clases (id_sesion, numero_clase_semanal, fecha_programada, hora_inicio, hora_fin, estado, tema_clase, usuario_creacion)
SELECT
    (SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2025-0004'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '14:00'::time,
    '15:00'::time,
    'programada',
    'Reconocimiento de letras y formación de palabras',
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
FROM (
    SELECT generate_series(
        '2025-01-10'::date,
        '2025-08-10'::date,
        '1 day'::interval
    ) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3, 5) -- lunes=1, miércoles=3, viernes=5
LIMIT 84; -- 3 clases por semana durante 7 meses

-- Cronograma para SP-2025-0005 (Matemáticas Básicas Centro Sur, martes y jueves)
INSERT INTO cronograma_clases (id_sesion, numero_clase_semanal, fecha_programada, hora_inicio, hora_fin, estado, tema_clase, usuario_creacion)
SELECT
    (SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2025-0005'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '15:00'::time,
    '16:00'::time,
    'programada',
    'Operaciones matemáticas básicas',
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
FROM (
    SELECT generate_series(
        '2025-01-15'::date,
        '2025-09-15'::date,
        '1 day'::interval
    ) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4) -- martes=2, jueves=4
LIMIT 64; -- 2 clases por semana durante 8 meses

-- =============================================
-- 16. DATOS DE ASISTENCIA DE EJEMPLO
-- =============================================

-- Crear algunas asistencias de ejemplo para demostración
-- (Solo para las primeras sesiones de cada cronograma)

-- Asistencias Sesión Terapéutica ST-2025-0001 (Sebastián)
INSERT INTO asistencia_sesiones (
    id_cronograma, id_paciente, asistio, hora_llegada, hora_salida,
    estado_asistencia, observaciones_terapeuta, objetivos_trabajados,
    progreso_observado, calificacion_sesion
)
SELECT 
    cs.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567900')),
    true, '08:00', '08:45', 'presente',
    'Sesión productiva, paciente colaborador',
    'Articulación de fonemas /r/ y /l/',
    'Mejora notable en pronunciación',
    4
FROM cronograma_sesiones cs
JOIN sesion_terapia st ON cs.id_sesion = st.id
WHERE st.codigo_sesion = 'ST-2025-0001'
AND cs.fecha_programada <= CURRENT_DATE
LIMIT 5;

-- Asistencias Sesión Fisioterapia ST-2025-0002 (Valentina)
INSERT INTO asistencia_sesiones (
    id_cronograma, id_paciente, asistio, hora_llegada, hora_salida,
    estado_asistencia, observaciones_terapeuta, objetivos_trabajados,
    progreso_observado, calificacion_sesion
)
SELECT 
    cs.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567901')),
    true, '09:00', '09:45', 'presente',
    'Excelente disposición para los ejercicios',
    'Fortalecimiento de pinza digital y coordinación',
    'Mejoras en fuerza y precisión',
    5
FROM cronograma_sesiones cs
JOIN sesion_terapia st ON cs.id_sesion = st.id
WHERE st.codigo_sesion = 'ST-2025-0002'
AND cs.fecha_programada <= CURRENT_DATE
LIMIT 4;

-- Asistencias Sesión Pedagógica SP-2025-0003 (Ana Sofía - Centro Norte)
INSERT INTO asistencia_clases (
    id_cronograma, id_paciente, asistio, hora_llegada, hora_salida,
    estado_asistencia, observaciones_educador, participacion_clase,
    comprension_tema, actividades_completadas, calificacion_clase
)
SELECT
    cc.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567907')),
    true, '08:00', '09:00', 'presente',
    'Excelente participación en actividades de lectura',
    'buena', 'buena', true, 8
FROM cronograma_clases cc
JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
WHERE sp.codigo_sesion = 'SP-2025-0003'
AND cc.fecha_programada <= CURRENT_DATE
LIMIT 6;

-- Asistencias Sesión Pedagógica SP-2025-0004 (Mateo - Centro Sur)
INSERT INTO asistencia_clases (
    id_cronograma, id_paciente, asistio, hora_llegada, hora_salida,
    estado_asistencia, observaciones_educador, participacion_clase,
    comprension_tema, actividades_completadas, calificacion_clase
)
SELECT
    cc.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567902')),
    true, '14:00', '15:00', 'presente',
    'Responde bien a estímulos visuales en lectoescritura',
    'buena', 'buena', true, 7
FROM cronograma_clases cc
JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
WHERE sp.codigo_sesion = 'SP-2025-0004'
AND cc.fecha_programada <= CURRENT_DATE
LIMIT 5;

-- Asistencias Sesión Pedagógica SP-2025-0005 (Isabella - Matemáticas Centro Sur)
INSERT INTO asistencia_clases (
    id_cronograma, id_paciente, asistio, hora_llegada, hora_salida,
    estado_asistencia, observaciones_educador, participacion_clase,
    comprension_tema, actividades_completadas, calificacion_clase,
    evaluacion_comportamiento
)
SELECT
    cc.id,
    (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567903')),
    true, '15:00', '16:00', 'presente',
    'Muy dedicada en resolver ejercicios matemáticos',
    'excelente', 'buena', true, 9, 'excelente'
FROM cronograma_clases cc
JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
WHERE sp.codigo_sesion = 'SP-2025-0005'
AND cc.fecha_programada <= CURRENT_DATE
LIMIT 5;

-- =============================================
-- 17. MENSAJES DE EJEMPLO
-- =============================================

-- Mensajes entre personal
INSERT INTO mensajes_chat (
    id_remitente, id_destinatario, mensaje, tipo_mensaje, prioridad,
    id_centro, leido
) VALUES
((SELECT id FROM usuario WHERE usuario = 'admin.norte'),
 (SELECT id FROM usuario WHERE usuario = 'terapeuta.ana'),
 'Recuerda completar el informe de progreso de Sebastián para la reunión del viernes.',
 'texto', 'normal',
 (SELECT id FROM centros WHERE codigo = 'NORTE'), false),

((SELECT id FROM usuario WHERE usuario = 'terapeuta.ana'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'),
 'Perfecto, ya está casi listo. Lo enviaré mañana.',
 'texto', 'normal',
 (SELECT id FROM centros WHERE codigo = 'NORTE'), false);

-- =============================================
-- 18. OBSERVACIONES DE EJEMPLO
-- =============================================

-- Observaciones de sesiones
INSERT INTO observaciones_sesiones (
    id_sesion, tipo_sesion, id_usuario, observacion, tipo_observacion,
    categoria, nivel_importancia, id_paciente
) VALUES
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-2025-0001'),
 'terapeutica',
 (SELECT id FROM usuario WHERE usuario = 'terapeuta.ana'),
 'El paciente muestra gran interés por las actividades con cuentos. Se recomienda incorporar más material narrativo.',
 'progreso', 'academico', 'medio',
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567900'))),

((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-2025-0004'),
 'pedagogica',
 (SELECT id FROM usuario WHERE usuario = 'pedagogo.sandra'),
 'Mateo necesita más tiempo para procesar las instrucciones. Considerar pausas más largas entre actividades.',
 'observacion', 'metodologico', 'medio',
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567902')));

-- =============================================
-- 19. VERIFICACIÓN FINAL
-- =============================================

-- Mostrar resumen de datos insertados
DO $$
DECLARE
    centros_count INTEGER;
    personas_count INTEGER;
    usuarios_count INTEGER;
    personal_count INTEGER;
    pacientes_count INTEGER;
    sesiones_t_count INTEGER;
    sesiones_p_count INTEGER;
    cronograma_s_count INTEGER;
    cronograma_c_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO centros_count FROM centros;
    SELECT COUNT(*) INTO personas_count FROM persona;
    SELECT COUNT(*) INTO usuarios_count FROM usuario;
    SELECT COUNT(*) INTO personal_count FROM personal;
    SELECT COUNT(*) INTO pacientes_count FROM paciente;
    SELECT COUNT(*) INTO sesiones_t_count FROM sesion_terapia;
    SELECT COUNT(*) INTO sesiones_p_count FROM sesion_pedagogica;
    SELECT COUNT(*) INTO cronograma_s_count FROM cronograma_sesiones;
    SELECT COUNT(*) INTO cronograma_c_count FROM cronograma_clases;

    RAISE NOTICE '=== RESUMEN DE DATOS INSERTADOS ===';
    RAISE NOTICE 'Centros: %', centros_count;
    RAISE NOTICE 'Personas: %', personas_count;
    RAISE NOTICE 'Usuarios: %', usuarios_count;
    RAISE NOTICE 'Personal: %', personal_count;
    RAISE NOTICE 'Pacientes: %', pacientes_count;
    RAISE NOTICE 'Sesiones Terapéuticas: %', sesiones_t_count;
    RAISE NOTICE 'Sesiones Pedagógicas: %', sesiones_p_count;
    RAISE NOTICE 'Cronograma Sesiones: %', cronograma_s_count;
    RAISE NOTICE 'Cronograma Clases: %', cronograma_c_count;
    RAISE NOTICE '=== DATOS CARGADOS EXITOSAMENTE ===';
END $$;

-- =============================================
-- 20. CONSULTAS DE VERIFICACIÓN
-- =============================================

-- Verificar usuarios y sus centros
SELECT 
    u.usuario,
    p.nombre || ' ' || p.apellido as nombre_completo,
    r.nombre as rol,
    c.nombre as centro
FROM usuario u
JOIN persona p ON u.id_persona = p.id  
JOIN rol r ON u.id_rol = r.id
JOIN centros c ON u.id_centro = c.id
ORDER BY c.nombre, r.nombre;

-- Verificar pacientes y sus especialidades
SELECT 
    p.nombre || ' ' || p.apellido as paciente,
    e.nombre as especialidad,
    pe.es_principal,
    c.nombre as centro
FROM paciente pac
JOIN persona p ON pac.id_persona = p.id
JOIN paciente_especialidades pe ON pac.id = pe.id_paciente
JOIN especialidad e ON pe.id_especialidad = e.id
JOIN centros c ON pac.id_centro = c.id
ORDER BY c.nombre, p.apellido;