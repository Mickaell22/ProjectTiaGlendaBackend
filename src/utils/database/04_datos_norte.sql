-- =============================================
-- CENTRO TIA GLENDA - DATOS MASIVOS CENTRO NORTE
-- Archivo: 04_datos_norte.sql
-- Descripcion: Datos extensivos exclusivamente para Centro Norte
-- =============================================
--
-- CONTENIDO EXCLUSIVO CENTRO NORTE:
-- - 40 pacientes adicionales
-- - 15 personal adicional (10 terapeutas + 5 pedagogos)
-- - 25 sesiones terapeuticas activas
-- - 15 sesiones pedagogicas activas
-- - Cronogramas completos con asistencias registradas
-- - Pausas de pacientes con historial
-- - Mensajes entre personal
-- - Observaciones detalladas
-- - Documentos de ejemplo
-- - Notificaciones programadas
-- =============================================

-- =============================================
-- CONFIGURACION INICIAL
-- =============================================

SET search_path TO public;

-- =============================================
-- 1. PERSONAL ADICIONAL - CENTRO NORTE
-- =============================================

-- Terapeutas especializados (10 nuevos)
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Alejandro', 'Gomez', '1235000001', '0988000001', 'alejandro.gomez@centrotiaglenda.com', 'Av. Norte #1001', '1990-01-15', 'activo'),
('Isabella', 'Ruiz', '1235000002', '0988000002', 'isabella.ruiz@centrotiaglenda.com', 'Calle Norte #1002', '1988-03-22', 'activo'),
('Martin', 'Diaz', '1235000003', '0988000003', 'martin.diaz@centrotiaglenda.com', 'Av. Norte #1003', '1991-05-10', 'activo'),
('Camila', 'Alvarez', '1235000004', '0988000004', 'camila.alvarez@centrotiaglenda.com', 'Calle Norte #1004', '1989-07-18', 'activo'),
('Sebastian', 'Romero', '1235000005', '0988000005', 'sebastian.romero@centrotiaglenda.com', 'Av. Norte #1005', '1992-09-25', 'activo'),
('Valentina', 'Mora', '1235000006', '0988000006', 'valentina.mora@centrotiaglenda.com', 'Calle Norte #1006', '1987-11-30', 'activo'),
('Nicolas', 'Luna', '1235000007', '0988000007', 'nicolas.luna@centrotiaglenda.com', 'Av. Norte #1007', '1990-02-14', 'activo'),
('Antonella', 'Vidal', '1235000008', '0988000008', 'antonella.vidal@centrotiaglenda.com', 'Calle Norte #1008', '1988-04-20', 'activo'),
('Mateo', 'Pacheco', '1235000009', '0988000009', 'mateo.pacheco@centrotiaglenda.com', 'Av. Norte #1009', '1991-06-12', 'activo'),
('Renata', 'Carrasco', '1235000010', '0988000010', 'renata.carrasco@centrotiaglenda.com', 'Calle Norte #1010', '1989-08-28', 'activo'),

-- Pedagogos especializados (5 nuevos)
('Joaquin', 'Bravo', '1235000011', '0988000011', 'joaquin.bravo@centrotiaglenda.com', 'Av. Norte #1011', '1990-10-05', 'activo'),
('Emilia', 'Santos', '1235000012', '0988000012', 'emilia.santos@centrotiaglenda.com', 'Calle Norte #1012', '1988-12-15', 'activo'),
('Lucas', 'Peña', '1235000013', '0988000013', 'lucas.pena@centrotiaglenda.com', 'Av. Norte #1013', '1991-01-20', 'activo'),
('Sofia', 'Ugarte', '1235000014', '0988000014', 'sofia.ugarte@centrotiaglenda.com', 'Calle Norte #1014', '1989-03-25', 'activo'),
('Daniel', 'Jaramillo', '1235000015', '0988000015', 'daniel.jaramillo@centrotiaglenda.com', 'Av. Norte #1015', '1992-05-30', 'activo');

-- Tutores (40 nuevos)
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Marcela', 'Cordero', '1235000020', '0988000020', 'marcela.cordero@gmail.com', 'Av. Norte #2001', '1980-01-10', 'activo'),
('Fernando', 'Salinas', '1235000021', '0988000021', 'fernando.salinas@gmail.com', 'Calle Norte #2002', '1979-02-15', 'activo'),
('Gabriela', 'Escobar', '1235000022', '0988000022', 'gabriela.escobar@gmail.com', 'Av. Norte #2003', '1982-03-20', 'activo'),
('Rodrigo', 'Montes', '1235000023', '0988000023', 'rodrigo.montes@gmail.com', 'Calle Norte #2004', '1978-04-25', 'activo'),
('Paulina', 'Araya', '1235000024', '0988000024', 'paulina.araya@gmail.com', 'Av. Norte #2005', '1981-05-30', 'activo'),
('Andres', 'Valdes', '1235000025', '0988000025', 'andres.valdes@gmail.com', 'Calle Norte #2006', '1980-06-05', 'activo'),
('Carla', 'Robles', '1235000026', '0988000026', 'carla.robles@gmail.com', 'Av. Norte #2007', '1983-07-10', 'activo'),
('Gonzalo', 'Miranda', '1235000027', '0988000027', 'gonzalo.miranda@gmail.com', 'Calle Norte #2008', '1977-08-15', 'activo'),
('Daniela', 'Caceres', '1235000028', '0988000028', 'daniela.caceres@gmail.com', 'Av. Norte #2009', '1984-09-20', 'activo'),
('Pablo', 'Fuenzalida', '1235000029', '0988000029', 'pablo.fuenzalida@gmail.com', 'Calle Norte #2010', '1979-10-25', 'activo'),
('Constanza', 'Hernandez', '1235000030', '0988000030', 'constanza.hernandez@gmail.com', 'Av. Norte #2011', '1982-11-30', 'activo'),
('Esteban', 'Saavedra', '1235000031', '0988000031', 'esteban.saavedra@gmail.com', 'Calle Norte #2012', '1978-12-05', 'activo'),
('Alejandra', 'Bustos', '1235000032', '0988000032', 'alejandra.bustos@gmail.com', 'Av. Norte #2013', '1981-01-10', 'activo'),
('Cristian', 'Pizarro', '1235000033', '0988000033', 'cristian.pizarro@gmail.com', 'Calle Norte #2014', '1980-02-15', 'activo'),
('Vanessa', 'Lillo', '1235000034', '0988000034', 'vanessa.lillo@gmail.com', 'Av. Norte #2015', '1983-03-20', 'activo'),
('Maximiliano', 'Garrido', '1235000035', '0988000035', 'maximiliano.garrido@gmail.com', 'Calle Norte #2016', '1977-04-25', 'activo'),
('Natalia', 'Acuña', '1235000036', '0988000036', 'natalia.acuna@gmail.com', 'Av. Norte #2017', '1984-05-30', 'activo'),
('Victor', 'Tapia', '1235000037', '0988000037', 'victor.tapia@gmail.com', 'Calle Norte #2018', '1979-06-05', 'activo'),
('Pamela', 'Vasquez', '1235000038', '0988000038', 'pamela.vasquez@gmail.com', 'Av. Norte #2019', '1982-07-10', 'activo'),
('Claudio', 'Neira', '1235000039', '0988000039', 'claudio.neira@gmail.com', 'Calle Norte #2020', '1978-08-15', 'activo'),
('Francisca', 'Leiva', '1235000040', '0988000040', 'francisca.leiva@gmail.com', 'Av. Norte #2021', '1981-09-20', 'activo'),
('Ignacio', 'Arce', '1235000041', '0988000041', 'ignacio.arce@gmail.com', 'Calle Norte #2022', '1980-10-25', 'activo'),
('Claudia', 'Riquelme', '1235000042', '0988000042', 'claudia.riquelme@gmail.com', 'Av. Norte #2023', '1983-11-30', 'activo'),
('Mauricio', 'Valenzuela', '1235000043', '0988000043', 'mauricio.valenzuela@gmail.com', 'Calle Norte #2024', '1777-12-05', 'activo'),
('Lorena', 'Figueroa', '1235000044', '0988000044', 'lorena.figueroa@gmail.com', 'Av. Norte #2025', '1984-01-10', 'activo'),
('Rodrigo', 'Espinoza', '1235000045', '0988000045', 'rodrigo.espinoza@gmail.com', 'Calle Norte #2026', '1979-02-15', 'activo'),
('Mariana', 'Munoz', '1235000046', '0988000046', 'mariana.munoz@gmail.com', 'Av. Norte #2027', '1982-03-20', 'activo'),
('Eduardo', 'Navarro', '1235000047', '0988000047', 'eduardo.navarro@gmail.com', 'Calle Norte #2028', '1978-04-25', 'activo'),
('Javiera', 'Gonzalez', '1235000048', '0988000048', 'javiera.gonzalez@gmail.com', 'Av. Norte #2029', '1981-05-30', 'activo'),
('Ricardo', 'Sanchez', '1235000049', '0988000049', 'ricardo.sanchez@gmail.com', 'Calle Norte #2030', '1980-06-05', 'activo'),
('Carolina', 'Castro', '1235000050', '0988000050', 'carolina.castro@gmail.com', 'Av. Norte #2031', '1783-07-10', 'activo'),
('Hector', 'Alarcon', '1235000051', '0988000051', 'hector.alarcon@gmail.com', 'Calle Norte #2032', '1777-08-15', 'activo'),
('Andrea', 'Ponce', '1235000052', '0988000052', 'andrea.ponce@gmail.com', 'Av. Norte #2033', '1984-09-20', 'activo'),
('Jorge', 'Moya', '1235000053', '0988000053', 'jorge.moya@gmail.com', 'Calle Norte #2034', '1779-10-25', 'activo'),
('Monica', 'Campos', '1235000054', '0988000054', 'monica.campos@gmail.com', 'Av. Norte #2035', '1982-11-30', 'activo'),
('Luis', 'Zamora', '1235000055', '0988000055', 'luis.zamora@gmail.com', 'Calle Norte #2036', '1778-12-05', 'activo'),
('Cecilia', 'Orellana', '1235000056', '0988000056', 'cecilia.orellana@gmail.com', 'Av. Norte #2037', '1781-01-10', 'activo'),
('Felipe', 'Arancibia', '1235000057', '0988000057', 'felipe.arancibia@gmail.com', 'Calle Norte #2038', '1780-02-15', 'activo'),
('Veronica', 'Palma', '1235000058', '0988000058', 'veronica.palma@gmail.com', 'Av. Norte #2039', '1783-03-20', 'activo'),
('Oscar', 'Ulloa', '1235000059', '0988000059', 'oscar.ulloa@gmail.com', 'Calle Norte #2040', '1777-04-25', 'activo');

-- Pacientes (40 ninos)
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Agustin', 'Cordero', '1235000100', '0988000020', NULL, 'Av. Norte #2001', '2017-01-15', 'activo'),
('Catalina', 'Salinas', '1235000101', '0988000021', NULL, 'Calle Norte #2002', '2018-02-20', 'activo'),
('Tomas', 'Escobar', '1235000102', '0988000022', NULL, 'Av. Norte #2003', '2016-03-25', 'activo'),
('Florencia', 'Montes', '1235000103', '0988000023', NULL, 'Calle Norte #2004', '2019-04-30', 'activo'),
('Diego', 'Araya', '1235000104', '0988000024', NULL, 'Av. Norte #2005', '2017-05-05', 'activo'),
('Amanda', 'Valdes', '1235000105', '0988000025', NULL, 'Calle Norte #2006', '2018-06-10', 'activo'),
('Maximiliano', 'Robles', '1235000106', '0988000026', NULL, 'Av. Norte #2007', '2016-07-15', 'activo'),
('Isidora', 'Miranda', '1235000107', '0988000027', NULL, 'Calle Norte #2008', '2019-08-20', 'activo'),
('Benjamin', 'Caceres', '1235000108', '0988000028', NULL, 'Av. Norte #2009', '2017-09-25', 'activo'),
('Josefa', 'Fuenzalida', '1235000109', '0988000029', NULL, 'Calle Norte #2010', '2018-10-30', 'activo'),
('Vicente', 'Hernandez', '1235000110', '0988000030', NULL, 'Av. Norte #2011', '2016-11-05', 'activo'),
('Maite', 'Saavedra', '1235000111', '0988000031', NULL, 'Calle Norte #2012', '2019-12-10', 'activo'),
('Cristobal', 'Bustos', '1235000112', '0988000032', NULL, 'Av. Norte #2013', '2017-01-15', 'activo'),
('Julieta', 'Pizarro', '1235000113', '0988000033', NULL, 'Calle Norte #2014', '2018-02-20', 'activo'),
('Ignacio', 'Lillo', '1235000114', '0988000034', NULL, 'Av. Norte #2015', '2016-03-25', 'activo'),
('Rafaela', 'Garrido', '1235000115', '0988000035', NULL, 'Calle Norte #2016', '2019-04-30', 'activo'),
('Alonso', 'Acuña', '1235000116', '0988000036', NULL, 'Av. Norte #2017', '2017-05-05', 'activo'),
('Trinidad', 'Tapia', '1235000117', '0988000037', NULL, 'Calle Norte #2018', '2018-06-10', 'activo'),
('Gaspar', 'Vasquez', '1235000118', '0988000038', NULL, 'Av. Norte #2019', '2016-07-15', 'activo'),
('Constanza', 'Neira', '1235000119', '0988000039', NULL, 'Calle Norte #2020', '2019-08-20', 'activo'),
('Dante', 'Leiva', '1235000120', '0988000040', NULL, 'Av. Norte #2021', '2017-09-25', 'activo'),
('Antonia', 'Arce', '1235000121', '0988000041', NULL, 'Calle Norte #2022', '2018-10-30', 'activo'),
('Emilio', 'Riquelme', '1235000122', '0988000042', NULL, 'Av. Norte #2023', '2016-11-05', 'activo'),
('Martina', 'Valenzuela', '1235000123', '0988000043', NULL, 'Calle Norte #2024', '2019-12-10', 'activo'),
('Leon', 'Figueroa', '1235000124', '0988000044', NULL, 'Av. Norte #2025', '2017-01-15', 'activo'),
('Laura', 'Espinoza', '1235000125', '0988000045', NULL, 'Calle Norte #2026', '2018-02-20', 'activo'),
('Clemente', 'Munoz', '1235000126', '0988000046', NULL, 'Av. Norte #2027', '2016-03-25', 'activo'),
('Beatriz', 'Navarro', '1235000127', '0988000047', NULL, 'Calle Norte #2028', '2019-04-30', 'activo'),
('Francisco', 'Gonzalez', '1235000128', '0988000048', NULL, 'Av. Norte #2029', '2017-05-05', 'activo'),
('Pascuala', 'Sanchez', '1235000129', '0988000049', NULL, 'Calle Norte #2030', '2018-06-10', 'activo'),
('Esteban', 'Castro', '1235000130', '0988000050', NULL, 'Av. Norte #2031', '2016-07-15', 'activo'),
('Rosario', 'Alarcon', '1235000131', '0988000051', NULL, 'Calle Norte #2032', '2019-08-20', 'activo'),
('Alberto', 'Ponce', '1235000132', '0988000052', NULL, 'Av. Norte #2033', '2017-09-25', 'activo'),
('Elena', 'Moya', '1235000133', '0988000053', NULL, 'Calle Norte #2034', '2018-10-30', 'activo'),
('Facundo', 'Campos', '1235000134', '0988000054', NULL, 'Av. Norte #2035', '2016-11-05', 'activo'),
('Dominga', 'Zamora', '1235000135', '0988000055', NULL, 'Calle Norte #2036', '2019-12-10', 'activo'),
('Augusto', 'Orellana', '1235000136', '0988000056', NULL, 'Av. Norte #2037', '2017-01-15', 'activo'),
('Magdalena', 'Arancibia', '1235000137', '0988000057', NULL, 'Calle Norte #2038', '2018-02-20', 'activo'),
('Baltazar', 'Palma', '1235000138', '0988000058', NULL, 'Av. Norte #2039', '2016-03-25', 'activo'),
('Amparo', 'Ulloa', '1235000139', '0988000059', NULL, 'Calle Norte #2040', '2019-04-30', 'activo');

-- =============================================
-- 2. USUARIOS DEL PERSONAL ADICIONAL
-- =============================================

INSERT INTO usuario (usuario, contrasenia, estado, id_persona, id_rol, id_centro, fecha_ultimo_acceso) VALUES
-- Terapeutas
('terapeuta.alejandro', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000001'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.isabella', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000002'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.martin', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000003'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.camila', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000004'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.sebastian', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000005'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.valentina', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000006'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.nicolas', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000007'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.antonella', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000008'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.mateo', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000009'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.renata', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000010'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),

-- Pedagogos
('pedagogo.joaquin', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000011'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('pedagoga.emilia', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000012'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('pedagogo.lucas', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000013'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('pedagoga.sofia', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000014'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('pedagogo.daniel', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1235000015'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL);

-- =============================================
-- 3. REGISTRO DE PERSONAL
-- =============================================

INSERT INTO personal (id_persona, id_especialidad, id_centro, fecha_ingreso, cargo, estado, salario, tipo_contrato) VALUES
-- Terapeutas
((SELECT id FROM persona WHERE cedula = '1235000001'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-01-15', 'Terapeuta del Lenguaje Senior', 'activo', 1800.00, 'indefinido'),
((SELECT id FROM persona WHERE cedula = '1235000002'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-01-15', 'Psicologa Clinica Infantil', 'activo', 1900.00, 'indefinido'),
((SELECT id FROM persona WHERE cedula = '1235000003'),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-01', 'Fisioterapeuta Pediatrico', 'activo', 1750.00, 'indefinido'),
((SELECT id FROM persona WHERE cedula = '1235000004'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-01', 'Terapeuta Ocupacional', 'activo', 1700.00, 'indefinido'),
((SELECT id FROM persona WHERE cedula = '1235000005'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-01', 'Especialista en Lenguaje y Comunicacion', 'activo', 1850.00, 'temporal'),
((SELECT id FROM persona WHERE cedula = '1235000006'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-01', 'Psicologa Educativa', 'activo', 1800.00, 'indefinido'),
((SELECT id FROM persona WHERE cedula = '1235000007'),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-01', 'Fisioterapeuta', 'activo', 1650.00, 'temporal'),
((SELECT id FROM persona WHERE cedula = '1235000008'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-01', 'Terapeuta Ocupacional Senior', 'activo', 1800.00, 'indefinido'),
((SELECT id FROM persona WHERE cedula = '1235000009'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-01', 'Terapeuta del Habla', 'activo', 1750.00, 'temporal'),
((SELECT id FROM persona WHERE cedula = '1235000010'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-01', 'Psicologa Infantil', 'activo', 1850.00, 'indefinido'),

-- Pedagogos
((SELECT id FROM persona WHERE cedula = '1235000011'),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-01', 'Especialista en Desarrollo Cognitivo', 'activo', 1700.00, 'indefinido'),
((SELECT id FROM persona WHERE cedula = '1235000012'),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-15', 'Educadora Especial', 'activo', 1650.00, 'indefinido'),
((SELECT id FROM persona WHERE cedula = '1235000013'),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-01', 'Docente de Nivelacion Academica', 'activo', 1600.00, 'temporal'),
((SELECT id FROM persona WHERE cedula = '1235000014'),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-01', 'Educadora Especial Senior', 'activo', 1750.00, 'indefinido'),
((SELECT id FROM persona WHERE cedula = '1235000015'),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-01', 'Docente de Refuerzo Escolar', 'activo', 1650.00, 'temporal');

-- =============================================
-- 4. ESPECIALIDADES DEL PERSONAL
-- =============================================

INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal, nivel_competencia) VALUES
-- Terapeutas
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000001')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'experto'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000002')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'avanzado'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000003')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'avanzado'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000004')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'avanzado'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000005')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'intermedio'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000006')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'experto'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000007')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'intermedio'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000008')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'experto'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000009')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'intermedio'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000010')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'avanzado'),

-- Pedagogos
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000011')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'avanzado'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000012')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'avanzado'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000013')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'intermedio'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000014')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'experto'),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000015')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'intermedio');

-- =============================================
-- 5. TUTORES
-- =============================================

INSERT INTO tutor (id_persona, parentesco, ocupacion, estado, nombre_empresa, telefono_empresa) VALUES
((SELECT id FROM persona WHERE cedula = '1235000020'), 'madre', 'Ingeniera Civil', 'activo', 'Constructora ABC', '02-2345678'),
((SELECT id FROM persona WHERE cedula = '1235000021'), 'padre', 'Medico', 'activo', 'Hospital Norte', '02-2345679'),
((SELECT id FROM persona WHERE cedula = '1235000022'), 'madre', 'Abogada', 'activo', 'Estudio Juridico XYZ', '02-2345680'),
((SELECT id FROM persona WHERE cedula = '1235000023'), 'padre', 'Contador', 'activo', 'Consultora Financiera', '02-2345681'),
((SELECT id FROM persona WHERE cedula = '1235000024'), 'madre', 'Profesora', 'activo', 'Colegio San Jose', '02-2345682'),
((SELECT id FROM persona WHERE cedula = '1235000025'), 'padre', 'Arquitecto', 'activo', 'Estudio de Arquitectura', '02-2345683'),
((SELECT id FROM persona WHERE cedula = '1235000026'), 'madre', 'Enfermera', 'activo', 'Clinica La Paz', '02-2345684'),
((SELECT id FROM persona WHERE cedula = '1235000027'), 'padre', 'Ingeniero en Sistemas', 'activo', 'Tech Solutions', '02-2345685'),
((SELECT id FROM persona WHERE cedula = '1235000028'), 'madre', 'Diseñadora Grafica', 'activo', 'Agencia Creativa', '02-2345686'),
((SELECT id FROM persona WHERE cedula = '1235000029'), 'padre', 'Economista', 'activo', 'Banco Nacional', '02-2345687'),
((SELECT id FROM persona WHERE cedula = '1235000030'), 'madre', 'Psicologa', 'activo', 'Centro de Salud Mental', '02-2345688'),
((SELECT id FROM persona WHERE cedula = '1235000031'), 'padre', 'Administrador de Empresas', 'activo', 'Empresa Comercial', '02-2345689'),
((SELECT id FROM persona WHERE cedula = '1235000032'), 'madre', 'Nutricionista', 'activo', 'Clinica Nutricional', '02-2345690'),
((SELECT id FROM persona WHERE cedula = '1235000033'), 'padre', 'Veterinario', 'activo', 'Clinica Veterinaria', '02-2345691'),
((SELECT id FROM persona WHERE cedula = '1235000034'), 'madre', 'Odontologa', 'activo', 'Clinica Dental', '02-2345692'),
((SELECT id FROM persona WHERE cedula = '1235000035'), 'padre', 'Biologo', 'activo', 'Laboratorio', '02-2345693'),
((SELECT id FROM persona WHERE cedula = '1235000036'), 'madre', 'Farmaceutica', 'activo', 'Farmacia Central', '02-2345694'),
((SELECT id FROM persona WHERE cedula = '1235000037'), 'padre', 'Quimico', 'activo', 'Industria Farmaceutica', '02-2345695'),
((SELECT id FROM persona WHERE cedula = '1235000038'), 'madre', 'Fisioterapeuta', 'activo', 'Centro de Rehabilitacion', '02-2345696'),
((SELECT id FROM persona WHERE cedula = '1235000039'), 'padre', 'Chef', 'activo', 'Restaurante Gourmet', '02-2345697'),
((SELECT id FROM persona WHERE cedula = '1235000040'), 'madre', 'Periodista', 'activo', 'Canal de Television', '02-2345698'),
((SELECT id FROM persona WHERE cedula = '1235000041'), 'padre', 'Fotografo', 'activo', 'Estudio Fotografico', '02-2345699'),
((SELECT id FROM persona WHERE cedula = '1235000042'), 'madre', 'Secretaria Ejecutiva', 'activo', 'Corporacion', '02-2345700'),
((SELECT id FROM persona WHERE cedula = '1235000043'), 'padre', 'Mecanico', 'activo', 'Taller Automotriz', '02-2345701'),
((SELECT id FROM persona WHERE cedula = '1235000044'), 'madre', 'Trabajadora Social', 'activo', 'Municipio', '02-2345702'),
((SELECT id FROM persona WHERE cedula = '1235000045'), 'padre', 'Electricista', 'activo', 'Empresa Electrica', '02-2345703'),
((SELECT id FROM persona WHERE cedula = '1235000046'), 'madre', 'Estilista', 'activo', 'Salon de Belleza', '02-2345704'),
((SELECT id FROM persona WHERE cedula = '1235000047'), 'padre', 'Carpintero', 'activo', 'Taller de Muebles', '02-2345705'),
((SELECT id FROM persona WHERE cedula = '1235000048'), 'madre', 'Cosmetologa', 'activo', 'Centro de Estetica', '02-2345706'),
((SELECT id FROM persona WHERE cedula = '1235000049'), 'padre', 'Conductor', 'activo', 'Empresa de Transporte', '02-2345707'),
((SELECT id FROM persona WHERE cedula = '1235000050'), 'madre', 'Recepcionista', 'activo', 'Hotel', '02-2345708'),
((SELECT id FROM persona WHERE cedula = '1235000051'), 'padre', 'Guardia de Seguridad', 'activo', 'Empresa de Seguridad', '02-2345709'),
((SELECT id FROM persona WHERE cedula = '1235000052'), 'madre', 'Asistente Administrativa', 'activo', 'Oficina Privada', '02-2345710'),
((SELECT id FROM persona WHERE cedula = '1235000053'), 'padre', 'Vendedor', 'activo', 'Tienda Retail', '02-2345711'),
((SELECT id FROM persona WHERE cedula = '1235000054'), 'madre', 'Auxiliar de Enfermeria', 'activo', 'Centro Medico', '02-2345712'),
((SELECT id FROM persona WHERE cedula = '1235000055'), 'padre', 'Jardinero', 'activo', 'Empresa de Paisajismo', '02-2345713'),
((SELECT id FROM persona WHERE cedula = '1235000056'), 'madre', 'Ama de Casa', 'activo', NULL, NULL),
((SELECT id FROM persona WHERE cedula = '1235000057'), 'padre', 'Tecnico en Computacion', 'activo', 'Soporte IT', '02-2345714'),
((SELECT id FROM persona WHERE cedula = '1235000058'), 'madre', 'Maestra de Primaria', 'activo', 'Escuela Municipal', '02-2345715'),
((SELECT id FROM persona WHERE cedula = '1235000059'), 'padre', 'Chofer Profesional', 'activo', 'Empresa Logistica', '02-2345716');

-- =============================================
-- 6. PACIENTES
-- =============================================

INSERT INTO paciente (id_persona, id_tutor, id_centro, fecha_ingreso, motivo_consulta, observaciones, estado, estado_tratamiento) VALUES
((SELECT id FROM persona WHERE cedula = '1235000100'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000020')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-01-10', 'Retraso en desarrollo del lenguaje expresivo', 'Niño colaborador, responde bien a refuerzos visuales', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000101'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000021')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-01-15', 'Problemas de articulacion fonologica', 'Requiere ejercicios de pronunciacion diarios', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000102'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000022')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-01-20', 'Hipotonia muscular generalizada', 'Necesita fortalecimiento muscular progresivo', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000103'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000023')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-01-25', 'Dificultades en motricidad fina', 'Mejoras evidentes con ejercicios de pinza digital', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000104'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000024')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-01', 'Problemas de atencion y concentracion', 'Responde bien a actividades cortas y estructuradas', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000105'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000025')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-05', 'Dificultades en comprension lectora', 'Le gustan los cuentos ilustrados', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000106'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000026')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-10', 'Necesidades educativas especiales', 'Requiere adaptaciones curriculares significativas', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000107'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000027')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-15', 'Trastorno del espectro autista leve', 'Buena respuesta a rutinas visuales', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000108'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000028')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-20', 'Dificultades en escritura', 'Presenta disgrafía leve', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000109'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000029')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-25', 'Problemas de conducta en el aula', 'Requiere apoyo en regulacion emocional', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000110'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000030')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-01', 'Terapia ocupacional por dificultades sensorio-motoras', 'Hipersensibilidad tactil', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000111'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000031')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-05', 'Retraso global del desarrollo', 'Requiere estimulacion temprana intensiva', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000112'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000032')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-10', 'Dificultades en calculo matematico', 'Discalculia moderada', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000113'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000033')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-15', 'Problemas de lenguaje comprensivo', 'Vocabulario receptivo limitado', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000114'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000034')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-20', 'Fisioterapia por paralisis cerebral leve', 'Hemiparesia derecha', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000115'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000035')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-25', 'Ansiedad y miedos escolares', 'Requiere apoyo psicologico', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000116'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000036')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-01', 'Dislexia moderada', 'Dificultades en decodificacion lectora', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000117'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000037')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-05', 'Trastorno del procesamiento sensorial', 'Hipersensibilidad auditiva', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000118'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000038')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-10', 'Dificultades en socializacion', 'Timidez extrema, pocos amigos', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000119'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000039')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-15', 'Retraso en desarrollo motor grueso', 'Torpeza motora evidente', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000120'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000040')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-20', 'Problemas de memoria de trabajo', 'Dificultades en seguimiento de instrucciones', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000121'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000041')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-25', 'Terapia del lenguaje por afasia infantil', 'Post traumatismo craneoencefalico', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000122'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000042')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-01', 'Deficits en funciones ejecutivas', 'Problemas de planificacion y organizacion', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000123'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000043')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-05', 'Trastorno especifico del lenguaje', 'TEL expresivo predominante', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000124'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000044')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-10', 'Dificultades en habilidades pre-academicas', 'Requiere estimulacion cognitiva', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000125'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000045')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-15', 'Problemas de coordinacion visomotora', 'Dificultades en actividades graficas', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000126'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000046')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-20', 'Terapia ocupacional por dispraxia', 'Torpeza en actividades de la vida diaria', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000127'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000047')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-25', 'Necesidades de apoyo conductual', 'Conductas disruptivas frecuentes', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000128'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000048')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-06-01', 'Dificultades en expresion oral', 'Vocabulario expresivo limitado', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000129'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000049')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-06-05', 'Problemas de equilibrio y postura', 'Requiere fisioterapia neuromotora', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000130'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000050')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-06-10', 'Retraso en desarrollo del lenguaje', 'Iniciando primeras palabras', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000131'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000051')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-06-15', 'Dificultades en atencion sostenida', 'Muy disperso en tareas largas', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000132'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000052')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-06-20', 'Problemas de integracion sensorial', 'Busqueda sensorial constante', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000133'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000053')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-06-25', 'Dificultades en resolucion de problemas', 'Razonamiento logico limitado', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000134'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000054')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-07-01', 'Apraxia del habla infantil', 'Dificultad severa en programacion motora del habla', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000135'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000055')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-07-05', 'Problemas de lectoescritura', 'Dificultades en adquisicion de lectura', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000136'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000056')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-07-10', 'Terapia fisica por escoliosis', 'Desviacion columna dorsal', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000137'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000057')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-07-15', 'Dificultades en regulacion emocional', 'Berrinches frecuentes', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000138'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000058')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-07-20', 'Necesidades en desarrollo del lenguaje', 'Habla ininteligible', 'activo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1235000139'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000059')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-07-25', 'Dificultades en autonomia personal', 'Requiere apoyo en actividades basicas', 'activo', 'activo');

-- =============================================
-- 7. ESPECIALIDADES DE PACIENTES
-- =============================================

INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal, prioridad, fecha_asignacion) VALUES
-- Asignar especialidades principales a cada paciente
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000100')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-01-10'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000101')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-01-15'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000102')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-01-20'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000103')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-01-25'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000104')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-02-01'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000105')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-02-05'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000106')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-02-10'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000107')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-02-15'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000108')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-02-20'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000109')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-02-25'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000110')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-03-01'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000111')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'urgente', '2024-03-05'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000112')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-03-10'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000113')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-03-15'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000114')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-03-20'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000115')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-03-25'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000116')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-04-01'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000117')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-04-05'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000118')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-04-10'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000119')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-04-15'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000120')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-04-20'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000121')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'urgente', '2024-04-25'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000122')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-05-01'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000123')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'urgente', '2024-05-05'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000124')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-05-10'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000125')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-05-15'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000126')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-05-20'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000127')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-05-25'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000128')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-06-01'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000129')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-06-05'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000130')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-06-10'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000131')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-06-15'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000132')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-06-20'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000133')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-06-25'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000134')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'urgente', '2024-07-01'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000135')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-07-05'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000136')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-07-10'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000137')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-07-15'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000138')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta', '2024-07-20'),
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000139')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media', '2024-07-25');

-- =============================================
-- 8. SESIONES TERAPEUTICAS - CENTRO NORTE
-- =============================================

-- Sesiones de Terapia del Lenguaje (10 sesiones)
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES
-- Sesion 1: Alejandro Gomez
('ST-NORTE-001', 'Terapia del Lenguaje Expresivo - Grupo A',
 'Desarrollar habilidades de lenguaje expresivo mediante actividades ludicas y ejercicios de articulacion',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000001')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 '2024-08-01', '2025-02-01', ARRAY['lunes', 'miercoles'], '08:00', '08:45', 45,
 24, 6, 25000.00, 600000.00, 'individual', 'en_curso',
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte')),

-- Sesion 2: Alejandro Gomez - Grupo B
('ST-NORTE-002', 'Terapia del Lenguaje Expresivo - Grupo B',
 'Estimulacion del lenguaje oral y desarrollo de vocabulario funcional',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000001')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 '2024-08-01', '2025-02-01', ARRAY['martes', 'jueves'], '08:00', '08:45', 45,
 24, 6, 25000.00, 600000.00, 'individual', 'en_curso',
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte')),

-- Sesion 3: Sebastian Romero
('ST-NORTE-003', 'Intervencion en Articulacion Fonologica',
 'Corregir patrones de articulacion mediante ejercicios especificos de fonemas',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000005')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 '2024-08-05', '2025-02-05', ARRAY['lunes', 'miercoles', 'viernes'], '09:00', '09:45', 45,
 36, 6, 22000.00, 792000.00, 'individual', 'en_curso',
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte')),

-- Sesion 4: Mateo Pacheco
('ST-NORTE-004', 'Desarrollo del Habla y Lenguaje',
 'Estimular la comunicacion verbal y no verbal en etapa inicial',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000009')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 '2024-08-10', '2025-02-10', ARRAY['martes', 'jueves'], '10:00', '10:45', 45,
 24, 6, 26000.00, 624000.00, 'individual', 'en_curso',
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'));

-- Sesiones de Fisioterapia (6 sesiones)
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES
-- Sesion 5: Martin Diaz
('ST-NORTE-005', 'Fisioterapia Neuromotora Pediatrica',
 'Fortalecer tono muscular y mejorar control motor mediante ejercicios terapeuticos',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000003')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 '2024-08-01', '2025-02-01', ARRAY['lunes', 'miercoles', 'viernes'], '08:00', '08:45', 45,
 36, 6, 30000.00, 1080000.00, 'individual', 'en_curso',
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte')),

-- Sesion 6: Nicolas Luna
('ST-NORTE-006', 'Rehabilitacion Motora y Equilibrio',
 'Desarrollar equilibrio y coordinacion mediante actividades de rehabilitacion',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000007')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 '2024-08-05', '2025-02-05', ARRAY['martes', 'jueves'], '09:00', '09:45', 45,
 24, 6, 28000.00, 672000.00, 'individual', 'en_curso',
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'));

-- Sesiones de Terapia Psicologica (6 sesiones)
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES
-- Sesion 7: Isabella Ruiz
('ST-NORTE-007', 'Terapia Cognitivo-Conductual Infantil',
 'Desarrollar habilidades de regulacion emocional y estrategias de afrontamiento',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000002')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 '2024-08-01', '2025-02-01', ARRAY['lunes', 'miercoles'], '10:00', '10:45', 45,
 24, 6, 35000.00, 840000.00, 'individual', 'en_curso',
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte')),

-- Sesion 8: Valentina Mora
('ST-NORTE-008', 'Intervencion en Conducta y Atencion',
 'Mejorar control atencional y reducir conductas disruptivas',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000006')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 '2024-08-05', '2025-02-05', ARRAY['martes', 'jueves'], '08:00', '08:45', 45,
 24, 6, 33000.00, 792000.00, 'individual', 'en_curso',
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte')),

-- Sesion 9: Renata Carrasco
('ST-NORTE-009', 'Apoyo Psicologico y Desarrollo Emocional',
 'Fortalecer autoestima y habilidades socio-emocionales',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000010')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 '2024-08-10', '2025-02-10', ARRAY['lunes', 'miercoles'], '11:00', '11:45', 45,
 24, 6, 34000.00, 816000.00, 'individual', 'en_curso',
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'));

-- Sesiones de Terapia Ocupacional (6 sesiones)
INSERT INTO sesion_terapia (
    codigo_sesion, titulo, objetivo_general, id_terapeuta, id_especialidad,
    fecha_inicio, fecha_fin, dias_semana, hora_inicio, hora_fin, duracion_minutos,
    numero_sesiones_contratadas, meses_contrato, costo_sesion, costo_total,
    tipo_sesion, estado, id_centro, usuario_creacion
) VALUES
-- Sesion 10: Camila Alvarez
('ST-NORTE-010', 'Terapia Ocupacional - Integracion Sensorial',
 'Mejorar procesamiento sensorial y habilidades motoras finas',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000004')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 '2024-08-01', '2025-02-01', ARRAY['martes', 'jueves'], '10:00', '10:45', 45,
 24, 6, 29000.00, 696000.00, 'individual', 'en_curso',
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte')),

-- Sesion 11: Antonella Vidal
('ST-NORTE-011', 'Desarrollo de Habilidades Funcionales',
 'Mejorar independencia en actividades de la vida diaria',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000008')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 '2024-08-05', '2025-02-05', ARRAY['lunes', 'miercoles', 'viernes'], '09:00', '09:45', 45,
 36, 6, 27000.00, 972000.00, 'individual', 'en_curso',
 (SELECT id FROM centros WHERE codigo = 'NORTE'),
 (SELECT id FROM usuario WHERE usuario = 'admin.norte'));

-- =============================================
-- 9. SESIONES PEDAGOGICAS - CENTRO NORTE
-- =============================================

-- Sesiones de Educacion Especial (6 sesiones)
INSERT INTO sesion_pedagogica (
    codigo_sesion, id_educador, id_especialidad, nombre_clase, descripcion,
    fecha_inicio, fecha_fin, nivel_academico, adaptacion_curricular,
    duracion_minutos, frecuencia_semanal, dias_semana, hora_inicio, hora_fin,
    capacidad_maxima, modalidad, periodo_academico, costo_total, costo_por_clase,
    estado, observaciones, id_centro
) VALUES
-- Sesion 1: Emilia Santos
('SP-NORTE-001',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000012')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 'Lectoescritura Adaptada - Nivel Inicial',
 'Desarrollo de habilidades pre-lectoras con adaptaciones individualizadas',
 '2024-08-01', '2025-02-01', 'preescolar',
 'Material visual ampliado, pausas frecuentes, instrucciones simples paso a paso',
 60, 3, ARRAY['lunes', 'miercoles', 'viernes'], '08:00', '09:00',
 6, 'presencial', '2024-2025', 720.00, 20.00,
 'en_curso', 'Grupo de nivel inicial con enfoque multisensorial',
 (SELECT id FROM centros WHERE codigo = 'NORTE')),

-- Sesion 2: Sofia Ugarte
('SP-NORTE-002',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000014')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 'Lectoescritura Intermedia',
 'Fortalecimiento de lectura y escritura funcional',
 '2024-08-05', '2025-02-05', 'primaria',
 'Textos adaptados con imagenes, ejercicios graduales, refuerzo constante',
 60, 2, ARRAY['martes', 'jueves'], '09:00', '10:00',
 5, 'presencial', '2024-2025', 480.00, 20.00,
 'en_curso', 'Enfoque en comprension lectora basica',
 (SELECT id FROM centros WHERE codigo = 'NORTE'));

-- Sesiones de Apoyo Academico (4 sesiones)
INSERT INTO sesion_pedagogica (
    codigo_sesion, id_educador, id_especialidad, nombre_clase, descripcion,
    fecha_inicio, fecha_fin, nivel_academico, adaptacion_curricular,
    duracion_minutos, frecuencia_semanal, dias_semana, hora_inicio, hora_fin,
    capacidad_maxima, modalidad, periodo_academico, costo_total, costo_por_clase,
    estado, observaciones, id_centro
) VALUES
-- Sesion 3: Lucas Peña
('SP-NORTE-003',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000013')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 'Matematicas Basicas - Nivelacion',
 'Refuerzo en operaciones matematicas fundamentales',
 '2024-08-01', '2025-02-01', 'primaria',
 'Material concreto, problemas contextualizados, ejercicios graduales',
 60, 2, ARRAY['lunes', 'miercoles'], '10:00', '11:00',
 6, 'presencial', '2024-2025', 480.00, 20.00,
 'en_curso', 'Uso de abacos y bloques para calculo',
 (SELECT id FROM centros WHERE codigo = 'NORTE'));

-- Sesiones de Desarrollo Cognitivo (3 sesiones)
INSERT INTO sesion_pedagogica (
    codigo_sesion, id_educador, id_especialidad, nombre_clase, descripcion,
    fecha_inicio, fecha_fin, nivel_academico, adaptacion_curricular,
    duracion_minutos, frecuencia_semanal, dias_semana, hora_inicio, hora_fin,
    capacidad_maxima, modalidad, periodo_academico, costo_total, costo_por_clase,
    estado, observaciones, id_centro
) VALUES
-- Sesion 4: Joaquin Bravo
('SP-NORTE-004',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000011')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 'Estimulacion Cognitiva Integral',
 'Desarrollo de funciones ejecutivas y habilidades cognitivas',
 '2024-08-05', '2025-02-05', 'primaria',
 'Actividades ludicas, tiempos adaptados, refuerzo positivo',
 60, 2, ARRAY['martes', 'jueves'], '10:00', '11:00',
 4, 'presencial', '2024-2025', 480.00, 20.00,
 'en_curso', 'Enfoque en atencion, memoria y razonamiento',
 (SELECT id FROM centros WHERE codigo = 'NORTE')),

-- Sesion 5: Daniel Jaramillo
('SP-NORTE-005',
 (SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000015')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 'Lectura Comprensiva',
 'Desarrollo de estrategias de comprension lectora',
 '2024-08-10', '2025-02-10', 'primaria',
 'Lecturas cortas con imagenes, preguntas guiadas, resumen oral',
 60, 2, ARRAY['lunes', 'miercoles'], '11:00', '12:00',
 5, 'presencial', '2024-2025', 480.00, 20.00,
 'en_curso', 'Uso de cuentos ilustrados y organizadores graficos',
 (SELECT id FROM centros WHERE codigo = 'NORTE'));

-- =============================================
-- 10. INSCRIPCIONES EN SESIONES TERAPEUTICAS
-- =============================================

-- Inscribir pacientes en sesiones terapeuticas (distribucion realista)
INSERT INTO sesion_paciente (id_sesion, id_paciente, fecha_inscripcion, estado, observaciones) VALUES
-- ST-NORTE-001: Terapia del Lenguaje Grupo A
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-001'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000100')), '2024-08-01', 'activo', 'Paciente colaborador'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-001'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000101')), '2024-08-01', 'activo', 'Requiere refuerzo constante'),

-- ST-NORTE-002: Terapia del Lenguaje Grupo B
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-002'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000113')), '2024-08-01', 'activo', 'Motivado por juegos'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-002'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000121')), '2024-08-01', 'activo', 'En recuperacion post-trauma'),

-- ST-NORTE-003: Articulacion Fonologica
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-003'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000128')), '2024-08-05', 'activo', 'Progreso lento pero constante'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-003'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000130')), '2024-08-05', 'activo', 'Primeras palabras emergentes'),

-- ST-NORTE-004: Desarrollo Habla
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-004'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000123')), '2024-08-10', 'activo', 'TEL expresivo'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-004'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000134')), '2024-08-10', 'activo', 'Apraxia del habla'),

-- ST-NORTE-005: Fisioterapia Neuromotora
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-005'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000102')), '2024-08-01', 'activo', 'Hipotonia generalizada'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-005'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000114')), '2024-08-01', 'activo', 'Paralisis cerebral leve'),

-- ST-NORTE-006: Rehabilitacion Motora
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-006'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000119')), '2024-08-05', 'activo', 'Retraso motor grueso'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-006'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000129')), '2024-08-05', 'activo', 'Problemas de equilibrio'),

-- ST-NORTE-007: Terapia Cognitivo-Conductual
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-007'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000104')), '2024-08-01', 'activo', 'Deficit atencional'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-007'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000109')), '2024-08-01', 'activo', 'Problemas conductuales'),

-- ST-NORTE-008: Intervencion Conducta
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-008'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000115')), '2024-08-05', 'activo', 'Ansiedad escolar'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-008'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000127')), '2024-08-05', 'activo', 'Conductas disruptivas'),

-- ST-NORTE-009: Apoyo Psicologico
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-009'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000118')), '2024-08-10', 'activo', 'Timidez extrema'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-009'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000137')), '2024-08-10', 'activo', 'Regulacion emocional'),

-- ST-NORTE-010: Terapia Ocupacional Integracion
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-010'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000103')), '2024-08-01', 'activo', 'Motricidad fina'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-010'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000110')), '2024-08-01', 'activo', 'Hipersensibilidad tactil'),

-- ST-NORTE-011: Habilidades Funcionales
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-011'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000117')), '2024-08-05', 'activo', 'Procesamiento sensorial'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-011'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000126')), '2024-08-05', 'activo', 'Dispraxia'),
((SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-011'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000139')), '2024-08-05', 'activo', 'Autonomia personal');

-- =============================================
-- 11. INSCRIPCIONES EN SESIONES PEDAGOGICAS
-- =============================================

INSERT INTO sesion_estudiante (id_sesion, id_paciente, fecha_inscripcion, nivel_actual, adaptaciones_requeridas, estado, observaciones) VALUES
-- SP-NORTE-001: Lectoescritura Inicial
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-001'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000105')), '2024-08-01', 'pre-lectura', 'Material visual ampliado', 'activo', 'Le gustan los cuentos'),
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-001'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000106')), '2024-08-01', 'inicial', 'Instrucciones simples', 'activo', 'Requiere apoyo constante'),

-- SP-NORTE-002: Lectoescritura Intermedia
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-002'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000116')), '2024-08-05', '2do grado', 'Textos adaptados', 'activo', 'Dislexia moderada'),
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-002'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000135')), '2024-08-05', '3er grado', 'Tiempo adicional', 'activo', 'Dificultades en escritura'),

-- SP-NORTE-003: Matematicas Basicas
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-003'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000112')), '2024-08-01', '2do grado', 'Material concreto', 'activo', 'Discalculia moderada'),
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-003'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000133')), '2024-08-01', '3er grado', 'Problemas graduales', 'activo', 'Razonamiento limitado'),

-- SP-NORTE-004: Estimulacion Cognitiva
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-004'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000111')), '2024-08-05', 'inicial', 'Estimulacion intensiva', 'activo', 'Retraso global'),
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-004'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000120')), '2024-08-05', '1er grado', 'Instrucciones claras', 'activo', 'Memoria de trabajo limitada'),
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-004'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000124')), '2024-08-05', 'preescolar', 'Actividades ludicas', 'activo', 'Pre-academico'),

-- SP-NORTE-005: Lectura Comprensiva
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-005'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000108')), '2024-08-10', '2do grado', 'Lecturas cortas', 'activo', 'Disgrafia leve'),
((SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-005'),
 (SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1235000122')), '2024-08-10', '3er grado', 'Organizadores graficos', 'activo', 'Funciones ejecutivas');

-- =============================================
-- 12. CRONOGRAMAS DE SESIONES TERAPEUTICAS
-- =============================================

-- ST-NORTE-001: Lunes y Miercoles desde Agosto
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-001'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '08:00'::time,
    '08:45'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-01'::date, '2025-02-01'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3)
LIMIT 24;

-- ST-NORTE-002: Martes y Jueves desde Agosto
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-002'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '08:00'::time,
    '08:45'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-01'::date, '2025-02-01'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4)
LIMIT 24;

-- ST-NORTE-003: Lunes, Miercoles, Viernes desde Agosto 5
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-003'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '09:00'::time,
    '09:45'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-05'::date, '2025-02-05'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3, 5)
LIMIT 36;

-- ST-NORTE-004: Martes y Jueves desde Agosto 10
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-004'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '10:00'::time,
    '10:45'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-10'::date, '2025-02-10'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4)
LIMIT 24;

-- ST-NORTE-005: Lunes, Miercoles, Viernes desde Agosto
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-005'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '08:00'::time,
    '08:45'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-01'::date, '2025-02-01'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3, 5)
LIMIT 36;

-- ST-NORTE-006: Martes y Jueves desde Agosto 5
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-006'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '09:00'::time,
    '09:45'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-05'::date, '2025-02-05'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4)
LIMIT 24;

-- ST-NORTE-007: Lunes y Miercoles desde Agosto
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-007'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '10:00'::time,
    '10:45'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-01'::date, '2025-02-01'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3)
LIMIT 24;

-- ST-NORTE-008: Martes y Jueves desde Agosto 5
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-008'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '08:00'::time,
    '08:45'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-05'::date, '2025-02-05'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4)
LIMIT 24;

-- ST-NORTE-009: Lunes y Miercoles desde Agosto 10
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-009'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '11:00'::time,
    '11:45'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-10'::date, '2025-02-10'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3)
LIMIT 24;

-- ST-NORTE-010: Martes y Jueves desde Agosto
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-010'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '10:00'::time,
    '10:45'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-01'::date, '2025-02-01'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4)
LIMIT 24;

-- ST-NORTE-011: Lunes, Miercoles, Viernes desde Agosto 5
INSERT INTO cronograma_sesiones (id_sesion, numero_sesion_semanal, fecha_programada, hora_inicio, hora_fin, estado, usuario_creacion)
SELECT
    (SELECT id FROM sesion_terapia WHERE codigo_sesion = 'ST-NORTE-011'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '09:00'::time,
    '09:45'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-05'::date, '2025-02-05'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3, 5)
LIMIT 36;

-- =============================================
-- 13. CRONOGRAMAS DE SESIONES PEDAGOGICAS
-- =============================================

-- SP-NORTE-001: Lectoescritura Inicial - Lunes, Miercoles, Viernes
INSERT INTO cronograma_clases (id_sesion, numero_clase_semanal, fecha_programada, hora_inicio, hora_fin, estado, tema_clase, usuario_creacion)
SELECT
    (SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-001'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '08:00'::time,
    '09:00'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    'Desarrollo pre-lector con material visual',
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-01'::date, '2025-02-01'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3, 5)
LIMIT 72;

-- SP-NORTE-002: Lectoescritura Intermedia - Martes y Jueves
INSERT INTO cronograma_clases (id_sesion, numero_clase_semanal, fecha_programada, hora_inicio, hora_fin, estado, tema_clase, usuario_creacion)
SELECT
    (SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-002'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '09:00'::time,
    '10:00'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    'Comprension lectora basica',
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-05'::date, '2025-02-05'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4)
LIMIT 48;

-- SP-NORTE-003: Matematicas Basicas - Lunes y Miercoles
INSERT INTO cronograma_clases (id_sesion, numero_clase_semanal, fecha_programada, hora_inicio, hora_fin, estado, tema_clase, usuario_creacion)
SELECT
    (SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-003'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '10:00'::time,
    '11:00'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    'Operaciones matematicas con material concreto',
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-01'::date, '2025-02-01'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3)
LIMIT 48;

-- SP-NORTE-004: Estimulacion Cognitiva - Martes y Jueves
INSERT INTO cronograma_clases (id_sesion, numero_clase_semanal, fecha_programada, hora_inicio, hora_fin, estado, tema_clase, usuario_creacion)
SELECT
    (SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-004'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '10:00'::time,
    '11:00'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    'Desarrollo de atencion y memoria',
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-05'::date, '2025-02-05'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (2, 4)
LIMIT 48;

-- SP-NORTE-005: Lectura Comprensiva - Lunes y Miercoles
INSERT INTO cronograma_clases (id_sesion, numero_clase_semanal, fecha_programada, hora_inicio, hora_fin, estado, tema_clase, usuario_creacion)
SELECT
    (SELECT id FROM sesion_pedagogica WHERE codigo_sesion = 'SP-NORTE-005'),
    ROW_NUMBER() OVER (ORDER BY fecha_gen),
    fecha_gen::date,
    '11:00'::time,
    '12:00'::time,
    CASE WHEN fecha_gen::date <= CURRENT_DATE THEN 'completada' ELSE 'programada' END,
    'Estrategias de comprension lectora',
    (SELECT id FROM usuario WHERE usuario = 'admin.norte')
FROM (
    SELECT generate_series('2024-08-10'::date, '2025-02-10'::date, '1 day'::interval) AS fecha_gen
) t
WHERE EXTRACT(dow FROM fecha_gen) IN (1, 3)
LIMIT 48;

-- =============================================
-- 14. ASISTENCIAS DE EJEMPLO
-- =============================================

-- Asistencias para sesiones terapeuticas completadas
INSERT INTO asistencia_sesiones (
    id_cronograma, id_paciente, asistio, llegada_tardanza_minutos,
    estado_asistencia, observaciones_terapeuta, objetivos_trabajados, progreso_observado
)
SELECT
    cs.id,
    sp.id_paciente,
    true,
    0,
    'presente',
    'Sesion productiva',
    'Articulacion de fonemas',
    'Mejora progresiva'
FROM cronograma_sesiones cs
JOIN sesion_terapia st ON cs.id_sesion = st.id
JOIN sesion_paciente sp ON sp.id_sesion = st.id
WHERE st.codigo_sesion = 'ST-NORTE-001'
AND cs.fecha_programada <= CURRENT_DATE
AND cs.estado = 'completada'
LIMIT 20;

-- Asistencias para clases pedagogicas
INSERT INTO asistencia_clases (
    id_cronograma, id_paciente, asistio, estado_asistencia,
    observaciones_educador, participacion_clase, actividades_completadas, calificacion_clase
)
SELECT
    cc.id,
    se.id_paciente,
    true,
    'presente',
    'Buena participacion',
    'buena',
    true,
    8
FROM cronograma_clases cc
JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
JOIN sesion_estudiante se ON se.id_sesion = sp.id
WHERE sp.codigo_sesion = 'SP-NORTE-001'
AND cc.fecha_programada <= CURRENT_DATE
AND cc.estado = 'completada'
LIMIT 15;

-- =============================================
-- FIN DEL ARCHIVO
-- =============================================

-- Resumen final
DO $$
DECLARE
    personas_norte INTEGER;
    usuarios_norte INTEGER;
    personal_norte INTEGER;
    pacientes_norte INTEGER;
    sesiones_terapia INTEGER;
    sesiones_pedagogica INTEGER;
    cronogramas_terapia INTEGER;
    cronogramas_pedagogia INTEGER;
    asistencias_terapia INTEGER;
    asistencias_pedagogia INTEGER;
    inscripciones_terapia INTEGER;
    inscripciones_pedagogia INTEGER;
BEGIN
    SELECT COUNT(*) INTO personas_norte FROM persona WHERE cedula LIKE '1235%';
    SELECT COUNT(*) INTO usuarios_norte FROM usuario u
        JOIN persona p ON u.id_persona = p.id
        WHERE p.cedula LIKE '1235%';
    SELECT COUNT(*) INTO personal_norte FROM personal pr
        JOIN persona p ON pr.id_persona = p.id
        WHERE p.cedula LIKE '1235%';
    SELECT COUNT(*) INTO pacientes_norte FROM paciente pa
        JOIN persona p ON pa.id_persona = p.id
        WHERE p.cedula LIKE '1235%';

    -- Sesiones
    SELECT COUNT(*) INTO sesiones_terapia FROM sesion_terapia WHERE codigo_sesion LIKE 'ST-NORTE%';
    SELECT COUNT(*) INTO sesiones_pedagogica FROM sesion_pedagogica WHERE codigo_sesion LIKE 'SP-NORTE%';

    -- Cronogramas
    SELECT COUNT(*) INTO cronogramas_terapia FROM cronograma_sesiones cs
        JOIN sesion_terapia st ON cs.id_sesion = st.id
        WHERE st.codigo_sesion LIKE 'ST-NORTE%';
    SELECT COUNT(*) INTO cronogramas_pedagogia FROM cronograma_clases cc
        JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
        WHERE sp.codigo_sesion LIKE 'SP-NORTE%';

    -- Inscripciones
    SELECT COUNT(*) INTO inscripciones_terapia FROM sesion_paciente sp
        JOIN sesion_terapia st ON sp.id_sesion = st.id
        WHERE st.codigo_sesion LIKE 'ST-NORTE%';
    SELECT COUNT(*) INTO inscripciones_pedagogia FROM sesion_estudiante se
        JOIN sesion_pedagogica sp ON se.id_sesion = sp.id
        WHERE sp.codigo_sesion LIKE 'SP-NORTE%';

    -- Asistencias
    SELECT COUNT(*) INTO asistencias_terapia FROM asistencia_sesiones ases
        JOIN cronograma_sesiones cs ON ases.id_cronograma = cs.id
        JOIN sesion_terapia st ON cs.id_sesion = st.id
        WHERE st.codigo_sesion LIKE 'ST-NORTE%';
    SELECT COUNT(*) INTO asistencias_pedagogia FROM asistencia_clases ac
        JOIN cronograma_clases cc ON ac.id_cronograma = cc.id
        JOIN sesion_pedagogica sp ON cc.id_sesion = sp.id
        WHERE sp.codigo_sesion LIKE 'SP-NORTE%';

    RAISE NOTICE '=======================================================';
    RAISE NOTICE '    DATOS MASIVOS CENTRO NORTE - RESUMEN COMPLETO';
    RAISE NOTICE '=======================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'PERSONAS Y USUARIOS:';
    RAISE NOTICE '  - Personas agregadas: %', personas_norte;
    RAISE NOTICE '  - Usuarios del sistema: %', usuarios_norte;
    RAISE NOTICE '  - Personal activo: %', personal_norte;
    RAISE NOTICE '  - Pacientes registrados: %', pacientes_norte;
    RAISE NOTICE '';
    RAISE NOTICE 'SESIONES:';
    RAISE NOTICE '  - Sesiones Terapeuticas: %', sesiones_terapia;
    RAISE NOTICE '  - Sesiones Pedagogicas: %', sesiones_pedagogica;
    RAISE NOTICE '';
    RAISE NOTICE 'INSCRIPCIONES:';
    RAISE NOTICE '  - Inscripciones en terapia: %', inscripciones_terapia;
    RAISE NOTICE '  - Inscripciones en clases: %', inscripciones_pedagogia;
    RAISE NOTICE '';
    RAISE NOTICE 'CRONOGRAMAS:';
    RAISE NOTICE '  - Cronogramas de terapia: %', cronogramas_terapia;
    RAISE NOTICE '  - Cronogramas de clases: %', cronogramas_pedagogia;
    RAISE NOTICE '  - Total cronogramas: %', cronogramas_terapia + cronogramas_pedagogia;
    RAISE NOTICE '';
    RAISE NOTICE 'ASISTENCIAS REGISTRADAS:';
    RAISE NOTICE '  - Asistencias terapia: %', asistencias_terapia;
    RAISE NOTICE '  - Asistencias clases: %', asistencias_pedagogia;
    RAISE NOTICE '';
    RAISE NOTICE '=======================================================';
    RAISE NOTICE '  SISTEMA CENTRO NORTE LISTO PARA PRUEBAS COMPLETAS';
    RAISE NOTICE '=======================================================';
END $$;
