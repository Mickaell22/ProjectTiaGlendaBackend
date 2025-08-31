# 🚀 Guía Completa: Configuración AWS S3 para Fotos de Asistencia
## Centro Tía Glenda - Sistema de Gestión de Fotos en la Nube

---

## 📋 **Tabla de Contenidos**
1. [Prerrequisitos](#prerrequisitos)
2. [Crear Cuenta AWS](#crear-cuenta-aws)
3. [Configurar Usuario IAM](#configurar-usuario-iam)
4. [Crear Bucket S3](#crear-bucket-s3)
5. [Configurar Permisos](#configurar-permisos)
6. [Instalar Dependencias](#instalar-dependencias)
7. [Configurar Variables de Entorno](#configurar-variables-de-entorno)
8. [Implementar el Código](#implementar-el-código)
9. [Migrar Fotos Existentes](#migrar-fotos-existentes)
10. [Pruebas y Validación](#pruebas-y-validación)
11. [Costos Estimados](#costos-estimados)
12. [Troubleshooting](#troubleshooting)

---

## 🔐 **1. Prerrequisitos**

### Antes de comenzar, necesitas:
- ✅ Tarjeta de crédito o débito válida
- ✅ Número de teléfono para verificación
- ✅ Dirección de correo electrónico
- ✅ Python 3.8+ instalado
- ✅ Acceso al servidor del proyecto

### Información que recopilarás:
- 📝 AWS Access Key ID
- 📝 AWS Secret Access Key
- 📝 Región AWS (ej: us-east-1)
- 📝 Nombre del bucket S3

---

## 🏗️ **2. Crear Cuenta AWS**

### 2.1. Registro inicial
1. Ve a: **https://aws.amazon.com/**
2. Clic en **"Create an AWS Account"**
3. Completa el formulario:
   - **Email address**: Tu correo profesional
   - **Password**: Contraseña segura (8+ caracteres)
   - **AWS account name**: `Centro-Tia-Glenda`

### 2.2. Información de contacto
- **Account type**: `Personal` (para centros pequeños) o `Professional`
- **Full name**: Tu nombre completo
- **Phone number**: Número de teléfono con código de país (+593 para Ecuador)
- **Country/Region**: Ecuador
- **Address**: Dirección del centro médico

### 2.3. Información de pago
- Ingresa los datos de tu tarjeta de crédito/débito
- **No se cobrará nada inicialmente** (tier gratuito por 12 meses)
- AWS solo cobra si excedes los límites gratuitos

### 2.4. Verificación de identidad
- AWS te llamará automáticamente
- Ingresa el PIN de 4 dígitos que aparece en pantalla
- Proceso toma 1-2 minutos

### 2.5. Seleccionar plan
- Elige **"Basic support - Free"**
- Para un centro médico pequeño es suficiente

### ⏱️ **Tiempo de activación: 1-24 horas**
AWS puede tomar hasta 24 horas en activar tu cuenta. Recibirás un email cuando esté lista.

---

## 👤 **3. Configurar Usuario IAM (Seguridad)**

### ¿Por qué crear un usuario IAM?
- **Seguridad**: No usar las credenciales root
- **Control granular**: Permisos específicos solo para S3
- **Rotación de claves**: Fácil cambio de credenciales

### 3.1. Acceder a la Consola AWS
1. Ve a: **https://console.aws.amazon.com/**
2. Inicia sesión con tu cuenta recién creada

### 3.2. Navegar a IAM
1. En la barra de búsqueda, escribe: **"IAM"**
2. Clic en **"IAM"** (Identity and Access Management)

### 3.3. Crear nuevo usuario
1. En el menú lateral izquierdo → **"Users"**
2. Clic en **"Create user"**
3. **User name**: `tia-glenda-s3-service`
4. **Select AWS credential type**: 
   - ✅ Marcar **"Access key - Programmatic access"**
   - ❌ NO marcar "Password - AWS Management Console access"
5. Clic en **"Next: Permissions"**

### 3.4. Asignar permisos S3
**Opción A - Permisos completos S3 (más fácil):**
1. Selecciona **"Attach existing policies directly"**
2. En el buscador, escribe: **"S3"**
3. Selecciona: **`AmazonS3FullAccess`**

**Opción B - Permisos específicos (más seguro):**
1. Selecciona **"Create policy"**
2. Ve a la pestaña **"JSON"**
3. Pega esta política personalizada:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:PutObjectAcl"
            ],
            "Resource": [
                "arn:aws:s3:::tia-glenda-fotos-asistencias/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::tia-glenda-fotos-asistencias"
            ]
        }
    ]
}
```

4. **Name**: `TiaGlendaS3Policy`
5. **Description**: `Permisos para gestionar fotos de asistencia en S3`
6. **Create policy**

### 3.5. Finalizar creación del usuario
1. Clic en **"Next: Tags"** (opcional, puedes saltarlo)
2. Clic en **"Next: Review"**
3. Revisa la configuración
4. Clic en **"Create user"**

### 3.6. ⚠️ **GUARDAR CREDENCIALES (CRÍTICO)**
**Esta es la ÚNICA vez que verás estas credenciales:**

```
Access key ID: AKIA1234567890EXAMPLE
Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY
```

**📝 COPIAR Y GUARDAR EN LUGAR SEGURO:**
- Usa un administrador de contraseñas
- O guárdalas en un archivo .txt temporal (eliminar después)
- **NUNCA las compartas públicamente**

### 3.7. Descargar archivo CSV (opcional)
- Clic en **"Download .csv"** para tener respaldo

---

## 🪣 **4. Crear Bucket S3**

### 4.1. Navegar a S3
1. En la consola AWS, busca: **"S3"**
2. Clic en **"S3"**

### 4.2. Crear nuevo bucket
1. Clic en **"Create bucket"**
2. **Bucket name**: `tia-glenda-fotos-asistencias`
   - Debe ser único globalmente
   - Solo minúsculas, números y guiones
   - Si está ocupado, prueba: `tia-glenda-fotos-asistencias-2024`

### 4.3. Configuración del bucket
**General configuration:**
- **AWS Region**: `US East (N. Virginia) us-east-1` 
  - *(Región más barata)*
  - O elige `US West (Oregon) us-west-2` *(más cercana geográficamente)*

**Object Ownership:**
- Selecciona: **"ACLs disabled (recommended)"**

**Block Public Access settings:**
- **Para fotos PRIVADAS (recomendado)**: Deja todas las opciones marcadas
- **Para fotos PÚBLICAS**: Desmarca "Block all public access"
  - ⚠️ Aparecerá una advertencia, escribe "confirm"

**Bucket Versioning:**
- **Disable** (para ahorrar costos)

**Tags (opcional):**
- Key: `Project`, Value: `TiaGlenda`
- Key: `Environment`, Value: `Production`

**Default encryption:**
- **Amazon S3 managed keys (SSE-S3)** - Gratis
- Deja las demás opciones por defecto

### 4.4. Crear bucket
- Revisa toda la configuración
- Clic en **"Create bucket"**

### 4.5. Estructura de carpetas (se crea automáticamente)
El código creará esta estructura:
```
tia-glenda-fotos-asistencias/
├── fotos-asistencias/
│   ├── asistencia-1/
│   │   ├── uuid1.jpg
│   │   └── uuid2.jpg
│   ├── asistencia-2/
│   │   └── uuid3.jpg
└── backups/ (futuro)
```

---

## 🔒 **5. Configurar Permisos (Solo si quieres fotos públicas)**

### 5.1. Si elegiste fotos PÚBLICAS
1. Entra al bucket recién creado
2. Ve a la pestaña **"Permissions"**
3. En **"Bucket policy"** → **"Edit"**
4. Pega esta política:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::tia-glenda-fotos-asistencias/fotos-asistencias/*"
        }
    ]
}
```

5. **Save changes**

### 5.2. URLs resultantes
- **Públicas**: `https://tia-glenda-fotos-asistencias.s3.amazonaws.com/fotos-asistencias/asistencia-1/foto.jpg`
- **Privadas**: URLs firmadas temporales generadas por el código

---

## 📦 **6. Instalar Dependencias**

### 6.1. Instalar boto3 (SDK de AWS para Python)
```bash
cd "C:\Users\ASUS\Desktop\Proyecto\Project B"
pip install boto3
```

### 6.2. Actualizar requirements.txt
Agregar al final de `requirements.txt`:
```
boto3==1.34.162
```

### 6.3. Verificar instalación
```bash
python -c "import boto3; print('boto3 instalado correctamente')"
```

---

## ⚙️ **7. Configurar Variables de Entorno**

### 7.1. Crear archivo .env (si no existe)
En la raíz del proyecto, crea/edita el archivo `.env`:

```bash
# Configuración existente...
DB_HOST=localhost
DB_PORT=5432
# ... otras variables ...

# 🆕 CONFIGURACIÓN AWS S3
AWS_ACCESS_KEY_ID=tu_access_key_aqui
AWS_SECRET_ACCESS_KEY=tu_secret_key_aqui
AWS_REGION=us-east-1
AWS_S3_BUCKET=tia-glenda-fotos-asistencias
AWS_S3_FOTOS_PREFIX=fotos-asistencias/

# Configuración de URLs
# Para fotos PÚBLICAS: usar public_url
# Para fotos PRIVADAS: usar signed_url
AWS_S3_URL_TYPE=signed_url
AWS_S3_SIGNED_URL_EXPIRATION=3600
```

### 7.2. ⚠️ Asegurar que .env está en .gitignore
Verificar que `.gitignore` contenga:
```
.env
*.env
```

### 7.3. Variables para producción (Railway/Heroku)
En tu plataforma de deployment, configura estas variables de entorno:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `AWS_S3_BUCKET`
- `AWS_S3_FOTOS_PREFIX`
- `AWS_S3_URL_TYPE`

---

## 💻 **8. Implementar el Código**

### 8.1. Crear servicio AWS S3
Archivo: `src/api/Service/AWSS3Service.py`

```python
# src/api/Service/AWSS3Service.py
import os
import boto3
import uuid
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError
from src.utils.general.logs import HandleLogs

class AWSS3Service:
    def __init__(self):
        try:
            self.access_key = os.getenv('AWS_ACCESS_KEY_ID')
            self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            self.region = os.getenv('AWS_REGION', 'us-east-1')
            self.bucket = os.getenv('AWS_S3_BUCKET')
            self.prefix = os.getenv('AWS_S3_FOTOS_PREFIX', 'fotos-asistencias/')
            self.url_type = os.getenv('AWS_S3_URL_TYPE', 'signed_url')
            self.expiration = int(os.getenv('AWS_S3_SIGNED_URL_EXPIRATION', 3600))
            
            # Validar configuración
            if not all([self.access_key, self.secret_key, self.bucket]):
                raise ValueError("Configuración AWS S3 incompleta")
            
            # Inicializar cliente S3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            
            HandleLogs.write_log("AWSS3Service inicializado correctamente")
            
        except Exception as e:
            HandleLogs.write_error(f"Error inicializando AWSS3Service: {str(e)}")
            raise
    
    def upload_file(self, file_obj, asistencia_id, filename):
        """Subir archivo a S3"""
        try:
            # Generar key único
            file_extension = filename.split('.')[-1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            s3_key = f"{self.prefix}asistencia-{asistencia_id}/{unique_filename}"
            
            # Subir archivo
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket,
                s3_key,
                ExtraArgs={
                    'ContentType': f'image/{file_extension}',
                    'Metadata': {
                        'original_name': filename,
                        'asistencia_id': str(asistencia_id),
                        'upload_date': datetime.now().isoformat()
                    }
                }
            )
            
            # Generar URL
            url = self.generate_url(s3_key)
            
            HandleLogs.write_log(f"Archivo subido a S3: {s3_key}")
            
            return {
                'success': True,
                'url': url,
                's3_key': s3_key,
                'filename': unique_filename
            }
            
        except ClientError as e:
            error_msg = f"Error AWS S3: {str(e)}"
            HandleLogs.write_error(error_msg)
            return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Error subiendo archivo: {str(e)}"
            HandleLogs.write_error(error_msg)
            return {'success': False, 'error': error_msg}
    
    def generate_url(self, s3_key):
        """Generar URL pública o firmada"""
        try:
            if self.url_type == 'public_url':
                return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{s3_key}"
            else:
                # URL firmada temporal
                return self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket, 'Key': s3_key},
                    ExpiresIn=self.expiration
                )
        except Exception as e:
            HandleLogs.write_error(f"Error generando URL: {str(e)}")
            return None
    
    def delete_file(self, s3_key):
        """Eliminar archivo de S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
            HandleLogs.write_log(f"Archivo eliminado de S3: {s3_key}")
            return True
        except Exception as e:
            HandleLogs.write_error(f"Error eliminando archivo S3: {str(e)}")
            return False
    
    def test_connection(self):
        """Probar conexión con S3"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
            return True
        except Exception as e:
            HandleLogs.write_error(f"Error conexión S3: {str(e)}")
            return False
```

### 8.2. Actualizar FotoAsistenciaService.py
Modificar el servicio existente para usar S3:

```python
# Agregar import al inicio
from src.api.Service.AWSS3Service import AWSS3Service

# Modificar el método procesar_y_guardar_imagen
@staticmethod
def procesar_y_guardar_imagen(archivo, asistencia_id, nombre_original):
    """Procesar imagen y subirla a AWS S3"""
    try:
        # Validar imagen (mantener validación existente)
        es_valida, mensaje = FotoAsistenciaService.validar_imagen(archivo)
        if not es_valida:
            return None, mensaje
        
        # Inicializar servicio S3
        s3_service = AWSS3Service()
        
        # Subir a S3
        result = s3_service.upload_file(archivo, asistencia_id, nombre_original)
        
        if result['success']:
            return result['url'], "Imagen subida a S3 exitosamente"
        else:
            # Fallback a almacenamiento local si S3 falla
            HandleLogs.write_error(f"S3 falló, usando almacenamiento local: {result['error']}")
            return FotoAsistenciaService._guardar_local(archivo, asistencia_id, nombre_original)
            
    except Exception as e:
        HandleLogs.write_error(f"Error en procesar_y_guardar_imagen: {str(e)}")
        # Fallback a local
        return FotoAsistenciaService._guardar_local(archivo, asistencia_id, nombre_original)

# Método auxiliar para fallback local (mantener código existente)
@staticmethod
def _guardar_local(archivo, asistencia_id, nombre_original):
    """Método fallback para almacenamiento local"""
    # ... código existente de guardado local ...
```

### 8.3. Endpoint de prueba S3
Agregar endpoint para probar conexión:

```python
# En api_routes.py, agregar este endpoint
@app.route('/api/test-s3', methods=['GET'])
@token_required
def test_s3_connection():
    """Probar conexión con AWS S3"""
    try:
        from src.api.Service.AWSS3Service import AWSS3Service
        from src.utils.general.response import response_success, response_error
        
        s3_service = AWSS3Service()
        if s3_service.test_connection():
            return response_success(None, "Conexión S3 exitosa")
        else:
            return response_error("Error de conexión S3", 500)
            
    except Exception as e:
        return response_error(f"Error configuración S3: {str(e)}", 500)
```

---

## 🔄 **9. Migrar Fotos Existentes**

### 9.1. Script de migración
Crear archivo: `migrate_fotos_to_s3.py`

```python
#!/usr/bin/env python3
# migrate_fotos_to_s3.py
import os
import sys
sys.path.append('src')

from src.api.Service.AWSS3Service import AWSS3Service
from src.api.Components.FotoAsistenciaComponent import FotoAsistenciaComponent

def migrate_existing_photos():
    """Migrar fotos existentes desde local a S3"""
    print("Iniciando migración de fotos a S3...")
    
    local_dir = "fotos_asistencias"
    if not os.path.exists(local_dir):
        print("No hay fotos locales para migrar")
        return
    
    s3_service = AWSS3Service()
    migrated = 0
    errors = 0
    
    for asistencia_folder in os.listdir(local_dir):
        asistencia_path = os.path.join(local_dir, asistencia_folder)
        if not os.path.isdir(asistencia_path):
            continue
        
        asistencia_id = asistencia_folder.replace('asistencia_', '')
        print(f"Procesando asistencia {asistencia_id}...")
        
        for filename in os.listdir(asistencia_path):
            file_path = os.path.join(asistencia_path, filename)
            
            try:
                with open(file_path, 'rb') as file:
                    result = s3_service.upload_file(file, asistencia_id, filename)
                    
                if result['success']:
                    print(f"  ✓ {filename} → S3")
                    migrated += 1
                    
                    # Actualizar BD con nueva URL
                    # (implementar según tu lógica de BD)
                    
                else:
                    print(f"  ✗ Error: {filename}")
                    errors += 1
                    
            except Exception as e:
                print(f"  ✗ Error procesando {filename}: {str(e)}")
                errors += 1
    
    print(f"\nMigración completada:")
    print(f"  Migradas: {migrated}")
    print(f"  Errores: {errors}")

if __name__ == "__main__":
    migrate_existing_photos()
```

### 9.2. Ejecutar migración
```bash
# Después de configurar las variables de entorno
python migrate_fotos_to_s3.py
```

---

## 🧪 **10. Pruebas y Validación**

### 10.1. Probar conexión S3
```bash
# Probar endpoint de conexión
curl -H "Authorization: Bearer tu_token" http://localhost:5000/api/test-s3
```

### 10.2. Probar subida de fotos
```bash
# Usar el script de prueba existente
python test_simple_fotos.py
```

### 10.3. Verificar en consola AWS
1. Ve a la consola S3
2. Entra a tu bucket
3. Verifica que las fotos se están subiendo correctamente
4. Chequea la estructura de carpetas

### 10.4. Monitorear costos
1. En AWS Console → "Billing & Cost Management"
2. Ve "Cost Explorer" para ver gastos diarios
3. Configura alertas de facturación

---

## 💰 **11. Costos Estimados**

### 11.1. Tier Gratuito (12 meses)
- **Almacenamiento**: 5 GB gratis
- **Requests GET**: 20,000 gratis/mes
- **Requests PUT**: 2,000 gratis/mes
- **Transferencia de datos**: 15 GB gratis/mes

### 11.2. Estimación para Centro Tía Glenda

**Escenario conservador:**
```
- 100 fotos/mes × 500KB = 50 MB/mes
- En 12 meses = 600 MB (dentro del tier gratuito)
- GET requests: ~1,000/mes (dentro del límite gratuito)
- PUT requests: ~100/mes (dentro del límite gratuito)

Costo mensual: $0.00 (primeros 12 meses)
```

**Después del primer año:**
```
- Almacenamiento: 600 MB × $0.023/GB = $0.01/mes
- Requests: Despreciables
- Total estimado: $0.05/mes máximo
```

### 11.3. Alertas de facturación recomendadas
- Configurar alerta a $1 USD/mes
- Configurar alerta a $5 USD/mes (para estar seguros)

---

## 🔧 **12. Troubleshooting**

### 12.1. Error: "NoCredentialsError"
```python
# Solución: Verificar variables de entorno
import os
print(os.getenv('AWS_ACCESS_KEY_ID'))  # Debe mostrar tu access key
print(os.getenv('AWS_SECRET_ACCESS_KEY'))  # Debe mostrar tu secret key
```

### 12.2. Error: "Access Denied"
- Verificar que el usuario IAM tiene permisos S3
- Verificar que el bucket existe
- Verificar que la región es correcta

### 12.3. Error: "Bucket does not exist"
- Verificar nombre del bucket en variables de entorno
- Verificar que el bucket se creó en la región correcta

### 12.4. URLs no funcionan
**Para URLs públicas:**
- Verificar política del bucket
- Verificar que "Block Public Access" está deshabilitado

**Para URLs firmadas:**
- Las URLs expiran según configuración
- Regenerar URL si expiró

### 12.5. Costos inesperados
- Verificar en "Cost Explorer" qué está causando cargos
- Revisar configuración de "Storage Class"
- Verificar que no hay transferencias de datos excesivas

---

## 📞 **13. Contacto y Soporte**

### AWS Support
- **Documentación**: https://docs.aws.amazon.com/s3/
- **Foro comunitario**: https://forums.aws.amazon.com/
- **Support básico**: Incluido gratis

### Centro Tía Glenda - Implementación
- Seguir esta guía paso a paso
- Guardar todas las credenciales de forma segura
- Hacer backup de la configuración

---

## ✅ **14. Checklist de Implementación**

### Preparación AWS:
- [ ] Cuenta AWS creada y activada
- [ ] Usuario IAM creado
- [ ] Credenciales AWS guardadas de forma segura
- [ ] Bucket S3 creado
- [ ] Permisos configurados

### Configuración del proyecto:
- [ ] boto3 instalado
- [ ] Variables de entorno configuradas
- [ ] AWSS3Service.py implementado
- [ ] FotoAsistenciaService.py actualizado
- [ ] Endpoint de prueba agregado

### Pruebas:
- [ ] Conexión S3 verificada
- [ ] Subida de fotos probada
- [ ] URLs funcionando
- [ ] Fotos existentes migradas
- [ ] Costos monitoreados

### Producción:
- [ ] Variables de entorno en servidor
- [ ] Backups configurados
- [ ] Alertas de facturación activas
- [ ] Documentación actualizada

---

## 🎯 **Resultado Final**

Una vez completada esta guía:

1. **Fotos de asistencia se subirán automáticamente a AWS S3**
2. **URLs seguras generadas automáticamente**
3. **Almacenamiento escalable e ilimitado**
4. **Costos mínimos** (gratis el primer año)
5. **Backup automático** y alta disponibilidad
6. **Integración transparente** con el sistema existente

---

*Guía creada para Centro Tía Glenda - Sistema de Gestión Médica*  
*Fecha: Agosto 2024*  
*Versión: 1.0*