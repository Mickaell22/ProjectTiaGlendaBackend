#!/usr/bin/env python3
"""
Script para generar el hash correcto del password admin
"""
import bcrypt
import sys
sys.path.append('.')

from src.utils.database.connection_db import DataBaseHandle

def generate_password_hash(password):
    """Generar hash de password usando bcrypt"""
    salt = bcrypt.gensalt()
    hash_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hash_password.decode('utf-8')

def fix_admin_password():
    """Actualizar el password del usuario admin"""
    print("=== ACTUALIZANDO PASSWORD DEL ADMIN ===")
    
    # Password correcto
    new_password = "Admin123!"
    print(f"Generando hash para password: {new_password}")
    
    # Generar hash
    password_hash = generate_password_hash(new_password)
    print(f"Hash generado: {password_hash}")
    
    # Actualizar en base de datos
    print("Actualizando en base de datos...")
    
    query = """
    UPDATE usuario 
    SET password_hash = %s, 
        fecha_modificacion = CURRENT_TIMESTAMP 
    WHERE username = 'admin'
    """
    
    success = DataBaseHandle.ExecuteNonQuery(query, [password_hash])
    
    if success:
        print("✅ Password actualizado exitosamente!")
        
        # Verificar el cambio
        verify_query = "SELECT username, password_hash FROM usuario WHERE username = 'admin'"
        result = DataBaseHandle.getRecords(verify_query, size=1)
        
        if result:
            print(f"✅ Verificación - Usuario: {result['username']}")
            print(f"✅ Verificación - Hash: {result['password_hash'][:50]}...")
        else:
            print("❌ Error al verificar el usuario")
            
    else:
        print("❌ Error al actualizar el password")
        return False
    
    return True

def test_login():
    """Probar el login con las nuevas credenciales"""
    print("\n=== PROBANDO LOGIN ===")
    
    # Obtener usuario
    query = "SELECT * FROM usuario WHERE username = 'admin'"
    user = DataBaseHandle.getRecords(query, size=1)
    
    if not user:
        print("❌ Usuario admin no encontrado")
        return False
    
    stored_hash = user['password_hash']
    test_password = "Admin123!"
    
    # Verificar password
    is_valid = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
    
    if is_valid:
        print(f"✅ Login exitoso con username: admin, password: {test_password}")
        return True
    else:
        print(f"❌ Login fallido con password: {test_password}")
        return False

if __name__ == "__main__":
    print("Iniciando actualización de password admin...")
    
    # Actualizar password
    if fix_admin_password():
        # Probar login
        test_login()
        print("\n🎉 ¡Todo listo! Credenciales: admin / Admin123!")
    else:
        print("\n❌ Error en la actualización")
        
    print("\nPuedes eliminar este archivo después de usarlo.")