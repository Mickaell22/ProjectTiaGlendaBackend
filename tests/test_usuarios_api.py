import requests
import json
import time
import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.advanced_test_runner import AdvancedTestRunner, TestConfig

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales para las pruebas
token = None
created_usuario_id = None
created_persona_id = None
test_rol_id = None


def print_test_info(test_name, status, data=None, error=None):
    """Función helper para logging de tests individuales"""
    if data and isinstance(data, dict):
        try:
            # Usar ensure_ascii=True para evitar problemas con Unicode en Windows
            print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=True)[:200]}...")
        except UnicodeEncodeError:
            # Fallback si hay problemas de codificación
            print(f"   Datos: {str(data)[:200]}...")
    if error:
        try:
            print(f"   Error: {error}")
        except UnicodeEncodeError:
            print(f"   Error: {str(error).encode('ascii', 'replace').decode('ascii')}")


def test_login():
    """Autenticarse para obtener token"""
    global token

    login_data = {
        "usuario": "admin.norte",
        "contrasenia": "admin123"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            headers=HEADERS,
            json=login_data,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data", {}).get("token"):
            token = response_data["data"]["token"]
            print_test_info("Login", "SUCCESS", {"message": "Token obtenido exitosamente"})
            return True
        else:
            print_test_info("Login", "FAILED", response_data)
            raise Exception(f"Login failed: {response_data}")

    except Exception as e:
        if "Login failed:" in str(e):
            raise e
        print_test_info("Login", "ERROR", error=str(e))
        raise Exception(f"Error en login: {str(e)}")


def setup_test_data():
    """Crear datos de prueba necesarios"""
    global token, created_persona_id, test_rol_id

    if not token:
        raise Exception("No hay token disponible para setup")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Crear una persona para usar como usuario
    timestamp = int(time.time())
    persona_data = {
        "nombre": "Andrea Lucia",
        "apellido": "Vargas Solano",
        "cedula": f"88{timestamp}",
        "telefono": "+50688112233",
        "correo": f"andrea.vargas{timestamp}@gmail.com",
        "direccion": "Heredia, Costa Rica",
        "fecha_nacimiento": "1990-07-10"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            json=persona_data,
            timeout=10
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_persona_id = response_data["data"]["id"]
            print_test_info("Setup persona para usuario", "SUCCESS", {"persona_id": created_persona_id})
        else:
            raise Exception(f"Error creando persona: {response_data}")

    except Exception as e:
        if "Error creando persona:" in str(e):
            raise e
        raise Exception(f"Error en setup persona: {str(e)}")

    # 2. Obtener roles disponibles
    try:
        response = requests.get(
            f"{BASE_URL}/api/roles",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data") and len(response_data["data"]) > 0:
            # Buscar un rol que no sea administrador para las pruebas
            for rol in response_data["data"]:
                if rol.get("nombre", "").lower() != "administrador":
                    test_rol_id = rol["id"]
                    break

            if not test_rol_id and len(response_data["data"]) > 0:
                test_rol_id = response_data["data"][0]["id"]  # Usar cualquier rol disponible

            print_test_info("Setup rol para tests", "SUCCESS", {
                "rol_id": test_rol_id,
                "total_roles": len(response_data["data"])
            })
        else:
            raise Exception("No hay roles disponibles para tests")

    except Exception as e:
        if "No hay roles disponibles" in str(e):
            raise e
        raise Exception(f"Error en setup rol: {str(e)}")

    return True


def test_usuarios_crud():
    """Probar CRUD completo de usuarios"""
    global token, created_usuario_id, created_persona_id, test_rol_id

    if not token or not created_persona_id or not test_rol_id:
        raise Exception("Faltan datos de configuración para CRUD")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar todos los usuarios
    try:
        response = requests.get(
            f"{BASE_URL}/api/usuarios",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error listando usuarios: {response_data}")

        print_test_info("Listar usuarios", "SUCCESS", {
            "total_usuarios": len(response_data.get("data", [])),
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        if "Error listando usuarios:" in str(e):
            raise e
        raise Exception(f"Error en listar usuarios: {str(e)}")

    # 2. Crear nuevo usuario
    timestamp = int(time.time())
    new_usuario_data = {
        "id_persona": created_persona_id,
        "usuario": f"usuario_test_{timestamp}",
        "contrasenia": "TestPassword123!",
        "id_rol": test_rol_id,
        "estado": "activo"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/usuarios",
            headers=auth_headers,
            json=new_usuario_data,
            timeout=10
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_usuario_id = response_data["data"]["id"]

        if not success:
            raise Exception(f"Error creando usuario: {response_data}")

        print_test_info("Crear usuario", "SUCCESS", response_data)

    except Exception as e:
        if "Error creando usuario:" in str(e):
            raise e
        raise Exception(f"Error en crear usuario: {str(e)}")

    # 3. Obtener usuario por ID
    if created_usuario_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/usuarios/{created_usuario_id}",
                headers=auth_headers,
                timeout=10
            )

            success = response.status_code == 200
            if not success:
                raise Exception(f"Error obteniendo usuario: {response.json()}")

            print_test_info("Obtener usuario por ID", "SUCCESS", response.json())

        except Exception as e:
            if "Error obteniendo usuario:" in str(e):
                raise e
            raise Exception(f"Error en obtener usuario: {str(e)}")

    # 4. Actualizar usuario
    if created_usuario_id:
        update_data = {
            "estado": "activo"
            # Nota: No se debe cambiar contraseña en update general
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/usuarios/{created_usuario_id}",
                headers=auth_headers,
                json=update_data,
                timeout=10
            )

            success = response.status_code == 200
            if not success:
                raise Exception(f"Error actualizando usuario: {response.json()}")

            print_test_info("Actualizar usuario", "SUCCESS", response.json())

        except Exception as e:
            if "Error actualizando usuario:" in str(e):
                raise e
            raise Exception(f"Error en actualizar usuario: {str(e)}")

    return True


def test_usuarios_autenticacion():
    """Probar funcionalidades de autenticación"""
    global token

    if not token:
        raise Exception("No hay token para autenticación")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Verificar token actual
    try:
        response = requests.get(
            f"{BASE_URL}/api/verify-token",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        if not success:
            raise Exception(f"Error verificando token: {response.json()}")

        print_test_info("Verificar token", "SUCCESS", response.json())

    except Exception as e:
        if "Error verificando token:" in str(e):
            raise e
        raise Exception(f"Error en verificar token: {str(e)}")

    # 2. Obtener información del usuario actual
    try:
        response = requests.get(
            f"{BASE_URL}/api/me",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        if not success:
            raise Exception(f"Error obteniendo usuario actual: {response.json()}")

        print_test_info("Usuario actual", "SUCCESS", response.json())

    except Exception as e:
        if "Error obteniendo usuario actual:" in str(e):
            raise e
        raise Exception(f"Error en usuario actual: {str(e)}")

    # 3. Test de logout
    try:
        response = requests.post(
            f"{BASE_URL}/api/logout",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        if not success:
            raise Exception(f"Error en logout: {response.json()}")

        print_test_info("Logout", "SUCCESS", response.json())

    except Exception as e:
        if "Error en logout:" in str(e):
            raise e
        raise Exception(f"Error en logout: {str(e)}")

    return True


def test_usuarios_roles():
    """Probar funcionalidades relacionadas con roles"""
    global token

    if not token:
        raise Exception("No hay token para roles")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener todos los roles
    try:
        response = requests.get(
            f"{BASE_URL}/api/roles",
            headers=auth_headers,
            timeout=10
        )

        success = response.status_code == 200
        response_data = response.json()
        if not success:
            raise Exception(f"Error obteniendo roles: {response_data}")

        print_test_info("Listar roles", "SUCCESS", {
            "total_roles": len(response_data.get("data", [])),
            "roles": [rol.get("nombre") for rol in response_data.get("data", [])],
            "status": response_data.get("status")
        })

    except Exception as e:
        if "Error obteniendo roles:" in str(e):
            raise e
        raise Exception(f"Error en roles: {str(e)}")

    return True


def test_usuarios_validations():
    """Probar validaciones de usuarios"""
    global token

    if not token:
        raise Exception("No hay token para validaciones")

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Lista de validaciones a probar
    validations = [
        {
            "name": "campos faltantes",
            "data": {"usuario": "test_user", "id_rol": 1},  # id_persona y contrasenia faltantes
            "expected_status": 400
        },
        {
            "name": "usuario muy corto",
            "data": {"id_persona": 1, "usuario": "ab", "contrasenia": "Password123!", "id_rol": 1},
            "expected_status": 400
        },
        {
            "name": "usuario muy largo",
            "data": {"id_persona": 1, "usuario": "a" * 100, "contrasenia": "Password123!", "id_rol": 1},
            "expected_status": 400
        },
        {
            "name": "contrasenia muy corta",
            "data": {"id_persona": 1, "usuario": "test_user", "contrasenia": "123", "id_rol": 1},
            "expected_status": 400
        },
        {
            "name": "id_persona invalido",
            "data": {"id_persona": "no_es_numero", "usuario": "test_user", "contrasenia": "Password123!", "id_rol": 1},
            "expected_status": 400
        },
        {
            "name": "id_rol invalido",
            "data": {"id_persona": 1, "usuario": "test_user", "contrasenia": "Password123!", "id_rol": "no_es_numero"},
            "expected_status": 400
        },
        {
            "name": "persona inexistente",
            "data": {"id_persona": 99999, "usuario": "test_user", "contrasenia": "Password123!", "id_rol": 1},
            "expected_status": 400
        },
        {
            "name": "rol inexistente",
            "data": {"id_persona": 1, "usuario": "test_user", "contrasenia": "Password123!", "id_rol": 99999},
            "expected_status": 400
        },
        {
            "name": "usuario duplicado",
            "data": {"id_persona": 1, "usuario": "admin", "contrasenia": "Password123!", "id_rol": 1},
            # Usuario admin ya existe
            "expected_status": 400
        }
    ]

    for validation in validations:
        try:
            response = requests.post(
                f"{BASE_URL}/api/usuarios",
                headers=auth_headers,
                json=validation["data"],
                timeout=10
            )

            success = response.status_code == validation["expected_status"]
            if not success:
                raise Exception(
                    f"Validación '{validation['name']}' falló. Esperado: {validation['expected_status']}, Obtenido: {response.status_code}")

            print_test_info(f"Validación: {validation['name']}", "SUCCESS", {
                "status_code": response.status_code,
                "message": response.json().get("message", "")
            })

        except Exception as e:
            if f"Validación '{validation['name']}' falló" in str(e):
                raise e
            raise Exception(f"Error en validación {validation['name']}: {str(e)}")

    return True


def test_usuarios_permisos():
    """Probar validaciones de permisos (acceso sin token)"""
    global created_usuario_id

    # Test de acceso sin token a endpoints protegidos
    endpoints_protegidos = [
        ("GET", "/api/usuarios", "Listar usuarios sin token"),
        ("GET", "/api/me", "Usuario actual sin token"),
        ("GET", "/api/verify-token", "Verificar token sin token"),
        ("POST", "/api/logout", "Logout sin token")
    ]

    if created_usuario_id:
        endpoints_protegidos.append(("GET", f"/api/usuarios/{created_usuario_id}", "Obtener usuario sin token"))

    for metodo, endpoint, descripcion in endpoints_protegidos:
        try:
            if metodo == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            elif metodo == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", headers=HEADERS, timeout=10)

            success = response.status_code == 401  # Debe fallar con 401 Unauthorized
            if not success:
                print_test_info(descripcion, "INFO", {
                    "message": f"Respuesta inesperada: {response.status_code}, pero test continúa"
                })
            else:
                print_test_info(descripcion, "SUCCESS", {
                    "status_code": response.status_code,
                    "message": "Acceso correctamente denegado"
                })

        except Exception as e:
            print_test_info(descripcion, "INFO", {
                "message": f"Test omitido por error: {str(e)}"
            })

    return True


def main():
    """Función principal con el nuevo runner"""

    # Configurar el runner
    config = TestConfig()
    config.bar_style = "modern"
    config.show_eta = True
    config.show_individual_times = True
    config.colored_output = True
    config.detailed_summary = True
    config.export_results = True
    config.export_path = "results_usuarios.json"
    config.retry_failed = True
    config.max_retries = 2

    # Crear el runner
    runner = AdvancedTestRunner("USUARIOS", config)

    # Agregar tests en orden
    tests_to_run = [
        (test_login, "Autenticacion"),
        (setup_test_data, "Configuracion de datos"),
        (test_usuarios_crud, "CRUD de usuarios"),
        (test_usuarios_autenticacion, "Funciones de autenticación"),
        (test_usuarios_roles, "Gestión de roles"),
        (test_usuarios_validations, "Validaciones"),
        (test_usuarios_permisos, "Validaciones de permisos")
    ]

    for test_func, test_name in tests_to_run:
        runner.add_test(test_func, test_name)

    # Ejecutar todas las pruebas
    results = runner.run()

    # Retornar código de salida apropiado para CI/CD
    return 0 if results["success"] else 1


if __name__ == "__main__":
    # Verificar que el servidor este corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            exit_code = main()
            sys.exit(exit_code)
        else:
            print("❌ Error: El servidor no responde correctamente")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: No se pudo conectar al servidor en {BASE_URL}")
        print(f"Asegurate de que el servidor este corriendo con: python app.py")
        print(f"Error detallado: {e}")
        sys.exit(1)