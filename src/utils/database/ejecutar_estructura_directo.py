#!/usr/bin/env python3
"""
ejecutar_estructura_directo.py
Script ultra-simple para ejecutar estructura sin psql
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

class SimpleExecutor:
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
        
        # Cargar configuración desde archivo si existe
        self.load_config_from_file()
        
        # Archivos SQL en orden
        self.sql_files = [
            "01.1_tablas_base.sql",
            "01.2_tablas_personal.sql", 
            "01.3_tablas_pacientes.sql",
            "01.4_tablas_sesiones.sql",
            "01.5_tablas_comunicacion.sql"
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

    def get_password_interactive(self):
        """Obtener password de forma interactiva si es necesario"""
        print("\n🔐 CONFIGURACIÓN DE BASE DE DATOS")
        print("=" * 50)
        print(f"Host: {self.config['host']}")
        print(f"Puerto: {self.config['port']}")
        print(f"Usuario: {self.config['user']}")
        print(f"Base de datos: {self.config['database']}")
        
        # Intentar con password por defecto primero
        print(f"\n🔑 Intentando con password por defecto...")
        
        try:
            # Probar conexión con configuración actual
            test_conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database='postgres'
            )
            test_conn.close()
            print("✅ Conexión exitosa con configuración por defecto!")
            return True
        except:
            pass
        
        # Si falla, pedir password
        print("⚠️  Password por defecto no funciona.")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                import getpass
                password = getpass.getpass(f"Ingresa el password para PostgreSQL usuario '{self.config['user']}': ")
                
                # Probar nueva password
                test_conn = psycopg2.connect(
                    host=self.config['host'],
                    port=self.config['port'],
                    user=self.config['user'],
                    password=password,
                    database='postgres'
                )
                test_conn.close()
                
                self.config['password'] = password
                print("✅ Password correcto!")
                return True
                
            except Exception as e:
                print(f"❌ Password incorrecto. Intento {attempt + 1}/{max_attempts}")
                if attempt == max_attempts - 1:
                    print("💥 Máximo de intentos alcanzado")
                    return False
        
        return False

    def create_database(self):
        """Crear base de datos si no existe"""
        self.print_step("PASO 1", "Creando/verificando base de datos")
        
        try:
            # Conectar a postgres para verificar/crear BD
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Verificar si existe
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.config['database'],)
            )
            
            if cursor.fetchone():
                self.print_step("PASO 1", f"Base de datos '{self.config['database']}' ya existe", True)
            else:
                self.print_step("PASO 1", f"Creando base de datos '{self.config['database']}'")
                cursor.execute(f'CREATE DATABASE "{self.config["database"]}"')
                self.print_step("PASO 1", "Base de datos creada exitosamente", True)
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            self.print_step("PASO 1", f"Error: {str(e)}", False)
            return False

    def connect_to_target_db(self):
        """Conectar a la base de datos objetivo"""
        self.print_step("PASO 2", "Conectando a base de datos objetivo")
        
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.print_step("PASO 2", "Conexión exitosa", True)
            return True
            
        except Exception as e:
            self.print_step("PASO 2", f"Error: {str(e)}", False)
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

    def execute_sql_files(self):
        """Ejecutar archivos SQL"""
        self.print_step("PASO 3", "Ejecutando archivos SQL")
        
        success_count = 0
        cursor = self.connection.cursor()
        
        for i, sql_file in enumerate(self.sql_files, 1):
            file_path = self.script_dir / sql_file
            
            if not file_path.exists():
                self.print_step(f"  {i}/{len(self.sql_files)}", f"❌ {sql_file} no encontrado", False)
                continue
            
            self.print_step(f"  {i}/{len(self.sql_files)}", f"Ejecutando {sql_file}")
            
            try:
                # Leer archivo con manejo seguro
                sql_content, encoding = self.read_sql_file_safe(file_path)
                
                if sql_content is None:
                    self.print_step(f"  {i}/{len(self.sql_files)}", f"❌ No se pudo leer {sql_file}", False)
                    continue
                
                # Ejecutar SQL
                cursor.execute(sql_content)
                success_count += 1
                self.print_step(f"  {i}/{len(self.sql_files)}", f"✅ {sql_file} OK (encoding: {encoding})", True)
                
                time.sleep(0.2)  # Pequeña pausa
                
            except Exception as e:
                error_msg = str(e)
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                self.print_step(f"  {i}/{len(self.sql_files)}", f"❌ Error en {sql_file}: {error_msg}", False)
        
        cursor.close()
        return success_count

    def verify_structure(self):
        """Verificar estructura creada"""
        self.print_step("PASO 4", "Verificando estructura")
        
        try:
            cursor = self.connection.cursor()
            
            # Contar tablas
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """)
            total_tables = cursor.fetchone()[0]
            
            # Contar funciones
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pg_proc p 
                JOIN pg_namespace n ON p.pronamespace = n.oid 
                WHERE n.nspname = 'public'
            """)
            total_functions = cursor.fetchone()[0]
            
            cursor.close()
            
            self.print_step("PASO 4", f"Tablas: {total_tables}, Funciones: {total_functions}", True)
            return total_tables, total_functions
            
        except Exception as e:
            self.print_step("PASO 4", f"Error verificando: {str(e)}", False)
            return 0, 0

    def run(self):
        """Ejecutar proceso completo"""
        print("\n🏥 CENTRO TÍA GLENDA - EJECUTOR DIRECTO")
        print("=" * 60)
        print("📋 Este script ejecutará la estructura de BD directamente")
        print("🔧 No requiere psql en PATH")
        print("=" * 60)
        
        # Configurar credenciales
        if not self.get_password_interactive():
            return False
        
        # Crear BD
        if not self.create_database():
            return False
        
        # Conectar
        if not self.connect_to_target_db():
            return False
        
        # Ejecutar archivos
        success_count = self.execute_sql_files()
        
        # Verificar
        total_tables, total_functions = self.verify_structure()
        
        # Cerrar conexión
        if self.connection:
            self.connection.close()
        
        # Resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN FINAL")
        print("=" * 60)
        print(f"📁 Archivos procesados: {success_count}/{len(self.sql_files)}")
        print(f"🗃️  Tablas creadas: {total_tables}")
        print(f"⚙️  Funciones creadas: {total_functions}")
        
        if success_count == len(self.sql_files) and total_tables > 0:
            print("\n🎉 ¡ESTRUCTURA CREADA EXITOSAMENTE!")
            print("✨ La base de datos está lista para usar")
            return True
        else:
            print("\n⚠️  ESTRUCTURA INCOMPLETA")
            print("💡 Algunos archivos pueden haber fallado")
            return False

def main():
    try:
        executor = SimpleExecutor()
        success = executor.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️  Interrumpido por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())