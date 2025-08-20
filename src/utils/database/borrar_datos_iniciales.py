#!/usr/bin/env python3
"""
borrar_datos_iniciales.py
Script para borrar datos iniciales de los centros
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

class DataCleaner:
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
                print("💡 La base de datos no existe, no hay nada que borrar")
            else:
                self.print_step("CONEXIÓN", f"Error de conexión: {str(e)}", False)
            return False
        except Exception as e:
            self.print_step("CONEXIÓN", f"Error: {str(e)}", False)
            return False

    def check_if_data_exists(self):
        """Verificar si existen datos para borrar"""
        self.print_step("VERIFICACIÓN", "Verificando datos existentes")
        
        try:
            cursor = self.connection.cursor()
            
            # Verificar diferentes tipos de datos
            checks = {
                'usuarios': "SELECT COUNT(*) FROM usuario",
                'personal': "SELECT COUNT(*) FROM personal",
                'pacientes': "SELECT COUNT(*) FROM paciente",
                'tutores': "SELECT COUNT(*) FROM tutor",
                'sesiones_terapia': "SELECT COUNT(*) FROM sesion_terapia",
                'sesiones_pedagogicas': "SELECT COUNT(*) FROM sesion_pedagogica",
                'documentos_personal': "SELECT COUNT(*) FROM documentos_personal",
                'documentos_pacientes': "SELECT COUNT(*) FROM documentos_paciente"
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
                    # Tabla no existe, ignorar
                    pass
            
            cursor.close()
            
            if total_records > 0:
                self.print_step("VERIFICACIÓN", f"Datos encontrados: {total_records} registros", True)
                print("📋 Detalles:")
                for detail in details:
                    print(f"    - {detail}")
                return True
            else:
                self.print_step("VERIFICACIÓN", "No hay datos para borrar", True)
                return False
                
        except Exception as e:
            self.print_step("VERIFICACIÓN", f"Error verificando datos: {str(e)}", False)
            return False

    def confirm_deletion(self):
        """Confirmar que el usuario quiere borrar los datos"""
        print("\n" + "=" * 65)
        print("⚠️  ADVERTENCIA: BORRADO DE DATOS")
        print("=" * 65)
        print("🔥 Esta acción borrará TODOS los datos de prueba:")
        print("   • Usuarios y personal")
        print("   • Pacientes y tutores")
        print("   • Sesiones terapéuticas y pedagógicas")
        print("   • Documentos asociados")
        print("   • Cronogramas y asistencias")
        print("")
        print("⚠️  ESTA ACCIÓN NO SE PUEDE DESHACER")
        print("=" * 65)
        
        while True:
            respuesta = input("\n¿Estás SEGURO que quieres borrar todos los datos? (escribir 'BORRAR' para confirmar): ").strip()
            
            if respuesta == 'BORRAR':
                print("✅ Confirmación recibida. Procediendo...")
                return True
            elif respuesta.lower() in ['n', 'no', 'cancelar', 'salir']:
                print("❌ Operación cancelada por el usuario")
                return False
            else:
                print("❌ Debes escribir exactamente 'BORRAR' para confirmar o 'no' para cancelar")

    def delete_data(self):
        """Borrar datos en el orden correcto para respetar foreign keys"""
        self.print_step("BORRADO", "Iniciando borrado de datos")
        
        cursor = self.connection.cursor()
        
        # Orden de borrado respetando dependencias (de hijos a padres)
        delete_queries = [
            # 1. Asistencias (dependen de cronogramas)
            ("Asistencias de sesiones", "DELETE FROM asistencia_sesiones"),
            ("Asistencias de clases", "DELETE FROM asistencia_clases"),
            
            # 2. Cronogramas (dependen de sesiones)
            ("Cronogramas de sesiones", "DELETE FROM cronograma_sesiones"),
            ("Cronogramas de clases", "DELETE FROM cronograma_clases"),
            
            # 3. Inscripciones (dependen de sesiones y pacientes)
            ("Inscripciones de pacientes", "DELETE FROM sesion_paciente"),
            ("Inscripciones de estudiantes", "DELETE FROM sesion_estudiante"),
            
            # 4. Sesiones (dependen de personal)
            ("Sesiones terapéuticas", "DELETE FROM sesion_terapia"),
            ("Sesiones pedagógicas", "DELETE FROM sesion_pedagogica"),
            
            # 5. Documentos (dependen de personal/pacientes)
            ("Documentos de personal", "DELETE FROM documentos_personal"),
            ("Documentos de pacientes", "DELETE FROM documentos_paciente"),
            
            # 6. Especialidades múltiples (dependen de pacientes)
            ("Especialidades de pacientes", "DELETE FROM paciente_especialidades"),
            ("Especialidades de personal", "DELETE FROM personal_especialidades"),
            
            # 7. Pacientes (dependen de tutores)
            ("Pacientes", "DELETE FROM paciente"),
            
            # 8. Tutores
            ("Tutores", "DELETE FROM tutor"),
            
            # 9. Personal (depende de persona y usuario)
            ("Personal", "DELETE FROM personal"),
            
            # 10. Usuarios (dependen de persona y rol)
            ("Usuarios", "DELETE FROM usuario"),
            
            # 11. Personas
            ("Personas", "DELETE FROM persona"),
            
            # 12. Catálogos básicos
            ("Especialidades", "DELETE FROM especialidad"),
            ("Roles", "DELETE FROM rol"),
            ("Centros", "DELETE FROM centros"),
            
            # 13. Reset secuencias
            ("Reset secuencias", """
                SELECT setval('seq_codigo_paciente', 1, false);
                SELECT setval('seq_codigo_sesion_terapia', 1, false);  
                SELECT setval('seq_codigo_sesion_pedagogica', 1, false);
            """)
        ]
        
        success_count = 0
        total_deleted = 0
        
        for i, (description, query) in enumerate(delete_queries, 1):
            self.print_step(f"  {i}/{len(delete_queries)}", f"Borrando {description}")
            
            try:
                cursor.execute(query)
                if cursor.rowcount > 0:
                    self.print_step(f"  {i}/{len(delete_queries)}", f"✅ {description}: {cursor.rowcount} registros", True)
                    total_deleted += cursor.rowcount
                else:
                    self.print_step(f"  {i}/{len(delete_queries)}", f"✅ {description}: 0 registros (ya vacío)", True)
                
                success_count += 1
                time.sleep(0.1)  # Pequeña pausa visual
                
            except psycopg2.Error as e:
                error_msg = str(e)
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                self.print_step(f"  {i}/{len(delete_queries)}", f"❌ Error en {description}: {error_msg}", False)
            except Exception as e:
                error_msg = str(e)
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                self.print_step(f"  {i}/{len(delete_queries)}", f"❌ Error en {description}: {error_msg}", False)
        
        cursor.close()
        return success_count, total_deleted

    def verify_cleanup(self):
        """Verificar que el borrado fue exitoso"""
        self.print_step("VERIFICACIÓN", "Verificando limpieza completa")
        
        try:
            cursor = self.connection.cursor()
            
            # Verificar que las tablas estén vacías
            checks = [
                'usuario', 'personal', 'paciente', 'tutor',
                'sesion_terapia', 'sesion_pedagogica', 'especialidad', 'rol', 'centros'
            ]
            
            remaining_data = {}
            total_remaining = 0
            
            for table in checks:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        remaining_data[table] = count
                        total_remaining += count
                except:
                    # Tabla no existe, ignorar
                    pass
            
            cursor.close()
            
            if total_remaining == 0:
                self.print_step("VERIFICACIÓN", "✅ Base de datos completamente limpia", True)
                return True
            else:
                self.print_step("VERIFICACIÓN", f"⚠️  Quedan {total_remaining} registros", False)
                print("📋 Registros restantes:")
                for table, count in remaining_data.items():
                    print(f"    - {table}: {count}")
                return False
                
        except Exception as e:
            self.print_step("VERIFICACIÓN", f"Error verificando: {str(e)}", False)
            return False

    def run(self):
        """Ejecutar proceso completo de borrado"""
        print("\n🗑️  CENTRO TÍA GLENDA - BORRADOR DE DATOS")
        print("=" * 65)
        print("⚠️  Este script borra TODOS los datos de prueba de la base de datos")
        print("=" * 65)
        
        # Conectar
        if not self.test_connection():
            return False
        
        # Verificar si hay datos
        if not self.check_if_data_exists():
            print("\n✅ No hay datos para borrar. La base de datos ya está limpia.")
            return True
        
        # Confirmar borrado
        if not self.confirm_deletion():
            return False
        
        # Borrar datos
        success_count, total_deleted = self.delete_data()
        
        # Verificar limpieza
        cleanup_successful = self.verify_cleanup()
        
        # Cerrar conexión
        if self.connection:
            self.connection.close()
        
        # Resumen
        print("\n" + "=" * 65)
        print("📊 RESUMEN DEL BORRADO")
        print("=" * 65)
        print(f"🗑️  Operaciones ejecutadas: {success_count}")
        print(f"📝 Total registros borrados: {total_deleted}")
        
        if cleanup_successful:
            print("\n🎉 ¡DATOS BORRADOS EXITOSAMENTE!")
            print("✨ La base de datos está completamente limpia")
            print("🔄 Puedes cargar nuevos datos con 'EJECUTAR_DATOS.bat'")
            return True
        else:
            print("\n⚠️  BORRADO INCOMPLETO")
            print("💡 Algunos datos pueden no haberse borrado correctamente")
            return False

def main():
    try:
        cleaner = DataCleaner()
        success = cleaner.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️  Interrumpido por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())