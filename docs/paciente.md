# Módulo de Pacientes - Centro Tía Glenda

## Resumen
Módulo que gestiona los pacientes del centro médico, incluyendo sus datos personales, especialidades múltiples, estados de tratamiento, documentos médicos y relaciones con tutores. Permite el manejo completo del historial clínico y seguimiento de tratamientos.

## Arquitectura del Módulo

### Componentes Principales
- **PacienteService**: Lógica de negocio y validaciones
- **PacienteComponent**: Acceso a datos y operaciones CRUD
- **DocumentoPacienteService**: Gestión de documentos médicos
- **Sistema de especialidades múltiples**: Gestión de tratamientos diversos
- **Control de estados**: Manejo de pausas y reactivaciones
- **Middleware**: Protección y control de acceso por centro

## Estructura de Base de Datos

### Tabla Principal: `paciente`
```sql
CREATE TABLE IF NOT EXISTS paciente (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL,
    id_tutor INTEGER NOT NULL,
    fecha_ingreso DATE NOT NULL,
    motivo_consulta TEXT,
    
    -- Control de tratamiento general
    estado_tratamiento VARCHAR(20) DEFAULT 'activo' CHECK (estado_tratamiento IN 
        ('activo', 'pausado', 'completado', 'derivado', 'alta')),
    fecha_inicio_tratamiento DATE,
    fecha_fin_tratamiento DATE,
    
    -- Pausas generales
    fecha_inicio_pausa_general DATE,
    fecha_fin_pausa_general DATE,
    motivo_pausa_general TEXT,
    observaciones_pausa_general TEXT,
    
    -- Estado del paciente
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN 
        ('activo', 'inactivo', 'alta', 'derivado', 'eliminado', 'pausado')),
    
    observaciones TEXT,
    id_centro INTEGER NOT NULL DEFAULT 13,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (persona_id) REFERENCES persona(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_tutor) REFERENCES tutor(id) ON DELETE RESTRICT,
    FOREIGN KEY (id_centro) REFERENCES centros(id) ON DELETE RESTRICT
);
```

### Tabla de Especialidades Múltiples: `paciente_especialidades`
```sql
CREATE TABLE IF NOT EXISTS paciente_especialidades (
    id SERIAL PRIMARY KEY,
    id_paciente INTEGER NOT NULL,
    id_especialidad INTEGER NOT NULL,
    
    -- Control de especialidad
    es_principal BOOLEAN DEFAULT FALSE,
    fecha_asignacion DATE DEFAULT CURRENT_DATE,
    fecha_inicio_tratamiento DATE,
    fecha_fin_tratamiento DATE,
    
    -- Estados específicos por especialidad
    estado_tratamiento VARCHAR(20) DEFAULT 'activo' CHECK (estado_tratamiento IN 
        ('activo', 'pausado', 'completado', 'suspendido')),
    
    -- Pausas específicas por especialidad
    fecha_inicio_pausa DATE,
    fecha_fin_pausa DATE,
    motivo_pausa TEXT,
    observaciones_pausa TEXT,
    
    observaciones TEXT,
    estado VARCHAR(10) DEFAULT 'activo' CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE CASCADE,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id) ON DELETE RESTRICT,
    
    -- Constraint para evitar duplicados
    UNIQUE (id_paciente, id_especialidad)
);
```

### Tabla de Documentos: `documentos_pacientes`
```sql
CREATE TABLE IF NOT EXISTS documentos_pacientes (
    id SERIAL PRIMARY KEY,
    id_paciente INTEGER NOT NULL,
    
    -- Información del archivo
    nombre_archivo VARCHAR(255) NOT NULL,
    nombre_original VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    tamaño_archivo INTEGER,
    tipo_mime VARCHAR(100),
    
    -- Clasificación del documento
    tipo_documento VARCHAR(50) NOT NULL CHECK (tipo_documento IN 
        ('general', 'historia_clinica', 'examenes_medicos', 'consentimientos', 
         'reportes_terapia', 'evaluaciones', 'otros')),
    
    descripcion TEXT,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento DATE,
    
    -- Control de acceso
    es_confidencial BOOLEAN DEFAULT FALSE,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER,
    
    FOREIGN KEY (id_paciente) REFERENCES paciente(id) ON DELETE CASCADE
);
```

### Relaciones con Otros Módulos
```sql
-- Datos personales base
paciente.persona_id → persona.id

-- Tutor responsable
paciente.id_tutor → tutor.id

-- Centro de atención
paciente.id_centro → centros.id

-- Especialidades múltiples
paciente_especialidades.id_paciente → paciente.id
paciente_especialidades.id_especialidad → especialidad.id

-- Sesiones de tratamiento
sesion_terapia.id_paciente → paciente.id
sesion_pedagogica.id_paciente → paciente.id
```

## Estados del Paciente

### Estados Generales
- **activo**: Paciente en tratamiento regular
- **inactivo**: Paciente temporalmente inactivo
- **pausado**: Pausa general de todos los tratamientos
- **alta**: Paciente dado de alta médica
- **derivado**: Paciente derivado a otra institución
- **eliminado**: Eliminación lógica del registro

### Estados de Tratamiento
- **activo**: Tratamiento en curso
- **pausado**: Tratamiento pausado temporalmente
- **completado**: Tratamiento finalizado exitosamente
- **derivado**: Derivado a otro profesional/centro
- **alta**: Alta médica del tratamiento

### Estados por Especialidad
- **activo**: Especialidad en tratamiento
- **pausado**: Especialidad pausada temporalmente
- **completado**: Tratamiento de especialidad finalizado
- **suspendido**: Especialidad suspendida por motivos médicos

## Endpoints del API

### 1. Listar Pacientes
```
GET /api/pacientes
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Lista de pacientes obtenida correctamente",
    "data": [
        {
            "id": 1,
            "fecha_ingreso": "2024-01-15",
            "estado_tratamiento": "activo",
            "observaciones": "Paciente colaborativo",
            "estado": "activo",
            "fecha_creacion": "2024-01-15T10:30:00",
            "persona_id": 5,
            "nombre_completo": "María González",
            "nombre": "María",
            "apellido": "González",
            "cedula": "1234567895",
            "telefono": "0987654325",
            "correo": "maria.gonzalez@email.com",
            "fecha_nacimiento": "2015-03-10",
            "tutor_id": 1,
            "parentesco": "madre",
            "nombre_tutor": "Ana Pérez",
            "telefono_tutor": "0998765432",
            "correo_tutor": "ana.perez@email.com",
            "especialidades": [
                {
                    "id": 1,
                    "nombre": "Terapia del Lenguaje",
                    "area": "Especialidad terapéutica",
                    "estado_tratamiento": "activo",
                    "es_principal": true,
                    "fecha_asignacion": "2024-01-15"
                }
            ],
            "total_especialidades": 1,
            "especialidades_activas": 1
        }
    ]
}
```

### 2. Obtener Paciente por ID
```
GET /api/pacientes/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Paciente encontrado",
    "data": {
        "id": 1,
        "fecha_ingreso": "2024-01-15",
        "estado_tratamiento": "activo",
        "observaciones": "Paciente colaborativo",
        "estado": "activo",
        "persona_id": 5,
        "nombre_completo": "María González",
        "nombre": "María",
        "apellido": "González",
        "cedula": "1234567895",
        "telefono": "0987654325",
        "correo": "maria.gonzalez@email.com",
        "fecha_nacimiento": "2015-03-10",
        "tutor_id": 1,
        "parentesco": "madre",
        "nombre_tutor": "Ana Pérez",
        "telefono_tutor": "0998765432",
        "correo_tutor": "ana.perez@email.com",
        "especialidades": [
            {
                "id": 1,
                "nombre": "Terapia del Lenguaje",
                "area": "Especialidad terapéutica",
                "estado_tratamiento": "activo",
                "es_principal": true,
                "fecha_asignacion": "2024-01-15"
            }
        ]
    }
}
```

### 3. Crear Paciente
```
POST /api/pacientes
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "persona_id": 6,
    "tutor_id": 2,
    "fecha_ingreso": "2024-01-20",
    "especialidad_id": 2,
    "fecha_inicio_tratamiento": "2024-01-22",
    "estado_tratamiento": "activo",
    "observaciones_tratamiento": "Inicio de terapia ocupacional",
    "observaciones": "Paciente requiere atención especializada"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Paciente creado exitosamente",
    "data": {
        "id": 2,
        "persona_id": 6,
        "nombre_completo": "Pedro Martínez",
        "tutor_id": 2,
        "nombre_tutor": "Luis Martínez",
        "fecha_ingreso": "2024-01-20",
        "estado": "activo",
        "fecha_creacion": "2024-01-20T14:30:00",
        "especialidades": [
            {
                "id": 2,
                "nombre": "Terapia Ocupacional",
                "area": "Especialidad terapéutica",
                "es_principal": true
            }
        ]
    }
}
```

### 4. Actualizar Paciente
```
PUT /api/pacientes/{id}
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "estado_tratamiento": "pausado",
    "observaciones": "Pausa temporal por motivos familiares"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Paciente actualizado exitosamente",
    "data": {
        "id": 2,
        "estado_tratamiento": "pausado",
        "observaciones": "Pausa temporal por motivos familiares",
        "fecha_modificacion": "2024-01-25T16:20:00"
    }
}
```

### 5. Cambiar Estado de Paciente
```
PUT /api/pacientes/{id}/estado
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "estado": "alta"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Estado del paciente cambiado a alta",
    "data": {
        "id": 2,
        "estado": "alta"
    }
}
```

### 6. Eliminar Paciente
```
DELETE /api/pacientes/{id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Paciente eliminado exitosamente",
    "data": null
}
```

### 7. Pacientes por Tutor
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
            "especialidades": []
        }
    ]
}
```

### 8. Estadísticas de Pacientes
```
GET /api/pacientes/estadisticas
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Estadísticas de pacientes obtenidas",
    "data": {
        "general": {
            "total_pacientes": 25,
            "pacientes_activos": 20,
            "pacientes_inactivos": 2,
            "pacientes_alta": 2,
            "pacientes_derivados": 1,
            "edad_promedio": 8.5
        },
        "por_estado": [
            {
                "estado": "activo",
                "total": 20
            },
            {
                "estado": "alta",
                "total": 2
            }
        ],
        "por_edad": [
            {
                "rango_edad": "0-4 años",
                "total": 8
            },
            {
                "rango_edad": "5-9 años",
                "total": 12
            },
            {
                "rango_edad": "10-14 años",
                "total": 5
            }
        ]
    }
}
```

### 9. Personas Disponibles para Pacientes
```
GET /api/pacientes/personas-disponibles
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Personas disponibles para paciente obtenidas",
    "data": [
        {
            "id": 7,
            "nombre": "Carlos",
            "apellido": "Rodríguez",
            "nombre_completo": "Carlos Rodríguez",
            "cedula": "1234567896",
            "telefono": "0987654326",
            "correo": "carlos.rodriguez@email.com",
            "fecha_nacimiento": "2016-08-15"
        }
    ]
}
```

## Gestión de Especialidades Múltiples

### 10. Obtener Especialidades del Paciente
```
GET /api/pacientes/{id}/especialidades
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidades del paciente obtenidas correctamente",
    "data": [
        {
            "id": 1,
            "id_especialidad": 1,
            "especialidad_nombre": "Terapia del Lenguaje",
            "especialidad_area": "Especialidad terapéutica",
            "fecha_asignacion": "2024-01-15",
            "fecha_inicio_tratamiento": "2024-01-16",
            "estado_tratamiento": "activo",
            "es_principal": true,
            "observaciones": "Progreso satisfactorio"
        }
    ]
}
```

### 11. Agregar Especialidad al Paciente
```
POST /api/pacientes/{id}/especialidades
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "especialidad_id": 3,
    "fecha_inicio_tratamiento": "2024-02-01",
    "observaciones": "Nueva especialidad de fisioterapia"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidad agregada exitosamente",
    "data": {
        "paciente_id": 1,
        "especialidad_id": 3
    }
}
```

### 12. Cambiar Especialidad Principal
```
PUT /api/pacientes/{id}/especialidad-principal
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "nueva_especialidad_principal": 3
}
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidad principal cambiada exitosamente",
    "data": {
        "paciente_id": 1,
        "nueva_especialidad_principal": 3
    }
}
```

### 13. Remover Especialidad del Paciente
```
DELETE /api/pacientes/{id}/especialidades/{especialidad_id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidad removida exitosamente",
    "data": null
}
```

### 14. Pausar Especialidad Específica
```
PUT /api/pacientes/{id}/especialidades/{especialidad_id}/pausar
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "fecha_inicio_pausa": "2024-02-15",
    "fecha_fin_pausa": "2024-03-01",
    "motivo_pausa": "Viaje familiar",
    "observaciones_pausa": "Pausa temporal por 2 semanas"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidad pausada exitosamente",
    "data": {
        "paciente_id": 1,
        "especialidad_id": 3
    }
}
```

### 15. Reactivar Especialidad
```
PUT /api/pacientes/{id}/especialidades/{especialidad_id}/reactivar
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Especialidad reactivada exitosamente",
    "data": {
        "paciente_id": 1,
        "especialidad_id": 3
    }
}
```

### 16. Pacientes por Especialidad
```
GET /api/pacientes/por-especialidad/{especialidad_id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Pacientes por especialidad obtenidos correctamente",
    "data": [
        {
            "id": 1,
            "nombre_completo": "María González",
            "estado": "activo",
            "estado_tratamiento": "activo",
            "especialidad_nombre": "Terapia del Lenguaje",
            "fecha_inicio_tratamiento": "2024-01-16"
        }
    ]
}
```

## Gestión de Documentos

### 17. Subir Documento
```
POST /api/pacientes/{id}/documentos
```

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data:**
```
archivo: [archivo PDF]
tipo_documento: historia_clinica
descripcion: Historia clínica inicial
es_confidencial: true
fecha_vencimiento: 2025-01-15
```

**Response:**
```json
{
    "success": true,
    "message": "Documento subido exitosamente",
    "data": {
        "id": 1,
        "nombre_archivo": "uuid123_historia_clinica.pdf",
        "tipo_documento": "historia_clinica",
        "descripcion": "Historia clínica inicial",
        "fecha_subida": "2024-01-20T15:30:00"
    }
}
```

### 18. Listar Documentos del Paciente
```
GET /api/pacientes/{id}/documentos
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Documentos obtenidos correctamente",
    "data": [
        {
            "id": 1,
            "nombre_archivo": "uuid123_historia_clinica.pdf",
            "nombre_original": "historia_clinica.pdf",
            "tipo_documento": "historia_clinica",
            "descripcion": "Historia clínica inicial",
            "tamaño_archivo": 2048576,
            "fecha_subida": "2024-01-20T15:30:00",
            "es_confidencial": true,
            "fecha_vencimiento": "2025-01-15"
        }
    ]
}
```

### 19. Descargar Documento
```
GET /api/pacientes/{id}/documentos/{documento_id}/descargar
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** Archivo PDF para descarga

### 20. Eliminar Documento
```
DELETE /api/pacientes/{id}/documentos/{documento_id}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "message": "Documento eliminado exitosamente",
    "data": null
}
```

## Implementación Técnica

### 1. Validaciones de Datos

#### Validación de Paciente
```python
def validate_paciente_data(data, is_update=False):
    """Validar datos completos del paciente"""
    errors = []
    
    # Campos requeridos para crear paciente
    if not is_update:
        required_fields = ['persona_id', 'tutor_id', 'fecha_ingreso']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field} es requerido")
    
    # Validar fecha_ingreso
    if 'fecha_ingreso' in data and data['fecha_ingreso']:
        fecha_validation = Validators.validate_date_format(data['fecha_ingreso'])
        if not fecha_validation['valid']:
            errors.append("Formato de fecha de ingreso inválido")
    
    # Validar estado_tratamiento
    if 'estado_tratamiento' in data and data['estado_tratamiento']:
        valid_states = ['activo', 'pausado', 'completado', 'derivado', 'alta']
        if data['estado_tratamiento'] not in valid_states:
            errors.append(f"Estado de tratamiento debe ser: {', '.join(valid_states)}")
    
    return {'valid': len(errors) == 0, 'message': '; '.join(errors)}
```

### 2. Reglas de Negocio

#### Unicidad de Persona como Paciente
```python
def check_persona_is_paciente(persona_id, exclude_id=None):
    """Una persona solo puede ser registrada una vez como paciente"""
    if exclude_id:
        query = "SELECT id FROM paciente WHERE persona_id = %s AND id != %s"
        params = (persona_id, exclude_id)
    else:
        query = "SELECT id FROM paciente WHERE persona_id = %s"
        params = (persona_id,)
    
    existing = DataBaseHandle.getRecords(query, params, size=1)
    return internal_response(True, existing is not None, "Consulta ejecutada")
```

#### Gestión de Especialidades Múltiples
```python
def agregar_especialidad_paciente(paciente_id, especialidad_id, fecha_inicio=None, observaciones=None, usuario_id=1):
    """Agregar especialidad con validaciones completas"""
    # Verificar que no exista ya la asociación activa
    existing = DataBaseHandle.getRecords(
        "SELECT id FROM paciente_especialidades WHERE id_paciente = %s AND id_especialidad = %s AND estado = 'activo'",
        (paciente_id, especialidad_id), size=1
    )
    
    if existing:
        return internal_response(False, None, "La especialidad ya está asignada a este paciente")
    
    # Insertar nueva especialidad
    success = DataBaseHandle.ExecuteNonQuery(
        "INSERT INTO paciente_especialidades (id_paciente, id_especialidad, fecha_inicio_tratamiento, observaciones, usuario_creacion) VALUES (%s, %s, %s, %s, %s)",
        (paciente_id, especialidad_id, fecha_inicio, observaciones, usuario_id)
    )
    
    return internal_response(success, None, "Especialidad agregada" if success else "Error")
```

### 3. Gestión de Documentos

#### Subida Segura de Archivos
```python
def upload_documento(paciente_id):
    """Subir documento PDF con validaciones de seguridad"""
    # Validar archivo
    if 'archivo' not in request.files:
        return response_error("No se proporcionó ningún archivo", 400)
    
    archivo = request.files['archivo']
    
    # Validar tipo (solo PDF)
    if not archivo.filename.lower().endswith('.pdf'):
        return response_error("Solo se permiten archivos PDF", 400)
    
    # Validar tamaño (máximo 10MB)
    archivo.seek(0, os.SEEK_END)
    tamaño_archivo = archivo.tell()
    archivo.seek(0)
    
    if tamaño_archivo > 10 * 1024 * 1024:
        return response_error("El archivo es demasiado grande. Máximo 10MB", 400)
    
    # Generar nombre único
    nombre_unico = f"{uuid.uuid4().hex}_{secure_filename(archivo.filename)}"
    
    # Crear carpeta del paciente
    paciente_data = PacienteComponent.get_paciente_by_id(paciente_id)['data']
    iniciales = f"{paciente_data['nombre'][0]}{paciente_data['apellido'][0]}".upper()
    carpeta_paciente = f"{iniciales}_{paciente_id}"
    ruta_carpeta = os.path.join("documentos_pacientes", carpeta_paciente)
    
    os.makedirs(ruta_carpeta, exist_ok=True)
    
    # Guardar archivo
    ruta_archivo = os.path.join(ruta_carpeta, nombre_unico)
    archivo.save(ruta_archivo)
```

### 4. Consultas SQL Principales

#### Pacientes con Información Completa
```sql
SELECT 
    pac.id,
    pac.fecha_ingreso,
    pac.estado_tratamiento,
    pac.observaciones,
    pac.estado,
    pac.fecha_creacion,
    pac.fecha_modificacion,
    -- Información del paciente (persona)
    p.id as persona_id,
    CONCAT(p.nombre, ' ', p.apellido) as nombre_completo,
    p.nombre,
    p.apellido,
    p.cedula,
    p.telefono,
    p.correo,
    p.direccion,
    p.fecha_nacimiento,
    -- Información del tutor
    t.id as tutor_id,
    t.parentesco,
    CONCAT(t.nombre, ' ', t.apellido) as nombre_tutor,
    t.telefono as telefono_tutor,
    t.email as correo_tutor
FROM paciente pac
INNER JOIN persona p ON pac.persona_id = p.id
INNER JOIN tutor t ON pac.id_tutor = t.id
WHERE pac.estado != 'eliminado'
ORDER BY p.nombre, p.apellido;
```

#### Especialidades del Paciente
```sql
SELECT 
    pe.id,
    pe.id_especialidad,
    e.nombre as especialidad_nombre,
    e.descripcion as especialidad_area,
    pe.fecha_asignacion,
    pe.fecha_inicio_tratamiento,
    pe.fecha_fin_tratamiento,
    pe.estado_tratamiento,
    pe.es_principal,
    pe.observaciones,
    pe.estado
FROM paciente_especialidades pe
INNER JOIN especialidad e ON pe.id_especialidad = e.id
WHERE pe.id_paciente = %s AND pe.estado != 'eliminado'
ORDER BY pe.es_principal DESC, e.descripcion, e.nombre;
```

#### Estadísticas de Pacientes
```sql
SELECT 
    COUNT(*) as total_pacientes,
    COUNT(CASE WHEN pac.estado = 'activo' THEN 1 END) as pacientes_activos,
    COUNT(CASE WHEN pac.estado = 'inactivo' THEN 1 END) as pacientes_inactivos,
    COUNT(CASE WHEN pac.estado = 'alta' THEN 1 END) as pacientes_alta,
    COUNT(CASE WHEN pac.estado = 'derivado' THEN 1 END) as pacientes_derivados,
    AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.fecha_nacimiento))) as edad_promedio
FROM paciente pac
INNER JOIN persona p ON pac.persona_id = p.id;
```

## Casos de Uso y Flujos

### 1. Registro de Nuevo Paciente
```
1. Crear persona → POST /api/personas
2. Crear tutor → POST /api/tutores
3. Registrar paciente → POST /api/pacientes
4. Sistema valida persona y tutor existen
5. Asigna especialidad principal si se proporciona
6. Paciente queda disponible para sesiones de tratamiento
```

### 2. Gestión de Especialidades Múltiples
```
1. Paciente con especialidad principal creado
2. Agregar especialidades adicionales → POST /api/pacientes/{id}/especialidades
3. Cambiar especialidad principal → PUT /api/pacientes/{id}/especialidad-principal
4. Pausar especialidades específicas → PUT /api/pacientes/{id}/especialidades/{esp_id}/pausar
5. Reactivar especialidades → PUT /api/pacientes/{id}/especialidades/{esp_id}/reactivar
```

### 3. Manejo de Estados y Pausas
```
1. Pausa temporal específica por especialidad
2. Pausa general del paciente → PUT /api/pacientes/{id}/estado (pausado)
3. Alta médica → PUT /api/pacientes/{id}/estado (alta)
4. Derivación → PUT /api/pacientes/{id}/estado (derivado)
5. Eliminación lógica → DELETE /api/pacientes/{id}
```

### 4. Gestión de Documentos Médicos
```
1. Subir documento → POST /api/pacientes/{id}/documentos
2. Sistema crea carpeta única por paciente (iniciales_id)
3. Genera nombre único con UUID
4. Valida tipo PDF y tamaño máximo 10MB
5. Clasifica por tipo de documento
6. Permite descarga segura por personal autorizado
```

## Tipos de Documentos Soportados

### Clasificación de Documentos
- **general**: Documentos generales del paciente
- **historia_clinica**: Historia clínica y antecedentes
- **examenes_medicos**: Resultados de exámenes y pruebas
- **consentimientos**: Consentimientos informados
- **reportes_terapia**: Reportes de sesiones terapéuticas
- **evaluaciones**: Evaluaciones y valoraciones
- **otros**: Otros documentos relevantes

### Almacenamiento de Archivos
```
documentos_pacientes/
├── MG_1/                    # Paciente María González (ID=1)
│   ├── uuid123_historia.pdf
│   └── uuid456_examen.pdf
├── PR_2/                    # Paciente Pedro Rodríguez (ID=2)
│   └── uuid789_reporte.pdf
```

## Integración con Otros Módulos

### Con Personas y Tutores
- **Extensión**: Paciente extiende persona con información médica
- **Responsabilidad**: Cada paciente tiene un tutor asignado
- **Validación**: Persona y tutor deben estar activos

### Con Especialidades
- **Especialidades múltiples**: Un paciente puede tener varias especialidades
- **Estados independientes**: Cada especialidad maneja su propio estado
- **Especialidad principal**: Una especialidad marcada como principal

### Con Centros
- **Asignación por centro**: Paciente pertenece a un centro específico
- **Filtrado automático**: Usuario ve solo pacientes de su centro
- **Centro por defecto**: ID=13 (Centro Norte) si no se especifica

### Con Sesiones
- **Sesiones terapéuticas**: Basadas en especialidades terapéuticas
- **Sesiones pedagógicas**: Basadas en especialidades pedagógicas
- **Compatibilidad**: Verificación con personal asignado

## Validaciones y Restricciones

### Campos Obligatorios
- **persona_id**: Debe existir en tabla persona y estar activa
- **tutor_id**: Debe existir en tabla tutor y estar activo
- **fecha_ingreso**: Fecha válida, no futura

### Reglas de Negocio
- **Unicidad de persona**: Una persona solo puede ser paciente una vez
- **Especialidades activas**: Solo especialidades activas pueden asignarse
- **Estados válidos**: Transiciones de estado controladas
- **Documentos seguros**: Solo archivos PDF, máximo 10MB

### Códigos de Error
- **400**: Datos inválidos, validaciones fallidas
- **401**: Token requerido o inválido
- **403**: Sin permisos suficientes
- **404**: Paciente, especialidad o documento no encontrado
- **409**: Conflicto (persona ya es paciente, especialidad duplicada)
- **500**: Error interno del servidor

## Configuración y Dependencias

### Variables de Entorno
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=centro_tia_glenda
CENTRO_PREDETERMINADO=13
```

### Rutas de Archivos
```bash
DOCUMENTOS_PACIENTES_PATH=./documentos_pacientes/
TAMAÑO_MAXIMO_ARCHIVO=10MB
TIPOS_ARCHIVO_PERMITIDOS=pdf
```

## Logging y Auditoría

El sistema registra:
- Creación de pacientes nuevos
- Modificaciones de datos y estados
- Asignación/remoción de especialidades
- Pausas y reactivaciones
- Subida y eliminación de documentos
- Cambios de estado y derivaciones

Ubicación: `src/utils/general/LOGS/`

## Testing

Pruebas incluidas para:
- CRUD completo de pacientes
- Gestión de especialidades múltiples
- Estados y pausas por especialidad
- Subida y gestión de documentos
- Validaciones de unicidad
- Integración con tutores y centros

Ejecutar: `python tests/test_pacientes_api.py`

## Consideraciones de Seguridad

### Control de Acceso
- **Por centro**: Usuarios ven solo pacientes de su centro
- **Documentos confidenciales**: Marcado específico para documentos sensibles
- **Validación de archivos**: Solo PDF, validación de tipo MIME

### Protección de Datos
- **Eliminación lógica**: Preservación de datos históricos
- **Encriptación de archivos**: Nombres únicos con UUID
- **Auditoría completa**: Registro de todos los cambios

### Integridad de Datos
- **Referencias válidas**: Verificación de personas y tutores existentes
- **Estados consistentes**: Validación de transiciones de estado
- **Backup de documentos**: Archivos físicos protegidos

## Limitaciones Actuales

### Documentos
- **Solo PDF**: No soporta otros tipos de archivo médico
- **Sin versionado**: No manejo de versiones de documentos
- **Sin firma digital**: Documentos no firmados digitalmente

### Especialidades
- **Sin jerarquía**: Especialidades independientes sin relaciones
- **Sin planificación**: No calendario de tratamientos por especialidad
- **Sin métricas**: No seguimiento de progreso por especialidad

## Recomendaciones de Mejora

### Futuras Implementaciones
1. **Expediente médico completo**: Integración con historias clínicas electrónicas
2. **Calendario de tratamientos**: Planificación de sesiones por especialidad
3. **Métricas de progreso**: Seguimiento de evolución del paciente
4. **Firma digital**: Documentos con firma electrónica
5. **Telemedicina**: Soporte para consultas remotas
6. **Alertas médicas**: Notificaciones de citas y tratamientos
7. **Reportes médicos**: Generación automática de reportes
8. **Integración DICOM**: Soporte para imágenes médicas
9. **Consentimientos digitales**: Formularios electrónicos
10. **API de laboratorios**: Integración con resultados de exámenes