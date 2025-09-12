# Configuración de Sistema por Centro - Implementación

## Contexto
El sistema "Centro Tía Glenda" maneja múltiples centros (Norte, Sur) y necesita un sistema de configuración específico por centro. Cada usuario puede configurar solo su centro asignado.

## Estado Actual de la Base de Datos

### Tabla `centros` (Ya existe)
```sql
CREATE TABLE centros (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(10) NOT NULL UNIQUE, -- Norte/Sur
    direccion VARCHAR(255),
    telefono VARCHAR(15),
    email VARCHAR(150),
    
    -- Configuración de horarios
    horario_apertura TIME DEFAULT '07:00',
    horario_cierre TIME DEFAULT '18:00',
    
    -- Configuración de turnos
    turno_principal VARCHAR(20) DEFAULT 'mixto',
    
    -- Estado y control
    estado VARCHAR(10) DEFAULT 'activo',
    observaciones TEXT,
    
    -- Campos de auditoría
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_modificacion INTEGER
);
```

### Datos del Usuario (Token JWT)
Cuando un usuario hace login, el token incluye:
```json
{
  "user": {
    "centro": {
      "codigo": "NORTE",
      "id": 1,
      "nombre": "Centro Norte",
      "turno": "matutino"
    },
    "id": 1,
    "usuario": "admin.norte"
  }
}
```

## Arquitectura Propuesta

### 1. Backend - Estructura
```
src/api/
├── Components/
│   └── ConfiguracionComponent.py
├── Service/
│   └── ConfiguracionService.py
└── routes/
    └── api_routes.py
```

### 2. Endpoints Necesarios
```python
# GET /api/configuracion/general - Obtener config del centro del usuario
# PUT /api/configuracion/general - Actualizar config del centro del usuario
```

### 3. Mapeo de Campos
**Tabla `centros` → Frontend**:
- `nombre` → `nombreCentro`
- `direccion` → `direccion`  
- `telefono` → `telefono`
- `email` → `email`
- `horario_apertura` → `horarioInicio`
- `horario_cierre` → `horarioFin`
- `observaciones` → `descripcion`

**Campos adicionales (valores fijos)**:
- `zonaHoraria: 'America/Guayaquil'`
- `formatoFecha: 'DD/MM/YYYY'`
- `formatoHora: '24h'`
- `moneda: 'USD'`
- `idioma: 'es'`

## Implementación Backend

### ConfiguracionComponent.py
```python
def get_configuracion_general(self, centro_id):
    """Obtener configuración del centro específico"""
    query = """
        SELECT 
            nombre as nombre_centro,
            direccion,
            telefono,
            email,
            horario_apertura as horario_inicio,
            horario_cierre as horario_fin,
            observaciones as descripcion
        FROM centros 
        WHERE id = %s
    """
    result = self.db.getRecords(query, (centro_id,))
    # Procesar resultado y agregar campos fijos

def update_configuracion_general(self, data, centro_id):
    """Actualizar configuración del centro específico"""
    query = """
        UPDATE centros SET
            nombre = %s,
            direccion = %s,
            telefono = %s,
            email = %s,
            horario_apertura = %s,
            horario_cierre = %s,
            observaciones = %s
        WHERE id = %s
    """
    # Ejecutar update
```

### ConfiguracionService.py
```python
@staticmethod
def get_configuracion_general():
    # Obtener centro_id del usuario actual
    centro_id = request.current_user.get('id_centro')
    
    component = ConfiguracionComponent()
    result = component.get_configuracion_general(centro_id)
    return response_success(result['data'])

@staticmethod  
def update_configuracion_general():
    data = request.get_json()
    centro_id = request.current_user.get('id_centro')
    
    # Mapear datos frontend → backend
    backend_data = {
        'nombre_centro': data.get('nombreCentro'),
        'direccion': data.get('direccion'),
        'telefono': data.get('telefono'),
        'email': data.get('email'),
        'horario_inicio': data.get('horarioInicio'),
        'horario_fin': data.get('horarioFin'),
        'descripcion': data.get('descripcion')
    }
    
    component = ConfiguracionComponent()
    result = component.update_configuracion_general(backend_data, centro_id)
    return response_success(None, "Configuración actualizada")
```

## Implementación Frontend

### ConfiguracionService.js
```javascript
class ConfiguracionService {
  static async getConfiguracionGeneral() {
    const response = await ApiService.get('/api/configuracion/general');
    return response.data;
  }

  static async updateConfiguracionGeneral(configuracion) {
    const response = await ApiService.put('/api/configuracion/general', configuracion);
    return response.data;
  }
}
```

### ConfiguracionGeneral.jsx
```jsx
import { useAuth } from '../../contexts/AuthContext';

const ConfiguracionGeneral = ({ configuracion, onSave }) => {
  const { user } = useAuth();
  
  const [formData, setFormData] = useState({
    nombreCentro: '',
    direccion: '',
    telefono: '',
    email: '',
    horarioInicio: '08:00',
    horarioFin: '17:00',
    zonaHoraria: 'America/Guayaquil',
    formatoFecha: 'DD/MM/YYYY',
    formatoHora: '24h',
    moneda: 'USD',
    idioma: 'es',
    descripcion: '',
    ...configuracion
  });

  return (
    <Card>
      <CardContent>
        <Box mb={3}>
          <Typography variant="h6">
            <Business sx={{ mr: 1 }} />
            Configuración del Centro
          </Typography>
          {user?.centro && (
            <Chip 
              label={`${user.centro.nombre} (${user.centro.codigo})`}
              color="primary"
              variant="outlined"
            />
          )}
        </Box>
        
        {/* Formulario con campos necesarios */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Nombre del Centro"
              name="nombreCentro"
              value={formData.nombreCentro}
              onChange={handleChange}
            />
          </Grid>
          {/* Más campos... */}
        </Grid>
      </CardContent>
    </Card>
  );
};
```

## Rutas
```javascript
// Router.jsx
{ path: '/configuracion', element: <ConfiguracionMain /> }

// api_routes.py  
@app.route('/api/configuracion/general', methods=['GET'])
@token_required
def get_configuracion_general():
    return ConfiguracionService.get_configuracion_general()

@app.route('/api/configuracion/general', methods=['PUT'])
@admin_required  
def update_configuracion_general():
    return ConfiguracionService.update_configuracion_general()
```

## Validaciones
1. **Backend**: Usuario debe tener `id_centro` en token
2. **Campos requeridos**: `nombre_centro`
3. **Formatos**: Email, teléfono, horarios
4. **Permisos**: Solo admin puede modificar

## Flujo de Datos
1. **Usuario accede** → `/configuracion`
2. **Frontend llama** → `GET /api/configuracion/general` 
3. **Backend obtiene** → `id_centro` del token JWT
4. **Backend consulta** → tabla `centros` WHERE `id = centro_id`
5. **Backend mapea** → campos snake_case → camelCase  
6. **Frontend muestra** → formulario con datos del centro
7. **Usuario guarda** → `PUT /api/configuracion/general`
8. **Backend actualiza** → registro específico del centro

## Ventajas
- ✅ **Usa tabla existente** (no crea nuevas estructuras)
- ✅ **Seguridad por usuario** (cada uno ve solo su centro)
- ✅ **Escalable** (fácil agregar más centros)
- ✅ **Auditable** (logs por centro)
- ✅ **Simple** (menos complejidad de base de datos)

## Campos del Formulario
**Información del Centro:**
- Nombre del Centro ⭐ (requerido)
- Dirección
- Teléfono  
- Email
- Horario de Inicio/Fin
- Descripción

**Configuraciones Regionales:**
- Zona Horaria (fijo: Ecuador)
- Formato de Fecha (fijo: DD/MM/YYYY)
- Formato de Hora (fijo: 24h)
- Moneda (fijo: USD)
- Idioma (fijo: es)

## Próximos Pasos
1. Implementar ConfiguracionComponent con los métodos mostrados
2. Implementar ConfiguracionService con manejo de centro_id
3. Crear/actualizar rutas en api_routes.py
4. Implementar frontend con AuthContext
5. Probar con usuarios de diferentes centros

## Comando para Empezar
```bash
# En nuevo chat, pega este documento y di:
"Implementa el sistema de configuración por centro siguiendo exactamente este documento MD"
```