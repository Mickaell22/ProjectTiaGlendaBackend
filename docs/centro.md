# Módulo de Centros - Centro Tía Glenda

## Resumen
Módulo que gestiona la información de los centros médicos del sistema, incluyendo sus configuraciones, horarios, turnos y asignaciones de personal. Define las sedes físicas donde se prestan los servicios y controla el acceso de usuarios según su centro asignado.

## Arquitectura del Módulo

### Componentes Principales
- **CentroService**: Lógica de negocio y validaciones
- **CentroComponent**: Acceso a datos y operaciones de consulta
- **Middleware de centros**: Control de acceso por centro asignado
- **Integración con login**: Selector de centros en autenticación
- **Sistema de estadísticas**: Métricas por centro

## Estructura de Base de Datos

### Tabla Principal: `centros`
```sql
CREATE TABLE IF NOT EXISTS centros (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(10) NOT NULL UNIQUE, -- NORTE/SUR
    direccion VARCHAR(255),
    telefono VARCHAR(15),
    email VARCHAR(150),
    
    -- Configuración de horarios
    horario_apertura TIME DEFAULT '07:00',
    horario_cierre TIME DEFAULT '18:00',
    
    -- Configuración de turnos
    turno_principal VARCHAR(20) DEFAULT 'mixto' CHECK (turno_principal IN ('matutino', 'vespertino', 'mixto')),
    
    -- Estado y control
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'mantenimiento')),
    observaciones TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);
```

### Centros Predefinidos del Sistema
```sql
-- Centro Norte (Matutino)
INSERT INTO centros (nombre, codigo, direccion, telefono, email, horario_apertura, horario_cierre, turno_principal, observaciones) VALUES 
('Centro Norte', 'NORTE', 'Av. Principal Norte #123, Sector Norte', '02-234-5678', 'norte@centrotiaglenda.com', '07:00', '15:00', 'matutino', 'Centro especializado en atención matutina');

-- Centro Sur (Vespertino)
INSERT INTO centros (nombre, codigo, direccion, telefono, email, horario_apertura, horario_cierre, turno_principal, observaciones) VALUES 
('Centro Sur', 'SUR', 'Calle Central Sur #456, Sector Sur', '02-345-6789', 'sur@centrotiaglenda.com', '13:00', '19:00', 'vespertino', 'Centro especializado en atención vespertina');
```

### Relaciones con Otros Módulos
```sql
-- Usuarios asignados a centros
usuario.id_centro → centros.id

-- Personal asignado a centros
personal.id_centro → centros.id

-- Pacientes asignados a centros
paciente.id_centro → centros.id

-- Sesiones realizadas en centros
sesion_terapia.id_centro → centros.id
sesion_pedagogica.id_centro → centros.id
```

## Características de los Centros

### 1. Centro Norte
**Configuración:**
- **Código**: NORTE
- **Turno**: Matutino (07:00 - 15:00)
- **Especialización**: Atención matutina
- **Ubicación**: Sector Norte de la ciudad

**Servicios:**
- Sesiones terapéuticas matutinas
- Clases pedagógicas de mañana
- Personal especializado en horario matutino
- Atención temprana para niños

### 2. Centro Sur
**Configuración:**
- **Código**: SUR
- **Turno**: Vespertino (13:00 - 19:00)
- **Especialización**: Atención vespertina
- **Ubicación**: Sector Sur de la ciudad

**Servicios:**
- Sesiones terapéuticas vespertinas
- Clases pedagógicas de tarde
- Personal especializado en horario vespertino
- Atención después de horarios escolares

## Endpoints del API

### 1. Centros Disponibles para Login
```
GET /api/centros-disponibles
```

**Headers:** Ninguno (Endpoint público)

**Response:**
```json
{
    "success": true,
    "message": "Centros para login obtenidos exitosamente",
    "data": [
        {
            "id": 13,
            "nombre": "Centro Norte",
            "codigo": "NORTE",
            "turno_principal": "matutino"
        },
        {
            "id": 14,
            "nombre": "Centro Sur",
            "codigo": "SUR",
            "turno_principal": "vespertino"
        }
    ]
}
```

### 2. Información Completa de Centros (Interno)
```
GET /api/centros (Endpoint interno - no expuesto públicamente)
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Centros obtenidos exitosamente",
    "data": [
        {
            "id": 13,
            "nombre": "Centro Norte",
            "codigo": "NORTE",
            "direccion": "Av. Principal Norte #123, Sector Norte",
            "telefono": "02-234-5678",
            "email": "norte@centrotiaglenda.com",
            "turno_principal": "matutino",
            "horario_apertura": "07:00:00",
            "horario_cierre": "15:00:00",
            "estado": "activo",
            "observaciones": "Centro especializado en atención matutina"
        },
        {
            "id": 14,
            "nombre": "Centro Sur",
            "codigo": "SUR",
            "direccion": "Calle Central Sur #456, Sector Sur",
            "telefono": "02-345-6789",
            "email": "sur@centrotiaglenda.com",
            "turno_principal": "vespertino",
            "horario_apertura": "13:00:00",
            "horario_cierre": "19:00:00",
            "estado": "activo",
            "observaciones": "Centro especializado en atención vespertina"
        }
    ]
}
```

### 3. Obtener Centro por ID (Interno)
```
GET /api/centros/{id} (Endpoint interno)
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Centro encontrado exitosamente",
    "data": {
        "id": 13,
        "nombre": "Centro Norte",
        "codigo": "NORTE",
        "direccion": "Av. Principal Norte #123, Sector Norte",
        "telefono": "02-234-5678",
        "email": "norte@centrotiaglenda.com",
        "turno_principal": "matutino",
        "horario_apertura": "07:00:00",
        "horario_cierre": "15:00:00",
        "estado": "activo",
        "observaciones": "Centro especializado en atención matutina"
    }
}
```

### 4. Obtener Centro por Código (Interno)
```
GET /api/centros/codigo/{codigo} (Endpoint interno)
```

**Parámetros:**
- `codigo`: NORTE o SUR

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Centro encontrado exitosamente",
    "data": {
        "id": 14,
        "nombre": "Centro Sur",
        "codigo": "SUR",
        "direccion": "Calle Central Sur #456, Sector Sur",
        "telefono": "02-345-6789",
        "email": "sur@centrotiaglenda.com",
        "turno_principal": "vespertino",
        "horario_apertura": "13:00:00",
        "horario_cierre": "19:00:00",
        "estado": "activo",
        "observaciones": "Centro especializado en atención vespertina"
    }
}
```

### 5. Validar Acceso de Usuario a Centro (Interno)
```
GET /api/centros/{centro_id}/validar-usuario/{user_id} (Endpoint interno)
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Usuario tiene acceso al centro",
    "data": {
        "id": 2,
        "id_centro": 13,
        "centro_nombre": "Centro Norte",
        "centro_codigo": "NORTE"
    }
}
```

### 6. Estadísticas de Centro (Interno)
```
GET /api/centros/{centro_id}/estadisticas (Endpoint interno)
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Estadísticas obtenidas exitosamente",
    "data": {
        "total_usuarios": 8,
        "total_personal": 5,
        "total_pacientes": 25,
        "total_sesiones_terapia": 45,
        "total_sesiones_pedagogicas": 12
    }
}
```

## Implementación Técnica

### 1. Servicio de Centros

#### CentroService
```python
class CentroService:
    
    @staticmethod
    def get_all_centros():
        """Obtener todos los centros activos"""
        try:
            result = CentroComponent.get_all_centros()
            
            if result["success"]:
                return {
                    "success": True,
                    "data": result["data"],
                    "message": "Centros obtenidos exitosamente"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "Error al obtener centros"
                }
                
        except Exception as e:
            HandleLogs.write_error(f"CentroService.get_all_centros - Error: {str(e)}")
            return {
                "success": False,
                "data": None,
                "message": f"Error del servicio: {str(e)}"
            }
    
    @staticmethod
    def get_centros_for_login():
        """Datos simplificados para selector de login"""
        try:
            result = CentroComponent.get_all_centros()
            
            if result["success"]:
                # Simplificar datos para el selector de login
                centros_login = []
                for centro in result["data"]:
                    centros_login.append({
                        "id": centro["id"],
                        "nombre": centro["nombre"],
                        "codigo": centro["codigo"],
                        "turno_principal": centro["turno_principal"]
                    })
                
                return {
                    "success": True,
                    "data": centros_login,
                    "message": "Centros para login obtenidos exitosamente"
                }
```

### 2. Validaciones de Acceso

#### Validación de Centro por Usuario
```python
def validate_user_centro_access(user_id, centro_id):
    """Verificar que usuario tenga acceso al centro especificado"""
    try:
        query = """
        SELECT 
            u.id,
            u.id_centro,
            c.nombre as centro_nombre,
            c.codigo as centro_codigo
        FROM usuario u
        INNER JOIN centros c ON u.id_centro = c.id
        WHERE u.id = %s AND u.id_centro = %s AND u.estado = 'activo' AND c.estado = 'activo'
        """
        
        access = DataBaseHandle.getRecords(query, (user_id, centro_id), size=1)
        
        return internal_response(True, access, "Validación completada")
        
    except Exception as e:
        HandleLogs.write_error(f"CentroComponent.validate_user_centro_access - Error: {str(e)}")
        return internal_response(False, None, f"Error: {str(e)}")
```

#### Validación de Códigos
```python
def validate_centro_codigo(codigo):
    """Validar código de centro"""
    if not codigo or codigo.strip() == "":
        return {
            "success": False,
            "message": "Código de centro requerido"
        }
    
    codigo = codigo.upper().strip()
    if codigo not in ["NORTE", "SUR"]:
        return {
            "success": False,
            "message": "Código de centro inválido. Debe ser NORTE o SUR"
        }
    
    return {"success": True, "codigo": codigo}
```

### 3. Integración con Autenticación

#### Selector de Centros en Login
```python
# En LoginService.get_centros_disponibles()
def get_centros_disponibles():
    """Centros disponibles para selector de login"""
    try:
        HandleLogs.write_log("LoginService.get_centros_disponibles - Solicitando centros para login")
        
        result = CentroService.get_centros_for_login()
        
        if result["success"]:
            return response_success(result["data"], result["message"])
        else:
            return response_error(result["message"], 500)
            
    except Exception as e:
        HandleLogs.write_error(f"LoginService.get_centros_disponibles - Error: {str(e)}")
        return response_error("Error obteniendo centros disponibles", 500)
```

#### Centro en Token JWT
```python
# El centro se incluye en el token JWT del usuario
token_data = {
    'user_id': user['id'],
    'username': user['usuario'],
    'rol': user['rol'],
    'centro_id': user['id_centro'],
    'centro_codigo': user['centro_codigo'],
    'centro_nombre': user['centro_nombre']
}
```

### 4. Consultas SQL Principales

#### Centros Activos
```sql
SELECT 
    id,
    nombre,
    codigo,
    direccion,
    telefono,
    email,
    turno_principal,
    horario_apertura,
    horario_cierre,
    estado,
    observaciones
FROM centros
WHERE estado = 'activo'
ORDER BY nombre ASC;
```

#### Estadísticas por Centro
```sql
SELECT 
    (SELECT COUNT(*) FROM usuario WHERE id_centro = %s AND estado = 'activo') as total_usuarios,
    (SELECT COUNT(*) FROM personal WHERE id_centro = %s AND estado = 'activo') as total_personal,
    (SELECT COUNT(*) FROM paciente WHERE id_centro = %s AND estado = 'activo') as total_pacientes,
    (SELECT COUNT(*) FROM sesion_terapia WHERE id_centro = %s AND estado = 'activo') as total_sesiones_terapia,
    (SELECT COUNT(*) FROM sesion_pedagogica WHERE id_centro = %s AND estado = 'activo') as total_sesiones_pedagogicas;
```

#### Validación de Acceso Usuario-Centro
```sql
SELECT 
    u.id,
    u.id_centro,
    c.nombre as centro_nombre,
    c.codigo as centro_codigo
FROM usuario u
INNER JOIN centros c ON u.id_centro = c.id
WHERE u.id = %s AND u.id_centro = %s AND u.estado = 'activo' AND c.estado = 'activo';
```

## Casos de Uso y Flujos

### 1. Selección de Centro en Login
```
1. Usuario accede al login → Frontend carga centros disponibles
2. Sistema consulta → GET /api/centros-disponibles
3. Usuario selecciona centro de preferencia
4. Frontend incluye centro_id en request de login
5. Sistema valida centro y genera token con información del centro
6. Usuario autenticado ve solo datos de su centro asignado
```

### 2. Control de Acceso por Centro
```
1. Usuario intenta acceder a datos de otro centro
2. Middleware extrae centro_id del token JWT
3. Compara con centro solicitado en la operación
4. Permite solo acceso a datos del centro asignado
5. Deniega acceso cruzado entre centros
```

### 3. Estadísticas por Centro
```
1. Administrador solicita estadísticas de su centro
2. Sistema consulta conteos por módulo (usuarios, personal, pacientes, sesiones)
3. Filtra solo datos del centro asignado al usuario
4. Retorna métricas específicas del centro
```

## Integración con Otros Módulos

### Con Usuarios
- **Asignación**: usuario.id_centro define el centro del usuario
- **Token JWT**: Centro incluido en token para control de acceso
- **Login**: Selector de centro en proceso de autenticación

### Con Personal
- **Asignación**: personal.id_centro define donde trabaja
- **Centro por defecto**: ID=13 (Centro Norte) si no se especifica
- **Filtrado**: Personal por centro específico

### Con Pacientes
- **Asignación**: paciente.id_centro define donde recibe atención
- **Servicios**: Pacientes atendidos según centro asignado
- **Horarios**: Respeta horarios del centro correspondiente

### Con Sesiones
- **Terapéuticas**: sesion_terapia.id_centro define ubicación
- **Pedagógicas**: sesion_pedagogica.id_centro define ubicación
- **Cronogramas**: Generados según horarios del centro
- **Personal disponible**: Filtrado por centro de la sesión

### Con Middleware de Seguridad
- **Centro middleware**: Valida acceso según centro asignado
- **Filtrado automático**: Solo datos del centro del usuario
- **Logs por centro**: Auditoría separada por centro

## Configuración de Centros

### Estados Válidos
- **activo**: Centro operativo y funcional
- **inactivo**: Centro cerrado temporalmente
- **mantenimiento**: Centro en mantenimiento programado

### Turnos Configurables
- **matutino**: Atención de mañana (07:00 - 15:00)
- **vespertino**: Atención de tarde (13:00 - 19:00)
- **mixto**: Atención todo el día

### Horarios Personalizables
```sql
-- Configuración por centro
horario_apertura TIME DEFAULT '07:00'
horario_cierre TIME DEFAULT '18:00'
```

## Validaciones y Restricciones

### Códigos de Centro
- **Únicos**: NORTE, SUR (no pueden duplicarse)
- **Formato**: Mayúsculas, sin espacios
- **Validación**: Solo códigos predefinidos permitidos

### Estados
- **Transiciones válidas**: activo ↔ inactivo ↔ mantenimiento
- **Restricciones**: No eliminar centros con usuarios activos
- **Validación**: Centro debe estar activo para nuevas asignaciones

### Horarios
- **Formato**: HH:MM (24 horas)
- **Validación**: horario_apertura < horario_cierre
- **Turnos coherentes**: Horarios deben coincidir con turno_principal

## Consideraciones de Seguridad

### Control de Acceso
- **Aislamiento por centro**: Usuarios solo ven datos de su centro
- **Validación en middleware**: Verificación automática en cada request
- **Token JWT**: Centro incluido para validación sin consulta BD

### Auditoría
- **Logs por centro**: Separación de logs por centro
- **Usuario responsable**: Registro de cambios por usuario
- **Accesos cruzados**: Log de intentos de acceso no autorizado

### Integridad de Datos
- **Referencias válidas**: Verificación de centro activo en asignaciones
- **Consistencia**: Horarios coherentes con turnos
- **Estados consistentes**: Validación de transiciones de estado

## Limitaciones Actuales

### Centros Fijos
- **Solo dos centros**: Norte y Sur predefinidos
- **No creación dinámica**: Centros definidos en scripts de BD
- **Códigos fijos**: NORTE/SUR no configurables

### Horarios Simples
- **Un horario por centro**: No maneja horarios diferentes por día
- **Sin excepciones**: No horarios especiales por fechas
- **Turnos básicos**: Solo matutino/vespertino/mixto

## Recomendaciones de Mejora

### Futuras Implementaciones
1. **Gestión de centros**: CRUD completo para crear/modificar centros
2. **Horarios avanzados**: Horarios diferentes por día de semana
3. **Calendario de excepciones**: Horarios especiales por fechas
4. **Multi-sede para usuarios**: Usuarios con acceso a múltiples centros
5. **Configuración de servicios**: Servicios específicos por centro
6. **Geolocalización**: Coordenadas GPS para ubicación
7. **Capacidades por centro**: Límites de pacientes/personal por centro
8. **Reportes comparativos**: Estadísticas entre centros
9. **Centro virtual**: Soporte para telemedicina/servicios remotos
10. **Jerarquía de centros**: Centros principales con sub-sedes