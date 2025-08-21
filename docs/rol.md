# Módulo de Roles - Centro Tía Glenda

## Resumen
Módulo que gestiona los roles y permisos del sistema, definiendo qué acciones puede realizar cada tipo de usuario. Es fundamental para el control de acceso basado en roles (RBAC) del sistema.

## Arquitectura del Módulo

### Componentes Principales
- **RolService**: Lógica de negocio para gestión de roles
- **Consultas directas**: Acceso simple a datos sin componente separado
- **Middleware**: Integración con @admin_required y @token_required
- **Sistema RBAC**: Control de acceso basado en roles

## Estructura de Base de Datos

### Tabla Principal: `rol`
```sql
CREATE TABLE IF NOT EXISTS rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);
```

### Roles Predefinidos del Sistema
```sql
-- Datos iniciales
INSERT INTO rol (nombre, descripcion, estado) VALUES
('Administrador', 'Acceso completo al sistema, gestión de usuarios y centros', 'activo'),
('Terapeuta', 'Personal especializado en terapias, gestión de pacientes asignados', 'activo'),
('Pedagógico', 'Personal especializado en educación, gestión de estudiantes', 'activo');
```

### Relaciones con Otros Módulos
```sql
-- Usuarios del sistema
usuario.rol_id → rol.id

-- Control de acceso en middleware
auth_middleware → verifica rol para permisos
```

## Roles del Sistema

### 1. Administrador
**Permisos:**
- Acceso completo a todos los módulos
- Gestión de usuarios y roles
- Configuración del sistema
- Acceso a reportes y estadísticas
- Gestión de centros médicos

**Endpoints exclusivos:**
```
POST /api/usuarios          - Crear usuarios
PUT /api/usuarios/{id}      - Actualizar usuarios  
DELETE /api/usuarios/{id}   - Desactivar usuarios
GET /api/personas/disponibles - Personas sin usuario
GET /api/usuarios           - Listar todos los usuarios
```

### 2. Terapeuta
**Permisos:**
- Gestión de pacientes asignados
- Creación y gestión de sesiones terapéuticas
- Registro de asistencias y observaciones
- Acceso a información de pacientes
- Generación de cronogramas de sesiones

**Funcionalidades:**
- Sesiones de terapia del lenguaje
- Sesiones de terapia ocupacional
- Sesiones de fisioterapia
- Sesiones de terapia psicológica

### 3. Pedagógico
**Permisos:**
- Gestión de estudiantes asignados
- Creación y gestión de sesiones pedagógicas
- Registro de asistencias y calificaciones
- Acceso a información de estudiantes
- Generación de cronogramas de clases

**Funcionalidades:**
- Clases de educación especial
- Sesiones de apoyo académico
- Programas de desarrollo cognitivo

## Endpoints del API

### 1. Obtener Roles Activos
```
GET /api/roles
```

**Headers:**
```
Authorization: Bearer <token>
```

**Permisos:** Cualquier usuario autenticado

**Response:**
```json
{
    "success": true,
    "message": "Lista de roles obtenida correctamente",
    "data": [
        {
            "id": 1,
            "nombre": "Administrador",
            "descripcion": "Acceso completo al sistema, gestión de usuarios y centros",
            "estado": "activo",
            "fecha_creacion": "2024-01-01T00:00:00"
        },
        {
            "id": 2,
            "nombre": "Terapeuta", 
            "descripcion": "Personal especializado en terapias, gestión de pacientes asignados",
            "estado": "activo",
            "fecha_creacion": "2024-01-01T00:00:00"
        },
        {
            "id": 3,
            "nombre": "Pedagógico",
            "descripcion": "Personal especializado en educación, gestión de estudiantes", 
            "estado": "activo",
            "fecha_creacion": "2024-01-01T00:00:00"
        }
    ]
}
```

## Implementación Técnica

### 1. Servicio de Roles

#### RolService
```python
class RolService:
    
    @staticmethod
    def get_roles():
        """Obtener lista de todos los roles activos"""
        try:
            HandleLogs.write_log("RolService.get_roles - Iniciando")
            
            query = """
            SELECT 
                id,
                nombre,
                descripcion,
                estado,
                fecha_creacion
            FROM rol 
            WHERE estado = 'activo'
            ORDER BY id
            """
            
            roles = DataBaseHandle.getRecords(query)
            
            if roles is not None:
                HandleLogs.write_log(f"RolService.get_roles - {len(roles)} roles encontrados")
                return response_success(roles, "Lista de roles obtenida correctamente")
            else:
                HandleLogs.write_error("RolService.get_roles - Error en consulta")
                return response_error("Error obteniendo roles", 500)
                
        except Exception as e:
            HandleLogs.write_error(f"RolService.get_roles - Error: {str(e)}")
            return response_error(f"Error interno: {str(e)}", 500)
```

### 2. Sistema de Control de Acceso

#### Middleware de Autenticación por Rol
```python
def admin_required(f):
    """Decorador para requerir rol de administrador"""
    
    @wraps(f)
    @token_required
    def decorated_function(*args, **kwargs):
        try:
            user = request.current_user
            
            # Verificar rol de administrador (case-insensitive)
            if user['rol'].lower() != 'administrador':
                HandleLogs.write_log(
                    f"auth_middleware.admin_required - Acceso denegado para usuario: {user['usuario']}"
                )
                return response_error(
                    "Acceso denegado. Se requieren permisos de administrador", 
                    403
                )
            
            return f(*args, **kwargs)
            
        except Exception as e:
            HandleLogs.write_error(f"auth_middleware.admin_required - Error: {str(e)}")
            return response_error("Error verificando permisos", 500)
    
    return decorated_function
```

#### Verificación en Token JWT
```python
# En LoginService.login()
token_data = {
    'id': user['id'],
    'usuario': user['usuario'],
    'rol': user['rol'],  # Rol incluido en token
    'nombre_completo': user['nombre_completo'],
    'id_centro': user['id_centro']
}

token = SecurityUtils.generate_token(token_data)
```

### 3. Integración con Usuarios

#### Consulta de Usuario con Rol
```sql
SELECT 
    u.id,
    u.usuario,
    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
    r.id as rol_id,
    r.nombre as rol,
    r.descripcion as rol_descripcion,
    u.estado
FROM usuario u
INNER JOIN persona p ON u.persona_id = p.id
INNER JOIN rol r ON u.rol_id = r.id
WHERE u.id = %s;
```

#### Validación de Rol Activo
```python
def validate_rol_exists(rol_id):
    """Verificar que el rol existe y está activo"""
    query = "SELECT id FROM rol WHERE id = %s AND estado = 'activo'"
    result = DataBaseHandle.getRecords(query, (rol_id,), size=1)
    return result is not None
```

## Control de Acceso por Endpoints

### Endpoints Públicos (Sin autenticación)
```python
@app.route('/api/login', methods=['POST'])
def login():
    # Sin decoradores de autenticación
```

### Endpoints con Token (Cualquier usuario autenticado)
```python
@app.route('/api/personas', methods=['GET'])
@token_required
def get_personas():
    # Requiere token válido, cualquier rol
```

### Endpoints Solo Administrador
```python
@app.route('/api/usuarios', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required  # Implica @token_required
def manage_usuarios():
    # Solo usuarios con rol = 'Administrador'
```

## Matriz de Permisos por Rol

### Administrador
| Módulo | Crear | Leer | Actualizar | Eliminar | Especiales |
|--------|-------|------|------------|----------|------------|
| Usuarios | ✓ | ✓ | ✓ | ✓ | Gestión completa |
| Personas | ✓ | ✓ | ✓ | ✓ | Personas disponibles |
| Personal | ✓ | ✓ | ✓ | ✓ | Asignación especialidades |
| Pacientes | ✓ | ✓ | ✓ | ✓ | Estado, especialidades |
| Sesiones | ✓ | ✓ | ✓ | ✓ | Todas las sesiones |
| Reportes | - | ✓ | - | - | Estadísticas globales |

### Terapeuta
| Módulo | Crear | Leer | Actualizar | Eliminar | Especiales |
|--------|-------|------|------------|----------|------------|
| Usuarios | - | Propio | Propio | - | Solo su perfil |
| Pacientes | - | Asignados | - | - | Solo sus pacientes |
| Sesiones Terapéuticas | ✓ | ✓ | ✓ | ✓ | Sus sesiones |
| Cronogramas | ✓ | ✓ | ✓ | - | Gestión horarios |
| Asistencias | ✓ | ✓ | ✓ | - | Registro asistencia |
| Observaciones | ✓ | ✓ | ✓ | ✓ | Sus observaciones |

### Pedagógico  
| Módulo | Crear | Leer | Actualizar | Eliminar | Especiales |
|--------|-------|------|------------|----------|------------|
| Usuarios | - | Propio | Propio | - | Solo su perfil |
| Estudiantes | - | Asignados | - | - | Solo sus estudiantes |
| Sesiones Pedagógicas | ✓ | ✓ | ✓ | ✓ | Sus sesiones |
| Cronogramas Clases | ✓ | ✓ | ✓ | - | Gestión horarios |
| Asistencias | ✓ | ✓ | ✓ | - | Registro asistencia |
| Calificaciones | ✓ | ✓ | ✓ | ✓ | Evaluaciones |

## Casos de Uso del Sistema de Roles

### 1. Asignación de Rol en Creación de Usuario
```
1. Administrador crea usuario → POST /api/usuarios
2. Sistema valida rol_id existe y está activo
3. Asigna rol al usuario en base de datos
4. Usuario hereda permisos del rol asignado
5. Token JWT incluye información del rol
```

### 2. Verificación de Permisos en Runtime
```
1. Usuario hace request → GET /api/usuarios
2. Middleware extrae rol del token JWT
3. Compara rol con requerimientos del endpoint (@admin_required)
4. Permite o deniega acceso según permisos
5. Logs intento de acceso para auditoría
```

### 3. Gestión de Roles por Administrador
```
1. Administrador consulta roles → GET /api/roles  
2. Sistema retorna solo roles activos
3. Administrador asigna roles a usuarios nuevos
4. Sistema valida integridad referencial
5. Cambios de rol requieren re-autenticación
```

## Consultas SQL del Módulo

### Obtener Roles Activos
```sql
SELECT 
    id,
    nombre,
    descripcion,
    estado,
    fecha_creacion
FROM rol 
WHERE estado = 'activo'
ORDER BY id;
```

### Verificar Rol Existe
```sql
SELECT id 
FROM rol 
WHERE id = %s AND estado = 'activo';
```

### Usuarios por Rol
```sql
SELECT 
    COUNT(*) as total_usuarios,
    r.nombre as rol
FROM usuario u
INNER JOIN rol r ON u.rol_id = r.id
WHERE u.estado = 'activo'
GROUP BY r.id, r.nombre
ORDER BY total_usuarios DESC;
```

## Integración con Otros Módulos

### Con Autenticación
- **Login**: Incluye rol en token JWT
- **Middleware**: Verifica rol para control de acceso
- **Sesión**: Mantiene rol en request.current_user

### Con Usuarios
- **Creación**: Requiere rol_id válido y activo
- **Actualización**: Permite cambio de rol por admin
- **Consulta**: JOIN con rol para obtener nombre y descripción

### Con Personal/Pacientes
- **Filtrado**: Terapeuta/Pedagógico ve solo asignados
- **Sesiones**: Acceso según rol y asignaciones
- **Reportes**: Datos limitados según permisos del rol

## Extensibilidad del Sistema

### Nuevos Roles
Para añadir nuevos roles:
```sql
INSERT INTO rol (nombre, descripcion, estado) VALUES
('Nuevo_Rol', 'Descripción del nuevo rol', 'activo');
```

### Nuevos Permisos
Para implementar permisos granulares:
```python
def permission_required(permission):
    """Decorador para permisos específicos"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(*args, **kwargs):
            if not user_has_permission(request.current_user, permission):
                return response_error("Acceso denegado", 403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

## Consideraciones de Seguridad

### Principio de Menor Privilegio
- Usuarios reciben permisos mínimos necesarios
- Roles específicos por función laboral
- Segregación de responsabilidades

### Auditoría y Monitoreo
- Log de todos los intentos de acceso
- Registro de cambios de roles
- Alertas de accesos denegados repetidos

### Validaciones
- Verificación de rol activo en cada request
- Validación de integridad referencial
- Control de estados (activo/inactivo)

## Limitaciones Actuales

### Roles Estáticos
- Roles predefinidos en base de datos
- No hay interfaz para crear roles dinámicamente
- Permisos codificados en middleware

### Permisos Binarios
- Solo permite/deniega acceso completo
- No hay permisos granulares por recurso
- Limitado a nivel de endpoint

### Jerarquía Plana
- No hay jerarquía de roles
- No herencia de permisos
- Cada rol es independiente

## Recomendaciones de Mejora

### Futuras Implementaciones
1. **Sistema de Permisos Granular**: Permisos específicos por recurso
2. **Roles Dinámicos**: Interfaz para crear/modificar roles
3. **Jerarquía de Roles**: Herencia de permisos padre-hijo
4. **Permisos Temporales**: Roles con fechas de expiración
5. **Audit Trail**: Historial completo de cambios de permisos