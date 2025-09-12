# 🚀 ROADMAP DE MEJORAS - SISTEMA TÍA GLENDA

## 📋 Resumen General

Este documento detalla las mejoras prioritarias para el Sistema Tía Glenda, organizadas en 4 fases principales para optimizar la experiencia del **personal del centro (terapeutas y pedagogos)** y añadir funcionalidades esenciales para la gestión interna.

---

## 🎯 FASE 1: MEJORA DEL DASHBOARD

### 📊 Objetivo
Rediseñar el dashboard para mostrar datos más lógicos y útiles para **terapeutas y pedagogos**, facilitando la gestión de sus actividades diarias.

### 🔍 Tareas a Realizar

#### 1.1 Auditoría de Rutas del Backend
**Estado:** 🔍 Pendiente Análisis
- [ ] Revisar todas las rutas existentes en `src/api/routes/api_routes.py`
- [ ] Evaluar endpoints de estadísticas actuales
- [ ] Identificar rutas que sirven datos para dashboard
- [ ] Documentar qué endpoints están funcionando correctamente
- [ ] Identificar endpoints que necesitan mejoras o reemplazo

#### 1.2 Análisis de Datos Necesarios
**Estado:** 🔍 Pendiente Análisis
- [ ] **Dashboard para Terapeutas:**
  - Mis sesiones del día/semana
  - Pacientes asignados y su progreso
  - Sesiones pendientes por realizar
  - Histórico de sesiones completadas
  
- [ ] **Dashboard para Pedagogos:**
  - Mis clases del día/semana
  - Estudiantes en mis grupos
  - Clases pendientes por realizar
  - Rendimiento de mis grupos
  
- [ ] **Dashboard Administrativo (Administradores):**
  - Resumen general de actividades del centro
  - Personal activo y disponibilidad
  - Estadísticas de ocupación de consultorios/aulas
  - Alertas del sistema

#### 1.3 Nuevos Endpoints Necesarios
**Estado:** ✏️ Por Implementar
- [ ] `GET /api/dashboard/mis-sesiones-hoy` (para terapeutas)
- [ ] `GET /api/dashboard/mis-clases-hoy` (para pedagogos)
- [ ] `GET /api/dashboard/mis-pacientes` (para terapeutas)
- [ ] `GET /api/dashboard/mis-estudiantes` (para pedagogos)
- [ ] `GET /api/dashboard/estadisticas-personal` (datos del personal logueado)
- [ ] `GET /api/dashboard/notificaciones-pendientes`

#### 1.4 Rediseño del Frontend Dashboard
**Estado:** 🎨 Por Diseñar
- [ ] **Dashboard Personalizado por Rol:**
  - Vista específica para terapeutas
  - Vista específica para pedagogos  
  - Vista específica para administradores
- [ ] **Componentes Intuitivos:**
  - Tarjetas de "Mis actividades de hoy"
  - Calendario semanal personalizado
  - Lista de tareas pendientes
  - Accesos rápidos a funciones frecuentes

---

## 📊 FASE 2: REESTRUCTURACIÓN DE REPORTES

### 🎯 Objetivo
Transformar la sección "Consultas y Reportes" en una sección optimizada de "Reportes y Estadísticas".

### 🔍 Tareas a Realizar

#### 2.1 Auditoría de Funcionalidades Actuales
**Estado:** 🔍 Pendiente Análisis
- [ ] Revisar qué hay en la sección actual de "Consultas"
- [ ] Identificar reportes útiles vs obsoletos
- [ ] Evaluar funcionalidades de exportación existentes

#### 2.2 Nuevos Reportes Sugeridos

##### 📈 Reportes de Sesiones Terapéuticas
- [ ] **Reporte de Asistencia por Paciente**
  - Gráfico de tendencia de asistencia
  - Porcentaje de sesiones completadas
  - Identificación de pacientes con baja asistencia
  
- [ ] **Reporte de Progreso Terapéutico**
  - Evolución de objetivos por paciente
  - Observaciones más frecuentes
  - Tiempo promedio de tratamiento
  
- [ ] **Reporte de Carga de Trabajo del Personal**
  - Sesiones por terapeuta
  - Horas trabajadas vs planificadas
  - Especialidades más demandadas

##### 📚 Reportes de Sesiones Pedagógicas
- [ ] **Reporte Académico por Estudiante**
  - Progreso en competencias
  - Asistencia a clases
  - Evaluaciones y calificaciones
  
- [ ] **Reporte de Rendimiento por Clase**
  - Participación estudiantil
  - Objetivos alcanzados
  - Materiales más utilizados

##### 📋 Reportes Administrativos
- [ ] **Reporte Financiero**
  - Ingresos por tipo de sesión
  - Costos operativos
  - Análisis de rentabilidad
  
- [ ] **Reporte de Utilización de Recursos**
  - Ocupación de aulas/consultorios
  - Uso de materiales
  - Eficiencia de horarios

#### 2.3 Funcionalidades de Exportación
**Estado:** 🔧 Por Implementar
- [ ] Exportación a PDF con gráficos
- [ ] Exportación a Excel con datos detallados
- [ ] Programación de reportes automáticos
- [ ] Sistema de suscripción a reportes por email

#### 2.4 Interfaz de Usuario Mejorada
**Estado:** 🎨 Por Diseñar
- [ ] Panel de filtros avanzados
- [ ] Vista previa de reportes
- [ ] Guardado de configuraciones favoritas
- [ ] Historial de reportes generados

---

## ⚙️ FASE 3: CONFIGURACIÓN DEL SISTEMA

### 🎯 Objetivo
Crear un módulo completo de configuración del sistema que permita personalizar y administrar diversos aspectos operativos.

### 🔍 Categorías de Configuración

#### 3.1 Configuración General
**Estado:** ✏️ Por Implementar
- [ ] **Información del Centro**
  - Nombre del centro
  - Logo institucional
  - Dirección y contacto
  - Horarios de operación
  
- [ ] **Configuración Regional**
  - Zona horaria
  - Formato de fecha y hora
  - Moneda local
  - Idioma del sistema

#### 3.2 Configuración de Sesiones
**Estado:** ✏️ Por Implementar
- [ ] **Sesiones Terapéuticas**
  - Duración predeterminada por especialidad
  - Tiempo de tolerancia para llegadas tardías
  - Configuración de recordatorios automáticos
  - Políticas de cancelación y reprogramación
  
- [ ] **Sesiones Pedagógicas**
  - Configuración de niveles académicos
  - Capacidad máxima por clase
  - Sistema de calificaciones
  - Períodos académicos

#### 3.3 Configuración de Notificaciones Push
**Estado:** 🔔 Por Implementar
- [ ] **Notificaciones de Horarios de Sesiones**
  - Recordatorios para terapeutas 15 min antes de sesión terapéutica
  - Recordatorios para pedagogos 15 min antes de clase
  - Notificaciones de sesiones reprogramadas
  - Alertas de cancelaciones de último momento
  
- [ ] **Configuración Personalizable**
  - Tiempo de anticipación configurable por usuario (5, 10, 15, 30 min)
  - Activar/desactivar notificaciones por tipo de sesión
  - Sonidos diferenciados por tipo de notificación
  - Modo silencioso en horarios específicos
  
- [ ] **Notificaciones del Sistema**
  - Cambios en cronogramas personales
  - Asignación de nuevos pacientes/estudiantes  
  - Mensajes del chat interno
  - Actualizaciones importantes del sistema

#### 3.4 Configuración de Usuarios y Permisos
**Estado:** 🔐 Por Implementar
- [ ] **Roles y Permisos**
  - Creación de roles personalizados
  - Asignación granular de permisos
  - Perfiles de acceso por módulo
  
- [ ] **Seguridad del Sistema**
  - Políticas de contraseñas
  - Tiempo de sesión automática
  - Registro de actividades (audit log)

#### 3.5 Configuración de Respaldos y Mantenimiento
**Estado:** 💾 Por Implementar
- [ ] **Respaldos Automáticos**
  - Frecuencia de respaldos
  - Ubicación de almacenamiento
  - Retención de archivos históricos
  
- [ ] **Mantenimiento del Sistema**
  - Limpieza automática de logs
  - Optimización de base de datos
  - Actualizaciones programadas

---

## 💬 FASE 4: SISTEMA DE CHAT INTERNO

### 🎯 Objetivo
Implementar un sistema de mensajería interna que permita comunicación eficiente entre usuarios del sistema.

### 🔍 Tareas a Realizar

### 🔔 Sistema de Notificaciones Push Integrado

#### Casos de Uso Específicos (Solo para Personal):
- **Terapeuta recibe**: "Sesión con Juan Pérez en 15 minutos - Consultorio 3"
- **Pedagogo recibe**: "Clase de Matemáticas Nivel Primario en 15 minutos - Aula 2"  
- **Reprogramación**: "Tu sesión del 10/09 14:00 ha sido reprogramada para 11/09 14:00"
- **Cancelación**: "Sesión con María García - Hoy 15:00 ha sido cancelada"
- **Asignaciones**: "Nuevo paciente asignado: Ana López - Primera sesión mañana 10:00"
- **Chat**: "Nuevo mensaje de Dr. Martínez"

#### Implementación Técnica:
- **Backend**: Job scheduler que revisa cronogramas cada minuto
- **Frontend**: Service Workers para mostrar notificaciones nativas del navegador
- **Base de Datos**: Tabla de notificaciones con estado (enviada/leída/descartada)
- **Tiempo Real**: WebSockets para entrega instantánea

---

## 💬 FASE 4: SISTEMA DE CHAT INTERNO

#### 4.1 Auditoría del Backend Existente
**Estado:** 🔍 Pendiente Análisis
- [ ] Revisar tabla `mensajes_chat` en base de datos
- [ ] Verificar endpoints existentes en `api_routes.py`
- [ ] Evaluar funcionalidades ya implementadas
- [ ] Identificar gaps y mejoras necesarias

#### 4.2 Backend del Sistema de Chat
**Estado:** 🔧 Por Implementar/Mejorar

##### Endpoints Necesarios:
- [ ] `GET /api/chat/conversaciones` - Lista de conversaciones
- [ ] `GET /api/chat/conversacion/{user_id}` - Mensajes con usuario específico
- [ ] `POST /api/chat/enviar` - Enviar nuevo mensaje
- [ ] `PUT /api/chat/marcar-leido/{message_id}` - Marcar como leído
- [ ] `GET /api/chat/usuarios-disponibles` - Lista usuarios para chat
- [ ] `GET /api/chat/notificaciones` - Mensajes no leídos

##### Funcionalidades Avanzadas:
- [ ] **Notificaciones en Tiempo Real**
  - Integración con WebSockets o Server-Sent Events
  - Notificaciones push de nuevos mensajes
  - Estado "en línea" de usuarios
  
- [ ] **Tipos de Mensaje**
  - Mensajes de texto
  - Archivos adjuntos (imágenes, documentos)
  - Mensajes del sistema (automáticos)
  
- [ ] **Organización de Conversaciones**
  - Chat individual entre usuarios
  - Grupos por departamento/especialidad
  - Mensajes oficiales/anuncios

#### 4.3 Frontend del Sistema de Chat
**Estado:** 🎨 Por Implementar

##### Interfaz Principal:
- [ ] **Panel de Conversaciones**
  - Lista de conversaciones activas
  - Búsqueda de usuarios
  - Indicadores de mensajes no leídos
  
- [ ] **Ventana de Chat**
  - Interfaz de mensajería moderna
  - Envío de archivos adjuntos
  - Timestamps y estado de lectura
  
- [ ] **Características UX**
  - Chat flotante/modal
  - Notificaciones de escritorio
  - Sonidos de notificación
  - Modo oscuro/claro

##### Integraciones:
- [ ] **Acceso Rápido**
  - Icono de chat en navbar
  - Contador de mensajes no leídos
  - Shortcuts de teclado
  
- [ ] **Contextual**
  - Chat rápido desde perfil de usuario
  - Mensajes relacionados con pacientes
  - Notificaciones integradas con el sistema

#### 4.4 Características Avanzadas
**Estado:** 🚀 Futuro

- [ ] **Chat de Video/Audio** (Opcional)
- [ ] **Mensajes Programados**
- [ ] **Historial de Conversaciones**
- [ ] **Búsqueda en Mensajes**
- [ ] **Integración con Notificaciones Email**

---

## 📅 CRONOGRAMA SUGERIDO

### 🗓️ Semana 1-2: FASE 1 (Dashboard)
- Días 1-3: Auditoría de rutas backend
- Días 4-7: Implementación de nuevos endpoints
- Días 8-14: Rediseño de frontend dashboard

### 🗓️ Semana 3-4: FASE 2 (Reportes)
- Días 15-18: Auditoría de reportes actuales
- Días 19-25: Implementación de nuevos reportes
- Días 26-28: Interfaz de reportes mejorada

### 🗓️ Semana 5: FASE 3 (Configuración)
- Días 29-32: Backend de configuración
- Días 33-35: Frontend de configuración

### 🗓️ Semana 6: FASE 4 (Chat)
- Días 36-38: Auditoría y backend de chat
- Días 39-42: Frontend de chat e integración

---

## 🛠️ STACK TECNOLÓGICO SUGERIDO

### Backend
- **Framework**: Flask (actual)
- **Base de Datos**: PostgreSQL (actual)
- **Tiempo Real**: Flask-SocketIO para chat
- **Reportes**: ReportLab para PDFs, openpyxl para Excel

### Frontend  
- **Framework**: React (actual)
- **UI Library**: Material-UI (actual)
- **Gráficos**: Chart.js o Recharts
- **Tiempo Real**: Socket.IO-client
- **Estado**: Context API + useReducer

### Herramientas
- **Notificaciones Push**: Web Push API + Service Workers
- **Archivos**: Multer para uploads
- **Tiempo Real**: WebSockets para notificaciones instantáneas
- **Documentación**: Swagger (actual)

---

## 🎯 CRITERIOS DE ÉXITO

### Métricas de Dashboard
- ✅ Tiempo de carga < 2 segundos
- ✅ Datos actualizados en tiempo real
- ✅ 100% de endpoints funcionando correctamente

### Métricas de Reportes
- ✅ 5+ tipos de reportes disponibles
- ✅ Exportación a múltiples formatos
- ✅ Filtros avanzados funcionales

### Métricas de Configuración
- ✅ Todas las configuraciones persistentes
- ✅ Interface intuitiva y fácil de usar
- ✅ Validaciones robustas

### Métricas de Chat
- ✅ Mensajes entregados < 1 segundo
- ✅ Notificaciones en tiempo real
- ✅ Interfaz responsive y moderna

---

## ⚠️ CONSIDERACIONES IMPORTANTES

### Seguridad
- 🔒 Validación de permisos en todos los endpoints nuevos
- 🔒 Sanitización de inputs en chat y configuraciones
- 🔒 Auditoría de cambios en configuración del sistema

### Performance
- ⚡ Paginación en reportes grandes
- ⚡ Cache para estadísticas de dashboard  
- ⚡ Optimización de queries de base de datos

### Escalabilidad
- 📈 Diseño modular para futuras expansiones
- 📈 APIs RESTful bien documentadas
- 📈 Separación clara de responsabilidades

### Compatibilidad
- 🌐 Soporte para múltiples navegadores
- 📱 Diseño responsive para móviles
- 🔄 Compatibilidad con versiones anteriores

---

*Documento creado el: 10 de Septiembre, 2025*  
*Última actualización: 10 de Septiembre, 2025*

**Nota:** Este roadmap debe ser revisado y ajustado según las prioridades del negocio y recursos disponibles.