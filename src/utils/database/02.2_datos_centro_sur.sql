-- =============================================
-- CENTRO TÍA GLENDA - DATOS INICIALES CENTRO SUR
-- Archivo: 02.2_datos_centro_sur.sql
-- IMPORTANTE: Ejecutar después de 02.1_datos_centro_norte.sql
-- =============================================

-- =============================================
-- 1. DATOS INICIALES - CENTRO SUR
-- =============================================
INSERT INTO centros (nombre, codigo, direccion, telefono, email, horario_apertura, horario_cierre, turno_principal, observaciones) VALUES 
('Centro Sur', 'SUR', 'Calle Central Sur #456, Sector Sur', '02-345-6789', 'sur@centrotiaglenda.com', '13:00', '19:00', 'vespertino', 'Centro especializado en atención vespertina');

-- =============================================
-- 2. PERSONAS - ADMINISTRADOR Y PERSONAL CENTRO SUR
-- =============================================

-- Administrador Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Carlos', 'Rodríguez', '1234567891', '0987654322', 'carlos.rodriguez@centrotiaglenda.com', 'Calle Bolívar #456', '1982-08-20', 'activo');

-- Personal Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Sandra', 'López', '1234567894', '0987654325', 'sandra.lopez@centrotiaglenda.com', 'Av. Sur #345', '1987-07-18', 'activo'),
('Miguel', 'Torres', '1234567895', '0987654326', 'miguel.torres@centrotiaglenda.com', 'Calle Sur #678', '1991-12-05', 'activo');

-- =============================================
-- 3. USUARIOS DEL SISTEMA - CENTRO SUR
-- =============================================

-- Asegurar que los roles necesarios existen (en caso de que no se ejecutó 02.1)
INSERT INTO rol (nombre, descripcion, estado) VALUES
('Administrador', 'Acceso completo al sistema, gestión de usuarios y centros', 'activo'),
('Terapeuta', 'Personal especializado en terapias, gestión de pacientes asignados', 'activo'),
('Pedagógico', 'Personal especializado en educación, gestión de estudiantes', 'activo')
ON CONFLICT (nombre) DO NOTHING;

-- Administrador Centro Sur
INSERT INTO usuario (usuario, contrasenia, estado, persona_id, rol_id, id_centro, fecha_ultimo_acceso) VALUES
('admin.sur', '$2b$12$HGyK9EndrLNZNiG3p2t9MOBM.2xxSFC51DKePTxgM83vnz.4D2LIm', 'activo', 
    (SELECT id FROM persona WHERE cedula = '1234567891'), 
    (SELECT id FROM rol WHERE nombre = 'Administrador'), 
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL); -- password: admin123

-- Personal Centro Sur
INSERT INTO usuario (usuario, contrasenia, estado, persona_id, rol_id, id_centro, fecha_ultimo_acceso) VALUES
('pedagogo.sandra', '$2b$12$HGyK9EndrLNZNiG3p2t9MOBM.2xxSFC51DKePTxgM83vnz.4D2LIm', 'activo', 
    (SELECT id FROM persona WHERE cedula = '1234567894'), 
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'), 
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL), -- password: admin123
('pedagogo.miguel', '$2b$12$HGyK9EndrLNZNiG3p2t9MOBM.2xxSFC51DKePTxgM83vnz.4D2LIm', 'activo', 
    (SELECT id FROM persona WHERE cedula = '1234567895'), 
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'), 
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL); -- password: admin123

-- =============================================
-- 4. PERSONAL DEL CENTRO SUR
-- =============================================
INSERT INTO personal (persona_id, id_especialidad, id_centro, fecha_ingreso, cargo, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567894'), 
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'), 
 (SELECT id FROM centros WHERE codigo = 'SUR'), 
 '2024-01-01', 'Licenciada en Educación Especial', 'activo'), -- Sandra López
((SELECT id FROM persona WHERE cedula = '1234567895'), 
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo'), 
 (SELECT id FROM centros WHERE codigo = 'SUR'), 
 '2024-01-01', 'Licenciado en Psicología Educativa', 'activo'); -- Miguel Torres

-- =============================================
-- 5. ESPECIALIDADES DEL PERSONAL - CENTRO SUR
-- =============================================

-- Sandra López - Educación Especial (Centro Sur)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567894')), 
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'), 
 TRUE); -- Educación Especial

-- Miguel Torres - Desarrollo Cognitivo (Centro Sur)
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
((SELECT id FROM personal WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567895')), 
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo'), 
 TRUE); -- Desarrollo Cognitivo

-- *** FASE 2: MÚLTIPLES ESPECIALIDADES PARA PERSONAL ***
-- Sandra también puede dar Apoyo Académico
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal, fecha_asignacion, observaciones, usuario_creacion) VALUES
((SELECT id FROM personal WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567894')), 
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico'), 
 FALSE, CURRENT_DATE, 'Especialidad secundaria en apoyo académico', 
 (SELECT id FROM usuario WHERE usuario = 'admin.sur'));

-- Miguel también puede dar Educación Especial
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal, fecha_asignacion, observaciones, usuario_creacion) VALUES
((SELECT id FROM personal WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567895')), 
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'), 
 FALSE, CURRENT_DATE, 'Especialidad secundaria en educación especial', 
 (SELECT id FROM usuario WHERE usuario = 'admin.sur'));

-- =============================================
-- 6. PERSONAS - TUTORES Y PACIENTES CENTRO SUR
-- =============================================

-- Tutores Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Elena', 'Morales', '1234567898', '0987654329', 'elena.morales@gmail.com', 'Av. Patria #567', '1980-01-22', 'activo'),
('Patricia', 'Silva', '1234567899', '0987654330', 'patricia.silva@gmail.com', 'Calle Sur #890', '1983-06-18', 'activo');

-- Pacientes Centro Sur
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Mateo', 'Morales', '1234567902', '0987654329', NULL, 'Av. Patria #567', '2019-11-20', 'activo'), -- 5 años
('Isabella', 'Silva', '1234567903', '0987654330', NULL, 'Calle Sur #890', '2016-09-12', 'activo'); -- 8 años

-- =============================================
-- 7. TUTORES - CENTRO SUR
-- =============================================
INSERT INTO tutor (nombre, apellido, cedula, telefono, email, direccion, parentesco, estado) VALUES
('Elena', 'Morales', '1234567898', '0987654329', 'elena.morales@gmail.com', 'Av. Patria #567', 'madre', 'activo'),
('Patricia', 'Silva', '1234567899', '0987654330', 'patricia.silva@gmail.com', 'Calle Sur #890', 'madre', 'activo');

-- =============================================
-- 8. PACIENTES - CENTRO SUR
-- =============================================

-- Pacientes Centro Sur (Horario vespertino) 
INSERT INTO paciente (persona_id, id_tutor, id_centro, fecha_ingreso, motivo_consulta, observaciones, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567902'), -- Mateo
 (SELECT id FROM tutor WHERE cedula = '1234567898'), -- Elena (madre)
 (SELECT id FROM centros WHERE codigo = 'SUR'), 
 '2024-03-01', 'Necesita apoyo en habilidades sociales y educación especial', 'Niño tímido pero receptivo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567903'), -- Isabella
 (SELECT id FROM tutor WHERE cedula = '1234567899'), -- Patricia (madre)
 (SELECT id FROM centros WHERE codigo = 'SUR'), 
 '2024-03-15', 'Estimulación del desarrollo cognitivo y habilidades intelectuales', 'Niña muy inteligente y curiosa', 'activo');

-- *** ESPECIALIDADES PARA PACIENTES ***
-- Mateo - Educación Especial (principal)
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal, fecha_asignacion, fecha_inicio_tratamiento, observaciones, usuario_creacion) VALUES
((SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567902')), -- Mateo
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'), 
 TRUE, '2024-03-01', '2024-03-08', 'Especialidad principal - Educación Especial', 
 (SELECT id FROM usuario WHERE usuario = 'admin.sur'));

-- Mateo también recibe Apoyo Académico
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal, fecha_asignacion, fecha_inicio_tratamiento, observaciones, usuario_creacion) VALUES
((SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567902')), -- Mateo
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico'), 
 FALSE, '2024-03-15', '2024-03-22', 'Apoyo académico complementario', 
 (SELECT id FROM usuario WHERE usuario = 'admin.sur'));

-- Isabella - Desarrollo Cognitivo (principal)
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal, fecha_asignacion, fecha_inicio_tratamiento, observaciones, usuario_creacion) VALUES
((SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567903')), -- Isabella
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo'), 
 TRUE, '2024-03-15', '2024-03-22', 'Especialidad principal - Desarrollo Cognitivo', 
 (SELECT id FROM usuario WHERE usuario = 'admin.sur'));

-- Isabella también recibe Educación Especial
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal, fecha_asignacion, fecha_inicio_tratamiento, observaciones, usuario_creacion) VALUES
((SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567903')), -- Isabella
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'), 
 FALSE, '2024-04-01', '2024-04-08', 'Educación especial complementaria', 
 (SELECT id FROM usuario WHERE usuario = 'admin.sur'));

-- *** FASE 2: EJEMPLO DE PAUSA POR ESPECIALIDAD ***
-- Pausar temporalmente el tratamiento de Apoyo Académico de Mateo
UPDATE paciente_especialidades 
SET estado_pausa = 'pausado_especialidad',
    fecha_inicio_pausa_esp = '2024-06-01',
    motivo_pausa_esp = 'Vacaciones escolares - Pausa temporal durante periodo vacacional'
WHERE id_paciente = (SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567902'))
  AND id_especialidad = (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico');

-- =============================================
-- 9. SESIONES PEDAGÓGICAS - CENTRO SUR
-- =============================================

-- Sesión Centro Sur - Educación Especial
INSERT INTO sesion_pedagogica (
    id_educador, id_especialidad, id_centro, nombre_clase, descripcion, fecha_inicio, fecha_fin,
    dias_semana, hora_inicio, duracion_minutos, nivel_academico, 
    frecuencia_semanal, capacidad_maxima, estado, usuario_creacion
) VALUES (
    (SELECT id FROM personal WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567894')), -- Sandra López
    (SELECT id FROM especialidad WHERE nombre = 'Educación Especial'), 
    (SELECT id FROM centros WHERE codigo = 'SUR'), 
    'Educación Especial - Tarde',
    'Clase vespertina de educación especial con metodología especializada',
    '2025-02-15',
    '2025-05-15',
    ARRAY['martes', 'jueves'],
    '15:00',
    60,
    'preescolar',
    2,
    8,
    'planificada',
    (SELECT id FROM usuario WHERE usuario = 'admin.sur')
);

-- =============================================
-- 10. ASIGNACIÓN DE ESTUDIANTES A SESIONES - CENTRO SUR
-- =============================================

-- Estudiantes en sesión pedagógica (Centro Sur)
INSERT INTO sesion_estudiante (id_sesion, id_paciente, fecha_inscripcion, nivel_actual, observaciones, estado, usuario_creacion) VALUES
((SELECT id FROM sesion_pedagogica WHERE nombre_clase = 'Educación Especial - Tarde'), 
 (SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567902')), -- Mateo
 '2025-02-15', 'preescolar', 'Mateo - Educación especial vespertina', 'activo', 
 (SELECT id FROM usuario WHERE usuario = 'admin.sur')),
((SELECT id FROM sesion_pedagogica WHERE nombre_clase = 'Educación Especial - Tarde'), 
 (SELECT id FROM paciente WHERE persona_id = (SELECT id FROM persona WHERE cedula = '1234567903')), -- Isabella
 '2025-02-15', 'primaria', 'Isabella - Desarrollo cognitivo complementario', 'activo', 
 (SELECT id FROM usuario WHERE usuario = 'admin.sur'));

-- =============================================
-- 11. GENERAR CRONOGRAMAS AUTOMÁTICOS - CENTRO SUR
-- =============================================

-- Generar cronograma para sesión pedagógica
SELECT generar_cronograma_sesion_pedagogica(
    (SELECT id FROM sesion_pedagogica WHERE nombre_clase = 'Educación Especial - Tarde')
);


-- =============================================
-- 13. MENSAJE DE FINALIZACIÓN
-- =============================================
SELECT 'Datos iniciales Centro Sur insertados exitosamente (incluye FASE 2)' AS mensaje;

-- =============================================
-- 14. INFORMACIÓN DE USUARIOS CREADOS - CENTRO SUR
-- =============================================
SELECT 'USUARIOS CENTRO SUR - Contraseña para todos: admin123' AS info;
SELECT 
    u.usuario, 
    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo, 
    r.nombre as rol, 
    c.nombre as centro 
FROM usuario u
JOIN persona p ON u.persona_id = p.id  
JOIN rol r ON u.rol_id = r.id
JOIN centros c ON u.id_centro = c.id
WHERE c.codigo = 'SUR'
ORDER BY r.nombre;

-- =============================================
-- 15. RESUMEN DE DATOS - CENTRO SUR
-- =============================================
/*
============================================================================
DATOS CENTRO SUR CREADOS:
============================================================================
✓ 1 Centro (Sur - Vespertino)
✓ 3 Usuarios (1 admin, 2 pedagogos)
✓ 2 Personal profesional con múltiples especialidades
✓ 2 Tutores y 2 Pacientes
✓ 1 Sesión pedagógica con cronograma automático
✓ FASE 2: Especialidades múltiples y pausas implementadas
✓ FASE 2: 4 documentos de ejemplo para el personal

CREDENCIALES DE ACCESO CENTRO SUR:
- admin.sur / admin123 (Administrador)
- pedagogo.sandra / admin123 (Pedagogo - Educación Especial/Apoyo Académico)
- pedagogo.miguel / admin123 (Pedagogo - Desarrollo Cognitivo/Educación Especial)

PACIENTES CON ESPECIALIDADES MÚLTIPLES:
- Mateo: Educación Especial (principal) + Apoyo Académico (pausado)
- Isabella: Desarrollo Cognitivo (principal) + Educación Especial

DOCUMENTOS DEL PERSONAL:
- Sandra López: Cédula + Título Universitario
- Miguel Torres: CV + Certificado (con vencimiento)

CASOS DE PRUEBA FASE 2:
✓ Especialidades múltiples para personal y pacientes
✓ Control de pausas por especialidad (Mateo - Apoyo Académico pausado)
✓ Sistema de documentos con metadatos y fechas de vencimiento
============================================================================
*/