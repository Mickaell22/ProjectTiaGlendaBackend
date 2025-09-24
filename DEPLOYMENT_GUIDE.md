# 🚀 Guía de Deployment: Centro Tía Glenda
## Railway + Dominio Personalizado (tiaglenda.com)

---

## 📋 **CHECKLIST COMPLETO**

### **FASE 1: Preparación Local**
- [ ] Verificar que la aplicación funciona localmente
- [ ] Revisar variables de entorno necesarias
- [ ] Confirmar configuración de Railway
- [ ] Limpiar archivos temporales y de debug
- [ ] Verificar requirements.txt actualizado

### **FASE 2: Configuración Railway**
- [ ] Crear cuenta en Railway.app
- [ ] Conectar repositorio GitHub
- [ ] Configurar variables de entorno en Railway
- [ ] Realizar primer deploy de prueba
- [ ] Verificar funcionamiento de la aplicación
- [ ] Configurar base de datos PostgreSQL en Railway

### **FASE 3: Dominio Personalizado**
- [ ] Registrar dominio tiaglenda.com (Namecheap/Cloudflare)
- [ ] Configurar DNS para apuntar a Railway
- [ ] Configurar dominio personalizado en Railway
- [ ] Activar certificado SSL automático
- [ ] Verificar funcionamiento con HTTPS

### **FASE 4: Configuración Final**
- [ ] Migrar datos de desarrollo a producción
- [ ] Configurar monitoreo y logs
- [ ] Realizar pruebas completas
- [ ] Documentar URLs y credenciales

---

## 🔧 **VARIABLES DE ENTORNO NECESARIAS**

### **Variables de Base de Datos:**
```bash
DB_HOST=<railway-postgres-host>
DB_PORT=5432
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=<railway-postgres-password>
```

### **Variables de Aplicación:**
```bash
JWT_SECRET=M2lrrawSow23Tgg-VhJozjjQwbkYRk30fiVjFsIjRgJ_VHvT5zl2bgn70ls-qzzMoYWQNo5aITvtJ7dteHaSzg
AMBIENTE=PRODUCTION
FLASK_ENV=production
PORT=5000
```

### **Variables Opcionales:**
```bash
FLASK_DEBUG=False
PYTHONPATH=/app/src
```

---

## 📝 **PASO A PASO DETALLADO**

### **1. Preparación Local (HOY)**

#### ✅ Verificar aplicación local:
```bash
cd "C:\Users\ASUS\Desktop\Proyecto\Project B"
python app.py
```
- Verificar que funciona en http://localhost:5000
- Probar endpoints principales (/api/test, /api/test-db)

#### ✅ Revisar configuración actual:
- Verificar `railway.json`
- Revisar `requirements.txt`
- Confirmar estructura de archivos

#### ✅ Limpiar proyecto:
```bash
# Eliminar archivos temporales
del *.pyc
del __pycache__
del test_*.py  # archivos de debug temporal
```

### **2. Configuración Railway (MAÑANA)**

#### ✅ Crear cuenta Railway:
1. Ir a https://railway.app
2. Registrarse con GitHub
3. Conectar repositorio del proyecto

#### ✅ Configurar proyecto:
1. **Crear nuevo proyecto desde GitHub**
2. **Seleccionar repositorio: Project B**
3. **Railway detectará automáticamente Python/Flask**

#### ✅ Configurar variables de entorno:
```
Variables → Add Variable:
- JWT_SECRET: M2lrrawSow23Tgg-VhJozjjQwbkYRk30fiVjFsIjRgJ_VHvT5zl2bgn70ls-qzzMoYWQNo5aITvtJ7dteHaSzg
- AMBIENTE: PRODUCTION
- FLASK_ENV: production
- PORT: 5000
```

#### ✅ Configurar PostgreSQL:
1. **Add Service → Database → PostgreSQL**
2. **Railway creará automáticamente las variables DB_***
3. **Conectar aplicación a la base de datos**

#### ✅ Primer deploy:
- Railway hará deploy automático
- Verificar logs de deployment
- Probar URL temporal de Railway

### **3. Configuración Dominio (DESPUÉS DEL DEPLOY)**

#### ✅ Registrar dominio:
**Opción A - Namecheap:**
1. Ir a namecheap.com
2. Buscar "tiaglenda.com"
3. Comprar dominio (~$12/año)

**Opción B - Cloudflare:**
1. Ir a cloudflare.com
2. Registrar dominio (~$9/año)
3. Beneficio: CDN incluido

#### ✅ Configurar DNS:
1. **En Railway: Settings → Domains**
2. **Add Custom Domain: tiaglenda.com**
3. **Railway dará instrucciones DNS específicas**
4. **En registrador de dominio:**
   - Tipo: CNAME
   - Nombre: @
   - Valor: [URL de Railway]

#### ✅ Configurar SSL:
- Railway configurará HTTPS automáticamente
- Verificar certificado válido
- Redirigir HTTP → HTTPS

### **4. Migración de Datos**

#### ✅ Exportar datos locales:
```bash
# Desde PostgreSQL local
pg_dump -U postgres -h localhost -d tia_glenda > backup_local.sql
```

#### ✅ Importar a Railway:
```bash
# Conectar a Railway PostgreSQL
psql <railway-connection-string> < backup_local.sql
```

### **5. Verificación Final**

#### ✅ Pruebas completas:
- [ ] https://tiaglenda.com funciona
- [ ] API endpoints responden correctamente
- [ ] Base de datos conectada
- [ ] Login/autenticación funciona
- [ ] Swagger docs accesibles en /docs
- [ ] Logs se generan correctamente

---

## 🔐 **SEGURIDAD**

### **Variables sensibles:**
- Nunca commitear JWT_SECRET
- Usar variables de entorno para passwords
- Activar HTTPS obligatorio

### **Base de datos:**
- Cambiar passwords por defecto
- Configurar backups automáticos
- Restringir acceso por IP si es posible

---

## 💰 **COSTOS ESTIMADOS**

### **Railway:**
- **Hobby Plan**: $5/mes (500 horas ejecución)
- **Pro Plan**: $20/mes (ilimitado)
- **Base de datos**: Incluida en el plan

### **Dominio:**
- **Namecheap**: ~$12/año
- **Cloudflare**: ~$9/año
- **Renovación**: Mismo precio anual

### **Total mensual estimado:**
- Railway Hobby + Dominio: ~$6/mes
- Railway Pro + Dominio: ~$21/mes

---

## 📞 **SOPORTE Y RECURSOS**

### **Railway:**
- Documentación: docs.railway.app
- Discord: discord.gg/railway
- Status: status.railway.app

### **Dominios:**
- Namecheap Support: soporte 24/7
- Cloudflare Docs: developers.cloudflare.com

### **Monitoreo:**
- Railway Dashboard: métricas incluidas
- Logs: disponibles en tiempo real
- Uptime: monitoring incluido

---

## 🚨 **POSIBLES PROBLEMAS Y SOLUCIONES**

### **Error de conexión BD:**
```bash
# Verificar variables de entorno
echo $DB_HOST
echo $DB_PASSWORD
```

### **Error de deployment:**
- Revisar logs en Railway Dashboard
- Verificar requirements.txt
- Confirmar Python version

### **Dominio no conecta:**
- Verificar propagación DNS (24-48h)
- Usar herramientas: whatsmydns.net
- Verificar configuración CNAME

### **SSL no funciona:**
- Esperar propagación DNS completa
- Verificar dominio en Railway Dashboard
- Forzar renovación de certificado

---

## 🔐 **JWT_SECRET GENERADO PARA PRODUCCIÓN**

```
M2lrrawSow23Tgg-VhJozjjQwbkYRk30fiVjFsIjRgJ_VHvT5zl2bgn70ls-qzzMoYWQNo5aITvtJ7dteHaSzg
```

**⚠️ IMPORTANTE:**
- Copia este secreto EXACTAMENTE como está
- Lo necesitarás mañana para configurar Railway
- NUNCA lo compartas ni lo subas a Git
- Es único para tu aplicación

---

## ✅ **PRÓXIMOS PASOS INMEDIATOS**

1. **HOY**: Revisar configuración local y limpiar proyecto
2. **MAÑANA**: Crear cuenta Railway y hacer primer deploy
3. **DESPUÉS**: Comprar dominio y configurar DNS
4. **FINAL**: Migrar datos y pruebas finales

**¿Todo listo para empezar mañana?** 🚀