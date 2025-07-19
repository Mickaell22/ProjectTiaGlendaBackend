import requests
import json
import time

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales para las pruebas
token = None
created_user_id = None


def print_section(title):
    """Imprimir seccion de pruebas"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_test(test_name, success, response_data=None, error=None):
    """Imprimir resultado de prueba"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} - {test_name}")

    if response_data:
        print(f"   Respuesta: {json.dumps(response_data, indent=4, ensure_ascii=False)}")

    if error:
        print(f"   Error: {error}")
    print()


def test_health_check():
    """Probar health check"""
    print_section("HEALTH CHECK")

    try:
        response = requests.get(f"{BASE_URL}/health")
        success = response.status_code == 200
        print_test("Health Check", success, response.json())
        return success
    except Exception as e:
        print_test("Health Check", False, error=str(e))
        return False


def test_api_basic():
    """Probar endpoints basicos"""
    print_section("ENDPOINTS BASICOS")

    # Test API
    try:
        response = requests.get(f"{BASE_URL}/api/test")
        success = response.status_code == 200
        print_test("API Test", success, response.json())
    except Exception as e:
        print_test("API Test", False, error=str(e))

    # Test Database
    try:
        response = requests.get(f"{BASE_URL}/api/test-db")
        success = response.status_code == 200
        print_test("Database Test", success, response.json())
        return success
    except Exception as e:
        print_test("Database Test", False, error=str(e))
        return False


def test_login():
    """Probar autenticacion"""
    global token
    print_section("AUTENTICACION")

    # Login exitoso
    login_data = {
        "usuario": "admin",
        "contrasenia": "admin123"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            headers=HEADERS,
            json=login_data
        )

        success = response.status_code == 200
        response_data = response.json()

        if success and response_data.get("data", {}).get("token"):
            token = response_data["data"]["token"]
            print_test("Login Exitoso", True, response_data)
        else:
            print_test("Login Exitoso", False, response_data)
            return False

    except Exception as e:
        print_test("Login Exitoso", False, error=str(e))
        return False

    # Login con credenciales incorrectas
    wrong_login_data = {
        "usuario": "admin",
        "contrasenia": "password_incorrecta"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/login",
            headers=HEADERS,
            json=wrong_login_data
        )

        success = response.status_code == 401
        print_test("Login con credenciales incorrectas", success, response.json())

    except Exception as e:
        print_test("Login con credenciales incorrectas", False, error=str(e))

    # Verificar token
    if token:
        auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

        try:
            response = requests.get(
                f"{BASE_URL}/api/verify-token",
                headers=auth_headers
            )

            success = response.status_code == 200
            print_test("Verificacion de Token", success, response.json())

        except Exception as e:
            print_test("Verificacion de Token", False, error=str(e))

    return token is not None


def test_protected_routes():
    """Probar rutas protegidas"""
    global token
    print_section("RUTAS PROTEGIDAS")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Test usuario actual
    try:
        response = requests.get(
            f"{BASE_URL}/api/me",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Obtener usuario actual", success, response.json())

    except Exception as e:
        print_test("Obtener usuario actual", False, error=str(e))

    # Test acceso sin token
    try:
        response = requests.get(f"{BASE_URL}/api/me")
        success = response.status_code == 401
        print_test("Acceso sin token (debe fallar)", success, response.json())

    except Exception as e:
        print_test("Acceso sin token", False, error=str(e))

    return True


def test_usuarios_crud():
    """Probar CRUD de usuarios"""
    global token, created_user_id
    print_section("CRUD DE USUARIOS")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Listar usuarios
    try:
        response = requests.get(
            f"{BASE_URL}/api/usuarios",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Listar usuarios", success, response.json())

    except Exception as e:
        print_test("Listar usuarios", False, error=str(e))

    # Obtener usuario por ID
    try:
        response = requests.get(
            f"{BASE_URL}/api/usuarios/1",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Obtener usuario por ID", success, response.json())

    except Exception as e:
        print_test("Obtener usuario por ID", False, error=str(e))

    # Crear nuevo usuario (necesitamos una persona primero)
    # Para esta prueba, usaremos persona_id = 1 (que deberia existir)
    new_user_data = {
        "usuario": f"test_user_{int(time.time())}",
        "contrasenia": "TestPassword123!",
        "persona_id": 1,
        "rol_id": 2,
        "estado": "activo"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/usuarios",
            headers=auth_headers,
            json=new_user_data
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_user_id = response_data["data"]["id"]

        print_test("Crear usuario", success, response_data)

    except Exception as e:
        print_test("Crear usuario", False, error=str(e))

    # Actualizar usuario creado
    if created_user_id:
        update_data = {
            "estado": "inactivo"
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/usuarios/{created_user_id}",
                headers=auth_headers,
                json=update_data
            )

            success = response.status_code == 200
            print_test("Actualizar usuario", success, response.json())

        except Exception as e:
            print_test("Actualizar usuario", False, error=str(e))

    # Eliminar usuario (eliminacion logica)
    if created_user_id:
        try:
            response = requests.delete(
                f"{BASE_URL}/api/usuarios/{created_user_id}",
                headers=auth_headers
            )

            success = response.status_code == 200
            print_test("Eliminar usuario", success, response.json())

        except Exception as e:
            print_test("Eliminar usuario", False, error=str(e))


def test_validations():
    """Probar validaciones"""
    global token
    print_section("VALIDACIONES")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Usuario con datos faltantes
    invalid_user_data = {
        "usuario": "",
        "contrasenia": "123"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/usuarios",
            headers=auth_headers,
            json=invalid_user_data
        )

        success = response.status_code == 400
        print_test("Validacion datos faltantes", success, response.json())

    except Exception as e:
        print_test("Validacion datos faltantes", False, error=str(e))

    # Contrasena debil
    weak_password_data = {
        "usuario": "test_weak",
        "contrasenia": "123",
        "persona_id": 1,
        "rol_id": 2
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/usuarios",
            headers=auth_headers,
            json=weak_password_data
        )

        success = response.status_code == 400
        print_test("Validacion contrasena debil", success, response.json())

    except Exception as e:
        print_test("Validacion contrasena debil", False, error=str(e))

    # Usuario duplicado
    duplicate_user_data = {
        "usuario": "admin",
        "contrasenia": "Password123!",
        "persona_id": 1,
        "rol_id": 2
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/usuarios",
            headers=auth_headers,
            json=duplicate_user_data
        )

        success = response.status_code == 400
        print_test("Validacion usuario duplicado", success, response.json())

    except Exception as e:
        print_test("Validacion usuario duplicado", False, error=str(e))


def test_logout():
    """Probar logout"""
    global token
    print_section("LOGOUT")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.post(
            f"{BASE_URL}/api/logout",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Logout", success, response.json())

    except Exception as e:
        print_test("Logout", False, error=str(e))


def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("INICIO DE PRUEBAS DEL API - SISTEMA TIA GLENDA")
    print("=" * 60)

    # Ejecutar pruebas en orden
    tests = [
        test_health_check,
        test_api_basic,
        test_login,
        test_protected_routes,
        test_usuarios_crud,
        test_validations,
        test_logout
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            result = test()
            if result is not False:
                passed += 1
        except Exception as e:
            print(f"Error ejecutando prueba: {e}")

    print_section("RESUMEN DE PRUEBAS")
    print(f"Pruebas ejecutadas: {total}")
    print(f"Pruebas exitosas: {passed}")
    print(f"Pruebas fallidas: {total - passed}")
    print(f"Porcentaje de exito: {(passed / total) * 100:.1f}%")


if __name__ == "__main__":
    # Verificar que el servidor este corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            run_all_tests()
        else:
            print("Error: El servidor no responde correctamente")
    except Exception as e:
        print(f"Error: No se pudo conectar al servidor en {BASE_URL}")
        print(f"Asegurate de que el servidor este corriendo con: python app.py")
        print(f"Error detallado: {e}")