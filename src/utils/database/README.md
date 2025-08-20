# Base de Datos - Centro Tía Glenda

## 🚀 Ejecutar Estructura de BD

### **Método Simple:**
```bash
# Doble clic en:
EJECUTAR.bat
```

### **Si necesitas cambiar credenciales:**
1. Editar `config_db.txt`
2. Cambiar `PASSWORD=postgres` por tu password
3. Ejecutar `EJECUTAR.bat`

## 📁 Archivos

### **Estructura (5 módulos):**
- `01.1_tablas_base.sql` - Centros, usuarios, roles, personas, especialidades
- `01.2_tablas_personal.sql` - Personal y especialidades múltiples
- `01.3_tablas_pacientes.sql` - Pacientes, tutores y control de pausas  
- `01.4_tablas_sesiones.sql` - Sesiones terapéuticas y pedagógicas
- `01.5_tablas_comunicacion.sql` - Chat interno y observaciones

### **Datos iniciales:**
- `02.1_datos_centro_norte.sql` - Datos del centro Norte
- `02.2_datos_centro_sur.sql` - Datos del centro Sur

### **Ejecución:**
- `EJECUTAR.bat` - Script principal
- `ejecutar_estructura_directo.py` - Motor del ejecutor
- `config_db.txt` - Configuración de credenciales

## ✅ Resultado

Después de ejecutar exitosamente:
- **22 tablas** creadas
- **23 funciones** PostgreSQL  
- **48 índices** optimizados
- **Sistema completo** listo para la API

## 🔄 Próximos Pasos

1. Cargar datos iniciales: `02.1_datos_centro_norte.sql` y `02.2_datos_centro_sur.sql`
2. Ejecutar API: `python app.py`
3. Ejecutar tests: `python tests/test_api_complete_master.py`