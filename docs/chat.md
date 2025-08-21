# Módulo de Chat - Centro Tía Glenda

## Resumen
Sistema de mensajería interna que permite la comunicación en tiempo real entre los usuarios del centro médico. Facilita la coordinación del personal, consultas rápidas, notificaciones urgentes y seguimiento de casos, manteniendo toda la comunicación centralizada y segura dentro del mismo centro.

## Arquitectura del Módulo

### Componentes Principales
- **ChatService**: Lógica de negocio, validaciones y sanitización
- **ChatComponent**: Acceso a datos y operaciones de base de datos
- **Sistema de notificaciones**: Alertas de mensajes no leídos
- **Control de permisos**: Usuarios solo del mismo centro
- **Búsqueda avanzada**: Localización de mensajes por contenido
- **Sanitización de seguridad**: Protección contra XSS e inyecciones

## Estructura de Base de Datos

### Tabla Principal: `mensajes_chat`
```sql
CREATE TABLE IF NOT EXISTS mensajes_chat (
    id SERIAL PRIMARY KEY,
    id_remitente INTEGER NOT NULL,
    id_destinatario INTEGER NOT NULL,
    mensaje TEXT NOT NULL,
    
    -- Fechas
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
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
    
    -- Organización por centro
    id_centro INTEGER NOT NULL,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Foreign Keys
    FOREIGN KEY (id_remitente) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_destinatario) REFERENCES usuario(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT,
    
    -- Índices para optimización
    INDEX idx_mensajes_chat_remitente (id_remitente),
    INDEX idx_mensajes_chat_destinatario (id_destinatario),
    INDEX idx_mensajes_chat_centro (id_centro),
    INDEX idx_mensajes_chat_fecha (fecha_envio),
    INDEX idx_mensajes_chat_leido (leido),
    INDEX idx_mensajes_chat_busqueda (id_centro, mensaje)
);
```

### Tipos de Mensaje
- **texto**: Mensaje de texto simple (predeterminado)
- **archivo**: Mensaje con archivo adjunto
- **imagen**: Mensaje con imagen adjunta
- **urgente**: Mensaje urgente con alta prioridad

### Niveles de Prioridad
- **baja**: Mensaje informativo sin urgencia
- **normal**: Mensaje estándar (predeterminado)
- **alta**: Mensaje importante que requiere atención
- **urgente**: Mensaje crítico que requiere respuesta inmediata

### Relaciones con Otros Módulos
```sql
-- Usuarios participantes
mensajes_chat.id_remitente → usuario.id
mensajes_chat.id_destinatario → usuario.id

-- Control por centro
mensajes_chat.id_centro → centros.id

-- Datos personales de usuarios
usuario.persona_id → persona.id (para nombres)
usuario.rol_id → rol.id (para identificar rol)
```

## Endpoints del API

### 1. Obtener Conversaciones
```
GET /api/chat/conversaciones
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Conversaciones obtenidas correctamente",
    "data": {
        "conversaciones": [
            {
                "id_contacto": 2,
                "nombre_contacto": "Dr. Luis Martínez",
                "fecha_ultimo_mensaje": "2024-01-20T15:30:00",
                "mensajes_no_leidos": 3
            },
            {
                "id_contacto": 5,
                "nombre_contacto": "Lic. Ana García",
                "fecha_ultimo_mensaje": "2024-01-20T14:15:00",
                "mensajes_no_leidos": 0
            }
        ]
    }
}
```

### 2. Obtener Mensajes de Conversación
```
GET /api/chat/mensajes/{id_contacto}
```

**Query Parameters:**
- `limite` (opcional): Número máximo de mensajes (predeterminado: 50, máximo: 200)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Mensajes obtenidos correctamente",
    "data": {
        "mensajes": [
            {
                "id": 1,
                "id_remitente": 1,
                "id_destinatario": 2,
                "mensaje": "Buenos días Dr. Martínez, necesito consultar sobre el paciente María González",
                "fecha_envio": "2024-01-20T14:30:00",
                "leido": true,
                "fecha_lectura": "2024-01-20T14:32:00",
                "tipo_mensaje": "texto",
                "prioridad": "normal",
                "nombre_remitente": "Carmen",
                "apellido_remitente": "López",
                "nombre_destinatario": "Luis",
                "apellido_destinatario": "Martínez",
                "es_remitente": true
            },
            {
                "id": 2,
                "id_remitente": 2,
                "id_destinatario": 1,
                "mensaje": "Hola Carmen, ¿qué necesitas saber específicamente?",
                "fecha_envio": "2024-01-20T14:35:00",
                "leido": false,
                "fecha_lectura": null,
                "tipo_mensaje": "texto",
                "prioridad": "normal",
                "nombre_remitente": "Luis",
                "apellido_remitente": "Martínez",
                "nombre_destinatario": "Carmen",
                "apellido_destinatario": "López",
                "es_remitente": false
            }
        ]
    }
}
```

### 3. Enviar Mensaje
```
POST /api/chat/enviar
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "id_destinatario": 2,
    "mensaje": "¿Podrías revisar los resultados de la última sesión de María?",
    "tipo_mensaje": "texto",
    "prioridad": "normal"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Mensaje enviado exitosamente",
    "data": {
        "id_mensaje": 3,
        "fecha_envio": "2024-01-20T15:30:00"
    }
}
```

### 4. Marcar Mensaje como Leído
```
PUT /api/chat/marcar-leido/{id_mensaje}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Mensaje marcado como leído",
    "data": null
}
```

### 5. Usuarios Disponibles para Chat
```
GET /api/chat/usuarios-disponibles
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Usuarios disponibles obtenidos correctamente",
    "data": {
        "usuarios": [
            {
                "id": 2,
                "nombre": "Luis",
                "apellido": "Martínez",
                "rol": "Terapeuta",
                "estado": "activo"
            },
            {
                "id": 3,
                "nombre": "Ana",
                "apellido": "García",
                "rol": "Pedagógico",
                "estado": "activo"
            },
            {
                "id": 4,
                "nombre": "Carlos",
                "apellido": "Rodríguez",
                "rol": "Administrador",
                "estado": "activo"
            }
        ]
    }
}
```

### 6. Estadísticas de Mensajes
```
GET /api/chat/estadisticas
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Estadísticas obtenidas correctamente",
    "data": {
        "estadisticas": {
            "total_mensajes": 45,
            "mensajes_no_leidos": 3,
            "mensajes_enviados": 25,
            "mensajes_recibidos": 20,
            "conversaciones_activas": 6
        }
    }
}
```

### 7. Buscar Mensajes
```
GET /api/chat/buscar
```

**Query Parameters:**
- `texto`: Texto a buscar (mínimo 3 caracteres, máximo 100)
- `id_contacto` (opcional): ID del contacto para buscar solo en esa conversación

**Headers:**
```
Authorization: Bearer <token>
```

**Example Request:**
```
GET /api/chat/buscar?texto=paciente María&id_contacto=2
```

**Response:**
```json
{
    "success": true,
    "message": "Búsqueda completada",
    "data": {
        "mensajes": [
            {
                "id": 1,
                "id_remitente": 1,
                "id_destinatario": 2,
                "mensaje": "necesito consultar sobre el paciente María González",
                "fecha_envio": "2024-01-20T14:30:00",
                "tipo_mensaje": "texto",
                "nombre_remitente": "Carmen",
                "apellido_remitente": "López",
                "nombre_destinatario": "Luis",
                "apellido_destinatario": "Martínez",
                "es_remitente": true
            }
        ]
    }
}
```

## Implementación Técnica

### 1. Sistema de Validaciones

#### Validación de Mensajes
```python
def validar_mensaje(data, usuario_autenticado):
    """Validar datos completos del mensaje"""
    errors = []
    
    # Campos requeridos
    required_fields = ['id_destinatario', 'mensaje']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'Campo requerido: {field}')
    
    # Validar contenido del mensaje
    mensaje = data['mensaje'].strip()
    if len(mensaje) == 0:
        errors.append('El mensaje no puede estar vacío')
    
    if len(mensaje) > 1000:
        errors.append('El mensaje no puede exceder 1000 caracteres')
    
    # Validar destinatario
    id_destinatario = data['id_destinatario']
    if not isinstance(id_destinatario, int) or id_destinatario <= 0:
        errors.append('ID de destinatario inválido')
    
    # No permitir envío a sí mismo
    if id_destinatario == usuario_autenticado['id']:
        errors.append('No puedes enviarte mensajes a ti mismo')
    
    return {'valid': len(errors) == 0, 'message': '; '.join(errors)}
```

### 2. Sistema de Sanitización

#### Sanitización de Contenido
```python
def _sanitizar_mensaje(mensaje):
    """Sanitizar contenido del mensaje para seguridad"""
    # Remover caracteres de control peligrosos
    mensaje = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', mensaje)
    
    # Normalizar espacios en blanco
    mensaje = re.sub(r'\s+', ' ', mensaje)
    
    # Remover HTML tags básicos (por seguridad)
    mensaje = re.sub(r'<[^>]*>', '', mensaje)
    
    return mensaje.strip()

def _sanitizar_busqueda(texto):
    """Sanitizar texto de búsqueda"""
    # Remover caracteres especiales de SQL
    texto = re.sub(r'[\'\"\\;]', '', texto)
    
    # Normalizar espacios
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto.strip()
```

### 3. Control de Permisos por Centro

#### Validación de Destinatario
```python
def validar_destinatario(id_destinatario, usuario_autenticado):
    """Verificar que el destinatario pertenece al mismo centro"""
    resultado_destinatarios = ChatComponent.obtener_usuarios_disponibles(
        usuario_autenticado['id'], 
        usuario_autenticado['id_centro']
    )
    
    if not resultado_destinatarios['success']:
        return {'valid': False, 'message': 'Error al validar destinatario'}
    
    destinatarios_validos = [u['id'] for u in resultado_destinatarios['usuarios']]
    if id_destinatario not in destinatarios_validos:
        return {'valid': False, 'message': 'Destinatario no válido o no pertenece al mismo centro'}
    
    return {'valid': True}
```

### 4. Consultas SQL Principales

#### Obtener Conversaciones del Usuario
```sql
SELECT DISTINCT
    CASE 
        WHEN mc.id_remitente = %s THEN mc.id_destinatario
        ELSE mc.id_remitente
    END as id_contacto,
    CASE 
        WHEN mc.id_remitente = %s THEN 
            CONCAT(p_dest.nombre, ' ', p_dest.apellido)
        ELSE 
            CONCAT(p_rem.nombre, ' ', p_rem.apellido)
    END as nombre_contacto,
    MAX(mc.fecha_envio) as fecha_ultimo_mensaje,
    COUNT(CASE WHEN mc.id_destinatario = %s AND mc.leido = false THEN 1 END) as mensajes_no_leidos
FROM mensajes_chat mc
LEFT JOIN usuario u_rem ON mc.id_remitente = u_rem.id
LEFT JOIN persona p_rem ON u_rem.persona_id = p_rem.id
LEFT JOIN usuario u_dest ON mc.id_destinatario = u_dest.id
LEFT JOIN persona p_dest ON u_dest.persona_id = p_dest.id
WHERE (mc.id_remitente = %s OR mc.id_destinatario = %s)
  AND mc.id_centro = %s
GROUP BY id_contacto, nombre_contacto
ORDER BY fecha_ultimo_mensaje DESC;
```

#### Mensajes de Conversación Específica
```sql
SELECT 
    mc.id,
    mc.id_remitente,
    mc.id_destinatario,
    mc.mensaje,
    mc.fecha_envio,
    mc.leido,
    mc.fecha_lectura,
    mc.tipo_mensaje,
    mc.prioridad,
    pr.nombre as nombre_remitente,
    pr.apellido as apellido_remitente,
    pd.nombre as nombre_destinatario,
    pd.apellido as apellido_destinatario,
    mc.id_remitente = %s as es_remitente
FROM mensajes_chat mc
JOIN usuario ur ON mc.id_remitente = ur.id
JOIN persona pr ON ur.persona_id = pr.id
JOIN usuario ud ON mc.id_destinatario = ud.id
JOIN persona pd ON ud.persona_id = pd.id
WHERE ((mc.id_remitente = %s AND mc.id_destinatario = %s)
    OR (mc.id_remitente = %s AND mc.id_destinatario = %s))
AND mc.id_centro = %s
ORDER BY mc.fecha_envio DESC
LIMIT %s;
```

#### Búsqueda de Mensajes
```sql
SELECT 
    mc.id,
    mc.id_remitente,
    mc.id_destinatario,
    mc.mensaje,
    mc.fecha_envio,
    mc.tipo_mensaje,
    pr.nombre as nombre_remitente,
    pr.apellido as apellido_remitente,
    pd.nombre as nombre_destinatario,
    pd.apellido as apellido_destinatario,
    mc.id_remitente = %s as es_remitente
FROM mensajes_chat mc
JOIN usuario ur ON mc.id_remitente = ur.id
JOIN persona pr ON ur.persona_id = pr.id
JOIN usuario ud ON mc.id_destinatario = ud.id
JOIN persona pd ON ud.persona_id = pd.id
WHERE (mc.id_remitente = %s OR mc.id_destinatario = %s)
AND mc.id_centro = %s
AND mc.mensaje ILIKE %s
ORDER BY mc.fecha_envio DESC
LIMIT 100;
```

## Casos de Uso y Flujos

### 1. Envío de Mensaje Urgente
```
1. Terapeuta necesita comunicación urgente con administrador
2. Selecciona contacto → GET /api/chat/usuarios-disponibles
3. Redacta mensaje con prioridad "urgente" → POST /api/chat/enviar
4. Sistema valida mismo centro y envía mensaje
5. Administrador ve notificación de mensaje no leído
6. Lee mensaje y responde → Auto-marcado como leído
```

### 2. Consulta sobre Paciente
```
1. Personal busca información sobre paciente específico
2. Inicia conversación con terapeuta responsable
3. Envía mensaje con detalles del paciente
4. Terapeuta recibe notificación y responde
5. Ambos pueden buscar mensajes anteriores sobre el paciente
6. Conversación queda registrada para referencia futura
```

### 3. Coordinación de Horarios
```
1. Administrador necesita coordinar cambio de horarios
2. Envía mensaje a múltiples terapeutas (una conversación por vez)
3. Cada terapeuta responde con disponibilidad
4. Administrador consulta estadísticas para ver respuestas pendientes
5. Confirma nuevo horario a través del chat
```

### 4. Búsqueda de Información Histórica
```
1. Usuario necesita recordar conversación anterior
2. Usa función de búsqueda → GET /api/chat/buscar
3. Ingresa palabras clave específicas
4. Sistema devuelve mensajes coincidentes ordenados por fecha
5. Usuario accede directamente a la conversación relevante
```

## Características de Seguridad

### Control de Acceso
- **Por centro**: Usuarios solo pueden chatear con colegas del mismo centro
- **Autenticación**: Todos los endpoints requieren token JWT válido
- **Validación de destinatario**: Verificación de permisos antes de envío

### Sanitización de Datos
- **Anti-XSS**: Remoción de tags HTML en mensajes
- **Anti-inyección**: Sanitización de búsquedas y contenido
- **Caracteres de control**: Filtrado de caracteres peligrosos

### Auditoría Completa
- **Registro de envíos**: Log de todos los mensajes enviados
- **Timestamps precisos**: Fecha/hora de envío y lectura
- **Usuario responsable**: Registro del emisor en cada mensaje

## Integración con Otros Módulos

### Con Usuarios y Roles
- **Identificación**: Nombres y roles visibles en conversaciones
- **Filtrado**: Solo usuarios activos del mismo centro
- **Contexto**: Rol del usuario visible para mejor comunicación

### Con Centros
- **Aislamiento**: Comunicación limitada por centro
- **Filtrado automático**: Sistema aplica filtro de centro transparentemente
- **Escalabilidad**: Soporte para múltiples centros independientes

### Con Sistema de Notificaciones
- **Contadores**: Mensajes no leídos por conversación
- **Estados**: Tracking de lectura de mensajes
- **Prioridades**: Diferenciación visual según urgencia

## Limitaciones Actuales

### Archivos Adjuntos
- **Solo estructura**: Tabla preparada pero funcionalidad no implementada
- **Sin validación**: No hay upload ni validación de archivos
- **Sin preview**: No visualización de imágenes en chat

### Notificaciones Push
- **Sin tiempo real**: No WebSockets o Server-Sent Events
- **Sin alertas**: No notificaciones fuera del sistema
- **Polling manual**: Usuario debe refrescar para ver nuevos mensajes

### Funcionalidades Avanzadas
- **Sin grupos**: Solo conversaciones uno-a-uno
- **Sin hilos**: No threading de conversaciones
- **Sin reacciones**: No emojis ni reacciones a mensajes

## Recomendaciones de Mejora

### Futuras Implementaciones
1. **WebSockets**: Comunicación en tiempo real
2. **Archivos adjuntos**: Upload y preview de documentos/imágenes
3. **Grupos de chat**: Conversaciones con múltiples participantes
4. **Notificaciones push**: Alertas fuera del navegador
5. **Mensajes programados**: Envío diferido de mensajes
6. **Hilos de conversación**: Threading para organizar discusiones
7. **Reacciones**: Emojis y reacciones rápidas
8. **Encriptación**: Cifrado end-to-end para mayor seguridad
9. **Backup de conversaciones**: Exportación de historial
10. **Integración con calendario**: Coordinación de citas via chat
11. **Plantillas**: Mensajes predefinidos para situaciones comunes
12. **Estados de usuario**: Online/offline/ausente

## Casos de Uso Específicos del Centro Médico

### Emergencias Médicas
```
1. Personal detecta emergencia con paciente
2. Envía mensaje urgente al administrador
3. Prioridad "urgente" resalta el mensaje
4. Coordinación rápida de respuesta
5. Seguimiento de acciones tomadas
```

### Consultas Terapéuticas
```
1. Terapeuta necesita segunda opinión
2. Contacta colega especialista via chat
3. Comparte detalles del caso (sin datos sensibles)
4. Recibe retroalimentación especializada
5. Aplicación de sugerencias en tratamiento
```

### Coordinación Interdisciplinaria
```
1. Paciente requiere atención múltiple
2. Terapeuta coordina con pedagogo
3. Establecen plan de trabajo conjunto
4. Seguimiento continuo via chat
5. Evaluación conjunta de progreso
```

### Comunicación Administrativa
```
1. Cambios en políticas o procedimientos
2. Administrador comunica a personal relevante
3. Confirmación de recepción via mensajes
4. Aclaración de dudas en tiempo real
5. Registro de comunicación oficial
```