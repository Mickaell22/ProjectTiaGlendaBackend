# Documentación de Endpoints - API Centro Tía Glenda

## Información General
- **Base URL**: `http://localhost:5000`
- **Autenticación**: JWT Bearer Token
- **Formato**: JSON
- **Puerto por defecto**: 5000 (configurable via variable `PORT`)
- **Versión**: 1.3.0
- **Swagger UI**: `http://localhost:5000/docs/`

## Arquitectura del Sistema
Este API sigue un patrón de 3 capas:
1. **Rutas** (Routes): Manejo de peticiones HTTP y validación de entrada
2. **Servicios** (Services): Lógica de negocio y validaciones
3. **Componentes** (Components): Acceso a datos y operaciones de base de datos

## Configuración CORS
El API está configurado para aceptar peticiones desde:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- `http://localhost:5174` (Vite alternativo)
- `http://localhost:5175` (Vite alternativo)
- Orígenes adicionales configurados via `CORS_ORIGINS` en variables de entorno

## Autenticación

### POST /api/login
Iniciar sesión y obtener token JWT

**Request Body:**
```json
{
  "usuario": "admin",
  "contrasenia": "admin123"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Autenticacion exitosa",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "usuario": "admin",
      "nombre_completo": "Admin Sistema",
      "rol": "Administrador",
      "correo": "admin@centro.com"
    }
  }
}
```

### GET /api/verify-token
Verificar validez del token (requiere Bearer token)

**Headers:**
```
Authorization: Bearer <token>
```

### POST /api/logout
Cerrar sesión (requiere Bearer token)

### GET /api/me
Obtener información del usuario autenticado

---

## Gestión de Personas

### GET /api/personas
Listar todas las personas

### POST /api/personas
Crear nueva persona

**Request Body:**
```json
{
  "nombre": "María Elena",
  "apellido": "García", 
  "cedula": "12345678",
  "telefono": "+50612345678",
  "correo": "maria@email.com",
  "direccion": "San José, Costa Rica",
  "fecha_nacimiento": "1990-05-15",
  "estado": "activo"
}
```

### GET /api/personas/{id}
Obtener persona por ID

**Parameters:**
- `id` (integer): ID de la persona

### PUT /api/personas/{id}
Actualizar persona existente

### DELETE /api/personas/{id}
Desactivar persona (solo administradores)

### GET /api/personas/disponibles
Personas sin usuario asignado (solo administradores)

---

## Gestión de Tutores

### GET /api/tutores
Listar todos los tutores

### POST /api/tutores
Crear nuevo tutor

**Request Body:**
```json
{
  "persona_id": 1,
  "parentesco": "madre",
  "es_contacto_emergencia": true,
  "observaciones_tutor": "Madre muy colaborativa"
}
```

**Parentesco válidos:**
- `madre`, `padre`, `abuelo`, `abuela`, `hermano`, `hermana`, `tio`, `tia`, `otro`

### GET /api/tutores/{id}
Obtener tutor por ID

### PUT /api/tutores/{id}
Actualizar tutor

### GET /api/tutores/activos
Solo tutores activos

### GET /api/tutores/estadisticas
Estadísticas de tutores

### GET /api/tutores/personas-disponibles
Personas disponibles para asignar como tutores

---

## Gestión de Pacientes

### GET /api/pacientes
Listar todos los pacientes

### POST /api/pacientes
Crear nuevo paciente

**Request Body:**
```json
{
  "persona_id": 1,
  "tutor_id": 1,
  "fecha_ingreso": "2023-01-15",
  "observaciones": "Paciente con necesidades de terapia ocupacional"
}
```

### GET /api/pacientes/{id}
Obtener paciente por ID

### PUT /api/pacientes/{id}
Actualizar paciente

### PUT /api/pacientes/{id}/estado
Cambiar estado del paciente

**Request Body:**
```json
{
  "estado": "activo"
}
```

**Estados válidos:**
- `activo`, `inactivo`, `alta`, `derivado`

### GET /api/pacientes/tutor/{tutor_id}
Pacientes de un tutor específico

### GET /api/pacientes/estadisticas
Estadísticas de pacientes

### GET /api/pacientes/personas-disponibles
Personas disponibles para asignar como pacientes

---

## Gestión de Especialidades

### GET /api/especialidades
Listar todas las especialidades

### POST /api/especialidades
Crear especialidad (solo administradores)

**Request Body:**
```json
{
  "nombre": "Terapia Ocupacional Pediátrica",
  "area": "terapeutico",
  "estado": "activo"
}
```

**Áreas válidas:**
- `terapeutico`, `pedagogico`

### GET /api/especialidades/{area}
Especialidades por área

**Parameters:**
- `area` (string): `terapeutico` o `pedagogico`

### GET /api/especialidades/id/{id}
Obtener especialidad por ID

### PUT /api/especialidades/id/{id}
Actualizar especialidad (solo administradores)

### DELETE /api/especialidades/id/{id}
Desactivar especialidad (solo administradores)

### GET /api/especialidades/activas
Solo especialidades activas

### GET /api/especialidades/estadisticas
Estadísticas de especialidades

---

## Gestión de Personal

### GET /api/personal
Listar todo el personal

### POST /api/personal
Registrar nuevo personal (solo administradores)

**Request Body:**
```json
{
  "persona_id": 1,
  "titulo_profesional": "Licenciatura en Terapia Ocupacional",
  "estado": "activo"
}
```

### GET /api/personal/{id}
Obtener personal por ID

### PUT /api/personal/{id}
Actualizar personal (solo administradores)

### DELETE /api/personal/{id}
Desactivar personal (solo administradores)

### GET /api/personal/area/{area}
Personal por área

**Parameters:**
- `area` (string): `terapeutico` o `pedagogico`

### GET /api/personal/estadisticas
Estadísticas del personal

### GET /api/personal/{id}/especialidades
Especialidades asignadas a un miembro del personal

### POST /api/personal/{id}/especialidades
Asignar especialidad al personal (solo administradores)

**Request Body:**
```json
{
  "especialidad_id": 1
}
```

### DELETE /api/personal/{personal_id}/especialidades/{especialidad_id}
Remover especialidad del personal (solo administradores)

---

## Gestión de Usuarios

### GET /api/usuarios
Listar usuarios (solo administradores)

### POST /api/usuarios
Crear usuario (solo administradores)

**Request Body:**
```json
{
  "usuario": "maria.garcia",
  "contrasenia": "Password123!",
  "persona_id": 2,
  "rol_id": 2,
  "estado": "activo"
}
```

**Estados válidos:**
- `activo`, `inactivo`, `bloqueado`

### GET /api/usuarios/{id}
Obtener usuario por ID

### PUT /api/usuarios/{id}
Actualizar usuario (solo administradores)

### DELETE /api/usuarios/{id}
Desactivar usuario (solo administradores)

---

## Gestión de Documentos de Pacientes

### POST /api/pacientes/{id}/documentos
Subir documento PDF para un paciente

**Request**: Multipart form data
```javascript
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('tipo_documento', 'historial_clinico');
formData.append('nombre_documento', 'Historia Clínica Inicial');
formData.append('descripcion', 'Primera evaluación del paciente');
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Documento subido exitosamente",
  "data": {
    "id": 123,
    "nombre_documento": "Historia Clínica Inicial",
    "tipo_documento": "historial_clinico",
    "ruta_archivo": "/documentos_pacientes/CV_9/uuid-filename.pdf"
  }
}
```

### GET /api/pacientes/{id}/documentos
Obtener lista de documentos de un paciente

### GET /api/pacientes/{paciente_id}/documentos/{documento_id}
Descargar un documento específico (retorna archivo PDF)

### PUT /api/pacientes/{paciente_id}/documentos/{documento_id}
Actualizar información de un documento (no el archivo físico)

**Request Body:**
```json
{
  "nombre_documento": "Historia Clínica Actualizada",
  "descripcion": "Versión actualizada con nuevos estudios"
}
```

### DELETE /api/pacientes/{paciente_id}/documentos/{documento_id}
Eliminar un documento

### GET /api/documentos/estadisticas
Estadísticas de documentos por tipo

---

## Gestión de Especialidades de Pacientes

### GET /api/pacientes/{id}/especialidades
Obtener especialidades asignadas a un paciente

### POST /api/pacientes/{id}/especialidades
Asignar una especialidad a un paciente

**Request Body:**
```json
{
  "especialidad_id": 1,
  "personal_id": 2,
  "fecha_inicio": "2023-01-15",
  "observaciones": "Requiere terapia física intensiva"
}
```

### PUT /api/pacientes/especialidades/{tratamiento_id}
Actualizar una asignación de especialidad

### DELETE /api/pacientes/especialidades/{tratamiento_id}
Eliminar una asignación de especialidad

### GET /api/pacientes/especialidades/{tratamiento_id}
Obtener detalles de una asignación específica

### GET /api/especialidades/{id}/pacientes
Obtener pacientes que tienen una especialidad específica

### GET /api/pacientes/especialidades/estadisticas
Obtener estadísticas de especialidades de pacientes

### GET /api/pacientes/{id}/especialidades/activos
Obtener tratamientos activos de un paciente

### GET /api/pacientes/{id}/especialidades/completados
Obtener tratamientos completados de un paciente

### GET /api/pacientes/{id}/especialidades/suspendidos
Obtener tratamientos suspendidos de un paciente

---

## Sesiones de Terapia

### GET /api/sesiones-terapia
Obtener todas las sesiones de terapia

### POST /api/sesiones-terapia
Crear nueva sesión con cronograma automático

**Request Body:**
```json
{
  "paciente_id": 1,
  "terapeuta_id": 2,
  "especialidad_id": 1,
  "fecha_inicio": "2025-07-26",
  "hora_inicio": "10:00:00",
  "duracion_minutos": 60,
  "tipo_sesion": "individual",
  "dias_semana": "lunes,miercoles,viernes",
  "observaciones": "Sesión de terapia física"
}
```

**Tipos de sesión:**
- `individual`, `grupal`

**Días de semana:**
- Formato: lista separada por comas (ej: "lunes,miercoles,viernes")

### GET /api/sesiones-terapia/{id}
Obtener sesión específica con cronograma

**Response incluye:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "codigo_sesion": "SES-001-2025",
    "paciente_id": 1,
    "terapeuta_id": 2,
    "cronograma": [
      {
        "fecha": "2025-07-26",
        "dia_semana": "sabado",
        "hora_inicio": "10:00:00",
        "hora_fin": "11:00:00"
      }
    ]
  }
}
```

### PUT /api/sesiones-terapia/{id}
Actualizar sesión

### DELETE /api/sesiones-terapia/{id}
Eliminar sesión

### GET /api/sesiones-terapia/{id}/cronograma
Obtener solo el cronograma de la sesión

### POST /api/sesiones-terapia/{id}/cronograma/generar
Regenerar cronograma de una sesión

### GET /api/sesiones-terapia/{id}/pacientes
Obtener pacientes asignados a una sesión

### POST /api/sesiones-terapia/{id}/pacientes
Agregar paciente a una sesión

**Request Body:**
```json
{
  "paciente_id": 5
}
```

### DELETE /api/sesiones-terapia/{sesion_id}/pacientes/{paciente_id}
Remover paciente de una sesión

### GET /api/sesiones-terapia/terapeuta/{terapeuta_id}
Sesiones asignadas a un terapeuta específico

### GET /api/sesiones-terapia/hoy
Sesiones programadas para hoy

### GET /api/sesiones-terapia/estadisticas
Estadísticas generales de sesiones

### GET /api/sesiones-terapia/pacientes-disponibles
Pacientes disponibles para asignar a sesiones

### GET /api/sesiones-terapia/terapeutas-disponibles
Terapeutas disponibles para asignar a sesiones

## Gestión de Cronograma y Asistencia - Sesiones de Terapia

### PUT /api/cronograma-sesiones/{cronograma_id}/realizar
Marcar sesión como realizada

### PUT /api/cronograma-sesiones/{cronograma_id}/reprogramar
Reprogramar una sesión específica

**Request Body:**
```json
{
  "nueva_fecha": "2025-08-10"
}
```

### GET /api/cronograma-sesiones/{cronograma_id}/asistencias
Obtener asistencias de una sesión específica del cronograma

### POST /api/sesiones-terapia/cronograma/{cronograma_id}/pacientes/{paciente_id}/asistencia
Registrar asistencia de un paciente

**Request Body:**
```json
{
  "asistio": true,
  "llegada_tardanza_minutos": 0,
  "observaciones": "Paciente muy colaborativo",
  "estado_animo": "alegre",
  "progreso_observado": "Mejora notable en movilidad"
}
```

### PUT /api/sesiones-terapia/cronograma/{cronograma_id}/pacientes/{paciente_id}/asistencia
Actualizar asistencia existente

### GET /api/sesiones-terapia/cronograma/{cronograma_id}/asistencia
Obtener todas las asistencias de una sesión del cronograma

### GET /api/sesiones-terapia/{sesion_id}/asistencias
Obtener todas las asistencias de una sesión de terapia

### GET /api/sesiones-terapia/asistencias/paciente/{paciente_id}
Obtener historial de asistencias de un paciente específico

### GET /api/sesiones-terapia/{sesion_id}/estadisticas-asistencia
Obtener estadísticas de asistencia de una sesión

---

## Sistema y Utilidades

### GET /health
Health check del sistema

**Response:**
```json
{
  "status": "success",
  "message": "Sistema funcionando correctamente"
}
```

### GET /api/test
Verificar que la API está funcionando

### GET /api/test-db
Verificar conexión a la base de datos PostgreSQL

**Response exitosa:**
```json
{
  "status": "success",
  "message": "Conexion a base de datos exitosa",
  "data": {
    "database": "centro_tia_glenda",
    "postgresql_version": "PostgreSQL 15.4",
    "total_usuarios": 3,
    "connection": "successful"
  }
}
```

### GET /api/test-db-status
Demostrar diferencia entre métodos `getRecords` vs `getRecordsWithStatus`

**Response:**
```json
{
  "status": "success",
  "message": "Comparacion de metodos getRecords completada",
  "data": {
    "valid_query": {
      "old_method": {"total_usuarios": 3},
      "new_method": {
        "success": true,
        "data": {"total_usuarios": 3},
        "error": null,
        "connection_error": false
      }
    },
    "empty_result": {
      "old_method": null,
      "new_method": {
        "success": true,
        "data": null,
        "error": null,
        "connection_error": false
      }
    },
    "error_query": {
      "old_method": null,
      "new_method": {
        "success": false,
        "data": null,
        "error": "relation \"tabla_inexistente\" does not exist",
        "connection_error": false
      }
    }
  }
}
```

### GET /api/roles
Listar roles disponibles en el sistema

---

## Códigos de Respuesta

### Exitosos
- **200 OK**: Operación exitosa, datos obtenidos correctamente
- **201 Created**: Recurso creado exitosamente (POST requests)

### Errores del Cliente (4xx)
- **400 Bad Request**: Datos inválidos, malformados o faltantes
  - Campos requeridos faltantes
  - Formato de datos incorrecto (ej: fecha inválida)
  - Valores fuera del rango permitido
- **401 Unauthorized**: Token JWT requerido o inválido
  - Token expirado
  - Token malformado
  - Sin header Authorization
- **403 Forbidden**: Sin permisos suficientes
  - Operaciones que requieren rol de administrador
  - Acceso denegado por reglas de negocio
- **404 Not Found**: Recurso no encontrado
  - ID inexistente
  - Endpoint no válido
- **409 Conflict**: Conflicto con el estado actual del recurso
  - Datos duplicados (ej: cédula ya existe)
  - Restricciones de integridad

### Errores del Servidor (5xx)
- **500 Internal Server Error**: Error interno del servidor
  - Errores de base de datos
  - Errores inesperados en la lógica de negocio
  - Problemas de conectividad

### Errores Comunes por Módulo

#### Sesiones de Terapia
- **400**: Días de semana inválidos o formato incorrecto
- **400**: Terapeuta no disponible en el horario especificado
- **404**: Paciente o terapeuta no encontrado
- **409**: Conflicto de horarios con otras sesiones

#### Documentos de Pacientes
- **400**: Archivo no es PDF o excede tamaño máximo
- **404**: Archivo físico no encontrado en el sistema
- **413**: Archivo demasiado grande (límite por defecto: 10MB)

---

## Formato de Respuestas

### Respuesta Exitosa
```json
{
  "status": "success",
  "message": "Operación exitosa",
  "data": { /* datos específicos */ }
}
```

### Respuesta de Error
```json
{
  "status": "error",
  "message": "Descripción del error",
  "code": 400
}
```

---

## Sesiones Pedagógicas

### GET /api/sesiones-pedagogicas
Obtener todas las sesiones pedagógicas con estadísticas completas

### POST /api/sesiones-pedagogicas
Crear nueva sesión pedagógica con cronograma automático

**Request Body:**
```json
{
  "titulo": "Matemáticas Básicas Grupo A",
  "pedagogo_id": 2,
  "especialidad_id": 3,
  "fecha_inicio": "2025-08-01",
  "fecha_fin": "2025-11-30",
  "dias_semana": "lunes,miercoles,viernes",
  "hora_inicio": "09:00",
  "duracion_minutos": 60,
  "numero_clases_programadas": 36,
  "nivel_academico": "basico",
  "capacidad_maxima": 12,
  "modalidad": "presencial",
  "costo_total": 18000.00,
  "periodo_academico": "2025-2",
  "observaciones": "Sesión para nivel básico de matemáticas"
}
```

### GET /api/sesiones-pedagogicas/{id}
Obtener sesión pedagógica específica

### PUT /api/sesiones-pedagogicas/{id}
Actualizar sesión pedagógica

### DELETE /api/sesiones-pedagogicas/{id}
Cancelar sesión pedagógica (eliminación lógica)

### GET /api/sesiones-pedagogicas/{id}/estudiantes
Obtener estudiantes asignados a una sesión

### POST /api/sesiones-pedagogicas/{id}/estudiantes
Agregar estudiante a una sesión

**Request Body:**
```json
{
  "paciente_id": 5,
  "costo_estudiante": 1500.00,
  "observaciones_estudiante": "Estudiante con buen rendimiento"
}
```

### DELETE /api/sesiones-pedagogicas/{id}/estudiantes/{paciente_id}
Remover estudiante de una sesión

### GET /api/sesiones-pedagogicas/{id}/cronograma
Obtener cronograma de clases de la sesión

### POST /api/sesiones-pedagogicas/{id}/cronograma/generar
Regenerar cronograma de clases automáticamente

### GET /api/sesiones-pedagogicas/pedagogo/{pedagogo_id}
Sesiones asignadas a un pedagogo específico

### GET /api/sesiones-pedagogicas/estadisticas
Estadísticas generales de sesiones pedagógicas

### GET /api/sesiones-pedagogicas/hoy
Clases programadas para hoy

### GET /api/sesiones-pedagogicas/estudiantes-disponibles
Obtener estudiantes disponibles para asignar a sesiones pedagógicas

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "nombre_completo": "Ana Sofía Morales",
      "cedula": "12345678",
      "edad": 8,
      "tutor": "María Morales"
    }
  ]
}
```

### GET /api/sesiones-pedagogicas/pedagogos-disponibles
Obtener pedagogos disponibles para asignar a sesiones

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 2,
      "nombre_completo": "Prof. Carlos Méndez",
      "especialidades": ["Matemáticas Básicas", "Lectoescritura"],
      "titulo_profesional": "Licenciado en Educación"
    }
  ]
}
```

## Gestión de Cronograma y Asistencia - Sesiones Pedagógicas

### PUT /api/cronograma-clases/{cronograma_id}/realizar
Marcar clase como realizada

### PUT /api/cronograma-clases/{cronograma_id}/reprogramar
Reprogramar una clase específica

**Request Body:**
```json
{
  "nueva_fecha": "2025-08-12"
}
```

### PUT /api/cronograma-clases/{cronograma_id}
Actualizar información de una clase del cronograma

**Request Body:**
```json
{
  "tema_clase": "Operaciones básicas con fracciones",
  "objetivos_clase": "Sumar y restar fracciones con denominadores diferentes",
  "material_requerido": "Calculadora, papel, ejercicios impresos",
  "tareas_asignadas": "Ejercicios página 45-47",
  "evaluacion_programada": true,
  "tipo_evaluacion": "quiz"
}
```

### GET /api/cronograma-clases/{cronograma_id}/asistencias
Obtener asistencias de una clase específica

### POST /api/cronograma-clases/{cronograma_id}/asistencias/{paciente_id}
Registrar asistencia de un estudiante a una clase

**Request Body:**
```json
{
  "asistio": true,
  "llegada_tardanza_minutos": 5,
  "observaciones_asistencia": "Llegó tarde por transporte",
  "participacion_clase": "alta",
  "tareas_entregadas": true,
  "notas_comportamiento": "Muy participativo y colaborativo",
  "calificacion_evaluacion": 85,
  "observaciones_evaluacion": "Buen dominio del tema, necesita reforzar cálculos"
}
```

**Valores válidos para `participacion_clase`:**
- `alta`, `media`, `baja`, `no_participo`

**Valores válidos para `calificacion_evaluacion`:**
- Número entre 0 y 100 (opcional, solo si hay evaluación)

---

## Instrucciones para Desarrollo de Frontend Debug

### Configuración del Proyecto Frontend

Para crear un frontend de debug que consuma esta API, seguir estas configuraciones:

#### 1. Variables de Entorno Frontend
```javascript
// .env o config.js
const API_CONFIG = {
  BASE_URL: 'http://localhost:5000',
  ENDPOINTS: {
    LOGIN: '/api/login',
    VERIFY_TOKEN: '/api/verify-token',
    HEALTH: '/health',
    TEST_DB: '/api/test-db'
  },
  DEBUG_MODE: true
}
```

#### 2. Autenticación y Headers
```javascript
// Configuración de headers para todas las peticiones
const getAuthHeaders = () => {
  const token = localStorage.getItem('jwt_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  };
};

// Interceptor para debugging
const apiRequest = async (url, options = {}) => {
  const fullUrl = `${API_CONFIG.BASE_URL}${url}`;
  const headers = getAuthHeaders();
  
  if (API_CONFIG.DEBUG_MODE) {
    console.log('🚀 API Request:', { url: fullUrl, method: options.method || 'GET', headers, body: options.body });
  }
  
  const response = await fetch(fullUrl, {
    ...options,
    headers: { ...headers, ...options.headers }
  });
  
  const data = await response.json();
  
  if (API_CONFIG.DEBUG_MODE) {
    console.log('📥 API Response:', { status: response.status, data });
  }
  
  return { response, data };
};
```

#### 3. Manejo de Errores y Debug
```javascript
// Componente de Debug Console
const DebugConsole = () => {
  const [logs, setLogs] = useState([]);
  
  const addLog = (type, message, data = null) => {
    setLogs(prev => [...prev, {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      type, // 'success', 'error', 'warning', 'info'
      message,
      data
    }]);
  };
  
  return (
    <div className="debug-console">
      <h3>Debug Console</h3>
      {logs.map(log => (
        <div key={log.id} className={`log-entry log-${log.type}`}>
          <span className="timestamp">{log.timestamp}</span>
          <span className="message">{log.message}</span>
          {log.data && <pre>{JSON.stringify(log.data, null, 2)}</pre>}
        </div>
      ))}
    </div>
  );
};
```

#### 4. Componentes de Testing por Módulo
```javascript
// Ejemplo: Componente de Test para Sesiones de Terapia
const TerapiaSessionDebugger = () => {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [cronograma, setCronograma] = useState([]);
  const [debugInfo, setDebugInfo] = useState({});
  
  const testCreateSession = async () => {
    const testData = {
      paciente_id: 1,
      terapeuta_id: 2,
      especialidad_id: 1,
      fecha_inicio: "2025-07-27",
      hora_inicio: "10:00:00",
      duracion_minutos: 60,
      tipo_sesion: "individual",
      dias_semana: "lunes,miercoles,viernes",
      observaciones: "Sesión de prueba desde frontend debug"
    };
    
    try {
      const { response, data } = await apiRequest('/api/sesiones-terapia', {
        method: 'POST',
        body: JSON.stringify(testData)
      });
      
      if (response.ok) {
        setDebugInfo(prev => ({...prev, lastCreated: data.data}));
        loadSessions(); // Recargar lista
      }
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };
  
  const debugCronograma = async (sessionId) => {
    try {
      const { response, data } = await apiRequest(`/api/sesiones-terapia/${sessionId}/cronograma`);
      setCronograma(data.data || []);
      
      // Análisis de cronograma para debug
      const analysis = {
        totalClases: data.data?.length || 0,
        fechaInicio: data.data?.[0]?.fecha,
        fechaFin: data.data?.[data.data?.length - 1]?.fecha,
        diasUnicos: [...new Set(data.data?.map(c => c.dia_semana))],
        problemasDetectados: []
      };
      
      // Detectar problemas comunes
      if (analysis.totalClases === 0) {
        analysis.problemasDetectados.push("No hay clases programadas");
      }
      
      if (analysis.diasUnicos.length === 0) {
        analysis.problemasDetectados.push("No se detectaron días de la semana válidos");
      }
      
      setDebugInfo(prev => ({...prev, cronogramaAnalysis: analysis}));
      
    } catch (error) {
      console.error('Error loading cronograma:', error);
    }
  };
  
  return (
    <div className="therapy-debugger">
      <h2>Therapy Sessions Debugger</h2>
      
      <button onClick={testCreateSession}>Test Create Session</button>
      <button onClick={() => loadSessions()}>Reload Sessions</button>
      
      <div className="sessions-list">
        {sessions.map(session => (
          <div key={session.id} className="session-item">
            <span>{session.codigo_sesion}</span>
            <button onClick={() => debugCronograma(session.id)}>
              Debug Cronograma
            </button>
          </div>
        ))}
      </div>
      
      {debugInfo.cronogramaAnalysis && (
        <div className="cronograma-analysis">
          <h3>Cronograma Analysis</h3>
          <pre>{JSON.stringify(debugInfo.cronogramaAnalysis, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};
```

#### 5. Endpoints Recomendados para Debug Interface

**Dashboard de Estado del Sistema:**
- `GET /health` - Estado general
- `GET /api/test-db` - Conexión base de datos
- `GET /api/verify-token` - Validez del token

**Datos de Testing Rápido:**
- `GET /api/personas/disponibles` - Personas sin usuario
- `GET /api/pacientes` - Lista de pacientes
- `GET /api/personal` - Lista de personal
- `GET /api/especialidades/activas` - Especialidades disponibles

**Módulos Principales para Testing:**
1. **Autenticación**: Login/logout con diferentes usuarios
2. **Pacientes**: CRUD completo con validaciones
3. **Sesiones de Terapia**: Creación y debug de cronogramas
4. **Sesiones Pedagógicas**: Gestión de estudiantes y clases
5. **Personal y Especialidades**: Asignaciones y relaciones

#### 6. Problemas Conocidos - Cronograma de Terapia

**Síntomas del problema:**
- Cronograma vacío después de crear sesión
- Error en generación de fechas
- Días de semana no reconocidos

**Debug checklist:**
```javascript
const debugCronogramaIssues = async (sessionId) => {
  const checks = {
    sessionExists: false,
    validDays: false,
    validDateRange: false,
    cronogramaGenerated: false
  };
  
  // 1. Verificar que la sesión existe
  const session = await apiRequest(`/api/sesiones-terapia/${sessionId}`);
  checks.sessionExists = session.response.ok;
  
  // 2. Verificar días de semana
  const diasSemana = session.data?.data?.dias_semana;
  checks.validDays = diasSemana && diasSemana.trim().length > 0;
  
  // 3. Verificar rango de fechas
  const fechaInicio = session.data?.data?.fecha_inicio;
  checks.validDateRange = fechaInicio && new Date(fechaInicio) > new Date();
  
  // 4. Verificar cronograma
  const cronograma = await apiRequest(`/api/sesiones-terapia/${sessionId}/cronograma`);
  checks.cronogramaGenerated = cronograma.data?.data?.length > 0;
  
  console.log('🔍 Cronograma Debug Results:', checks);
  return checks;
};
```

---

## Consideraciones de Fechas y Zonas Horarias

### Formatos de Fecha Utilizados
El sistema utiliza diferentes formatos de fecha dependiendo del endpoint:

1. **Cronograma endpoints** (ej: `/api/sesiones-terapia/{id}/cronograma`):
   - Formato: `"2025-08-06"` (YYYY-MM-DD string)
   - Fuente: Campos DATE de PostgreSQL convertidos con `isoformat()`
   - **Seguro para JavaScript**: `new Date("2025-08-06")` no causa problemas de timezone

2. **Asistencias endpoints** (ej: `/api/sesiones-terapia/{id}/asistencias`):
   - Formato: `"Wed, 06 Aug 2025 00:00:00 GMT"` (GMT datetime string)
   - Fuente: Campos TIMESTAMP convertidos por el serializador JSON de Flask
   - **⚠️ Problemático**: Puede causar conversión de timezone en el frontend

### Problema de Timezone en Frontend
```javascript
// CORRECTO - No hay conversión de timezone
new Date("2025-08-06") // → Wed Aug 06 2025

// PROBLEMÁTICO - Se convierte a timezone local
new Date("Wed, 06 Aug 2025 00:00:00 GMT") 
// → Tue Aug 05 2025 19:00:00 GMT-0500 (¡DÍA ANTERIOR!)
```

### Recomendaciones para Frontend
```javascript
// Función helper para manejar fechas de forma segura
const parseAPIDate = (dateString) => {
  // Si es formato ISO simple, usar directamente
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
    return new Date(dateString + 'T00:00:00');
  }
  
  // Si es GMT string, convertir a fecha local sin tiempo
  if (dateString.includes('GMT')) {
    const date = new Date(dateString);
    return new Date(date.getFullYear(), date.getMonth(), date.getDate());
  }
  
  return new Date(dateString);
};
```

---

## Notas Importantes

1. **Autenticación**: Todos los endpoints excepto `/api/login`, `/health`, `/api/test` y `/api/test-db` requieren token JWT
2. **Permisos**: Endpoints marcados como "solo administradores" requieren rol de administrador
3. **Cronogramas**: Al crear sesiones (terapia o pedagógicas), el sistema genera automáticamente el cronograma basado en los días de la semana especificados
4. **Estados**: Los recursos tienen estados que controlan su visibilidad y funcionalidad en el sistema
5. **Fechas**: Usar formato ISO (YYYY-MM-DD) para fechas y HH:MM:SS para horas
6. **Códigos de sesión**: Se generan automáticamente con formato "ST-YYYY-NNN" para terapia y "SP-YYYY-NNN" para pedagógicas
7. **Archivos**: Solo se aceptan archivos PDF para documentos de pacientes
8. **Logging**: Todas las operaciones se registran en logs diarios ubicados en `src/utils/general/LOGS/`

## Validaciones y Reglas de Negocio

### Validaciones Generales
- **Cédula**: Debe ser única en el sistema
- **Correo electrónico**: Formato válido y único por persona
- **Fechas**: No se permiten fechas futuras para fechas de nacimiento
- **Estados**: Solo valores predefinidos (`activo`, `inactivo`, etc.)

### Reglas de Negocio Específicas

#### Pacientes
- Un paciente debe tener un tutor asignado
- Un paciente puede tener múltiples especialidades asignadas
- El estado del paciente afecta su elegibilidad para nuevas sesiones

#### Sesiones de Terapia
- Los días de semana deben estar en formato: `"lunes,miercoles,viernes"`
- Días válidos: `lunes`, `martes`, `miercoles`, `jueves`, `viernes`, `sabado`, `domingo`
- La duración debe ser entre 30 y 180 minutos
- El terapeuta debe tener la especialidad asignada

#### Sesiones Pedagógicas
- Capacidad máxima entre 5 y 20 estudiantes
- La fecha de fin debe ser posterior a la fecha de inicio
- El número de clases programadas debe ser coherente con el rango de fechas

#### Documentos
- Solo archivos PDF son permitidos
- Tamaño máximo: 10MB por archivo
- Nombres de archivo se sanitizan automáticamente

### Campos de Auditoría
Todos los recursos incluyen campos de auditoría automáticos:
- `fecha_creacion`: Timestamp de creación
- `fecha_modificacion`: Timestamp de última modificación  
- `usuario_creacion`: ID del usuario que creó el registro
- `usuario_modificacion`: ID del usuario que hizo la última modificación

---

## Swagger UI

La documentación interactiva está disponible en:
```
http://localhost:5000/docs/
```

Cuando la aplicación esté ejecutándose, puedes acceder a la interfaz Swagger para probar los endpoints directamente.

### Características del Swagger UI
- **Autenticación**: Botón "Authorize" para configurar Bearer token
- **Try it out**: Ejecutar endpoints directamente desde la interfaz
- **Schemas**: Visualización completa de modelos de datos
- **Examples**: Valores de ejemplo para todos los parámetros
- **Response samples**: Ejemplos de respuestas exitosas y de error

### Configuración de Autenticación en Swagger
1. Hacer login via `/api/login` para obtener el token
2. Clickear el botón "Authorize" en Swagger UI
3. Introducir: `Bearer <su-token-jwt>`
4. Todos los endpoints protegidos funcionarán automáticamente