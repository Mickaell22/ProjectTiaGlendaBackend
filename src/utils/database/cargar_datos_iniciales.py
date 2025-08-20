#!/usr/bin/env python3
"""
cargar_datos_iniciales.py
Script para cargar datos iniciales de los centros
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
        
        # Archivos SQL de datos en orden
        self.data_files = [
            "02.1_datos_centro_norte.sql",
            "02.2_datos_centro_sur.sql"
        ]

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
                print("💡 Ejecutar primero: EJECUTAR.bat")
            else:
                self.print_step("CONEXIÓN", f"Error de conexión: {str(e)}", False)
            return False
        except Exception as e:
            self.print_step("CONEXIÓN", f"Error: {str(e)}", False)
            return False

    def check_if_data_exists(self):
        """Verificar si ya existen datos"""
        self.print_step("VERIFICACIÓN", "Verificando si ya existen datos")
        
        try:
            cursor = self.connection.cursor()
            
            # Verificar si existen centros
            cursor.execute("SELECT COUNT(*) FROM centros")
            centros_count = cursor.fetchone()[0]
            
            # Verificar si existen roles
            cursor.execute("SELECT COUNT(*) FROM rol")
            roles_count = cursor.fetchone()[0]
            
            # Verificar si existen especialidades
            cursor.execute("SELECT COUNT(*) FROM especialidad")
            especialidades_count = cursor.fetchone()[0]
            
            cursor.close()
            
            if centros_count > 0 or roles_count > 0 or especialidades_count > 0:
                self.print_step("VERIFICACIÓN", f"Datos existentes encontrados (Centros: {centros_count}, Roles: {roles_count}, Especialidades: {especialidades_count})", True)
                
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

    def execute_data_files(self):
        """Ejecutar archivos de datos"""
        self.print_step("CARGA", "Ejecutando archivos de datos iniciales")
        
        success_count = 0
        cursor = self.connection.cursor()
        
        for i, data_file in enumerate(self.data_files, 1):
            file_path = self.script_dir / data_file
            
            if not file_path.exists():
                self.print_step(f"  {i}/{len(self.data_files)}", f"❌ {data_file} no encontrado", False)
                continue
            
            self.print_step(f"  {i}/{len(self.data_files)}", f"Ejecutando {data_file}")
            
            try:
                # Leer archivo con manejo seguro
                sql_content, encoding = self.read_sql_file_safe(file_path)
                
                if sql_content is None:
                    self.print_step(f"  {i}/{len(self.data_files)}", f"❌ No se pudo leer {data_file}", False)
                    continue
                
                # Ejecutar SQL
                cursor.execute(sql_content)
                success_count += 1
                self.print_step(f"  {i}/{len(self.data_files)}", f"✅ {data_file} OK (encoding: {encoding})", True)
                
                time.sleep(0.2)  # Pequeña pausa
                
            except psycopg2.Error as e:
                error_msg = str(e)
                # Si es error de duplicado, es normal
                if "duplicate key" in error_msg.lower() or "already exists" in error_msg.lower():
                    self.print_step(f"  {i}/{len(self.data_files)}", f"⚠️  {data_file} - Datos ya existen (normal)", True)
                    success_count += 1
                else:
                    if len(error_msg) > 100:
                        error_msg = error_msg[:100] + "..."
                    self.print_step(f"  {i}/{len(self.data_files)}", f"❌ Error SQL en {data_file}: {error_msg}", False)
            except Exception as e:
                error_msg = str(e)
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                self.print_step(f"  {i}/{len(self.data_files)}", f"❌ Error en {data_file}: {error_msg}", False)
        
        cursor.close()
        return success_count

    def verify_data_loaded(self):
        """Verificar datos cargados"""
        self.print_step("VERIFICACIÓN", "Verificando datos cargados")
        
        try:
            cursor = self.connection.cursor()
            
            # Verificar centros
            cursor.execute("SELECT COUNT(*), string_agg(nombre, ', ') FROM centros")
            centros_result = cursor.fetchone()
            centros_count = centros_result[0]
            centros_names = centros_result[1] or "Ninguno"
            
            # Verificar roles
            cursor.execute("SELECT COUNT(*), string_agg(nombre, ', ') FROM rol")
            roles_result = cursor.fetchone()
            roles_count = roles_result[0]
            roles_names = roles_result[1] or "Ninguno"
            
            # Verificar especialidades
            cursor.execute("SELECT COUNT(*), string_agg(nombre, ', ' ORDER BY nombre) FROM especialidad")
            esp_result = cursor.fetchone()
            esp_count = esp_result[0]
            esp_names = esp_result[1] or "Ninguno"
            
            cursor.close()
            
            self.print_step("VERIFICACIÓN", f"Centros: {centros_count} ({centros_names})", True)
            self.print_step("VERIFICACIÓN", f"Roles: {roles_count} ({roles_names})", True)
            self.print_step("VERIFICACIÓN", f"Especialidades: {esp_count}", True)
            
            if esp_count > 0:
                print(f"    📋 Especialidades: {esp_names}")
            
            return centros_count, roles_count, esp_count
            
        except Exception as e:
            self.print_step("VERIFICACIÓN", f"Error verificando: {str(e)}", False)
            return 0, 0, 0

    def run(self):
        """Ejecutar proceso completo"""
        print("\n🏥 CENTRO TÍA GLENDA - CARGADOR DE DATOS INICIALES")
        print("=" * 65)
        print("📋 Este script carga los datos iniciales de centros y catálogos")
        print("=" * 65)
        
        # Conectar
        if not self.test_connection():
            return False
        
        # Verificar si ya existen datos
        if not self.check_if_data_exists():
            return False
        
        # Ejecutar archivos
        success_count = self.execute_data_files()
        
        # Verificar datos cargados
        centros_count, roles_count, esp_count = self.verify_data_loaded()
        
        # Cerrar conexión
        if self.connection:
            self.connection.close()
        
        # Resumen
        print("\n" + "=" * 65)
        print("📊 RESUMEN FINAL")
        print("=" * 65)
        print(f"📁 Archivos procesados: {success_count}/{len(self.data_files)}")
        print(f"🏢 Centros: {centros_count}")
        print(f"👤 Roles: {roles_count}")
        print(f"🩺 Especialidades: {esp_count}")
        
        if success_count == len(self.data_files) and centros_count > 0:
            print("\n🎉 ¡DATOS INICIALES CARGADOS EXITOSAMENTE!")
            print("✨ El sistema está listo para crear usuarios y pacientes")
            print("🚀 Siguiente paso: Ejecutar la API con 'python app.py'")
            return True
        else:
            print("\n⚠️  CARGA INCOMPLETA")
            print("💡 Algunos archivos pueden haber fallado")
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