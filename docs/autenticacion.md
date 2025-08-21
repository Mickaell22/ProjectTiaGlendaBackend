# Sistema de Autenticación - Centro Tía Glenda

## Resumen
Sistema de autenticación basado en JWT (JSON Web Tokens) con roles de usuario, integración con centros médicos y middleware de seguridad robusto.

## Arquitectura del Sistema

### Componentes Principales
- **LoginService**: Lógica de negocio para autenticación
- **LoginComponent**: Acceso a datos de usuarios
- **SecurityUtils**: Utilidades de seguridad (JWT, bcrypt)
- **Middleware**: Decoradores para protección de endpoints

## Endpoints de Autenticación

### 1. Login
```
POST /api/login
```

**Request Body:**
```json
{
    "usuario": "string",
    "contrasenia": "string"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Autenticacion exitosa",
    "data": {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id": 1,
            "usuario": "admin",
            "nombre_completo": "Juan Pérez",
            "rol": "administrador",
            "correo": "admin@centro.com",
            "centro": {
                "id": 1,
                "nombre": "Centro Principal",
                "codigo": "CP001",
                "turno": "matutino"
            }
        }
    }
}
```

### 2. Verificar Token
```
GET /api/verify-token
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Token valido",
    "data": {
        "user_id": 1,
        "username": "admin",
        "rol": "administrador",
        "exp": 1640995200,
        "iat": 1640908800
    }
}
```

### 3. Obtener Perfil
```
GET /api/me
```

**Headers:**
```
Authorization: Bearer <token>
```

### 4. Logout
```
POST /api/logout
```

### 5. Centros Disponibles
```
GET /api/centros-disponibles
```

## Implementación Técnica

### 1. Configuración de Seguridad

#### Variables de Entorno
```bash
JWT_SECRET=tu_clave_secreta_muy_fuerte
DB_HOST=localhost
DB_PORT=5432
DB_NAME=centro_tia_glenda
DB_USER=postgres
DB_PASSWORD=password
```

#### Configuración JWT
- **Algoritmo**: HS256
- **Expiración**: 24 horas (configurable)
- **Claims incluidos**: user_id, username, rol, exp, iat

### 2. Estructura de Base de Datos

#### Tablas Principales
```sql
-- Tabla usuarios
usuario (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR UNIQUE NOT NULL,
    contrasenia VARCHAR NOT NULL,
    estado VARCHAR DEFAULT 'activo',
    persona_id INTEGER REFERENCES persona(id),
    rol_id INTEGER REFERENCES rol(id),
    id_centro INTEGER REFERENCES centros(id),
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_ultimo_acceso TIMESTAMP
)

-- Tabla personas (datos personales)
persona (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    apellido VARCHAR NOT NULL,
    correo VARCHAR UNIQUE,
    telefono VARCHAR,
    cedula VARCHAR UNIQUE
)

-- Tabla roles
rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    descripcion TEXT
)

-- Tabla centros
centros (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR NOT NULL,
    codigo VARCHAR UNIQUE,
    turno_principal VARCHAR
)
```

### 3. Implementación del Middleware

#### Token Required
```python
from functools import wraps
from flask import request
from src.utils.general.security import SecurityUtils

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener token del header Authorization
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return response_error("Token de acceso requerido", 401)
        
        # Formato: "Bearer <token>"
        token = auth_header.split(' ')[1]
        
        # Verificar token
        token_result = SecurityUtils.verify_token(token)
        
        if not token_result['success']:
            return response_error(token_result['message'], 401)
        
        # Verificar usuario activo
        user_result = LoginComponent.get_user_by_id(
            token_result['data']['user_id']
        )
        
        if not user_result['success'] or not user_result['data']:
            return response_error("Usuario no encontrado o inactivo", 401)
        
        # Agregar usuario al request
        request.current_user = user_result['data']
        
        return f(*args, **kwargs)
    
    return decorated_function
```

#### Admin Required
```python
def admin_required(f):
    @wraps(f)
    @token_required
    def decorated_function(*args, **kwargs):
        user = request.current_user
        
        if user['rol'].lower() != 'administrador':
            return response_error(
                "Acceso denegado. Se requieren permisos de administrador", 
                403
            )
        
        return f(*args, **kwargs)
    
    return decorated_function
```

### 4. Utilidades de Seguridad

#### Hash de Contraseñas
```python
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(
        password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )
```

#### Generación de Tokens
```python
import jwt
from datetime import datetime, timedelta, timezone

def generate_token(user_data, expires_hours=24):
    secret_key = config.get('secret_jwt')
    now = datetime.now(timezone.utc)
    
    payload = {
        'user_id': user_data['id'],
        'username': user_data['usuario'],
        'rol': user_data['rol'],
        'exp': now + timedelta(hours=expires_hours),
        'iat': now
    }
    
    return jwt.encode(payload, secret_key, algorithm='HS256')
```

## Protección de Endpoints

### Ejemplo de Uso en Rutas
```python
@app.route('/api/usuarios', methods=['GET'])
@admin_required
def get_usuarios():
    # Solo administradores pueden acceder
    pass

@app.route('/api/perfil', methods=['GET'])
@token_required
def get_perfil():
    # Usuario autenticado puede acceder
    user = request.current_user
    pass
```

### Manejo de Errores

#### Códigos de Estado
- **200**: Autenticación exitosa
- **400**: Datos de entrada inválidos
- **401**: Token inválido/expirado o credenciales incorrectas
- **403**: Sin permisos suficientes
- **500**: Error interno del servidor

#### Mensajes de Error
```json
{
    "success": false,
    "message": "Token expirado",
    "data": null
}
```

## Flujo de Autenticación

### 1. Login del Usuario
```
1. Usuario envía credenciales → POST /api/login
2. Sistema valida usuario y contraseña
3. Genera token JWT con datos del usuario
4. Actualiza fecha de último acceso
5. Retorna token y datos del usuario
```

### 2. Acceso a Recursos Protegidos
```
1. Cliente incluye token en header Authorization
2. Middleware extrae y verifica token
3. Valida que usuario siga activo
4. Agrega datos de usuario al request
5. Permite acceso al endpoint
```

### 3. Manejo de Expiración
```
1. Cliente recibe error 401 "Token expirado"
2. Redirige a login para nueva autenticación
3. Usuario ingresa credenciales nuevamente
4. Obtiene nuevo token válido
```

## Consideraciones de Seguridad

### Mejores Prácticas Implementadas
- **Contraseñas hasheadas** con bcrypt y salt único
- **Tokens con expiración** (24 horas por defecto)
- **Validación de usuario activo** en cada request
- **Headers de autorización** estándar (Bearer)
- **Logging detallado** de intentos de autenticación
- **Separación de roles** (usuario/administrador)

### Configuraciones Recomendadas
- Usar HTTPS en producción
- Rotar claves JWT periódicamente
- Implementar rate limiting en /api/login
- Configurar CORS apropiadamente
- Validar entrada de usuario (SQL injection prevention)

## Dependencias

```bash
pip install Flask==2.3.3
pip install PyJWT==2.8.0
pip install bcrypt==4.0.1
pip install psycopg2==2.9.10
```

## Logs y Monitoreo

El sistema registra automáticamente:
- Intentos de login (exitosos/fallidos)
- Verificaciones de token
- Accesos denegados por permisos
- Errores de autenticación

Ubicación: `src/utils/general/LOGS/`

## Testing

Pruebas incluidas para:
- Login con credenciales válidas/inválidas
- Verificación de tokens válidos/expirados
- Acceso con/sin permisos de administrador
- Manejo de errores de conexión BD

Ejecutar: `python tests/test_autenticacion_api.py`