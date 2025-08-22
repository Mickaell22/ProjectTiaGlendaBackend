#!/usr/bin/env python3
"""
04_limpiar_datos.py
Script para limpiar datos del sistema
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
                print("💡 La base de datos no existe, no hay nada que limpiar")
            else:
                self.print_step("CONEXIÓN", f"Error de conexión: {str(e)}", False)
            return False
        except Exception as e:
            self.print_step("CONEXIÓN", f"Error: {str(e)}", False)
            return False

    def check_if_data_exists(self):
        """Verificar si existen datos para limpiar"""
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
                'cronogramas': "SELECT COUNT(*) FROM cronograma_sesiones",
                'asistencias': "SELECT COUNT(*) FROM asistencia_sesiones",
                'mensajes': "SELECT COUNT(*) FROM mensajes_chat",
                'observaciones': "SELECT COUNT(*) FROM observaciones_sesiones"
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
                self.print_step("VERIFICACIÓN", "No hay datos para limpiar", True)
                return False
                
        except Exception as e:
            self.print_step("VERIFICACIÓN", f"Error verificando datos: {str(e)}", False)
            return False

    def show_cleanup_options(self):
        """Mostrar opciones de limpieza"""
        print("\n" + "=" * 70)
        print("🧹 OPCIONES DE LIMPIEZA")
        print("=" * 70)
        print("1. 🗑️  LIMPIEZA COMPLETA - Borrar todos los datos")
        print("   └── Usuarios, personal, pacientes, sesiones, todo")
        print("")
        print("2. 📊 LIMPIEZA PARCIAL - Borrar solo datos operacionales")
        print("   └── Sesiones, cronogramas, asistencias, mensajes")
        print("   └── Mantener: centros, roles, especialidades, usuarios, personal, pacientes")
        print("")
        print("3. 🧪 LIMPIEZA DE PRUEBAS - Borrar solo datos de ejemplo")
        print("   └── Asistencias, mensajes, observaciones de prueba")
        print("   └── Mantener: estructura básica y sesiones")
        print("")
        print("4. ❌ CANCELAR")
        print("=" * 70)
        
        while True:
            try:
                option = input("\nSelecciona una opción (1-4): ").strip()
                if option in ['1', '2', '3', '4']:
                    return int(option)
                else:
                    print("❌ Opción inválida. Selecciona 1, 2, 3 o 4")
            except KeyboardInterrupt:
                print("\n⏹️  Operación cancelada")
                return 4

    def confirm_cleanup(self, option):
        """Confirmar limpieza"""
        cleanup_descriptions = {
            1: "LIMPIEZA COMPLETA - Se borrarán TODOS los datos",
            2: "LIMPIEZA PARCIAL - Se borrarán datos operacionales",
            3: "LIMPIEZA DE PRUEBAS - Se borrarán solo datos de ejemplo"
        }
        
        print(f"\n⚠️  CONFIRMACIÓN: {cleanup_descriptions[option]}")
        print("⚠️  ESTA ACCIÓN NO SE PUEDE DESHACER")
        
        while True:
            respuesta = input("\n¿Estás SEGURO? (escribir 'CONFIRMAR' para proceder): ").strip()
            
            if respuesta == 'CONFIRMAR':
                print("✅ Confirmación recibida. Procediendo...")
                return True
            elif respuesta.lower() in ['n', 'no', 'cancelar', 'salir']:
                print("❌ Operación cancelada por el usuario")
                return False
            else:
                print("❌ Debes escribir exactamente 'CONFIRMAR' para proceder o 'no' para cancelar")

    def execute_complete_cleanup(self):
        """Ejecutar limpieza completa"""
        self.print_step("LIMPIEZA", "Iniciando limpieza completa")
        
        cursor = self.connection.cursor()
        
        # Orden de borrado respetando dependencias (de hijos a padres)
        delete_queries = [
            # 1. Datos operacionales
            ("Asistencias de sesiones", "DELETE FROM asistencia_sesiones"),
            ("Asistencias de clases", "DELETE FROM asistencia_clases"),
            ("Cronogramas de sesiones", "DELETE FROM cronograma_sesiones"),
            ("Cronogramas de clases", "DELETE FROM cronograma_clases"),
            ("Mensajes de chat", "DELETE FROM mensajes_chat"),
            ("Observaciones de sesiones", "DELETE FROM observaciones_sesiones"),
            
            # 2. Inscripciones
            ("Inscripciones de pacientes", "DELETE FROM sesion_paciente"),
            ("Inscripciones de estudiantes", "DELETE FROM sesion_estudiante"),
            
            # 3. Sesiones
            ("Sesiones terapéuticas", "DELETE FROM sesion_terapia"),
            ("Sesiones pedagógicas", "DELETE FROM sesion_pedagogica"),
            
            # 4. Documentos
            ("Documentos de personal", "DELETE FROM documentos_personal"),
            ("Documentos de pacientes", "DELETE FROM documentos_paciente"),
            
            # 5. Relaciones especialidades
            ("Especialidades de pacientes", "DELETE FROM paciente_especialidades"),
            ("Especialidades de personal", "DELETE FROM personal_especialidades"),
            
            # 6. Entidades principales
            ("Pacientes", "DELETE FROM paciente"),
            ("Tutores", "DELETE FROM tutor"),
            ("Personal", "DELETE FROM personal"),
            ("Usuarios", "DELETE FROM usuario"),
            ("Personas", "DELETE FROM persona"),
            
            # 7. Catálogos
            ("Especialidades", "DELETE FROM especialidad"),
            ("Roles", "DELETE FROM rol"),
            ("Centros", "DELETE FROM centros"),
            
            # 8. Reset secuencias
            ("Reset secuencias", """
                SELECT setval('seq_codigo_paciente', 1, false);
                SELECT setval('seq_codigo_sesion_terapia', 1, false);  
                SELECT setval('seq_codigo_sesion_pedagogica', 1, false);
            """)
        ]
        
        return self._execute_delete_queries(cursor, delete_queries)

    def execute_partial_cleanup(self):
        """Ejecutar limpieza parcial"""
        self.print_step("LIMPIEZA", "Iniciando limpieza parcial")
        
        cursor = self.connection.cursor()
        
        # Solo borrar datos operacionales
        delete_queries = [
            ("Asistencias de sesiones", "DELETE FROM asistencia_sesiones"),
            ("Asistencias de clases", "DELETE FROM asistencia_clases"),
            ("Cronogramas de sesiones", "DELETE FROM cronograma_sesiones"),
            ("Cronogramas de clases", "DELETE FROM cronograma_clases"),
            ("Mensajes de chat", "DELETE FROM mensajes_chat"),
            ("Observaciones de sesiones", "DELETE FROM observaciones_sesiones"),
            ("Inscripciones de pacientes", "DELETE FROM sesion_paciente"),
            ("Inscripciones de estudiantes", "DELETE FROM sesion_estudiante"),
            ("Sesiones terapéuticas", "DELETE FROM sesion_terapia"),
            ("Sesiones pedagógicas", "DELETE FROM sesion_pedagogica"),
            ("Reset secuencias de sesiones", """
                SELECT setval('seq_codigo_sesion_terapia', 1, false);  
                SELECT setval('seq_codigo_sesion_pedagogica', 1, false);
            """)
        ]
        
        return self._execute_delete_queries(cursor, delete_queries)

    def execute_test_cleanup(self):
        """Ejecutar limpieza de datos de prueba"""
        self.print_step("LIMPIEZA", "Iniciando limpieza de datos de prueba")
        
        cursor = self.connection.cursor()
        
        # Solo borrar datos de ejemplo/prueba
        delete_queries = [
            ("Asistencias de ejemplo", "DELETE FROM asistencia_sesiones"),
            ("Asistencias de clases de ejemplo", "DELETE FROM asistencia_clases"),
            ("Mensajes de ejemplo", "DELETE FROM mensajes_chat"),
            ("Observaciones de ejemplo", "DELETE FROM observaciones_sesiones")
        ]
        
        return self._execute_delete_queries(cursor, delete_queries)

    def _execute_delete_queries(self, cursor, delete_queries):
        """Ejecutar consultas de borrado"""
        success_count = 0
        total_deleted = 0
        
        for i, (description, query) in enumerate(delete_queries, 1):
            self.print_step(f"  {i}/{len(delete_queries)}", f"Procesando {description}")
            
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

    def verify_cleanup(self, option):
        """Verificar que la limpieza fue exitosa"""
        self.print_step("VERIFICACIÓN", "Verificando limpieza")
        
        try:
            cursor = self.connection.cursor()
            
            if option == 1:  # Limpieza completa
                checks = ['usuario', 'personal', 'paciente', 'tutor', 'sesion_terapia', 'especialidad', 'rol', 'centros']
            elif option == 2:  # Limpieza parcial
                checks = ['sesion_terapia', 'sesion_pedagogica', 'cronograma_sesiones', 'mensajes_chat']
            else:  # Limpieza de pruebas
                checks = ['asistencia_sesiones', 'asistencia_clases', 'mensajes_chat', 'observaciones_sesiones']
            
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
                self.print_step("VERIFICACIÓN", "✅ Limpieza completada exitosamente", True)
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
        """Ejecutar proceso completo de limpieza"""
        print("\n🧹 CENTRO TÍA GLENDA - LIMPIADOR DE DATOS")
        print("=" * 70)
        print("⚠️  Este script permite limpiar datos selectivamente")
        print("=" * 70)
        
        # Conectar
        if not self.test_connection():
            return False
        
        # Verificar si hay datos
        if not self.check_if_data_exists():
            print("\n✅ No hay datos para limpiar. La base de datos ya está limpia.")
            return True
        
        # Mostrar opciones
        option = self.show_cleanup_options()
        
        if option == 4:  # Cancelar
            print("⏹️  Operación cancelada por el usuario")
            return True
        
        # Confirmar limpieza
        if not self.confirm_cleanup(option):
            return False
        
        # Ejecutar limpieza según opción
        if option == 1:
            success_count, total_deleted = self.execute_complete_cleanup()
        elif option == 2:
            success_count, total_deleted = self.execute_partial_cleanup()
        elif option == 3:
            success_count, total_deleted = self.execute_test_cleanup()
        
        # Verificar limpieza
        cleanup_successful = self.verify_cleanup(option)
        
        # Cerrar conexión
        if self.connection:
            self.connection.close()
        
        # Resumen
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE LIMPIEZA")
        print("=" * 70)
        print(f"🗑️  Operaciones ejecutadas: {success_count}")
        print(f"📝 Total registros eliminados: {total_deleted}")
        
        if cleanup_successful:
            print("\n🎉 ¡LIMPIEZA COMPLETADA EXITOSAMENTE!")
            if option == 1:
                print("✨ La base de datos está completamente limpia")
                print("🔄 Puedes cargar nuevos datos con '02_cargar_datos.py'")
            elif option == 2:
                print("✨ Los datos operacionales han sido limpiados")
                print("🔄 La estructura básica se mantiene intacta")
            else:
                print("✨ Los datos de prueba han sido limpiados")
                print("🔄 Los datos principales se mantienen")
            return True
        else:
            print("\n⚠️  LIMPIEZA INCOMPLETA")
            print("💡 Algunos datos pueden no haberse limpiado correctamente")
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