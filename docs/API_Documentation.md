# Documentación de Endpoints - API Centro Tía Glenda

## Información General
- **Base URL**: `http://localhost:5000`
- **Autenticación**: JWT Bearer Token
- **Formato**: JSON
- **Puerto por defecto**: 5000 (configurable via variable `PORT`)

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

### GET /api/sesiones-terapia/terapeuta/{terapeuta_id}
Sesiones asignadas a un terapeuta específico

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

### GET /api/roles
Listar roles disponibles en el sistema

---

## Códigos de Respuesta

### Exitosos
- **200**: Operación exitosa
- **201**: Recurso creado exitosamente

### Errores del Cliente
- **400**: Datos inválidos o malformados
- **401**: Token requerido o inválido
- **403**: Sin permisos suficientes (requiere admin)
- **404**: Recurso no encontrado

### Errores del Servidor
- **500**: Error interno del servidor

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

## Notas Importantes

1. **Autenticación**: Todos los endpoints excepto `/api/login`, `/health`, `/api/test` y `/api/test-db` requieren token JWT
2. **Permisos**: Endpoints marcados como "solo administradores" requieren rol de administrador
3. **Cronogramas**: Al crear sesiones (terapia o pedagógicas), el sistema genera automáticamente el cronograma basado en los días de la semana especificados
4. **Estados**: Los recursos tienen estados que controlan su visibilidad y funcionalidad en el sistema
5. **Fechas**: Usar formato ISO (YYYY-MM-DD) para fechas y HH:MM:SS para horas
6. **Códigos de sesión**: Se generan automáticamente con formato "ST-YYYY-NNN" para terapia y "SP-YYYY-NNN" para pedagógicas

---

## Swagger UI

La documentación interactiva está disponible en:
```
http://localhost:5000/docs/
```

Cuando la aplicación esté ejecutándose, puedes acceder a la interfaz Swagger para probar los endpoints directamente.