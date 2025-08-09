-- =============================================
-- CENTRO TÍA GLENDA - DATOS INICIALES PARA RAILWAY
-- Archivo: 02_datos_iniciales_railway.sql
-- Adaptado para Railway (sin \c centro_tia_glenda)
-- =============================================

-- =============================================
-- IMPORTANTE: No necesitamos \c centro_tia_glenda
-- Railway ya está conectado a la base de datos correcta
-- =============================================

-- =============================================
-- 1. CATÁLOGOS BÁSICOS INDEPENDIENTES
-- =============================================

-- =============================================
-- 1.1 ROLES DEL SISTEMA
-- =============================================
INSERT INTO rol (nombre, descripcion) VALUES 
('Administrador', 'Acceso completo al sistema. Puede gestionar usuarios, configuraciones y generar todos los reportes'),
('Terapeuta', 'Personal del área terapéutica. Acceso a gestión de pacientes y tratamientos'),
('Pedagógico', 'Personal del área pedagógica. Acceso a gestión de alumnos y seguimiento académico'),
('Cliente', 'Cliente externo. Solo consulta de información pública e horarios disponibles');

-- =============================================
-- 1.2 ESPECIALIDADES DEL CENTRO
-- =============================================

-- Especialidades Terapéuticas
INSERT INTO especialidad (nombre, descripcion, area) VALUES 
('Terapia del Lenguaje', 'Tratamiento de trastornos de comunicación, habla y lenguaje', 'terapeutico'),
('Fisioterapia', 'Rehabilitación física y motora', 'terapeutico'),
('Terapia Ocupacional', 'Desarrollo de habilidades para actividades de la vida diaria', 'terapeutico'),
('Psicología Clínica', 'Evaluación y tratamiento de trastornos psicológicos', 'terapeutico'),
('Fonoaudiología', 'Rehabilitación de trastornos de la audición y comunicación', 'terapeutico'),
('Neuropsicología', 'Evaluación y rehabilitación de funciones cognitivas', 'terapeutico');

-- Especialidades Pedagógicas
INSERT INTO especialidad (nombre, descripcion, area) VALUES 
('Educación Inicial', 'Atención pedagógica para niños de 0-5 años', 'pedagogico'),
('Educación Especial', 'Apoyo pedagógico para estudiantes con necesidades especiales', 'pedagogico'),
('Psicopedagogía', 'Intervención en dificultades de aprendizaje', 'pedagogico'),
('Estimulación Temprana', 'Desarrollo integral en primeros años de vida', 'pedagogico'),
('Apoyo Académico', 'Refuerzo educativo en materias específicas', 'pedagogico'),
('Lectoescritura', 'Enseñanza y refuerzo de habilidades de lectura y escritura', 'pedagogico');

-- =============================================
-- 2. DATOS ADMINISTRATIVOS INICIALES
-- =============================================

-- =============================================
-- 2.1 PERSONA ADMINISTRADOR PRINCIPAL
-- =============================================
INSERT INTO persona (
    nombre, 
    apellido, 
    cedula, 
    telefono, 
    correo, 
    direccion,
    fecha_nacimiento
) VALUES (
    'Glenda María', 
    'Administradora Centro', 
    '1234567890', 
    '+593999123456', 
    'admin@centro-tia-glenda.com', 
    'Centro Tía Glenda - Dirección Principal',
    '1985-05-15'
);

-- =============================================
-- 2.2 USUARIO ADMINISTRADOR PRINCIPAL
-- =============================================
-- Password: Admin123! (hasheado)
INSERT INTO usuario (
    persona_id, 
    rol_id, 
    username, 
    password_hash
) VALUES (
    1,
    (SELECT id FROM rol WHERE nombre = 'Administrador'),
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LQ4lqO.aDwQiOZ9QPQO3QVz3qgzqD4z5rQZwW'
);

-- =============================================
-- 2.3 PERSONAL ADMINISTRATIVO
-- =============================================
INSERT INTO personal (
    persona_id, 
    codigo_empleado, 
    fecha_ingreso,
    observaciones
) VALUES (
    1,
    'CTG-001',
    '2024-01-01',
    'Administrador principal del sistema'
);

-- =============================================
-- 3. DATOS DE EJEMPLO PARA DESARROLLO
-- =============================================

-- =============================================
-- 3.1 PERSONAL TERAPÉUTICO DE EJEMPLO
-- =============================================
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, fecha_nacimiento) VALUES 
('Ana María', 'González López', '1234567891', '+593999123457', 'ana.gonzalez@centro-tia-glenda.com', '1988-03-20'),
('Carlos Eduardo', 'Ramírez Silva', '1234567892', '+593999123458', 'carlos.ramirez@centro-tia-glenda.com', '1985-11-10'),
('María José', 'Fernández Torres', '1234567893', '+593999123459', 'maria.fernandez@centro-tia-glenda.com', '1990-07-25');

INSERT INTO personal (persona_id, codigo_empleado, fecha_ingreso, observaciones) VALUES 
(2, 'CTG-002', '2024-01-15', 'Especialista en Terapia del Lenguaje'),
(3, 'CTG-003', '2024-01-15', 'Especialista en Fisioterapia'),
(4, 'CTG-004', '2024-02-01', 'Especialista en Terapia Ocupacional');

-- Asignar especialidades al personal
INSERT INTO personal_especialidad (personal_id, especialidad_id) VALUES 
(2, (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje')),
(3, (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia')),
(4, (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional'));

-- =============================================
-- 3.2 USUARIOS DEL PERSONAL
-- =============================================
-- Passwords: Terapeuta123!
INSERT INTO usuario (persona_id, rol_id, username, password_hash) VALUES 
(2, (SELECT id FROM rol WHERE nombre = 'Terapeuta'), 'ana.gonzalez', '$2b$12$LQv3c1yqBWVHxkd0LQ4lqO.aDwQiOZ9QPQO3QVz3qgzqD4z5rQZwW'),
(3, (SELECT id FROM rol WHERE nombre = 'Terapeuta'), 'carlos.ramirez', '$2b$12$LQv3c1yqBWVHxkd0LQ4lqO.aDwQiOZ9QPQO3QVz3qgzqD4z5rQZwW'),
(4, (SELECT id FROM rol WHERE nombre = 'Terapeuta'), 'maria.fernandez', '$2b$12$LQv3c1yqBWVHxkd0LQ4lqO.aDwQiOZ9QPQO3QVz3qgzqD4z5rQZwW');

-- =============================================
-- 3.3 TUTORES DE EJEMPLO
-- =============================================
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, fecha_nacimiento) VALUES 
('Patricia Elena', 'Morales Vega', '1234567894', '+593999123460', 'patricia.morales@email.com', '1982-09-12'),
('Roberto Carlos', 'Jiménez Ruiz', '1234567895', '+593999123461', 'roberto.jimenez@email.com', '1980-04-08'),
('Carmen Isabel', 'Herrera León', '1234567896', '+593999123462', 'carmen.herrera@email.com', '1985-12-03');

INSERT INTO tutor (persona_id, parentesco, es_representante_legal) VALUES 
(5, 'Madre', true),
(6, 'Padre', true),
(7, 'Madre', true);

-- =============================================
-- 3.4 PACIENTES/ESTUDIANTES DE EJEMPLO
-- =============================================
INSERT INTO persona (nombre, apellido, cedula, telefono, fecha_nacimiento) VALUES 
('Sofía Alejandra', 'Morales Jiménez', '1234567897', '+593999123463', '2018-06-15'),
('Diego Sebastián', 'González Herrera', '1234567898', '+593999123464', '2019-02-28'),
('Valentina Andrea', 'Ramírez León', '1234567899', '+593999123465', '2017-10-10');

INSERT INTO paciente (persona_id, codigo_paciente, fecha_ingreso, motivo_ingreso) VALUES 
(8, 'PAC-001', '2024-03-01', 'Dificultades en el desarrollo del lenguaje'),
(9, 'PAC-002', '2024-03-01', 'Retraso en desarrollo motor'),
(10, 'PAC-003', '2024-03-05', 'Apoyo en proceso de aprendizaje');

-- Asignar tutores a pacientes
INSERT INTO paciente_tutor (paciente_id, tutor_id, es_principal) VALUES 
(1, 1, true),  -- Sofía -> Patricia (madre)
(2, 2, true),  -- Diego -> Roberto (padre) 
(3, 3, true);  -- Valentina -> Carmen (madre)

-- Asignar especialidades a pacientes
INSERT INTO paciente_especialidad (paciente_id, especialidad_id) VALUES 
(1, (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje')),
(2, (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia')),
(3, (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico'));

-- =============================================
-- 3.5 SESIONES DE EJEMPLO
-- =============================================

-- Sesiones terapéuticas
INSERT INTO sesion_terapeutica (
    paciente_id, 
    personal_id, 
    especialidad_id, 
    fecha_programada, 
    hora_inicio, 
    hora_fin,
    observaciones_pre
) VALUES 
(1, 2, (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'), '2024-08-12', '09:00', '09:45', 'Primera sesión de evaluación'),
(1, 2, (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje'), '2024-08-14', '09:00', '09:45', 'Continuidad del tratamiento'),
(2, 3, (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia'), '2024-08-12', '10:00', '10:45', 'Evaluación inicial motora');

-- Sesión pedagógica grupal
INSERT INTO sesion_pedagogica (
    personal_id,
    especialidad_id,
    nombre_sesion,
    descripcion,
    fecha_programada,
    hora_inicio,
    hora_fin,
    capacidad_maxima
) VALUES (
    4,
    (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico'),
    'Refuerzo de Lectoescritura - Nivel Inicial',
    'Sesión grupal para reforzar habilidades básicas de lectura y escritura',
    '2024-08-15',
    '14:00',
    '15:00',
    6
);

-- Inscribir estudiantes a la sesión pedagógica
INSERT INTO sesion_pedagogica_estudiante (sesion_pedagogica_id, paciente_id) VALUES 
(1, 3);

-- =============================================
-- 4. VERIFICACIÓN DE DATOS INSERTADOS
-- =============================================

-- Mostrar resumen de datos creados
SELECT 'Roles creados' as tabla, COUNT(*) as registros FROM rol
UNION ALL
SELECT 'Especialidades creadas' as tabla, COUNT(*) as registros FROM especialidad
UNION ALL
SELECT 'Personas creadas' as tabla, COUNT(*) as registros FROM persona
UNION ALL
SELECT 'Usuarios creados' as tabla, COUNT(*) as registros FROM usuario
UNION ALL
SELECT 'Personal creado' as tabla, COUNT(*) as registros FROM personal
UNION ALL
SELECT 'Tutores creados' as tabla, COUNT(*) as registros FROM tutor
UNION ALL
SELECT 'Pacientes creados' as tabla, COUNT(*) as registros FROM paciente
UNION ALL
SELECT 'Sesiones terapéuticas' as tabla, COUNT(*) as registros FROM sesion_terapeutica
UNION ALL
SELECT 'Sesiones pedagógicas' as tabla, COUNT(*) as registros FROM sesion_pedagogica
ORDER BY tabla;

-- =============================================
-- FIN DEL SCRIPT DE DATOS INICIALES
-- =============================================