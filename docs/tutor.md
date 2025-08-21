# Módulo de Tutores - Centro Tía Glenda

## Resumen
Módulo que gestiona los tutores o responsables legales de los pacientes, incluyendo información personal, laboral, de contacto y relaciones familiares. Los tutores son fundamentales para el funcionamiento del centro ya que actúan como responsables y punto de contacto principal para los pacientes menores de edad o que requieren acompañamiento.

## Arquitectura del Módulo

### Componentes Principales
- **TutorService**: Lógica de negocio y validaciones
- **TutorComponent**: Acceso a datos y operaciones CRUD
- **Sistema de validaciones**: Control de unicidad y datos obligatorios
- **Integración con personas**: Relación con tabla persona por cédula
- **Control de pacientes**: Gestión de pacientes asignados por tutor

## Estructura de Base de Datos

### Tabla Principal: `tutor`
```sql
CREATE TABLE IF NOT EXISTS tutor (
    id SERIAL PRIMARY KEY,
    
    -- Información personal
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    email VARCHAR(255),
    direccion VARCHAR(255),
    
    -- Relación familiar
    parentesco VARCHAR(50) NOT NULL CHECK (parentesco IN 
        ('padre', 'madre', 'abuelo', 'abuela', 'tio', 'tia', 
         'hermano', 'hermana', 'tutor_legal', 'otro')),
    
    -- Información laboral
    ocupacion VARCHAR(100),
    nombre_empresa VARCHAR(150),
    direccion_empresa VARCHAR(255),
    telefono_empresa VARCHAR(15),
    
    -- Control
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo')),
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    -- Índices para optimización
    INDEX idx_tutor_cedula (cedula),
    INDEX idx_tutor_estado (estado),
    INDEX idx_tutor_parentesco (parentesco)
);
```

### Tipos de Parentesco Soportados
- **padre**: Padre biológico o adoptivo
- **madre**: Madre biológica o adoptiva
- **abuelo**: Abuelo paterno o materno
- **abuela**: Abuela paterna o materna
- **tio**: Tío paterno o materno
- **tia**: Tía paterna o materna
- **hermano**: Hermano mayor responsable
- **hermana**: Hermana mayor responsable
- **tutor_legal**: Tutor legal designado
- **otro**: Otro tipo de relación familiar

### Relaciones con Otros Módulos
```sql
-- Pacientes bajo tutela
paciente.id_tutor → tutor.id

-- Relación con personas (por cédula)
tutor.cedula ↔ persona.cedula (referencia lógica)

-- Sesiones donde participa como responsable
sesion_terapia.observaciones → incluye contacto con tutor
sesion_pedagogica.observaciones → incluye contacto con tutor
```

## Endpoints del API

### 1. Listar Tutores
```
GET /api/tutores
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Lista de tutores obtenida correctamente",
    "data": [
        {
            "id": 1,
            "nombre": "Ana",
            "apellido": "Pérez",
            "nombre_completo": "Ana Pérez",
            "cedula": "1234567890",
            "telefono": "0998765432",
            "email": "ana.perez@email.com",
            "direccion": "Av. Principal #123",
            "parentesco": "madre",
            "ocupacion": "Doctora",
            "nombre_empresa": "Hospital Central",
            "direccion_empresa": "Calle Salud #456",
            "telefono_empresa": "02-234-5678",
            "estado": "activo",
            "fecha_creacion": "2024-01-10T09:15:00",
            "fecha_modificacion": null,
            "total_pacientes": 2,
            "pacientes_activos": 2
        }
    ]
}
```

### 2. Obtener Tutor por ID
```
GET /api/tutores/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Tutor encontrado",
    "data": {
        "id": 1,
        "nombre": "Ana",
        "apellido": "Pérez",
        "nombre_completo": "Ana Pérez",
        "cedula": "1234567890",
        "telefono": "0998765432",
        "email": "ana.perez@email.com",
        "direccion": "Av. Principal #123",
        "parentesco": "madre",
        "ocupacion": "Doctora",
        "nombre_empresa": "Hospital Central",
        "direccion_empresa": "Calle Salud #456",
        "telefono_empresa": "02-234-5678",
        "estado": "activo",
        "fecha_creacion": "2024-01-10T09:15:00",
        "fecha_modificacion": null,
        "pacientes": [
            {
                "id": 1,
                "persona_id": 5,
                "nombre_completo": "María González",
                "nombre": "María",
                "apellido": "González",
                "cedula": "1234567895",
                "fecha_nacimiento": "2015-03-10",
                "fecha_ingreso": "2024-01-15",
                "estado": "activo"
            },
            {
                "id": 3,
                "persona_id": 8,
                "nombre_completo": "Carlos González",
                "nombre": "Carlos",
                "apellido": "González",
                "cedula": "1234567898",
                "fecha_nacimiento": "2012-08-22",
                "fecha_ingreso": "2024-01-18",
                "estado": "activo"
            }
        ]
    }
}
```

### 3. Crear Tutor
```
POST /api/tutores
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "nombre": "Luis",
    "apellido": "Martínez",
    "cedula": "1234567891",
    "telefono": "0987654321",
    "email": "luis.martinez@email.com",
    "direccion": "Calle Segunda #789",
    "parentesco": "padre",
    "ocupacion": "Ingeniero",
    "nombre_empresa": "TechCorp S.A.",
    "direccion_empresa": "Zona Industrial #123",
    "telefono_empresa": "02-345-6789",
    "estado": "activo"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Tutor creado exitosamente",
    "data": {
        "id": 2,
        "nombre": "Luis",
        "apellido": "Martínez",
        "nombre_completo": "Luis Martínez",
        "cedula": "1234567891",
        "telefono": "0987654321",
        "email": "luis.martinez@email.com",
        "direccion": "Calle Segunda #789",
        "parentesco": "padre",
        "ocupacion": "Ingeniero",
        "nombre_empresa": "TechCorp S.A.",
        "direccion_empresa": "Zona Industrial #123",
        "telefono_empresa": "02-345-6789",
        "estado": "activo",
        "fecha_creacion": "2024-01-20T11:30:00",
        "pacientes": []
    }
}
```

### 4. Actualizar Tutor
```
PUT /api/tutores/{id}
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "telefono": "0999888777",
    "email": "nuevo.email@empresa.com",
    "direccion": "Nueva Dirección #456",
    "ocupacion": "Ingeniero Senior",
    "telefono_empresa": "02-999-8888"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Tutor actualizado exitosamente",
    "data": {
        "id": 2,
        "nombre": "Luis",
        "apellido": "Martínez",
        "telefono": "0999888777",
        "email": "nuevo.email@empresa.com",
        "direccion": "Nueva Dirección #456",
        "ocupacion": "Ingeniero Senior",
        "telefono_empresa": "02-999-8888",
        "fecha_modificacion": "2024-01-25T16:45:00"
    }
}
```

### 5. Desactivar Tutor
```
DELETE /api/tutores/{id}
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
    "message": "Tutor desactivado exitosamente",
    "data": null
}
```

### 6. Tutores Activos (Para Combos/Selects)
```
GET /api/tutores/activos
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Tutores activos obtenidos correctamente",
    "data": [
        {
            "id": 1,
            "nombre_completo": "Ana Pérez",
            "nombre": "Ana",
            "apellido": "Pérez",
            "parentesco": "madre",
            "telefono": "0998765432",
            "email": "ana.perez@email.com"
        },
        {
            "id": 2,
            "nombre_completo": "Luis Martínez",
            "nombre": "Luis",
            "apellido": "Martínez",
            "parentesco": "padre",
            "telefono": "0999888777",
            "email": "nuevo.email@empresa.com"
        }
    ]
}
```

### 7. Estadísticas de Tutores
```
GET /api/tutores/estadisticas
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Estadísticas de tutores obtenidas",
    "data": {
        "general": {
            "total_tutores": 15,
            "tutores_activos": 12,
            "tutores_inactivos": 3,
            "promedio_pacientes_por_tutor": 1.8
        },
        "por_parentesco": [
            {
                "parentesco": "madre",
                "total": 8,
                "activos": 7
            },
            {
                "parentesco": "padre",
                "total": 5,
                "activos": 4
            },
            {
                "parentesco": "abuela",
                "total": 2,
                "activos": 1
            }
        ]
    }
}
```

### 8. Personas Disponibles para Tutores
```
GET /api/tutores/personas-disponibles
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Personas disponibles para tutor obtenidas",
    "data": [
        {
            "id": 9,
            "nombre": "Sandra",
            "apellido": "López",
            "nombre_completo": "Sandra López",
            "cedula": "1234567892",
            "telefono": "0987654322",
            "correo": "sandra.lopez@email.com"
        }
    ]
}
```

### 9. Pacientes de un Tutor
```
GET /api/pacientes/tutor/{tutor_id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Pacientes del tutor obtenidos correctamente",
    "data": [
        {
            "id": 1,
            "nombre_completo": "María González",
            "estado": "activo",
            "estado_tratamiento": "activo",
            "fecha_ingreso": "2024-01-15",
            "fecha_nacimiento": "2015-03-10",
            "especialidades": []
        }
    ]
}
```

## Implementación Técnica

### 1. Validaciones de Datos

#### Validación de Tutor
```python
def validate_tutor_data(data, is_update=False):
    """Validar datos completos del tutor"""
    errors = []
    
    # Campos requeridos para crear tutor
    if not is_update:
        required_fields = ['nombre', 'apellido', 'cedula', 'parentesco']
        for field in required_fields:
            if not data.get(field) or not data[field].strip():
                errors.append(f"{field} es requerido")
    
    # Validar nombre
    if 'nombre' in data and data['nombre']:
        nombre = data['nombre'].strip()
        if len(nombre) < 2 or len(nombre) > 100:
            errors.append("Nombre debe tener entre 2 y 100 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$", nombre):
            errors.append("Nombre solo puede contener letras y espacios")
    
    # Validar cédula
    if 'cedula' in data and data['cedula']:
        if not re.match(r"^[0-9]{7,20}$", data['cedula']):
            errors.append("Cédula debe contener solo números (7-20 dígitos)")
    
    # Validar email
    if 'email' in data and data['email']:
        if not validate_email_format(data['email']):
            errors.append("Formato de email inválido")
    
    # Validar parentesco
    if 'parentesco' in data and data['parentesco']:
        valid_parentescos = ['padre', 'madre', 'abuelo', 'abuela', 'tio', 'tia', 
                            'hermano', 'hermana', 'tutor_legal', 'otro']
        if data['parentesco'] not in valid_parentescos:
            errors.append(f"Parentesco debe ser uno de: {', '.join(valid_parentescos)}")
    
    return {'valid': len(errors) == 0, 'message': '; '.join(errors)}
```

### 2. Reglas de Negocio

#### Unicidad de Cédula
```python
def check_cedula_exists(cedula, exclude_id=None):
    """Verificar si ya existe un tutor con la cédula especificada"""
    try:
        if exclude_id:
            query = "SELECT id FROM tutor WHERE cedula = %s AND id != %s"
            params = (cedula, exclude_id)
        else:
            query = "SELECT id FROM tutor WHERE cedula = %s"
            params = (cedula,)
        
        existing = DataBaseHandle.getRecords(query, params, size=1)
        return internal_response(True, existing is not None, "Consulta ejecutada")
        
    except Exception as e:
        HandleLogs.write_error(f"TutorComponent.check_cedula_exists - Error: {str(e)}")
        return internal_response(False, None, f"Error: {str(e)}")
```

#### Restricciones de Eliminación
```python
def deactivate_tutor(tutor_id):
    """No permitir desactivar si tiene pacientes activos"""
    # Verificar si tiene pacientes activos
    patients_check = """
        SELECT COUNT(*) as total 
        FROM paciente 
        WHERE id_tutor = %s AND estado = 'activo'
    """
    active_patients = DataBaseHandle.getRecords(patients_check, (tutor_id,), size=1)
    
    if active_patients and active_patients['total'] > 0:
        return internal_response(False, None,
            f"No se puede desactivar el tutor porque tiene {active_patients['total']} paciente(s) activo(s)")
    
    # Proceder con desactivación
```

### 3. Estructura del Servicio

#### TutorService (Capa de Lógica)
```python
class TutorService:
    
    @staticmethod
    def create_tutor():
        # 1. Obtener y validar datos
        data = request.get_json()
        validation_result = Validators.validate_tutor_data(data, is_update=False)
        
        if not validation_result['valid']:
            return response_error(validation_result['message'], 400)
        
        # 2. Preparar datos para inserción
        tutor_data = {
            'nombre': data['nombre'].strip(),
            'apellido': data['apellido'].strip(),
            'cedula': data['cedula'].strip(),
            'telefono': data.get('telefono', '').strip(),
            'email': data.get('email', '').strip(),
            'direccion': data.get('direccion', '').strip(),
            'parentesco': data['parentesco'],
            'ocupacion': data.get('ocupacion', '').strip(),
            'direccion_empresa': data.get('direccion_empresa', '').strip(),
            'telefono_empresa': data.get('telefono_empresa', '').strip(),
            'nombre_empresa': data.get('nombre_empresa', '').strip(),
            'estado': data.get('estado', 'activo'),
            'usuario_creacion': getattr(request, 'current_user', {}).get('id', 1)
        }
        
        # 3. Delegar a componente
        result = TutorComponent.create_tutor(tutor_data)
        
        # 4. Retornar respuesta
        if result['success']:
            return response_inserted(result['data'], "Tutor creado exitosamente")
        else:
            return response_error(result['message'], 400)
```

#### TutorComponent (Capa de Datos)
```python
class TutorComponent:
    
    @staticmethod
    def create_tutor(data):
        try:
            # Verificar unicidad de cédula
            cedula_check = DataBaseHandle.getRecords(
                "SELECT id FROM tutor WHERE cedula = %s",
                (data['cedula'],), size=1
            )
            if cedula_check:
                return internal_response(False, None, "Ya existe un tutor con esta cédula")
            
            # Insertar nuevo tutor
            insert_query = """
                INSERT INTO tutor (
                    nombre, apellido, cedula, telefono, email, direccion,
                    parentesco, ocupacion, direccion_empresa, telefono_empresa,
                    nombre_empresa, estado, usuario_creacion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
            
            new_id = DataBaseHandle.ExecuteInsert(insert_query, params)
            
            if new_id:
                new_tutor = TutorComponent.get_tutor_by_id(new_id)
                return internal_response(True, new_tutor['data'], "Tutor creado exitosamente")
            
        except Exception as e:
            return internal_response(False, None, f"Error: {str(e)}")
```

### 4. Consultas SQL Principales

#### Tutores con Información de Pacientes
```sql
SELECT 
    t.id,
    t.nombre,
    t.apellido,
    CONCAT(t.nombre, ' ', t.apellido) as nombre_completo,
    t.cedula,
    t.telefono,
    t.email,
    t.direccion,
    t.parentesco,
    t.ocupacion,
    t.direccion_empresa,
    t.telefono_empresa,
    t.nombre_empresa,
    t.estado,
    t.fecha_creacion,
    t.fecha_modificacion,
    COUNT(pac.id) as total_pacientes,
    COUNT(CASE WHEN pac.estado = 'activo' THEN 1 END) as pacientes_activos
FROM tutor t
LEFT JOIN paciente pac ON t.id = pac.id_tutor
GROUP BY t.id, t.nombre, t.apellido, t.cedula, t.telefono, t.email, 
         t.direccion, t.parentesco, t.ocupacion, t.direccion_empresa,
         t.telefono_empresa, t.nombre_empresa, t.estado, 
         t.fecha_creacion, t.fecha_modificacion
ORDER BY t.nombre, t.apellido;
```

#### Pacientes de un Tutor
```sql
SELECT 
    pac.id,
    pac.fecha_ingreso,
    pac.estado,
    pac.codigo_paciente,
    pp.id as persona_id,
    CONCAT(pp.nombre, ' ', pp.apellido) as nombre_completo,
    pp.nombre,
    pp.apellido,
    pp.cedula,
    pp.fecha_nacimiento
FROM paciente pac
INNER JOIN persona pp ON pac.persona_id = pp.id
WHERE pac.id_tutor = %s
ORDER BY pp.nombre, pp.apellido;
```

#### Estadísticas por Parentesco
```sql
SELECT 
    parentesco,
    COUNT(*) as total,
    COUNT(CASE WHEN estado = 'activo' THEN 1 END) as activos
FROM tutor
GROUP BY parentesco
ORDER BY total DESC;
```

## Casos de Uso y Flujos

### 1. Registro de Nuevo Tutor
```
1. Administrador/Usuario crea tutor → POST /api/tutores
2. Sistema valida datos obligatorios y formatos
3. Verifica unicidad de cédula
4. Valida parentesco contra lista permitida
5. Inserta en base de datos
6. Tutor disponible para asignar a pacientes
```

### 2. Asignación de Tutor a Paciente
```
1. Al crear paciente → POST /api/pacientes
2. Frontend obtiene tutores activos → GET /api/tutores/activos
3. Usuario selecciona tutor de la lista
4. Sistema valida tutor activo y crea relación
5. Paciente queda bajo responsabilidad del tutor
```

### 3. Gestión de Información de Contacto
```
1. Actualizar datos de contacto → PUT /api/tutores/{id}
2. Sistema valida nuevos datos
3. Actualiza información personal y laboral
4. Cambios reflejados en comunicaciones con pacientes
5. Logs registro de modificación
```

### 4. Desactivación de Tutor
```
1. Administrador intenta desactivar → DELETE /api/tutores/{id}
2. Sistema verifica no tenga pacientes activos
3. Si tiene pacientes activos, bloquea desactivación
4. Si no tiene pacientes, cambia estado a inactivo
5. Tutor no aparece en listas de selección
```

## Integración con Otros Módulos

### Con Pacientes
- **Responsabilidad**: Cada paciente tiene un tutor asignado
- **Comunicación**: Punto de contacto principal para el centro
- **Restricción**: No se puede desactivar tutor con pacientes activos

### Con Personas
- **Relación lógica**: Conexión por cédula (no FK directa)
- **Disponibilidad**: Personas sin tutor aparecen como disponibles
- **Validación**: Previene duplicación por cédula

### Con Sesiones
- **Contacto**: Información de tutor en sesiones terapéuticas
- **Comunicación**: Reportes y seguimiento a tutores
- **Participación**: Involucrados en el progreso del paciente

### Con Centros
- **Indirecto**: A través de pacientes asignados
- **Filtrado**: Tutores visibles según centro del usuario
- **Comunicación**: Contacto localizado por centro

## Validaciones y Restricciones

### Campos Obligatorios
- **nombre**: 2-100 caracteres, solo letras y espacios
- **apellido**: 2-100 caracteres, solo letras y espacios
- **cedula**: 7-20 dígitos, solo números, único
- **parentesco**: Debe estar en lista predefinida

### Campos Opcionales
- **telefono**: 8-15 dígitos para contacto
- **email**: Formato email válido
- **direccion**: Hasta 255 caracteres
- **ocupacion**: Información laboral
- **datos_empresa**: Información laboral completa

### Reglas de Negocio
- **Unicidad de cédula**: No duplicación de identidades
- **Estados válidos**: activo, inactivo
- **Eliminación protegida**: No desactivar con pacientes activos
- **Parentescos válidos**: Solo relaciones familiares definidas

### Códigos de Error
- **400**: Datos inválidos, cédula duplicada, validación fallida
- **401**: Token requerido o inválido
- **403**: Sin permisos de administrador (para eliminar)
- **404**: Tutor no encontrado
- **409**: Cédula duplicada, tutor con pacientes activos
- **500**: Error interno del servidor

## Configuración y Dependencias

### Variables de Entorno
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=centro_tia_glenda
```

### Librerías Requeridas
```bash
pip install email-validator==2.1.0
pip install validators==0.22.0
```

## Logging y Auditoría

El sistema registra:
- Creación de tutores nuevos
- Modificaciones de datos de contacto
- Intentos de desactivación
- Consultas de tutores disponibles
- Errores de validación y duplicación
- Asignaciones a pacientes

Ubicación: `src/utils/general/LOGS/`

## Testing

Pruebas incluidas para:
- CRUD completo de tutores
- Validación de campos obligatorios
- Verificación de unicidad de cédula
- Restricciones de eliminación con pacientes
- Consultas de tutores activos
- Estadísticas por parentesco

Ejecutar: `python tests/test_tutores_api.py`

## Consideraciones de Seguridad

### Control de Acceso
- **Consulta**: Cualquier usuario autenticado puede ver tutores
- **Modificación**: Cualquier usuario puede crear/actualizar
- **Eliminación**: Solo administradores pueden desactivar

### Protección de Datos
- **Eliminación lógica**: Preservación de datos históricos
- **Validación de entrada**: Prevención de inyección SQL
- **Logs detallados**: Auditoría de cambios sin datos sensibles

### Integridad de Datos
- **Unicidad garantizada**: Prevención de duplicación por cédula
- **Referencias válidas**: Validación antes de desactivar
- **Estados consistentes**: Control de transiciones de estado

## Limitaciones Actuales

### Parentescos Fijos
- **Lista predefinida**: Solo parentescos en el sistema
- **Sin personalización**: No permite parentescos personalizados
- **Un parentesco**: Solo una relación por tutor

### Información Laboral Básica
- **Campos simples**: Información laboral limitada
- **Sin validación empresarial**: No verifica existencia de empresas
- **Un empleo**: Solo una empresa por tutor

### Comunicación
- **Sin notificaciones**: No alertas automáticas a tutores
- **Sin portal**: No acceso directo del tutor al sistema
- **Comunicación manual**: Contacto solo por teléfono/email

## Recomendaciones de Mejora

### Futuras Implementaciones
1. **Portal de tutores**: Acceso web para seguimiento de pacientes
2. **Notificaciones automáticas**: SMS/email de citas y progresos
3. **Múltiples contactos**: Varios números y emails por tutor
4. **Documentos digitales**: Subida de documentos de identificación
5. **Calendario compartido**: Coordinación de citas con tutores
6. **Chat integrado**: Comunicación directa con personal del centro
7. **Historial de comunicaciones**: Registro de contactos realizados
8. **Autorización digital**: Consentimientos y autorizaciones en línea
9. **Geolocalización**: Ubicación para emergencias
10. **Múltiples tutores**: Varios responsables por paciente
11. **Jerarquía de contacto**: Orden de prioridad en comunicaciones
12. **Integración con calendarios**: Sincronización con Google/Outlook

## Casos de Uso Específicos

### Comunicación de Emergencia
```
1. Personal identifica emergencia con paciente
2. Sistema obtiene datos de tutor → GET /api/tutores/{id}
3. Contacto inmediato por teléfono principal
4. Si no responde, usar teléfono empresa
5. Registro de comunicación en logs del sistema
```

### Seguimiento de Progreso
```
1. Terapeuta completa sesión con paciente
2. Sistema identifica tutor del paciente
3. Genera reporte de progreso automático
4. Envío de información a email del tutor
5. Tutor recibe actualización del tratamiento
```

### Coordinación de Citas
```
1. Personal programa nueva sesión
2. Sistema consulta disponibilidad de paciente
3. Notificación automática a tutor por email/SMS
4. Confirmación o reprogramación según respuesta
5. Actualización en calendario del centro
```