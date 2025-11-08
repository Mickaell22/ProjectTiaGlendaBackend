-- ============================================
-- TRIGGER PARA FINALIZACION AUTOMATICA DE SESIONES PEDAGOGICAS
-- ============================================
-- Este trigger actualiza automaticamente el estado de una sesion pedagogica
-- a 'finalizada' cuando todas sus clases del cronograma estan completas.

-- Primero, eliminar el trigger si existe
DROP TRIGGER IF EXISTS trigger_actualizar_estado_sesion_pedagogica ON cronograma_clases;

-- Eliminar la funcion si existe
DROP FUNCTION IF EXISTS actualizar_estado_sesion_pedagogica();

-- Crear la funcion que actualizara el estado de la sesion
CREATE OR REPLACE FUNCTION actualizar_estado_sesion_pedagogica()
RETURNS TRIGGER AS $$
DECLARE
    total_clases INTEGER;
    clases_completadas INTEGER;
    sesion_id_actual INTEGER;
    estado_actual VARCHAR(50);
BEGIN
    -- Obtener el ID de la sesion (NEW para INSERT/UPDATE, OLD para DELETE)
    IF TG_OP = 'DELETE' THEN
        sesion_id_actual := OLD.id_sesion;
    ELSE
        sesion_id_actual := NEW.id_sesion;
    END IF;

    -- Obtener el estado actual de la sesion
    SELECT estado INTO estado_actual
    FROM sesion_pedagogica
    WHERE id = sesion_id_actual;

    -- Solo proceder si la sesion no esta cancelada o ya finalizada
    IF estado_actual NOT IN ('cancelada', 'finalizada') THEN
        -- Contar total de clases programadas para esta sesion
        SELECT COUNT(*) INTO total_clases
        FROM cronograma_clases
        WHERE id_sesion = sesion_id_actual;

        -- Contar clases completadas (estado = 'realizada')
        SELECT COUNT(*) INTO clases_completadas
        FROM cronograma_clases
        WHERE id_sesion = sesion_id_actual
          AND estado = 'realizada';

        -- Si todas las clases estan completadas y hay al menos una clase
        IF total_clases > 0 AND clases_completadas = total_clases THEN
            -- Actualizar el estado de la sesion a 'finalizada'
            UPDATE sesion_pedagogica
            SET estado = 'finalizada',
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id = sesion_id_actual;

            RAISE NOTICE 'Sesion pedagogica % finalizada automaticamente: % de % clases completadas',
                         sesion_id_actual, clases_completadas, total_clases;
        END IF;
    END IF;

    -- Retornar el registro apropiado segun la operacion
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Crear el trigger en la tabla cronograma_clases
CREATE TRIGGER trigger_actualizar_estado_sesion_pedagogica
AFTER INSERT OR UPDATE OR DELETE ON cronograma_clases
FOR EACH ROW
EXECUTE FUNCTION actualizar_estado_sesion_pedagogica();

-- Mensaje de confirmacion
COMMENT ON TRIGGER trigger_actualizar_estado_sesion_pedagogica ON cronograma_clases IS
'Trigger que actualiza automaticamente el estado de una sesion pedagogica a finalizada cuando todas sus clases estan completadas';

COMMENT ON FUNCTION actualizar_estado_sesion_pedagogica() IS
'Funcion que verifica si todas las clases de una sesion pedagogica estan completadas y actualiza el estado de la sesion a finalizada';

-- Fin del script
SELECT 'Trigger de finalizacion automatica para sesiones pedagogicas creado exitosamente' AS mensaje;
