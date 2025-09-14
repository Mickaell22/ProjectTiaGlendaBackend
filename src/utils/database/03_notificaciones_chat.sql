-- =============================================
-- CENTRO TÍA GLENDA - SISTEMA DE NOTIFICACIONES PUSH
-- Archivo: 03_notificaciones_chat.sql
-- Descripción: Creación de tablas para notificaciones automáticas
-- =============================================

-- Eliminar tablas si existen
DROP TABLE IF EXISTS notificaciones_push CASCADE;
DROP TABLE IF EXISTS configuracion_notificaciones_push CASCADE;

-- =============================================
-- TABLA: CONFIGURACION_NOTIFICACIONES_PUSH
-- =============================================
CREATE TABLE configuracion_notificaciones_push (
    id INTEGER PRIMARY KEY DEFAULT 1,
    
    -- Configuración general
    notificaciones_habilitadas BOOLEAN DEFAULT TRUE,
    
    -- Configuración de sesiones terapéuticas
    notificar_sesiones_terapia BOOLEAN DEFAULT TRUE,
    minutos_previos_sesion_terapia INTEGER DEFAULT 15,
    
    -- Configuración de clases pedagógicas
    notificar_clases_pedagogicas BOOLEAN DEFAULT TRUE,
    minutos_previos_clase_pedagogica INTEGER DEFAULT 15,
    
    -- Configuración de cancelaciones y reprogramaciones
    notificar_cancelaciones BOOLEAN DEFAULT TRUE,
    notificar_reprogramaciones BOOLEAN DEFAULT TRUE,
    
    -- Configuración de mensajes de chat
    notificar_mensajes_chat BOOLEAN DEFAULT TRUE,
    notificar_solo_mensajes_urgentes BOOLEAN DEFAULT FALSE,
    
    -- Configuración de horarios de silencio
    horario_silencio_inicio TIME DEFAULT '22:00:00',
    horario_silencio_fin TIME DEFAULT '07:00:00',
    
    -- Configuración de frecuencia de verificación
    intervalo_verificacion_minutos INTEGER DEFAULT 1,
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

-- Insertar configuración por defecto
INSERT INTO configuracion_notificaciones_push DEFAULT VALUES;

-- =============================================
-- TABLA: NOTIFICACIONES_PUSH
-- =============================================
CREATE TABLE notificaciones_push (
    id SERIAL PRIMARY KEY,
    
    -- Usuario destinatario
    id_usuario INTEGER NOT NULL,
    id_centro INTEGER NOT NULL,
    
    -- Contenido de la notificación
    titulo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,
    
    -- Tipo de notificación
    tipo_notificacion VARCHAR(30) NOT NULL CHECK (tipo_notificacion IN (
        'sesion_terapia', 'clase_pedagogica', 'cancelacion', 
        'reprogramacion', 'mensaje_chat', 'recordatorio_general'
    )),
    
    -- Prioridad
    prioridad VARCHAR(10) DEFAULT 'normal' CHECK (prioridad IN ('baja', 'normal', 'alta', 'urgente')),
    
    -- Estado de envío
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN (
        'pendiente', 'enviada', 'leida', 'expirada', 'fallida'
    )),
    
    -- Información de contexto (JSON)
    contexto JSONB,
    
    -- URL de acción (opcional)
    url_accion VARCHAR(255),
    
    -- Control de tiempo
    fecha_programada TIMESTAMP NOT NULL,
    fecha_envio TIMESTAMP,
    fecha_lectura TIMESTAMP,
    fecha_expiracion TIMESTAMP,
    
    -- Intentos de envío
    intentos_envio INTEGER DEFAULT 0,
    max_intentos INTEGER DEFAULT 3,
    ultimo_error TEXT,
    
    -- Auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Claves foráneas
    CONSTRAINT fk_notif_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id) ON DELETE CASCADE,
    CONSTRAINT fk_notif_centro FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE CASCADE
);

-- =============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =============================================

-- Índices para búsquedas frecuentes
CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario ON notificaciones_push(id_usuario);
CREATE INDEX IF NOT EXISTS idx_notificaciones_centro ON notificaciones_push(id_centro);
CREATE INDEX IF NOT EXISTS idx_notificaciones_estado ON notificaciones_push(estado);
CREATE INDEX IF NOT EXISTS idx_notificaciones_tipo ON notificaciones_push(tipo_notificacion);
CREATE INDEX IF NOT EXISTS idx_notificaciones_fecha_programada ON notificaciones_push(fecha_programada);

-- Índice compuesto para el job scheduler
CREATE INDEX IF NOT EXISTS idx_notificaciones_pendientes ON notificaciones_push(estado, fecha_programada) 
WHERE estado = 'pendiente';

-- Índice para notificaciones por usuario y estado
CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_estado ON notificaciones_push(id_usuario, estado, fecha_programada);

-- =============================================
-- TRIGGERS PARA AUDITORÍA
-- =============================================

-- Trigger para actualizar fecha_modificacion en configuracion_notificaciones_push
CREATE OR REPLACE FUNCTION trigger_notif_config_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_configuracion_notificaciones_push_fecha_modificacion
    BEFORE UPDATE ON configuracion_notificaciones_push
    FOR EACH ROW
    EXECUTE FUNCTION trigger_notif_config_fecha_modificacion();

-- Trigger para actualizar fecha_modificacion en notificaciones_push
CREATE OR REPLACE FUNCTION trigger_notif_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_modificacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_notificaciones_push_fecha_modificacion
    BEFORE UPDATE ON notificaciones_push
    FOR EACH ROW
    EXECUTE FUNCTION trigger_notif_fecha_modificacion();

-- =============================================
-- FUNCIONES AUXILIARES
-- =============================================

-- Función para verificar si está en horario de silencio
CREATE OR REPLACE FUNCTION esta_en_horario_silencio()
RETURNS BOOLEAN AS $$
DECLARE
    config RECORD;
    hora_actual TIME;
BEGIN
    SELECT horario_silencio_inicio, horario_silencio_fin 
    INTO config 
    FROM configuracion_notificaciones_push 
    WHERE id = 1;
    
    hora_actual := CURRENT_TIME;
    
    -- Si el horario de silencio cruza medianoche
    IF config.horario_silencio_inicio > config.horario_silencio_fin THEN
        RETURN hora_actual >= config.horario_silencio_inicio OR hora_actual <= config.horario_silencio_fin;
    ELSE
        RETURN hora_actual >= config.horario_silencio_inicio AND hora_actual <= config.horario_silencio_fin;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Función para limpiar notificaciones expiradas
CREATE OR REPLACE FUNCTION limpiar_notificaciones_expiradas()
RETURNS INTEGER AS $$
DECLARE
    notificaciones_eliminadas INTEGER;
BEGIN
    -- Marcar como expiradas las notificaciones pendientes que han superado su fecha de expiración
    UPDATE notificaciones_push 
    SET estado = 'expirada',
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE estado = 'pendiente' 
        AND fecha_expiracion IS NOT NULL 
        AND fecha_expiracion < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS notificaciones_eliminadas = ROW_COUNT;
    
    -- Eliminar físicamente notificaciones expiradas o leídas de más de 30 días
    DELETE FROM notificaciones_push 
    WHERE estado IN ('expirada', 'leida') 
        AND fecha_modificacion < CURRENT_TIMESTAMP - INTERVAL '30 days';
    
    RETURN notificaciones_eliminadas;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- COMENTARIOS PARA DOCUMENTACIÓN
-- =============================================

COMMENT ON TABLE configuracion_notificaciones_push IS 'Configuración global del sistema de notificaciones push';
COMMENT ON TABLE notificaciones_push IS 'Cola de notificaciones push para usuarios del sistema';

COMMENT ON COLUMN notificaciones_push.contexto IS 'Información adicional en formato JSON (IDs de sesiones, etc.)';
COMMENT ON COLUMN notificaciones_push.url_accion IS 'URL para redireccionar cuando el usuario hace clic en la notificación';
COMMENT ON COLUMN notificaciones_push.fecha_programada IS 'Momento en que debe enviarse la notificación';
COMMENT ON COLUMN notificaciones_push.fecha_expiracion IS 'Momento después del cual la notificación ya no es relevante';

-- =============================================
-- DATOS INICIALES DE CONFIGURACIÓN
-- =============================================

-- Verificar que la configuración por defecto existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM configuracion_notificaciones_push WHERE id = 1) THEN
        INSERT INTO configuracion_notificaciones_push (
            notificaciones_habilitadas,
            notificar_sesiones_terapia,
            minutos_previos_sesion_terapia,
            notificar_clases_pedagogicas,
            minutos_previos_clase_pedagogica,
            notificar_cancelaciones,
            notificar_reprogramaciones,
            notificar_mensajes_chat,
            notificar_solo_mensajes_urgentes,
            horario_silencio_inicio,
            horario_silencio_fin,
            intervalo_verificacion_minutos
        ) VALUES (
            TRUE,    -- notificaciones_habilitadas
            TRUE,    -- notificar_sesiones_terapia
            15,      -- minutos_previos_sesion_terapia
            TRUE,    -- notificar_clases_pedagogicas
            15,      -- minutos_previos_clase_pedagogica
            TRUE,    -- notificar_cancelaciones
            TRUE,    -- notificar_reprogramaciones
            TRUE,    -- notificar_mensajes_chat
            FALSE,   -- notificar_solo_mensajes_urgentes
            '22:00:00', -- horario_silencio_inicio
            '07:00:00', -- horario_silencio_fin
            1        -- intervalo_verificacion_minutos
        );
    END IF;
END $$;