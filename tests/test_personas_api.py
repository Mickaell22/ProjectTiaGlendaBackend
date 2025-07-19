import requests
import json
import time

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales para las pruebas
token = None
created_persona_id = None


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


def test_login():
    """Autenticarse para obtener token"""
    global token
    print_section("AUTENTICACION PARA PRUEBAS")

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
            print_test("Login para pruebas", True, {"message": "Token obtenido exitosamente"})
            return True
        else:
            print_test("Login para pruebas", False, response_data)
            return False

    except Exception as e:
        print_test("Login para pruebas", False, error=str(e))
        return False


def test_get_roles():
    """Probar obtener roles"""
    global token
    print_section("PRUEBAS DE ROLES")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{BASE_URL}/api/roles",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Obtener roles", success, response.json())
        return success

    except Exception as e:
        print_test("Obtener roles", False, error=str(e))
        return False


def test_personas_crud():
    """Probar CRUD completo de personas"""
    global token, created_persona_id
    print_section("CRUD DE PERSONAS")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar personas
    try:
        response = requests.get(
            f"{BASE_URL}/api/personas",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Listar personas", success, {
            "total_personas": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        print_test("Listar personas", False, error=str(e))

    # 2. Crear nueva persona
    new_persona_data = {
        "nombre": "Maria Elena",
        "apellido": "García",
        "cedula": f"99{int(time.time())}",  # Cedula única
        "telefono": "+50699887766",
        "correo": f"maria.garcia.{int(time.time())}@email.com",
        "direccion": "San José, Costa Rica",
        "fecha_nacimiento": "1990-05-15",
        "estado": "activo"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            json=new_persona_data
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_persona_id = response_data["data"]["id"]

        print_test("Crear persona", success, response_data)

    except Exception as e:
        print_test("Crear persona", False, error=str(e))

    # 3. Obtener persona por ID
    if created_persona_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/personas/{created_persona_id}",
                headers=auth_headers
            )

            success = response.status_code == 200
            print_test("Obtener persona por ID", success, response.json())

        except Exception as e:
            print_test("Obtener persona por ID", False, error=str(e))

    # 4. Actualizar persona
    if created_persona_id:
        update_data = {
            "telefono": "+50699887700",
            "direccion": "Cartago, Costa Rica - Actualizada"
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/personas/{created_persona_id}",
                headers=auth_headers,
                json=update_data
            )

            success = response.status_code == 200
            print_test("Actualizar persona", success, response.json())

        except Exception as e:
            print_test("Actualizar persona", False, error=str(e))

    # 5. Obtener personas disponibles para usuario
    try:
        response = requests.get(
            f"{BASE_URL}/api/personas/disponibles",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Personas disponibles para usuario", success, {
            "total_disponibles": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        print_test("Personas disponibles para usuario", False, error=str(e))


def test_personas_validations():
    """Probar validaciones de personas"""
    global token
    print_section("VALIDACIONES DE PERSONAS")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Persona con campos faltantes
    invalid_persona_data = {
        "nombre": "",
        "apellido": "Test",
        # cedula faltante
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            json=invalid_persona_data
        )

        success = response.status_code == 400
        print_test("Validacion campos faltantes", success, response.json())

    except Exception as e:
        print_test("Validacion campos faltantes", False, error=str(e))

    # 2. Cedula duplicada
    duplicate_cedula_data = {
        "nombre": "Test",
        "apellido": "Duplicado",
        "cedula": "12345678",  # Cedula que ya existe en la BD
        "telefono": "+50699887766",
        "correo": "test.duplicado@email.com"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            json=duplicate_cedula_data
        )

        success = response.status_code == 400
        print_test("Validacion cedula duplicada", success, response.json())

    except Exception as e:
        print_test("Validacion cedula duplicada", False, error=str(e))

    # 3. Email invalido
    invalid_email_data = {
        "nombre": "Test",
        "apellido": "Email",
        "cedula": f"88{int(time.time())}",
        "correo": "email_invalido_sin_arroba"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            json=invalid_email_data
        )

        success = response.status_code == 400
        print_test("Validacion email invalido", success, response.json())

    except Exception as e:
        print_test("Validacion email invalido", False, error=str(e))

    # 4. Fecha de nacimiento futura
    future_date_data = {
        "nombre": "Test",
        "apellido": "Futuro",
        "cedula": f"77{int(time.time())}",
        "fecha_nacimiento": "2030-01-01"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/personas",
            headers=auth_headers,
            json=future_date_data
        )

        success = response.status_code == 400
        print_test("Validacion fecha futura", success, response.json())

    except Exception as e:
        print_test("Validacion fecha futura", False, error=str(e))


def test_delete_persona():
    """Probar eliminación de persona"""
    global token, created_persona_id
    print_section("ELIMINACION DE PERSONA")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    if not created_persona_id:
        print_test("Sin persona para eliminar", False, error="No hay persona creada")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Eliminar persona creada en las pruebas
    try:
        response = requests.delete(
            f"{BASE_URL}/api/personas/{created_persona_id}",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Eliminar persona", success, response.json())

    except Exception as e:
        print_test("Eliminar persona", False, error=str(e))

    # Intentar eliminar persona administrador (debe fallar)
    try:
        response = requests.delete(
            f"{BASE_URL}/api/personas/1",
            headers=auth_headers
        )

        success = response.status_code == 400
        print_test("Validacion eliminar admin (debe fallar)", success, response.json())

    except Exception as e:
        print_test("Validacion eliminar admin", False, error=str(e))


def run_all_tests():
    """Ejecutar todas las pruebas de personas"""
    print("INICIO DE PRUEBAS DEL MODULO DE PERSONAS")
    print("=" * 60)

    # Ejecutar pruebas en orden
    tests = [
        test_login,
        test_get_roles,
        test_personas_crud,
        test_personas_validations,
        test_delete_persona
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