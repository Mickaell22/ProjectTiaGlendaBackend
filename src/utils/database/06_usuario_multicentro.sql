-- =============================================
-- SISTEMA MULTI-CENTRO PARA USUARIOS
-- Archivo: 06_usuario_multicentro.sql
-- Descripcion: Implementa soporte para usuarios con acceso a multiples centros
-- =============================================

-- =============================================
-- PASO 1: CREAR TABLA USUARIO_CENTROS
-- =============================================

-- Eliminar tabla si existe (para desarrollo/testing)
DROP TABLE IF EXISTS usuario_centros CASCADE;

-- Crear tabla de relacion usuario-centros
CREATE TABLE usuario_centros (
    id SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    id_centro INTEGER NOT NULL,

    -- Control de centro predeterminado
    es_centro_predeterminado BOOLEAN DEFAULT FALSE,

    -- Auditoría
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,

    -- Claves foráneas
    FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE CASCADE,

    -- Constraint para evitar duplicados
    UNIQUE(id_usuario, id_centro)
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_usuario_centros_usuario ON usuario_centros(id_usuario);
CREATE INDEX IF NOT EXISTS idx_usuario_centros_centro ON usuario_centros(id_centro);
CREATE INDEX IF NOT EXISTS idx_usuario_centros_predeterminado ON usuario_centros(id_usuario, es_centro_predeterminado);

-- Trigger para actualizar fecha_modificacion
CREATE TRIGGER trigger_usuario_centros_fecha_modificacion
    BEFORE UPDATE ON usuario_centros
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- Comentarios
COMMENT ON TABLE usuario_centros IS 'Relacion de usuarios con multiples centros de atencion';
COMMENT ON COLUMN usuario_centros.es_centro_predeterminado IS 'Indica si este es el centro predeterminado del usuario al iniciar sesion';

-- =============================================
-- PASO 2: MIGRAR DATOS EXISTENTES
-- =============================================

-- Migrar todos los usuarios existentes con su centro actual a la nueva tabla
INSERT INTO usuario_centros (id_usuario, id_centro, es_centro_predeterminado, usuario_creacion)
SELECT
    id as id_usuario,
    id_centro,
    TRUE as es_centro_predeterminado,
    1 as usuario_creacion
FROM usuario
WHERE id_centro IS NOT NULL
ON CONFLICT (id_usuario, id_centro) DO NOTHING;

-- =============================================
-- PASO 3: ASIGNAR TODOS LOS USUARIOS A AMBOS CENTROS
-- =============================================
-- Nota: Segun los requerimientos, todos los trabajadores actuales
-- trabajan en ambos centros (Norte y Sur)

-- Obtener IDs de los centros
DO $$
DECLARE
    centro_norte_id INTEGER;
    centro_sur_id INTEGER;
BEGIN
    -- Obtener ID del Centro Norte
    SELECT id INTO centro_norte_id FROM centros WHERE codigo = 'NORTE' LIMIT 1;

    -- Obtener ID del Centro Sur
    SELECT id INTO centro_sur_id FROM centros WHERE codigo = 'SUR' LIMIT 1;

    -- Verificar que ambos centros existen
    IF centro_norte_id IS NULL OR centro_sur_id IS NULL THEN
        RAISE NOTICE 'ADVERTENCIA: No se encontraron ambos centros (Norte y Sur)';
        RAISE NOTICE 'Centro Norte ID: %, Centro Sur ID: %', centro_norte_id, centro_sur_id;
    ELSE
        -- Agregar todos los usuarios al Centro Norte (si no estan ya)
        INSERT INTO usuario_centros (id_usuario, id_centro, es_centro_predeterminado, usuario_creacion)
        SELECT
            id as id_usuario,
            centro_norte_id as id_centro,
            -- Es predeterminado solo si el usuario actualmente esta en Norte
            CASE WHEN id_centro = centro_norte_id THEN TRUE ELSE FALSE END as es_centro_predeterminado,
            1 as usuario_creacion
        FROM usuario
        WHERE NOT EXISTS (
            SELECT 1 FROM usuario_centros uc
            WHERE uc.id_usuario = usuario.id
            AND uc.id_centro = centro_norte_id
        )
        ON CONFLICT (id_usuario, id_centro) DO NOTHING;

        -- Agregar todos los usuarios al Centro Sur (si no estan ya)
        INSERT INTO usuario_centros (id_usuario, id_centro, es_centro_predeterminado, usuario_creacion)
        SELECT
            id as id_usuario,
            centro_sur_id as id_centro,
            -- Es predeterminado solo si el usuario actualmente esta en Sur
            CASE WHEN id_centro = centro_sur_id THEN TRUE ELSE FALSE END as es_centro_predeterminado,
            1 as usuario_creacion
        FROM usuario
        WHERE NOT EXISTS (
            SELECT 1 FROM usuario_centros uc
            WHERE uc.id_usuario = usuario.id
            AND uc.id_centro = centro_sur_id
        )
        ON CONFLICT (id_usuario, id_centro) DO NOTHING;

        RAISE NOTICE 'Migracion completada: Todos los usuarios ahora tienen acceso a ambos centros';
    END IF;
END $$;

-- =============================================
-- PASO 4: FUNCION PARA OBTENER CENTROS DE UN USUARIO
-- =============================================

CREATE OR REPLACE FUNCTION get_centros_usuario(p_id_usuario INTEGER)
RETURNS TABLE (
    id INTEGER,
    nombre VARCHAR(100),
    codigo VARCHAR(10),
    direccion VARCHAR(255),
    telefono VARCHAR(15),
    es_predeterminado BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.nombre,
        c.codigo,
        c.direccion,
        c.telefono,
        uc.es_centro_predeterminado as es_predeterminado
    FROM usuario_centros uc
    INNER JOIN centros c ON uc.id_centro = c.id
    WHERE uc.id_usuario = p_id_usuario
    AND c.estado = 'activo'
    ORDER BY uc.es_centro_predeterminado DESC, c.nombre ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_centros_usuario(INTEGER) IS 'Obtiene la lista de centros disponibles para un usuario';

-- =============================================
-- PASO 5: FUNCION PARA VALIDAR ACCESO A CENTRO
-- =============================================

CREATE OR REPLACE FUNCTION validar_acceso_centro(
    p_id_usuario INTEGER,
    p_id_centro INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_tiene_acceso BOOLEAN;
BEGIN
    -- Verificar si el usuario tiene acceso al centro
    SELECT EXISTS(
        SELECT 1
        FROM usuario_centros
        WHERE id_usuario = p_id_usuario
        AND id_centro = p_id_centro
    ) INTO v_tiene_acceso;

    RETURN v_tiene_acceso;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validar_acceso_centro(INTEGER, INTEGER) IS 'Valida si un usuario tiene acceso a un centro especifico';

-- =============================================
-- PASO 6: FUNCION PARA ESTABLECER CENTRO PREDETERMINADO
-- =============================================

CREATE OR REPLACE FUNCTION establecer_centro_predeterminado(
    p_id_usuario INTEGER,
    p_id_centro INTEGER
) RETURNS BOOLEAN AS $$
BEGIN
    -- Verificar que el usuario tiene acceso a ese centro
    IF NOT validar_acceso_centro(p_id_usuario, p_id_centro) THEN
        RAISE EXCEPTION 'El usuario no tiene acceso al centro especificado';
    END IF;

    -- Quitar el flag de predeterminado de todos los centros del usuario
    UPDATE usuario_centros
    SET es_centro_predeterminado = FALSE
    WHERE id_usuario = p_id_usuario;

    -- Establecer el nuevo centro predeterminado
    UPDATE usuario_centros
    SET es_centro_predeterminado = TRUE
    WHERE id_usuario = p_id_usuario
    AND id_centro = p_id_centro;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION establecer_centro_predeterminado(INTEGER, INTEGER) IS 'Establece el centro predeterminado para un usuario';

-- =============================================
-- PASO 7: TRIGGER PARA GARANTIZAR UN CENTRO PREDETERMINADO
-- =============================================

CREATE OR REPLACE FUNCTION garantizar_centro_predeterminado()
RETURNS TRIGGER AS $$
DECLARE
    v_count_centros INTEGER;
    v_count_predeterminados INTEGER;
BEGIN
    -- Si es un INSERT, verificar si el usuario ya tiene centros
    IF TG_OP = 'INSERT' THEN
        -- Contar cuantos centros tiene el usuario
        SELECT COUNT(*) INTO v_count_centros
        FROM usuario_centros
        WHERE id_usuario = NEW.id_usuario;

        -- Si es el primer centro, hacerlo predeterminado
        IF v_count_centros = 1 THEN
            NEW.es_centro_predeterminado = TRUE;
        END IF;

        -- Si se marca como predeterminado, quitar el flag de los demas
        IF NEW.es_centro_predeterminado = TRUE THEN
            UPDATE usuario_centros
            SET es_centro_predeterminado = FALSE
            WHERE id_usuario = NEW.id_usuario
            AND id != NEW.id;
        END IF;
    END IF;

    -- Si es un UPDATE y se quita el flag de predeterminado
    IF TG_OP = 'UPDATE' AND OLD.es_centro_predeterminado = TRUE AND NEW.es_centro_predeterminado = FALSE THEN
        -- Contar cuantos predeterminados quedan
        SELECT COUNT(*) INTO v_count_predeterminados
        FROM usuario_centros
        WHERE id_usuario = NEW.id_usuario
        AND es_centro_predeterminado = TRUE
        AND id != NEW.id;

        -- Si no queda ninguno predeterminado, mantener este como predeterminado
        IF v_count_predeterminados = 0 THEN
            NEW.es_centro_predeterminado = TRUE;
            RAISE NOTICE 'No se puede quitar el ultimo centro predeterminado del usuario';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger
CREATE TRIGGER trigger_garantizar_centro_predeterminado
    BEFORE INSERT OR UPDATE ON usuario_centros
    FOR EACH ROW
    EXECUTE FUNCTION garantizar_centro_predeterminado();

COMMENT ON FUNCTION garantizar_centro_predeterminado() IS 'Garantiza que cada usuario tenga al menos un centro predeterminado';

-- =============================================
-- PASO 8: NOTA IMPORTANTE SOBRE LA COLUMNA id_centro EN USUARIO
-- =============================================
-- IMPORTANTE: La columna id_centro en la tabla usuario se mantiene
-- por compatibilidad con el codigo existente, pero ahora se usa
-- principalmente como referencia del centro predeterminado.
--
-- La relacion usuario_centros es la fuente de verdad para
-- determinar a que centros tiene acceso un usuario.
--
-- En el futuro, se puede considerar hacer id_centro NULLABLE
-- y deprecar su uso a favor de usuario_centros.
-- =============================================

-- =============================================
-- VERIFICACION FINAL
-- =============================================

DO $$
DECLARE
    v_total_usuarios INTEGER;
    v_total_relaciones INTEGER;
    v_usuarios_sin_centros INTEGER;
BEGIN
    -- Contar usuarios
    SELECT COUNT(*) INTO v_total_usuarios FROM usuario WHERE estado = 'activo';

    -- Contar relaciones
    SELECT COUNT(*) INTO v_total_relaciones FROM usuario_centros;

    -- Contar usuarios sin centros
    SELECT COUNT(*) INTO v_usuarios_sin_centros
    FROM usuario u
    WHERE u.estado = 'activo'
    AND NOT EXISTS (
        SELECT 1 FROM usuario_centros uc WHERE uc.id_usuario = u.id
    );

    RAISE NOTICE '==============================================';
    RAISE NOTICE 'MIGRACION MULTI-CENTRO COMPLETADA';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Total de usuarios activos: %', v_total_usuarios;
    RAISE NOTICE 'Total de relaciones usuario-centro: %', v_total_relaciones;
    RAISE NOTICE 'Usuarios sin centros asignados: %', v_usuarios_sin_centros;
    RAISE NOTICE '==============================================';

    IF v_usuarios_sin_centros > 0 THEN
        RAISE WARNING 'HAY USUARIOS SIN CENTROS ASIGNADOS. Por favor, asigneles centros manualmente.';
    END IF;
END $$;
