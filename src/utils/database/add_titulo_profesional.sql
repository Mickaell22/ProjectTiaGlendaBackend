-- Agregar campo titulo_profesional a la tabla personal
-- Este campo ya se requiere en el frontend y backend

ALTER TABLE personal 
ADD COLUMN titulo_profesional VARCHAR(100);

-- Opcional: Migrar datos existentes del campo cargo al nuevo campo titulo_profesional
-- UPDATE personal SET titulo_profesional = cargo WHERE titulo_profesional IS NULL;

-- Comentar la línea anterior si prefieres que titulo_profesional sea independiente de cargo