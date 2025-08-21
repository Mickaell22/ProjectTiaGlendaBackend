aho# Módulo de Usuarios - Centro Tía Glenda

## Resumen
Módulo que gestiona las cuentas de usuario del sistema, incluyendo credenciales de acceso, roles, permisos y configuraciones. Se integra con el módulo de Personas para obtener datos personales y con Roles para gestionar permisos.

## Arquitectura del Módulo

### Componentes Principales
- **UsuarioService**: Lógica de negocio y validaciones
- **UsuarioComponent**: Acceso a datos y operaciones CRUD
- **SecurityUtils**: Manejo de contraseñas hasheadas
- **Validators**: Validación de datos de entrada
- **Middleware**: Protección con admin_required y token_required

## Estructura de Base de Datos

### Tabla Principal: `usuario`
```sql
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasenia VARCHAR(255) NOT NULL,
    persona_id INTEGER REFERENCES persona(id) NOT NULL,
    rol_id INTEGER REFERENCES rol(id) NOT NULL,
    id_centro INTEGER REFERENCES centros(id) DEFAULT 13,
    estado VARCHAR(20) DEFAULT 'activo',
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_modificacion TIMESTAMP,
    fecha_ultimo_acceso TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);
```

### Relaciones con Otros Módulos
```sql
-- Datos personales
usuario.persona_id → persona.id

-- Rol y permisos
usuario.rol_id → rol.id

-- Centro asignado
usuario.id_centro → centros.id
```

### Tabla de Roles: `rol`
```sql
CREATE TABLE rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    estado VARCHAR(20) DEFAULT 'activo',
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- Datos iniciales
INSERT INTO rol (id, nombre, descripcion) VALUES
(1, 'administrador', 'Acceso completo al sistema'),
(2, 'usuario', 'Usuario estándar del sistema');
```

## Endpoints del API

### 1. Listar Usuarios
```
GET /api/usuarios
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
    "message": "Lista de usuarios obtenida correctamente",
    "data": [
        {
            "id": 1,
            "usuario": "admin",
            "nombre_completo": "Juan Pérez",
            "nombre": "Juan",
            "apellido": "Pérez",
            "cedula": "1234567890",
            "telefono": "0987654321",
            "correo": "admin@centro.com",
            "direccion": "Av. Principal 123",
            "fecha_nacimiento": "1990-05-15",
            "rol_id": 1,
            "rol": "administrador",
            "rol_nombre": "administrador",
            "persona_id": 1,
            "estado": "activo",
            "fecha_creacion": "2024-01-15T10:30:00",
            "fecha_modificacion": null,
            "fecha_ultimo_acceso": "2024-01-20T14:25:00"
        }
    ]
}
```

### 2. Obtener Usuario por ID
```
GET /api/usuarios/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Usuario encontrado",
    "data": {
        "id": 1,
        "usuario": "admin",
        "nombre_completo": "Juan Pérez",
        "nombre": "Juan",
        "apellido": "Pérez",
        "cedula": "1234567890",
        "telefono": "0987654321",
        "correo": "admin@centro.com",
        "fecha_nacimiento": "1990-05-15",
        "rol": "administrador",
        "rol_id": 1,
        "estado": "activo",
        "fecha_creacion": "2024-01-15T10:30:00",
        "fecha_modificacion": null
    }
}
```

### 3. Crear Usuario
```
POST /api/usuarios
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
    "usuario": "maria.gonzalez",
    "contrasenia": "MiPassword123!",
    "persona_id": 2,
    "rol_id": 2,
    "estado": "activo"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Usuario creado exitosamente",
    "data": {
        "id": 2,
        "usuario": "maria.gonzalez",
        "nombre_completo": "María González",
        "rol": "usuario",
        "rol_id": 2,
        "estado": "activo",
        "fecha_creacion": "2024-01-15T11:45:00"
    }
}
```

### 4. Actualizar Usuario
```
PUT /api/usuarios/{id}
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Permisos:** Solo administradores

**Request Body (campos opcionales):**
```json
{
    "usuario": "nuevo.usuario",
    "rol_id": 1,
    "estado": "activo"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Usuario actualizado exitosamente",
    "data": {
        "id": 2,
        "usuario": "nuevo.usuario",
        "rol_id": 1,
        "rol": "administrador",
        "fecha_modificacion": "2024-01-15T14:20:00"
    }
}
```

### 5. Desactivar Usuario
```
DELETE /api/usuarios/{id}
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
    "message": "Usuario desactivado exitosamente",
    "data": null
}
```

### 6. Cambiar Contraseña
```
PUT /api/usuarios/{id}/cambiar-contrasenia
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "nueva_contrasenia": "NuevaPassword123!",
    "confirmar_contrasenia": "NuevaPassword123!"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Contraseña actualizada exitosamente",
    "data": null
}
```

### 7. Obtener Roles Disponibles
```
GET /api/roles
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Lista de roles obtenida correctamente",
    "data": [
        {
            "id": 1,
            "nombre": "administrador",
            "descripcion": "Acceso completo al sistema",
            "estado": "activo",
            "fecha_creacion": "2024-01-01T00:00:00"
        },
        {
            "id": 2,
            "nombre": "usuario",
            "descripcion": "Usuario estándar del sistema",
            "estado": "activo",
            "fecha_creacion": "2024-01-01T00:00:00"
        }
    ]
}
```

## Implementación Técnica

### 1. Validaciones de Datos

#### Validación de Usuario
```python
def validate_usuario_data(data, is_update=False):
    """Validar datos completos de usuario"""
    errors = []
    
    # Campos requeridos para crear usuario
    if not is_update:
        required_fields = ['usuario', 'contrasenia', 'persona_id', 'rol_id']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field} es requerido")
    
    # Validar nombre de usuario
    if 'usuario' in data and data['usuario']:
        username = data['usuario'].strip()
        if len(username) < 3 or len(username) > 50:
            errors.append("Usuario debe tener entre 3 y 50 caracteres")
        if not re.match("^[a-zA-Z0-9._-]+$", username):
            errors.append("Usuario solo puede contener letras, números, puntos, guiones")
    
    # Validar contraseña
    if 'contrasenia' in data and data['contrasenia']:
        password_validation = validate_password(data['contrasenia'])
        if not password_validation['valid']:
            errors.append(password_validation['message'])
    
    return {'valid': len(errors) == 0, 'message': '; '.join(errors)}
```

#### Validación de Contraseña
```python
def validate_password(password):
    """Validar fortaleza de contraseña"""
    errors = []
    
    if len(password) < 8:
        errors.append("debe tener al menos 8 caracteres")
    
    if not re.search(r"[A-Z]", password):
        errors.append("debe contener al menos una mayúscula")
    
    if not re.search(r"[a-z]", password):
        errors.append("debe contener al menos una minúscula")
    
    if not re.search(r"\d", password):
        errors.append("debe contener al menos un número")
    
    return {
        'valid': len(errors) == 0,
        'message': f"Contraseña inválida: {', '.join(errors)}" if errors else "Contraseña válida"
    }
```

### 2. Reglas de Negocio

#### Unicidad de Username
```python
def check_username_exists(username, exclude_id=None):
    """Verificar si nombre de usuario ya existe"""
    if exclude_id:
        query = "SELECT id FROM usuario WHERE usuario = %s AND id != %s"
        params = (username, exclude_id)
    else:
        query = "SELECT id FROM usuario WHERE usuario = %s"
        params = (username,)
    
    existing = DataBaseHandle.getRecords(query, params, size=1)
    return existing is not None
```

#### Restricciones de Eliminación
```python
def delete_usuario(usuario_id):
    # No permitir eliminar usuario admin principal (ID=1)
    if usuario_id == 1:
        return response_error("No se puede eliminar el usuario administrador principal", 400)
    
    # Proceder con desactivación lógica
    result = UsuarioComponent.deactivate_usuario(usuario_id)
```

### 3. Seguridad de Contraseñas

#### Hash con bcrypt
```python
import bcrypt

def hash_password(password):
    """Hashear contraseña con bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Verificar contraseña"""
    return bcrypt.checkpw(
        password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )
```

#### Cambio de Contraseña Seguro
```python
def change_password(usuario_id, nueva_contrasenia):
    """Cambiar contraseña con validaciones"""
    # Verificar usuario activo
    user_check = "SELECT estado FROM usuario WHERE id = %s"
    user = DataBaseHandle.getRecords(user_check, (usuario_id,))
    
    if not user or user['estado'] != 'activo':
        return internal_response(False, None, "Usuario no encontrado o inactivo")
    
    # Hash nueva contraseña
    hashed_password = SecurityUtils.hash_password(nueva_contrasenia)
    
    # Actualizar en BD
    update_query = """
        UPDATE usuario 
        SET contrasenia = %s, fecha_modificacion = CURRENT_TIMESTAMP
        WHERE id = %s
    """
    
    success = DataBaseHandle.ExecuteNonQuery(update_query, (hashed_password, usuario_id))
    return internal_response(success, None, "Contraseña actualizada" if success else "Error")
```

### 4. Estructura del Servicio

#### UsuarioService (Capa de Lógica)
```python
class UsuarioService:
    
    @staticmethod
    def create_usuario():
        # 1. Obtener y validar datos
        data = request.get_json()
        validation = Validators.validate_usuario_data(data, is_update=False)
        
        if not validation['valid']:
            return response_error(validation['message'], 400)
        
        # 2. Hashear contraseña
        hashed_password = SecurityUtils.hash_password(data['contrasenia'])
        if not hashed_password:
            return response_error("Error procesando contraseña", 500)
        
        # 3. Preparar datos
        user_data = {
            'usuario': data['usuario'].strip(),
            'contrasenia': hashed_password,
            'persona_id': int(data['persona_id']),
            'rol_id': int(data['rol_id']),
            'estado': data.get('estado', 'activo'),
            'usuario_creacion': request.current_user['id']
        }
        
        # 4. Delegar a componente
        result = UsuarioComponent.create_usuario(user_data)
        
        # 5. Retornar respuesta
        if result['success']:
            return response_success(result['data'], "Usuario creado")
        else:
            return response_error(result['message'], 400)
```

## Consultas SQL Principales

### Usuario con Información Completa
```sql
SELECT 
    u.id,
    u.usuario,
    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
    p.nombre,
    p.apellido,
    p.cedula,
    p.telefono,
    p.correo,
    p.direccion,
    p.fecha_nacimiento,
    r.id as rol_id,
    r.nombre as rol,
    u.persona_id,
    u.estado,
    u.fecha_creacion,
    u.fecha_modificacion,
    u.fecha_ultimo_acceso
FROM usuario u
INNER JOIN persona p ON u.persona_id = p.id
INNER JOIN rol r ON u.rol_id = r.id
ORDER BY u.id;
```

### Verificación de Username Único
```sql
SELECT id FROM usuario 
WHERE usuario = %s AND id != %s;
```

## Casos de Uso y Flujos

### 1. Creación de Usuario
```
1. Administrador selecciona persona → GET /api/personas/disponibles
2. Administrador crea usuario → POST /api/usuarios
3. Sistema valida datos y unicidad de username
4. Hashea contraseña con bcrypt
5. Inserta en BD con centro por defecto
6. Retorna usuario creado con información completa
7. Logs registro de creación
```

### 2. Cambio de Contraseña
```
1. Usuario solicita cambio → PUT /api/usuarios/{id}/cambiar-contrasenia
2. Sistema valida fortaleza de nueva contraseña
3. Verifica confirmación de contraseña
4. Hashea nueva contraseña
5. Actualiza en BD con timestamp
6. Logs cambio de contraseña
```

### 3. Gestión de Estados
```
1. Administrador desactiva usuario → DELETE /api/usuarios/{id}
2. Sistema verifica que no es admin principal (ID=1)
3. Cambia estado a 'inactivo' (eliminación lógica)
4. Usuario no podrá autenticarse
5. Datos históricos se mantienen
```

## Integración con Otros Módulos

### Con Autenticación
- **Login**: Verifica credenciales contra tabla usuario
- **Token JWT**: Incluye user_id, username, rol
- **Middleware**: Valida token y obtiene datos de usuario

### Con Personas
- **Creación**: Requiere persona_id existente
- **Consultas**: JOIN con persona para datos completos
- **Restricción**: Una persona puede tener solo un usuario

### Con Roles
- **Asignación**: rol_id define permisos del usuario
- **Validación**: Solo roles activos pueden asignarse
- **Middleware**: admin_required verifica rol = 'administrador'

## Validaciones y Restricciones

### Campos Obligatorios
- **usuario**: 3-50 caracteres, alfanumérico con puntos/guiones, único
- **contrasenia**: mínimo 8 caracteres, mayúscula, minúscula, número
- **persona_id**: debe existir en tabla persona
- **rol_id**: debe existir en tabla rol y estar activo

### Reglas de Negocio
- **Username único** en todo el sistema
- **Una persona = un usuario** (relación 1:1)
- **Admin principal** (ID=1) no se puede eliminar
- **Eliminación lógica** (estado = inactivo)
- **Centro por defecto** si no se especifica

### Códigos de Error
- **400**: Datos inválidos, username duplicado, validación fallida
- **401**: Token requerido o inválido
- **403**: Sin permisos de administrador
- **404**: Usuario no encontrado
- **500**: Error interno, problema hasheando contraseña

## Configuración y Dependencias

### Librerías Requeridas
```bash
pip install bcrypt==4.0.1
pip install PyJWT==2.8.0
pip install psycopg2==2.9.10
```

### Variables de Entorno
```bash
JWT_SECRET=clave_secreta_jwt
DB_HOST=localhost
DB_PORT=5432
DB_NAME=centro_tia_glenda
```

## Logging y Auditoría

El sistema registra:
- Creación de usuarios nuevos
- Modificaciones de datos con usuario responsable
- Cambios de contraseña (sin registrar la contraseña)
- Desactivación de usuarios
- Intentos de creación con username duplicado
- Errores de validación y base de datos

Ubicación: `src/utils/general/LOGS/`

## Testing

Pruebas incluidas:
- CRUD completo de usuarios
- Validación de contraseñas fuertes
- Verificación de unicidad de username
- Restricciones de eliminación de admin
- Cambio de contraseña con validaciones
- Integración con autenticación JWT

Ejecutar: `python tests/test_usuarios_api.py`

## Consideraciones de Seguridad

### Mejores Prácticas Implementadas
- **Contraseñas hasheadas** con bcrypt y salt único
- **Validación de fortaleza** de contraseñas
- **Eliminación lógica** para mantener auditoría
- **Restricción de admin principal** para evitar lockout
- **Logs detallados** sin exponer contraseñas
- **Validación de entrada** para prevenir inyecciones

### Recomendaciones Adicionales
- Implementar política de expiración de contraseñas
- Añadir autenticación de dos factores (2FA)
- Rate limiting en endpoints de creación
- Notificaciones de cambios de contraseña
- Auditoría de accesos fallidos