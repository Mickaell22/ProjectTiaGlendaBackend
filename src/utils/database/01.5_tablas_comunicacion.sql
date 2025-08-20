-- =============================================
-- CENTRO TÍA GLENDA - TABLAS DE COMUNICACIÓN Y OBSERVACIONES
-- Archivo: 01.5_tablas_comunicacion.sql
-- Descripción: Sistema de chat interno y observaciones de sesiones
-- =============================================

-- =============================================
-- 1. TABLA: MENSAJES_CHAT (Sistema de chat interno)
-- =============================================
CREATE TABLE IF NOT EXISTS mensajes_chat (
    id SERIAL PRIMARY KEY,
    id_remitente INTEGER NOT NULL,
    id_destinatario INTEGER NOT NULL,
    mensaje TEXT NOT NULL,
    
    -- Control de lectura
    leido BOOLEAN DEFAULT FALSE,
    fecha_lectura TIMESTAMP,
    
    -- Metadatos del mensaje
    tipo_mensaje VARCHAR(20) DEFAULT 'texto' CHECK (tipo_mensaje IN ('texto', 'archivo', 'imagen', 'urgente')),
    prioridad VARCHAR(10) DEFAULT 'normal' CHECK (prioridad IN ('baja', 'normal', 'alta', 'urgente')),
    es_privado BOOLEAN DEFAULT FALSE,
    
    -- Archivos adjuntos
    ruta_archivo VARCHAR(500),
    nombre_archivo VARCHAR(255),
    tamaño_archivo INTEGER,
    tipo_mime VARCHAR(100),
    
    -- Control por centro
    id_centro INTEGER NOT NULL,
    
    -- Control de eliminación
    eliminado_remitente BOOLEAN DEFAULT FALSE,
    eliminado_destinatario BOOLEAN DEFAULT FALSE,
    fecha_eliminacion_remitente TIMESTAMP,
    fecha_eliminacion_destinatario TIMESTAMP,
    
    -- Auditoría
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_remitente) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_destinatario) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);

-- =============================================
-- 2. TABLA: OBSERVACIONES_SESIONES (Observaciones de sesiones)
-- =============================================
CREATE TABLE IF NOT EXISTS observaciones_sesiones (
    id SERIAL PRIMARY KEY,
    id_sesion INTEGER NOT NULL, -- Puede ser terapéutica o pedagógica
    tipo_sesion VARCHAR(20) NOT NULL CHECK (tipo_sesion IN ('terapeutica', 'pedagogica')),
    id_usuario INTEGER NOT NULL, -- Quien hace la observación
    
    -- Contenido de la observación
    observacion TEXT NOT NULL,
    tipo_observacion VARCHAR(20) DEFAULT 'observacion' CHECK (tipo_observacion IN 
        ('observacion', 'nota', 'alerta', 'progreso', 'falta', 'incidente', 'logro', 'preocupacion')),
    
    -- Control de privacidad
    es_privada BOOLEAN DEFAULT FALSE, -- Solo visible para admin y quien la creó
    es_seguimiento BOOLEAN DEFAULT FALSE, -- Requiere seguimiento
    fecha_seguimiento DATE,
    seguimiento_completado BOOLEAN DEFAULT FALSE,
    
    -- Categorización
    categoria VARCHAR(50), -- comportamiento, academico, social, familiar, etc.
    nivel_importancia VARCHAR(10) DEFAULT 'medio' CHECK (nivel_importancia IN ('bajo', 'medio', 'alto', 'critico')),
    
    -- Archivos adjuntos
    ruta_archivo VARCHAR(500),
    nombre_archivo VARCHAR(255),
    tipo_mime VARCHAR(100),
    
    -- Etiquetas para búsqueda
    etiquetas TEXT[], -- Array de etiquetas
    
    -- Relaciones
    id_paciente INTEGER, -- Paciente específico (si aplica)
    observacion_padre INTEGER, -- Para respuestas o seguimientos
    
    -- Auditoría
    fecha_observacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE SET NULL,
    FOREIGN KEY (observacion_padre) REFERENCES observaciones_sesiones(id) ON DELETE SET NULL
);

-- =============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =============================================

-- Índices para mensajes_chat
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_remitente ON mensajes_chat(id_remitente);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_destinatario ON mensajes_chat(id_destinatario);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_centro ON mensajes_chat(id_centro);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_fecha ON mensajes_chat(fecha_envio);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_leido ON mensajes_chat(leido);
CREATE INDEX IF NOT EXISTS idx_mensajes_chat_conversacion ON mensajes_chat(id_remitente, id_destinatario, fecha_envio);

-- Índices para observaciones_sesiones
CREATE INDEX IF NOT EXISTS idx_observaciones_sesion ON observaciones_sesiones(id_sesion, tipo_sesion);
CREATE INDEX IF NOT EXISTS idx_observaciones_usuario ON observaciones_sesiones(id_usuario);
CREATE INDEX IF NOT EXISTS idx_observaciones_paciente ON observaciones_sesiones(id_paciente);
CREATE INDEX IF NOT EXISTS idx_observaciones_tipo ON observaciones_sesiones(tipo_observacion);
CREATE INDEX IF NOT EXISTS idx_observaciones_fecha ON observaciones_sesiones(fecha_observacion);
CREATE INDEX IF NOT EXISTS idx_observaciones_seguimiento ON observaciones_sesiones(es_seguimiento, seguimiento_completado);
CREATE INDEX IF NOT EXISTS idx_observaciones_privada ON observaciones_sesiones(es_privada);
CREATE INDEX IF NOT EXISTS idx_observaciones_etiquetas ON observaciones_sesiones USING gin(etiquetas);

-- =============================================
-- TRIGGERS PARA AUDITORÍA
-- =============================================
CREATE TRIGGER trigger_mensajes_chat_fecha_modificacion
    BEFORE UPDATE ON mensajes_chat
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_observaciones_sesiones_fecha_modificacion
    BEFORE UPDATE ON observaciones_sesiones
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_fecha_modificacion();

-- =============================================
-- FUNCIONES PARA CHAT
-- =============================================

-- Función para marcar mensaje como leído
CREATE OR REPLACE FUNCTION marcar_mensaje_leido(p_id_mensaje INTEGER, p_id_usuario INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    -- Verificar que el usuario es el destinatario
    IF EXISTS (
        SELECT 1 FROM mensajes_chat 
        WHERE id = p_id_mensaje 
        AND id_destinatario = p_id_usuario
        AND leido = FALSE
    ) THEN
        UPDATE mensajes_chat SET
            leido = TRUE,
            fecha_lectura = CURRENT_TIMESTAMP,
            fecha_modificacion = CURRENT_TIMESTAMP
        WHERE id = p_id_mensaje;
        
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener conversaciones del usuario
CREATE OR REPLACE FUNCTION obtener_conversaciones_usuario(p_id_usuario INTEGER)
RETURNS TABLE (
    id_conversacion INTEGER,
    nombre_contacto VARCHAR,
    ultimo_mensaje TEXT,
    fecha_ultimo_mensaje TIMESTAMP,
    mensajes_no_leidos INTEGER,
    es_ultimo_mensaje_mio BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH conversaciones AS (
        SELECT DISTINCT
            CASE 
                WHEN mc.id_remitente = p_id_usuario THEN mc.id_destinatario
                ELSE mc.id_remitente
            END as id_contacto
        FROM mensajes_chat mc
        WHERE (mc.id_remitente = p_id_usuario OR mc.id_destinatario = p_id_usuario)
        AND mc.eliminado_remitente = FALSE 
        AND mc.eliminado_destinatario = FALSE
    ),
    ultimo_mensaje_por_conversacion AS (
        SELECT 
            c.id_contacto,
            mc.mensaje,
            mc.fecha_envio,
            mc.id_remitente = p_id_usuario as es_mio,
            ROW_NUMBER() OVER (PARTITION BY c.id_contacto ORDER BY mc.fecha_envio DESC) as rn
        FROM conversaciones c
        JOIN mensajes_chat mc ON (
            (mc.id_remitente = p_id_usuario AND mc.id_destinatario = c.id_contacto)
            OR (mc.id_remitente = c.id_contacto AND mc.id_destinatario = p_id_usuario)
        )
        WHERE mc.eliminado_remitente = FALSE 
        AND mc.eliminado_destinatario = FALSE
    )
    SELECT 
        c.id_contacto,
        pe.nombre || ' ' || pe.apellido as nombre_contacto,
        um.mensaje,
        um.fecha_envio,
        COALESCE(
            (SELECT COUNT(*)::INTEGER 
             FROM mensajes_chat mc2 
             WHERE mc2.id_remitente = c.id_contacto 
             AND mc2.id_destinatario = p_id_usuario 
             AND mc2.leido = FALSE
             AND mc2.eliminado_destinatario = FALSE), 0
        ) as mensajes_no_leidos,
        um.es_mio
    FROM conversaciones c
    JOIN usuario u ON c.id_contacto = u.id
    JOIN persona pe ON u.persona_id = pe.id
    LEFT JOIN ultimo_mensaje_por_conversacion um ON c.id_contacto = um.id_contacto AND um.rn = 1
    ORDER BY um.fecha_envio DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Función para buscar mensajes
CREATE OR REPLACE FUNCTION buscar_mensajes(
    p_id_usuario INTEGER,
    p_texto_busqueda TEXT DEFAULT NULL,
    p_id_contacto INTEGER DEFAULT NULL,
    p_fecha_desde DATE DEFAULT NULL,
    p_fecha_hasta DATE DEFAULT NULL
) RETURNS TABLE (
    id_mensaje INTEGER,
    id_remitente INTEGER,
    nombre_remitente VARCHAR,
    id_destinatario INTEGER,
    nombre_destinatario VARCHAR,
    mensaje TEXT,
    fecha_envio TIMESTAMP,
    leido BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mc.id,
        mc.id_remitente,
        pr.nombre || ' ' || pr.apellido as nombre_remitente,
        mc.id_destinatario,
        pd.nombre || ' ' || pd.apellido as nombre_destinatario,
        mc.mensaje,
        mc.fecha_envio,
        mc.leido
    FROM mensajes_chat mc
    JOIN usuario ur ON mc.id_remitente = ur.id
    JOIN persona pr ON ur.persona_id = pr.id
    JOIN usuario ud ON mc.id_destinatario = ud.id
    JOIN persona pd ON ud.persona_id = pd.id
    WHERE (mc.id_remitente = p_id_usuario OR mc.id_destinatario = p_id_usuario)
    AND mc.eliminado_remitente = FALSE 
    AND mc.eliminado_destinatario = FALSE
    AND (p_texto_busqueda IS NULL OR mc.mensaje ILIKE '%' || p_texto_busqueda || '%')
    AND (p_id_contacto IS NULL OR mc.id_remitente = p_id_contacto OR mc.id_destinatario = p_id_contacto)
    AND (p_fecha_desde IS NULL OR mc.fecha_envio::DATE >= p_fecha_desde)
    AND (p_fecha_hasta IS NULL OR mc.fecha_envio::DATE <= p_fecha_hasta)
    ORDER BY mc.fecha_envio DESC;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- FUNCIONES PARA OBSERVACIONES
-- =============================================

-- Función para obtener observaciones de una sesión
CREATE OR REPLACE FUNCTION obtener_observaciones_sesion(
    p_id_sesion INTEGER,
    p_tipo_sesion VARCHAR(20),
    p_id_usuario INTEGER DEFAULT NULL
) RETURNS TABLE (
    id_observacion INTEGER,
    observacion TEXT,
    tipo_observacion VARCHAR,
    nombre_usuario VARCHAR,
    fecha_observacion TIMESTAMP,
    es_seguimiento BOOLEAN,
    nivel_importancia VARCHAR,
    categoria VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        obs.id,
        obs.observacion,
        obs.tipo_observacion,
        pe.nombre || ' ' || pe.apellido as nombre_usuario,
        obs.fecha_observacion,
        obs.es_seguimiento,
        obs.nivel_importancia,
        obs.categoria
    FROM observaciones_sesiones obs
    JOIN usuario u ON obs.id_usuario = u.id
    JOIN persona pe ON u.persona_id = pe.id
    WHERE obs.id_sesion = p_id_sesion
    AND obs.tipo_sesion = p_tipo_sesion
    AND (
        obs.es_privada = FALSE 
        OR obs.id_usuario = p_id_usuario 
        OR p_id_usuario IS NULL
    )
    ORDER BY obs.fecha_observacion DESC;
END;
$$ LANGUAGE plpgsql;

-- Función para buscar observaciones
CREATE OR REPLACE FUNCTION buscar_observaciones(
    p_texto_busqueda TEXT DEFAULT NULL,
    p_tipo_observacion VARCHAR DEFAULT NULL,
    p_tipo_sesion VARCHAR DEFAULT NULL,
    p_id_usuario INTEGER DEFAULT NULL,
    p_fecha_desde DATE DEFAULT NULL,
    p_fecha_hasta DATE DEFAULT NULL,
    p_solo_seguimientos BOOLEAN DEFAULT FALSE
) RETURNS TABLE (
    id_observacion INTEGER,
    observacion TEXT,
    tipo_observacion VARCHAR,
    tipo_sesion VARCHAR,
    nombre_usuario VARCHAR,
    fecha_observacion TIMESTAMP,
    es_seguimiento BOOLEAN,
    nivel_importancia VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        obs.id,
        obs.observacion,
        obs.tipo_observacion,
        obs.tipo_sesion,
        pe.nombre || ' ' || pe.apellido as nombre_usuario,
        obs.fecha_observacion,
        obs.es_seguimiento,
        obs.nivel_importancia
    FROM observaciones_sesiones obs
    JOIN usuario u ON obs.id_usuario = u.id
    JOIN persona pe ON u.persona_id = pe.id
    WHERE (p_texto_busqueda IS NULL OR obs.observacion ILIKE '%' || p_texto_busqueda || '%')
    AND (p_tipo_observacion IS NULL OR obs.tipo_observacion = p_tipo_observacion)
    AND (p_tipo_sesion IS NULL OR obs.tipo_sesion = p_tipo_sesion)
    AND (p_id_usuario IS NULL OR obs.id_usuario = p_id_usuario)
    AND (p_fecha_desde IS NULL OR obs.fecha_observacion::DATE >= p_fecha_desde)
    AND (p_fecha_hasta IS NULL OR obs.fecha_observacion::DATE <= p_fecha_hasta)
    AND (p_solo_seguimientos = FALSE OR obs.es_seguimiento = TRUE)
    AND (obs.es_privada = FALSE OR obs.id_usuario = p_id_usuario)
    ORDER BY obs.fecha_observacion DESC;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener seguimientos pendientes
CREATE OR REPLACE FUNCTION obtener_seguimientos_pendientes(p_id_usuario INTEGER DEFAULT NULL)
RETURNS TABLE (
    id_observacion INTEGER,
    observacion TEXT,
    tipo_sesion VARCHAR,
    fecha_seguimiento DATE,
    dias_pendientes INTEGER,
    nivel_importancia VARCHAR,
    nombre_usuario VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        obs.id,
        obs.observacion,
        obs.tipo_sesion,
        obs.fecha_seguimiento,
        (obs.fecha_seguimiento - CURRENT_DATE)::INTEGER as dias_pendientes,
        obs.nivel_importancia,
        pe.nombre || ' ' || pe.apellido as nombre_usuario
    FROM observaciones_sesiones obs
    JOIN usuario u ON obs.id_usuario = u.id
    JOIN persona pe ON u.persona_id = pe.id
    WHERE obs.es_seguimiento = TRUE
    AND obs.seguimiento_completado = FALSE
    AND obs.fecha_seguimiento IS NOT NULL
    AND (p_id_usuario IS NULL OR obs.id_usuario = p_id_usuario)
    AND (obs.es_privada = FALSE OR obs.id_usuario = p_id_usuario)
    ORDER BY obs.fecha_seguimiento ASC;
END;
$$ LANGUAGE plpgsql;

-- Función para completar seguimiento
CREATE OR REPLACE FUNCTION completar_seguimiento(
    p_id_observacion INTEGER,
    p_id_usuario INTEGER,
    p_observacion_seguimiento TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    observacion_seguimiento_id INTEGER;
BEGIN
    -- Verificar permisos
    IF NOT EXISTS (
        SELECT 1 FROM observaciones_sesiones 
        WHERE id = p_id_observacion 
        AND (id_usuario = p_id_usuario OR NOT es_privada)
    ) THEN
        RETURN FALSE;
    END IF;
    
    -- Marcar seguimiento como completado
    UPDATE observaciones_sesiones SET
        seguimiento_completado = TRUE,
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id = p_id_observacion;
    
    -- Si hay observación de seguimiento, crearla
    IF p_observacion_seguimiento IS NOT NULL THEN
        INSERT INTO observaciones_sesiones (
            id_sesion, tipo_sesion, id_usuario, observacion,
            tipo_observacion, observacion_padre
        )
        SELECT 
            id_sesion, tipo_sesion, p_id_usuario, p_observacion_seguimiento,
            'seguimiento', p_id_observacion
        FROM observaciones_sesiones
        WHERE id = p_id_observacion;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- COMENTARIOS EN TABLAS
-- =============================================
COMMENT ON TABLE mensajes_chat IS 'Sistema de mensajería interna entre usuarios del centro';
COMMENT ON TABLE observaciones_sesiones IS 'Observaciones y notas sobre sesiones terapéuticas y pedagógicas';

COMMENT ON COLUMN mensajes_chat.es_privado IS 'Indica si el mensaje es privado (solo visible para remitente y destinatario)';
COMMENT ON COLUMN mensajes_chat.prioridad IS 'Prioridad del mensaje para notificaciones';
COMMENT ON COLUMN observaciones_sesiones.es_privada IS 'Solo visible para quien la creó y administradores';
COMMENT ON COLUMN observaciones_sesiones.es_seguimiento IS 'Requiere seguimiento o acción posterior';
COMMENT ON COLUMN observaciones_sesiones.etiquetas IS 'Etiquetas para categorización y búsqueda avanzada';