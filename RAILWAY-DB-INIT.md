# 🗄️ Inicializar Base de Datos en Railway

## 📋 Scripts Listos para Railway

Se han creado scripts SQL adaptados para Railway:
- ✅ `01_estructura_tablas_railway.sql` - Crea todas las tablas
- ✅ `02_datos_iniciales_railway.sql` - Inserta datos iniciales

## 🚀 Opción 1: Railway Dashboard (Más Fácil)

### Paso 1: Abrir Railway Dashboard
1. Ve a [railway.app](https://railway.app)
2. Abre tu proyecto
3. Click en tu servicio de **PostgreSQL**
4. Click en la pestaña **Query**

### Paso 2: Ejecutar Script de Estructura
1. **Copiar** el contenido completo de `01_estructura_tablas_railway.sql`
2. **Pegar** en el editor de Query de Railway
3. **Ejecutar** (botón Run o Ctrl+Enter)
4. **Verificar** que dice "Query executed successfully"

### Paso 3: Ejecutar Script de Datos
1. **Copiar** el contenido completo de `02_datos_iniciales_railway.sql`
2. **Pegar** en el editor de Query de Railway
3. **Ejecutar** (botón Run o Ctrl+Enter)
4. **Verificar** el resumen al final con los registros creados

## 🚀 Opción 2: Desde línea de comandos

### Prerrequisitos:
- Tener `psql` instalado
- Tener los scripts en tu computadora

### Comandos:
```bash
# Conectar y ejecutar estructura
psql "postgresql://postgres:eSZYNwXdnDVwFArHZssQfwDKsoWlqTiL@centerbeam.proxy.rlwy.net:17141/railway" -f 01_estructura_tablas_railway.sql

# Conectar y ejecutar datos iniciales  
psql "postgresql://postgres:eSZYNwXdnDVwFArHZssQfwDKsoWlqTiL@centerbeam.proxy.rlwy.net:17141/railway" -f 02_datos_iniciales_railway.sql
```

## ✅ Verificación

Después de ejecutar los scripts, verifica ejecutando esta query:

```sql
-- Verificar tablas creadas
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Verificar datos insertados
SELECT 'Roles' as tabla, COUNT(*) as registros FROM rol
UNION ALL
SELECT 'Especialidades' as tabla, COUNT(*) as registros FROM especialidad
UNION ALL
SELECT 'Usuarios' as tabla, COUNT(*) as registros FROM usuario
UNION ALL
SELECT 'Pacientes' as tabla, COUNT(*) as registros FROM paciente
ORDER BY tabla;
```

**Resultado esperado:**
- ✅ 14 tablas creadas (rol, persona, usuario, etc.)
- ✅ 4 roles insertados
- ✅ 12 especialidades insertadas
- ✅ 4 usuarios creados
- ✅ 3 pacientes de ejemplo

## 👤 Usuario Administrador Creado

**Credenciales de acceso:**
- **Username:** `admin`
- **Password:** `Admin123!`
- **Rol:** Administrador (acceso completo)

## 📊 Datos de Ejemplo Incluidos

### Personal de ejemplo:
- **Ana González** - Terapia del Lenguaje
- **Carlos Ramírez** - Fisioterapia  
- **María Fernández** - Terapia Ocupacional

### Pacientes de ejemplo:
- **Sofía Morales** - Terapia del Lenguaje
- **Diego González** - Fisioterapia
- **Valentina Ramírez** - Apoyo Académico

### Especialidades incluidas:
**Terapéuticas:** Terapia del Lenguaje, Fisioterapia, Terapia Ocupacional, Psicología Clínica, Fonoaudiología, Neuropsicología

**Pedagógicas:** Educación Inicial, Educación Especial, Psicopedagogía, Estimulación Temprana, Apoyo Académico, Lectoescritura

## 🚨 Importante

- **Solo ejecutar UNA VEZ** - Los scripts incluyen `DROP TABLE IF EXISTS`
- **Backup automático** - Railway hace backups automáticos
- **Datos de prueba** - Los datos de ejemplo son seguros para desarrollo

## 🐛 Si algo sale mal

### Error: "relation does not exist"
- Ejecutar primero el script de estructura (01_...)
- Luego ejecutar el script de datos (02_...)

### Error: "permission denied"  
- Usar la URL externa para conexión desde local
- Railway Dashboard siempre funciona

### Error: "database does not exist"
- Los scripts están adaptados para la DB `railway`
- No intentar crear nueva base de datos

## 🎯 Próximo Paso

Una vez inicializada la base de datos:
1. **Deploy del backend** en Railway
2. **Probar login** con usuario `admin` / `Admin123!`
3. **Verificar** endpoints de API funcionando

¡Tu base de datos Railway está lista para usar! 🎉