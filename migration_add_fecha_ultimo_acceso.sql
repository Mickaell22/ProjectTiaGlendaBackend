-- Migración: Agregar campo fecha_ultimo_acceso a tabla usuario
-- Ejecutar este script para bases de datos existentes

-- Verificar si la columna no existe y agregarla
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='usuario' 
        AND column_name='fecha_ultimo_acceso'
    ) THEN
        ALTER TABLE usuario ADD COLUMN fecha_ultimo_acceso TIMESTAMP;
        RAISE NOTICE 'Columna fecha_ultimo_acceso agregada exitosamente a la tabla usuario';
    ELSE
        RAISE NOTICE 'La columna fecha_ultimo_acceso ya existe en la tabla usuario';
    END IF;
END $$;

-- Actualizar índices si es necesario
-- CREATE INDEX IF NOT EXISTS idx_usuario_ultimo_acceso ON usuario(fecha_ultimo_acceso);

-- Comentario sobre la nueva columna
COMMENT ON COLUMN usuario.fecha_ultimo_acceso IS 'Fecha y hora del último acceso exitoso del usuario al sistema';