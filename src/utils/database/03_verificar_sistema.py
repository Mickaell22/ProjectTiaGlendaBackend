#!/usr/bin/env python3
"""
03_verificar_sistema.py
Script para verificar el estado completo del sistema
Centro Tía Glenda
"""

import sys
from pathlib import Path

# Intentar importar psycopg2
try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 no instalado")
    print("💡 Instalar con: pip install psycopg2-binary")
    sys.exit(1)

def load_config():
    """Cargar configuración de la base de datos"""
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'centro_tia_glenda',
        'user': 'postgres',
        'password': '1234'
    }
    
    config_file = Path(__file__).parent / 'config_db.txt'
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if key in config:
                            if key == 'port':
                                config[key] = int(value)
                            else:
                                config[key] = value
        except Exception as e:
            print(f"⚠️  Error leyendo config_db.txt: {e}")
            print("📋 Usando configuración por defecto")
    
    return config

def verify_structure(cursor):
    """Verificar estructura de la base de datos"""
    print("🔧 VERIFICACIÓN DE ESTRUCTURA")
    print("-" * 50)
    
    try:
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
        
        # Mostrar resultados
        print(f"📋 Tablas: {total_tables}")
        print(f"⚙️  Funciones: {total_functions}")
        print(f"🔧 Triggers: {total_triggers}")
        print(f"🔄 Secuencias: {total_sequences}")
        
        # Evaluar estructura
        if total_tables >= 22:
            print("✅ Estructura: COMPLETA")
            return True
        elif total_tables > 0:
            print("⚠️  Estructura: INCOMPLETA")
            return False
        else:
            print("❌ Estructura: NO EXISTE")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def verify_data(cursor):
    """Verificar datos del sistema"""
    print("\n📊 VERIFICACIÓN DE DATOS")
    print("-" * 50)
    
    try:
        # Definir verificaciones principales
        main_checks = [
            ('Centros', 'SELECT COUNT(*) FROM centros'),
            ('Roles', 'SELECT COUNT(*) FROM rol'),  
            ('Especialidades', 'SELECT COUNT(*) FROM especialidad'),
            ('Usuarios', 'SELECT COUNT(*) FROM usuario'),
            ('Personal', 'SELECT COUNT(*) FROM personal'),
            ('Tutores', 'SELECT COUNT(*) FROM tutor'),
            ('Pacientes', 'SELECT COUNT(*) FROM paciente'),
            ('Sesiones Terapéuticas', 'SELECT COUNT(*) FROM sesion_terapia'),
            ('Sesiones Pedagógicas', 'SELECT COUNT(*) FROM sesion_pedagogica')
        ]
        
        # Verificaciones adicionales
        additional_checks = [
            ('Especialidades de Pacientes', 'SELECT COUNT(*) FROM paciente_especialidades'),
            ('Especialidades de Personal', 'SELECT COUNT(*) FROM personal_especialidades'),
            ('Inscripciones Terapia', 'SELECT COUNT(*) FROM sesion_paciente'),
            ('Inscripciones Pedagogía', 'SELECT COUNT(*) FROM sesion_estudiante'),
            ('Cronogramas Sesiones', 'SELECT COUNT(*) FROM cronograma_sesiones'),
            ('Cronogramas Clases', 'SELECT COUNT(*) FROM cronograma_clases'),
            ('Asistencias Sesiones', 'SELECT COUNT(*) FROM asistencia_sesiones'),
            ('Asistencias Clases', 'SELECT COUNT(*) FROM asistencia_clases'),
            ('Mensajes Chat', 'SELECT COUNT(*) FROM mensajes_chat'),
            ('Observaciones', 'SELECT COUNT(*) FROM observaciones_sesiones')
        ]
        
        total_registros = 0
        tablas_con_datos = 0
        
        # Verificar datos principales
        print("📋 Datos principales:")
        for nombre, query in main_checks:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                total_registros += count
                
                if count > 0:
                    tablas_con_datos += 1
                    status = "✅"
                else:
                    status = "⚪"
                
                print(f"  {status} {nombre:<25}: {count:>3}")
                
            except Exception as e:
                print(f"  ❌ {nombre:<25}: Error")
        
        # Verificar datos adicionales
        print("\n📋 Datos adicionales:")
        for nombre, query in additional_checks:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                total_registros += count
                
                if count > 0:
                    tablas_con_datos += 1
                    status = "✅"
                else:
                    status = "⚪"
                
                print(f"  {status} {nombre:<25}: {count:>3}")
                
            except Exception as e:
                print(f"  ❌ {nombre:<25}: Error")
        
        print(f"\n📊 Total registros: {total_registros}")
        print(f"📋 Tablas con datos: {tablas_con_datos}/{len(main_checks) + len(additional_checks)}")
        
        return total_registros, tablas_con_datos
        
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")
        return 0, 0

def verify_business_logic(cursor):
    """Verificar lógica de negocio"""
    print("\n🧩 VERIFICACIÓN DE LÓGICA DE NEGOCIO")
    print("-" * 50)
    
    try:
        business_checks = []
        
        # Verificar que cada paciente tenga al menos una especialidad principal
        cursor.execute("""
            SELECT COUNT(*) 
            FROM paciente p
            WHERE NOT EXISTS (
                SELECT 1 FROM paciente_especialidades pe 
                WHERE pe.id_paciente = p.id 
                AND pe.es_principal = true
            )
        """)
        pacientes_sin_especialidad = cursor.fetchone()[0]
        business_checks.append(("Pacientes sin especialidad principal", pacientes_sin_especialidad, 0))
        
        # Verificar que cada personal tenga al menos una especialidad principal
        cursor.execute("""
            SELECT COUNT(*) 
            FROM personal p
            WHERE NOT EXISTS (
                SELECT 1 FROM personal_especialidades pe 
                WHERE pe.id_personal = p.id 
                AND pe.es_principal = true
            )
        """)
        personal_sin_especialidad = cursor.fetchone()[0]
        business_checks.append(("Personal sin especialidad principal", personal_sin_especialidad, 0))
        
        # Verificar códigos únicos de pacientes
        cursor.execute("""
            SELECT COUNT(*) - COUNT(DISTINCT codigo_paciente) 
            FROM paciente 
            WHERE codigo_paciente IS NOT NULL
        """)
        codigos_duplicados = cursor.fetchone()[0]
        business_checks.append(("Códigos de paciente duplicados", codigos_duplicados, 0))
        
        # Verificar sesiones con cronogramas
        cursor.execute("""
            SELECT COUNT(*) 
            FROM sesion_terapia st
            WHERE NOT EXISTS (
                SELECT 1 FROM cronograma_sesiones cs 
                WHERE cs.id_sesion = st.id
            )
            AND st.estado = 'en_curso'
        """)
        sesiones_sin_cronograma = cursor.fetchone()[0]
        business_checks.append(("Sesiones activas sin cronograma", sesiones_sin_cronograma, 0))
        
        # Mostrar resultados
        all_passed = True
        for check_name, actual, expected in business_checks:
            if actual == expected:
                print(f"✅ {check_name}: {actual} (correcto)")
            else:
                print(f"⚠️  {check_name}: {actual} (esperado: {expected})")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error verificando lógica de negocio: {e}")
        return False

def show_system_summary(cursor):
    """Mostrar resumen del sistema"""
    print("\n🏥 RESUMEN DEL SISTEMA")
    print("-" * 50)
    
    try:
        # Información de centros
        cursor.execute("SELECT nombre, codigo FROM centros ORDER BY nombre")
        centros = cursor.fetchall()
        if centros:
            print("🏢 Centros configurados:")
            for nombre, codigo in centros:
                print(f"   • {nombre} ({codigo})")
        
        # Información de usuarios por rol
        cursor.execute("""
            SELECT r.nombre as rol,
                   COUNT(*) as total,
                   COUNT(CASE WHEN u.estado = 'activo' THEN 1 END) as activos
            FROM usuario u 
            JOIN rol r ON u.id_rol = r.id
            GROUP BY r.nombre
            ORDER BY r.nombre
        """)
        usuarios_stats = cursor.fetchall()
        if usuarios_stats:
            print("\n👥 Usuarios por rol:")
            for rol, total, activos in usuarios_stats:
                print(f"   • {rol}: {activos}/{total} activos")
        
        # Información de especialidades
        cursor.execute("""
            SELECT area, COUNT(*) 
            FROM especialidad 
            GROUP BY area 
            ORDER BY area
        """)
        especialidades_stats = cursor.fetchall()
        if especialidades_stats:
            print("\n🩺 Especialidades por área:")
            for area, count in especialidades_stats:
                print(f"   • {area}: {count}")
        
        # Resumen de actividad
        cursor.execute("SELECT COUNT(*) FROM sesion_terapia WHERE estado = 'en_curso'")
        sesiones_activas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sesion_pedagogica WHERE estado = 'en_curso'")
        clases_activas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM paciente WHERE estado = 'activo'")
        pacientes_activos = cursor.fetchone()[0]
        
        print(f"\n📈 Actividad actual:")
        print(f"   • Pacientes activos: {pacientes_activos}")
        print(f"   • Sesiones terapéuticas activas: {sesiones_activas}")
        print(f"   • Sesiones pedagógicas activas: {clases_activas}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error mostrando resumen: {e}")
        return False

def main():
    """Función principal de verificación"""
    try:
        # Cargar configuración
        config = load_config()
        
        # Header
        print("\n🏥 CENTRO TÍA GLENDA - VERIFICACIÓN COMPLETA DEL SISTEMA")
        print("=" * 70)
        
        # Conectar a la base de datos
        print("🔍 Conectando a la base de datos...")
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        print("✅ Conexión exitosa\n")
        
        # Verificaciones
        structure_ok = verify_structure(cursor)
        total_data, tables_with_data = verify_data(cursor)
        business_ok = verify_business_logic(cursor)
        
        # Resumen del sistema (solo si hay datos)
        if total_data > 0:
            show_system_summary(cursor)
        
        # Evaluación final
        print("\n" + "=" * 70)
        print("🎯 EVALUACIÓN FINAL")
        print("=" * 70)
        
        if structure_ok and total_data >= 50 and business_ok:
            print("🟢 ESTADO GENERAL: SISTEMA COMPLETAMENTE FUNCIONAL")
            print("✨ Todos los componentes están correctamente configurados")
            print("🚀 El sistema está listo para producción")
        elif structure_ok and total_data > 0:
            print("🟡 ESTADO GENERAL: SISTEMA PARCIALMENTE FUNCIONAL")
            print("⚠️  Algunos datos o validaciones pueden faltar")
            print("💡 Revisar las advertencias mostradas arriba")
        elif structure_ok:
            print("🟠 ESTADO GENERAL: ESTRUCTURA LISTA, SIN DATOS")
            print("📋 Ejecutar: 02_cargar_datos.py para cargar datos")
        else:
            print("🔴 ESTADO GENERAL: SISTEMA NO FUNCIONAL")
            print("💥 La estructura de base de datos está incompleta")
            print("📋 Ejecutar: 01_ejecutar_estructura.py primero")
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Verificaciones:")
        print("   • ¿PostgreSQL está ejecutándose?")
        print("   • ¿Configuración correcta en config_db.txt?")
        print("   • ¿Base de datos existe? (ejecutar 01_ejecutar_estructura.py)")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()