import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.general.security import SecurityUtils

# Generar hash para cualquier contraseña
passwords_to_hash = ["admin123"]

for password in passwords_to_hash:
    hashed = SecurityUtils.hash_password(password)
    print(f"Contraseña: {password}")
    print(f"Hash generado: {hashed}")
    print(f"UPDATE usuario SET contrasenia = '{hashed}' WHERE usuario = 'admin';")
    print("-" * 60)