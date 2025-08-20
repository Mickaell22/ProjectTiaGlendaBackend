#!/usr/bin/env python3
"""
verificar_datos.py
Script para verificar el estado de los datos en la base de datos
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

def main():
    """Función principal de verificación"""
    try:
        # Cargar configuración
        config = load_config()
        
        # Conectar a la base de datos
        print("🔍 Conectando a la base de datos...")
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        print("✅ Conexión exitosa a la base de datos")
        print("")
        print("📋 Estado actual de los datos:")
        print("=" * 60)
        
        # Definir verificaciones
        checks = [
            ('Centros', 'SELECT COUNT(*) FROM centros'),
            ('Roles', 'SELECT COUNT(*) FROM rol'),  
            ('Especialidades', 'SELECT COUNT(*) FROM especialidad'),
            ('Usuarios', 'SELECT COUNT(*) FROM usuario'),
            ('Personal', 'SELECT COUNT(*) FROM personal'),
            ('Tutores', 'SELECT COUNT(*) FROM tutor'),
            ('Pacientes', 'SELECT COUNT(*) FROM paciente'),
            ('Especialidades de Pacientes', 'SELECT COUNT(*) FROM paciente_especialidades'),
            ('Especialidades de Personal', 'SELECT COUNT(*) FROM personal_especialidades'),
            ('Sesiones Terapéuticas', 'SELECT COUNT(*) FROM sesion_terapia'),
            ('Sesiones Pedagógicas', 'SELECT COUNT(*) FROM sesion_pedagogica'),
            ('Inscripciones Terapia', 'SELECT COUNT(*) FROM sesion_paciente'),
            ('Inscripciones Pedagogía', 'SELECT COUNT(*) FROM sesion_estudiante'),
            ('Cronogramas Sesiones', 'SELECT COUNT(*) FROM cronograma_sesiones'),
            ('Cronogramas Clases', 'SELECT COUNT(*) FROM cronograma_clases'),
            ('Documentos Personal', 'SELECT COUNT(*) FROM documentos_personal'),
            ('Documentos Pacientes', 'SELECT COUNT(*) FROM documentos_paciente')
        ]
        
        total_registros = 0
        tablas_con_datos = 0
        
        for nombre, query in checks:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                total_registros += count
                
                if count > 0:
                    tablas_con_datos += 1
                    status = "✅"
                else:
                    status = "⚪"
                
                print(f"{status} {nombre:<25}: {count:>3} registros")
                
            except psycopg2.Error as e:
                print(f"❌ {nombre:<25}: Error ({str(e)[:30]}...)")
            except Exception as e:
                print(f"❌ {nombre:<25}: Error ({str(e)[:30]}...)")
        
        print("=" * 60)
        print(f"📊 Total registros: {total_registros}")
        print(f"📋 Tablas con datos: {tablas_con_datos}/{len(checks)}")
        print("")
        
        # Análisis del estado
        if total_registros == 0:
            print("🔴 ESTADO: Base de datos VACÍA")
            print("💡 Usar opción 1 para cargar datos iniciales")
        elif total_registros < 20:
            print("🟡 ESTADO: Pocos datos detectados")
            print("💡 Posible carga incompleta o datos parciales")
        elif tablas_con_datos < 10:
            print("🟠 ESTADO: Carga parcial")
            print("💡 Algunas tablas están vacías")
        else:
            print("🟢 ESTADO: Base de datos con DATOS COMPLETOS")
            print("✨ Sistema listo para usar")
        
        # Información adicional si hay datos
        if total_registros > 0:
            print("")
            print("📋 Información adicional:")
            print("-" * 40)
            
            # Verificar centros
            try:
                cursor.execute("SELECT nombre, codigo FROM centros ORDER BY nombre")
                centros = cursor.fetchall()
                if centros:
                    print("🏥 Centros configurados:")
                    for nombre, codigo in centros:
                        print(f"   • {nombre} ({codigo})")
            except:
                pass
            
            # Verificar usuarios
            try:
                cursor.execute("""
                    SELECT COUNT(*) as total,
                           COUNT(CASE WHEN r.nombre = 'Administrador' THEN 1 END) as admins,
                           COUNT(CASE WHEN r.nombre = 'Terapeuta' THEN 1 END) as terapeutas,
                           COUNT(CASE WHEN r.nombre = 'Pedagógico' THEN 1 END) as pedagogos
                    FROM usuario u 
                    LEFT JOIN rol r ON u.rol_id = r.id
                """)
                stats = cursor.fetchone()
                if stats and stats[0] > 0:
                    print("👥 Usuarios por rol:")
                    print(f"   • Administradores: {stats[1] or 0}")
                    print(f"   • Terapeutas: {stats[2] or 0}")
                    print(f"   • Pedagogos: {stats[3] or 0}")
            except:
                pass
        
        cursor.close()
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión: {e}")
        print("💡 Verificaciones:")
        print("   • PostgreSQL está ejecutándose?")
        print("   • Configuración correcta en config_db.txt?")
        print("   • Base de datos existe? (usar EJECUTAR.bat primero)")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()