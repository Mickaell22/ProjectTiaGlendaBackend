-- =============================================
-- MIGRACION: Soporte para Multiples Tutores por Paciente
-- Fecha: 2025-01-08
-- Descripcion: Permite que un paciente tenga multiples tutores/responsables
-- =============================================

-- PASO 1: Crear tabla intermedia paciente_tutor
-- Esta tabla maneja la relacion muchos-a-muchos entre pacientes y tutores
CREATE TABLE IF NOT EXISTS paciente_tutor (
    id SERIAL PRIMARY KEY,
    id_paciente INTEGER NOT NULL,
    id_tutor INTEGER NOT NULL,
    es_principal BOOLEAN DEFAULT FALSE,
    tipo_relacion VARCHAR(50), -- padre, madre, abuelo, tio, tutor_legal, etc.
    fecha_asignacion DATE DEFAULT CURRENT_DATE,
    observaciones TEXT,
    puede_autorizar BOOLEAN DEFAULT TRUE, -- Si puede autorizar tratamientos
    puede_retirar BOOLEAN DEFAULT TRUE, -- Si puede retirar al paciente
    contacto_emergencia BOOLEAN DEFAULT FALSE, -- Si es contacto de emergencia
    prioridad_contacto INTEGER DEFAULT 1, -- Orden de prioridad al contactar (1=primero)

    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,

    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE CASCADE,
    FOREIGN KEY (id_tutor) REFERENCES tutor(id) ON DELETE RESTRICT,

    -- Constraint para evitar duplicados
    UNIQUE (id_paciente, id_tutor)
);

-- PASO 2: Migrar datos existentes de paciente.id_tutor a paciente_tutor
-- Esto preserva las relaciones actuales marcandolas como principales
INSERT INTO paciente_tutor (
    id_paciente,
    id_tutor,
    es_principal,
    tipo_relacion,
    puede_autorizar,
    puede_retirar,
    contacto_emergencia,
    prioridad_contacto,
    estado,
    usuario_creacion,
    fecha_creacion
)
SELECT
    p.id as id_paciente,
    p.id_tutor,
    TRUE as es_principal, -- El tutor actual se marca como principal
    t.parentesco as tipo_relacion,
    TRUE as puede_autorizar,
    TRUE as puede_retirar,
    TRUE as contacto_emergencia,
    1 as prioridad_contacto,
    'activo' as estado,
    p.usuario_creacion,
    p.fecha_creacion
FROM paciente p
INNER JOIN tutor t ON p.id_tutor = t.id
WHERE p.id_tutor IS NOT NULL
ON CONFLICT (id_paciente, id_tutor) DO NOTHING;

-- PASO 3: Hacer el campo id_tutor NULLABLE en la tabla paciente
-- IMPORTANTE: Ejecutar esto solo DESPUES de verificar que la migracion fue exitosa
-- ALTER TABLE paciente ALTER COLUMN id_tutor DROP NOT NULL;

-- PASO 4 (OPCIONAL): Eliminar constraint de foreign key de id_tutor
-- Esto se puede hacer mas adelante cuando se verifique que todo funciona correctamente
-- ALTER TABLE paciente DROP CONSTRAINT paciente_id_tutor_fkey;

-- PASO 5: Crear indices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_paciente_tutor_paciente ON paciente_tutor(id_paciente);
CREATE INDEX IF NOT EXISTS idx_paciente_tutor_tutor ON paciente_tutor(id_tutor);
CREATE INDEX IF NOT EXISTS idx_paciente_tutor_principal ON paciente_tutor(id_paciente, es_principal) WHERE es_principal = TRUE;
CREATE INDEX IF NOT EXISTS idx_paciente_tutor_emergencia ON paciente_tutor(id_paciente, contacto_emergencia) WHERE contacto_emergencia = TRUE;

-- PASO 6: Crear trigger para actualizar fecha_modificacion
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion_paciente_tutor()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_fecha_modificacion_paciente_tutor
BEFORE UPDATE ON paciente_tutor
FOR EACH ROW
EXECUTE FUNCTION actualizar_fecha_modificacion_paciente_tutor();

-- PASO 7: Crear trigger para validar que solo haya un tutor principal por paciente
CREATE OR REPLACE FUNCTION validar_un_tutor_principal()
RETURNS TRIGGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    -- Solo validar si se esta marcando como principal
    IF NEW.es_principal = TRUE THEN
        -- Contar cuantos tutores principales tiene el paciente (excluyendo el actual)
        SELECT COUNT(*) INTO v_count
        FROM paciente_tutor
        WHERE id_paciente = NEW.id_paciente
          AND es_principal = TRUE
          AND estado = 'activo'
          AND id != COALESCE(NEW.id, 0);

        -- Si ya existe otro principal, remover el flag del anterior automaticamente
        IF v_count > 0 THEN
            UPDATE paciente_tutor
            SET es_principal = FALSE,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_paciente = NEW.id_paciente
              AND es_principal = TRUE
              AND estado = 'activo'
              AND id != COALESCE(NEW.id, 0);
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validar_un_tutor_principal
BEFORE INSERT OR UPDATE ON paciente_tutor
FOR EACH ROW
EXECUTE FUNCTION validar_un_tutor_principal();

-- PASO 8: Crear vista para facilitar consultas de pacientes con sus tutores
CREATE OR REPLACE VIEW vista_pacientes_tutores AS
SELECT
    pac.id as paciente_id,
    pac.codigo_paciente,
    CONCAT(p_pac.nombre, ' ', p_pac.apellido) as nombre_paciente,
    p_pac.cedula as cedula_paciente,

    -- Informacion del tutor
    pt.id as paciente_tutor_id,
    t.id as tutor_id,
    CONCAT(p_tut.nombre, ' ', p_tut.apellido) as nombre_tutor,
    p_tut.cedula as cedula_tutor,
    p_tut.telefono as telefono_tutor,
    p_tut.correo as correo_tutor,

    -- Relacion
    pt.es_principal,
    pt.tipo_relacion,
    pt.puede_autorizar,
    pt.puede_retirar,
    pt.contacto_emergencia,
    pt.prioridad_contacto,
    pt.observaciones as observaciones_relacion,
    pt.estado as estado_relacion,

    -- Informacion adicional del tutor
    t.ocupacion,
    t.nombre_empresa,
    t.telefono_empresa,

    pac.estado as estado_paciente,
    pac.estado_tratamiento
FROM paciente pac
INNER JOIN persona p_pac ON pac.id_persona = p_pac.id
LEFT JOIN paciente_tutor pt ON pac.id = pt.id_paciente AND pt.estado = 'activo'
LEFT JOIN tutor t ON pt.id_tutor = t.id
LEFT JOIN persona p_tut ON t.id_persona = p_tut.id
WHERE pac.estado != 'eliminado'
ORDER BY pac.id, pt.es_principal DESC, pt.prioridad_contacto;

-- PASO 9: Agregar comentarios a las tablas y columnas
COMMENT ON TABLE paciente_tutor IS 'Relacion muchos-a-muchos entre pacientes y tutores/responsables';
COMMENT ON COLUMN paciente_tutor.es_principal IS 'Indica si este es el tutor principal del paciente (solo uno puede serlo)';
COMMENT ON COLUMN paciente_tutor.tipo_relacion IS 'Tipo de relacion familiar o legal con el paciente';
COMMENT ON COLUMN paciente_tutor.puede_autorizar IS 'Si el tutor puede autorizar tratamientos medicos';
COMMENT ON COLUMN paciente_tutor.puede_retirar IS 'Si el tutor puede retirar al paciente del centro';
COMMENT ON COLUMN paciente_tutor.contacto_emergencia IS 'Si es un contacto de emergencia prioritario';
COMMENT ON COLUMN paciente_tutor.prioridad_contacto IS 'Orden de prioridad al contactar (1=primero, 2=segundo, etc)';

-- =============================================
-- INSTRUCCIONES DE ROLLBACK (en caso de necesitar revertir)
-- =============================================
-- DROP VIEW IF EXISTS vista_pacientes_tutores;
-- DROP TRIGGER IF EXISTS trigger_validar_un_tutor_principal ON paciente_tutor;
-- DROP FUNCTION IF EXISTS validar_un_tutor_principal();
-- DROP TRIGGER IF EXISTS trigger_actualizar_fecha_modificacion_paciente_tutor ON paciente_tutor;
-- DROP FUNCTION IF EXISTS actualizar_fecha_modificacion_paciente_tutor();
-- DROP TABLE IF EXISTS paciente_tutor CASCADE;
-- ALTER TABLE paciente ALTER COLUMN id_tutor SET NOT NULL; -- Solo si se ejecuto PASO 3

-- =============================================
-- VERIFICACION POST-MIGRACION
-- =============================================
-- Ejecutar estas queries para verificar que la migracion fue exitosa:
--
-- 1. Verificar que todos los pacientes tienen al menos un tutor:
-- SELECT p.id, p.codigo_paciente, COUNT(pt.id) as total_tutores
-- FROM paciente p
-- LEFT JOIN paciente_tutor pt ON p.id = pt.id_paciente AND pt.estado = 'activo'
-- WHERE p.estado != 'eliminado'
-- GROUP BY p.id, p.codigo_paciente
-- HAVING COUNT(pt.id) = 0;
-- (Esta query debe retornar 0 filas)
--
-- 2. Verificar que cada paciente tiene exactamente un tutor principal:
-- SELECT id_paciente, COUNT(*) as total_principales
-- FROM paciente_tutor
-- WHERE es_principal = TRUE AND estado = 'activo'
-- GROUP BY id_paciente
-- HAVING COUNT(*) != 1;
-- (Esta query debe retornar 0 filas)
--
-- 3. Ver estadisticas generales:
-- SELECT
--     COUNT(DISTINCT id_paciente) as total_pacientes,
--     COUNT(*) as total_relaciones,
--     AVG(tutores_por_paciente) as promedio_tutores
-- FROM (
--     SELECT id_paciente, COUNT(*) as tutores_por_paciente
--     FROM paciente_tutor
--     WHERE estado = 'activo'
--     GROUP BY id_paciente
-- ) sub;
