-- Agregar campo nombre_original a la tabla documentos_personal
-- Este campo almacenará el nombre original del archivo subido por el usuario

ALTER TABLE documentos_personal
ADD COLUMN IF NOT EXISTS nombre_original VARCHAR(255);

-- Actualizar registros existentes: copiar nombre_archivo a nombre_original
UPDATE documentos_personal
SET nombre_original = nombre_archivo
WHERE nombre_original IS NULL;

-- Comentario: nombre_archivo contiene el nombre con UUID, nombre_original el nombre del archivo subido
