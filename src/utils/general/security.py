import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from src.utils.general.config import get_config
from src.utils.general.logs import HandleLogs


class SecurityUtils:

    @staticmethod
    def hash_password(password):
        """Hashear contraseña con bcrypt"""
        try:
            # Generar salt y hashear
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            HandleLogs.write_error(f"SecurityUtils.hash_password - Error: {str(e)}")
            return None

    @staticmethod
    def verify_password(password, hashed_password):
        """Verificar contraseña"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            HandleLogs.write_error(f"SecurityUtils.verify_password - Error: {str(e)}")
            return False

    @staticmethod
    def generate_token(user_data, expires_hours=24):
        """Generar token JWT"""
        try:
            config = get_config()
            secret_key = config.get('secret_jwt')

            # Payload del token (usando datetime con timezone)
            now = datetime.now(timezone.utc)
            payload = {
                'user_id': user_data['id'],
                'username': user_data['usuario'],
                'rol': user_data['rol'],
                'exp': now + timedelta(hours=expires_hours),
                'iat': now
            }

            # Generar token
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            return token

        except Exception as e:
            HandleLogs.write_error(f"SecurityUtils.generate_token - Error: {str(e)}")
            return None

    @staticmethod
    def verify_token(token):
        """Verificar y decodificar token JWT"""
        try:
            config = get_config()
            secret_key = config.get('secret_jwt')

            # Decodificar token
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return {
                'success': True,
                'data': payload,
                'message': 'Token valido'
            }

        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'data': None,
                'message': 'Token expirado'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'data': None,
                'message': 'Token invalido'
            }
        except Exception as e:
            HandleLogs.write_error(f"SecurityUtils.verify_token - Error: {str(e)}")
            return {
                'success': False,
                'data': None,
                'message': f'Error verificando token: {str(e)}'
            }