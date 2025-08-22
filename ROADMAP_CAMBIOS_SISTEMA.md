# Roadmap de Cambios - Sistema Centro Tía Glenda

# Falta fase 4 INCOMPETENTE 

## Resumen Ejecutivo
Este documento consolida y organiza los cambios planificados para el sistema de gestión del Centro Tía Glenda, incluyendo la implementación de un sistema multi-centro (Norte y Sur), mejoras en los módulos existentes y nuevas funcionalidades.

## 1. IMPLEMENTACIÓN MULTI-CENTRO

### 1.1 Base de Datos
- **Nueva tabla**: `centros`
  - `id_centro` (PK)
  - `nombre_centro` (Norte/Sur)
  - `direccion`
  - `horario_operacion`
  - `estado` (activo/inactivo)

- **Modificaciones a tablas existentes**: Agregar campo `id_centro` como FK a:
  - `usuarios`
  - `personal`
  - `pacientes`
  - `sesion_terapia`
  - `sesion_pedagogica`

### 1.2 Sistema de Login
- Selector de centro en pantalla de login
- Filtrado automático de datos según centro seleccionado
- Sessions separadas por centro

### 1.3 Gestión de Horarios
- **Centro Norte**: Operación matutina
- **Centro Sur**: Operación vespertina
- Configuración flexible de horarios por centro

## 2. MÓDULO USUARIOS

### 2.1 Perfil de Usuario
- **Campo nuevo**: `foto_perfil` (BYTEA o VARCHAR para ruta)
- Funcionalidad de subida de imágenes
- Vista de perfil personalizada

### 2.2 Sistema de Chat
- **Nueva tabla**: `mensajes_chat`
  - `id_mensaje` (PK)
  - `id_remitente` (FK usuarios)
  - `id_destinatario` (FK usuarios)
  - `mensaje` (TEXT)
  - `fecha_envio` (TIMESTAMP)
  - `leido` (BOOLEAN)
  - `id_centro` (FK centros)

## 3. MÓDULO PERSONAL

### 3.1 Especialidades Múltiples
- **Nueva tabla**: `personal_especialidades`
  - `id_personal` (FK)
  - `id_especialidad` (FK)
  - `fecha_asignacion`

### 3.2 Gestión de Documentos
- **Nueva tabla**: `documentos_personal`
  - `id_documento` (PK)
  - `id_personal` (FK)
  - `tipo_documento` (cedula, curriculum, certificados, etc.)
  - `nombre_archivo`
  - `ruta_archivo`
  - `fecha_subida`

### 3.3 Roles y Permisos
- **Administradores**: Acceso completo a todos los módulos
- **Terapeutas/Pedagogos**: 
  - Solo consulta de citas asignadas
  - Edición de perfil propio
  - Información no sensible de pacientes

## 4. MÓDULO PACIENTES

### 4.1 Especialidades Múltiples
- **Nueva tabla**: `paciente_especialidades`
  - `id_paciente` (FK)
  - `id_especialidad` (FK)
  - `fecha_asignacion`
  - `estado` (activo/pausado)

### 4.2 Control de Pausas
- **Campos nuevos en `pacientes`**:
  - `fecha_inicio_pausa` (DATE)
  - `fecha_fin_pausa` (DATE)
  - `motivo_pausa` (TEXT)
  - `estado_tratamiento` (activo/pausado/finalizado)

### 4.3 Vista Detallada
- Integración de información de sesiones
- Historial de asistencias
- Información de tutores
- Exportación a PDF

## 5. MÓDULO TUTORES

### 5.1 Información Laboral
- **Campos nuevos**:
  - `ocupacion` (VARCHAR)
  - `direccion_empresa` (VARCHAR)
  - `telefono_empresa` (VARCHAR)
  - `nombre_empresa` (VARCHAR)

## 6. MÓDULO ESPECIALIDADES

### 6.1 Correcciones
- Fix en funcionalidad de editar especialidades
- Validaciones mejoradas

## 7. MÓDULOS DE SESIONES

### 7.1 Sesiones Terapéuticas
- **Búsqueda avanzada**: Por terapeuta o paciente
- **Integración de horarios** en vista principal
- **Cálculo automático de honorarios**:
  - 15% total: 10% terapeuta, 5% centro
- **Reprogramación individual** de sesiones
- Exportación a PDF

### 7.2 Sesiones Pedagógicas
- **Reprogramación individual** de sesiones
- Mejora en organización de vistas
- Integración con cronograma

### 7.3 Sistema de Observaciones
- **Nueva tabla**: `observaciones_sesiones`
  - `id_observacion` (PK)
  - `id_sesion` (FK - puede ser terapéutica o pedagógica)
  - `tipo_sesion` (terapeutica/pedagogica)
  - `id_usuario` (FK usuarios)
  - `observacion` (TEXT)
  - `tipo_observacion` (falta, observacion, nota)
  - `fecha_registro` (TIMESTAMP)

## 8. DASHBOARD Y ESTADÍSTICAS

### 8.1 Métricas por Centro
- Estadísticas separadas por centro
- Comparativas Norte vs Sur
- Indicadores de rendimiento

### 8.2 Reportes
- Asistencias por centro
- Rendimiento de personal
- Ocupación de horarios

## 9. SECURITY Y PERMISOS

### 9.1 Información Sensible
- **Administradores**: Acceso completo
- **Terapeutas/Pedagogos**: Información limitada
  - Sin acceso a números telefónicos completos
  - Sin acceso a direcciones completas
  - Solo información necesaria para el tratamiento

## 10. FASES DE IMPLEMENTACIÓN

### Fase 1: Base Multi-Centro
1. Crear tabla centros
2. Modificar sistema de login
3. Implementar filtrado por centro

### Fase 2: Módulos Core
1. Especialidades múltiples (Personal y Pacientes)
2. Sistema de documentos
3. Control de pausas en pacientes

### Fase 3: Funcionalidades Avanzadas
1. Sistema de chat
2. Fotos de perfil
3. Sistema de observaciones

### Fase 4: Reportes y Estadísticas
1. Dashboard mejorado
2. Exportación PDF
3. Métricas por centro

## 11. CONSIDERACIONES TÉCNICAS

### Base de Datos
- Migrations para tablas existentes
- Índices para campos de filtrado por centro
- Triggers para mantener integridad referencial

### Backend (Flask)
- Middleware para filtrado automático por centro
- Nuevos endpoints para funcionalidades
- Validaciones de permisos por rol

### Frontend
- Selector de centro en login
- Interfaces diferenciadas por rol
- Componentes para subida de archivos

### Seguridad
- Validación de permisos por centro
- Encriptación de documentos sensibles
- Audit trail de cambios importantes