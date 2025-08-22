import re
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, date
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
    def validate_name(name, field_name="nombre"):
        """Validar nombres y apellidos"""
        if not name or len(name.strip()) < 2:
            return {'valid': False, 'message': f'{field_name} debe tener al menos 2 caracteres'}

        if len(name.strip()) > 100:
            return {'valid': False, 'message': f'{field_name} no puede tener mas de 100 caracteres'}

        # Solo letras, espacios, acentos y apostrofes
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s']+$", name):
            return {
                'valid': False,
                'message': f'{field_name} solo puede contener letras, espacios y apostrofes'
            }

        return {'valid': True, 'message': f'{field_name} valido'}

    @staticmethod
    def validate_date(date_string, field_name="fecha"):
        """Validar formato de fecha"""
        if not date_string:
            return {'valid': True, 'message': f'{field_name} es opcional'}

        try:
            # Intentar parsear la fecha en formato YYYY-MM-DD
            if isinstance(date_string, str):
                parsed_date = datetime.strptime(date_string, '%Y-%m-%d').date()
            elif isinstance(date_string, date):
                parsed_date = date_string
            else:
                return {'valid': False, 'message': f'{field_name} debe estar en formato YYYY-MM-DD'}

            # Verificar que la fecha no sea futura para fecha de nacimiento
            if field_name.lower() == 'fecha_nacimiento' and parsed_date > date.today():
                return {'valid': False, 'message': 'Fecha de nacimiento no puede ser futura'}

            # Verificar que la fecha de nacimiento no sea muy antigua (más de 120 años)
            if field_name.lower() == 'fecha_nacimiento':
                min_date = date.today().replace(year=date.today().year - 120)
                if parsed_date < min_date:
                    return {'valid': False, 'message': 'Fecha de nacimiento no puede ser anterior a 120 años'}

            return {'valid': True, 'message': f'{field_name} valida'}

        except ValueError:
            return {'valid': False, 'message': f'{field_name} debe estar en formato YYYY-MM-DD'}

    @staticmethod
    def validate_direccion(direccion):
        """Validar direccion"""
        if not direccion:
            return {'valid': True, 'message': 'Direccion es opcional'}

        if len(direccion.strip()) > 255:
            return {'valid': False, 'message': 'Direccion no puede tener mas de 255 caracteres'}

        return {'valid': True, 'message': 'Direccion valida'}

    @staticmethod
    def validate_usuario_data(data, is_update=False):
        """Validar datos completos de usuario"""
        errors = []

        # Campos requeridos para crear usuario
        if not is_update:
            required_validation = Validators.validate_required_fields(
                data, ['usuario', 'contrasenia', 'id_persona', 'id_rol']
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
        numeric_fields = ['id_persona', 'id_rol', 'usuario_creacion', 'usuario_modificacion']
        for field in numeric_fields:
            if field in data and data[field]:
                try:
                    int(data[field])
                except (ValueError, TypeError):
                    errors.append(f"{field} debe ser un numero entero")

        if errors:
            return {'valid': False, 'message': '; '.join(errors)}

        return {'valid': True, 'message': 'Datos de usuario validos'}

    @staticmethod
    def validate_persona_data(data, is_update=False):
        """Validar datos completos de persona"""
        errors = []

        # Campos requeridos para crear persona
        if not is_update:
            required_validation = Validators.validate_required_fields(
                data, ['nombre', 'apellido', 'cedula']
            )
            if not required_validation['valid']:
                errors.append(required_validation['message'])

        # Validar nombre si está presente
        if 'nombre' in data and data['nombre']:
            name_validation = Validators.validate_name(data['nombre'], 'Nombre')
            if not name_validation['valid']:
                errors.append(name_validation['message'])

        # Validar apellido si está presente
        if 'apellido' in data and data['apellido']:
            lastname_validation = Validators.validate_name(data['apellido'], 'Apellido')
            if not lastname_validation['valid']:
                errors.append(lastname_validation['message'])

        # Validar cedula si está presente
        if 'cedula' in data and data['cedula']:
            cedula_validation = Validators.validate_cedula(data['cedula'])
            if not cedula_validation['valid']:
                errors.append(cedula_validation['message'])

        # Validar telefono si está presente
        if 'telefono' in data and data['telefono']:
            phone_validation = Validators.validate_phone(data['telefono'])
            if not phone_validation['valid']:
                errors.append(phone_validation['message'])

        # Validar correo si está presente
        if 'correo' in data and data['correo']:
            email_validation = Validators.validate_email(data['correo'])
            if not email_validation['valid']:
                errors.append(email_validation['message'])

        # Validar direccion si está presente
        if 'direccion' in data and data['direccion']:
            address_validation = Validators.validate_direccion(data['direccion'])
            if not address_validation['valid']:
                errors.append(address_validation['message'])

        # Validar fecha de nacimiento si está presente
        if 'fecha_nacimiento' in data and data['fecha_nacimiento']:
            date_validation = Validators.validate_date(data['fecha_nacimiento'], 'fecha_nacimiento')
            if not date_validation['valid']:
                errors.append(date_validation['message'])

        # Validar estado si está presente
        if 'estado' in data and data['estado']:
            valid_states = ['activo', 'inactivo']
            if data['estado'] not in valid_states:
                errors.append(f"Estado debe ser uno de: {', '.join(valid_states)}")

        # Validar IDs numéricos
        numeric_fields = ['usuario_creacion', 'usuario_modificacion']
        for field in numeric_fields:
            if field in data and data[field]:
                try:
                    int(data[field])
                except (ValueError, TypeError):
                    errors.append(f"{field} debe ser un numero entero")

        if errors:
            return {'valid': False, 'message': '; '.join(errors)}

        return {'valid': True, 'message': 'Datos de persona validos'}

    @staticmethod
    def validate_especialidad_data(data, is_update=False):
        """Validar datos completos de especialidad"""
        errors = []

        # Campos requeridos para crear especialidad
        if not is_update:
            required_validation = Validators.validate_required_fields(
                data, ['nombre', 'area']
            )
            if not required_validation['valid']:
                errors.append(required_validation['message'])

        # Validar nombre si está presente
        if 'nombre' in data and data['nombre']:
            name_validation = Validators.validate_especialidad_name(data['nombre'])
            if not name_validation['valid']:
                errors.append(name_validation['message'])

        # Validar área si está presente
        if 'area' in data and data['area']:
            area_validation = Validators.validate_area(data['area'])
            if not area_validation['valid']:
                errors.append(area_validation['message'])

        # Validar estado si está presente
        if 'estado' in data and data['estado']:
            valid_states = ['activo', 'inactivo']
            if data['estado'] not in valid_states:
                errors.append(f"Estado debe ser uno de: {', '.join(valid_states)}")

        # Validar IDs numéricos
        numeric_fields = ['usuario_creacion', 'usuario_modificacion']
        for field in numeric_fields:
            if field in data and data[field]:
                try:
                    int(data[field])
                except (ValueError, TypeError):
                    errors.append(f"{field} debe ser un numero entero")

        if errors:
            return {'valid': False, 'message': '; '.join(errors)}

        return {'valid': True, 'message': 'Datos de especialidad validos'}

    @staticmethod
    def validate_especialidad_name(nombre):
        """Validar nombre de especialidad"""
        if not nombre or len(nombre.strip()) < 3:
            return {'valid': False, 'message': 'Nombre de especialidad debe tener al menos 3 caracteres'}

        if len(nombre.strip()) > 150:
            return {'valid': False, 'message': 'Nombre de especialidad no puede tener mas de 150 caracteres'}

        # Permitir letras, números, espacios, paréntesis, guiones y algunos caracteres especiales
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s\(\)\-\.\,\/]+$", nombre):
            return {
                'valid': False,
                'message': 'Nombre de especialidad contiene caracteres no permitidos'
            }

        return {'valid': True, 'message': 'Nombre de especialidad valido'}

    @staticmethod
    def validate_area(area):
        """Validar área de especialidad"""
        valid_areas = ['Especialidad terapéutica', 'Especialidad pedagógica']

        if area not in valid_areas:
            return {
                'valid': False,
                'message': f"Área debe ser una de: {', '.join(valid_areas)}"
            }

        return {'valid': True, 'message': 'Área valida'}

    @staticmethod
    def validate_personal_data(data, is_update=False):
        """Validar datos completos de personal"""
        errors = []

        # Campos requeridos para crear personal
        if not is_update:
            required_validation = Validators.validate_required_fields(
                data, ['persona_id']
            )
            if not required_validation['valid']:
                errors.append(required_validation['message'])

        # Validar persona_id si está presente
        if 'persona_id' in data and data['persona_id']:
            try:
                persona_id = int(data['persona_id'])
                if persona_id <= 0:
                    errors.append("ID de persona debe ser un numero positivo")
            except (ValueError, TypeError):
                errors.append("ID de persona debe ser un numero entero")

        # Validar titulo_profesional si está presente
        if 'titulo_profesional' in data and data['titulo_profesional']:
            titulo_validation = Validators.validate_titulo_profesional(data['titulo_profesional'])
            if not titulo_validation['valid']:
                errors.append(titulo_validation['message'])

        # Validar estado si está presente
        if 'estado' in data and data['estado']:
            valid_states = ['activo', 'inactivo']
            if data['estado'] not in valid_states:
                errors.append(f"Estado debe ser uno de: {', '.join(valid_states)}")

        # Validar IDs numéricos
        numeric_fields = ['usuario_creacion', 'usuario_modificacion']
        for field in numeric_fields:
            if field in data and data[field]:
                try:
                    int(data[field])
                except (ValueError, TypeError):
                    errors.append(f"{field} debe ser un numero entero")

        if errors:
            return {'valid': False, 'message': '; '.join(errors)}

        return {'valid': True, 'message': 'Datos de personal validos'}

    @staticmethod
    def validate_titulo_profesional(titulo):
        """Validar título profesional"""
        if not titulo:
            return {'valid': True, 'message': 'Título profesional es opcional'}

        if len(titulo.strip()) > 200:
            return {'valid': False, 'message': 'Título profesional no puede tener mas de 200 caracteres'}

        # Permitir letras, números, espacios, paréntesis, puntos, comas y algunos caracteres especiales
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s\(\)\-\.\,\/\:]+$", titulo):
            return {
                'valid': False,
                'message': 'Título profesional contiene caracteres no permitidos'
            }

        return {'valid': True, 'message': 'Título profesional valido'}

    @staticmethod
    def validate_tutor_data(data, is_update=False):
        """Validar datos completos de tutor"""
        errors = []

        # Campos requeridos para crear tutor
        if not is_update:
            required_validation = Validators.validate_required_fields(
                data, ['nombre', 'apellido', 'cedula', 'parentesco']
            )
            if not required_validation['valid']:
                errors.append(required_validation['message'])

        # Validar nombre si está presente
        if 'nombre' in data and data['nombre']:
            if len(data['nombre'].strip()) < 2:
                errors.append("Nombre debe tener al menos 2 caracteres")
            if len(data['nombre'].strip()) > 100:
                errors.append("Nombre no puede tener más de 100 caracteres")

        # Validar apellido si está presente
        if 'apellido' in data and data['apellido']:
            if len(data['apellido'].strip()) < 2:
                errors.append("Apellido debe tener al menos 2 caracteres")
            if len(data['apellido'].strip()) > 100:
                errors.append("Apellido no puede tener más de 100 caracteres")

        # Validar cédula si está presente
        if 'cedula' in data and data['cedula']:
            cedula_validation = Validators.validate_cedula(data['cedula'])
            if not cedula_validation['valid']:
                errors.append(cedula_validation['message'])

        # Validar email si está presente
        if 'email' in data and data['email'] and data['email'].strip():
            email_validation = Validators.validate_email(data['email'])
            if not email_validation['valid']:
                errors.append(email_validation['message'])

        # Validar teléfono si está presente
        if 'telefono' in data and data['telefono'] and data['telefono'].strip():
            phone_validation = Validators.validate_phone(data['telefono'])
            if not phone_validation['valid']:
                errors.append(phone_validation['message'])

        # Validar parentesco si está presente
        if 'parentesco' in data and data['parentesco']:
            parentesco_validation = Validators.validate_parentesco(data['parentesco'])
            if not parentesco_validation['valid']:
                errors.append(parentesco_validation['message'])

        # Validar ocupacion si está presente
        if 'ocupacion' in data and data['ocupacion'] and data['ocupacion'].strip():
            if len(data['ocupacion'].strip()) > 100:
                errors.append("Ocupación no puede tener más de 100 caracteres")

        # Validar dirección si está presente
        if 'direccion' in data and data['direccion'] and data['direccion'].strip():
            if len(data['direccion'].strip()) > 255:
                errors.append("Dirección no puede tener más de 255 caracteres")

        # Validar estado si está presente
        if 'estado' in data and data['estado']:
            valid_states = ['activo', 'inactivo']
            if data['estado'] not in valid_states:
                errors.append(f"Estado debe ser uno de: {', '.join(valid_states)}")

        # Validar IDs numéricos
        numeric_fields = ['usuario_creacion', 'usuario_modificacion']
        for field in numeric_fields:
            if field in data and data[field]:
                try:
                    int(data[field])
                except (ValueError, TypeError):
                    errors.append(f"{field} debe ser un numero entero")

        if errors:
            return {'valid': False, 'message': '; '.join(errors)}

        return {'valid': True, 'message': 'Datos de tutor validos'}

    @staticmethod
    def validate_parentesco(parentesco):
        """Validar parentesco del tutor"""
        valid_parentescos = ['padre', 'madre', 'abuelo', 'abuela', 'tio', 'tia', 'hermano', 'hermana', 'tutor_legal']

        if parentesco not in valid_parentescos:
            return {
                'valid': False,
                'message': f"Parentesco debe ser uno de: {', '.join(valid_parentescos)}"
            }

        return {'valid': True, 'message': 'Parentesco valido'}

    @staticmethod
    def validate_paciente_data(data, is_update=False):
        """Validar datos completos de paciente"""
        errors = []

        # Campos requeridos para crear paciente
        if not is_update:
            required_validation = Validators.validate_required_fields(
                data, ['persona_id', 'tutor_id', 'especialidad_id', 'fecha_ingreso', 'fecha_inicio_tratamiento']
            )
            if not required_validation['valid']:
                errors.append(required_validation['message'])

        # Validar persona_id si está presente
        if 'persona_id' in data and data['persona_id']:
            try:
                persona_id = int(data['persona_id'])
                if persona_id <= 0:
                    errors.append("ID de persona debe ser un numero positivo")
            except (ValueError, TypeError):
                errors.append("ID de persona debe ser un numero entero")

        # Validar tutor_id si está presente
        if 'tutor_id' in data and data['tutor_id']:
            try:
                tutor_id = int(data['tutor_id'])
                if tutor_id <= 0:
                    errors.append("ID de tutor debe ser un numero positivo")
            except (ValueError, TypeError):
                errors.append("ID de tutor debe ser un numero entero")

        # Validar especialidad_id si está presente
        if 'especialidad_id' in data and data['especialidad_id']:
            try:
                especialidad_id = int(data['especialidad_id'])
                if especialidad_id <= 0:
                    errors.append("ID de especialidad debe ser un numero positivo")
            except (ValueError, TypeError):
                errors.append("ID de especialidad debe ser un numero entero")

        # Validar fecha_ingreso si está presente
        if 'fecha_ingreso' in data and data['fecha_ingreso']:
            date_validation = Validators.validate_date(data['fecha_ingreso'], 'fecha_ingreso')
            if not date_validation['valid']:
                errors.append(date_validation['message'])
            else:
                # Verificar que la fecha de ingreso no sea futura
                try:
                    from datetime import datetime, date
                    if isinstance(data['fecha_ingreso'], str):
                        fecha_ingreso = datetime.strptime(data['fecha_ingreso'], '%Y-%m-%d').date()
                    else:
                        fecha_ingreso = data['fecha_ingreso']

                    if fecha_ingreso > date.today():
                        errors.append("La fecha de ingreso no puede ser futura")
                except:
                    errors.append("Formato de fecha de ingreso inválido")

        # Validar observaciones si están presentes
        if 'observaciones' in data and data['observaciones']:
            if len(data['observaciones'].strip()) > 1000:
                errors.append("Las observaciones no pueden tener mas de 1000 caracteres")

        # Validar estado si está presente
        if 'estado' in data and data['estado']:
            valid_states = ['activo', 'inactivo', 'alta', 'derivado']
            if data['estado'] not in valid_states:
                errors.append(f"Estado debe ser uno de: {', '.join(valid_states)}")

        # Validar IDs numéricos
        numeric_fields = ['usuario_creacion', 'usuario_modificacion']
        for field in numeric_fields:
            if field in data and data[field]:
                try:
                    int(data[field])
                except (ValueError, TypeError):
                    errors.append(f"{field} debe ser un numero entero")

        if errors:
            return {'valid': False, 'message': '; '.join(errors)}

        return {'valid': True, 'message': 'Datos de paciente validos'}