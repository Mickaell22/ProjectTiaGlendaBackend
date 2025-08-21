# Módulo de Personal - Centro Tía Glenda

## Resumen
Módulo que gestiona el personal/empleados del centro médico, incluyendo sus especialidades múltiples, documentos, centros de trabajo y relaciones laborales. Extiende el módulo de Personas para añadir información específica de empleados.

## Arquitectura del Módulo

### Componentes Principales
- **PersonalService**: Lógica de negocio y validaciones
- **PersonalComponent**: Acceso a datos y operaciones CRUD
- **DocumentoPersonalService**: Gestión de documentos del personal
- **Validators**: Validación de datos específicos del personal
- **Middleware**: Protección con admin_required para gestión

## Estructura de Base de Datos

### Tabla Principal: `personal`
```sql
CREATE TABLE IF NOT EXISTS personal (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL,
    id_especialidad INTEGER NOT NULL, -- Especialidad principal
    numero_registro VARCHAR(50) UNIQUE,
    fecha_ingreso DATE NOT NULL,
    fecha_salida DATE,
    cargo VARCHAR(100),
    tipo_contrato VARCHAR(20) CHECK (tipo_contrato IN ('indefinido', 'temporal', 'honorarios', 'practicante')),
    salario DECIMAL(10,2),
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'vacaciones', 'licencia')),
    observaciones TEXT,
    id_centro INTEGER NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);
```

### Tabla de Especialidades Múltiples: `personal_especialidades`
```sql
CREATE TABLE IF NOT EXISTS personal_especialidades (
    id SERIAL PRIMARY KEY,
    id_personal INTEGER NOT NULL,
    id_especialidad INTEGER NOT NULL,
    es_principal BOOLEAN DEFAULT FALSE,
    nivel_competencia VARCHAR(20) DEFAULT 'basico' CHECK (nivel_competencia IN ('basico', 'intermedio', 'avanzado', 'experto')),
    certificacion VARCHAR(255),
    fecha_asignacion DATE DEFAULT CURRENT_DATE,
    fecha_vencimiento_certificacion DATE,
    observaciones TEXT,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'suspendido')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_personal) REFERENCES personal(id) ON DELETE CASCADE,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE RESTRICT,
    
    -- Constraint para evitar duplicados
    UNIQUE (id_personal, id_especialidad)
);
```

### Tabla de Documentos: `documentos_personal`
```sql
CREATE TABLE IF NOT EXISTS documentos_personal (
    id SERIAL PRIMARY KEY,
    id_personal INTEGER NOT NULL,
    tipo_documento VARCHAR(50) NOT NULL CHECK (tipo_documento IN 
        ('cedula', 'curriculum', 'titulo_profesional', 'certificacion', 'contrato', 
         'acuerdo_confidencialidad', 'referencias', 'antecedentes_penales', 'record_policial', 'otros')),
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    tamaño_archivo INTEGER,
    tipo_mime VARCHAR(100),
    descripcion TEXT,
    es_obligatorio BOOLEAN DEFAULT FALSE,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATE,
    
    -- Control de validación (solo admin puede validar)
    estado_validacion VARCHAR(20) DEFAULT 'pendiente' CHECK (estado_validacion IN 
        ('pendiente', 'en_revision', 'aprobado', 'rechazado', 'vencido')),
    validado_por INTEGER, -- ID del usuario que validó
    fecha_validacion TIMESTAMP,
    observaciones_validacion TEXT,
    
    FOREIGN KEY (id_personal) REFERENCES personal(id) ON DELETE CASCADE,
    FOREIGN KEY (validado_por) REFERENCES usuario(id)
);
```

### Relaciones con Otros Módulos
```sql
-- Datos personales base
personal.persona_id → persona.id

-- Especialidad principal
personal.id_especialidad → especialidad.id

-- Centro de trabajo
personal.id_centro → centros.id

-- Especialidades múltiples
personal_especialidades.id_personal → personal.id
personal_especialidades.id_especialidad → especialidad.id

-- Usuario del sistema (opcional)
usuario.persona_id → persona.id (misma persona)
```

## Endpoints del API

### 1. Listar Personal
```
GET /api/personal
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Lista del personal obtenida correctamente",
    "data": [
        {
            "id": 1,
            "titulo_profesional": "Terapeuta del Lenguaje",
            "id_centro": 13,
            "estado": "activo",
            "fecha_creacion": "2024-01-15T10:30:00",
            "fecha_modificacion": null,
            "persona_id": 2,
            "nombre_completo": "Ana Martínez",
            "nombre": "Ana",
            "apellido": "Martínez",
            "cedula": "1234567892",
            "telefono": "0987654323",
            "correo": "ana.martinez@centrotiaglenda.com",
            "direccion": "Av. Norte #789",
            "usuario_id": 2,
            "nombre_usuario": "ana.martinez",
            "rol_usuario": "Terapeuta",
            "centro_nombre": "Centro Norte",
            "centro_codigo": "NORTE",
            "centro_turno": "matutino",
            "especialidades": [
                {
                    "id": 1,
                    "nombre": "Terapia del Lenguaje",
                    "area": "Especialidad terapéutica",
                    "fecha_asignacion": "2024-01-15T10:30:00"
                },
                {
                    "id": 4,
                    "nombre": "Terapia Psicológica", 
                    "area": "Especialidad terapéutica",
                    "fecha_asignacion": "2024-01-20T14:15:00"
                }
            ]
        }
    ]
}
```

### 2. Obtener Personal por ID
```
GET /api/personal/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Personal encontrado",
    "data": {
        "id": 1,
        "titulo_profesional": "Terapeuta del Lenguaje",
        "estado": "activo",
        "fecha_creacion": "2024-01-15T10:30:00",
        "persona_id": 2,
        "nombre_completo": "Ana Martínez",
        "nombre": "Ana",
        "apellido": "Martínez",
        "cedula": "1234567892",
        "telefono": "0987654323",
        "correo": "ana.martinez@centrotiaglenda.com",
        "fecha_nacimiento": "1990-03-10",
        "usuario_id": 2,
        "nombre_usuario": "ana.martinez",
        "rol_usuario": "Terapeuta",
        "especialidades": [
            {
                "id": 1,
                "nombre": "Terapia del Lenguaje",
                "area": "Especialidad terapéutica",
                "fecha_asignacion": "2024-01-15T10:30:00"
            }
        ]
    }
}
```

### 3. Crear Personal
```
POST /api/personal
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Permisos:** Solo administradores

**Request Body:**
```json
{
    "persona_id": 3,
    "titulo_profesional": "Fisioterapeuta",
    "estado": "activo",
    "especialidades": [
        {"id": 3},
        {"id": 1}
    ]
}
```

**Response:**
```json
{
    "success": true,
    "message": "Personal creado exitosamente",
    "data": {
        "id": 2,
        "persona_id": 3,
        "titulo_profesional": "Fisioterapeuta",
        "nombre_completo": "Carlos Rodríguez",
        "estado": "activo",
        "fecha_creacion": "2024-01-15T11:45:00",
        "especialidades": [
            {
                "id": 3,
                "nombre": "Fisioterapia",
                "area": "Especialidad terapéutica"
            },
            {
                "id": 1,
                "nombre": "Terapia del Lenguaje",
                "area": "Especialidad terapéutica"
            }
        ]
    }
}
```

### 4. Actualizar Personal
```
PUT /api/personal/{id}
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Permisos:** Solo administradores

**Request Body:**
```json
{
    "titulo_profesional": "Fisioterapeuta Senior",
    "estado": "activo",
    "especialidades": [
        {"id": 3},
        {"id": 2}
    ]
}
```

**Response:**
```json
{
    "success": true,
    "message": "Personal actualizado exitosamente",
    "data": {
        "id": 2,
        "titulo_profesional": "Fisioterapeuta Senior",
        "fecha_modificacion": "2024-01-15T14:20:00",
        "especialidades": [
            {
                "id": 3,
                "nombre": "Fisioterapia",
                "area": "Especialidad terapéutica"
            },
            {
                "id": 2,
                "nombre": "Terapia Ocupacional",
                "area": "Especialidad terapéutica"
            }
        ]
    }
}
```

### 5. Desactivar Personal
```
DELETE /api/personal/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Permisos:** Solo administradores

**Response:**
```json
{
    "success": true,
    "message": "Personal desactivado exitosamente",
    "data": null
}
```

### 6. Obtener Personal por Área
```
GET /api/personal/area/{area}
```

**Parámetros de área:**
- `terapeutico`: Personal con especialidades terapéuticas
- `pedagogico`: Personal con especialidades pedagógicas

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Personal de terapeutico obtenido correctamente",
    "data": [
        {
            "id": 1,
            "titulo_profesional": "Terapeuta del Lenguaje",
            "estado": "activo",
            "persona_id": 2,
            "nombre_completo": "Ana Martínez",
            "nombre": "Ana",
            "apellido": "Martínez",
            "correo": "ana.martinez@centrotiaglenda.com",
            "especialidades_en_area": 2
        }
    ]
}
```

### 7. Estadísticas del Personal
```
GET /api/personal/estadisticas
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Estadísticas del personal obtenidas",
    "data": {
        "general": {
            "total_personal": 15,
            "personal_activo": 12,
            "personal_inactivo": 3,
            "con_usuario": 10,
            "sin_usuario": 5
        },
        "por_area": [
            {
                "area": "Especialidad terapéutica",
                "personal_por_area": 8
            },
            {
                "area": "Especialidad pedagógica",
                "personal_por_area": 4
            }
        ]
    }
}
```

## Gestión de Especialidades

### 8. Obtener Especialidades del Personal
```
GET /api/personal/{id}/especialidades
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidades del personal obtenidas",
    "data": [
        {
            "id": 1,
            "nombre": "Terapia del Lenguaje",
            "area": "Especialidad terapéutica",
            "fecha_asignacion": "2024-01-15T10:30:00"
        },
        {
            "id": 4,
            "nombre": "Terapia Psicológica",
            "area": "Especialidad terapéutica", 
            "fecha_asignacion": "2024-01-20T14:15:00"
        }
    ]
}
```

### 9. Asignar Especialidad al Personal
```
POST /api/personal/{id}/especialidades
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Permisos:** Solo administradores

**Request Body:**
```json
{
    "especialidad_id": 2
}
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidad asignada exitosamente",
    "data": {
        "assignment_id": 15
    }
}
```

### 10. Actualizar Especialidad del Personal
```
PUT /api/personal/{id}/especialidades/{especialidad_id}
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "nivel_competencia": "avanzado",
    "es_principal": true,
    "certificacion": "Certificación Avanzada en Terapia del Lenguaje",
    "observaciones": "Especialidad principal con certificación internacional"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidad actualizada exitosamente",
    "data": {
        "personal_id": 1,
        "especialidad_id": 1
    }
}
```

### 11. Remover Especialidad del Personal
```
DELETE /api/personal/{id}/especialidades/{especialidad_id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Permisos:** Solo administradores

**Response:**
```json
{
    "success": true,
    "message": "Especialidad removida exitosamente",
    "data": null
}
```

### 12. Personal por Especialidad
```
GET /api/personal/por-especialidad/{especialidad_id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Personal por especialidad obtenido correctamente",
    "data": [
        {
            "id": 1,
            "titulo_profesional": "Terapeuta del Lenguaje",
            "id_centro": 13,
            "persona_id": 2,
            "nombre_completo": "Ana Martínez",
            "nombre": "Ana",
            "apellido": "Martínez",
            "centro_nombre": "Centro Norte",
            "centro_codigo": "NORTE",
            "especialidad_nombre": "Terapia del Lenguaje",
            "especialidad_area": "Especialidad terapéutica"
        }
    ]
}
```

### 13. Especialidades Disponibles para Asignar
```
GET /api/personal/especialidades-disponibles
```

**Query Parameters:**
- `personal_id` (opcional): ID del personal para filtrar especialidades no asignadas

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidades disponibles obtenidas correctamente",
    "data": [
        {
            "id": 5,
            "nombre": "Educación Especial",
            "area": "Especialidad pedagógica",
            "descripcion": "Especialidad pedagógica para la educación especializada"
        },
        {
            "id": 6,
            "nombre": "Apoyo Académico",
            "area": "Especialidad pedagógica",
            "descripcion": "Especialidad pedagógica para refuerzo académico"
        }
    ]
}
```

## Implementación Técnica

### 1. Validaciones de Datos

#### Validación de Personal
```python
def validate_personal_data(data, is_update=False):
    """Validar datos completos del personal"""
    errors = []
    
    # Campos requeridos para crear personal
    if not is_update:
        required_fields = ['persona_id']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field} es requerido")
    
    # Validar persona_id
    if 'persona_id' in data:
        try:
            persona_id = int(data['persona_id'])
            if persona_id <= 0:
                errors.append("ID de persona debe ser mayor a 0")
        except (ValueError, TypeError):
            errors.append("ID de persona debe ser un número entero")
    
    # Validar titulo_profesional
    if 'titulo_profesional' in data and data['titulo_profesional']:
        if len(data['titulo_profesional'].strip()) > 100:
            errors.append("Título profesional no puede exceder 100 caracteres")
    
    return {'valid': len(errors) == 0, 'message': '; '.join(errors)}
```

### 2. Reglas de Negocio

#### Unicidad de Persona como Personal
```python
def check_persona_is_personal(persona_id, exclude_id=None):
    """Una persona solo puede ser registrada una vez como personal"""
    if exclude_id:
        query = "SELECT id FROM personal WHERE persona_id = %s AND id != %s"
        params = (persona_id, exclude_id)
    else:
        query = "SELECT id FROM personal WHERE persona_id = %s"
        params = (persona_id,)
    
    existing = DataBaseHandle.getRecords(query, params, size=1)
    return existing is not None
```

#### Gestión de Especialidades Múltiples
```python
def assign_especialidad(personal_id, especialidad_id, usuario_creacion=1):
    """Asignar especialidad con validaciones completas"""
    # Verificar personal existe y está activo
    personal = DataBaseHandle.getRecords(
        "SELECT estado FROM personal WHERE id = %s", 
        (personal_id,), size=1
    )
    
    if not personal or personal['estado'] != 'activo':
        return internal_response(False, None, "Personal no encontrado o inactivo")
    
    # Verificar especialidad existe y está activa
    especialidad = DataBaseHandle.getRecords(
        "SELECT estado FROM especialidad WHERE id = %s", 
        (especialidad_id,), size=1
    )
    
    if not especialidad or especialidad['estado'] != 'activo':
        return internal_response(False, None, "Especialidad no encontrada o inactiva")
    
    # Verificar no esté ya asignada
    existing = DataBaseHandle.getRecords(
        "SELECT id FROM personal_especialidades WHERE id_personal = %s AND id_especialidad = %s",
        (personal_id, especialidad_id), size=1
    )
    
    if existing:
        return internal_response(False, None, "Especialidad ya asignada")
    
    # Asignar especialidad
    success = DataBaseHandle.ExecuteNonQuery(
        "INSERT INTO personal_especialidades (id_personal, id_especialidad, usuario_creacion) VALUES (%s, %s, %s)",
        (personal_id, especialidad_id, usuario_creacion)
    )
    
    return internal_response(success, None, "Especialidad asignada" if success else "Error")
```

### 3. Consultas SQL Principales

#### Personal con Información Completa
```sql
SELECT 
    p.id,
    p.cargo as titulo_profesional,
    p.id_centro,
    p.estado,
    p.fecha_creacion,
    p.fecha_modificacion,
    pe.id as persona_id,
    CONCAT(pe.nombre, ' ', pe.apellido) as nombre_completo,
    pe.nombre,
    pe.apellido,
    pe.cedula,
    pe.telefono,
    pe.correo,
    pe.direccion,
    u.id as usuario_id,
    u.usuario as nombre_usuario,
    r.nombre as rol_usuario,
    c.nombre as centro_nombre,
    c.codigo as centro_codigo,
    c.turno_principal as centro_turno
FROM personal p
INNER JOIN persona pe ON p.persona_id = pe.id
LEFT JOIN usuario u ON pe.id = u.persona_id
LEFT JOIN rol r ON u.rol_id = r.id
LEFT JOIN centros c ON p.id_centro = c.id
WHERE p.estado != 'eliminado'
ORDER BY c.nombre, pe.nombre, pe.apellido;
```

#### Especialidades del Personal
```sql
SELECT 
    e.id,
    e.nombre,
    e.descripcion as area,
    ps.fecha_creacion as fecha_asignacion,
    ps.nivel_competencia,
    ps.es_principal,
    ps.certificacion
FROM personal_especialidades ps
INNER JOIN especialidad e ON ps.id_especialidad = e.id
WHERE ps.id_personal = %s AND e.estado = 'activo'
ORDER BY ps.es_principal DESC, e.descripcion, e.nombre;
```

#### Personal por Área de Especialidad
```sql
SELECT DISTINCT
    p.id,
    p.cargo as titulo_profesional,
    pe.id as persona_id,
    CONCAT(pe.nombre, ' ', pe.apellido) as nombre_completo,
    COUNT(ps.id_especialidad) as especialidades_en_area
FROM personal p
INNER JOIN persona pe ON p.persona_id = pe.id
INNER JOIN personal_especialidades ps ON p.id = ps.id_personal
INNER JOIN especialidad e ON ps.id_especialidad = e.id
WHERE e.descripcion LIKE %s AND p.estado = 'activo' AND e.estado = 'activo'
GROUP BY p.id, p.cargo, pe.id, pe.nombre, pe.apellido
ORDER BY pe.nombre, pe.apellido;
```

## Casos de Uso y Flujos

### 1. Registro de Nuevo Personal
```
1. Administrador crea persona → POST /api/personas
2. Administrador registra como personal → POST /api/personal
3. Sistema valida persona no esté ya registrada como personal
4. Asigna centro por defecto y especialidad principal
5. Opcionalmente asigna especialidades adicionales
6. Genera usuario del sistema → POST /api/usuarios
7. Personal puede acceder al sistema con rol asignado
```

### 2. Gestión de Especialidades Múltiples
```
1. Personal creado con especialidad principal
2. Administrador asigna especialidades adicionales → POST /api/personal/{id}/especialidades
3. Sistema valida especialidades no duplicadas
4. Actualiza competencias y certificaciones → PUT /api/personal/{id}/especialidades/{esp_id}
5. Personal puede atender pacientes de todas sus especialidades
6. Remueve especialidades si es necesario → DELETE /api/personal/{id}/especialidades/{esp_id}
```

### 3. Filtrado y Búsqueda de Personal
```
1. Buscar por área → GET /api/personal/area/terapeutico
2. Buscar por especialidad → GET /api/personal/por-especialidad/{id}
3. Personal disponible para nuevas especialidades → GET /api/personal/especialidades-disponibles
4. Estadísticas generales → GET /api/personal/estadisticas
```

## Integración con Otros Módulos

### Con Personas
- **Extensión**: Personal extiende persona con información laboral
- **Validación**: Una persona solo puede ser personal una vez
- **Datos compartidos**: Información personal, contacto, identificación

### Con Especialidades
- **Especialidades múltiples**: Un personal puede tener varias especialidades
- **Competencias**: Nivel de competencia por especialidad
- **Filtrado**: Búsqueda de personal por especialidad específica

### Con Usuarios
- **Integración**: Mismo persona_id para personal y usuario
- **Roles**: Personal típicamente tiene rol "Terapeuta" o "Pedagógico"
- **Acceso**: Personal con usuario puede acceder al sistema

### Con Sesiones Terapéuticas/Pedagógicas
- **Asignación**: Personal asignado a sesiones según especialidades
- **Filtrado**: Solo personal con especialidades compatibles
- **Cronogramas**: Personal disponible para programar sesiones

### Con Centros
- **Asignación**: Personal pertenece a un centro específico
- **Filtrado**: Consultas por centro de trabajo
- **Horarios**: Respeta horarios del centro asignado

## Documentos del Personal

El módulo incluye gestión completa de documentos:

### Tipos de Documentos Soportados
- **cedula**: Cédula de identidad
- **curriculum**: Hoja de vida
- **titulo_profesional**: Título universitario
- **certificacion**: Certificaciones profesionales
- **contrato**: Contrato laboral
- **acuerdo_confidencialidad**: Acuerdos de confidencialidad
- **referencias**: Referencias laborales
- **antecedentes_penales**: Antecedentes penales
- **record_policial**: Récord policial
- **otros**: Otros documentos

### Estados de Validación
- **pendiente**: Documento subido, pendiente de revisión
- **en_revision**: En proceso de validación
- **aprobado**: Documento validado y aprobado
- **rechazado**: Documento rechazado
- **vencido**: Documento con fecha de vencimiento pasada

### Endpoints de Documentos
```
GET /api/personal/{id}/documentos - Listar documentos del personal
POST /api/personal/{id}/documentos - Subir documento
GET /api/documentos-personal/{id} - Obtener documento específico
PUT /api/documentos-personal/{id} - Actualizar documento
DELETE /api/documentos-personal/{id} - Eliminar documento
GET /api/documentos-personal/{id}/descargar - Descargar archivo
PUT /api/documentos-personal/{id}/validar - Validar documento (admin)
GET /api/documentos-personal/vencimientos - Documentos por vencer
GET /api/documentos-personal/estadisticas - Estadísticas de documentos
```

## Validaciones y Restricciones

### Campos Obligatorios
- **persona_id**: Debe existir en tabla persona y no estar duplicado
- **estado**: Valores válidos (activo, inactivo, vacaciones, licencia)

### Campos Opcionales
- **titulo_profesional**: Hasta 100 caracteres
- **especialidades**: Array de IDs de especialidades válidas

### Reglas de Negocio
- **Unicidad de persona**: Una persona solo puede ser personal una vez
- **Especialidades activas**: Solo se pueden asignar especialidades activas
- **No duplicación**: Una especialidad no puede asignarse dos veces al mismo personal
- **Estado activo**: Solo personal activo puede tener especialidades asignadas

### Códigos de Error
- **400**: Datos inválidos, persona ya es personal, especialidad duplicada
- **401**: Token requerido o inválido
- **403**: Sin permisos de administrador
- **404**: Personal o especialidad no encontrada
- **500**: Error interno del servidor

## Configuración y Dependencias

### Variables de Entorno
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=centro_tia_glenda
CENTRO_PREDETERMINADO=13  # Centro Norte por defecto
```

### Archivos de Documentos
```bash
RUTA_DOCUMENTOS_PERSONAL=/documentos_personal/
TAMAÑO_MAXIMO_ARCHIVO=10MB
TIPOS_ARCHIVO_PERMITIDOS=pdf,doc,docx,jpg,jpeg,png
```

## Logging y Auditoría

El sistema registra:
- Creación de personal nuevo
- Asignación/remoción de especialidades
- Modificaciones de datos laborales
- Subida y validación de documentos
- Consultas de personal por área/especialidad
- Cambios de estado del personal

Ubicación: `src/utils/general/LOGS/`

## Testing

Pruebas incluidas para:
- CRUD completo de personal
- Gestión de especialidades múltiples
- Validación de unicidad de persona
- Filtrado por áreas y especialidades
- Subida y gestión de documentos
- Integración con usuarios y sesiones

Ejecutar: `python tests/test_personal_api.py`

## Consideraciones de Seguridad

### Control de Acceso
- **Gestión**: Solo administradores pueden crear/modificar personal
- **Consulta**: Personal puede ver información básica
- **Documentos**: Acceso restringido según rol y pertenencia

### Validación de Datos
- **Integridad referencial**: Verificación de personas y especialidades existentes
- **Unicidad**: Prevención de duplicación de personal
- **Estados válidos**: Validación de estados y transiciones permitidas

### Auditoría Completa
- **Trazabilidad**: Usuario responsable de cada cambio
- **Timestamps**: Registro de fechas de creación/modificación
- **Logs detallados**: Registro de todas las operaciones importantes

## Limitaciones Actuales

### Especialidades
- **Limitación de competencias**: Solo 4 niveles básicos
- **Sin jerarquía**: No hay especialidades padre-hijo
- **Certificaciones simples**: Solo texto libre para certificaciones

### Centros de Trabajo
- **Centro único**: Personal asignado a un solo centro
- **Sin rotaciones**: No maneja rotaciones entre centros
- **Horarios fijos**: No personalización de horarios por personal

## Recomendaciones de Mejora

### Futuras Implementaciones
1. **Horarios personalizados**: Horarios específicos por personal
2. **Rotaciones de centro**: Sistema de asignaciones temporales
3. **Evaluaciones de desempeño**: Módulo de evaluación periódica
4. **Certificaciones digitales**: Integración con sistemas de certificación
5. **Gestión de vacaciones**: Calendario de ausencias y licencias
6. **Reportes avanzados**: Dashboards de productividad y estadísticas