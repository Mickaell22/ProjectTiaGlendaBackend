# Configuración CORS para Railway

## 🌐 Problema y Solución

El frontend desplegado en Railway (`projecttiaglendadebug-k.up.railway.app`) necesita comunicarse con el backend. Para esto, el backend Flask debe permitir estas conexiones mediante CORS.

## ✅ Cambios Implementados

### En `app.py`:
- **Auto-detección de Railway**: Detecta automáticamente si está en Railway
- **CORS dinámico**: Permite dominios `.railway.app` y `.up.railway.app`
- **Variables de entorno**: Soporta `CORS_ORIGINS` personalizada
- **Configuración completa**: Headers, métodos y credenciales configurados

### Configuración CORS actual:
```python
# Auto-detecta dominio Railway
railway_domain = os.getenv('RAILWAY_STATIC_URL')
if railway_domain:
    cors_origins.append(f"https://{railway_domain}")

# Si estamos en Railway, permitir subdominios railway.app
if os.getenv('RAILWAY_ENVIRONMENT'):
    cors_origins.extend([
        'https://*.railway.app',
        'https://*.up.railway.app'
    ])
```

## 🚀 Configuración en Railway

### Opción 1: Configuración Automática (Recomendada)
Railway detectará automáticamente los dominios necesarios. Solo asegúrate de que tu backend esté desplegado.

### Opción 2: Configuración Manual
Si necesitas especificar dominios exactos:

```bash
# En Railway Dashboard o CLI
railway variables set CORS_ORIGINS=https://projecttiaglendadebug-k.up.railway.app

# Para múltiples dominios
railway variables set CORS_ORIGINS=https://projecttiaglendadebug-k.up.railway.app,https://tu-dominio-personalizado.com
```

## 🔍 Verificación

### 1. Verificar logs del backend:
El backend imprimirá los orígenes CORS configurados:
```
CORS configurado para orígenes: ['http://localhost:5173', 'https://projecttiaglendadebug-k.up.railway.app', ...]
```

### 2. Testear desde el frontend:
- Abrir `https://projecttiaglendadebug-k.up.railway.app/`
- Intentar hacer login
- Verificar que no hay errores CORS en la consola del navegador

### 3. Testear endpoints directamente:
```bash
# Test health check
curl https://tu-backend.up.railway.app/health

# Test CORS preflight
curl -X OPTIONS \
  -H "Origin: https://projecttiaglendadebug-k.up.railway.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  https://tu-backend.up.railway.app/api/login
```

## 🐛 Troubleshooting

### Error: "CORS policy: No 'Access-Control-Allow-Origin'"
**Solución:**
1. Verificar que el backend esté desplegado y funcionando
2. Confirmar que `CORS_ORIGINS` incluye tu dominio frontend
3. Redeplegar el backend después de cambios

### Error: "Network Error" o "Failed to fetch"
**Posibles causas:**
1. Backend no desplegado o caído
2. URL del backend incorrecta en el frontend (`VITE_API_BASE_URL`)
3. Variables de entorno no configuradas

### Verificar configuración actual:
```bash
# Acceder a tu backend Railway
https://tu-backend.up.railway.app/

# Debería mostrar mensaje de bienvenida con endpoints disponibles
```

## 📝 Variables de Entorno Requeridas

### Backend (Railway):
```env
# Opcional - Railway detectará automáticamente
CORS_ORIGINS=https://projecttiaglendadebug-k.up.railway.app

# Railway establecerá automáticamente
RAILWAY_ENVIRONMENT=production
DATABASE_URL=postgresql://...
PORT=railway_assigned_port
```

### Frontend (Railway):
```env
# Reemplazar con tu backend desplegado
VITE_API_BASE_URL=https://tu-backend.up.railway.app
```

## ✅ Checklist de Despliegue

- [x] Backend Flask configurado con CORS dinámico
- [x] Frontend Vite configurado con `allowedHosts: 'all'`
- [ ] Backend desplegado en Railway
- [ ] Frontend desplegado en Railway
- [ ] Variables de entorno configuradas
- [ ] CORS funcionando correctamente
- [ ] Login y API funcionando

¡Con estos cambios, tu aplicación debería funcionar correctamente entre Railway deployments! 🎉