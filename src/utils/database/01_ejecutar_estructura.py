#!/usr/bin/env python3
"""
01_ejecutar_estructura.py
Script para ejecutar la estructura completa de la base de datos
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

class StructureExecutor:
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
        
        # Archivo SQL consolidado
        self.structure_file = "01_estructura_completa.sql"

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

    def execute_structure_file(self):
        """Ejecutar archivo de estructura completa"""
        self.print_step("PASO 3", "Ejecutando estructura completa")
        
        file_path = self.script_dir / self.structure_file
        
        if not file_path.exists():
            self.print_step("PASO 3", f"❌ {self.structure_file} no encontrado", False)
            return False
        
        self.print_step("PASO 3", f"Procesando {self.structure_file}")
        
        try:
            # Leer archivo con manejo seguro
            sql_content, encoding = self.read_sql_file_safe(file_path)
            
            if sql_content is None:
                self.print_step("PASO 3", f"❌ No se pudo leer {self.structure_file}", False)
                return False
            
            # Ejecutar SQL
            cursor = self.connection.cursor()
            cursor.execute(sql_content)
            cursor.close()
            
            self.print_step("PASO 3", f"✅ {self.structure_file} ejecutado exitosamente (encoding: {encoding})", True)
            return True
            
        except psycopg2.Error as e:
            error_msg = str(e)
            if len(error_msg) > 200:
                error_msg = error_msg[:200] + "..."
            self.print_step("PASO 3", f"❌ Error SQL: {error_msg}", False)
            return False
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 200:
                error_msg = error_msg[:200] + "..."
            self.print_step("PASO 3", f"❌ Error: {error_msg}", False)
            return False

    def verify_structure(self):
        """Verificar estructura creada"""
        self.print_step("PASO 4", "Verificando estructura creada")
        
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
                AND p.prokind = 'f'
            """)
            total_functions = cursor.fetchone()[0]
            
            # Contar triggers
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pg_trigger 
                WHERE tgisinternal = false
            """)
            total_triggers = cursor.fetchone()[0]
            
            # Contar secuencias
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pg_class 
                WHERE relkind = 'S'
                AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            """)
            total_sequences = cursor.fetchone()[0]
            
            cursor.close()
            
            self.print_step("PASO 4", f"Tablas: {total_tables}", True)
            self.print_step("PASO 4", f"Funciones: {total_functions}", True)
            self.print_step("PASO 4", f"Triggers: {total_triggers}", True)
            self.print_step("PASO 4", f"Secuencias: {total_sequences}", True)
            
            return total_tables, total_functions, total_triggers, total_sequences
            
        except Exception as e:
            self.print_step("PASO 4", f"Error verificando: {str(e)}", False)
            return 0, 0, 0, 0

    def run(self):
        """Ejecutar proceso completo"""
        print("\n🏥 CENTRO TÍA GLENDA - EJECUTOR DE ESTRUCTURA CONSOLIDADA")
        print("=" * 70)
        print("📋 Este script ejecuta la estructura completa de BD en un solo archivo")
        print("🔧 Incluye: tablas, funciones, triggers, índices y secuencias")
        print("=" * 70)
        
        # Configurar credenciales
        if not self.get_password_interactive():
            return False
        
        # Crear BD
        if not self.create_database():
            return False
        
        # Conectar
        if not self.connect_to_target_db():
            return False
        
        # Ejecutar estructura
        if not self.execute_structure_file():
            return False
        
        # Verificar
        total_tables, total_functions, total_triggers, total_sequences = self.verify_structure()
        
        # Cerrar conexión
        if self.connection:
            self.connection.close()
        
        # Resumen
        print("\n" + "=" * 70)
        print("📊 RESUMEN FINAL")
        print("=" * 70)
        print(f"🗃️  Tablas creadas: {total_tables}")
        print(f"⚙️  Funciones creadas: {total_functions}")
        print(f"🔧 Triggers creados: {total_triggers}")
        print(f"🔄 Secuencias creadas: {total_sequences}")
        
        if total_tables >= 22:  # Esperamos al menos 22 tablas
            print("\n🎉 ¡ESTRUCTURA CREADA EXITOSAMENTE!")
            print("✨ La base de datos está lista para cargar datos")
            print("🚀 Siguiente paso: Ejecutar '02_cargar_datos.py'")
            return True
        else:
            print("\n⚠️  ESTRUCTURA INCOMPLETA")
            print("💡 La estructura puede no haberse creado correctamente")
            return False

def main():
    try:
        executor = StructureExecutor()
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