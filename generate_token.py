# generate_token.py - Generar un token JWT válido para pruebas

import sys
import os
sys.path.append('.')

from src.utils.general.security import SecurityUtils
from datetime import datetime, timedelta

def main():
    print("Generador de Token JWT para Pruebas")
    print("=" * 50)
    
    # Datos de usuario de prueba (usar datos reales de tu base de datos)
    user_data = {
        'id': 1,
        'usuario': 'admin.norte',
        'rol': 'Administrador'
    }
    
    try:
        # Generar token con 24 horas de duración
        token = SecurityUtils.generate_token(user_data, expires_hours=24)
        
        print("Token generado exitosamente:")
        print(f"Usuario: {user_data['usuario']}")
        print(f"Rol: {user_data['rol']}")
        print("Valido por: 24 horas")
        print(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Expira: {(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("TOKEN JWT:")
        print("-" * 50)
        print(token)
        print("-" * 50)
        print()
        print("Para usar en el frontend:")
        print("1. Abre la consola del navegador (F12)")
        print("2. Ejecuta:")
        print(f'   localStorage.setItem("jwt_token", "{token}")')
        print("3. Recarga la página")
        print()
        print("Para usar en pruebas de API:")
        print(f'   Authorization: Bearer {token}')
        
    except Exception as e:
        print(f"Error generando token: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())