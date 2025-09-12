# Tests del Sistema de Reportes

Este documento describe la suite de tests implementada para el **Sistema de Reportes** del Centro Tía Glenda.

## Archivo de Tests

**Ubicación**: `tests/test_reportes_api.py`

## Cobertura de Tests

### 🔐 Tests de Autenticación
- **Login Admin**: Obtiene token de administrador para ejecutar tests
- **Login Personal**: Obtiene token de personal (o simula con admin si no existe)

### 📊 Tests de Endpoints de Reportes

#### Reportes Terapéuticos
- **Asistencia por Paciente**: Genera reporte de asistencia a sesiones terapéuticas
- **Progreso Terapéutico**: Evalúa el avance de pacientes en tratamiento

#### Reportes Pedagógicos  
- **Académico por Estudiante**: Rendimiento académico y asistencia de estudiantes
- **Rendimiento por Clase**: Efectividad de clases pedagógicas

#### Reportes Administrativos (Solo Admin)
- **Carga de Trabajo Personal**: Análisis de productividad del personal
- **Utilización de Recursos**: Uso de aulas y consultorios
- **Estadísticas Generales**: Indicadores clave del centro

#### Funcionalidad Base
- **Reportes Disponibles**: Lista de reportes según rol de usuario

### 📤 Tests de Exportación
- **Export PDF**: Exportación de reportes a formato PDF
- **Export Excel**: Exportación de reportes a formato Excel (XLSX)

### ✅ Tests de Validación y Seguridad
- **Validación de Filtros**: Verifica validación de fechas incorrectas
- **Acceso sin Token**: Confirma que se requiere autenticación
- **Permisos por Rol**: Verifica que personal no accede a reportes de admin

## Estructura de Tests

### Configuración
```python
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}
```

### Variables Globales
- `admin_token`: Token JWT de administrador
- `personal_token`: Token JWT de personal (si existe)
- `admin_user_info`: Información del usuario admin
- `personal_user_info`: Información del usuario personal

### Filtros de Prueba
Los tests utilizan filtros estándar:
```python
filtros = {
    "fecha_inicio": "2024-01-01",
    "fecha_fin": "2024-12-31"
}
```

## Casos de Test Específicos

### 1. Reportes con Datos
Cada test de reporte verifica:
- Status code 200
- Estructura de respuesta correcta
- Metadatos incluidos (total_registros, fecha_generación, etc.)

### 2. Exportación de Archivos
Tests de exportación verifican:
- Content-type correcto
- Archivo generado exitosamente
- Datos de prueba estructurados

### 3. Validación de Permisos
- Admin puede acceder a todos los reportes
- Personal solo accede a reportes permitidos
- Validación de filtros de fechas

## Datos de Prueba

### Estructura de Datos para Exportación
```python
export_data = {
    "data": [
        ["Paciente 1", "1234567890", "Sesión Terapia", "Psicología", "Terapeuta 1", 10, 8, 2, 80.0],
        ["Paciente 2", "0987654321", "Sesión Terapia", "Fonoaudiología", "Terapeuta 2", 12, 10, 2, 83.3]
    ],
    "metadata": {
        "tipo_reporte": "asistencia_paciente",
        "total_registros": 2,
        "fecha_generacion": "2024-XX-XX",
        "generado_por": "Test User"
    }
}
```

## Ejecución de Tests

### Individual
```bash
cd tests
python test_reportes_api.py
```

### Como parte del Suite Completo
```bash
cd tests
python test_api_complete_master.py
```

## Resultados Esperados

### Estados de Test
- **PASS**: Test exitoso
- **FAIL**: Test falló (funcionalidad incorrecta)  
- **ERROR**: Error técnico durante ejecución
- **SKIP**: Test omitido (condiciones no cumplidas)

### Casos de SKIP Comunes
- Token de admin no disponible
- Usuario de personal no existe en sistema
- Servidor no responde

## Configuración del Test Runner

El archivo utiliza `AdvancedTestRunner` con:
- **show_progress**: Barra de progreso en tiempo real
- **show_details**: Detalles de cada test
- **export_results**: Exporta resultados a `results_reportes.json`

## Integración con Test Master

El test está integrado en `test_api_complete_master.py` como:
```python
("REPORTES", "test_reportes_api.py")
```

## Dependencias

### Librerías Python
- `requests`: Para llamadas HTTP
- `json`: Manejo de datos JSON
- `datetime`: Manejo de fechas
- `tempfile`: Archivos temporales para exportación

### Servicios Requeridos
- Flask app corriendo en puerto 5000
- Base de datos PostgreSQL configurada
- Usuario admin.norte con contraseña admin123

## Troubleshooting

### Errores Comunes
1. **ConnectionError**: Verificar que Flask app esté corriendo
2. **401 Unauthorized**: Verificar credenciales de login
3. **Timeout**: Aumentar timeout para reportes con muchos datos
4. **Export Fails**: Verificar dependencias de reportlab y openpyxl

### Logs y Debugging
Los tests incluyen logging detallado con:
- Datos de respuesta (truncados a 200 chars)
- Códigos de error HTTP
- Mensajes de excepción

## Mantenimiento

### Actualizar Tests
Al agregar nuevos tipos de reporte:
1. Crear función `test_nuevo_reporte()`
2. Agregar a lista de tests en `main()`
3. Documentar en este README

### Datos de Test
Los filtros de fecha pueden requerir actualización anual para mantener relevancia de los datos de prueba.