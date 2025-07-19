import unittest
import sys
import os

# Agregar el directorio padre al path para importar modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.general.security import SecurityUtils
from src.utils.general.validators import Validators


class TestSecurityUtils(unittest.TestCase):
    """Pruebas para utilidades de seguridad"""

    def test_hash_password(self):
        """Probar hasheo de contraseñas"""
        password = "test_password_123"
        hashed = SecurityUtils.hash_password(password)

        self.assertIsNotNone(hashed)
        self.assertNotEqual(password, hashed)
        self.assertTrue(len(hashed) > 50)  # bcrypt produce hashes largos

    def test_verify_password(self):
        """Probar verificacion de contraseñas"""
        password = "test_password_123"
        hashed = SecurityUtils.hash_password(password)

        # Contraseña correcta
        self.assertTrue(SecurityUtils.verify_password(password, hashed))

        # Contraseña incorrecta
        self.assertFalse(SecurityUtils.verify_password("wrong_password", hashed))

    def test_generate_token(self):
        """Probar generacion de tokens JWT"""
        user_data = {
            'id': 1,
            'usuario': 'test_user',
            'rol': 'Administrador'
        }

        token = SecurityUtils.generate_token(user_data)
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 50)  # JWT es largo

    def test_verify_token(self):
        """Probar verificacion de tokens JWT"""
        user_data = {
            'id': 1,
            'usuario': 'test_user',
            'rol': 'Administrador'
        }

        token = SecurityUtils.generate_token(user_data)
        result = SecurityUtils.verify_token(token)

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['user_id'], user_data['id'])
        self.assertEqual(result['data']['username'], user_data['usuario'])


class TestValidators(unittest.TestCase):
    """Pruebas para validadores"""

    def test_validate_required_fields(self):
        """Probar validacion de campos requeridos"""
        data = {
            'campo1': 'valor1',
            'campo2': '',
            'campo3': 'valor3'
        }

        # Campos que existen
        result = Validators.validate_required_fields(data, ['campo1', 'campo3'])
        self.assertTrue(result['valid'])

        # Campo faltante
        result = Validators.validate_required_fields(data, ['campo1', 'campo4'])
        self.assertFalse(result['valid'])

        # Campo vacio
        result = Validators.validate_required_fields(data, ['campo1', 'campo2'])
        self.assertFalse(result['valid'])

    def test_validate_email(self):
        """Probar validacion de emails"""
        # Email valido con dominio real
        result = Validators.validate_email('test@gmail.com')
        print(f"Resultado email valido: {result}")  # Debug
        self.assertTrue(result['valid'])

        # Email invalido
        result = Validators.validate_email('email_invalido')
        print(f"Resultado email invalido: {result}")  # Debug
        self.assertFalse(result['valid'])

    def test_validate_password(self):
        """Probar validacion de contraseñas"""
        # Contraseña valida
        result = Validators.validate_password('Password123!')
        self.assertTrue(result['valid'])

        # Contraseña muy corta
        result = Validators.validate_password('123')
        self.assertFalse(result['valid'])

        # Sin mayuscula
        result = Validators.validate_password('password123!')
        self.assertFalse(result['valid'])

        # Sin minuscula
        result = Validators.validate_password('PASSWORD123!')
        self.assertFalse(result['valid'])

        # Sin numero
        result = Validators.validate_password('Password!')
        self.assertFalse(result['valid'])

    def test_validate_username(self):
        """Probar validacion de nombres de usuario"""
        # Usuario valido
        result = Validators.validate_username('usuario123')
        self.assertTrue(result['valid'])

        # Usuario muy corto
        result = Validators.validate_username('ab')
        self.assertFalse(result['valid'])

        # Usuario muy largo
        result = Validators.validate_username('a' * 51)
        self.assertFalse(result['valid'])

        # Caracteres especiales invalidos
        result = Validators.validate_username('usuario@#$')
        self.assertFalse(result['valid'])

    def test_validate_cedula(self):
        """Probar validacion de cedulas"""
        # Cedula valida
        result = Validators.validate_cedula('12345678')
        self.assertTrue(result['valid'])

        # Cedula muy corta
        result = Validators.validate_cedula('123')
        self.assertFalse(result['valid'])

        # Cedula con letras
        result = Validators.validate_cedula('12345abc')
        self.assertFalse(result['valid'])

    def test_validate_phone(self):
        """Probar validacion de telefonos"""
        # Telefono valido
        result = Validators.validate_phone('+50612345678')
        self.assertTrue(result['valid'])

        # Telefono vacio (opcional)
        result = Validators.validate_phone('')
        self.assertTrue(result['valid'])

        # Telefono muy corto
        result = Validators.validate_phone('123')
        self.assertFalse(result['valid'])


if __name__ == '__main__':
    print("Ejecutando pruebas unitarias...")
    unittest.main()