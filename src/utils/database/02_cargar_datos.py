#!/usr/bin/env python3
"""
02_cargar_datos.py
Script para cargar datos completos de los centros
Centro Tía Glenda
"""

import os
import sys
import time
from pathlib import Path

# Intentar importar psycopg2
try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("❌ psycopg2 no encontrado. Instalando...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class DataLoader:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.connection = None
        
        # Configuración por defecto
        self.config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'centro_tia_glenda',
            'user': 'postgres',
            'password': '1234'
        }
        
        # Cargar configuración desde archivo
        self.load_config_from_file()
        
        # Archivo SQL consolidado de datos
        self.data_file = "02_datos_completos.sql"

    def load_config_from_file(self):
        """Cargar configuración desde archivo config_db.txt"""
        config_file = self.script_dir / 'config_db.txt'
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip().lower()
                            value = value.strip()
                            
                            if key == 'host':
                                self.config['host'] = value
                            elif key == 'port':
                                self.config['port'] = int(value)
                            elif key == 'database':
                                self.config['database'] = value
                            elif key == 'user':
                                self.config['user'] = value
                            elif key == 'password':
                                self.config['password'] = value
                
                print(f"✅ Configuración cargada desde config_db.txt")
            except Exception as e:
                print(f"⚠️  Error leyendo config_db.txt: {e}")
                print(f"📋 Usando configuración por defecto")

    def print_step(self, step, message, success=None):
        """Imprimir paso con formato simple"""
        if success is True:
            print(f"✅ {step}: {message}")
        elif success is False:
            print(f"❌ {step}: {message}")
        else:
            print(f"🔄 {step}: {message}")

    def test_connection(self):
        """Probar conexión a la base de datos"""
        self.print_step("CONEXIÓN", "Probando conexión a la base de datos")
        
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.print_step("CONEXIÓN", "Conexión exitosa", True)
            return True
            
        except psycopg2.OperationalError as e:
            if "database" in str(e) and "does not exist" in str(e):
                self.print_step("CONEXIÓN", f"Base de datos '{self.config['database']}' no existe", False)
                print("💡 Ejecutar primero: 01_ejecutar_estructura.py")
            else:
                self.print_step("CONEXIÓN", f"Error de conexión: {str(e)}", False)
            return False
        except Exception as e:
            self.print_step("CONEXIÓN", f"Error: {str(e)}", False)
            return False

    def check_database_structure(self):
        """Verificar que la estructura existe"""
        self.print_step("VERIFICACIÓN", "Verificando estructura de base de datos")
        
        try:
            cursor = self.connection.cursor()
            
            # Verificar si existen las tablas principales
            essential_tables = ['centros', 'rol', 'especialidad', 'persona', 'usuario', 'personal', 'paciente']
            missing_tables = []
            
            for table in essential_tables:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table,))
                
                if not cursor.fetchone()[0]:
                    missing_tables.append(table)
            
            cursor.close()
            
            if missing_tables:
                self.print_step("VERIFICACIÓN", f"Faltan tablas: {', '.join(missing_tables)}", False)
                print("💡 Ejecutar primero: 01_ejecutar_estructura.py")
                return False
            else:
                self.print_step("VERIFICACIÓN", "Estructura de base de datos verificada", True)
                return True
                
        except Exception as e:
            self.print_step("VERIFICACIÓN", f"Error verificando estructura: {str(e)}", False)
            return False

    def check_if_data_exists(self):
        """Verificar si ya existen datos"""
        self.print_step("VERIFICACIÓN", "Verificando si ya existen datos")
        
        try:
            cursor = self.connection.cursor()
            
            # Verificar datos en tablas principales
            checks = {
                'centros': "SELECT COUNT(*) FROM centros",
                'roles': "SELECT COUNT(*) FROM rol",
                'especialidades': "SELECT COUNT(*) FROM especialidad",
                'usuarios': "SELECT COUNT(*) FROM usuario",
                'personal': "SELECT COUNT(*) FROM personal",
                'pacientes': "SELECT COUNT(*) FROM paciente"
            }
            
            total_records = 0
            details = []
            
            for table_name, query in checks.items():
                try:
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    total_records += count
                    if count > 0:
                        details.append(f"{table_name}: {count}")
                except:
                    pass
            
            cursor.close()
            
            if total_records > 0:
                self.print_step("VERIFICACIÓN", f"Datos existentes encontrados: {total_records} registros", True)
                print("📋 Detalles:")
                for detail in details:
                    print(f"    - {detail}")
                
                # Preguntar si continuar
                print("\n🤔 Ya existen datos en la base de datos.")
                respuesta = input("¿Quieres continuar y agregar más datos? (s/n): ").lower().strip()
                
                if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
                    print("✅ Continuando con la carga de datos...")
                    return True
                else:
                    print("⏹️  Proceso cancelado por el usuario")
                    return False
            else:
                self.print_step("VERIFICACIÓN", "Base de datos vacía, procederemos a cargar datos", True)
                return True
                
        except Exception as e:
            self.print_step("VERIFICACIÓN", f"Error verificando datos: {str(e)}", False)
            return False

    def read_sql_file_safe(self, file_path):
        """Leer archivo SQL con manejo seguro de codificación"""
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'ascii']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                return content, encoding
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
        
        # Último intento: leer como binario y decodificar manualmente
        try:
            with open(file_path, 'rb') as file:
                content_bytes = file.read()
            
            # Intentar decodificar ignorando errores
            content = content_bytes.decode('utf-8', errors='ignore')
            return content, 'utf-8-ignore'
        except:
            return None, None

    def execute_data_file(self):
        """Ejecutar archivo de datos completo"""
        self.print_step("CARGA", "Ejecutando archivo de datos completos")
        
        file_path = self.script_dir / self.data_file
        
        if not file_path.exists():
            self.print_step("CARGA", f"❌ {self.data_file} no encontrado", False)
            return False
        
        self.print_step("CARGA", f"Procesando {self.data_file}")
        
        try:
            # Leer archivo con manejo seguro
            sql_content, encoding = self.read_sql_file_safe(file_path)
            
            if sql_content is None:
                self.print_step("CARGA", f"❌ No se pudo leer {self.data_file}", False)
                return False
            
            # Ejecutar SQL
            cursor = self.connection.cursor()
            cursor.execute(sql_content)
            cursor.close()
            
            self.print_step("CARGA", f"✅ {self.data_file} ejecutado exitosamente (encoding: {encoding})", True)
            return True
            
        except psycopg2.Error as e:
            error_msg = str(e)
            # Si es error de duplicado, es normal en algunos casos
            if "duplicate key" in error_msg.lower() or "already exists" in error_msg.lower():
                self.print_step("CARGA", f"⚠️  {self.data_file} - Algunos datos ya existen (normal)", True)
                return True
            else:
                if len(error_msg) > 200:
                    error_msg = error_msg[:200] + "..."
                self.print_step("CARGA", f"❌ Error SQL: {error_msg}", False)
                return False
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 200:
                error_msg = error_msg[:200] + "..."
            self.print_step("CARGA", f"❌ Error: {error_msg}", False)
            return False

    def verify_data_loaded(self):
        """Verificar datos cargados"""
        self.print_step("VERIFICACIÓN", "Verificando datos cargados")
        
        try:
            cursor = self.connection.cursor()
            
            # Verificaciones detalladas
            verifications = []
            
            # Verificar centros
            cursor.execute("SELECT COUNT(*), string_agg(nombre, ', ') FROM centros")
            centros_result = cursor.fetchone()
            centros_count = centros_result[0]
            centros_names = centros_result[1] or "Ninguno"
            verifications.append(("Centros", centros_count, centros_names))
            
            # Verificar roles
            cursor.execute("SELECT COUNT(*), string_agg(nombre, ', ') FROM rol")
            roles_result = cursor.fetchone()
            roles_count = roles_result[0]
            roles_names = roles_result[1] or "Ninguno"
            verifications.append(("Roles", roles_count, roles_names))
            
            # Verificar especialidades
            cursor.execute("SELECT COUNT(*) FROM especialidad")
            esp_count = cursor.fetchone()[0]
            verifications.append(("Especialidades", esp_count, ""))
            
            # Verificar usuarios
            cursor.execute("SELECT COUNT(*) FROM usuario")
            usuarios_count = cursor.fetchone()[0]
            verifications.append(("Usuarios", usuarios_count, ""))
            
            # Verificar personal
            cursor.execute("SELECT COUNT(*) FROM personal")
            personal_count = cursor.fetchone()[0]
            verifications.append(("Personal", personal_count, ""))
            
            # Verificar pacientes
            cursor.execute("SELECT COUNT(*) FROM paciente")
            pacientes_count = cursor.fetchone()[0]
            verifications.append(("Pacientes", pacientes_count, ""))
            
            # Verificar sesiones
            cursor.execute("SELECT COUNT(*) FROM sesion_terapia")
            sesiones_t_count = cursor.fetchone()[0]
            verifications.append(("Sesiones Terapéuticas", sesiones_t_count, ""))
            
            cursor.execute("SELECT COUNT(*) FROM sesion_pedagogica")
            sesiones_p_count = cursor.fetchone()[0]
            verifications.append(("Sesiones Pedagógicas", sesiones_p_count, ""))
            
            # Verificar cronogramas
            cursor.execute("SELECT COUNT(*) FROM cronograma_sesiones")
            cronograma_s_count = cursor.fetchone()[0]
            verifications.append(("Cronograma Sesiones", cronograma_s_count, ""))
            
            cursor.execute("SELECT COUNT(*) FROM cronograma_clases")
            cronograma_c_count = cursor.fetchone()[0]
            verifications.append(("Cronograma Clases", cronograma_c_count, ""))
            
            cursor.close()
            
            # Mostrar resultados
            total_records = 0
            for name, count, details in verifications:
                total_records += count
                if details:
                    self.print_step("VERIFICACIÓN", f"{name}: {count} ({details})", True)
                else:
                    self.print_step("VERIFICACIÓN", f"{name}: {count}", True)
            
            return total_records
            
        except Exception as e:
            self.print_step("VERIFICACIÓN", f"Error verificando: {str(e)}", False)
            return 0

    def run(self):
        """Ejecutar proceso completo"""
        print("\n🏥 CENTRO TÍA GLENDA - CARGADOR DE DATOS COMPLETOS")
        print("=" * 70)
        print("📋 Este script carga todos los datos iniciales en un solo archivo")
        print("🎯 Incluye: centros, personal, pacientes, sesiones y datos de ejemplo")
        print("=" * 70)
        
        # Conectar
        if not self.test_connection():
            return False
        
        # Verificar estructura
        if not self.check_database_structure():
            return False
        
        # Verificar si ya existen datos
        if not self.check_if_data_exists():
            return False
        
        # Ejecutar archivo de datos
        if not self.execute_data_file():
            return False
        
        # Verificar datos cargados
        total_records = self.verify_data_loaded()
        
        # Cerrar conexión
        if self.connection:
            self.connection.close()
        
        # Resumen
        print("\n" + "=" * 70)
        print("📊 RESUMEN FINAL")
        print("=" * 70)
        print(f"📝 Total registros cargados: {total_records}")
        
        if total_records >= 50:  # Esperamos al menos 50 registros
            print("\n🎉 ¡DATOS CARGADOS EXITOSAMENTE!")
            print("✨ El sistema está completamente configurado")
            print("🚀 Siguiente paso: Ejecutar la API con 'python app.py'")
            print("🔗 Acceder a: http://localhost:5000/docs/ para ver Swagger")
            return True
        else:
            print("\n⚠️  CARGA INCOMPLETA")
            print("💡 Los datos pueden no haberse cargado correctamente")
            return False

def main():
    try:
        loader = DataLoader()
        success = loader.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️  Interrumpido por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())