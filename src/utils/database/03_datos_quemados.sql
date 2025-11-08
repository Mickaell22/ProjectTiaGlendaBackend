-- =============================================
-- CENTRO TIA GLENDA - DATOS DE PRUEBA EXTENSIVOS
-- Archivo: 03_datos_quemados.sql
-- Descripcion: Datos masivos para pruebas completas del sistema
-- =============================================
--
-- CREDENCIALES DE PRUEBA (password: admin123 para todos):
-- Ver 02_datos_completos.sql para credenciales de usuarios existentes
--
-- CONTENIDO:
-- - 30+ pacientes adicionales (15 por centro)
-- - 12+ personal adicional (terapeutas y pedagogos)
-- - 15+ sesiones terapeuticas activas
-- - 10+ sesiones pedagogicas activas
-- - Cronogramas completos con asistencias
-- - Pausas de pacientes y historiales
-- - Mensajes y observaciones
-- - Documentos de pacientes y personal
-- - Notificaciones de ejemplo
-- =============================================

-- =============================================
-- CONFIGURACION INICIAL
-- =============================================

SET search_path TO public;

-- =============================================
-- 1. PERSONAS ADICIONALES - CENTRO NORTE
-- =============================================

-- Personal Centro Norte (6 terapeutas y 4 pedagogos adicionales)
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
-- Terapeutas
('Sofia', 'Ramirez', '1234567910', '0987654340', 'sofia.ramirez@centrotiaglenda.com', 'Av. Norte #111', '1991-02-14', 'activo'),
('Pablo', 'Castillo', '1234567911', '0987654341', 'pablo.castillo@centrotiaglenda.com', 'Calle Norte #222', '1989-05-23', 'activo'),
('Gabriela', 'Moreno', '1234567912', '0987654342', 'gabriela.moreno@centrotiaglenda.com', 'Av. Norte #333', '1992-08-16', 'activo'),
('Roberto', 'Silva', '1234567913', '0987654343', 'roberto.silva@centrotiaglenda.com', 'Calle Norte #444', '1988-11-09', 'activo'),
('Daniela', 'Ortiz', '1234567914', '0987654344', 'daniela.ortiz@centrotiaglenda.com', 'Av. Norte #555', '1990-04-27', 'activo'),
('Fernando', 'Guzman', '1234567915', '0987654345', 'fernando.guzman@centrotiaglenda.com', 'Calle Norte #666', '1987-07-19', 'activo'),

-- Pedagogos
('Valeria', 'Castro', '1234567916', '0987654346', 'valeria.castro@centrotiaglenda.com', 'Av. Norte #777', '1991-09-30', 'activo'),
('Andres', 'Herrera', '1234567917', '0987654347', 'andres.herrera@centrotiaglenda.com', 'Calle Norte #888', '1989-12-05', 'activo'),
('Monica', 'Paredes', '1234567918', '0987654348', 'monica.paredes@centrotiaglenda.com', 'Av. Norte #999', '1993-01-18', 'activo'),
('Ricardo', 'Salazar', '1234567919', '0987654349', 'ricardo.salazar@centrotiaglenda.com', 'Calle Norte #101', '1988-03-22', 'activo');

-- Tutores Centro Norte (15 tutores)
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Andrea', 'Lopez', '1234567920', '0987654350', 'andrea.lopez@gmail.com', 'Av. Norte #201', '1982-06-10', 'activo'),
('Jorge', 'Mendez', '1234567921', '0987654351', 'jorge.mendez@gmail.com', 'Calle Norte #202', '1980-09-15', 'activo'),
('Silvia', 'Rojas', '1234567922', '0987654352', 'silvia.rojas@gmail.com', 'Av. Norte #203', '1985-12-20', 'activo'),
('Mario', 'Cruz', '1234567923', '0987654353', 'mario.cruz@gmail.com', 'Calle Norte #204', '1978-03-25', 'activo'),
('Lucia', 'Reyes', '1234567924', '0987654354', 'lucia.reyes@gmail.com', 'Av. Norte #205', '1983-07-30', 'activo'),
('Carlos', 'Navarro', '1234567925', '0987654355', 'carlos.navarro@gmail.com', 'Calle Norte #206', '1981-10-05', 'activo'),
('Patricia', 'Soto', '1234567926', '0987654356', 'patricia.soto@gmail.com', 'Av. Norte #207', '1984-01-12', 'activo'),
('Diego', 'Ramos', '1234567927', '0987654357', 'diego.ramos@gmail.com', 'Calle Norte #208', '1979-04-18', 'activo'),
('Veronica', 'Fernandez', '1234567928', '0987654358', 'veronica.fernandez@gmail.com', 'Av. Norte #209', '1986-08-23', 'activo'),
('Alberto', 'Guerrero', '1234567929', '0987654359', 'alberto.guerrero@gmail.com', 'Calle Norte #210', '1977-11-28', 'activo'),
('Isabel', 'Molina', '1234567930', '0987654360', 'isabel.molina@gmail.com', 'Av. Norte #211', '1982-02-14', 'activo'),
('Francisco', 'Delgado', '1234567931', '0987654361', 'francisco.delgado@gmail.com', 'Calle Norte #212', '1980-05-19', 'activo'),
('Laura', 'Campos', '1234567932', '0987654362', 'laura.campos@gmail.com', 'Av. Norte #213', '1985-08-24', 'activo'),
('Rodrigo', 'Benitez', '1234567933', '0987654363', 'rodrigo.benitez@gmail.com', 'Calle Norte #214', '1978-11-29', 'activo'),
('Adriana', 'Aguilar', '1234567934', '0987654364', 'adriana.aguilar@gmail.com', 'Av. Norte #215', '1983-03-05', 'activo');

-- Pacientes Centro Norte (15 ninos)
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Lucas', 'Lopez', '1234567935', '0987654350', NULL, 'Av. Norte #201', '2017-01-15', 'activo'),
('Martina', 'Mendez', '1234567936', '0987654351', NULL, 'Calle Norte #202', '2018-03-20', 'activo'),
('Santiago', 'Rojas', '1234567937', '0987654352', NULL, 'Av. Norte #203', '2016-05-25', 'activo'),
('Camila', 'Cruz', '1234567938', '0987654353', NULL, 'Calle Norte #204', '2019-07-30', 'activo'),
('Nicolas', 'Reyes', '1234567939', '0987654354', NULL, 'Av. Norte #205', '2017-09-05', 'activo'),
('Valentina', 'Navarro', '1234567940', '0987654355', NULL, 'Calle Norte #206', '2018-11-10', 'activo'),
('Benjamin', 'Soto', '1234567941', '0987654356', NULL, 'Av. Norte #207', '2016-01-15', 'activo'),
('Sofia', 'Ramos', '1234567942', '0987654357', NULL, 'Calle Norte #208', '2019-03-20', 'activo'),
('Matias', 'Fernandez', '1234567943', '0987654358', NULL, 'Av. Norte #209', '2017-05-25', 'activo'),
('Emma', 'Guerrero', '1234567944', '0987654359', NULL, 'Calle Norte #210', '2018-07-30', 'activo'),
('Daniel', 'Molina', '1234567945', '0987654360', NULL, 'Av. Norte #211', '2016-09-05', 'activo'),
('Antonella', 'Delgado', '1234567946', '0987654361', NULL, 'Calle Norte #212', '2019-11-10', 'activo'),
('Gabriel', 'Campos', '1234567947', '0987654362', NULL, 'Av. Norte #213', '2017-01-15', 'activo'),
('Renata', 'Benitez', '1234567948', '0987654363', NULL, 'Calle Norte #214', '2018-03-20', 'activo'),
('Joaquin', 'Aguilar', '1234567949', '0987654364', NULL, 'Av. Norte #215', '2016-05-25', 'activo');

-- =============================================
-- 2. PERSONAS ADICIONALES - CENTRO SUR
-- =============================================

-- Personal Centro Sur (6 terapeutas y 4 pedagogos adicionales)
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
-- Terapeutas
('Mariana', 'Villanueva', '1234567950', '0987654370', 'mariana.villanueva@centrotiaglenda.com', 'Av. Sur #111', '1990-02-10', 'activo'),
('Javier', 'Dominguez', '1234567951', '0987654371', 'javier.dominguez@centrotiaglenda.com', 'Calle Sur #222', '1988-04-15', 'activo'),
('Carolina', 'Suarez', '1234567952', '0987654372', 'carolina.suarez@centrotiaglenda.com', 'Av. Sur #333', '1991-06-20', 'activo'),
('Esteban', 'Rios', '1234567953', '0987654373', 'esteban.rios@centrotiaglenda.com', 'Calle Sur #444', '1989-08-25', 'activo'),
('Natalia', 'Palacios', '1234567954', '0987654374', 'natalia.palacios@centrotiaglenda.com', 'Av. Sur #555', '1992-10-30', 'activo'),
('Cristian', 'Espinoza', '1234567955', '0987654375', 'cristian.espinoza@centrotiaglenda.com', 'Calle Sur #666', '1987-12-05', 'activo'),

-- Pedagogos
('Alejandra', 'Nunez', '1234567956', '0987654376', 'alejandra.nunez@centrotiaglenda.com', 'Av. Sur #777', '1990-01-10', 'activo'),
('Mauricio', 'Carrillo', '1234567957', '0987654377', 'mauricio.carrillo@centrotiaglenda.com', 'Calle Sur #888', '1988-03-15', 'activo'),
('Lorena', 'Medina', '1234567958', '0987654378', 'lorena.medina@centrotiaglenda.com', 'Av. Sur #999', '1991-05-20', 'activo'),
('Gustavo', 'Pena', '1234567959', '0987654379', 'gustavo.pena@centrotiaglenda.com', 'Calle Sur #101', '1989-07-25', 'activo');

-- Tutores Centro Sur (15 tutores)
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Monica', 'Vargas', '1234567960', '0987654380', 'monica.vargas@gmail.com', 'Av. Sur #201', '1981-09-08', 'activo'),
('Hector', 'Cardenas', '1234567961', '0987654381', 'hector.cardenas@gmail.com', 'Calle Sur #202', '1979-11-12', 'activo'),
('Beatriz', 'Lara', '1234567962', '0987654382', 'beatriz.lara@gmail.com', 'Av. Sur #203', '1984-01-16', 'activo'),
('Raul', 'Ibarra', '1234567963', '0987654383', 'raul.ibarra@gmail.com', 'Calle Sur #204', '1977-03-20', 'activo'),
('Claudia', 'Ochoa', '1234567964', '0987654384', 'claudia.ochoa@gmail.com', 'Av. Sur #205', '1982-05-24', 'activo'),
('Sergio', 'Sandoval', '1234567965', '0987654385', 'sergio.sandoval@gmail.com', 'Calle Sur #206', '1980-07-28', 'activo'),
('Gloria', 'Fuentes', '1234567966', '0987654386', 'gloria.fuentes@gmail.com', 'Av. Sur #207', '1983-09-01', 'activo'),
('Miguel Angel', 'Vega', '1234567967', '0987654387', 'miguelangel.vega@gmail.com', 'Calle Sur #208', '1978-11-05', 'activo'),
('Rosa', 'Cortez', '1234567968', '0987654388', 'rosa.cortez@gmail.com', 'Av. Sur #209', '1985-01-09', 'activo'),
('Felipe', 'Santana', '1234567969', '0987654389', 'felipe.santana@gmail.com', 'Calle Sur #210', '1976-03-13', 'activo'),
('Angelica', 'Alarcon', '1234567970', '0987654390', 'angelica.alarcon@gmail.com', 'Av. Sur #211', '1981-05-17', 'activo'),
('Oscar', 'Bravo', '1234567971', '0987654391', 'oscar.bravo@gmail.com', 'Calle Sur #212', '1979-07-21', 'activo'),
('Norma', 'Gallegos', '1234567972', '0987654392', 'norma.gallegos@gmail.com', 'Av. Sur #213', '1984-09-25', 'activo'),
('Ernesto', 'Lozano', '1234567973', '0987654393', 'ernesto.lozano@gmail.com', 'Calle Sur #214', '1977-11-29', 'activo'),
('Cecilia', 'Duran', '1234567974', '0987654394', 'cecilia.duran@gmail.com', 'Av. Sur #215', '1982-02-02', 'activo');

-- Pacientes Centro Sur (15 ninos)
INSERT INTO persona (nombre, apellido, cedula, telefono, correo, direccion, fecha_nacimiento, estado) VALUES
('Emilia', 'Vargas', '1234567975', '0987654380', NULL, 'Av. Sur #201', '2017-02-10', 'activo'),
('Tomas', 'Cardenas', '1234567976', '0987654381', NULL, 'Calle Sur #202', '2018-04-15', 'activo'),
('Lucia', 'Lara', '1234567977', '0987654382', NULL, 'Av. Sur #203', '2016-06-20', 'activo'),
('Agustin', 'Ibarra', '1234567978', '0987654383', NULL, 'Calle Sur #204', '2019-08-25', 'activo'),
('Catalina', 'Ochoa', '1234567979', '0987654384', NULL, 'Av. Sur #205', '2017-10-30', 'activo'),
('Ian', 'Sandoval', '1234567980', '0987654385', NULL, 'Calle Sur #206', '2018-12-05', 'activo'),
('Julieta', 'Fuentes', '1234567981', '0987654386', NULL, 'Av. Sur #207', '2016-02-10', 'activo'),
('Maximiliano', 'Vega', '1234567982', '0987654387', NULL, 'Calle Sur #208', '2019-04-15', 'activo'),
('Olivia', 'Cortez', '1234567983', '0987654388', NULL, 'Av. Sur #209', '2017-06-20', 'activo'),
('Felipe', 'Santana', '1234567984', '0987654389', NULL, 'Calle Sur #210', '2018-08-25', 'activo'),
('Regina', 'Alarcon', '1234567985', '0987654390', NULL, 'Av. Sur #211', '2016-10-30', 'activo'),
('Bruno', 'Bravo', '1234567986', '0987654391', NULL, 'Calle Sur #212', '2019-12-05', 'activo'),
('Alma', 'Gallegos', '1234567987', '0987654392', NULL, 'Av. Sur #213', '2017-02-10', 'activo'),
('Dylan', 'Lozano', '1234567988', '0987654393', NULL, 'Calle Sur #214', '2018-04-15', 'activo'),
('Victoria', 'Duran', '1234567989', '0987654394', NULL, 'Av. Sur #215', '2016-06-20', 'activo');

-- =============================================
-- 3. USUARIOS DEL PERSONAL ADICIONAL
-- =============================================

-- Personal Centro Norte
INSERT INTO usuario (usuario, contrasenia, estado, id_persona, id_rol, id_centro, fecha_ultimo_acceso) VALUES
-- Terapeutas
('terapeuta.sofia', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567910'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.pablo', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567911'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.gabriela', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567912'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.roberto', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567913'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.daniela', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567914'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('terapeuta.fernando', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567915'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),

-- Pedagogos
('pedagoga.valeria', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567916'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('pedagogo.andres', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567917'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('pedagoga.monica', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567918'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL),
('pedagogo.ricardo', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567919'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'NORTE'), NULL);

-- Personal Centro Sur
INSERT INTO usuario (usuario, contrasenia, estado, id_persona, id_rol, id_centro, fecha_ultimo_acceso) VALUES
-- Terapeutas
('terapeuta.mariana', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567950'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL),
('terapeuta.javier', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567951'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL),
('terapeuta.carolina', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567952'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL),
('terapeuta.esteban', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567953'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL),
('terapeuta.natalia', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567954'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL),
('terapeuta.cristian', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567955'),
    (SELECT id FROM rol WHERE nombre = 'Terapeuta'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL),

-- Pedagogos
('pedagoga.alejandra', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567956'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL),
('pedagogo.mauricio', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567957'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL),
('pedagoga.lorena', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567958'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL),
('pedagogo.gustavo', '$2b$12$otmv88HeRL46p1eAltu5m.jQ11VLmL.jTo3Z4sqliPn05ljJ46/U6', 'activo',
    (SELECT id FROM persona WHERE cedula = '1234567959'),
    (SELECT id FROM rol WHERE nombre = 'Pedagógico'),
    (SELECT id FROM centros WHERE codigo = 'SUR'), NULL);

-- =============================================
-- 4. REGISTRO DE PERSONAL ADICIONAL
-- =============================================

-- Personal Centro Norte
INSERT INTO personal (id_persona, id_especialidad, id_centro, fecha_ingreso, cargo, estado) VALUES
-- Terapeutas
((SELECT id FROM persona WHERE cedula = '1234567910'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-01', 'Psicologa Clinica', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567911'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-01', 'Terapeuta Ocupacional', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567912'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-01', 'Especialista en Lenguaje', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567913'),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-01', 'Fisioterapeuta', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567914'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-01', 'Psicologa Infantil', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567915'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-01', 'Terapeuta Ocupacional', 'activo'),

-- Pedagogos
((SELECT id FROM persona WHERE cedula = '1234567916'),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-02-01', 'Docente de Apoyo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567917'),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-01', 'Psicologo Educativo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567918'),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-01', 'Educadora Especial', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567919'),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-01', 'Docente de Refuerzo', 'activo');

-- Personal Centro Sur
INSERT INTO personal (id_persona, id_especialidad, id_centro, fecha_ingreso, cargo, estado) VALUES
-- Terapeutas
((SELECT id FROM persona WHERE cedula = '1234567950'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-02-01', 'Psicologa Clinica', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567951'),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-02-01', 'Fisioterapeuta Pediatrico', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567952'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-03-01', 'Terapeuta del Habla', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567953'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-03-01', 'Terapeuta Ocupacional', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567954'),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-04-01', 'Psicologa Infantil', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567955'),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-04-01', 'Fisioterapeuta', 'activo'),

-- Pedagogos
((SELECT id FROM persona WHERE cedula = '1234567956'),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-02-01', 'Docente de Apoyo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567957'),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-03-01', 'Psicologo Educativo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567958'),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-03-01', 'Educadora Especial', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567959'),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-04-01', 'Docente de Nivelacion', 'activo');

-- =============================================
-- 5. ESPECIALIDADES DEL PERSONAL ADICIONAL
-- =============================================

-- Centro Norte - Asignar especialidades principales
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
-- Terapeutas
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567910')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567911')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567912')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567913')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567914')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567915')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),

-- Pedagogos
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567916')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567917')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567918')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567919')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE);

-- Centro Sur - Asignar especialidades principales
INSERT INTO personal_especialidades (id_personal, id_especialidad, es_principal) VALUES
-- Terapeutas
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567950')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567951')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567952')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567953')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567954')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567955')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),

-- Pedagogos
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567956')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567957')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567958')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE),
((SELECT id FROM personal WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567959')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE);

-- =============================================
-- 6. TUTORES ADICIONALES
-- =============================================

-- Centro Norte
INSERT INTO tutor (id_persona, parentesco, ocupacion, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567920'), 'madre', 'Enfermera', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567921'), 'padre', 'Ingeniero', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567922'), 'madre', 'Profesora', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567923'), 'padre', 'Contador', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567924'), 'madre', 'Abogada', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567925'), 'padre', 'Arquitecto', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567926'), 'madre', 'Medica', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567927'), 'padre', 'Empresario', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567928'), 'madre', 'Psicologa', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567929'), 'padre', 'Comerciante', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567930'), 'madre', 'Secretaria', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567931'), 'padre', 'Tecnico', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567932'), 'madre', 'Diseñadora', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567933'), 'padre', 'Mecanico', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567934'), 'madre', 'Farmaceutica', 'activo');

-- Centro Sur
INSERT INTO tutor (id_persona, parentesco, ocupacion, estado) VALUES
((SELECT id FROM persona WHERE cedula = '1234567960'), 'madre', 'Enfermera', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567961'), 'padre', 'Ingeniero Civil', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567962'), 'madre', 'Profesora', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567963'), 'padre', 'Contador Publico', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567964'), 'madre', 'Abogada', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567965'), 'padre', 'Arquitecto', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567966'), 'madre', 'Medica Pediatra', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567967'), 'padre', 'Empresario', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567968'), 'madre', 'Psicologa Clinica', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567969'), 'padre', 'Comerciante', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567970'), 'madre', 'Administradora', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567971'), 'padre', 'Tecnico Informatico', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567972'), 'madre', 'Diseñadora Grafica', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567973'), 'padre', 'Mecanico Automotriz', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567974'), 'madre', 'Farmaceutica', 'activo');

-- =============================================
-- 7. PACIENTES ADICIONALES
-- =============================================

-- Centro Norte
INSERT INTO paciente (id_persona, id_tutor, id_centro, fecha_ingreso, motivo_consulta, observaciones, estado) VALUES
-- Pacientes con tutores correspondientes
((SELECT id FROM persona WHERE cedula = '1234567935'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567920')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-01', 'Retraso en el desarrollo del lenguaje', 'Niño sociable, responde bien a estimulos visuales', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567936'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567921')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-05', 'Dificultades de concentración', 'Requiere rutinas estructuradas', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567937'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567922')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-10', 'Apoyo en motricidad fina', 'Muy motivado en actividades artisticas', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567938'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567923')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-03-15', 'Problemas de articulacion', 'Paciente timido al inicio de las sesiones', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567939'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567924')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-01', 'Refuerzo en lectoescritura', 'Le gustan mucho los cuentos y dibujar', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567940'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567925')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-05', 'Terapia ocupacional', 'Necesita apoyo en actividades de la vida diaria', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567941'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567926')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-10', 'Apoyo en matematicas', 'Estudiante dedicado pero con dificultades en calculo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567942'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567927')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-04-15', 'Dificultades de pronunciacion', 'Muy activa, le gustan los juegos de palabras', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567943'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567928')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-01', 'Fisioterapia por hipotonía', 'Paciente colaborador, muestra mejoras constantes', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567944'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567929')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-05', 'Apoyo en escritura', 'Le cuesta la motricidad fina', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567945'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567930')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-10', 'Terapia del lenguaje', 'Niño muy expresivo, dificultad en fonemas', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567946'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567931')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-05-15', 'Problemas de atencion', 'Requiere pausas frecuentes en actividades', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567947'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567932')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-06-01', 'Apoyo en comprension lectora', 'Estudiante motivado por historias de aventuras', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567948'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567933')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-06-05', 'Terapia ocupacional', 'Necesita fortalecer independencia funcional', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567949'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567934')),
 (SELECT id FROM centros WHERE codigo = 'NORTE'), '2024-06-10', 'Refuerzo academico general', 'Niño sociable, le gusta trabajar en grupo', 'activo');

-- Centro Sur
INSERT INTO paciente (id_persona, id_tutor, id_centro, fecha_ingreso, motivo_consulta, observaciones, estado) VALUES
-- Pacientes con tutores correspondientes
((SELECT id FROM persona WHERE cedula = '1234567975'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567960')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-03-01', 'Retraso en el lenguaje', 'Niña timida pero muy aplicada', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567976'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567961')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-03-05', 'Fisioterapia neurologica', 'Requiere ejercicios especificos de fortalecimiento', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567977'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567962')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-03-10', 'Apoyo en matematicas', 'Le cuesta resolver problemas pero muy persistente', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567978'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567963')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-03-15', 'Terapia del habla', 'Niño muy activo, responde bien a juegos', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567979'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567964')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-04-01', 'Educacion especial', 'Necesita adaptaciones curriculares', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567980'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567965')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-04-05', 'Terapia ocupacional', 'Muy motivado en actividades practicas', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567981'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567966')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-04-10', 'Apoyo en lectoescritura', 'Le encanta leer pero tiene dificultades en escritura', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567982'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567967')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-04-15', 'Fisioterapia pediatrica', 'Paciente colaborador, sigue instrucciones bien', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567983'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567968')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-05-01', 'Problemas de articulacion', 'Niña expresiva, dificultad con algunos sonidos', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567984'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567969')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-05-05', 'Desarrollo cognitivo', 'Necesita estimulacion cognitiva adicional', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567985'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567970')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-05-10', 'Apoyo academico', 'Estudiante aplicada, necesita refuerzo en ciencias', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567986'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567971')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-05-15', 'Terapia del lenguaje', 'Niño muy comunicativo, problemas en pronunciacion', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567987'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567972')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-06-01', 'Educacion especial', 'Requiere atencion individualizada', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567988'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567973')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-06-05', 'Terapia ocupacional', 'Muy independiente, trabaja bien solo', 'activo'),
((SELECT id FROM persona WHERE cedula = '1234567989'),
 (SELECT id FROM tutor WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567974')),
 (SELECT id FROM centros WHERE codigo = 'SUR'), '2024-06-10', 'Apoyo en escritura', 'Le cuesta la escritura pero muy perseverante', 'activo');

-- =============================================
-- 8. ESPECIALIDADES DE PACIENTES ADICIONALES
-- =============================================

-- Centro Norte - Asignar especialidades a pacientes nuevos
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal, prioridad) VALUES
-- Lucas Lopez - Terapia del Lenguaje
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567935')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta'),
-- Martina Mendez - Terapia Psicologica
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567936')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media'),
-- Santiago Rojas - Fisioterapia
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567937')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media'),
-- Camila Cruz - Terapia del Lenguaje
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567938')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta'),
-- Nicolas Reyes - Educacion Especial
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567939')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media'),
-- Valentina Navarro - Terapia Ocupacional
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567940')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta'),
-- Benjamin Soto - Apoyo Academico
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567941')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media'),
-- Sofia Ramos - Terapia del Lenguaje
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567942')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media'),
-- Matias Fernandez - Fisioterapia
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567943')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta'),
-- Emma Guerrero - Educacion Especial
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567944')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media'),
-- Daniel Molina - Terapia del Lenguaje
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567945')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta'),
-- Antonella Delgado - Terapia Psicologica
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567946')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Psicológica' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media'),
-- Gabriel Campos - Educacion Especial
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567947')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media'),
-- Renata Benitez - Terapia Ocupacional
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567948')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'alta'),
-- Joaquin Aguilar - Desarrollo Cognitivo
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567949')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'NORTE')), TRUE, 'media');

-- Centro Sur - Asignar especialidades a pacientes nuevos
INSERT INTO paciente_especialidades (id_paciente, id_especialidad, es_principal, prioridad) VALUES
-- Emilia Vargas - Terapia del Lenguaje
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567975')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'alta'),
-- Tomas Cardenas - Fisioterapia
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567976')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'alta'),
-- Lucia Lara - Apoyo Academico
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567977')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'media'),
-- Agustin Ibarra - Terapia del Lenguaje
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567978')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'media'),
-- Catalina Ochoa - Educacion Especial
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567979')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'alta'),
-- Ian Sandoval - Terapia Ocupacional
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567980')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'media'),
-- Julieta Fuentes - Educacion Especial
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567981')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'media'),
-- Maximiliano Vega - Fisioterapia
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567982')),
 (SELECT id FROM especialidad WHERE nombre = 'Fisioterapia' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'media'),
-- Olivia Cortez - Terapia del Lenguaje
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567983')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'alta'),
-- Felipe Santana - Desarrollo Cognitivo
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567984')),
 (SELECT id FROM especialidad WHERE nombre = 'Desarrollo Cognitivo' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'alta'),
-- Regina Alarcon - Apoyo Academico
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567985')),
 (SELECT id FROM especialidad WHERE nombre = 'Apoyo Académico' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'media'),
-- Bruno Bravo - Terapia del Lenguaje
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567986')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia del Lenguaje' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'media'),
-- Alma Gallegos - Educacion Especial
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567987')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'alta'),
-- Dylan Lozano - Terapia Ocupacional
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567988')),
 (SELECT id FROM especialidad WHERE nombre = 'Terapia Ocupacional' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'media'),
-- Victoria Duran - Educacion Especial
((SELECT id FROM paciente WHERE id_persona = (SELECT id FROM persona WHERE cedula = '1234567989')),
 (SELECT id FROM especialidad WHERE nombre = 'Educación Especial' AND id_centro = (SELECT id FROM centros WHERE codigo = 'SUR')), TRUE, 'media');

-- =============================================
-- FIN DEL ARCHIVO
-- =============================================

-- Resumen de datos insertados
DO $$
DECLARE
    personas_total INTEGER;
    usuarios_total INTEGER;
    personal_total INTEGER;
    pacientes_total INTEGER;
BEGIN
    SELECT COUNT(*) INTO personas_total FROM persona;
    SELECT COUNT(*) INTO usuarios_total FROM usuario;
    SELECT COUNT(*) INTO personal_total FROM personal;
    SELECT COUNT(*) INTO pacientes_total FROM paciente;

    RAISE NOTICE '========================================';
    RAISE NOTICE 'DATOS MASIVOS INSERTADOS EXITOSAMENTE';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Total Personas: %', personas_total;
    RAISE NOTICE 'Total Usuarios: %', usuarios_total;
    RAISE NOTICE 'Total Personal: %', personal_total;
    RAISE NOTICE 'Total Pacientes: %', pacientes_total;
    RAISE NOTICE '========================================';
    RAISE NOTICE 'NOTA: Ejecutar scripts de sesiones y cronogramas por separado';
    RAISE NOTICE '========================================';
END $$;
