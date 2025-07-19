import requests
import json
import time

# Configuracion base
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Variables globales para las pruebas
token = None
created_especialidad_id = None


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


def test_especialidades_crud():
    """Probar CRUD completo de especialidades"""
    global token, created_especialidad_id
    print_section("CRUD DE ESPECIALIDADES")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Listar todas las especialidades
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Listar todas las especialidades", success, {
            "total_especialidades": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        print_test("Listar todas las especialidades", False, error=str(e))

    # 2. Listar especialidades por área - Terapéutico
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades/terapeutico",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Listar especialidades terapéuticas", success, {
            "total_terapeuticas": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        print_test("Listar especialidades terapéuticas", False, error=str(e))

    # 3. Listar especialidades por área - Pedagógico
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades/pedagogico",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Listar especialidades pedagógicas", success, {
            "total_pedagogicas": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        print_test("Listar especialidades pedagógicas", False, error=str(e))

    # 4. Crear nueva especialidad
    new_especialidad_data = {
        "nombre": f"Especialidad de Prueba {int(time.time())}",
        "area": "terapeutico",
        "estado": "activo"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/especialidades",
            headers=auth_headers,
            json=new_especialidad_data
        )

        success = response.status_code == 201
        response_data = response.json()

        if success and response_data.get("data", {}).get("id"):
            created_especialidad_id = response_data["data"]["id"]

        print_test("Crear especialidad", success, response_data)

    except Exception as e:
        print_test("Crear especialidad", False, error=str(e))

    # 5. Obtener especialidad por ID
    if created_especialidad_id:
        try:
            response = requests.get(
                f"{BASE_URL}/api/especialidades/id/{created_especialidad_id}",
                headers=auth_headers
            )

            success = response.status_code == 200
            print_test("Obtener especialidad por ID", success, response.json())

        except Exception as e:
            print_test("Obtener especialidad por ID", False, error=str(e))

    # 6. Actualizar especialidad
    if created_especialidad_id:
        update_data = {
            "nombre": f"Especialidad Actualizada {int(time.time())}"
        }

        try:
            response = requests.put(
                f"{BASE_URL}/api/especialidades/id/{created_especialidad_id}",
                headers=auth_headers,
                json=update_data
            )

            success = response.status_code == 200
            print_test("Actualizar especialidad", success, response.json())

        except Exception as e:
            print_test("Actualizar especialidad", False, error=str(e))


def test_especialidades_endpoints_adicionales():
    """Probar endpoints adicionales de especialidades"""
    global token
    print_section("ENDPOINTS ADICIONALES")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Obtener especialidades activas
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades/activas",
            headers=auth_headers
        )

        success = response.status_code == 200
        response_data = response.json()
        print_test("Especialidades activas", success, {
            "total_activas": len(response_data.get("data", [])) if success else 0,
            "status": response_data.get("status"),
            "message": response_data.get("message")
        })

    except Exception as e:
        print_test("Especialidades activas", False, error=str(e))

    # 2. Obtener estadísticas
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades/estadisticas",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Estadísticas de especialidades", success, response.json())

    except Exception as e:
        print_test("Estadísticas de especialidades", False, error=str(e))


def test_especialidades_validations():
    """Probar validaciones de especialidades"""
    global token
    print_section("VALIDACIONES DE ESPECIALIDADES")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # 1. Especialidad con campos faltantes
    invalid_especialidad_data = {
        "nombre": "",
        # area faltante
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/especialidades",
            headers=auth_headers,
            json=invalid_especialidad_data
        )

        success = response.status_code == 400
        print_test("Validacion campos faltantes", success, response.json())

    except Exception as e:
        print_test("Validacion campos faltantes", False, error=str(e))

    # 2. Área inválida
    invalid_area_data = {
        "nombre": "Especialidad Test",
        "area": "area_inexistente"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/especialidades",
            headers=auth_headers,
            json=invalid_area_data
        )

        success = response.status_code == 400
        print_test("Validacion area invalida", success, response.json())

    except Exception as e:
        print_test("Validacion area invalida", False, error=str(e))

    # 3. Nombre muy corto
    short_name_data = {
        "nombre": "AB",
        "area": "terapeutico"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/especialidades",
            headers=auth_headers,
            json=short_name_data
        )

        success = response.status_code == 400
        print_test("Validacion nombre muy corto", success, response.json())

    except Exception as e:
        print_test("Validacion nombre muy corto", False, error=str(e))

    # 4. Especialidad duplicada (intentar crear una que ya existe)
    duplicate_data = {
        "nombre": "Terapia Ocupacional Pediátrica",  # Ya existe en la BD
        "area": "terapeutico"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/especialidades",
            headers=auth_headers,
            json=duplicate_data
        )

        success = response.status_code == 400
        print_test("Validacion especialidad duplicada", success, response.json())

    except Exception as e:
        print_test("Validacion especialidad duplicada", False, error=str(e))

    # 5. Área inválida en endpoint
    try:
        response = requests.get(
            f"{BASE_URL}/api/especialidades/area_inexistente",
            headers=auth_headers
        )

        success = response.status_code == 400
        print_test("Validacion area invalida en endpoint", success, response.json())

    except Exception as e:
        print_test("Validacion area invalida en endpoint", False, error=str(e))


def test_delete_especialidad():
    """Probar eliminación de especialidad"""
    global token, created_especialidad_id
    print_section("ELIMINACION DE ESPECIALIDAD")

    if not token:
        print_test("Sin token para pruebas", False, error="No hay token disponible")
        return False

    if not created_especialidad_id:
        print_test("Sin especialidad para eliminar", False, error="No hay especialidad creada")
        return False

    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}

    # Eliminar especialidad creada en las pruebas
    try:
        response = requests.delete(
            f"{BASE_URL}/api/especialidades/id/{created_especialidad_id}",
            headers=auth_headers
        )

        success = response.status_code == 200
        print_test("Eliminar especialidad", success, response.json())

    except Exception as e:
        print_test("Eliminar especialidad", False, error=str(e))

    # Intentar eliminar especialidad que tiene personal asignado (debería fallar)
    try:
        response = requests.delete(
            f"{BASE_URL}/api/especialidades/id/1",  # ID 1 probablemente tiene personal asignado
            headers=auth_headers
        )

        success = response.status_code == 400
        print_test("Validacion eliminar con personal asignado (debe fallar)", success, response.json())

    except Exception as e:
        print_test("Validacion eliminar con personal asignado", False, error=str(e))


def run_all_tests():
    """Ejecutar todas las pruebas de especialidades"""
    print("INICIO DE PRUEBAS DEL MODULO DE ESPECIALIDADES")
    print("=" * 60)

    # Ejecutar pruebas en orden
    tests = [
        test_login,
        test_especialidades_crud,
        test_especialidades_endpoints_adicionales,
        test_especialidades_validations,
        test_delete_especialidad
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