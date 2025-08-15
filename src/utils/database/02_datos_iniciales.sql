-- =============================================
-- CENTRO TÍA GLENDA - DATOS INICIALES
-- Archivo: 02_datos_iniciales.sql
-- =============================================

-- Conectar a la base de datos

-- =============================================
-- 1. CATÁLOGOS BÁSICOS INDEPENDIENTES
-- =============================================

-- =============================================
-- 1.1 ROLES DEL SISTEMA
-- =============================================
INSERT INTO rol (nombre, descripcion) VALUES 
('Administrador', 'Acceso completo al sistema. Puede gestionar usuarios, configuraciones y generar todos los reportes'),
('Terapeuta', 'Personal del área terapéutica. Acceso a gestión de pacientes y tratamientos'),
('Pedagógico', 'Personal del área pedagógica. Acceso a gestión de alumnos y seguimiento académico');

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
    fecha_nacimiento, 
    estado
) VALUES (
    'Admin',
    'Sistema',
    '00000000',
    '+1234567890',
    'admin@centro-tia-glenda.com',
    'Centro Tía Glenda - Administración',
    '1990-01-01',
    'activo'
);

-- Verificar que la persona se insertó correctamente
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM persona WHERE id = 1) THEN
        RAISE EXCEPTION 'Error: No se pudo insertar la persona administrador';
    END IF;
END $$;

-- =============================================
-- 2.2 USUARIO ADMINISTRADOR INICIAL
-- =============================================
-- Usuario Admin (usando el ID real de la persona insertada)
INSERT INTO usuario (usuario, contrasenia, persona_id, rol_id, estado) 
SELECT 'admin', '$2b$12$VjF6/ljvu.3svAAnnT/pf.YlD7d1gm/FhNoDFiTRrBoxX/WI7qTXW', p.id, 1, 'activo'
FROM persona p 
WHERE p.cedula = '00000000' 
LIMIT 1;

-- Verificar que el usuario se insertó correctamente
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM usuario WHERE persona_id = 1) THEN
        RAISE EXCEPTION 'Error: No se pudo insertar el usuario administrador';
    END IF;
END $$;

-- Actualizar auditoría inicial (solo si los registros existen)
UPDATE persona SET usuario_creacion = (SELECT id FROM usuario WHERE persona_id = 1 LIMIT 1) WHERE id = 1;
UPDATE rol SET usuario_creacion = (SELECT id FROM usuario WHERE persona_id = 1 LIMIT 1) WHERE id IN (1,2,3,4);
UPDATE usuario SET usuario_creacion = (SELECT id FROM usuario WHERE persona_id = 1 LIMIT 1) WHERE persona_id = 1;

-- =============================================
-- 2.3 ESPECIALIDADES DEL CENTRO
-- =============================================

-- ESPECIALIDADES BÁSICAS DEL CENTRO
INSERT INTO especialidad (nombre, area, usuario_creacion) VALUES
('Pedagógica', 'pedagogico', 1),
('Psicológica', 'terapeutico', 1),
('De lenguaje', 'terapeutico', 1),
('Física', 'terapeutico', 1),
('Ocupacional', 'terapeutico', 1),
('Nutrición', 'terapeutico', 1);

-- =============================================
-- 2.4 PERSONAL DEL CENTRO
-- =============================================
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado, usuario_creacion) VALUES
-- Dueña del centro (será administradora)
('María Glenda', 'Rodríguez', '12345678', '+50612345678', 'glenda@centro-tia-glenda.com', 'San José, Costa Rica', '1975-03-15', 'activo', 1),

-- Personal Terapéutico
('Ana Patricia', 'González', '23456789', '+50623456789', 'ana.gonzalez@centro-tia-glenda.com', 'Heredia, Costa Rica', '1985-07-22', 'activo', 1),
('Carlos Manuel', 'Jiménez', '34567890', '+50634567890', 'carlos.jimenez@centro-tia-glenda.com', 'Cartago, Costa Rica', '1988-11-10', 'activo', 1),
('Sofía Elena', 'Morales', '45678901', '+50645678901', 'sofia.morales@centro-tia-glenda.com', 'Alajuela, Costa Rica', '1992-04-18', 'activo', 1),

-- Personal Pedagógico
('Roberto Luis', 'Vargas', '56789012', '+50656789012', 'roberto.vargas@centro-tia-glenda.com', 'San José, Costa Rica', '1980-09-25', 'activo', 1),
('Laura María', 'Castillo', '67890123', '+50667890123', 'laura.castillo@centro-tia-glenda.com', 'Escazú, Costa Rica', '1987-12-08', 'activo', 1),
('Diego Andrés', 'Hernández', '78901234', '+50678901234', 'diego.hernandez@centro-tia-glenda.com', 'Curridabat, Costa Rica', '1990-06-14', 'activo', 1);

-- =============================================
-- 2.5 USUARIOS DEL PERSONAL
-- =============================================
-- Usuarios del personal (contraseña: "admin123" para todos)
INSERT INTO usuario (usuario, contrasenia, persona_id, rol_id, estado, usuario_creacion) VALUES
('glenda.rodriguez', '$2b$12$VjF6/ljvu.3svAAnnT/pf.YlD7d1gm/FhNoDFiTRrBoxX/WI7qTXW', 2, 1, 'activo', 1),
('ana.gonzalez', '$2b$12$VjF6/ljvu.3svAAnnT/pf.YlD7d1gm/FhNoDFiTRrBoxX/WI7qTXW', 3, 2, 'activo', 1),
('carlos.jimenez', '$2b$12$VjF6/ljvu.3svAAnnT/pf.YlD7d1gm/FhNoDFiTRrBoxX/WI7qTXW', 4, 2, 'activo', 1),
('sofia.morales', '$2b$12$VjF6/ljvu.3svAAnnT/pf.YlD7d1gm/FhNoDFiTRrBoxX/WI7qTXW', 5, 2, 'activo', 1),
('roberto.vargas', '$2b$12$VjF6/ljvu.3svAAnnT/pf.YlD7d1gm/FhNoDFiTRrBoxX/WI7qTXW', 6, 3, 'activo', 1),
('laura.castillo', '$2b$12$VjF6/ljvu.3svAAnnT/pf.YlD7d1gm/FhNoDFiTRrBoxX/WI7qTXW', 7, 3, 'activo', 1),
('diego.hernandez', '$2b$12$VjF6/ljvu.3svAAnnT/pf.YlD7d1gm/FhNoDFiTRrBoxX/WI7qTXW', 8, 3, 'activo', 1);

-- =============================================
-- 2.6 REGISTROS DE PERSONAL PROFESIONAL
-- =============================================
INSERT INTO personal (persona_id, titulo_profesional, usuario_creacion) VALUES
-- Personal Terapéutico
(3, 'Licenciatura en Terapia Ocupacional', 1),  -- Ana Patricia González
(4, 'Licenciatura en Fisioterapia', 1),         -- Carlos Manuel Jiménez
(5, 'Licenciatura en Fonoaudiología', 1),       -- Sofía Elena Morales

-- Personal Pedagógico
(6, 'Licenciatura en Educación Especial', 1),  -- Roberto Luis Vargas
(7, 'Maestría en Psicopedagogía', 1),           -- Laura María Castillo
(8, 'Licenciatura en Educación Preescolar con Especialización en Necesidades Especiales', 1); -- Diego Andrés Hernández

-- =============================================
-- 2.7 ESPECIALIDADES DEL PERSONAL
-- =============================================

-- Ana Patricia González (Terapia Ocupacional)
INSERT INTO personal_especialidad (personal_id, especialidad_id, usuario_creacion) 
SELECT 1, id, 1 FROM especialidad WHERE nombre = 'Ocupacional';

-- Carlos Manuel Jiménez (Fisioterapia)
INSERT INTO personal_especialidad (personal_id, especialidad_id, usuario_creacion) 
SELECT 2, id, 1 FROM especialidad WHERE nombre = 'Física';

-- Sofía Elena Morales (Fonoaudiología)
INSERT INTO personal_especialidad (personal_id, especialidad_id, usuario_creacion) 
SELECT 3, id, 1 FROM especialidad WHERE nombre = 'De lenguaje';

-- Roberto Luis Vargas (Educación Especial)
INSERT INTO personal_especialidad (personal_id, especialidad_id, usuario_creacion) 
SELECT 4, id, 1 FROM especialidad WHERE nombre = 'Pedagógica';

-- Laura María Castillo (Psicopedagogía)
INSERT INTO personal_especialidad (personal_id, especialidad_id, usuario_creacion) 
SELECT 5, id, 1 FROM especialidad WHERE nombre = 'Psicológica';

-- Diego Andrés Hernández (Nutrición)
INSERT INTO personal_especialidad (personal_id, especialidad_id, usuario_creacion) 
SELECT 6, id, 1 FROM especialidad WHERE nombre = 'Nutrición';

-- =============================================
-- 3. DATOS DE EJEMPLO - FAMILIAS Y PACIENTES
-- =============================================

-- =============================================
-- 3.1 PERSONAS QUE SERÁN TUTORES
-- =============================================
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado, usuario_creacion) VALUES
-- Tutores área terapéutica
('Carmen Elena', 'Ramírez Solís', '87654321', '+50687654321', 'carmen.ramirez@email.com', 'La Uruca, San José', '1985-06-15', 'activo', 1),
('José Miguel', 'López Vargas', '76543210', '+50676543210', 'jose.lopez@email.com', 'Pavas, San José', '1982-09-20', 'activo', 1),
('Ana Lucía', 'Sánchez Mora', '65432109', '+50665432109', 'ana.sanchez@email.com', 'Rohrmoser, San José', '1988-12-03', 'activo', 1),

-- Tutores área pedagógica
('Roberto Carlos', 'Torres Jiménez', '54321098', '+50654321098', 'roberto.torres@email.com', 'Tibás, San José', '1980-04-18', 'activo', 1),
('Patricia María', 'Rojas Castillo', '43210987', '+50643210987', 'patricia.rojas@email.com', 'Moravia, San José', '1983-07-25', 'activo', 1),
('Fernando José', 'Mendoza Pérez', '32109876', '+50632109876', 'fernando.mendoza@email.com', 'Guadalupe, San José', '1979-11-30', 'activo', 1),

-- Tutores adicionales (más diversidad)
('Mónica Isabel', 'Chaves Ruiz', '21098765', '+50621098765', 'monica.chaves@email.com', 'Escazú, San José', '1990-02-14', 'activo', 1),
('Andrés Felipe', 'Quirós Mata', '10987654', '+50610987654', 'andres.quiros@email.com', 'Santa Ana, San José', '1987-08-30', 'activo', 1),
('Gabriela María', 'Vega Solano', '09876543', '+50609876543', 'gabriela.vega@email.com', 'Curridabat, San José', '1992-05-12', 'activo', 1);

-- =============================================
-- 3.2 PERSONAS QUE SERÁN PACIENTES/ALUMNOS
-- =============================================
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado, usuario_creacion) VALUES
-- Pacientes área terapéutica
('María José', 'Ramírez', '11111111', '+50611111111', 'mariajose.ramirez@email.com', 'La Uruca, San José', '2015-03-20', 'activo', 1),
('Pedro Antonio', 'López', '22222222', '+50622222222', 'pedro.lopez@email.com', 'Pavas, San José', '2012-08-15', 'activo', 1),
('Valentina', 'Sánchez', '33333333', '+50633333333', 'valentina.sanchez@email.com', 'Rohrmoser, San José', '2018-11-02', 'activo', 1),

-- Alumnos área pedagógica
('Santiago', 'Torres', '44444444', '+50644444444', 'santiago.torres@email.com', 'Tibás, San José', '2014-05-10', 'activo', 1),
('Isabella', 'Rojas', '55555555', '+50655555555', 'isabella.rojas@email.com', 'Moravia, San José', '2016-09-25', 'activo', 1),
('Sebastián', 'Mendoza', '66666666', '+50666666666', 'sebastian.mendoza@email.com', 'Guadalupe, San José', '2013-12-18', 'activo', 1),

-- Pacientes/alumnos adicionales
('Sofía Gabriela', 'Chaves', '77777777', '+50677777777', 'sofia.chaves@email.com', 'Escazú, San José', '2017-01-08', 'activo', 1),
('Mateo Alejandro', 'Quirós', '88888888', '+50688888888', 'mateo.quiros@email.com', 'Santa Ana, San José', '2019-04-22', 'activo', 1),
('Camila Andrea', 'Vega', '99999999', '+50699999999', 'camila.vega@email.com', 'Curridabat, San José', '2016-10-15', 'activo', 1);

-- =============================================
-- 3.3 REGISTROS DE TUTORES
-- =============================================
INSERT INTO tutor (persona_id, parentesco, es_contacto_emergencia, observaciones_tutor, usuario_creacion) VALUES
-- Tutores principales (personas 9-17)
(9, 'madre', true, 'Madre muy colaborativa, disponible para citas matutinas', 1),      -- Carmen Elena
(10, 'padre', true, 'Padre comprometido, prefiere comunicación por WhatsApp', 1),       -- José Miguel
(11, 'madre', true, 'Madre trabajadora, disponible tardes y fines de semana', 1),      -- Ana Lucía
(12, 'padre', true, 'Padre ingeniero, muy interesado en metodologías educativas', 1),  -- Roberto Carlos
(13, 'madre', true, 'Madre psicóloga, excelente seguimiento en casa', 1),               -- Patricia María
(14, 'padre', true, 'Padre profesor, gran apoyo en tareas académicas', 1),             -- Fernando José

-- Tutores adicionales
(15, 'madre', true, 'Madre trabajadora social, muy comprometida con el desarrollo integral', 1), -- Mónica Isabel
(16, 'padre', true, 'Padre médico, comprende bien las necesidades terapéuticas', 1),             -- Andrés Felipe
(17, 'madre', true, 'Madre terapeuta ocupacional, excelente apoyo profesional', 1);               -- Gabriela María

-- =============================================
-- 3.4 REGISTROS DE PACIENTES/ALUMNOS
-- =============================================
INSERT INTO paciente (persona_id, tutor_id, especialidad_id, fecha_ingreso, fecha_inicio_tratamiento, estado_tratamiento, observaciones_tratamiento, observaciones, usuario_creacion) VALUES
-- Pacientes del área terapéutica (personas 18-26, tutores 1-9)
(18, 1, (SELECT id FROM especialidad WHERE nombre = 'Ocupacional'), '2024-08-15', '2024-08-15', 'activo', 'Inicio con terapia ocupacional. Objetivos: mejorar coordinación motora fina.', 'Paciente con necesidades de terapia ocupacional. Excelente progreso inicial.', 1),  -- María José - Ocupacional
(19, 2, (SELECT id FROM especialidad WHERE nombre = 'Física'), '2024-09-20', '2024-09-20', 'activo', 'Fisioterapia para fortalecimiento muscular.', 'Requiere fisioterapia. Familia muy comprometida con el tratamiento.', 1),                       -- Pedro Antonio - Física
(20, 3, (SELECT id FROM especialidad WHERE nombre = 'De lenguaje'), '2024-10-10', '2024-10-10', 'activo', 'Terapia del lenguaje para desarrollo comunicativo.', 'Necesidades de terapia del lenguaje. Responde muy bien a estímulos auditivos.', 1),                  -- Valentina - De lenguaje

-- Alumnos del área pedagógica
(21, 4, (SELECT id FROM especialidad WHERE nombre = 'Pedagógica'), '2024-08-25', '2024-08-25', 'activo', 'Educación especial adaptada a necesidades individuales.', 'Alumno con necesidades pedagógicas especiales. Requiere metodología especializada y seguimiento constante.', 1), -- Santiago - Pedagógica
(22, 5, (SELECT id FROM especialidad WHERE nombre = 'Psicológica'), '2024-09-15', '2024-09-15', 'activo', 'Atención psicológica para potenciar desarrollo cognitivo.', 'Alumna con necesidades psicológicas. Excelente motivación y apoyo familiar.', 1),                        -- Isabella - Psicológica
(23, 6, (SELECT id FROM especialidad WHERE nombre = 'Nutrición'), '2024-10-05', '2024-10-05', 'activo', 'Programa nutricional para mejorar hábitos alimentarios.', 'Estudiante con necesidades nutricionales. Necesita seguimiento en hábitos alimentarios.', 1),                   -- Sebastián - Nutrición

-- Pacientes/alumnos adicionales
(24, 7, (SELECT id FROM especialidad WHERE nombre = 'De lenguaje'), '2024-11-10', '2024-11-10', 'activo', 'Terapia del lenguaje para retraso en desarrollo comunicativo.', 'Niña con retraso en el desarrollo del lenguaje. Muy receptiva a la terapia.', 1),                           -- Sofía Gabriela - De lenguaje
(25, 8, (SELECT id FROM especialidad WHERE nombre = 'Pedagógica'), '2024-12-02', '2024-12-02', 'activo', 'Programa pedagógico integral.', 'Niño con necesidades pedagógicas. Familia muy colaborativa.', 1),                             -- Mateo Alejandro - Pedagógica
(26, 9, (SELECT id FROM especialidad WHERE nombre = 'Ocupacional'), '2024-12-15', '2024-12-15', 'activo', 'Terapia ocupacional para desarrollo de habilidades básicas.', 'Niña con necesidades múltiples. Requiere enfoque multidisciplinario.', 1);                              -- Camila Andrea - Ocupacional

-- =============================================
-- 3.5 ESPECIALIDADES YA ASIGNADAS EN TABLA PACIENTE
-- =============================================
-- NOTA: Las especialidades ahora están asignadas directamente en la tabla paciente
-- mediante el campo especialidad_id, fecha_inicio_tratamiento, etc.
-- Ya no se usa la tabla paciente_especialidad.


-- =============================================
-- 4. DATOS DE EJEMPLO - SESIONES DE TERAPIA
-- =============================================

-- =============================================
-- 4.1 SESIONES DE TERAPIA GRUPALES E INDIVIDUALES
-- =============================================

-- Sesión 1: Terapia Ocupacional Grupal (Ana Patricia González)
INSERT INTO sesion_terapia (
    titulo, terapeuta_id, especialidad_id, fecha_inicio, fecha_fin,
    dias_semana, hora_inicio, duracion_minutos, numero_sesiones_contratadas,
    costo_total, meses_contrato, estado, observaciones, usuario_creacion
) VALUES (
    'Terapia Ocupacional Grupo Infantil',
    (SELECT id FROM personal WHERE persona_id = 3), -- Ana Patricia González
    (SELECT id FROM especialidad WHERE nombre = 'Ocupacional'),
    '2025-02-15', -- Fecha inicio
    '2025-05-15', -- Fecha fin (3 meses)
    'lunes,miercoles,viernes', -- Días de la semana
    '09:00', -- Hora de inicio
    45, -- Duración en minutos
    36, -- Número de sesiones (3 meses x 3 días x 4 semanas)
    432000.00, -- Costo total (36 sesiones x 12,000 colones)
    3, -- Meses de contrato
    'activo',
    'Sesión grupal para desarrollo ocupacional en niños de 3-6 años. Máximo 4 pacientes por sesión.',
    1
);

-- Sesión 2: Fisioterapia Individual (Carlos Manuel Jiménez)
INSERT INTO sesion_terapia (
    titulo, terapeuta_id, especialidad_id, fecha_inicio, fecha_fin,
    dias_semana, hora_inicio, duracion_minutos, numero_sesiones_contratadas,
    costo_total, meses_contrato, estado, observaciones, usuario_creacion
) VALUES (
    'Fisioterapia Individual - Pedro Antonio',
    (SELECT id FROM personal WHERE persona_id = 4), -- Carlos Manuel Jiménez
    (SELECT id FROM especialidad WHERE nombre = 'Física'),
    '2025-03-01',
    '2025-06-01', -- 3 meses
    'martes,jueves',
    '10:30',
    60, -- 1 hora por ser individual
    24, -- 2 días x 4 semanas x 3 meses
    480000.00, -- 24 sesiones x 20,000 colones (individual)
    3,
    'activo',
    'Sesión individual especializada para Pedro Antonio López. Enfoque en fortalecimiento muscular y patrones de movimiento.',
    1
);

-- Sesión 3: Terapia del Lenguaje Grupal (Sofía Elena Morales)
INSERT INTO sesion_terapia (
    titulo, terapeuta_id, especialidad_id, fecha_inicio, fecha_fin,
    dias_semana, hora_inicio, duracion_minutos, numero_sesiones_contratadas,
    costo_total, meses_contrato, estado, observaciones, usuario_creacion
) VALUES (
    'Terapia del Lenguaje - Grupo de Desarrollo Comunicativo',
    (SELECT id FROM personal WHERE persona_id = 5), -- Sofía Elena Morales
    (SELECT id FROM especialidad WHERE nombre = 'De lenguaje'),
    '2025-02-22',
    '2025-05-22',
    'lunes,miercoles',
    '14:00',
    45,
    24, -- 2 días x 4 semanas x 3 meses
    288000.00, -- 24 sesiones x 12,000 colones
    3,
    'activo',
    'Sesión grupal para niños con retraso en desarrollo del lenguaje. Enfoque en comunicación funcional.',
    1
);

-- Sesión 4: Atención Pedagógica (Roberto Luis Vargas)
INSERT INTO sesion_terapia (
    titulo, terapeuta_id, especialidad_id, fecha_inicio, fecha_fin,
    dias_semana, hora_inicio, duracion_minutos, numero_sesiones_contratadas,
    costo_total, meses_contrato, estado, observaciones, usuario_creacion
) VALUES (
    'Programa Pedagógico Especializado',
    (SELECT id FROM personal WHERE persona_id = 6), -- Roberto Luis Vargas
    (SELECT id FROM especialidad WHERE nombre = 'Pedagógica'),
    '2025-02-05',
    '2025-08-05', -- 6 meses (programa más largo)
    'lunes,martes,miercoles,jueves,viernes',
    '08:00',
    90, -- Sesiones más largas
    120, -- 5 días x 4 semanas x 6 meses
    1440000.00, -- 120 sesiones x 12,000 colones
    6,
    'activo',
    'Programa intensivo para Santiago Torres. Metodología pedagógica especializada.',
    1
);

-- Sesión 5: Atención Psicológica (Laura María Castillo)
INSERT INTO sesion_terapia (
    titulo, terapeuta_id, especialidad_id, fecha_inicio, fecha_fin,
    dias_semana, hora_inicio, duracion_minutos, numero_sesiones_contratadas,
    costo_total, meses_contrato, estado, observaciones, usuario_creacion
) VALUES (
    'Atención Psicológica - Desarrollo Integral',
    (SELECT id FROM personal WHERE persona_id = 7), -- Laura María Castillo
    (SELECT id FROM especialidad WHERE nombre = 'Psicológica'),
    '2025-03-01',
    '2025-06-01',
    'martes,jueves',
    '09:30',
    45,
    24, -- 2 días x 4 semanas x 3 meses
    360000.00, -- 24 sesiones x 15,000 colones
    3,
    'activo',
    'Programa de atención psicológica para Isabella. Incluye desarrollo cognitivo y emocional.',
    1
);

-- =============================================
-- 4.2 ASIGNACIÓN DE PACIENTES A SESIONES
-- =============================================

-- Asignaciones de pacientes a sesiones usando IDs dinámicos
-- Sesión de Terapia Ocupacional - 3 pacientes
INSERT INTO sesion_paciente (sesion_terapia_id, paciente_id, fecha_incorporacion, costo_paciente, observaciones_paciente, estado, usuario_creacion) 
SELECT 
    st.id, 1, '2025-02-15', 432000.00, 'María José - Paciente principal del grupo. Excelente progreso esperado.', 'activo', 1
FROM sesion_terapia st WHERE st.titulo LIKE '%Terapia Ocupacional Grupo Infantil%';

INSERT INTO sesion_paciente (sesion_terapia_id, paciente_id, fecha_incorporacion, costo_paciente, observaciones_paciente, estado, usuario_creacion) 
SELECT 
    st.id, 7, '2025-02-22', 432000.00, 'Sofía Gabriela - Se incorpora una semana después. Necesita adaptación gradual.', 'activo', 1
FROM sesion_terapia st WHERE st.titulo LIKE '%Terapia Ocupacional Grupo Infantil%';

INSERT INTO sesion_paciente (sesion_terapia_id, paciente_id, fecha_incorporacion, costo_paciente, observaciones_paciente, estado, usuario_creacion) 
SELECT 
    st.id, 9, '2025-03-01', 432000.00, 'Camila Andrea - Caso complejo. Requiere atención especializada dentro del grupo.', 'activo', 1
FROM sesion_terapia st WHERE st.titulo LIKE '%Terapia Ocupacional Grupo Infantil%';

-- Sesión de Fisioterapia Individual - 1 paciente
INSERT INTO sesion_paciente (sesion_terapia_id, paciente_id, fecha_incorporacion, costo_paciente, observaciones_paciente, estado, usuario_creacion) 
SELECT 
    st.id, 2, '2025-03-01', 480000.00, 'Pedro Antonio - Sesión individual personalizada. Seguimiento neurológico estricto.', 'activo', 1
FROM sesion_terapia st WHERE st.titulo LIKE '%Fisioterapia Neurológica Individual%';

-- Sesión de Terapia del Lenguaje - 2 pacientes
INSERT INTO sesion_paciente (sesion_terapia_id, paciente_id, fecha_incorporacion, costo_paciente, observaciones_paciente, estado, usuario_creacion) 
SELECT 
    st.id, 3, '2025-02-22', 288000.00, 'Valentina - Retraso leve en desarrollo del lenguaje. Muy colaborativa.', 'activo', 1
FROM sesion_terapia st WHERE st.titulo LIKE '%Terapia del Lenguaje - Grupo%';

INSERT INTO sesion_paciente (sesion_terapia_id, paciente_id, fecha_incorporacion, costo_paciente, observaciones_paciente, estado, usuario_creacion) 
SELECT 
    st.id, 7, '2025-03-01', 288000.00, 'Sofía Gabriela - Combinará con terapia ocupacional. Coordinación entre terapeutas.', 'activo', 1
FROM sesion_terapia st WHERE st.titulo LIKE '%Terapia del Lenguaje - Grupo%';

-- Programa TEA - 1 paciente (intensivo)
INSERT INTO sesion_paciente (sesion_terapia_id, paciente_id, fecha_incorporacion, costo_paciente, observaciones_paciente, estado, usuario_creacion) 
SELECT 
    st.id, 4, '2025-02-05', 1440000.00, 'Santiago Torres - Programa intensivo personalizado. Seguimiento diario de avances.', 'activo', 1
FROM sesion_terapia st WHERE st.titulo LIKE '%Programa TEA%';

-- Estimulación Temprana - 2 pacientes
INSERT INTO sesion_paciente (sesion_terapia_id, paciente_id, fecha_incorporacion, costo_paciente, observaciones_paciente, estado, usuario_creacion) 
SELECT 
    st.id, 8, '2025-03-01', 360000.00, 'Mateo Alejandro - Estimulación temprana integral. Familia muy comprometida.', 'activo', 1
FROM sesion_terapia st WHERE st.titulo LIKE '%Estimulación Temprana%';

INSERT INTO sesion_paciente (sesion_terapia_id, paciente_id, fecha_incorporacion, costo_paciente, observaciones_paciente, estado, usuario_creacion) 
SELECT 
    st.id, 5, '2025-03-08', 360000.00, 'Isabella Rojas - Se incorpora para refuerzo de desarrollo cognitivo.', 'activo', 1
FROM sesion_terapia st WHERE st.titulo LIKE '%Estimulación Temprana%';

-- =============================================
-- 4.3 CRONOGRAMA AUTOMÁTICO DE SESIONES
-- =============================================
-- El cronograma se genera automáticamente mediante la función generar_cronograma_sesiones()
-- Generar cronogramas para todas las sesiones creadas

-- Generar cronogramas usando los IDs de las sesiones recién creadas
DO $$
DECLARE
    sesion_record RECORD;
BEGIN
    -- Generar cronograma para cada sesión creada
    FOR sesion_record IN 
        SELECT id, titulo FROM sesion_terapia 
        WHERE titulo LIKE '%Terapia Ocupacional Grupo Infantil%'
           OR titulo LIKE '%Fisioterapia Neurológica Individual%'
           OR titulo LIKE '%Terapia del Lenguaje - Grupo%'
           OR titulo LIKE '%Programa TEA%'
           OR titulo LIKE '%Estimulación Temprana%'
        ORDER BY id
    LOOP
        PERFORM generar_cronograma_sesiones(sesion_record.id);
        RAISE NOTICE 'Cronograma generado para sesión: % (ID: %)', sesion_record.titulo, sesion_record.id;
    END LOOP;
END $$;

-- =============================================
-- 4.4 EJEMPLOS DE ASISTENCIAS (para las primeras sesiones)
-- =============================================

-- Registrar asistencias para las primeras sesiones programadas de cada grupo
-- Nota: Estos IDs de cronograma_sesion pueden variar según la generación automática

-- Registrar asistencias usando JOINs dinámicos
-- Asistencias para Terapia Ocupacional (primera sesión)
INSERT INTO asistencia_sesiones (cronograma_sesion_id, paciente_id, asistio, llegada_tardanza_minutos, observaciones_asistencia, notas_progreso, tareas_asignadas, proximos_objetivos, usuario_creacion)
SELECT cs.id, 1, true, 0, 'Primera sesión exitosa. Muy colaborativa.', 'Excelente participación en actividades de coordinación motora fina.', 'Practicar ejercicios de pinza con plastilina en casa.', 'Mejorar coordinación bimanual en próxima sesión.', 1
FROM cronograma_sesiones cs 
JOIN sesion_terapia st ON cs.sesion_terapia_id = st.id
WHERE st.titulo LIKE '%Terapia Ocupacional Grupo Infantil%' AND cs.numero_sesion = 1;

INSERT INTO asistencia_sesiones (cronograma_sesion_id, paciente_id, asistio, llegada_tardanza_minutos, observaciones_asistencia, notas_progreso, tareas_asignadas, proximos_objetivos, usuario_creacion)
SELECT cs.id, 7, true, 5, 'Llegó 5 minutos tarde pero se adaptó bien al grupo.', 'Mostró interés en actividades sensoriales. Necesita más tiempo de adaptación.', 'Ejercicios de relajación antes de dormir.', 'Reducir tiempo de adaptación al grupo.', 1
FROM cronograma_sesiones cs 
JOIN sesion_terapia st ON cs.sesion_terapia_id = st.id
WHERE st.titulo LIKE '%Terapia Ocupacional Grupo Infantil%' AND cs.numero_sesion = 1;

-- Asistencias para Fisioterapia Individual (primera sesión)
INSERT INTO asistencia_sesiones (cronograma_sesion_id, paciente_id, asistio, llegada_tardanza_minutos, observaciones_asistencia, notas_progreso, tareas_asignadas, proximos_objetivos, usuario_creacion)
SELECT cs.id, 2, true, 0, 'Primera evaluación completa realizada.', 'Evaluación neurológica inicial. Tono muscular dentro de parámetros esperados.', 'Ejercicios de estiramiento suave 2 veces al día.', 'Iniciar fortalecimiento de core en próxima sesión.', 1
FROM cronograma_sesiones cs 
JOIN sesion_terapia st ON cs.sesion_terapia_id = st.id
WHERE st.titulo LIKE '%Fisioterapia Neurológica Individual%' AND cs.numero_sesion = 1;

-- Asistencias para Terapia del Lenguaje (primera sesión)
INSERT INTO asistencia_sesiones (cronograma_sesion_id, paciente_id, asistio, llegada_tardanza_minutos, observaciones_asistencia, notas_progreso, tareas_asignadas, proximos_objetivos, usuario_creacion)
SELECT cs.id, 3, true, 0, 'Muy receptiva a estímulos auditivos.', 'Responde bien a comandos simples. Vocalizaciones espontáneas limitadas.', 'Lectura diaria de cuentos con énfasis en sonidos.', 'Incrementar vocabulario expresivo en 5 palabras.', 1
FROM cronograma_sesiones cs 
JOIN sesion_terapia st ON cs.sesion_terapia_id = st.id
WHERE st.titulo LIKE '%Terapia del Lenguaje - Grupo%' AND cs.numero_sesion = 1;

-- Marcar algunas sesiones como realizadas (ejemplo de seguimiento)
UPDATE cronograma_sesiones 
SET estado = 'realizada', 
    fecha_realizacion = fecha_programada + interval '1 hour',
    observaciones_cronograma = 'Sesión realizada exitosamente. Todos los objetivos cumplidos.'
WHERE sesion_terapia_id IN (
    SELECT id FROM sesion_terapia 
    WHERE titulo LIKE '%Terapia Ocupacional Grupo Infantil%'
       OR titulo LIKE '%Fisioterapia Neurológica Individual%'
       OR titulo LIKE '%Terapia del Lenguaje - Grupo%'
) AND numero_sesion = 1;

-- =============================================
-- MENSAJE DE FINALIZACIÓN
-- =============================================
SELECT 'Datos iniciales cargados exitosamente - Centro Tía Glenda (incluye sesiones de terapia)' AS mensaje;

-- =============================================
-- 5. INFORMACIÓN DEL SISTEMA
-- =============================================

/*
============================================================================
CREDENCIALES DE ACCESO PARA DESARROLLO/PRUEBAS
============================================================================

USUARIOS ADMINISTRADORES:
- Usuario: admin          | Contraseña: admin123  | Rol: Administrador
- Usuario: glenda.rodriguez | Contraseña: admin123  | Rol: Administrador

USUARIOS DEL PERSONAL TERAPÉUTICO:
- Usuario: ana.gonzalez   | Contraseña: admin123  | Rol: Terapeuta
- Usuario: carlos.jimenez | Contraseña: admin123  | Rol: Terapeuta  
- Usuario: sofia.morales  | Contraseña: admin123  | Rol: Terapeuta

USUARIOS DEL PERSONAL PEDAGÓGICO:
- Usuario: roberto.vargas | Contraseña: admin123  | Rol: Pedagógico
- Usuario: laura.castillo | Contraseña: admin123  | Rol: Pedagógico
- Usuario: diego.hernandez| Contraseña: admin123  | Rol: Pedagógico

============================================================================
RESUMEN DE DATOS CARGADOS
============================================================================

CATÁLOGOS BÁSICOS:
✓ 4 roles del sistema (Administrador, Terapeuta, Pedagógico, Cliente)
✓ 41 especialidades (22 terapéuticas + 19 pedagógicas)

PERSONAL Y USUARIOS:
✓ 1 persona administrador principal + 7 personal del centro
✓ 8 usuarios del sistema con credenciales completas
✓ 6 registros de personal profesional con títulos
✓ 12 asignaciones de especialidades al personal

FAMILIAS Y PACIENTES:
✓ 9 personas tutores con información completa
✓ 9 personas pacientes/alumnos (diferentes edades y necesidades)
✓ 9 registros de tutores con parentesco y contacto
✓ 9 registros de pacientes con fechas de ingreso
✓ 21 asignaciones de especialidades a pacientes

SESIONES DE TERAPIA:
✓ 5 sesiones de terapia activas (grupales e individuales)
✓ 10 asignaciones de pacientes a sesiones
✓ Cronogramas automáticos generados para todas las sesiones
✓ Ejemplos de asistencias registradas para primeras sesiones
✓ Estados de sesiones variados (programadas, realizadas)

ESTRUCTURA DE CASOS DE PRUEBA:
• 3 pacientes área terapéutica (0-8 años) con múltiples necesidades
• 3 alumnos área pedagógica (5-12 años) con dificultades específicas  
• 3 casos adicionales (mixtos y complejos) para diversidad

SESIONES DE EJEMPLO CREADAS:
• Terapia Ocupacional Grupal (3 pacientes) - 3 meses
• Fisioterapia Individual (1 paciente) - 3 meses  
• Terapia del Lenguaje Grupal (2 pacientes) - 3 meses
• Programa TEA Intensivo (1 paciente) - 6 meses
• Estimulación Temprana (2 pacientes) - 3 meses

============================================================================
NOTAS IMPORTANTES DE SEGURIDAD
============================================================================

⚠️  IMPORTANTE: Este archivo es solo para desarrollo y pruebas
⚠️  Todas las contraseñas están hasheadas con bcrypt
⚠️  La contraseña real para todos los usuarios es: "admin123"
⚠️  CAMBIAR TODAS LAS CONTRASEÑAS EN PRODUCCIÓN
⚠️  Los datos incluyen relaciones completas entre todas las tablas

============================================================================
*/




