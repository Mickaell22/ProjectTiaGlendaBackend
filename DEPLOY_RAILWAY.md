# 🚀 Deploy en Railway - Centro Tía Glenda

Esta guía te permite desplegar tu backend en Railway cuando estés listo.

## 📋 Prerequisitos

1. Cuenta en [Railway](https://railway.app/)
2. Cuenta en GitHub (tu proyecto debe estar en GitHub)
3. Railway CLI instalado

## 🔧 Instalación de Railway CLI

```bash
# Windows
npm install -g @railway/cli

# macOS
brew install railway

# Linux
curl -fsSL https://railway.app/install.sh | sh
```

## 🎯 Pasos para Deploy

### 1. Preparar el Repositorio
```bash
# Asegúrate de que todos los cambios estén en GitHub
git add .
git commit -m "Preparado para deploy en Railway"
git push origin main
```

### 2. Login en Railway
```bash
railway login
```

### 3. Crear Proyecto
```bash
# Opción A: Desde el directorio del proyecto
railway init

# Opción B: Conectar repositorio existente de GitHub
# Ve a railway.app → New Project → Deploy from GitHub
```

### 4. Agregar Base de Datos PostgreSQL
```bash
# Agregar PostgreSQL al proyecto
railway add postgresql
```

### 5. Configurar Variables de Entorno

En Railway Dashboard → Variables:

**Variables Requeridas:**
```env
AMBIENTE=PRODUCTION
JWT_SECRET=tu_jwt_secret_super_seguro_cambiar_esto
DEBUG=False
```

**Variables Opcionales:**
```env
CORS_ORIGINS=https://tu-frontend.vercel.app,https://tu-dominio.com
LOG_LEVEL=INFO
```

> **⚠️ IMPORTANTE:** Railway automáticamente provee `DATABASE_URL` para PostgreSQL.

### 6. Deploy
```bash
# Deploy automático
railway up

# O deploy con logs en vivo
railway up --detach
```

## 🔍 Verificar Deploy

1. **Health Check:** `https://tu-app.up.railway.app/health`
2. **API Test:** `https://tu-app.up.railway.app/api/test`
3. **Swagger Docs:** `https://tu-app.up.railway.app/docs/`

## 📊 Monitoreo

```bash
# Ver logs en tiempo real
railway logs

# Ver variables de entorno
railway variables

# Información del proyecto
railway status
```

## 🔄 Updates/Redeploy

```bash
# Railway hace redeploy automático en cada push a main
git add .
git commit -m "Update backend"
git push origin main

# O redeploy manual
railway up
```

## 🐛 Troubleshooting

### Error de Base de Datos
```bash
# Verificar conexión de BD
railway logs --tail
```

### Error de Variables de Entorno
```bash
# Listar variables actuales
railway variables

# Agregar variable faltante
railway variables set JWT_SECRET=tu_nuevo_secreto
```

### Error de Build
- Verificar que `requirements.txt` está bien formateado
- Verificar que `railway.json` existe
- Revisar logs: `railway logs`

## 📁 Archivos de Configuración Incluidos

✅ `railway.json` - Configuración de Railway
✅ `requirements.txt` - Dependencias Python (corregido)
✅ `.env.example` - Template de variables de entorno
✅ `src/utils/general/config.py` - Soporte para DATABASE_URL
✅ `app.py` - CORS configurado para producción

## 💰 Costos Estimados

- **Hobby Plan:** $5/mes
- **Pro Plan:** $20/mes (más recursos)
- **Base de datos:** Incluida en plan

## 🔐 Seguridad

**Antes de Deploy:**
1. Cambiar `JWT_SECRET` por uno único y seguro
2. Configurar `CORS_ORIGINS` con tu dominio real
3. **NUNCA** subir archivos `.env` al repositorio

## 📞 Soporte

- Railway Docs: https://docs.railway.app/
- Discord de Railway: https://railway.app/discord
- GitHub Issues de tu proyecto

---

**¡Tu proyecto está listo para producción! 🎉**