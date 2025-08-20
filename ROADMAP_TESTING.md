# Roadmap de Testing - Sistema Centro Tía Glenda

## Resumen Ejecutivo
Este documento define la estrategia completa de testing para todas las funcionalidades del sistema Centro Tía Glenda, incluyendo los módulos existentes y las nuevas funcionalidades implementadas en las Fases 2 y 3.

## 📋 Estado Actual de Tests

### Tests Existentes ✅
1. **test_autenticacion_api.py** - Sistema de autenticación y JWT
2. **test_personas_api.py** - CRUD de personas
3. **test_usuarios_api.py** - Gestión de usuarios
4. **test_roles_api.py** - Gestión de roles
5. **test_personal_api.py** - Gestión de personal
6. **test_pacientes_api.py** - Gestión de pacientes
7. **test_tutores_api.py** - Gestión de tutores
8. **test_especialidades_api.py** - Gestión de especialidades
9. **test_sesiones_terapia_api.py** - Sesiones terapéuticas
10. **test_sesiones_pedagogicas_api.py** - Sesiones pedagógicas
11. **test_documentos_pacientes_api.py** - Documentos de pacientes
12. **test_units.py** - Tests unitarios
13. **test_api_complete_master.py** - Test runner maestro

### Tests Faltantes ❌
1. **test_chat_api.py** - Sistema de chat (Fase 3)
2. **test_fotos_perfil_api.py** - Fotos de perfil (Fase 3)
3. **test_observaciones_api.py** - Sistema de observaciones (Fase 3)
4. **test_especialidades_multiples_api.py** - Especialidades múltiples (Fase 2)
5. **test_documentos_personal_api.py** - Documentos de personal (Fase 2)
6. **test_control_pausas_api.py** - Control de pausas en pacientes (Fase 2)
7. **test_integracion_completa.py** - Tests de integración entre módulos

## 🎯 Plan de Testing por Módulos

### **FASE 1: Tests para Nuevas Funcionalidades (Fases 2-3)**

#### 1. Sistema de Chat (`test_chat_api.py`)
**Endpoints a probar:**
- `POST /api/chat/enviar` - Enviar mensaje
- `GET /api/chat/conversaciones` - Obtener conversaciones
- `GET /api/chat/mensajes/{id_contacto}` - Mensajes de conversación
- `PUT /api/chat/marcar-leido/{id_mensaje}` - Marcar como leído
- `GET /api/chat/usuarios-disponibles` - Usuarios disponibles
- `GET /api/chat/estadisticas` - Estadísticas de mensajes
- `GET /api/chat/buscar` - Buscar mensajes

**Casos de prueba:**
- ✅ Envío exitoso de mensajes
- ✅ Validación de permisos por centro
- ✅ Prevención de auto-mensajes
- ✅ Marcado correcto de mensajes leídos
- ✅ Filtrado de mensajes privados
- ✅ Búsqueda con diferentes criterios
- ❌ Envío con datos inválidos
- ❌ Acceso sin autenticación

#### 2. Fotos de Perfil (`test_fotos_perfil_api.py`)
**Endpoints a probar:**
- `POST /api/perfil/foto` - Subir foto propia
- `GET /api/perfil/foto` - Obtener foto propia
- `DELETE /api/perfil/foto` - Eliminar foto propia
- `POST /api/usuarios/{id}/foto` - Admin: subir foto
- `GET /api/usuarios/{id}/foto` - Ver foto de usuario
- `DELETE /api/usuarios/{id}/foto` - Admin: eliminar foto
- `GET /api/fotos-perfil/estadisticas` - Estadísticas
- `GET /api/fotos-perfil/formatos` - Formatos soportados

**Casos de prueba:**
- ✅ Subida exitosa de imagen válida
- ✅ Validación de tipos de archivo
- ✅ Redimensionamiento automático
- ✅ Control de permisos admin vs usuario
- ✅ Eliminación correcta de archivos
- ❌ Subida de archivos muy grandes
- ❌ Formatos no soportados
- ❌ Acceso sin permisos

#### 3. Sistema de Observaciones (`test_observaciones_api.py`)
**Endpoints a probar:**
- `POST /api/observaciones` - Crear observación
- `GET /api/observaciones/sesion/{id}/{tipo}` - Observaciones de sesión
- `GET /api/observaciones/{id}` - Observación específica
- `PUT /api/observaciones/{id}` - Actualizar observación
- `DELETE /api/observaciones/{id}` - Eliminar observación
- `GET /api/observaciones/estadisticas` - Estadísticas
- `GET /api/observaciones/seguimientos-pendientes` - Seguimientos
- `GET /api/observaciones/buscar` - Búsqueda avanzada

**Casos de prueba:**
- ✅ Creación de observaciones por tipo
- ✅ Validación de permisos por sesión
- ✅ Filtrado de observaciones privadas
- ✅ Sistema de seguimiento
- ✅ Búsqueda con múltiples criterios
- ❌ Creación sin permisos
- ❌ Observaciones con datos inválidos

#### 4. Especialidades Múltiples (`test_especialidades_multiples_api.py`)
**Funcionalidades a probar:**
- Asignación múltiple para personal
- Asignación múltiple para pacientes
- Especialidad principal
- Control de competencias
- Validación de compatibilidad

**Casos de prueba:**
- ✅ Asignación exitosa de múltiples especialidades
- ✅ Designación de especialidad principal
- ✅ Validación personal-especialidad compatible
- ✅ Control de estados y fechas
- ❌ Asignación duplicada
- ❌ Especialidades incompatibles

#### 5. Documentos de Personal (`test_documentos_personal_api.py`)
**Funcionalidades a probar:**
- Subida de documentos
- Validación por administradores
- Control de vencimientos
- Documentos obligatorios vs opcionales
- Acceso por permisos

**Casos de prueba:**
- ✅ Subida exitosa de documentos
- ✅ Validación por admin
- ✅ Control de documentos obligatorios
- ✅ Alertas de vencimiento
- ❌ Acceso a documentos confidenciales sin permisos

#### 6. Control de Pausas (`test_control_pausas_api.py`)
**Funcionalidades a probar:**
- Pausa general de paciente
- Pausa por especialidad
- Reanudación de tratamientos
- Historial de pausas
- Detección de pausas vencidas

**Casos de prueba:**
- ✅ Pausa general correcta
- ✅ Pausa específica por especialidad
- ✅ Reanudación automática
- ✅ Historial completo
- ❌ Pausa de paciente ya pausado
- ❌ Fechas inválidas

### **FASE 2: Actualización de Tests Existentes**

#### Actualizaciones Necesarias:
1. **test_personal_api.py** - Integrar especialidades múltiples
2. **test_pacientes_api.py** - Integrar control de pausas y especialidades
3. **test_sesiones_terapia_api.py** - Integrar observaciones
4. **test_sesiones_pedagogicas_api.py** - Integrar observaciones
5. **test_usuarios_api.py** - Integrar fotos de perfil

### **FASE 3: Tests de Integración**

#### 1. Test de Integración Completa (`test_integracion_completa.py`)
**Flujos a probar:**
- Registro completo de paciente con especialidades múltiples
- Asignación de personal con especialidades compatibles
- Creación de sesiones con observaciones
- Flujo completo de pausa y reanudación
- Comunicación entre usuarios via chat
- Gestión completa de documentos

#### 2. Test de Rendimiento
- Carga simultánea de usuarios
- Múltiples operaciones de chat
- Subida masiva de documentos
- Consultas complejas de observaciones

### **FASE 4: Actualización del Test Runner**

#### Mejoras al `test_api_complete_master.py`:
- Incluir todos los nuevos módulos
- Reporte detallado por funcionalidad
- Métricas de coverage por módulo
- Tests de regresión automatizados
- Configuración flexible de tests

## 📊 Métricas de Testing

### Objetivos de Coverage:
- **Endpoints API**: 100% de cobertura
- **Casos de éxito**: 100% cubiertos
- **Casos de error**: 90% cubiertos
- **Validaciones de seguridad**: 100% cubiertas
- **Tests de integración**: 80% de flujos principales

### Tipos de Tests:
1. **Unitarios** (30%): Funciones específicas
2. **Integración** (50%): Interacción entre módulos
3. **End-to-End** (15%): Flujos completos
4. **Seguridad** (5%): Validaciones de permisos

## ⚡ Plan de Ejecución

### Semana 1: Tests Nuevos Módulos
- Días 1-2: Sistema de chat
- Días 3-4: Fotos de perfil y observaciones
- Días 5-7: Especialidades múltiples y control de pausas

### Semana 2: Actualización y Optimización
- Días 1-3: Actualizar tests existentes
- Días 4-5: Tests de integración
- Días 6-7: Optimización del test runner

### Semana 3: Validación y Documentación
- Días 1-3: Ejecución completa y correcciones
- Días 4-5: Documentación de tests
- Días 6-7: Setup de CI/CD para tests automáticos

## 🔧 Herramientas y Configuración

### Dependencias de Testing:
```python
# Existentes
import requests
import json
import unittest
import time

# Nuevas para archivos
import io
import os
from PIL import Image

# Para tests de rendimiento
import threading
import concurrent.futures
```

### Estructura de Archivos de Test:
```
tests/
├── test_chat_api.py                    # Nuevo
├── test_fotos_perfil_api.py           # Nuevo
├── test_observaciones_api.py          # Nuevo
├── test_especialidades_multiples_api.py # Nuevo
├── test_documentos_personal_api.py    # Nuevo
├── test_control_pausas_api.py         # Nuevo
├── test_integracion_completa.py       # Nuevo
├── test_api_complete_master.py        # Actualizar
└── utils/
    ├── advanced_test_runner.py        # Actualizar
    ├── test_helpers.py                # Nuevo
    └── mock_data.py                   # Nuevo
```

## 🎯 Criterios de Éxito

### Para cada módulo nuevo:
- ✅ 100% de endpoints cubiertos
- ✅ Casos positivos y negativos
- ✅ Validación de permisos
- ✅ Tests de datos inválidos
- ✅ Verificación de integración con DB

### Para el sistema completo:
- ✅ Todos los tests pasan sin errores
- ✅ Tiempo de ejecución < 10 minutos
- ✅ Cobertura > 90% de funcionalidades críticas
- ✅ Tests automatizados en CI/CD
- ✅ Documentación completa de casos de test

Este roadmap asegura la calidad y estabilidad de todas las funcionalidades implementadas en el sistema Centro Tía Glenda.