import re
from email_validator import validate_email, EmailNotValidError
from src.utils.general.logs import HandleLogs


class Validators:

    @staticmethod
    def validate_required_fields(data, required_fields):
        """Validar campos requeridos"""
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == "":
                missing_fields.append(field)

        if missing_fields:
            return {
                'valid': False,
                'message': f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            }
        return {'valid': True, 'message': 'Validacion exitosa'}

    @staticmethod
    def validate_email(email):
        """Validar formato de email"""
        try:
            validate_email(email)
            return {'valid': True, 'message': 'Email valido'}
        except EmailNotValidError as e:
            return {'valid': False, 'message': f'Email invalido: {str(e)}'}

    @staticmethod
    def validate_password(password):
        """Validar contraseña"""
        errors = []

        if len(password) < 8:
            errors.append("debe tener al menos 8 caracteres")

        if not re.search(r"[A-Z]", password):
            errors.append("debe contener al menos una mayuscula")

        if not re.search(r"[a-z]", password):
            errors.append("debe contener al menos una minuscula")

        if not re.search(r"\d", password):
            errors.append("debe contener al menos un numero")

        if errors:
            return {
                'valid': False,
                'message': f"Contrasena invalida: {', '.join(errors)}"
            }
        return {'valid': True, 'message': 'Contrasena valida'}

    @staticmethod
    def validate_username(username):
        """Validar nombre de usuario"""
        if len(username) < 3:
            return {'valid': False, 'message': 'Usuario debe tener al menos 3 caracteres'}

        if len(username) > 50:
            return {'valid': False, 'message': 'Usuario no puede tener mas de 50 caracteres'}

        if not re.match("^[a-zA-Z0-9._-]+$", username):
            return {
                'valid': False,
                'message': 'Usuario solo puede contener letras, numeros, puntos, guiones y guiones bajos'
            }

        return {'valid': True, 'message': 'Usuario valido'}

    @staticmethod
    def validate_cedula(cedula):
        """Validar formato de cedula"""
        if not cedula or len(cedula) < 7 or len(cedula) > 20:
            return {'valid': False, 'message': 'Cedula debe tener entre 7 y 20 caracteres'}

        if not re.match("^[0-9]+$", cedula):
            return {'valid': False, 'message': 'Cedula solo puede contener numeros'}

        return {'valid': True, 'message': 'Cedula valida'}

    @staticmethod
    def validate_phone(phone):
        """Validar formato de telefono"""
        if not phone:
            return {'valid': True, 'message': 'Telefono es opcional'}

        # Remover espacios y caracteres especiales para validar
        clean_phone = re.sub(r'[^\d+]', '', phone)

        if len(clean_phone) < 8 or len(clean_phone) > 15:
            return {'valid': False, 'message': 'Telefono debe tener entre 8 y 15 digitos'}

        return {'valid': True, 'message': 'Telefono valido'}

    @staticmethod
    def validate_usuario_data(data, is_update=False):
        """Validar datos completos de usuario"""
        errors = []

        # Campos requeridos para crear usuario
        if not is_update:
            required_validation = Validators.validate_required_fields(
                data, ['usuario', 'contrasenia', 'persona_id', 'rol_id']
            )
            if not required_validation['valid']:
                errors.append(required_validation['message'])

        # Validar usuario si está presente
        if 'usuario' in data and data['usuario']:
            username_validation = Validators.validate_username(data['usuario'])
            if not username_validation['valid']:
                errors.append(username_validation['message'])

        # Validar contraseña si está presente
        if 'contrasenia' in data and data['contrasenia']:
            password_validation = Validators.validate_password(data['contrasenia'])
            if not password_validation['valid']:
                errors.append(password_validation['message'])

        # Validar IDs numéricos
        numeric_fields = ['persona_id', 'rol_id', 'usuario_creacion', 'usuario_modificacion']
        for field in numeric_fields:
            if field in data and data[field]:
                try:
                    int(data[field])
                except (ValueError, TypeError):
                    errors.append(f"{field} debe ser un numero entero")

        if errors:
            return {'valid': False, 'message': '; '.join(errors)}

        return {'valid': True, 'message': 'Datos de usuario validos'}