# Módulo de Personas - Centro Tía Glenda

## Resumen
Módulo central que gestiona la información personal base de todos los individuos del sistema (empleados, pacientes, tutores). Funciona como tabla maestra para otros módulos.

## Arquitectura del Módulo

### Componentes Principales
- **PersonaService**: Lógica de negocio y validaciones
- **PersonaComponent**: Acceso a datos y operaciones CRUD
- **Validators**: Validación de datos de entrada
- **Middleware**: Protección con token_required y admin_required

## Estructura de Base de Datos

### Tabla Principal: `persona`
```sql
CREATE TABLE persona (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    correo VARCHAR(255) UNIQUE,
    direccion VARCHAR(255),
    fecha_nacimiento DATE,
    estado VARCHAR(20) DEFAULT 'activo',
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);
```

### Relaciones con Otros Módulos
```sql
-- Usuarios del sistema
usuario.persona_id → persona.id

-- Personal/empleados
personal.persona_id → persona.id

-- Pacientes
paciente.persona_id → persona.id

-- Tutores/responsables
tutor.persona_id → persona.id
```

## Endpoints del API

### 1. Listar Personas
```
GET /api/personas
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Lista de personas obtenida correctamente",
    "data": [
        {
            "id": 1,
            "nombre": "Juan",
            "apellido": "Pérez",
            "nombre_completo": "Juan Pérez",
            "cedula": "1234567890",
            "telefono": "0987654321",
            "correo": "juan.perez@email.com",
            "direccion": "Av. Principal 123",
            "fecha_nacimiento": "1990-05-15",
            "estado": "activo",
            "fecha_creacion": "2024-01-15T10:30:00",
            "fecha_modificacion": null,
            "tiene_usuario": "Si",
            "rol_usuario": "administrador"
        }
    ]
}
```

### 2. Obtener Persona por ID
```
GET /api/personas/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Persona encontrada",
    "data": {
        "id": 1,
        "nombre": "Juan",
        "apellido": "Pérez",
        "nombre_completo": "Juan Pérez",
        "cedula": "1234567890",
        "telefono": "0987654321",
        "correo": "juan.perez@email.com",
        "direccion": "Av. Principal 123",
        "fecha_nacimiento": "1990-05-15",
        "estado": "activo",
        "fecha_creacion": "2024-01-15T10:30:00",
        "fecha_modificacion": null,
        "tiene_usuario": "Si",
        "usuario_id": 1,
        "nombre_usuario": "admin",
        "rol_usuario": "administrador"
    }
}
```

### 3. Crear Persona
```
POST /api/personas
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "nombre": "María",
    "apellido": "González",
    "cedula": "0987654321",
    "telefono": "0998765432",
    "correo": "maria.gonzalez@email.com",
    "direccion": "Calle Secundaria 456",
    "fecha_nacimiento": "1985-12-20",
    "estado": "activo"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Persona creada exitosamente",
    "data": {
        "id": 2,
        "nombre": "María",
        "apellido": "González",
        "nombre_completo": "María González",
        "cedula": "0987654321",
        "telefono": "0998765432",
        "correo": "maria.gonzalez@email.com",
        "direccion": "Calle Secundaria 456",
        "fecha_nacimiento": "1985-12-20",
        "estado": "activo",
        "fecha_creacion": "2024-01-15T11:45:00",
        "tiene_usuario": "No",
        "rol_usuario": null
    }
}
```

### 4. Actualizar Persona
```
PUT /api/personas/{id}
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body (campos opcionales):**
```json
{
    "telefono": "0999888777",
    "correo": "nuevo.correo@email.com",
    "direccion": "Nueva Dirección 789"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Persona actualizada exitosamente",
    "data": {
        "id": 2,
        "nombre": "María",
        "apellido": "González",
        "telefono": "0999888777",
        "correo": "nuevo.correo@email.com",
        "direccion": "Nueva Dirección 789",
        "fecha_modificacion": "2024-01-15T14:20:00"
    }
}
```

### 5. Desactivar Persona
```
DELETE /api/personas/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Permisos:** Requiere rol de administrador

**Response:**
```json
{
    "success": true,
    "message": "Persona desactivada exitosamente",
    "data": null
}
```

### 6. Personas Disponibles (Sin Usuario)
```
GET /api/personas/disponibles
```

**Headers:**
```
Authorization: Bearer <token>
```

**Permisos:** Requiere rol de administrador

**Response:**
```json
{
    "success": true,
    "message": "Personas disponibles para crear usuario",
    "data": [
        {
            "id": 3,
            "nombre": "Carlos",
            "apellido": "Rodríguez",
            "nombre_completo": "Carlos Rodríguez",
            "cedula": "1122334455",
            "correo": "carlos.rodriguez@email.com"
        }
    ]
}
```

## Implementación Técnica

### 1. Validaciones de Datos

#### Validación de Persona
```python
def validate_persona_data(data, is_update=False):
    """Validar datos completos de persona"""
    errors = []
    
    # Campos requeridos para crear persona
    if not is_update:
        required_fields = ['nombre', 'apellido', 'cedula']
        for field in required_fields:
            if not data.get(field) or not data[field].strip():
                errors.append(f"{field} es requerido")
    
    # Validaciones específicas
    if 'nombre' in data:
        if len(data['nombre'].strip()) < 2:
            errors.append("Nombre debe tener al menos 2 caracteres")
            
    if 'cedula' in data:
        if not re.match("^[0-9]{7,20}$", data['cedula']):
            errors.append("Cédula debe contener solo números (7-20 dígitos)")
    
    if 'correo' in data and data['correo']:
        if not validate_email_format(data['correo']):
            errors.append("Formato de correo inválido")
    
    # ... más validaciones
    
    return {'valid': len(errors) == 0, 'message': '; '.join(errors)}
```

### 2. Reglas de Negocio

#### Unicidad de Datos
- **Cédula**: Debe ser única en todo el sistema
- **Correo**: Debe ser único si se proporciona
- **Verificación en creación y actualización**

#### Estados
- **activo**: Persona habilitada en el sistema
- **inactivo**: Persona deshabilitada (eliminación lógica)

#### Restricciones de Eliminación
```python
def deactivate_persona(persona_id):
    # No permitir desactivar si tiene usuario activo
    user_check = "SELECT estado FROM usuario WHERE persona_id = %s"
    user_exists = DataBaseHandle.getRecords(user_check, (persona_id,))
    
    if user_exists and user_exists['estado'] == 'activo':
        return error("No se puede desactivar persona con usuario activo")
    
    # Proceder con desactivación
```

### 3. Estructura del Servicio

#### PersonaService (Capa de Lógica)
```python
class PersonaService:
    
    @staticmethod
    def create_persona():
        # 1. Obtener datos del request
        data = request.get_json()
        
        # 2. Validar datos
        validation = Validators.validate_persona_data(data, is_update=False)
        if not validation['valid']:
            return response_error(validation['message'], 400)
        
        # 3. Agregar metadatos
        data['usuario_creacion'] = request.current_user['id']
        
        # 4. Delegar a componente
        result = PersonaComponent.create_persona(data)
        
        # 5. Retornar respuesta
        if result['success']:
            return response_success(result['data'], "Persona creada")
        else:
            return response_error(result['message'], 400)
```

#### PersonaComponent (Capa de Datos)
```python
class PersonaComponent:
    
    @staticmethod
    def create_persona(data):
        try:
            # Verificar unicidad de cédula
            if check_cedula_exists(data['cedula']):
                return internal_response(False, None, "Cédula ya existe")
            
            # Insertar en base de datos
            query = """
                INSERT INTO persona (nombre, apellido, cedula, telefono, 
                                   correo, direccion, fecha_nacimiento, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            new_id = DataBaseHandle.ExecuteInsert(query, params)
            
            if new_id:
                # Retornar persona creada completa
                new_persona = get_persona_by_id(new_id)
                return internal_response(True, new_persona, "Persona creada")
            
        except Exception as e:
            return internal_response(False, None, f"Error: {str(e)}")
```

### 4. Consultas SQL Principales

#### Listar Personas con Información de Usuario
```sql
SELECT 
    p.id,
    p.nombre,
    p.apellido,
    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
    p.cedula,
    p.telefono,
    p.correo,
    p.direccion,
    p.fecha_nacimiento,
    p.estado,
    p.fecha_creacion,
    p.fecha_modificacion,
    CASE 
        WHEN u.id IS NOT NULL THEN 'Si'
        ELSE 'No'
    END as tiene_usuario,
    r.nombre as rol_usuario
FROM persona p
LEFT JOIN usuario u ON p.id = u.persona_id
LEFT JOIN rol r ON u.rol_id = r.id
ORDER BY p.id;
```

#### Personas Disponibles (Sin Usuario)
```sql
SELECT 
    p.id,
    p.nombre,
    p.apellido,
    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
    p.cedula,
    p.correo
FROM persona p
LEFT JOIN usuario u ON p.id = u.persona_id
WHERE u.id IS NULL AND p.estado = 'activo'
ORDER BY p.nombre, p.apellido;
```

## Casos de Uso y Flujos

### 1. Creación de Persona Nueva
```
1. Usuario autenticado envía datos → POST /api/personas
2. Sistema valida formato de datos
3. Verifica unicidad de cédula y correo
4. Inserta en base de datos
5. Retorna persona creada con ID asignado
6. Logs registro de creación
```

### 2. Búsqueda de Personas para Crear Usuario
```
1. Administrador solicita → GET /api/personas/disponibles
2. Sistema consulta personas sin usuario asociado
3. Filtra solo personas activas
4. Retorna lista para selección
```

### 3. Actualización de Datos Personales
```
1. Usuario envía cambios → PUT /api/personas/{id}
2. Sistema valida que persona existe
3. Verifica unicidad de campos modificados
4. Actualiza solo campos proporcionados
5. Registra usuario que modificó y timestamp
6. Retorna datos actualizados
```

## Validaciones y Restricciones

### Campos Obligatorios
- **nombre**: 2-100 caracteres, solo letras y espacios
- **apellido**: 2-100 caracteres, solo letras y espacios  
- **cedula**: 7-20 dígitos, solo números, único

### Campos Opcionales
- **telefono**: 8-15 dígitos
- **correo**: formato email válido, único
- **direccion**: hasta 255 caracteres
- **fecha_nacimiento**: formato YYYY-MM-DD, no futura, no más de 120 años atrás

### Códigos de Error
- **400**: Datos inválidos o campos faltantes
- **401**: Token requerido o inválido
- **403**: Sin permisos de administrador
- **404**: Persona no encontrada
- **409**: Cédula o correo duplicado
- **500**: Error interno del servidor

## Dependencias y Configuración

### Librerías Requeridas
```bash
pip install email-validator==2.1.0
pip install psycopg2==2.9.10
```

### Variables de Entorno
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=centro_tia_glenda
DB_USER=postgres
DB_PASSWORD=password
```

## Logging y Auditoría

El sistema registra automáticamente:
- Creación de personas nuevas
- Modificaciones con usuario responsable
- Intentos de eliminación
- Consultas de personas disponibles
- Errores de validación y base de datos

Ubicación: `src/utils/general/LOGS/`

## Testing

Pruebas incluidas para:
- CRUD completo de personas
- Validaciones de campos obligatorios
- Verificación de unicidad de cédula/correo
- Restricciones de eliminación
- Consultas de personas disponibles

Ejecutar: `python tests/test_personas_api.py`

## Integración con Otros Módulos

### Como Tabla Maestra
- **Usuario**: Referencia persona_id para datos personales
- **Personal**: Extiende persona con información laboral
- **Paciente**: Extiende persona con información médica
- **Tutor**: Referencia persona como responsable

### Flujo Típico de Integración
```
1. Crear persona base → POST /api/personas
2. Crear usuario del sistema → POST /api/usuarios (usando persona_id)
3. Asignar como personal → POST /api/personal (usando persona_id)
```

## Consideraciones de Seguridad

- **Eliminación lógica**: No se eliminan físicamente los registros
- **Validación de entrada**: Prevención de inyección SQL
- **Unicidad garantizada**: Evita duplicación de identidades
- **Auditoría completa**: Registro de cambios con timestamp y usuario
- **Acceso controlado**: Endpoints protegidos con autenticación