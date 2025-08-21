# Módulo de Especialidades - Centro Tía Glenda

## Resumen
Módulo central que gestiona el catálogo de especialidades médicas, terapéuticas y pedagógicas del centro. Define las áreas de atención disponibles y sirve como base para asignaciones de personal y pacientes, así como para la verificación de compatibilidades entre profesionales y beneficiarios.

## Arquitectura del Módulo

### Componentes Principales
- **EspecialidadService**: Lógica de negocio y validaciones
- **EspecialidadComponent**: Acceso a datos y operaciones CRUD
- **Sistema de compatibilidad**: Verificación entre personal y pacientes
- **Estadísticas avanzadas**: Métricas de uso y distribución
- **Middleware**: Protección con admin_required para gestión

## Estructura de Base de Datos

### Tabla Principal: `especialidad`
```sql
CREATE TABLE IF NOT EXISTS especialidad (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT, -- Área: terapéutica/pedagógica
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);

CREATE INDEX IF NOT EXISTS idx_especialidad_nombre ON especialidad(nombre);
```

### Especialidades Predefinidas del Sistema
```sql
-- Especialidades Terapéuticas
INSERT INTO especialidad (nombre, descripcion, estado) VALUES
('Terapia del Lenguaje', 'Especialidad terapéutica para el desarrollo del lenguaje y comunicación', 'activo'),
('Terapia Ocupacional', 'Especialidad terapéutica para el desarrollo de habilidades ocupacionales', 'activo'),
('Fisioterapia', 'Especialidad terapéutica para el desarrollo y rehabilitación física', 'activo'),
('Terapia Psicológica', 'Especialidad terapéutica para el bienestar psicológico y emocional', 'activo'),

-- Especialidades Pedagógicas
('Educación Especial', 'Especialidad pedagógica para la educación especializada', 'activo'),
('Apoyo Académico', 'Especialidad pedagógica para refuerzo académico', 'activo'),
('Desarrollo Cognitivo', 'Especialidad pedagógica para el desarrollo cognitivo', 'activo');
```

### Relaciones con Otros Módulos
```sql
-- Personal con especialidades múltiples
personal.id_especialidad → especialidad.id (principal)
personal_especialidades.id_especialidad → especialidad.id (múltiples)

-- Pacientes con especialidades múltiples
paciente.id_especialidad → especialidad.id (principal)
paciente_especialidades.id_especialidad → especialidad.id (múltiples)

-- Sesiones según especialidad
sesion_terapia.id_especialidad → especialidad.id
sesion_pedagogica.id_especialidad → especialidad.id
```

## Áreas de Especialidad

### 1. Área Terapéutica
**Descripción:** Especialidades médicas y terapéuticas para rehabilitación y tratamiento

**Especialidades incluidas:**
- **Terapia del Lenguaje**: Desarrollo del habla, comunicación y deglución
- **Terapia Ocupacional**: Habilidades de la vida diaria y motricidad fina
- **Fisioterapia**: Rehabilitación física y motricidad gruesa
- **Terapia Psicológica**: Bienestar emocional y comportamental

**Personal asociado:** Terapeutas con formación médica especializada
**Sesiones:** Sesiones terapéuticas individualizadas o grupales

### 2. Área Pedagógica
**Descripción:** Especialidades educativas para desarrollo académico y cognitivo

**Especialidades incluidas:**
- **Educación Especial**: Metodologías educativas adaptadas
- **Apoyo Académico**: Refuerzo en materias específicas
- **Desarrollo Cognitivo**: Estimulación de procesos mentales

**Personal asociado:** Pedagogos y educadores especializados
**Sesiones:** Clases pedagógicas estructuradas con cronogramas académicos

## Endpoints del API

### 1. Listar Todas las Especialidades
```
GET /api/especialidades
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Lista de especialidades obtenida correctamente",
    "data": [
        {
            "id": 1,
            "nombre": "Terapia del Lenguaje",
            "area": "Especialidad terapéutica para el desarrollo del lenguaje y comunicación",
            "estado": "activo",
            "fecha_creacion": "2024-01-01T00:00:00",
            "fecha_modificacion": null,
            "personal_asignado": 3
        },
        {
            "id": 2,
            "nombre": "Terapia Ocupacional",
            "area": "Especialidad terapéutica para el desarrollo de habilidades ocupacionales",
            "estado": "activo",
            "fecha_creacion": "2024-01-01T00:00:00",
            "fecha_modificacion": null,
            "personal_asignado": 2
        },
        {
            "id": 5,
            "nombre": "Educación Especial",
            "area": "Especialidad pedagógica para la educación especializada",
            "estado": "activo",
            "fecha_creacion": "2024-01-01T00:00:00",
            "fecha_modificacion": null,
            "personal_asignado": 2
        }
    ]
}
```

### 2. Especialidades por Área
```
GET /api/especialidades/{area}
```

**Parámetros de área:**
- `terapeutico`: Especialidades terapéuticas
- `pedagogico`: Especialidades pedagógicas

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidades de terapeutico obtenidas correctamente",
    "data": [
        {
            "id": 1,
            "nombre": "Terapia del Lenguaje",
            "area": "Especialidad terapéutica para el desarrollo del lenguaje y comunicación",
            "estado": "activo",
            "fecha_creacion": "2024-01-01T00:00:00",
            "personal_asignado": 3
        },
        {
            "id": 2,
            "nombre": "Terapia Ocupacional",
            "area": "Especialidad terapéutica para el desarrollo de habilidades ocupacionales",
            "estado": "activo",
            "fecha_creacion": "2024-01-01T00:00:00",
            "personal_asignado": 2
        }
    ]
}
```

### 3. Obtener Especialidad por ID
```
GET /api/especialidades/id/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidad encontrada",
    "data": {
        "id": 1,
        "nombre": "Terapia del Lenguaje",
        "area": "Especialidad terapéutica para el desarrollo del lenguaje y comunicación",
        "estado": "activo",
        "fecha_creacion": "2024-01-01T00:00:00",
        "fecha_modificacion": null,
        "personal_asignado": 3
    }
}
```

### 4. Crear Especialidad
```
POST /api/especialidades
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
    "nombre": "Terapia Conductual",
    "area": "Especialidad terapéutica para modificación de conducta",
    "estado": "activo"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidad creada exitosamente",
    "data": {
        "id": 8,
        "nombre": "Terapia Conductual",
        "area": "Especialidad terapéutica para modificación de conducta",
        "estado": "activo",
        "fecha_creacion": "2024-01-15T11:30:00",
        "personal_asignado": 0
    }
}
```

### 5. Actualizar Especialidad
```
PUT /api/especialidades/id/{id}
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
    "nombre": "Terapia Conductual Aplicada",
    "area": "Especialidad terapéutica para modificación de conducta y análisis aplicado",
    "estado": "activo"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidad actualizada exitosamente",
    "data": {
        "id": 8,
        "nombre": "Terapia Conductual Aplicada",
        "area": "Especialidad terapéutica para modificación de conducta y análisis aplicado",
        "estado": "activo",
        "fecha_modificacion": "2024-01-15T14:20:00",
        "personal_asignado": 0
    }
}
```

### 6. Desactivar Especialidad
```
DELETE /api/especialidades/id/{id}
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
    "message": "Especialidad desactivada exitosamente",
    "data": null
}
```

### 7. Especialidades Activas (Para Combos/Selects)
```
GET /api/especialidades/activas
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidades activas obtenidas correctamente",
    "data": [
        {
            "id": 1,
            "nombre": "Terapia del Lenguaje",
            "area": "Especialidad terapéutica para el desarrollo del lenguaje y comunicación"
        },
        {
            "id": 5,
            "nombre": "Educación Especial",
            "area": "Especialidad pedagógica para la educación especializada"
        }
    ]
}
```

### 8. Estadísticas de Especialidades
```
GET /api/especialidades/estadisticas
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Estadísticas de especialidades obtenidas",
    "data": [
        {
            "area": "Especialidad terapéutica",
            "total_especialidades": 4,
            "activas": 4,
            "inactivas": 0
        },
        {
            "area": "Especialidad pedagógica",
            "total_especialidades": 3,
            "activas": 3,
            "inactivas": 0
        }
    ]
}
```

## Sistema de Compatibilidad

### 9. Verificar Compatibilidad Personal-Paciente
```
GET /api/compatibilidad-especialidades/{personal_id}/{paciente_id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Compatibilidad verificada exitosamente",
    "data": {
        "personal_id": 1,
        "paciente_id": 2,
        "especialidades_personal": 3,
        "especialidades_paciente": 2,
        "especialidades_comunes": 2,
        "porcentaje_compatibilidad": 100.0,
        "es_compatible": true,
        "recomendacion": "Asignación recomendada"
    }
}
```

### 10. Estadísticas de Especialidades Múltiples
```
GET /api/especialidades-multiples/estadisticas
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Estadísticas de especialidades múltiples obtenidas",
    "data": {
        "resumen": {
            "personal_con_especialidades": 8,
            "pacientes_con_especialidades": 15,
            "total_asignaciones_personal": 18,
            "total_asignaciones_pacientes": 25,
            "promedio_especialidades_personal": 2.25,
            "promedio_especialidades_paciente": 1.67
        },
        "especialidades_mas_asignadas": [
            {
                "nombre": "Terapia del Lenguaje",
                "descripcion": "Especialidad terapéutica",
                "personal_asignado": 3,
                "pacientes_asignados": 8,
                "total_asignaciones": 11
            },
            {
                "nombre": "Educación Especial",
                "descripcion": "Especialidad pedagógica",
                "personal_asignado": 2,
                "pacientes_asignados": 6,
                "total_asignaciones": 8
            }
        ]
    }
}
```

## Implementación Técnica

### 1. Validaciones de Datos

#### Validación de Especialidad
```python
def validate_especialidad_data(data, is_update=False):
    """Validar datos completos de especialidad"""
    errors = []
    
    # Campos requeridos para crear especialidad
    if not is_update:
        required_fields = ['nombre', 'area']
        for field in required_fields:
            if not data.get(field) or not data[field].strip():
                errors.append(f"{field} es requerido")
    
    # Validar nombre
    if 'nombre' in data and data['nombre']:
        nombre = data['nombre'].strip()
        if len(nombre) < 3 or len(nombre) > 100:
            errors.append("Nombre debe tener entre 3 y 100 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-()]+$", nombre):
            errors.append("Nombre solo puede contener letras, espacios, guiones y paréntesis")
    
    # Validar área
    if 'area' in data and data['area']:
        valid_areas = [
            'Especialidad terapéutica',
            'Especialidad pedagógica'
        ]
        if data['area'] not in valid_areas:
            errors.append(f"Área debe ser una de: {', '.join(valid_areas)}")
    
    return {'valid': len(errors) == 0, 'message': '; '.join(errors)}
```

### 2. Reglas de Negocio

#### Unicidad por Nombre y Área
```python
def check_nombre_exists(nombre, area, exclude_id=None):
    """Verificar si nombre ya existe en la misma área"""
    if exclude_id:
        query = "SELECT id FROM especialidad WHERE nombre = %s AND descripcion = %s AND id != %s"
        params = (nombre, area, exclude_id)
    else:
        query = "SELECT id FROM especialidad WHERE nombre = %s AND descripcion = %s"
        params = (nombre, area)
    
    existing = DataBaseHandle.getRecords(query, params, size=1)
    return existing is not None
```

#### Restricciones de Eliminación
```python
def deactivate_especialidad(especialidad_id):
    """No permitir desactivar si hay personal asignado"""
    personal_check = """
        SELECT COUNT(*) as total 
        FROM personal_especialidades 
        WHERE id_especialidad = %s
    """
    personal_count = DataBaseHandle.getRecords(personal_check, (especialidad_id,), size=1)
    
    if personal_count and personal_count['total'] > 0:
        return internal_response(False, None,
            f"No se puede desactivar la especialidad porque tiene {personal_count['total']} miembro(s) del personal asignado(s)")
    
    # Proceder con desactivación
```

### 3. Sistema de Compatibilidad Avanzado

#### Algoritmo de Compatibilidad
```python
def verificar_compatibilidad_especialidades(personal_id, paciente_id):
    """Verificar compatibilidad entre personal y paciente"""
    # Obtener especialidades del personal
    especialidades_personal = DataBaseHandle.getRecords("""
        SELECT pe.id_especialidad 
        FROM personal_especialidades pe
        INNER JOIN especialidad e ON pe.id_especialidad = e.id
        WHERE pe.id_personal = %s AND pe.estado = 'activo'
    """, (personal_id,))
    
    # Obtener especialidades del paciente
    especialidades_paciente = DataBaseHandle.getRecords("""
        SELECT pe.id_especialidad 
        FROM paciente_especialidades pe
        INNER JOIN especialidad e ON pe.id_especialidad = e.id
        WHERE pe.id_paciente = %s AND pe.estado = 'activo'
    """, (paciente_id,))
    
    # Calcular intersección
    esp_personal_ids = {esp['id_especialidad'] for esp in especialidades_personal} if especialidades_personal else set()
    esp_paciente_ids = {esp['id_especialidad'] for esp in especialidades_paciente} if especialidades_paciente else set()
    
    especialidades_comunes = esp_personal_ids.intersection(esp_paciente_ids)
    
    # Calcular porcentaje de compatibilidad
    total_especialidades_paciente = len(esp_paciente_ids)
    total_compatibles = len(especialidades_comunes)
    
    porcentaje_compatibilidad = (total_compatibles / total_especialidades_paciente * 100) if total_especialidades_paciente > 0 else 0
    
    # Generar recomendación
    if porcentaje_compatibilidad >= 50:
        recomendacion = "Asignación recomendada"
    elif porcentaje_compatibilidad > 0:
        recomendacion = "Revisar asignación"
    else:
        recomendacion = "No compatible"
    
    return {
        "personal_id": personal_id,
        "paciente_id": paciente_id,
        "especialidades_personal": len(esp_personal_ids),
        "especialidades_paciente": len(esp_paciente_ids),
        "especialidades_comunes": total_compatibles,
        "porcentaje_compatibilidad": round(porcentaje_compatibilidad, 2),
        "es_compatible": porcentaje_compatibilidad > 0,
        "recomendacion": recomendacion
    }
```

### 4. Consultas SQL Principales

#### Especialidades con Conteo de Personal
```sql
SELECT 
    e.id,
    e.nombre,
    e.descripcion as area,
    e.estado,
    e.fecha_creacion,
    e.fecha_modificacion,
    COUNT(pe.id) as personal_asignado
FROM especialidad e
LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad
GROUP BY e.id, e.nombre, e.descripcion, e.estado, e.fecha_creacion, e.fecha_modificacion
ORDER BY e.descripcion, e.nombre;
```

#### Estadísticas por Área
```sql
SELECT 
    descripcion as area,
    COUNT(*) as total_especialidades,
    COUNT(CASE WHEN estado = 'activo' THEN 1 END) as activas,
    COUNT(CASE WHEN estado = 'inactivo' THEN 1 END) as inactivas
FROM especialidad
GROUP BY descripcion
ORDER BY descripcion;
```

#### Especialidades Más Asignadas
```sql
SELECT 
    e.nombre,
    e.descripcion,
    COUNT(DISTINCT pe.id_personal) as personal_asignado,
    COUNT(DISTINCT pac.id_paciente) as pacientes_asignados,
    (COUNT(DISTINCT pe.id_personal) + COUNT(DISTINCT pac.id_paciente)) as total_asignaciones
FROM especialidad e
LEFT JOIN personal_especialidades pe ON e.id = pe.id_especialidad AND pe.estado = 'activo'
LEFT JOIN paciente_especialidades pac ON e.id = pac.id_especialidad AND pac.estado = 'activo'
WHERE e.estado = 'activo'
GROUP BY e.id, e.nombre, e.descripcion
ORDER BY total_asignaciones DESC
LIMIT 5;
```

## Casos de Uso y Flujos

### 1. Creación de Nueva Especialidad
```
1. Administrador crea especialidad → POST /api/especialidades
2. Sistema valida unicidad de nombre en área
3. Asigna estado activo por defecto
4. Especialidad disponible para asignar a personal/pacientes
5. Aparece en combos de selección
```

### 2. Asignación de Personal a Especialidad
```
1. Administrador asigna especialidad → POST /api/personal/{id}/especialidades
2. Sistema verifica compatibilidad de áreas
3. Personal puede atender pacientes de esa especialidad
4. Se actualiza en estadísticas de uso
```

### 3. Verificación de Compatibilidad
```
1. Sistema consulta especialidades del personal
2. Consulta especialidades del paciente
3. Calcula intersección de especialidades comunes
4. Genera porcentaje de compatibilidad
5. Recomienda asignación según porcentaje
```

### 4. Gestión de Estados
```
1. Administrador desactiva especialidad → DELETE /api/especialidades/id/{id}
2. Sistema verifica no hay personal asignado
3. Cambia estado a 'inactivo'
4. No aparece en nuevas asignaciones
5. Mantiene datos históricos
```

## Integración con Otros Módulos

### Con Personal
- **Especialidad principal**: personal.id_especialidad
- **Especialidades múltiples**: personal_especialidades
- **Filtrado**: Personal por especialidad específica
- **Competencias**: Niveles de competencia por especialidad

### Con Pacientes
- **Especialidad principal**: paciente.id_especialidad
- **Especialidades múltiples**: paciente_especialidades
- **Estados**: Activo, pausado, inactivo por especialidad
- **Tratamientos**: Pacientes por especialidad específica

### Con Sesiones
- **Sesiones terapéuticas**: Basadas en especialidades terapéuticas
- **Sesiones pedagógicas**: Basadas en especialidades pedagógicas
- **Asignaciones**: Personal y pacientes compatibles
- **Cronogramas**: Programación según especialidad

### Con Roles
- **Terapeuta**: Acceso a especialidades terapéuticas
- **Pedagógico**: Acceso a especialidades pedagógicas
- **Administrador**: Gestión completa de especialidades

## Validaciones y Restricciones

### Campos Obligatorios
- **nombre**: 3-100 caracteres, letras, espacios, guiones y paréntesis
- **area**: Debe ser "Especialidad terapéutica" o "Especialidad pedagógica"

### Reglas de Negocio
- **Unicidad**: Nombre único por área
- **Estados válidos**: activo, inactivo
- **Eliminación protegida**: No se puede desactivar si hay personal asignado
- **Área consistente**: Especialidades terapéuticas vs pedagógicas

### Códigos de Error
- **400**: Datos inválidos, nombre duplicado en área
- **401**: Token requerido o inválido
- **403**: Sin permisos de administrador
- **404**: Especialidad no encontrada
- **409**: Conflicto por personal asignado
- **500**: Error interno del servidor

## Configuración y Dependencias

### Variables de Entorno
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=centro_tia_glenda
```

### Datos Iniciales Requeridos
```sql
-- Script de inserción de especialidades básicas
INSERT INTO especialidad (nombre, descripcion) VALUES
-- Terapéuticas
('Terapia del Lenguaje', 'Especialidad terapéutica'),
('Terapia Ocupacional', 'Especialidad terapéutica'),
('Fisioterapia', 'Especialidad terapéutica'),
('Terapia Psicológica', 'Especialidad terapéutica'),
-- Pedagógicas
('Educación Especial', 'Especialidad pedagógica'),
('Apoyo Académico', 'Especialidad pedagógica'),
('Desarrollo Cognitivo', 'Especialidad pedagógica');
```

## Logging y Auditoría

El sistema registra:
- Creación de especialidades nuevas
- Modificaciones de nombre y área
- Desactivación de especialidades
- Verificaciones de compatibilidad
- Consultas de estadísticas
- Errores de asignación por especialidad inactiva

Ubicación: `src/utils/general/LOGS/`

## Testing

Pruebas incluidas para:
- CRUD completo de especialidades
- Validación de unicidad nombre-área
- Verificación de compatibilidad personal-paciente
- Restricciones de eliminación con personal asignado
- Estadísticas de uso y distribución
- Filtrado por área (terapéutica/pedagógica)

Ejecutar: `python tests/test_especialidades_api.py`

## Consideraciones de Seguridad

### Control de Acceso
- **Gestión**: Solo administradores pueden crear/modificar especialidades
- **Consulta**: Personal puede ver especialidades según su área
- **Compatibilidad**: Verificación automática de asignaciones válidas

### Integridad de Datos
- **Unicidad garantizada**: Prevención de especialidades duplicadas
- **Referencias válidas**: Verificación antes de desactivar
- **Estados consistentes**: Validación de transiciones de estado

### Auditoría Completa
- **Trazabilidad**: Usuario responsable de cada cambio
- **Timestamps**: Registro de fechas de creación/modificación
- **Logs detallados**: Registro de compatibilidades verificadas

## Limitaciones Actuales

### Áreas Fijas
- **Solo dos áreas**: Terapéutica y pedagógica predefinidas
- **Sin jerarquías**: No hay sub-especialidades o especialidades padre-hijo
- **Clasificación simple**: Área como texto libre en descripción

### Compatibilidad Básica
- **Algoritmo simple**: Solo intersección de especialidades
- **Sin pesos**: Todas las especialidades tienen igual importancia
- **Sin contexto**: No considera experiencia o certificaciones

## Recomendaciones de Mejora

### Futuras Implementaciones
1. **Jerarquía de especialidades**: Sistema padre-hijo para sub-especialidades
2. **Pesos de compatibilidad**: Importancia relativa por especialidad
3. **Certificaciones**: Niveles de certificación por especialidad
4. **Áreas dinámicas**: Sistema de categorías configurable
5. **Compatibilidad avanzada**: Algoritmos más sofisticados considerando experiencia
6. **Especialidades temporales**: Especialidades con fechas de vigencia
7. **Requisitos previos**: Especialidades que requieren otras como prerequisito
8. **Métricas de efectividad**: Seguimiento de resultados por especialidad