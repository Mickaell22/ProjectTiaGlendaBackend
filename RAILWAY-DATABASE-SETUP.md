# 🗄️ Configuración de Base de Datos Railway

## ✅ Estado Actual

Tu base de datos PostgreSQL ya está configurada en Railway con las siguientes credenciales:

### 🔗 URLs de Conexión:
- **Interna (recomendada)**: `postgresql://postgres:eSZYNwXdnDVwFArHZssQfwDKsoWlqTiL@postgres.railway.internal:5432/railway`
- **Externa**: `postgresql://postgres:eSZYNwXdnDVwFArHZssQfwDKsoWlqTiL@centerbeam.proxy.rlwy.net:17141/railway`

### 📊 Variables Disponibles:
```env
DATABASE_URL=postgresql://postgres:eSZYNwXdnDVwFArHZssQfwDKsoWlqTiL@postgres.railway.internal:5432/railway
DATABASE_PUBLIC_URL=postgresql://postgres:eSZYNwXdnDVwFArHZssQfwDKsoWlqTiL@centerbeam.proxy.rlwy.net:17141/railway

# Variables PostgreSQL nativas
PGHOST=postgres.railway.internal
PGPORT=5432  
PGDATABASE=railway
PGUSER=postgres
PGPASSWORD=eSZYNwXdnDVwFArHZssQfwDKsoWlqTiL
```

## 🚀 Configuración Automática

Tu aplicación Flask ya está configurada para usar Railway automáticamente:

### ✅ En `src/utils/general/config.py`:
- **Auto-detección**: Parsea `DATABASE_URL` automáticamente
- **Fallback**: Usa variables individuales si es necesario
- **Prioridad**: Variables de entorno > archivo config > defaults

### ✅ En `src/utils/database/connection_db.py`:
- **Conexión robusta**: Manejo de errores y reconexión
- **Pool de conexiones**: Optimizado para PostgreSQL
- **Logging**: Errores registrados automáticamente

## 📋 Checklist de Deployment

### 1. **Variables de Entorno Requeridas** (Railway las establecerá automáticamente):
- [x] `DATABASE_URL` - ✅ Configurada
- [x] `PGHOST` - ✅ Configurada  
- [x] `PGPORT` - ✅ Configurada
- [x] `PGDATABASE` - ✅ Configurada
- [x] `PGUSER` - ✅ Configurada
- [x] `PGPASSWORD` - ✅ Configurada

### 2. **Variables Adicionales a Configurar**:
```bash
# Variables requeridas para el backend
railway variables set JWT_SECRET=tu_jwt_secret_super_seguro_cambiar_en_produccion
railway variables set AMBIENTE=PRODUCTION
railway variables set DEBUG=False

# Variables opcionales
railway variables set LOG_LEVEL=INFO
railway variables set CORS_ORIGINS=https://projecttiaglendadebug-k.up.railway.app
```

### 3. **Estructura de Base de Datos**:
- [ ] **Ejecutar scripts SQL**: `01_estructura_tablas.sql`
- [ ] **Datos iniciales**: `02_datos_iniciales.sql`  
- [ ] **Verificar tablas**: Usar el script de prueba

## 🧪 Test de Conexión

Ejecuta el script de prueba para verificar la conexión:

```bash
# Desde Project B
python test_railway_db_connection.py
```

**Resultados esperados:**
- ✅ Conexión exitosa
- ✅ Consulta de prueba funciona
- ✅ Tablas detectadas (si ya están creadas)

## 🔧 Configuración de Tablas

### Opción 1: Ejecutar desde local con Railway DB
```bash
# Conectar a Railway DB desde local
psql "postgresql://postgres:eSZYNwXdnDVwFArHZssQfwDKsoWlqTiL@centerbeam.proxy.rlwy.net:17141/railway"

# Ejecutar scripts
\i src/utils/database/01_estructura_tablas.sql
\i src/utils/database/02_datos_iniciales.sql
```

### Opción 2: Desde Railway Dashboard
1. Abrir Railway Dashboard > Database
2. Query tab > Copiar contenido de los archivos SQL
3. Ejecutar manualmente

### Opción 3: API Endpoint (recomendado)
```bash
# Una vez desplegado el backend
curl -X POST https://tu-backend.railway.app/api/setup-database
```

## 📊 Endpoints de Verificación

Una vez desplegado, verifica:

### Health Check:
```bash
curl https://tu-backend.railway.app/health
```
**Resultado esperado**: `{"status": "healthy", ...}`

### Database Test:
```bash
curl https://tu-backend.railway.app/api/test-db
```
**Resultado esperado**: Conexión exitosa y tablas listadas

### Swagger Documentation:
- 🌐 `https://tu-backend.railway.app/docs`

## 🐛 Troubleshooting

### Error: "Connection refused"
**Causa**: Usando URL externa desde dentro de Railway
**Solución**: Railway usa `DATABASE_URL` (interna) automáticamente

### Error: "Database does not exist"  
**Causa**: Base de datos sin tablas
**Solución**: Ejecutar scripts SQL de estructura

### Error: "Authentication failed"
**Causa**: Credenciales incorrectas
**Solución**: Verificar que Railway estableció las variables correctamente

### Error: "SSL required"
**Causa**: Railway requiere SSL
**Solución**: Agregar `?sslmode=require` a la URL si es necesario

## 🔒 Seguridad

### ✅ Configuración Segura:
- **SSL**: Conexiones encriptadas por defecto
- **Firewall**: Solo accesible desde Railway network
- **Credenciales**: Generadas automáticamente
- **Backups**: Railway hace backups automáticos

### ⚠️ Importante:
- **NUNCA** hacer commit de credenciales al repositorio
- **Rotar** credenciales si se comprometen
- **Usar** URL interna para conexiones desde Railway

## 🎯 Próximos Pasos

1. **Deploy Backend**: `railway deploy` desde Project B
2. **Configurar Variables**: JWT_SECRET, AMBIENTE, etc.
3. **Ejecutar Scripts**: Crear tablas y datos iniciales
4. **Verificar**: Health check y test de DB
5. **Conectar Frontend**: Actualizar `VITE_API_BASE_URL`

¡Tu base de datos PostgreSQL está lista para producción en Railway! 🎉