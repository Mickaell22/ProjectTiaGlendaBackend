#!/usr/bin/env python3
"""
Test de conexión a base de datos Railway
Ejecutar antes de deployment para verificar configuración
"""

import os
import sys
sys.path.append('.')

from src.utils.database.connection_db import DataBaseHandle
from src.utils.general.config import get_config


def test_database_connection():
    """Probar conexión a la base de datos Railway"""
    print("=" * 60)
    print("TEST DE CONEXIÓN A BASE DE DATOS RAILWAY")
    print("=" * 60)
    
    # Mostrar configuración actual
    print("\n1. CONFIGURACIÓN ACTUAL:")
    print("-" * 40)
    config = get_config()
    
    print(f"DB Host: {config.get('db_host', 'N/A')}")
    print(f"DB Port: {config.get('db_port', 'N/A')}")
    print(f"DB Name: {config.get('db_name', 'N/A')}")
    print(f"DB User: {config.get('db_user', 'N/A')}")
    print(f"DB Pass: {'*' * len(config.get('db_pass', '')) if config.get('db_pass') else 'N/A'}")
    
    # Mostrar variables de entorno relevantes
    print(f"\nDATABASE_URL: {'Set' if os.getenv('DATABASE_URL') else 'Not set'}")
    print(f"DATABASE_PUBLIC_URL: {'Set' if os.getenv('DATABASE_PUBLIC_URL') else 'Not set'}")
    print(f"RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'Not set')}")
    
    # Probar conexión
    print("\n2. PROBANDO CONEXIÓN:")
    print("-" * 40)
    
    try:
        conn = DataBaseHandle.get_connection()
        
        if conn:
            print("✅ Conexión exitosa!")
            
            # Probar consulta simple
            result = DataBaseHandle.getRecords("SELECT 1 as test", size=1)
            if result:
                print("✅ Consulta de prueba exitosa!")
                print(f"   Resultado: {result}")
            else:
                print("❌ Error en consulta de prueba")
                
            conn.close()
        else:
            print("❌ Error al conectar a la base de datos")
            return False
            
    except Exception as e:
        print(f"❌ Excepción durante conexión: {str(e)}")
        return False
    
    print("\n3. VERIFICANDO TABLAS:")
    print("-" * 40)
    
    try:
        # Verificar que existen tablas principales
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
        """
        
        tables = DataBaseHandle.getRecords(tables_query)
        
        if tables:
            print(f"✅ Se encontraron {len(tables)} tablas:")
            for table in tables[:5]:  # Mostrar primeras 5
                print(f"   - {table['table_name']}")
            if len(tables) > 5:
                print(f"   ... y {len(tables) - 5} más")
        else:
            print("⚠️  No se encontraron tablas (base de datos vacía)")
            
    except Exception as e:
        print(f"❌ Error verificando tablas: {str(e)}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
    
    return True


def show_railway_setup_instructions():
    """Mostrar instrucciones para configurar Railway"""
    print("\n" + "=" * 60)
    print("INSTRUCCIONES DE CONFIGURACIÓN RAILWAY")
    print("=" * 60)
    
    print("\n1. VARIABLES DE ENTORNO EN RAILWAY:")
    print("   Railway establecerá automáticamente:")
    print("   - DATABASE_URL")
    print("   - PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD")
    
    print("\n2. VARIABLES ADICIONALES A CONFIGURAR:")
    print("   railway variables set JWT_SECRET=tu_jwt_secret_super_seguro")
    print("   railway variables set AMBIENTE=PRODUCTION")
    print("   railway variables set DEBUG=False")
    print("   railway variables set CORS_ORIGINS=https://tu-frontend.railway.app")
    
    print("\n3. VERIFICAR DEPLOYMENT:")
    print("   - Backend: https://tu-backend.railway.app/health")
    print("   - Docs: https://tu-backend.railway.app/docs")
    
    print("\n4. SI HAY PROBLEMAS:")
    print("   - Verificar logs en Railway Dashboard")
    print("   - Usar DATABASE_PUBLIC_URL si hay problemas de conectividad")
    print("   - Verificar que las tablas existan en la base de datos")


if __name__ == "__main__":
    print("Iniciando test de conexión a Railway PostgreSQL...")
    
    # Test de conexión
    success = test_database_connection()
    
    # Mostrar instrucciones
    show_railway_setup_instructions()
    
    if success:
        print("\n🎉 ¡La configuración de base de datos está lista para Railway!")
    else:
        print("\n⚠️  Revisar configuración antes del deployment.")
    
    sys.exit(0 if success else 1)