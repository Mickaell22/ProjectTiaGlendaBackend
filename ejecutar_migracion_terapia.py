#!/usr/bin/env python3
"""
Script para ejecutar migración específica de sesiones terapia
"""

import psycopg2
import sys
import os

def ejecutar_migracion():
    """Ejecutar migración para sesiones terapia"""
    
    # Configuración de conexión de DEVELOPMENT
    config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'centro_tia_glenda',
        'user': 'postgres',
        'password': '1234'
    }
    
    try:
        print("=== INICIANDO MIGRACIÓN SESIONES TERAPIA ===")
        print(f"Conectando a BD: {config['database']} en {config['host']}:{config['port']}")
        
        # Conectar a la base de datos
        conn = psycopg2.connect(**config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("[OK] Conexion establecida")
        
        # Leer el archivo de migración
        migration_file = "migration_sesiones_terapia_only.sql"
        if not os.path.exists(migration_file):
            raise Exception(f"Archivo de migracion no encontrado: {migration_file}")
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print(f"[OK] Archivo de migracion leido: {migration_file}")
        
        # Ejecutar la migración
        print("Ejecutando migracion...")
        cursor.execute(migration_sql)
        
        print("[OK] Migracion ejecutada exitosamente")
        
        # Verificar las columnas agregadas
        print("\n=== VERIFICACION POST-MIGRACION ===")
        
        # Verificar cronograma_sesiones
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'cronograma_sesiones' 
            AND column_name = 'fecha_realizacion'
        """)
        result = cursor.fetchone()
        if result:
            print(f"[OK] cronograma_sesiones.fecha_realizacion: {result[1]} (nullable: {result[2]})")
        else:
            print("[ERROR] cronograma_sesiones.fecha_realizacion: NO ENCONTRADA")
        
        # Verificar asistencia_sesiones
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'asistencia_sesiones' 
            AND column_name = 'llegada_tardanza_minutos'
        """)
        result = cursor.fetchone()
        if result:
            print(f"[OK] asistencia_sesiones.llegada_tardanza_minutos: {result[1]} (default: {result[3]})")
        else:
            print("[ERROR] asistencia_sesiones.llegada_tardanza_minutos: NO ENCONTRADA")
        
        # Verificar función
        cursor.execute("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_name = 'calcular_tardanza_asistencia'
        """)
        result = cursor.fetchone()
        if result:
            print(f"[OK] Funcion calcular_tardanza_asistencia: EXISTE")
        else:
            print("[ERROR] Funcion calcular_tardanza_asistencia: NO ENCONTRADA")
        
        # Verificar trigger
        cursor.execute("""
            SELECT trigger_name, event_object_table
            FROM information_schema.triggers 
            WHERE trigger_name = 'trigger_calcular_tardanza'
            AND event_object_table = 'asistencia_sesiones'
        """)
        result = cursor.fetchone()
        if result:
            print(f"[OK] Trigger trigger_calcular_tardanza: EXISTE en {result[1]}")
        else:
            print("[ERROR] Trigger trigger_calcular_tardanza: NO ENCONTRADO")
        
        cursor.close()
        conn.close()
        
        print("\n=== MIGRACION COMPLETADA EXITOSAMENTE ===")
        return True
        
    except psycopg2.Error as e:
        print(f"[ERROR] Error de PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error general: {e}")
        return False

if __name__ == "__main__":
    success = ejecutar_migracion()
    sys.exit(0 if success else 1)